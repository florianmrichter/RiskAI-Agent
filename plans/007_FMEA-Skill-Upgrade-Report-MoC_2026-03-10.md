# FMEA-System: Umfassendes Upgrade — Skill, Report & MoC

## Context

Das bestehende FMEA-System funktioniert gut für erfahrene Nutzer, hat aber drei kritische Schwachstellen:

1. **Interview-Prozess zu passiv** — der Agent wartet, erklärt zu wenig, prüft keine Vollständigkeit. Nutzer ohne FMEA-Hintergrund kommen nicht selbstständig ans Ziel.
2. **Report unstrukturiert** — ein Informationsniveau für alle Leser (Plant Engineer, Management, Auditor, neue Kollegen, MoC-Verantwortliche). Maßnahmen gehen unter, Priorisierung fehlt.
3. **Kein Management of Change** — bestehende Analysen können nicht versioniert fortgeführt werden. Bei Änderungen muss alles neu gemacht werden.

**Ansatz: Report-getrieben.** Erst den perfekten Report definieren → rückwärts ableiten welche Daten gebraucht werden → Interview anpassen → MoC obendrauf.

---

## Design-Entscheidungen (abgestimmt)

### Zielgruppen des Reports
1. Anlagenverantwortlicher Ingenieur
2. Externe Auditoren / Behörden
3. Management / Entscheider
4. Zukünftige Kollegen & neue Mitarbeiter
5. Sicherheitsingenieure für Management of Change

### Autonomiemodi
- **Geführt** (Einsteiger): vollständige Moderation, Skala immer sichtbar, plant-spezifische Beispiele
- **Experte** (erfahrene Anwender): direkter Dialog, keine Erklärungen, kompakte Vollständigkeitsprüfung
- **Autonom** (maximales Vertrauen): Agent führt komplett durch, Nutzer bestätigt nur Highlight-Fragen
- Modus ist **jederzeit wechselbar** während der Analyse

### Konfidenz-Felder (zwei getrennt)
- `daten_konfidenz`: Qualität der Eingangsdaten (CCPS/OREDA-Referenz vs. Schätzung)
- `agent_konfidenz`: Selbsteinschätzung des Agenten, mit Begründungspflicht
- Beide: `hoch / mittel / niedrig` — bei `niedrig` automatisches Review-Flag im Report

### MoC-Versioning
- v1.0 wird eingefroren (PDF + DB-Snapshot)
- Änderungsbeschreibung eingeben → betroffene Komponenten identifizieren → nur diese neu bewerten
- v2.0 entsteht mit Delta-Markierungen; Unveränderte Teile übernommen mit Verweis auf v1.0
- Technisch: neues `project_id` mit `parent_version`-Verweis

### Offen für separaten Plan
- Anlagendaten-Interview-Skill: Frage ob eigener Skill behalten oder mit FMEA zusammenführen (eigene Session)

---

## Phase 1: Datenmodell erweitern

**Ziel:** Neue Felder in DB + Datenstrukturen, die alle späteren Phasen unterstützen.

### Dateien zu ändern

**`tools/storage.py`** (Haupt-CRUD für SQLite)
- `risk_assessments`-Tabelle: neue Felder hinzufügen
  - `daten_konfidenz TEXT DEFAULT 'mittel'` (hoch/mittel/niedrig)
  - `agent_konfidenz TEXT DEFAULT 'mittel'` (hoch/mittel/niedrig)
  - `agent_konfidenz_begruendung TEXT` (Pflichtfeld wenn niedrig)
  - `daten_quelle TEXT` (CCPS / OREDA / Betriebserfahrung / Expertenschätzung / KI-Vorschlag)
- `measures`-Tabelle: neue Felder
  - `prioritaet TEXT DEFAULT 'empfohlen'` (pflicht / empfohlen / optional)
  - `aufwand TEXT` (gering / mittel / hoch)
  - `kosten_klasse TEXT` (klein / mittel / gross) — klein=<5k, mittel=5-50k, gross=>50k
  - `assigned_to TEXT` (optional)
  - `target_date TEXT` (optional)
  - `implementation_status TEXT DEFAULT 'geplant'` (geplant / in_bearbeitung / umgesetzt)
