#!/usr/bin/env python3
"""
Generate 9 FMEA report design concept previews (Runde 6).
Structure: grouped by Fehlerart (Thermisch / Mechanisch / MSR)
Data: project_id=1 (Ethylacetatproduktion 20TA42) from data/fmea.db
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "fmea.db")
OUT_DIR = os.path.join(BASE_DIR, ".tmp", "report_previews")


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────

def load_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    categories = []
    selected = {
        "Thermisch":   {"full": 1, "compact": 2},
        "Mechanisch":  {"full": 2, "compact": 2},
        "MSR":         {"full": 2, "compact": 2},
    }

    for fehlerart, counts in selected.items():
        # Full cards: hoch or mittel, highest RPZ first
        cur.execute("""
            SELECT fm.id, fm.fehler_id, fm.fehlermodus, fm.fehlerart, fm.kontext_beschreibung,
                   c.name as komp_name, f.beschreibung as funktion,
                   ra.S, ra.O, ra.D, ra.rpz, ra.rpz_status,
                   ra.begruendung_S, ra.begruendung_O, ra.begruendung_D, ra.override_applied
            FROM failure_modes fm
            JOIN functions f ON fm.function_id=f.id
            JOIN components c ON f.component_id=c.id
            JOIN risk_assessments ra ON ra.failure_mode_id=fm.id
            WHERE c.project_id=1 AND fm.fehlerart=? AND ra.rpz_status IN ('hoch','mittel','kritisch')
            ORDER BY ra.rpz DESC
            LIMIT ?
        """, (fehlerart, counts["full"]))
        full_rows = [dict(r) for r in cur.fetchall()]

        # Compact cards: niedrig, varied RPZ
        cur.execute("""
            SELECT fm.id, fm.fehler_id, fm.fehlermodus, fm.fehlerart, fm.kontext_beschreibung,
                   c.name as komp_name, f.beschreibung as funktion,
                   ra.S, ra.O, ra.D, ra.rpz, ra.rpz_status,
                   ra.begruendung_S, ra.begruendung_O, ra.begruendung_D, ra.override_applied
            FROM failure_modes fm
            JOIN functions f ON fm.function_id=f.id
            JOIN components c ON f.component_id=c.id
            JOIN risk_assessments ra ON ra.failure_mode_id=fm.id
            WHERE c.project_id=1 AND fm.fehlerart=? AND ra.rpz_status='niedrig'
            ORDER BY ra.rpz DESC
            LIMIT ?
        """, (fehlerart, counts["compact"]))
        compact_rows = [dict(r) for r in cur.fetchall()]

        # Enrich each FM
        all_fms = []
        for fm in full_rows + compact_rows:
            fm["is_full"] = fm in full_rows
            fm_id = fm["id"]
            cur.execute("SELECT * FROM failure_causes WHERE failure_mode_id=? LIMIT 3", (fm_id,))
            fm["causes"] = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT * FROM failure_effects WHERE failure_mode_id=?", (fm_id,))
            row = cur.fetchone()
            fm["effects"] = dict(row) if row else {}
            cur.execute("SELECT name, typ, wirkung, sil_level FROM current_controls WHERE failure_mode_id=? LIMIT 2", (fm_id,))
            fm["controls"] = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT name, S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu, begruendung FROM measures WHERE failure_mode_id=? LIMIT 2", (fm_id,))
            fm["measures"] = [dict(r) for r in cur.fetchall()]
            all_fms.append(fm)

        # Stats
        all_statuses = [fm["rpz_status"] for fm in all_fms]
        hoch_cnt = sum(1 for s in all_statuses if s in ("hoch","kritisch"))
        mittel_cnt = sum(1 for s in all_statuses if s == "mittel")
        niedrig_cnt = sum(1 for s in all_statuses if s == "niedrig")
        max_rpz = max(fm["rpz"] for fm in all_fms) if all_fms else 0

        categories.append({
            "name": fehlerart,
            "fms": all_fms,
            "hoch_cnt": hoch_cnt,
            "mittel_cnt": mittel_cnt,
            "niedrig_cnt": niedrig_cnt,
            "max_rpz": max_rpz,
        })

    conn.close()
    return categories


# ─────────────────────────────────────────────
# STATUS HELPERS (shared across all designs)
# ─────────────────────────────────────────────

STATUS_COLORS = {
    "kritisch": {"text": "#7F1D1D", "bg": "#FFF5F5", "border": "#DC2626", "border_w": "4px"},
    "hoch":     {"text": "#7C2D12", "bg": "#FFF7ED", "border": "#C2410C", "border_w": "4px"},
    "mittel":   {"text": "#713F12", "bg": "#FEFCE8", "border": "#B45309", "border_w": "3px"},
    "niedrig":  {"text": "#14532D", "bg": "#F0FDF4", "border": "#16A34A", "border_w": "2px"},
}

STATUS_DARK = {
    "kritisch": {"text": "#FCA5A5", "bg": "rgba(220,38,38,0.12)", "border": "#DC2626", "border_w": "4px"},
    "hoch":     {"text": "#FDBA74", "bg": "rgba(194,65,12,0.12)", "border": "#C2410C", "border_w": "4px"},
    "mittel":   {"text": "#FDE68A", "bg": "rgba(180,83,9,0.12)",  "border": "#B45309", "border_w": "3px"},
    "niedrig":  {"text": "#6EE7B7", "bg": "rgba(22,163,74,0.10)", "border": "#16A34A", "border_w": "2px"},
}

STATUS_LABEL = {
    "kritisch": "KRITISCH", "hoch": "HOCH", "mittel": "MITTEL", "niedrig": "NIEDRIG"
}

def sc(status, key, dark=False):
    palette = STATUS_DARK if dark else STATUS_COLORS
    return palette.get(status, STATUS_COLORS["niedrig"])[key]


# ─────────────────────────────────────────────
# CATEGORY SECTION ICONS (SVG inline, Phosphor-style)
# ─────────────────────────────────────────────

CATEGORY_ICONS = {
    "Thermisch": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>
    </svg>""",
    "Mechanisch": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2"/>
    </svg>""",
    "MSR": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>""",
}

CATEGORY_LABELS = {
    "Thermisch": "Thermisch",
    "Mechanisch": "Mechanisch",
    "MSR": "Mess-, Steuer- & Regeltechnik",
}


# ─────────────────────────────────────────────
# SOD RENDERERS
# ─────────────────────────────────────────────

