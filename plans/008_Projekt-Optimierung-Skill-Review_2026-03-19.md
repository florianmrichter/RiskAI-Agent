# 008 — Projekt-Optimierung: Skill-basierter Review

**Datum:** 2026-03-19
**Status:** ENTWURF — zur Durchsicht mit User

---

## Zusammenfassung

6 parallele Analysen des gesamten Projekts aus der Perspektive aller aktiven Skills (inkl. Frontend-Design). Ergebnis: 56 konkrete Verbesserungsvorschläge in 8 Kategorien, priorisiert nach Impact und Aufwand.

---

## Kategorie 1: Security (3 HIGH, 5 MEDIUM/LOW)

### S1 — API-Keys in .env rotieren [HIGH]

- `.env` enthält Klartext-Keys (Gemini, GROQ, OpenRouter)
- `.env` ist korrekt in `.gitignore`, aber Keys sollten trotzdem rotiert werden
- **Aktion:** Keys rotieren, `.env.example` als Template pflegen

### S2 — Path-Traversal-Schutz in fmea_loader.py [HIGH]

- `tools/fmea_loader.py:45-56` — `importlib` lädt Module dynamisch ohne Pfad-Validierung
- `task_folder` könnte `../` enthalten → beliebiger Code-Load
- **Aktion:** `Path.resolve()` + Check gegen `TASKS_ROOT`

### S3 — SQL-Injection bei Spaltennamen in storage.py [HIGH]

- `tools/storage.py:336,432` — Spaltennamen via f-String interpoliert
- Aktuell nicht von User-Input gespeist, aber fragiles Pattern
- **Aktion:** Whitelist-Validierung für Spaltennamen

### S4 — Context-Manager für FMEAStorage durchsetzen [MEDIUM]

- 10+ Dateien nutzen `db = FMEAStorage(...)` ohne `with`-Statement
- Bei Exception wird `db.close()` nie aufgerufen → Resource-Leak
- **Aktion:** Alle Stellen auf `with FMEAStorage(...) as db:` umstellen

### S5 — Timeout für urllib in report_generator.py [MEDIUM]

- `tools/report_generator.py` — Font-Download ohne Timeout (kann hängen)
- **Aktion:** `timeout=10` an `urllib.request.urlopen()` anfügen

### S6 — JSON-Schema-Validierung bei load_plant_data automatisch [MEDIUM]

- `validate_plant_data()` existiert, wird aber nicht automatisch aufgerufen
- **Aktion:** In `load_plant_data()` standardmäßig `validate_plant_data()` einbauen

### S7 — Audit-Logging für DB-Operationen [LOW]

- Kein Log wer wann welche DB-Mutation durchgeführt hat
- **Aktion:** Logging für CRUD-Operationen in `storage.py`

### S8 — Rate-Limiting für API-Calls [LOW]

- Keine Throttling-Logik bei externen API-Aufrufen
- **Aktion:** Exponential Backoff einbauen

---

## Kategorie 2: Code-Qualität & Vereinfachung (8 Items)

### C1 — validate_anlagendaten() aufteilen [MEDIUM]

- `tools/validate_anlagendaten.py:85-467` — 382 Zeilen in einer Funktion
- 7 verschiedene Validierungschecks vermischt
- **Aktion:** In 5 Helper-Funktionen extrahieren

### C2 — validate_completeness() aufteilen [MEDIUM]

- `tools/validate_completeness.py:32-330` — 299 Zeilen, 7 Phasen
- **Aktion:** Analog zu C1 modularisieren

### C3 — FMEAStorage aufteilen [MEDIUM]

- `tools/storage.py` — 826 Zeilen, 50+ Methoden, Single Responsibility verletzt
- **Aktion:** Aufteilen in `ProjectRepo`, `FailureModeRepo`, `RiskAssessmentRepo`, `MeasureRepo`

### C4 — Zentraler Config-Loader [LOW]

- 3 verschiedene Patterns für JSON-Config-Loading (direkt, mit Check, mit Fallback)
- **Aktion:** `tools/config_loader.py` mit `load_json_config(path, default)` erstellen

### C5 — Error-Handling vereinheitlichen [LOW]

- Mix aus Silent Failure (leeres Dict), Exception Raising, Try-Except Wrapper
- **Aktion:** Pattern festlegen: Exceptions für Fehler, Try-Except nur für Graceful Degradation

### C6 — Unused Import entfernen [LOW]

