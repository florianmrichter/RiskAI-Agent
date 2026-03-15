"""
FMEA Goldstandard Eval — End-to-End Qualitätsprüfung

Prüft die inhaltliche Korrektheit von FMEA-Bewertungen auf 4 Ebenen:

1. FORMALE KORREKTHEIT
   - RPZ-Mathematik (S×O×D = RPZ)
   - RPZ-Klassifizierung (kritisch/hoch/mittel/niedrig)
   - Sonderregeln (S>=9 → hoch, D>=9&S>=7 → kritisch)
   - Safety Overrides (Ex-Schutz → S>=10, Gefahrstoff → S>=9, etc.)

2. VOLLSTÄNDIGKEIT
   - Konfidenzfelder (daten_konfidenz, agent_konfidenz, daten_quelle)
   - Begründungen (begruendung_S/O/D)
   - Maßnahmen bei RPZ >= 100
   - Kontext-Beschreibung, Controls, Ursachen, Folgen

3. PLAUSIBILITÄT
   - S-Werte bei bekanntem Kontext (Ex-Zone, Gefahrstoffe, Sicherheitsbauteile)
   - O-Werte vs. CCPS/OREDA-Referenz (wenn daten_quelle angegeben)
   - Konsistenz: Ähnliche Fehlermodi → ähnliche Bewertungen

4. GOLDSTANDARD-VERGLEICH (nach Testmodus-Run)
   - Exportiert bestehende Bewertungen als Referenz-JSON
   - Vergleicht neue Bewertungen gegen Referenz → Abweichungs-Score

Usage:
    # Vollständige Prüfung eines Projekts:
    python tests/eval_goldstandard.py --project-id 1

    # Goldstandard exportieren (für spätere Vergleiche):
    python tests/eval_goldstandard.py --export --project-id 3

    # Vergleich gegen Goldstandard:
    python tests/eval_goldstandard.py --compare goldstandard_buechi.json --project-id 3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.fmea_standards import (
    classify_rpz, apply_special_rules, SAFETY_OVERRIDES, S_SCALE, O_SCALE, D_SCALE
)
from tools.storage import FMEAStorage


def _load_all_assessments(db: FMEAStorage, project_id: int) -> list[dict]:
    """Lade alle Bewertungen mit vollem Kontext."""
    rows = db.conn.execute("""
        SELECT fm.id as fm_id, fm.fehler_id, fm.fehlermodus, fm.fehlerart,
               fm.kontext_beschreibung, fm.controls_einschraenkung, fm.empfehlung,
               ra.S, ra.O, ra.D, ra.rpz, ra.rpz_status,
               ra.begruendung_S, ra.begruendung_O, ra.begruendung_D,
               ra.daten_konfidenz, ra.agent_konfidenz, ra.daten_quelle,
               ra.override_applied,
               c.komp_id, c.name as komponente, c.typ as komp_typ,
               c.parameters_json as komp_params, c.kontext_json as komp_kontext,
               p.name as projekt_name
        FROM risk_assessments ra
        JOIN failure_modes fm ON ra.failure_mode_id = fm.id
        JOIN functions f ON fm.function_id = f.id
        JOIN components c ON f.component_id = c.id
        JOIN projects p ON c.project_id = p.id
        WHERE c.project_id = ?
    """, (project_id,)).fetchall()
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════
# Eval 1: Formale Korrektheit
# ═══════════════════════════════════════════════════════════════

def eval_formal(assessments: list[dict]) -> dict:
    """Prüft RPZ-Mathematik, Klassifizierung und Sonderregeln."""
    results = {"total": 0, "passed": 0, "errors": []}

    for a in assessments:
        results["total"] += 1
        errors = []

        # 1a. RPZ-Mathematik
        expected_rpz = a["S"] * a["O"] * a["D"]
        if a["rpz"] != expected_rpz:
            errors.append(f"RPZ-MATH: {a['rpz']} != {a['S']}×{a['O']}×{a['D']}={expected_rpz}")

        # 1b. Basis-Klassifizierung
        base_status = classify_rpz(a["rpz"])

        # 1c. Sonderregeln anwenden
        final_status, rule = apply_special_rules(a["S"], a["O"], a["D"], base_status)

        if a["rpz_status"] != final_status:
            errors.append(
                f"KLASSIFIZIERUNG: ist '{a['rpz_status']}', soll '{final_status}'"
                f" (RPZ={a['rpz']}, S={a['S']}, O={a['O']}, D={a['D']})"
                f"{f' — Sonderregel: {rule}' if rule else ''}"
            )

        # 1d. S/O/D-Wertebereiche
        for field, value in [("S", a["S"]), ("O", a["O"]), ("D", a["D"])]:
            if not (1 <= value <= 10):
                errors.append(f"WERTEBEREICH: {field}={value} nicht in [1,10]")

        if errors:
            for e in errors:
                results["errors"].append(f"{a['fehler_id']}: {e}")
        else:
            results["passed"] += 1

    return results


# ═══════════════════════════════════════════════════════════════
# Eval 2: Vollständigkeit
# ═══════════════════════════════════════════════════════════════

def eval_completeness(assessments: list[dict], db: FMEAStorage) -> dict:
    """Prüft ob alle Pflichtfelder befüllt sind."""
    results = {"total": 0, "complete": 0, "errors": []}

    for a in assessments:
        results["total"] += 1
        missing = []

        # Konfidenzfelder
        if not a.get("daten_konfidenz"):
            missing.append("daten_konfidenz")
        if not a.get("agent_konfidenz"):
            missing.append("agent_konfidenz")
        if not a.get("daten_quelle"):
            missing.append("daten_quelle")

        # Begründungen
        if not a.get("begruendung_S"):
            missing.append("begruendung_S")
        if not a.get("begruendung_O"):
            missing.append("begruendung_O")
        if not a.get("begruendung_D"):
            missing.append("begruendung_D")

        # Kontext
        if not a.get("kontext_beschreibung") or len(a.get("kontext_beschreibung", "")) < 20:
            missing.append("kontext_beschreibung (zu kurz oder leer)")

        # Ursachen, Folgen, Controls
        causes = db.get_failure_causes(a["fm_id"])
        if not causes:
            missing.append("causes (keine Ursachen)")

        effects = db.get_failure_effect(a["fm_id"])
        if not effects:
            missing.append("effects (keine Folgen)")

        controls = db.get_current_controls(a["fm_id"])
        if not controls:
            missing.append("controls (keine Controls)")

        # Maßnahmen bei RPZ >= 100
        if a["rpz"] >= 100 or a["S"] >= 9:
            measures = db.get_measures(a["fm_id"])
            if not measures:
                missing.append(f"measures (RPZ={a['rpz']}, S={a['S']} → Maßnahmen Pflicht)")

        if missing:
            results["errors"].append(f"{a['fehler_id']}: {', '.join(missing)}")
        else:
            results["complete"] += 1

    return results


# ═══════════════════════════════════════════════════════════════
# Eval 3: Plausibilität
# ═══════════════════════════════════════════════════════════════

def eval_plausibility(assessments: list[dict]) -> dict:
    """Prüft ob S/O/D-Werte im Kontext plausibel sind."""
    results = {"total": 0, "plausible": 0, "warnings": []}

    # Keywords für Safety-Overrides
    ex_keywords = ["ex-schutz", "atex", "zone 0", "zone 1", "zone 2",
                   "explosionsschutz", "explosionsfähig", "ex-zone"]
    hazmat_keywords = ["säure", "lauge", "toxisch", "giftig", "gefahrstoff",
                       "ätzend", "karzinogen", "schwefelsäure", "salzsäure"]
    safety_keywords = ["berstscheibe", "psv", "not-aus", "sicherheitsventil",
                       "sicherheitsbauteil", "bsv", "sil"]

    for a in assessments:
        results["total"] += 1
        warnings = []

        # Kontext-Text zusammenbauen
        context_text = " ".join(filter(None, [
            a.get("kontext_beschreibung", ""),
            a.get("fehlermodus", ""),
            a.get("komponente", ""),
            str(a.get("komp_kontext", "")),
            str(a.get("komp_params", "")),
        ])).lower()

        # 3a. Ex-Schutz → S sollte >= 8 sein
        if any(kw in context_text for kw in ex_keywords):
            if a["S"] < 8:
                warnings.append(f"S={a['S']} zu niedrig bei Ex-Kontext (erwartet ≥8)")

        # 3b. Gefahrstoff → S sollte >= 7 sein
        if any(kw in context_text for kw in hazmat_keywords):
            if a["S"] < 7:
                warnings.append(f"S={a['S']} zu niedrig bei Gefahrstoff-Kontext (erwartet ≥7)")

        # 3c. Sicherheitsbauteil → S sollte >= 8 sein
        if any(kw in context_text for kw in safety_keywords):
            if a["S"] < 8:
                warnings.append(f"S={a['S']} zu niedrig bei Sicherheitsbauteil-Kontext (erwartet ≥8)")

        # 3d. O-Wert-Plausibilität: O=1 bedeutet < 1 in 1000 Jahren — extrem selten
        if a["O"] <= 1 and a["S"] >= 8:
            warnings.append(f"O={a['O']} bei S={a['S']} — sehr optimistisch? Bitte prüfen.")

        # 3e. D-Plausibilität: D=1 (autom. Abschaltung) nur wenn tatsächlich SIL/Interlock
        if a["D"] == 1:
            if "sil" not in context_text and "interlock" not in context_text:
                warnings.append(f"D=1 (autom. Abschaltung) ohne SIL/Interlock im Kontext")

        if warnings:
            for w in warnings:
                results["warnings"].append(f"{a['fehler_id']}: {w}")
        else:
            results["plausible"] += 1

    return results


# ═══════════════════════════════════════════════════════════════
# Eval 4: Goldstandard Export/Vergleich
# ═══════════════════════════════════════════════════════════════

def export_goldstandard(assessments: list[dict], output_path: str):
    """Exportiert aktuelle Bewertungen als Goldstandard-JSON."""
    goldstandard = []
    for a in assessments:
        goldstandard.append({
            "fehler_id": a["fehler_id"],
            "fehlermodus": a["fehlermodus"],
            "komp_id": a["komp_id"],
            "S": a["S"],
            "O": a["O"],
            "D": a["D"],
            "rpz": a["rpz"],
            "rpz_status": a["rpz_status"],
            "daten_quelle": a.get("daten_quelle"),
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"assessments": goldstandard, "total": len(goldstandard)}, f, indent=2, ensure_ascii=False)

    print(f"Goldstandard exportiert: {output_path} ({len(goldstandard)} Bewertungen)")


def compare_goldstandard(assessments: list[dict], goldstandard_path: str) -> dict:
    """Vergleicht aktuelle Bewertungen gegen Goldstandard."""
    with open(goldstandard_path, "r", encoding="utf-8") as f:
        gold = json.load(f)

    gold_map = {g["fehler_id"]: g for g in gold["assessments"]}

    results = {
        "total": 0, "matched": 0, "deviated": 0, "missing_in_new": 0, "new_items": 0,
        "deviations": [], "s_deviations": [], "o_deviations": [], "d_deviations": [],
    }

    # Vergleich: Goldstandard → aktuelle Bewertungen
    current_map = {a["fehler_id"]: a for a in assessments}

    for fid, g in gold_map.items():
        results["total"] += 1
        if fid not in current_map:
            results["missing_in_new"] += 1
            results["deviations"].append(f"{fid}: im Goldstandard, aber nicht in neuer Bewertung")
            continue

        c = current_map[fid]
        devs = []

        for field in ["S", "O", "D"]:
            diff = c[field] - g[field]
            if diff != 0:
                devs.append(f"{field}: {g[field]}→{c[field]} (Δ{diff:+d})")
                results[f"{field.lower()}_deviations"].append(abs(diff))

        if c["rpz_status"] != g["rpz_status"]:
            devs.append(f"Status: {g['rpz_status']}→{c['rpz_status']}")

        if devs:
            results["deviated"] += 1
            results["deviations"].append(f"{fid} ({g['fehlermodus']}): {', '.join(devs)}")
        else:
            results["matched"] += 1

    # Neue Items (in aktuell, aber nicht im Goldstandard)
    for fid in current_map:
        if fid not in gold_map:
            results["new_items"] += 1

    # Statistiken
    for field in ["s", "o", "d"]:
        devs = results[f"{field}_deviations"]
        if devs:
            results[f"{field}_mean_deviation"] = sum(devs) / len(devs)
            results[f"{field}_max_deviation"] = max(devs)
            results[f"{field}_within_1"] = sum(1 for d in devs if d <= 1) / len(devs) * 100
        else:
            results[f"{field}_mean_deviation"] = 0
            results[f"{field}_max_deviation"] = 0
            results[f"{field}_within_1"] = 100

    return results


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="FMEA Goldstandard Eval")
    parser.add_argument("--project-id", type=int, default=None, help="Project ID")
    parser.add_argument("--db-path", type=str, default=None, help="DB path")
    parser.add_argument("--export", type=str, default=None,
                        metavar="FILE", help="Export Goldstandard to JSON file")
    parser.add_argument("--compare", type=str, default=None,
                        metavar="FILE", help="Compare against Goldstandard JSON")
    args = parser.parse_args()

    db_path = args.db_path or str(Path(__file__).parent.parent / "data" / "fmea.db")

    with FMEAStorage(db_path) as db:
        # Projekt bestimmen
        project_id = args.project_id
        if project_id is None:
            row = db.conn.execute("SELECT MAX(id) FROM projects").fetchone()
            project_id = row[0] if row else None
            if project_id is None:
                print("ERROR: Keine Projekte in der Datenbank")
                sys.exit(1)

        project = dict(db.conn.execute(
            "SELECT name, anlage_name FROM projects WHERE id = ?", (project_id,)
        ).fetchone())

        assessments = _load_all_assessments(db, project_id)

        if not assessments:
            print(f"Keine Bewertungen für Projekt {project['name']} (ID={project_id})")
            sys.exit(1)

        # Export-Modus
        if args.export:
            export_goldstandard(assessments, args.export)
            return

        # Header
        print(f"\n{'='*70}")
        print(f"FMEA Goldstandard Eval — {project['name']} (ID={project_id})")
        print(f"{'='*70}")
        print(f"Bewertungen: {len(assessments)}\n")

        all_passed = True

        # Eval 1: Formale Korrektheit
        print("━━━ Eval 1: Formale Korrektheit ━━━")
        formal = eval_formal(assessments)
        print(f"  Geprüft: {formal['total']} | Bestanden: {formal['passed']} | Fehler: {len(formal['errors'])}")
        for err in formal["errors"]:
            print(f"  ✗ {err}")
        if formal["errors"]:
            all_passed = False

        # Eval 2: Vollständigkeit
        print("\n━━━ Eval 2: Vollständigkeit ━━━")
        completeness = eval_completeness(assessments, db)
        print(f"  Geprüft: {completeness['total']} | Vollständig: {completeness['complete']} | Lücken: {len(completeness['errors'])}")
        for err in completeness["errors"][:10]:
            print(f"  ⚠ {err}")
        if len(completeness["errors"]) > 10:
            print(f"  ... und {len(completeness['errors']) - 10} weitere")

        # Eval 3: Plausibilität
        print("\n━━━ Eval 3: Plausibilität ━━━")
        plausibility = eval_plausibility(assessments)
        print(f"  Geprüft: {plausibility['total']} | Plausibel: {plausibility['plausible']} | Warnungen: {len(plausibility['warnings'])}")
        for warn in plausibility["warnings"][:10]:
            print(f"  ⚠ {warn}")
        if len(plausibility["warnings"]) > 10:
            print(f"  ... und {len(plausibility['warnings']) - 10} weitere")

        # Eval 4: Goldstandard-Vergleich (wenn --compare)
        if args.compare:
            print("\n━━━ Eval 4: Goldstandard-Vergleich ━━━")
            comparison = compare_goldstandard(assessments, args.compare)
            print(f"  Referenz: {comparison['total']} | Übereinstimmend: {comparison['matched']} | Abweichend: {comparison['deviated']}")
            print(f"  Fehlend: {comparison['missing_in_new']} | Neu: {comparison['new_items']}")
            print(f"\n  S-Abweichung: Ø{comparison['s_mean_deviation']:.1f} | Max: {comparison['s_max_deviation']} | ≤1 Stufe: {comparison['s_within_1']:.0f}%")
            print(f"  O-Abweichung: Ø{comparison['o_mean_deviation']:.1f} | Max: {comparison['o_max_deviation']} | ≤1 Stufe: {comparison['o_within_1']:.0f}%")
            print(f"  D-Abweichung: Ø{comparison['d_mean_deviation']:.1f} | Max: {comparison['d_max_deviation']} | ≤1 Stufe: {comparison['d_within_1']:.0f}%")

            if comparison["deviations"]:
                print(f"\n  Abweichungen:")
                for dev in comparison["deviations"][:15]:
                    print(f"    → {dev}")
                if len(comparison["deviations"]) > 15:
                    print(f"    ... und {len(comparison['deviations']) - 15} weitere")

            if comparison["deviated"] > 0:
                all_passed = False

        # Summary
        print(f"\n{'='*70}")
        status = "BESTANDEN" if all_passed else "NICHT BESTANDEN"
        score = formal["passed"] / max(formal["total"], 1) * 100
        print(f"Ergebnis: {status}")
        print(f"Formale Korrektheit: {score:.0f}%")
        print(f"Vollständigkeit: {completeness['complete']}/{completeness['total']}")
        print(f"Plausibilität: {plausibility['plausible']}/{plausibility['total']} (ohne Warnungen)")
        print(f"{'='*70}\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
