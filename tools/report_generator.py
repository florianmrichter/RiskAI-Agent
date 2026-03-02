"""
FMEA Report Generator (HTML/CSS → PDF via WeasyPrint)

Generates a professional FMEA report that visually matches the Risk AI Web-App.
The report is first rendered as HTML (Jinja2 + CSS) then converted to PDF.

Usage:
    from tools.report_generator import generate_report
    pdf_path = generate_report(project_id)
"""

import base64
import json
import sys
import tempfile
import urllib.request
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
import squarify

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage
from tools.chart_comparison import generate_comparison as _generate_chart_comparison
from config.fmea_standards import (
    S_SCALE as S_INFO,
    O_SCALE as O_INFO,
    D_SCALE as D_INFO,
    RPZ_COLORS as RPZ_HEX,
    RPZ_THRESHOLDS,
    RPZ_LABELS,
    classify_rpz,
    apply_special_rules,
)

_OUTFIT_FONT_STYLE_CACHE = None

def _get_outfit_font_style():
    """Build <style> with @font-face for Outfit 400+800, base64-encoded TTF."""
    global _OUTFIT_FONT_STYLE_CACHE
    if _OUTFIT_FONT_STYLE_CACHE is not None:
        return _OUTFIT_FONT_STYLE_CACHE

    fonts_dir = Path(__file__).parent.parent / ".tmp" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    font_urls = {
        "outfit-400.ttf": "https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4TC1C4E.ttf",
        "outfit-800.ttf": "https://fonts.gstatic.com/s/outfit/v15/QGYyz_MVcBeNP4NjuGObqx1XmO1I4bCyC4E.ttf",
    }

    css_parts = []
    for fname, url in font_urls.items():
        local = fonts_dir / fname
        if not local.exists():
            local.write_bytes(urllib.request.urlopen(url).read())
        b64 = base64.b64encode(local.read_bytes()).decode()
        weight = "400" if "400" in fname else "800"
        css_parts.append(
            f"@font-face{{font-family:'Outfit';font-style:normal;font-weight:{weight};"
            f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}"
        )

    _OUTFIT_FONT_STYLE_CACHE = "<style>" + "".join(css_parts) + "</style>"
    return _OUTFIT_FONT_STYLE_CACHE


STOP_ORDER = {"S": 0, "T": 1, "O": 2, "P": 3}
STOP_LABELS = {"S": "Substitution", "T": "Technisch", "O": "Organisatorisch", "P": "Persönlich"}
STOP_ICONS = {"S": "↻", "T": "⚙", "O": "☰", "P": "👤"}

LOGO_SVG_SMALL = """<svg style="height:6mm;width:auto;" viewBox="0 0 100 80" xmlns="http://www.w3.org/2000/svg">
<!-- Antenna -->
<line x1="50" y1="5" x2="50" y2="15" stroke="#2C2C54" stroke-width="2" stroke-linecap="round"/>
<rect x="46" y="2" width="8" height="5" rx="1" fill="#F5004F"/>

<!-- Head (cropped, no body) -->
<rect x="8" y="15" width="84" height="64" rx="6" fill="#2C2C54"/>

<!-- Glasses -->
<rect x="11" y="24" width="32" height="24" rx="7" fill="none" stroke="#E8C547" stroke-width="2.5"/>
<rect x="57" y="24" width="32" height="24" rx="7" fill="none" stroke="#E8C547" stroke-width="2.5"/>
<line x1="43" y1="36" x2="57" y2="36" stroke="#E8C547" stroke-width="2.5" stroke-linecap="round"/>
<line x1="11" y1="36" x2="8" y2="37" stroke="#E8C547" stroke-width="2" stroke-linecap="round"/>
<line x1="89" y1="36" x2="92" y2="37" stroke="#E8C547" stroke-width="2" stroke-linecap="round"/>

<!-- Eyes -->
<circle cx="27" cy="36" r="8.5" fill="#EFD9CE"/>
<circle cx="73" cy="36" r="8.5" fill="#EFD9CE"/>
<circle cx="27" cy="36" r="4.5" fill="#1a1730"/>
<circle cx="73" cy="36" r="4.5" fill="#1a1730"/>
<circle cx="29" cy="34" r="1.8" fill="#EFD9CE"/>
<circle cx="75" cy="34" r="1.8" fill="#EFD9CE"/>

<!-- Mouth -->
<path d="M34,58 Q50,66 66,58" stroke="#EFD9CE" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.4"/>

<!-- Red dot -->
<circle cx="84" cy="21" r="4" fill="#F5004F"/>
</svg>"""


