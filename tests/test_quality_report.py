"""Unit tests for quality report generation."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage
from tools.observability import generate_quality_report


class TestQualityReport(unittest.TestCase):
    """Test quality report generation."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = FMEAStorage(self.db_path)
        self.project_id = self.db.create_project("Test-Projekt", "Testanlage")
        comp_id = self.db.insert_component(
            self.project_id, "K-001", "Pumpe P-201", "Pumpe",
            "Mechanisch", system_name="System",
        )
        func_id = self.db.insert_function(
            comp_id, "F-001", "Hauptfunktion", "Dosierung"
        )
        self.fm_id = self.db.insert_failure_mode(
            func_id, "FM-001", "Leckage", "Mechanisch"
        )
        self.db.insert_risk_assessment(
            self.fm_id, S=5, O=3, D=4,
        )

    def tearDown(self):
        self.db.close()
        for suffix in ("", "-shm", "-wal"):
            path = self.db_path + suffix
            if os.path.exists(path):
                os.remove(path)

    def test_report_generates_without_feedback(self):
        """Report should work even without any feedback data."""
        report = generate_quality_report(self.db_path)
        self.assertIn("Quality Report", report)
        self.assertIn("Keine", report)

    def test_report_with_feedback(self):
        """Report should include correction statistics."""
        self.db.record_confirmation(self.fm_id, self.project_id, "S", 5)
        self.db.record_correction(
            self.fm_id, self.project_id, "D", 4, 6, "Detection zu optimistisch"
        )
        report = generate_quality_report(self.db_path)
        self.assertIn("Quality Report", report)
        self.assertIn("Korrekturrate", report)

    def test_report_filtered_by_project(self):
        """Report should filter by project_id when specified."""
        self.db.record_confirmation(self.fm_id, self.project_id, "S", 5)
        report = generate_quality_report(self.db_path, project_id=self.project_id)
        self.assertIn("Test-Projekt", report)

    def test_report_contains_all_sections(self):
        """Report should contain all expected sections."""
        self.db.record_confirmation(self.fm_id, self.project_id, "S", 5)
        report = generate_quality_report(self.db_path)
        self.assertIn("Skill-Performance", report)
        self.assertIn("Schwachstellen", report)
        self.assertIn("Kalibrierungsregeln", report)
        self.assertIn("Gesamtstatistik", report)


if __name__ == "__main__":
    unittest.main()
