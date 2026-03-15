"""
Agent Eval: RPZ Classification Validation

Semi-automated eval — run AFTER a manual FMEA skill execution.
Reads the DB and validates that RPZ classifications are correct.

Usage:
    python tests/eval_fmea_rpz.py [--project-id N] [--db-path PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.fmea_standards import classify_rpz, apply_special_rules
from tools.storage import FMEAStorage

# Known test cases for agent eval
EXPECTED_CLASSIFICATIONS = [
    {"S": 7, "O": 4, "D": 6, "rpz": 168, "expected_status": "mittel"},
    {"S": 10, "O": 10, "D": 3, "rpz": 300, "expected_status": "kritisch"},
    {"S": 5, "O": 5, "D": 4, "rpz": 100, "expected_status": "mittel"},
    {"S": 3, "O": 3, "D": 3, "rpz": 27, "expected_status": "niedrig"},
]


def validate_rpz_classifications(db: FMEAStorage, project_id: int) -> dict:
    """Validate all RPZ classifications in a project."""
    results = {"total": 0, "passed": 0, "failed": 0, "errors": []}

    rows = db.conn.execute("""
        SELECT fm.fehler_id, fm.fehlermodus, fm.fehlerart,
               ra.S, ra.O, ra.D, ra.rpz, ra.rpz_status,
               ra.override_applied,
               c.name as komponente, c.typ as komponenten_typ
        FROM risk_assessments ra
        JOIN failure_modes fm ON ra.failure_mode_id = fm.id
        JOIN functions f ON fm.function_id = f.id
        JOIN components c ON f.component_id = c.id
        WHERE c.project_id = ?
    """, (project_id,)).fetchall()

    for row in rows:
        row = dict(row)
        results["total"] += 1

        S, O, D = row["S"], row["O"], row["D"]
        actual_rpz = row["rpz"]
        actual_status = row["rpz_status"]

        # 1. Check RPZ math
        expected_rpz = S * O * D
        if actual_rpz != expected_rpz:
            results["failed"] += 1
            results["errors"].append(
                f"MATH ERROR: {row['fehler_id']} — RPZ={actual_rpz}, expected S*O*D={expected_rpz}"
            )
            continue

        # 2. Check base classification
        base_status = classify_rpz(actual_rpz)

        # 3. Check with special rules
        final_status, rule = apply_special_rules(S, O, D, base_status)

        if actual_status != final_status:
            results["failed"] += 1
            results["errors"].append(
                f"CLASSIFICATION ERROR: {row['fehler_id']} '{row['fehlermodus']}' — "
                f"RPZ={actual_rpz} (S={S},O={O},D={D}), "
                f"actual='{actual_status}', expected='{final_status}'"
                f"{f' (Sonderregel: {rule})' if rule else ''}"
            )
        else:
            results["passed"] += 1

    return results


def validate_confidence_fields(db: FMEAStorage, project_id: int) -> dict:
    """Check that confidence fields are populated."""
    results = {"total": 0, "missing": 0, "errors": []}

    rows = db.conn.execute("""
        SELECT fm.fehler_id, ra.daten_konfidenz, ra.agent_konfidenz
        FROM risk_assessments ra
        JOIN failure_modes fm ON ra.failure_mode_id = fm.id
        JOIN functions f ON fm.function_id = f.id
        JOIN components c ON f.component_id = c.id
        WHERE c.project_id = ?
    """, (project_id,)).fetchall()

    for row in rows:
        row = dict(row)
        results["total"] += 1
        missing = []
        if not row.get("daten_konfidenz"):
            missing.append("daten_konfidenz")
        if not row.get("agent_konfidenz"):
            missing.append("agent_konfidenz")
        if missing:
            results["missing"] += 1
            results["errors"].append(
                f"{row['fehler_id']}: missing {', '.join(missing)}"
            )

    return results


def validate_measures_for_high_rpz(db: FMEAStorage, project_id: int) -> dict:
    """Check that high/critical RPZ items have at least one measure."""
    results = {"total_high": 0, "with_measures": 0, "without_measures": 0, "errors": []}

    rows = db.conn.execute("""
        SELECT fm.id, fm.fehler_id, fm.fehlermodus,
               ra.rpz, ra.rpz_status
        FROM risk_assessments ra
        JOIN failure_modes fm ON ra.failure_mode_id = fm.id
        JOIN functions f ON fm.function_id = f.id
        JOIN components c ON f.component_id = c.id
        WHERE c.project_id = ? AND ra.rpz >= 100
    """, (project_id,)).fetchall()

    for row in rows:
        row = dict(row)
        results["total_high"] += 1

        measures = db.conn.execute(
            "SELECT COUNT(*) FROM measures WHERE failure_mode_id = ?",
            (row["id"],)
        ).fetchone()[0]

        if measures > 0:
            results["with_measures"] += 1
        else:
            results["without_measures"] += 1
            results["errors"].append(
                f"{row['fehler_id']} '{row['fehlermodus']}' — "
                f"RPZ={row['rpz']} ({row['rpz_status']}), keine Maßnahmen definiert"
            )

    return results


def main():
    parser = argparse.ArgumentParser(description="FMEA Agent Eval: RPZ Validation")
    parser.add_argument("--project-id", type=int, default=None,
                        help="Project ID to validate (default: latest)")
    parser.add_argument("--db-path", type=str, default=None,
                        help="Path to fmea.db (default: data/fmea.db)")
    args = parser.parse_args()

    db_path = args.db_path or str(Path(__file__).parent.parent / "data" / "fmea.db")
    db = FMEAStorage(db_path)

    project_id = args.project_id
    if project_id is None:
        row = db.conn.execute("SELECT MAX(id) FROM projects").fetchone()
        project_id = row[0] if row else None
        if project_id is None:
            print("ERROR: No projects found in database")
            sys.exit(1)

    project = db.conn.execute(
        "SELECT name, anlage_name FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    print(f"\n{'='*60}")
    print(f"FMEA Agent Eval — Projekt: {dict(project)['name']} (ID={project_id})")
    print(f"{'='*60}\n")

    # Eval 1: RPZ Classifications
    print("--- Eval 1: RPZ-Klassifikation ---")
    rpz_results = validate_rpz_classifications(db, project_id)
    print(f"  Total: {rpz_results['total']}")
    print(f"  Passed: {rpz_results['passed']}")
    print(f"  Failed: {rpz_results['failed']}")
    for err in rpz_results["errors"]:
        print(f"  ✗ {err}")

    # Eval 2: Confidence Fields
    print("\n--- Eval 2: Konfidenzfelder ---")
    conf_results = validate_confidence_fields(db, project_id)
    print(f"  Total: {conf_results['total']}")
    print(f"  Missing: {conf_results['missing']}")
    for err in conf_results["errors"][:5]:
        print(f"  ✗ {err}")
    if len(conf_results["errors"]) > 5:
        print(f"  ... und {len(conf_results['errors']) - 5} weitere")

    # Eval 3: Measures for high RPZ
    print("\n--- Eval 3: Maßnahmen bei RPZ >= 100 ---")
    meas_results = validate_measures_for_high_rpz(db, project_id)
    print(f"  Total (RPZ>=100): {meas_results['total_high']}")
    print(f"  Mit Maßnahmen: {meas_results['with_measures']}")
    print(f"  Ohne Maßnahmen: {meas_results['without_measures']}")
    for err in meas_results["errors"][:5]:
        print(f"  ✗ {err}")

    # Summary
    print(f"\n{'='*60}")
    all_passed = (rpz_results["failed"] == 0)
    status = "PASSED" if all_passed else "FAILED"
    print(f"Ergebnis: {status}")
    print(f"{'='*60}\n")

    db.close()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
