#!/usr/bin/env python3
"""
Löscht alle FMEA-Daten (Funktionen, Fehlermodi, Ursachen, Folgen, Controls, Maßnahmen)
für ein Projekt. Behält die Komponentenstruktur bei.

Verwendung: Reset einer Risikoanalyse, wenn z.B. Archiv-Daten fälschlich übernommen wurden.

Usage:
    python tools/clear_fmea_for_project.py Risikoanalyse/Ethylacetatproduktion_20TA42
    python tools/clear_fmea_for_project.py Risikoanalyse/Ethylacetatproduktion_20TA42 --reset-files
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.workflow_state import load_state, save_state


def clear_fmea_for_project(task_folder: str, db_path: str = None) -> dict:
    """
    Löscht alle FMEA-Daten für alle Komponenten des Projekts.
    Returns: Statistik der gelöschten Einträge.
    """
    db = FMEAStorage(db_path)
    proj = db.get_project_by_task_folder(task_folder)
    if not proj:
        db.close()
        raise ValueError(f"Projekt mit task_folder '{task_folder}' nicht gefunden")

    project_id = proj["id"]
    component_ids = [
        r[0]
        for r in db.conn.execute(
            "SELECT id FROM components WHERE project_id = ?", (project_id,)
        ).fetchall()
    ]

    if not component_ids:
        db.close()
        return {"deleted_functions": 0, "deleted_failure_modes": 0}

    ph = ",".join("?" * len(component_ids))
    func_ids = [
        r[0]
        for r in db.conn.execute(
            f"SELECT id FROM functions WHERE component_id IN ({ph})", component_ids
        ).fetchall()
    ]

    if not func_ids:
        db.close()
        return {"deleted_functions": 0, "deleted_failure_modes": 0}

    func_ph = ",".join("?" * len(func_ids))
    fm_ids = [
        r[0]
        for r in db.conn.execute(
            f"SELECT id FROM failure_modes WHERE function_id IN ({func_ph})", func_ids
        ).fetchall()
    ]

    deleted = {
        "measures": 0,
        "risk_assessments": 0,
        "current_controls": 0,
        "failure_effects": 0,
        "failure_causes": 0,
        "failure_modes": 0,
        "functions": 0,
    }

    if fm_ids:
        fm_ph = ",".join("?" * len(fm_ids))
        for table, col in [
            ("measures", "failure_mode_id"),
            ("risk_assessments", "failure_mode_id"),
            ("current_controls", "failure_mode_id"),
            ("failure_effects", "failure_mode_id"),
            ("failure_causes", "failure_mode_id"),
        ]:
            cur = db.conn.execute(
                f"DELETE FROM {table} WHERE {col} IN ({fm_ph})", fm_ids
            )
            deleted[table] = cur.rowcount

        cur = db.conn.execute(
            f"DELETE FROM failure_modes WHERE id IN ({fm_ph})", fm_ids
        )
        deleted["failure_modes"] = cur.rowcount

    cur = db.conn.execute(
        f"DELETE FROM functions WHERE id IN ({func_ph})", func_ids
    )
    deleted["functions"] = cur.rowcount

    db.conn.commit()
    db.close()
    return deleted


def reset_fmea_explicit(task_folder: str) -> None:
    """Setzt fmea_explicit.py auf leeren Stub."""
    base = Path(__file__).parent.parent
    path = base / "tasks" / task_folder / "fmea_explicit.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '''"""
Explizite FMEA-Definitionen pro Komponente – Agent-Output.

Der Agent analysiert jede Komponente einzeln und ergänzt diese Datei.
get_fmea_for_component(komp_id) liefert die Definition für insert_fmea_for_component.
"""

def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})

_FMEA = {}
''',
        encoding="utf-8",
    )


def reset_workflow_state_fmea(task_folder: str) -> None:
    """Setzt alle Komponenten auf fmea=pending, Phase fmea=in_progress."""
    state = load_state(task_folder)
    if state is None:
        return
    components = state.get("components", {})
    for komp_id in components:
        components[komp_id]["fmea"] = "pending"
    state["phases"] = state.get("phases", {})
    state["phases"]["fmea"] = "in_progress"
    state["phases"]["struktur"] = "done"
    state["phase"] = "fmea"
    state["current_komp_id"] = None
    save_state(task_folder, state)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Löscht FMEA-Daten für ein Projekt (DB + optional Dateien)"
    )
    ap.add_argument("task_folder", help="z.B. Risikoanalyse/Ethylacetatproduktion_20TA42")
    ap.add_argument(
        "--reset-files",
        action="store_true",
        help="Zusätzlich fmea_explicit.py leeren und workflow_state zurücksetzen",
    )
    args = ap.parse_args()

    print(f"Lösche FMEA-Daten für {args.task_folder}...")
    result = clear_fmea_for_project(args.task_folder)
    print("DB:", result)

    if args.reset_files:
        reset_fmea_explicit(args.task_folder)
        print("fmea_explicit.py auf leeren Stub gesetzt.")
        reset_workflow_state_fmea(args.task_folder)
        print("workflow_state.json: alle Komponenten fmea=pending.")
