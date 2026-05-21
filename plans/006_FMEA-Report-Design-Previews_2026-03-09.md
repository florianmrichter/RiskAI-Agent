# Plan: Zwei Real-Data-Previews (je 1 pro Design-Stil) + Überarbeitetes Farbsystem

**Datum:** 2026-03-09
**Status:** Bereit zur Umsetzung

---

## Anforderungen

1. **Farben kräftiger** — Status-Farben (kritisch/hoch/mittel/niedrig) müssen wesentlich deutlicher sein, eindeutig identifizierbar und klar vom Terracotta-Akzent abgehoben

2. **Zwei separate Previews mit echten Confidence-Anlage-Daten** (erste ~5 Seiten):
   - **Preview A** — im Stil von `preview_05_warm_authority` (dunkler Header, Cormorant Garamond, Cream-Hintergrund, Gold-Akzente)
   - **Preview B** — im Stil von `preview_07b_forest` (weißer Hintergrund, Libre Franklin, Quadrat-Dot-Scale, Forest-Grün)

3. **Vollständige Ursachen bei Niedrig-FMs** — alle Ursachen explizit aufgelistet (ID + Beschreibung + Phase), nicht nur eine Zählung

---

## Output-Dateien

| Datei | Inhalt |
|-------|--------|
| `.tmp/report_previews/preview_real_05_warm_authority.html` | Design 05 Stil, echte Daten |
| `.tmp/report_previews/preview_real_07b_forest.html` | Design 07b Stil, echte Daten |
| `.tmp/report_previews/index.html` | +Runde 5 Einträge |

---

## Datengrundlage

- Datenbank: `data/fmea.db`, Projekt-ID 2 (Confidence-Anlage 20TA24)
- Aktuell verfügbar: 30 FMs — 7 mittel · 23 niedrig (hoch noch nicht in DB)
- Tabellen: `failure_modes`, `risk_assessments`, `failure_causes`, `failure_effects`, `current_controls`, `measures`, `functions`, `components`
- Join-Pfad: `failure_modes → functions → components` (project_id=2)

---

## Design-Spec

### Kräftige Statusfarben (für beide Previews)

| Status | text | bg | border | accent |
|--------|------|-----|--------|--------|
| KRITISCH | `#991B1B` | `#FEF2F2` | `#F87171` | `#DC2626` |
| HOCH | `#9A3412` | `#FFF7ED` | `#F97316` | `#EA580C` |
| MITTEL | `#92400E` | `#FFFBEB` | `#FBBF24` | `#D97706` |
| NIEDRIG | `#14532D` | `#F0FDF4` | `#22C55E` | `#16A34A` |

### Zwei-Tier Layout (für beide Previews)

**Mittel/Hoch/Kritisch — Vollständige Karte:**
- SOD-Visualisierung (stilabhängig: Dot-Scale oder Gauge)
- Begründung je S/O/D
- RPZ-Box
- Ursachen-Tabelle (alle)
- Fehlerfolgen
- Controls
- Maßnahmen

**Niedrig — Kompaktkarte:**
- SOD-Visualisierung (kleinere Version)
- Begründung je S/O/D
- **ALLE Ursachen explizit** (ID + Beschreibung + Phase)
- Kurze Folgen-Notiz (Freitext)
- Verdict-Box: "Vollständig bewertet — RPZ X unter Handlungsschwelle (100). Keine Maßnahmen erforderlich."
- OHNE: Fehlerfolgen-Grid, Controls-Tabelle, Maßnahmen-Sektion

### Preview A — Warm Authority Stil (Design 05)

- **Typografie:** Cormorant Garamond (Headings, 700) + Plus Jakarta Sans (Body)
- **Hintergrund:** Warm cream `#FDFBF8`
- **Header:** Dunkel `#1C1208` mit Gold-Akzent `#D97706`
- **SOD:** Keine Dot-Scale — stattdessen große Zahl + Begründung (Original-Stil von 05)
- **Karten:** Linker Status-Balken (4px, farbig nach Status)

### Preview B — Nordic Forest Stil (Design 07b)

- **Typografie:** Libre Franklin (400/600/700)
- **Hintergrund:** Reines Weiß `#FFFFFF`
- **Header:** Schlicht, Forest-Grün `#2D5A3D` als Textakzent
- **SOD:** 10 Quadrat-Dots (7×7px, gefüllt vs. leer) — Original-Stil von 07b
- **Karten:** Kein Statusbalken — dünne `0.5px` Border, Statusbadge im Header

---

## Nach Preview-Approval

1. Design auswählen (oder Terracotta-CSS übernehmen)
2. `templates/fmea_report.html` — Schleife in zwei Tiers splitten
3. `templates/fmea_style.css` — Compact-Card-Klassen ergänzen
4. `templates/fmea_style_terracotta.css` — Neue kräftige Statusfarben
5. Neuen PDF-Report für Confidence-Anlage generieren
