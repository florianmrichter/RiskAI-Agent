"""
Proof of Concept -- Full FMEA pipeline run for 3 representative components.

Demonstrates the complete data flow through all 9 entities:
  Project → Component → Function → FailureMode → FailureCause → FailureEffect
  → RiskAssessment → CurrentControl → Measure

This script contains the Agent's analysis results hardcoded as the
deterministic "recording" of what the Agent would produce.
In production, the Agent generates this dynamically.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.rpz_calculator import calculate_and_store_rpz

PROJECT_ID = 1


def run_funktionsanalyse(db: FMEAStorage):
    """Schritt 3: Funktionsanalyse für 3 Komponenten."""
    print("\n=== Schritt 3: Funktionsanalyse ===")

    # KOMP-001: Synthesereaktor R-101
    c1 = db.get_component_by_komp_id("KOMP-001")
    db.insert_function(c1["id"], "KOMP-001-F1", "Hauptfunktion",
        "Stellt den geschlossenen Reaktionsraum für die säurekatalysierte Fischer-Veresterung von Ethanol mit Essigsäure bereit",
        [
            {"id": "KOMP-001-F1-A1", "parameter": "Betriebstemperatur", "sollwert": "80 °C (Bereich 20-100 °C, Design -20 bis 180 °C)"},
            {"id": "KOMP-001-F1-A2", "parameter": "Betriebsdruck", "sollwert": "1 bar (Bereich 0.5-1.2 bar, Design -0.9 bis 6 bar)"},
            {"id": "KOMP-001-F1-A3", "parameter": "Füllvolumen", "sollwert": "Max. 400 L (Nennvolumen 500 L, LSHH bei 480 L)"},
        ])
    db.insert_function(c1["id"], "KOMP-001-F2", "Nebenfunktion",
        "Gewährleistet Dichtheit gegen Ethanol, Essigsäure, Schwefelsäure und Ethylacetat unter Betriebsbedingungen",
        [
            {"id": "KOMP-001-F2-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage an allen Flanschverbindungen, Stutzen und Mannloch"},
            {"id": "KOMP-001-F2-A2", "parameter": "Werkstoffbeständigkeit", "sollwert": "1.4571 (316Ti) beständig gegen Essigsäure bis 100 °C und H2SO4 1%"},
        ])
    db.insert_function(c1["id"], "KOMP-001-F3", "Nebenfunktion",
        "Ermöglicht die kontrollierte azeotrope Destillation zur Wasserabtrennung über die integrierte Kolonne K-101",
        [
            {"id": "KOMP-001-F3-A1", "parameter": "Trennleistung", "sollwert": "10 theoretische Böden, Ethylacetat-Reinheit > 99.5 Gew.-%"},
        ])
    print(f"  KOMP-001: 3 Funktionen gespeichert")

    # KOMP-013: PIC-402 (Drucktransmitter)
    c13 = db.get_component_by_komp_id("KOMP-013")
    db.insert_function(c13["id"], "KOMP-013-F1", "Hauptfunktion",
        "Misst den Prozessdruck im Reaktor R-101 kontinuierlich und steuert die PID-Druckregelung",
        [
            {"id": "KOMP-013-F1-A1", "parameter": "Messbereich", "sollwert": "-1 bis 8 bar"},
            {"id": "KOMP-013-F1-A2", "parameter": "Genauigkeit", "sollwert": "±0.1 bar"},
            {"id": "KOMP-013-F1-A3", "parameter": "SIL-Level", "sollwert": "SIL-1"},
        ])
    db.insert_function(c13["id"], "KOMP-013-F2", "Nebenfunktion",
        "Liefert Eingangssignal für die Sicherheitsabschaltung bei Überdruck (PSHH)",
        [
            {"id": "KOMP-013-F2-A1", "parameter": "Signalausgabe", "sollwert": "4-20 mA, HART-Protokoll"},
            {"id": "KOMP-013-F2-A2", "parameter": "Ex-Schutz", "sollwert": "ATEX Zone 1, IP65"},
        ])
    print(f"  KOMP-013: 2 Funktionen gespeichert")

    # KOMP-017: PSV-410 (Sicherheitsventil)
    c17 = db.get_component_by_komp_id("KOMP-017")
    db.insert_function(c17["id"], "KOMP-017-F1", "Hauptfunktion",
        "Begrenzt den Druck im Reaktor R-101 durch automatisches Öffnen bei Überschreitung des Ansprechdrucks",
        [
            {"id": "KOMP-017-F1-A1", "parameter": "Ansprechdruck", "sollwert": "6 bar (= Design-Druck Reaktor)"},
            {"id": "KOMP-017-F1-A2", "parameter": "Abblasmenge", "sollwert": "1500 kg/h bei Volllast"},
            {"id": "KOMP-017-F1-A3", "parameter": "Prüfintervall", "sollwert": "1 Jahr (wiederkehrende Prüfung)"},
        ])
    db.insert_function(c17["id"], "KOMP-017-F2", "Nebenfunktion",
        "Leitet abgeblasene Medien sicher zur Fackelanlage ab",
        [
            {"id": "KOMP-017-F2-A1", "parameter": "Abblaseleitung", "sollwert": "DN50, druckfest, zur Fackel geführt"},
        ])
    print(f"  KOMP-017: 2 Funktionen gespeichert")


def run_fehleranalyse(db: FMEAStorage):
    """Schritt 4: Fehleranalyse für alle Funktionen der 3 Komponenten."""
    print("\n=== Schritt 4: Fehleranalyse ===")

    # --- KOMP-001-F1: Reaktionsraum bereitstellen ---
    f1 = db.get_function_by_funktion_id("KOMP-001-F1")

    # FM1: Überdruck
    fm1_id = db.insert_failure_mode(f1["id"], "KOMP-001-F1-FM1",
        "Überdruck im Reaktor über 6 bar (Design-Limit)", "Prozess")
    db.insert_failure_cause(fm1_id, "KOMP-001-F1-FM1-UC1",
        "Unkontrollierte exotherme Reaktion (Runaway) durch zu schnelle Eduktzugabe",
        "Betrieb", "Betrieb",
        "SOP mit maximaler Dosiergeschwindigkeit und Temperatur-Trigger für Dosier-Stopp")
    db.insert_failure_cause(fm1_id, "KOMP-001-F1-FM1-UC2",
        "Unterdimensionierung des Kühlsystems für worst-case Exothermie-Szenario",
        "Design", "Detaildesign",
        "Wärmebilanz mit adiabatischem Temperaturanstieg und Sicherheitsfaktor 1.5")
    db.insert_failure_cause(fm1_id, "KOMP-001-F1-FM1-UC3",
        "Versagen des Kühlwasserkreislaufs (Pumpenausfall oder Ventilblockade)",
        "Wartung", "Wartung",
        "Redundante Kühlwasserpumpe und jährliche Funktionsprüfung der Kühlwasserventile")
    db.insert_failure_effect(fm1_id,
        mensch_stufe="Schwere Verletzung",
        mensch_beschreibung="Verätzungsgefahr durch austretende heiße Essigsäure/Ethanol-Dämpfe bei Bersten",
        umwelt_stufe="Betriebsbereich",
        umwelt_beschreibung="Medien werden im Auffangraum aufgefangen, keine externe Kontamination erwartet",
        anlage_stufe="Totalausfall",
        anlage_beschreibung="Stillstand 2-4 Wochen für Behältertausch oder -reparatur und Neuabnahme durch Behörde",
        kosten_stufe="Bis 500.000 €",
        kosten_beschreibung="Behältertausch 185.000 €, Chargenverlust, Reinigung, behördliche Neuabnahme")
    db.insert_current_control(fm1_id, "PIC-402", "Sensor", "B", "SIL-1",
        "Drucktransmitter mit PID-Regelung, Messbereich -1 bis 8 bar, Genauigkeit ±0.1 bar", "D")
    db.insert_current_control(fm1_id, "PSV-410", "Sicherheitsventil", "E", None,
        "Sicherheitsventil Ansprechdruck 6 bar, DN50, 1500 kg/h, Abblaseleitung zur Fackel", "O")
    db.insert_current_control(fm1_id, "BSV-411", "Sicherheitsventil", "E", None,
        "Berstscheibe 6.5 bar, DN50, Hastelloy C276, redundant zu PSV-410", "O")
    db.insert_risk_assessment(fm1_id, S=8, O=3, D=2,
        begruendung_S="S=8 aus Dimension 'Mensch': Chemische Verbrühungsgefahr durch heiße Essigsäure-/Ethanol-Dämpfe bei Versagen der sekundären Barrieren",
        begruendung_O="O=3: Dreifache Absicherung (PID-Regelung + PSV-410 + BSV-411) und SIL-1 Temperaturverriegelung minimieren Eintrittswahrscheinlichkeit",
        begruendung_D="D=2: PIC-402 (SIL-1) löst bei Druckanstieg Alarm aus; PSV-410 begrenzt mechanisch bei 6 bar; zusätzlich BSV-411 als letzte Barriere")
    print(f"  KOMP-001-F1-FM1: Überdruck (3 Ursachen, 3 Controls)")

    # FM2: Temperaturabweichung
    fm2_id = db.insert_failure_mode(f1["id"], "KOMP-001-F1-FM2",
        "Reaktionstemperatur übersteigt 100 °C (oberer Betriebsgrenzwert)", "Thermisch")
    db.insert_failure_cause(fm2_id, "KOMP-001-F1-FM2-UC1",
        "Defektes Regelventil am Dampfmantel HM-101 bleibt in Offenstellung",
        "Wartung", "Wartung",
        "Stellungsrückmeldung mit Alarmierung bei Diskrepanz und jährliche Ventilprüfung")
    db.insert_failure_cause(fm2_id, "KOMP-001-F1-FM2-UC2",
        "Kalibrierabweichung des Temperaturfühlers TIC-401 zeigt zu niedrigen Wert an",
        "Wartung", "Wartung",
        "Halbjährliche Kalibrierung mit Referenztemperatur und Vergleich TI-401a/b")
    db.insert_failure_cause(fm2_id, "KOMP-001-F1-FM2-UC3",
        "Fehlende Temperaturverriegelung im DCS bei manueller Dampffreigabe",
        "Design", "Detaildesign",
        "Implementierung einer unabhängigen TSHH-Verriegelung über SIS (S7-400F)")
    db.insert_failure_effect(fm2_id,
        mensch_stufe="Leichte Verletzung",
        mensch_beschreibung="Verbrühungsgefahr bei Berührung heißer Oberflächen (Rohrleitungen, Stutzen)",
        umwelt_stufe="Keine",
        umwelt_beschreibung="Keine Umweltauswirkung bei geschlossenem System",
        anlage_stufe="Teilausfall",
        anlage_beschreibung="Chargenabbruch, Produkt außerhalb Spezifikation, Reinigung erforderlich",
        kosten_stufe="Bis 50.000 €",
        kosten_beschreibung="Chargenverlust ca. 15.000 €, Reinigung 5.000 €, Produktionsausfall 30.000 €")
    db.insert_current_control(fm2_id, "TIC-401", "Sensor", "B", "SIL-1",
        "Temperaturfühler mit PID-Regelung, -30 bis 180 °C, ±0.5 °C, T90 < 5 s", "D")
    db.insert_current_control(fm2_id, "TI-401a", "Sensor", "B", None,
        "Unabhängiger Temperaturfühler Mantel Eingang, 0-200 °C, Vergleichsmessung", "D")
    db.insert_risk_assessment(fm2_id, S=6, O=4, D=3,
        begruendung_S="S=6 aus Dimension 'Anlage': Chargenabbruch mit Produktverlust, aber kein struktureller Anlagenschaden",
        begruendung_O="O=4: Einzelne Temperaturregelschleife ohne unabhängige Verriegelung; Ventilklemmgefahr bei Dampf-Kondensat",
        begruendung_D="D=3: TIC-401 erkennt Abweichung, aber keine automatische Abschaltung bei Überschreitung; manuelle Intervention erforderlich")
    print(f"  KOMP-001-F1-FM2: Übertemperatur (3 Ursachen, 2 Controls)")

    # FM3: Überfüllung
    fm3_id = db.insert_failure_mode(f1["id"], "KOMP-001-F1-FM3",
        "Füllstand übersteigt 400 L (max. Füllvolumen), Risiko der Überfüllung bis 480 L (LSHH)", "Prozess")
    db.insert_failure_cause(fm3_id, "KOMP-001-F1-FM3-UC1",
        "Fehlerhafte Chargenkalkulation im Rezept führt zu zu großer Eduktemenge",
        "Betrieb", "Betrieb",
        "Automatische Volumenberechnung im DCS mit Plausibilitätsprüfung gegen Rezeptdatenbank")
    db.insert_failure_cause(fm3_id, "KOMP-001-F1-FM3-UC2",
        "Radar-Füllstandsmessung LIC-403 liefert Fehlwert durch Schaumbildung auf der Oberfläche",
        "Design", "Detaildesign",
        "Geführtes Radar (TDR) statt Freistrahl-Radar bei schäumenden Medien oder Ultraschall als Backup")
    db.insert_failure_cause(fm3_id, "KOMP-001-F1-FM3-UC3",
        "Versagen des Dosier-Stopp-Befehls durch Kommunikationsausfall zwischen DCS und Dosierpumpen",
        "Design", "Detaildesign",
        "Hardwired Emergency Stop unabhängig vom Feldbussystem")
    db.insert_failure_effect(fm3_id,
        mensch_stufe="Leichte Verletzung",
        mensch_beschreibung="Medienaustritt durch Überlaufstutzen in Auffangwanne, geringe direkte Personengefährdung",
        umwelt_stufe="Betriebsbereich",
        umwelt_beschreibung="Ethanol/Essigsäure in Auffangwanne, WGK 1, keine externe Kontamination",
        anlage_stufe="Teilausfall",
        anlage_beschreibung="Chargenabbruch, Reinigung des Auffangraums, ca. 1-2 Tage Stillstand",
        kosten_stufe="Bis 30.000 €",
        kosten_beschreibung="Chargenverlust 15.000 €, Reinigung 5.000 €, Entsorgung kontaminierter Flüssigkeit")
    db.insert_current_control(fm3_id, "LIC-403", "Sensor", "B", "SIL-1",
        "Radar-Füllstandssensor, 0-500 L, PID-Regelung, ±1%", "D")
    db.insert_current_control(fm3_id, "LSHH-403", "Verriegelung", "A", "SIL-2",
        "Vibrations-Grenzschalter bei 480 L, unabhängig von LIC-403, Überfüllsicherung", "O")
    db.insert_risk_assessment(fm3_id, S=5, O=2, D=2,
        begruendung_S="S=5 aus Dimension 'Anlage': Chargenabbruch und Reinigung, aber kein struktureller Schaden und geringe Personengefährdung",
        begruendung_O="O=2: SIL-2 Überfüllsicherung LSHH-403 als unabhängige Barriere vor Überlauf, hohe Zuverlässigkeit",
        begruendung_D="D=2: Zwei unabhängige Messsysteme (LIC-403 Radar + LSHH-403 Vibration) erkennen Überfüllung")
    print(f"  KOMP-001-F1-FM3: Überfüllung (3 Ursachen, 2 Controls)")

    # --- KOMP-013-F1: Druckmessung ---
    f13 = db.get_function_by_funktion_id("KOMP-013-F1")
    fm4_id = db.insert_failure_mode(f13["id"], "KOMP-013-F1-FM1",
        "Eingefrorener Messwert: PIC-402 zeigt konstanten Druck obwohl Prozessdruck steigt", "MSR")
    db.insert_failure_cause(fm4_id, "KOMP-013-F1-FM1-UC1",
        "Verstopfte Impulsleitung durch Produktablagerung oder Kondensatansammlung",
        "Wartung", "Wartung",
        "Monatliche Impulsleitungsspülung und jährliche Demontage-Inspektion")
    db.insert_failure_cause(fm4_id, "KOMP-013-F1-FM1-UC2",
        "Membranbruch im Drucktransmitter durch Korrosion (Essigsäure-Exposition)",
        "Design", "Detaildesign",
        "Hastelloy-Membran statt Edelstahl bei Essigsäure-Exposition, oder Membranschutz")
    db.insert_failure_cause(fm4_id, "KOMP-013-F1-FM1-UC3",
        "Elektronikausfall durch EMV-Störung oder Feuchteeintritt trotz IP65",
        "Fertigung", "Inbetriebnahme",
        "EMV-Test bei Inbetriebnahme, Kabelverlegung getrennt von Leistungskabeln, jährlicher IP-Test")
    db.insert_failure_effect(fm4_id,
        mensch_stufe="Schwere Verletzung",
        mensch_beschreibung="Unerkannter Druckanstieg kann zu Bersten führen (sekundäre Folge via FM1)",
        umwelt_stufe="Betriebsbereich",
        umwelt_beschreibung="Indirekte Folge: Bei Bersten Medienaustritt im Auffangraum",
        anlage_stufe="Totalausfall",
        anlage_beschreibung="Druckregelung blind, PSV-410/BSV-411 als letzte Barriere, potentiell Anlagenstillstand",
        kosten_stufe="Bis 500.000 €",
        kosten_beschreibung="Sekundärfolge: Bei Versagen aller Barrieren wie bei FM1")
    db.insert_current_control(fm4_id, "TIC-401", "Sensor", "B", "SIL-1",
        "Temperaturfühler zeigt indirekt Druckanstieg (steigende Temperatur korreliert mit Druck)", "D")
    db.insert_current_control(fm4_id, "PSV-410", "Sicherheitsventil", "E", None,
        "Mechanische Druckbegrenzung bei 6 bar unabhängig von Elektronik", "O")
    db.insert_risk_assessment(fm4_id, S=8, O=4, D=4,
        begruendung_S="S=8 aus Dimension 'Mensch': Frozen Value führt zu blindem Regler, Druckanstieg unerkannt, sekundäres Berst-Risiko",
        begruendung_O="O=4: Impulsleitungsverstopfung bei Batch-Betrieb mit Essigsäure bekanntes Problem; kein redundanter Transmitter",
        begruendung_D="D=4: Kein automatischer Plausibilitätscheck im DCS; Erkennung nur durch manuelle Beobachtung oder indirekt über Temperatur")
    print(f"  KOMP-013-F1-FM1: Frozen Value (3 Ursachen, 2 Controls)")

    # --- KOMP-017-F1: PSV Druckbegrenzung ---
    f17 = db.get_function_by_funktion_id("KOMP-017-F1")
    fm5_id = db.insert_failure_mode(f17["id"], "KOMP-017-F1-FM1",
        "PSV-410 öffnet nicht bei Erreichen des Ansprechdrucks von 6 bar (Fail-to-open)", "Sicherheit")
    db.insert_failure_cause(fm5_id, "KOMP-017-F1-FM1-UC1",
        "Korrosionsprodukte (Essigsäure-bedingt) blockieren den Ventilsitz",
        "Wartung", "Wartung",
        "Jährliche Demontage-Prüfung mit Sitzinspektion und Funktionstest am Prüfstand")
    db.insert_failure_cause(fm5_id, "KOMP-017-F1-FM1-UC2",
        "Falsche Federspannung nach letzter Wartung (Prüfstand-Einstellfehler)",
        "Wartung", "Wartung",
        "Vier-Augen-Prinzip bei Einstellung, dokumentierter Funktionstest vor Wiedereinbau")
    db.insert_failure_cause(fm5_id, "KOMP-017-F1-FM1-UC3",
        "Polymerisation/Verklebung der Sitzfläche durch Produktreste im Ventilkörper",
        "Design", "Detaildesign",
        "Schutzkappe oder Spülanschluss am PSV, oder Wahl eines PSV mit offener Bauform")
    db.insert_failure_effect(fm5_id,
        mensch_stufe="Lebensgefahr",
        mensch_beschreibung="Unkontrollierter Druckaufbau bis Berstscheibe (6.5 bar), bei deren Versagen Bersten des Reaktors",
        umwelt_stufe="Standortgrenze",
        umwelt_beschreibung="Bei Totalversagen: Austritt von Ethanol/Essigsäure mit Brand-/Explosionsgefahr (Ethylacetat Fp -4°C)",
        anlage_stufe="Totalausfall",
        anlage_beschreibung="Zerstörung des Reaktors, Kontamination des Reaktorraums, monatelanger Stillstand",
        kosten_stufe="Über 1.000.000 €",
        kosten_beschreibung="Reaktorersatz 185.000 €, Gebäudeschäden, Umweltsanierung, behördliche Auflagen, Betriebsunterbrechung")
    db.insert_current_control(fm5_id, "BSV-411", "Sicherheitsventil", "E", None,
        "Berstscheibe 6.5 bar als redundante letzte Barriere hinter PSV-410", "O")
    db.insert_current_control(fm5_id, "PIC-402", "Sensor", "B", "SIL-1",
        "Drucktransmitter erkennt Druckanstieg über 6 bar und alarmiert Bediener", "D")
    db.insert_risk_assessment(fm5_id, S=10, O=3, D=3,
        begruendung_S="S=10 aus Dimension 'Mensch': Lebensgefahr durch Bersten unter Druck mit brennbaren/ätzenden Medien in Ex-Zone 1",
        begruendung_O="O=3: Jährliche Prüfung gemäß BetrSichV, aber korrosive Medien erhöhen Ausfallwahrscheinlichkeit zwischen Prüfungen",
        begruendung_D="D=3: BSV-411 als passive Backup-Barriere und PIC-402 mit Alarm, aber Erkennung erst bei Drucküberschreitung")
    print(f"  KOMP-017-F1-FM1: PSV Fail-to-open (3 Ursachen, 2 Controls)")


def run_rpz_berechnung(db: FMEAStorage):
    """Schritt 5: RPZ-Berechnung mit Safety Guard."""
    print("\n=== Schritt 5: RPZ-Berechnung ===")
    stats = calculate_and_store_rpz(PROJECT_ID, db.db_path)
    print(f"  Fehlermodi berechnet: {stats['total']}")
    print(f"  Safety-Overrides: {stats['overrides_applied']}")
    print(f"  Verteilung: {stats['rpz_distribution']}")


def run_massnahmen(db: FMEAStorage):
    """Schritt 6: Maßnahmen für Fehlermodi mit RPZ >= 100."""
    print("\n=== Schritt 6: Maßnahmenoptimierung ===")

    high_risk = db.get_all_failure_modes_with_rpz(PROJECT_ID, min_rpz=100)
    print(f"  Fehlermodi mit RPZ >= 100: {len(high_risk)}")

    for fm in high_risk:
        print(f"  → {fm['fehler_id']}: RPZ={fm['rpz']} ({fm['rpz_status']})")

    # Maßnahme für KOMP-013-F1-FM1 (Frozen Value, RPZ=128)
    fm_frozen = db.get_failure_mode_by_fehler_id("KOMP-013-F1-FM1")
    if fm_frozen:
        db.insert_measure(fm_frozen["id"],
            name="Redundanter Drucktransmitter PIC-402b mit Plausibilitätsüberwachung",
            abe_kategorie="B",
            beschreibung="Installation eines zweiten Drucktransmitters (diverse Redundanz: anderer Hersteller/Messprinzip) mit automatischem Plausibilitätsvergleich im DCS. Bei Abweichung >0.3 bar Alarm und Umschaltung auf gültigen Wert. SIL-1 1oo2-Auswertung.",
            ziel="D",
            S_neu=8, O_neu=4, D_neu=2,
            begruendung="D sinkt von 4 auf 2: Redundanter Transmitter mit automatischem Plausibilitätscheck erkennt Frozen Value sofort durch Vergleich beider Messwerte. 1oo2-Auswertung gewährleistet Verfügbarkeit.")
        print(f"    Maßnahme für KOMP-013-F1-FM1: RPZ 128 → 64")

    # Maßnahme für KOMP-017-F1-FM1 (PSV Fail-to-open, RPZ hoch nach Override)
    fm_psv = db.get_failure_mode_by_fehler_id("KOMP-017-F1-FM1")
    if fm_psv:
        db.insert_measure(fm_psv["id"],
            name="Halbjährliche PSV-Funktionsprüfung mit Online-Diagnosesystem",
            abe_kategorie="A",
            beschreibung="Verkürzung des Prüfintervalls von 12 auf 6 Monate. Installation eines akustischen Emissionsmonitors (AE-Sensor) am PSV-Gehäuse zur kontinuierlichen Zustandsüberwachung. Erkennt Anlaufen, Leckage und Verklebung in Echtzeit.",
            ziel="O",
            S_neu=10, O_neu=2, D_neu=3,
            begruendung="O sinkt von 3 auf 2: Halbiertes Prüfintervall reduziert die Expositionszeit. AE-Monitoring erkennt mechanische Veränderungen (Korrosion, Verklebung) zwischen den Prüfungen und ermöglicht zustandsbasierte Wartung.")
        print(f"    Maßnahme für KOMP-017-F1-FM1: RPZ 90 → 60")

    # Maßnahme für KOMP-001-F1-FM2 (Übertemperatur)
    fm_temp = db.get_failure_mode_by_fehler_id("KOMP-001-F1-FM2")
    if fm_temp:
        ra = db.get_risk_assessment(fm_temp["id"])
        if ra and ra["rpz"] >= 100:
            db.insert_measure(fm_temp["id"],
                name="Unabhängige TSHH-Verriegelung über SIS mit automatischer Dampfabschaltung",
                abe_kategorie="A",
                beschreibung="SIL-2 Temperaturverriegelung über SIS (S7-400F), unabhängig vom DCS. TSHH bei 95 °C schließt Dampf-Regelventil und öffnet Notkühlkreislauf (Sole -10°C). Eigener Temperaturfühler, nicht TIC-401.",
                ziel="O",
                S_neu=6, O_neu=2, D_neu=3,
                begruendung="O sinkt von 4 auf 2: Unabhängige SIL-2 Verriegelung eliminiert Einzelfehler-Pfad. Automatische Abschaltung statt manueller Intervention. Eigener Temperaturfühler eliminiert Common-Cause mit TIC-401.")
            print(f"    Maßnahme für KOMP-001-F1-FM2: RPZ {ra['rpz']} → 36")


def run_export(db: FMEAStorage):
    """Schritt 7: Export."""
    print("\n=== Schritt 7: Export ===")
    from tools.export import export_fmea
    result = export_fmea(PROJECT_ID, ".tmp/fmea_ethylacetat_poc", db.db_path)
    for fmt, path in result.items():
        print(f"  {fmt}: {path}")


def main():
    print("=" * 60)
    print("FMEA Proof of Concept -- Ethylacetat-Anlage 20TA41")
    print("=" * 60)

    db = FMEAStorage()

    run_funktionsanalyse(db)
    run_fehleranalyse(db)
    run_rpz_berechnung(db)
    run_massnahmen(db)
    run_export(db)

    print("\n" + "=" * 60)
    stats = db.get_project_statistics(PROJECT_ID)
    print(f"ZUSAMMENFASSUNG:")
    print(f"  Komponenten: {stats['components']}")
    print(f"  Funktionen: {stats['functions']}")
    print(f"  Fehlermodi: {stats['failure_modes']}")
    print(f"  Maßnahmen: {stats['measures']}")
    print(f"  RPZ-Verteilung: {stats['rpz_distribution']}")
    print("=" * 60)

    db.close()


if __name__ == "__main__":
    main()
