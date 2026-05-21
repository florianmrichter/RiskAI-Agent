"""Eval-Tests für validate_completeness Gate 2 (Checks 5-7).

Tests:
1. S too low for ATEX context → KRITISCH
2. O deviation from reliability data → WARNUNG
3. D ignores MSR equipment → WARNUNG
4. High RPZ without measures → KRITISCH
5. System without FMs → WARNUNG
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage


def _create_test_db(tmp_dir):
    """Create a test DB with a project, component, function, FM, and risk assessment."""
    db_path = os.path.join(tmp_dir, "test_fmea.db")
    db = FMEAStorage(db_path)
    return db, db_path


def _insert_full_fm(db, project_id, komp_id, comp_name, comp_typ,
                    funktion_id, fehler_id, fehlermodus, fehlerart,
                    S, O, D, system_name=None):
    """Helper: insert component → function → FM → risk_assessment. Returns FM id."""
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
        beschreibung="Testfunktion",
    )
    fm_id = db.insert_failure_mode(
        function_id=func_id,
        fehler_id=fehler_id,
        fehlermodus=fehlermodus,
        fehlerart=fehlerart,
    )
    rpz = S * O * D
    db.insert_risk_assessment(
        failure_mode_id=fm_id,
        S=S, O=O, D=D,
        rpz=rpz,
    )
    return fm_id


class TestSODPlausibility(unittest.TestCase):
    """Check 5: S/O/D plausibility checks."""

    def test_s_too_low_for_atex(self):
        """FM with Ex-keywords but S < 10 → KRITISCH finding."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db, db_path = _create_test_db(tmp_dir)
            pid = db.create_project("Test ATEX", "Testanlage")

            # Component name contains ATEX keyword
            _insert_full_fm(
                db, pid,
                komp_id="KOMP-001",
                comp_name="Ex-Schutz Ventilator",
                comp_typ="mechanisch",
                funktion_id="FUNK-001",
                fehler_id="FM-001",
                fehlermodus="Motorüberhitzung in Zone 1",
                fehlerart="ausfall",
                S=6, O=4, D=5,  # S=6 is too low for ATEX (min 10)
            )
            db.close()

            # Create minimal anlagendaten
            task_folder_name = "Test_ATEX_Project"
            task_path = Path(tmp_dir) / "tasks" / "Risikoanalyse" / task_folder_name
            task_path.mkdir(parents=True, exist_ok=True)
            ad = {"systems": [], "substances": [], "media": []}
            (task_path / "anlagendaten.json").write_text(json.dumps(ad))

            from tools.validate_completeness import validate_completeness

            # Patch the task folder base path
            with patch("tools.validate_completeness.Path") as mock_path_cls:
                # We need to let other Path usages work normally, so only patch
                # the specific resolution in the function.
                # Simpler: call with task_folder=None (no anlagendaten) since
                # Check 5a only needs the FM data from DB.
                result = validate_completeness(pid, task_folder=None, db_path=db_path)

            # Should have a KRITISCH finding about S being too low
            kritisch = [w for w in result["warnings"] if w.startswith("KRITISCH:") and "S=" in w]
            self.assertTrue(
                len(kritisch) >= 1,
                f"Expected KRITISCH finding for ATEX S too low, got warnings: {result['warnings']}"
            )
            self.assertIn("FM-001", kritisch[0])
            self.assertFalse(result["passed"], "Should fail due to KRITISCH finding")

    def test_o_deviation_from_reliability(self):
        """FM with O far from CCPS reference → WARNUNG."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db, db_path = _create_test_db(tmp_dir)
            pid = db.create_project("Test O-Dev", "Testanlage")

            # Kreiselpumpe — reliability DB suggests O~7 for this type
            # O=1 deviates by 6 from richtwert 7 (>3 threshold)
            _insert_full_fm(
                db, pid,
                komp_id="KOMP-002",
                comp_name="Kreiselpumpe P-101",
                comp_typ="mechanisch",
                funktion_id="FUNK-002",
                fehler_id="FM-002",
                fehlermodus="Totaler Ausfall",
                fehlerart="ausfall",
                S=5, O=1, D=3,  # O=1 vs richtwert ~7, deviation=6 > 3
            )
            db.close()

            from tools.validate_completeness import validate_completeness
            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            # Should have WARNUNG about O deviation
            o_warnings = [w for w in result["warnings"] if "WARNUNG:" in w and "O=" in w and "FM-002" in w]
            self.assertTrue(
                len(o_warnings) >= 1,
                f"Expected WARNUNG for O deviation, got warnings: {result['warnings']}"
            )

    def test_d_ignores_msr(self):
        """FM with D=9 despite MSR equipment in Anlagendaten → WARNUNG."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db, db_path = _create_test_db(tmp_dir)
            pid = db.create_project("Test D-MSR", "Testanlage")

            _insert_full_fm(
                db, pid,
                komp_id="KOMP-003",
                comp_name="Reaktor R-100",
                comp_typ="prozess",
                funktion_id="FUNK-003",
                fehler_id="FM-003",
                fehlermodus="Temperaturanstieg",
                fehlerart="abweichung",
                S=5, O=3, D=9,  # D=9 despite MSR
            )
            db.close()

            # Create anlagendaten with MSR equipment
            task_folder_rel = "Risikoanalyse/Test_D_MSR"
            base = Path(__file__).parent.parent / "tasks" / task_folder_rel
            base.mkdir(parents=True, exist_ok=True)
            ad = {
                "systems": [],
                "substances": [],
                "media": [],
                "msrEquipment": [
                    {"name": "TIC-001", "typ": "Temperaturregler"},
                    {"name": "PIC-001", "typ": "Druckregler"},
                ],
            }
            (base / "anlagendaten.json").write_text(json.dumps(ad))

            try:
                from tools.validate_completeness import validate_completeness
                result = validate_completeness(pid, task_folder=task_folder_rel, db_path=db_path)

                d_warnings = [w for w in result["warnings"] if "WARNUNG:" in w and "D=" in w and "FM-003" in w]
                self.assertTrue(
                    len(d_warnings) >= 1,
                    f"Expected WARNUNG for D with MSR, got warnings: {result['warnings']}"
                )
            finally:
                # Clean up created test directory
                import shutil
                if base.exists():
                    shutil.rmtree(base)


