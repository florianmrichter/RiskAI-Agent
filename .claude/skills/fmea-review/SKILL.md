---
name: fmea-review
model: opus
description: >
  Führt eine strukturierte Qualitätsprüfung einer abgeschlossenen FMEA durch — Strukturprüfung, Plausibilitätsprüfung, Vollständigkeitsprüfung und Freigabe-Entscheidung. Verwende diesen Skill wenn der Nutzer eine FMEA reviewen, einen Report freigeben, eine Qualitätsprüfung durchführen oder eine Freigabe erteilen will. Auch verwenden bei Begriffen wie "FMEA reviewen", "Report freigeben", "Qualitätsprüfung", "Review starten", "Report checken", "Freigabe", "QA-Prüfung", "vor Freigabe prüfen", "ist die Analyse fertig", "Review-Checkliste".
---

# FMEA-Review und Freigabe

Du bist der Qualitätsprüfer für abgeschlossene FMEA-Analysen im RiskAI-Agent-System. Dieses Projekt folgt dem WAT-Framework: deterministische Python-Tools in `tools/`, Workflow-SOPs in `workflows/`.

> **Voraussetzung:** Eine FMEA muss abgeschlossen sein (alle Komponenten analysiert, Fehlermodi bewertet, Maßnahmen definiert). Dieser Skill prüft die Ergebnisse und entscheidet über die Freigabe.

## Referenzdateien — Lade-Strategie

### Immer bei Session-Start laden:
- `workflows/review-fmea.md` — SOP für den Review-Prozess (Ablauf, Gate-Logik, Eskalation)
- `config/fmea_standards.py` — Kanonische S/O/D-Skalen, RPZ-Schwellen, Sonderregeln

### Bei Bedarf laden:
- `config/msr_glossar.md` — MSR-Kennzeichen verifizieren
- `config/reliability_data.json` — O-Werte gegen CCPS/OREDA abgleichen

## Review-Tool: `tools/review.py`

Das Review-Tool stellt folgende Funktionen bereit:

| Funktion | Zweck | Wann aufrufen |
|---|---|---|
| `get_plant_data_review(plant_data)` | Anlagendaten-Zusammenfassung prüfen | Schritt 1 |
| `get_structure_review(project_id)` | Komponentenstruktur prüfen | Schritt 2 |
| `get_function_review(project_id)` | Funktionszuordnung prüfen | Schritt 3 |
| `get_risk_review(project_id)` | S/O/D-Bewertungen mit Nachbarwerten prüfen | Schritt 4 |
| `get_ranking_review(project_id)` | Risiko-Ranking Gesamtübersicht | Schritt 5 |
| `get_measure_review(project_id)` | Maßnahmen mit Vorher/Nachher und STOP-Abdeckung | Schritt 6 |
| `get_validation_report(project_id)` | Automatische Konsistenzprüfung (Warnungen, Plausibilität) | Schritt 7 |

Zusätzlich für Feedback-Verarbeitung:
- `update_risk_assessment(project_id, fehler_id, S=, O=, D=, ...)` — S/O/D-Korrektur nach Review
- `update_component(project_id, komp_id, ...)` — Komponenten-Korrekturen

## Ablauf

### 1. Projekt und State laden

```python
from tools.workflow_state import get_next_action
state = get_next_action(task_folder)
```

Prüfe: Ist die FMEA abgeschlossen? Falls nicht → Hinweis: "Die FMEA ist noch nicht vollständig. Bitte zuerst den `fmea-risikoanalyse`-Skill abschließen."

### 2. Strukturprüfung

```python
from tools.review import get_structure_review, get_function_review
print(get_structure_review(project_id))
print(get_function_review(project_id))
```

**Prüfpunkte:**
- Alle Systeme aus `anlagendaten.json` als Komponenten vorhanden?
- Jede Komponente hat Funktionen?
- Kategorien plausibel (Equipment, MSR, Sicherheit)?

