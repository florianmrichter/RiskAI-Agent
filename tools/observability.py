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


def generate_quality_report(db_path: str | None = None, project_id: int | None = None) -> str:
    """
    Generate a comprehensive markdown-formatted quality report.

    Covers correction rates, common patterns, calibration rules, overall stats.
    (Merged from former quality_report.py)
    """
    from tools.calibration import analyze_corrections, load_calibration_rules

    with FMEAStorage(db_path) as db:
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("  FMEA Skill Quality Report")
        report_lines.append("=" * 50)
        report_lines.append(f"  Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("")

        # Section 1: Project Overview & Correction Rates
        report_lines.append("\u2500" * 50)
        report_lines.append("  1. Skill-Performance \u00fcber Zeit")
        report_lines.append("\u2500" * 50)

        projects = db.conn.execute(
            "SELECT id, name, datum FROM projects ORDER BY id"
        ).fetchall()

        project_rates = []
        for p in projects:
            if project_id is not None and p["id"] != project_id:
                continue
            rate = db.get_correction_rate(p["id"])
            if rate["total"] > 0:
                project_rates.append({
                    "id": p["id"],
                    "name": p["name"],
                    "datum": p["datum"],
                    **rate,
                })

        if project_rates:
            for pr in project_rates:
                bar_filled = int(pr["correction_rate"] * 10)
                bar = "\u2588" * bar_filled + "\u2591" * (10 - bar_filled)
                report_lines.append(
                    f"  {pr['name'][:30]:<30} Korrekturrate {pr['correction_rate']:.0%}  "
                    f"{bar}  ({pr['corrections']}/{pr['total']} korrigiert)"
                )

            if len(project_rates) >= 2:
                first_rate = project_rates[0]["correction_rate"]
                last_rate = project_rates[-1]["correction_rate"]
                diff = first_rate - last_rate
                if diff > 0:
                    report_lines.append(f"\n  Trend: \u2193 Verbesserung um {diff:.0%} \u00fcber {len(project_rates)} Projekte")
                elif diff < 0:
                    report_lines.append(f"\n  Trend: \u2191 Verschlechterung um {abs(diff):.0%} \u00fcber {len(project_rates)} Projekte")
                else:
                    report_lines.append(f"\n  Trend: \u2192 Stabil \u00fcber {len(project_rates)} Projekte")
        else:
            report_lines.append("  Keine Feedback-Daten vorhanden.")

        report_lines.append("")

        # Section 2: Common Correction Patterns
        report_lines.append("\u2500" * 50)
        report_lines.append("  2. Wo liegt der Agent falsch? (Schwachstellen)")
        report_lines.append("\u2500" * 50)

        analysis = analyze_corrections(db_path)

        if analysis["total_corrections"] > 0:
            report_lines.append("  H\u00e4ufigste Korrektur-Muster:")
            for i, p in enumerate(analysis.get("patterns", [])[:5], 1):
                cal_rules = load_calibration_rules()
                has_rule = any(
                    r.get("condition", {}).get("komponenten_typ", "").lower() == p["komponenten_typ"].lower()
                    and r.get("condition", {}).get("field") == p["field"]
                    for r in cal_rules.get("rules", [])
                )
                rule_status = "\u2192 Regel aktiv" if has_rule else "\u2192 noch keine Regel"
                direction = "untersch\u00e4tzt" if p["avg_delta"] > 0 else "\u00fcbersch\u00e4tzt"
                report_lines.append(
                    f"    {i}. {p['komponenten_typ']} + {p.get('fehlerart', '?')} \u2192 "
                    f"{p['field']} {direction} (\u00d8 {p['avg_delta']:+.1f}, {p['occurrences']} F\u00e4lle)  {rule_status}"
                )

            report_lines.append("\n  Felder-Bias:")
            for field, bias in analysis.get("field_bias", {}).items():
                direction_text = {
                    "zu_niedrig": "Agent tendiert zu niedrig",
                    "zu_hoch": "Agent tendiert zu hoch",
                    "neutral": "Agent liegt neutral",
                }
                hint = ""
                if field == max(analysis["field_bias"], key=lambda f: abs(analysis["field_bias"][f]["avg_delta"])):
                    hint = " \u2190 gr\u00f6\u00dftes Verbesserungspotential"
                report_lines.append(
                    f"    {field}: {direction_text.get(bias['direction'], bias['direction'])} "
                    f"(\u00d8 {bias['avg_delta']:+.1f}){hint}"
                )
        else:
            report_lines.append("  Keine Korrekturen vorhanden \u2014 noch kein Lernmaterial.")

        report_lines.append("")

        # Section 3: Calibration Rule Effectiveness
        report_lines.append("\u2500" * 50)
        report_lines.append("  3. Kalibrierungsregeln \u2014 Wirksamkeit")
        report_lines.append("\u2500" * 50)

        cal_rules = load_calibration_rules()
        rules = cal_rules.get("rules", [])

        if rules:
            report_lines.append(f"  Aktive Regeln: {len(rules)}")
            for rule in rules:
                report_lines.append(
                    f"    {rule['id']}: {rule.get('evidence', 'Keine Details')}  "
                    f"[{rule.get('confidence', '?')}]"
                )
        else:
            report_lines.append("  Keine Kalibrierungsregeln aktiv.")

        report_lines.append("")

        # Section 4: Overall Statistics
        report_lines.append("\u2500" * 50)
        report_lines.append("  4. Gesamtstatistik")
        report_lines.append("\u2500" * 50)

        total_assessments = db.conn.execute(
            "SELECT COUNT(*) FROM risk_assessments"
        ).fetchone()[0]
        total_feedback = db.conn.execute(
            "SELECT COUNT(*) FROM assessment_feedback"
        ).fetchone()[0]
        total_corrections = db.conn.execute(
            "SELECT COUNT(*) FROM assessment_feedback WHERE feedback_type = 'correction'"
        ).fetchone()[0]
        total_confirmations = total_feedback - total_corrections

        report_lines.append(f"  Bewertungen gesamt:     {total_assessments}")
        report_lines.append(f"  Feedback gesamt:        {total_feedback}")
        report_lines.append(f"    davon Best\u00e4tigungen:  {total_confirmations}")
        report_lines.append(f"    davon Korrekturen:    {total_corrections}")
        report_lines.append(f"  Kalibrierungsregeln:    {len(rules)}")
        report_lines.append(f"  Plausibilit\u00e4ts-Checks:  {len(cal_rules.get('plausibility_checks', []))}")

        report_lines.append("")
        report_lines.append("=" * 50)

        return "\n".join(report_lines)


if __name__ == "__main__":
    import json as _json
    dashboard = get_full_dashboard()
    print(_json.dumps(dashboard, indent=2, ensure_ascii=False))