# ═══════════════════════════════════════════════════════════════
# Chart Rendering (matplotlib → file path)
# ═══════════════════════════════════════════════════════════════

def _chart_path(tmp_dir: str, name: str) -> str:
    return str(Path(tmp_dir) / f"{name}.png")


def _render_rpz_donut(stats: dict, tmp_dir: str) -> str:
    order = ["kritisch", "hoch", "mittel", "niedrig"]
    dist = stats.get("rpz_distribution", {})
    vals = [dist.get(s, 0) for s in order]
    cols = [RPZ_HEX[s] for s in order]
    lbls = [f"{s.capitalize()}: {v}" for s, v in zip(order, vals)]
    total = sum(vals)
    if total == 0:
        vals, cols, lbls = [1], ["#CCC"], ["Keine Daten"]
        total = 1

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.pie(vals, colors=cols, autopct="%1.0f%%", startangle=90,
           pctdistance=0.78, textprops={"fontsize": 9, "color": "white", "fontweight": "bold"})
    ax.add_patch(plt.Circle((0, 0), 0.55, fc="white"))
    ax.text(0, 0.08, str(total), ha="center", va="center", fontsize=22, fontweight="bold", color="#1F2937")
    ax.text(0, -0.15, "Risiken", ha="center", va="center", fontsize=9, color="#6B7280")
    ax.legend(lbls, loc="lower center", fontsize=8, ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.08))
    ax.set_title("Risiko-Verteilung", fontsize=12, fontweight="bold", color="#1F2937", pad=12)

    p = _chart_path(tmp_dir, "rpz_donut")
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def _render_risk_matrix(fmea_data: list, tmp_dir: str) -> str:
    from config.fmea_standards import RPZ_THRESHOLDS

    fig, ax = plt.subplots(figsize=(9, 7.5))

    zone_colors = {
        "kritisch": "#F5004F20",
        "hoch":     "#FD7E1420",
        "mittel":   "#E8C54718",
        "niedrig":  "#00A38912",
    }
    for s_val in range(1, 11):
        for o_val in range(1, 11):
            rpz_cell = s_val * o_val
            if rpz_cell >= RPZ_THRESHOLDS["kritisch"] / 10:
                c = zone_colors["kritisch"]
            elif rpz_cell >= RPZ_THRESHOLDS["hoch"] / 10:
                c = zone_colors["hoch"]
            elif rpz_cell >= RPZ_THRESHOLDS["mittel"] / 10:
                c = zone_colors["mittel"]
            else:
                c = zone_colors["niedrig"]
            ax.add_patch(plt.Rectangle((o_val - 0.5, s_val - 0.5), 1, 1,
                                        facecolor=c, edgecolor="white", linewidth=0.5))

    rpz_norm = mcolors.Normalize(vmin=1, vmax=500)
    # Custom colormap: Teal -> Yellow -> Orange -> Pink/Red
    cmap_colors = ["#00A389", "#E8C547", "#FD7E14", "#F5004F"]
    rpz_cmap = mcolors.LinearSegmentedColormap.from_list("risk_theme", cmap_colors, N=256)

    for fm in fmea_data:
        s, o, d = fm.get("S", 0), fm.get("O", 0), fm.get("D", 0)
        rpz = fm.get("rpz", s * o * d)
        size = 6 + d * 2.0
        color = rpz_cmap(rpz_norm(min(rpz, 500)))
        ax.scatter(o, s, s=size**2, c=[color], edgecolors="white", linewidths=1.5, zorder=5)
        short = "-".join(fm.get("fehler_id", "").split("-")[-2:])
        ax.annotate(short, (o, s), textcoords="offset points", xytext=(8, 8),
                    fontsize=6.5, color="#1F2937", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

    ax.set(xlabel="Auftreten (O)", ylabel="Bedeutung (S)", xticks=range(1, 11), yticks=range(1, 11),
           xlim=(0.5, 10.5), ylim=(0.5, 10.5))
    ax.xaxis.label.set(fontsize=11, fontweight="bold", color="#1F2937")
    ax.yaxis.label.set(fontsize=11, fontweight="bold", color="#1F2937")
    ax.set_title("Risikomatrix  (S vs. O)     Größe = Detection (D)     Farbe = RPZ",
                  fontsize=11, fontweight="bold", pad=14, color="#1F2937")

    sm = plt.cm.ScalarMappable(cmap=rpz_cmap, norm=rpz_norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("RPZ", fontsize=10, fontweight="bold")

    zone_handles = [
        mpatches.Patch(facecolor="#dc354540", label=f"Kritisch (≥{RPZ_THRESHOLDS['kritisch']})"),
        mpatches.Patch(facecolor="#ff980040", label=f"Hoch (≥{RPZ_THRESHOLDS['hoch']})"),
        mpatches.Patch(facecolor="#ffc10730", label=f"Mittel (≥{RPZ_THRESHOLDS['mittel']})"),
        mpatches.Patch(facecolor="#28a74525", label=f"Niedrig (<{RPZ_THRESHOLDS['mittel']})"),
    ]
    for d_val in [2, 5, 8]:
        sz = 6 + d_val * 2.0
        zone_handles.append(
            ax.scatter([], [], s=sz**2, c="gray", alpha=0.4, edgecolors="white", linewidths=1, label=f"D = {d_val}")
        )
    ax.legend(handles=zone_handles, loc="upper left", fontsize=7, framealpha=0.9,
              title="Risikozonen / Detection (D)", title_fontsize=8)

    p = _chart_path(tmp_dir, "risk_matrix")
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def _render_treemap_single(fmea_data: list, with_measures: bool, title: str,
                           ax, corner_radius: float = 0.012):
    """Render one treemap with rounded rectangles and modern styling."""
    from matplotlib.patches import FancyBboxPatch

    items = []
    for fm in fmea_data:
        fid = fm.get("fehler_id", "?")
        short = "-".join(fid.split("-")[-2:])
        if with_measures and fm.get("measures"):
            best = min(fm["measures"], key=lambda m: int(m.get("rpz_neu") or 9999))
            rpz = int(best.get("rpz_neu") or fm.get("rpz", 1))
            st = best.get("rpz_status_neu") or fm.get("rpz_status", "niedrig")
        else:
            rpz, st = int(fm.get("rpz", 1)), fm.get("rpz_status", "niedrig")
        items.append({"short": short, "rpz": max(rpz, 5),
                      "color": RPZ_HEX.get(st, "#AAA"), "status": st})
    items.sort(key=lambda x: -x["rpz"])
    if not items:
        items = [{"short": "---", "rpz": 1, "color": "#CCC", "status": "niedrig"}]

    sizes = [i["rpz"] for i in items]
    normed = squarify.normalize_sizes(sizes, 1.0, 1.0)
    rects = squarify.squarify(normed, 0, 0, 1.0, 1.0)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="700", color="#1F2937", pad=14,
                 fontfamily="sans-serif")

    pad = 0.006
    for rect, item in zip(rects, items):
        x, y, w, h = rect["x"] + pad, rect["y"] + pad, rect["dx"] - 2*pad, rect["dy"] - 2*pad
        if w <= 0 or h <= 0:
            continue

        base_color = item["color"]
        r = min(corner_radius, w / 3, h / 3)

        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0,rounding_size={r}",
            facecolor=base_color, edgecolor="white", linewidth=1.8,
            alpha=0.92, zorder=2,
        )
        ax.add_patch(box)

        highlight = FancyBboxPatch(
            (x + 0.002, y + h * 0.55), w - 0.004, h * 0.42,
            boxstyle=f"round,pad=0,rounding_size={r * 0.7}",
            facecolor="white", edgecolor="none", alpha=0.08, zorder=3,
        )
        ax.add_patch(highlight)

        cx, cy = x + w / 2, y + h / 2
        area = w * h
        if area > 0.02:
            fs_id, fs_rpz = 8.5, 7.5
        elif area > 0.008:
            fs_id, fs_rpz = 7, 6
        else:
            fs_id, fs_rpz = 5.5, 5

        if h > 0.06:
            ax.text(cx, cy + 0.012, item["short"], ha="center", va="center",
                    fontsize=fs_id, fontweight="700", color="white",
                    fontfamily="sans-serif", zorder=4)
            ax.text(cx, cy - 0.022, str(item["rpz"]), ha="center", va="center",
                    fontsize=fs_rpz, fontweight="400", color=(1, 1, 1, 0.85),
                    fontfamily="sans-serif", zorder=4)
        else:
            ax.text(cx, cy, f"{item['short']}  {item['rpz']}", ha="center", va="center",
                    fontsize=fs_id * 0.85, fontweight="700", color="white",
                    fontfamily="sans-serif", zorder=4)


