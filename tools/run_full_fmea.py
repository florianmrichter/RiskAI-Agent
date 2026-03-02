"""
Vollständige FMEA-Analyse -- Automatisierte Pipeline für alle Komponenten.

Führt Schritte 1-7 durch:
  1. Anlagendaten laden
  2. Strukturanalyse (Projekt + Komponenten)
  3. Funktionsanalyse (pro Komponente)
  4. Fehleranalyse (pro Funktion)
  5. RPZ-Berechnung + Validierung
  6. Maßnahmen (STOP+ABE) für RPZ >= 100
  7. Report generieren

Usage:
    python tools/run_full_fmea.py [--project-id 1] [--json tasks/Risikoanalyse/Ethylacetatproduktion_20TA41/anlagendaten.json]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.load_plant_data import load_plant_data
from tools.structure_analysis import analyze_structure, save_components_to_db
from tools.storage import FMEAStorage
from tools.rpz_calculator import calculate_and_store_rpz
from tools.report_generator import generate_report
from tools.reliability_lookup import ReliabilityDB
from tools.failure_templates import get_templates_for_component

# ─── Typische Funktionen pro Komponententyp (Workflow-basiert) ───
FUNKTIONEN_PRO_TYP = {
    "prozess": [
        ("Hauptfunktion", "Stellt den Prozessraum/Behälter für die verfahrenstechnische Operation bereit"),
        ("Nebenfunktion", "Gewährleistet Dichtheit gegen Prozessmedien unter Betriebsbedingungen"),
        ("Nebenfunktion", "Ermöglicht sichere Befüllung und Entleerung"),
    ],
    "thermisch": [
        ("Hauptfunktion", "Überträgt Wärme zwischen Prozess und Kühl-/Heizmedium"),
        ("Nebenfunktion", "Begrenzt Temperaturgradienten zur Vermeidung thermischer Spannungen"),
    ],
    "mechanisch": [
        ("Hauptfunktion", "Erzeugt Durchmischung/Strömung im Prozessmedium"),
        ("Nebenfunktion", "Gewährleistet Dichtheit der Wellenabdichtung gegen Prozessmedien"),
    ],
    "elektrisch": [
        ("Hauptfunktion", "Misst Prozessgröße und liefert Signal für Regelung/Überwachung"),
        ("Nebenfunktion", "Liefert Eingang für Sicherheitsabschaltung (falls SIL)"),
    ],
    "sicherheit": [
        ("Hauptfunktion", "Begrenzt Druck durch automatisches Öffnen bei Überschreitung des Ansprechdrucks"),
        ("Nebenfunktion", "Leitet abgeblasene Medien sicher ab"),
    ],
    "dosierung": [
        ("Hauptfunktion", "Fördert Medium mit definierter Dosierrate in den Prozess"),
        ("Nebenfunktion", "Gewährleistet Dichtheit gegen Prozessmedien"),
    ],
    "sonstige": [
        ("Hauptfunktion", "Erfüllt die primäre Aufgabe der Komponente im Prozess"),
    ],
}

# ─── Typische Fehlermodi pro Funktionstyp (vereinfacht) ───
FEHLERMODI_PRO_FUNKTION = {
    "prozess": ["Überdruck über Design-Limit", "Übertemperatur über Betriebsgrenze", "Überfüllung"],
    "thermisch": ["Verlust der Wärmeabfuhr", "Lokale Überhitzung", "Thermischer Schock"],
    "mechanisch": ["Wellenabdichtung undicht", "Lagerausfall", "Vibration/Resonanz"],
    "elektrisch": ["Eingefrorener Messwert (Frozen Value)", "Messwertdrift", "Signalausfall"],
    "sicherheit": ["Öffnet nicht bei Ansprechdruck (Fail-to-open)", "Frühzeitiges Ansprechen", "Leckage"],
    "dosierung": ["Überdosierung", "Unterdosierung", "Membranbruch"],
    "sonstige": ["Funktionsausfall", "Leckage", "Blockade"],
}


def _get_typ_fuer_fehlermodi(kat: str) -> str:
    """Kategorie -> Typ für Fehlermodi-Mapping."""
    if kat == "msr":
        return "elektrisch"
    if kat == "equipment":
        return "prozess"
    return kat if kat in FEHLERMODI_PRO_FUNKTION else "sonstige"


def step1_load_and_structure(json_path: str, project_id: int, db_path: str = None) -> dict:
    """Schritt 1+2: Daten laden, Struktur analysieren, Projekt anlegen."""
    plant_data = load_plant_data(json_path)
    db = FMEAStorage(db_path)
    proj = db.get_project(project_id)
    if not proj:
        project_id = db.create_project(
            plant_data.get("bezeichnung", "FMEA-Projekt"),
            plant_data.get("teilanlage_nr", ""),
        )
    components = analyze_structure(plant_data)
    # Nur Komponenten einfügen, die noch nicht existieren
    existing = {c["komp_id"] for c in db.get_components(project_id)}
    to_save = [c for c in components if c["komp_id"] not in existing]
    if to_save:
        for c in to_save:
            db.insert_component(
                project_id=project_id,
                komp_id=c["komp_id"],
                name=c["name"],
                typ=c["typ"],
                kategorie=c["kategorie"],
                system_name=c["system_name"],
                beschreibung=c["beschreibung"],
                parameters=c["parameters"],
                kontext=c["lean_context"],
            )
    db.close()
    return {"plant_data": plant_data, "components": components, "project_id": project_id}


def step3_funktionsanalyse(project_id: int, db_path: str = None):
    """Schritt 3: Funktionen für alle Komponenten ohne Funktionen."""
    db = FMEAStorage(db_path)
    components = db.get_components(project_id)
    rdb = ReliabilityDB()
    func_count = 0
    for comp in components:
        funcs = db.get_functions(comp["id"])
        if funcs:
            continue
        typ = comp.get("typ", "sonstige")
        patterns = FUNKTIONEN_PRO_TYP.get(typ, FUNKTIONEN_PRO_TYP["sonstige"])
        for i, (ftyp, beschr) in enumerate(patterns[:3], 1):  # max 3 pro Komponente
            fid = f"{comp['komp_id']}-F{i}"
            db.insert_function(
                comp["id"],
                fid,
                ftyp,
                f"{beschr} ({comp['name']})",
                [{"id": f"{fid}-A1", "parameter": "Betriebsgrenzen", "sollwert": "Gemäß Design-Limits"}],
            )
            func_count += 1
    db.close()
    return func_count


def step4_fehleranalyse(project_id: int, db_path: str = None):
    """Schritt 4: Fehlermodi, Ursachen, Folgen, Controls, S/O/D für alle Funktionen."""
    db = FMEAStorage(db_path)
    rdb = ReliabilityDB()
    fm_count = 0
    components = db.get_components(project_id)
    for comp in components:
        funcs = db.get_functions(comp["id"])
        typ_key = _get_typ_fuer_fehlermodi(comp.get("kategorie", "sonstige"))
        fehlermodi_liste = FEHLERMODI_PRO_FUNKTION.get(typ_key, FEHLERMODI_PRO_FUNKTION["sonstige"])
        for func in funcs:
            fms = db.get_failure_modes(func["id"])
            if fms:
                continue
            for j, fm_desc in enumerate(fehlermodi_liste[:2], 1):  # max 2 pro Funktion
                fehler_id = f"{func['funktion_id']}-FM{j}"
                fm_id = db.insert_failure_mode(func["id"], fehler_id, fm_desc, "Prozess")
                db.insert_failure_cause(
                    fm_id, f"{fehler_id}-UC1",
                    "Betriebsbedingte Abweichung oder Verschleiß",
                    "Betrieb", "Betrieb", "Regelmäßige Inspektion",
                )
                db.insert_failure_cause(
                    fm_id, f"{fehler_id}-UC2",
                    "Design- oder Fertigungsmangel",
                    "Design", "Detaildesign", "Qualitätssicherung",
                )
                db.insert_failure_effect(
                    fm_id,
                    mensch_stufe="Leichte bis schwere Verletzung",
                    mensch_beschreibung="Medienfreisetzung, Verätzungs- oder Verbrennungsgefahr",
                    umwelt_stufe="Betriebsbereich",
                    umwelt_beschreibung="Auffangwanne, keine externe Kontamination",
                    anlage_stufe="Teilausfall",
                    anlage_beschreibung="Stillstand für Reparatur/Reinigung",
                    kosten_stufe="Bis 100.000 €",
                    kosten_beschreibung="Reparatur, Chargenverlust, Reinigung",
                )
                # O-Richtwert aus Reliability-DB wenn möglich
                o_val = 4
                eq_map = {"prozess": "druckbehaelter", "thermisch": "rohrbuendel", "mechanisch": "kreiselpumpe",
                          "elektrisch": "drucktransmitter", "sicherheit": "sicherheitsventil_psv", "dosierung": "dosierpumpe_membran"}
                eq_type = eq_map.get(typ_key, "druckbehaelter")
                try:
                    info = rdb.get_equipment_info(eq_type)
                    if info and info.get("typische_fehlermodi"):
                        o_val = info["typische_fehlermodi"][0].get("o_richtwert", 4)
                except Exception:
                    pass
                db.insert_current_control(fm_id, "DCS-Überwachung", "Sensor", "B", None, "Prozessleitsystem", "D")
                db.insert_risk_assessment(
                    fm_id, S=7, O=o_val, D=4,
                    begruendung_S="Medienfreisetzung in Ex-Zone, Personengefährdung",
                    begruendung_O=f"O={o_val} aus Zuverlässigkeitsdaten/Erfahrung",
                    begruendung_D="Regelung erkennt Abweichung, manuelle Intervention",
                )
                fm_count += 1
    db.close()
    return fm_count


def step6_massnahmen(project_id: int, db_path: str = None):
    """Schritt 6: Maßnahmen – KEINE generische Logik.
    Maßnahmen werden ausschließlich explizit pro Fehlermodus definiert (Agent-Einzelfallanalyse
    oder config/measures_explicit). Kein automatisches Einfügen von Platzhaltern."""
    db = FMEAStorage(db_path)
    high = db.get_all_failure_modes_with_rpz(project_id, min_rpz=100)
    ohne = sum(1 for fm in high if not db.get_measures(fm["id"]))
    db.close()
    return 0  # Keine generischen Maßnahmen mehr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-id", type=int, default=1)
    ap.add_argument("--json", default="tasks/Risikoanalyse/Ethylacetatproduktion_20TA41/anlagendaten.json")
    ap.add_argument("--output-dir", default="tasks/Risikoanalyse/Ethylacetatproduktion_20TA41")
    args = ap.parse_args()
    json_path = Path(__file__).parent.parent / args.json
    if not json_path.exists():
        print(f"Fehler: {json_path} nicht gefunden.")
        sys.exit(1)
    print("=" * 60)
    print("Vollständige FMEA-Analyse")
    print("=" * 60)
    print("\n[1+2] Anlagendaten laden, Struktur analysieren...")
    ctx = step1_load_and_structure(str(json_path), args.project_id)
    print(f"      Projekt {ctx['project_id']}, {len(ctx['components'])} Komponenten")
    print("\n[3] Funktionsanalyse...")
    nf = step3_funktionsanalyse(ctx["project_id"])
    print(f"      {nf} neue Funktionen")
    print("\n[4] Fehleranalyse...")
    nfm = step4_fehleranalyse(ctx["project_id"])
    print(f"      {nfm} neue Fehlermodi")
    print("\n[5] RPZ-Berechnung...")
    stats = calculate_and_store_rpz(ctx["project_id"])
    print(f"      {stats['total']} Fehlermodi, Verteilung: {stats['rpz_distribution']}")
    print("\n[6] Maßnahmen (RPZ >= 100)...")
    nm = step6_massnahmen(ctx["project_id"])
    print(f"      {nm} Maßnahmen ergänzt")
    print("\n[7] Report generieren...")
    out_dir = Path(__file__).parent.parent / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    anlage = ctx["plant_data"].get("bezeichnung", "Report").replace(" ", "_")
    pdf_path = generate_report(
        ctx["project_id"],
        output_path=str(out_dir / f"FMEA_Bericht_{anlage}_{ctx['plant_data'].get('teilanlage_nr', '')}.pdf"),
    )
    print(f"      Report: {pdf_path}")
    print("\n" + "=" * 60)
    print("FMEA-Analyse abgeschlossen.")
    print("=" * 60)


if __name__ == "__main__":
    main()
