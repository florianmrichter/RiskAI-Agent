"""
Validates FMEA completeness before report generation.

Checks:
1. Gefahrenfelder coverage (26 mandatory hazard fields)
2. Utility/interface coverage
3. 9-category coverage
4. CCF identification
5. S/O/D plausibility (safety overrides, reliability data, MSR)
6. Measures effectiveness (high-RPZ without measures, RPZ reduction)
7. Cross-FM + Anlagendaten alignment (system coverage, hazardous substances)

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
from config.fmea_standards import GEFAHRENFELDER, FEHLERMODI_VORLAGEN, SAFETY_OVERRIDES
from tools.storage import FMEAStorage
from tools._base import tool_entry
from tools.rpz_calculator import check_safety_overrides
from tools.reliability_lookup import suggest_for_component


# ---------------------------------------------------------------------------
# Helper: build combined FM text for keyword searches
# ---------------------------------------------------------------------------

def _fm_texts_joined(fms: list[dict]) -> str:
    """Join fehlermodus + funktion_beschreibung + komponente for all FMs (lowercase)."""
    return " ".join(
        (fm.get("fehlermodus", "") + " " +
         fm.get("funktion_beschreibung", "") + " " +
         fm.get("komponente", ""))
        if isinstance(fm, dict) else ""
        for fm in fms
    ).lower()


# ---------------------------------------------------------------------------
# Phase 1: Category coverage (9 categories)
# ---------------------------------------------------------------------------

def _check_categories(fms: list[dict], ad: dict | None) -> tuple[dict, list[str]]:
    """Return (details_dict, warnings) for category coverage."""
    fm_categories = set()
    for fm in fms:
        cat = fm.get("fehlerart", "").lower() if isinstance(fm, dict) else ""
        if cat:
            fm_categories.add(cat)

    all_categories = set(FEHLERMODI_VORLAGEN.keys())
    missing_categories = all_categories - fm_categories

    details = {
        "covered": sorted(fm_categories),
        "missing": sorted(missing_categories),
    }
    warnings = [
        f"Kategorie '{cat}' hat keinen zugeordneten Fehlermodus"
        for cat in missing_categories
    ]
    return details, warnings


# ---------------------------------------------------------------------------
# Phase 2: Gefahrenfelder coverage (mandatory only)
# ---------------------------------------------------------------------------

def _check_gefahrenfelder(fms: list[dict], ad: dict | None) -> tuple[dict, list[str]]:
    """Return (details_dict, warnings) for mandatory Gefahrenfelder coverage."""
    pflicht_felder = {k: v for k, v in GEFAHRENFELDER.items() if v.get("pflicht", False)}

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

    details = {
        "covered": covered_gf,
        "missing": missing_gf,
    }
    warnings = [
        f"Pflicht-Gefahrenfeld nicht abgedeckt: {gf}"
        for gf in missing_gf
    ]
    return details, warnings


# ---------------------------------------------------------------------------
# Phase 3: Utility/interface coverage
# ---------------------------------------------------------------------------

def _check_utilities(fms: list[dict], ad: dict | None) -> tuple[dict | None, list[str]]:
    """Return (details_dict_or_None, warnings) for utility/interface coverage."""
    if ad is None:
        return None, []

    fm_texts = _fm_texts_joined(fms)

    missing_utilities = []
    covered_utilities = []
    for m in ad.get("media", []):
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

    details = {
        "covered": covered_utilities,
        "missing": missing_utilities,
    }
    warnings = [
        f"Utility/Schnittstelle ohne zugeordneten FM: {u}"
        for u in missing_utilities
    ]

    # Check for backflow-related FMs
    backflow_keywords = ["rückstr", "backflow", "rückfluss", "reverse flow", "rückstrom"]
    has_backflow_fm = any(kw in fm_texts for kw in backflow_keywords)
    has_pressure_interfaces = len(ad.get("media", [])) > 0
    if has_pressure_interfaces and not has_backflow_fm:
        warnings.append("Keine Rückströmungs-Fehlermodi gefunden, obwohl Utility-Schnittstellen existieren")

    return details, warnings


# ---------------------------------------------------------------------------
# Phase 4: CCF candidates
# ---------------------------------------------------------------------------

def _check_ccf_candidates(fms: list[dict], ad: dict | None) -> tuple[list[str], list[str]]:
    """Return (ccf_candidates_list, warnings) for common cause failure detection."""
    if ad is None:
        return [], []

    ccf_candidates = []
    for util in ad.get("media", []):
        name = util.get("name", "")
        if util.get("fmea_critical", False) or util.get("failureConsequence"):
            ccf_candidates.append(f"{name}: Ausfall betrifft möglicherweise mehrere Komponenten")

    warnings = []
    if ccf_candidates:
        warnings.append(f"{len(ccf_candidates)} CCF-Kandidaten identifiziert — prüfen ob Kaskaden-FMs vorhanden")

    return ccf_candidates, warnings


# ---------------------------------------------------------------------------
# Phase 5: S/O/D plausibility
# ---------------------------------------------------------------------------

def _check_sod_plausibility(fms: list[dict], ad: dict | None) -> tuple[list[str], list[str]]:
    """Return (sod_findings, warnings) for S/O/D plausibility checks."""
    sod_findings = []

    for fm in fms:
        fehler_id = fm.get("fehler_id", "?")
        S = fm.get("S")
        O = fm.get("O")
        D = fm.get("D")

        # 5a: S-Plausibility via safety overrides
        if S is not None:
            fm_data = {
                "fehlermodus": fm.get("fehlermodus", ""),
                "fehlerart": fm.get("fehlerart", ""),
                "komponente": fm.get("komponente", ""),
                "typ": fm.get("komponenten_typ", ""),
            }
            min_S, label = check_safety_overrides(fm_data)
            if min_S is not None and S < min_S:
                sod_findings.append(
                    f"KRITISCH: FM '{fehler_id}' S={S} zu niedrig — "
                    f"Safety Override '{label}' erfordert min S={min_S}"
                )

        # 5b: O-Plausibility via reliability lookup
        if O is not None:
            comp_name = fm.get("komponente", "")
            comp_typ = fm.get("komponenten_typ", "")
            try:
                match = suggest_for_component(comp_name, comp_typ)
            except Exception:
                match = None
            if match:
                from tools.reliability_lookup import ReliabilityDB
                try:
                    rdb = ReliabilityDB()
                    suggestion = rdb.suggest_o_value(
                        failure_rate_fpmh=match.get("failure_rate_fpmh"),
                        equipment_type=match.get("equipment_type"),
                    )
                    richtwert = suggestion.get("o_wert")
                    if richtwert is not None and abs(O - richtwert) > 3:
                        sod_findings.append(
                            f"WARNUNG: FM '{fehler_id}' O={O} weicht stark von "
                            f"CCPS/OREDA-Richtwert ab (erwartet ~{richtwert})"
                        )
                except Exception:
                    pass

        # 5c: D-Plausibility — MSR equipment present but D high
        if D is not None and D > 7 and ad is not None:
            msr_equipment = ad.get("msrEquipment", ad.get("msr_equipment", []))
            if msr_equipment:
                sod_findings.append(
                    f"WARNUNG: FM '{fehler_id}' D={D} trotz vorhandener MSR-Ausstattung"
                )

    # sod_findings are also the warnings
    return sod_findings, list(sod_findings)


# ---------------------------------------------------------------------------
# Phase 6: Measures effectiveness
# ---------------------------------------------------------------------------

def _check_measures_effectiveness(fms: list[dict], db: FMEAStorage) -> tuple[list[str], list[str]]:
    """Return (measures_findings, warnings) for measures effectiveness checks."""
    measures_findings = []

    for fm in fms:
        fehler_id = fm.get("fehler_id", "?")
        fm_id = fm.get("id")
        rpz = fm.get("rpz")

        if rpz is not None and rpz >= 200 and fm_id is not None:
            measure_rows = db.conn.execute(
                "SELECT * FROM measures WHERE failure_mode_id = ?", (fm_id,)
            ).fetchall()
            if not measure_rows:
                measures_findings.append(
                    f"KRITISCH: FM '{fehler_id}' RPZ={rpz} ohne Maßnahmen"
                )
            else:
                rpz_reduced = False
                for m in measure_rows:
                    m_dict = dict(m)
                    rpz_neu = m_dict.get("rpz_neu")
                    if rpz_neu is not None and rpz_neu < rpz:
                        rpz_reduced = True
                        break
                if not rpz_reduced:
                    measures_findings.append(
                        f"WARNUNG: FM '{fehler_id}' Maßnahmen senken RPZ nicht"
                    )

    return measures_findings, list(measures_findings)


# ---------------------------------------------------------------------------
# Phase 7: Cross-FM + Anlagendaten alignment
# ---------------------------------------------------------------------------

def _check_cross_fm_alignment(fms: list[dict], ad: dict | None) -> tuple[list[str], list[str]]:
    """Return (alignment_findings, warnings) for cross-FM alignment checks."""
    if ad is None:
        return [], []

    alignment_findings = []

    # 7a: Every system in Anlagendaten should have at least one FM
    fm_komponenten = set()
    for fm in fms:
        komp = fm.get("komponente", "")
        if komp:
            fm_komponenten.add(komp.lower())

    for sys_entry in ad.get("systems", []):
        sys_name = sys_entry.get("name", "")
        if sys_name:
            found = any(sys_name.lower() in k for k in fm_komponenten)
            if not found:
                found = any(sys_name.lower() in k or k in sys_name.lower() for k in fm_komponenten)
            if not found:
                alignment_findings.append(
                    f"WARNUNG: System '{sys_name}' hat keine Fehlermodi"
                )

    # 7b: Hazardous substances (WGK>=2 or GHS02/GHS06) should be referenced in FMs
    fm_texts = _fm_texts_joined(fms)
    hazardous_ghs = {"ghs02", "ghs06"}

    for substance in ad.get("substances", ad.get("gefahrstoffe", [])):
        name = substance.get("name", "")
        wgk = substance.get("WGK", substance.get("wgk", 0))
        ghs_codes = [c.lower() for c in substance.get("ghs", substance.get("GHS", []))]

        is_hazardous = False
        try:
            if int(wgk) >= 2:
                is_hazardous = True
        except (ValueError, TypeError):
            pass
        if any(g in hazardous_ghs for g in ghs_codes):
            is_hazardous = True

        if is_hazardous and name and name.lower() not in fm_texts:
            alignment_findings.append(
                f"WARNUNG: Gefahrstoff '{name}' nicht in Fehlermodi referenziert"
            )

    return alignment_findings, list(alignment_findings)


# ---------------------------------------------------------------------------
# Main validation function
# ---------------------------------------------------------------------------

@tool_entry
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
    with FMEAStorage(db_path) as db:
        return _validate_completeness_impl(db, project_id, task_folder)


def _validate_completeness_impl(db: FMEAStorage, project_id: int, task_folder: str = None) -> dict:
    warnings = []
    details = {}

    # Load all failure modes for this project
    try:
        fms = db.get_all_failure_modes_with_rpz(project_id)
    except Exception:
        fms = []

    if not fms:
        return {
            "passed": False,
            "warnings": ["Keine Fehlermodi in der DB gefunden."],
            "details": {}
        }

    # Load Anlagendaten if task_folder is provided
    ad = None
    if task_folder:
        base = Path(__file__).parent.parent / "tasks" / task_folder
        anlagendaten_path = base / "anlagendaten.json"
        if anlagendaten_path.exists():
            with open(anlagendaten_path, "r") as f:
                ad = json.load(f)

    # --- Phase 1: Category coverage ---
    cat_details, cat_warnings = _check_categories(fms, ad)
    details["categories"] = cat_details
    warnings.extend(cat_warnings)

    # --- Phase 2: Gefahrenfelder coverage ---
    gf_details, gf_warnings = _check_gefahrenfelder(fms, ad)
    details["gefahrenfelder"] = gf_details
    warnings.extend(gf_warnings)

    # --- Phase 3: Utility/interface coverage ---
    util_details, util_warnings = _check_utilities(fms, ad)
    if util_details is not None:
        details["utilities"] = util_details
    warnings.extend(util_warnings)

    # --- Phase 4: CCF candidates ---
    ccf_candidates, ccf_warnings = _check_ccf_candidates(fms, ad)
    if ad is not None:
        details["ccf_candidates"] = ccf_candidates
    warnings.extend(ccf_warnings)

    # --- Phase 5: S/O/D plausibility ---
    sod_findings, sod_warnings = _check_sod_plausibility(fms, ad)
    details["sod_plausibility"] = sod_findings
    warnings.extend(sod_warnings)

    # --- Phase 6: Measures effectiveness ---
    meas_findings, meas_warnings = _check_measures_effectiveness(fms, db)
    details["measures_effectiveness"] = meas_findings
    warnings.extend(meas_warnings)

    # --- Phase 7: Cross-FM + Anlagendaten alignment ---
    align_findings, align_warnings = _check_cross_fm_alignment(fms, ad)
    details["alignment"] = align_findings
    warnings.extend(align_warnings)

    # passed = False if any KRITISCH finding exists
    passed = not any(w.startswith("KRITISCH:") for w in warnings)

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

    if "sod_plausibility" in details and details["sod_plausibility"]:
        lines.append(f"\n--- S/O/D-Plausibilität ({len(details['sod_plausibility'])} Findings) ---")
        for f in details["sod_plausibility"]:
            if f.startswith("KRITISCH:"):
                lines.append(f"  \u26a0 {f}")
            else:
                lines.append(f"  \u26a1 {f}")

    if "measures_effectiveness" in details and details["measures_effectiveness"]:
        lines.append(f"\n--- Maßnahmen-Wirksamkeit ({len(details['measures_effectiveness'])} Findings) ---")
        for f in details["measures_effectiveness"]:
            if f.startswith("KRITISCH:"):
                lines.append(f"  \u26a0 {f}")
            else:
                lines.append(f"  \u26a1 {f}")

    if "alignment" in details and details["alignment"]:
        lines.append(f"\n--- Cross-FM / Anlagendaten-Alignment ({len(details['alignment'])} Findings) ---")
        for f in details["alignment"]:
            if f.startswith("KRITISCH:"):
                lines.append(f"  \u26a0 {f}")
            else:
                lines.append(f"  \u26a1 {f}")

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
