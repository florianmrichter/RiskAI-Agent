from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.report_generator import (
    _strip_sod_prefix,
    _rpz_color,
    _sod_data,
    _compute_matrix_data,
    _compute_treemap_data,
    _embed_images_base64,
    _load_plant_data,
    _chart_path,
    LOGO_SVG_SMALL,
    STOP_ICONS,
)
from config.fmea_standards import RPZ_COLORS, RPZ_THRESHOLDS, classify_rpz


# ═══════════════════════════════════════════════════════════════
# Helper: build minimal FM dicts for testing
# ═══════════════════════════════════════════════════════════════

def _make_fm(fehler_id="KOMP-001-F1-FM01", S=5, O=4, D=3, rpz=None,
             rpz_status=None, fehlermodus="Testfehler", measures=None,
             funktion_id="FUNC-001", **extra):
    rpz = rpz or S * O * D
    rpz_status = rpz_status or classify_rpz(rpz)
    fm = {
        "fehler_id": fehler_id,
        "S": S, "O": O, "D": D,
        "rpz": rpz,
        "rpz_status": rpz_status,
        "fehlermodus": fehlermodus,
        "funktion_id": funktion_id,
        "funktion_beschreibung": "Testfunktion",
        "komponente": "Testkomp",
        "measures": measures or [],
    }
    fm.update(extra)
    return fm


def _make_measure(name="Maßnahme A", stop_kategorie="S", rpz_neu=30,
                  rpz_status_neu="niedrig", **extra):
    m = {
        "name": name,
        "stop_kategorie": stop_kategorie,
        "rpz_neu": rpz_neu,
        "rpz_status_neu": rpz_status_neu,
        "abe_kategorie": "A",
        "prioritaet": "empfohlen",
        "aufwand": "mittel",
        "kosten_klasse": "B",
        "assigned_to": "",
        "target_date": "",
        "implementation_status": "geplant",
    }
    m.update(extra)
    return m


# ═══════════════════════════════════════════════════════════════
# 1) strip_sod_prefix (existing — keep as-is)
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# 2) _rpz_color
# ═══════════════════════════════════════════════════════════════

class TestRpzColor(unittest.TestCase):

    def test_returns_kritisch_color(self):
        self.assertEqual(_rpz_color("kritisch"), RPZ_COLORS["kritisch"])

    def test_returns_hoch_color(self):
        self.assertEqual(_rpz_color("hoch"), RPZ_COLORS["hoch"])

    def test_returns_mittel_color(self):
        self.assertEqual(_rpz_color("mittel"), RPZ_COLORS["mittel"])

    def test_returns_niedrig_color(self):
        self.assertEqual(_rpz_color("niedrig"), RPZ_COLORS["niedrig"])

    def test_unknown_status_returns_fallback(self):
        self.assertEqual(_rpz_color("unbekannt"), "#6B7280")

    def test_empty_string_returns_fallback(self):
        self.assertEqual(_rpz_color(""), "#6B7280")


# ═══════════════════════════════════════════════════════════════
# 3) _sod_data generator
# ═══════════════════════════════════════════════════════════════

class TestSodData(unittest.TestCase):

    def test_yields_three_tuples(self):
        fm = {"S": 5, "O": 3, "D": 7}
        result = list(_sod_data(fm))
        self.assertEqual(len(result), 3)

    def test_keys_are_s_o_d(self):
        fm = {"S": 5, "O": 3, "D": 7}
        keys = [t[0] for t in _sod_data(fm)]
        self.assertEqual(keys, ["S", "O", "D"])

    def test_values_match_fm(self):
        fm = {"S": 8, "O": 2, "D": 4}
        vals = [t[1] for t in _sod_data(fm)]
        self.assertEqual(vals, [8, 2, 4])

    def test_missing_keys_default_to_zero(self):
        fm = {}
        vals = [t[1] for t in _sod_data(fm)]
        self.assertEqual(vals, [0, 0, 0])


# ═══════════════════════════════════════════════════════════════
# 4) _compute_matrix_data
# ═══════════════════════════════════════════════════════════════

