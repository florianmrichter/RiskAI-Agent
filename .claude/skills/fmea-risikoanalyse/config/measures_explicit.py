"""
Explizite Maßnahmen pro Fehlermodus – Template/Referenz.

Diese Datei dient als Vorlage. Die eigentlichen Maßnahmen-Generatoren liegen pro
Projekt in tasks/{task_folder}/measures_explicit.py – dort definiert der Agent
oder ein Generator get_measures_for_fehlermodus.

Basis für Fehlertypen: config.fmea_standards.FEHLERMODI_VORLAGEN – Katalog der
Fehlertypen pro Kategorie. Bei der Maßnahmenentwicklung kann der Agent den
Fehlertyp (z.B. "Erosion/Abrasions", "Frozen Value") nutzen, um passende
Maßnahmen nach STOP-Prinzip und ABE-Hierarchie abzuleiten.

Format: get_measures_for_fehlermodus(fehler_id, fehlermodus, komponente) -> list
Rückgabe: Liste von Maßnahme-Dicts oder [] wenn keine definiert.

Archiv: Die projektspezifischen Ethylacetat-Maßnahmen (KOMP-002 bis KOMP-047)
wurden nach archive/2026-03-01_Ethylacetat_FMEA_Referenz/ verschoben.
"""


def get_measures_for_fehlermodus(fehler_id: str, fehlermodus: str, komponente: str) -> list:
    """
    Liefert explizite Maßnahmen für den Fehlermodus.
    Rückgabe: Liste von Maßnahme-Dicts oder [] wenn keine definiert.
    Projektspezifisch: Wird aus tasks/{task_folder}/measures_explicit.py oder
    config/measures_explicit.py geladen.
    """
    return []
