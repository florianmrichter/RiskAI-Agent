"""
Equipment Reliability Lookup -- Query failure rates and typical failure modes.

Provides O-value guidance based on published equipment reliability data
(CCPS Guidelines, IEC 61511, IEEE Std 493, public OREDA summaries).

Usage:
    from tools.reliability_lookup import ReliabilityDB, suggest_for_component, get_o_suggestion
    rdb = ReliabilityDB()
    info = rdb.get_equipment_info("kreiselpumpe")
    o_value = rdb.suggest_o_value(failure_rate_fpmh=50)

    # Smart-Matching: Komponente → Equipment-Typ
    match = suggest_for_component("Glasreaktor R-20TA43", "prozess", "Büchi miniPilot 15L")
    # → {"equipment_type": "glasreaktor", "confidence": "hoch", ...}

    # Helper: komp_id → alle O-Richtwerte
    suggestion = get_o_suggestion("KOMP-001", project_id=4)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_FILE = Path(__file__).parent.parent / "config" / "reliability_data.json"


class ReliabilityDB:
    def __init__(self, data_path: str = None):
        path = Path(data_path) if data_path else DATA_FILE
        with open(path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._index = self._build_index()

    def _build_index(self) -> dict:
        """Build a flat lookup index: equipment_type -> data."""
        index = {}
        for cat_key, cat in self._data.get("equipment_categories", {}).items():
            for typ_key, typ_data in cat.get("typen", {}).items():
                entry = {
                    "kategorie": cat_key,
                    "kategorie_beschreibung": cat.get("beschreibung", ""),
                    "typ": typ_key,
                    **typ_data,
                }
                index[typ_key] = entry
                index[typ_key.lower().replace("_", " ")] = entry
        return index

    def list_categories(self) -> list:
        """List all equipment categories with their types."""
        result = []
        for cat_key, cat in self._data.get("equipment_categories", {}).items():
            typen = list(cat.get("typen", {}).keys())
            result.append({
                "kategorie": cat_key,
                "beschreibung": cat.get("beschreibung", ""),
                "typen": typen,
            })
        return result

    def list_equipment_types(self) -> list:
        """List all available equipment types."""
        return sorted(self._index.keys())

    def get_equipment_info(self, equipment_type: str) -> dict:
        """
        Get reliability data for a specific equipment type.

        Args:
            equipment_type: e.g. "kreiselpumpe", "drucktransmitter", "sicherheitsventil_psv"

        Returns:
            Dict with failure_rate, mtbf_hours, typische_fehlermodi, etc.
            None if not found.
        """
        key = equipment_type.lower().replace(" ", "_")
        return self._index.get(key) or self._index.get(equipment_type)

    def get_failure_modes(self, equipment_type: str) -> list:
        """Get typical failure modes with O-value suggestions for an equipment type."""
        info = self.get_equipment_info(equipment_type)
        if not info:
            return []
        return info.get("typische_fehlermodi", [])

    def suggest_o_value(self, failure_rate_fpmh: float = None, equipment_type: str = None,
                        failure_mode: str = None) -> dict:
        """
        Suggest an O-value based on failure rate or equipment/failure mode.

        Priority:
        1. If failure_mode + equipment_type given: use the specific O-richtwert
        2. If failure_rate_fpmh given: map via the O-scale
        3. If equipment_type given: use the overall failure rate

        Returns:
            Dict with o_wert, begruendung, and quelle.
        """
        o_scale = self._data.get("o_skala_zuordnung", {}).get("zuordnung", [])

        if equipment_type and failure_mode:
            modes = self.get_failure_modes(equipment_type)
            for m in modes:
                if failure_mode.lower() in m["modus"].lower():
                    return {
                        "o_wert": m["o_richtwert"],
                        "begruendung": (
                            f"Typischer O-Wert fuer '{m['modus']}' bei "
                            f"{equipment_type}: {m['anteil_prozent']}% aller Ausfaelle"
                        ),
                        "quelle": "Reliability Reference DB (CCPS/IEEE/OREDA-basiert)",
                    }

        if failure_rate_fpmh is None and equipment_type:
            info = self.get_equipment_info(equipment_type)
            if info:
                failure_rate_fpmh = info.get("failure_rate")

        if failure_rate_fpmh is not None:
            for entry in o_scale:
                if "fpmh_bis" in entry and failure_rate_fpmh <= entry["fpmh_bis"]:
                    return {
                        "o_wert": entry["o_wert"],
                        "begruendung": (
                            f"Ausfallrate {failure_rate_fpmh} FPMH entspricht "
                            f"O={entry['o_wert']} ({entry['beschreibung']})"
                        ),
                        "quelle": "O-Skala-Zuordnung nach AIAG-VDA",
                    }
                if "fpmh_ab" in entry and failure_rate_fpmh >= entry["fpmh_ab"]:
                    return {
                        "o_wert": entry["o_wert"],
                        "begruendung": (
                            f"Ausfallrate {failure_rate_fpmh} FPMH entspricht "
                            f"O={entry['o_wert']} ({entry['beschreibung']})"
                        ),
                        "quelle": "O-Skala-Zuordnung nach AIAG-VDA",
                    }

        return {"o_wert": None, "begruendung": "Keine Daten verfuegbar", "quelle": None}

    def get_critical_failure_modes(self, equipment_type: str = None) -> list:
        """Get all failure modes marked as critical (safety-relevant)."""
        results = []
        types_to_check = {}

        if equipment_type:
            info = self.get_equipment_info(equipment_type)
            if info:
                types_to_check = {equipment_type: info}
        else:
            types_to_check = self._index

        seen = set()
        for typ_key, info in types_to_check.items():
            if info.get("typ") in seen:
                continue
            seen.add(info.get("typ"))
            for mode in info.get("typische_fehlermodi", []):
                if mode.get("kritisch"):
                    results.append({
                        "equipment": info.get("typ", typ_key),
                        "kategorie": info.get("kategorie", ""),
                        **mode,
                    })
        return results


# ── Keyword-Mapping: Komponentenname → Equipment-Typ ──

# Jedes Keyword wird gegen Name, Typ und Beschreibung der Komponente geprüft.
# Reihenfolge: spezifischste Keywords zuerst.
COMPONENT_KEYWORDS = [
    # Reaktoren / Behälter
    (["glasreaktor", "glas-reaktor", "borosilikat", "büchi", "buchi"], "glasreaktor"),
    (["rührreaktor", "ruehrreaktor", "rührbehälter", "ruehrbehaelter", "rührkessel"], "ruehrwerksreaktor"),
    (["druckbehälter", "druckbehaelter", "autoklav"], "druckbehaelter"),
    (["lagertank", "vorlagebehälter", "vorlagefass", "pufferbehälter"], "lagertank_atmosphaerisch"),
    # Pumpen
    (["dosierpumpe", "membranpumpe", "dosierung"], "dosierpumpe_membran"),
    (["kolbenpumpe", "kolbendosier"], "dosierpumpe_kolben"),
    (["kreiselpumpe", "zentrifugalpumpe", "pumpe"], "kreiselpumpe"),
    # Ventile
    (["sicherheitsventil", "psv", "überdruckventil"], "sicherheitsventil_psv"),
    (["regelventil", "stellventil", "pneumatisch"], "regelventil_pneumatisch"),
    (["magnetventil", "solenoid"], "magnetventil"),
    (["handventil", "absperrventil", "kugelhahn"], "handventil_absperr"),
    # Wärmetauscher
    (["plattenwärmetauscher", "plattenwaermetauscher"], "plattenwaermetauscher"),
    (["rohrbündel", "rohrbuendel", "wärmetauscher", "waermetauscher", "kondensator", "kühler"], "rohrbuendel"),
    # Doppelmantel / Temperierung
    (["doppelmantel", "heizmantel", "kühlmantel"], "rohrbuendel"),
    (["thermostat", "temperiergerät", "lauda", "huber", "julabo"], "thermostat_extern"),
    (["rückflusskühler", "rueckflusskuehler", "intensivkühler"], "rueckflusskuehler"),
    # MSR
    (["temperatursensor", "pt100", "pt1000", "thermoelement", "tic", "ti-"], "temperatursensor_widerstand"),
    (["drucktransmitter", "drucksensor", "pic", "pi-", "pt-"], "drucktransmitter"),
    (["füllstandsmessung", "füllstandsensor", "radar", "lic", "li-", "lt-"], "fuellstandsmessung_radar"),
    (["durchflussmesser", "coriolis", "fic", "fi-"], "durchflussmesser_coriolis"),
    (["regler", "pid", "sps"], "regler_pid"),
    # Sicherheit
    (["berstscheibe", "bsv"], "berstscheibe"),
    (["gaswarnung", "gaswarn", "gasdetektor"], "gaswarnanlage"),
    (["sis", "sil 2", "sil-2", "not-aus", "nothalt"], "sis_abschaltung_sil2"),
    (["sil 1", "sil-1"], "sis_abschaltung_sil1"),
    # Elektrisch
    (["elektromotor", "motor", "antrieb"], "elektromotor_niederspannung"),
    (["frequenzumrichter", "fu", "vfd"], "frequenzumrichter"),
    # Dichtungen
    (["gleitringdichtung doppelt", "doppelte gleitring"], "gleitringdichtung_doppelt"),
    (["gleitringdichtung", "gleitring", "wellendichtung"], "gleitringdichtung_einfach"),
    # Rohrleitungen
    (["kompensator", "metallbalg"], "kompensator_metallbalg"),
    (["flansch", "flanschverbindung"], "flanschverbindung"),
    (["rohrleitung", "verrohrung", "leitung"], "rohrleitung_edelstahl"),
    # Rührwerk (→ Equipment, nicht Reaktor)
    (["rührwerk", "ruehrwerk", "rührer", "ruehrer", "agitator"], "ruehrwerksreaktor"),
]


def suggest_for_component(name: str, typ: str = "", beschreibung: str = "") -> dict | None:
    """Match a component to the best equipment type from ReliabilityDB.

    Args:
        name: Component name (e.g. "Glasreaktor R-20TA43")
        typ: Component type (e.g. "prozess", "mechanisch")
        beschreibung: Optional description

    Returns:
        Dict with equipment_type, reliability data, and O-richtwerte.
        None if no match found.
    """
    search_text = f"{name} {typ} {beschreibung}".lower()

    for keywords, equipment_type in COMPONENT_KEYWORDS:
        for kw in keywords:
            if kw.lower() in search_text:
                rdb = ReliabilityDB()
                info = rdb.get_equipment_info(equipment_type)
                if info:
                    return {
                        "equipment_type": equipment_type,
                        "matched_keyword": kw,
                        "failure_rate_fpmh": info.get("failure_rate"),
                        "mtbf_hours": info.get("mtbf_hours"),
                        "fehlermodi": info.get("typische_fehlermodi", []),
                        "quelle": "CCPS/OREDA",
                        "daten_konfidenz": "hoch",
                    }
    return None


def get_o_suggestion(komp_id: str, project_id: int, db_path: str | None = None) -> dict:
    """Get O-value suggestions for a component from ReliabilityDB.

    Loads the component from DB, matches it to an equipment type,
    and returns all available O-richtwerte for its failure modes.

    Args:
        komp_id: Component ID (e.g. "KOMP-001")
        project_id: Project ID in database
        db_path: Optional DB path

    Returns:
        Dict with match info, O-richtwerte per failure mode, or "no_match" info.
    """
    from tools.storage import FMEAStorage
    db = FMEAStorage(db_path)
    comp = db.get_component_by_komp_id(komp_id, project_id)
    db.close()

    if not comp:
        return {"status": "error", "message": f"Komponente {komp_id} nicht gefunden"}

    match = suggest_for_component(
        name=comp.get("name", ""),
        typ=comp.get("typ", ""),
        beschreibung=comp.get("beschreibung", ""),
    )

    if not match:
        return {
            "status": "no_match",
            "komp_id": komp_id,
            "komponente": comp.get("name"),
            "message": f"Kein passender Equipment-Typ in ReliabilityDB für '{comp.get('name')}'. O-Wert muss manuell geschätzt werden.",
            "empfehlung_daten_konfidenz": "mittel",
            "empfehlung_daten_quelle": "Betriebserfahrung",
        }

    # Build per-failure-mode O suggestions
    o_richtwerte = []
    for fm in match.get("fehlermodi", []):
        o_richtwerte.append({
            "fehlermodus": fm["modus"],
            "o_richtwert": fm["o_richtwert"],
            "anteil_prozent": fm.get("anteil_prozent"),
            "kritisch": fm.get("kritisch", False),
        })

    return {
        "status": "match",
        "komp_id": komp_id,
        "komponente": comp.get("name"),
        "equipment_type": match["equipment_type"],
        "matched_keyword": match["matched_keyword"],
        "failure_rate_fpmh": match["failure_rate_fpmh"],
        "mtbf_hours": match["mtbf_hours"],
        "o_richtwerte": o_richtwerte,
        "empfehlung_daten_konfidenz": "hoch",
        "empfehlung_daten_quelle": "CCPS/OREDA",
        "hinweis": f"ReliabilityDB-Match: '{comp.get('name')}' → {match['equipment_type']} (Keyword: '{match['matched_keyword']}'). Ausfallrate: {match['failure_rate_fpmh']} FPMH.",
    }


if __name__ == "__main__":
    rdb = ReliabilityDB()

    print("=== Kategorien ===")
    for cat in rdb.list_categories():
        print(f"  {cat['kategorie']}: {', '.join(cat['typen'])}")

    print("\n=== Kreiselpumpe ===")
    info = rdb.get_equipment_info("kreiselpumpe")
    if info:
        print(f"  Failure Rate: {info['failure_rate']} FPMH")
        print(f"  MTBF: {info['mtbf_hours']} h")
        for fm in info.get("typische_fehlermodi", []):
            print(f"    - {fm['modus']} ({fm['anteil_prozent']}%, O~{fm['o_richtwert']})")

    print("\n=== O-Wert-Vorschlag ===")
    suggestion = rdb.suggest_o_value(equipment_type="drucktransmitter", failure_mode="Drift")
    print(f"  {suggestion}")

    print("\n=== Kritische Fehlermodi ===")
    for crit in rdb.get_critical_failure_modes():
        print(f"  [{crit['equipment']}] {crit['modus']} (O~{crit['o_richtwert']})")
