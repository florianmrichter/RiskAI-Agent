#!/usr/bin/env python3
"""
DEPRECATED: Wendet vordefinierte Maßnahmen aus Config auf Fehlermodi an.

Dieses Tool liest aus measures_explicit.py und schreibt in die DB – widerspricht
dem Prinzip "frische Risikobewertung pro Analyse". Bei jeder Risikoanalyse sollen
Risiken neu bewertet werden; der Agent soll Maßnahmen entwickeln und über
tools/insert_measures.insert_measures_for_fehlermodus einspielen.

Nutze stattdessen: tools/generate_measures.run_generate_measures (lädt projektspezifisch)
oder tools/insert_measures.insert_measures_for_fehlermodus (Agent übergibt Daten direkt)

Dieses Tool bleibt für Sonderfälle (z.B. manueller Batch-Import) erhalten,
wird aber nicht mehr im Standard-Workflow verwendet.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.generate_measures import run_generate_measures


def apply_all_explicit_measures(project_id: int = 2, task_folder: str = None, db_path: str = None) -> dict:
    """
    Wendet explizit definierte Maßnahmen an.
    Delegiert an run_generate_measures (lädt aus tasks/{task_folder}/measures_explicit oder config).
    """
    result = run_generate_measures(project_id, task_folder or "Risikoanalyse/Ethylacetatproduktion_20TA41", db_path)
    return {"applied": result["inserted"], "skipped": result["skipped"], "missing": result["missing"]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-id", type=int, default=2)
    ap.add_argument("--task-folder", default="Risikoanalyse/Ethylacetatproduktion_20TA41")
    args = ap.parse_args()
    result = apply_all_explicit_measures(args.project_id, task_folder=args.task_folder)
    print("Maßnahmen angewendet:", result["applied"])
    if result["missing"]:
        print("Ohne Definition (Agent muss analysieren):", result["missing"])
