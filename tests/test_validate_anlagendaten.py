"""
Tests for Gate 1: validate_anlagendaten.

7 test cases covering schema, FMEA-critical fields, value ranges,
cross-references, and consistency rules.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.validate_anlagendaten import validate_anlagendaten


def _make_valid_anlagendaten() -> dict:
    """Return a minimal but valid anlagendaten dict (Buechi-style)."""
    return {
        "teilanlage_nr": "20TA99",
        "bezeichnung": "Test-Reaktor 10L",
        "location": {
            "site": "Werk Test",
            "building": "Geb. 1",
            "room": "R100",
        },
        "processDescription": {
            "description": "Testprozess",
            "operatingMode": "Batch",
            "purpose": "Test",
            "operatingStates": ["Normalbetrieb", "Anfahren", "Abfahren"],
            "knownIncidents": [],
        },
        "betriebserfahrungen": [],
        "systems": [
            {
                "name": "Reaktor R-99",
                "type": "main",
                "description": "Testreaktor",
                "parameters": {
                    "Nennvolumen": "10 L",
                    "Material": "Edelstahl 1.4571",
                    "ExZone": "Zone 2",
                },
                "designData": [
                    {"key": "MinTemperatur", "label": "Min. Temperatur", "value": "-40", "unit": "°C"},
                    {"key": "MaxTemperatur", "label": "Max. Temperatur", "value": "200", "unit": "°C"},
                    {"key": "DesignDruck", "label": "Auslegungsdruck", "value": "6", "unit": "barg"},
                    {"key": "Betriebsdruck", "label": "Betriebsdruck", "value": "2", "unit": "barg"},
                    {"key": "Betriebstemperatur", "label": "Betriebstemperatur", "value": "80", "unit": "°C"},
                    {"key": "Nennvolumen", "label": "Nennvolumen", "value": "10", "unit": "L"},
                ],
                "processConditions": {
                    "Betriebstemperatur": "80 °C",
                    "Betriebsdruck": "2 barg",
                },
                "equipment": [],
                "msrEquipment": [
                    {
                        "name": "TIC-99",
                        "type": "Temperature Controller",
                        "sil": "SIL 1",
                        "parameters": {"Funktion": "Temperaturregelung"},
                    }
                ],
                "securityFeatures": [],
                "substanceProcessConditions": {
                    "Ethanol": {"state": "flüssig", "temperature": "80 °C"},
                },
                "connectedSystems": {
                    "upstream": [],
                    "downstream": [],
                },
            }
        ],
        "feedstocks": [
            {
                "name": "Ethanol",
                "category": "feedstock",
                "parameters": {
                    "casNumber": "64-17-5",
                    "flashPoint": "13 °C",
                    "hPhrases": "H225, H319",
                    "wgk": "1",
                },
            }
        ],
        "products": [],
        "byproducts": [],
        "media": [
            {
                "name": "Kühlwasser",
                "category": "heating-cooling",
                "failureConsequence": "Kein Kühlen möglich",
                "parameters": {"Betriebsdruck": "4 barg"},
            }
        ],
        "psa": {
            "standard": ["Schutzbrille", "Laborkittel"],
        },
        "awsv": {
            "anlage_awsv_relevant": False,
        },
    }


class _TempAnlagendaten:
    """Context manager that writes anlagendaten.json to a temp directory
    and monkey-patches the base path used by validate_anlagendaten."""

    def __init__(self, data: dict):
        self.data = data
        self._tmpdir = None
        self._orig_parent = None

    def __enter__(self):
        self._tmpdir = tempfile.mkdtemp()
        # Create directory structure: <tmpdir>/tasks/Risikoanalyse/<folder>/
        self.folder_name = "test_project"
        target_dir = Path(self._tmpdir) / "tasks" / "Risikoanalyse" / self.folder_name
        target_dir.mkdir(parents=True)
        with open(target_dir / "anlagendaten.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

        # Monkey-patch: we override Path(__file__).parent.parent in the module
        import tools.validate_anlagendaten as mod
        self._orig_func = mod.validate_anlagendaten

        base_path = Path(self._tmpdir)

        def patched_validate(task_folder, schema_path=None):
            ad_path = base_path / "tasks" / "Risikoanalyse" / task_folder / "anlagendaten.json"
            if not ad_path.exists():
                return {
                    "passed": False,
                    "fmea_readiness_pct": 0,
                    "critical": [f"anlagendaten.json nicht gefunden: {ad_path}"],
                    "warnings": [],
                    "info": [],
                    "details": {},
                }
            with open(ad_path, "r", encoding="utf-8") as fh:
                ad = json.load(fh)

            # Call the real logic by temporarily writing to the expected location
            # Instead, we use a simpler approach: call with the real function
            # but swap the base path calculation.
            return self._orig_func.__wrapped__(ad) if hasattr(self._orig_func, '__wrapped__') else self._run_real(ad)

        self._patched = patched_validate
        return self

    def _run_real(self, ad):
        """Run all validation checks with the loaded data directly."""
        # Import internals
        import tools.validate_anlagendaten as mod
        # We need to run the checks without relying on file I/O
        # Easiest: temporarily write to a known location
        import tools.validate_anlagendaten
        return None  # fallback, won't be used

    def validate(self):
        """Run validation on the temp data."""
        import tools.validate_anlagendaten as mod
        # Override the module-level path resolution
        original_file = mod.__file__
        # Create a fake __file__ that makes Path(__file__).parent.parent == self._tmpdir
        fake_tools_dir = Path(self._tmpdir) / "tools"
        fake_tools_dir.mkdir(exist_ok=True)
        mod.__file__ = str(fake_tools_dir / "validate_anlagendaten.py")
        try:
            result = mod.validate_anlagendaten(self.folder_name)
        finally:
            mod.__file__ = original_file
        return result

    def __exit__(self, *args):
        import shutil
        if self._tmpdir:
            shutil.rmtree(self._tmpdir, ignore_errors=True)


class TestValidateAnlagendaten(unittest.TestCase):
    """Gate 1 validation tests."""

    def _validate(self, data: dict) -> dict:
        """Helper: write data to temp dir and validate."""
        with _TempAnlagendaten(data) as ctx:
            return ctx.validate()

    # ------------------------------------------------------------------
    # 1. Vollständig valide Daten
    # ------------------------------------------------------------------
    def test_valid_complete(self):
        """Fully valid data passes with no criticals."""
        data = _make_valid_anlagendaten()
        result = self._validate(data)
        self.assertTrue(result["passed"], f"Expected passed=True, got criticals: {result['critical']}")
        self.assertEqual(len(result["critical"]), 0)
        self.assertGreater(result["fmea_readiness_pct"], 0)

    # ------------------------------------------------------------------
    # 2. Pflichtfeld fehlt
    # ------------------------------------------------------------------
    def test_missing_required_fields(self):
        """Missing teilanlage_nr triggers critical."""
        data = _make_valid_anlagendaten()
        del data["teilanlage_nr"]
        result = self._validate(data)
        self.assertFalse(result["passed"])
        self.assertTrue(
            any("teilanlage_nr" in c for c in result["critical"]),
            f"Expected 'teilanlage_nr' in criticals: {result['critical']}"
        )

    # ------------------------------------------------------------------
    # 3. FMEA-kritisches Feld fehlt (ExZone)
    # ------------------------------------------------------------------
    def test_missing_fmea_critical_fields(self):
        """Missing ExZone in system parameters triggers critical."""
        data = _make_valid_anlagendaten()
        del data["systems"][0]["parameters"]["ExZone"]
        result = self._validate(data)
        self.assertFalse(result["passed"])
        self.assertTrue(
            any("ExZone" in c for c in result["critical"]),
            f"Expected 'ExZone' in criticals: {result['critical']}"
        )

    # ------------------------------------------------------------------
    # 4. Wertebereich überschritten
    # ------------------------------------------------------------------
    def test_value_ranges_exceeded(self):
        """Temperature 1500°C exceeds allowed range."""
        data = _make_valid_anlagendaten()
        data["systems"][0]["designData"].append(
            {"key": "MaxTemperatur", "label": "Max. Temperatur", "value": "1500", "unit": "°C"}
        )
        # Remove the original MaxTemperatur to avoid duplicate
        data["systems"][0]["designData"] = [
            d for d in data["systems"][0]["designData"] if d["key"] != "MaxTemperatur"
        ] + [{"key": "MaxTemperatur", "label": "Max. Temperatur", "value": "1500", "unit": "°C"}]
        result = self._validate(data)
        self.assertFalse(result["passed"])
        self.assertTrue(
            any("Wertebereich" in c and "1500" in c for c in result["critical"]),
            f"Expected range violation in criticals: {result['critical']}"
        )

    # ------------------------------------------------------------------
    # 5. Cross-Reference Mismatch
    # ------------------------------------------------------------------
    def test_cross_reference_mismatch(self):
        """Feedstock not in substanceProcessConditions triggers warning."""
        data = _make_valid_anlagendaten()
        # Add a feedstock that is NOT in any system's substanceProcessConditions
        data["feedstocks"].append({
            "name": "Toluol",
            "category": "feedstock",
            "parameters": {
                "flashPoint": "4 °C",
                "hPhrases": "H225, H304, H315",
                "wgk": "2",
            },
        })
        result = self._validate(data)
        self.assertTrue(
            any("Toluol" in w for w in result["warnings"]),
            f"Expected 'Toluol' in warnings: {result['warnings']}"
        )

    # ------------------------------------------------------------------
    # 6. ATEX-Konsistenz: ExZone ohne Flammpunkt
    # ------------------------------------------------------------------
    def test_atex_consistency(self):
        """ExZone defined but no feedstock has flashPoint triggers critical."""
        data = _make_valid_anlagendaten()
        # Remove flashPoint from all feedstocks
        for fs in data["feedstocks"]:
            params = fs.get("parameters", {})
            params.pop("flashPoint", None)
            props = fs.get("properties", {})
            if isinstance(props, dict):
                props.pop("flashPoint", None)
        result = self._validate(data)
        self.assertFalse(result["passed"])
        self.assertTrue(
            any("ExZone" in c and "Flammpunkt" in c for c in result["critical"]),
            f"Expected ATEX consistency critical: {result['critical']}"
        )

    # ------------------------------------------------------------------
    # 7. WGK-Konsistenz: WGK>=2 aber AwSV nicht relevant
    # ------------------------------------------------------------------
    def test_wgk_consistency(self):
        """WGK >= 2 but awsv not relevant triggers warning."""
        data = _make_valid_anlagendaten()
        # Set WGK to 2
        data["feedstocks"][0]["parameters"]["wgk"] = "2"
        # Ensure awsv.anlage_awsv_relevant is False
        data["awsv"] = {"anlage_awsv_relevant": False}
        result = self._validate(data)
        self.assertTrue(
            any("WGK" in w for w in result["warnings"]),
            f"Expected WGK consistency warning: {result['warnings']}"
        )


if __name__ == "__main__":
    unittest.main()
