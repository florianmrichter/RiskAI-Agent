"""Unit tests for FMEAStorage."""
from __future__ import annotations

import os
import sys
import sqlite3
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage


class _StorageTestCase(unittest.TestCase):
    """Base class that creates a temp DB and cleans up after each test."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = FMEAStorage(self.db_path)

    def tearDown(self):
        self.db.close()
        for suffix in ("", "-shm", "-wal"):
            path = self.db_path + suffix
            if os.path.exists(path):
                os.remove(path)

    # ── helpers ──

    def _create_project(self, name="Test-Projekt", anlage="Testanlage"):
        return self.db.create_project(name, anlage)

    def _create_component(self, project_id, komp_id="K-001"):
        return self.db.insert_component(
            project_id=project_id,
            komp_id=komp_id,
            name="Reaktor",
            typ="Apparat",
            kategorie="Verfahrenstechnik",
            system_name="Reaktorsystem",
            beschreibung="Glasreaktor 50 L",
            parameters={"volumen": 50},
            kontext={"medium": "Ethylacetat"},
        )

    def _create_function(self, component_id, funktion_id="F-001"):
        return self.db.insert_function(
            component_id=component_id,
            funktion_id=funktion_id,
            typ="Prozess",
            beschreibung="Temperatur halten",
            anforderungen=["T < 80 °C"],
        )

    def _create_failure_mode(self, function_id, fehler_id="FM-001"):
        return self.db.insert_failure_mode(
            function_id=function_id,
            fehler_id=fehler_id,
            fehlermodus="Temperatur zu hoch",
            fehlerart="Funktionsverlust",
        )


class TestCreateProject(_StorageTestCase):

    def test_returns_positive_integer(self):
        pid = self._create_project()
        self.assertIsInstance(pid, int)
        self.assertGreater(pid, 0)

    def test_two_projects_get_different_ids(self):
        pid1 = self._create_project("Projekt A", "Anlage A")
        pid2 = self._create_project("Projekt B", "Anlage B")
        self.assertNotEqual(pid1, pid2)


class TestInsertComponent(_StorageTestCase):

    def test_get_component_returns_correct_data(self):
        pid = self._create_project()
        self._create_component(pid, komp_id="K-100")

        comp = self.db.get_component_by_komp_id("K-100")
        self.assertIsNotNone(comp)
        self.assertEqual(comp["komp_id"], "K-100")
        self.assertEqual(comp["name"], "Reaktor")
        self.assertEqual(comp["typ"], "Apparat")
        self.assertEqual(comp["kategorie"], "Verfahrenstechnik")
        self.assertEqual(comp["system_name"], "Reaktorsystem")
        self.assertEqual(comp["parameters"]["volumen"], 50)
        self.assertEqual(comp["kontext"]["medium"], "Ethylacetat")

    def test_get_nonexistent_component_returns_none(self):
        result = self.db.get_component_by_komp_id("DOES-NOT-EXIST")
        self.assertIsNone(result)


class TestInsertFunction(_StorageTestCase):

    def test_insert_function_no_error(self):
        pid = self._create_project()
        cid = self._create_component(pid)
        fid = self._create_function(cid, funktion_id="F-100")
        self.assertIsNotNone(fid)
        self.assertIsInstance(fid, int)

    def test_function_has_correct_funktion_id(self):
        pid = self._create_project()
        cid = self._create_component(pid)
        self._create_function(cid, funktion_id="F-200")

        func = self.db.get_function_by_funktion_id("F-200")
        self.assertIsNotNone(func)
        self.assertEqual(func["funktion_id"], "F-200")
        self.assertEqual(func["typ"], "Prozess")
        self.assertEqual(func["beschreibung"], "Temperatur halten")


class TestForeignKeys(_StorageTestCase):

    def test_component_with_invalid_project_id_raises(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.insert_component(
                project_id=99999,
                komp_id="K-BAD",
                name="Ghost",
                typ="Apparat",
                kategorie="Test",
            )

    def test_function_with_invalid_component_id_raises(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.insert_function(
                component_id=99999,
                funktion_id="F-BAD",
                typ="Prozess",
                beschreibung="Should fail",
            )


class TestRiskAssessment(_StorageTestCase):

    def test_insert_and_get_risk_assessment(self):
        pid = self._create_project()
        cid = self._create_component(pid)
        fid = self._create_function(cid)
        fm_id = self._create_failure_mode(fid)

        self.db.insert_risk_assessment(
            failure_mode_id=fm_id,
            S=7, O=4, D=6,
            begruendung_S="Schwere Verletzung",
            begruendung_O="Selten",
            begruendung_D="Erkennung schwierig",
        )
        ra = self.db.get_risk_assessment(fm_id)
        self.assertIsNotNone(ra)
        self.assertEqual(ra["S"], 7)
        self.assertEqual(ra["O"], 4)
        self.assertEqual(ra["D"], 6)
        self.assertEqual(ra["rpz"], 168)


class TestGetFullFmeaData(_StorageTestCase):

    def test_returns_nested_structure(self):
        pid = self._create_project()
        cid = self._create_component(pid)
        fid = self._create_function(cid)
        fm_id = self._create_failure_mode(fid)
        self.db.insert_risk_assessment(
            failure_mode_id=fm_id, S=5, O=3, D=2,
        )

        data = self.db.get_full_fmea_data(pid)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

        entry = data[0]
        # Each entry is a failure mode dict with nested sub-entities
        self.assertEqual(entry["fehler_id"], "FM-001")
        self.assertIn("causes", entry)
        self.assertIn("controls", entry)
        self.assertIn("measures", entry)
        self.assertIn("risk", entry)
        self.assertIsInstance(entry["causes"], list)
        self.assertIsInstance(entry["measures"], list)

    def test_includes_component_and_function_info(self):
        pid = self._create_project()
        cid = self._create_component(pid, komp_id="K-500")
        fid = self._create_function(cid, funktion_id="F-500")
        fm_id = self._create_failure_mode(fid, fehler_id="FM-500")
        self.db.insert_risk_assessment(failure_mode_id=fm_id, S=3, O=2, D=1)

        data = self.db.get_full_fmea_data(pid)
        entry = data[0]
        self.assertEqual(entry["komp_id"], "K-500")
        self.assertEqual(entry["funktion_id"], "F-500")
        self.assertEqual(entry["komponente"], "Reaktor")


if __name__ == "__main__":
    unittest.main()
