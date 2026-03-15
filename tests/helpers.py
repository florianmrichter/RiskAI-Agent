"""Shared test helpers -- paths, temp DB, data loaders."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJ_ROOT))

TASKS_DIR = PROJ_ROOT / "tasks" / "Risikoanalyse"
BUECHI_DIR = TASKS_DIR / "Buechi_Glasreaktor_50L_20TA42"
METHANOL_DIR = TASKS_DIR / "MethanolDosierung_10TA01"
ETHYLACETAT_DIR = TASKS_DIR / "Ethylacetatproduktion_20TA41"

BUECHI_DATA_PATH = BUECHI_DIR / "anlagendaten.json"
METHANOL_DATA_PATH = METHANOL_DIR / "anlagendaten.json"


def load_json(path):
    """Load a JSON file and return parsed data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@contextmanager
def temp_db():
    """Context manager that creates a temp SQLite DB and cleans up after."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        for suffix in ("", "-shm", "-wal"):
            try:
                os.unlink(path + suffix)
            except FileNotFoundError:
                pass


class FMEATestCase(unittest.TestCase):
    """Base test case with common helpers."""

    @classmethod
    def setUpClass(cls):
        cls.proj_root = PROJ_ROOT

    def assert_valid_komp_id(self, komp_id):
        """Assert that a component ID matches KOMP-NNN format."""
        self.assertRegex(komp_id, r"^KOMP-\d{3}$")
