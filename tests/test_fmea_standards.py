from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.fmea_standards import (
    CAUSE_ORIGINS,
    D_SCALE,
    FAILURE_TYPES,
    FEHLERMODI_VORLAGEN,
    GEFAHRENFELDER,
    O_SCALE,
    PREVENTION_PHASES,
    RPZ_THRESHOLDS,
    S_SCALE,
    SAFETY_OVERRIDES,
    SPECIAL_RULES,
)


class TestScales(unittest.TestCase):
    """Validate that S, O, D scales each have keys 1-10 with 2-string tuples."""

    def test_s_scale_keys(self):
        self.assertEqual(set(S_SCALE.keys()), set(range(1, 11)))

    def test_o_scale_keys(self):
        self.assertEqual(set(O_SCALE.keys()), set(range(1, 11)))

    def test_d_scale_keys(self):
        self.assertEqual(set(D_SCALE.keys()), set(range(1, 11)))

    def test_s_scale_values_are_two_string_tuples(self):
        for key, val in S_SCALE.items():
            self.assertIsInstance(val, tuple, f"S_SCALE[{key}] is not a tuple")
            self.assertEqual(len(val), 2, f"S_SCALE[{key}] does not have 2 elements")
            self.assertIsInstance(val[0], str)
            self.assertIsInstance(val[1], str)

    def test_o_scale_values_are_two_string_tuples(self):
        for key, val in O_SCALE.items():
            self.assertIsInstance(val, tuple, f"O_SCALE[{key}] is not a tuple")
            self.assertEqual(len(val), 2, f"O_SCALE[{key}] does not have 2 elements")
            self.assertIsInstance(val[0], str)
            self.assertIsInstance(val[1], str)

    def test_d_scale_values_are_two_string_tuples(self):
        for key, val in D_SCALE.items():
            self.assertIsInstance(val, tuple, f"D_SCALE[{key}] is not a tuple")
            self.assertEqual(len(val), 2, f"D_SCALE[{key}] does not have 2 elements")
            self.assertIsInstance(val[0], str)
            self.assertIsInstance(val[1], str)


class TestThresholds(unittest.TestCase):
    """Validate RPZ threshold ordering and types."""

    def test_kritisch_greater_than_hoch(self):
        self.assertGreater(RPZ_THRESHOLDS["kritisch"], RPZ_THRESHOLDS["hoch"])

    def test_hoch_greater_than_mittel(self):
        self.assertGreater(RPZ_THRESHOLDS["hoch"], RPZ_THRESHOLDS["mittel"])

    def test_exact_values(self):
        self.assertEqual(RPZ_THRESHOLDS["kritisch"], 300)
        self.assertEqual(RPZ_THRESHOLDS["hoch"], 200)
        self.assertEqual(RPZ_THRESHOLDS["mittel"], 100)

    def test_all_positive_integers(self):
        for key, val in RPZ_THRESHOLDS.items():
            self.assertIsInstance(val, int, f"RPZ_THRESHOLDS[{key}] is not int")
            self.assertGreater(val, 0, f"RPZ_THRESHOLDS[{key}] is not positive")


class TestFailureTypes(unittest.TestCase):
    """Validate FAILURE_TYPES list."""

    def test_at_least_five_entries(self):
        self.assertGreaterEqual(len(FAILURE_TYPES), 5)

    def test_all_non_empty_strings(self):
        for ft in FAILURE_TYPES:
            self.assertIsInstance(ft, str)
            self.assertTrue(len(ft) > 0, f"Empty string in FAILURE_TYPES")


class TestSafetyOverrides(unittest.TestCase):
    """Validate SAFETY_OVERRIDES structure."""

    def test_each_override_has_keywords(self):
        for override in SAFETY_OVERRIDES:
            self.assertIn("keywords", override)
            self.assertIsInstance(override["keywords"], list)
            self.assertGreater(len(override["keywords"]), 0)

    def test_each_override_has_min_s(self):
        for override in SAFETY_OVERRIDES:
            self.assertIn("min_S", override)
            self.assertIsInstance(override["min_S"], int)
            self.assertGreaterEqual(override["min_S"], 1)
            self.assertLessEqual(override["min_S"], 10)

    def test_each_override_has_label(self):
        for override in SAFETY_OVERRIDES:
            self.assertIn("label", override)
            self.assertIsInstance(override["label"], str)
            self.assertTrue(len(override["label"]) > 0)