class TestComputeMatrixData(unittest.TestCase):

    def test_empty_fmea_returns_empty_points(self):
        result = _compute_matrix_data([])
        self.assertEqual(result["points"], [])
        self.assertEqual(result["zones"], [])
        self.assertEqual(result["cols"], 10)
        self.assertEqual(result["rows"], 10)

    def test_single_fm_returns_one_point(self):
        fms = [_make_fm(S=5, O=4, D=3)]
        result = _compute_matrix_data(fms)
        self.assertEqual(len(result["points"]), 1)

    def test_zones_always_100_cells(self):
        fms = [_make_fm(S=5, O=4, D=3)]
        result = _compute_matrix_data(fms)
        self.assertEqual(len(result["zones"]), 100)  # 10x10 grid

    def test_point_has_required_keys(self):
        fms = [_make_fm(S=7, O=6, D=5, fehler_id="KOMP-001-F1-FM03")]
        point = _compute_matrix_data(fms)["points"][0]
        for key in ("fehler_id", "short", "s", "o", "d", "rpz", "rpz_status",
                     "col", "row", "size", "color", "zindex"):
            self.assertIn(key, point, f"Missing key: {key}")

    def test_short_label_extracts_last_segment(self):
        fms = [_make_fm(fehler_id="KOMP-001-F1-FM07")]
        point = _compute_matrix_data(fms)["points"][0]
        self.assertEqual(point["short"], "FM07")

    def test_multiple_fms_same_cell_jitter(self):
        """Two FMs at same S,O should have different col/row positions."""
        fms = [
            _make_fm(fehler_id="KOMP-001-F1-FM01", S=5, O=4, D=3),
            _make_fm(fehler_id="KOMP-001-F1-FM02", S=5, O=4, D=6),
        ]
        result = _compute_matrix_data(fms)
        pts = result["points"]
        self.assertEqual(len(pts), 2)
        # Jittered points should differ in at least col or row
        self.assertFalse(
            pts[0]["col"] == pts[1]["col"] and pts[0]["row"] == pts[1]["row"],
            "Two FMs in same cell should be jittered apart",
        )

    def test_zone_classification_niedrig(self):
        """S=1, O=1 cell should be classified as 'niedrig'."""
        fms = [_make_fm(S=1, O=1, D=1)]
        result = _compute_matrix_data(fms)
        zone_1_1 = [z for z in result["zones"] if z["s"] == 1 and z["o"] == 1]
        self.assertEqual(len(zone_1_1), 1)
        self.assertEqual(zone_1_1[0]["zone"], "niedrig")

    def test_zone_classification_high_corner(self):
        """S=10, O=10 cell should be 'kritisch'."""
        fms = [_make_fm(S=10, O=10, D=10)]
        result = _compute_matrix_data(fms)
        zone_10_10 = [z for z in result["zones"] if z["s"] == 10 and z["o"] == 10]
        self.assertEqual(zone_10_10[0]["zone"], "kritisch")

    def test_point_color_is_rgb_string(self):
        fms = [_make_fm(S=5, O=4, D=3)]
        point = _compute_matrix_data(fms)["points"][0]
        self.assertTrue(point["color"].startswith("rgb("))


# ═══════════════════════════════════════════════════════════════
# 5) _compute_treemap_data
# ═══════════════════════════════════════════════════════════════