class TestMeasuresEffectiveness(unittest.TestCase):
    """Check 6: Measures effectiveness."""

    def test_high_rpz_without_measures(self):
        """FM with RPZ >= 200 and no measures → KRITISCH."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db, db_path = _create_test_db(tmp_dir)
            pid = db.create_project("Test Measures", "Testanlage")

            _insert_full_fm(
                db, pid,
                komp_id="KOMP-004",
                comp_name="Druckbehälter B-100",
                comp_typ="prozess",
                funktion_id="FUNK-004",
                fehler_id="FM-004",
                fehlermodus="Überdruck",
                fehlerart="abweichung",
                S=8, O=5, D=6,  # RPZ = 240 >= 200
            )
            db.close()

            from tools.validate_completeness import validate_completeness
            result = validate_completeness(pid, task_folder=None, db_path=db_path)

            kritisch = [w for w in result["warnings"] if "KRITISCH:" in w and "FM-004" in w and "ohne Maßnahmen" in w]
            self.assertTrue(
                len(kritisch) >= 1,
                f"Expected KRITISCH for high RPZ without measures, got: {result['warnings']}"
            )
            self.assertFalse(result["passed"])


class TestCrossFMAlignment(unittest.TestCase):
    """Check 7: Cross-FM + Anlagendaten alignment."""

    def test_cross_fm_inconsistency(self):
        """System in Anlagendaten without any FM → WARNUNG."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db, db_path = _create_test_db(tmp_dir)
            pid = db.create_project("Test Alignment", "Testanlage")

            # FM for Reaktor, but not for "Destillationskolonne"
            _insert_full_fm(
                db, pid,
                komp_id="KOMP-005",
                comp_name="Reaktor R-200",
                comp_typ="prozess",
                funktion_id="FUNK-005",
                fehler_id="FM-005",
                fehlermodus="Temperaturabweichung",
                fehlerart="abweichung",
                S=4, O=3, D=4,
            )
            db.close()

            # Anlagendaten has a system "Destillationskolonne" that has no FM
            task_folder_rel = "Risikoanalyse/Test_Alignment"
            base = Path(__file__).parent.parent / "tasks" / task_folder_rel
            base.mkdir(parents=True, exist_ok=True)
            ad = {
                "systems": [
                    {"name": "Reaktor R-200"},
                    {"name": "Destillationskolonne K-300"},
                ],
                "substances": [],
                "media": [],
            }
            (base / "anlagendaten.json").write_text(json.dumps(ad))

            try:
                from tools.validate_completeness import validate_completeness
                result = validate_completeness(pid, task_folder=task_folder_rel, db_path=db_path)

                alignment_warnings = [
                    w for w in result["warnings"]
                    if "WARNUNG:" in w and "Destillationskolonne" in w and "keine Fehlermodi" in w
                ]
                self.assertTrue(
                    len(alignment_warnings) >= 1,
                    f"Expected WARNUNG for system without FM, got: {result['warnings']}"
                )
            finally:
                import shutil
                if base.exists():
                    shutil.rmtree(base)


if __name__ == "__main__":
    unittest.main()