def sod_thin_arc(val, label, desc, begruendung, accent, dark=False):
    """Thin SVG arc gauge (Obsidian style)."""
    pct = (val - 1) / 9
    r = 22; cx = 28; cy = 28
    import math
    start_x = cx + r * math.cos(math.pi)
    start_y = cy + r * math.sin(math.pi)
    end_x = cx + r * math.cos(math.pi + pct * math.pi)
    end_y = cy + r * math.sin(math.pi + pct * math.pi)
    large = 1 if pct > 0.5 else 0
    text_col = "#9090A8" if dark else "#888"
    val_col = "#E8E8F0" if dark else "#1A1A1A"
    arc_col = accent
    track_col = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.08)"
    return f"""<div class="sod-item">
      <svg width="56" height="34" viewBox="0 0 56 34">
        <path d="M {cx-r},{cy} A {r},{r} 0 0,1 {cx+r},{cy}" fill="none" stroke="{track_col}" stroke-width="2.5"/>
        <path d="M {cx-r},{cy} A {r},{r} 0 0,1 {end_x:.2f},{end_y:.2f}" fill="none" stroke="{arc_col}" stroke-width="2.5" stroke-linecap="round"/>
        <text x="{cx}" y="{cy-4}" text-anchor="middle" font-size="13" font-weight="700" fill="{val_col}">{val}</text>
        <text x="{cx}" y="{cy+8}" text-anchor="middle" font-size="7" fill="{text_col}" letter-spacing="1">{label}</text>
      </svg>
      <div class="sod-meta">
        <div class="sod-desc">{desc[:60] if desc else ''}</div>
        {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
      </div>
    </div>"""


def sod_dot_grid(val, label, desc, begruendung, accent, dark=False):
    """2×5 dot grid (Chalk / Polar style)."""
    dots = ""
    for i in range(10):
        row, col = divmod(i, 5)
        x = col * 11 + 2
        y = row * 11 + 2
        filled = i < val
        fill = accent if filled else ("rgba(255,255,255,0.1)" if dark else "rgba(0,0,0,0.08)")
        dots += f'<rect x="{x}" y="{y}" width="7" height="7" rx="1.5" fill="{fill}"/>'
    text_col = "#9090A8" if dark else "#888"
    val_col = "#E8E8F0" if dark else "#1A1A1A"
    return f"""<div class="sod-item">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <svg width="57" height="24" viewBox="0 0 57 24">{dots}</svg>
        <span style="font-size:20px;font-weight:700;color:{val_col}">{val}</span>
        <span style="font-size:9px;color:{text_col};letter-spacing:1px">{label}</span>
      </div>
      <div class="sod-desc">{desc[:60] if desc else ''}</div>
      {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
    </div>"""


def sod_segmented_bar(val, label, desc, begruendung, accent, dark=False):
    """Segmented battery-style bar (Dusk style)."""
    segs = ""
    for i in range(10):
        active = i < val
        col = accent if active else ("rgba(255,255,255,0.07)" if dark else "#E8E4DD")
        segs += f'<div style="flex:1;height:12px;background:{col};border-radius:1px"></div>'
    text_col = "#9090A8" if dark else "#7A7260"
    val_col = "#E8E8F0" if dark else "#1A1A1A"
    return f"""<div class="sod-item">
      <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:5px">
        <span style="font-size:22px;font-weight:700;color:{val_col}">{val}</span>
        <span style="font-size:9px;letter-spacing:1.5px;color:{text_col}">{label}</span>
      </div>
      <div style="display:flex;gap:2px;margin-bottom:5px">{segs}</div>
      <div class="sod-desc">{desc[:60] if desc else ''}</div>
      {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
    </div>"""


def sod_text_only(val, label, desc, begruendung, accent, dark=False):
    """Large number + horizontal rule (Muji style)."""
    text_col = "#8A8680" if not dark else "#9090A8"
    val_col = "#1A1714" if not dark else "#E8E8F0"
    return f"""<div class="sod-item">
      <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:6px">
        <span style="font-size:32px;font-weight:400;color:{val_col};letter-spacing:-1px">{val}</span>
        <span style="font-size:8px;letter-spacing:2px;color:{text_col}">{label}</span>
      </div>
      <div style="width:100%;height:1px;background:{accent};opacity:0.3;margin-bottom:6px"></div>
      <div class="sod-desc">{desc[:60] if desc else ''}</div>
      {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
    </div>"""


def sod_filled_dot(val, label, desc, begruendung, accent, dark=False):
    """Filled circle with scale label (Emerald style)."""
    import math
    r = 18; cx = 20; cy = 20
    pct = val / 10
    end_x = cx + r * math.cos(-math.pi/2 + pct * 2 * math.pi)
    end_y = cy + r * math.sin(-math.pi/2 + pct * 2 * math.pi)
    large = 1 if pct > 0.5 else 0
    track_col = "rgba(0,0,0,0.07)" if not dark else "rgba(255,255,255,0.07)"
    val_col = "#1A2520" if not dark else "#E8E8F0"
    text_col = "#888" if not dark else "#9090A8"
    return f"""<div class="sod-item">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <svg width="40" height="40" viewBox="0 0 40 40">
          <circle cx="20" cy="20" r="18" fill="none" stroke="{track_col}" stroke-width="3"/>
          <path d="M 20,2 A 18,18 0 {large},1 {end_x:.2f},{end_y:.2f}" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
          <text x="20" y="25" text-anchor="middle" font-size="13" font-weight="700" fill="{val_col}">{val}</text>
        </svg>
        <div>
          <div style="font-size:9px;letter-spacing:1.5px;color:{text_col}">{label}</div>
          <div class="sod-desc" style="margin-top:2px">{desc[:50] if desc else ''}</div>
        </div>
      </div>
      {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
    </div>"""


def sod_numerical(val, label, desc, begruendung, accent, dark=False):
    """Numbers only, no visualization (Mercury style)."""
    val_col = "#E8E8F0" if dark else "#1A1A2E"
    label_col = accent
    desc_col = "#9090A8" if dark else "#6B7280"
    return f"""<div class="sod-item">
      <div style="display:flex;align-items:baseline;gap:6px;border-left:3px solid {accent};padding-left:10px;margin-bottom:4px">
        <span style="font-size:28px;font-weight:300;color:{val_col};letter-spacing:-1px">{val}</span>
        <span style="font-size:9px;letter-spacing:2px;color:{label_col};font-weight:600">{label}</span>
      </div>
      <div class="sod-desc" style="padding-left:13px">{desc[:60] if desc else ''}</div>
      {'<div class="sod-grund" style="padding-left:13px">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
    </div>"""


