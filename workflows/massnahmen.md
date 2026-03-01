# Maßnahmenoptimierung -- SOP

## Ziel
Für Fehlermodi mit RPZ >= 100 (mittel/hoch/kritisch): Technische Maßnahmen nach ABE-Hierarchie entwickeln und Restrisiko bewerten.

## Input (pro Fehlermodus)
- Fehlermodus: `fehler_id`, `fehlermodus`, `fehlerart`
- Risikobewertung: S, O, D, RPZ, Status
- Ursachen: Liste mit Herkunft und Präventionsphase
- Bestehende Controls: Welche Sensorik/Sicherheitseinrichtungen sind bereits vorhanden?
- Anlagenkontext: Prozessbedingungen, Stoffe, Design-Limits

## Laden der relevanten Fehlermodi

```python
from tools.storage import FMEAStorage
db = FMEAStorage()
high_risk = db.get_all_failure_modes_with_rpz(project_id, min_rpz=100)
```

## ABE-Hierarchie (strikt einhalten)

### A -- Vermeidung (Occurrence senken)
Eliminierung der Fehlerursache durch Design-Änderung.
- **Priorität 1** -- wird immer zuerst geprüft
- Beispiele: Druckfeste Bauweise, inhärent sichere Chemie, redundante Systeme
- Effekt: **O wird gesenkt**, S und D bleiben gleich

### B -- Entdeckung (Detection verbessern)
Sensorik und Überwachung, die den Fehler VOR dem Schadenseintritt erkennt.
- **Priorität 2** -- wenn Vermeidung nicht möglich/wirtschaftlich
- Beispiele: SIL-klassifizierte Messketten, Inline-Überwachung, automatische Abschaltung
- Effekt: **D wird gesenkt**, S und O bleiben gleich

### E -- Abschwächung (Severity begrenzen)
Folgenbegrenzung nach Fehlereinritt.
- **Priorität 3** -- letzte Option
- Beispiele: Auffangwannen, Sicherheitsventile, Sprinkleranlagen
- Effekt: **S wird gesenkt** (nur selten möglich), O und D bleiben gleich

## Analyse-Regeln

### 1. Prüfe bestehende Controls
- Welche Maßnahmen sind BEREITS vorhanden? (CurrentControls aus der DB)
- Ist eine vorhandene Maßnahme ausreichend? → Dann nur Dokumentation
- Ist eine Redundanz oder SIL-Erhöhung nötig? → Konkret benennen

### 2. Prüfe Stoffdaten
- Nutze Flammpunkte, Siedepunkte, Explosionsgrenzen aus dem Kontext
- Beispiel: "Ethylacetat hat Flammpunkt -4 °C → Zone 1 berechtigt → Ex-geschützter Sensor erforderlich"

### 3. Prüfe Präventionsphasen der Ursachen
- Ursachen mit Phase "Konzept" oder "Detaildesign" → Design-Maßnahme (Kat. A) priorisieren
- Ursachen mit Phase "Betrieb" oder "Wartung" → Entdeckung (Kat. B) oder organisatorisch

### 4. Logik-Check
- Wenn ABE-Kategorie = A → NUR O darf sinken
- Wenn ABE-Kategorie = B → NUR D darf sinken
- Wenn ABE-Kategorie = E → NUR S darf sinken (selten)
- S darf NICHT erhöht werden
- Begründe explizit, welcher Faktor warum gesenkt wird

## Output-Format (JSON)

```json
{
  "fehler_id": "KOMP-001-F1-FM1",
  "massnahme": {
    "name": "Redundanter Drucktransmitter PT-402b mit SIL-2 Verriegelung",
    "abe_kategorie": "B",
    "beschreibung": "Installation eines zweiten unabhängigen Drucktransmitters (1oo2-Auswertung) mit automatischer Abschaltung bei p > 5.5 bar, unabhängig vom Prozessleitsystem über SIS (S7-400F).",
    "ziel": "D",
    "S_neu": 8,
    "O_neu": 3,
    "D_neu": 1,
    "begruendung": "D sinkt von 2 auf 1: Zweiter unabhängiger Drucktransmitter in SIL-2 Konfiguration erkennt Drucküberschreitung zuverlässiger als einzelner PIC-402. Automatische Abschaltung über SIS-Ebene (unabhängig von DCS)."
  }
}
```

## Speichern

```python
from tools.storage import FMEAStorage
db = FMEAStorage()

db.insert_measure(
    failure_mode_id=fm_db_id,
    name="Redundanter Drucktransmitter PT-402b",
    abe_kategorie="B",
    beschreibung="...",
    ziel="D",
    S_neu=8, O_neu=3, D_neu=1,
    begruendung="..."
)
```

## Qualitätskriterien
- ABE-Hierarchie eingehalten (A vor B vor E)
- Logik-Check bestanden (nur der richtige Faktor gesenkt)
- Konkrete technische Maßnahme (nicht "Sensor installieren" sondern "SIL-2 Drucktransmitter Typ K mit 1oo2-Auswertung")
- Bezug zu vorhandener Sensorik und Sicherheitseinrichtungen
- Restrisiko-Bewertung plausibel und begründet
