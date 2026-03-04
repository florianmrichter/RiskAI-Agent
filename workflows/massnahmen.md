# Maßnahmenoptimierung -- SOP

## WICHTIG: Keine generische Maßnahmen-Logik
Maßnahmen werden **ausschließlich durch Einzelfall-Analyse** definiert. Kein Keyword-Matching, keine Fallback-Platzhalter. Der Agent analysiert jeden Fehlermodus mit RPZ >= 100 einzeln und formuliert konkrete, komponentenspezifische Maßnahmen. **Frische Bewertung:** Keine Wiederverwendung vordefinierter Maßnahmen aus früheren Analysen.

## Ziel
Für Fehlermodi mit RPZ >= 100 (mittel/hoch/kritisch): Mehrere Maßnahmen nach dem **STOP-Prinzip** und der **ABE-Hierarchie** entwickeln, Restrisiko pro Maßnahme bewerten, und dem Benutzer zur Auswahl vorlegen.

## Input (pro Fehlermodus)
- Fehlermodus: `fehler_id`, `fehlermodus`, `fehlerart`
- Risikobewertung: S, O, D, RPZ, Status
- Ursachen: Liste mit Herkunft und Präventionsphase
- Bestehende Controls: Welche Sensorik/Sicherheitseinrichtungen sind bereits vorhanden?
- Anlagenkontext: Prozessbedingungen, Stoffe, Design-Limits

## Ablauf: Fehlermodi laden → Generieren/Analysieren → Einspielen

1. **Fehlermodi laden** (RPZ >= 100 oder Status hoch/kritisch):
```python
from tools.storage import FMEAStorage
db = FMEAStorage()
high_risk = db.get_failure_modes_needing_measures(project_id)
db.close()
```

2. **Maßnahmen generieren:** `python tools/generate_measures.py --project-id 1` lädt projektspezifische Generatoren aus `tasks/{task_folder}/measures_explicit.py` oder `config/measures_explicit.py`. Fehlermodi ohne Generator bleiben für Agent-Analyse.

3. **Pro Fehlermodus ohne Generator:** Agent analysiert (STOP, ABE, S_neu/O_neu/D_neu), erstellt Maßnahmen-Liste

4. **Einspielen** mit `tools/insert_measures.insert_measures_for_fehlermodus` (Agent übergibt Daten direkt)

5. **Report neu generieren (Pflicht):** Nach jedem Einspielen von Maßnahmen – ob über `generate_measures` oder manuell über `insert_measures_for_fehlermodus` – den FMEA-Report sofort neu erzeugen, damit das PDF die aktuellen Maßnahmen enthält:
   ```python
   from tools.report_generator import generate_report
   generate_report(project_id, task_folder="Risikoanalyse/Ethylacetatproduktion_20TA42")
   ```
   Ohne diesen Schritt ist die Maßnahmenphase nicht abgeschlossen.

## Zweidimensionale Klassifizierung: ABE x STOP

Jede Maßnahme wird auf zwei Achsen klassifiziert:

### Achse 1: ABE-Hierarchie (Wirkung im FMEA-Kontext)

Die ABE-Hierarchie bestimmt, **welchen Risikofaktor** eine Maßnahme senkt. Die Reihenfolge A → B → E gibt die Prüfpriorität vor.

#### A -- Vermeidung (Occurrence senken)
Eliminierung der Fehlerursache durch Design-Änderung.
- **Priorität 1** -- wird immer zuerst geprüft
- Beispiele: Druckfeste Bauweise, inhärent sichere Chemie, redundante Systeme
- Effekt: **O wird gesenkt**, S und D bleiben gleich

#### B -- Entdeckung (Detection verbessern)
Sensorik und Überwachung, die den Fehler VOR dem Schadenseintritt erkennt.
- **Priorität 2** -- wenn Vermeidung nicht möglich/wirtschaftlich
- Beispiele: SIL-klassifizierte Messketten, Inline-Überwachung, automatische Abschaltung
- Effekt: **D wird gesenkt**, S und O bleiben gleich

#### E -- Abschwächung (Severity begrenzen)
Folgenbegrenzung nach Fehlereintritt.
- **Priorität 3** -- letzte Option
- Beispiele: Auffangwannen, Sicherheitsventile, Sprinkleranlagen
- Effekt: **S wird gesenkt** (nur selten möglich), O und D bleiben gleich

