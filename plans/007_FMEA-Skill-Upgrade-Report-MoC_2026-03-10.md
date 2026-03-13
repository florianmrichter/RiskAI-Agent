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

### Dateien zu ändern (Phase 1)

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

```text
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

```text
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
- Am Ende: Zusammenfassung + nur Highlight-Fragen ausgeben (Format: "Ich habe [Komponente X] vollständig bewertet: [N] Fehlermodi, [M] mit RPZ ≥ 100. Drei Punkte wo ich menschliches Urteil empfehle: [1] [2] [3]")
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

### Dateien zu ändern (Phase 3)

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

```text
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

```text
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
| --- | --- | --- |
| `tools/storage.py` | 1 | Neue DB-Felder (risk_assessments, measures, projects) |
| `tools/workflow_state.py` | 1 | autonomy_mode Feld |
| `tools/migrate_db.py` | 1 | Neu erstellen |
| `templates/fmea_report.html` | 2 | Komplettes Redesign (4-stufig) |
| `tools/report_generator.py` | 2 | report_context erweitern, Delta-Logik |
| `.claude/skills/fmea-risikoanalyse/SKILL.md` | 3 | Modus-Logik, Konfidenz-Pflicht, Write-back-Pflicht |
| `.claude/skills/fmea-risikoanalyse/references/fmea-workflow.md` | 3 | Verhaltensregeln pro Modus |
| `.claude/skills/fmea-risikoanalyse/references/fmea-standards.md` | 3 | Konfidenz + Datenquellen |
| `workflows/fmea-workflow.md` | 3 | Modus-Syntax + neue Felder (+ Sync zu skills/) |
| `tools/load_plant_data.py` | 3+5 | `update_plant_data()` Funktion hinzufügen |
| `tools/moc_manager.py` | 4 | Neu erstellen |
| `.claude/skills/anlagendaten-interview/SKILL.md` | 5 | Autonomiemodi, Readiness-Check, Bridge |
| `.claude/skills/anlagendaten-interview/references/interview-phasen.md` | 5 | FMEA-kritische Markierungen, Vorfälle, Checkpoints |
| `.claude/skills/anlagendaten-interview/references/anlagendaten-schema.json` | 5 | betriebserfahrungen[], interview_status |

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

### Phase 5

- [ ] Interview-Start zeigt Modus-Auswahl (Geführt / Experte / Import)
- [ ] Modus "Import": JSON einfügen → Validierung → nur Lücken nachfragen
- [ ] Phase 2 fragt nach bekannten Störfällen → wird in `betriebserfahrungen[]` gespeichert
- [ ] FMEA-kritische Felder (SIL, ATEX, PSV) werden hervorgehoben wenn leer
- [ ] Phasen-Checkpoint nach jedem System in Phase 4
- [ ] FMEA-Readiness-Score am Ende: korrekte Prozentberechnung
- [ ] Unterbrochenes Interview: beim Neustart Wiederaufsetzen-Angebot
- [ ] Bridge: "Direkt FMEA starten?" führt nahtlos in fmea-risikoanalyse-Skill über

---

## Phase 5: Anlagendaten-Interview — Analyse & Upgrade

### Entscheidung: Getrennt lassen — mit Bridge-Protocol

**Empfehlung: Skills bleiben getrennt.** Die Integration erfolgt über ein explizites Bridge-Protocol, nicht durch Zusammenlegung.

**Argumente für getrennte Skills:**

| Pro getrennt | Begründung |
| --- | --- |
| Single Responsibility | Klarer Input/Output-Vertrag pro Skill |
| Verschiedene Nutzergruppen | Anlagenverantwortlicher macht Interview; Sicherheitsingenieur macht FMEA |
| Wiederverwendbarkeit | Interview kann auch für Compliance, andere Analysen genutzt werden |
| Unterbrechungsschutz | Wenn FMEA abbricht, sind Anlagendaten sicher gespeichert |
| Onboarding | Neue Nutzer: erst Interview verstehen → dann FMEA starten |
| Kontextfenster | Ein sehr großer merged Skill würde die Moderation-Qualität senken |

**Argumente gegen Zusammenlegen (Nachteile getrennte Skills):**

