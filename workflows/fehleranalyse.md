# Fehleranalyse -- SOP

## Ziel
Für jede Funktion: Fehlermodi identifizieren, Ursachen mit Herkunft und Präventionsphase dokumentieren, Folgen in 4 Dimensionen bewerten, bestehende Controls erfassen, S/O/D vorläufig bewerten.

## Input (pro Funktion)
- Funktion: `funktion_id`, `beschreibung`, `anforderungen`
- Komponente: `komp_id`, `name`, `typ`, `parameters`
- Kontext: `lean_context` (Prozessbedingungen, Design-Limits, Stoffe, Sensoren, Sicherheitseinrichtungen)
- Fehlervorlagen: Output von `tools/failure_templates.py`

## Vorbereitung

```python
from tools.failure_templates import get_templates_for_component, format_templates_for_prompt

templates = get_templates_for_component(
    komp_id="KOMP-001",
    component_type="prozess",
    search_text=funktion_beschreibung + " ".join(a["parameter"] for a in anforderungen)
)
template_text = format_templates_for_prompt(templates)
```

## Analyse-Regeln

### 1. Fehlermodi (mindestens 3 pro Funktion)
- ID-Format: `{funktion_id}-FM1`, `{funktion_id}-FM2`, ...
- KONKRET formulieren mit Bezug auf Grenzwerte: "Überdruck über 6 bar" statt "Zu hoher Druck"
- Jeder Grenzwert aus den Anforderungen sollte mindestens einen Fehlermodus erzeugen
- `fehlerart` aus: Prozess, Thermisch, Mechanisch, Equipment, Elektrisch, MSR, Sicherheit, Dosierung

### 2. Fehlerursachen (3-5 pro Fehlermodus)
- ID-Format: `{fehler_id}-UC1`, `{fehler_id}-UC2`, ...
- Verteilt auf verschiedene Herkunftskategorien:

| Herkunft | Beispiele |
|----------|-----------|
| **Design** | Unterdimensionierung, falsche Werkstoffwahl, fehlende Redundanz |
| **Fertigung** | Schweißfehler, Montage-Fehler, falsches Drehmoment |
| **Betrieb** | Fehlbedienung, falsche Sollwerte, Überlastung |
| **Wartung** | Übersprungene Inspektionen, falsche Ersatzteile, fehlende Kalibrierung |

- Jede Ursache bekommt eine **Präventionsphase** -- der frühestmögliche Zeitpunkt zur Verhinderung:

| Phase | Wann | Beispiel-Maßnahme |
|-------|------|-------------------|
| **Konzept** | Grundlayout / Verfahrensauswahl | Inhärent sichere Chemie wählen |
| **Detaildesign** | Konstruktion / Spezifikation | Redundante Sensoren vorsehen |
| **Fertigung** | Herstellung / Montage | 100%-Röntgenprüfung der Schweißnähte |
| **Inbetriebnahme** | FAT/SAT / Abnahme | Druckprobe mit 1.5x Auslegungsdruck |
| **Betrieb** | Normaler Anlagenbetrieb | SOP mit Checkliste vor Chargenstart |
| **Wartung** | Instandhaltung | Membranwechsel alle 2000 Bh |

- `praeventionshinweis`: Was hätte man in dieser Phase konkret tun können?

### 3. Fehlerfolgen (4 Dimensionen)
Für jeden Fehlermodus in 4 Dimensionen bewerten:

| Dimension | Bewertung | Beispiel |
|-----------|-----------|---------|
| **mensch** | Stufe + Beschreibung | "Schwere Verletzung -- Verätzungsgefahr durch austretende Essigsäure" |
| **umwelt** | Stufe + Beschreibung | "Betriebsbereich -- Medien in Auffangwanne, keine externe Kontamination" |
| **anlage** | Stufe + Beschreibung | "Totalausfall -- 4 Wochen Stillstand für Behältertausch" |
| **kosten** | Stufe + Beschreibung | "Bis 500.000 € -- Behälter + Charge + Reinigung + Behördl. Abnahme" |

### 4. Bestehende Controls (CurrentControls -- IST)
Aus dem `lean_context` die vorhandenen Sensoren und Sicherheitseinrichtungen zuordnen:
- Welcher Sensor / welche Sicherheitseinrichtung ist für DIESEN Fehlermodus relevant?
- Typ: Sensor / Sicherheitsventil / Verriegelung / SOP / Prüfung
- Wirkung: A (Vermeidung) / B (Entdeckung) / E (Abschwächung)
- Beeinflusst: O (Eintrittswahrscheinlichkeit) oder D (Entdeckungswahrscheinlichkeit)

### 5. Risikobewertung (S/O/D vorläufig)

