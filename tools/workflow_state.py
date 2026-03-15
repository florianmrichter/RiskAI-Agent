#!/usr/bin/env python3
"""
Workflow-State für FMEA-Automatisierung.

Persistiert den Fortschritt pro task_folder. Ermöglicht dem Agent,
beim Session-Start den nächsten offenen Schritt zu ermitteln.

Usage:
    from tools.workflow_state import load_state, get_next_action, mark_component_done, get_autonomy_mode, set_autonomy_mode, get_report_quality, set_report_quality
    state = load_state("Risikoanalyse/Ethylacetatproduktion_20TA42")
    action = get_next_action("Risikoanalyse/Ethylacetatproduktion_20TA42")
    mode = get_autonomy_mode("Risikoanalyse/Ethylacetatproduktion_20TA42")
    set_autonomy_mode("Risikoanalyse/Ethylacetatproduktion_20TA42", "experte")
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

TASKS_ROOT = Path(__file__).parent.parent / "tasks"
PHASES_ORDER = ["struktur", "fmea", "rpz_validierung", "massnahmen", "report"]


def _state_path(task_folder: str) -> Path:
    return TASKS_ROOT / task_folder / "workflow_state.json"


def load_state(task_folder: str) -> Optional[dict]:
    """Lädt den Workflow-State. None wenn nicht vorhanden."""
    path = _state_path(task_folder)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(task_folder: str, state: dict) -> None:
    """Speichert den Workflow-State."""
    path = _state_path(task_folder)
    path.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_next_action(task_folder: str) -> Optional[dict]:
    """
    Ermittelt die nächste Aktion basierend auf dem State.

    Returns:
        {"action": str, "phase": str, "komp_id": str | None, "phase_status": str} | None
        action: "init_structure" | "analyze_fmea" | "rpz_validierung" | "apply_measures" | "generate_report" | None
    """
    state = load_state(task_folder)
    if state is None:
        return {"action": "init_structure", "phase": "struktur", "komp_id": None, "phase_status": "pending"}

    phases = state.get("phases", {})
    components = state.get("components", {})

    for phase in PHASES_ORDER:
        status = phases.get(phase, "pending")
        if status == "in_progress":
            if phase == "struktur":
                return {"action": "init_structure", "phase": phase, "komp_id": None, "phase_status": status}
            if phase == "fmea":
                next_komp = _next_component_needing(components, "fmea")
                if next_komp:
                    return {"action": "analyze_fmea", "phase": phase, "komp_id": next_komp, "phase_status": status}
                return {"action": "mark_phase_done", "phase": phase, "komp_id": None, "phase_status": status}
            if phase == "rpz_validierung":
                return {"action": "rpz_validierung", "phase": phase, "komp_id": None, "phase_status": status}
            if phase == "massnahmen":
                next_komp = _next_component_needing(components, "measures")
                if next_komp:
                    return {"action": "apply_measures", "phase": phase, "komp_id": next_komp, "phase_status": status}
                return {"action": "mark_phase_done", "phase": phase, "komp_id": None, "phase_status": status}
            if phase == "report":
                return {"action": "generate_report", "phase": phase, "komp_id": None, "phase_status": status}
        if status == "pending":
            if phase == "struktur":
                return {"action": "init_structure", "phase": phase, "komp_id": None, "phase_status": status}
            if phase == "fmea":
                next_komp = _next_component_needing(components, "fmea")
                if next_komp:
                    return {"action": "analyze_fmea", "phase": phase, "komp_id": next_komp, "phase_status": status}
            if phase == "rpz_validierung":
                return {"action": "rpz_validierung", "phase": phase, "komp_id": None, "phase_status": status}
            if phase == "massnahmen":
                next_komp = _next_component_needing(components, "measures")
                if next_komp:
                    return {"action": "apply_measures", "phase": phase, "komp_id": next_komp, "phase_status": status}
            if phase == "report":
                return {"action": "generate_report", "phase": phase, "komp_id": None, "phase_status": status}

    return None


def _next_component_needing(components: dict, step: str) -> Optional[str]:
    """Findet die nächste Komponente, die den Schritt step braucht."""
    def _sort_key(k: str) -> int:
        try:
            return int(k.split("-")[1]) if "-" in k else 0
        except (ValueError, IndexError):
            return 0

    for komp_id in sorted(components.keys(), key=_sort_key):
        c = components.get(komp_id, {})
        if step == "fmea":
            if c.get("fmea") not in ("done", "in_progress"):
                return komp_id
        elif step == "measures":
            if c.get("fmea") == "done" and c.get("measures") not in ("done", "in_progress"):
                return komp_id
    return None


def mark_component_done(task_folder: str, komp_id: str, step: str) -> None:
    """Markiert einen Schritt für eine Komponente als erledigt."""
    state = load_state(task_folder)
    if state is None:
        state = _default_state(task_folder)
    if "components" not in state:
        state["components"] = {}
    if komp_id not in state["components"]:
        state["components"][komp_id] = {}
    state["components"][komp_id][step] = "done"
    state["current_komp_id"] = komp_id
    state["phase"] = state.get("phase", "fmea")
    save_state(task_folder, state)


def mark_component_in_progress(task_folder: str, komp_id: str, step: str) -> None:
    """Markiert einen Schritt für eine Komponente als in Bearbeitung."""
    state = load_state(task_folder)
    if state is None:
        state = _default_state(task_folder)
    if "components" not in state:
        state["components"] = {}
    if komp_id not in state["components"]:
        state["components"][komp_id] = {}
    state["components"][komp_id][step] = "in_progress"
    state["current_komp_id"] = komp_id
    save_state(task_folder, state)


def get_autonomy_mode(task_folder: str) -> str:
    """Returns the current autonomy mode: 'geführt' | 'experte' | 'autonom'. Default: 'geführt'."""
    state = load_state(task_folder)
    if state is None:
        return "geführt"
    return state.get("autonomy_mode", "geführt")


def set_autonomy_mode(task_folder: str, mode: str) -> None:
    """Persist autonomy mode in workflow_state.json. mode: 'geführt' | 'experte' | 'autonom'."""
    valid = {"geführt", "experte", "autonom"}
    if mode not in valid:
        raise ValueError(f"Ungültiger Modus '{mode}'. Erlaubt: {valid}")
    state = load_state(task_folder)
    if state is None:
        state = _default_state(task_folder)
    state["autonomy_mode"] = mode
    save_state(task_folder, state)


def get_report_quality(task_folder: str) -> str:
    """Returns the current report quality: 'ausfuehrlich' | 'reduziert'. Default: 'ausfuehrlich'."""
    state = load_state(task_folder)
    if state is None:
        return "ausfuehrlich"
    return state.get("report_quality", "ausfuehrlich")


def set_report_quality(task_folder: str, quality: str) -> None:
    """Persist report quality in workflow_state.json. quality: 'ausfuehrlich' | 'reduziert'."""
    valid = {"ausfuehrlich", "reduziert"}
    if quality not in valid:
        raise ValueError(f"Ungültige Report-Qualität '{quality}'. Erlaubt: {valid}")
    state = load_state(task_folder)
    if state is None:
        state = _default_state(task_folder)
    state["report_quality"] = quality
    save_state(task_folder, state)


def mark_phase_done(task_folder: str, phase: str) -> None:
    """Markiert eine Phase als abgeschlossen und setzt die nächste auf in_progress."""
    state = load_state(task_folder)
    if state is None:
        state = _default_state(task_folder)
    if "phases" not in state:
        state["phases"] = {p: "pending" for p in PHASES_ORDER}
    state["phases"][phase] = "done"
    idx = PHASES_ORDER.index(phase) if phase in PHASES_ORDER else 0
    next_phase = PHASES_ORDER[idx + 1] if idx + 1 < len(PHASES_ORDER) else None
    if next_phase:
        state["phases"][next_phase] = "in_progress"
        state["phase"] = next_phase
    save_state(task_folder, state)


def init_state_from_structure(task_folder: str, project_id: int, komp_ids: list[str]) -> dict:
    """
    Initialisiert den State nach Strukturanalyse.
    Alle Komponenten werden mit functions/fmea/measures = pending angelegt.
    """
    state = {
        "project_id": project_id,
        "task_folder": task_folder,
        "phase": "fmea",
        "current_komp_id": komp_ids[0] if komp_ids else None,
        "autonomy_mode": "geführt",
        "session_started": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "phases": {
            "struktur": "done",
            "fmea": "in_progress",
            "rpz_validierung": "pending",
            "massnahmen": "pending",
            "report": "pending",
        },
        "components": {kid: {"fmea": "pending", "measures": "pending"} for kid in komp_ids},
    }
    save_state(task_folder, state)
    return state


def get_progress_summary(task_folder: str) -> str:
    """Gibt eine kompakte Fortschrittsanzeige zurück."""
    state = load_state(task_folder)
    if state is None:
        return "Kein State vorhanden."

    components = state.get("components", {})
    total = len(components)
    done_fmea = sum(1 for c in components.values() if c.get("fmea") == "done")
    done_measures = sum(1 for c in components.values() if c.get("measures") == "done")
    current = state.get("current_komp_id", "?")
    phase = state.get("phase", "?")
    elapsed = _calc_elapsed(state)

    return f"Phase: {phase} | Komponente: {current} ({done_fmea}/{total} FMEA) | Maßnahmen: {done_measures}/{total} | {elapsed}"


def _calc_elapsed(state: dict) -> str:
    """Berechnet die verstrichene Session-Zeit."""
    started = state.get("session_started")
    if not started:
        return "Keine Zeiterfassung"
    try:
        start_dt = datetime.fromisoformat(started)
        delta = datetime.now() - start_dt
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        if hours > 0:
            return f"{hours}h {minutes}min"
        return f"{minutes}min"
    except (ValueError, TypeError):
        return "?"


def start_session_timer(task_folder: str) -> None:
    """Setzt den Session-Timer, falls noch nicht gesetzt."""
    state = load_state(task_folder)
    if state is None:
        state = _default_state(task_folder)
    if not state.get("session_started"):
        state["session_started"] = datetime.now().isoformat()
        save_state(task_folder, state)


def _default_state(task_folder: str) -> dict:
    return {
        "project_id": None,
        "task_folder": task_folder,
        "phase": "struktur",
        "current_komp_id": None,
        "autonomy_mode": "geführt",
        "session_started": None,
        "last_updated": datetime.now().isoformat(),
        "phases": {p: "pending" for p in PHASES_ORDER},
        "components": {},
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("task_folder", help="z.B. Risikoanalyse/Ethylacetatproduktion_20TA42")
    ap.add_argument("--action", action="store_true", help="Zeige nächste Aktion")
    args = ap.parse_args()
    if args.action:
        a = get_next_action(args.task_folder)
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        s = load_state(args.task_folder)
        print(json.dumps(s, indent=2, ensure_ascii=False) if s else "Kein State vorhanden.")