def sod_half_ring(val, label, desc, begruendung, accent, dark=False):
    """SVG half-ring gauge (Chamois style)."""
    import math
    pct = (val - 1) / 9
    r = 24; cx = 30; cy = 30
    end_x = cx + r * math.cos(math.pi * (1 + pct))
    end_y = cy + r * math.sin(math.pi * (1 + pct))
    large = 1 if pct > 0.5 else 0
    track_col = "rgba(0,0,0,0.06)" if not dark else "rgba(255,255,255,0.06)"
    val_col = "#2A2018" if not dark else "#E8E8F0"
    text_col = "#9A8870" if not dark else "#9090A8"
    return f"""<div class="sod-item">
      <svg width="60" height="36" viewBox="0 0 60 36">
        <path d="M {cx-r},{cy} A {r},{r} 0 0,1 {cx+r},{cy}" fill="none" stroke="{track_col}" stroke-width="4"/>
        <path d="M {cx-r},{cy} A {r},{r} 0 0,1 {end_x:.2f},{end_y:.2f}" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>
        <text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="14" font-weight="600" fill="{val_col}">{val}</text>
        <text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="7" fill="{text_col}" letter-spacing="1">{label}</text>
      </svg>
      <div class="sod-meta">
        <div class="sod-desc">{desc[:60] if desc else ''}</div>
        {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
      </div>
    </div>"""


def sod_square_dot(val, label, desc, begruendung, accent, dark=False):
    """Square dots in ice-blue palette (Polar style)."""
    dots = ""
    for i in range(10):
        x = i * 12 + 2
        filled = i < val
        fill = accent if filled else "rgba(219,234,254,0.2)" if not dark else "rgba(255,255,255,0.06)"
        dots += f'<rect x="{x}" y="2" width="8" height="8" rx="2" fill="{fill}"/>'
    text_col = "#94A3B8" if not dark else "#9090A8"
    val_col = "#1E293B" if not dark else "#E8E8F0"
    return f"""<div class="sod-item">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <svg width="122" height="12" viewBox="0 0 122 12">{dots}</svg>
        <span style="font-size:18px;font-weight:600;color:{val_col}">{val}</span>
        <span style="font-size:9px;color:{text_col};letter-spacing:1px">{label}</span>
      </div>
      <div class="sod-desc">{desc[:60] if desc else ''}</div>
      {'<div class="sod-grund">' + (begruendung[:80] if begruendung else '') + '</div>' if begruendung else ''}
    </div>"""


SOD_RENDERERS = {
    "thin_arc":     sod_thin_arc,
    "dot_grid":     sod_dot_grid,
    "segmented_bar": sod_segmented_bar,
    "text_only":    sod_text_only,
    "filled_dot":   sod_filled_dot,
    "numerical":    sod_numerical,
    "half_ring":    sod_half_ring,
    "square_dot":   sod_square_dot,
}

SOD_DESCRIPTIONS = {
    "S": "Bedeutung",
    "O": "Auftreten",
    "D": "Entdeckung",
}


# ─────────────────────────────────────────────
# CARD RENDERERS
# ─────────────────────────────────────────────

def render_full_card(fm, design):
    status = fm["rpz_status"]
    dark = design.get("is_dark", False)
    pal = STATUS_DARK if dark else STATUS_COLORS
    s_pal = pal[status]
    sod_fn = SOD_RENDERERS[design["sod_style"]]
    acc = design["accent"]

    sod_s = sod_fn(fm["S"], "S", "Bedeutung – Schweregrad", fm.get("begruendung_S"), acc, dark)
    sod_o = sod_fn(fm["O"], "O", "Auftreten – Wahrscheinlichkeit", fm.get("begruendung_O"), acc, dark)
    sod_d = sod_fn(fm["D"], "D", "Entdeckung – Detektierbarkeit", fm.get("begruendung_D"), acc, dark)

    causes_html = ""
    for c in fm.get("causes", []):
        causes_html += f"""<div class="cause-row">
          <span class="cause-id">{c.get('ursache_id','')}</span>
          <span class="cause-desc">{c.get('beschreibung','')}</span>
          <span class="cause-phase">{c.get('praeventionsphase','')}</span>
        </div>"""

    effects = fm.get("effects", {})
    eff_html = ""
    for key, label in [("mensch_stufe","Mensch"), ("umwelt_stufe","Umwelt"), ("anlage_stufe","Anlage"), ("kosten_stufe","Kosten")]:
        val = effects.get(key, "—")
        eff_html += f'<div class="eff-row"><span class="eff-label">{label}</span><span class="eff-val">{val}</span></div>'

    controls_html = ""
    for ctrl in fm.get("controls", []):
        controls_html += f"""<div class="ctrl-row">
          <span class="ctrl-name">{ctrl['name']}</span>
          <span class="ctrl-type">{ctrl['typ']}</span>
          <span class="ctrl-wirkung">{ctrl.get('wirkung','')[:60]}</span>
        </div>"""

    measures_html = ""
    for m in fm.get("measures", []):
        new_status = m.get("rpz_status_neu", "niedrig")
        ms_pal = pal[new_status]
        measures_html += f"""<div class="measure-row">
          <div class="measure-name">{m['name']}</div>
          <div class="measure-delta">RPZ {fm['rpz']} → <strong>{m['rpz_neu']}</strong>
            <span class="badge-mini" style="color:{ms_pal['text']};background:{ms_pal['bg']};border-color:{ms_pal['border']}">{new_status.upper()}</span>
          </div>
          {'<div class="measure-begr">' + (m.get("begruendung","")[:80] if m.get("begruendung") else "") + '</div>' if m.get("begruendung") else ""}
        </div>"""

    card_border_style = design.get("card_style", "border_left")
    border_css = ""
    if card_border_style == "border_left":
        border_css = f"border-left:{s_pal['border_w']} solid {s_pal['border']};"
    elif card_border_style == "hairline":
        border_css = f"border:0.5px solid {s_pal['border']};border-top:2px solid {s_pal['border']};"
    else:
        border_css = f"border:1px solid {s_pal['border']};"

    override_note = ""
    if fm.get("override_applied"):
        override_note = f'<div class="override-note">⚠ AIAG-VDA Sonderregel: {fm["override_applied"]}</div>'

    context = fm.get("kontext_beschreibung", "")
    context_html = f'<div class="fm-context">{context}</div>' if context else ""

    bg_card = design.get("bg_card", "#FFFFFF")

    return f"""
<div class="fm-card fm-full" style="background:{bg_card};{border_css}">
  <div class="card-header">
    <div class="card-header-left">
      <div class="fm-id">{fm['fehler_id']}</div>
      <div class="fm-title">{fm['fehlermodus']}</div>
      <div class="fm-komp">{fm['komp_name']} · {fm['funktion']}</div>
    </div>
    <div class="card-header-right">
      <div class="rpz-box" style="color:{s_pal['text']};background:{s_pal['bg']};border-color:{s_pal['border']}">
        <div class="rpz-value">{fm['rpz']}</div>
        <div class="rpz-label">RPZ</div>
        <div class="rpz-formula">{fm['S']} × {fm['O']} × {fm['D']}</div>
      </div>
      <div class="status-badge" style="color:{s_pal['text']};background:{s_pal['bg']};border-color:{s_pal['border']}">{STATUS_LABEL[status]}</div>
    </div>
  </div>
  {context_html}
  <div class="sod-row">
    {sod_s}
    <div class="sod-mult">×</div>
    {sod_o}
    <div class="sod-mult">×</div>
    {sod_d}
  </div>
  {override_note}
  <div class="details-grid">
    <div class="details-col">
      <div class="section-label">Fehlerursachen</div>
      <div class="causes-list">{causes_html}</div>
    </div>
    <div class="details-col">
      <div class="section-label">Fehlerfolgen</div>
      <div class="effects-list">{eff_html}</div>
    </div>
  </div>
  {'<div class="controls-section"><div class="section-label">Bestehende Maßnahmen</div>' + controls_html + '</div>' if controls_html else ''}
  {'<div class="measures-section"><div class="section-label">Empfohlene Maßnahmen</div>' + measures_html + '</div>' if measures_html else ''}
</div>"""


