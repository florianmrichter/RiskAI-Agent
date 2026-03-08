# Skill: anlagendaten-interview

Ein Claude Code Skill für das strukturierte Erheben von Anlagendaten als Vorbereitung einer FMEA-Risikoanalyse.

## Was dieser Skill macht

- Strukturiertes 7-Phasen-Interview mit dem Anlagenbetreiber
- Automatisches Abrufen von Stoffdaten aus PubChem (Flammpunkt, GHS, H-Sätze, ...)
- Erzeugt eine vollständige `anlagendaten.json` nach festgelegtem Schema
- Bereitet alles für den `fmea-risikoanalyse`-Skill vor

## Voraussetzungen

- [Claude Code](https://claude.ai/code) installiert
- PubChem MCP Server (empfohlen, für automatische Stoffdaten)

## Installation

### 1. Skill-Bundle herunterladen

Den gesamten Ordner `anlagendaten-interview/` in dein Projekt kopieren:

```
dein-projekt/
└── .claude/
    └── skills/
        └── anlagendaten-interview/    ← dieser Ordner
            ├── SKILL.md
            ├── README.md
            └── references/
                ├── interview-phasen.md
                └── anlagendaten-schema.json
```

Dieser Skill benötigt **keine Python-Tools** — Claude führt das Interview direkt durch und schreibt die JSON-Datei.

### 2. Aufgaben-Verzeichnis anlegen

```bash
mkdir -p tasks/Risikoanalyse/
```

## Nutzung

Öffne Claude Code im Projekt-Root und starte das Interview:

```
Ich möchte eine neue Anlage erfassen. Starte das Anlagendaten-Interview.
```

Am Ende des Interviews wird automatisch gespeichert unter:
```
tasks/Risikoanalyse/{AnlagenName}/anlagendaten.json
```

Danach kannst du mit dem `fmea-risikoanalyse`-Skill die eigentliche Analyse starten.

## Interview-Phasen

| Phase | Inhalt |
|-------|--------|
| 1 | Grunddaten: Teilanlagen-Nr., Bezeichnung, Standort |
| 2 | Prozessbeschreibung: Zweck, Betriebsweise, Rahmenbedingungen |
| 3 | Stoffe: Edukte, Produkte, Hilfs-/Betriebsstoffe + Sicherheitsdaten |
| 4 | Systeme: Equipment, MSR, Sicherheitseinrichtungen, Verbindungen |
| 5 | Medien: Dampf, Kühlwasser, Stickstoff, Druckluft, Strom |
| 6 | Leitsystem & Sicherheitssystem: DCS, SIS, Gaswarnung |
| 7 | Systemgrenzen: Was ist explizit nicht im Scope? |

## Enthaltene Referenzdateien

| Datei | Inhalt |
|-------|--------|
| `references/interview-phasen.md` | Vollständige Fragenliste für alle 7 Phasen |
| `references/anlagendaten-schema.json` | JSON-Schema mit Beispiel (Ethylacetatproduktion) |
