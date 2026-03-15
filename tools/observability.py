"""
Observability — Projektübergreifende Auswertungen und KI-Performance-Metriken.

Liefert Daten für ein Dashboard oder Report-Anhang:
- Korrekturrate pro Projekt und gesamt
- Welche Komponenten-Typen sind problematisch
- Analyse-Dauer pro Projekt
- Token-Verbrauch pro Projekt
- Kalibrierungs-Effektivität
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage

TASKS_ROOT = Path(__file__).parent.parent / "tasks" / "Risikoanalyse"


def get_project_overview(db_path: str | None = None) -> list[dict]:
    """Übersicht aller Projekte mit Kernmetriken."""
    with FMEAStorage(db_path) as db:
        projects = db.conn.execute("SELECT * FROM projects ORDER BY id").fetchall()
        result = []
        for p in projects:
            p = dict(p)
            pid = p["id"]
            stats = db.get_project_statistics(pid)
            correction_rate = db.get_correction_rate(pid)
            result.append({
                "id": pid,
                "name": p.get("anlage_name", p["name"]),
                "task_folder": p.get("task_folder"),
                "status": p.get("status"),
                "version": p.get("version", "1.0"),
                "komponenten": stats.get("components", 0),
                "fehlermodi": stats.get("failure_modes", 0),
                "massnahmen": stats.get("measures", 0),
                "rpz_verteilung": stats.get("rpz_distribution", {}),
                "korrekturrate": correction_rate.get("correction_rate", 0.0),
                "korrekturen": correction_rate.get("corrections", 0),
                "bestaetigungen": correction_rate.get("confirmations", 0),
            })
    return result


def get_correction_patterns(db_path: str | None = None) -> dict:
    """Analyse: Wo liegt der Agent systematisch falsch?"""
    with FMEAStorage(db_path) as db:
        patterns = db.get_feedback_patterns()
    return patterns


def get_confidence_distribution(db_path: str | None = None) -> dict:
    """Verteilung der Konfidenz-Stufen über alle Bewertungen."""
    with FMEAStorage(db_path) as db:
        rows = db.conn.execute("""
            SELECT daten_konfidenz, agent_konfidenz, COUNT(*) as count
            FROM risk_assessments
            WHERE daten_konfidenz IS NOT NULL
            GROUP BY daten_konfidenz, agent_konfidenz
        """).fetchall()

    distribution = {}
    for row in rows:
        key = f"{row[0]}/{row[1]}"
        distribution[key] = row[2]

    # Totals
    total = sum(distribution.values())
    daten_counts = {}
    agent_counts = {}
    for row in rows:
        daten_counts[row[0]] = daten_counts.get(row[0], 0) + row[2]
        agent_counts[row[1]] = agent_counts.get(row[1], 0) + row[2]

    return {
        "total_assessments": total,
        "daten_konfidenz": daten_counts,
        "agent_konfidenz": agent_counts,
        "combined": distribution,
    }


def get_token_overview() -> list[dict]:
    """Token-Verbrauch pro Projekt (aus token_usage.json Dateien)."""
    results = []
    if not TASKS_ROOT.exists():
        return results
    for project_dir in sorted(TASKS_ROOT.iterdir()):
        token_file = project_dir / "token_usage.json"
        if token_file.exists():
            with open(token_file, encoding="utf-8") as f:
                data = json.load(f)
            results.append({
                "projekt": project_dir.name,
                "sessions": data.get("session_count", 0),
                "total_tokens": data.get("total_tokens", 0),
                "total_input": data.get("total_input", 0),
                "total_output": data.get("total_output", 0),
            })
    return results


def get_full_dashboard(db_path: str | None = None) -> dict:
    """Komplett-Dashboard: Alle Metriken auf einen Blick."""
    projects = get_project_overview(db_path)
    confidence = get_confidence_distribution(db_path)
    tokens = get_token_overview()

    # Aggregierte Metriken
    total_fm = sum(p["fehlermodi"] for p in projects)
    total_measures = sum(p["massnahmen"] for p in projects)
    total_corrections = sum(p["korrekturen"] for p in projects)
    total_confirmations = sum(p["bestaetigungen"] for p in projects)
    total_feedback = total_corrections + total_confirmations
    avg_correction_rate = round(total_corrections / total_feedback, 3) if total_feedback > 0 else 0.0

    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "projekte": len(projects),
            "fehlermodi_gesamt": total_fm,
            "massnahmen_gesamt": total_measures,
            "feedback_gesamt": total_feedback,
            "korrekturrate_gesamt": avg_correction_rate,
            "bewertungen_gesamt": confidence.get("total_assessments", 0),
        },
        "projekte": projects,
        "konfidenz_verteilung": confidence,
        "token_verbrauch": tokens,
    }


if __name__ == "__main__":
    import json as _json
    dashboard = get_full_dashboard()
    print(_json.dumps(dashboard, indent=2, ensure_ascii=False))