def render_compact_card(fm, design):
    status = fm["rpz_status"]
    dark = design.get("is_dark", False)
    pal = STATUS_DARK if dark else STATUS_COLORS
    s_pal = pal[status]
    bg_card = design.get("bg_card", "#FFFFFF")
    acc = design["accent"]

    card_border_style = design.get("card_style", "border_left")
    if card_border_style == "border_left":
        border_css = f"border-left:{s_pal['border_w']} solid {s_pal['border']};"
    elif card_border_style == "hairline":
        border_css = f"border:0.5px solid {s_pal['border']};"
    else:
        border_css = f"border:1px solid {s_pal['border']};"

    causes_html = " &nbsp;·&nbsp; ".join(
        f"<span class='inline-cause'>{c.get('ursache_id','')} {c.get('beschreibung','')[:40]}</span>"
        for c in fm.get("causes", [])[:3]
    )

    return f"""
<div class="fm-card fm-compact" style="background:{bg_card};{border_css}">
  <div class="compact-header">
    <div class="compact-left">
      <span class="fm-id-small">{fm['fehler_id']}</span>
      <span class="fm-title-small">{fm['fehlermodus'][:70]}</span>
      <span class="fm-komp-small">{fm['komp_name']}</span>
    </div>
    <div class="compact-right">
      <div class="rpz-inline" style="color:{s_pal['text']}">RPZ <strong>{fm['rpz']}</strong> = {fm['S']}×{fm['O']}×{fm['D']}</div>
      <div class="status-badge-small" style="color:{s_pal['text']};background:{s_pal['bg']};border-color:{s_pal['border']}">{STATUS_LABEL[status]}</div>
    </div>
  </div>
  {'<div class="compact-causes"><span class="causes-label">Ursachen:</span> ' + causes_html + '</div>' if causes_html else ''}
  <div class="compact-verdict" style="color:{s_pal['text']}">Vollständig bewertet — RPZ {fm['rpz']} unter Handlungsschwelle (100). Keine Maßnahmen erforderlich.</div>
</div>"""


def render_section_header(category, design):
    name = category["name"]
    label = CATEGORY_LABELS.get(name, name)
    icon = CATEGORY_ICONS.get(name, "")
    stats_parts = []
    if category["hoch_cnt"]: stats_parts.append(f"{category['hoch_cnt']} hoch")
    if category["mittel_cnt"]: stats_parts.append(f"{category['mittel_cnt']} mittel")
    if category["niedrig_cnt"]: stats_parts.append(f"{category['niedrig_cnt']} niedrig")
    stats_parts.append(f"max. RPZ {category['max_rpz']}")
    stats_str = " · ".join(stats_parts)

    dark = design.get("is_dark", False)
    acc = design["accent"]
    sec_style = design.get("section_style", "rule")
    bg_sec = design.get("bg_section", "transparent")
    text_col = design.get("text_secondary", "#666")

    if sec_style == "band":
        border_css = f"background:{bg_sec};border-top:1px solid {acc};border-bottom:1px solid rgba(255,255,255,0.05);"
    elif sec_style == "rule":
        border_css = f"background:transparent;border-top:1px solid {acc};padding-top:16px;"
    else:
        border_css = "background:transparent;"

    return f"""
<div class="section-header" style="{border_css}">
  <div class="section-header-inner">
    <div class="section-icon" style="color:{acc}">{icon}</div>
    <div class="section-title-group">
      <div class="section-name" style="color:{acc}">{label.upper()}</div>
      <div class="section-stats" style="color:{text_col}">{stats_str}</div>
    </div>
  </div>
</div>"""


# ─────────────────────────────────────────────
# DESIGN CONFIGS
# ─────────────────────────────────────────────

