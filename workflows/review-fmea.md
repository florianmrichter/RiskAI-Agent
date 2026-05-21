# Review-Workflow: FMEA-Qualitätsprüfung und Freigabe

## Zweck

Dieser Workflow beschreibt die standardisierte Qualitätsprüfung einer abgeschlossenen FMEA-Risikoanalyse. Er wird **nach Abschluss der FMEA** und **vor der Report-Freigabe** durchgeführt.

## Wann aufrufen

- Die FMEA-Analyse ist abgeschlossen (alle Komponenten bearbeitet)
- Maßnahmen sind eingespielt
- Der Nutzer will den Report freigeben oder die Analyse abschließen
- Vor einer MoC-Versionierung (Version einfrieren)

## Voraussetzungen

- Projekt existiert in `tasks/Risikoanalyse/{projekt}/`
- FMEA-Daten sind in `data/fmea.db` eingespielt
- `workflow_state.json` zeigt Status ≥ "Maßnahmen abgeschlossen"

## Review-Tool: `tools/review.py`

Das Review-Tool bietet sieben Prüfschritte, die sequentiell durchlaufen werden:

### Schritt 1: Anlagendaten-Review

**Funktion:** `get_plant_data_review(plant_data)`

**Prüft:**
- Systeme, Equipment, MSR-Technik, Sicherheitseinrichtungen vollständig
- Einsatzstoffe und Produkte definiert
- Warnungen bei fehlenden Daten (keine MSR, keine Sicherheitseinrichtungen)

**Aktion bei Warnung:** Anlagendaten ergänzen via `tools/load_plant_data.update_plant_data()`.

### Schritt 2: Struktur-Review

**Funktion:** `get_structure_review(project_id)`

**Prüft:**
- Alle Komponenten pro System aufgelistet
- Kategorisierung korrekt (Equipment, MSR, Sicherheit)
- Keine Systeme ohne Komponenten

**Aktion bei Warnung:** Fehlende Komponenten nacherfassen.

### Schritt 3: Funktions-Review

**Funktion:** `get_function_review(project_id)`

**Prüft:**
- Jede Komponente hat mindestens eine Funktion
- Haupt-/Nebenfunktionen sinnvoll zugeordnet
- Anforderungen (Soll-Werte) plausibel

**Aktion bei Warnung:** Funktionen ergänzen oder korrigieren.

### Schritt 4: Risikobewertungs-Review

**Funktion:** `get_risk_review(project_id)` (Detailansicht) + `get_ranking_review(project_id)` (Gesamtübersicht)

**Prüft:**
- S/O/D-Werte im Kontext (Nachbarwerte werden angezeigt — eine Stufe höher und niedriger)
- Sonderregeln korrekt angewendet (S>=9 → mindestens HOCH; D>=9 und S>=7 → KRITISCH)
- RPZ-Treiber-Analyse: Welcher Faktor treibt das Risiko? Ist das plausibel?
- Begründungen vorhanden (begruendung_S, begruendung_O, begruendung_D)
- Konsistenz: Gleiche Fehlerarten sollten ähnliche S-Werte haben (Schwankung < 5)

**Aktion bei Warnung:** S/O/D korrigieren via `update_risk_assessment()`.

### Schritt 5: Maßnahmen-Review

**Funktion:** `get_measure_review(project_id)`

**Prüft:**
- **STOP-Abdeckung:** Alle 4 Kategorien (Substitution, Technisch, Organisatorisch, Persönlich) abgedeckt?
- **ABE-Kategorisierung:** Vermeidung (A), Begrenzung (B), Entdeckung (E) korrekt zugeordnet?
- **Vorher/Nachher-Vergleich:** RPZ-Reduktion plausibel? Keine magischen Reduktionen ohne Erklärung?
- **Fehlende Maßnahmen:** Kritische/hohe FMs ohne Maßnahmen?
- **Iterationen:** Maßnahmen mit Iteration > 1 auf Konsistenz prüfen

