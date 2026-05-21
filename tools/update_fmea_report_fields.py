#!/usr/bin/env python3
"""
Aktualisiert kontext_beschreibung, controls_einschraenkung und hinweis in der DB
aus fmea_explicit.py und measures_explicit.py – ohne bestehende FMEA-Daten zu löschen.

Verwendung nach Ergänzung der Felder in den Config-Dateien:
    python tools/update_fmea_report_fields.py Risikoanalyse/Ethylacetatproduktion_20TA42

Liest:
- fmea_explicit: kontext_beschreibung, controls_einschraenkung pro Fehlermodus
- measures_explicit: hinweis pro Maßnahme
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.fmea_loader import get_fmea_for_component, load_measures_module

KOMP_IDS = ["KOMP-001", "KOMP-002", "KOMP-003", "KOMP-004", "KOMP-005", "KOMP-006", "KOMP-007"]


def update_report_fields(task_folder: str, project_id: int = None, db_path: str = None) -> dict:
    """
    Aktualisiert kontext_beschreibung, controls_einschraenkung (failure_modes)
    und hinweis (measures) aus den Config-Dateien.

    Returns: {"failure_modes_updated": n, "measures_updated": n}
    """
    with FMEAStorage(db_path) as db:
        if project_id is None:
            proj = db.get_project_by_task_folder(task_folder)
            if not proj:
                raise ValueError(f"Projekt mit task_folder '{task_folder}' nicht gefunden")
            project_id = proj["id"]

        stats = {"failure_modes_updated": 0, "measures_updated": 0}

        # 1. Failure modes: kontext_beschreibung, controls_einschraenkung
        for komp_id in KOMP_IDS:
            fmea_data = get_fmea_for_component(task_folder, komp_id)
            if not fmea_data:
                continue
            for fm in fmea_data.get("failure_modes", []):
                fehler_id = fm.get("fehler_id")
                if not fehler_id:
                    continue
                kontext = fm.get("kontext_beschreibung")
                einschraenkung = fm.get("controls_einschraenkung")
                if kontext is not None or einschraenkung is not None:
                    if db.update_failure_mode_report_fields(
                        fehler_id,
                        kontext_beschreibung=kontext,
                        controls_einschraenkung=einschraenkung,
                    ):
                        stats["failure_modes_updated"] += 1

        # 2. Measures: hinweis
        mod = load_measures_module(task_folder)
        if mod and hasattr(mod, "_MEASURES"):
            _MEASURES = mod._MEASURES
            for fehler_id, measures in _MEASURES.items():
                fm = db.get_failure_mode_by_fehler_id(fehler_id)
                if not fm:
                    continue
                fm_id = fm["id"]
                for m in measures:
                    hinweis = m.get("hinweis")
                    if hinweis and m.get("name"):
                        if db.update_measure_hinweis(fm_id, m["name"], hinweis):
                            stats["measures_updated"] += 1

    return stats


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Update kontext_beschreibung, controls_einschraenkung, hinweis from config")
    ap.add_argument("task_folder", help="z.B. Risikoanalyse/Ethylacetatproduktion_20TA42")
    ap.add_argument("--project-id", type=int, help="Projekt-ID (optional, wird aus task_folder ermittelt)")
    ap.add_argument("--db", help="Pfad zur fmea.db")
    args = ap.parse_args()
    result = update_report_fields(
        args.task_folder,
        project_id=args.project_id,
        db_path=args.db,
    )
    print(f"Aktualisiert: {result['failure_modes_updated']} Fehlermodi, {result['measures_updated']} Maßnahmen")