| Problem | Erklärung |
| --- | --- |
| Übergabe ist ein Reibungspunkt | Nach dem Interview muss der Nutzer manuell den FMEA-Skill starten |
| Kontextverlust | FMEA-Skill kennt nicht, was im Interview besprochen wurde — nur das JSON |
| Mid-FMEA Datenlücken | Wenn FMEA fehlende Anlagendaten erhebt, werden diese bisher nicht zurückgeschrieben |
| Kein gemeinsamer Autonomiemodus | Interview kennt keinen Expert/Autonom-Modus — immer gleiche Führungstiefe |

#### Lösung: Bridge-Protocol (statt Merge)

- FMEA-Skill kann fehlende Daten direkt erheben → sofort in `anlagendaten.json` zurückschreiben (bereits in Phase 3 geplant via `update_plant_data()`)
- Interview-Skill bekommt Autonomiemodi analog zum FMEA-Skill
- Interview endet mit FMEA-Readiness-Check + optionalem direkten Übergang

---

### Schwächen des aktuellen Anlagendaten-Interview-Skills (aus FMEA-Perspektive)

#### Schwäche 1: Keine FMEA-Relevanz-Orientierung

- Das Interview fragt alle 7 Phasen gleich ab, unabhängig davon was für die FMEA kritisch ist
- FMEA-kritische Daten (Sicherheitsventile, SIL-Einstufungen, ATEX-Zonen, Notkühlung) werden nicht hervorgehoben
- Ein Nutzer weiß nicht, welche Lücken die FMEA blockieren werden

#### Schwäche 2: Phase 4 überwältigend

- 4a bis 4g für jede Komponente — bei einer Anlage mit 5+ Systemen zu lang
- Kein Checkpoint: "Wir haben jetzt System 1 vollständig. Weiter mit System 2?"
- Sub-Phasen 4d (MSR) und 4e (Sicherheitseinrichtungen) sind FMEA-kritisch aber werden gleich behandelt wie 4g (Hersteller)

#### Schwäche 3: Kein Wiederaufsetzen bei Unterbrechung

- Wenn das Interview nach Phase 3 abbricht, gibt es keinen Mechanismus um bei Phase 4 wieder einzusteigen
- Keine Speicherung des Interview-Fortschritts

#### Schwäche 4: Kein Autonomiemodus

- Immer geführtes Interview, max 3–4 Fragen pro Runde
- Ein erfahrener Sicherheitsingenieur möchte vielleicht direkt eine JSON-Struktur einfügen oder kurze Stichpunkte liefern

#### Schwäche 5: Keine FMEA-Readiness-Bewertung am Ende

- Interview endet mit "Du kannst jetzt den fmea-risikoanalyse-Skill starten"
- Keine Aussage: "Folgende Felder sind noch leer und könnten die FMEA verlangsamen: [...]"
- Keine Ampel: Wie vollständig sind die Daten wirklich?

#### Schwäche 6: Historische Vorfälle fehlen

- Phase 2 (Prozessbeschreibung) und Phase 4 fragen nicht nach bekannten Störfällen, Beinaheunfällen oder Betriebserfahrungen
- Diese Information ist Gold für FMEA-O-Werte (Occurrence-Bewertung)

#### Schwäche 7: Utility-Systeme werden als Vollständig behandelt

- Phase 5 (Medien/Betriebsstoffe) wird abgehakt ohne FMEA-Kontext
- Für FMEA: Utility-Ausfall ist eine eigenständige Fehlermodus-Kategorie
- Interview sollte betonen: "Diese Daten brauchst du später für Fehlermodus-Kategorien wie 'Kühlwasserausfall'"

---

### Konkrete Verbesserungen (Phase 5 Umsetzung)

#### 5a: Autonomiemodi für Interview-Skill

Analog zu FMEA-Skill — drei Modi:

- **Geführt** (Default, Einsteiger): Wie heute, max 3–4 Fragen pro Runde, immer zusammenfassen, alles erklären
- **Experte** (Erfahrene Anwender): Kompaktere Fragen, kein Erklären von Standards, direktes Vorgehen pro Phase
- **Import** (maximale Effizienz): Nutzer liefert strukturierte Daten (Stichpunkte / Tabelle / JSON), Agent validiert und füllt Lücken gezielt

