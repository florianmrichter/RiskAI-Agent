"""Direct unit tests for tools/validate_completeness.validate_completeness().

Tests each of the 7 validation phases:
1. Category coverage (9 categories)
2. Gefahrenfelder coverage (mandatory hazard fields)
3. Utility/interface coverage
4. CCF candidate identification
5. S/O/D plausibility (safety overrides, reliability, MSR)
6. Measures effectiveness (high RPZ without measures, RPZ reduction)
7. Cross-FM + Anlagendaten alignment (systems, hazardous substances)

Plus edge cases and return-structure checks.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJ_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJ_ROOT))

from config.fmea_standards import FEHLERMODI_VORLAGEN, GEFAHRENFELDER
from tools.storage import FMEAStorage
from tools.validate_completeness import validate_completeness, format_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_db(tmp_dir: str) -> tuple:
    """Create a fresh FMEAStorage in *tmp_dir*. Returns (db, db_path)."""
    db_path = os.path.join(tmp_dir, "test.db")
    db = FMEAStorage(db_path)
    return db, db_path


def _insert_fm(db, project_id, komp_id, comp_name, comp_typ,
               funktion_id, fehler_id, fehlermodus, fehlerart,
               S, O, D, system_name=None, funktion_beschreibung="Testfunktion"):
    """Insert component -> function -> FM -> risk_assessment. Returns FM row id."""
    comp_id = db.insert_component(
        project_id=project_id,
        komp_id=komp_id,
        name=comp_name,
        typ=comp_typ,
        kategorie="prozess",
        system_name=system_name,
    )
    func_id = db.insert_function(
        component_id=comp_id,
        funktion_id=funktion_id,
        typ="hauptfunktion",
        beschreibung=funktion_beschreibung,
    )
    fm_id = db.insert_failure_mode(
        function_id=func_id,
        fehler_id=fehler_id,
        fehlermodus=fehlermodus,
        fehlerart=fehlerart,
    )
    db.insert_risk_assessment(failure_mode_id=fm_id, S=S, O=O, D=D)
    return fm_id


def _write_anlagendaten(tmp_dir: str, task_folder: str, ad: dict) -> Path:
    """Write anlagendaten.json into the expected location and return the path."""
    base = PROJ_ROOT / "tasks" / task_folder
    base.mkdir(parents=True, exist_ok=True)
    path = base / "anlagendaten.json"
    path.write_text(json.dumps(ad, ensure_ascii=False))
    return base


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestReturnStructure(unittest.TestCase):
    """Validate the shape of the return dict regardless of content."""

    def test_return_keys_present(self):
        """Result must have 'passed', 'warnings', 'details'."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("Struct", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                       "FUNK-001", "FM-001", "Ausfall", "ausfall", 5, 3, 3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            self.assertIn("passed", result)
            self.assertIn("warnings", result)
            self.assertIn("details", result)
            self.assertIsInstance(result["passed"], bool)
            self.assertIsInstance(result["warnings"], list)
            self.assertIsInstance(result["details"], dict)

    def test_details_contain_expected_sections(self):
        """Details should always include categories, gefahrenfelder, sod_plausibility, measures_effectiveness."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("Sections", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                       "FUNK-001", "FM-001", "Ausfall", "ausfall", 4, 3, 3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            for key in ("categories", "gefahrenfelder", "sod_plausibility", "measures_effectiveness"):
                self.assertIn(key, result["details"], f"Missing details key: {key}")


class TestEmptyProject(unittest.TestCase):
    """Edge case: project exists but has zero failure modes."""

    def test_no_failure_modes_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("Empty", "Anlage")
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            self.assertFalse(result["passed"])
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("Keine Fehlermodi", result["warnings"][0])
            self.assertEqual(result["details"], {})


class TestCategoryCoverage(unittest.TestCase):
    """Phase 1: 9-category coverage check."""

    def test_single_category_reports_missing(self):
        """One FM in 'ausfall' should report all other categories as missing."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("Cat", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                       "FUNK-001", "FM-001", "Leckage", "ausfall", 4, 3, 3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            cats = result["details"]["categories"]
            # 'ausfall' is not a key in FEHLERMODI_VORLAGEN; the actual keys are
            # prozess, thermisch, mechanisch, etc. So 'ausfall' won't match any.
            all_cat_keys = set(FEHLERMODI_VORLAGEN.keys())
            # Every standard category should be missing since 'ausfall' is not one of them
            self.assertEqual(set(cats["missing"]), all_cat_keys)

    def test_all_categories_covered(self):
        """One FM per category -> no category warnings."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("AllCats", "Anlage")
            for i, cat in enumerate(FEHLERMODI_VORLAGEN.keys(), start=1):
                _insert_fm(
                    db, pid,
                    f"KOMP-{i:03d}", f"Komp-{cat}", "mechanisch",
                    f"FUNK-{i:03d}", f"FM-{i:03d}",
                    f"Fehler-{cat}", cat,
                    S=4, O=3, D=3,
                )
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            cats = result["details"]["categories"]
            self.assertEqual(cats["missing"], [])
            # No "Kategorie" warnings
            cat_warnings = [w for w in result["warnings"] if "Kategorie" in w]
            self.assertEqual(len(cat_warnings), 0)


class TestGefahrenfelderCoverage(unittest.TestCase):
    """Phase 2: Mandatory Gefahrenfelder check."""

    def test_missing_pflicht_gefahrenfelder_reported(self):
        """FM with only 'prozess' covers some GFs but not all pflicht ones."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("GF", "Anlage")
            # 'prozess' covers GFs whose fm_kategorien include "Prozess"
            _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                       "FUNK-001", "FM-001", "Druckabweichung", "prozess", 5, 3, 3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            gf = result["details"]["gefahrenfelder"]
            # Some pflicht GFs require 'Thermisch', 'MSR', etc. that are not covered
            self.assertTrue(len(gf["missing"]) > 0, "Should have uncovered pflicht GFs")
            # GFs that map to 'Prozess' should be covered
            self.assertTrue(len(gf["covered"]) > 0, "Prozess should cover some GFs")

    def test_all_pflicht_covered(self):
        """FMs spanning all fm_kategorien referenced by pflicht GFs -> no GF warnings."""
        pflicht = {k: v for k, v in GEFAHRENFELDER.items() if v.get("pflicht")}
        needed_cats = set()
        for gf_data in pflicht.values():
            for c in gf_data.get("fm_kategorien", []):
                needed_cats.add(c.lower())

        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("AllGF", "Anlage")
            for i, cat in enumerate(sorted(needed_cats), start=1):
                _insert_fm(
                    db, pid,
                    f"KOMP-{i:03d}", f"Komp-{cat}", "mechanisch",
                    f"FUNK-{i:03d}", f"FM-{i:03d}",
                    f"Fehler-{cat}", cat,
                    S=4, O=3, D=3,
                )
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            gf = result["details"]["gefahrenfelder"]
            self.assertEqual(gf["missing"], [],
                             f"All pflicht GFs should be covered but missing: {gf['missing']}")