- `projects`-Tabelle: neue Felder
  - `version TEXT DEFAULT '1.0'`
  - `parent_version_id INTEGER` (FK auf projects.id, NULL für v1.0)
  - `version_beschreibung TEXT` (leer für v1.0, Änderungsbeschreibung für Folgeversionen)
  - `erstellt_von TEXT`
  - `geprueft_von TEXT`
  - `frozen INTEGER DEFAULT 0` (1 = eingefroren, keine weiteren Änderungen möglich)

**`tools/workflow_state.py`**
- `autonomy_mode` in workflow_state.json speichern: `geführt / experte / autonom`
- Modus-Wechsel-Funktion: `set_autonomy_mode(task_folder, mode)`
- Getter: `get_autonomy_mode(task_folder)` mit Default `geführt`

**Migration:** Neue `tools/migrate_db.py` — safe ALTER TABLE mit IF NOT EXISTS-Check für jedes neue Feld.

---

## Phase 2: Report-Template redesign (4-stufige Architektur)

**Ziel:** `templates/fmea_report.html` komplett umstrukturieren.

### Neue Struktur

```
Deckblatt
  └── Versions-Header: "Version X.Y — [Datum]" + "(ersetzt vX.0 vom [Datum])" wenn MoC
  └── Freigabe-Stempel: Erstellt von / Geprüft von (Felder, auch leer = "ausstehend")

Stufe 1: Executive Summary (1–2 Seiten)
  └── Ampel-Übersicht: kritisch / hoch / mittel / niedrig (große Icons, Zahlen)
  └── Top 3–5 Risiken: eine Zeile pro Risiko, RPZ, Status-Badge
  └── Maßnahmen-Highlights: "X Pflicht-Maßnahmen sofort erforderlich"
  └── Gesamtbewertung: kurzer Satz zur Anlage insgesamt

Stufe 2: Maßnahmen-Cockpit (3–5 Seiten)
  └── Tabelle aller Maßnahmen, sortiert nach RPZ-Delta (höchste Wirkung oben)
  └── Spalten: Fehlermodus | Maßnahme | STOP | ABE | Priorität | Aufwand | Kosten-Klasse | RPZ vorher→nachher | Zuständig | Zieldatum | Status
  └── Priorität farblich: Pflicht (rot) / Empfohlen (orange) / Optional (grau)

Stufe 3: Technische Detailkarten (Hauptteil)
  └── Pro Komponente: Header mit Komp-ID, Name, Typ
  └── Vollkarten (kritisch/hoch): wie heute, aber kompakter
      └── Konfidenz-Badges: daten_konfidenz + agent_konfidenz (sichtbar in SOD-Bereich)
      └── Review-Flag wenn agent_konfidenz=niedrig: "⚠ KI-Bewertung unsicher — Expertenprüfung empfohlen"
      └── Datenquelle pro O-Wert: kleiner Badge ("CCPS" / "OREDA" / "Schätzung" etc.)
      └── MoC-Badge wenn Karte geändert: "Neu in v2.0 — [Änderungsgrund]"
  └── Kompaktkarten (mittel/niedrig):
      └── SOD-Visualisierung (kleiner)
      └── Ursachen: ID + Beschreibung + Phase (alle, explizit)
      └── Verdict-Box: "Vollständig bewertet — RPZ [X] unter Grenzwert. Keine Maßnahmen erforderlich."
      └── Konfidenz-Badges

Stufe 4: Audit-Anhang
  └── Versionshistorie (leer bei v1.0; Delta-Log bei v2.0+)
  └── Freigabe-Sektion (Name / Datum / Rolle für Ersteller & Reviewer)
  └── Methodikverweis (AIAG-VDA, IEC 61511, CCPS — bisher im Hauptteil)
  └── Abkürzungsverzeichnis (bleibt)
  └── Vollständige Maßnahmentabelle (bleibt, aber mit neuen Spalten)
```

