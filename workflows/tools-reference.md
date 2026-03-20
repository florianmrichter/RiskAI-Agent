# Tools Reference

Quick reference for all Python tools in `tools/`.

| Datei | Zweck | Kernfunktionen | Ext. Abhängigkeiten |
|---|---|---|---|
| `_base.py` | Zentrale Infrastruktur (Logging, Config-Laden) | `get_logger`, `tool_entry`, `load_json_config` | - |
| `calibration.py` | Plausibilitätsprüfung und Kalibrierungsregeln | `load_calibration_rules`, `check_plausibility`, `apply_calibration`, `generate_rules` | - |
| `chart_comparison.py` | Vergleichsbilder (6 Chart-Typen) generieren | `generate_comparison` | matplotlib, numpy |
| `cleanup_generic_data.py` | Generische FMEA-Daten entfernen (KOMP-002+) | `cleanup_generic_data` | - |
| `clear_fmea_for_project.py` | Alle FMEA-Daten eines Projekts löschen | `clear_fmea_for_project`, `reset_fmea_explicit`, `reset_workflow_state_fmea` | - |
| `export.py` | FMEA-Daten als Excel/JSON exportieren | `export_json`, `export_excel`, `export_fmea` | openpyxl |
| `failure_templates.py` | Fehlermodi-Katalog pro Komponententyp | `get_templates`, `get_templates_for_component`, `format_templates_for_prompt` | - |
| `fmea_loader.py` | FMEA-/Massnahmen-Config dynamisch aus Task-Ordner laden | `get_fmea_for_component`, `load_measures_module` | importlib |
| `generate_measures.py` | Massnahmen-Generierung fuer FMs mit RPZ >= 100 | `run_generate_measures` | - |
| `init_fmea_fresh.py` | Kompletter FMEA-Neustart (DB + State) | `main` | - |
| `insert_fmea_explicit.py` | Explizite FMEA-Daten (Funktionen, FMs, S/O/D) einfuegen | `insert_fmea_for_component` | - |
| `insert_measures.py` | Agent-generierte Massnahmen in DB einfuegen | `insert_measures_for_fehlermodus` | - |
| `load_plant_data.py` | Anlagendaten aus JSON/n8n laden und validieren | `load_plant_data`, `validate_plant_data`, `get_plant_summary` | - |
| `migrate_db.py` | Datenbank-Migrationen ausfuehren | `run_migrations` | - |
| `moc_manager.py` | Management of Change: Versionierung, Freeze, Delta | `freeze_version`, `create_new_version`, `get_version_history`, `get_delta` | - |
| `observability.py` | Projektuebergreifende Auswertungen und KI-Performance | `get_project_overview`, `get_correction_patterns`, `get_full_dashboard` | - |
| `reliability_lookup.py` | CCPS/OREDA-Ausfallraten abfragen | `get_o_suggestion`, `suggest_for_component`, `list_equipment_types` | - |
| `report_generator.py` | HTML/CSS-Report generieren (PDF via WeasyPrint) | `generate_report` | jinja2, matplotlib, numpy, playwright |
| `review.py` | Human-in-the-Loop Review-Support | `get_plant_data_review`, `get_risk_review`, `get_measure_review`, `get_full_review` | - |
| `rpz_calculator.py` | RPZ berechnen + Safety-Guard-Overrides anwenden | `calculate_rpz`, `check_safety_overrides`, `calculate_and_store_rpz` | - |
| `run_full_fmea.py` | Automatisierte FMEA-Pipeline (alle Schritte) | `step1_load_and_structure`, `step3_funktionsanalyse`, `step4_fehleranalyse`, `step6_massnahmen` | - |
| `storage.py` | SQLite-CRUD fuer alle 9 FMEA-Entitaeten | `create_project`, `insert_component`, `insert_failure_mode`, `insert_measure`, `get_full_fmea_data` | - |
| `storage_migrations.py` | Schema-Migrationen fuer die FMEA-DB | `run_all` | - |
| `structure_analysis.py` | Anlagendaten in Einzelkomponenten zerlegen | `analyze_structure`, `save_components_to_db` | - |
| `update_checklist.py` | Checklist.md aus DB generieren | `update_checklist` | - |
| `update_fmea_report_fields.py` | Kontext/Controls/Hinweis in DB aktualisieren | `update_report_fields` | - |
| `validate_anlagendaten.py` | Gate 1: anlagendaten.json vor FMEA validieren | `validate_anlagendaten`, `format_report` | - |
| `validate_completeness.py` | Gate 2: FMEA-Vollstaendigkeit vor Report pruefen | `validate_completeness`, `format_report` | - |
| `workflow_state.py` | Workflow-State persistieren und naechsten Schritt ermitteln | `get_next_action`, `mark_component_done`, `get_autonomy_mode`, `set_autonomy_mode` | - |
