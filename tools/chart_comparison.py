"""
Chart Comparison Tool -- Generates a single image comparing 6 chart types
for RPZ distribution visualization, using echte Analysedaten.

Usage:
    from tools.chart_comparison import generate_comparison
    generate_comparison(rpz_distribution={"kritisch": 3, "hoch": 4, ...})
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
from config.fmea_standards import RPZ_COLORS

ORDER = ["kritisch", "hoch", "mittel", "niedrig"]
COLORS = [RPZ_COLORS[k] for k in ORDER]
LABELS = [k.capitalize() for k in ORDER]


def _chart_a_donut(ax, values, total):
    """A: Donut"""
    wedges, texts, autotexts = ax.pie(
        values, colors=COLORS, autopct="%1.0f%%", startangle=90,
        pctdistance=0.78, textprops={"fontsize": 8, "color": "white", "fontweight": "bold"},
    )
    ax.add_patch(plt.Circle((0, 0), 0.55, fc="white"))
    ax.text(0, 0.08, str(total), ha="center", va="center",
            fontsize=18, fontweight="bold", color="#1F2937")
    ax.text(0, -0.15, "Risiken", ha="center", va="center",
            fontsize=8, color="#6B7280")
    ax.set_title("A: Donut", fontsize=10, fontweight="bold", pad=10, color="#1F2937")


def _chart_b_stacked_bar(ax, values, total):
    """B: Gestapelter Horizontalbalken"""
    left = 0
    bar_height = 0.6
    for val, col, lbl in zip(values, COLORS, LABELS):
        pct = val / total * 100 if total else 0
        ax.barh(0, pct, height=bar_height, left=left, color=col, edgecolor="white", linewidth=1.5)
        if pct > 6:
            ax.text(left + pct / 2, 0, f"{val}\n({pct:.0f}%)",
                    ha="center", va="center", fontsize=7.5, fontweight="bold", color="white")
        left += pct

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([])
    ax.set_xlabel("Anteil (%)", fontsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("B: Gestapelter Balken", fontsize=10, fontweight="bold", pad=10, color="#1F2937")

    handles = [mpatches.Patch(color=c, label=f"{l}: {v}") for c, l, v in zip(COLORS, LABELS, values)]
    ax.legend(handles=handles, loc="upper center", fontsize=6.5, ncol=4, frameon=False,
              bbox_to_anchor=(0.5, -0.15))


def _chart_c_waffle(ax, values, total):
    """C: Waffle-Chart (10x10 Raster)"""
    total_cells = 100
    cell_counts = [round(v / total * total_cells) if total else 0 for v in values]
    diff = total_cells - sum(cell_counts)
    cell_counts[0] += diff

    grid = []
    for count, color in zip(cell_counts, COLORS):
        grid.extend([color] * count)

    for i in range(10):
        for j in range(10):
            idx = i * 10 + j
            color = grid[idx] if idx < len(grid) else "#EEE"
            ax.add_patch(plt.Rectangle((j, 9 - i), 0.9, 0.9, facecolor=color,
                                        edgecolor="white", linewidth=1.2, joinstyle="round"))

    ax.set_xlim(-0.1, 10.1)
    ax.set_ylim(-0.1, 10.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("C: Waffle-Chart", fontsize=10, fontweight="bold", pad=10, color="#1F2937")

    handles = [mpatches.Patch(color=c, label=f"{l}: {v}") for c, l, v in zip(COLORS, LABELS, values)]
    ax.legend(handles=handles, loc="upper center", fontsize=6.5, ncol=4, frameon=False,
              bbox_to_anchor=(0.5, -0.02))


def _chart_d_gauge(ax, values, total):
    """D: Gauge/Tachometer"""
    zone_ranges = [(0, 25, COLORS[3]), (25, 50, COLORS[2]), (50, 75, COLORS[1]), (75, 100, COLORS[0])]
    for start, end, color in zone_ranges:
        theta_start = np.radians(180 - end * 1.8)
        theta_end = np.radians(180 - start * 1.8)
        angles = np.linspace(theta_start, theta_end, 50)
        xs_outer = 1.0 * np.cos(angles)
        ys_outer = 1.0 * np.sin(angles)
        xs_inner = 0.6 * np.cos(angles)
        ys_inner = 0.6 * np.sin(angles)
        xs = np.concatenate([xs_outer, xs_inner[::-1]])
        ys = np.concatenate([ys_outer, ys_inner[::-1]])
        ax.fill(xs, ys, color=color, alpha=0.85)

    risk_score = (values[0] * 4 + values[1] * 3 + values[2] * 2 + values[3] * 1) / max(total, 1)
    needle_pct = (risk_score - 1) / 3 * 100
    needle_angle = np.radians(180 - needle_pct * 1.8)
    ax.plot([0, 0.85 * np.cos(needle_angle)], [0, 0.85 * np.sin(needle_angle)],
            color="#1F2937", linewidth=2.5, solid_capstyle="round")
    ax.add_patch(plt.Circle((0, 0), 0.08, fc="#1F2937", zorder=5))

    for pct, lbl in [(12.5, "Niedrig"), (37.5, "Mittel"), (62.5, "Hoch"), (87.5, "Kritisch")]:
        a = np.radians(180 - pct * 1.8)
        ax.text(0.8 * np.cos(a), 0.8 * np.sin(a) + 0.02, lbl,
                ha="center", va="center", fontsize=5.5, fontweight="bold", color="#1F2937")

    ax.text(0, -0.2, f"Score: {risk_score:.1f}/4", ha="center", va="center",
            fontsize=9, fontweight="bold", color="#1F2937")

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.35, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("D: Gauge/Tachometer", fontsize=10, fontweight="bold", pad=10, color="#1F2937")


def _chart_e_bullet(ax, values, total):
    """E: Bullet-Chart"""
    bar_height = 0.4
    bg_ranges = [(0, total, "#F3F4F6"), (0, total * 0.75, "#E5E7EB"), (0, total * 0.5, "#D1D5DB")]
    for start, end, color in bg_ranges:
        ax.barh(0, end - start, left=start, height=0.8, color=color, edgecolor="none")

    cumulative = 0
    for val, col, lbl in zip(values, COLORS, LABELS):
        ax.barh(0, val, left=cumulative, height=bar_height, color=col, edgecolor="white", linewidth=0.5)
        if val > 1:
            ax.text(cumulative + val / 2, 0, str(val),
                    ha="center", va="center", fontsize=7.5, fontweight="bold", color="white")
        cumulative += val

    target = total * 0.35
    ax.plot([target, target], [-0.45, 0.45], color="#1F2937", linewidth=2.5)
    ax.text(target, 0.55, f"Ziel: {target:.0f}", ha="center", fontsize=6.5,
            fontweight="bold", color="#1F2937")

    ax.set_xlim(0, total + 1)
    ax.set_ylim(-0.8, 0.9)
    ax.set_yticks([])
    ax.set_xlabel("Anzahl Fehlermodi", fontsize=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title("E: Bullet-Chart", fontsize=10, fontweight="bold", pad=10, color="#1F2937")

    handles = [mpatches.Patch(color=c, label=f"{l}: {v}") for c, l, v in zip(COLORS, LABELS, values)]
    handles.append(plt.Line2D([0], [0], color="#1F2937", linewidth=2.5, label="Zielwert"))
    ax.legend(handles=handles, loc="upper center", fontsize=6.5, ncol=5, frameon=False,
              bbox_to_anchor=(0.5, -0.15))


def _chart_f_lollipop(ax, values, total):
    """F: Lollipop-Chart"""
    x = np.arange(len(LABELS))
    for i, (val, col, lbl) in enumerate(zip(values, COLORS, LABELS)):
        ax.plot([i, i], [0, val], color=col, linewidth=2.5, solid_capstyle="round")
        ax.scatter(i, val, s=val * 25 + 60, color=col, edgecolors="white",
                   linewidths=2, zorder=5)
        ax.text(i, val + 0.8, str(val), ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=col)

    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, fontsize=8, fontweight="600")
    ax.set_ylabel("Anzahl", fontsize=8)
    ax.set_ylim(0, max(values) + 3 if any(values) else 5)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_title("F: Lollipop-Chart", fontsize=10, fontweight="bold", pad=10, color="#1F2937")


def generate_comparison(rpz_distribution: dict = None, output_path: str = None) -> str:
    """Generate a 2x3 grid comparing 6 chart types for RPZ distribution.

    Args:
        rpz_distribution: dict with keys "kritisch", "hoch", "mittel", "niedrig"
                          and integer counts as values. Uses fallback data if None.
        output_path: where to save the PNG. Defaults to .tmp/chart_vergleich.png
    """
    fallback = {"kritisch": 3, "hoch": 5, "mittel": 8, "niedrig": 12}
    data = rpz_distribution or fallback
    values = [data.get(k, 0) for k in ORDER]
    total = sum(values)

    if output_path is None:
        out_dir = Path(__file__).parent.parent / ".tmp"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / "chart_vergleich.png")

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle(
        "RPZ-Verteilung – 6 Visualisierungen im Vergleich",
        fontsize=16, fontweight="bold", color="#1F2937", y=0.97,
    )
    fig.text(0.5, 0.935,
             f"Analysedaten: Kritisch={data.get('kritisch', 0)}, "
             f"Hoch={data.get('hoch', 0)}, Mittel={data.get('mittel', 0)}, "
             f"Niedrig={data.get('niedrig', 0)} (Gesamt: {total})",
             ha="center", fontsize=10, color="#6B7280")

    chart_funcs = [_chart_a_donut, _chart_b_stacked_bar, _chart_c_waffle,
                   _chart_d_gauge, _chart_e_bullet, _chart_f_lollipop]
    for ax, func in zip(axes.flat, chart_funcs):
        func(ax, values, total)

    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    result = generate_comparison(output_path=path)
    print(f"Chart-Vergleich generiert: {result}")
