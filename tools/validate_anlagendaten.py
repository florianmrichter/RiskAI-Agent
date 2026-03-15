"""
Gate 1: Validates anlagendaten.json before FMEA analysis.

Checks:
1. Schema completeness (required fields)
2. FMEA-critical fields (ExZone, SIL, Flammpunkt, etc.)
3. Value ranges (temperature, pressure, volume, flash point)
4. Cross-references (feedstocks ↔ systems, media ↔ systems)
5. Consistency rules (ATEX↔Flammpunkt, WGK↔AwSV, toxicity↔PSA, operating≤design)

Usage:
    from tools.validate_anlagendaten import validate_anlagendaten
    result = validate_anlagendaten("Buechi_Glasreaktor_15L_20TA43")
    # result = {"passed": bool, "fmea_readiness_pct": int, "critical": [...], ...}
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_numeric(value) -> float | None:
    """Extract first numeric value from a string like '6', '80-100', '-20 °C'."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    m = re.search(r'-?\d+(?:\.\d+)?', s)
    if m:
        return float(m.group())
    return None


def _get_design_value(system: dict, key: str) -> float | None:
    """Get a numeric value from system.designData by key."""
    for entry in system.get("designData", []):
        if entry.get("key") == key:
            return _parse_numeric(entry.get("value"))
    return None


def _get_process_condition_value(system: dict, key: str) -> float | None:
    """Get a numeric value from system.processConditions by key."""
    pc = system.get("processConditions", {})
    val = pc.get(key)
    return _parse_numeric(val)


def _has_toxic_h_statements(h_phrases_str: str) -> bool:
    """Check if H-phrases string contains H300-H311 (acute toxicity)."""
    if not h_phrases_str:
        return False
    # Extract all H-numbers
    nums = re.findall(r'H(\d+)', str(h_phrases_str))
    for n in nums:
        num = int(n)
        if 300 <= num <= 311:
            return True
    return False


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------

REQUIRED_ROOT_FIELDS = [
    "teilanlage_nr",
    "bezeichnung",
    "processDescription",
    "systems",
    "feedstocks",
    "media",
]