### Achse 2: STOP-Prinzip (Art der Maßnahme)

Das STOP-Prinzip bestimmt, **welche Art von Maßnahme** ergriffen wird. Die Reihenfolge S → T → O → P gibt die Wirksamkeitshierarchie vor.

#### S -- Substitution
Gefährliches durch weniger Gefährliches ersetzen.
- Höchste Wirksamkeit -- eliminiert die Gefährdung an der Quelle
- Beispiele: Ersatz eines brennbaren Lösemittels durch ein nicht-brennbares, Verwendung eines weniger toxischen Katalysators, Design-Änderung die Druckbelastung vermeidet
- Typische ABE-Kombination: **A** (Vermeidung durch Substitution)

#### T -- Technisch
Technische Schutzeinrichtungen installieren.
- Hohe Wirksamkeit -- wirkt unabhängig vom menschlichen Verhalten
- Beispiele: SIL-klassifizierte Sicherheitsventile, redundante Drucktransmitter, automatische Abschaltungen, Berstscheiben, Auffangwannen, Ex-Schutz
- Typische ABE-Kombination: **B** (Entdeckung) oder **E** (Abschwächung)

#### O -- Organisatorisch
Betriebliche Regelungen und Prozesse.
- Mittlere Wirksamkeit -- abhängig von Einhaltung durch Personal
- Beispiele: Wartungspläne, Betriebsanweisungen, Schulungsprogramme, Notfallprozeduren, Checklisten, Freigabeverfahren, regelmäßige Sicherheitsaudits
- Typische ABE-Kombination: **B** (Entdeckung) oder **A** (Vermeidung durch Prozessänderung)

#### P -- Persönlich
Persönliche Schutzausrüstung und Verhaltensregeln.
- Niedrigste Wirksamkeit -- letzte Verteidigungslinie
- Beispiele: Chemikalienbeständige Schutzkleidung, Atemschutz, Gesichtsschutz, Gehörschutz, Zugangskontrollen, persönliche Gaswarner
- Typische ABE-Kombination: **E** (Abschwächung der persönlichen Folgen)

## Ablauf: Initiale Generierung + Iterative Vertiefung

### Phase 1: Initiale Generierung

Für jeden Fehlermodus mit RPZ >= 100:

1. Prüfe für **jede STOP-Kategorie** (S, T, O, P), ob eine sinnvolle Maßnahme möglich ist
2. Generiere **mindestens eine Maßnahme pro STOP-Kategorie**, wenn technisch/fachlich begründbar
3. Ordne jeder Maßnahme die passende **ABE-Kategorie** zu
4. Bewerte für jede Maßnahme das **Restrisiko** (S_neu, O_neu, D_neu)
5. Erstelle eine **Abdeckungsbewertung**: Welche STOP-Kategorien sind gut abgedeckt, wo besteht Potenzial für mehr?

### Phase 2: Hybrid-Feedback (iterativ)

Nach der initialen Generierung:

1. **Präsentiere** dem Benutzer alle Maßnahmen mit der Abdeckungsbewertung
2. **Empfehle**, in welchen STOP-Kategorien eine Vertiefung sinnvoll wäre (mit Begründung)
3. **Benutzer entscheidet**:
   - "Ausreichend" → Maßnahmen speichern
   - "Mehr in Kategorie T" → Weitere technische Maßnahmen generieren
   - "Mehr in Kategorie O und P" → Weitere organisatorische und persönliche Maßnahmen generieren
4. Bei Vertiefung: **Mehrere Varianten** pro STOP-Kategorie generieren (z.B. günstige vs. umfassende Lösung, unterschiedliche Wirkungsgrade)
5. Dieser Zyklus kann **wiederholt** werden, bis der Benutzer zufrieden ist

## Analyse-Regeln

### 1. Prüfe bestehende Controls
- Welche Maßnahmen sind BEREITS vorhanden? (CurrentControls aus der DB)
- Ist eine vorhandene Maßnahme ausreichend? → Dann nur Dokumentation
- Ist eine Redundanz oder SIL-Erhöhung nötig? → Konkret benennen

### 2. Prüfe Stoffdaten
- Nutze Flammpunkte, Siedepunkte, Explosionsgrenzen aus dem Kontext
- Beispiel: "Ethylacetat hat Flammpunkt -4 °C → Zone 1 berechtigt → Ex-geschützter Sensor erforderlich"

