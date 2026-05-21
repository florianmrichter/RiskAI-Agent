# Skill: fmea-risikoanalyse

Ein Claude Code Skill für vollständige FMEA-Risikoanalysen von Industrieanlagen — vom Session-Start bis zum fertigen HTML-Report.

## Was dieser Skill macht

- Strukturierte Moderation einer FMEA (Failure Mode and Effects Analysis)
- Fehlermodi sammeln, S/O/D bewerten, RPZ berechnen
- Maßnahmen definieren und einspielen
- HTML-Report generieren
- Zustand zwischen Sessions persistieren (Workflow-State)

## Voraussetzungen

- [Claude Code](https://claude.ai/code) installiert
- Python 3.9+
- PubChem MCP Server (optional, für Stoffdaten im Interview-Skill)

## Installation

### 1. Skill-Bundle herunterladen

Den gesamten Ordner `fmea-risikoanalyse/` in dein Projekt kopieren:

```
dein-projekt/
└── .claude/
    └── skills/
        └── fmea-risikoanalyse/    ← dieser Ordner
            ├── SKILL.md
            ├── README.md
            ├── references/
            ├── tools/
            ├── templates/
            └── config/
```

### 2. Dateien an die richtigen Stellen kopieren

Die Tools, Templates und Config müssen im Projekt-Root liegen, damit die Python-Importe funktionieren:

```bash
# Aus dem Skill-Bundle in den Projekt-Root kopieren
cp -r .claude/skills/fmea-risikoanalyse/tools/     ./tools/
cp -r .claude/skills/fmea-risikoanalyse/templates/ ./templates/
cp -r .claude/skills/fmea-risikoanalyse/config/    ./config/
```

### 3. Python-Abhängigkeiten installieren

```bash
pip install jinja2 weasyprint
```

### 4. Datenbankverzeichnis anlegen

```bash
mkdir -p data/
```

Die SQLite-Datenbank (`data/fmea.db`) wird beim ersten Start automatisch angelegt.

### 5. Umgebungsvariablen (optional)

Lege eine `.env`-Datei im Projekt-Root an:

```env
# Aktiviert den vollautomatischen Testmodus (kein Passwort = Testmodus deaktiviert)
FMEA_TESTMODE_PASSWORD=dein_passwort
```

### 6. Aufgaben-Verzeichnis anlegen

```bash
mkdir -p tasks/Risikoanalyse/
```

## Nutzung

Öffne Claude Code im Projekt-Root und starte eine FMEA:

```
Ich möchte eine FMEA für die Ethylacetatproduktion starten.
```

Claude lädt den Skill automatisch und führt dich durch die Analyse.

**Hinweis:** Für eine neue Anlage zuerst den `anlagendaten-interview`-Skill ausführen, um die `anlagendaten.json` zu erstellen.

## Dateistruktur nach der Installation

```
dein-projekt/
├── .claude/skills/fmea-risikoanalyse/   ← Skill (bleibt hier)
├── tools/                                ← Python-Tools
├── templates/                            ← HTML-Report-Template
├── config/                               ← FMEA-Standards, Glossar
├── data/                                 ← SQLite-Datenbank (gitignore!)
└── tasks/
    └── Risikoanalyse/
        └── MeineAnlage/
            ├── anlagendaten.json
            ├── fmea_explicit.json
            └── report.html
```

## Enthaltene Referenzdateien

| Datei | Inhalt |
|-------|--------|
| `workflows/fmea-workflow.md` | Moderator-Rolle, Ablauf, Phasen |
| `.claude/skills/fmea-risikoanalyse/references/fmea-standards.md` | S/O/D-Skalen, RPZ-Schwellen, Fehlermodi-Vorlagen |
| `config/msr_glossar.md` | MSR-Kennzeichen (TIC, PIC, LIC, PSV, ...) |
| `.claude/skills/fmea-risikoanalyse/references/sod-referenzkarte.md` | Kompakte S/O/D-Referenz für die Bewertung |
