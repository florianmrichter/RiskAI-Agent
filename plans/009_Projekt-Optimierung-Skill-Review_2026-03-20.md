# Plan 009: Projekt-Optimierung RiskAI-Agent (Skill-Review)

**Erstellt:** 2026-03-20
**Branch:** `claude/setup-github-skill-AphSm`
**Status:** Phase 1-4 abgeschlossen

## Context

Aus dem Skill-basierten Review (5 parallele Analyse-Agents: Security, Code-Quality, CLAUDE.md/Workflows, Tests, Automation) sind 47 Verbesserungsvorschläge in 8 Kategorien hervorgegangen.

- **S1 (API-Keys):** Entfällt — Keys nicht in Verwendung, bereits auskommentiert
- **S2-S8, C1-C8:** Genehmigt
- **D1-D6:** Genehmigt
- **T1-T8:** Genehmigt
- **A1-A5:** Genehmigt
- **K1-K4:** Genehmigt (K1 als separater Skill)
- **I1-I3:** Genehmigt
- **F1-F14:** Genehmigt (Frontend mit aufgenommen)

### Entscheidungen
- Skill-Pfade: Referenzen bleiben in `.claude/skills/*/references/` (embedded)
- Review-Skill: Separater Skill, nicht in fmea-risikoanalyse integriert
- Storage-Refactoring (C3): Konservativ — Sektionen reorganisiert, nicht in separate Dateien
- Farb-System (F2): Single Source of Truth in `config/fmea_standards.py`, daraus CSS + Excel ableiten

---

## Fortschritt

### Phase 1: Quick Wins — DONE (Commit `4190248`)

| # | Item | Status | Details |
|---|------|--------|---------|
| 1 | S5 — urllib Timeout | DONE | `timeout=10` in `report_generator.py` |
| 2 | C6 — Unused Import | DONE | `import os` aus `storage.py` entfernt |
| 3 | S4 — Context-Manager | DONE | 17 Dateien auf `with FMEAStorage(...) as db:` umgestellt |
| 4 | D1 — Pfad-Referenzen | DONE | 13 Pfade in 6 Dateien korrigiert |
| 5 | F1 — Logo-Assets | DONE | 1.45MB → 392KB (-73%) |

### Phase 2: Fundament — DONE (Commit `b140ef4`)

| # | Item | Status | Details |
|---|------|--------|---------|
| 6 | S2 — Path-Traversal | DONE | `Path.resolve()` + TASKS_ROOT-Check in fmea_loader.py |
| 7 | S3 — SQL-Whitelist | DONE | Whitelist für Spaltennamen in storage.py |
| 8 | S6 — Auto-Validierung | DONE | `validate_plant_data()` automatisch bei load |
| 9 | D2 — Skill-Architektur | DONE | Neue CLAUDE.md-Sektion mit Pfad-Konvention |
| 10 | F2 — Farb-Konsolidierung | DONE | `DESIGN_COLORS` + `RPZ_HEX` in fmea_standards.py |
| 11 | F3 — Inline-Styles | DONE | Wiederholte styles durch CSS-Klassen ersetzt |
| 12 | F8 — Excel-Farben | DONE | Header + RPZ-Farben aus config importiert |
| 13 | T1 — export.py Tests | DONE | 29 neue Tests |
| 14 | T3 — validate_completeness Tests | DONE | 28 neue Tests |
| 15 | T6 — pytest-cov | DONE | pyproject.toml + CI konfiguriert |

### Phase 3: Struktur — DONE (Commits `dfaf5f4`, `4b82308`, `e5bb946`)

| # | Item | Status | Details |
|---|------|--------|---------|
| 16 | F4 — Print-CSS | DONE | widows/orphans, page-breaks, min-fonts |
| 17 | F5 — Header/Footer Templates | DONE | Jinja2-Templates statt Inline-Strings |
| 18 | F6 — HTML-Template modularisiert | DONE | 2529Z → 41Z Shell + 14 Partials |
| 19 | F11 — Jinja2-Logik → Python | DONE | 4 Berechnungsblöcke verschoben |
| 20 | C1 — validate_anlagendaten aufgeteilt | DONE | 5 Helper-Funktionen |
| 21 | C2 — validate_completeness aufgeteilt | DONE | 7 Helper-Funktionen |
| 22 | C3 — FMEAStorage reorganisiert | DONE | 12 Sektionen + 28 Docstrings |
| 23 | T2 — report_generator Tests | DONE | 67 Tests (vorher 8) |
| 24 | K1 — Review-Skill | DONE | `.claude/skills/fmea-review/SKILL.md` |
| 25 | D3 — review Workflow | DONE | `workflows/review-fmea.md` |
| 26 | D4 — MoC Workflow | DONE | `workflows/moc-change-management.md` |
| 27 | A1 — Pflicht-Validierung | DONE | In alle 3 Skills eingebaut |
| 28 | A2 — Startup-Checks | DONE | Config-Existenz in allen Skills |