class TestSpecialRules(unittest.TestCase):
    """Validate SPECIAL_RULES structure."""

    def test_each_rule_has_required_keys(self):
        for rule in SPECIAL_RULES:
            self.assertIn("id", rule)
            self.assertIn("description", rule)
            self.assertIn("condition", rule)
            self.assertIn("override_status", rule)

    def test_condition_is_callable(self):
        for rule in SPECIAL_RULES:
            self.assertTrue(callable(rule["condition"]), f"Rule {rule['id']} condition is not callable")


class TestCauseOrigins(unittest.TestCase):
    """Validate CAUSE_ORIGINS list."""

    def test_non_empty(self):
        self.assertGreater(len(CAUSE_ORIGINS), 0)

    def test_contains_design(self):
        self.assertIn("Design", CAUSE_ORIGINS)

    def test_contains_betrieb(self):
        self.assertIn("Betrieb", CAUSE_ORIGINS)


class TestPreventionPhases(unittest.TestCase):
    """Validate PREVENTION_PHASES list."""

    def test_non_empty(self):
        self.assertGreater(len(PREVENTION_PHASES), 0)

    def test_contains_konzept(self):
        self.assertIn("Konzept", PREVENTION_PHASES)

    def test_contains_betrieb(self):
        self.assertIn("Betrieb", PREVENTION_PHASES)


class TestGefahrenfelder(unittest.TestCase):
    """Validate GEFAHRENFELDER dict."""

    def test_at_least_20_entries(self):
        self.assertGreaterEqual(len(GEFAHRENFELDER), 20)

    def test_each_entry_has_name(self):
        for key, val in GEFAHRENFELDER.items():
            self.assertIn("name", val, f"GEFAHRENFELDER[{key}] missing 'name'")

    def test_each_entry_has_fm_kategorien_list(self):
        for key, val in GEFAHRENFELDER.items():
            self.assertIn("fm_kategorien", val, f"GEFAHRENFELDER[{key}] missing 'fm_kategorien'")
            self.assertIsInstance(val["fm_kategorien"], list, f"GEFAHRENFELDER[{key}] fm_kategorien is not a list")

    def test_each_entry_has_pflicht_bool(self):
        for key, val in GEFAHRENFELDER.items():
            self.assertIn("pflicht", val, f"GEFAHRENFELDER[{key}] missing 'pflicht'")
            self.assertIsInstance(val["pflicht"], bool, f"GEFAHRENFELDER[{key}] pflicht is not bool")


class TestFehlermodi(unittest.TestCase):
    """Validate FEHLERMODI_VORLAGEN dict."""

    REQUIRED_KEYS = ["prozess", "thermisch", "mechanisch", "msr", "sicherheit"]

    def test_has_required_category_keys(self):
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, FEHLERMODI_VORLAGEN, f"Missing category '{key}'")

    def test_each_category_has_at_least_two_entries(self):
        for key in self.REQUIRED_KEYS:
            self.assertGreaterEqual(
                len(FEHLERMODI_VORLAGEN[key]), 2,
                f"Category '{key}' has fewer than 2 entries",
            )

    def test_each_entry_has_typ_and_beschreibung(self):
        for category, entries in FEHLERMODI_VORLAGEN.items():
            for i, entry in enumerate(entries):
                self.assertIn("typ", entry, f"FEHLERMODI_VORLAGEN[{category}][{i}] missing 'typ'")
                self.assertIn("beschreibung", entry, f"FEHLERMODI_VORLAGEN[{category}][{i}] missing 'beschreibung'")


if __name__ == "__main__":
    unittest.main()
