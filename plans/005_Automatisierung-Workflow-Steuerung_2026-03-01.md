# Plan: Automatisierung und Workflow-Steuerung

**Datum:** 2026-03-01  
**Status:** Ausgearbeitet – bereit für Implementierung  
**Auslöser:** Nutzer möchte nicht jedes Mal von Neuem anstoßen müssen; der Agent soll den Workflow selbstständig vorgeben.

---

## Ziel

Ein **Automatismus** einbauen, sodass der Agent:
- den FMEA-Workflow **proaktiv** und **selbstgesteuert** durchläuft
- den Nutzer nicht bei jedem Schritt neu anstoßen muss
- klar kommuniziert, wo er steht und was als Nächstes kommt

---

## Kernanforderung

> „Ich möchte nicht jedes Mal von Neuem anstoßen müssen, sondern du gibst ganz klar den Workflow vor.“

---

## Gewählter Ansatz: Kombination (State + Checkliste + Cursor Rule)

Die drei Elemente ergänzen sich:

| Element | Zweck |
|--------|-------|
| **workflow_state.json** | Maschinenlesbarer Zustand für Tools und Skripte |
| **checklist.md** | Menschenlesbare Fortschrittsanzeige, Git-freundlich |
| **Cursor Rule** | Agent-Verhalten bei Session-Start und während der Arbeit |

---

## 1. Workflow-State-Machine

### Datei: `tasks/{task_folder}/workflow_state.json`

```json
{
  "project_id": 1,
  "task_folder": "Risikoanalyse",
  "phase": "fehleranalyse",
  "current_komp_id": "KOMP-018",
  "last_updated": "2026-03-01T14:30:00",
  "phases": {
    "struktur": "done",
    "funktionsanalyse": "done",
    "fehleranalyse": "in_progress",
    "rpz_validierung": "pending",
    "massnahmen": "pending",
    "report": "pending"
  },
  "components": {
    "KOMP-002": {"fmea": "done", "measures": "done"},
    "KOMP-017": {"fmea": "done", "measures": "pending"},
    "KOMP-018": {"fmea": "in_progress", "measures": "pending"}
  }
}
```

### Phasen-Logik

1. **struktur** – Anlagendaten laden, Komponenten in DB (einmalig)
2. **funktionsanalyse** – Pro Komponente: Definition in fmea_explicit.py → insert
3. **fehleranalyse** – Pro Komponente: Fehlermodi in fmea_explicit.py → insert
4. **rpz_validierung** – RPZ berechnen, Validierung, Review
5. **massnahmen** – Pro Fehlermodus RPZ≥100: Agent bewertet RPZ, schlägt Maßnahmen vor → `insert_measures_for_fehlermodus` (kein Lesen aus Config)
6. **report** – PDF generieren

**Frische Bewertung:** Bei jeder Risikoanalyse werden Risiken neu bewertet. Keine Wiederverwendung vordefinierter Analysen aus früheren Läufen. `fmea_explicit` und `measures_explicit` sind **Output** (Dokumentation), keine **Input-Bibliothek**.

### Tool: `tools/workflow_state.py`

- `load_state(task_folder)` → dict
- `save_state(task_folder, state)` → void
- `get_next_action(task_folder)` → `{"action": "analyze_fmea", "komp_id": "KOMP-018", "phase": "fehleranalyse"}`
- `mark_component_done(task_folder, komp_id, step)` → void

---

## 2. Checkliste (checklist.md)

### Datei: `tasks/{task_folder}/checklist.md`

**Entscheidung: Option B – automatisch generieren**

Ein Tool `tools/update_checklist.py` liest DB + Config und schreibt die aktuelle `checklist.md`. So bleibt die Übersicht immer aktuell ohne manuelle Pflege.

```markdown
# FMEA-Fortschritt: Ethylacetat 20TA41

| KOMP-ID | Name | Funktionen | Fehlermodi | Maßnahmen |
|---------|------|------------|------------|-----------|
| KOMP-002 | HM-101 | ✓ | ✓ | ✓ |
| KOMP-017 | PSV-410 | ✓ | ✓ | offen |
| KOMP-018 | TI-401 | ✓ | offen | - |
```

- **Input:** Nur DB (components, functions, failure_modes, measures) – kein Abgleich mit Config
- **Output:** Aktualisierte checklist.md
- Agent kann sie lesen und dem Nutzer zeigen: „17 von 47 Komponenten fertig, nächste: KOMP-018“

---

## 3. Cursor Rule (Agent-Anweisung)

### Datei: `.cursor/rules/fmea-workflow.md` (neu)

