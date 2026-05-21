"""Integration test: Full FMEA pipeline with Büchi data."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.load_plant_data import load_plant_data, validate_plant_data
from tools.structure_analysis import analyze_structure
from tools.storage import FMEAStorage

PROJ_ROOT = Path(__file__).parent.parent
BUECHI_JSON = PROJ_ROOT / "tasks" / "Risikoanalyse" / "Buechi_Glasreaktor_50L_20TA42" / "anlagendaten.json"
HAS_BUECHI = BUECHI_JSON.exists()


@unittest.skipUnless(HAS_BUECHI, "Büchi test data not available")
class TestFullPipeline(unittest.TestCase):
    """End-to-end: load → structure → DB storage."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.plant_data = load_plant_data(str(BUECHI_JSON))

    def tearDown(self):
        for suffix in ("", "-shm", "-wal"):
            try:
                os.unlink(self.db_path + suffix)
            except FileNotFoundError:
                pass

    def test_load_plant_data(self):
        self.assertIn("systems", self.plant_data)
        self.assertIsInstance(self.plant_data["systems"], list)
        self.assertGreater(len(self.plant_data["systems"]), 0)

    def test_validate_plant_data_no_errors(self):
        warnings = validate_plant_data(self.plant_data)
        errors = [w for w in warnings if "FEHLER" in w]
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")

    def test_structure_analysis(self):
        components = analyze_structure(self.plant_data)
        self.assertEqual(len(components), 17)

    def test_store_components_in_db(self):
        db = FMEAStorage(self.db_path)
        project_id = db.create_project("Büchi Test", "20TA42", task_folder="Risikoanalyse/Test")

        components = analyze_structure(self.plant_data)
        for comp in components:
            db.insert_component(
                project_id=project_id,
                komp_id=comp["komp_id"],
                name=comp["name"],
                typ=comp["typ"],
                kategorie=comp["kategorie"],
                system_name=comp.get("system_name", ""),
                beschreibung=comp.get("beschreibung", ""),
                parameters=comp.get("parameters", {}),
                kontext=comp.get("lean_context", {}),
            )

        # Verify all components stored
        for comp in components:
            stored = db.get_component_by_komp_id(comp["komp_id"])
            self.assertIsNotNone(stored, f"Component {comp['komp_id']} not found in DB")
            self.assertEqual(stored["name"], comp["name"])

        db.close()

    def test_pipeline_project_statistics(self):
        db = FMEAStorage(self.db_path)
        project_id = db.create_project("Pipeline Test", "20TA42")
        components = analyze_structure(self.plant_data)

        for comp in components:
            db.insert_component(
                project_id=project_id,
                komp_id=comp["komp_id"],
                name=comp["name"],
                typ=comp["typ"],
                kategorie=comp["kategorie"],
                system_name=comp.get("system_name", ""),
                beschreibung=comp.get("beschreibung", ""),
            )

        stats = db.get_project_statistics(project_id)
        self.assertEqual(stats["components"], 17)
        db.close()


if __name__ == "__main__":
    unittest.main()
