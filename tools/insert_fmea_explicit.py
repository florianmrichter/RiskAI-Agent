#!/usr/bin/env python3
"""
Fügt explizit definierte FMEA-Daten (Funktionen, Fehlermodi, Ursachen, Folgen, S/O/D)
für eine Komponente in die Datenbank ein.

Keine generische Logik. Jeder Eintrag muss vom Agent einzeln analysiert und hier
explizit definiert sein.

Usage:
    from tools.insert_fmea_explicit import insert_fmea_for_component
    from tools.fmea_loader import get_fmea_for_component
    insert_fmea_for_component(project_id, "<komp_id>", task_folder="Risikoanalyse/Ethylacetatproduktion_20TA42")
    # oder mit expliziten Daten:
    insert_fmea_for_component(project_id, "<komp_id>", fmea_data=my_data)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.storage import FMEAStorage


def insert_fmea_for_component(
    project_id: int,
    komp_id: str,
    fmea_data: dict = None,
    task_folder: str = None,
    db_path: str = None,
) -> dict:
    """
    Fügt FMEA-Daten für eine Komponente ein.

    fmea_data: {
        "functions": [
            {
                "funktion_id": "<komp_id>-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "...",
                "anforderungen": [{"id": "...", "parameter": "...", "sollwert": "..."}]
            }
        ],
        "failure_modes": [
            {
                "funktion_id": "<komp_id>-F1",
                "fehlermodus": "...",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "...", "beschreibung": "...", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "..."}
                ],
                "effects": {
                    "mensch": ("Stufe", "Beschreibung"),
                    "umwelt": ("Stufe", "Beschreibung"),
                    "anlage": ("Stufe", "Beschreibung"),
                    "kosten": ("Stufe", "Beschreibung"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "...", "beeinflusst": "D", "einschraenkung": "..."}
                ],
                "S": 8, "O": 3, "D": 5,
                "begruendung_S": "...", "begruendung_O": "...", "begruendung_D": "...",
                "kontext_beschreibung": "...", "controls_einschraenkung": "..."
            }
        ]
    }

    Returns: {"functions": n, "failure_modes": n}
    """
    if fmea_data is None and task_folder:
        from tools.fmea_loader import get_fmea_for_component
        fmea_data = get_fmea_for_component(task_folder, komp_id)
    if not fmea_data:
        raise ValueError(f"Keine FMEA-Daten für {komp_id}. Bitte task_folder angeben oder fmea_data übergeben.")

    db = FMEAStorage(db_path)
    comp = db.get_component_by_komp_id(komp_id)
    if not comp:
        db.close()
        raise ValueError(f"Komponente {komp_id} nicht gefunden")

    comp_id = comp["id"]
    func_id_to_db_id = {}
    stats = {"functions": 0, "failure_modes": 0}

    for func in fmea_data.get("functions", []):
        fid = db.insert_function(
            comp_id,
            func["funktion_id"],
            func["typ"],
            func["beschreibung"],
            func.get("anforderungen", []),
        )
        func_id_to_db_id[func["funktion_id"]] = fid
        stats["functions"] += 1

    for fm in fmea_data.get("failure_modes", []):
        func_id = fm["funktion_id"]
        if func_id not in func_id_to_db_id:
            func_row = db.get_function_by_funktion_id(func_id)
            if func_row:
                func_id_to_db_id[func_id] = func_row["id"]
            else:
                continue
        func_db_id = func_id_to_db_id[func_id]

        fehler_id = fm.get("fehler_id")
        if not fehler_id:
            existing = db.get_failure_modes(func_db_id)
            fehler_id = f"{func_id}-FM{len(existing)+1}"

        fm_id = db.insert_failure_mode(
            func_db_id,
            fehler_id,
            fm["fehlermodus"],
            fm["fehlerart"],
            kontext_beschreibung=fm.get("kontext_beschreibung"),
            controls_einschraenkung=fm.get("controls_einschraenkung"),
        )
        stats["failure_modes"] += 1

        for uc in fm.get("causes", []):
            db.insert_failure_cause(
                fm_id,
                uc["ursache_id"],
                uc["beschreibung"],
                uc["herkunft"],
                uc.get("praeventionsphase") or uc.get("phase", "Betrieb"),
                uc.get("praeventionshinweis") or uc.get("hinweis"),
            )

        e = fm.get("effects", {})
        if e:
            db.insert_failure_effect(
                fm_id,
                mensch_stufe=e.get("mensch", ("", ""))[0],
                mensch_beschreibung=e.get("mensch", ("", ""))[1],
                umwelt_stufe=e.get("umwelt", ("", ""))[0],
                umwelt_beschreibung=e.get("umwelt", ("", ""))[1],
                anlage_stufe=e.get("anlage", ("", ""))[0],
                anlage_beschreibung=e.get("anlage", ("", ""))[1],
                kosten_stufe=e.get("kosten", ("", ""))[0],
                kosten_beschreibung=e.get("kosten", ("", ""))[1],
            )

        for ctrl in fm.get("controls", []):
            db.insert_current_control(
                fm_id,
                ctrl["name"],
                ctrl["typ"],
                ctrl["wirkung"],
                ctrl.get("sil_level"),
                ctrl.get("beschreibung"),
                ctrl.get("beeinflusst"),
                ctrl.get("einschraenkung"),
            )

        db.insert_risk_assessment(
            fm_id,
            S=fm["S"],
            O=fm["O"],
            D=fm["D"],
            begruendung_S=fm.get("begruendung_S"),
            begruendung_O=fm.get("begruendung_O"),
            begruendung_D=fm.get("begruendung_D"),
        )

    db.close()

    if task_folder:
        from tools.workflow_state import mark_component_done
        mark_component_done(task_folder, komp_id, "fmea")

    return stats
