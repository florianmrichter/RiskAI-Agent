#!/usr/bin/env python3
"""
Entfernt generische FMEA-Daten für Komponenten KOMP-002 bis KOMP-047.
Behält KOMP-001 (detaillierte Analyse) unverändert.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage


def cleanup_generic_data(project_id: int = 2, db_path: str = None) -> dict:
    """Löscht Funktionen, Fehlermodi und zugehörige Daten für KOMP-002 bis KOMP-047."""
    db = FMEAStorage(db_path)

    # Komponenten KOMP-002 bis KOMP-047
    komp_ids = [f"KOMP-{i:03d}" for i in range(2, 48)]
    component_ids = []
    for row in db.conn.execute(
        "SELECT id FROM components WHERE project_id = ? AND komp_id IN ({})".format(
            ",".join("?" * len(komp_ids))
        ),
        [project_id] + komp_ids,
    ).fetchall():
        component_ids.append(row[0])

    if not component_ids:
        db.close()
        return {"deleted_functions": 0, "deleted_failure_modes": 0}

    placeholders = ",".join("?" * len(component_ids))

    # Funktionen dieser Komponenten
    func_ids = [
        r[0]
        for r in db.conn.execute(
            f"SELECT id FROM functions WHERE component_id IN ({placeholders})",
            component_ids,
        ).fetchall()
    ]

    if not func_ids:
        db.close()
        return {"deleted_functions": 0, "deleted_failure_modes": 0}

    func_ph = ",".join("?" * len(func_ids))

    # Failure modes dieser Funktionen
    fm_ids = [
        r[0]
        for r in db.conn.execute(
            f"SELECT id FROM failure_modes WHERE function_id IN ({func_ph})",
            func_ids,
        ).fetchall()
    ]

    deleted = {"measures": 0, "risk_assessments": 0, "current_controls": 0,
               "failure_effects": 0, "failure_causes": 0, "failure_modes": 0, "functions": 0}

    if fm_ids:
        fm_ph = ",".join("?" * len(fm_ids))
        for table, col in [
            ("measures", "failure_mode_id"),
            ("risk_assessments", "failure_mode_id"),
            ("current_controls", "failure_mode_id"),
            ("failure_effects", "failure_mode_id"),
            ("failure_causes", "failure_mode_id"),
        ]:
            cur = db.conn.execute(f"DELETE FROM {table} WHERE {col} IN ({fm_ph})", fm_ids)
            deleted[table] = cur.rowcount

        cur = db.conn.execute(f"DELETE FROM failure_modes WHERE id IN ({fm_ph})", fm_ids)
        deleted["failure_modes"] = cur.rowcount

    cur = db.conn.execute(f"DELETE FROM functions WHERE id IN ({func_ph})", func_ids)
    deleted["functions"] = cur.rowcount

    db.conn.commit()
    db.close()
    return deleted


if __name__ == "__main__":
    result = cleanup_generic_data(2)
    print("Gelöscht:", result)