def _render_treemap_pair(fmea_data: list, tmp_dir: str) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(wspace=0.08)

    _render_treemap_single(fmea_data, False, "Initial-Risiko (Vor Maßnahmen)", ax1)
    _render_treemap_single(fmea_data, True, "Residual-Risiko (Nach Maßnahmen)", ax2)

    legend_items = [
        ("Kritisch (≥ 200)", RPZ_HEX.get("kritisch", "#F5004F")),
        ("Hoch (≥ 125)", RPZ_HEX.get("hoch", "#FD7E14")),
        ("Mittel (≥ 50)", RPZ_HEX.get("mittel", "#E8C547")),
        ("Niedrig (< 50)", RPZ_HEX.get("niedrig", "#00A389")),
    ]
    handles = [mpatches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.1",
               facecolor=c, edgecolor="none", alpha=0.92) for _, c in legend_items]
    labels = [l for l, _ in legend_items]
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.01),
               handlelength=1.2, handleheight=0.8)

    p = _chart_path(tmp_dir, "treemap_pair")
    fig.savefig(p, dpi=220, bbox_inches="tight", facecolor="white", pad_inches=0.3)
    plt.close(fig)
    return p


def _render_rpz_comparison(fmea_data: list, tmp_dir: str):
    items = [fm for fm in fmea_data if fm.get("measures")]
    if not items:
        return None
    items.sort(key=lambda x: x.get("rpz", 0), reverse=True)
    labels, before, after = [], [], []
    for fm in items:
        labels.append("-".join(fm.get("fehler_id", "?").split("-")[-2:]))
        before.append(fm.get("rpz", 0))
        best = min(fm["measures"], key=lambda m: (m.get("rpz_neu") or 9999))
        after.append(best.get("rpz_neu") or fm.get("rpz", 0))
    y = np.arange(len(labels))
    h = 0.35
    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 0.6 + 1)))
    ax.barh(y + h / 2, before, h, label="Vorher", color="#F5004F", alpha=0.85)
    ax.barh(y - h / 2, after, h, label="Nachher", color="#00A389", alpha=0.85)
    ax.axvline(x=100, color="#E8C547", linestyle="--", linewidth=1.2, alpha=0.7, label="Grenzwert 100")
    ax.set(yticks=y, xlabel="RPZ")
    ax.set_yticklabels(labels, fontsize=9)
    ax.xaxis.label.set(fontsize=11, fontweight="bold")
    ax.set_title("RPZ-Vergleich: Vorher vs. Nachher", fontsize=12, fontweight="bold", pad=12, color="#1F2937")
    ax.legend(loc="lower right", fontsize=8)
    ax.invert_yaxis()

    p = _chart_path(tmp_dir, "rpz_comparison")
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


