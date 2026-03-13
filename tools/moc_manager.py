"""
Management of Change (MoC) Tool für das FMEA-System.

Ermöglicht das Einfrieren von Versionen und das Anlegen neuer Versionen
mit selektiver Neubewertung betroffener Komponenten.

Usage:
    from tools.moc_manager import freeze_version, create_new_version, get_version_history, get_delta
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage

TASKS_ROOT = Path(__file__).parent.parent / "tasks"


# ── Versionen einfrieren ──

def freeze_version(project_id: int, db_path: str = None) -> dict:
    """
    Friert ein Projekt ein (frozen=1) und erstellt einen JSON-Snapshot.

    Returns:
        {"success": True, "snapshot_path": str, "project": dict}
    """
    db = FMEAStorage(db_path)
    project = db.get_project(project_id)
    if not project:
        db.close()
        raise ValueError(f"Projekt {project_id} nicht gefunden")

    if project.get("frozen"):
        db.close()
        return {"success": False, "error": f"Projekt {project_id} ist bereits eingefroren"}

    # Snapshot erstellen
    task_folder = project.get("task_folder")
    if task_folder:
        versions_dir = TASKS_ROOT / task_folder / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        version = project.get("version", "1.0")
        snapshot_path = versions_dir / f"v{version}_snapshot.json"

        fmea_data = db.get_full_fmea_data(project_id)
        snapshot = {
            "project": dict(project),
            "fmea_data": fmea_data,
            "frozen_at": datetime.now().isoformat(),
        }
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
    else:
        snapshot_path = None

    # Einfrieren in DB
    db.freeze_project(project_id)
    updated = db.get_project(project_id)
    db.close()

    return {
        "success": True,
        "snapshot_path": str(snapshot_path) if snapshot_path else None,
        "project": updated,
    }


# ── Neue Version anlegen ──

def create_new_version(project_id: int, change_description: str,
                       changed_components: list, new_version: str = None,
                       erstellt_von: str = None, db_path: str = None) -> dict:
    """
    Legt eine neue Projektversion an. Kopiert unveränderte Komponenten,
    markiert betroffene Komponenten als 'neu_bewertet'.

    Args:
        project_id: ID des Eltern-Projekts (wird eingefroren)
        change_description: Beschreibung der Änderung (z.B. "Pumpe P-101 ersetzt")
        changed_components: Liste der betroffenen komp_ids (z.B. ["KOMP-002"])
        new_version: Versionsnummer der neuen Version (auto wenn None)
        erstellt_von: Name des Erstellers

    Returns:
        {"success": True, "new_project_id": int, "copied_fms": int, "affected_components": list}
    """
    db = FMEAStorage(db_path)
    parent = db.get_project(project_id)
    if not parent:
        db.close()
        raise ValueError(f"Eltern-Projekt {project_id} nicht gefunden")

    # Eltern-Version einfrieren
    if not parent.get("frozen"):
        freeze_version(project_id, db_path)

    # Versionsnummer ableiten
    if new_version is None:
        parent_ver = parent.get("version", "1.0")
        try:
            major, minor = parent_ver.split(".")
            new_version = f"{major}.{int(minor) + 1}"
        except Exception:
            new_version = "2.0"

    # Neues Projekt anlegen
    new_project_id = db.create_project(
        name=parent["name"],
        anlage_name=parent.get("anlage_name"),
        task_folder=parent.get("task_folder"),
        version=new_version,
        parent_version_id=project_id,
        version_beschreibung=change_description,
        erstellt_von=erstellt_von,
    )

    # Komponenten, Funktionen, Fehlermodi kopieren
    components = db.get_components(project_id)
    changed_set = set(changed_components)
    copied_fms = 0

    for comp in components:
        komp_id = comp["komp_id"]
        is_changed = komp_id in changed_set

        new_comp_id = db.insert_component(
            project_id=new_project_id,
            komp_id=komp_id,
            name=comp["name"],
            typ=comp["typ"],
            kategorie=comp["kategorie"],
            system_name=comp.get("system_name"),
            beschreibung=comp.get("beschreibung"),
            parameters=comp.get("parameters", {}),
            kontext=comp.get("kontext", {}),
        )

        functions = db.get_functions(comp["id"])
        for func in functions:
            new_func_id = db.insert_function(
                component_id=new_comp_id,
                funktion_id=func["funktion_id"],
                typ=func["typ"],
                beschreibung=func["beschreibung"],
                anforderungen=func.get("anforderungen", []),
            )
            if not new_func_id:
                continue

            fms = db.get_failure_modes(func["id"])
            for fm in fms:
                moc_status = "neu_bewertet" if is_changed else "unverändert"
                new_fm_id = db.insert_failure_mode(
                    function_id=new_func_id,
                    fehler_id=fm["fehler_id"],
                    fehlermodus=fm["fehlermodus"],
                    fehlerart=fm["fehlerart"],
                    kontext_beschreibung=fm.get("kontext_beschreibung"),
                    controls_einschraenkung=fm.get("controls_einschraenkung"),
                )
                if not new_fm_id:
                    continue

                # moc_status + herkunft setzen
                db.conn.execute(
                    "UPDATE failure_modes SET moc_status=?, moc_herkunft_version=? WHERE id=?",
                    (moc_status, parent.get("version", "1.0"), new_fm_id)
                )
                db.conn.commit()

                if not is_changed:
                    # Unveränderte FMs: Daten 1:1 übernehmen
                    _copy_fm_data(db, fm["id"], new_fm_id)
                    copied_fms += 1

    db.close()
    return {
        "success": True,
        "new_project_id": new_project_id,
        "new_version": new_version,
        "copied_fms": copied_fms,
        "affected_components": list(changed_set),
        "unchanged_components": [c["komp_id"] for c in components if c["komp_id"] not in changed_set],
    }


def _copy_fm_data(db: FMEAStorage, source_fm_id: int, target_fm_id: int):
    """Kopiert Causes, Effects, Risk, Controls, Measures von einer FM in eine andere."""
    for cause in db.get_failure_causes(source_fm_id):
        try:
            db.insert_failure_cause(
                failure_mode_id=target_fm_id,
                ursache_id=cause["ursache_id"],
                beschreibung=cause["beschreibung"],
                herkunft=cause["herkunft"],
                praeventionsphase=cause["praeventionsphase"],
                praeventionshinweis=cause.get("praeventionshinweis"),
            )
        except Exception:
            pass

    effect = db.get_failure_effect(source_fm_id)
    if effect:
        db.insert_failure_effect(
            failure_mode_id=target_fm_id,
            mensch_stufe=effect.get("mensch_stufe"),
            mensch_beschreibung=effect.get("mensch_beschreibung"),
            umwelt_stufe=effect.get("umwelt_stufe"),
            umwelt_beschreibung=effect.get("umwelt_beschreibung"),
            anlage_stufe=effect.get("anlage_stufe"),
            anlage_beschreibung=effect.get("anlage_beschreibung"),
            kosten_stufe=effect.get("kosten_stufe"),
            kosten_beschreibung=effect.get("kosten_beschreibung"),
        )

    risk = db.get_risk_assessment(source_fm_id)
    if risk:
        db.insert_risk_assessment(
            failure_mode_id=target_fm_id,
            S=risk["S"], O=risk["O"], D=risk["D"],
            begruendung_S=risk.get("begruendung_S"),
            begruendung_O=risk.get("begruendung_O"),
            begruendung_D=risk.get("begruendung_D"),
            rpz=risk["rpz"],
            rpz_status=risk["rpz_status"],
            override_applied=risk.get("override_applied"),
            daten_konfidenz=risk.get("daten_konfidenz", "mittel"),
            agent_konfidenz=risk.get("agent_konfidenz", "mittel"),
            agent_konfidenz_begruendung=risk.get("agent_konfidenz_begruendung"),
            daten_quelle=risk.get("daten_quelle"),
        )

    for ctrl in db.get_current_controls(source_fm_id):
        db.insert_current_control(
            failure_mode_id=target_fm_id,
            name=ctrl["name"],
            typ=ctrl["typ"],
            wirkung=ctrl["wirkung"],
            sil_level=ctrl.get("sil_level"),
            beschreibung=ctrl.get("beschreibung"),
            beeinflusst=ctrl.get("beeinflusst"),
            einschraenkung=ctrl.get("einschraenkung"),
        )

    for m in db.get_measures(source_fm_id):
        db.insert_measure(
            failure_mode_id=target_fm_id,
            name=m["name"],
            abe_kategorie=m["abe_kategorie"],
            stop_kategorie=m.get("stop_kategorie"),
            beschreibung=m["beschreibung"],
            ziel=m.get("ziel"),
            S_neu=m.get("S_neu"),
            O_neu=m.get("O_neu"),
            D_neu=m.get("D_neu"),
            rpz_neu=m.get("rpz_neu"),
            rpz_status_neu=m.get("rpz_status_neu"),
            begruendung=m.get("begruendung"),
            hinweis=m.get("hinweis"),
            iteration=m.get("iteration", 1),
            prioritaet=m.get("prioritaet", "empfohlen"),
            aufwand=m.get("aufwand"),
            kosten_klasse=m.get("kosten_klasse"),
            assigned_to=m.get("assigned_to"),
            target_date=m.get("target_date"),
            implementation_status=m.get("implementation_status", "geplant"),
        )


# ── Versionshistorie ──

def get_version_history(task_folder: str, db_path: str = None) -> list:
    """Gibt alle Versionen eines Projekts zurück, geordnet nach ID."""
    db = FMEAStorage(db_path)
    versions = db.get_project_versions(task_folder)
    db.close()
    return versions


# ── Delta zwischen Versionen ──

def get_delta(project_id_old: int, project_id_new: int, db_path: str = None) -> dict:
    """
    Vergleicht zwei Projektversionen und gibt ein strukturiertes Delta zurück.

    Returns:
        {
            "changed": [{"fehler_id": str, "old": {...}, "new": {...}}],
            "added": [fm_dict],
            "removed": [fm_dict],
            "unchanged_count": int,
        }
    """
    db = FMEAStorage(db_path)
    old_fmea = {fm["fehler_id"]: fm for fm in db.get_full_fmea_data(project_id_old)}
    new_fmea = {fm["fehler_id"]: fm for fm in db.get_full_fmea_data(project_id_new)}
    db.close()

    changed = []
    added = []
    removed = []
    unchanged_count = 0

    for fid, fm_new in new_fmea.items():
        if fid not in old_fmea:
            added.append(fm_new)
        else:
            fm_old = old_fmea[fid]
            if (fm_old.get("S") != fm_new.get("S") or
                    fm_old.get("O") != fm_new.get("O") or
                    fm_old.get("D") != fm_new.get("D")):
                changed.append({
                    "fehler_id": fid,
                    "old": fm_old,
                    "new": fm_new,
                    "s_delta": (fm_new.get("S", 0) or 0) - (fm_old.get("S", 0) or 0),
                    "o_delta": (fm_new.get("O", 0) or 0) - (fm_old.get("O", 0) or 0),
                    "d_delta": (fm_new.get("D", 0) or 0) - (fm_old.get("D", 0) or 0),
                    "rpz_delta": (fm_new.get("rpz", 0) or 0) - (fm_old.get("rpz", 0) or 0),
                })
            else:
                unchanged_count += 1

    for fid, fm_old in old_fmea.items():
        if fid not in new_fmea:
            removed.append(fm_old)

    return {
        "changed": changed,
        "added": added,
        "removed": removed,
        "unchanged_count": unchanged_count,
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="FMEA Management of Change")
    sub = ap.add_subparsers(dest="cmd")

    p_freeze = sub.add_parser("freeze", help="Version einfrieren")
    p_freeze.add_argument("project_id", type=int)

    p_history = sub.add_parser("history", help="Versionshistorie anzeigen")
    p_history.add_argument("task_folder")

    p_delta = sub.add_parser("delta", help="Delta zwischen zwei Versionen")
    p_delta.add_argument("old_project_id", type=int)
    p_delta.add_argument("new_project_id", type=int)

    args = ap.parse_args()

    if args.cmd == "freeze":
        result = freeze_version(args.project_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.cmd == "history":
        versions = get_version_history(args.task_folder)
        for v in versions:
            print(f"v{v.get('version', '?')} | ID={v['id']} | {v['datum'][:10]} | frozen={v.get('frozen', 0)}")
    elif args.cmd == "delta":
        delta = get_delta(args.old_project_id, args.new_project_id)
        print(f"Geändert: {len(delta['changed'])} | Hinzugefügt: {len(delta['added'])} | Entfernt: {len(delta['removed'])} | Unverändert: {delta['unchanged_count']}")
    else:
        ap.print_help()