DESIGNS = [
    {
        "id": "v2_01_obsidian",
        "name": "Obsidian",
        "tagline": "Bloomberg Terminal meets McKinsey — Dunkel, Präzise, Autoritativ",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "font_heading": "'Inter', sans-serif",
        "font_body": "'Inter', sans-serif",
        "bg_primary": "#0A0A0F",
        "bg_page": "#0E0E16",
        "bg_card": "#13131E",
        "bg_section": "rgba(255,255,255,0.03)",
        "bg_header": "#050509",
        "text_primary": "#E8E8F0",
        "text_secondary": "#7070A0",
        "text_muted": "#40405A",
        "accent": "#A0A0C8",
        "accent2": "#6060A8",
        "border_color": "rgba(255,255,255,0.07)",
        "sod_style": "thin_arc",
        "is_dark": True,
        "card_style": "border_left",
        "section_style": "band",
        "extra_css": """
          body { background: #050509; }
          .report-wrapper { box-shadow: 0 40px 120px rgba(0,0,0,0.8); }
          .header-block { background: #050509; border-bottom: 1px solid rgba(255,255,255,0.06); }
          .header-rule { background: #A0A0C8; height: 1px; margin: 0; }
          .report-title { font-size: 26px; font-weight: 300; letter-spacing: 3px; text-transform: uppercase; }
          .report-subtitle { font-size: 10px; letter-spacing: 4px; opacity: 0.4; text-transform: uppercase; margin-top: 4px; }
          .stat-value { font-size: 28px; font-weight: 200; }
          .stat-label { font-size: 8px; letter-spacing: 2px; opacity: 0.4; }
        """,
    },
    {
        "id": "v2_02_chalk",
        "name": "Chalk",
        "tagline": "Schweizer Editorial — Maximales Whitespace, Haarlinien-Raster",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;800&display=swap",
        "font_heading": "'Inter', sans-serif",
        "font_body": "'Inter', sans-serif",
        "bg_primary": "#FFFFFF",
        "bg_page": "#F0F0F0",
        "bg_card": "#FFFFFF",
        "bg_section": "transparent",
        "bg_header": "#FFFFFF",
        "text_primary": "#111111",
        "text_secondary": "#888888",
        "text_muted": "#BBBBBB",
        "accent": "#111111",
        "accent2": "#888888",
        "border_color": "#E8E8E8",
        "sod_style": "dot_grid",
        "is_dark": False,
        "card_style": "hairline",
        "section_style": "rule",
        "extra_css": """
          .header-block { background: #FFFFFF; border-bottom: 1px solid #111; }
          .header-rule { background: #111; height: 2px; }
          .report-title { font-size: 28px; font-weight: 800; letter-spacing: -1px; }
          .report-subtitle { font-size: 10px; color: #888; font-weight: 300; letter-spacing: 1px; margin-top: 6px; }
          .stat-value { font-size: 32px; font-weight: 800; letter-spacing: -1px; }
          .stat-label { font-size: 8px; color: #888; font-weight: 300; letter-spacing: 1px; }
          .fm-card { box-shadow: none; }
          .section-name { font-weight: 800; font-size: 10px; letter-spacing: 3px; }
        """,
    },
    {
        "id": "v2_03_dusk",
        "name": "Dusk",
        "tagline": "Morgan Stanley Naval Authority — Strukturierte Seriosität",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap",
        "font_heading": "'Libre Baskerville', serif",
        "font_body": "'Inter', sans-serif",
        "bg_primary": "#F4F1EC",
        "bg_page": "#E8E4DD",
        "bg_card": "#FAF8F4",
        "bg_section": "#EDE9E1",
        "bg_header": "#2B3D5C",
        "text_primary": "#1A2030",
        "text_secondary": "#5A6880",
        "text_muted": "#9AAABB",
        "accent": "#2B3D5C",
        "accent2": "#7A90B0",
        "border_color": "#DDD8CE",
        "sod_style": "segmented_bar",
        "is_dark": False,
        "card_style": "border_left",
        "section_style": "band",
        "extra_css": """
          .header-block { background: #2B3D5C; }
          .header-rule { background: #7A90B0; height: 1px; }
          .report-title { font-family: 'Libre Baskerville', serif; font-size: 28px; font-weight: 700; color: #FFFFFF; }
          .report-subtitle { font-size: 10px; color: rgba(255,255,255,0.5); letter-spacing: 2px; margin-top: 6px; }
          .stat-value { font-size: 28px; font-weight: 700; font-family: 'Libre Baskerville', serif; color: #FFFFFF; }
          .stat-label { font-size: 8px; color: rgba(255,255,255,0.4); letter-spacing: 2px; }
          .section-name { font-family: 'Libre Baskerville', serif; }
          .chapter-num { font-size: 72px; font-weight: 700; color: #2B3D5C; opacity: 0.08; line-height: 1; position: absolute; right: 24px; top: -8px; }
        """,
    },
    {
        "id": "v2_04_muji",
        "name": "Muji",
        "tagline": "Japanische Designphilosophie — Extreme Stille, Tusche-Linien",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;700&family=DM+Sans:wght@300;400;500&display=swap",
        "font_heading": "'Noto Serif JP', serif",
        "font_body": "'DM Sans', sans-serif",
        "bg_primary": "#F9F7F4",
        "bg_page": "#EFECE7",
        "bg_card": "#FDFCFA",
        "bg_section": "transparent",
        "bg_header": "#F9F7F4",
        "text_primary": "#1A1714",
        "text_secondary": "#8A8478",
        "text_muted": "#C4BFB8",
        "accent": "#1A1714",
        "accent2": "#8A8478",
        "border_color": "#E0DDD8",
        "sod_style": "text_only",
        "is_dark": False,
        "card_style": "hairline",
        "section_style": "minimal",
        "extra_css": """
          .header-block { background: #F9F7F4; border-bottom: 1px solid #1A1714; }
          .header-rule { display: none; }
          .report-title { font-family: 'Noto Serif JP', serif; font-size: 22px; font-weight: 300; letter-spacing: 4px; }
          .report-subtitle { font-size: 9px; letter-spacing: 4px; color: #8A8478; font-weight: 300; margin-top: 8px; }
          .stat-value { font-family: 'Noto Serif JP', serif; font-size: 28px; font-weight: 300; }
          .stat-label { font-size: 8px; letter-spacing: 2px; color: #8A8478; font-weight: 300; }
          .fm-card { border-radius: 0; box-shadow: none; }
          .section-name { font-family: 'Noto Serif JP', serif; font-weight: 300; letter-spacing: 4px; font-size: 9px; }
        """,
    },
    {
        "id": "v2_05_copper",
        "name": "Copper",
        "tagline": "Industriell-Premium — Siemens/Bosch Jahresbericht, Kupfer-Akzent",
        "fonts_url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap",
        "font_heading": "'DM Serif Display', serif",
        "font_body": "'DM Sans', sans-serif",
        "bg_primary": "#F2F0ED",
        "bg_page": "#E6E3DE",
        "bg_card": "#F8F6F3",
        "bg_section": "#EAE7E2",
        "bg_header": "#1C1A18",
        "text_primary": "#1C1A18",
        "text_secondary": "#7A7260",
        "text_muted": "#B0AA9E",
        "accent": "#B87333",
        "accent2": "#8A5820",
        "border_color": "#D8D3CB",
        "sod_style": "half_ring",
        "is_dark": False,
        "card_style": "border_left",
        "section_style": "band",
        "extra_css": """
          .header-block { background: #1C1A18; }
          .header-rule { background: #B87333; height: 2px; }
          .report-title { font-family: 'DM Serif Display', serif; font-size: 30px; color: #F8F6F3; letter-spacing: 0.5px; }
          .report-subtitle { font-size: 10px; color: rgba(248,246,243,0.45); letter-spacing: 2px; font-family: 'DM Sans', sans-serif; margin-top: 6px; }
          .stat-value { font-family: 'DM Serif Display', serif; font-size: 30px; color: #F8F6F3; }
          .stat-label { font-size: 8px; color: rgba(248,246,243,0.4); letter-spacing: 2px; }
          .section-name { font-family: 'DM Serif Display', serif; font-size: 12px; }
        """,
    },
    {
        "id": "v2_06_emerald",
        "name": "Emerald",
        "tagline": "Rolex / LVMH Annual Report — Smaragd, Elfenbein, Feine Goldlinie",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Jost:wght@300;400;500;600&display=swap",
        "font_heading": "'Cormorant Garamond', serif",
        "font_body": "'Jost', sans-serif",
        "bg_primary": "#FAF8F3",
        "bg_page": "#EEE9DF",
        "bg_card": "#FDFCF8",
        "bg_section": "#F3F0EA",
        "bg_header": "#1B4D3E",
        "text_primary": "#1A2520",
        "text_secondary": "#607060",
        "text_muted": "#A0B0A8",
        "accent": "#1B4D3E",
        "accent2": "#C9A84C",
        "border_color": "#D8D2C4",
        "sod_style": "filled_dot",
        "is_dark": False,
        "card_style": "border_left",
        "section_style": "rule",
        "extra_css": """
          .header-block { background: #1B4D3E; border-bottom: 1px solid #C9A84C; }
          .header-rule { background: #C9A84C; height: 1px; }
          .report-title { font-family: 'Cormorant Garamond', serif; font-size: 32px; font-weight: 600; color: #FAF8F3; letter-spacing: 1px; }
          .report-subtitle { font-size: 10px; color: rgba(250,248,243,0.5); letter-spacing: 3px; font-family: 'Jost', sans-serif; font-weight: 300; margin-top: 6px; }
          .stat-value { font-family: 'Cormorant Garamond', serif; font-size: 34px; font-weight: 600; color: #FAF8F3; }
          .stat-label { font-size: 8px; color: rgba(250,248,243,0.4); letter-spacing: 2px; }
          .section-name { font-family: 'Cormorant Garamond', serif; font-size: 13px; font-weight: 600; }
          .fm-title { font-family: 'Cormorant Garamond', serif; font-size: 17px; }
        """,
    },
    {
        "id": "v2_07_mercury",
        "name": "Mercury",
        "tagline": "Scientific Journal (Nature) — Indigo als einzige Farbe, Zahlen regieren",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap",
        "font_heading": "'Source Serif 4', serif",
        "font_body": "'IBM Plex Sans', sans-serif",
        "bg_primary": "#FFFFFF",
        "bg_page": "#F0F0F2",
        "bg_card": "#FFFFFF",
        "bg_section": "#F8F8FC",
        "bg_header": "#FFFFFF",
        "text_primary": "#1A1A2E",
        "text_secondary": "#6B7080",
        "text_muted": "#B0B4C0",
        "accent": "#3730A3",
        "accent2": "#6366F1",
        "border_color": "#E4E6F0",
        "sod_style": "numerical",
        "is_dark": False,
        "card_style": "hairline",
        "section_style": "rule",
        "extra_css": """
          .header-block { background: #FFFFFF; border-bottom: 2px solid #3730A3; }
          .header-rule { display: none; }
          .report-title { font-family: 'Source Serif 4', serif; font-size: 26px; font-weight: 600; color: #1A1A2E; }
          .report-subtitle { font-size: 9px; letter-spacing: 2px; color: #6B7080; font-family: 'IBM Plex Sans', sans-serif; margin-top: 6px; }
          .stat-value { font-family: 'IBM Plex Sans', sans-serif; font-size: 28px; font-weight: 300; color: #3730A3; }
          .stat-label { font-size: 8px; color: #B0B4C0; letter-spacing: 1.5px; }
          .section-name { color: #3730A3 !important; font-family: 'IBM Plex Sans', sans-serif; font-size: 9px; letter-spacing: 3px; }
          .fm-title { font-family: 'Source Serif 4', serif; font-size: 16px; }
        """,
    },
    {
        "id": "v2_08_chamois",
        "name": "Chamois",
        "tagline": "Uhrmacher-Luxus — Verdigris, Chamois, Handwerk-Präzision",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Mulish:wght@300;400;500;600&display=swap",
        "font_heading": "'Playfair Display', serif",
        "font_body": "'Mulish', sans-serif",
        "bg_primary": "#F7F3EC",
        "bg_page": "#EAE5DB",
        "bg_card": "#FCF9F4",
        "bg_section": "#EEE9DF",
        "bg_header": "#2E3530",
        "text_primary": "#2A2018",
        "text_secondary": "#8A7860",
        "text_muted": "#BFB5A5",
        "accent": "#4A7C7A",
        "accent2": "#C8A068",
        "border_color": "#D8D0C0",
        "sod_style": "half_ring",
        "is_dark": False,
        "card_style": "border_left",
        "section_style": "band",
        "extra_css": """
          .header-block { background: #2E3530; }
          .header-rule { background: #4A7C7A; height: 1px; }
          .report-title { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: #FCF9F4; }
          .report-subtitle { font-size: 10px; color: rgba(252,249,244,0.45); letter-spacing: 3px; font-family: 'Mulish', sans-serif; font-weight: 300; margin-top: 6px; }
          .stat-value { font-family: 'Playfair Display', serif; font-size: 30px; color: #FCF9F4; }
          .stat-label { font-size: 8px; color: rgba(252,249,244,0.4); letter-spacing: 2px; }
          .section-name { font-family: 'Playfair Display', serif; font-size: 12px; }
          .fm-title { font-family: 'Playfair Display', serif; font-size: 16px; }
        """,
    },
    {
        "id": "v2_09_polar",
        "name": "Polar",
        "tagline": "Skandinavisch (Nokia/Ericsson) — Eisblau, Plus Jakarta Sans, Kristallklarheit",
        "fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap",
        "font_heading": "'Plus Jakarta Sans', sans-serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "bg_primary": "#F8FAFB",
        "bg_page": "#EBF0F4",
        "bg_card": "#FFFFFF",
        "bg_section": "#EEF4F8",
        "bg_header": "#1E2D3D",
        "text_primary": "#1E293B",
        "text_secondary": "#64748B",
        "text_muted": "#B0BEC8",
        "accent": "#3B82F6",
        "accent2": "#DBEAFE",
        "border_color": "#E2EBF0",
        "sod_style": "square_dot",
        "is_dark": False,
        "card_style": "border_left",
        "section_style": "band",
        "extra_css": """
          .header-block { background: #1E2D3D; }
          .header-rule { background: #3B82F6; height: 1px; }
          .report-title { font-size: 24px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.5px; }
          .report-subtitle { font-size: 10px; color: rgba(255,255,255,0.4); letter-spacing: 1px; font-weight: 300; margin-top: 6px; }
          .stat-value { font-size: 28px; font-weight: 700; color: #FFFFFF; }
          .stat-label { font-size: 8px; color: rgba(255,255,255,0.4); letter-spacing: 1.5px; }
          .section-header { border-radius: 4px; }
        """,
    },
]


