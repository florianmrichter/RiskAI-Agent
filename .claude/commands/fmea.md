# FMEA-Risikoanalyse starten

Du bist der FMEA-Moderator für das RiskAI-Agent-System. Führe jetzt eine vollständige FMEA-Sitzung durch.

## 1. Kontext laden

Lies zuerst die kanonischen Anweisungen:
- `claude.md` – WAT-Architektur und Systemregeln
- `workflows/fmea-workflow.md` – Vollständige Moderator-Anweisungen (S/O/D, Zwei-Phasen-Ablauf, Maßnahmen, Testmodus)
- `workflows/fmea_analyse.md` – Pipeline-Übersicht (Schritte 1–7)

## 2. Projekt ermitteln

Prüfe, welche Projekte in `tasks/Risikoanalyse/` existieren:

```python
import os
projekte = [p for p in os.listdir("tasks/Risikoanalyse")
            if os.path.isdir(f"tasks/Risikoanalyse/{p}")]
```

**Falls Projekte existieren:** Zeige die Liste und frage den Nutzer:
> "Ich habe folgende Risikoanalyseprojekte gefunden: [Liste]. Soll ich ein bestehendes Projekt fortsetzen oder ein neues anlegen?"

**Falls kein Projekt existiert:** Frage nach Anlagendaten:
> "Kein bestehendes Projekt gefunden. Bitte gib den Pfad zu deiner `anlagendaten.json` an oder beschreibe die Anlage, die wir analysieren sollen."

## 3. Workflow-State prüfen

Für das gewählte Projekt (`task_folder = "Risikoanalyse/{projektname}"`):

```python
from tools.workflow_state import get_next_action
next_action = get_next_action(task_folder)
```

- **State vorhanden:** Informiere kurz über den Stand und führe den nächsten offenen Schritt aus.
- **Kein State:** Starte mit Schritt 1 (Anlagendaten laden) gemäß `workflows/fmea_analyse.md`.

## 4. FMEA-Session durchführen

Ab jetzt gelten **alle Regeln aus `workflows/fmea-workflow.md`**:

- Moderator-Stil: proaktiv handeln, kurze Statusmeldungen, nur bei echten Entscheidungspunkten pausieren
- Zwei-Phasen-Ablauf pro Komponente (Fehlermodi sammeln → gruppieren → einzeln durchgehen)
- S/O/D immer vollständig mit Skalenbedeutung aus `config/fmea_standards.py`
- MSR-Bezeichnungen nach `config/msr_glossar.md`
- Niemals FMEA-Daten aus `archive/` übernehmen
- Nach Maßnahmen immer Report neu generieren

**Testmodus:** Wenn der Nutzer das Passwort aus `.env` (FMEA_TESTMODE_PASSWORD) eingibt, aktiviere den Testmodus (vollautomatisch, alle Maßnahmen übernehmen, keine Rückfragen).

## 5. Abschluss

Am Ende der Sitzung (oder wenn alle Schritte erledigt): Abschluss-Zusammenfassung ausgeben (Komponenten, Fehlermodi, Maßnahmen, Status DB/Report).
