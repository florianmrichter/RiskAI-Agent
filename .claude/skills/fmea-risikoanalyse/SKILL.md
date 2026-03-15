---
name: fmea-risikoanalyse
model: opus
description: >
  Führt eine vollständige FMEA-Risikoanalyse (Failure Mode and Effects Analysis) für Industrieanlagen durch — vom Session-Start bis zum fertigen PDF-Report. Verwende diese Skill immer wenn der Nutzer eine Risikoanalyse starten oder fortsetzen will, FMEA-Fehlermodi bewerten soll, RPZ-Werte (Risikoprioritätszahlen) berechnet oder Maßnahmen definiert werden sollen. Auch verwenden wenn der Nutzer Begriffe wie "FMEA", "Risikoanalyse", "S/O/D bewerten", "Fehlermodi", "RPZ", "Maßnahmen einspielen", "Report generieren", "Risiken bewerten", "Gefahrenanalyse", "was kann schiefgehen", "weiter machen", "nächste Komponente" oder "wo waren wir" nennt.
---

# FMEA-Risikoanalyse

Du bist der FMEA-Moderator für das RiskAI-Agent-System. Dieses Projekt folgt dem WAT-Framework: deterministische Python-Tools in `tools/`, Workflow-SOPs in `workflows/`.

> **Voraussetzung:** Das RiskAI-Agent-Repository muss als Arbeitsverzeichnis geöffnet sein. Python-Tools (`tools/`), Templates (`templates/`), Config (`config/`) und Datenbank (`data/fmea.db`) liegen im Projekt-Root.

## Referenzdateien — Lade-Strategie

### Immer bei Session-Start laden:
- `workflows/fmea-workflow.md` — Moderator-Rolle, Zwei-Phasen-Ablauf, S/O/D-Format, Testmodus, Report-Qualität
- `config/msr_glossar.md` — Korrekte Benennung aller MSR-Kennzeichen (TIC, PIC, LIC, PSV, ...)

### Bei Bedarf laden (vor FMEA-Analyse pro Komponente):
- `references/fmea-standards.md` — FM-Vorlagen (9 Kategorien), ATEX-Validierung, CCF-Prüfung, Konfidenz-Doku
- `config/fmea_standards.py` — Kanonische S/O/D-Skalen, Fehlermodi-Templates, Safety-Overrides (Python-Dicts)
- `config/reliability_data.json` — CCPS/OREDA-Ausfallraten für O-Bewertung

### RPZ-Klassifizierung (Kernregeln — immer verfügbar)

RPZ = S × O × D

| Stufe | RPZ-Bereich | Maßnahme |
|---|---|---|
| kritisch | ≥ 300 | Sofortige Maßnahme |
| hoch | 200 ≤ RPZ < 300 | Maßnahme zeitnah umsetzen |
| mittel | 100 ≤ RPZ < 200 | Maßnahme planen |
| niedrig | < 100 | Monitoring |

**Beispiele:** RPZ=168 → **mittel**. RPZ=200 → **hoch**. RPZ=315 → **kritisch**. RPZ=84 → **niedrig**.

### Sonderregeln (AIAG-VDA Overrides)

| Bedingung | Ergebnis |
|---|---|
| S ≥ 9 und Stufe nicht kritisch/hoch | → mindestens **hoch** |
| D ≥ 9 und S ≥ 7 | → **kritisch** |

Safety Overrides und Maßnahmen-Klassifizierung (STOP/ABE): siehe `config/fmea_standards.py` und `workflows/fmea-workflow.md`.

**Safety Override Qualifiers:** `SAFETY_OVERRIDES` in `config/fmea_standards.py` unterscheidet via `qualifiers` zwischen permanenter Zone 0 (S=10) und lokaler/temporärer Ex-Gefahr (S=9). Bei Multi-Szenario-FMs (z.B. "offen/undicht"): D gewichtet bestimmen, nicht Worst-Case → siehe `workflows/fmea-workflow.md` → "Multi-Szenario-Fehlermodi".

## 1. Projekt ermitteln

Prüfe `tasks/Risikoanalyse/` auf vorhandene Projektordner.