**Aktion bei Warnung:** Maßnahmen ergänzen oder anpassen.

### Schritt 6: Automatische Validierung

**Funktion:** `get_validation_report(project_id)` + `validate_completeness(project_id, task_folder)`

**Prüft automatisch:**
- Funktionen ohne Fehlermodi
- Hohe Severity (S>=9) ohne Maßnahmen
- Kritische/hohe RPZ-Status ohne Maßnahmen
- Fehlende STOP-Kategorien bei kritischen/hohen FMs
- S-Wert-Schwankungen bei gleicher Fehlerart
- Mögliche Duplikate (>70% Wortübereinstimmung)
- Sonderregeln-Verletzungen
- S/O/D-Plausibilität gegen Safety-Overrides und CCPS/OREDA
- Cross-FM-Alignment (Systeme/Gefahrstoffe ohne FMs)

### Schritt 7: Holistische Prüfung (Agent-Reasoning)

Nicht automatisierbar — der Agent bewertet:
- Ist das Gesamtbild stimmig?
- Sind die Proportionen der Bewertungen nachvollziehbar?
- Gibt es Lücken im Sicherheitskonzept?
- Fehlen Querverbindungen zwischen Systemen?

## Umgang mit Findings

### Klassifizierung

| Typ | Bedeutung | Aktion |
|---|---|---|
| **KRITISCH** | Blockiert Freigabe | FM korrigieren, erneut validieren |
| **WARNUNG** | Nutzer-Entscheidung erforderlich | Akzeptieren (mit Begründung) oder korrigieren |
| **HINWEIS** | Informativ | Zur Kenntnis nehmen, nicht blockierend |

### Eskalationslogik

1. **KRITISCH-Finding gefunden:** Review stoppt → Finding dem Nutzer zeigen → Korrektur durchführen → Validierung wiederholen
2. **Nur WARNUNGEN:** Alle Warnungen auflisten → Nutzer entscheidet pro Warnung: korrigieren oder akzeptieren (mit Begründung dokumentieren)
3. **Keine Findings:** Direkt zur Freigabe

### Korrekturschleife

```
Finding erkannt → FM korrigieren → RPZ neu berechnen → erneut validieren → bis keine KRITISCH-Findings
```

Maximal 3 Iterationen. Falls nach 3 Iterationen noch KRITISCH-Findings offen: Eskalation an den Nutzer mit vollständiger Auflistung.

## Freigabe-Prozess

### Gate-Bedingungen (alle müssen erfüllt sein)

1. Keine offenen KRITISCH-Findings
2. Alle WARNUNGEN adressiert (korrigiert oder mit Begründung akzeptiert)
3. Review-Checkliste vom Nutzer bestätigt
4. Report ist aktuell (nach letzter Änderung neu generiert)

### Nach Freigabe

1. **Version einfrieren:** `tools.moc_manager.freeze_version(project_id)` — erstellt JSON-Snapshot, setzt `frozen=1`
2. **Report generieren** (falls nicht aktuell): `tools.report_generator.generate_report(project_id, task_folder)`
3. **State aktualisieren:** Review-Status und Freigabe-Datum im `workflow_state.json` dokumentieren

### Ohne Freigabe (Nacharbeit)

1. Offene Findings dokumentieren
2. Betroffene Fehlermodi markieren
3. Zurück an `fmea-risikoanalyse`-Skill zur Nachbearbeitung
4. Nach Nacharbeit: Review erneut durchlaufen

## Tools

- `tools/review.py` — Alle Review-Funktionen (Struktur, Risiko, Maßnahmen, Validierung, Feedback)
- `tools/validate_completeness.py` — Erweiterte Validierung (S/O/D-Plausibilität, Cross-FM-Alignment)
- `tools/moc_manager.freeze_version(project_id)` — Version einfrieren nach Freigabe
- `tools/report_generator.generate_report(project_id, task_folder)` — Report-PDF erzeugen
