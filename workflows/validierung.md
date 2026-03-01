# Validierung & Konsistenz-Check -- SOP

## Ziel
Abschließende Prüfung der gesamten FMEA-Analyse auf Konsistenz, Vollständigkeit, Doppelungen und Plausibilität. Wird nach der RPZ-Berechnung und vor der Maßnahmenentwicklung durchgeführt.

## Voraussetzungen
- Fehleranalyse (Schritt 4) vollständig abgeschlossen
- RPZ-Berechnung (Schritt 5) durchgeführt
- Alle Daten in der DB gespeichert

## Durchführung

### Tool-Aufruf

```python
from tools.review import get_validation_report
report = get_validation_report(project_id)
print(report)
```

### Automatische Prüfungen

Das Validierungstool prüft folgende Aspekte:

#### 1. Vollständigkeit
- Hat jede Funktion mindestens einen Fehlermodus?
- Haben alle Fehlermodi Ursachen, Folgen und Controls?
- Sind alle S/O/D-Werte begründet?

#### 2. Plausibilität
- S >= 9 ohne definierte Maßnahmen → **Warnung**: Sicherheitsrelevant, Maßnahme erforderlich
- Status "kritisch" oder "hoch" ohne Maßnahmen → **Warnung**
- S = 1 bei Fehlermodus mit Gefahrstoff-Freisetzung → **Unplausibel**

#### 3. Konsistenz
- Gleiche Fehlerart (z.B. "Mechanisch"), aber stark abweichende S-Werte (Differenz >= 5)
- → Begründung erforderlich, warum der gleiche Fehlertyp sehr unterschiedlich bewertet wird

#### 4. Doppelungserkennung
- Fehlermodi mit > 70% Wortübereinstimmung in der Beschreibung
- → Prüfen ob es sich um echte Doppelungen handelt oder unterschiedliche Ausprägungen

#### 5. Sonderregeln (AIAG-VDA)
- B >= 9 und Status nicht mindestens "hoch" → **Sonderregel greift**
- D >= 9 und B >= 7 und Status nicht "kritisch" → **Sonderregel greift**
- Diese Regeln sind in `config/fmea_standards.py` definiert

#### 6. Kontext-Abgleich (Agent-Aufgabe)
Die folgenden Prüfungen führt der Agent manuell durch, weil sie kontextabhängig sind:

- **Ex-Zone Abgleich:** Wenn die Anlage in Ex-Zone 1 steht, müssen ALLE Leckage-Fehlermodi dies in der Severity reflektieren (typischerweise S >= 8)
- **Gefahrstoff-Abgleich:** Wenn Stoffe mit Flammpunkt < 0°C eingesetzt werden (z.B. Ethylacetat), muss das in Leckage- und Temperatur-Fehlermodi berücksichtigt sein
- **SIL-Level Abgleich:** Wenn SIL-bewertete Sicherheitseinrichtungen vorhanden sind, müssen deren Ausfälle explizit als Fehlermodi betrachtet werden
- **Upstream/Downstream:** Fehler in vorgelagerten Systemen (z.B. Dosiersystem) können Fehler im nachgelagerten System (z.B. Reaktor) verursachen -- ist das berücksichtigt?

## Umgang mit Ergebnissen

### Bei Warnungen

1. Jeden Warnpunkt dem Nutzer vorlegen
2. Gemeinsam entscheiden: Ist die Warnung berechtigt?
3. Falls ja: Bewertung anpassen via `review.update_risk_assessment()`
4. Falls nein: Begründung dokumentieren (wird im Audit-Trail gespeichert)

### Bei Sonderregeln

Sonderregeln werden automatisch angewendet. Der Nutzer wird informiert:

> "Für Fehlermodus F2-FM1 wurde die Sonderregel 'B >= 9 → mindestens hoch' angewendet.
> Aktueller Status wird von 'mittel' auf 'hoch' angehoben."

### Bei Doppelungen

1. Dem Nutzer beide Fehlermodi zeigen
2. Entscheidung: Zusammenführen oder als separate Risiken beibehalten?
3. Falls zusammenführen: Einen Fehlermodus löschen, den anderen anpassen

## Integration in die Pipeline

Der Validierungs-Check ist Teil von Schritt 5 in `workflows/fmea_analyse.md`.
Er wird **nach** der RPZ-Berechnung und **vor** dem Review des Risiko-Rankings durchgeführt.

```
Schritt 5a: RPZ-Berechnung (Tool: rpz_calculator.py)
Schritt 5b: Validierung (Tool: review.get_validation_report())
Schritt 5c: REVIEW: Risiko-Ranking + Validierungsergebnisse dem Nutzer zeigen
```
