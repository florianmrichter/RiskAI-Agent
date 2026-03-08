"""
FMEA Review Tool -- Human-in-the-Loop Support

Generates formatted review summaries for each analysis step and
processes user feedback back into the database.

Usage:
    from tools.review import get_structure_review, get_ranking_review
    print(get_structure_review(project_id))
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage
from config.fmea_standards import (
    S_SCALE, O_SCALE, D_SCALE,
    RPZ_THRESHOLDS, RPZ_COLORS, RPZ_LABELS,
    classify_rpz, apply_special_rules,
)


def _db(db_path=None):
    return FMEAStorage(db_path)


# ═══════════════════════════════════════════════════════════════
# Schritt 1: Plant Data Review
# ═══════════════════════════════════════════════════════════════

def get_plant_data_review(plant_data: dict) -> str:
    """Format a summary of loaded plant data for human review."""
    lines = ["## Anlagendaten – Zusammenfassung\n"]

    pd = plant_data.get("processDescription", {})
    loc = plant_data.get("location", {})

    lines.append(f"**Anlage:** {plant_data.get('name', '–')}")
    lines.append(f"**Teilanlage:** {plant_data.get('teilanlage_nr', '–')}")
    if pd.get("purpose"):
        lines.append(f"**Zweck:** {pd['purpose']}")
    if pd.get("operatingMode"):
        lines.append(f"**Betriebsart:** {pd['operatingMode']}")
    if loc.get("site"):
        lines.append(f"**Standort:** {loc.get('site', '')} / {loc.get('building', '')} / {loc.get('room', '')}")

    systems = plant_data.get("systems", [])
    lines.append(f"\n**Systeme:** {len(systems)}")
    for sys in systems:
        eq_count = len(sys.get("equipment", []))
        msr_count = len(sys.get("msrEquipment", []))
        safety_count = len(sys.get("safetyFeatures", sys.get("securityFeatures", [])))
        lines.append(f"  - {sys.get('name', '?')} ({sys.get('type', '?')}): "
                      f"{eq_count} Equipment, {msr_count} MSR, {safety_count} Sicherheit")

    feedstocks = plant_data.get("feedstocks", [])
    products = plant_data.get("products", [])
    if feedstocks:
        lines.append(f"\n**Einsatzstoffe:** {', '.join(s.get('name', '?') for s in feedstocks)}")
    if products:
        lines.append(f"**Produkte:** {', '.join(s.get('name', '?') for s in products)}")

    warnings = []
    if not systems:
        warnings.append("Keine Systeme erkannt")
    if not feedstocks:
        warnings.append("Keine Einsatzstoffe definiert")
    for sys in systems:
        if not sys.get("msrEquipment"):
            warnings.append(f"System '{sys.get('name', '?')}' hat keine MSR-Technik")
        if not sys.get("safetyFeatures") and not sys.get("securityFeatures"):
            warnings.append(f"System '{sys.get('name', '?')}' hat keine Sicherheitseinrichtungen")

    if warnings:
        lines.append(f"\n**⚠ Warnungen ({len(warnings)}):**")
        for w in warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Schritt 2: Structure Review
# ═══════════════════════════════════════════════════════════════

def get_structure_review(project_id: int, db_path=None) -> str:
    """Format the component list for human review."""
    db = _db(db_path)
    components = db.get_components(project_id)
    db.close()

    by_system = defaultdict(list)
    for c in components:
        by_system[c.get("system_name", "Unbekannt")].append(c)

    lines = [f"## Strukturanalyse – {len(components)} Komponenten in {len(by_system)} Systemen\n"]

    for sys_name, comps in by_system.items():
        by_kat = defaultdict(int)
        for c in comps:
            by_kat[c["kategorie"]] += 1

        kat_str = ", ".join(f"{v} {k}" for k, v in sorted(by_kat.items()))
        lines.append(f"### {sys_name} ({kat_str})")

        for c in comps:
            lines.append(f"  - `{c['komp_id']}` {c['name']} ({c['typ']}, {c['kategorie']})")

        lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Schritt 3: Function Review
# ═══════════════════════════════════════════════════════════════

def get_function_review(project_id: int, component_id: int = None, db_path=None) -> str:
    """Format functions for human review, optionally filtered to one component."""
    db = _db(db_path)
    components = db.get_components(project_id)

    lines = ["## Funktionsanalyse – Übersicht\n"]

    for comp in components:
        if component_id and comp["id"] != component_id:
            continue

        functions = db.get_functions(comp["id"])
        if not functions:
            lines.append(f"### {comp['name']} (`{comp['komp_id']}`) – Keine Funktionen")
            continue

        lines.append(f"### {comp['name']} (`{comp['komp_id']}`) – {len(functions)} Funktionen")

        for func in functions:
            typ_label = "Haupt" if func["typ"] == "haupt" else "Neben"
            lines.append(f"  - **{func['funktion_id']}** [{typ_label}]: {func['beschreibung']}")

            if func.get("anforderungen"):
                for anf in func["anforderungen"][:3]:
                    param = anf.get("parameter", "?")
                    soll = anf.get("soll", "?")
                    lines.append(f"    - {param}: {soll}")

        lines.append("")

    db.close()
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Schritt 4: Risk Review (einzelner Fehlermodus)
# ═══════════════════════════════════════════════════════════════

def _format_sod_with_neighbors(value: int, scale: dict, label: str) -> list:
    """Format a S/O/D value with its neighboring scale values for context.
    Shows current value plus one above and one below so the reviewer
    can quickly judge if the rating should be higher or lower."""
    lines = []
    info = scale.get(value, ("?", "?"))

    below = value - 1
    above = value + 1

    if below >= 1:
        b_info = scale.get(below, ("?", "?"))
        lines.append(f"    ↓ {label}={below}: {b_info[0]} – {b_info[1]}")
    lines.append(f"  → **{label} = {value}**: {info[0]} – {info[1]}")
    if above <= 10:
        a_info = scale.get(above, ("?", "?"))
        lines.append(f"    ↑ {label}={above}: {a_info[0]} – {a_info[1]}")

    return lines


def _identify_rpz_driver(S: int, O: int, D: int) -> str:
    """Identify which factor contributes most to the RPZ and explain why.
    The 'driver' is the factor whose reduction would most effectively
    lower the overall RPZ."""
    factors = {"S": S, "O": O, "D": D}
    driver_key = max(factors, key=factors.get)
    driver_val = factors[driver_key]

    driver_labels = {
        "S": "Bedeutung (S)",
        "O": "Auftreten (O)",
        "D": "Entdeckung (D)",
    }
    driver_explanations = {
        "S": f"Die Schwere der Auswirkung (S={driver_val}) ist der größte Einzelfaktor. "
             "S lässt sich meist nur durch konstruktive Änderungen senken.",
        "O": f"Die Auftretenswahrscheinlichkeit (O={driver_val}) treibt das Risiko. "
             "Vermeidungsmaßnahmen (Kat. A) können O direkt reduzieren.",
        "D": f"Die Entdeckungswahrscheinlichkeit (D={driver_val}) ist der Haupttreiber. "
             "Bessere Prüfungen oder Überwachung (Kat. B) können D senken.",
    }

    if driver_val == max(factors.values()) and list(factors.values()).count(driver_val) > 1:
        tied = [k for k, v in factors.items() if v == driver_val]
        tied_labels = [driver_labels[k] for k in tied]
        return (f"Mehrere Faktoren gleich hoch ({', '.join(tied_labels)} = {driver_val}). "
                "Maßnahmen sollten bevorzugt O oder D adressieren, da S konstruktionsbedingt "
                "oft schwer änderbar ist.")

    return driver_explanations[driver_key]


def get_risk_review(project_id: int, fehler_id: str = None, db_path=None) -> str:
    """Format a single failure mode for detailed S/O/D review.
    Includes neighboring scale values and driver explanation."""
    db = _db(db_path)

    if fehler_id:
        fm_data = db.get_failure_mode_by_fehler_id(fehler_id)
        if not fm_data:
            db.close()
            return f"Fehlermodus '{fehler_id}' nicht gefunden."
        fms = [fm_data]
    else:
        fms_raw = db.get_all_failure_modes_with_rpz(project_id)
        fms = sorted(fms_raw, key=lambda x: x.get("rpz", 0), reverse=True)

    lines = []
    for fm in fms:
        fm_id = fm["id"]
        ra = db.get_risk_assessment(fm_id)
        causes = db.get_failure_causes(fm_id)
        effects = db.get_failure_effect(fm_id)
        controls = db.get_current_controls(fm_id)

        fid = fm.get("fehler_id", "?")
        lines.append(f"### {fid}: {fm.get('fehlermodus', '?')}")
        lines.append(f"**Fehlerart:** {fm.get('fehlerart', '?')}\n")

        if causes:
            lines.append("**Ursachen:**")
            for c in causes:
                lines.append(f"  - [{c['herkunft']}] {c['beschreibung']}")
            lines.append("")

        if effects:
            lines.append("**Folgen:**")
            for dim in ["mensch", "umwelt", "anlage", "kosten"]:
                desc = effects.get(f"{dim}_beschreibung", "")
                if desc:
                    lines.append(f"  - **{dim.capitalize()}:** {desc}")
            lines.append("")

        if controls:
            lines.append("**Bestehende Controls:**")
            for ctrl in controls:
                lines.append(f"  - [{ctrl['wirkung']}] {ctrl['name']} ({ctrl['typ']})"
                             f"{' – ' + ctrl['beschreibung'] if ctrl.get('beschreibung') else ''}")
            lines.append("")

        if ra:
            S, O, D = ra["S"], ra["O"], ra["D"]
            rpz = ra["rpz"]
            status = ra["rpz_status"]

            lines.append("**Risikobewertung:**")
            lines.append("")
            lines.extend(_format_sod_with_neighbors(S, S_SCALE, "S"))
            if ra.get("begruendung_S"):
                lines.append(f"    Begründung: {ra['begruendung_S']}")
            lines.append("")
            lines.extend(_format_sod_with_neighbors(O, O_SCALE, "O"))
            if ra.get("begruendung_O"):
                lines.append(f"    Begründung: {ra['begruendung_O']}")
            lines.append("")
            lines.extend(_format_sod_with_neighbors(D, D_SCALE, "D"))
            if ra.get("begruendung_D"):
                lines.append(f"    Begründung: {ra['begruendung_D']}")

            lines.append(f"\n  **RPZ = {rpz} ({status.upper()})**")

            lines.append(f"\n  **Treiber-Analyse:** {_identify_rpz_driver(S, O, D)}")

            if ra.get("override_applied"):
                lines.append(f"  Override: {ra['override_applied']}")

        lines.append("\n---\n")

    db.close()
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Schritt 5: Ranking Review
# ═══════════════════════════════════════════════════════════════

def get_ranking_review(project_id: int, db_path=None) -> str:
    """Format the complete risk ranking for human review."""
    db = _db(db_path)
    fms = db.get_all_failure_modes_with_rpz(project_id)
    stats = db.get_project_statistics(project_id)
    db.close()

    fms_sorted = sorted(fms, key=lambda x: x.get("rpz", 0), reverse=True)
    dist = stats.get("rpz_distribution", {})

    lines = ["## Risiko-Ranking – Gesamtübersicht\n"]
    lines.append(f"**Fehlermodi gesamt:** {len(fms_sorted)}")
    lines.append(f"**Verteilung:** "
                 f"{dist.get('kritisch', 0)} kritisch, "
                 f"{dist.get('hoch', 0)} hoch, "
                 f"{dist.get('mittel', 0)} mittel, "
                 f"{dist.get('niedrig', 0)} niedrig\n")

    lines.append("| # | Fehler-ID | Fehlermodus | S | O | D | RPZ | Status |")
    lines.append("|---|-----------|-------------|---|---|---|-----|--------|")

    for i, fm in enumerate(fms_sorted, 1):
        fid = fm.get("fehler_id", "?")
        desc = fm.get("fehlermodus", "?")
        if len(desc) > 60:
            desc = desc[:57] + "..."
        s, o, d = fm.get("S", 0), fm.get("O", 0), fm.get("D", 0)
        rpz = fm.get("rpz", 0)
        status = fm.get("rpz_status", "?").upper()
        lines.append(f"| {i} | {fid} | {desc} | {s} | {o} | {d} | {rpz} | {status} |")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Schritt 6: Measure Review
# ═══════════════════════════════════════════════════════════════

STOP_LABELS = {
    "S": "Substitution",
    "T": "Technisch",
    "O": "Organisatorisch",
    "P": "Persönlich",
}

STOP_ORDER = {"S": 0, "T": 1, "O": 2, "P": 3}


def _sort_measures_by_stop(measures: list) -> list:
    return sorted(measures, key=lambda m: STOP_ORDER.get(m.get("stop_kategorie", ""), 99))


def _build_stop_coverage(measures: list) -> dict:
    """Analyse which STOP categories are covered and how many measures each has."""
    coverage = {}
    for kat in ["S", "T", "O", "P"]:
        kat_measures = [m for m in measures if m.get("stop_kategorie") == kat]
        coverage[kat] = {
            "label": STOP_LABELS[kat],
            "vorhanden": len(kat_measures) > 0,
            "anzahl": len(kat_measures),
        }
    return coverage


def get_measure_review(project_id: int, db_path=None) -> str:
    """Format measures with before/after comparison and STOP coverage for human review."""
    db = _db(db_path)
    fmea_data = db.get_full_fmea_data(project_id)
    db.close()

    fms_with_measures = [fm for fm in fmea_data if fm.get("measures")]

    if not fms_with_measures:
        return "## Maßnahmen – Keine Maßnahmen definiert"

    total_measures = sum(len(fm["measures"]) for fm in fms_with_measures)
    lines = ["## Maßnahmen – Vorher/Nachher-Vergleich (STOP + ABE)\n"]
    lines.append(f"**{total_measures} Maßnahmen** "
                 f"für **{len(fms_with_measures)} Fehlermodi**\n")

    all_measures = [m for fm in fms_with_measures for m in fm.get("measures", [])]
    global_coverage = _build_stop_coverage(all_measures)
    lines.append("### STOP-Abdeckung (Gesamtprojekt)\n")
    lines.append("| STOP-Kategorie | Abgedeckt | Anzahl |")
    lines.append("|----------------|-----------|--------|")
    for kat in ["S", "T", "O", "P"]:
        c = global_coverage[kat]
        check = "Ja" if c["vorhanden"] else "**Nein**"
        lines.append(f"| {c['label']} ({kat}) | {check} | {c['anzahl']} |")
    lines.append("")

    missing = [STOP_LABELS[k] for k in ["S", "T", "O", "P"]
               if not global_coverage[k]["vorhanden"]]
    if missing:
        lines.append(f"**Fehlende STOP-Kategorien:** {', '.join(missing)}\n")

    for fm in sorted(fms_with_measures, key=lambda x: x.get("rpz", 0), reverse=True):
        fid = fm.get("fehler_id", "?")
        ra = fm.get("risk", {})
        rpz_before = ra.get("rpz", 0)
        status_before = ra.get("rpz_status", "?")

        lines.append(f"### {fid}: {fm.get('fehlermodus', '?')}")
        lines.append(f"**Vorher:** S={ra.get('S', '?')} O={ra.get('O', '?')} D={ra.get('D', '?')} "
                     f"→ RPZ={rpz_before} ({status_before.upper()})\n")

        fm_coverage = _build_stop_coverage(fm["measures"])
        fm_missing = [STOP_LABELS[k] for k in ["S", "T", "O", "P"]
                      if not fm_coverage[k]["vorhanden"]]
        if fm_missing:
            lines.append(f"  *Keine Maßnahmen in:* {', '.join(fm_missing)}\n")

        sorted_measures = _sort_measures_by_stop(fm["measures"])

        current_stop = None
        for m in sorted_measures:
            stop_kat = m.get("stop_kategorie", "?")
            if stop_kat != current_stop:
                current_stop = stop_kat
                stop_label = STOP_LABELS.get(stop_kat, stop_kat)
                lines.append(f"  **── {stop_label} ({stop_kat}) ──**\n")

            abe = m.get("abe_kategorie", "?")
            iteration = m.get("iteration", 1)
            iter_tag = f" [Iteration {iteration}]" if iteration > 1 else ""
            lines.append(f"  **[{abe}] {m.get('name', '?')}**{iter_tag}")
            lines.append(f"  {m.get('beschreibung', '')}")
            rpz_new = m.get("rpz_neu", "?")
            status_new = m.get("rpz_status_neu", "?")
            lines.append(f"  **Nachher:** S={m.get('S_neu', '?')} O={m.get('O_neu', '?')} "
                         f"D={m.get('D_neu', '?')} → RPZ={rpz_new} ({str(status_new).upper()})")
            if m.get("begruendung"):
                lines.append(f"  Begründung: {m['begruendung']}")
            lines.append("")

        lines.append("---\n")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Validation Report
# ═══════════════════════════════════════════════════════════════

def get_validation_report(project_id: int, db_path=None) -> str:
    """Run consistency checks and return a validation report."""
    db = _db(db_path)
    components = db.get_components(project_id)
    fmea_data = db.get_full_fmea_data(project_id)

    warnings = []
    infos = []

    # 1. Completeness: every function should have failure modes
    for comp in components:
        functions = db.get_functions(comp["id"])
        for func in functions:
            fms = db.get_failure_modes(func["id"])
            if not fms:
                warnings.append(
                    f"Funktion '{func['funktion_id']}' ({func['beschreibung'][:50]}) "
                    f"hat keine Fehlermodi"
                )

    # 2. Plausibility: high severity without measures + STOP coverage
    for fm in fmea_data:
        ra = fm.get("risk", {})
        S = ra.get("S", 0)
        rpz = ra.get("rpz", 0)
        rpz_status = ra.get("rpz_status", "niedrig")

        if S >= 9 and not fm.get("measures"):
            warnings.append(
                f"{fm.get('fehler_id', '?')}: S={S} aber keine Maßnahmen definiert "
                f"(RPZ={rpz}, {rpz_status})"
            )

        if rpz_status in ("kritisch", "hoch") and not fm.get("measures"):
            warnings.append(
                f"{fm.get('fehler_id', '?')}: Status={rpz_status} aber keine Maßnahmen"
            )

        if fm.get("measures") and rpz_status in ("kritisch", "hoch"):
            stop_kats = {m.get("stop_kategorie") for m in fm["measures"] if m.get("stop_kategorie")}
            missing_stop = [k for k in ["S", "T", "O", "P"] if k not in stop_kats]
            if missing_stop:
                missing_labels = [STOP_LABELS.get(k, k) for k in missing_stop]
                warnings.append(
                    f"{fm.get('fehler_id', '?')}: Status={rpz_status}, "
                    f"fehlende STOP-Kategorien: {', '.join(missing_labels)}"
                )

    # 3. S/O/D consistency: similar failure types should have similar ratings
    by_type = defaultdict(list)
    for fm in fmea_data:
        by_type[fm.get("fehlerart", "?")].append(fm)

    for ftype, fms in by_type.items():
        if len(fms) < 2:
            continue
        s_values = [fm.get("S", 0) for fm in fms]
        s_range = max(s_values) - min(s_values)
        if s_range >= 5:
            fids = [fm.get("fehler_id", "?") for fm in fms]
            warnings.append(
                f"Fehlerart '{ftype}': S-Werte schwanken stark "
                f"(min={min(s_values)}, max={max(s_values)}). "
                f"Betroffene: {', '.join(fids[:3])}"
            )

    # 4. Duplicate detection: similar failure mode descriptions
    descriptions = [(fm.get("fehler_id", "?"), fm.get("fehlermodus", "").lower()) for fm in fmea_data]
    for i, (id1, desc1) in enumerate(descriptions):
        for j, (id2, desc2) in enumerate(descriptions[i + 1:], i + 1):
            words1 = set(desc1.split())
            words2 = set(desc2.split())
            if len(words1) > 3 and len(words2) > 3:
                overlap = len(words1 & words2) / max(len(words1 | words2), 1)
                if overlap > 0.7:
                    warnings.append(
                        f"Mögliche Dopplung: {id1} und {id2} "
                        f"(Übereinstimmung {overlap:.0%})"
                    )

    # 5. Special rules check
    for fm in fmea_data:
        ra = fm.get("risk", {})
        S, O, D = ra.get("S", 0), ra.get("O", 0), ra.get("D", 0)
        current_status = ra.get("rpz_status", "niedrig")
        new_status, rule_desc = apply_special_rules(S, O, D, current_status)
        if rule_desc:
            warnings.append(
                f"{fm.get('fehler_id', '?')}: Sonderregel greift – {rule_desc} "
                f"(aktuell: {current_status} → sollte: {new_status})"
            )

    db.close()

    lines = ["## Validierungsbericht\n"]
    lines.append(f"**Fehlermodi geprüft:** {len(fmea_data)}")
    lines.append(f"**Warnungen:** {len(warnings)}")
    lines.append(f"**Hinweise:** {len(infos)}\n")

    if warnings:
        lines.append("### Warnungen")
        for i, w in enumerate(warnings, 1):
            lines.append(f"  {i}. {w}")
        lines.append("")

    if infos:
        lines.append("### Hinweise")
        for i, info in enumerate(infos, 1):
            lines.append(f"  {i}. {info}")
        lines.append("")

    if not warnings and not infos:
        lines.append("Keine Probleme gefunden. Analyse ist konsistent.")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# Feedback Processing
# ═══════════════════════════════════════════════════════════════

def update_risk_assessment(project_id: int, fehler_id: str,
                           S: int = None, O: int = None, D: int = None,
                           begruendung_S: str = None,
                           begruendung_O: str = None,
                           begruendung_D: str = None,
                           angepasst_von: str = "nutzer",
                           db_path=None) -> dict:
    """
    Update S/O/D values for a failure mode based on user feedback.
    Recalculates RPZ and applies special rules.
    Returns the updated assessment.
    """
    db = _db(db_path)
    fm = db.get_failure_mode_by_fehler_id(fehler_id)
    if not fm:
        db.close()
        raise ValueError(f"Fehlermodus '{fehler_id}' nicht gefunden")

    ra = db.get_risk_assessment(fm["id"])
    if not ra:
        db.close()
        raise ValueError(f"Keine Risikobewertung für '{fehler_id}'")

    new_S = S if S is not None else ra["S"]
    new_O = O if O is not None else ra["O"]
    new_D = D if D is not None else ra["D"]
    new_rpz = new_S * new_O * new_D
    new_status = classify_rpz(new_rpz)

    final_status, rule_desc = apply_special_rules(new_S, new_O, new_D, new_status)

    override_parts = []
    if ra.get("override_applied"):
        override_parts.append(ra["override_applied"])
    if rule_desc:
        override_parts.append(f"Sonderregel: {rule_desc}")

    changes = []
    if S is not None and S != ra["S"]:
        changes.append(f"S: {ra['S']}→{S}")
    if O is not None and O != ra["O"]:
        changes.append(f"O: {ra['O']}→{O}")
    if D is not None and D != ra["D"]:
        changes.append(f"D: {ra['D']}→{D}")

    if changes:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        override_parts.append(f"[{angepasst_von} {timestamp}] {', '.join(changes)}")

    update_kwargs = {
        "S": new_S, "O": new_O, "D": new_D,
        "rpz": new_rpz, "rpz_status": final_status,
        "override_applied": " | ".join(override_parts) if override_parts else None,
    }
    if begruendung_S is not None:
        update_kwargs["begruendung_S"] = begruendung_S
    if begruendung_O is not None:
        update_kwargs["begruendung_O"] = begruendung_O
    if begruendung_D is not None:
        update_kwargs["begruendung_D"] = begruendung_D

    db.update_risk_assessment(fm["id"], **update_kwargs)
    db.close()

    return {
        "fehler_id": fehler_id,
        "S": new_S, "O": new_O, "D": new_D,
        "rpz": new_rpz, "rpz_status": final_status,
        "changes": changes,
        "special_rule": rule_desc,
    }


def update_component(project_id: int, komp_id: str, db_path=None, **kwargs) -> dict:
    """Update component attributes (e.g., system_name, typ) based on user feedback."""
    db = _db(db_path)
    comp = db.get_component_by_komp_id(komp_id)
    if not comp:
        db.close()
        raise ValueError(f"Komponente '{komp_id}' nicht gefunden")

    allowed = {"name", "typ", "kategorie", "system_name", "beschreibung"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [komp_id]
        db.conn.execute(f"UPDATE components SET {set_clause} WHERE komp_id = ?", values)
        db.conn.commit()

    result = db.get_component_by_komp_id(komp_id)
    db.close()
    return result
