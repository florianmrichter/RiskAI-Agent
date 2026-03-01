# RiskAI-Agent

KI-gestütztes Framework für automatisierte Risikoanalysen (FMEA) nach AIAG-VDA Standard.

## Überblick

RiskAI-Agent nutzt die **WAT-Architektur** (Workflows, Agents, Tools), um FMEA-Analysen für verfahrenstechnische Anlagen durchzuführen. Die Architektur trennt KI-Reasoning (Claude) von deterministischer Ausführung (Python-Tools), was Zuverlässigkeit und Reproduzierbarkeit sicherstellt.

## Architektur

```
Agent (Claude) — Orchestrierung + FMEA-Fachanalyse
    ├── Workflows (SOPs)  — Schritt-für-Schritt-Anleitungen
    └── Tools (Python)    — Laden, Berechnen, Speichern, Exportieren
                               └── Storage (SQLite + JSON)
```

## Pipeline

| Schritt | Typ | Beschreibung |
|---------|-----|--------------|
| 1. Anlagendaten laden | Tool | JSON/RTF → strukturiertes Anlagenobjekt |
| 2. Strukturanalyse | Tool | Zerlegung in Systeme, Equipment, MSR, Sicherheit |
| 3. Funktionsanalyse | Agent | Haupt-/Nebenfunktionen mit Anforderungen |
| 4. Fehleranalyse | Agent + Tool | Fehlermodi, Ursachen, Folgen, S/O/D-Bewertung |
| 5. RPZ-Berechnung | Tool | RPZ + Safety-Guard-Overrides |
| 6. Maßnahmenoptimierung | Agent | Maßnahmen nach ABE-Hierarchie |
| 7. Export | Tool | Excel/JSON/HTML-Report |

## Projektstruktur

```
RiskAI-Agent/
├── tools/           # Python-Skripte für deterministische Ausführung
├── workflows/       # Markdown-SOPs (Standard Operating Procedures)
├── config/          # FMEA-Standards und Bewertungsskalen
├── templates/       # HTML/CSS-Templates für Reports
├── plans/           # Architektur- und Strategiepläne
├── tasks/           # Aufgaben-spezifische Eingabedaten
├── .tmp/            # Temporäre Verarbeitungsdateien (gitignored)
└── requirements.txt # Python-Abhängigkeiten
```

## Setup

```bash
pip install -r requirements.txt
```

### Voraussetzungen

- Python 3.10+
- API-Schlüssel in `.env` (siehe `claude.md` für Details)

## Standards

- FMEA nach **AIAG-VDA** (harmonisierter Standard)
- 10-Punkte Bewertungsskalen für Severity, Occurrence, Detection
- Safety-Guard-System für automatische Risiko-Overrides
- ABE-Hierarchie für Maßnahmen (Abstellen → Begrenzen → Erkennen)

## Berichts-Features

- **Detaillierte Risiko-Cards** mit S/O/D-Bewertung, Ursachen, Folgen, Controls und Maßnahmen an einem Ort
- **Ausführliche Controls-Tabelle** mit Beschreibung und Wirkungsbereich statt reiner Pill-Badges
- **Maßnahmen-Checkliste** im Anhang zur systematischen Abarbeitung
- **Visualisierungen**: Donut-Chart, Risikomatrix, Treemap (vorher/nachher), RPZ-Vergleichs-Balkendiagramm
- **Review-Tool mit S/O/D-Skala-Kontext**: zeigt Nachbarwerte zur besseren Einschätzung
- **Treiber-Analyse**: erklärt welcher Faktor (S, O oder D) das Risiko dominiert und wie man ihn adressiert

## Tasks

- **Risikoanalyse**: Anlagendaten in `tasks/Risikoanalyse/anlagendaten.json`, FMEA-Config in `tasks/Risikoanalyse/` (JSON).

## Status

**In aktiver Entwicklung** — POC für Synthesereaktor R-101 erfolgreich abgeschlossen. Anlagendaten als JSON; Templates und Tools (Review, RPZ) aktualisiert.
