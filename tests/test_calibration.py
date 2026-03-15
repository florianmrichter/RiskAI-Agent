"""Unit tests for calibration system (plausibility checks, pattern analysis, rule generation)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.calibration import (
    check_plausibility,
    apply_calibration,
    analyze_corrections,
    generate_rules,
    select_training_candidates,
    load_calibration_rules,
    RULES_PATH,
)


class _CalibrationTestCase(unittest.TestCase):
    """Base class with temp DB and cleanup."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = FMEAStorage(self.db_path)
        # Create a test project with components + failure modes
        self.project_id = self.db.create_project("Test-Projekt", "Testanlage")
        self.comp_id = self.db.insert_component(
            self.project_id, "K-001", "Pumpe P-201", "Pumpe",
            "Mechanisch", system_name="Dosiersystem",
            parameters={"medium": "Ethylacetat"},
            kontext={"ex_zone": "Zone 1"},
        )
        self.func_id = self.db.insert_function(
            self.comp_id, "F-001", "Hauptfunktion", "Dosierung Ethylacetat"
        )
        self.fm_id = self.db.insert_failure_mode(
            self.func_id, "FM-001", "Leckage", "Mechanisch"
        )
        self.ra_id = self.db.insert_risk_assessment(
            self.fm_id, S=5, O=3, D=4,
            begruendung_S="Test", begruendung_O="Test", begruendung_D="Test",
            agent_konfidenz="mittel",
        )
        # Save original rules path and create temp rules
        self._orig_rules = None
        if RULES_PATH.exists():
            self._orig_rules = RULES_PATH.read_text()

    def tearDown(self):
        self.db.close()
        for suffix in ("", "-shm", "-wal"):
            path = self.db_path + suffix
            if os.path.exists(path):
                os.remove(path)
        # Restore original rules
        if self._orig_rules is not None:
            RULES_PATH.write_text(self._orig_rules)

    def _add_more_failure_modes(self):
        """Add additional failure modes for pattern testing."""
        fm_ids = []
        for i in range(2, 7):
            fm_id = self.db.insert_failure_mode(
                self.func_id, f"FM-{i:03d}", f"Fehlermodus {i}", "Mechanisch"
            )
            self.db.insert_risk_assessment(
                fm_id, S=5, O=3, D=4,
                agent_konfidenz="mittel",
            )
            fm_ids.append(fm_id)
        return fm_ids


class TestPlausibilityChecks(_CalibrationTestCase):
    """Test static plausibility checks."""

    def test_ex_schutz_low_S_warns(self):
        """Ex-Schutz context with S < 8 should trigger warning."""
        fm_data = {"fehlermodus": "Explosion", "fehlerart": "Sicherheit",
                   "kontext": "Ex-Schutz Zone 1, ATEX"}
        warnings = check_plausibility(fm_data, S=5, O=3, D=4)
        self.assertTrue(any("PLZ-001" in w["rule_id"] for w in warnings))

    def test_ex_schutz_high_S_no_warn(self):
        """Ex-Schutz context with S >= 8 should not trigger warning."""
        fm_data = {"fehlermodus": "Explosion", "kontext": "Ex-Schutz Zone 1"}
        warnings = check_plausibility(fm_data, S=9, O=3, D=4)
        plz001 = [w for w in warnings if w["rule_id"] == "PLZ-001"]
        self.assertEqual(len(plz001), 0)

    def test_sicherheitsventil_low_S_warns(self):
        """PSV context with S < 9 should trigger PLZ-002."""
        fm_data = {"fehlermodus": "PSV versagt", "fehlerart": "Sicherheit",
                   "kontext": "Sicherheitsventil PSV-101"}
        warnings = check_plausibility(fm_data, S=7, O=2, D=3)
        self.assertTrue(any("PLZ-002" in w["rule_id"] for w in warnings))

    def test_redundante_messung_high_D_warns(self):
        """Redundant measurement with D > 5 should trigger PLZ-003."""
        fm_data = {"kontext": "redundante Temperaturmessung 2oo3"}
        warnings = check_plausibility(fm_data, S=5, O=3, D=7)
        self.assertTrue(any("PLZ-003" in w["rule_id"] for w in warnings))

    def test_no_context_no_warnings(self):
        """No special context should produce no warnings."""
        fm_data = {"fehlermodus": "Normaler Fehler", "fehlerart": "Prozess"}
        warnings = check_plausibility(fm_data, S=5, O=3, D=4)
        self.assertEqual(len(warnings), 0)


