# Config-Struktur

Zentrale Konfiguration und Vorlagen für FMEA-Analysen.

## Dateien

| Datei | Zweck |
|-------|--------|
| **fmea_standards.py** | FEHLERMODI_VORLAGEN (Katalog nach Kategorien), Bewertungsskalen S/O/D, STOP-Labels. Wird vom Agent als Checkliste für Fehlertypen pro Komponente genutzt. |
| **measures_explicit.py** | Fallback-Template (liefert leere Liste). Projektspezifische Maßnahmen liegen in `tasks/{task_folder}/measures_explicit.py` – dort definiert der Agent oder ein Generator `get_measures_for_fehlermodus`. |
| **fmea_explicit.py** | Fallback-Template (liefert leeres Dict). Projektspezifische FMEA-Daten liegen in `tasks/{task_folder}/fmea_explicit.py` – dort schreibt der Agent seine Analyse (Funktionen, Fehlermodi, S/O/D). |
| **reliability_data.json** | Zuverlässigkeitsdaten für O-Bewertung (Ausfallraten, Equipment-Kategorien). Wird von `tools/reliability_lookup.py` geladen. |
| **msr_glossar.md** | MSR-Begriffe und Erklärungen. |
| **wissen/** | Domain-Wissen aus Kontext-Recherchen (z. B. verfahrenstechnik_esterifizierung.md). Ergänzung zu Anlagendaten, keine primäre Quelle. |

## tasks vs. config

- **Projektdaten** (FMEA-Definitionen, Maßnahmen pro Fehlermodus) gehören in `tasks/Risikoanalyse/{projekt}/` (fmea_explicit.py, measures_explicit.py).
- **Config** enthält nur globale Standards und leere Fallbacks; `tools/fmea_loader.py` lädt zuerst aus dem task_folder, bei Bedarf aus config.

## Siehe auch

- [tasks/Risikoanalyse/README.md](../tasks/Risikoanalyse/README.md) – Struktur der Projektordner
- [tools/README.md](../tools/README.md) – fmea_loader, generate_measures
