#!/usr/bin/env python3
"""
Kompletter Neustart der FMEA-Analyse.

1. Setzt DB zurück (optional, mit --reset)
2. Lädt Anlagendaten
3. Erstellt Projekt mit task_folder
4. Speichert Komponenten
5. Initialisiert workflow_state.json
6. Generiert checklist.md

Usage:
    python tools/init_fmea_fresh.py --task-folder Risikoanalyse/Ethylacetatproduktion_20TA42 [--reset]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.load_plant_data import load_plant_data
from tools.structure_analysis import analyze_structure, save_components_to_db
from tools.storage import FMEAStorage
from tools.workflow_state import init_state_from_structure
from tools.update_checklist import update_checklist


def _write_empty_fmea_explicit(task_dir: Path) -> None:
    """Leere fmea_explicit.py – Agent füllt bei Analyse."""
    path = task_dir / "fmea_explicit.py"
    path.write_text('''"""
Explizite FMEA-Definitionen pro Komponente – Agent-Output.

Der Agent analysiert jede Komponente einzeln und ergänzt diese Datei.
get_fmea_for_component(komp_id) liefert die Definition für insert_fmea_for_component.
"""

def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})

_FMEA = {}
''', encoding="utf-8")


def _write_empty_measures_explicit(task_dir: Path) -> None:
    """Leere measures_explicit.py – get_measures_for_fehlermodus liefert []."""
    path = task_dir / "measures_explicit.py"
    path.write_text('''"""
Explizite Maßnahmen pro Fehlermodus – Agent-Output.

Der Agent analysiert Fehlermodi mit RPZ >= 100 und ergänzt diese Datei
oder ruft insert_measures_for_fehlermodus direkt auf.
generate_measures.py lädt dieses Modul – liefert [] wenn keine Maßnahmen definiert.
"""


def get_measures_for_fehlermodus(fehler_id: str, fehlermodus: str, komponente: str) -> list:
    """
    Liefert explizite Maßnahmen für den Fehlermodus.
    Rückgabe: Liste von Maßnahme-Dicts oder [] wenn keine definiert.
    """
    return []
''', encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="FMEA komplett von vorne starten")
    ap.add_argument("--reset", action="store_true", help="DB löschen und neu anlegen")
    ap.add_argument("--task-folder", required=True, help="z.B. Risikoanalyse/Ethylacetatproduktion_20TA42")
    ap.add_argument("--json", default=None, help="Pfad zu anlagendaten.json (default: tasks/{task_folder}/anlagendaten.json)")
    args = ap.parse_args()

    base = Path(__file__).parent.parent
    json_path = args.json or str(base / "tasks" / args.task_folder / "anlagendaten.json")
    db_path = str(base / "data" / "fmea.db")
    state_path = base / "tasks" / args.task_folder / "workflow_state.json"

    print("=" * 60)
    print("FMEA – Kompletter Neustart")
    print("=" * 60)

    task_dir = base / "tasks" / args.task_folder
    task_dir.mkdir(parents=True, exist_ok=True)

    if args.reset:
        if Path(db_path).exists():
            Path(db_path).unlink()
            print("[Reset] DB gelöscht.")
        if state_path.exists():
            state_path.unlink()
            print("[Reset] workflow_state.json gelöscht.")
        # Leere Config-Stubs (frische Bewertung: keine vordefinierten Analysen)
        _write_empty_fmea_explicit(task_dir)
        _write_empty_measures_explicit(task_dir)
        print("[Reset] fmea_explicit.py und measures_explicit.py auf leere Stubs gesetzt.")
    else:
        # Bei neuem Task-Ordner: leere Stubs anlegen falls nicht vorhanden
        if not (task_dir / "fmea_explicit.py").exists():
            _write_empty_fmea_explicit(task_dir)
            print("[Init] fmea_explicit.py (leer) angelegt.")
        if not (task_dir / "measures_explicit.py").exists():
            _write_empty_measures_explicit(task_dir)
            print("[Init] measures_explicit.py (leer) angelegt.")

    print(f"\n[1] Lade Anlagendaten: {json_path}")
    plant_data = load_plant_data(json_path)
    bezeichnung = plant_data.get("bezeichnung", "FMEA-Projekt")
    teilanlage = plant_data.get("teilanlage_nr", "")

    print(f"    Anlage: {bezeichnung} {teilanlage}")

    print("\n[2] Strukturanalyse...")
    components = analyze_structure(plant_data)
    print(f"    {len(components)} Komponenten erkannt")

    print("\n[3] Projekt anlegen...")
    db = FMEAStorage(db_path)
    project_id = db.create_project(bezeichnung, teilanlage, task_folder=args.task_folder)
    db.close()
    print(f"    Projekt-ID: {project_id}")

    print("\n[4] Komponenten speichern...")
    save_components_to_db(components, project_id, db_path)
    print(f"    {len(components)} Komponenten in DB")

    print("\n[5] Workflow-State initialisieren...")
    komp_ids = [c["komp_id"] for c in components]
    init_state_from_structure(args.task_folder, project_id, komp_ids)
    print(f"    State: tasks/{args.task_folder}/workflow_state.json")

    print("\n[6] Checklist generieren...")
    out = update_checklist(args.task_folder, db_path)
    print(f"    {out}")

    print("\n" + "=" * 60)
    print("Neustart abgeschlossen. Nächster Schritt: FMEA-Analyse pro Komponente.")
    print("Der Agent kann jetzt mit get_next_action() die nächste Komponente ermitteln.")
    print("=" * 60)


if __name__ == "__main__":
    main()