class TestFeedbackRecording(_CalibrationTestCase):
    """Test recording corrections and confirmations."""

    def test_record_confirmation(self):
        """Confirmation should be recorded with delta=0."""
        fb_id = self.db.record_confirmation(
            self.fm_id, self.project_id, "S", 5, source="workflow"
        )
        self.assertIsNotNone(fb_id)
        history = self.db.get_feedback_history(self.project_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["feedback_type"], "confirmation")
        self.assertEqual(history[0]["delta"], 0)

    def test_record_correction(self):
        """Correction should update risk_assessments and record delta."""
        fb_id = self.db.record_correction(
            self.fm_id, self.project_id, "S",
            original=5, corrected=8,
            reason="Lösemittel-Brandgefahr",
            context={"komponenten_typ": "Pumpe", "medium": "Ethylacetat"},
        )
        self.assertIsNotNone(fb_id)
        # Check feedback record
        history = self.db.get_feedback_history(self.project_id, "correction")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["delta"], 3)
        self.assertEqual(history[0]["reason"], "Lösemittel-Brandgefahr")
        # Check risk_assessments was updated
        ra = self.db.get_risk_assessment(self.fm_id)
        self.assertEqual(ra["S"], 8)
        self.assertEqual(ra["original_S"], 5)
        self.assertEqual(ra["human_corrected"], 1)
        self.assertEqual(ra["correction_count"], 1)
        # RPZ should be recalculated
        self.assertEqual(ra["rpz"], 8 * 3 * 4)

    def test_correction_rate(self):
        """Correction rate should be calculated correctly."""
        self.db.record_confirmation(self.fm_id, self.project_id, "S", 5)
        self.db.record_confirmation(self.fm_id, self.project_id, "O", 3)
        self.db.record_correction(
            self.fm_id, self.project_id, "D", 4, 6, "Schlechte Detection"
        )
        rate = self.db.get_correction_rate(self.project_id)
        self.assertEqual(rate["total"], 3)
        self.assertEqual(rate["corrections"], 1)
        self.assertAlmostEqual(rate["correction_rate"], 0.33, places=2)

    def test_multiple_corrections_increment_count(self):
        """Multiple corrections should increment correction_count."""
        self.db.record_correction(
            self.fm_id, self.project_id, "S", 5, 7, "Erste Korrektur"
        )
        self.db.record_correction(
            self.fm_id, self.project_id, "O", 3, 5, "Zweite Korrektur"
        )
        ra = self.db.get_risk_assessment(self.fm_id)
        self.assertEqual(ra["correction_count"], 2)
        self.assertEqual(ra["original_S"], 5)  # First original preserved


