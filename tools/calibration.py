"""
Calibration System -- Plausibility checks and pattern-based calibration rules.

Analyzes expert corrections from the assessment_feedback table to identify
systematic patterns and generate calibration rules that improve future assessments.

Usage:
    from tools.calibration import check_plausibility, analyze_corrections, generate_rules

    # Check a single assessment
    warnings = check_plausibility(fm_data, S=5, O=3, D=4)

    # Generate calibration rules from correction history
    python tools/calibration.py --generate-rules
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

RULES_PATH = Path(__file__).parent.parent / "config" / "calibration_rules.json"


def load_calibration_rules() -> dict:
    """Load calibration rules from config file."""
    if not RULES_PATH.exists():
        return {"rules": [], "plausibility_checks": []}
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_plausibility(fm_data: dict, S: int, O: int, D: int) -> list[dict]:
    """
    Check if S/O/D values are plausible given the failure mode context.

    Args:
        fm_data: dict with keys like komponenten_typ, fehlerart, fehlermodus, medium, etc.
        S, O, D: proposed severity, occurrence, detection values

    Returns:
        list of warning dicts: [{"rule_id": "PLZ-001", "warning": "...", "field": "S", "suggested": 8}]
    """
    config = load_calibration_rules()
    warnings = []

    # Static plausibility checks from config
    for check in config.get("plausibility_checks", []):
        triggered = _evaluate_plausibility_condition(check["condition"], fm_data, S, O, D)
        if triggered:
            warnings.append({
                "rule_id": check.get("id", "PLZ-???"),
                "warning": check["warning"],
                "field": check.get("field"),
                "suggested": check.get("suggested_value"),
            })

    return warnings


def _evaluate_plausibility_condition(condition: str, fm_data: dict, S: int, O: int, D: int) -> bool:
    """Evaluate a plausibility check condition string against context."""
    # Build a searchable context string from fm_data
    context_text = " ".join(str(v) for v in fm_data.values() if v).lower()

    # Parse condition: "keyword AND field < value" or "keyword AND field > value"
    parts = [p.strip() for p in condition.split(" AND ")]

    for part in parts:
        # Check keyword conditions
        if part.startswith("ex_schutz"):
            keywords = ["ex-schutz", "explosionsschutz", "zone 0", "zone 1", "atex", "ex-zone"]
            if not any(kw in context_text for kw in keywords):
                return False
        elif part.startswith("sicherheitsventil"):
            keywords = ["sicherheitsventil", "psv", "berstscheibe", "safety valve"]
            if not any(kw in context_text for kw in keywords):
                return False
        elif part.startswith("redundante_messung"):
            keywords = ["redundant", "2oo3", "1oo2", "diversitär"]
            if not any(kw in context_text for kw in keywords):
                return False
        elif part.startswith("sil_absicherung"):
            keywords = ["sil", "sil-1", "sil-2", "sil-3", "sicherheitsgerichtet"]
            if not any(kw in context_text for kw in keywords):
                return False
        elif part.startswith("gefahrstoff"):
            keywords = ["gefahrstoff", "toxisch", "giftig", "säure", "lauge", "chlor", "lösemittel"]
            if not any(kw in context_text for kw in keywords):
                return False
        elif part.startswith("pumpe"):
            keywords = ["pumpe", "pump", "kreiselpumpe", "membranpumpe", "dosierpumpe"]
            if not any(kw in context_text for kw in keywords):
                return False
        # Check value comparisons
        elif "<" in part:
            field_name, threshold = part.split("<")
            field_name = field_name.strip()
            threshold = int(threshold.strip())
            val = {"S": S, "O": O, "D": D}.get(field_name)
            if val is None or val >= threshold:
                return False
        elif ">" in part:
            field_name, threshold = part.split(">")
            field_name = field_name.strip()
            threshold = int(threshold.strip())
            val = {"S": S, "O": O, "D": D}.get(field_name)
            if val is None or val <= threshold:
                return False

    return True


def apply_calibration(fm_data: dict, S: int, O: int, D: int) -> dict:
    """
    Apply calibration rules to adjust S/O/D values based on learned patterns.

    Returns:
        dict: {"S": adjusted_S, "O": adjusted_O, "D": adjusted_D,
               "adjustments": [{"rule_id": "CAL-001", "field": "S", "old": 5, "new": 7, "reason": "..."}]}
    """
    config = load_calibration_rules()
    adjustments = []
    adjusted = {"S": S, "O": O, "D": D}

    context_text = " ".join(str(v) for v in fm_data.values() if v).lower()

    for rule in config.get("rules", []):
        condition = rule.get("condition", {})

        # Check if rule condition matches
        match = True
        for key, value in condition.items():
            if key == "field":
                continue
            if key == "komponenten_typ":
                if value.lower() not in context_text:
                    match = False
                    break
            elif key == "fehlerart":
                if value.lower() not in context_text:
                    match = False
                    break
            elif key == "medium":
                if value.lower() not in context_text:
                    match = False
                    break

        if not match:
            continue

        field = condition.get("field", rule.get("field"))
        if not field or field not in adjusted:
            continue

        adjustment_str = rule.get("adjustment", "+0")
        adj_value = int(adjustment_str.replace("+", ""))
        old_val = adjusted[field]
        new_val = max(1, min(10, old_val + adj_value))

        if new_val != old_val:
            adjusted[field] = new_val
            adjustments.append({
                "rule_id": rule["id"],
                "field": field,
                "old": old_val,
                "new": new_val,
                "reason": f"Kalibrierung {rule['id']}: {field} von {old_val} auf {new_val} ({rule.get('evidence', '')})",
            })

    return {**adjusted, "adjustments": adjustments}


def analyze_corrections(db_path: str | None = None) -> dict:
    """
    Analyze correction history and identify systematic patterns.

    Returns dict with total_corrections, correction_rate, patterns, field_bias.
    """
    from tools.storage import FMEAStorage

    with FMEAStorage(db_path) as db:
        patterns = db.get_feedback_patterns()

        # Add per-project correction rates
        projects = db.conn.execute("SELECT id, name FROM projects").fetchall()
        project_rates = []
        for p in projects:
            rate = db.get_correction_rate(p["id"])
            if rate["total"] > 0:
                project_rates.append({
                    "project_id": p["id"],
                    "project_name": p["name"],
                    **rate,
                })

        patterns["project_rates"] = project_rates
        return patterns


def generate_rules(db_path: str | None = None, min_occurrences: int = 3) -> dict:
    """
    Generate calibration rules from correction patterns and save to config file.

    Args:
        db_path: Path to SQLite database
        min_occurrences: Minimum corrections with same pattern to generate a rule

    Returns:
        dict: The generated rules configuration
    """
    analysis = analyze_corrections(db_path)

    # Load existing rules to preserve plausibility_checks
    existing = load_calibration_rules()

    rules = []
    rule_counter = 1

    for pattern in analysis.get("patterns", []):
        if pattern["occurrences"] < min_occurrences:
            continue
        if abs(pattern["avg_delta"]) < 0.5:
            continue

        adj = int(round(pattern["avg_delta"]))
        if adj == 0:
            continue

        rule_id = f"CAL-{rule_counter:03d}"
        rules.append({
            "id": rule_id,
            "condition": {
                "komponenten_typ": pattern["komponenten_typ"],
                "fehlerart": pattern.get("fehlerart", ""),
                "field": pattern["field"],
            },
            "adjustment": f"+{adj}" if adj > 0 else str(adj),
            "confidence": pattern["confidence"],
            "evidence": (
                f"{pattern['occurrences']} Korrekturen bei {pattern['komponenten_typ']}/{pattern.get('fehlerart', '?')} "
                f"zeigten {pattern['field']}-{'Unterschätzung' if adj > 0 else 'Überschätzung'} um Ø {abs(pattern['avg_delta'])}"
            ),
        })
        rule_counter += 1

    config = {
        "generated_at": datetime.now().isoformat(),
        "based_on_corrections": analysis.get("total_corrections", 0),
        "rules": rules,
        "plausibility_checks": existing.get("plausibility_checks", []),
    }

    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    return config


def select_training_candidates(db_path: str | None = None, n: int = 10) -> list[dict]:
    """
    Select assessments that would benefit most from expert training.

    Priority:
    1. Assessments with low agent_konfidenz
    2. Component types with few feedback entries
    3. Failure modes historically often corrected

    Returns list of candidate dicts.
    """
    from tools.storage import FMEAStorage

    with FMEAStorage(db_path) as db:
        # Get assessments with low confidence
        candidates = db.conn.execute("""
            SELECT ra.*, fm.fehler_id, fm.fehlermodus, fm.fehlerart,
                   f.beschreibung as funktion_beschreibung,
                   c.komp_id, c.name as komponente, c.typ as komponenten_typ,
                   c.system_name, c.project_id
            FROM risk_assessments ra
            JOIN failure_modes fm ON ra.failure_mode_id = fm.id
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            ORDER BY
                CASE ra.agent_konfidenz
                    WHEN 'niedrig' THEN 1
                    WHEN 'mittel' THEN 2
                    WHEN 'hoch' THEN 3
                    ELSE 2
                END,
                ra.correction_count DESC
            LIMIT ?
        """, (n * 3,)).fetchall()  # Fetch more, then filter

        # Get component types that have little feedback
        feedback_counts = db.conn.execute("""
            SELECT c.typ, COUNT(*) as cnt
            FROM assessment_feedback af
            JOIN failure_modes fm ON af.failure_mode_id = fm.id
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            GROUP BY c.typ
        """).fetchall()
        covered_types = {row["typ"]: row["cnt"] for row in feedback_counts}

        # Score and sort candidates
        scored = []
        for c in candidates:
            score = 0
            if c["agent_konfidenz"] == "niedrig":
                score += 10
            elif c["agent_konfidenz"] == "mittel":
                score += 5

            type_coverage = covered_types.get(c["komponenten_typ"], 0)
            if type_coverage < 3:
                score += 8
            elif type_coverage < 5:
                score += 4

            correction_count = c["correction_count"] or 0
            score += min(correction_count * 2, 6)

            scored.append((score, dict(c)))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:n]]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FMEA Calibration System")
    parser.add_argument("--generate-rules", action="store_true",
                        help="Generate calibration rules from correction history")
    parser.add_argument("--analyze", action="store_true",
                        help="Show correction analysis without generating rules")
    parser.add_argument("--min-occurrences", type=int, default=3,
                        help="Minimum occurrences for rule generation (default: 3)")
    parser.add_argument("--db-path", type=str, default=None,
                        help="Path to database file")
    args = parser.parse_args()

    if args.generate_rules:
        print("=== Generating Calibration Rules ===")
        config = generate_rules(args.db_path, args.min_occurrences)
        print(f"Generated {len(config['rules'])} rules from {config['based_on_corrections']} corrections")
        for rule in config["rules"]:
            print(f"  {rule['id']}: {rule['condition']} → {rule['adjustment']} ({rule['confidence']})")
        print(f"Saved to: {RULES_PATH}")
    elif args.analyze:
        print("=== Correction Analysis ===")
        analysis = analyze_corrections(args.db_path)
        print(f"Total corrections: {analysis['total_corrections']}")
        print(f"\nField bias:")
        for field, bias in analysis.get("field_bias", {}).items():
            print(f"  {field}: Ø {bias['avg_delta']:+.1f} ({bias['direction']}, {bias['count']} Korrekturen)")
        print(f"\nPatterns ({len(analysis.get('patterns', []))}):")
        for p in analysis.get("patterns", []):
            print(f"  {p['komponenten_typ']}/{p.get('fehlerart', '?')} → {p['field']} Ø {p['avg_delta']:+.1f} "
                  f"({p['occurrences']} Fälle, {p['confidence']})")
    else:
        parser.print_help()