### 3. Prüfe Präventionsphasen der Ursachen
- Ursachen mit Phase "Konzept" oder "Detaildesign" → Design-Maßnahme (Kat. A + STOP-S) priorisieren
- Ursachen mit Phase "Betrieb" oder "Wartung" → Entdeckung (Kat. B + STOP-T/O) oder organisatorisch

### 4. Logik-Check (ABE-Konsistenz)
- Wenn ABE-Kategorie = A → NUR O darf sinken
- Wenn ABE-Kategorie = B → NUR D darf sinken
- Wenn ABE-Kategorie = E → NUR S darf sinken (selten)
- S darf NICHT erhöht werden
- Begründe explizit, welcher Faktor warum gesenkt wird

### 5. STOP-Vollständigkeit
- Prüfe für jede STOP-Kategorie, ob eine sinnvolle Maßnahme existiert
- Wenn keine Maßnahme in einer Kategorie möglich ist, begründe warum
- Substitution (S) ist oft bei bestehenden Anlagen eingeschränkt → trotzdem prüfen

## Output-Format Phase 1 (JSON)

```json
{
  "fehler_id": "<fehler_id>",
  "massnahmen": [
    {
      "name": "Ersatz von Ethanol durch weniger flüchtigen Ester",
      "stop_kategorie": "S",
      "abe_kategorie": "A",
      "beschreibung": "Substitution des Ethanols (Flammpunkt 13 °C) durch Isopropylacetat (Flammpunkt 18 °C) als Lösemittel. Reduziert die Zündgefahr im Normalbetrieb.",
      "ziel": "O",
      "S_neu": 8,
      "O_neu": 2,
      "D_neu": 3,
      "begruendung": "O sinkt von 4 auf 2: Substitution eliminiert die Hauptursache der erhöhten Brandgefahr durch höheren Flammpunkt.",
      "iteration": 1
    },
    {
      "name": "Redundanter Drucktransmitter PT-402b mit SIL-2 Verriegelung",
      "stop_kategorie": "T",
      "abe_kategorie": "B",
      "beschreibung": "Installation eines zweiten unabhängigen Drucktransmitters (1oo2-Auswertung) mit automatischer Abschaltung bei p > 5.5 bar, unabhängig vom Prozessleitsystem über SIS (S7-400F).",
      "ziel": "D",
      "S_neu": 8,
      "O_neu": 3,
      "D_neu": 1,
      "begruendung": "D sinkt von 3 auf 1: Zweiter unabhängiger Drucktransmitter in SIL-2 Konfiguration erkennt Drucküberschreitung zuverlässiger als einzelner PIC-402.",
      "iteration": 1
    },
    {
      "name": "Monatliche Druckprüfung mit dokumentierter Checkliste",
      "stop_kategorie": "O",
      "abe_kategorie": "B",
      "beschreibung": "Einführung einer monatlichen Druckprüfung aller drucktragenden Bauteile mit dokumentierter Checkliste, Vier-Augen-Prinzip und Eskalationsprozess bei Abweichungen.",
      "ziel": "D",
      "S_neu": 8,
      "O_neu": 3,
      "D_neu": 4,
      "begruendung": "D sinkt von 6 auf 4: Regelmäßige Prüfung erhöht die Entdeckungswahrscheinlichkeit von schleichender Degradation.",
      "iteration": 1
    },
    {
      "name": "Chemikalienbeständige Schutzkleidung Kat. III",
      "stop_kategorie": "P",
      "abe_kategorie": "E",
      "beschreibung": "Bereitstellung und Tragepflicht von chemikalienbeständiger Schutzkleidung (EN 14605), Gesichtsschutzschild und Chemikalienschutzhandschuhen im Reaktorbereich.",
      "ziel": "S",
      "S_neu": 5,
      "O_neu": 3,
      "D_neu": 3,
      "begruendung": "S sinkt von 8 auf 5: PSA schwächt die persönlichen Folgen einer Medienfreisetzung ab.",
      "iteration": 1
    }
  ],
  "abdeckung": {
    "S": {"vorhanden": true, "anzahl": 1, "empfehlung": "Ausreichend -- Substitution wurde geprüft."},
    "T": {"vorhanden": true, "anzahl": 1, "empfehlung": "Vertiefung möglich: Weitere Redundanz-Optionen oder Berstscheibe denkbar."},
    "O": {"vorhanden": true, "anzahl": 1, "empfehlung": "Vertiefung möglich: Notfallprozedur und Schulungsprogramm ergänzen."},
    "P": {"vorhanden": true, "anzahl": 1, "empfehlung": "Ausreichend -- PSA-Pflicht definiert."}
  },
  "gesamt_empfehlung": "Grundabdeckung in allen STOP-Kategorien vorhanden. Vertiefung in T und O empfohlen."
}
```

