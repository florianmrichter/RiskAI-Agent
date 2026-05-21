"""
Explizite Maßnahmen pro Fehlermodus – Agent-Output.

Der Agent analysiert Fehlermodi mit RPZ >= 100 und ergänzt diese Datei
oder ruft insert_measures_for_fehlermodus direkt auf.
generate_measures.py lädt dieses Modul – liefert [] wenn keine Maßnahmen definiert.
"""


def get_measures_for_fehlermodus(fehler_id: str, fehlermodus: str, komponente: str) -> list:
    """
    Liefert explizite Maßnahmen für den Fehlermodus.
    Rückgabe: Liste von Maßnahme-Dicts oder [] wenn keine definiert.
    """
    return []
