# FMEA-Workflow-Automatismus

## Archiv-Regel (NIEMALS verletzen)
- Jede Risikoanalyse ist NEU. Kopiere NIEMALS FMEA-Daten aus `archive/` oder anderen Projekten.
- Einzige Quelle: `tasks/Risikoanalyse/{projekt}/anlagendaten.json` des aktuellen Projekts.

Bei Session-Start:
1. Prüfe ob `tasks/Risikoanalyse/{projekt}/workflow_state.json` existiert (z.B. Ethylacetatproduktion_20TA41)
2. Falls nein: Struktur initialisieren (Anlagendaten laden, Komponenten in DB), State anlegen, dann weiter
3. Falls ja: Lade State, ermittle nächsten offenen Schritt
4. Gib dem Nutzer eine klare Statusmeldung:
   "FMEA: Phase [fmea], nächste Komponente [komp_id] ([name]).
    Soll ich die Einzelfall-Analyse für [komp_id] durchführen?"
5. Führe den Schritt aus, sobald der Nutzer zustimmt (oder "ja" / "weiter" sagt)
6. Speichere den aktualisierten State nach jedem abgeschlossenen Schritt

## Tools
- `tools/workflow_state.get_next_action("Risikoanalyse/Ethylacetatproduktion_20TA41")` – nächste Aktion
- `tools/workflow_state.init_state_from_structure(...)` – nach Strukturanalyse
- `tools/insert_fmea_explicit.insert_fmea_for_component(project_id, komp_id, task_folder="Risikoanalyse/Ethylacetatproduktion_20TA41")` – FMEA einspielen
- `tools/update_checklist.update_checklist("Risikoanalyse/Ethylacetatproduktion_20TA41")` – Checkliste aktualisieren

## Review-Punkte (Hybrid-Ansatz)
- Erste Komponente / explizite Anfrage: Zeige Zusammenfassung, warte auf "ok" oder "einspielen"
- Bei "weiter" oder "mach die nächsten 3": Automatisch einspielen ohne vorherige Anzeige
- Nach RPZ-Validierung: Zeige Ranking, warte auf Freigabe vor Maßnahmenphase

## Config
- FMEA-Definitionen: `tasks/Risikoanalyse/{projekt}/fmea_explicit.py`
- Maßnahmen: `tasks/Risikoanalyse/{projekt}/measures_explicit.py`
