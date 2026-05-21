"""
Grading-Script für FMEA-Skill Eval.
Vergleicht Subagent-Output (result.json) gegen Goldstandard und prüft Assertions.
"""
from __future__ import annotations
import json, sys, os
from pathlib import Path

def grade_result(result_path: str, goldstandard_path: str, assertions: list[dict]) -> dict:
    """Grade ein einzelnes result.json gegen Goldstandard."""

    with open(result_path, 'r') as f:
        result = json.load(f)

    with open(goldstandard_path, 'r') as f:
        gold = json.load(f)

    # Find matching goldstandard assessment
    gold_map = {a['fehler_id']: a for a in gold['assessments']}
    fid = result.get('fehler_id', '')
    gold_entry = gold_map.get(fid, {})

    grades = []

    for assertion in assertions:
        name = assertion['name']
        desc = assertion.get('description', name)
        passed = False
        evidence = ""

        atype = assertion.get('type', '')
        field = assertion.get('field', '')

        if atype == 'text_length':
            text = result.get(field, '') or ''
            min_len = assertion.get('min_length', 0)
            actual_len = len(text)
            passed = actual_len >= min_len
            evidence = f"{field}: {actual_len}z (min {min_len}z)"

        elif atype == 'value_match':
            actual = result.get(field)
            expected = assertion.get('expected')
            tolerance = assertion.get('tolerance', 0)
            if isinstance(expected, str):
                passed = str(actual).lower() == expected.lower()
                evidence = f"{field}: '{actual}' (expected '{expected}')"
            else:
                passed = abs((actual or 0) - expected) <= tolerance
                evidence = f"{field}: {actual} (expected {expected} ±{tolerance})"

        elif atype == 'value_min':
            actual = result.get(field, 0) or 0
            min_val = assertion.get('min_value', 0)
            passed = actual >= min_val
            evidence = f"{field}: {actual} (min {min_val})"

        elif atype == 'rpz_math':
            s, o, d = result.get('S', 0), result.get('O', 0), result.get('D', 0)
            rpz = result.get('rpz', 0)
            expected = s * o * d
            passed = rpz == expected
            evidence = f"RPZ={rpz}, S×O×D={s}×{o}×{d}={expected}"

        elif atype == 'field_present':
            val = result.get(field)
            passed = val is not None and val != '' and val != 'None'
            evidence = f"{field}: {'present' if passed else 'missing'} (value: {val})"

        elif atype == 'text_contains':
            text = str(result.get(field, '') or '').lower()
            keywords = assertion.get('contains', [])
            found = [kw for kw in keywords if kw.lower() in text]
            passed = len(found) > 0
            evidence = f"{field}: found {found} (searched {keywords})"

        elif atype == 'measures_exist':
            measures = result.get('measures', [])
            passed = len(measures) > 0 if isinstance(measures, list) else bool(measures)
            evidence = f"measures: {len(measures) if isinstance(measures, list) else 'present' if measures else 'missing'}"

        else:
            evidence = f"Unknown assertion type: {atype}"

        grades.append({
            "text": name + ": " + desc,
            "passed": passed,
            "evidence": evidence,
        })

    # S/O/D delta vs goldstandard
    deltas = {}
    for field in ['S', 'O', 'D']:
        if field in gold_entry and field in result:
            deltas[field] = {
                'gold': gold_entry[field],
                'actual': result[field],
                'delta': result[field] - gold_entry[field],
            }

    return {
        "fehler_id": fid,
        "expectations": grades,
        "pass_rate": sum(1 for g in grades if g['passed']) / max(len(grades), 1),
        "total_assertions": len(grades),
        "passed_assertions": sum(1 for g in grades if g['passed']),
        "sod_deltas": deltas,
    }


def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('fmea-risikoanalyse-workspace/iteration-1')
    goldstandard = sys.argv[2] if len(sys.argv) > 2 else 'tasks/Risikoanalyse/Buechi_Glasreaktor_15L_20TA43/goldstandard_20TA43.json'
    evals_path = sys.argv[3] if len(sys.argv) > 3 else 'fmea-risikoanalyse-workspace/evals/evals.json'

    with open(evals_path) as f:
        evals = json.load(f)

    print(f"\n{'='*70}")
    print(f"FMEA Skill Eval — Grading")
    print(f"{'='*70}\n")

    for ev in evals['evals']:
        eval_name = ev['name']
        assertions = ev.get('assertions', [])

        for variant in ['with_skill', 'without_skill']:
            result_path = workspace / eval_name / variant / 'outputs' / 'result.json'

            if not result_path.exists():
                print(f"⚠ {eval_name}/{variant}: result.json nicht gefunden")
                continue

            grading = grade_result(str(result_path), goldstandard, assertions)

            # Save grading.json
            grading_path = workspace / eval_name / variant / 'grading.json'
            with open(grading_path, 'w') as f:
                json.dump(grading, f, indent=2, ensure_ascii=False)

            status = "✅" if grading['pass_rate'] == 1.0 else "⚠️" if grading['pass_rate'] >= 0.5 else "❌"
            print(f"{status} {eval_name}/{variant}: {grading['passed_assertions']}/{grading['total_assertions']} ({grading['pass_rate']*100:.0f}%)")

            for g in grading['expectations']:
                icon = "✓" if g['passed'] else "✗"
                print(f"    {icon} {g['text']}")
                print(f"      → {g['evidence']}")

            if grading.get('sod_deltas'):
                deltas = grading['sod_deltas']
                parts = [f"{k}: {v['actual']} (gold={v['gold']}, Δ{v['delta']:+d})" for k, v in deltas.items()]
                print(f"    SOD: {', '.join(parts)}")
            print()

    print(f"{'='*70}")


if __name__ == '__main__':
    main()
