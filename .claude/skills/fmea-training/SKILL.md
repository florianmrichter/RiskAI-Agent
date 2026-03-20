---
name: fmea-training
model: sonnet
description: >
  Trainingsmodus für das FMEA-Bewertungssystem. Präsentiert dem Fachexperten gezielt
  S/O/D-Bewertungen zur Überprüfung und sammelt strukturiertes Feedback für die
  Kalibrierung des Agents. Verwende diese Skill wenn der Nutzer "FMEA trainieren",
  "Bewertungen überprüfen", "Agent kalibrieren", "Training starten", "Bewertungen checken",
  "wo lag ich falsch", "Qualität verbessern", "Feedback geben", "Korrekturen einpflegen",
  "wie gut bewertet der Agent", "Training-Session" oder "Kalibrierung starten" sagt.
---

# FMEA-Training

Du führst eine gezielte Trainings-Session durch, um die Qualität deiner S/O/D-Bewertungen zu verbessern. Kein produktiver FMEA-Lauf — sondern ein überwachtes Training, bei dem der Fachexperte deine Bewertungen bestätigt oder korrigiert.

S/O/D-Skalenbedeutungen aus `config/fmea_standards.py` (S_SCALE, O_SCALE, D_SCALE) laden. Druckbare Referenz: `.claude/skills/fmea-risikoanalyse/references/sod-referenzkarte.md`.

## Ablauf

### 1. Kandidaten auswählen

`select_training_candidates(n=10)` aus `tools.calibration` aufrufen. Liefert vollständige Dicts mit FM-Kontext (komp_id, komp_typ, funktion, project_id, S/O/D, Begründungen, Konfidenz etc.).

Auswahl-Priorität:
1. Bewertungen mit `agent_konfidenz = niedrig`
2. Komponenten-Typen mit wenig bisherigem Feedback
3. Fehlermodi, die historisch oft korrigiert wurden

### 2. Kontext laden (pro Kandidat)

Für jeden Kandidaten den vollständigen Kontext über die FMEAStorage-API laden — kein raw SQL:

```python
with FMEAStorage() as db:
    causes = db.get_failure_causes(fm_id)
    effects = db.get_failure_effect(fm_id)
    controls = db.get_current_controls(fm_id)
    risk = db.get_risk_assessment(fm_id)
```

Die Basis-Infos (komp_id, komp_typ, fehlermodus, fehlerart, project_id etc.) kommen bereits aus dem `select_training_candidates()`-Dict von Schritt 1.

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

Wenn `kontext_beschreibung` leer oder zu kurz ist (< 50 Zeichen), eine eigene kurze Einordnung aus den Ursachen/Folgen formulieren. Der Experte braucht immer den "Worum geht es?"-Kontext.

### 4. Feedback erfassen

S, O, D **einzeln** bestätigen lassen — nicht pauschal "alles OK?"

- **Bestätigung:** `db.record_confirmation(fm_id, project_id, field="S", value=S, source="training")`
- **Korrektur:** `db.record_correction(fm_id, project_id, field="S", original=agent_S, corrected=expert_S, reason="...", context={...}, source="training")`

Bei Korrektur: RPZ wird automatisch neu berechnet.

### 5. Zusammenfassung

```
Training abgeschlossen: {total} Bewertungen
- {confirmed} bestätigt ({confirmed_pct}%)
- {corrected} korrigiert ({corrected_pct}%)
- Haupterkenntnis: {top_finding}
```

### 6. Kalibrierung aktualisieren

Am Ende: `generate_rules()` aus `tools.calibration` aufrufen — aktualisiert automatisch `config/calibration_rules.json`.

## Regeln

- Jede Runde: EINEN Fehlermodus zeigen, nicht mehrere gleichzeitig
- S, O, D einzeln bestätigen lassen — nicht pauschal "alles OK?"
- Bei Korrektur: IMMER nach Begründung fragen ("Warum?")
- Kontext immer mitliefern: "Worum geht es?", Ursachen, Folgen, Controls
- Wenn kontext_beschreibung fehlt: eigene Kurzeinordnung formulieren
- Am Ende: Kalibrierungsregeln automatisch neu generieren
- Maximal 15 Runden pro Session (Experten-Ermüdung vermeiden)

---

## Massnahmen-Training Modus

Trigger: "Massnahmen trainieren", "Massnahmen-Training", "measures training"

### Ablauf

1. **FM laden**: Fehlermodus mit aktuellem RPZ aus DB holen (RPZ >= 100)
2. **Kontext zeigen**: Fehlermodus, Ursachen, Folgen, S/O/D, aktueller RPZ
3. **Experte bewerten lassen**:
   - STOP-Kategorie vorschlagen (S/T/O/P)
   - ABE-Kategorie vorschlagen (A/B/E)
   - Erwartete RPZ-Reduktion schätzen (neue S/O/D-Werte)
4. **Vergleich**: Agent zeigt seine eigene Empfehlung und vergleicht
5. **Feedback sammeln**: Bei Abweichung nach Begründung fragen
6. **Tracking**: Übereinstimmungsrate über alle Runden mitführen

### Darstellung pro Runde

```
=== Runde X/15 — Massnahmen-Training ===
FM: [fehler_id] — [fehlermodus]
Komponente: [name] ([typ])
RPZ: [S]×[O]×[D] = [RPZ] ([status])

Ursachen: [Liste]
Folgen: [Mensch/Umwelt/Anlage/Kosten]
Aktuelle Controls: [Liste]

Frage: Welche Massnahme würden Sie empfehlen?
→ STOP-Kategorie: S / T / O / P ?
→ ABE-Kategorie: A / B / E ?
→ Geschätzte neue Werte: S_neu, O_neu, D_neu ?
```

### Auswertung

Am Ende der Session:
- Übereinstimmungsrate STOP: X%
- Übereinstimmungsrate ABE: X%
- Durchschnittliche RPZ-Abweichung: ±Y
- Auffällige Muster (z.B. "Experte bevorzugt technische Massnahmen stärker")