class TestComputeTreemapData(unittest.TestCase):

    def test_empty_fmea_returns_empty(self):
        self.assertEqual(_compute_treemap_data([], with_measures=False), [])

    def test_single_fm_returns_one_rect(self):
        fms = [_make_fm(rpz=100, rpz_status="mittel")]
        result = _compute_treemap_data(fms, with_measures=False)
        self.assertEqual(len(result), 1)

    def test_rect_has_layout_keys(self):
        fms = [_make_fm(rpz=100, rpz_status="mittel")]
        item = _compute_treemap_data(fms, with_measures=False)[0]
        for key in ("x", "y", "w", "h", "fehler_id", "short", "rpz", "color", "status"):
            self.assertIn(key, item, f"Missing key: {key}")

    def test_with_measures_uses_best_rpz_neu(self):
        m1 = _make_measure(rpz_neu=50, rpz_status_neu="niedrig")
        m2 = _make_measure(rpz_neu=20, rpz_status_neu="niedrig")
        fms = [_make_fm(rpz=200, rpz_status="hoch", measures=[m1, m2])]
        result = _compute_treemap_data(fms, with_measures=True)
        # Should pick the measure with lowest rpz_neu (20), but clamped to min 5
        self.assertEqual(result[0]["rpz"], 20)

    def test_without_measures_uses_original_rpz(self):
        m = _make_measure(rpz_neu=20)
        fms = [_make_fm(rpz=200, rpz_status="hoch", measures=[m])]
        result = _compute_treemap_data(fms, with_measures=False)
        self.assertEqual(result[0]["rpz"], 200)

    def test_rpz_clamped_to_min_5(self):
        fms = [_make_fm(rpz=2, rpz_status="niedrig")]
        result = _compute_treemap_data(fms, with_measures=False)
        self.assertGreaterEqual(result[0]["rpz"], 5)

    def test_sorted_descending_by_rpz(self):
        fms = [
            _make_fm(fehler_id="A", rpz=50, rpz_status="niedrig"),
            _make_fm(fehler_id="B", rpz=300, rpz_status="kritisch"),
            _make_fm(fehler_id="C", rpz=150, rpz_status="hoch"),
        ]
        result = _compute_treemap_data(fms, with_measures=False)
        rpz_values = [r["rpz"] for r in result]
        self.assertEqual(rpz_values, sorted(rpz_values, reverse=True))

    def test_color_matches_rpz_status(self):
        fms = [_make_fm(rpz=350, rpz_status="kritisch")]
        result = _compute_treemap_data(fms, with_measures=False)
        self.assertEqual(result[0]["color"], RPZ_COLORS["kritisch"])

    def test_short_label_two_segments(self):
        fms = [_make_fm(fehler_id="KOMP-002-F3-FM12", rpz=100)]
        result = _compute_treemap_data(fms, with_measures=False)
        self.assertEqual(result[0]["short"], "F3-FM12")


# ═══════════════════════════════════════════════════════════════
# 6) _embed_images_base64
# ═══════════════════════════════════════════════════════════════