# ─────────────────────────────────────────────
# SHARED CSS
# ─────────────────────────────────────────────

def shared_css(design):
    d = design
    dark = d.get("is_dark", False)
    return f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: {d['font_body']};
  background: {d['bg_page']};
  color: {d['text_primary']};
  -webkit-font-smoothing: antialiased;
  padding: 40px 20px;
}}
.report-wrapper {{
  width: 794px;
  margin: 0 auto;
  background: {d['bg_primary']};
  box-shadow: 0 20px 80px rgba(0,0,0,0.18);
}}
.header-block {{
  padding: 36px 48px 28px;
}}
.header-inner {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}}
.header-rule {{
  width: 100%;
  height: 1px;
  margin-top: 20px;
}}
.report-meta {{ font-size: 9px; letter-spacing: 2px; color: rgba(255,255,255,0.4); text-transform: uppercase; margin-bottom: 10px; font-family: {d['font_body']}; }}
.report-title {{ font-family: {d['font_heading']}; color: {d['text_primary']}; }}
.report-subtitle {{ font-family: {d['font_body']}; }}
.header-stats {{ display: flex; gap: 28px; align-items: flex-end; }}
.stat-item {{ text-align: right; }}
.stat-value {{ font-family: {d['font_heading']}; display: block; }}
.stat-label {{ text-transform: uppercase; display: block; margin-top: 2px; }}
.content-area {{ padding: 32px 48px 48px; }}

