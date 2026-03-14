"""
Set agent status — writes a human-readable status message to agent_status.json.

Usage:
    python3 tools/set_agent_status.py "Analysiere Betriebsdrücke für Ventil V-101…"
    python3 tools/set_agent_status.py "done"   # marks work as complete (shows ✓ in chat panel)

Requires .active_task_folder file in repo root pointing to the current task folder.
"""

import json
import sys
import time
from pathlib import Path

_repo_root = Path(__file__).parent.parent
active_task_file = _repo_root / ".active_task_folder"

if not active_task_file.exists():
    sys.exit(0)  # silently do nothing if no active task

task_folder = _repo_root / active_task_file.read_text(encoding="utf-8").strip()
status_file = task_folder / "agent_status.json"

msg = sys.argv[1] if len(sys.argv) > 1 else ""
status = {
    "text": msg,
    "done": msg == "done",
    "ts":   int(time.time()),
}

task_folder.mkdir(parents=True, exist_ok=True)
status_file.write_text(json.dumps(status, ensure_ascii=False), encoding="utf-8")
