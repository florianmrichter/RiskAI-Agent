"""
Explizite FMEA-Definitionen pro Komponente – Template/Referenz.

Diese Datei dient als Vorlage. Die eigentlichen FMEA-Daten liegen pro Projekt in
tasks/{task_folder}/fmea_explicit.py – dort schreibt der Agent seine Analyse.

Basis für Fehlermodi: config.fmea_standards.FEHLERMODI_VORLAGEN – Katalog nach
Kategorien (prozess, thermisch, mechanisch, equipment, msr, sicherheit, dosierung,
sonstiges). Der Agent nutzt ihn als Checkliste, welche Fehlertypen pro Komponente
relevant sind. Keine blinde Übernahme – jede S/O/D-Bewertung einzeln.

Format: get_fmea_for_component(komp_id) -> dict mit functions und failure_modes.

Archiv: Die projektspezifischen Ethylacetat-Daten (KOMP-002 bis KOMP-047) wurden
nach archive/2026-03-01_Ethylacetat_FMEA_Referenz/ verschoben.
"""


def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})


_FMEA = {}