| Kennzahl | Bewertung | Begründung |
|----------|-----------|------------|
| **S** (1-10) | Maximum der 4 Schadensdimensionen | Kausalitätskette erklären |
| **O** (1-10) | Eintrittswahrscheinlichkeit | 3-Säulen: Komplexität, Umgebung, Design-Absicherung |
| **D** (1-10) | Entdeckung VOR Schadenseintritt | Prüfmittel, Ort, Zeitpunkt nennen |

## Output-Format (JSON)

```json
{
  "funktion_id": "KOMP-001-F1",
  "komponenten_id": "KOMP-001",
  "komponente": "Synthesereaktor R-101",
  "failure_modes": [
    {
      "fehler_id": "KOMP-001-F1-FM1",
      "fehlermodus": "Überdruck im Reaktor über 6 bar (Design-Limit)",
      "fehlerart": "Prozess",
      "causes": [
        {
          "ursache_id": "KOMP-001-F1-FM1-UC1",
          "beschreibung": "Fehlbedienung: Heizmantelventile während exothermer Phase voll geöffnet",
          "herkunft": "Betrieb",
          "praeventionsphase": "Betrieb",
          "praeventionshinweis": "SOP mit expliziter Checkliste für Heizmantel-Freigabe"
        },
        {
          "ursache_id": "KOMP-001-F1-FM1-UC2",
          "beschreibung": "Unterdimensionierung des Not-Entspannungssystems für worst-case Exothermie",
          "herkunft": "Design",
          "praeventionsphase": "Detaildesign",
          "praeventionshinweis": "Auslegungsberechnung nach API 520/521 mit konservativem Szenario"
        }
      ],
      "effects": {
        "mensch": {"stufe": "Schwere Verletzung", "beschreibung": "Verätzungsgefahr durch austretende heiße Dämpfe"},
        "umwelt": {"stufe": "Betriebsbereich", "beschreibung": "Medien im Auffangraum, keine externe Kontamination"},
        "anlage": {"stufe": "Totalausfall", "beschreibung": "Stillstand 4 Wochen für Behältertausch und Neuabnahme"},
        "kosten": {"stufe": "Bis 500.000 €", "beschreibung": "Behälter + Charge + Reinigung + behördliche Abnahme"}
      },
      "current_controls": [
        {
          "name": "PIC-402",
          "typ": "Sensor",
          "wirkung": "B",
          "sil_level": "SIL-1",
          "beschreibung": "Drucktransmitter mit PID-Regelung, Messbereich -1 bis 8 bar",
          "beeinflusst": "D"
        },
        {
          "name": "PSV-410",
          "typ": "Sicherheitsventil",
          "wirkung": "E",
          "sil_level": null,
          "beschreibung": "Sicherheitsventil Ansprechdruck 6 bar, DN50, Abblaseleitung zur Fackel",
          "beeinflusst": "O"
        }
      ],
      "risk_assessment": {
        "S": 8,
        "begruendung_S": "S=8 aus Dimension 'Mensch': Chemische Verbrühungsgefahr überwiegt Sachschäden",
        "O": 3,
        "begruendung_O": "O=3: SIL-1 Druckregelung + SIL-2 Temperaturverriegelung minimieren Wahrscheinlichkeit",
        "D": 2,
        "begruendung_D": "D=2: PIC-402 löst bei 3.4 bar Alarm aus, PSV-410 begrenzt bei 6 bar automatisch"
      }
    }
  ]
}
```

## Speichern

Nach jeder analysierten Funktion sofort in die DB:

```python
from tools.storage import FMEAStorage
db = FMEAStorage()

fm_db_id = db.insert_failure_mode(function_id=..., fehler_id="...", fehlermodus="...", fehlerart="...")

for cause in causes:
    db.insert_failure_cause(fm_db_id, cause["ursache_id"], cause["beschreibung"],
                            cause["herkunft"], cause["praeventionsphase"],
                            cause.get("praeventionshinweis"))

db.insert_failure_effect(fm_db_id, mensch_stufe=..., mensch_beschreibung=..., ...)

for ctrl in current_controls:
    db.insert_current_control(fm_db_id, ctrl["name"], ctrl["typ"], ctrl["wirkung"],
                              ctrl.get("sil_level"), ctrl.get("beschreibung"),
                              ctrl.get("beeinflusst"))

db.insert_risk_assessment(fm_db_id, S=..., O=..., D=...,
                          begruendung_S=..., begruendung_O=..., begruendung_D=...)
```

## Qualitätskriterien
- Mindestens 3 Fehlermodi pro Funktion
- Mindestens 3 Ursachen pro Fehlermodus, verteilt auf verschiedene Herkunftskategorien
- Jede Ursache hat eine Präventionsphase und einen konkreten Präventionshinweis
- Alle 4 Schadensdimensionen bewertet
- Bestehende Controls aus dem Kontext korrekt zugeordnet
- S/O/D-Begründungen referenzieren konkrete Anlagendaten (IDs, Werte)
