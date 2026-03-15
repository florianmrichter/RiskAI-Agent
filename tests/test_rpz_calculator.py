from __future__ import annotations

"""
Tests for RPZ classification, calculation, special rules, and safety overrides.

Covers:
- classify_rpz boundary values
- calculate_rpz arithmetic and status mapping
- apply_special_rules AIAG-VDA overrides
- check_safety_overrides keyword-based S elevation
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.fmea_standards import (
    classify_rpz,
    apply_special_rules,
    SAFETY_OVERRIDES,
    RPZ_THRESHOLDS,
)
from tools.rpz_calculator import calculate_rpz, check_safety_overrides


class TestClassifyRpz(unittest.TestCase):
    """Test RPZ classification against threshold boundaries."""

    def test_below_mittel_is_niedrig(self):
        self.assertEqual(classify_rpz(99), "niedrig")

    def test_exact_mittel_boundary(self):
        self.assertEqual(classify_rpz(100), "mittel")

    def test_top_of_mittel_range(self):
        self.assertEqual(classify_rpz(199), "mittel")

    def test_exact_hoch_boundary(self):
        self.assertEqual(classify_rpz(200), "hoch")

    def test_top_of_hoch_range(self):
        self.assertEqual(classify_rpz(299), "hoch")

    def test_exact_kritisch_boundary(self):
        self.assertEqual(classify_rpz(300), "kritisch")

    def test_rpz_168_is_mittel_regression(self):
        """REGRESSION: RPZ=168 was incorrectly classified as 'hoch' by agents."""
        self.assertEqual(classify_rpz(168), "mittel")

    def test_very_high_rpz_is_kritisch(self):
        self.assertEqual(classify_rpz(1000), "kritisch")


class TestCalculateRpz(unittest.TestCase):
    """Test RPZ calculation (S * O * D) and status mapping."""

    def test_168_mittel(self):
        result = calculate_rpz(S=7, O=4, D=6)
        self.assertEqual(result["rpz"], 168)
        self.assertEqual(result["rpz_status"], "mittel")

    def test_300_kritisch(self):
        result = calculate_rpz(S=10, O=10, D=3)
        self.assertEqual(result["rpz"], 300)
        self.assertEqual(result["rpz_status"], "kritisch")

    def test_1_niedrig(self):
        result = calculate_rpz(S=1, O=1, D=1)
        self.assertEqual(result["rpz"], 1)
        self.assertEqual(result["rpz_status"], "niedrig")


class TestSpecialRules(unittest.TestCase):
    """Test AIAG-VDA special rule overrides via apply_special_rules."""

    def test_severity_override_when_niedrig(self):
        """S>=9 with niedrig status should be overridden to hoch."""
        status, desc = apply_special_rules(S=9, O=1, D=1, rpz_status="niedrig")
        self.assertEqual(status, "hoch")
        self.assertIsNotNone(desc)

    def test_severity_override_not_applied_when_already_hoch(self):
        """S>=9 with hoch status should stay hoch (rule condition excludes hoch)."""
        status, desc = apply_special_rules(S=9, O=5, D=5, rpz_status="hoch")
        self.assertEqual(status, "hoch")
        self.assertIsNone(desc)

    def test_detection_severity_override_to_kritisch(self):
        """D>=9 and S>=7 should override to kritisch."""
        status, desc = apply_special_rules(S=7, O=2, D=9, rpz_status="mittel")
        self.assertEqual(status, "kritisch")
        self.assertIsNotNone(desc)

    def test_detection_rule_not_triggered_when_s_below_7(self):
        """D>=9 but S<7 should not trigger detection_severity_override."""
        status, desc = apply_special_rules(S=6, O=2, D=9, rpz_status="mittel")
        self.assertEqual(status, "mittel")
        self.assertIsNone(desc)

    def test_no_rule_applies(self):
        """Moderate values should not trigger any special rule."""
        status, desc = apply_special_rules(S=5, O=5, D=5, rpz_status="mittel")
        self.assertEqual(status, "mittel")
        self.assertIsNone(desc)


class TestSafetyOverrides(unittest.TestCase):
    """Test check_safety_overrides keyword matching and S elevation."""

    def test_ex_schutz_override(self):
        data = {
            "fehlermodus": "Ex-Schutz Versagen",
            "fehlerart": "",
            "komponente": "",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 10)
        self.assertIn("Explosionsschutz", label)

    def test_toxisch_override(self):
        data = {
            "fehlermodus": "Toxischer Austritt",
            "fehlerart": "",
            "komponente": "",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 9)
        self.assertIn("Gefahrstoff", label)

    def test_psv_component_override(self):
        data = {
            "fehlermodus": "",
            "fehlerart": "",
            "komponente": "PSV-410",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 10)
        self.assertIn("Sicherheitsgerichtetes", label)

    def test_no_override_for_pumpenausfall(self):
        data = {
            "fehlermodus": "Pumpenausfall",
            "fehlerart": "",
            "komponente": "",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertIsNone(s_val)
        self.assertIsNone(label)

    def test_highest_override_wins(self):
        """When multiple rules match, highest min_S should win."""
        data = {
            "fehlermodus": "ex-schutz und toxisch",
            "fehlerart": "",
            "komponente": "",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 10)

    def test_ex_schutz_qualifier_handloch(self):
        """Local/temporary Zone 0 (open handhole) should get S=9, not S=10."""
        data = {
            "fehlermodus": "Betrieb mit offenem Handloch — Zone 0 lokal",
            "fehlerart": "",
            "komponente": "Handloch HL-43",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 9)
        self.assertIn("lokal", label.lower())

    def test_permanent_zone0_still_10(self):
        """Permanent Zone 0 (N2 loss in reactor) should stay S=10."""
        data = {
            "fehlermodus": "Verlust N2-Inertisierung — Zone 0 im Reaktor",
            "fehlerart": "",
            "komponente": "Reaktor R-43",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 10)
        self.assertIn("Explosionsschutz", label)

    def test_qualifier_undicht_leckage(self):
        """Leak-related Zone 0 should also get S=9 via qualifier."""
        data = {
            "fehlermodus": "Leckage an Dichtung — explosionsfähige Atmosphäre Zone 0",
            "fehlerart": "",
            "komponente": "",
            "typ": "",
        }
        s_val, label = check_safety_overrides(data)
        self.assertEqual(s_val, 9)
        self.assertIn("lokal", label.lower())


if __name__ == "__main__":
    unittest.main()