**`tools/report_generator.py`**
- `report_context`-Dict um alle neuen Felder erweitern
- Konfidenz-Aggregation: Zähle `agent_konfidenz=niedrig`-Fehlermodi → Summary-Warnung
- MoC-Delta: wenn `parent_version_id` vorhanden → Delta-Daten aus parent-Projekt laden
- Maßnahmen-Cockpit-Daten: sortiert nach `(rpz - rpz_neu)` DESC

---

## Phase 3: FMEA-Skill redesign (Autonomiespektrum + bessere Moderation)

**Ziel:** `.claude/skills/fmea-risikoanalyse/SKILL.md` + `references/fmea-workflow.md` umschreiben.

### Skill-Start-Sequenz (neu)

```
1. Workflow-State laden → Modus prüfen
2. Falls kein Modus gesetzt: Modus-Auswahl präsentieren (einmalig, kurz)
   "Wie möchtest du arbeiten?
   [G] Geführt — ich erkläre jeden Schritt
   [E] Experte — direkt, kein Grundlagenwissen
   [A] Autonom — ich mache alles, du bestätigst nur Highlights
   Du kannst jederzeit wechseln mit: /modus G|E|A"
3. Modus in workflow_state.json speichern
4. Weiter mit nächster Aktion
```

### Modus "Geführt" — neue Verhaltensregeln

**Beim S/O/D-Assessment:**
- Immer Skala zeigen + 2 plant-spezifische Beispiele aus bereits bewerteten Fehlermodi dieses Projekts
- Format: "Für S (Schweregrad): Skala 1–10. In diesem Projekt haben wir z.B. [FM-001: S=8 wegen...] und [FM-003: S=3 weil...]. Was würdest du für diesen Fehlermodus sagen?"

**Konfidenz automatisch begründen:**
- Nach jeder S/O/D-Vergabe: Agent fügt `daten_quelle` + `agent_konfidenz` + `agent_konfidenz_begruendung` in die Ausgabe ein
- Wenn `agent_konfidenz=niedrig`: explizit ansprechen: "Ich bin bei diesem O-Wert nicht sicher, weil [Grund]. Empfehle Überprüfung."

**Vollständigkeitsprüfung am Ende jeder Komponente:**
- Alle 9 FM-Kategorien durchgehen: welche wurden behandelt, welche als "nicht relevant" markiert?
- "Ich habe für Kategorie [Dosierung] noch keinen Fehlermodus — ist das bewusst nicht relevant für [Komponente X]?"
- Utility-Pflichtcheck: N₂, Kühlwasser, Thermostat, Abluft, Elektro — explizit dokumentiert

**Safety-Override immer laut:**
- Nie still anwenden: "Ich habe S auf [9] angehoben — [ATEX-Bereich, Sonderregel greift]. Begründung: [...]"

### Modus "Autonom" — neue Verhaltensregeln

- Agent führt Komponente vollständig durch ohne Zwischenfragen
- Am Ende: Zusammenfassung + nur Highlight-Fragen ausgeben
  - Format: "Ich habe [Komponente X] vollständig bewertet: [N] Fehlermodi, [M] mit RPZ ≥ 100. Drei Punkte wo ich menschliches Urteil empfehle: [1] [2] [3]"
- `agent_konfidenz=niedrig`-Fehlermodi **immer** vorlegen, egal welcher Modus

### Modus-Wechsel während der Analyse

- Nutzer kann jederzeit `/modus G`, `/modus E`, `/modus A` eingeben
- Agent bestätigt: "Modus gewechselt zu [Geführt]. Ab jetzt erkläre ich wieder jeden Schritt."
- Wird in workflow_state.json persistiert

### Anlagendaten-Write-back während der FMEA

Wenn der Agent während einer laufenden Analyse fehlende Anlagendaten erhebt (z.B. fehlende Auslegungstemperatur, unbekanntes Sicherheitsventil), **müssen diese Daten zurück in `anlagendaten.json` geschrieben werden**.

**Regel:**

