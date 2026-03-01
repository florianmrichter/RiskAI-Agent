# Plan 001: FMEA-Framework Architektur

**Datum:** 2026-03-01
**Status:** Abgeschlossen
**Ziel:** Wiederverwendbares Framework für automatisierte Risikoanalysen (FMEA) nach AIAG-VDA

---

## 1. Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT (Claude)                        │
│         Orchestrierung + FMEA-Fachanalyse               │
│                                                         │
│  Liest Workflows (SOPs) → Trifft Entscheidungen →      │
│  Ruft Tools auf → Führt Fachanalyse durch               │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
    ┌──────▼──────┐           ┌───────▼───────┐
    │  Workflows  │           │    Tools      │
    │  (SOPs)     │           │  (Python)     │
    │             │           │               │
    │  Schritt-   │           │  Laden,       │
    │  für-       │           │  Berechnen,   │
    │  Schritt    │           │  Speichern,   │
    │  Anleitungen│           │  Exportieren  │
    └─────────────┘           └───────┬───────┘
                                      │
                              ┌───────▼───────┐
                              │   Storage     │
                              │  (Lokal)      │
                              │               │
                              │  SQLite DB    │
                              │  + JSON       │
                              └───────────────┘
```

### Warum diese Architektur?

Der n8n-Workflow hat eine feste Pipeline. Unser Ansatz ist flexibler:
- Claude macht das **Reasoning** direkt (keine externen LLM-Calls nötig)
- Deterministische Schritte (RPZ, Safety Guard) laufen als **Python-Tools**
- Zwischenergebnisse werden nach jedem Schritt **gespeichert** (Checkpointing)
- Kontext bleibt klein: Komponenten werden **einzeln/batchweise** verarbeitet

---

## 2. Pipeline-Schritte

### Schritt 1: Anlagendaten laden
- **Typ:** Tool (deterministisch)
- **Tool:** `tools/load_plant_data.py`
- **Input:** JSON/RTF mit Anlagenbeschreibung
- **Output:** Strukturiertes Anlagenobjekt (validiert)

### Schritt 2: Strukturanalyse
- **Typ:** Tool (deterministisch)
- **Tool:** `tools/structure_analysis.py`
- **Input:** Anlagenobjekt
- **Output:** Liste aller Komponenten mit KOMP-IDs, Typen, Kontext
- **Logik:** Zerlegung in Systeme → Equipment → MSR → Sicherheit (wie im n8n-Workflow)

### Schritt 3: Funktionsanalyse
- **Typ:** Agent (Claude-Reasoning)
- **Workflow:** `workflows/funktionsanalyse.md`
- **Input:** Einzelne Komponente + Systemkontext
- **Output:** Haupt-/Nebenfunktionen mit messbaren Anforderungen
- **Verarbeitung:** Komponentenweise (Kontext klein halten)

### Schritt 4: Fehleranalyse
- **Typ:** Agent (Claude-Reasoning) + Tool (Templates)
- **Tool:** `tools/failure_templates.py` (liefert typische Fehlerbilder)
- **Workflow:** `workflows/fehleranalyse.md`
- **Input:** Funktion + Anforderungen + Fehlervorlagen + Anlagenkontext
- **Output:** Fehlermodi, Ursachen, Folgen, S/O/D-Bewertung

### Schritt 5: RPZ-Berechnung & Klassifizierung
- **Typ:** Tool (deterministisch)
- **Tool:** `tools/rpz_calculator.py`
- **Input:** S/O/D-Werte
- **Output:** RPZ + Status (kritisch/hoch/mittel/niedrig)
- **Inkl.:** Safety-Guard-Overrides (Ex-Schutz, Gefahrstoffe, Sicherheitsbauteile)

### Schritt 6: Maßnahmenoptimierung
- **Typ:** Agent (Claude-Reasoning)
- **Workflow:** `workflows/massnahmen.md`
- **Input:** Fehlermodi mit hoher RPZ + Anlagenkontext + vorhandene Sensorik
- **Output:** Mehrere Maßnahmen nach **STOP-Prinzip** (Substitution, Technisch, Organisatorisch, Persönlich) x **ABE-Hierarchie** + Restrisiko-Bewertung pro Maßnahme
- **Feedback-Schleife:** KI empfiehlt Abdeckung, Benutzer kann gezielt weitere Maßnahmen in bestimmten STOP-Kategorien anfordern

### Schritt 7: Ergebnis-Assembly & Export
- **Typ:** Tool (deterministisch)
- **Tool:** `tools/export.py`
- **Input:** Alle FMEA-Daten aus der DB
- **Output:** Excel-Datei / JSON-Report

---

## 3. Datenmodell (SQLite)

Das Schema ist normalisiert: Fehlermodi, Ursachen, Folgen und Risikobewertungen sind in eigenen Tabellen.

```sql
-- Projekte/Analysen
projects (id, name, anlage_name, datum, status)

-- Komponenten aus Strukturanalyse
components (id, project_id, komp_id, name, typ, kategorie, system_name,
            beschreibung, parameters_json, kontext_json)

-- Funktionen aus Funktionsanalyse
functions (id, component_id, funktion_id, typ, beschreibung,
           anforderungen_json)

-- Fehlermodi aus Fehleranalyse
failure_modes (id, function_id, fehler_id, fehlermodus, fehlerart)

-- Fehlerursachen (n:1 zu failure_modes)
failure_causes (id, failure_mode_id, ursache_id, beschreibung,
                herkunft, praeventionsphase, praeventionshinweis)

-- Fehlerfolgen (1:1 zu failure_modes)
failure_effects (id, failure_mode_id,
                 mensch_stufe, mensch_beschreibung,
                 umwelt_stufe, umwelt_beschreibung,
                 anlage_stufe, anlage_beschreibung,
                 kosten_stufe, kosten_beschreibung)

