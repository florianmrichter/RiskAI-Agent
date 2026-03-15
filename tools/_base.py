"""
Zentrale Infrastruktur für alle FMEA-Tools.
- Logging (Console + Datei)
- Tool-Entry-Decorator mit Timing und Error-Handling
"""

import logging
import logging.handlers
import time
import functools
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
