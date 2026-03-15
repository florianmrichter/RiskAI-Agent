from __future__ import annotations

"""
Tests for plant data loading and validation.

Covers:
- load_plant_data: JSON loading, structure verification
- validate_plant_data: error/warning detection for invalid and valid data
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.load_plant_data import load_plant_data, validate_plant_data

PROJECT_ROOT = Path(__file__).parent.parent
TEST_DATA_PATH = PROJECT_ROOT / "tasks" / "Risikoanalyse" / "Buechi_Glasreaktor_50L_20TA42" / "anlagendaten.json"
TEST_DATA_EXISTS = TEST_DATA_PATH.is_file()


class TestLoadPlantData(unittest.TestCase):
    """Test loading plant data from JSON files."""

    @unittest.skipUnless(TEST_DATA_EXISTS, "Buechi test data not available")
    def test_load_returns_dict_with_systems(self):
        """Loading Buechi JSON returns a dict containing a 'systems' key."""
        data = load_plant_data(str(TEST_DATA_PATH))
        self.assertIsInstance(data, dict)
        self.assertIn("systems", data)

    @unittest.skipUnless(TEST_DATA_EXISTS, "Buechi test data not available")
    def test_systems_is_non_empty_list(self):
        """The 'systems' value is a non-empty list."""
        data = load_plant_data(str(TEST_DATA_PATH))
        self.assertIsInstance(data["systems"], list)
        self.assertGreater(len(data["systems"]), 0)

    @unittest.skipUnless(TEST_DATA_EXISTS, "Buechi test data not available")
    def test_each_system_has_name(self):
        """Every system entry has a 'name' key."""
        data = load_plant_data(str(TEST_DATA_PATH))
        for i, system in enumerate(data["systems"]):
            with self.subTest(system_index=i):
                self.assertIn("name", system)


class TestValidatePlantData(unittest.TestCase):
    """Test plant data validation logic."""

    def test_empty_dict_returns_errors(self):
        """Validating an empty dict returns at least one FEHLER or error entry."""
        results = validate_plant_data({})
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        has_error = any(
            "FEHLER" in entry.upper() or "ERROR" in entry.upper()
            for entry in results
        )
        self.assertTrue(has_error, f"Expected FEHLER/error in validation results: {results}")

    @unittest.skipUnless(TEST_DATA_EXISTS, "Buechi test data not available")
    def test_valid_data_no_fehler(self):
        """Validating Buechi data returns a list with no FEHLER entries (warnings are OK)."""
        data = load_plant_data(str(TEST_DATA_PATH))
        results = validate_plant_data(data)
        self.assertIsInstance(results, list)
        fehler_entries = [e for e in results if "FEHLER" in e.upper()]
        self.assertEqual(
            len(fehler_entries), 0,
            f"Unexpected FEHLER in valid data: {fehler_entries}",
        )


if __name__ == "__main__":
    unittest.main()
