from __future__ import annotations

"""
Tests for tools/reliability_lookup.py — ReliabilityDB, keyword matching, O-value suggestions.

Covers:
- ReliabilityDB initialization and index building
- get_equipment_info for known and unknown types
- get_failure_modes retrieval
- suggest_o_value via failure_rate, equipment_type, and failure_mode
- get_critical_failure_modes (all and filtered)
- list_categories and list_equipment_types
- COMPONENT_KEYWORDS matching via suggest_for_component
- Edge cases: empty data, missing keys, no match
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.reliability_lookup import (
    COMPONENT_KEYWORDS,
    ReliabilityDB,
    suggest_for_component,
)


class TestReliabilityDBInit(unittest.TestCase):
    """Test initialization and index building."""

    def test_loads_default_data(self):
        rdb = ReliabilityDB()
        self.assertIsInstance(rdb._data, dict)
        self.assertIn("equipment_categories", rdb._data)

    def test_index_contains_known_types(self):
        rdb = ReliabilityDB()
        self.assertIn("kreiselpumpe", rdb._index)
        self.assertIn("glasreaktor", rdb._index)
        self.assertIn("drucktransmitter", rdb._index)

    def test_custom_data_path(self):
        minimal = {
            "equipment_categories": {
                "test_cat": {
                    "beschreibung": "Test",
                    "typen": {
                        "test_typ": {
                            "failure_rate": 99,
                            "mtbf_hours": 1000,
                            "typische_fehlermodi": [],
                        }
                    },
                }
            },
            "o_skala_zuordnung": {"zuordnung": []},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(minimal, f)
            f.flush()
            rdb = ReliabilityDB(data_path=f.name)
        info = rdb.get_equipment_info("test_typ")
        self.assertIsNotNone(info)
        self.assertEqual(info["failure_rate"], 99)

    def test_empty_categories(self):
        empty = {"equipment_categories": {}, "o_skala_zuordnung": {"zuordnung": []}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(empty, f)
            f.flush()
            rdb = ReliabilityDB(data_path=f.name)
        self.assertEqual(rdb.list_categories(), [])
        self.assertEqual(rdb.list_equipment_types(), [])


class TestGetEquipmentInfo(unittest.TestCase):
    """Test equipment info lookup with various key formats."""

    def setUp(self):
        self.rdb = ReliabilityDB()

    def test_known_type_returns_dict(self):
        info = self.rdb.get_equipment_info("kreiselpumpe")
        self.assertIsNotNone(info)
        self.assertEqual(info["failure_rate"], 50)
        self.assertEqual(info["mtbf_hours"], 20000)

    def test_unknown_type_returns_none(self):
        info = self.rdb.get_equipment_info("fluxkompensator")
        self.assertIsNone(info)

    def test_lookup_with_spaces(self):
        """Type keys with underscores should be findable via spaces."""
        info = self.rdb.get_equipment_info("sicherheitsventil psv")
        self.assertIsNotNone(info)
        self.assertEqual(info["typ"], "sicherheitsventil_psv")

    def test_lookup_case_insensitive(self):
        info = self.rdb.get_equipment_info("Kreiselpumpe")
        self.assertIsNotNone(info)


class TestGetFailureModes(unittest.TestCase):
    """Test failure mode retrieval."""

    def setUp(self):
        self.rdb = ReliabilityDB()

    def test_returns_modes_for_known_type(self):
        modes = self.rdb.get_failure_modes("kreiselpumpe")
        self.assertIsInstance(modes, list)
        self.assertGreater(len(modes), 0)
        self.assertIn("modus", modes[0])
        self.assertIn("o_richtwert", modes[0])

    def test_returns_empty_for_unknown_type(self):
        modes = self.rdb.get_failure_modes("unknown_thing")
        self.assertEqual(modes, [])


class TestSuggestOValue(unittest.TestCase):
    """Test O-value suggestion logic."""

    def setUp(self):
        self.rdb = ReliabilityDB()

    def test_by_failure_rate_low(self):
        result = self.rdb.suggest_o_value(failure_rate_fpmh=1)
        self.assertEqual(result["o_wert"], 1)

    def test_by_failure_rate_medium(self):
        result = self.rdb.suggest_o_value(failure_rate_fpmh=50)
        self.assertEqual(result["o_wert"], 7)

    def test_by_failure_rate_very_high(self):
        result = self.rdb.suggest_o_value(failure_rate_fpmh=300)
        self.assertEqual(result["o_wert"], 10)

    def test_by_equipment_type_only(self):
        result = self.rdb.suggest_o_value(equipment_type="kreiselpumpe")
        # kreiselpumpe has failure_rate=50 → O=7
        self.assertEqual(result["o_wert"], 7)

    def test_by_equipment_and_failure_mode(self):
        result = self.rdb.suggest_o_value(
            equipment_type="drucktransmitter", failure_mode="Drift"
        )
        self.assertIsNotNone(result["o_wert"])
        self.assertIn("CCPS", result.get("quelle", ""))

    def test_no_data_returns_none_o(self):
        result = self.rdb.suggest_o_value()
        self.assertIsNone(result["o_wert"])
        self.assertIn("Keine Daten", result["begruendung"])

    def test_unknown_equipment_no_rate(self):
        result = self.rdb.suggest_o_value(equipment_type="nonexistent")
        self.assertIsNone(result["o_wert"])

    def test_failure_mode_not_matching(self):
        """Known equipment but non-matching failure mode falls back to rate."""
        result = self.rdb.suggest_o_value(
            equipment_type="kreiselpumpe", failure_mode="Totalverdampfung"
        )
        # Falls through to failure_rate lookup → O=7 for rate=50
        self.assertEqual(result["o_wert"], 7)


class TestCriticalFailureModes(unittest.TestCase):
    """Test critical failure mode filtering."""

    def setUp(self):
        self.rdb = ReliabilityDB()

    def test_returns_critical_modes_all(self):
        criticals = self.rdb.get_critical_failure_modes()
        self.assertIsInstance(criticals, list)
        self.assertGreater(len(criticals), 0)
        for c in criticals:
            self.assertTrue(c.get("kritisch", False))

    def test_critical_for_specific_type(self):
        criticals = self.rdb.get_critical_failure_modes("glasreaktor")
        self.assertGreater(len(criticals), 0)
        for c in criticals:
            self.assertEqual(c["equipment"], "glasreaktor")

    def test_no_critical_for_type_without(self):
        criticals = self.rdb.get_critical_failure_modes("kreiselpumpe")
        self.assertEqual(len(criticals), 0)


class TestListMethods(unittest.TestCase):
    """Test list_categories and list_equipment_types."""

    def setUp(self):
        self.rdb = ReliabilityDB()

    def test_list_categories_non_empty(self):
        cats = self.rdb.list_categories()
        self.assertGreater(len(cats), 0)
        self.assertIn("kategorie", cats[0])
        self.assertIn("typen", cats[0])

    def test_list_equipment_types_sorted(self):
        types = self.rdb.list_equipment_types()
        self.assertGreater(len(types), 0)
        self.assertEqual(types, sorted(types))


class TestComponentKeywords(unittest.TestCase):
    """Test COMPONENT_KEYWORDS structure and suggest_for_component matching."""

    def test_keywords_list_non_empty(self):
        self.assertGreater(len(COMPONENT_KEYWORDS), 10)

    def test_each_entry_has_keywords_and_type(self):
        for keywords, equipment_type in COMPONENT_KEYWORDS:
            self.assertIsInstance(keywords, list)
            self.assertGreater(len(keywords), 0)
            self.assertIsInstance(equipment_type, str)

    def test_suggest_glasreaktor(self):
        result = suggest_for_component("Glasreaktor R-20TA43", "prozess", "Büchi miniPilot")
        self.assertIsNotNone(result)
        self.assertEqual(result["equipment_type"], "glasreaktor")
        self.assertEqual(result["daten_konfidenz"], "hoch")

    def test_suggest_pumpe_generic(self):
        result = suggest_for_component("Pumpe P-101", "mechanisch")
        self.assertIsNotNone(result)
        self.assertEqual(result["equipment_type"], "kreiselpumpe")

    def test_suggest_dosierpumpe_specific(self):
        """Dosierpumpe should match before generic pumpe."""
        result = suggest_for_component("Dosierpumpe DP-01", "mechanisch")
        self.assertIsNotNone(result)
        self.assertIn("dosierpumpe", result["equipment_type"])

    def test_suggest_no_match(self):
        result = suggest_for_component("Schreibtischlampe", "buero")
        self.assertIsNone(result)

    def test_suggest_match_in_description(self):
        """Keyword in beschreibung should also trigger a match."""
        result = suggest_for_component("Unbekannt-001", "", "mit Berstscheibe gesichert")
        self.assertIsNotNone(result)
        self.assertEqual(result["equipment_type"], "berstscheibe")

    def test_suggest_returns_expected_keys(self):
        result = suggest_for_component("Sicherheitsventil SV-01")
        self.assertIsNotNone(result)
        expected_keys = {
            "equipment_type", "matched_keyword", "failure_rate_fpmh",
            "mtbf_hours", "fehlermodi", "quelle", "daten_konfidenz",
        }
        self.assertEqual(set(result.keys()), expected_keys)


if __name__ == "__main__":
    unittest.main()
