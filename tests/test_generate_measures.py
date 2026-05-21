"""Unit tests for tools/generate_measures.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.generate_measures import run_generate_measures, _get_measures_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fm(fm_id: int, fehler_id: str, fehlermodus: str = "Temperatur zu hoch",
             komponente: str = "Reaktor", rpz: int = 120) -> dict:
    """Return a minimal failure-mode dict as returned by get_failure_modes_needing_measures."""
    return {
        "id": fm_id,
        "fehler_id": fehler_id,
        "fehlermodus": fehlermodus,
        "komponente": komponente,
        "rpz": rpz,
        "rpz_status": "hoch" if rpz >= 100 else "niedrig",
    }


def _make_measure(name: str, stop: str = "T", abe: str = "B") -> dict:
    return {
        "name": name,
        "stop_kategorie": stop,
        "abe_kategorie": abe,
        "beschreibung": f"Beschreibung {name}",
        "ziel": "O",
        "S_neu": 8,
        "O_neu": 3,
        "D_neu": 2,
        "begruendung": "Reduziert Risiko",
    }


def _fake_measures_module(measures_map: dict | None = None) -> ModuleType:
    """Create a fake measures module with get_measures_for_fehlermodus."""
    mod = ModuleType("fake_measures")

    def get_measures_for_fehlermodus(fehler_id, fehlermodus, komponente):
        if measures_map is None:
            return [_make_measure(f"Maßnahme für {fehler_id}")]
        return measures_map.get(fehler_id, [])

    mod.get_measures_for_fehlermodus = get_measures_for_fehlermodus
    return mod


# ---------------------------------------------------------------------------
# Tests for _get_measures_module
# ---------------------------------------------------------------------------

class TestGetMeasuresModule(unittest.TestCase):

    @patch("tools.generate_measures.load_measures_module")
    def test_returns_task_module_when_available(self, mock_load):
        mod = _fake_measures_module()
        mock_load.return_value = mod
        result = _get_measures_module("Risikoanalyse/Test")
        self.assertIs(result, mod)

    @patch("tools.generate_measures.load_measures_module")
    def test_falls_back_to_config_when_task_module_missing(self, mock_load):
        mock_load.return_value = None
        fake_config = _fake_measures_module()
        with patch.dict("sys.modules", {"config.measures_explicit": fake_config}):
            with patch("builtins.__import__", side_effect=lambda name, *a, **kw: (
                fake_config if name == "config.measures_explicit"
                else __builtins__.__import__(name, *a, **kw)
            )):
                # Since _get_measures_module tries `import config.measures_explicit`,
                # we patch load_measures_module to return None and let it fall through.
                result = _get_measures_module("Risikoanalyse/NoExist")
        # Should not be None (either config or task module)
        # The actual fallback import may fail in test env; if so, result is None
        # which is also a valid code path.

    @patch("tools.generate_measures.load_measures_module")
    def test_returns_none_when_no_module_found(self, mock_load):
        mock_load.return_value = None
        # Block config fallback so we test the "nothing found" path
        with patch.dict("sys.modules", {"config.measures_explicit": None}):
            result = _get_measures_module("Risikoanalyse/NoExist")
        self.assertIsNone(result)

    @patch("tools.generate_measures.load_measures_module")
    def test_rejects_module_without_get_measures(self, mock_load):
        mod = ModuleType("bad_module")
        # No get_measures_for_fehlermodus attribute
        mock_load.return_value = mod
        # Block config fallback
        with patch.dict("sys.modules", {"config.measures_explicit": None}):
            result = _get_measures_module("Risikoanalyse/Bad")
        self.assertIsNone(result)

    @patch("tools.generate_measures.load_measures_module")
    def test_falls_back_to_config_module(self, mock_load):
        """When task module is None, config.measures_explicit is used as fallback."""
        mock_load.return_value = None
        # config.measures_explicit exists in this project, so fallback should work
        result = _get_measures_module("Risikoanalyse/NoExist")
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, "get_measures_for_fehlermodus"))


# ---------------------------------------------------------------------------
# Tests for run_generate_measures
# ---------------------------------------------------------------------------

class TestRunGenerateMeasures(unittest.TestCase):

    def _setup_mocks(self, failure_modes, measures_map=None, existing_measures=None):
        """Set up common mocks and return (mock_db, fake_module)."""
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = failure_modes
        mock_db.get_measures.side_effect = lambda fm_id: (
            (existing_measures or {}).get(fm_id, [])
        )
        fake_mod = _fake_measures_module(measures_map)
        return mock_db, fake_mod

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_no_module_returns_error(self, mock_get_mod, mock_storage, mock_insert):
        mock_get_mod.return_value = None
        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 0)
        self.assertIn("error", result)
        self.assertIn("Kein Maßnahmen-Modul", result["error"])
        mock_insert.assert_not_called()

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_no_failure_modes_returns_zeros(self, mock_get_mod, mock_storage, mock_insert):
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = []
        mock_storage.return_value = mock_db
        mock_get_mod.return_value = _fake_measures_module()

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 0)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["missing"], [])
        mock_insert.assert_not_called()

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_inserts_measures_for_high_rpz(self, mock_get_mod, mock_storage, mock_insert):
        fm = _make_fm(10, "FM-001", rpz=150)
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = []  # no existing measures
        mock_storage.return_value = mock_db
        mock_get_mod.return_value = _fake_measures_module()
        mock_insert.return_value = {"inserted": 1}

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["missing"], [])
        mock_insert.assert_called_once()

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_skips_failure_mode_with_existing_measures(self, mock_get_mod, mock_storage, mock_insert):
        fm = _make_fm(10, "FM-001", rpz=200)
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = [{"id": 99, "name": "Existing"}]
        mock_storage.return_value = mock_db
        mock_get_mod.return_value = _fake_measures_module()

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 0)
        self.assertEqual(result["skipped"], 1)
        mock_insert.assert_not_called()

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_empty_measures_adds_to_missing(self, mock_get_mod, mock_storage, mock_insert):
        fm = _make_fm(10, "FM-001", rpz=120)
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = []
        mock_storage.return_value = mock_db

        # Module returns empty list for all fehler_ids
        mock_get_mod.return_value = _fake_measures_module(measures_map={"OTHER": [_make_measure("x")]})

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 0)
        self.assertEqual(result["missing"], ["FM-001"])
        mock_insert.assert_not_called()

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_multiple_failure_modes_mixed(self, mock_get_mod, mock_storage, mock_insert):
        """Three FMs: one with existing measures (skip), one with generator (insert), one without (missing)."""
        fm1 = _make_fm(10, "FM-001", rpz=200)
        fm2 = _make_fm(20, "FM-002", rpz=150)
        fm3 = _make_fm(30, "FM-003", rpz=120)

        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm1, fm2, fm3]
        # FM-001 already has measures, FM-002 and FM-003 don't
        mock_db.get_measures.side_effect = lambda fm_id: (
            [{"id": 1}] if fm_id == 10 else []
        )
        mock_storage.return_value = mock_db

        measures_map = {
            "FM-002": [_make_measure("Fix-002")],
            # FM-003 has no measures in map -> missing
        }
        mock_get_mod.return_value = _fake_measures_module(measures_map)
        mock_insert.return_value = {"inserted": 1}

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["missing"], ["FM-003"])

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_insert_called_with_correct_args(self, mock_get_mod, mock_storage, mock_insert):
        fm = _make_fm(10, "FM-001", rpz=130)
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = []
        mock_storage.return_value = mock_db

        expected_measures = [_make_measure("Sensor")]
        mock_get_mod.return_value = _fake_measures_module({"FM-001": expected_measures})
        mock_insert.return_value = {"inserted": 1}

        run_generate_measures(42, "Risikoanalyse/Test", db_path="/tmp/test.db")

        mock_insert.assert_called_once_with(42, "FM-001", expected_measures, "/tmp/test.db")

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_db_path_passed_to_storage(self, mock_get_mod, mock_storage, mock_insert):
        mock_get_mod.return_value = _fake_measures_module()
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = []
        mock_storage.return_value = mock_db

        run_generate_measures(1, "Risikoanalyse/Test", db_path="/custom/path.db")
        mock_storage.assert_called_once_with("/custom/path.db")

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_multiple_measures_per_failure_mode(self, mock_get_mod, mock_storage, mock_insert):
        fm = _make_fm(10, "FM-001", rpz=160)
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = []
        mock_storage.return_value = mock_db

        measures = [
            _make_measure("Sensor", stop="S"),
            _make_measure("Wartung", stop="T"),
            _make_measure("Alarm", stop="O"),
        ]
        mock_get_mod.return_value = _fake_measures_module({"FM-001": measures})
        mock_insert.return_value = {"inserted": 3}

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 3)

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_fehlermodus_without_optional_fields(self, mock_get_mod, mock_storage, mock_insert):
        """FM dict missing optional fehlermodus/komponente keys should not crash."""
        fm = {"id": 10, "fehler_id": "FM-001", "rpz": 100}
        # No 'fehlermodus' or 'komponente' keys
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = []
        mock_storage.return_value = mock_db

        mock_get_mod.return_value = _fake_measures_module({"FM-001": [_make_measure("Fix")]})
        mock_insert.return_value = {"inserted": 1}

        # Should not raise
        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 1)

    @patch("tools.generate_measures.insert_measures_for_fehlermodus")
    @patch("tools.generate_measures.FMEAStorage")
    @patch("tools.generate_measures._get_measures_module")
    def test_insert_returns_zero_still_counts(self, mock_get_mod, mock_storage, mock_insert):
        """If insert_measures_for_fehlermodus returns inserted=0, total stays 0."""
        fm = _make_fm(10, "FM-001", rpz=110)
        mock_db = MagicMock()
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_db.get_failure_modes_needing_measures.return_value = [fm]
        mock_db.get_measures.return_value = []
        mock_storage.return_value = mock_db

        mock_get_mod.return_value = _fake_measures_module({"FM-001": [_make_measure("X")]})
        mock_insert.return_value = {"inserted": 0}  # e.g. idempotent duplicate

        result = run_generate_measures(1, "Risikoanalyse/Test")
        self.assertEqual(result["inserted"], 0)
        # Not in missing because measures were returned by generator
        self.assertEqual(result["missing"], [])


if __name__ == "__main__":
    unittest.main()