**Erster Start:** Wenn `workflow_state.json` nicht existiert → Agent initialisiert automatisch: Struktur laden (Schritt 1+2), State anlegen, dann mit nächstem Schritt fortfahren.

```markdown
# FMEA-Workflow-Automatismus

Bei Session-Start:
1. Prüfe ob `tasks/{task_folder}/workflow_state.json` existiert
2. Falls nein: Struktur initialisieren (Anlagendaten laden, Komponenten in DB), State anlegen, dann weiter
3. Falls ja: Lade State, ermittle nächsten offenen Schritt
4. Gib dem Nutzer eine klare Statusmeldung:
   "FMEA Ethylacetat: Phase [fehleranalyse], nächste Komponente KOMP-018 (TI-401).
    Soll ich die Einzelfall-Analyse für KOMP-018 durchführen?"
5. Führe den Schritt aus, sobald der Nutzer zustimmt (oder "ja" / "weiter" sagt)
6. Speichere den aktualisierten State nach jedem abgeschlossenen Schritt

Review-Punkte (Hybrid-Ansatz):
- Erste Komponente / explizite Anfrage: Zeige Zusammenfassung, warte auf "ok" oder "einspielen"
- Bei "weiter" oder "mach die nächsten 3": Automatisch einspielen ohne vorherige Anzeige
- Nach RPZ-Validierung: Zeige Ranking, warte auf Freigabe vor Maßnahmenphase
```

---

## 4. Review-Punkte (konkret)

**Entscheidung: Hybrid-Ansatz**

| Schritt | Review-Inhalt | Aktion bei Freigabe |
|--------|--------------|---------------------|
| Nach Struktur | Komponentenliste | `save_components_to_db` bereits erfolgt, Nutzer bestätigt Zuordnung |
| Pro Komponente FMEA (neu) | Funktionen + Fehlermodi | Agent zeigt Definition, Nutzer sagt "einspielen" → `insert_fmea_explicit` |
| Pro Komponente FMEA (weiter) | – | Nutzer sagt "weiter" oder "mach die nächsten 3" → Agent spielt automatisch ein, ohne vorher jede Definition zu zeigen |
| Nach RPZ | Risiko-Ranking | Nutzer bestätigt → Phase massnahmen freigeben |
| Pro Fehlermodus Maßnahme (neu) | Vorher/Nachher | Agent zeigt Maßnahme, Nutzer sagt "übernehmen" → `apply_explicit_measures` |
| Pro Fehlermodus Maßnahme (weiter) | – | Bei "weiter" automatisch einspielen |
| Report | PDF fertig | Kein Review, nur Info |

**Logik:** Bei der **ersten** Komponente einer Session oder bei expliziter Anfrage „zeig mir die Analyse“ → Review. Bei „weiter“ oder „mach die nächsten 3“ → automatisch einspielen.

---

## 5. Batch vs. Einzeln

**Empfehlung: 1 Komponente pro Agent-Lauf**

- Grund: Kontext-Management – 47 Komponenten auf einmal überlasten den Agent
- Ausnahme: Nutzer kann explizit sagen „mach die nächsten 3“ – dann max. 3 Komponenten
- Skript `run_full_fmea_explicit.py` kann im Hintergrund laufen, stoppt aber bei jedem Review-Punkt und wartet auf Input (z.B. leere Datei `tasks/Risikoanalyse/REVIEW_OK` als Signal)

---

## 6. Fehlerbehandlung

| Szenario | Verhalten |
|----------|-----------|
| Abbruch durch Nutzer | State bleibt stehen, nächster Start: gleicher Schritt |
| Tool wirft Fehler | State nicht ändern, Fehlermeldung zeigen, Nutzer entscheidet (wiederholen/skip/manuell) |
| Teilstand (z.B. 5 von 7 Fehlermodi eingespielt) | DB ist konsistent pro Komponente; State zeigt "in_progress", Agent macht bei KOMP-X weiter |
| State-Datei korrupt | Fallback: checklist.md lesen oder DB abfragen (components ohne functions = offen) |

---

## 7. Priorisierung der Komponenten

**Reihenfolge:** Wie in `structure_analysis` – Systeme zuerst, dann Equipment, MSR, Sicherheit.

- Begründung: Prozessfluss und Abhängigkeiten (z.B. Reaktor vor Kondensator)
- Alternative „nach Risiko“ erst sinnvoll nach Fehleranalyse – kann in Phase 2 ergänzt werden

---

## 8. Dokumentation des Fortschritts

