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
| 6. Maßnahmenoptimierung | Agent | Maßnahmen nach STOP-Prinzip + ABE-Hierarchie |
| 7. Export | Tool | Excel/JSON/HTML-Report |

## Projektstruktur

```
RiskAI-Agent/
├── tools/           # Python-Skripte für deterministische Ausführung
├── workflows/       # Markdown-SOPs (Standard Operating Procedures)
├── config/          # FMEA-Standards, Zuverlässigkeitsdaten
├── templates/       # HTML/CSS-Templates für Reports
├── plans/           # Architektur- und Strategiepläne
├── tasks/           # Aufgaben-spezifische Eingabedaten
├── data/            # SQLite-Datenbank fmea.db (gitignored)
├── archive/         # Archivierte Analyse-Läufe
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
- ABE-Hierarchie für Maßnahmen (Vermeidung → Entdeckung → Abschwächung)
- STOP-Prinzip (Substitution → Technisch → Organisatorisch → Persönlich)

## Berichts-Features

- **Detaillierte Risiko-Cards** mit S/O/D-Bewertung, Ursachen, Folgen, Controls und Maßnahmen an einem Ort
- **Ausführliche Controls-Tabelle** mit Beschreibung und Wirkungsbereich statt reiner Pill-Badges
- **Maßnahmen-Checkliste** im Anhang zur systematischen Abarbeitung
- **Visualisierungen**: Donut-Chart, Risikomatrix, Treemap (vorher/nachher), RPZ-Vergleich, 6-Chart-Typen-Vergleich
- **Review-Tool mit S/O/D-Skala-Kontext**: zeigt Nachbarwerte zur besseren Einschätzung
- **Treiber-Analyse**: erklärt welcher Faktor (S, O oder D) das Risiko dominiert und wie man ihn adressiert

## Ablauf des Programms

### Einstieg (drei Varianten)

| Situation | Aktion |
|-----------|--------|
| **Kompletter Neustart** (DB löschen, leere Configs) | `python tools/init_fmea_fresh.py --reset --task-folder Risikoanalyse/Ethylacetatproduktion_20TA41` |
| **Neues Projekt** (DB existiert noch nicht, Task-Ordner neu) | `python tools/init_fmea_fresh.py --task-folder Risikoanalyse/NeuesProjekt` |
| **FMEA zurücksetzen** (nur ein Projekt, DB bleibt) | `python tools/clear_fmea_for_project.py Risikoanalyse/Ethylacetatproduktion_20TA42 --reset-files` |
| **Fortsetzen** (workflow_state.json vorhanden) | Agent startet, liest State, ermittelt nächste Aktion mit `get_next_action("Risikoanalyse/Ethylacetatproduktion_20TA41")` |

### Phasen-Reihenfolge

```
struktur → fmea → rpz_validierung → massnahmen → report
```

---

### Phase 1: Struktur

**Ziel:** Anlagendaten laden, Komponenten erkennen, Projekt in DB anlegen.

| Schritt | Tool/Aktion | Output |
|---------|-------------|--------|
| 1 | `load_plant_data(json_path)` | Anlagenobjekt |
| 2 | `analyze_structure(plant_data)` | Komponentenliste |
| 3 | `create_project()` + `save_components_to_db()` | Projekt + Komponenten in DB |
| 4 | `init_state_from_structure(task_folder, project_id, komp_ids)` | workflow_state.json |

**Oder alles auf einmal:** `init_fmea_fresh.py` führt Schritte 1–4 aus.

**Dateien:** `tasks/{task_folder}/anlagendaten.json` (Input), `data/fmea.db` (DB), `tasks/{task_folder}/workflow_state.json`

---

### Phase 2: FMEA (Funktionen + Fehlermodi)

**Ziel:** Pro Komponente Funktionen und Fehlermodi analysieren, in DB einspielen.

| Schritt | Wer | Aktion |
|---------|-----|--------|
| 1 | Agent | Liest `workflows/fmea_analyse.md`, `workflows/funktionsanalyse.md`, `workflows/fehleranalyse.md` |
| 2 | Agent | Analysiert Komponente (Name, Typ, Kontext aus DB). Nutzt `config.fmea_standards.FEHLERMODI_VORLAGEN` als Checkliste für relevante Fehlertypen pro Kategorie (prozess, thermisch, mechanisch, equipment, msr, sicherheit, dosierung, sonstiges). |
| 3 | Agent | Schreibt Definition in `tasks/{task_folder}/fmea_explicit.py` (Funktionen + Fehlermodi mit S/O/D) |
| 4 | Tool | `insert_fmea_for_component(project_id, komp_id, task_folder)` liest aus fmea_explicit und schreibt in DB |
| 5 | Agent | Ruft `mark_component_done(task_folder, komp_id, "fmea")` auf |

**Nächste Komponente:** `get_next_action()` liefert `{"action": "analyze_fmea", "komp_id": "..."}`.

**Wichtig:** fmea_explicit.py ist **Output** – der Agent füllt sie bei jeder Analyse. Bei Neustart mit `--reset` wird sie geleert.

**Archiv-Regel:** Jede Risikoanalyse ist NEU. NIEMALS FMEA-Daten aus `archive/` oder anderen Projekten übernehmen. Einzige Quelle: `anlagendaten.json` des aktuellen Projekts.

---

### Phase 3: RPZ-Validierung

**Ziel:** RPZ berechnen, Safety-Guard-Overrides anwenden, Risiko-Ranking prüfen.

| Schritt | Tool | Aktion |
|---------|------|--------|
| 1 | `rpz_calculator.calculate_and_store_rpz(project_id)` | RPZ = S × O × D für alle Fehlermodi, speichert in DB |
| 2 | Agent | Zeigt Risiko-Ranking, Nutzer bestätigt oder passt S/O/D an |
| 3 | Agent | Ruft `mark_phase_done(task_folder, "rpz_validierung")` auf |

---

### Phase 4: Maßnahmen

**Ziel:** Für Fehlermodi mit RPZ ≥ 100 (oder Status hoch/kritisch) Maßnahmen definieren und in DB speichern.

**Zwei Wege – je nachdem, ob ein Generator existiert:**

| Variante | Wann | Wer | Aktion |
|----------|------|-----|--------|
| **A: Generator** | `tasks/{task_folder}/measures_explicit.py` oder `config/measures_explicit.py` hat `get_measures_for_fehlermodus` und liefert Maßnahmen für den Fehlermodus | Tool | `python tools/generate_measures.py --project-id 1` lädt das Modul, ruft für jeden Fehlermodus `get_measures_for_fehlermodus(fehler_id, fehlermodus, komponente)` auf, spielt über `insert_measures_for_fehlermodus` ein |
| **B: Agent** | Kein Generator für den Fehlermodus (Modul liefert `[]`) | Agent | Analysiert Fehlermodus (STOP-Prinzip, ABE-Hierarchie), erstellt Maßnahmen-Liste, ruft `insert_measures_for_fehlermodus(project_id, fehler_id, measures)` auf |

**Typischer Ablauf:** Zuerst `generate_measures.py` ausführen. Fehlermodi ohne Generator werden ausgegeben – der Agent analysiert diese und ruft `insert_measures_for_fehlermodus` auf.

**Dateien:** `tasks/{task_folder}/measures_explicit.py` (projektspezifisch, optional) oder `config/measures_explicit.py` (Fallback)

---

### Phase 5: Report

**Ziel:** PDF-Bericht generieren.

| Schritt | Tool | Output |
|---------|------|--------|
| 1 | `report_generator.generate_report(project_id, ...)` | PDF in `tasks/{task_folder}/` |

---

### Übersicht: Wichtige Dateien

| Datei | Rolle |
|-------|-------|
| `tasks/{task_folder}/anlagendaten.json` | Input: Anlagendaten |
| `tasks/{task_folder}/fmea_explicit.py` | Agent-Output: FMEA-Definitionen pro Komponente (wird von insert_fmea gelesen) |
| `tasks/{task_folder}/measures_explicit.py` | Optional: `get_measures_for_fehlermodus` für Maßnahmen-Generatoren (projektspezifisch) |
| `tasks/{task_folder}/workflow_state.json` | Fortschritt: Phasen, Komponenten-Status |
| `tasks/{task_folder}/checklist.md` | Menschenlesbare Übersicht (wird aus DB generiert) |
| `data/fmea.db` | SQLite: Projekte, Komponenten, Funktionen, Fehlermodi, Maßnahmen |

---

### Workflow-Automatisierung

- **Session-Start:** Agent prüft `workflow_state.json`, ruft `get_next_action(task_folder)` aus `tools/workflow_state.py` auf
- **Nächste Aktion:** `init_structure` \| `analyze_fmea` \| `rpz_validierung` \| `apply_measures` \| `generate_report`
- **Maßnahmen aus measures_explicit anwenden:** `python tools/apply_explicit_measures.py` (projektabhängig)
- **Checklist aktualisieren:** `python tools/update_checklist.py Risikoanalyse/Ethylacetatproduktion_20TA41`

## Tasks

```
tasks/
├── Risikoanalyse/                    # FMEA-basierte Risikoanalyse
│   ├── Ethylacetatproduktion_20TA41/ # Ethylacetat-Anlage
│   ├── Ethylacetatproduktion_20TA42/ # Ethylacetat-Anlage (Variante)
│   ├── Destillationskolonne_XY/       # (bei Bedarf anlegen)
│   └── Schwefelsaureherstellung/     # (bei Bedarf anlegen)
└── Compliance/                        # (anderer Aufgabentyp)
    └── Anlage_ABC/
```

Jeder Projektordner enthält: `anlagendaten.json`, `fmea_explicit.py`, `measures_explicit.py`, `workflow_state.json`, `checklist.md`, ggf. Report-PDF. Siehe `tasks/Risikoanalyse/README.md`.

## Status

**In aktiver Entwicklung** — **Frische Bewertung pro Analyse:** Agent analysiert jede Komponente neu, schreibt in `fmea_explicit.py`, Einspielung mit `tools/insert_fmea_explicit.py`. Maßnahmen: `tools/generate_measures.py` nutzt projektspezifische Generatoren aus `tasks/{task_folder}/measures_explicit.py` (oder `config/measures_explicit.py`); Fehlermodi ohne Generator werden vom Agent über `insert_measures_for_fehlermodus` eingespielt.
