"""
RPZ Calculator -- Compute Risk Priority Numbers and apply Safety Guard overrides.

Takes S/O/D values from the database, computes RPZ, classifies risk level,
and applies mandatory overrides for safety-critical contexts.

Usage:
    from tools.rpz_calculator import calculate_and_store_rpz
    stats = calculate_and_store_rpz(project_id)
"""

import json
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage
from config.fmea_standards import (
    classify_rpz, apply_special_rules, SAFETY_OVERRIDES, RPZ_THRESHOLDS,
)


def check_safety_overrides(failure_mode_data: dict) -> tuple:
    """
    Check if safety overrides apply based on the failure mode itself.
    Only searches in fehlermodus description, fehlerart, and component name/type --
    NOT in the full lean_context (which always contains plant-wide substance data).
    Returns (new_S_value, override_label) or (None, None) if no override.
    """
    relevant_fields = " ".join([
        failure_mode_data.get("fehlermodus", ""),
        failure_mode_data.get("fehlerart", ""),
        failure_mode_data.get("komponente", ""),
        failure_mode_data.get("typ", ""),
    ]).lower()

    highest_override = None
    highest_min_S = 0

    for rule in SAFETY_OVERRIDES:
        if any(kw in relevant_fields for kw in rule["keywords"]):
            effective_min_S = rule["min_S"]
            effective_label = rule["label"]

            # Check qualifiers: more specific context → adjusted min_S
            for qualifier in rule.get("qualifiers", []):
                if any(qkw in relevant_fields for qkw in qualifier["context_keywords"]):
                    effective_min_S = qualifier["min_S"]
                    effective_label = qualifier["label"]
                    break  # First matching qualifier wins

            if effective_min_S > highest_min_S:
                highest_min_S = effective_min_S
                highest_override = effective_label

    return (highest_min_S, highest_override) if highest_override else (None, None)


def calculate_rpz(S: int, O: int, D: int) -> dict:
    """Calculate RPZ and classify."""
    rpz = S * O * D
    return {
        "S": S, "O": O, "D": D,
        "rpz": rpz,
        "rpz_status": classify_rpz(rpz),
    }


def calculate_and_store_rpz(project_id: int, db_path: str = None) -> dict:
    """
    Recalculate RPZ for all failure modes in a project.
    Applies safety guard overrides and FMEA special rules.
    Returns statistics.
    """
    db = FMEAStorage(db_path)

    failure_modes = db.conn.execute("""
        SELECT fm.id, fm.fehler_id, fm.fehlermodus, fm.fehlerart,
               c.name as komponente, c.typ as komponenten_typ,
               c.kontext_json, c.parameters_json
        FROM failure_modes fm
        JOIN functions f ON fm.function_id = f.id
        JOIN components c ON f.component_id = c.id
        WHERE c.project_id = ?
    """, (project_id,)).fetchall()

    stats = {"total": 0, "overrides_applied": 0, "special_rules_applied": 0,
             "rpz_distribution": {}}

    for fm_row in failure_modes:
        fm = dict(fm_row)
        fm_id = fm["id"]

        ra = db.get_risk_assessment(fm_id)
        if not ra:
            continue

        stats["total"] += 1
        S, O, D = ra["S"], ra["O"], ra["D"]

        fm_context = {
            "fehlermodus": fm["fehlermodus"],
            "fehlerart": fm["fehlerart"],
            "komponente": fm["komponente"],
            "typ": fm["komponenten_typ"],
            "kontext": fm.get("kontext_json", "{}"),
            "parameters": fm.get("parameters_json", "{}"),
        }

        override_S, override_label = check_safety_overrides(fm_context)
        override_text = None

        if override_S is not None and S < override_S:
            S = override_S
            override_text = f"OVERRIDE: {override_label} (S angehoben auf {S})"
            stats["overrides_applied"] += 1

        rpz = S * O * D
        rpz_status = classify_rpz(rpz)

        final_status, rule_desc = apply_special_rules(S, O, D, rpz_status)
        if rule_desc:
            override_parts = [override_text] if override_text else []
            override_parts.append(f"Sonderregel: {rule_desc}")
            override_text = " | ".join(override_parts)
            rpz_status = final_status
            stats["special_rules_applied"] += 1

        db.update_risk_assessment(
            fm_id,
            S=S, rpz=rpz, rpz_status=rpz_status,
            override_applied=override_text
        )

        stats["rpz_distribution"][rpz_status] = stats["rpz_distribution"].get(rpz_status, 0) + 1

    db.close()
    return stats


if __name__ == "__main__":
    print("=== RPZ Calculator ===")
    print(f"\nGrenzwerte: {RPZ_THRESHOLDS}")
    print(f"Safety-Overrides: {len(SAFETY_OVERRIDES)} Regeln")

    for rule in SAFETY_OVERRIDES:
        print(f"  - {rule['label']}: min S={rule['min_S']} bei Keywords {rule['keywords'][:3]}...")

    test_cases = [
        (8, 3, 2),
        (5, 5, 5),
        (10, 6, 5),
        (3, 2, 2),
    ]
    print("\nTest-Berechnungen:")
    for s, o, d in test_cases:
        result = calculate_rpz(s, o, d)
        print(f"  S={s} O={o} D={d} → RPZ={result['rpz']} ({result['rpz_status']})")
