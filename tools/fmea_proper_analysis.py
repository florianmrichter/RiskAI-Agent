#!/usr/bin/env python3
"""
FMEA-Analyse – KEINE generische Logik.

Funktionen und Fehlermodi werden ausschließlich explizit pro Komponente in
tasks/{task_folder}/fmea_explicit.py definiert. Der Agent führt die Einzelfall-Analyse durch
und ergänzt die Definitionen. tools/insert_fmea_explicit.py fügt sie in die DB ein.

Dieses Skript enthält nur noch Hilfsfunktionen (z.B. _get_component_item für
Anlagendaten-Lookup). Keine _build_functions, _build_failure_modes mehr.
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.load_plant_data import load_plant_data
from tools.storage import FMEAStorage


# ─── Hilfsfunktionen (keine generische Erzeugung) ───
def _get_component_item(plant_data: dict, komp_id: str) -> dict:
    """Finde das Anlagendaten-Item für eine Komponente (Equipment/MSR/Security)."""
    counter = 1
    for system in plant_data.get("systems", []):
        if f"KOMP-{counter:03d}" == komp_id:
            return {"system": system, "item": system, "source": "system"}
        counter += 1
        for key, cat in [("equipment", "equipment"), ("msrEquipment", "msr"), ("securityFeatures", "sicherheit")]:
            for sub in system.get(key, []):
                if f"KOMP-{counter:03d}" == komp_id:
                    return {"system": system, "item": sub, "source": key}
                counter += 1
    return None


# ─── Keine generische Erzeugung mehr ───
# Funktionen und Fehlermodi werden ausschließlich in tasks/{task_folder}/fmea_explicit.py
# pro Komponente definiert und mit tools/insert_fmea_explicit.py eingefügt.
# Der Agent führt die Einzelfall-Analyse Schritt für Schritt durch.


if __name__ == "__main__":
    print("FMEA-Analyse erfolgt ausschließlich über explizite Definitionen.")
    print("1. Agent analysiert Komponente einzeln (tasks/Risikoanalyse/Ethylacetatproduktion_20TA42/anlagendaten.json)")
    print("2. Definition in tasks/{task_folder}/fmea_explicit.py ergänzen")
    print("3. tools/insert_fmea_explicit.py ausführen")
    print("4. tools/generate_measures.py oder insert_measures_for_fehlermodus für Maßnahmen")