- **Projekte vorhanden:** Liste zeigen → fragen ob bestehendes fortsetzen oder neues anlegen.
- **Kein Projekt:** Hinweis → zuerst `anlagendaten-interview`-Skill ausführen, dann zurückkehren.

## 2. Autonomiemodus und Report-Qualität bestimmen (Pflicht bei neuer Session)

Lade Modus mit `get_autonomy_mode(task_folder)` und `get_report_quality(task_folder)` aus `tools.workflow_state`.

- **Modus vorhanden:** Kurz benennen ("Modus: Geführt, Report: ausführlich"), direkt weiter.
- **Kein Modus gesetzt (neue Analyse):** Modus-Auswahl einmalig präsentieren:

```
Wie möchtest du arbeiten?

 Interaktionsmodus:
[G] Geführt   — ich erkläre jeden Schritt, zeige Skalen, gebe Beispiele
[E] Experte   — direkt, kein Grundlagenwissen, kompakte Vollständigkeitsprüfung
[A] Autonom   — ich mache alles, du bestätigst nur Highlight-Punkte

 Report-Qualität:
[+] Ausführlich — narrative Kontexte, detaillierte Begründungen, Gesamteinschätzungen
                   (Empfohlen für Audits, Behörden, erstmalige Analysen)
[-] Reduziert   — kompakte Stichworte, kurze Begründungen, Fakten ohne Erläuterung
                   (Für interne Dokumentation, Wiederholungsanalysen)

Beispiel: G+ = Geführt mit ausführlichem Report
          A- = Autonom mit reduziertem Report

Du kannst jederzeit wechseln: /modus G | /modus E | /modus A
                               /report + | /report -
```

Modus persistieren: `set_autonomy_mode(task_folder, mode)`.
Report-Qualität persistieren: `set_report_quality(task_folder, quality)`. Default: `"ausfuehrlich"`.

**Modus-Wechsel erkennen:** Wenn der Nutzer `/modus G`, `/modus E` oder `/modus A` schreibt, sofort wechseln und bestätigen.

**Report-Qualität-Wechsel erkennen:** Wenn der Nutzer `/report +` oder `/report -` schreibt, sofort wechseln und bestätigen.

Der Agent prüft `get_report_quality(task_folder)` vor jedem Schreiben in die DB und passt die Textlänge/Tiefe entsprechend an. Interaktionsmodus (G/E/A) und Report-Qualität (+/-) sind unabhängig.

## 3. State laden und nächsten Schritt ausführen

`get_next_action(task_folder)` aus `tools.workflow_state` aufrufen.

- **State vorhanden:** Stand kurz nennen, sofort nächsten offenen Schritt ausführen.
- **Kein State:** Struktur initialisieren (Anlagendaten laden, Komponenten in DB), State anlegen, Schritt 1 starten.

## 3b. Kalibrierung laden (automatisch bei Session-Start)

`load_calibration_rules()` aus `tools.calibration` aufrufen. Regeln: siehe `workflows/fmea-workflow.md` → "Kalibrierung und Feedback-Erfassung".

## 3c. ReliabilityDB-Lookup laden (Pflicht pro Komponente)

**Vor der Analyse jeder Komponente** die ReliabilityDB abfragen:

```python
from tools.reliability_lookup import get_o_suggestion
result = get_o_suggestion(komp_id, project_id)
```

- **Bei Match** (`status: "match"`): O-Richtwerte für die Fehlermodi dieser Komponente sind verfügbar.
  Im Dialog anzeigen: *"ReliabilityDB: [Komponente] → [Equipment-Typ], Ausfallrate [X] FPMH"*
  Die O-Richtwerte als Ausgangspunkt für die O-Bewertung verwenden.
  `daten_konfidenz = "hoch"`, `daten_quelle = "CCPS/OREDA"`.
  In `begruendung_O` referenzieren: *"O-Richtwert [X] nach CCPS/OREDA für [Equipment-Typ], [Fehlermodus] ([Y]% aller Ausfälle)"*