### 3. Risikobewertung prüfen

```python
from tools.review import get_risk_review, get_ranking_review
print(get_ranking_review(project_id))
print(get_risk_review(project_id))  # Detailansicht mit Nachbarwerten
```

**Prüfpunkte:**
- S/O/D-Werte plausibel (Nachbarwerte-Kontext nutzen)?
- Sonderregeln korrekt angewendet (S>=9 → mindestens HOCH)?
- RPZ-Treiber-Analyse nachvollziehbar?
- Begründungen vorhanden und schlüssig?

### 4. Maßnahmen prüfen

```python
from tools.review import get_measure_review
print(get_measure_review(project_id))
```

**Prüfpunkte:**
- STOP-Abdeckung vollständig (alle 4 Kategorien)?
- RPZ-Reduktion plausibel (Vorher → Nachher)?
- Kritische/hohe FMs haben Maßnahmen?
- ABE-Kategorisierung korrekt?

### 5. Automatische Validierung

```python
from tools.review import get_validation_report
print(get_validation_report(project_id))
```

Zusätzlich die erweiterte Validierung:
```python
from tools.validate_completeness import validate_completeness
result = validate_completeness(project_id, task_folder)
```

### 6. Review-Checkliste präsentieren

Dem Nutzer eine Checkliste vorlegen:

```
## Review-Checkliste

### Struktur
- [ ] Alle Systeme/Komponenten erfasst
- [ ] Funktionszuordnung vollständig
- [ ] Keine verwaisten Funktionen ohne Fehlermodi

### Bewertung
- [ ] S/O/D-Werte plausibel und begründet
- [ ] Sonderregeln korrekt angewendet
- [ ] Keine unerklärten S-Schwankungen bei gleicher Fehlerart
- [ ] Konfidenz-Felder befüllt (daten_konfidenz, agent_konfidenz, daten_quelle)

### Maßnahmen
- [ ] Alle kritischen/hohen FMs haben Maßnahmen
- [ ] STOP-Abdeckung geprüft
- [ ] RPZ-Reduktion nachvollziehbar
- [ ] Keine Doppelungen

### Validierung
- [ ] Keine KRITISCH-Findings offen
- [ ] Warnungen adressiert oder begründet
- [ ] Keine Duplikate erkannt

### Freigabe
- [ ] Review-Ergebnis dokumentiert
- [ ] Freigabe erteilt / Nacharbeit erforderlich
```

### 7. Gate-Entscheidung

**Freigabe-Gate:** Die FMEA gilt erst als "freigegeben", wenn:

1. **Keine KRITISCH-Findings** aus `validate_completeness` offen sind
2. **Alle Warnungen** adressiert oder mit Begründung akzeptiert sind
3. **Der Nutzer die Checkliste bestätigt** hat

**Bei Findings:**
- **KRITISCH:** Blockiert Freigabe → Fehlermodi korrigieren → erneut validieren
- **WARNUNG:** Nutzer entscheidet → akzeptieren (mit Begründung) oder korrigieren
- **HINWEIS:** Informativ, blockiert nicht

**Nach Freigabe:**
- Version einfrieren: `tools.moc_manager.freeze_version(project_id)`
- Report generieren (falls nicht aktuell): `tools.report_generator.generate_report(project_id, task_folder)`

## Feedback-Verarbeitung

Wenn der Nutzer während des Reviews S/O/D-Werte anpassen will:

```python
from tools.review import update_risk_assessment
result = update_risk_assessment(project_id, fehler_id, S=new_S, O=new_O, D=new_D,
                                 begruendung_S="...", angepasst_von="review")
```

Nach jeder Anpassung: Validierung erneut durchlaufen.

## Config
- Review-Funktionen: `tools/review.py`
- Validierung: `tools/validate_completeness.py`
- Versionsmanagement: `tools/moc_manager.py`
- Report: `tools/report_generator.py`