# ═══════════════════════════════════════════════════════════════
# Template Helpers (exposed to Jinja2)
# ═══════════════════════════════════════════════════════════════

def _sod_data(fm: dict):
    """Yield (key, value, css_class, label, info_tuple) for S, O, D."""
    yield ("S", fm.get("S", 0), "s", "Bedeutung (S)", S_INFO.get(fm.get("S", 0), ("", "")))
    yield ("O", fm.get("O", 0), "o", "Auftreten (O)", O_INFO.get(fm.get("O", 0), ("", "")))
    yield ("D", fm.get("D", 0), "d", "Entdeckung (D)", D_INFO.get(fm.get("D", 0), ("", "")))


def _rpz_color(status: str) -> str:
    return RPZ_HEX.get(status, "#6B7280")


# ═══════════════════════════════════════════════════════════════
# Plant Data Loader (RTF → JSON)
# ═══════════════════════════════════════════════════════════════

def _load_plant_data(path: str = None, task_folder: str = None) -> dict:
    """Load plant data from JSON or RTF file."""
    tasks_root = Path(__file__).parent.parent / "tasks"
    base = tasks_root / (task_folder or "Risikoanalyse/Ethylacetatproduktion_20TA41")

    if path:
        candidates = [Path(path)]
    else:
        candidates = [
            base / "anlagendaten.json",
            base / "Anlagendaten.json",
            base / "Anlagendaten.rtf",
        ]

    for p in candidates:
        if not p.exists():
            continue

        raw = p.read_text(encoding="utf-8", errors="replace")

        if p.suffix.lower() == ".json":
            try:
                data = json.loads(raw)
                return data[0] if isinstance(data, list) else data
            except json.JSONDecodeError:
                continue

        # RTF fallback
        try:
            from striprtf.striprtf import rtf_to_text
            text = rtf_to_text(raw)
        except ImportError:
            text = raw

        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            continue
        try:
            data = json.loads(text[start : end + 1])
            return data[0] if isinstance(data, list) and len(data) > 0 else {}
        except json.JSONDecodeError:
            continue

    return {}