- `tools/storage.py:14` — `import os` unbenutzt
- **Aktion:** Entfernen

### C7 — Template-Stubs verschieben [LOW]

- `config/fmea_explicit.py` und `config/measures_explicit.py` sind leere Templates
- **Aktion:** Nach `templates/` verschieben oder als deprecated markieren

### C8 — N+1-Query in validate_completeness.py [LOW]

- `tools/validate_completeness.py:241-262` — SELECT pro Failure Mode statt Batch
- **Aktion:** Batch-Load mit `WHERE failure_mode_id IN (...)`

---

## Kategorie 3: Dokumentation & Pfad-Konsistenz (6 Items)

### D1 — Pfad-Referenzen korrigieren [HIGH]

8 falsche Pfade in Docs:


| Dokument                 | Referenz                          | Korrekt                                              |
| ------------------------ | --------------------------------- | ---------------------------------------------------- |
| CLAUDE.md:101            | `references/fmea-workflow.md`     | `workflows/fmea-workflow.md`                         |
| fmea-workflow.md:18      | `references/sod-referenzkarte.md` | `.claude/skills/.../references/sod-referenzkarte.md` |
| fmea-workflow.md:449     | `references/fmea-standards.md`    | `.claude/skills/.../references/fmea-standards.md`    |
| SKILL.md:138             | `references/fmea-standards.md`    | `.claude/skills/.../references/fmea-standards.md`    |
| anlagendaten SKILL.md:21 | `references/interview-phasen.md`  | `.claude/skills/.../references/interview-phasen.md`  |


- **Aktion:** Alle Pfade einheitlich korrigieren, Konvention festlegen (embedded vs. global)

### D2 — Skill-Bundle-Architektur dokumentieren [HIGH]

- Unklar ob `references/`-Dateien in Skill-Ordnern bleiben oder global kopiert werden
- **Aktion:** Sektion in CLAUDE.md: "Skill Architecture" mit klarer Pfad-Konvention

### D3 — Fehlender Workflow: review.py [MEDIUM]

- `tools/review.py` (632 Zeilen) hat keinen Workflow in `workflows/`
- **Aktion:** `workflows/review-fmea.md` erstellen

### D4 — Fehlender Workflow: moc_manager.py [MEDIUM]

- `tools/moc_manager.py` (369 Zeilen) hat keinen Workflow
- **Aktion:** `workflows/moc-change-management.md` erstellen

### D5 — Fehlender Workflow: observability.py [LOW]

- Tool existiert, ist aber nicht in Skill-Flow integriert
- **Aktion:** `workflows/observability-metrics.md` erstellen

### D6 — Tools ohne Workflow dokumentieren [LOW]

- 11 Tools in `tools/` ohne Workflow-Referenz (chart_comparison, cleanup_generic_data, clear_fmea_for_project, export, init_fmea_fresh, migrate_db, observability, run_full_fmea, storage_migrations, structure_analysis, update_fmea_report_fields)
- **Aktion:** In `tools/README.md` kategorisieren (Active / Utility / Legacy)

---

## Kategorie 4: Test-Coverage & Eval (8 Items)

### T1 — export.py testen [HIGH]

- 895 Zeilen, 8 Funktionen, 0 Tests — generiert User-facing Deliverables
- **Aktion:** 15-20 Tests (Excel-Formatting, Sheet-Erstellung, Edge Cases)

### T2 — report_generator.py testen [HIGH]

- 895 Zeilen, 13 Funktionen, nur 8 Tests (nur `strip_sod_prefix`)
- **Aktion:** 30+ Tests für PDF-Generierung, HTML-Templates, Charts

### T3 — validate_completeness.py testen [HIGH]

- Gate-2-Check für Report-Freigabe — 0 direkte Tests
- **Aktion:** 12+ Tests für S/O/D-Plausibilität, Maßnahmen-Sufficiency, CCF

### T4 — generate_measures.py testen [MEDIUM]

- Maßnahmen-Generierung — 0 Tests
- **Aktion:** 10+ Tests für STOP/ABE-Hierarchie

### T5 — reliability_lookup.py testen [MEDIUM]

- OREDA/CCPS-Lookup — 0 Tests
- **Aktion:** 8+ Tests für Referenz-Lookups, Fallback-Logik

### T6 — Coverage-Metrics einführen [MEDIUM]

- Kein `pytest-cov`, keine Coverage-Schwellen
- **Aktion:** `pytest-cov` in dev-deps, 70% Minimum in CI