## Output-Format Phase 2 -- Vertiefung (JSON)

Bei Benutzer-Feedback "Mehr in Kategorie T":

```json
{
  "fehler_id": "<fehler_id>",
  "neue_massnahmen": [
    {
      "name": "Automatische Druckentlastung über PSV mit Auffangbehälter",
      "stop_kategorie": "T",
      "abe_kategorie": "E",
      "beschreibung": "Installation eines Proportional-Sicherheitsventils (PSV, Typ 4x) am Reaktorkopf mit Ableitung in einen 5 m³ Auffangbehälter. Ansprechdruck 5.0 bar.",
      "ziel": "S",
      "S_neu": 4,
      "O_neu": 3,
      "D_neu": 1,
      "begruendung": "S sinkt von 8 auf 4: PSV begrenzt den maximalen Systemdruck und verhindert Bersten. Auffangbehälter verhindert Medienfreisetzung.",
      "iteration": 2
    },
    {
      "name": "SIL-3 Drucküberwachung mit 2oo3-Voting",
      "stop_kategorie": "T",
      "abe_kategorie": "B",
      "beschreibung": "Drei unabhängige Drucktransmitter in 2oo3-Voting-Konfiguration mit SIL-3 Nachweis. Automatische Reaktorabschaltung über dediziertes SIS.",
      "ziel": "D",
      "S_neu": 8,
      "O_neu": 3,
      "D_neu": 1,
      "begruendung": "D sinkt auf 1: Höhere SIL-Stufe als Alternative zur SIL-2 Lösung. Höhere Verfügbarkeit durch 2oo3-Architektur.",
      "iteration": 2
    }
  ]
}
```

## Speichern

**Tool:** `tools/insert_measures.insert_measures_for_fehlermodus` – Agent übergibt Maßnahmen-Daten direkt, kein Lesen aus Config.

```python
from tools.insert_measures import insert_measures_for_fehlermodus

massnahmen = [
    {
        "name": "Redundanter Drucktransmitter PT-402b",
        "abe_kategorie": "B",
        "stop_kategorie": "T",
        "beschreibung": "Installation eines zweiten unabhängigen Drucktransmitters (1oo2-Auswertung)...",
        "ziel": "D",
        "S_neu": 8, "O_neu": 3, "D_neu": 1,
        "begruendung": "D sinkt von 3 auf 1: Zweiter Transmitter erkennt Drucküberschreitung zuverlässiger.",
        "iteration": 1
    },
    # ... weitere Maßnahmen
]
result = insert_measures_for_fehlermodus(
    project_id=project_id,
    fehler_id="<fehler_id>",
    measures=massnahmen
)
# result = {"inserted": n}
```

Optional: Agent kann Maßnahmen in `tasks/{task_folder}/measures_explicit.py` dokumentieren (Audit-Trail), bevor er `insert_measures_for_fehlermodus` aufruft. Kein automatisches Lesen durch Tools.

## Qualitätskriterien
- ABE-Hierarchie eingehalten (A vor B vor E)
- STOP-Prinzip angewendet (S vor T vor O vor P als Prüfreihenfolge)
- Jede STOP-Kategorie geprüft (ggf. mit Begründung warum keine Maßnahme möglich)
- Logik-Check bestanden (nur der richtige Faktor gesenkt gemäß ABE)
- Konkrete Maßnahme (nicht "Sensor installieren" sondern "SIL-2 Drucktransmitter Typ K mit 1oo2-Auswertung")
- Bezug zu vorhandener Sensorik und Sicherheitseinrichtungen
- Restrisiko-Bewertung plausibel und begründet pro Maßnahme
- Abdeckungsbewertung für den Benutzer erstellt