def validate_anlagendaten(task_folder: str, schema_path: str = None) -> dict:
    """
    Validate anlagendaten.json for FMEA readiness.

    Args:
        task_folder: Relative path under tasks/Risikoanalyse/, e.g. 'Buechi_Glasreaktor_15L_20TA43'
        schema_path: Optional path to schema JSON (unused — checks are hardcoded)

    Returns:
        {
            "passed": bool,
            "fmea_readiness_pct": int,
            "critical": [str],
            "warnings": [str],
            "info": [str],
            "details": {}
        }
    """
    base = Path(__file__).parent.parent / "tasks" / "Risikoanalyse" / task_folder
    ad_path = base / "anlagendaten.json"

    critical = []
    warnings = []
    info = []
    details = {}

    # --- Load file ---
    if not ad_path.exists():
        return {
            "passed": False,
            "fmea_readiness_pct": 0,
            "critical": [f"anlagendaten.json nicht gefunden: {ad_path}"],
            "warnings": [],
            "info": [],
            "details": {},
        }

    with open(ad_path, "r", encoding="utf-8") as f:
        ad = json.load(f)

    # -----------------------------------------------------------------------
    # 1. Schema completeness — required root fields
    # -----------------------------------------------------------------------
    missing_root = []
    for field in REQUIRED_ROOT_FIELDS:
        val = ad.get(field)
        if val is None or val == "" or val == []:
            missing_root.append(field)

    if missing_root:
        critical.append(f"Pflichtfelder fehlen: {', '.join(missing_root)}")
    details["schema_completeness"] = {
        "required": REQUIRED_ROOT_FIELDS,
        "missing": missing_root,
    }

    # -----------------------------------------------------------------------
    # 2. FMEA-critical fields
    # -----------------------------------------------------------------------
    fmea_issues = []

    systems = ad.get("systems", [])
    feedstocks = ad.get("feedstocks", [])
    media = ad.get("media", [])
    process_desc = ad.get("processDescription", {})

    # 2a. Per system: ExZone in parameters
    systems_without_exzone = []
    for sys_entry in systems:
        params = sys_entry.get("parameters", {})
        if not params.get("ExZone"):
            systems_without_exzone.append(sys_entry.get("name", "?"))
    if systems_without_exzone:
        fmea_issues.append(f"ExZone fehlt in parameters: {', '.join(systems_without_exzone)}")

    # 2b. Per system: SIL in msrEquipment (check if ANY msr has sil/silLevel)
    systems_without_sil_info = []
    for sys_entry in systems:
        msr_list = sys_entry.get("msrEquipment", [])
        has_any_sil = False
        for msr in msr_list:
            sil_val = msr.get("sil") or msr.get("silLevel")
            if sil_val is not None and sil_val != "":
                has_any_sil = True
                break
        if msr_list and not has_any_sil:
            # Only flag as info — many small plants have no SIL-rated instruments
            systems_without_sil_info.append(sys_entry.get("name", "?"))
    if systems_without_sil_info:
        info.append(f"Kein SIL-Eintrag in MSR-Equipment: {', '.join(systems_without_sil_info)}")

    # 2c. Per feedstock: flashPoint
    feedstocks_without_fp = []
    for fs in feedstocks:
        # Check both schema variants: properties.flashPoint and parameters.flashPoint
        fp = None
        props = fs.get("properties", {})
        if isinstance(props, dict):
            fp = props.get("flashPoint")
        if not fp:
            params = fs.get("parameters", {})
            if isinstance(params, dict):
                fp = params.get("flashPoint")
        if not fp:
            feedstocks_without_fp.append(fs.get("name", "?"))
    if feedstocks_without_fp:
        fmea_issues.append(f"Flammpunkt fehlt bei Feedstocks: {', '.join(feedstocks_without_fp)}")

    # 2d. failureConsequence in media
    media_without_fc = []
    for m in media:
        if not m.get("failureConsequence"):
            media_without_fc.append(m.get("name", "?"))
    if media_without_fc:
        info.append(f"failureConsequence fehlt bei Media: {', '.join(media_without_fc)}")

    # 2e. operatingStates in processDescription
    if not process_desc.get("operatingStates"):
        fmea_issues.append("operatingStates fehlt in processDescription")

    # 2f. knownIncidents in processDescription
    if not process_desc.get("knownIncidents") and not ad.get("betriebserfahrungen"):
        info.append("knownIncidents/betriebserfahrungen nicht dokumentiert")

    if fmea_issues:
        for issue in fmea_issues:
            critical.append(f"FMEA-kritisch: {issue}")

    details["fmea_critical"] = {
        "systems_without_exzone": systems_without_exzone,
        "systems_without_sil": systems_without_sil_info,
        "feedstocks_without_flashpoint": feedstocks_without_fp,
        "media_without_failureconsequence": media_without_fc,
        "missing_operating_states": not bool(process_desc.get("operatingStates")),
    }

    # -----------------------------------------------------------------------
    # 3. Value ranges
    # -----------------------------------------------------------------------
    range_issues = []

    RANGES = {
        "Temperatur": (-200, 1000, "°C"),
        "Druck": (-1, 500, "barg"),
        "Flammpunkt": (-200, 500, "°C"),
    }

    # 3a. Check designData in systems
    temp_keys = ["MinTemperatur", "MaxTemperatur", "Betriebstemperatur"]
    pressure_keys = ["MinDruck", "MaxDruck", "DesignDruck", "Betriebsdruck"]
    volume_keys = ["Nennvolumen", "MaxFüllvolumen"]

    for sys_entry in systems:
        sys_name = sys_entry.get("name", "?")
        for key in temp_keys:
            val = _get_design_value(sys_entry, key)
            if val is not None:
                lo, hi, unit = RANGES["Temperatur"]
                if val < lo or val > hi:
                    range_issues.append(f"{sys_name}.{key}={val}{unit} außerhalb [{lo}..{hi}]")

        for key in pressure_keys:
            val = _get_design_value(sys_entry, key)
            if val is not None:
                lo, hi, unit = RANGES["Druck"]
                if val < lo or val > hi:
                    range_issues.append(f"{sys_name}.{key}={val}{unit} außerhalb [{lo}..{hi}]")

        for key in volume_keys:
            val = _get_design_value(sys_entry, key)
            if val is not None and val < 0:
                range_issues.append(f"{sys_name}.{key}={val} — Volumen kann nicht negativ sein")

    # 3b. Check feedstock flash points
    for fs in feedstocks:
        fs_name = fs.get("name", "?")
        fp_val = None
        props = fs.get("properties", {})
        if isinstance(props, dict):
            fp_val = _parse_numeric(props.get("flashPoint"))
        if fp_val is None:
            params = fs.get("parameters", {})
            if isinstance(params, dict):
                fp_val = _parse_numeric(params.get("flashPoint"))
        if fp_val is not None:
            lo, hi, unit = RANGES["Flammpunkt"]
            if fp_val < lo or fp_val > hi:
                range_issues.append(f"Feedstock {fs_name}: Flammpunkt={fp_val}{unit} außerhalb [{lo}..{hi}]")

    if range_issues:
        for issue in range_issues:
            critical.append(f"Wertebereich: {issue}")

    details["value_ranges"] = {"issues": range_issues}

    # -----------------------------------------------------------------------
    # 4. Cross-references
    # -----------------------------------------------------------------------
    xref_issues = []

    # 4a. Feedstocks must appear in at least one system's substanceProcessConditions
    all_spc_substances = set()
    for sys_entry in systems:
        spc = sys_entry.get("substanceProcessConditions", {})
        if isinstance(spc, dict):
            all_spc_substances.update(spc.keys())
        # Also check substances.feedstocks list
        subst = sys_entry.get("substances", {})
        if isinstance(subst, dict):
            for cat_list in subst.values():
                if isinstance(cat_list, list):
                    all_spc_substances.update(cat_list)

    for fs in feedstocks:
        fs_name = fs.get("name", "")
        if fs_name and fs_name not in all_spc_substances:
            xref_issues.append(f"Feedstock '{fs_name}' nicht in substanceProcessConditions referenziert")

    # 4b. Media.anschluss must reference existing system (if field exists)
    system_names = {s.get("name", "") for s in systems}
    system_names_lower = {n.lower() for n in system_names if n}
    for m in media:
        anschluss = m.get("anschluss")
        if anschluss and isinstance(anschluss, str):
            # Check if the anschluss text references any known system
            found = any(sn in anschluss.lower() for sn in system_names_lower if sn)
            if not found:
                xref_issues.append(f"Media '{m.get('name', '?')}' Anschluss '{anschluss}' referenziert kein bekanntes System")

    # 4c. connectedSystems consistency
    for sys_entry in systems:
        sys_name = sys_entry.get("name", "?")
        cs = sys_entry.get("connectedSystems", {})
        if isinstance(cs, dict):
            for direction in ["upstream", "downstream"]:
                for connected in cs.get(direction, []):
                    # connected can be string or dict
                    ref_name = None
                    if isinstance(connected, str):
                        ref_name = connected
                    elif isinstance(connected, dict):
                        ref_name = connected.get("system", "")
                    # We don't flag out-of-scope as an issue
                    if ref_name and "nicht im scope" not in ref_name.lower():
                        # Check if this references a known system
                        ref_lower = ref_name.lower()
                        found = any(sn in ref_lower or ref_lower in sn for sn in system_names_lower if sn)
                        if not found:
                            info.append(f"connectedSystem '{ref_name}' ({direction} von {sys_name}) nicht als System definiert")

    if xref_issues:
        for issue in xref_issues:
            warnings.append(f"Cross-Referenz: {issue}")

    details["cross_references"] = {"issues": xref_issues}

    # -----------------------------------------------------------------------
    # 5. Consistency rules
    # -----------------------------------------------------------------------
    consistency_issues_critical = []
    consistency_issues_warning = []

    # 5a. ExZone → at least one feedstock must have flashPoint
    has_exzone = any(
        sys_entry.get("parameters", {}).get("ExZone")
        for sys_entry in systems
    )
    has_any_flashpoint = False
    for fs in feedstocks:
        props = fs.get("properties", {})
        params = fs.get("parameters", {})
        if isinstance(props, dict) and props.get("flashPoint"):
            has_any_flashpoint = True
            break
        if isinstance(params, dict) and params.get("flashPoint"):
            has_any_flashpoint = True
            break
    if has_exzone and not has_any_flashpoint:
        consistency_issues_critical.append(
            "ExZone definiert, aber kein Feedstock hat einen Flammpunkt — ATEX-Bewertung unvollständig"
        )

    # 5b. WGK >= 2 → awsv.anlage_awsv_relevant should be true
    has_wgk_ge2 = False
    for fs in feedstocks:
        wgk = None
        props = fs.get("properties", {})
        params = fs.get("parameters", {})
        if isinstance(props, dict):
            wgk = _parse_numeric(props.get("wgk"))
        if wgk is None and isinstance(params, dict):
            wgk = _parse_numeric(params.get("wgk"))
        # Also check hazards.wgk
        hazards = fs.get("hazards", {})
        if isinstance(hazards, dict) and wgk is None:
            wgk = _parse_numeric(hazards.get("wgk"))
        if wgk is not None and wgk >= 2:
            has_wgk_ge2 = True
            break
    awsv = ad.get("awsv", {})
    if has_wgk_ge2 and isinstance(awsv, dict) and not awsv.get("anlage_awsv_relevant"):
        consistency_issues_warning.append(
            "WGK >= 2 bei mindestens einem Feedstock, aber awsv.anlage_awsv_relevant ist nicht true"
        )

    # 5c. Toxic H-statements (H300-H311) → PSA should be defined
    has_toxic = False
    for fs in feedstocks:
        h_str = None
        props = fs.get("properties", {})
        params = fs.get("parameters", {})
        hazards = fs.get("hazards", {})
        if isinstance(hazards, dict):
            h_list = hazards.get("hStatements", [])
            if isinstance(h_list, list):
                h_str = ", ".join(h_list)
            elif isinstance(h_list, str):
                h_str = h_list
        if not h_str and isinstance(params, dict):
            h_str = params.get("hPhrases", "")
        if not h_str and isinstance(props, dict):
            h_str = props.get("hStatements", "")
        if _has_toxic_h_statements(h_str):
            has_toxic = True
            break
    psa = ad.get("psa")
    if has_toxic and not psa:
        consistency_issues_warning.append(
            "Toxische H-Sätze (H300-H311) vorhanden, aber kein PSA-Abschnitt definiert"
        )

    # 5d. Operating conditions ≤ design limits
    for sys_entry in systems:
        sys_name = sys_entry.get("name", "?")

        # Betriebsdruck ≤ DesignDruck (or MaxDruck)
        op_pressure = _get_design_value(sys_entry, "Betriebsdruck")
        if op_pressure is None:
            op_pressure = _get_process_condition_value(sys_entry, "MaxBetriebsdruck")
        design_pressure = _get_design_value(sys_entry, "DesignDruck")
        if design_pressure is None:
            design_pressure = _get_design_value(sys_entry, "MaxDruck")
        if op_pressure is not None and design_pressure is not None:
            if op_pressure > design_pressure:
                consistency_issues_critical.append(
                    f"{sys_name}: Betriebsdruck ({op_pressure}) > Auslegungsdruck ({design_pressure})"
                )

        # Betriebstemperatur ≤ MaxTemperatur
        op_temp = _get_design_value(sys_entry, "Betriebstemperatur")
        if op_temp is None:
            op_temp = _get_process_condition_value(sys_entry, "MaxBetriebstemperatur")
        max_temp = _get_design_value(sys_entry, "MaxTemperatur")
        if op_temp is not None and max_temp is not None:
            if op_temp > max_temp:
                consistency_issues_critical.append(
                    f"{sys_name}: Betriebstemperatur ({op_temp}) > MaxTemperatur ({max_temp})"
                )

    for issue in consistency_issues_critical:
        critical.append(f"Konsistenz: {issue}")
    for issue in consistency_issues_warning:
        warnings.append(f"Konsistenz: {issue}")

    details["consistency"] = {
        "critical": consistency_issues_critical,
        "warnings": consistency_issues_warning,
    }

    # -----------------------------------------------------------------------
    # Result
    # -----------------------------------------------------------------------
    passed = len(critical) == 0
    fmea_readiness_pct = max(0, 100 - (len(critical) * 10 + len(warnings) * 3))

    return {
        "passed": passed,
        "fmea_readiness_pct": fmea_readiness_pct,
        "critical": critical,
        "warnings": warnings,
        "info": info,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def format_report(result: dict) -> str:
    """Format validation result as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("Gate 1: Anlagendaten-Validierung")
    lines.append("=" * 60)

    status = "BESTANDEN" if result["passed"] else "NICHT BESTANDEN"
    lines.append(f"\nStatus: {status}")
    lines.append(f"FMEA-Readiness: {result['fmea_readiness_pct']}%")
    lines.append(f"Critical: {len(result['critical'])}  |  Warnings: {len(result['warnings'])}  |  Info: {len(result['info'])}")

    if result["critical"]:
        lines.append("\n--- Critical ---")
        for i, c in enumerate(result["critical"], 1):
            lines.append(f"  {i}. {c}")

    if result["warnings"]:
        lines.append("\n--- Warnings ---")
        for i, w in enumerate(result["warnings"], 1):
            lines.append(f"  {i}. {w}")

    if result["info"]:
        lines.append("\n--- Info ---")
        for i, inf in enumerate(result["info"], 1):
            lines.append(f"  {i}. {inf}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gate 1: Anlagendaten-Validierung")
    parser.add_argument("task_folder", help="Relativer Pfad unter tasks/Risikoanalyse/")
    parser.add_argument("--schema", default=None, help="Optionaler Pfad zum Schema JSON")
    args = parser.parse_args()

    result = validate_anlagendaten(args.task_folder, args.schema)
    print(format_report(result))