### T7 — Eval-Scripts in CI integrieren [MEDIUM]

- `eval_goldstandard.py` und `eval_fmea_rpz.py` laufen nur manuell
- **Aktion:** Als pytest-kompatible Tests wrappen, in CI-Pipeline aufnehmen

### T8 — Pre-commit Hooks einrichten [LOW]

- Kein `.pre-commit-config.yaml`
- **Aktion:** Pre-commit mit ruff + pytest-Subset konfigurieren

---

## Kategorie 5: Automation & Hooks (5 Items)

### A1 — Pre-Commit Validierungs-Hook [HIGH]

- Vor `save_state()` automatisch `validate_completeness()` ausführen
- Verhindert unvollständige FMEAs im Git

### A2 — Config-Validierung bei Skill-Start [HIGH]

- Beim Laden eines Skills automatisch prüfen ob alle Config-Dateien existieren und parsbar sind
- Fail-Fast statt mysteriöse Fehler mittendrin

### A3 — Auto-Bridge: Interview → FMEA [MEDIUM]

- Wenn `anlagendaten-interview` fertig → automatisch `fmea-risikoanalyse` anbieten
- Nahtloser Übergang statt manueller Prompt

### A4 — Auto-Bridge: FMEA → Training [MEDIUM]

- Nach Report-Generierung → Training anbieten für FMs mit niedriger Agent-Konfidenz
- **Trigger:** `agent_konfidenz = "niedrig"` FMs pre-selektiert

### A5 — Post-Insert Daten-Normalisierung [LOW]

- Nach `insert_fmea_explicit()` und `insert_measures()` automatisch Text normalisieren
- Whitespace trimmen, Encoding prüfen, Gefahrenfelder-Schema validieren

---

## Kategorie 6: Skill-Verbesserungen (4 Items)

### K1 — Neuer Skill: Report-Review & Sign-off [HIGH]

- `tools/review.py` (632 Zeilen) existiert, aber kein Skill drumherum
- **Trigger:** "FMEA reviewen", "Report freigeben", "Qualitätsprüfung"
- **Output:** Review-Checkliste, Sign-off-Status, Korrekturen zurück in DB

### K2 — fmea-training erweitern: Maßnahmen-Training [MEDIUM]

- Aktuell nur S/O/D-Training
- **Erweiterung:** STOP-Kategorie-Zuweisung, Maßnahmen-Effektivitäts-Klassifikation
- Verbessert Agent-Qualität bei Maßnahmenempfehlungen

### K3 — anlagendaten-interview: Resume-Logik verbessern [MEDIUM]

- Unterscheidung NEW vs. RESUME fehlt in Trigger-Words
- **Aktion:** Trigger "Anlagendaten fortsetzen" hinzufügen
- Auto-Detect: Wenn `anlagendaten.json` existiert → Resume vorschlagen

### K4 — Neuer Skill: Bulk-Projekt-Validator [LOW]

- `validate_anlagendaten()` für einzelne Projekte → Batch für alle unter `tasks/Risikoanalyse/`
- Portfolio-Health-Check über alle Projekte

---

## Kategorie 7: CI/CD & Infrastruktur (3 Items)

### I1 — GitHub Actions erweitern [MEDIUM]

- Aktuell nur ruff + pytest
- **Ergänzen:** Coverage-Report, Eval-Tests, Skill-Referenz-Validierung

### I2 — Makefile für lokale Entwicklung [LOW]

- `make test`, `make lint`, `make coverage`, `make eval`
- **Aktion:** Makefile im Projekt-Root erstellen

### I3 — TESTING.md Guide [LOW]

- Dokumentation: Wie Tests laufen, Subsets, Evals, Goldstandard-Update
- **Aktion:** `TESTING.md` erstellen

---

## Kategorie 8: Frontend & Report-Design (14 Items)

### F1 — Logo-Assets optimieren [HIGH]

- `templates/assets/scholar-navy.png` (836 KB) und `scholar-white.png` (651 KB) sind viel zu groß
- Logos sollten <200 KB sein; besser: SVG statt PNG
- **Aktion:** PNGs mit pngquant/optipng komprimieren oder durch SVG ersetzen

### F2 — Farb-Definitionen konsolidieren [HIGH]

