"""
Load and validate plant data from JSON files or n8n workflow exports.

Supports:
  - Direct JSON plant data files
  - n8n workflow exports (extracts jsCode from "Anlagendaten" node)

Usage:
    python tools/load_plant_data.py <path_to_json>
"""

import json
import re
import sys
from pathlib import Path


def load_from_json_file(filepath: str) -> dict:
    """Load plant data from a plain JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
    return data


def load_from_n8n_workflow(filepath: str) -> dict:
    """Extract plant data from an n8n workflow export JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    nodes = workflow.get("nodes", [])
    anlagendaten_node = None
    for node in nodes:
        if node.get("name") == "Anlagendaten" and node.get("type") == "n8n-nodes-base.code":
            anlagendaten_node = node
            break

    if not anlagendaten_node:
        raise ValueError("No 'Anlagendaten' code node found in n8n workflow")

    js_code = anlagendaten_node["parameters"]["jsCode"]

    match = re.search(r'return\s+(\[[\s\S]*\])\s*;?\s*$', js_code)
    if not match:
        raise ValueError("Could not extract JSON array from jsCode")

    raw_json = match.group(1)
    data = json.loads(raw_json)

    if isinstance(data, list) and len(data) == 1:
        data = data[0]

    return data


def load_plant_data(filepath: str) -> dict:
    """Auto-detect file type and load plant data."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if "nodes" in raw and "connections" in raw:
        return load_from_n8n_workflow(filepath)
    return load_from_json_file(filepath)


def validate_plant_data(data: dict) -> list:
    """Validate plant data structure. Returns list of warnings (empty = OK)."""
    warnings = []

    required_top = ["systems"]
    for field in required_top:
        if field not in data:
            warnings.append(f"FEHLER: Pflichtfeld '{field}' fehlt")

    recommended_top = ["teilanlage_nr", "bezeichnung", "location", "processDescription",
                       "feedstocks", "products"]
    for field in recommended_top:
        if field not in data:
            warnings.append(f"WARNUNG: Empfohlenes Feld '{field}' fehlt")

    systems = data.get("systems", [])
    if not systems:
        warnings.append("FEHLER: Keine Systeme definiert")
        return warnings

    for i, sys in enumerate(systems):
        prefix = f"systems[{i}] '{sys.get('name', 'UNNAMED')}'"
        if "name" not in sys:
            warnings.append(f"FEHLER: {prefix} hat keinen Namen")
        if "equipment" not in sys and "msrEquipment" not in sys:
            warnings.append(f"WARNUNG: {prefix} hat weder Equipment noch MSR-Equipment")
        if "processConditions" not in sys:
            warnings.append(f"WARNUNG: {prefix} hat keine Prozessbedingungen")

    return warnings


def get_plant_summary(data: dict) -> dict:
    """Generate a summary of plant data for quick overview."""
    systems = data.get("systems", [])
    total_equipment = sum(len(s.get("equipment", [])) for s in systems)
    total_msr = sum(len(s.get("msrEquipment", [])) for s in systems)
    total_safety = sum(len(s.get("securityFeatures", [])) for s in systems)

    substances = set()
    for cat in ["feedstocks", "products", "byproducts"]:
        for item in data.get(cat, []):
            substances.add(item.get("name", ""))

    return {
        "anlage": data.get("bezeichnung", "Unbekannt"),
        "teilanlage_nr": data.get("teilanlage_nr", "N/A"),
        "standort": data.get("location", {}).get("site", "N/A"),
        "systeme": len(systems),
        "system_namen": [s.get("name", "") for s in systems],
        "equipment_gesamt": total_equipment,
        "msr_gesamt": total_msr,
        "sicherheit_gesamt": total_safety,
        "stoffe": sorted(substances),
        "medien": [m.get("name", "") for m in data.get("media", [])],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/load_plant_data.py <path_to_json>")
        sys.exit(1)

    filepath = sys.argv[1]
    data = load_plant_data(filepath)
    warnings = validate_plant_data(data)
    summary = get_plant_summary(data)

    print("\n=== Anlagendaten geladen ===")
    print(f"Anlage: {summary['anlage']}")
    print(f"Teilanlage: {summary['teilanlage_nr']}")
    print(f"Standort: {summary['standort']}")
    print(f"Systeme: {summary['systeme']} ({', '.join(summary['system_namen'])})")
    print(f"Equipment: {summary['equipment_gesamt']}")
    print(f"MSR-Stellen: {summary['msr_gesamt']}")
    print(f"Sicherheitseinrichtungen: {summary['sicherheit_gesamt']}")
    print(f"Stoffe: {', '.join(summary['stoffe'])}")
    print(f"Medien: {', '.join(summary['medien'])}")

    if warnings:
        print(f"\n=== {len(warnings)} Validierungshinweise ===")
        for w in warnings:
            print(f"  {w}")
    else:
        print("\nValidierung: OK")
