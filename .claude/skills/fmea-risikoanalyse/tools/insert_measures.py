#!/usr/bin/env python3
"""
Fügt Agent-generierte Maßnahmen für einen Fehlermodus in die DB ein.

Kein Lesen aus measures_explicit. Der Agent analysiert Fehlermodi mit RPZ >= 100,
entwickelt Maßnahmen nach STOP-Prinzip und ABE-Hierarchie, und übergibt sie hier.

Usage:
    from tools.insert_measures import insert_measures_for_fehlermodus
    measures = [
        {"name": "Leckage-Detektor am Mannloch", "abe_kategorie": "B", "stop_kategorie": "T",
         "beschreibung": "...", "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 2,
         "begruendung": "D sinkt: Direkte Überwachung erkennt Undichtheit früh"},
    ]
    insert_measures_for_fehlermodus(project_id=1, fehler_id="<fehler_id>", measures=measures)
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage


def insert_measures_for_fehlermodus(
    project_id: int,
    fehler_id: str,
    measures: List[Dict[str, Any]],
    db_path: str = None,
) -> Dict[str, int]:
    """
    Fügt Maßnahmen für einen Fehlermodus ein.

    Args:
        project_id: Projekt-ID (zur Verifizierung, dass der Fehlermodus zum Projekt gehört)
        fehler_id: z.B. "R-101-F2-FM1" (projektspezifisch)
        measures: Liste von Maßnahme-Dicts mit mindestens name, abe_kategorie, beschreibung.
                  Optional: stop_kategorie, ziel, S_neu, O_neu, D_neu, begruendung, iteration

    Returns:
        {"inserted": n}
    """
    if not measures:
        return {"inserted": 0}

    db = FMEAStorage(db_path)
    fm = db.get_failure_mode_by_fehler_id(fehler_id)
    if not fm:
        db.close()
        raise ValueError(f"Fehlermodus {fehler_id} nicht gefunden")

    # Verifizieren, dass der Fehlermodus zum Projekt gehört
    rows = db.conn.execute("""
        SELECT c.project_id FROM failure_modes fm
        JOIN functions f ON fm.function_id = f.id
        JOIN components c ON f.component_id = c.id
        WHERE fm.fehler_id = ?
    """, (fehler_id,)).fetchall()
    if not rows or rows[0][0] != project_id:
        db.close()
        raise ValueError(f"Fehlermodus {fehler_id} gehört nicht zu Projekt {project_id}")

    # Überspringen, wenn bereits Maßnahmen vorhanden (idempotent)
    existing = db.get_measures(fm["id"])
    if existing:
        db.close()
        return {"inserted": 0}

    ids = db.insert_measures_batch(fm["id"], measures)
    db.close()
    return {"inserted": len(ids)}


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-id", type=int, required=True)
    ap.add_argument("--fehler-id", required=True)
    ap.add_argument("--measures", required=True, help="JSON-Array von Maßnahmen")
    args = ap.parse_args()
    measures = json.loads(args.measures)
    result = insert_measures_for_fehlermodus(args.project_id, args.fehler_id, measures)
    print(f"Eingefügt: {result['inserted']} Maßnahmen")
