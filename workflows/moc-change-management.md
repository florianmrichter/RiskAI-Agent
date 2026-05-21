# Management of Change (MoC) — Workflow

## Zweck

Dieser Workflow beschreibt den standardisierten Prozess für Änderungen an bestehenden FMEA-Analysen. Er stellt sicher, dass Änderungen nachvollziehbar, versioniert und mit Freigabe-Gates kontrolliert werden.

## Wann aufrufen

- Eine Anlage wird umgebaut oder erweitert
- Komponenten werden ersetzt oder modifiziert
- Betriebsbedingungen ändern sich (Stoffe, Drücke, Temperaturen)
- Neue Erkenntnisse erfordern eine Neubewertung bestehender Fehlermodi
- Regulatorische Änderungen erfordern eine Aktualisierung

## Tool: `tools/moc_manager.py`

| Funktion | Zweck |
|---|---|
| `freeze_version(project_id)` | Aktuelle Version einfrieren, JSON-Snapshot erstellen |
| `create_new_version(project_id, change_description, changed_components)` | Neue Version anlegen, betroffene Komponenten markieren |
| `get_version_history(task_folder)` | Alle Versionen eines Projekts anzeigen |
| `get_delta(project_id_old, project_id_new)` | Strukturierter Vergleich zweier Versionen |

## Ablauf

### Schritt 1: Änderungsbedarf feststellen

**Trigger:** Der Nutzer meldet eine Änderung an der Anlage oder den Betriebsbedingungen.

**Dokumentieren:**
- Was hat sich geändert? (Beschreibung)
- Welche Komponenten sind betroffen? (komp_ids)
- Wer hat die Änderung veranlasst? (erstellt_von)

### Schritt 2: Aktuelle Version einfrieren

**Vor jeder Änderung** muss die aktuelle Version eingefroren werden. Das verhindert, dass freigegebene Ergebnisse überschrieben werden.

```python
from tools.moc_manager import freeze_version
result = freeze_version(project_id)
```

**Was passiert:**
- Projekt wird in der DB als `frozen=1` markiert (keine weiteren Änderungen möglich)
- JSON-Snapshot wird erstellt unter `tasks/Risikoanalyse/{projekt}/versions/v{version}_snapshot.json`
- Snapshot enthält: Projekt-Metadaten, alle FMEA-Daten, Zeitstempel

**Fehlerfall:** Projekt ist bereits eingefroren → kein erneutes Einfrieren nötig, weiter mit Schritt 3.

### Schritt 3: Neue Version anlegen

```python
from tools.moc_manager import create_new_version
result = create_new_version(
    project_id=project_id,
    change_description="Pumpe P-101 durch dichtungslose Magnetkupplungspumpe ersetzt",
    changed_components=["KOMP-002", "KOMP-005"],
    erstellt_von="Max Mustermann"
)
```

**Was passiert:**
- Neue Projektversion wird in der DB angelegt (auto-inkrementierende Versionsnummer)
- **Unveränderte Komponenten:** Alle Daten (Fehlermodi, Ursachen, Folgen, Bewertungen, Maßnahmen) werden 1:1 kopiert, Status `unverändert`
- **Betroffene Komponenten:** Struktur wird kopiert, aber als `neu_bewertet` markiert — diese müssen neu analysiert werden

**Rückgabe:**
- `new_project_id` — ID der neuen Version
- `copied_fms` — Anzahl der übernommenen Fehlermodi
- `affected_components` — Liste der neu zu bewertenden Komponenten
- `unchanged_components` — Liste der übernommenen Komponenten

### Schritt 4: Betroffene Komponenten neu bewerten

Für jede als `neu_bewertet` markierte Komponente:

1. **Prüfen:** Was hat sich konkret geändert? (neues Equipment, andere Betriebsbedingungen, neue Controls)
2. **Fehlermodi aktualisieren:** Bestehende FMs anpassen, neue FMs hinzufügen, obsolete FMs entfernen
3. **S/O/D neu bewerten:** Unter Berücksichtigung der Änderung
4. **Maßnahmen prüfen:** Bestehende Maßnahmen noch wirksam? Neue nötig?

Hierfür den `fmea-risikoanalyse`-Skill nutzen — er arbeitet dann nur die betroffenen Komponenten ab.

### Schritt 5: Delta-Analyse

Nach der Neubewertung den Vergleich zur Vorgängerversion erstellen:

```python
from tools.moc_manager import get_delta
delta = get_delta(project_id_old, project_id_new)
```

**Rückgabe:**
- `changed` — Fehlermodi mit geänderten S/O/D-Werten (inkl. Delta pro Wert)
- `added` — Neue Fehlermodi in der neuen Version
- `removed` — Entfernte Fehlermodi
- `unchanged_count` — Anzahl unverändert übernommener FMs

**Dem Nutzer präsentieren:** Zusammenfassung der Änderungen mit Vorher/Nachher-Vergleich der RPZ-Werte.

### Schritt 6: Freigabe-Gate

Die neue Version muss den gleichen Review-Prozess durchlaufen wie eine Erstanalyse (siehe `workflows/review-fmea.md`):

1. Validierung via `validate_completeness(new_project_id, task_folder)`
2. Keine KRITISCH-Findings offen
3. Review-Checkliste bestätigt
4. Report neu generiert

**Zusätzlich bei MoC:**
- Delta-Analyse vom Nutzer geprüft und akzeptiert
- Begründung für jede Änderung dokumentiert
- Bei S-Wert-Erhöhung: Sicherheitsbewertung durch Fachkraft erforderlich

### Schritt 7: Abschluss und Audit-Trail

Nach Freigabe:

1. **Neue Version einfrieren:** `freeze_version(new_project_id)`
2. **Report generieren:** `generate_report(new_project_id, task_folder)`
3. **Versionshistorie dokumentieren:** `get_version_history(task_folder)` für den Audit-Trail

## Versionshistorie einsehen

```python
from tools.moc_manager import get_version_history
versions = get_version_history(task_folder)
```

Zeigt alle Versionen mit: Versionsnummer, Projekt-ID, Datum, Frozen-Status. Für Audits und Nachvollziehbarkeit.

## Audit-Trail

Jede Version enthält:
- **Wer** hat die Änderung veranlasst? (`erstellt_von`)
- **Was** wurde geändert? (`version_beschreibung`)
- **Wann** wurde die Version erstellt/eingefroren? (Zeitstempel)
- **Welche Komponenten** waren betroffen? (`changed_components`)
- **Was ist das Delta?** (S/O/D-Änderungen, neue/entfernte FMs)
- **JSON-Snapshot** der eingefrorenen Version (vollständige FMEA-Daten zum Zeitpunkt der Freigabe)

## Regeln

1. **Niemals eine eingefrorene Version direkt bearbeiten.** Immer eine neue Version anlegen.
2. **Unveränderte Daten werden übernommen, nicht neu erstellt.** Das spart Zeit und stellt Konsistenz sicher.
3. **Jede Änderung braucht eine Beschreibung.** Keine Versionierung ohne `change_description`.
4. **Betroffene Komponenten explizit benennen.** Nicht pauschal alles als "geändert" markieren.
5. **Freigabe-Gate ist Pflicht.** Keine Version wird ohne Review als "freigegeben" betrachtet.
6. **Snapshots nicht löschen.** Sie sind Teil des Audit-Trails.
