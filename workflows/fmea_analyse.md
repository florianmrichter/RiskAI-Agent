# FMEA-Analyse -- Haupt-SOP (Interaktiv)

## Ziel
Vollständige FMEA-Analyse einer verfahrenstechnischen Anlage nach AIAG-VDA Standard.
**Human-in-the-Loop**: Nach jedem Analyseschritt präsentierst du dem Nutzer die Ergebnisse und wartest auf Freigabe, bevor du weitermachst.

## Voraussetzungen
- Anlagendaten als JSON (direkt oder im n8n-Workflow-Export)
- Python 3.9+ mit sqlite3

## Pipeline-Übersicht

```
Schritt 1: Daten laden        → Tool: load_plant_data.py
           ↓ REVIEW: Datenzusammenfassung zeigen
Schritt 2: Strukturanalyse    → Tool: structure_analysis.py
           ↓ REVIEW: Komponentenliste freigeben
Schritt 3: Funktionsanalyse   → Agent (pro Komponente) → Workflow: funktionsanalyse.md
           ↓ REVIEW: Funktionen pro Komponente freigeben
Schritt 4: Fehleranalyse      → Agent (pro Funktion) → Workflow: fehleranalyse.md
           ↓ REVIEW: Jeden Fehlermodus einzeln durchgehen (S/O/D besprechen)
Schritt 5: RPZ + Validierung  → Tool: rpz_calculator.py + Konsistenz-Check
           ↓ REVIEW: Risiko-Ranking freigeben
Schritt 6: Maßnahmen          → Agent (RPZ >= mittel) → Workflow: massnahmen.md
           ↓ REVIEW: Maßnahmen + Restrisiko freigeben
Schritt 7: Report             → Tool: report_generator.py
```

---

## Schritt 1: Anlagendaten laden

```python
from tools.load_plant_data import load_plant_data
plant_data = load_plant_data("pfad/zur/datei.json")
```

### REVIEW nach Schritt 1
Präsentiere dem Nutzer eine Zusammenfassung:

```python
from tools.review import get_plant_data_review
print(get_plant_data_review(plant_data))
```

Zeige:
- Anlagenname, Standort, Betriebsart
- Anzahl Systeme, Equipment, MSR-Stellen, Sicherheitseinrichtungen
- Einsatzstoffe mit GHS-Einstufung
- Erkannte Warnungen oder fehlende Daten

**Frage an den Nutzer:**
> "Hier ist die Zusammenfassung der geladenen Anlagendaten. Sind alle Systeme und Stoffe korrekt erkannt? Fehlt etwas?"

**WARTE auf Freigabe** bevor du weitermachst.

---

## Schritt 2: Strukturanalyse

```python
from tools.structure_analysis import analyze_structure, save_components_to_db
from tools.storage import FMEAStorage

db = FMEAStorage()
project_id = db.create_project("Projektname", "Anlagenname")
components = analyze_structure(plant_data)
save_components_to_db(components, project_id)
```

### REVIEW nach Schritt 2
Präsentiere die Komponentenliste:

```python
from tools.review import get_structure_review
print(get_structure_review(project_id))
```

Zeige pro System:
- Systemname und Typ
- Anzahl Equipment / MSR / Sicherheitseinrichtungen
- Komponentenliste mit KOMP-IDs und Typ-Zuordnungen

**Frage an den Nutzer:**
> "Ich habe X Komponenten in Y Systemen erkannt. Sind die Zuordnungen korrekt? Gehört eine Komponente in ein anderes System?"

**WARTE auf Freigabe.** Bei Korrekturen: `review.update_component(...)` aufrufen.

---

## Schritt 3: Funktionsanalyse (Agent)

Für jede Komponente: Lies `workflows/funktionsanalyse.md` und führe die Analyse durch.

**Kontext-Management:**
- Verarbeite Komponenten EINZELN oder in kleinen Gruppen (max. 5)
- Lade pro Komponente: Name, Typ, Parameter, lean_context
- Speichere jede Funktion sofort in die DB

**Reihenfolge:** Systeme zuerst, dann Equipment, dann MSR, dann Sicherheit.

### REVIEW nach Schritt 3
Präsentiere die Funktionen pro Komponente:

```python
from tools.review import get_function_review
print(get_function_review(project_id))
```

Zeige pro Komponente:
- Komponentenname
- Alle identifizierten Funktionen (Haupt- und Nebenfunktionen)
- Anforderungen mit messbaren Grenzwerten

**Frage an den Nutzer:**
> "Hier sind die identifizierten Funktionen für [Komponente]. Fehlt eine wichtige Funktion? Sind die Anforderungen realistisch?"

**WARTE auf Freigabe.** Bei Ergänzungen: Funktion in DB einfügen.

---

## Schritt 4: Fehleranalyse (Agent) -- WICHTIGSTER REVIEW-PUNKT

Für jede Funktion: Lies `workflows/fehleranalyse.md` und führe die Analyse durch.

**Vorbereitung:**
1. Lade Fehlervorlagen: `from tools.failure_templates import get_templates_for_component`
2. Lade den Kontext der Komponente aus der DB
3. Lade die FMEA-Konfiguration: `from config.fmea_standards import FMEA_CONFIG`

**Pro Funktion erzeugen:**
- FailureModes (WAS geht schief?)
- FailureCauses (WARUM? + Herkunft + Präventionsphase)
- FailureEffects (Konsequenzen in 4 Dimensionen)
- CurrentControls (WAS ist bereits vorhanden?)
- RiskAssessment (S/O/D mit Begründung)

### REVIEW nach Schritt 4 -- Risiko-Walkthrough
**Gehe jeden Fehlermodus EINZELN mit dem Nutzer durch:**

