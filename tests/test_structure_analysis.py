from __future__ import annotations

"""
Tests for structure analysis of plant data.

Covers:
- analyze_structure: component extraction, count, and required fields
- Component ID format validation (KOMP-NNN pattern)
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.structure_analysis import analyze_structure
from tools.load_plant_data import load_plant_data

PROJECT_ROOT = Path(__file__).parent.parent
TEST_DATA_PATH = PROJECT_ROOT / "tasks" / "Risikoanalyse" / "Buechi_Glasreaktor_50L_20TA42" / "anlagendaten.json"
TEST_DATA_EXISTS = TEST_DATA_PATH.is_file()

KOMP_ID_PATTERN = re.compile(r"^KOMP-\d{3}$")


@unittest.skipUnless(TEST_DATA_EXISTS, "Buechi test data not available")
class TestAnalyzeStructure(unittest.TestCase):
    """Test structure analysis output for Buechi Glasreaktor data."""

    @classmethod
    def setUpClass(cls):
        cls.plant_data = load_plant_data(str(TEST_DATA_PATH))
        cls.components = analyze_structure(cls.plant_data)

    def test_returns_17_components(self):
        """Buechi data should yield exactly 17 components."""
        self.assertEqual(len(self.components), 17)

    def test_all_have_valid_komp_id(self):
        """Every component has a 'komp_id' matching KOMP-NNN."""
        for comp in self.components:
            with self.subTest(komp_id=comp.get("komp_id")):
                self.assertIn("komp_id", comp)
                self.assertRegex(comp["komp_id"], KOMP_ID_PATTERN)

    def test_all_have_name(self):
        """Every component has a non-empty 'name' string."""
        for comp in self.components:
            with self.subTest(komp_id=comp.get("komp_id")):
                self.assertIn("name", comp)
                self.assertIsInstance(comp["name"], str)
                self.assertTrue(comp["name"].strip(), "name must not be empty")

    def test_all_have_typ(self):
        """Every component has a non-empty 'typ' string."""
        for comp in self.components:
            with self.subTest(komp_id=comp.get("komp_id")):
                self.assertIn("typ", comp)
                self.assertIsInstance(comp["typ"], str)
                self.assertTrue(comp["typ"].strip(), "typ must not be empty")

    def test_all_have_kategorie(self):
        """Every component has a non-empty 'kategorie' string."""
        for comp in self.components:
            with self.subTest(komp_id=comp.get("komp_id")):
                self.assertIn("kategorie", comp)
                self.assertIsInstance(comp["kategorie"], str)
                self.assertTrue(comp["kategorie"].strip(), "kategorie must not be empty")


if __name__ == "__main__":
    unittest.main()