- Risiko-Farben an 3 Stellen definiert: CSS (`--risk-`*), Python (`RPZ_COLORS`), Export (`RPZ_COLORS` dict)
- Farben weichen voneinander ab (CSS: `#DC2626`, Export: `#FF0000`)
- **Aktion:** Single Source of Truth in `config/fmea_standards.py`, daraus CSS + Excel generieren

### F3 — Inline-Styles aus HTML-Template entfernen [HIGH]

- `templates/fmea_report.html` — Tabellenzellen mit wiederholten `style="padding:6px..."` Attributen
- **Aktion:** CSS-Klassen erstellen (`.table-cell`, `.table-header`), HTML um ~30% reduzieren

### F4 — Print-CSS vervollständigen [HIGH]

- Keine `widows`/`orphans`-Regeln, keine expliziten Page-Breaks zwischen Sektionen
- Risk-Cards ohne `page-break-inside: avoid`
- Appendix-Tabellen mit 7.2pt Schrift — zu klein für Druck
- **Aktion:** `@media print {}` Sektion in `fmea_style.css` erweitern

### F5 — Header/Footer als Templates [HIGH]

- `tools/report_generator.py:842-861` — Header/Footer als inline HTML-Strings zusammengebaut
- **Aktion:** Separate `header.html` / `footer.html` Template-Dateien

### F6 — HTML-Template modularisieren [MEDIUM]

- `fmea_report.html` — 3.000+ Zeilen monolithisch, keine `{% include %}` oder `{% macro %}`
- Wiederholte Patterns (Risk-Cards, Tabellen-Header)
- **Aktion:** Aufteilen in Partials: `cover.html`, `sidebar.html`, `risk-card.html`, `appendix.html`

### F7 — Excel-Legende hinzufügen [MEDIUM]

- Export hat farbcodierte RPZ-Zellen aber keine Erklärung
- **Aktion:** "Legende"-Sheet als erstes Tab in Excel mit Farbcodes + Bedeutung

### F8 — Excel-Farben an CSS anpassen [MEDIUM]

- Header: Excel `#2F5496` vs. CSS `#1E3A5F` — Markeninkonsistenz
- RPZ: Excel `#FF0000` vs. CSS `#DC2626`
- **Aktion:** Farben aus zentraler Config übernehmen

### F9 — Chart-Auflösung verbessern [MEDIUM]

- Matplotlib-Charts bei 200 DPI als PNG — kann Artefakte haben
- **Aktion:** SVG statt PNG exportieren, oder mindestens 300 DPI

### F10 — Farbkontrast verbessern (Accessibility) [MEDIUM]

- `--text-muted: #9CA3AF` auf `--bg: #F7F8FA` — Kontrast ~2.5:1 (WCAG-Fail)
- **Aktion:** Minimum `#6B7280` für Lesetext, `--text-muted` nur für dekorative Elemente

### F11 — Jinja2-Logik in Python verlagern [MEDIUM]

- Komplexe `namespace()`-Hacks und Dict-Lookups im Template
- **Aktion:** Preprocessing in `report_generator.py`, Template nur für Darstellung

### F12 — Excel-Spaltenbreiten & Text-Wrapping [LOW]

- Feste 18er Breite für alle Spalten, kein Text-Wrapping
- Lange Beschreibungen werden abgeschnitten
- **Aktion:** Auto-Fit mit Minimum-Breiten, `wrap_text=True` für Beschreibungsfelder

### F13 — CSS-Duplikate bereinigen [LOW]

- Doppelte Farbdefinitionen in CSS (`--risk-`* vs. `--rpz-*` vs. SOD-Badge-Colors)
- **Aktion:** Konsolidieren auf ein Set

### F14 — Alternating Row Shading in Excel [LOW]

- Keine Zebra-Streifen in Excel-Tabellen
- **Aktion:** Alternierend `#F5F5F5` Hintergrund für bessere Lesbarkeit

---

## Priorisierte Umsetzungsreihenfolge

### Phase 1: Quick Wins (1 Tag)


| #   | Item                                  | Aufwand | Impact          |
| --- | ------------------------------------- | ------- | --------------- |
| 1   | S1 — API-Keys rotieren                | 10 min  | Kritisch        |
| 2   | S5 — Timeout für urllib               | 2 min   | Quick Fix       |
| 3   | C6 — Unused Import entfernen          | 1 min   | Cleanup         |
| 4   | S4 — Context-Manager durchsetzen      | 30 min  | Resource Safety |
| 5   | D1 — Pfad-Referenzen korrigieren      | 30 min  | Konsistenz      |
| 6   | F1 — Logo-Assets optimieren (PNG→SVG) | 30 min  | Dateigröße -60% |


