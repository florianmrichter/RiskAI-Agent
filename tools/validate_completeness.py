"""
Validates FMEA completeness before report generation.

Checks:
1. Gefahrenfelder coverage (26 mandatory hazard fields)
2. Utility/interface coverage
3. 9-category coverage
4. CCF identification

Usage:
    from tools.validate_completeness import validate_completeness
    result = validate_completeness(project_id, task_folder)
    # result = {"passed": bool, "warnings": [...], "details": {...}}
"""
from __future__ import annotations

import json
from pathlib import Path

# Import the GEFAHRENFELDER dict from config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.fmea_standards import GEFAHRENFELDER, FEHLERMODI_VORLAGEN
from tools.storage import FMEAStorage


def validate_completeness(project_id: int, task_folder: str = None, db_path: str = None) -> dict:
    """
    Validate FMEA completeness for a project before report generation.

    Returns:
        {
            "passed": bool,  # True if no critical warnings
            "warnings": [str],  # List of warning messages
            "details": {
                "gefahrenfelder": {"covered": [...], "missing": [...]},
                "categories": {"covered": [...], "missing": [...]},
                "utilities": {"covered": [...], "missing": [...]},
                "ccf_candidates": [...]
            }
        }
    """
    db = FMEAStorage(db_path)
    warnings = []
    details = {}

    # Load all failure modes for this project via get_all_failure_modes_with_rpz
    try:
        fms = db.get_all_failure_modes_with_rpz(project_id)
    except Exception:
        fms = []

    if not fms:
        db.close()
        return {
            "passed": False,
            "warnings": ["Keine Fehlermodi in der DB gefunden."],
            "details": {}
        }

    # --- 1. Category check (9 categories) ---
    fm_categories = set()
    for fm in fms:
        cat = fm.get("fehlerart", "").lower() if isinstance(fm, dict) else ""
        if cat:
            fm_categories.add(cat)

    all_categories = set(FEHLERMODI_VORLAGEN.keys())
    missing_categories = all_categories - fm_categories
    details["categories"] = {
        "covered": sorted(fm_categories),
        "missing": sorted(missing_categories)
    }
    for cat in missing_categories:
        warnings.append(f"Kategorie '{cat}' hat keinen zugeordneten Fehlermodus")

    # --- 2. Gefahrenfelder check (mandatory only) ---
    pflicht_felder = {k: v for k, v in GEFAHRENFELDER.items() if v.get("pflicht", False)}
    # We can't automatically determine which GF a FM covers without explicit tagging,
    # so we check category-level coverage as a proxy
    covered_gf_categories = set()
    for fm in fms:
        cat = fm.get("fehlerart", "").lower() if isinstance(fm, dict) else ""
        covered_gf_categories.add(cat)

    missing_gf = []
    covered_gf = []
    for gf_id, gf_data in pflicht_felder.items():
        gf_cats = [c.lower() for c in gf_data.get("fm_kategorien", [])]
        if any(c in covered_gf_categories for c in gf_cats):
            covered_gf.append(gf_id)
        else:
            missing_gf.append(f"{gf_id}: {gf_data['name']}")

    details["gefahrenfelder"] = {
        "covered": covered_gf,
        "missing": missing_gf
    }
    for gf in missing_gf:
        warnings.append(f"Pflicht-Gefahrenfeld nicht abgedeckt: {gf}")

    # --- 3. Utility/interface check ---
    ad = None
    if task_folder:
        base = Path(__file__).parent.parent / "tasks" / task_folder
        anlagendaten_path = base / "anlagendaten.json"
        if anlagendaten_path.exists():
            with open(anlagendaten_path, "r") as f:
                ad = json.load(f)

            # Check media entries
            media = ad.get("media", [])
            fm_texts = " ".join([
                (fm.get("fehlermodus", "") + " " +
                 fm.get("funktion_beschreibung", "") + " " +
                 fm.get("komponente", ""))
                if isinstance(fm, dict) else ""
                for fm in fms
            ]).lower()

            missing_utilities = []
            covered_utilities = []
            for m in media:
                name = m.get("name", "")
                if name.lower() in fm_texts or any(
                    kw in fm_texts for kw in name.lower().split()
                ):
                    covered_utilities.append(name)
                else:
                    missing_utilities.append(name)

            # Check connectedSystems
            for sys_entry in ad.get("systems", []):
                cs = sys_entry.get("connectedSystems", {})
                for direction in ["upstream", "downstream"]:
                    for connected in cs.get(direction, []):
                        if isinstance(connected, str) and "nicht im scope" not in connected.lower():
                            sys_name = connected.split("(")[0].strip()
                            if sys_name.lower() not in fm_texts:
                                missing_utilities.append(f"{sys_name} ({direction})")

            details["utilities"] = {
                "covered": covered_utilities,
                "missing": missing_utilities
            }
            for u in missing_utilities:
                warnings.append(f"Utility/Schnittstelle ohne zugeordneten FM: {u}")

            # Check for backflow-related FMs
            backflow_keywords = ["rückstr", "backflow", "rückfluss", "reverse flow", "rückstrom"]
            has_backflow_fm = any(kw in fm_texts for kw in backflow_keywords)
            has_pressure_interfaces = len(media) > 0  # simplified check
            if has_pressure_interfaces and not has_backflow_fm:
                warnings.append("Keine Rückströmungs-Fehlermodi gefunden, obwohl Utility-Schnittstellen existieren")

    # --- 4. CCF candidates ---
    ccf_candidates = []
    if task_folder and ad is not None:
        utilities_in_use = ad.get("media", [])
        for util in utilities_in_use:
            name = util.get("name", "")
            if util.get("fmea_critical", False) or util.get("failureConsequence"):
                ccf_candidates.append(f"{name}: Ausfall betrifft möglicherweise mehrere Komponenten")

        details["ccf_candidates"] = ccf_candidates
        if ccf_candidates:
            warnings.append(f"{len(ccf_candidates)} CCF-Kandidaten identifiziert — prüfen ob Kaskaden-FMs vorhanden")

    db.close()

    passed = not any("Pflicht-Gefahrenfeld" in w for w in warnings)

    return {
        "passed": passed,
        "warnings": warnings,
        "details": details
    }