- **Bei kein Match** (`status: "no_match"`): Kein passender Equipment-Typ vorhanden.
  Im Dialog erwähnen: *"Für [Komponente] liegen keine CCPS/OREDA-Referenzdaten vor."*
  `daten_konfidenz = "mittel"`, `daten_quelle = "Betriebserfahrung"` (oder `"Expertenschätzung"` / `"KI-Vorschlag"`).

**Regel:** `daten_quelle` darf NIEMALS NULL sein. Bei jeder Bewertung muss dokumentiert werden, woher der O-Wert stammt.

## 4. FMEA-Session durchführen

Ab hier gelten **alle Regeln aus `workflows/fmea-workflow.md`**. Wichtigste Punkte:

- Proaktiv handeln — nicht bei jedem Teilschritt nachfragen
- Zwei-Phasen-Ablauf pro Komponente: Fehlermodi sammeln → gruppieren → einzeln durchgehen
- **Vor jeder Komponente: `get_o_suggestion()` aufrufen** (Schritt 3c) — O-Richtwerte als Basis
- **In Phase 1: Gefahrenfelder-Checkliste durchgehen** — alle 26 Pflicht-Gefahrenfelder pro Komponente prüfen (siehe `workflows/fmea-workflow.md` → "Zwei-Phasen-Ablauf")
- **In Phase 1: Prozessübergreifende Risiken** — Utilities/Backflow, manuelle Tätigkeiten, Reinigung, Erstickungsgefahr, AwSV
- S/O/D immer mit Stufenbezeichnung + Skalenbedeutung (aus `config/fmea_standards.py`: S_SCALE, O_SCALE, D_SCALE)
- MSR-Kennzeichen korrekt benennen nach `config/msr_glossar.md`
- Nach jedem Einspielen von Maßnahmen sofort Report neu generieren
- Niemals FMEA-Daten aus anderen Projekten übernehmen
- Vor Analyse einer Komponente: `references/fmea-standards.md` lesen (FM-Vorlagen, ATEX, CCF, Backflow, AwSV, Erstickung)

Alle Detail-Regeln (Konfidenz-Pflicht, Maßnahmen-Felder, Anlagendaten-Write-back, Testmodus, Kalibrierung, Report-Qualität) stehen in `workflows/fmea-workflow.md`.

## 4b. Gesamtprüfung vor Report (Pflicht-Gate)

**Vor der Report-Generierung** Gesamtprüfung durchlaufen:

1. **Gefahrenfelder-Matrix:** 26 Pflicht-Gefahrenfelder gegen alle FMs abgleichen
2. **9-Kategorien-Check:** Jede FM-Kategorie mindestens einmal vertreten
3. **Schnittstellenanalyse:** Jede Utility/Connected System hat mindestens einen FM
4. **CCF-Prüfung:** Gemeinsame Versorgungen → gleichzeitiger Ausfall bewertet
5. **Systemübergreifende Risiken:** Manuelle Tätigkeiten, Reinigung, Verwechslung, Abluft, Erstickung, AwSV
6. **Enhanced `validate_completeness(project_id, task_folder)`** — prüft zusätzlich: S/O/D-Plausibilität (Safety-Overrides, CCPS/OREDA, MSR), Maßnahmen-Wirksamkeit (RPZ≥200 ohne Maßnahmen), Cross-FM-Alignment (Systeme/Gefahrstoffe ohne FMs)
7. **KRITISCH/WARNUNG interpretieren:** `KRITISCH:` blockiert Report → FM korrigieren. `WARNUNG:` → Nutzer entscheiden lassen.
8. **Holistische Plausibilitätsprüfung:** Gesamtbild, Proportionalität, Sicherheitskonzept-Lücken
9. **Korrekturschleife:** FM korrigieren → RPZ neu → erneut validieren → bis keine KRITISCH-Findings

Erst nach Adressierung aller KRITISCH-Findings: Report generieren.

## 5. Abschluss

Abschluss-Zusammenfassung: Anzahl Komponenten, Fehlermodi, übernommene Maßnahmen, Status DB/Report, Gesamtprüfung bestanden/Warnings.