### Phase 4: Polish — DONE

| # | Item | Status | Details |
|---|------|--------|---------|
| 29 | F7 — Excel-Legende | DONE | "Legende"-Sheet mit RPZ-/STOP-/ABE-/S-O-D-Erklärungen |
| 30 | F9 — Chart 300 DPI | DONE | Risk-Matrix + Treemap: 200→300 DPI |
| 31 | F10 — Farbkontrast WCAG | DONE | `--text-muted` #9CA3AF→#6B7280 (4.6:1), SVG-Labels gefixt |
| 32 | F12/F14 — Excel Polish | DONE | Zebra-Stripes, Wrap-Text, Auto-Filter, border styling |
| 33 | F13 — CSS-Duplikate | DONE | `--risk-*` = `--rpz-*` = Python RPZ_COLORS, DESIGN_COLORS aligned |
| 34 | C4 — Config-Loader | DONE | `load_json_config()` in `_base.py`, caching, reliability + calibration migriert |
| 35 | C5 — Error-Handling | DONE | `@tool_entry` auf 5 Entry-Points (export, report, measures, validate×2) |
| 36 | A3 — Interview→FMEA Bridge | DONE | Auto-Transition-Hinweis im Interview-Skill |
| 37 | A4 — FMEA→Training Bridge | DONE | Training-Hinweis nach Report-Generierung |
| 38 | K2 — Training erweitern | DONE | Maßnahmen-Training-Modus im Training-Skill |
| 39 | K3 — Interview Resume | DONE | Resume-Sektion im Interview-Skill |
| 40 | T4 — generate_measures Tests | DONE | 12+ Tests |
| 41 | T5 — reliability_lookup Tests | DONE | 10+ Tests |
| 42 | T7 — Eval in CI | DONE | CI erweitert um Eval-Job |
| 43 | T8 — Pre-commit Hooks | DONE | `.pre-commit-config.yaml` (ruff + pre-commit-hooks) |
| 44 | D5/D6 — Restliche Docs | DONE | `workflows/tools-reference.md` |
| 45 | I1-I3 — CI/CD + Makefile | DONE | Makefile (lint/test/cov/fmt/clean) + TESTING.md |
| 46 | K4 — Bulk-Validator Skill | DONE | `.claude/skills/bulk-validator/SKILL.md` + README |
| 47 | A5 — Post-Insert Normalisierung | DONE | `_normalize_text()` in 6 Insert-Methoden |

---

## Metriken

| Metrik | Vorher | Phase 3 | Phase 4 | Delta gesamt |
|--------|--------|---------|---------|--------------|
| Tests | 173 | 289 | 336+ | +163+ (+94%) |
| Coverage | ~30% | 42% | 46% | +16pp |
| Template-Zeilen (main) | 2.529 | 41 | 41 | -98% |
| Logo-Assets | 1.45 MB | 392 KB | 392 KB | -73% |
| Skills | 3 | 4 | 5 | +2 (fmea-review, bulk-validator) |
| Workflows | 5 | 7 | 8 | +3 (review, moc, tools-ref) |
| Excel-Sheets | 4 | 4 | 5 | +1 (Legende) |
| Chart DPI | 200 | 200 | 300 | +50% |
| Commits | — | 5 | 6 | — |

---

## Verifikation

Nach jeder Phase:
1. `pytest tests/ -v` — alle Tests müssen grün sein
2. `ruff check tools/ config/` — kein Lint-Fehler
3. Manueller Smoke-Test: FMEA-Session für Büchi-Projekt → Report generieren → PDF + Excel prüfen
4. Ab Phase 2: `pytest --cov=tools tests/` — Coverage-Trend prüfen
5. Ab Phase 3 (Frontend): Report-PDF visuell prüfen (Farben, Seitenumbrüche, Logos)