def format_report(result: dict) -> str:
    """Format validation result as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("FMEA-Vollständigkeitsprüfung")
    lines.append("=" * 60)

    status = "BESTANDEN" if result["passed"] else "WARNINGS"
    lines.append(f"\nStatus: {status}")
    lines.append(f"Warnings: {len(result['warnings'])}")

    if result["warnings"]:
        lines.append("\n--- Warnings ---")
        for i, w in enumerate(result["warnings"], 1):
            lines.append(f"  {i}. {w}")

    details = result.get("details", {})

    if "categories" in details:
        cats = details["categories"]
        lines.append(f"\n--- Kategorien ({len(cats['covered'])}/{ len(cats['covered']) + len(cats['missing']) }) ---")
        if cats["missing"]:
            lines.append(f"  Fehlend: {', '.join(cats['missing'])}")

    if "gefahrenfelder" in details:
        gf = details["gefahrenfelder"]
        lines.append(f"\n--- Gefahrenfelder ({len(gf['covered'])}/{len(gf['covered'])+len(gf['missing'])}) ---")
        if gf["missing"]:
            for m in gf["missing"]:
                lines.append(f"  Fehlend: {m}")

    if "utilities" in details:
        ut = details["utilities"]
        if ut["missing"]:
            lines.append("\n--- Utilities ohne FM ---")
            for m in ut["missing"]:
                lines.append(f"  {m}")

    if "ccf_candidates" in details and details["ccf_candidates"]:
        lines.append("\n--- CCF-Kandidaten ---")
        for c in details["ccf_candidates"]:
            lines.append(f"  {c}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FMEA Completeness Validation")
    parser.add_argument("project_id", type=int)
    parser.add_argument("--task-folder", required=True)
    args = parser.parse_args()

    result = validate_completeness(args.project_id, args.task_folder)
    print(format_report(result))
