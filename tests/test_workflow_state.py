"""Tests for tools.workflow_state module."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import tools.workflow_state as ws
from tools.workflow_state import (
    get_autonomy_mode,
    get_next_action,
    get_report_quality,
    load_state,
    save_state,
    set_autonomy_mode,
    set_report_quality,
)


class _TempTasksMixin:
    """Creates a temporary TASKS_ROOT and patches it for each test."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.mkdtemp(prefix="ws_test_")
        self._patcher = patch.object(ws, "TASKS_ROOT", Path(self._tmpdir))
        self._patcher.start()

    def tearDown(self) -> None:
        self._patcher.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)


TASK = "Risikoanalyse/_unittest_temp"


class TestLoadState(_TempTasksMixin, unittest.TestCase):
    def test_load_nonexistent_returns_none(self) -> None:
        result = load_state(TASK)
        self.assertIsNone(result)


class TestSaveAndLoad(_TempTasksMixin, unittest.TestCase):
    def test_roundtrip_preserves_data(self) -> None:
        data = {"phase": "fmea", "components": {"K-01": {"fmea": "done"}}}
        save_state(TASK, data)
        loaded = load_state(TASK)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["phase"], "fmea")
        self.assertEqual(loaded["components"]["K-01"]["fmea"], "done")
        # save_state adds last_updated
        self.assertIn("last_updated", loaded)


class TestGetNextAction(_TempTasksMixin, unittest.TestCase):
    def test_no_state_returns_dict_with_action(self) -> None:
        result = get_next_action(TASK)
        self.assertIsInstance(result, dict)
        self.assertIn("action", result)


class TestAutonomyMode(_TempTasksMixin, unittest.TestCase):
    def test_set_and_get_gefuehrt(self) -> None:
        set_autonomy_mode(TASK, "geführt")
        self.assertEqual(get_autonomy_mode(TASK), "geführt")

    def test_set_and_get_experte(self) -> None:
        set_autonomy_mode(TASK, "experte")
        self.assertEqual(get_autonomy_mode(TASK), "experte")

    def test_set_and_get_autonom(self) -> None:
        set_autonomy_mode(TASK, "autonom")
        self.assertEqual(get_autonomy_mode(TASK), "autonom")

    def test_invalid_mode_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            set_autonomy_mode(TASK, "ungültig")


class TestReportQuality(_TempTasksMixin, unittest.TestCase):
    def test_default_is_ausfuehrlich(self) -> None:
        self.assertEqual(get_report_quality(TASK), "ausfuehrlich")

    def test_set_and_get_reduziert(self) -> None:
        set_report_quality(TASK, "reduziert")
        self.assertEqual(get_report_quality(TASK), "reduziert")

    def test_set_and_get_ausfuehrlich(self) -> None:
        set_report_quality(TASK, "ausfuehrlich")
        self.assertEqual(get_report_quality(TASK), "ausfuehrlich")

    def test_invalid_quality_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            set_report_quality(TASK, "ungültig")


if __name__ == "__main__":
    unittest.main()
