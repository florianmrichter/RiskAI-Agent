"""
FMEA Report Generator (HTML/CSS → PDF via WeasyPrint)

Generates a professional FMEA report that visually matches the Risk AI Web-App.
The report is first rendered as HTML (Jinja2 + CSS) then converted to PDF.

Usage:
    from tools.report_generator import generate_report
    pdf_path = generate_report(project_id)
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections import OrderedDict
from collections.abc import Generator
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

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage
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

_OUTFIT_FONT_STYLE_CACHE: str | None = None

def _get_outfit_font_style() -> str:
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


def _embed_images_base64(html: str) -> str:
    """Replace file:// image src URIs with base64 data URIs for standalone HTML viewing."""
    def replace_uri(m: re.Match) -> str:
        raw = m.group(1)
        # file:///path → /path
        if raw.startswith("file:///"):
            fpath = raw[7:]
        elif raw.startswith("file://"):
            fpath = raw[7:]
        else:
            return m.group(0)
        try:
            data = Path(fpath).read_bytes()
            b64 = base64.b64encode(data).decode()
            return f'src="data:image/png;base64,{b64}"'
        except Exception:
            return m.group(0)
    return re.sub(r'src="(file://[^"]+)"', replace_uri, html)


from tools._base import STOP_ORDER, STOP_LABELS
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
# Interactive Chart Data (for HTML template rendering)
# ═══════════════════════════════════════════════════════════════

def _compute_matrix_data(fmea_data: list[dict]) -> dict:
    """Compute risk matrix data for interactive SVG rendering in the template.

    Always shows the full 10x10 grid so empty zones are visible for context.
    """
    import math
    from collections import defaultdict

    if not fmea_data:
        return {"zones": [], "points": [], "cols": 10, "rows": 10}

    # Always full 10x10 grid
    s_min, s_max = 1, 10
    o_min, o_max = 1, 10
    cols, rows = 10, 10

    # Zone colors for each grid cell
    zones = []
    for s_val in range(1, 11):
        for o_val in range(1, 11):
            rpz_cell = s_val * o_val
            if rpz_cell >= RPZ_THRESHOLDS["kritisch"] / 10:
                zone = "kritisch"
            elif rpz_cell >= RPZ_THRESHOLDS["hoch"] / 10:
                zone = "hoch"
            elif rpz_cell >= RPZ_THRESHOLDS["mittel"] / 10:
                zone = "mittel"
            else:
                zone = "niedrig"
            zones.append({"s": s_val, "o": o_val, "zone": zone,
                          "col": o_val - 1, "row": 10 - s_val})

    # RPZ → color via linear interpolation
    cmap_stops = [
        (0.0, (0, 163, 137)),    # #00A389
        (0.33, (232, 197, 71)),   # #E8C547
        (0.66, (253, 126, 20)),   # #FD7E14
        (1.0, (245, 0, 79)),     # #F5004F
    ]

    def rpz_to_color(rpz: int) -> str:
        t = min(rpz, 500) / 500.0
        for i in range(len(cmap_stops) - 1):
            t0, c0 = cmap_stops[i]
            t1, c1 = cmap_stops[i + 1]
            if t <= t1:
                f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                r = int(c0[0] + f * (c1[0] - c0[0]))
                g = int(c0[1] + f * (c1[1] - c0[1]))
                b = int(c0[2] + f * (c1[2] - c0[2]))
                return f"rgb({r},{g},{b})"
        return f"rgb({cmap_stops[-1][1][0]},{cmap_stops[-1][1][1]},{cmap_stops[-1][1][2]})"

    # Group FMs by cell and compute jittered positions
    cell_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for fm in fmea_data:
        s, o = fm.get("S", 0), fm.get("O", 0)
        cell_groups[(s, o)].append(fm)

    points = []
    for (s_cell, o_cell), group in cell_groups.items():
        n = len(group)
        group.sort(key=lambda f: f.get("rpz", 0), reverse=True)
        for i, fm in enumerate(group):
            d = fm.get("D", 0)
            rpz = fm.get("rpz", s_cell * o_cell * d)
            fid = fm.get("fehler_id", "")
            # Short label: just the FM number (e.g. "FM01" from "KOMP-001-F1-FM01")
            parts = fid.split("-")
            short = parts[-1] if parts else fid

            if n == 1:
                ox, oy = 0.0, 0.0
            else:
                radius = 0.28
                angle = 2 * math.pi * i / n - math.pi / 2
                ox = radius * math.cos(angle)
                oy = radius * math.sin(angle)

            col_pos = (o_cell - 1) + 0.5 + ox
            row_pos = (10 - s_cell) + 0.5 + oy

            points.append({
                "fehler_id": fid,
                "short": short,
                "s": s_cell,
                "o": o_cell,
                "d": d,
                "rpz": rpz,
                "rpz_status": fm.get("rpz_status", "niedrig"),
                "fehlermodus": (fm.get("fehlermodus") or "")[:60],
                "col": round(col_pos, 3),
                "row": round(row_pos, 3),
                "size": 5 + d * 1.5,
                "color": rpz_to_color(rpz),
                "zindex": i,
            })

    return {"zones": zones, "points": points, "cols": cols, "rows": rows}