/* Section header */
.section-header {{
  padding: 14px 0;
  margin-bottom: 20px;
  margin-top: 36px;
  position: relative;
}}
.section-header:first-child {{ margin-top: 0; }}
.section-header-inner {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.section-icon {{ display: flex; align-items: center; }}
.section-title-group {{ display: flex; flex-direction: column; gap: 2px; }}
.section-name {{
  font-family: {d['font_body']};
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}}
.section-stats {{
  font-size: 9px;
  font-weight: 400;
}}

/* Cards */
.fm-card {{
  border-radius: 3px;
  margin-bottom: 14px;
  overflow: hidden;
  background: {d['bg_card']};
  border: 1px solid {d['border_color']};
}}
.card-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 18px 20px 12px;
  border-bottom: 1px solid {d['border_color']};
}}
.card-header-left {{ flex: 1; min-width: 0; }}
.card-header-right {{ display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; margin-left: 16px; }}
.fm-id {{ font-size: 8px; letter-spacing: 1.5px; color: {d['accent']}; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }}
.fm-title {{ font-family: {d['font_heading']}; font-size: 14px; font-weight: 600; line-height: 1.3; color: {d['text_primary']}; margin-bottom: 4px; }}
.fm-komp {{ font-size: 9px; color: {d['text_muted']}; }}
.fm-context {{
  font-size: 10.5px; font-style: italic; color: {d['text_secondary']};
  padding: 10px 20px; border-bottom: 1px solid {d['border_color']};
  line-height: 1.6;
}}
.rpz-box {{
  text-align: center;
  padding: 8px 14px;
  border: 1px solid;
  border-radius: 2px;
  min-width: 70px;
}}
.rpz-value {{ font-family: {d['font_heading']}; font-size: 28px; font-weight: 700; line-height: 1; }}
.rpz-label {{ font-size: 7px; letter-spacing: 2px; opacity: 0.6; text-transform: uppercase; }}
.rpz-formula {{ font-size: 8px; opacity: 0.5; margin-top: 2px; }}
.status-badge {{
  font-size: 7.5px; font-weight: 700; letter-spacing: 1.5px;
  padding: 3px 7px; border-radius: 2px; border: 1px solid;
  text-transform: uppercase;
}}
.badge-mini {{
  font-size: 7px; font-weight: 700; letter-spacing: 1px;
  padding: 2px 5px; border-radius: 2px; border: 1px solid;
  text-transform: uppercase; margin-left: 6px;
}}

/* SOD */
.sod-row {{
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 16px 20px;
  border-bottom: 1px solid {d['border_color']};
}}
.sod-item {{
  flex: 1;
  padding: 0 12px;
}}
.sod-item:first-child {{ padding-left: 0; }}
.sod-item:last-child {{ padding-right: 0; }}
.sod-meta {{ margin-top: 4px; }}
.sod-desc {{ font-size: 9px; color: {d['text_secondary']}; line-height: 1.4; }}
.sod-grund {{ font-size: 8.5px; color: {d['text_muted']}; margin-top: 3px; line-height: 1.4; font-style: italic; }}
.sod-mult {{
  font-size: 14px; color: {d['text_muted']}; padding-top: 10px;
  flex-shrink: 0;
}}
.override-note {{
  font-size: 9.5px; color: #7C2D12; background: #FFF7ED;
  border-left: 3px solid #C2410C; padding: 8px 16px;
  border-bottom: 1px solid rgba(194,65,12,0.15);
}}

/* Details */
.details-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 1px solid {d['border_color']};
}}
.details-col {{ padding: 12px 20px; }}
.details-col:first-child {{ border-right: 1px solid {d['border_color']}; }}
.section-label {{ font-size: 7.5px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: {d['accent']}; margin-bottom: 8px; }}
.cause-row {{ display: grid; grid-template-columns: auto 1fr auto; gap: 6px; padding: 4px 0; border-bottom: 0.5px solid {d['border_color']}; align-items: baseline; }}
.cause-row:last-child {{ border-bottom: none; }}
.cause-id {{ font-size: 8px; font-weight: 600; color: {d['accent']}; white-space: nowrap; }}
.cause-desc {{ font-size: 9px; color: {d['text_secondary']}; line-height: 1.4; }}
.cause-phase {{ font-size: 7.5px; color: {d['text_muted']}; white-space: nowrap; }}
.eff-row {{ display: flex; justify-content: space-between; align-items: baseline; padding: 4px 0; border-bottom: 0.5px dotted {d['border_color']}; }}
.eff-row:last-child {{ border-bottom: none; }}
.eff-label {{ font-size: 8.5px; color: {d['text_muted']}; }}
.eff-val {{ font-size: 9px; font-weight: 500; color: {d['text_secondary']}; }}
.controls-section {{ padding: 12px 20px; border-bottom: 1px solid {d['border_color']}; }}
.ctrl-row {{ display: grid; grid-template-columns: auto auto 1fr; gap: 8px; padding: 4px 0; border-bottom: 0.5px solid {d['border_color']}; align-items: baseline; }}
.ctrl-row:last-child {{ border-bottom: none; }}
.ctrl-name {{ font-size: 9px; font-weight: 600; color: {d['accent']}; }}
.ctrl-type {{ font-size: 7.5px; color: {d['text_muted']}; }}
.ctrl-wirkung {{ font-size: 9px; color: {d['text_secondary']}; }}
.measures-section {{ padding: 12px 20px; }}
.measure-row {{ padding: 6px 0; border-bottom: 0.5px solid {d['border_color']}; }}
.measure-row:last-child {{ border-bottom: none; }}
.measure-name {{ font-size: 9.5px; font-weight: 500; color: {d['text_primary']}; margin-bottom: 3px; }}
.measure-delta {{ font-size: 8.5px; color: {d['text_muted']}; }}
.measure-begr {{ font-size: 8px; color: {d['text_muted']}; font-style: italic; margin-top: 2px; }}