### Phase 2: Fundament (3-5 Tage)


| #   | Item                                     | Aufwand | Impact                 |
| --- | ---------------------------------------- | ------- | ---------------------- |
| 7   | S2 — Path-Traversal-Schutz               | 1h      | Security               |
| 8   | S3 — SQL-Spaltennamen-Whitelist          | 1h      | Security               |
| 9   | S6 — Auto-Validierung in load_plant_data | 30 min  | Datenqualität          |
| 10  | D2 — Skill-Architektur dokumentieren     | 1h      | Klarheit               |
| 11  | F2 — Farb-Definitionen konsolidieren     | 2h      | Design-Konsistenz      |
| 12  | F3 — Inline-Styles entfernen             | 3h      | HTML -30%, Wartbarkeit |
| 13  | F8 — Excel-Farben an CSS anpassen        | 1h      | Marken-Konsistenz      |
| 14  | T1 — export.py testen                    | 3h      | Coverage               |
| 15  | T3 — validate_completeness testen        | 2h      | Coverage               |
| 16  | T6 — pytest-cov einführen                | 30 min  | Messbarkeit            |


### Phase 3: Struktur (1-2 Wochen)


| #   | Item                                   | Aufwand | Impact                     |
| --- | -------------------------------------- | ------- | -------------------------- |
| 17  | F4 — Print-CSS vervollständigen        | 2h      | PDF-Qualität               |
| 18  | F5 — Header/Footer als Templates       | 1h      | Wartbarkeit                |
| 19  | F6 — HTML-Template modularisieren      | 4h      | Architektur                |
| 20  | F11 — Jinja2-Logik in Python verlagern | 2h      | Trennung Logik/Darstellung |
| 21  | C1 — validate_anlagendaten aufteilen   | 2h      | Wartbarkeit                |
| 22  | C3 — FMEAStorage aufteilen             | 4h      | Architektur                |
| 23  | T2 — report_generator testen           | 4h      | Coverage                   |
| 24  | K1 — Review-Skill erstellen            | 4h      | Funktionalität             |
| 25  | D3/D4 — Fehlende Workflows erstellen   | 2h      | Dokumentation              |
| 26  | A1/A2 — Validierungs-Hooks             | 2h      | Automation                 |


### Phase 4: Polish (fortlaufend)


| #   | Item                                   | Aufwand | Impact        |
| --- | -------------------------------------- | ------- | ------------- |
| 27  | F7 — Excel-Legende hinzufügen          | 1h      | UX            |
| 28  | F9 — Chart-Auflösung (SVG statt PNG)   | 2h      | Schärfe       |
| 29  | F10 — Farbkontrast WCAG-konform        | 1h      | Accessibility |
| 30  | F12/F14 — Excel Spaltenbreiten + Zebra | 1h      | Lesbarkeit    |
| 31  | A3/A4 — Skill Auto-Bridges             | 2h      | UX            |
| 32  | K2 — Training erweitern                | 3h      | Qualität      |
| 33  | T7 — Eval in CI                        | 2h      | Automation    |
| 34  | I1 — GitHub Actions erweitern          | 2h      | DevOps        |
| 35  | T4/T5 — Weitere Tests                  | 4h      | Coverage      |


---

## Offene Fragen für Durchsicht

1. **API-Keys:** Sollen wir die Keys jetzt sofort rotieren oder erst beim nächsten Deployment?
2. **Storage-Refactoring (C3):** FMEAStorage aufteilen ist invasiv — lohnt sich das jetzt oder erst bei nächstem größeren Umbau?
3. **Review-Skill (K1):** Soll das ein separater Skill sein oder in `fmea-risikoanalyse` integriert?
4. **Skill-Pfade (D1/D2):** Embedded in `.claude/skills/*/references/` belassen oder nach `references/` global kopieren?
5. **Coverage-Ziel (T6):** 70% als Minimum realistisch? Oder erstmal 50% und schrittweise erhöhen?
6. **Template-Modularisierung (F6):** Lohnt sich das Aufteilen in Partials jetzt, oder erst wenn weitere Report-Varianten kommen?
7. **Design-System (F2):** Soll eine zentrale `config/colors.py` die Single Source of Truth werden, aus der CSS und Excel generiert werden?