def _compute_treemap_data(fmea_data: list[dict], with_measures: bool) -> list[dict]:
    """Compute treemap rectangles for interactive HTML rendering."""
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
        items.append({
            "fehler_id": fid,
            "short": short,
            "rpz": max(rpz, 5),
            "color": RPZ_HEX.get(st, "#AAA"),
            "status": st,
            "fehlermodus": (fm.get("fehlermodus") or "")[:50],
        })
    items.sort(key=lambda x: -x["rpz"])
    if not items:
        return []

    sizes = [i["rpz"] for i in items]
    normed = squarify.normalize_sizes(sizes, 100.0, 100.0)
    rects = squarify.squarify(normed, 0, 0, 100.0, 100.0)

    for rect, item in zip(rects, items):
        item["x"] = round(rect["x"], 2)
        item["y"] = round(rect["y"], 2)
        item["w"] = round(rect["dx"], 2)
        item["h"] = round(rect["dy"], 2)
    return items


# ═══════════════════════════════════════════════════════════════
# Chart Rendering (matplotlib → file path) — PDF fallback
# ═══════════════════════════════════════════════════════════════

def _chart_path(tmp_dir: str, name: str) -> str:
    return str(Path(tmp_dir) / f"{name}.png")


def _render_risk_matrix(fmea_data: list[dict], tmp_dir: str) -> str:
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

    # Group FMs by grid cell (S, O) to apply jitter for overlapping bubbles
    from collections import defaultdict
    cell_groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for fm in fmea_data:
        s, o = fm.get("S", 0), fm.get("O", 0)
        cell_groups[(s, o)].append(fm)

    for (s_cell, o_cell), group in cell_groups.items():
        n = len(group)
        # Sort by RPZ descending so highest-risk bubble is on top
        group.sort(key=lambda f: f.get("rpz", 0), reverse=True)
        for i, fm in enumerate(group):
            d = fm.get("D", 0)
            rpz = fm.get("rpz", s_cell * o_cell * d)
            size = 6 + d * 2.0
            color = rpz_cmap(rpz_norm(min(rpz, 500)))

            # Jitter: distribute multiple bubbles in a cell around center
            if n == 1:
                ox, oy = 0.0, 0.0
            else:
                radius = 0.25
                angle = 2 * np.pi * i / n - np.pi / 2
                ox = radius * np.cos(angle)
                oy = radius * np.sin(angle)

            px, py = o_cell + ox, s_cell + oy
            ax.scatter(px, py, s=size**2, c=[color], edgecolors="white",
                       linewidths=1.5, zorder=5 + i, alpha=0.9)
            short = "-".join(fm.get("fehler_id", "").split("-")[-2:])
            # Stagger annotation positions to avoid label overlap
            ann_angle = 2 * np.pi * i / max(n, 2)
            ann_dx = 8 + 6 * np.cos(ann_angle)
            ann_dy = 8 + 6 * np.sin(ann_angle)
            ax.annotate(short, (px, py), textcoords="offset points",
                        xytext=(ann_dx, ann_dy),
                        fontsize=6.5, color="#1F2937", fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85),
                        zorder=10 + i)

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


def _render_treemap_single(fmea_data: list[dict], with_measures: bool, title: str,
                           ax: plt.Axes, corner_radius: float = 0.012) -> None:
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


def _render_treemap_pair(fmea_data: list[dict], tmp_dir: str) -> str:
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


# ═══════════════════════════════════════════════════════════════
# Template Helpers (exposed to Jinja2)
# ═══════════════════════════════════════════════════════════════

def _sod_data(fm: dict) -> Generator[tuple[str, int, str, str, tuple[str, str]], None, None]:
    """Yield (key, value, css_class, label, info_tuple) for S, O, D."""
    yield ("S", fm.get("S", 0), "s", "Bedeutung (S)", S_INFO.get(fm.get("S", 0), ("", "")))
    yield ("O", fm.get("O", 0), "o", "Auftreten (O)", O_INFO.get(fm.get("O", 0), ("", "")))
    yield ("D", fm.get("D", 0), "d", "Entdeckung (D)", D_INFO.get(fm.get("D", 0), ("", "")))