- Jede neue Information über die Anlage (Equipment-Daten, Prozessparameter, MSR-Daten, Stoffe) die im FMEA-Dialog erhoben wird → sofort in `anlagendaten.json` persistieren
- Tool: `tools/load_plant_data.py` erweitern um `update_plant_data(task_folder, path, value)` Funktion
- Agent dokumentiert im Dialog: *"Ich habe [Sicherheitsventil PSV-101, Ansprechdruck 3.5 bar] in den Anlagendaten ergänzt."*
- Verhindert Datenverlust wenn Session unterbrochen wird
- Sorgt dafür dass bei späteren Versionen (MoC) die Anlagendaten vollständig sind

**Dateien zu ändern (Phase 3 ergänzen):**

- `tools/load_plant_data.py` — `update_plant_data()`-Funktion hinzufügen
- `.claude/skills/fmea-risikoanalyse/SKILL.md` — Pflicht: neue Anlagendaten sofort zurückschreiben

---

### Neue Maßnahmen-Felder im Interview

Beim Maßnahmen-Vorschlag ergänzen:
- `prioritaet`: Agent schlägt vor basierend auf RPZ und S-Wert. Pflicht wenn S≥9 oder RPZ≥300
- `aufwand` + `kosten_klasse`: strukturiert, nicht mehr Freitext
- `assigned_to` + `target_date`: optionale Felder, Agent fragt nur im Modus "Geführt" danach

### Dateien zu ändern

- `.claude/skills/fmea-risikoanalyse/SKILL.md` — Modus-Logik, neue Felder, Konfidenz-Pflicht
- `.claude/skills/fmea-risikoanalyse/references/fmea-workflow.md` — neue Verhaltensregeln pro Modus
- `.claude/skills/fmea-risikoanalyse/references/fmea-standards.md` — Konfidenz-Dokumentation, Datenquellen-Typen
- `workflows/fmea-workflow.md` — Modus-Wechsel-Syntax, neue Felder
- **Sync:** Wenn `workflows/fmea-workflow.md` oder `config/fmea_standards.py` geändert → Kopien in `.claude/skills/fmea-risikoanalyse/references/` nachziehen (wie in CLAUDE.md definiert)

---

## Phase 4: Management of Change

**Ziel:** Neue Tool + Workflow-Erweiterung für Versionsmanagement.

### Neues Tool: `tools/moc_manager.py`

```python
# Hauptfunktionen:
freeze_version(project_id)
    # Setzt projects.frozen=1
    # Erstellt DB-Snapshot als JSON in task_folder/versions/v{N}.json
    # Gibt Bestätigung zurück

create_new_version(project_id, change_description, changed_components)
    # Erstellt neues Projekt mit parent_version_id=project_id
    # Kopiert alle NICHT betroffenen Komponenten + Fehlermodi
    # Markiert kopierte Daten mit moc_status='unverändert'
    # Betroffene Komponenten: moc_status='neu_bewertet'
    # Gibt new_project_id zurück

get_version_history(task_folder)
    # Gibt Liste aller Versionen für diese Anlage zurück

get_delta(project_id_old, project_id_new)
    # Vergleicht Fehlermodi, S/O/D-Werte, Maßnahmen
    # Gibt strukturiertes Delta-Dict zurück für Report
```

### DB-Erweiterung

`failure_modes`-Tabelle:
- `moc_status TEXT DEFAULT 'original'` (original / unverändert / neu_bewertet / hinzugefügt / entfernt)
- `moc_herkunft_version TEXT` (von welcher Version übernommen)

### MoC-Workflow im Skill

```
Nutzer: "Ich möchte eine neue Version anlegen — Pumpe P-101 wurde ersetzt"

Agent:
1. tools/moc_manager.freeze_version(current_project_id) → v1.0 einfrieren
2. Betroffene Komponenten identifizieren (Agent analysiert Änderungsbeschreibung)
3. "Ich identifiziere folgende betroffene Komponenten: [KOMP-002 Pumpe P-101]. Soll ich auch [KOMP-003 Saugleitung] mit einbeziehen?" (nur Geführt/Experte; Autonom: selbst entscheiden)
4. tools/moc_manager.create_new_version(...) → v2.0 anlegen
5. Nur betroffene Komponenten neu bewerten (im gewählten Modus)
6. Report v2.0 generieren mit Delta-Markierungen
```

### Verzeichnisstruktur (erweitert)

