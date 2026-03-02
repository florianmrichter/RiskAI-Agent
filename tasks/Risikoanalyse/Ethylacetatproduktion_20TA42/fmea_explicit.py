"""
Explizite FMEA-Definitionen pro Komponente – Agent-Output.

Der Agent analysiert jede Komponente einzeln und ergänzt diese Datei.
get_fmea_for_component(komp_id) liefert die Definition für insert_fmea_for_component.
"""

def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})

_FMEA = {}
