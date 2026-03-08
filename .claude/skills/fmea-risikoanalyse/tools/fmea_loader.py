#!/usr/bin/env python3
"""
Dynamischer Import von FMEA- und Maßnahmen-Config aus tasks/{task_folder}/.

Ermöglicht projektspezifische Config-Dateien pro task_folder.

Usage:
    from tools.fmea_loader import get_fmea_for_component, load_measures_module
    fmea_data = get_fmea_for_component("Risikoanalyse/Ethylacetatproduktion_20TA42", "<komp_id>")
    mod = load_measures_module("Risikoanalyse/Ethylacetatproduktion_20TA42")
"""

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

TASKS_ROOT = Path(__file__).parent.parent / "tasks"


def get_fmea_for_component(task_folder: str, komp_id: str) -> dict:
    """Lädt FMEA-Daten für eine Komponente aus tasks/{task_folder}/fmea_explicit.py."""
    mod = _load_module(task_folder, "fmea_explicit")
    if mod is None:
        return {}
    return getattr(mod, "get_fmea_for_component", lambda _: {})(komp_id)


def load_measures_module(task_folder: str):
    """
    Lädt das Maßnahmen-Modul aus tasks/{task_folder}/measures_explicit.py.
    Returns: Modul mit get_measures_for_fehlermodus und allen _xxx-Helferfunktionen.
    """
    return _load_module(task_folder, "measures_explicit")


def _load_module(task_folder: str, module_name: str):
    """Lädt ein Python-Modul aus tasks/{task_folder}/{module_name}.py.
    task_folder kann Pfad sein, z.B. Risikoanalyse/Ethylacetatproduktion_20TA42."""
    path = TASKS_ROOT / task_folder / f"{module_name}.py"
    if not path.exists():
        return None
    mod_name = f"tasks.{task_folder.replace('/', '.')}.{module_name}"
    spec = importlib.util.spec_from_file_location(
        mod_name,
        path,
        submodule_search_locations=[str(path.parent)],
    )
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod
