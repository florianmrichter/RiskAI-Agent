import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.load_plant_data import load_plant_data
from tools.structure_analysis import analyze_structure

def setup_poc():
    db = FMEAStorage()
    
    # 1. Create Project
    # We want ID=1 for poc_run.py compatibility
    # If DB is new, it will be 1.
    project = db.get_project(1)
    if not project:
        print("Creating project...")
        pid = db.create_project("Ethylacetat-Anlage", "20TA41")
        print(f"Project created with ID: {pid}")
    else:
        print(f"Project 1 already exists: {project['name']}")
        pid = 1

    # 2. Load Plant Data
    json_path = Path("tasks/Risikoanalyse/Ethylacetatproduktion_20TA41/anlagendaten.json")
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return

    print("Loading plant data...")
    plant_data = load_plant_data(str(json_path))
    
    # 3. Analyze & Save Components
    print("Analyzing structure...")
    components = analyze_structure(plant_data)
    
    # Check if components already exist to avoid duplicates if run multiple times
    existing = db.get_components(pid)
    if not existing:
        print(f"Saving {len(components)} components to DB...")
        count = 0
        for comp in components:
            db.insert_component(
                project_id=pid,
                komp_id=comp["komp_id"],
                name=comp["name"],
                typ=comp["typ"],
                kategorie=comp["kategorie"],
                system_name=comp["system_name"],
                beschreibung=comp.get("beschreibung"),
                parameters=comp.get("parameters"),
                kontext=comp.get("lean_context"),
            )
            count += 1
        print(f"Saved {count} components.")
    else:
        print(f"Components already exist ({len(existing)} found). Skipping insertion.")

    db.close()

if __name__ == "__main__":
    setup_poc()
