---
name: fmea-training
model: sonnet
description: >
  Trainingsmodus für das FMEA-Bewertungssystem. Präsentiert dem Fachexperten gezielt
  S/O/D-Bewertungen zur Überprüfung und sammelt strukturiertes Feedback für die
  Kalibrierung des Agents. Verwende diese Skill wenn der Nutzer "FMEA trainieren",
  "Bewertungen überprüfen", "Agent kalibrieren" oder "Training starten" sagt.
---

# FMEA-Training

Du führst eine gezielte Trainings-Session durch, um die Qualität deiner S/O/D-Bewertungen zu verbessern. Kein produktiver FMEA-Lauf — sondern ein überwachtes Training, bei dem der Fachexperte deine Bewertungen bestätigt oder korrigiert.

## Ablauf

### 1. Kandidaten auswählen

```python
from tools.calibration import select_training_candidates
candidates = select_training_candidates(n=10)
```

Auswahl-Priorität:
1. Bewertungen mit `agent_konfidenz = niedrig`
2. Komponenten-Typen mit wenig bisherigem Feedback
3. Fehlermodi, die historisch oft korrigiert wurden

### 2. Kontext laden (pro Kandidat)

Für jeden Kandidaten den vollständigen Kontext aus der DB laden:

```python
from tools.storage import FMEAStorage
db = FMEAStorage()

# Fehlermodus mit Komponente, Projekt, Funktion
fm_data = db.conn.execute('''
    SELECT fm.id, fm.fehlermodus, fm.fehlerart, fm.kontext_beschreibung,
           fm.controls_einschraenkung, fm.empfehlung,
           c.komp_id, c.typ as komp_typ,
           f.beschreibung as funktion,
           p.anlage_name, p.id as project_id, p.task_folder
    FROM failure_modes fm
    JOIN functions f ON fm.function_id = f.id
    JOIN components c ON f.component_id = c.id
    JOIN projects p ON c.project_id = p.id
    WHERE fm.id = ?
''', (fm_id,)).fetchone()

# Ursachen, Folgen, Controls, S/O/D-Begründungen laden
causes = db.conn.execute('SELECT beschreibung, herkunft FROM failure_causes WHERE failure_mode_id=?', (fm_id,)).fetchall()
effects = db.conn.execute('SELECT * FROM failure_effects WHERE failure_mode_id=?', (fm_id,)).fetchall()
controls = db.conn.execute('SELECT name, typ, wirkung, beschreibung, beeinflusst FROM current_controls WHERE failure_mode_id=?', (fm_id,)).fetchall()
ra = db.conn.execute('SELECT S, O, D, rpz, rpz_status, begruendung_S, begruendung_O, begruendung_D, daten_konfidenz, agent_konfidenz, daten_quelle FROM risk_assessments WHERE failure_mode_id=?', (fm_id,)).fetchone()
```

### 3. Training-Runden — Präsentation im Moderator-Stil

Pro Kandidat dem Experten im gleichen Stil wie der FMEA-Skill präsentieren:

```
Training-Runde {i}/{total}
Projekt: {anlage_name} | Komponente: {komp_id} ({komp_typ})

--- {fehler_id}: {fehlermodus} ---

Worum geht es?
{kontext_beschreibung}

Ursachen:
1. {ursache_1}
2. {ursache_2}
...

Folgen:
- Mensch: {mensch_beschreibung}
- Umwelt: {umwelt_beschreibung}
- Anlage: {anlage_beschreibung}
- Kosten: {kosten_beschreibung}

Bestehende Controls:
- {control_1}: {beschreibung} (beeinflusst: {S/O/D})
- {control_2}: ...

Einschränkung der Controls: {controls_einschraenkung}

---

Meine Bewertung:

S = {S} (Severity / Bedeutung): {S_label} — {S_beschreibung}
  Begründung: {begruendung_S}

O = {O} (Occurrence / Auftreten): {O_label} — {O_beschreibung}
  Begründung: {begruendung_O}

D = {D} (Detection / Entdeckung): {D_label} — {D_beschreibung}
  Begründung: {begruendung_D}

RPZ = {rpz} ({rpz_status})
Konfidenz: Daten={daten_konfidenz}, Agent={agent_konfidenz}

---

Beginnen wir mit S = {S}. Passt das?
```

Wichtig: Wenn `kontext_beschreibung` leer oder zu kurz ist (< 50 Zeichen), eine eigene kurze Einordnung aus den Ursachen/Folgen formulieren. Der Experte braucht immer den "Worum geht es?"-Kontext.

S/O/D-Skalenbedeutungen aus `config/fmea_standards.py` (S_SCALE, O_SCALE, D_SCALE) laden und bei der Präsentation angeben.

### 4. Feedback erfassen

S, O, D **einzeln** bestätigen lassen — nicht pauschal "alles OK?"

```python
from tools.storage import FMEAStorage
db = FMEAStorage()

# Bei Bestätigung:
db.record_confirmation(
    failure_mode_id=fm_id, project_id=project_id,
    field="S", value=S, source="training"
)

# Bei Korrektur:
db.record_correction(
    failure_mode_id=fm_id, project_id=project_id,
    field="S", original=agent_S, corrected=expert_S,
    reason="Experten-Begründung",
    context={"komponenten_typ": typ, "fehlerart": art, "medium": medium},
    source="training"
)
```

### 5. Zusammenfassung

Nach allen Runden:

```
Training abgeschlossen: {total} Bewertungen
- {confirmed} bestätigt ({confirmed_pct}%)
- {corrected} korrigiert ({corrected_pct}%)
- Haupterkenntnis: {top_finding}
```

### 6. Kalibrierung aktualisieren

```python
from tools.calibration import generate_rules
config = generate_rules()
print(f"Kalibrierungsregeln aktualisiert: {len(config['rules'])} Regeln")
```

## Regeln

- Jede Runde: EINEN Fehlermodus zeigen, nicht mehrere gleichzeitig
- S, O, D einzeln bestätigen lassen — nicht pauschal "alles OK?"
- Bei Korrektur: IMMER nach Begründung fragen ("Warum?")
- Kontext immer mitliefern: "Worum geht es?", Ursachen, Folgen, Controls
- Wenn kontext_beschreibung fehlt: eigene Kurzeinordnung formulieren
- Am Ende: Kalibrierungsregeln automatisch neu generieren
- Maximal 15 Runden pro Session (Experten-Ermüdung vermeiden)
