from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.report_generator import _strip_sod_prefix


class TestStripSodPrefix(unittest.TestCase):

    def test_severity_prefix_with_parens_and_colon(self):
        self.assertEqual(
            _strip_sod_prefix("S=7 (Sehr hoch): Vollausfall der Anlage"),
            "Vollausfall der Anlage",
        )

    def test_detection_prefix_with_parens_and_colon(self):
        self.assertEqual(
            _strip_sod_prefix("D=3 (Wahrscheinlich): Automatisch erkannt"),
            "Automatisch erkannt",
        )

    def test_occurrence_prefix_with_colon_no_parens(self):
        self.assertEqual(
            _strip_sod_prefix("O=5: Gelegentliches Auftreten"),
            "Gelegentliches Auftreten",
        )

    def test_spaces_around_equals(self):
        self.assertEqual(
            _strip_sod_prefix("S = 10 (Gefährlich): Todesfälle möglich"),
            "Todesfälle möglich",
        )

    def test_no_prefix_unchanged(self):
        self.assertEqual(
            _strip_sod_prefix("Kein Prefix vorhanden"),
            "Kein Prefix vorhanden",
        )

    def test_empty_string(self):
        self.assertEqual(_strip_sod_prefix(""), "")

    def test_none_input(self):
        self.assertIsNone(_strip_sod_prefix(None))

    def test_no_colon_after_parens(self):
        self.assertEqual(
            _strip_sod_prefix("S=7 (Sehr hoch) Ohne Doppelpunkt"),
            "Ohne Doppelpunkt",
        )


if __name__ == "__main__":
    unittest.main()