class TestPatternAnalysis(_CalibrationTestCase):
    """Test pattern detection from corrections."""

    def test_no_corrections_empty_patterns(self):
        """No corrections should return empty patterns."""
        patterns = self.db.get_feedback_patterns()
        self.assertEqual(patterns["total_corrections"], 0)
        self.assertEqual(len(patterns["patterns"]), 0)

    def test_pattern_detection(self):
        """Multiple similar corrections should be detected as pattern."""
        fm_ids = self._add_more_failure_modes()
        # Record 3+ corrections with same pattern (Mechanisch, S too low)
        for fm_id in [self.fm_id] + fm_ids[:2]:
            self.db.record_correction(
                fm_id, self.project_id, "S",
                original=5, corrected=8,
                reason="S zu niedrig bei Pumpen",
                context={"komponenten_typ": "Pumpe"},
            )
        patterns = self.db.get_feedback_patterns()
        self.assertGreaterEqual(patterns["total_corrections"], 3)
        self.assertTrue(len(patterns["patterns"]) > 0)
        # Check field bias
        self.assertIn("S", patterns["field_bias"])
        self.assertGreater(patterns["field_bias"]["S"]["avg_delta"], 0)

    def test_field_bias_direction(self):
        """Field bias should correctly identify direction."""
        fm_ids = self._add_more_failure_modes()
        # S consistently too low (positive delta)
        for fm_id in [self.fm_id] + fm_ids[:1]:
            self.db.record_correction(
                fm_id, self.project_id, "S", 5, 8, "Zu niedrig"
            )
        # D consistently too high (negative delta)
        for fm_id in fm_ids[1:3]:
            self.db.record_correction(
                fm_id, self.project_id, "D", 6, 3, "Zu hoch"
            )
        patterns = self.db.get_feedback_patterns()
        self.assertEqual(patterns["field_bias"]["S"]["direction"], "zu_niedrig")
        self.assertEqual(patterns["field_bias"]["D"]["direction"], "zu_hoch")


class TestRuleGeneration(_CalibrationTestCase):
    """Test calibration rule generation."""

    def test_generate_rules_empty(self):
        """No corrections should generate no rules."""
        config = generate_rules(self.db_path, min_occurrences=3)
        self.assertEqual(len(config["rules"]), 0)
        self.assertEqual(config["based_on_corrections"], 0)

    def test_generate_rules_from_pattern(self):
        """Sufficient corrections should generate a calibration rule."""
        fm_ids = self._add_more_failure_modes()
        # 4 corrections with same pattern
        for fm_id in [self.fm_id] + fm_ids[:3]:
            self.db.record_correction(
                fm_id, self.project_id, "S", 5, 8, "Pumpen-Muster",
                context={"komponenten_typ": "Pumpe"},
            )
        config = generate_rules(self.db_path, min_occurrences=3)
        self.assertGreater(len(config["rules"]), 0)
        rule = config["rules"][0]
        self.assertIn("CAL-", rule["id"])
        self.assertIn("adjustment", rule)
        # Plausibility checks should be preserved
        self.assertIn("plausibility_checks", config)

    def test_rules_file_written(self):
        """Generated rules should be written to config file."""
        generate_rules(self.db_path)
        self.assertTrue(RULES_PATH.exists())
        with open(RULES_PATH) as f:
            config = json.load(f)
        self.assertIn("rules", config)
        self.assertIn("generated_at", config)


class TestCalibrationApplication(_CalibrationTestCase):
    """Test applying calibration rules to assessments."""

    def test_no_rules_no_adjustment(self):
        """Without rules, values should not change."""
        fm_data = {"komponenten_typ": "Pumpe", "fehlerart": "Mechanisch"}
        result = apply_calibration(fm_data, S=5, O=3, D=4)
        self.assertEqual(result["S"], 5)
        self.assertEqual(result["O"], 3)
        self.assertEqual(result["D"], 4)
        self.assertEqual(len(result["adjustments"]), 0)


class TestTrainingCandidates(_CalibrationTestCase):
    """Test training candidate selection."""

    def test_select_candidates(self):
        """Should return candidates sorted by training priority."""
        candidates = select_training_candidates(self.db_path, n=5)
        self.assertIsInstance(candidates, list)
        # Should return at least our one assessment
        self.assertGreaterEqual(len(candidates), 1)

    def test_low_confidence_prioritized(self):
        """Low-confidence assessments should come first."""
        fm_ids = self._add_more_failure_modes()
        # Set one FM to low confidence
        self.db.update_risk_assessment(
            fm_ids[0], agent_konfidenz="niedrig"
        )
        candidates = select_training_candidates(self.db_path, n=5)
        self.assertGreater(len(candidates), 0)
        # First candidate should be the low-confidence one
        self.assertEqual(candidates[0]["agent_konfidenz"], "niedrig")


if __name__ == "__main__":
    unittest.main()