-- Risikobewertung (1:1 zu failure_modes)
risk_assessments (id, failure_mode_id,
                  S, O, D, begruendung_S, begruendung_O, begruendung_D,
                  rpz, rpz_status, override_applied)

-- Bestehende Controls (n:1 zu failure_modes)
current_controls (id, failure_mode_id, name, typ, wirkung,
                  sil_level, beschreibung, beeinflusst)

-- Maßnahmen aus Optimierung (n:1 zu failure_modes, mehrere pro Fehlermodus)
measures (id, failure_mode_id, name,
          abe_kategorie,                              -- A/B/E (Wirkung)
          stop_kategorie,                             -- S/T/O/P (Art der Maßnahme)
          beschreibung, ziel,
          S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu,
          begruendung,
          iteration)                                  -- 1=initial, 2+=Vertiefung
```

---

## 4. Tools

| Tool | Zweck | Status |
|------|-------|--------|
| `tools/load_plant_data.py` | Anlagendaten laden & validieren | Erledigt |
| `tools/structure_analysis.py` | Komponenten-Zerlegung mit ID-Vergabe | Erledigt |
| `tools/failure_templates.py` | Fehlervorlagen nach Komponententyp | Erledigt |
| `tools/rpz_calculator.py` | RPZ-Berechnung + Safety Guard + Sonderregeln | Erledigt |
| `tools/storage.py` | SQLite CRUD (inkl. STOP-Kategorien, Batch-Insert, Migration) | Erledigt |
| `tools/export.py` | Excel/JSON-Export (inkl. STOP-Spalte, Farbkodierung) | Erledigt |
| `tools/review.py` | Human-in-the-Loop Review + Feedback + STOP-Abdeckung | Erledigt |
| `tools/report_generator.py` | PDF-Report mit Playwright (Charts, Risk Matrix) | Erledigt |
| `config/fmea_standards.py` | Zentrale FMEA-Konfiguration (RPZ-Grenzen, Skalen, Sonderregeln) | Erledigt |
| `tools/mermaid_renderer.py` | Mermaid-Diagramme zu SVG/PNG rendern (Flowcharts, System-Uebersichten) | Erledigt |
| `tools/reliability_lookup.py` | Zuverlaessigkeitsdaten-Abfrage (Ausfallraten, O-Wert-Vorschlaege) | Erledigt |

---

## 5. Workflows/SOPs

| Workflow | Zweck | Status |
|----------|-------|--------|
| `workflows/fmea_analyse.md` | Haupt-SOP: Gesamtablauf mit Human-in-the-Loop Review | Erledigt |
| `workflows/funktionsanalyse.md` | Anleitung für Funktionsanalyse | Erledigt |
| `workflows/fehleranalyse.md` | Anleitung für Fehleranalyse inkl. S/O/D | Erledigt |
| `workflows/massnahmen.md` | Maßnahmenentwicklung nach STOP x ABE mit Feedback-Schleife | Erledigt |
| `workflows/validierung.md` | Konsistenz- und Vollständigkeitsprüfung | Erledigt |

---

## 6. Verbesserungen gegenüber dem n8n-Workflow

| Aspekt | n8n-Workflow (alt) | Neues Framework |
|--------|-------------------|-----------------|
| Orchestrierung | Feste Pipeline | Agent-gesteuert, flexibel |
| LLM | Groq/Llama 4 (extern) | Claude direkt (höhere Qualität) |
| Kontext | Gesamter Workflow im Speicher | Komponentenweise, gespeichert |
| Speicherung | Nur am Ende (JSON-File) | Nach jedem Schritt (SQLite) |
| Fehlerbehandlung | JSON-Parsing-Hoffnung | Strukturiertes Checkpointing |
| Wiederverwendbarkeit | Hardcoded für eine Anlage | Framework für beliebige Anlagen |
| Rate Limiting | Wait-Nodes (30s) | Nicht nötig (kein externer LLM) |

---

## 7. Implementierungsreihenfolge

### Phase 1: Fundament -- Erledigt
1. `tools/storage.py` -- Datenbank-Setup & CRUD
2. `tools/load_plant_data.py` -- Anlagendaten laden
3. `tools/structure_analysis.py` -- Strukturanalyse
4. `workflows/fmea_analyse.md` -- Haupt-SOP

### Phase 2: Analyse-Kern -- Erledigt
5. `workflows/funktionsanalyse.md` -- SOP Funktionsanalyse
6. `tools/failure_templates.py` -- Fehlervorlagen
7. `workflows/fehleranalyse.md` -- SOP Fehleranalyse
8. `tools/rpz_calculator.py` -- RPZ + Safety Guard

### Phase 3: Optimierung & Output -- Erledigt
9. `workflows/massnahmen.md` -- SOP Maßnahmen (inkl. STOP-Prinzip + Feedback-Schleife)
10. `tools/export.py` -- Excel/JSON-Export (inkl. STOP-Kategorien)

### Phase 4: Erster Durchlauf -- Erledigt
11. Vollständige FMEA der Ethylacetat-Anlage als Proof of Concept (PDF-Bericht generiert)

### Phase 5: Optimierung -- Erledigt (siehe Plan 002)
12. Human-in-the-Loop interaktiver Workflow
13. Zentrale Konfiguration (`config/fmea_standards.py`)
14. Review-Tool (`tools/review.py`)
15. Validierungs-Workflow
16. Optische Verbesserungen (Risk Matrix, Cover, Fonts, Farben)
17. STOP-Prinzip x ABE Maßnahmen-Generierung (siehe Plan 003)
