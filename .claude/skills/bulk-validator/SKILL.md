---
name: bulk-validator
description: Portfolio-Health-Check — validiert alle FMEA-Projekte in tasks/Risikoanalyse/. Trigger-Words: "Portfolio-Check", "alle Analysen prüfen", "Bulk-Validierung", "Health-Check", "alle Projekte validieren"
---

# Bulk-Validator — Portfolio Health-Check

## Zweck
Führt eine automatische Qualitätsprüfung über **alle** FMEA-Projekte im `tasks/Risikoanalyse/`-Ordner durch. Identifiziert fehlende Daten, unvollständige Analysen und kritische Risiken auf Portfolio-Ebene.

## Ablauf

### 1. Projekte scannen
```
Scanne tasks/Risikoanalyse/ nach Projektordnern (jeder Ordner mit anlagendaten.json)
```

### 2. Pro Projekt prüfen

Für jedes gefundene Projekt die folgenden Checks durchführen:

| Check | Kriterium | Status |
|-------|-----------|--------|
| **Anlagendaten** | `anlagendaten.json` existiert und ist valides JSON | PASS/FAIL |
| **DB vorhanden** | Projekt in `data/fmea.db` mit mindestens 1 Komponente | PASS/FAIL |
| **FM-Abdeckung** | Alle Komponenten haben mindestens 1 Fehlermodus | PASS/WARN |
| **RPZ-Verteilung** | Nicht alle FMs "niedrig" (wäre unrealistisch) | PASS/WARN |
| **Maßnahmen** | Alle FMs mit RPZ ≥ 100 haben mindestens 1 Maßnahme | PASS/WARN |
| **Report** | PDF-Report wurde generiert (existiert im Projektordner) | PASS/INFO |

### 3. Zusammenfassung ausgeben

Formatiere das Ergebnis als Tabelle:

```
📊 Portfolio Health-Check — [Datum]

| Projekt              | Anlage | FMs | Kritisch | Maßn. | Status |
|----------------------|--------|-----|----------|-------|--------|
| Ethylacetat_20TA42   | 20TA42 | 23  | 2        | 18    | ✅ OK  |
| Buechi_15L_20TA43    | 20TA43 | 15  | 1        | 12    | ⚠ WARN |
| ...                  |        |     |          |       |        |

Zusammenfassung: X Projekte geprüft, Y OK, Z Warnungen, W kritisch
```

### 4. Kritische Issues hervorheben

Am Ende alle FAIL- und WARN-Items auflisten mit konkreten Handlungsempfehlungen.

## Tools

Nutze folgende Tools für die Prüfung:
- `tools/validate_anlagendaten.py` — Gate 1: Anlagendaten-Validierung
- `tools/validate_completeness.py` — Gate 2: FMEA-Vollständigkeit
- `tools/storage.py` — DB-Abfragen (Projekt-Statistiken)

## Regeln

1. **Niemals Daten ändern** — der Bulk-Validator ist read-only
2. **Projekte ohne anlagendaten.json überspringen** (kein Fehler, nur Info)
3. **Fehler in einem Projekt stoppt nicht den Rest** — alle Projekte prüfen
4. **Ergebnis immer als Tabelle** — für schnelle Übersicht
