"""
FMEA Report Generator (HTML/CSS → PDF via WeasyPrint)

Generates a professional FMEA report that visually matches the Risk AI Web-App.
The report is first rendered as HTML (Jinja2 + CSS) then converted to PDF.

Usage:
    from tools.report_generator import generate_report
    pdf_path = generate_report(project_id)
"""

import json
import sys
import tempfile
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
from config.fmea_standards import (
    S_SCALE as S_INFO,
    O_SCALE as O_INFO,
    D_SCALE as D_INFO,
    RPZ_COLORS as RPZ_HEX,
    RPZ_THRESHOLDS,
    RPZ_LABELS,
)


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
        "kritisch": "#dc354520",
        "hoch":     "#ff980020",
        "mittel":   "#ffc10718",
        "niedrig":  "#28a74512",
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
    rpz_cmap = matplotlib.colormaps["RdYlGn_r"].resampled(256)

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


def _render_treemap_pair(fmea_data: list, tmp_dir: str) -> str:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    for ax, with_m, title in [(ax1, False, "Initial-Risiko (Vor Maßnahmen)"),
                               (ax2, True,  "Aktuelles Risiko (Mit Maßnahmen)")]:
        items = []
        for fm in fmea_data:
            fid = fm.get("fehler_id", "?")
            short = "-".join(fid.split("-")[-2:])
            if with_m and fm.get("measures"):
                best = min(fm["measures"], key=lambda m: (m.get("rpz_neu") or 9999))
                rpz = best.get("rpz_neu") or fm.get("rpz", 1)
                st = best.get("rpz_status_neu") or fm.get("rpz_status", "niedrig")
            else:
                rpz, st = fm.get("rpz", 1), fm.get("rpz_status", "niedrig")
            items.append({"label": f"{short}\n{max(rpz, 5)}", "rpz": max(rpz, 5),
                          "color": RPZ_HEX.get(st, "#AAA")})
        items.sort(key=lambda x: -x["rpz"])
        if not items:
            items = [{"label": "---", "rpz": 1, "color": "#CCC"}]

        squarify.plot(sizes=[i["rpz"] for i in items], label=[i["label"] for i in items],
                      color=[i["color"] for i in items], alpha=0.88,
                      text_kwargs={"fontsize": 7.5, "fontweight": "bold", "color": "white"}, ax=ax, pad=2)
        ax.axis("off")
        ax.set_title(title, fontsize=11, fontweight="bold", color="#1F2937", pad=10)

    handles = [mpatches.Patch(color=RPZ_HEX[s], label=s.capitalize()) for s in RPZ_HEX]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, -0.02))

    p = _chart_path(tmp_dir, "treemap_pair")
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
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
    ax.barh(y + h / 2, before, h, label="Vorher", color="#dc3545", alpha=0.85)
    ax.barh(y - h / 2, after, h, label="Nachher", color="#28a745", alpha=0.85)
    ax.axvline(x=100, color="#ff9800", linestyle="--", linewidth=1.2, alpha=0.7, label="Grenzwert 100")
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

def _load_plant_data(rtf_path: str = None) -> dict:
    """Extract the JSON payload from the Anlagendaten.rtf file."""
    if rtf_path is None:
        rtf_path = str(Path(__file__).parent.parent / "tasks" / "risikoanalyse" / "Anlagendaten.rtf")
    p = Path(rtf_path)
    if not p.exists():
        return {}
    raw = p.read_text(encoding="utf-8", errors="replace")

    try:
        from striprtf.striprtf import rtf_to_text
        text = rtf_to_text(raw)
    except ImportError:
        text = raw

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return {}

    try:
        data = json.loads(text[start : end + 1])
        return data[0] if isinstance(data, list) and len(data) > 0 else {}
    except json.JSONDecodeError:
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

        # Group failure modes by function
        func_groups = OrderedDict()
        for fm in fmea_data:
            fid = fm.get("funktion_id", "?")
            if fid not in func_groups:
                func_groups[fid] = {"beschreibung": fm.get("funktion_beschreibung", ""), "fms": []}
            func_groups[fid]["fms"].append(fm)

        top5 = sorted(fmea_data, key=lambda x: x.get("rpz", 0), reverse=True)[:5]
        fmea_sorted = sorted(fmea_data, key=lambda x: x.get("rpz", 0), reverse=True)
        dist = stats.get("rpz_distribution", {})
        high_risk_count = dist.get("kritisch", 0) + dist.get("hoch", 0)
        total_measures = sum(len(fm.get("measures", [])) for fm in fmea_data)

        # Load plant data from RTF
        plant_data = _load_plant_data()

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
            scales=[
                ("S", "Bedeutung (S)", S_INFO),
                ("O", "Auftreten (O)", O_INFO),
                ("D", "Entdeckung (D)", D_INFO),
            ],
            sod_data=_sod_data,
            rpz_color=_rpz_color,
            plant=plant_data,
        )

        # Write temporary HTML to feed Playwright (it needs a file: URL for CSS)
        tmp_html = Path(tmp_dir) / "report.html"
        tmp_html.write_text(html_content, encoding="utf-8")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        header_html = (
            '<div style="width:100%;font-size:7pt;font-family:Inter,Segoe UI,sans-serif;'
            'padding:6mm 18mm 0 18mm;display:flex;justify-content:space-between;color:#9CA3AF;'
            'border-bottom:0.5px solid #E5E7EB;">'
            '<span>FMEA-Bericht – ' + (project.get("anlage_name") or "") + '</span>'
            '<span>AIAG-VDA FMEA</span>'
            '</div>'
        )
        footer_html = (
            '<div style="width:100%;font-size:7pt;font-family:Inter,Segoe UI,sans-serif;'
            'padding:0 18mm 6mm 18mm;display:flex;justify-content:space-between;color:#9CA3AF;'
            'border-top:0.5px solid #E5E7EB;">'
            '<span style="font-style:italic;">Vertraulich – nur für internen Gebrauch</span>'
            '<span>Seite <span class="pageNumber"></span> / <span class="totalPages"></span></span>'
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