def _strip_sod_prefix(text: str | None) -> str | None:
    """Entfernt redundanten SOD-Prefix wie 'S=7 (Sehr hoch): ' aus Begründungstext."""
    if not text:
        return text
    return re.sub(r'^[SOD]\s*=\s*\d+\s*(\([^)]*\))?\s*:?\s*', '', text).strip()


def _rpz_color(status: str) -> str:
    return RPZ_HEX.get(status, "#6B7280")


# ═══════════════════════════════════════════════════════════════
# Plant Data Loader (RTF → JSON)
# ═══════════════════════════════════════════════════════════════

def _load_plant_data(path: str | None = None, task_folder: str | None = None) -> dict:
    """Load plant data from JSON or RTF file."""
    tasks_root = Path(__file__).parent.parent / "tasks"
    if path:
        candidates = [Path(path)]
    else:
        if not task_folder:
            raise ValueError("task_folder erforderlich wenn path nicht angegeben")
        base = tasks_root / task_folder
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

def generate_report(project_id: int, output_path: str | None = None, task_folder: str | None = None, db_path: str | None = None, css_name: str = "fmea_style.css") -> str:
    """Generate the FMEA PDF report for a given project."""

    with FMEAStorage(db_path) as db:
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

    if output_path is None:
        if task_folder:
            out_dir = Path(__file__).parent.parent / "tasks" / task_folder
        else:
            out_dir = Path(__file__).parent.parent / ".tmp"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f"FMEA_Bericht_{project.get('anlage_name', 'Report')}.pdf")

    template_dir = Path(__file__).parent.parent / "templates"

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Compute interactive chart data (for clickable HTML charts)
        matrix_data = _compute_matrix_data(fmea_data)
        treemap_before = _compute_treemap_data(fmea_data, with_measures=False)
        treemap_after = _compute_treemap_data(fmea_data, with_measures=True)

        # Group failure modes by function
        func_groups = OrderedDict()
        for fm in fmea_data:
            fid = fm.get("funktion_id", "?")
            if fid not in func_groups:
                func_groups[fid] = {"beschreibung": fm.get("funktion_beschreibung", ""), "fms": []}
            func_groups[fid]["fms"].append(fm)

        def _stop_sort_key(m: dict) -> int:
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

        task_folder = task_folder or project.get("task_folder")
        if not task_folder:
            raise ValueError("task_folder erforderlich – weder übergeben noch in Projekt gespeichert")

        plant_data = _load_plant_data(task_folder=task_folder)

        # ── MoC-Änderungen aus Anlagendaten extrahieren ──
        moc_changes = []
        for sys_item in plant_data.get("systems", []):
            for equip in sys_item.get("equipment", []):
                params = equip.get("parameters", {})
                if params.get("MoC_Datum"):
                    moc_changes.append({
                        "equipment": equip,
                        "system": sys_item,
                        "datum": params["MoC_Datum"],
                        "beschreibung": params.get("MoC_Beschreibung", ""),
                    })

        # FMs, die zu geänderten Equipment-Einträgen gehören (Keyword-Matching auf fehler_id)
        moc_keywords = set()
        for chg in moc_changes:
            for word in chg["equipment"]["name"].split():
                if len(word) >= 4:
                    moc_keywords.add(word[:6].upper())
        moc_keywords.add("FILTER")  # Fallback für bekanntes Namensmuster

        moc_fms = [
            fm for fm in fmea_data
            if any(kw in fm.get("fehler_id", "").upper() for kw in moc_keywords)
            or any(kw in fm.get("fehlermodus", "").upper() for kw in moc_keywords)
        ]

        # ── Konfidenz-Aggregation ──
        low_konfidenz_fms = [fm for fm in fmea_data if fm.get("agent_konfidenz") == "niedrig"]
        konfidenz_warning = len(low_konfidenz_fms) > 0

        # ── Pflicht-Maßnahmen (S≥9 oder RPZ≥300) ──
        pflicht_massnahmen_count = sum(
            1 for fm in fmea_data
            for m in fm.get("measures", [])
            if m.get("prioritaet") == "pflicht"
        )

        # ── Maßnahmen-Cockpit: sortiert nach RPZ-Delta (höchste Wirkung oben) ──
        cockpit_rows = []
        for fm in fmea_data:
            for m in fm.get("measures", []):
                rpz_vorher = fm.get("rpz", 0)
                rpz_nachher = m.get("rpz_neu") or rpz_vorher
                delta = rpz_vorher - rpz_nachher
                cockpit_rows.append({
                    "fehler_id": fm.get("fehler_id", ""),
                    "fehlermodus": fm.get("fehlermodus", ""),
                    "komponente": fm.get("komponente", ""),
                    "massnahme_name": m.get("name", ""),
                    "stop_kategorie": m.get("stop_kategorie", ""),
                    "abe_kategorie": m.get("abe_kategorie", ""),
                    "prioritaet": m.get("prioritaet", "empfohlen"),
                    "aufwand": m.get("aufwand", ""),
                    "kosten_klasse": m.get("kosten_klasse", ""),
                    "rpz_vorher": rpz_vorher,
                    "rpz_nachher": rpz_nachher,
                    "rpz_delta": delta,
                    "rpz_status_vorher": fm.get("rpz_status", ""),
                    "rpz_status_nachher": m.get("rpz_status_neu", ""),
                    "assigned_to": m.get("assigned_to", ""),
                    "target_date": m.get("target_date", ""),
                    "implementation_status": m.get("implementation_status", "geplant"),
                })
        cockpit_rows.sort(key=lambda x: x["rpz_delta"], reverse=True)

        # ── MoC-Delta (wenn parent_version vorhanden) ──
        moc_delta = None
        parent_version_id = project.get("parent_version_id")
        if parent_version_id:
            with FMEAStorage(db_path) as db2:
                parent_project = db2.get_project(parent_version_id)
                parent_fmea = db2.get_full_fmea_data(parent_version_id)
            parent_by_id = {fm["fehler_id"]: fm for fm in parent_fmea}
            current_by_id = {fm["fehler_id"]: fm for fm in fmea_data}
            changed = []
            added = []
            removed = []
            for fid, fm in current_by_id.items():
                if fid not in parent_by_id:
                    added.append(fm)
                elif (fm.get("S") != parent_by_id[fid].get("S") or
                      fm.get("O") != parent_by_id[fid].get("O") or
                      fm.get("D") != parent_by_id[fid].get("D")):
                    changed.append({"current": fm, "parent": parent_by_id[fid]})
            for fid, fm in parent_by_id.items():
                if fid not in current_by_id:
                    removed.append(fm)
            moc_delta = {
                "parent_project": parent_project,
                "changed": changed,
                "added": added,
                "removed": removed,
                "change_description": project.get("version_beschreibung", ""),
            }

        # Jinja2 rendering
        env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
        env.filters['strip_sod_prefix'] = _strip_sod_prefix
        template = env.get_template("fmea_report.html")

        css_file = template_dir / css_name

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
            matrix_data=matrix_data,
            treemap_before=treemap_before,
            treemap_after=treemap_after,
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
            cockpit_rows=cockpit_rows,
            moc_delta=moc_delta,
            moc_changes=moc_changes,
            moc_fms=moc_fms,
            report_context={
                "special_rule_count": special_rule_count,
                "stop_coverage": stop_coverage,
                "max_rpz": max_rpz,
                "avg_rpz": avg_rpz,
                "best_reduction": best_reduction,
                "avg_reduction": avg_reduction if best_reduction else 0,
                "fms_with_measures_count": len(fms_with_measures),
                "low_konfidenz_count": len(low_konfidenz_fms),
                "konfidenz_warning": konfidenz_warning,
                "pflicht_massnahmen_count": pflicht_massnahmen_count,
                "has_moc": moc_delta is not None,
                "version": project.get("version", "1.0"),
                "erstellt_von": project.get("erstellt_von", ""),
                "geprueft_von": project.get("geprueft_von", ""),
            },
        )

        # Write temporary HTML to feed Playwright (it needs a file: URL for CSS)
        tmp_html = Path(tmp_dir) / "report.html"
        tmp_html.write_text(html_content, encoding="utf-8")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        project_name = project.get("name") or ""
        anlage_name = project.get("anlage_name") or ""
        # Format: "Anlagenname (Teilanlage) – Risikoanalyse"
        # e.g. "Ethylacetat-Anlage (20TA42) – Risikoanalyse"
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

        # Save rendered HTML alongside the PDF (with embedded base64 images for offline viewing)
        html_output = Path(output_path).with_suffix('.html')
        html_output.write_text(_embed_images_base64(html_content), encoding='utf-8')
        print(f"HTML-Vorschau gespeichert: {html_output}")

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
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/report_generator.py <project_id> [output_path] [task_folder]")
        sys.exit(1)
    generate_report(
        int(sys.argv[1]),
        sys.argv[2] if len(sys.argv) > 2 else None,
        task_folder=sys.argv[3] if len(sys.argv) > 3 else None,
    )
