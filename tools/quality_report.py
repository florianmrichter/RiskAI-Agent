"""
Quality Report -- Agent performance dashboard for FMEA assessments.

Generates reports showing:
- Correction rates per project (trending down = system learning)
- Most common correction patterns
- Calibration rule effectiveness
- Coverage gaps (expert-added failure modes)

Usage:
    python tools/quality_report.py [--project-id N] [--html]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_quality_report(db_path=None, project_id=None):
    """
    Generate a comprehensive quality report.

    Returns:
        str: Markdown-formatted report
    """
    from tools.storage import FMEAStorage
    from tools.calibration import load_calibration_rules, analyze_corrections

    db = FMEAStorage(db_path)

    try:
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("  FMEA Skill Quality Report")
        report_lines.append("=" * 50)
        report_lines.append(f"  Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("")

        # Section 1: Project Overview & Correction Rates
        report_lines.append("─" * 50)
        report_lines.append("  1. Skill-Performance über Zeit")
        report_lines.append("─" * 50)

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
                bar = "█" * bar_filled + "░" * (10 - bar_filled)
                report_lines.append(
                    f"  {pr['name'][:30]:<30} Korrekturrate {pr['correction_rate']:.0%}  "
                    f"{bar}  ({pr['corrections']}/{pr['total']} korrigiert)"
                )

            if len(project_rates) >= 2:
                first_rate = project_rates[0]["correction_rate"]
                last_rate = project_rates[-1]["correction_rate"]
                diff = first_rate - last_rate
                if diff > 0:
                    report_lines.append(f"\n  Trend: ↓ Verbesserung um {diff:.0%} über {len(project_rates)} Projekte")
                elif diff < 0:
                    report_lines.append(f"\n  Trend: ↑ Verschlechterung um {abs(diff):.0%} über {len(project_rates)} Projekte")
                else:
                    report_lines.append(f"\n  Trend: → Stabil über {len(project_rates)} Projekte")
        else:
            report_lines.append("  Keine Feedback-Daten vorhanden.")

        report_lines.append("")

        # Section 2: Common Correction Patterns
        report_lines.append("─" * 50)
        report_lines.append("  2. Wo liegt der Agent falsch? (Schwachstellen)")
        report_lines.append("─" * 50)

        analysis = analyze_corrections(db_path)

        if analysis["total_corrections"] > 0:
            report_lines.append("  Häufigste Korrektur-Muster:")
            for i, p in enumerate(analysis.get("patterns", [])[:5], 1):
                cal_rules = load_calibration_rules()
                has_rule = any(
                    r.get("condition", {}).get("komponenten_typ", "").lower() == p["komponenten_typ"].lower()
                    and r.get("condition", {}).get("field") == p["field"]
                    for r in cal_rules.get("rules", [])
                )
                rule_status = "→ Regel aktiv" if has_rule else "→ noch keine Regel"
                direction = "unterschätzt" if p["avg_delta"] > 0 else "überschätzt"
                report_lines.append(
                    f"    {i}. {p['komponenten_typ']} + {p.get('fehlerart', '?')} → "
                    f"{p['field']} {direction} (Ø {p['avg_delta']:+.1f}, {p['occurrences']} Fälle)  {rule_status}"
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
                    hint = " ← größtes Verbesserungspotential"
                report_lines.append(
                    f"    {field}: {direction_text.get(bias['direction'], bias['direction'])} "
                    f"(Ø {bias['avg_delta']:+.1f}){hint}"
                )
        else:
            report_lines.append("  Keine Korrekturen vorhanden — noch kein Lernmaterial.")

        report_lines.append("")

        # Section 3: Calibration Rule Effectiveness
        report_lines.append("─" * 50)
        report_lines.append("  3. Kalibrierungsregeln — Wirksamkeit")
        report_lines.append("─" * 50)

        cal_rules = load_calibration_rules()
        rules = cal_rules.get("rules", [])

        if rules:
            report_lines.append(f"  Aktive Regeln: {len(rules)}")
            for rule in rules:
                # Check how many times rule was applied and confirmed
                report_lines.append(
                    f"    {rule['id']}: {rule.get('evidence', 'Keine Details')}  "
                    f"[{rule.get('confidence', '?')}]"
                )
        else:
            report_lines.append("  Keine Kalibrierungsregeln aktiv.")

        report_lines.append("")

        # Section 4: Overall Statistics
        report_lines.append("─" * 50)
        report_lines.append("  4. Gesamtstatistik")
        report_lines.append("─" * 50)

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
        report_lines.append(f"    davon Bestätigungen:  {total_confirmations}")
        report_lines.append(f"    davon Korrekturen:    {total_corrections}")
        report_lines.append(f"  Kalibrierungsregeln:    {len(rules)}")
        report_lines.append(f"  Plausibilitäts-Checks:  {len(cal_rules.get('plausibility_checks', []))}")

        report_lines.append("")
        report_lines.append("=" * 50)

        return "\n".join(report_lines)
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FMEA Quality Report")
    parser.add_argument("--project-id", type=int, default=None,
                        help="Filter by project ID")
    parser.add_argument("--db-path", type=str, default=None,
                        help="Path to database file")
    args = parser.parse_args()

    report = generate_quality_report(args.db_path, args.project_id)
    print(report)
