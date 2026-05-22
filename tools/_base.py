"""
Zentrale Infrastruktur für alle FMEA-Tools.
- Logging (Console + Datei)
- Tool-Entry-Decorator mit Timing und Error-Handling
"""
from __future__ import annotations

import functools
import json
import logging
import logging.handlers
import time
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "data"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Rotating file handler
_file_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / "fmea.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
)
_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))

# Console handler (nur Warnings+)
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.WARNING)
_console_handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))


def get_logger(name: str) -> logging.Logger:
    """Logger für ein Tool erstellen. Schreibt in Console (WARNING+) und data/fmea.log (DEBUG+)."""
    logger = logging.getLogger(f"fmea.{name}")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_file_handler)
        logger.addHandler(_console_handler)
    return logger


def tool_entry(func):
    """Decorator für Tool-Funktionen: Logging, Timing, Error-Handling.

    Wrapped die Funktion so, dass:
    - Start und Ende geloggt werden (mit Dauer)
    - Fehler abgefangen und als {"success": False, "error": ...} zurückgegeben werden
    - Erfolg als {"success": True, "data": ...} zurückgegeben wird
    """
    logger = get_logger(func.__module__ or func.__name__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        func_name = func.__qualname__
        logger.info(f"START {func_name}")
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"OK {func_name} ({duration:.2f}s)")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"FAIL {func_name} ({duration:.2f}s): {e}", exc_info=True)
            raise

    return wrapper


# ═══════════════════════════════════════════════════════════════
# Shared STOP / RPZ Utilities
# ═══════════════════════════════════════════════════════════════

STOP_ORDER = {"S": 0, "T": 1, "O": 2, "P": 3}

STOP_LABELS = {
    "S": "Substitution",
    "T": "Technisch",
    "O": "Organisatorisch",
    "P": "Persönlich",
}


def _sort_measures_by_stop(measures: list) -> list:
    """Sort measures by STOP hierarchy (S before T before O before P)."""
    return sorted(measures, key=lambda m: STOP_ORDER.get(m.get("stop_kategorie", ""), 99))


# ═══════════════════════════════════════════════════════════════
# Central JSON Config Loader
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent

_config_cache = {}


def load_json_config(relative_path: str, *, cache: bool = True) -> dict | list:
    """Load a JSON config file relative to project root.

    Args:
        relative_path: Path relative to project root (e.g. 'config/reliability_data.json')
        cache: If True, cache the parsed result for repeated calls.

    Returns:
        Parsed JSON data (dict or list).

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if cache and relative_path in _config_cache:
        return _config_cache[relative_path]

    path = PROJECT_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if cache:
        _config_cache[relative_path] = data
    return data