```python
from tools.review import get_risk_review
print(get_risk_review(project_id, fehler_id="KOMP-001-F2-FM1"))
```

Für jeden Fehlermodus zeigen:
1. Fehlermodus-Beschreibung
2. Ursachen (mit Herkunft)
3. Folgen (4 Dimensionen)
4. Bestehende Controls
5. **S/O/D-Bewertung mit Begründung** -- das ist der Kernpunkt
6. RPZ und vorläufige Klassifizierung

**Frage an den Nutzer:**
> "**F2-FM1: Flanschleckage am Mannloch**
> S=8 (Verbrennungsgefahr), O=4 (~alle 2 Jahre), D=6 (nur visuelle Prüfung)
> RPZ = 192 (MITTEL)
>
> Stimmst du zu? Möchtest du einen Wert anpassen?"

**WARTE auf Freigabe pro Fehlermodus.** Bei Anpassungen:

```python
from tools.review import update_risk_assessment
update_risk_assessment(project_id, "KOMP-001-F2-FM1",
    O=5, begruendung_O="Nutzer: 3 Leckagen im letzten Jahr",
    angepasst_von="nutzer")
```

---

## Schritt 5: RPZ-Berechnung + Validierung

```python
from tools.rpz_calculator import calculate_and_store_rpz
stats = calculate_and_store_rpz(project_id)
```

Automatisch:
- RPZ = S × O × D
- Klassifizierung nach `config/fmea_standards.py` (300/200/100)
- Safety-Guard-Overrides (Ex-Schutz, Gefahrstoffe, Sicherheitsbauteile)
- FMEA-Sonderregeln (B >= 9, E >= 9 + B >= 7)

### Konsistenz-Check (Validierung)
Führe den Validierungs-Workflow aus: `workflows/validierung.md`

```python
from tools.review import get_validation_report
print(get_validation_report(project_id))
```

Prüft:
- Doppelungs-Erkennung (ähnliche Fehlermodi)
- Kontext-Abgleich (Ex-Zone, Gefahrstoffe in Severity reflektiert?)
- S/O/D-Konsistenz (gleiche Fehlerart, aber verschiedene Bewertung?)
- Vollständigkeit (jede Funktion hat Fehlermodi?)
- Plausibilität (S=10 ohne Maßnahme? S=1 bei Gefahrstoff?)

### REVIEW nach Schritt 5
Präsentiere das vollständige Risiko-Ranking:

```python
from tools.review import get_ranking_review
print(get_ranking_review(project_id))
```

Zeige:
- Sortierte Risiko-Tabelle (RPZ absteigend)
- Farbcodierung (kritisch/hoch/mittel/niedrig)
- Validierungs-Ergebnisse und Warnungen
- Zusammenfassung: X kritisch, Y hoch, Z mittel, W niedrig

**Frage an den Nutzer:**
> "Hier ist das vollständige Risiko-Ranking. Gibt es Risiken, die du anders einordnen würdest? Sollen wir Validierungswarnungen besprechen?"

**WARTE auf Freigabe.**

---

## Schritt 6: Maßnahmenoptimierung (Agent)

Nur für Fehlermodi mit RPZ >= mittel (gemäß `config/fmea_standards.py`).
Lies `workflows/massnahmen.md` und entwickle Maßnahmen nach ABE-Hierarchie.

### REVIEW nach Schritt 6
Präsentiere Maßnahmen mit Vorher/Nachher-Vergleich:

```python
from tools.review import get_measure_review
print(get_measure_review(project_id))
```

Zeige pro Maßnahme:
- Fehlermodus-Referenz
- Maßnahmentyp (A/B/E) und Beschreibung
- **Vorher:** S=X, O=Y, D=Z → RPZ=ABC (STATUS)
- **Nachher:** S=X', O=Y', D=Z' → RPZ=ABC' (STATUS')
- Begründung für die Verbesserung

**Frage an den Nutzer:**
> "Hier sind die vorgeschlagenen Maßnahmen. Sind sie realistisch umsetzbar? Gibt es Maßnahmen, die ihr bereits plant?"

**WARTE auf Freigabe.**

---

## Schritt 7: Report

```python
from tools.report_generator import generate_report
pdf_path = generate_report(project_id)
```

Der Report enthält automatisch:
- Alle Analyseergebnisse
- Audit-Trail: Welche Bewertungen vom Nutzer angepasst wurden
- Zeitstempel der Freigaben

---

## Kontext-Management-Regeln

1. **Nie den gesamten Datensatz auf einmal laden** -- immer komponentenweise
2. **Nach jedem Analyseschritt speichern** -- bei Abbruch geht nichts verloren
3. **Kontext pro Komponente** enthält nur: eigene Parameter + Systemkontext (Design-Limits, Prozessbedingungen, Stoffe, Sensoren, Sicherheitseinrichtungen)
4. **Zwischen Schritten: DB als Wahrheitsquelle** -- nicht den Agent-Kontext
5. **Reviews sind Pflicht** -- nie einen Schritt überspringen, auch wenn der Nutzer drängelt
6. **Nutzer-Feedback dokumentieren** -- jede Anpassung wird mit Quelle "nutzer" markiert

## Fehlerbehandlung

- Tool wirft Fehler → Fehlermeldung lesen, Tool-Code prüfen, fixen, erneut ausführen
- Agent-Analyse unvollständig → Fehlende Felder identifizieren, Komponente erneut analysieren
- Validierungswarnungen → Dem Benutzer zeigen, gemeinsam entscheiden
- Nutzer widerspricht KI-Bewertung → **Nutzer hat Recht** -- Wert anpassen und Begründung dokumentieren
