"""
Equipment Reliability Lookup -- Query failure rates and typical failure modes.

Provides O-value guidance based on published equipment reliability data
(CCPS Guidelines, IEC 61511, IEEE Std 493, public OREDA summaries).

Usage:
    from tools.reliability_lookup import ReliabilityDB
    rdb = ReliabilityDB()
    info = rdb.get_equipment_info("kreiselpumpe")
    o_value = rdb.suggest_o_value(failure_rate_fpmh=50)
"""

import json
from pathlib import Path

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
