"""
Structure Analysis -- Decompose plant data into individual components with IDs.

Mirrors the n8n "Structure Analysis" node logic:
  Plant → Systems → Equipment / MSR / Safety → Individual components with KOMP-IDs

Usage:
    from tools.structure_analysis import analyze_structure
    components = analyze_structure(plant_data)
"""

import json
import re
import sys
from pathlib import Path


def _infer_component_type(name: str, type_str: str, parameters: dict = None) -> str:
    """Determine component type from name, type string, and parameters."""
    combined = f"{name} {type_str or ''}".upper()

    if re.search(r'SICHERHEIT|PSV|BSV|BERST|UEBERDRUCK|NOTAUS|NOT-AUS|ALARM|AUFFANG', combined):
        return 'sicherheit'
    if re.search(r'STICKSTOFF|VAKUUM|NETZ|VERSORGUNG|MEDIEN|DRUCKLUFT', combined):
        return 'prozess'
    if re.search(r'DOSIER|MEMBRAN', combined):
        return 'dosierung'
    if re.search(r'PUMPE|VERDICHTER|TURBINE|GETRIEBE|LAGER|WELLE|KUPPLUNG|RUEHRER|RUEHRWERK|RÜHRWERK', combined):
        return 'mechanisch'
    if re.search(r'HEIZ|KUEHL|KÜHL|WAERME|WÄRME|KONDENSATOR|MANTEL|DAMPF|NOTKUEHL|NOTKÜHL|SOLE', combined):
        return 'thermisch'
    if re.search(r'REAKTOR|TANK|BEHAELTER|BEHÄLTER|VORLAGE|KOLONNE|DESTILLAT|FILTER', combined):
        return 'prozess'
    if re.search(r'SENSOR|TRANSMITTER|MESSUMFORMER|SCHALTER|RELAIS|TIC|PIC|LIC|FIC|SIC|'
                 r'TEMPERATUR|DRUCK|FUELLSTAND|FÜLLSTAND|DURCHFLUSS|ANZEIGE|REGLER', combined):
        return 'elektrisch'

    return 'sonstige'


def _build_system_context(system: dict, substance_details: dict) -> dict:
    """Build the lean context object for a system (passed to all sub-components)."""
    substance_names = []
    subs = system.get("substances", {})
    for cat in ["feedstocks", "products", "intermediates", "unassigned"]:
        substance_names.extend(subs.get(cat, []))

    active_substances = []
    for name in substance_names:
        active_substances.append({
            "name": name,
            "details": substance_details.get(name, "Keine Details verfügbar")
        })

    return {
        "description": system.get("description", ""),
        "process_conditions": system.get("processConditions", {}),
        "design_limits": system.get("designData", []),
        "active_substances": active_substances,
        "safety_features": system.get("securityFeatures", []),
        "available_sensors": system.get("msrEquipment", []),
        "substance_process_conditions": system.get("substanceProcessConditions", {}),
    }


def analyze_structure(plant_data: dict) -> list:
    """
    Decompose plant data into a flat list of components.

    Returns list of dicts, each with:
      komp_id, name, beschreibung, typ, kategorie, system_name,
      parameters, lean_context
    """
    substance_details = {}
    for cat in ["feedstocks", "products", "byproducts", "media"]:
        for item in plant_data.get(cat, []):
            substance_details[item["name"]] = {
                "properties": item.get("properties", ""),
                "params": item.get("parameters", {})
            }

    results = []
    counter = 1

    for system in plant_data.get("systems", []):
        sys_context = _build_system_context(system, substance_details)

        sys_typ = _infer_component_type(system["name"], system.get("type", ""), system.get("parameters"))
        if sys_typ == 'sonstige':
            sys_typ = 'prozess'

        results.append({
            "komp_id": f"KOMP-{counter:03d}",
            "name": system["name"],
            "beschreibung": system.get("description", ""),
            "typ": sys_typ,
            "kategorie": "system",
            "system_name": system["name"],
            "parameters": system.get("parameters", {}),
            "lean_context": sys_context,
        })
        counter += 1

        sub_groups = [
            ("equipment", "equipment"),
            ("msrEquipment", "msr"),
            ("securityFeatures", "sicherheit"),
        ]

        for key, cat in sub_groups:
            for sub_item in system.get(key, []):
                typ = _infer_component_type(
                    sub_item.get("name", ""),
                    sub_item.get("type", ""),
                    sub_item.get("parameters")
                )
                if cat == "msr" and typ == "sonstige":
                    typ = "elektrisch"
                if cat == "sicherheit":
                    typ = "sicherheit"

                results.append({
                    "komp_id": f"KOMP-{counter:03d}",
                    "name": sub_item.get("name", "UNNAMED"),
                    "beschreibung": sub_item.get("type", ""),
                    "typ": typ,
                    "kategorie": cat,
                    "system_name": system["name"],
                    "parameters": sub_item.get("parameters", {}),
                    "lean_context": sys_context,
                })
                counter += 1

    return results


def save_components_to_db(components: list, project_id: int, db_path: str = None):
    """Save analyzed components to the FMEA database."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.storage import FMEAStorage

    db = FMEAStorage(db_path)
    saved = 0
    for comp in components:
        db.insert_component(
            project_id=project_id,
            komp_id=comp["komp_id"],
            name=comp["name"],
            typ=comp["typ"],
            kategorie=comp["kategorie"],
            system_name=comp["system_name"],
            beschreibung=comp["beschreibung"],
            parameters=comp["parameters"],
            kontext=comp["lean_context"],
        )
        saved += 1
    db.close()
    return saved


if __name__ == "__main__":
    from load_plant_data import load_plant_data

    if len(sys.argv) < 2:
        print("Usage: python tools/structure_analysis.py <path_to_json>")
        sys.exit(1)

    data = load_plant_data(sys.argv[1])
    components = analyze_structure(data)

    type_counts = {}
    cat_counts = {}
    for c in components:
        type_counts[c["typ"]] = type_counts.get(c["typ"], 0) + 1
        cat_counts[c["kategorie"]] = cat_counts.get(c["kategorie"], 0) + 1

    print(f"\n=== Strukturanalyse: {len(components)} Komponenten ===")
    print(f"\nNach Typ:")
    for t, n in sorted(type_counts.items()):
        print(f"  {t}: {n}")
    print(f"\nNach Kategorie:")
    for c, n in sorted(cat_counts.items()):
        print(f"  {c}: {n}")
    print(f"\nKomponenten-Liste:")
    for c in components:
        print(f"  {c['komp_id']} | {c['typ']:12s} | {c['kategorie']:10s} | {c['system_name']:25s} | {c['name']}")