class TestEmbedImagesBase64(unittest.TestCase):

    def test_no_file_uris_unchanged(self):
        html = '<img src="https://example.com/img.png">'
        self.assertEqual(_embed_images_base64(html), html)

    def test_file_uri_replaced_with_base64(self):
        # Create a tiny temp file to embed
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # minimal PNG header bytes
            tmp_path = f.name
        try:
            html = f'<img src="file://{tmp_path}">'
            result = _embed_images_base64(html)
            self.assertIn("data:image/png;base64,", result)
            self.assertNotIn("file://", result)
        finally:
            os.unlink(tmp_path)

    def test_nonexistent_file_uri_unchanged(self):
        html = '<img src="file:///nonexistent/path/img.png">'
        self.assertEqual(_embed_images_base64(html), html)

    def test_multiple_file_uris(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x89PNG")
            tmp_path = f.name
        try:
            html = f'<img src="file://{tmp_path}"><img src="file://{tmp_path}">'
            result = _embed_images_base64(html)
            self.assertEqual(result.count("data:image/png;base64,"), 2)
        finally:
            os.unlink(tmp_path)


# ═══════════════════════════════════════════════════════════════
# 7) _chart_path
# ═══════════════════════════════════════════════════════════════

class TestChartPath(unittest.TestCase):

    def test_returns_png_path(self):
        result = _chart_path("/tmp/charts", "risk_matrix")
        self.assertEqual(result, "/tmp/charts/risk_matrix.png")

    def test_path_type_is_string(self):
        result = _chart_path("/some/dir", "treemap")
        self.assertIsInstance(result, str)


# ═══════════════════════════════════════════════════════════════
# 8) _load_plant_data
# ═══════════════════════════════════════════════════════════════

class TestLoadPlantData(unittest.TestCase):

    def test_loads_json_dict(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"anlage": "Test", "systems": []}, f)
            tmp_path = f.name
        try:
            result = _load_plant_data(path=tmp_path)
            self.assertEqual(result["anlage"], "Test")
        finally:
            os.unlink(tmp_path)

    def test_loads_json_list_returns_first(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"anlage": "First"}, {"anlage": "Second"}], f)
            tmp_path = f.name
        try:
            result = _load_plant_data(path=tmp_path)
            self.assertEqual(result["anlage"], "First")
        finally:
            os.unlink(tmp_path)

    def test_nonexistent_path_returns_empty(self):
        result = _load_plant_data(path="/nonexistent/path/data.json")
        self.assertEqual(result, {})

    def test_invalid_json_returns_empty(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {{{")
            tmp_path = f.name
        try:
            result = _load_plant_data(path=tmp_path)
            self.assertEqual(result, {})
        finally:
            os.unlink(tmp_path)

    def test_missing_task_folder_raises(self):
        with self.assertRaises(ValueError):
            _load_plant_data(path=None, task_folder=None)


# ═══════════════════════════════════════════════════════════════
# 9) Constants & module-level objects
# ═══════════════════════════════════════════════════════════════

class TestModuleConstants(unittest.TestCase):

    def test_stop_icons_has_four_keys(self):
        self.assertEqual(set(STOP_ICONS.keys()), {"S", "T", "O", "P"})

    def test_logo_svg_is_valid_svg(self):
        self.assertIn("<svg", LOGO_SVG_SMALL)
        self.assertIn("</svg>", LOGO_SVG_SMALL)


# ═══════════════════════════════════════════════════════════════
# 10) Jinja2 template loading (smoke test)
# ═══════════════════════════════════════════════════════════════

class TestTemplateLoading(unittest.TestCase):

    def test_template_file_exists(self):
        template_dir = Path(__file__).parent.parent / "templates"
        self.assertTrue((template_dir / "fmea_report.html").exists())

    def test_jinja_env_loads_template(self):
        from jinja2 import Environment, FileSystemLoader
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
        template = env.get_template("fmea_report.html")
        self.assertIsNotNone(template)

    def test_strip_sod_prefix_as_jinja_filter(self):
        from jinja2 import Environment, FileSystemLoader
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
        env.filters["strip_sod_prefix"] = _strip_sod_prefix
        # Quick inline template to verify filter works in Jinja context
        t = env.from_string("{{ text|strip_sod_prefix }}")
        result = t.render(text="S=5 (Hoch): Druckverlust")
        self.assertEqual(result, "Druckverlust")


# ═══════════════════════════════════════════════════════════════
# 11) FM grouping / sorting logic (from generate_report)
# ═══════════════════════════════════════════════════════════════

class TestFMGroupingAndSorting(unittest.TestCase):
    """Test the grouping/sorting logic used inside generate_report."""

    def test_group_by_funktion_id(self):
        fms = [
            _make_fm(fehler_id="A", funktion_id="F1"),
            _make_fm(fehler_id="B", funktion_id="F2"),
            _make_fm(fehler_id="C", funktion_id="F1"),
        ]
        func_groups = OrderedDict()
        for fm in fms:
            fid = fm.get("funktion_id", "?")
            if fid not in func_groups:
                func_groups[fid] = {"fms": []}
            func_groups[fid]["fms"].append(fm)
        self.assertEqual(len(func_groups), 2)
        self.assertEqual(len(func_groups["F1"]["fms"]), 2)
        self.assertEqual(len(func_groups["F2"]["fms"]), 1)

    def test_top5_sorted_by_rpz_descending(self):
        fms = [_make_fm(fehler_id=f"FM{i}", rpz=i * 50) for i in range(1, 8)]
        top5 = sorted(fms, key=lambda x: x.get("rpz", 0), reverse=True)[:5]
        self.assertEqual(len(top5), 5)
        self.assertEqual(top5[0]["rpz"], 350)
        self.assertEqual(top5[4]["rpz"], 150)

    def test_measures_sorted_by_stop_order(self):
        from tools._base import STOP_ORDER
        measures = [
            _make_measure(stop_kategorie="P"),
            _make_measure(stop_kategorie="S"),
            _make_measure(stop_kategorie="O"),
            _make_measure(stop_kategorie="T"),
        ]
        sorted_m = sorted(measures, key=lambda m: STOP_ORDER.get(m.get("stop_kategorie", ""), 99))
        cats = [m["stop_kategorie"] for m in sorted_m]
        self.assertEqual(cats, ["S", "T", "O", "P"])


# ═══════════════════════════════════════════════════════════════
# 12) Report context aggregation logic
# ═══════════════════════════════════════════════════════════════

class TestReportContextAggregation(unittest.TestCase):
    """Test the aggregation logic that generate_report uses to build context."""

    def _build_context(self, fmea_data):
        """Replicate the aggregation logic from generate_report."""
        total_measures = sum(len(fm.get("measures", [])) for fm in fmea_data)
        fms_with_measures = [fm for fm in fmea_data if fm.get("measures")]
        max_rpz = max((fm.get("rpz", 0) for fm in fmea_data), default=0)
        avg_rpz = round(sum(fm.get("rpz", 0) for fm in fmea_data) / max(len(fmea_data), 1))

        stop_coverage = {}
        for kat in ["S", "T", "O", "P"]:
            stop_coverage[kat] = sum(
                1 for fm in fmea_data
                for m in fm.get("measures", [])
                if m.get("stop_kategorie") == kat
            )

        best_reduction = None
        avg_reduction = 0
        if fms_with_measures:
            reductions = []
            for fm in fms_with_measures:
                best = min(fm["measures"], key=lambda m: m.get("rpz_neu") or 9999)
                if best.get("rpz_neu"):
                    reductions.append(fm["rpz"] - best["rpz_neu"])
            if reductions:
                best_reduction = max(reductions)
                avg_reduction = round(sum(reductions) / len(reductions))

        return {
            "total_measures": total_measures,
            "max_rpz": max_rpz,
            "avg_rpz": avg_rpz,
            "stop_coverage": stop_coverage,
            "best_reduction": best_reduction,
            "avg_reduction": avg_reduction,
            "fms_with_measures_count": len(fms_with_measures),
        }

    def test_empty_fmea_aggregation(self):
        ctx = self._build_context([])
        self.assertEqual(ctx["total_measures"], 0)
        self.assertEqual(ctx["max_rpz"], 0)
        self.assertEqual(ctx["avg_rpz"], 0)
        self.assertIsNone(ctx["best_reduction"])

    def test_single_fm_no_measures(self):
        fms = [_make_fm(rpz=120)]
        ctx = self._build_context(fms)
        self.assertEqual(ctx["total_measures"], 0)
        self.assertEqual(ctx["max_rpz"], 120)
        self.assertEqual(ctx["avg_rpz"], 120)
        self.assertEqual(ctx["fms_with_measures_count"], 0)

    def test_measures_counted_correctly(self):
        fms = [
            _make_fm(rpz=200, measures=[_make_measure(), _make_measure()]),
            _make_fm(rpz=100, measures=[_make_measure()]),
        ]
        ctx = self._build_context(fms)
        self.assertEqual(ctx["total_measures"], 3)
        self.assertEqual(ctx["fms_with_measures_count"], 2)

    def test_best_reduction_calculated(self):
        fms = [
            _make_fm(rpz=300, measures=[_make_measure(rpz_neu=50)]),
            _make_fm(rpz=200, measures=[_make_measure(rpz_neu=100)]),
        ]
        ctx = self._build_context(fms)
        # 300-50=250, 200-100=100 → best=250
        self.assertEqual(ctx["best_reduction"], 250)
        self.assertEqual(ctx["avg_reduction"], 175)  # (250+100)/2

    def test_stop_coverage_counts(self):
        fms = [
            _make_fm(measures=[
                _make_measure(stop_kategorie="S"),
                _make_measure(stop_kategorie="T"),
            ]),
            _make_fm(measures=[
                _make_measure(stop_kategorie="S"),
            ]),
        ]
        ctx = self._build_context(fms)
        self.assertEqual(ctx["stop_coverage"]["S"], 2)
        self.assertEqual(ctx["stop_coverage"]["T"], 1)
        self.assertEqual(ctx["stop_coverage"]["O"], 0)
        self.assertEqual(ctx["stop_coverage"]["P"], 0)

    def test_avg_rpz_rounded(self):
        fms = [_make_fm(rpz=101), _make_fm(rpz=102)]
        ctx = self._build_context(fms)
        # (101+102)/2 = 101.5 → rounds to 102
        self.assertEqual(ctx["avg_rpz"], 102)


# ═══════════════════════════════════════════════════════════════
# 13) Cockpit rows logic
# ═══════════════════════════════════════════════════════════════

class TestCockpitRows(unittest.TestCase):

    def _build_cockpit(self, fmea_data):
        cockpit_rows = []
        for fm in fmea_data:
            for m in fm.get("measures", []):
                rpz_vorher = fm.get("rpz", 0)
                rpz_nachher = m.get("rpz_neu") or rpz_vorher
                delta = rpz_vorher - rpz_nachher
                cockpit_rows.append({
                    "fehler_id": fm.get("fehler_id", ""),
                    "massnahme_name": m.get("name", ""),
                    "rpz_vorher": rpz_vorher,
                    "rpz_nachher": rpz_nachher,
                    "rpz_delta": delta,
                })
        cockpit_rows.sort(key=lambda x: x["rpz_delta"], reverse=True)
        return cockpit_rows

    def test_empty_measures_no_rows(self):
        fms = [_make_fm(measures=[])]
        self.assertEqual(self._build_cockpit(fms), [])

    def test_sorted_by_delta_descending(self):
        fms = [
            _make_fm(fehler_id="A", rpz=300, measures=[_make_measure(rpz_neu=200)]),
            _make_fm(fehler_id="B", rpz=400, measures=[_make_measure(rpz_neu=50)]),
        ]
        rows = self._build_cockpit(fms)
        self.assertEqual(rows[0]["fehler_id"], "B")  # delta 350
        self.assertEqual(rows[1]["fehler_id"], "A")  # delta 100

    def test_delta_calculation(self):
        fms = [_make_fm(rpz=250, measures=[_make_measure(rpz_neu=75)])]
        rows = self._build_cockpit(fms)
        self.assertEqual(rows[0]["rpz_delta"], 175)


# ═══════════════════════════════════════════════════════════════
# 14) Special rules integration
# ═══════════════════════════════════════════════════════════════

class TestSpecialRulesIntegration(unittest.TestCase):
    """Test the special_rule annotation logic from generate_report."""

    def _annotate_fm(self, fm):
        from config.fmea_standards import classify_rpz, apply_special_rules
        S, O, D = fm.get("S", 0), fm.get("O", 0), fm.get("D", 0)
        rpz = fm.get("rpz", S * O * D)
        calc_status = classify_rpz(rpz)
        final_status, rule_desc = apply_special_rules(S, O, D, calc_status)
        if rule_desc:
            fm["special_rule"] = {
                "description": rule_desc,
                "calculated_status": calc_status,
                "final_status": final_status,
            }
        return fm

    def test_severity_9_override_to_hoch(self):
        fm = _make_fm(S=9, O=1, D=1, rpz=9, rpz_status="niedrig")
        result = self._annotate_fm(fm)
        self.assertIn("special_rule", result)
        self.assertEqual(result["special_rule"]["final_status"], "hoch")

    def test_no_override_for_normal_fm(self):
        fm = _make_fm(S=5, O=4, D=3, rpz=60, rpz_status="niedrig")
        result = self._annotate_fm(fm)
        self.assertNotIn("special_rule", result)

    def test_detection_severity_override_to_kritisch(self):
        fm = _make_fm(S=8, O=2, D=9, rpz=144, rpz_status="mittel")
        result = self._annotate_fm(fm)
        self.assertIn("special_rule", result)
        self.assertEqual(result["special_rule"]["final_status"], "kritisch")


if __name__ == "__main__":
    unittest.main()
