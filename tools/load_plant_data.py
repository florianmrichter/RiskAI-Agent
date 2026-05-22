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


def load_plant_data(filepath: str, auto_validate: bool = True) -> dict:
    """Auto-detect file type and load plant data.
    If auto_validate is True, runs validate_plant_data and raises on critical errors."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if "nodes" in raw and "connections" in raw:
        data = load_from_n8n_workflow(filepath)
    else:
        data = load_from_json_file(filepath)

    if auto_validate:
        warnings = validate_plant_data(data)
        critical = [w for w in warnings if w.startswith("CRITICAL")]
        if critical:
            raise ValueError(f"Plant data validation failed: {'; '.join(critical)}")

    return data


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

    for i, system in enumerate(systems):
        prefix = f"systems[{i}] '{system.get('name', 'UNNAMED')}'"
        if "name" not in system:
            warnings.append(f"FEHLER: {prefix} hat keinen Namen")
        if "equipment" not in system and "msrEquipment" not in system:
            warnings.append(f"WARNUNG: {prefix} hat weder Equipment noch MSR-Equipment")
        if "processConditions" not in system:
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


def update_plant_data(task_folder: str, path: str, value) -> bool:
    """
    Write a single value into anlagendaten.json using a dot-path or bracket-path notation.

    Examples:
        update_plant_data("Risikoanalyse/MyPlant", "systems[0].equipment[2].designPressure", "4.5 bar")
        update_plant_data("Risikoanalyse/MyPlant", "betriebserfahrungen", [])

    Returns True on success, False if file not found.
    """
    import re as _re
    from pathlib import Path as _Path

    tasks_root = _Path(__file__).parent.parent / "tasks"
    json_path = tasks_root / task_folder / "anlagendaten.json"
    if not json_path.exists():
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize: unwrap single-element list
    _wrapped = isinstance(data, list) and len(data) == 1
    obj = data[0] if _wrapped else data

    # Walk the path and set the value
    parts = _re.split(r"\.|\[(\d+)\]", path)
    parts = [p for p in parts if p is not None and p != ""]

    node = obj
    for i, part in enumerate(parts[:-1]):
        if part.isdigit():
            node = node[int(part)]
        else:
            if part not in node:
                node[part] = {}
            node = node[part]

    last = parts[-1]
    if last.isdigit():
        node[int(last)] = value
    else:
        node[last] = value

    out = [obj] if _wrapped else obj
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    return True


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
