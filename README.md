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

## Status

**In aktiver Entwicklung** — Phase 1 (Fundament) abgeschlossen, Phase 2 (Analyse-Kern) in Arbeit.
