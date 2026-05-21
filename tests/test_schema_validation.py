"""Validate all existing anlagendaten.json files against expected schema."""
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJ_ROOT = Path(__file__).parent.parent
TASKS_DIR = PROJ_ROOT / "tasks" / "Risikoanalyse"


def find_all_anlagendaten():
    """Find all anlagendaten.json files in tasks/Risikoanalyse/."""
    if not TASKS_DIR.exists():
        return []
    results = []
    for project_dir in TASKS_DIR.iterdir():
        if project_dir.is_dir():
            json_file = project_dir / "anlagendaten.json"
            if json_file.exists():
                results.append(json_file)
    return results


@unittest.skipUnless(TASKS_DIR.exists(), "tasks/Risikoanalyse/ not available")
class TestSchemaValidation(unittest.TestCase):
    """Validate all anlagendaten.json files have correct structure."""

    @classmethod
    def setUpClass(cls):
        cls.files = find_all_anlagendaten()
        cls.data = {}
        for f in cls.files:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
                if isinstance(d, list) and len(d) == 1:
                    d = d[0]
                cls.data[f.parent.name] = d

    def test_at_least_one_project_exists(self):
        self.assertGreater(len(self.files), 0, "No anlagendaten.json files found")

    def test_all_have_systems(self):
        for name, data in self.data.items():
            with self.subTest(project=name):
                self.assertIn("systems", data, f"{name}: missing 'systems' key")
                self.assertIsInstance(data["systems"], list)
                self.assertGreater(len(data["systems"]), 0, f"{name}: empty systems")

    def test_all_systems_have_name(self):
        for name, data in self.data.items():
            for i, system in enumerate(data.get("systems", [])):
                with self.subTest(project=name, system_index=i):
                    self.assertIn("name", system, f"{name} system[{i}]: missing name")
                    self.assertTrue(system["name"], f"{name} system[{i}]: empty name")

    def test_systems_have_content(self):
        """Each system should have at least one content field (equipment, msrEquipment, or other data)."""
        for name, data in self.data.items():
            for i, system in enumerate(data.get("systems", [])):
                with self.subTest(project=name, system=system.get("name", i)):
                    # Systems can have equipment, msrEquipment, or other structural keys
                    content_keys = set(system.keys()) - {"name", "description"}
                    self.assertGreater(
                        len(content_keys), 0,
                        f"{name}/{system.get('name', i)}: system has no content beyond name"
                    )


if __name__ == "__main__":
    unittest.main()