```
tasks/Risikoanalyse/Ethylacetatproduktion_20TA41/
├── anlagendaten.json
├── workflow_state.json
├── versions/
│   ├── v1.0_snapshot.json    ← eingefroren
│   └── v2.0_snapshot.json    ← nach MoC
├── FMEA_Bericht_v1.0.pdf
└── FMEA_Bericht_v2.0.pdf
```

---

## Reihenfolge der Implementierung

1. **Phase 1** — DB-Migrationen + workflow_state Modus-Erweiterung (Fundament)
2. **Phase 2** — Report-Template (4-stufige Architektur) + report_generator.py
3. **Phase 3** — Skill-Update (SKILL.md + fmea-workflow.md) mit Modus-Logik
4. **Phase 4** — moc_manager.py + MoC-Workflow

Jede Phase ist unabhängig testbar. Phase 2 kann mit Mock-Daten getestet werden bevor Phase 3 fertig ist.

---

## Kritische Dateien

| Datei | Phase | Art der Änderung |
|---|---|---|
| `tools/storage.py` | 1 | Neue DB-Felder (risk_assessments, measures, projects) |
| `tools/workflow_state.py` | 1 | autonomy_mode Feld |
| `tools/migrate_db.py` | 1 | Neu erstellen |
| `templates/fmea_report.html` | 2 | Komplettes Redesign (4-stufig) |
| `tools/report_generator.py` | 2 | report_context erweitern, Delta-Logik |
| `.claude/skills/fmea-risikoanalyse/SKILL.md` | 3 | Modus-Logik, Konfidenz-Pflicht |
| `.claude/skills/fmea-risikoanalyse/references/fmea-workflow.md` | 3 | Verhaltensregeln pro Modus |
| `.claude/skills/fmea-risikoanalyse/references/fmea-standards.md` | 3 | Konfidenz + Datenquellen |
| `workflows/fmea-workflow.md` | 3 | Modus-Syntax + neue Felder (+ Sync zu skills/) |
| `tools/moc_manager.py` | 4 | Neu erstellen |

---

## Verifikation

### Phase 1
- [ ] `python tools/migrate_db.py` auf bestehendem Projekt ausführen → keine Fehler, neue Felder vorhanden
- [ ] `tools/workflow_state.py` Modus setzen/lesen testen

### Phase 2
- [ ] Report mit bestehenden Projektdaten (Ethylacetatproduktion_20TA41) generieren
- [ ] Executive Summary zeigt korrekte Ampel-Übersicht
- [ ] Maßnahmen-Cockpit sortiert nach RPZ-Delta
- [ ] Kompaktkarten für niedrig/mittel erscheinen korrekt
- [ ] Konfidenz-Badges im Report sichtbar (auch wenn noch leer/default)
- [ ] Audit-Anhang mit Versions-Stempel vorhanden

### Phase 3
- [ ] Neues Projekt starten → Modus-Auswahl erscheint
- [ ] Im Modus "Geführt": S/O/D-Frage zeigt Skala + plant-spezifische Beispiele
- [ ] Vollständigkeitsprüfung am Ende einer Komponente korrekt
- [ ] Safety-Override wird laut erklärt
- [ ] `/modus A` wechselt zu Autonom, wird in workflow_state gespeichert
- [ ] `agent_konfidenz=niedrig`-FM wird auch in Modus "Autonom" vorgelegt

### Phase 4
- [ ] `moc_manager.freeze_version()` → JSON-Snapshot erstellt
- [ ] `moc_manager.create_new_version()` → neues Projekt angelegt, unveränderte FMs kopiert
- [ ] Report v2.0 zeigt MoC-Badges auf geänderten Karten
- [ ] Delta-Log im Audit-Anhang korrekt befüllt

---

## Zukünftige Initiative (separater Plan)

**Anlagendaten-Interview-Skill:** Entscheidung ob `anlagendaten-interview` als eigenständiger Skill bleibt oder mit `fmea-risikoanalyse` zusammengeführt wird. Besondere Frage: Kann der Agent während einer laufenden FMEA-Analyse fehlende Anlagendaten direkt nacherheben, ohne den Skill wechseln zu müssen?