| Ort | Inhalt |
|-----|--------|
| `checklist.md` | Komponenten-Fortschritt, pro Task-Ordner |
| `workflow_state.json` | Vollständiger State für Tools |
| README.md | Kurzer Hinweis: „FMEA-Fortschritt: siehe tasks/Risikoanalyse/checklist.md“ |
| Report (PDF) | Endstand nach Abschluss |

---

## 9. Integration mit n8n (optional, später)

- n8n kann `workflow_state.json` lesen und z.B. per Webhook den Agent triggern
- Oder: Agent läuft in Cursor, n8n nur für Report-Upload (Google Drive etc.)
- Keine Änderung am State-Konzept nötig

---

## 10. Benachrichtigungen

**Phase 1:** Keine Push-Benachrichtigungen. Agent zeigt Status bei Session-Start.

**Phase 2 (optional):** Wenn gewünscht – z.B. E-Mail oder Slack bei „KOMP-020 fertig, bereit für Review“ – über separates Tool.

---

## 11. Multi-Projekt-Fähigkeit (FMEA-Definitionen)

**Auslöser:** Bei einer zweiten Anlage blockieren die globalen Config-Dateien die Analyse, da sie weiterhin Anlage 1 enthalten.

### Ausgangslage

- [config/fmea_explicit.py](config/fmea_explicit.py) – 47 Komponenten Ethylacetat
- [config/measures_explicit.py](config/measures_explicit.py) – Maßnahmen für KOMP-002 bis KOMP-047

### Gewählter Ansatz: Projektbezogene Ordner (Ansatz 3)

Jede Anlage hat eigenen Task-Ordner mit eigenen Config-Dateien und eigenem `workflow_state.json`.

**Zielstruktur:**
```
tasks/
├── Risikoanalyse/                    # Ethylacetat 20TA41
│   ├── anlagendaten.json
│   ├── fmea_explicit.py              # aus config/ verschoben
│   ├── measures_explicit.py
│   ├── workflow_state.json
│   └── checklist.md
├── Anlage_B/
│   ├── anlagendaten.json
│   ├── fmea_explicit.py
│   ├── measures_explicit.py
│   ├── workflow_state.json
│   └── checklist.md
```

**Änderungen:**
- `config/fmea_explicit.py` → `tasks/Risikoanalyse/fmea_explicit.py` (analog measures)
- Tabelle `projects` um `task_folder` erweitern
- `insert_fmea_explicit` und `apply_explicit_measures` erhalten Parameter `task_folder`; dynamischer Import aus `tasks/{task_folder}/`
- `workflow_state.json` und `checklist.md` sind pro `task_folder`

**Vorteile:** Klare Trennung pro Anlage, Definitionen in Git versionierbar, State pro Projekt.

### Reihenfolge der Umsetzung

1. Ansatz 3 (task_folder) umsetzen – vor oder parallel zur Workflow-Automatisierung
2. Workflow-State + Checkliste + Cursor Rule implementieren
3. Optional: Export-Tool DB → JSON für Backup

---

## Implementierungs-Roadmap

**Entscheidung: task_folder von Anfang an** – Multi-Projekt-Struktur wird direkt in Phase A umgesetzt.

### Phase A: Grundlagen (mit task_folder)

**Migration: Sauberer Schnitt** – Neue Struktur, alte Config als Referenz kopieren (nicht verschieben).

1. **task_folder-Konzept:** Tabelle `projects` um `task_folder` erweitern
2. **Config neu:** `tasks/Risikoanalyse/fmea_explicit.py` und `measures_explicit.py` anlegen – Inhalt aus `config/` als Referenz kopieren
3. **Tools anpassen:** `insert_fmea_explicit`, `apply_explicit_measures` erhalten Parameter `task_folder`; dynamischer Import aus `tasks/{task_folder}/`
4. **tools/workflow_state.py** – load, save, get_next_action, mark_done (alle mit task_folder)
5. **tools/update_checklist.py** – generiert checklist.md aus DB + Config
6. **tasks/Risikoanalyse/workflow_state.json** – initial anlegen (oder beim ersten Lauf)
7. **.cursor/rules/fmea-workflow.md** – Agent-Anweisung (inkl. Hybrid-Review)

### Phase B: Integration

8. Workflow `fmea_analyse.md` um Verweis auf workflow_state ergänzen
9. `insert_fmea_explicit` und `apply_explicit_measures` nach Erfolg State aktualisieren (oder Agent ruft `mark_component_done` auf)
10. `update_checklist` nach jedem Einspielen aufrufen (oder Agent ruft es auf)
11. Test mit 2–3 Komponenten (z.B. KOMP-017, KOMP-018, KOMP-019)

### Phase C: Optional (später)

- Export-Tool DB → JSON für Backup
- n8n-Integration