class TestUtilityCoverage(unittest.TestCase):
    """Phase 3: Utility/interface check (requires anlagendaten)."""

    def test_missing_utility_warning(self):
        """Media entry not referenced in any FM text -> warning."""
        task_folder = "Risikoanalyse/_test_utility_coverage"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("Util", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                           "FUNK-001", "FM-001", "Temperaturabweichung", "thermisch",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [
                        {"name": "Stickstoff"},
                        {"name": "Kühlwasser"},
                    ],
                }
                base = _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                utilities = result["details"].get("utilities", {})
                # Neither 'Stickstoff' nor 'Kühlwasser' appear in FM texts
                self.assertTrue(len(utilities.get("missing", [])) >= 1,
                                f"Should warn about unreferenced media, got: {utilities}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_utility_covered_when_referenced(self):
        """Media name appears in FM text -> not missing."""
        task_folder = "Risikoanalyse/_test_utility_covered"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("UtilOk", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                           "FUNK-001", "FM-001",
                           "Ausfall Kühlwasser führt zu Überhitzung", "thermisch",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [{"name": "Kühlwasser"}],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                utilities = result["details"].get("utilities", {})
                self.assertIn("Kühlwasser", utilities.get("covered", []))
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_backflow_warning_when_media_present(self):
        """Media entries exist but no backflow FM -> warning."""
        task_folder = "Risikoanalyse/_test_backflow"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("Backflow", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                           "FUNK-001", "FM-001", "Totalausfall", "ausfall",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [{"name": "Dampf"}],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                backflow_w = [w for w in result["warnings"] if "Rückströmung" in w]
                self.assertTrue(len(backflow_w) >= 1,
                                f"Expected backflow warning, got: {result['warnings']}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)


class TestCCFCandidates(unittest.TestCase):
    """Phase 4: CCF candidate identification."""

    def test_ccf_candidate_detected(self):
        """Media with fmea_critical=True -> CCF candidate."""
        task_folder = "Risikoanalyse/_test_ccf"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("CCF", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                           "FUNK-001", "FM-001", "Ausfall", "prozess", 4, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [
                        {"name": "Stickstoff", "fmea_critical": True},
                        {"name": "Kühlwasser", "failureConsequence": "Runaway"},
                    ],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                ccf = result["details"].get("ccf_candidates", [])
                self.assertEqual(len(ccf), 2, f"Expected 2 CCF candidates, got: {ccf}")
                ccf_warnings = [w for w in result["warnings"] if "CCF" in w]
                self.assertTrue(len(ccf_warnings) >= 1)
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_no_ccf_when_not_critical(self):
        """Media without fmea_critical or failureConsequence -> no CCF candidates."""
        task_folder = "Risikoanalyse/_test_no_ccf"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("NoCCF", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                           "FUNK-001", "FM-001", "Ausfall", "prozess", 4, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [{"name": "Wasser"}],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                ccf = result["details"].get("ccf_candidates", [])
                self.assertEqual(len(ccf), 0)
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)


class TestSODPlausibilityDirect(unittest.TestCase):
    """Phase 5: S/O/D plausibility checks."""

    def test_safety_override_s_too_low(self):
        """FM with ATEX keyword but S < min_S -> KRITISCH."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("SOverride", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Ex-Schutz Motor", "mechanisch",
                       "FUNK-001", "FM-001", "Motorausfall Zone 1", "ausfall",
                       S=5, O=3, D=3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            kritisch = [w for w in result["warnings"] if w.startswith("KRITISCH:") and "S=" in w]
            self.assertTrue(len(kritisch) >= 1,
                            f"Expected KRITISCH for S too low, got: {result['warnings']}")
            self.assertFalse(result["passed"])

    def test_no_safety_override_when_s_sufficient(self):
        """FM with ATEX keyword and S=10 -> no KRITISCH for S."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("SOk", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Ex-Schutz Motor", "mechanisch",
                       "FUNK-001", "FM-001", "Motorausfall Zone 1", "ausfall",
                       S=10, O=3, D=3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            s_kritisch = [w for w in result["warnings"]
                          if w.startswith("KRITISCH:") and "S=" in w and "FM-001" in w]
            self.assertEqual(len(s_kritisch), 0,
                             f"Should not have KRITISCH for S=10, got: {s_kritisch}")

    def test_d_high_with_msr_equipment(self):
        """FM with D > 7 and MSR equipment in anlagendaten -> WARNUNG."""
        task_folder = "Risikoanalyse/_test_d_msr"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("DMSR", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                           "FUNK-001", "FM-001", "Temperatur hoch", "thermisch",
                           S=5, O=3, D=8)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [],
                    "msrEquipment": [{"name": "TIC-100", "typ": "Temperaturregler"}],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                d_warnings = [w for w in result["warnings"] if "D=" in w and "MSR" in w]
                self.assertTrue(len(d_warnings) >= 1,
                                f"Expected D/MSR warning, got: {result['warnings']}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_d_low_no_msr_warning(self):
        """FM with D <= 7 -> no MSR warning even if MSR equipment present."""
        task_folder = "Risikoanalyse/_test_d_ok"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("DOk", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor", "prozess",
                           "FUNK-001", "FM-001", "Temperatur hoch", "thermisch",
                           S=5, O=3, D=5)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [],
                    "media": [],
                    "msrEquipment": [{"name": "TIC-100", "typ": "Temperaturregler"}],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                d_warnings = [w for w in result["warnings"] if "D=" in w and "MSR" in w]
                self.assertEqual(len(d_warnings), 0,
                                 f"D<=7 should not trigger MSR warning, got: {d_warnings}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)


class TestMeasuresEffectivenessDirect(unittest.TestCase):
    """Phase 6: Measures effectiveness checks."""

    def test_high_rpz_no_measures_kritisch(self):
        """RPZ >= 200 without any measures -> KRITISCH."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("NoMeas", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Behälter", "prozess",
                       "FUNK-001", "FM-001", "Überdruck", "prozess",
                       S=8, O=5, D=6)  # RPZ = 240
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            kritisch = [w for w in result["warnings"]
                        if "KRITISCH:" in w and "FM-001" in w and "ohne Maßnahmen" in w]
            self.assertTrue(len(kritisch) >= 1)
            self.assertFalse(result["passed"])

    def test_high_rpz_with_effective_measure_no_warning(self):
        """RPZ >= 200 with a measure that reduces RPZ -> no measures warning."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("MeasOk", "Anlage")
            fm_id = _insert_fm(db, pid, "KOMP-001", "Behälter", "prozess",
                               "FUNK-001", "FM-001", "Überdruck", "prozess",
                               S=8, O=5, D=6)  # RPZ = 240
            db.insert_measure(
                failure_mode_id=fm_id, name="SIL-2 Abschaltung",
                abe_kategorie="A", beschreibung="Druckbegrenzung",
                S_neu=8, O_neu=2, D_neu=2, rpz_neu=32,
            )
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            meas_findings = result["details"]["measures_effectiveness"]
            self.assertEqual(len(meas_findings), 0,
                             f"Effective measure should clear warning, got: {meas_findings}")

    def test_high_rpz_with_ineffective_measure_warning(self):
        """RPZ >= 200 with measure that does not reduce RPZ -> WARNUNG."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("MeasBad", "Anlage")
            fm_id = _insert_fm(db, pid, "KOMP-001", "Behälter", "prozess",
                               "FUNK-001", "FM-001", "Überdruck", "prozess",
                               S=8, O=5, D=6)  # RPZ = 240
            db.insert_measure(
                failure_mode_id=fm_id, name="Schulung",
                abe_kategorie="B", beschreibung="Personalschulung",
                rpz_neu=250,  # does not reduce
            )
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            meas_findings = result["details"]["measures_effectiveness"]
            warn = [f for f in meas_findings if "RPZ nicht" in f]
            self.assertTrue(len(warn) >= 1,
                            f"Expected 'RPZ nicht' warning, got: {meas_findings}")

    def test_low_rpz_no_measures_no_warning(self):
        """RPZ < 200 without measures -> no measures warning."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("LowRPZ", "Anlage")
            _insert_fm(db, pid, "KOMP-001", "Ventil", "mechanisch",
                       "FUNK-001", "FM-001", "Leichte Leckage", "mechanisch",
                       S=3, O=3, D=3)  # RPZ = 27
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            meas_findings = result["details"]["measures_effectiveness"]
            self.assertEqual(len(meas_findings), 0)


class TestCrossFMAlignment(unittest.TestCase):
    """Phase 7: Cross-FM alignment with Anlagendaten."""

    def test_system_without_fm_warning(self):
        """System in anlagendaten but no matching FM component -> WARNUNG."""
        task_folder = "Risikoanalyse/_test_alignment_sys"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("Align", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Reaktor R-100", "prozess",
                           "FUNK-001", "FM-001", "Temperaturabweichung", "thermisch",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [
                        {"name": "Reaktor R-100"},
                        {"name": "Destillationskolonne K-200"},
                    ],
                    "substances": [],
                    "media": [],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                align = result["details"].get("alignment", [])
                dest_warn = [a for a in align if "Destillationskolonne" in a]
                self.assertTrue(len(dest_warn) >= 1,
                                f"Expected warning for uncovered system, got: {align}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_hazardous_substance_not_referenced_warning(self):
        """Substance with WGK>=2 not in FM texts -> WARNUNG."""
        task_folder = "Risikoanalyse/_test_align_subst"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("HazSub", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                           "FUNK-001", "FM-001", "Leckage", "mechanisch",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [
                        {"name": "Methanol", "WGK": 2, "ghs": ["GHS02", "GHS06"]},
                    ],
                    "media": [],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                align = result["details"].get("alignment", [])
                subst_warn = [a for a in align if "Methanol" in a]
                self.assertTrue(len(subst_warn) >= 1,
                                f"Expected warning for unreferenced hazardous substance, got: {align}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_hazardous_substance_referenced_no_warning(self):
        """Hazardous substance referenced in FM text -> no warning."""
        task_folder = "Risikoanalyse/_test_align_subst_ok"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("HazOk", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                           "FUNK-001", "FM-001",
                           "Methanol-Leckage an Gleitringdichtung", "mechanisch",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [
                        {"name": "Methanol", "WGK": 3, "ghs": ["GHS02"]},
                    ],
                    "media": [],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                align = result["details"].get("alignment", [])
                subst_warn = [a for a in align if "Methanol" in a]
                self.assertEqual(len(subst_warn), 0,
                                 f"Methanol is referenced, should not warn: {align}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)

    def test_non_hazardous_substance_no_warning(self):
        """Substance with WGK<2 and no dangerous GHS -> no warning even if unreferenced."""
        task_folder = "Risikoanalyse/_test_align_safe"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db, db_path = _make_db(tmp)
                pid = db.create_project("SafeSub", "Anlage")
                _insert_fm(db, pid, "KOMP-001", "Pumpe", "mechanisch",
                           "FUNK-001", "FM-001", "Leckage", "mechanisch",
                           5, 3, 3)
                db.close()

                ad = {
                    "systems": [],
                    "substances": [
                        {"name": "Wasser", "WGK": 0, "ghs": []},
                    ],
                    "media": [],
                }
                _write_anlagendaten(tmp, task_folder, ad)

                result = validate_completeness(pid, task_folder=task_folder, db_path=db_path)

                align = result["details"].get("alignment", [])
                water_warn = [a for a in align if "Wasser" in a]
                self.assertEqual(len(water_warn), 0,
                                 f"Non-hazardous substance should not warn: {align}")
        finally:
            cleanup = PROJ_ROOT / "tasks" / task_folder
            if cleanup.exists():
                shutil.rmtree(cleanup)


class TestPassedFlag(unittest.TestCase):
    """The 'passed' flag is False only when KRITISCH warnings exist."""

    def test_passed_true_with_only_warnungen(self):
        """Warnings but no KRITISCH -> passed=True."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("PassOk", "Anlage")
            # Low RPZ, no ATEX keywords -> no KRITISCH
            _insert_fm(db, pid, "KOMP-001", "Ventil", "mechanisch",
                       "FUNK-001", "FM-001", "Leichte Leckage", "mechanisch",
                       S=3, O=3, D=3)
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            # There will be category/GF warnings, but none KRITISCH
            self.assertTrue(result["passed"])

    def test_passed_false_with_kritisch(self):
        """KRITISCH warning -> passed=False."""
        with tempfile.TemporaryDirectory() as tmp:
            db, db_path = _make_db(tmp)
            pid = db.create_project("PassFail", "Anlage")
            # High RPZ without measures -> KRITISCH
            _insert_fm(db, pid, "KOMP-001", "Behälter", "prozess",
                       "FUNK-001", "FM-001", "Versagen", "prozess",
                       S=10, O=5, D=5)  # RPZ = 250
            db.close()

            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            self.assertFalse(result["passed"])


class TestFormatReport(unittest.TestCase):
    """Smoke test for format_report()."""

    def test_format_report_returns_string(self):
        result = {
            "passed": True,
            "warnings": ["Test-Warning"],
            "details": {
                "categories": {"covered": ["prozess"], "missing": ["thermisch"]},
                "gefahrenfelder": {"covered": ["1.1"], "missing": ["1.6: Temperatur"]},
            },
        }
        report = format_report(result)
        self.assertIsInstance(report, str)
        self.assertIn("BESTANDEN", report)
        self.assertIn("Test-Warning", report)

    def test_format_report_warnings_status(self):
        result = {
            "passed": False,
            "warnings": ["KRITISCH: etwas"],
            "details": {},
        }
        report = format_report(result)
        self.assertIn("WARNINGS", report)


if __name__ == "__main__":
    unittest.main()
