#!/usr/bin/env python3
"""
Generiert checklist.md aus DB.

Liest den Projektstand ausschließlich aus der Datenbank:
- Hat Komponente Funktionen und Fehlermodi? (FMEA)
- Hat Fehlermodus Maßnahmen?

Kein Abgleich mit fmea_explicit – frische Bewertung pro Analyse.

Usage:
    python tools/update_checklist.py Risikoanalyse/Ethylacetatproduktion_20TA42
    from tools.update_checklist import update_checklist
    update_checklist("Risikoanalyse/Ethylacetatproduktion_20TA42")
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.workflow_state import load_state


def update_checklist(task_folder: str, db_path: str = None) -> str:
    """
    Generiert checklist.md für den task_folder.
    Returns: Pfad zur geschriebenen Datei.
    """
    state = load_state(task_folder)
    if state is None:
        return _write_empty_checklist(task_folder)

    project_id = state.get("project_id")
    if not project_id:
        return _write_empty_checklist(task_folder)

    with FMEAStorage(db_path) as db:
        proj = db.get_project(project_id)
        if not proj:
            return _write_empty_checklist(task_folder)

        components = db.get_components(project_id)
        rows = []

        for comp in components:
            komp_id = comp["komp_id"]
            name = comp.get("name", "")

            # FMEA in DB?
            funcs = db.get_functions(comp["id"])
            has_functions = len(funcs) > 0
            fm_count = 0
            for f in funcs:
                fm_count += len(db.get_failure_modes(f["id"]))
            has_fmea = has_functions and fm_count > 0

            # Maßnahmen in DB?
            measures_count = 0
            if has_fmea:
                for f in funcs:
                    for fm in db.get_failure_modes(f["id"]):
                        measures_count += len(db.get_measures(fm["id"]))
            has_measures = measures_count > 0

            fmea_status = "✓" if has_fmea else "offen"
            measures_status = "✓" if has_measures else "offen"

            rows.append((komp_id, name, fmea_status, measures_status))

    # Projektname für Überschrift
    proj_name = proj.get("anlage_name") or proj.get("name", "FMEA-Projekt")

    return _write_checklist(task_folder, proj_name, rows)


def _write_checklist(task_folder: str, proj_name: str, rows: list) -> str:
    path = Path(__file__).parent.parent / "tasks" / task_folder / "checklist.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# FMEA-Fortschritt: {proj_name}",
        "",
        "| KOMP-ID | Name | FMEA | Maßnahmen |",
        "|---------|------|------|-----------|",
    ]
    for komp_id, name, fmea_status, measures_status in rows:
        lines.append(f"| {komp_id} | {name} | {fmea_status} | {measures_status} |")

    lines.extend(["", f"*Generiert aus DB. {len(rows)} Komponenten.*"])
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def _write_empty_checklist(task_folder: str) -> str:
    path = Path(__file__).parent.parent / "tasks" / task_folder / "checklist.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"# FMEA-Fortschritt: {task_folder}\n\nNoch keine Struktur initialisiert. Führe zuerst die Strukturanalyse durch.\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/update_checklist.py <task_folder>")
        print("  z.B. python tools/update_checklist.py Risikoanalyse/Ethylacetatproduktion_20TA42")
        sys.exit(1)
    task = sys.argv[1]
    out = update_checklist(task)
    print(f"Checklist geschrieben: {out}")