# ═══════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════

def generate_report(project_id: int, output_path: str = None, db_path: str = None) -> str:
    """Generate the FMEA PDF report for a given project."""

    db = FMEAStorage(db_path)
    project = db.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    stats = db.get_project_statistics(project_id)
    fmea_data = db.get_full_fmea_data(project_id)
    components = db.get_components(project_id)

    func_details = {}
    for comp in components:
        functions = db.get_functions(comp["id"])
        for f in functions:
            func_details[f["funktion_id"]] = {
                "beschreibung": f["beschreibung"],
                "typ": f["typ"],
                "anforderungen": f.get("anforderungen", []),
                "component_name": comp["name"],
                "component_typ": comp.get("typ", ""),
            }
    db.close()

    if output_path is None:
        out_dir = Path(__file__).parent.parent / ".tmp"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f"FMEA_Bericht_{project.get('anlage_name', 'Report')}.pdf")

    template_dir = Path(__file__).parent.parent / "templates"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Render charts (convert to file:// URIs for Playwright)
        donut_img = Path(_render_rpz_donut(stats, tmp_dir)).as_uri()
        matrix_img = Path(_render_risk_matrix(fmea_data, tmp_dir)).as_uri()
        treemap_img = Path(_render_treemap_pair(fmea_data, tmp_dir)).as_uri()
        _cmp = _render_rpz_comparison(fmea_data, tmp_dir)
        comparison_img = Path(_cmp).as_uri() if _cmp else None
        _chart_cmp = _generate_chart_comparison(
            rpz_distribution=stats.get("rpz_distribution", {}),
            output_path=str(Path(tmp_dir) / "chart_comparison.png"),
        )
        chart_comparison_img = Path(_chart_cmp).as_uri()

        # Group failure modes by function
        func_groups = OrderedDict()
        for fm in fmea_data:
            fid = fm.get("funktion_id", "?")
            if fid not in func_groups:
                func_groups[fid] = {"beschreibung": fm.get("funktion_beschreibung", ""), "fms": []}
            func_groups[fid]["fms"].append(fm)

        def _stop_sort_key(m):
            return STOP_ORDER.get(m.get("stop_kategorie", ""), 99)

        for fm in fmea_data:
            if fm.get("measures"):
                fm["measures"] = sorted(fm["measures"], key=_stop_sort_key)

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

        top5 = sorted(fmea_data, key=lambda x: x.get("rpz", 0), reverse=True)[:5]
        fmea_sorted = sorted(fmea_data, key=lambda x: x.get("rpz", 0), reverse=True)
        dist = stats.get("rpz_distribution", {})
        high_risk_count = dist.get("kritisch", 0) + dist.get("hoch", 0)
        total_measures = sum(len(fm.get("measures", [])) for fm in fmea_data)

        special_rule_count = sum(1 for fm in fmea_data if fm.get("special_rule"))
        fms_with_measures = [fm for fm in fmea_data if fm.get("measures")]
        stop_coverage = {}
        for kat in ["S", "T", "O", "P"]:
            stop_coverage[kat] = sum(
                1 for fm in fmea_data
                for m in fm.get("measures", [])
                if m.get("stop_kategorie") == kat
            )
        max_rpz = max((fm.get("rpz", 0) for fm in fmea_data), default=0)
        avg_rpz = round(sum(fm.get("rpz", 0) for fm in fmea_data) / max(len(fmea_data), 1))
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

        task_folder = project.get("task_folder") or "Risikoanalyse/Ethylacetatproduktion_20TA41"
        plant_data = _load_plant_data(task_folder=task_folder)

        # Jinja2 rendering
        env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
        template = env.get_template("fmea_report.html")

        css_file = template_dir / "fmea_style.css"

        html_content = template.render(
            css_path=css_file.as_uri(),
            project=project,
            stats=stats,
            components=components,
            fmea_data=fmea_data,
            fmea_sorted=fmea_sorted,
            top5=top5,
            func_groups=func_groups,
            high_risk_count=high_risk_count,
            total_measures=total_measures,
            now=datetime.now().strftime("%d.%m.%Y %H:%M"),
            donut_img=donut_img,
            matrix_img=matrix_img,
            treemap_img=treemap_img,
            comparison_img=comparison_img,
            chart_comparison_img=chart_comparison_img,
            scales=[
                ("S", "Bedeutung (S)", S_INFO),
                ("O", "Auftreten (O)", O_INFO),
                ("D", "Entdeckung (D)", D_INFO),
            ],
            sod_data=_sod_data,
            rpz_color=_rpz_color,
            plant=plant_data,
            stop_labels=STOP_LABELS,
            stop_icons=STOP_ICONS,
            func_details=func_details,
            abe_labels={"A": "Vermeidung", "B": "Entdeckung", "E": "Abschwächung"},
            report_context={
                "special_rule_count": special_rule_count,
                "stop_coverage": stop_coverage,
                "max_rpz": max_rpz,
                "avg_rpz": avg_rpz,
                "best_reduction": best_reduction,
                "avg_reduction": avg_reduction if best_reduction else 0,
                "fms_with_measures_count": len(fms_with_measures),
            },
        )

        # Write temporary HTML to feed Playwright (it needs a file: URL for CSS)
        tmp_html = Path(tmp_dir) / "report.html"
        tmp_html.write_text(html_content, encoding="utf-8")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        project_name = project.get("name") or ""
        anlage_name = project.get("anlage_name") or ""
        # Format: "Anlagenname (Teilanlage) – Risikoanalyse"
        # e.g. "Ethylacetat-Anlage (20TA41) – Risikoanalyse"
        header_right_text = f"{project_name} ({anlage_name}) – Risikoanalyse" if anlage_name else f"{project_name} – Risikoanalyse"

        outfit_style = _get_outfit_font_style()

        ff = "Outfit,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
        header_html = (
            outfit_style +
            '<div style="width:100%;font-size:7pt;font-family:' + ff + ' !important;'
            'padding:5mm 18mm 2mm 18mm;display:flex;justify-content:space-between;'
            'align-items:center;color:#6B7280;border-bottom:0.5px solid #E5E7EB;">'
            '<div style="display:flex;align-items:center;gap:2mm;font-family:' + ff + ' !important;">' + LOGO_SVG_SMALL +
            '<span style="font-weight:800;color:#2C2C54;font-family:' + ff + ' !important;">'
            'Risk <span style="color:#F5004F;">Agent</span></span></div>'
            '<span style="font-weight:400;font-family:' + ff + ' !important;">' + header_right_text + '</span>'
            '</div>'
        )
        footer_html = (
            outfit_style +
            '<div style="width:100%;font-size:6pt;font-family:' + ff + ' !important;font-weight:400;'
            'padding:2mm 18mm 5mm 18mm;display:flex;justify-content:space-between;'
            'align-items:center;color:#D1D5DB;">'
            '<span style="font-family:' + ff + ' !important;">Vertraulich</span>'
            '<span style="font-family:' + ff + ' !important;"><span class="pageNumber"></span> / <span class="totalPages"></span></span>'
            '</div>'
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(tmp_html.as_uri(), wait_until="networkidle")
            page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template=header_html,
                footer_template=footer_html,
                margin={"top": "22mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
            )
            browser.close()

    print(f"FMEA-Bericht generiert: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/report_generator.py <project_id> [output_path]")
        sys.exit(1)
    generate_report(int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
