# Tool-Index

Übersicht aller Python-Tools mit Zweck, Status und verwendenden Workflows.

## Alle Tools

| Tool | Zweck | Status | Workflows |
|------|-------|--------|-----------|
| storage.py | SQLite CRUD, Projekte, Komponenten, FMEA | aktiv | alle |
| load_plant_data.py | Anlagendaten JSON/RTF laden | aktiv | fmea_analyse |
| structure_analysis.py | Komponenten zerlegen, IDs vergeben | aktiv | fmea_analyse |
| init_fmea_fresh.py | Kompletter Neustart (Struktur + State) | aktiv | - |
| insert_fmea_explicit.py | FMEA aus fmea_explicit in DB | aktiv | fmea_analyse |
| fmea_loader.py | Lädt fmea_explicit/measures_explicit | aktiv | insert_fmea, generate_measures |
| insert_measures.py | Maßnahmen pro Fehlermodus einfügen | aktiv | massnahmen |
| generate_measures.py | Maßnahmen aus measures_explicit | aktiv | massnahmen |
| rpz_calculator.py | RPZ + Safety-Guard | aktiv | fmea_analyse |
| report_generator.py | PDF-Report mit Charts | aktiv | fmea_analyse |
| review.py | Human-in-the-Loop Zusammenfassungen | aktiv | fmea_analyse, validierung |
| workflow_state.py | State, get_next_action | aktiv | fmea_analyse |
| update_checklist.py | checklist.md aus DB | aktiv | - |
| failure_templates.py | Fehlervorlagen pro Komponententyp | aktiv | fehleranalyse |
| reliability_lookup.py | O-Wert-Vorschläge | aktiv | fehleranalyse |
| chart_comparison.py | RPZ-Vergleichs-Chart | aktiv | report_generator |
| export.py | Excel/JSON-Export | aktiv | - |
| clear_fmea_for_project.py | FMEA eines Projekts zurücksetzen | aktiv | - |
| cleanup_generic_data.py | KOMP-002 bis KOMP-047 löschen | einmalig | - |
| run_full_fmea.py | Vollständige Pipeline (ohne Agent) | aktiv | - |
| update_fmea_report_fields.py | kontext_beschreibung etc. aus Config | aktiv | - |
| observability.py | Dashboard-Metriken + Quality Report | aktiv | - |

## Status

- **aktiv** – im Standard-Workflow oder manuell genutzt
- **einmalig** – für spezielle Aufräum-Aktionen (z. B. cleanup_generic_data)

## Siehe auch

- [workflows/README.md](../workflows/README.md) – welche Workflows welche Tools aufrufen
