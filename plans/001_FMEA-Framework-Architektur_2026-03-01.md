# Plan 001: FMEA-Framework Architektur

**Datum:** 2026-03-01
**Status:** Entwurf
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
- **Output:** Maßnahmen nach ABE-Hierarchie + Restrisiko-Bewertung

### Schritt 7: Ergebnis-Assembly & Export
- **Typ:** Tool (deterministisch)
- **Tool:** `tools/export.py`
- **Input:** Alle FMEA-Daten aus der DB
- **Output:** Excel-Datei / JSON-Report

---

## 3. Datenmodell (SQLite)

```sql
-- Projekte/Analysen
projects (id, name, anlage, datum, status)

-- Komponenten aus Strukturanalyse
components (id, project_id, komp_id, name, typ, kategorie, system_name, 
            beschreibung, parameters_json, kontext_json)

-- Funktionen aus Funktionsanalyse
functions (id, component_id, funktion_id, typ, beschreibung, 
           anforderungen_json)

-- Fehlermodi aus Fehleranalyse
failure_modes (id, function_id, fehler_id, fehlermodus, fehlerart,
               ursachen_json, folgen_json,
               S, O, D, rpz, rpz_status,
               begruendung_S, begruendung_O, begruendung_D)

-- Maßnahmen aus Optimierung
measures (id, failure_mode_id, name, abe_kategorie, beschreibung,
          S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu,
          begruendung)
```

---

## 4. Tools (zu erstellen)

| Tool | Zweck | Priorität |
|------|-------|-----------|
| `tools/load_plant_data.py` | Anlagendaten laden & validieren | P1 |
| `tools/structure_analysis.py` | Komponenten-Zerlegung mit ID-Vergabe | P1 |
| `tools/failure_templates.py` | Fehlervorlagen nach Komponententyp | P1 |
| `tools/rpz_calculator.py` | RPZ-Berechnung + Safety Guard | P1 |
| `tools/storage.py` | SQLite CRUD-Operationen | P1 |
| `tools/export.py` | Excel/JSON-Export | P2 |

---

## 5. Workflows/SOPs (zu erstellen)

| Workflow | Zweck | Priorität |
|----------|-------|-----------|
| `workflows/fmea_analyse.md` | Haupt-SOP: Gesamtablauf der FMEA | P1 |
| `workflows/funktionsanalyse.md` | Anleitung für Funktionsanalyse | P1 |
| `workflows/fehleranalyse.md` | Anleitung für Fehleranalyse inkl. S/O/D | P1 |
| `workflows/massnahmen.md` | Anleitung für Maßnahmenentwicklung | P1 |

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

### Phase 1: Fundament (heute)
1. `tools/storage.py` -- Datenbank-Setup & CRUD
2. `tools/load_plant_data.py` -- Anlagendaten laden
3. `tools/structure_analysis.py` -- Strukturanalyse
4. `workflows/fmea_analyse.md` -- Haupt-SOP

### Phase 2: Analyse-Kern
5. `workflows/funktionsanalyse.md` -- SOP Funktionsanalyse
6. `tools/failure_templates.py` -- Fehlervorlagen
7. `workflows/fehleranalyse.md` -- SOP Fehleranalyse
8. `tools/rpz_calculator.py` -- RPZ + Safety Guard

### Phase 3: Optimierung & Output
9. `workflows/massnahmen.md` -- SOP Maßnahmen
10. `tools/export.py` -- Excel-Export

### Phase 4: Erster Durchlauf
11. Vollständige FMEA der Ethylacetat-Anlage als Proof of Concept