Modus-Auswahl am Anfang des Interview-Skills:

```text
"Wie möchtest du die Anlagendaten erfassen?
[G] Geführt — ich führe dich durch alle 7 Phasen Schritt für Schritt
[E] Experte — direkt, kein Grundlagenwissen, kompakt
[I] Import — du lieferst strukturierte Daten, ich validiere und frage nach Lücken
Du kannst jederzeit wechseln: /modus G|E|I"
```

#### 5b: FMEA-Kritisch-Markierungen in interview-phasen.md

In `references/interview-phasen.md` werden FMEA-kritische Felder explizit markiert:

```text
⚠️ FMEA-KRITISCH — Diese Felder blockieren die FMEA wenn leer:
- Phase 4d: SIL-Einstufung aller sicherheitsrelevanten MSR-Kreise
- Phase 4e: Alle Sicherheitsventile (PSV), Berstscheiben, Notstopp-Einrichtungen
- Phase 4a: ATEX-Zone pro Komponente
- Phase 5: Notkühlung (Medium, Temperatur, Auslösung)
- Phase 6: SIS-Funktionen (LSHH, TSHH, PSHH mit Schwellen)
```

Agent betont diese in allen Modi: "Das ist eine FMEA-kritische Information — ohne sie kann ich den O/D-Wert für Sicherheitskreise nicht korrekt bewerten."

#### 5c: Historische Vorfälle als neue Frage (Phase 2 Ergänzung)

In Phase 2 (Prozessbeschreibung) neue Frage hinzufügen:

```text
"Gibt es bekannte Störfälle, Beinaheunfälle oder häufige Betriebsstörungen an dieser Anlage?
Wenn ja: Was ist passiert, wie oft, was war die Ursache?
(Diese Information hilft mir, die Häufigkeitsbewertung (O-Werte) der FMEA realistisch zu gestalten)"
```

Daten werden in `anlagendaten.json` unter neuem Feld `betriebserfahrungen[]` gespeichert:

- `datum`, `beschreibung`, `ursache`, `konsequenz`, `massnahme`

#### 5d: FMEA-Readiness-Score am Ende des Interviews

Nach Phase 7 berechnet der Agent einen strukturierten Readiness-Check:

```text
FMEA-Bereitschaftscheck:
✅ Prozessbeschreibung: vollständig
✅ Stoffe: vollständig (PubChem bestätigt)
⚠️ System R-101 — SIL-Einstufung fehlt (FMEA-kritisch)
⚠️ System DS-200 — ATEX-Zone nicht angegeben
✅ Medien: vollständig
✅ Leitsystem: vollständig
✅ Systemgrenzen: dokumentiert

FMEA-Bereitschaft: 85% — 2 FMEA-kritische Felder fehlen.
Empfehlung: Diese jetzt ergänzen oder nach dem Start der FMEA direkt nacherheben.
```

#### 5e: Phasen-Checkpoint für Phase 4 (Multi-System)

Bei mehr als 2 Systemen: nach jeder abgeschlossenen Komponente in Phase 4 expliziter Checkpoint:

```text
"[System R-101 — vollständig erfasst]
Alle 7 Sub-Phasen (4a–4g) abgeschlossen. 3 FMEA-kritische Felder vorhanden.
→ Weiter mit System DS-200?"
```

#### 5f: Unterbrechungs-Wiederaufsetzen

Neues Feld in `anlagendaten.json`: `interview_status` mit `phase`, `subphase`, `current_system`

Beim Start des Interview-Skills prüfen:

- Existiert `anlagendaten.json` bereits mit `interview_status.complete = false`?
- Wenn ja: "Du hast das Interview zuletzt bei Phase 4, System DS-200 unterbrochen. Weiter machen?"

#### 5g: Nahtloser Übergang zur FMEA (Bridge)

Am Ende des Interviews, nach dem Readiness-Check:

```text
"Anlagendaten gespeichert. ✅
FMEA-Bereitschaft: 100% (oder: 85% — 2 Felder offen)

Möchtest du jetzt direkt mit der FMEA-Risikoanalyse starten?
[J] Ja, FMEA starten — ich lade die Anlagendaten automatisch
[N] Nein, ich starte die FMEA später mit: /skill fmea-risikoanalyse"
```
