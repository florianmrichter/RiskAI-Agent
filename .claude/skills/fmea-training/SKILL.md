---
name: fmea-training
model: opus
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

### 2. Training-Runden

Pro Kandidat dem Experten präsentieren:

```
Training-Runde {i}/{total}

Komponente: {komponente} ({komponenten_typ})
Fehlermodus: {fehlermodus}
Fehlerart: {fehlerart}

Meine Einschätzung:
  S = {S} ({S_label} — {S_beschreibung})
  O = {O} ({O_label} — {O_beschreibung})
  D = {D} ({D_label} — {D_beschreibung})

Begründung: {begruendung_kurz}

Teilen Sie diese Einschätzung?
[✓ Ja]  [✗ Nein, weil...]
```

### 3. Feedback erfassen

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

### 4. Zusammenfassung

Nach allen Runden:

```
Training abgeschlossen: {total} Bewertungen
- {confirmed} bestätigt ({confirmed_pct}%)
- {corrected} korrigiert ({corrected_pct}%)
- Haupterkenntnis: {top_finding}
```

### 5. Kalibrierung aktualisieren

```python
from tools.calibration import generate_rules
config = generate_rules()
print(f"Kalibrierungsregeln aktualisiert: {len(config['rules'])} Regeln")
```

## Regeln

- Jede Runde: EINEN Fehlermodus zeigen, nicht mehrere gleichzeitig
- S, O, D einzeln bestätigen lassen — nicht pauschal "alles OK?"
- Bei Korrektur: IMMER nach Begründung fragen ("Warum?")
- Kontext mitliefern: Komponente, Medium, Betriebsbedingungen
- Am Ende: Kalibrierungsregeln automatisch neu generieren
- Maximal 15 Runden pro Session (Experten-Ermüdung vermeiden)
