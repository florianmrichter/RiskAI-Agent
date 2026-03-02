#!/usr/bin/env python3
"""
Maßnahmen-Generierung für Fehlermodi mit RPZ >= 100.

Lädt projektspezifische Maßnahmen-Generatoren aus tasks/{task_folder}/measures_explicit.py
oder config/measures_explicit.py. Die geladene Datei muss get_measures_for_fehlermodus(fehler_id, fehlermodus, komponente)
bereitstellen. Folgt workflows/massnahmen.md: STOP-Prinzip (S/T/O/P) und ABE-Hierarchie (A/B/E).

Für neue Projekte: tasks/{task_folder}/measures_explicit.py anlegen mit get_measures_for_fehlermodus.

Usage:
    python tools/generate_measures.py --project-id 1 --task-folder Risikoanalyse/Ethylacetatproduktion_20TA42
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.insert_measures import insert_measures_for_fehlermodus
from tools.fmea_loader import load_measures_module


def _get_measures_module(task_folder: str):
    """Lädt Maßnahmen-Modul aus task_folder, Fallback auf config."""
    mod = load_measures_module(task_folder)
    if mod and hasattr(mod, "get_measures_for_fehlermodus"):
        return mod
    try:
        import config.measures_explicit as config_mod
        return config_mod
    except ImportError:
        return None


def run_generate_measures(project_id: int, task_folder: str = "Risikoanalyse", db_path: str = None) -> dict:
    """
    Generiert und speichert Maßnahmen für alle Fehlermodi mit RPZ >= 100 (oder Status hoch/kritisch).

    Nutzt get_measures_for_fehlermodus aus dem geladenen Maßnahmen-Modul.
    Fehlermodi ohne Generator bleiben für Agent-Analyse.

    Returns:
        {"inserted": n, "skipped": m, "missing": [fehler_ids ohne Generator]}
    """
    mod = _get_measures_module(task_folder)
    if not mod:
        return {"inserted": 0, "skipped": 0, "missing": [], "error": "Kein Maßnahmen-Modul gefunden"}

    get_measures = mod.get_measures_for_fehlermodus

    db = FMEAStorage(db_path)
    high = db.get_failure_modes_needing_measures(project_id)
    inserted_total = 0
    skipped = 0
    missing = []

    for fm in high:
        if db.get_measures(fm["id"]):
            skipped += 1
            continue

        fehler_id = fm["fehler_id"]
        fehlermodus = fm.get("fehlermodus", "")
        komponente = fm.get("komponente", "")

        measures = get_measures(fehler_id, fehlermodus, komponente)

        if not measures:
            missing.append(fehler_id)
            continue

        result = insert_measures_for_fehlermodus(project_id, fehler_id, measures, db_path)
        inserted_total += result["inserted"]
        if result["inserted"] > 0:
            print(f"  {fehler_id}: {result['inserted']} Maßnahmen eingefügt")

    db.close()
    return {"inserted": inserted_total, "skipped": skipped, "missing": missing}


def main():
    import argparse
    from tools.workflow_state import load_state

    ap = argparse.ArgumentParser(description="Maßnahmen für Fehlermodi mit RPZ>=100 generieren")
    ap.add_argument("--project-id", type=int, default=None, help="Projekt-ID (default: aus workflow_state)")
    ap.add_argument("--task-folder", required=True, help="z.B. Risikoanalyse/Ethylacetatproduktion_20TA42")
    ap.add_argument("--db-path", default=None)
    args = ap.parse_args()

    project_id = args.project_id
    if project_id is None:
        state = load_state(args.task_folder)
        if state and state.get("project_id"):
            project_id = state["project_id"]
        else:
            print("Fehler: --project-id erforderlich oder workflow_state.json mit project_id")
            sys.exit(1)

    base = Path(__file__).parent.parent
    db_path = args.db_path or str(base / "data" / "fmea.db")

    print("=" * 60)
    print(f"Maßnahmen-Generierung – Projekt {project_id}")
    print("=" * 60)

    result = run_generate_measures(project_id, args.task_folder, db_path)

    if result.get("error"):
        print(f"Fehler: {result['error']}")
        sys.exit(1)

    print(f"\nEingefügt: {result['inserted']} Maßnahmen")
    if result["skipped"]:
        print(f"Übersprungen (bereits vorhanden): {result['skipped']}")
    if result["missing"]:
        print(f"Ohne Generator (Agent muss analysieren): {result['missing']}")

    print("=" * 60)


if __name__ == "__main__":
    main()
