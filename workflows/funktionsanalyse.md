# Funktionsanalyse -- SOP

## Ziel
Für jede Komponente: Haupt- und Nebenfunktionen identifizieren, messbare Anforderungen ableiten.

## Input (pro Komponente)
- `komp_id`, `name`, `typ`, `kategorie`
- `parameters` (spezifische Kennwerte der Komponente)
- `lean_context` (Systemkontext: Prozessbedingungen, Design-Limits, Stoffe, Sensoren)

## Regeln

### 1. Hauptfunktion (genau 1 pro Komponente)
- ID-Format: `{komp_id}-F1`
- Aktiv formuliert: "Fördert...", "Misst...", "Hält...", "Schützt..."
- Beschreibt den PRIMÄREN Zweck der Komponente

### 2. Nebenfunktionen (1-4 pro Komponente)
- ID-Format: `{komp_id}-F2`, `{komp_id}-F3`, ...
- Typische Nebenfunktionen nach Typ:

| Komponententyp | Typische Nebenfunktionen |
|---|---|
| prozess | Dichtheit, Druckfestigkeit, Beständigkeit gegen Medien |
| thermisch | Wärmeübertragung, Temperaturkonstanz, Korrosionsbeständigkeit |
| mechanisch | Dichtheit (Wellenabdichtung), Laufruhe, Verschleißbeständigkeit |
| elektrisch/msr | Messgenauigkeit, Signalstabilität, Ex-Schutz |
| sicherheit | Verfügbarkeit, Ansprechverhalten, Prüfbarkeit |
| dosierung | Dosiergenauigkeit, Reproduzierbarkeit, Trockenlaufschutz |

### 3. Anforderungen (mindestens 1 pro Funktion)
- ID-Format: `{funktion_id}-A1`, `{funktion_id}-A2`, ...
- MÜSSEN messbar sein und sich auf konkrete Werte aus dem Kontext beziehen
- Nutze die Design-Limits und Prozessbedingungen aus `lean_context`

**Beispiel SCHLECHT:** "Druck halten"
**Beispiel GUT:** "Betriebsdruck 1 bar (Bereich 0.5-1.2 bar) halten, Design-Limit 6 bar"

## Output-Format (JSON)

```json
{
  "komponenten_id": "KOMP-001",
  "komponente": "Synthesereaktor R-101",
  "komponenten_typ": "prozess",
  "funktionen": [
    {
      "funktion_id": "KOMP-001-F1",
      "typ": "Hauptfunktion",
      "beschreibung": "Stellt den Reaktionsraum für die Fischer-Veresterung bereit",
      "anforderungen": [
        {
          "id": "KOMP-001-F1-A1",
          "parameter": "Betriebstemperatur",
          "sollwert": "80 °C (Bereich 20-100 °C, Design -20 bis 180 °C)"
        },
        {
          "id": "KOMP-001-F1-A2",
          "parameter": "Betriebsdruck",
          "sollwert": "1 bar (Bereich 0.5-1.2 bar, Design -0.9 bis 6 bar)"
        }
      ]
    },
    {
      "funktion_id": "KOMP-001-F2",
      "typ": "Nebenfunktion",
      "beschreibung": "Gewährleistet Dichtheit gegen Ethanol, Essigsäure und Ethylacetat",
      "anforderungen": [
        {
          "id": "KOMP-001-F2-A1",
          "parameter": "Leckagerate",
          "sollwert": "Null-Leckage (Flansche, Stutzen, Mannloch)"
        }
      ]
    }
  ]
}
```

## Speichern

Nach jeder analysierten Komponente sofort in die DB:

```python
from tools.storage import FMEAStorage
db = FMEAStorage()
component = db.get_component_by_komp_id("KOMP-001")
db.insert_function(
    component_id=component["id"],
    funktion_id="KOMP-001-F1",
    typ="Hauptfunktion",
    beschreibung="...",
    anforderungen=[{"id": "KOMP-001-F1-A1", "parameter": "...", "sollwert": "..."}]
)
```

## Qualitätskriterien
- Jede Funktion hat mindestens 1 messbare Anforderung
- Anforderungen referenzieren konkrete Werte aus dem Kontext
- Hauptfunktion ist klar vom Nebenfunktionen abgegrenzt
- Keine generischen Beschreibungen ohne Bezug zur konkreten Anlage
