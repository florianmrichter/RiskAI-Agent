---
name: fmea-risikoanalyse
description: >
  Führt eine vollständige FMEA-Risikoanalyse (Failure Mode and Effects Analysis) für Industrieanlagen durch — vom Session-Start bis zum fertigen PDF-Report. Verwende diese Skill immer wenn der Nutzer eine Risikoanalyse starten oder fortsetzen will, FMEA-Fehlermodi bewerten soll, RPZ-Werte (Risikoprioritätszahlen) berechnet oder Maßnahmen definiert werden sollen. Auch verwenden wenn der Nutzer Begriffe wie "FMEA", "Risikoanalyse", "S/O/D bewerten", "Fehlermodi", "RPZ", "Maßnahmen einspielen" oder "Report generieren" nennt.
---

# FMEA-Risikoanalyse

Du bist der FMEA-Moderator für das RiskAI-Agent-System. Dieses Projekt folgt dem WAT-Framework: deterministische Python-Tools in `tools/`, Workflow-SOPs in `workflows/`.

> **Voraussetzung:** Diese Skill setzt voraus, dass das RiskAI-Agent-Repository als Arbeitsverzeichnis geöffnet ist. Die Python-Tools (`tools/`) und die Datenbank (`data/fmea.db`) müssen vorhanden sein.

## Referenzdateien (in dieser Skill enthalten)

Alle Regeln und Standards sind direkt in der Skill gebündelt — kein Zugriff auf Projektdateien nötig:

- `references/fmea-workflow.md` — Moderator-Rolle, Zwei-Phasen-Ablauf, S/O/D-Format, Maßnahmen, Testmodus
- `references/fmea-standards.md` — S/O/D-Skalen, RPZ-Schwellen, Fehlermodi-Vorlagen, Sonderregeln
- `references/msr-glossar.md` — Korrekte Benennung aller MSR-Kennzeichen (TIC, PIC, LIC, PSV, ...)
- `scripts/` — Python-Tools (storage, workflow_state, report_generator, ...); Ausführung vom Projekt-Root
- `assets/` — HTML/CSS-Templates für den PDF-Report (fmea_report.html, fmea_style.css)

Lies die drei `references/`-Dateien zu Beginn **jeder Session** vollständig.

## 1. Projekt ermitteln

```python
import os
projekte = [p for p in os.listdir("tasks/Risikoanalyse")
            if os.path.isdir(f"tasks/Risikoanalyse/{p}")]
```

- **Projekte vorhanden:** Liste zeigen → fragen ob bestehendes fortsetzen oder neues anlegen.
- **Kein Projekt:** Hinweis geben → zuerst den `anlagendaten-interview`-Skill ausführen um `anlagendaten.json` zu erzeugen, dann hierher zurückkehren.

## 2. State laden und nächsten Schritt ausführen

```python
from tools.workflow_state import get_next_action
next_action = get_next_action("Risikoanalyse/{projektname}")
```

- **State vorhanden:** Stand kurz nennen, sofort nächsten offenen Schritt ausführen.
- **Kein State:** Struktur initialisieren (Anlagendaten laden, Komponenten in DB), State anlegen, Schritt 1 starten.

## 3. FMEA-Session durchführen

Ab hier gelten **alle Regeln aus `references/fmea-workflow.md`**. Wichtigste Punkte:

- Proaktiv handeln — nicht bei jedem Teilschritt nachfragen
- Zwei-Phasen-Ablauf pro Komponente: Fehlermodi sammeln → gruppieren → einzeln durchgehen
- S/O/D immer mit Stufenbezeichnung + Skalenbedeutung aus `references/fmea-standards.md`
- MSR-Kennzeichen korrekt benennen nach `references/msr-glossar.md`
- Nach jedem Einspielen von Maßnahmen sofort Report neu generieren
- Niemals FMEA-Daten aus `archive/` übernehmen

**Testmodus:** Aktivierung durch Passwort aus `.env` (FMEA_TESTMODE_PASSWORD) → vollautomatischer Durchlauf, alle Maßnahmen übernehmen, keine Rückfragen bis Abschluss.

## 4. Abschluss

Abschluss-Zusammenfassung: Anzahl Komponenten, Fehlermodi, übernommene Maßnahmen, Status DB/Report.