/* Compact card */
.fm-compact {{ padding: 10px 16px; }}
.compact-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; gap: 12px; }}
.compact-left {{ flex: 1; display: flex; flex-direction: column; gap: 2px; }}
.fm-id-small {{ font-size: 7.5px; letter-spacing: 1.5px; color: {d['accent']}; font-weight: 600; text-transform: uppercase; }}
.fm-title-small {{ font-size: 11px; font-weight: 500; color: {d['text_primary']}; line-height: 1.3; }}
.fm-komp-small {{ font-size: 8.5px; color: {d['text_muted']}; }}
.compact-right {{ display: flex; flex-direction: column; align-items: flex-end; gap: 4px; flex-shrink: 0; }}
.rpz-inline {{ font-size: 9px; }}
.status-badge-small {{
  font-size: 7px; font-weight: 700; letter-spacing: 1px;
  padding: 2px 6px; border-radius: 2px; border: 1px solid;
  text-transform: uppercase;
}}
.compact-causes {{ font-size: 8.5px; color: {d['text_muted']}; margin-bottom: 5px; line-height: 1.5; }}
.causes-label {{ font-weight: 600; color: {d['text_secondary']}; }}
.inline-cause {{ }}
.compact-verdict {{
  font-size: 8.5px; font-style: italic; opacity: 0.7;
  padding: 4px 8px; border-radius: 2px;
  background: {d['bg_section']};
}}

/* Tier divider */
.tier-divider {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0 12px;
}}
.tier-line {{ flex: 1; height: 0.5px; background: {d['border_color']}; }}
.tier-label {{ font-size: 8px; letter-spacing: 1.5px; color: {d['text_muted']}; text-transform: uppercase; white-space: nowrap; }}

/* Footer */
.footer-block {{
  padding: 16px 48px;
  border-top: 1px solid {d['border_color']};
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.footer-text {{ font-size: 8px; color: {d['text_muted']}; letter-spacing: 1px; }}
"""


# ─────────────────────────────────────────────
# FULL REPORT RENDERER
# ─────────────────────────────────────────────

def render_report(design, categories):
    d = design
    total_fms = sum(len(cat["fms"]) for cat in categories)
    total_hoch = sum(cat["hoch_cnt"] for cat in categories)
    total_mittel = sum(cat["mittel_cnt"] for cat in categories)
    total_niedrig = sum(cat["niedrig_cnt"] for cat in categories)
    max_rpz = max(cat["max_rpz"] for cat in categories) if categories else 0

    # Build content
    content_parts = []
    for cat in categories:
        content_parts.append(render_section_header(cat, design))
        # Full cards first
        full_fms = [fm for fm in cat["fms"] if fm["is_full"]]
        compact_fms = [fm for fm in cat["fms"] if not fm["is_full"]]
        for fm in full_fms:
            content_parts.append(render_full_card(fm, design))
        if compact_fms:
            content_parts.append(f"""
<div class="tier-divider">
  <div class="tier-line"></div>
  <div class="tier-label">Niedrig-Risiko — vollständig bewertet, keine Maßnahmen</div>
  <div class="tier-line"></div>
</div>""")
            for fm in compact_fms:
                content_parts.append(render_compact_card(fm, design))

    stat_col = "rgba(255,255,255,0.5)" if d.get("is_dark") else d["text_muted"]

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FMEA Report — {d['name']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{d['fonts_url']}" rel="stylesheet">
<style>
{shared_css(design)}
{d.get('extra_css', '')}
</style>
</head>
<body>
<div class="report-wrapper">
  <div class="header-block">
    <div class="report-meta">Ethylacetatproduktion · Teilanlage 20TA42 · FMEA Risikoanalyse 2026</div>
    <div class="header-inner">
      <div>
        <div class="report-title">{d['name']}</div>
        <div class="report-subtitle">{d['tagline']}</div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-value">{total_hoch + total_mittel}</span>
          <span class="stat-label" style="color:{stat_col}">Maßnahmen</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{total_niedrig}</span>
          <span class="stat-label" style="color:{stat_col}">Niedrig</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{max_rpz}</span>
          <span class="stat-label" style="color:{stat_col}">Max RPZ</span>
        </div>
      </div>
    </div>
    <div class="header-rule"></div>
  </div>
  <div class="content-area">
    {''.join(content_parts)}
  </div>
  <div class="footer-block">
    <span class="footer-text">FMEA Risikoanalyse · Ethylacetatproduktion · Vertraulich</span>
    <span class="footer-text">Design: {d['name']} · Runde 6</span>
  </div>
</div>
</body>
</html>"""
    return html


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Loading data from DB...")
    categories = load_data()
    print(f"Loaded {sum(len(c['fms']) for c in categories)} failure modes across {len(categories)} categories")

    generated = []
    for design in DESIGNS:
        fname = f"preview_{design['id']}.html"
        fpath = os.path.join(OUT_DIR, fname)
        html = render_report(design, categories)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ {fname}")
        generated.append((design, fname))

    # Update index.html
    update_index(generated)
    print(f"\nDone. {len(generated)} previews written to {OUT_DIR}")


def update_index(generated):
    index_path = os.path.join(OUT_DIR, "index.html")
    if not os.path.exists(index_path):
        print("  (index.html not found, skipping)")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_entries = ""
    for design, fname in generated:
        new_entries += f"""
        <div class="preview-card">
          <a href="{fname}" class="preview-link">
            <div class="preview-title">{design['name']}</div>
            <div class="preview-desc">{design['tagline']}</div>
            <div class="preview-meta">Runde 6 · Fehlerart-Struktur · {design['sod_style']}</div>
          </a>
        </div>"""

    runde6_block = f"""
    <!-- Runde 6: 9 neue Design-Konzepte (Fehlerart-Struktur) -->
    <div class="round-header">
      <h2>Runde 6 — 9 neue Konzepte (Fehlerart-Struktur)</h2>
      <p>Gliederung nach Thermisch / Mechanisch / MSR · echte DB-Daten · 9 eigenständige Ästhetiken</p>
    </div>
    <div class="preview-grid">{new_entries}
    </div>"""

    # Try to inject before </body>
    if "</body>" in content:
        content = content.replace("</body>", runde6_block + "\n</body>")
    else:
        content += runde6_block

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✓ index.html updated (Runde 6)")


if __name__ == "__main__":
    main()
