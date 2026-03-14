"""
FMEA Chat Server — FastAPI + SSE File-Bridge

Connects the FMEA HTML report (browser) to the running Claude Code agent
via JSON files acting as an inbox/outbox bridge.

Usage:
    python3 tools/fmea_chat_server.py <task_folder>
    # e.g.: python3 tools/fmea_chat_server.py tasks/Risikoanalyse/Ethylacetatproduktion_20TA41

The server picks a free port and writes it to {task_folder}/.chat_server_port
"""

import asyncio
import json
import socket
import sys
import time
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

# ── Setup ─────────────────────────────────────────────────────────────────────

if len(sys.argv) < 2:
    print("Usage: python3 tools/fmea_chat_server.py <task_folder>")
    sys.exit(1)

_repo_root = Path(__file__).parent.parent
task_folder = _repo_root / sys.argv[1]
task_folder.mkdir(parents=True, exist_ok=True)

INBOX_FILE  = task_folder / "chat_inbox.json"
OUTBOX_FILE = task_folder / "chat_outbox.json"
STATUS_FILE = task_folder / "agent_status.json"
PORT_FILE   = task_folder / ".chat_server_port"

# Initialise files if they don't exist
def _init_files():
    if not INBOX_FILE.exists():
        INBOX_FILE.write_text("[]", encoding="utf-8")
    if not OUTBOX_FILE.exists():
        OUTBOX_FILE.write_text("[]", encoding="utf-8")
    if not STATUS_FILE.exists():
        STATUS_FILE.write_text('{"text":"","done":true,"ts":0}', encoding="utf-8")

_init_files()

# ── Find the HTML report ───────────────────────────────────────────────────────

def _find_html_report() -> Path | None:
    candidates = list(task_folder.glob("*.html"))
    if candidates:
        # Prefer files with "bericht" or "report" in name
        for c in candidates:
            if "bericht" in c.name.lower() or "report" in c.name.lower():
                return c
        return candidates[0]
    return None


# ── Free port helper ──────────────────────────────────────────────────────────

def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


PORT = _get_free_port()
PORT_FILE.write_text(str(PORT), encoding="utf-8")
print(f"[fmea-chat-server] Task folder : {task_folder}")
print(f"[fmea-chat-server] Listening on: http://localhost:{PORT}")

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="FMEA Chat Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SSE state ─────────────────────────────────────────────────────────────────

_sse_queues: list[asyncio.Queue] = []
_last_outbox_len = 0
_last_status_ts  = 0


async def _file_watcher():
    """Poll inbox/outbox/status files every 500ms and push SSE events."""
    global _last_outbox_len, _last_status_ts
    while True:
        await asyncio.sleep(0.5)
        try:
            # Outbox: push new replies
            outbox = json.loads(OUTBOX_FILE.read_text(encoding="utf-8"))
            if len(outbox) > _last_outbox_len:
                new_msgs = outbox[_last_outbox_len:]
                _last_outbox_len = len(outbox)
                for msg in new_msgs:
                    event = json.dumps({"type": "reply", "data": msg})
                    for q in list(_sse_queues):
                        await q.put(event)

            # Status: push if changed
            status = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            if status.get("ts", 0) != _last_status_ts:
                _last_status_ts = status.get("ts", 0)
                event = json.dumps({"type": "status", "data": status})
                for q in list(_sse_queues):
                    await q.put(event)
        except Exception:
            pass  # silently ignore transient read errors


@app.on_event("startup")
async def startup():
    asyncio.create_task(_file_watcher())


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_report():
    """Serve the FMEA HTML report, injecting the chat server port."""
    html_path = _find_html_report()
    if not html_path:
        return HTMLResponse("<h2>Kein HTML-Report gefunden in " + str(task_folder) + "</h2>", status_code=404)

    html = html_path.read_text(encoding="utf-8")
    # Inject port before </head> or at top of <body>
    inject = f"<script>const CHAT_SERVER_PORT = {PORT};</script>\n"
    if "</head>" in html:
        html = html.replace("</head>", inject + "</head>", 1)
    elif "<body" in html:
        idx = html.index("<body")
        insert_at = html.index(">", idx) + 1
        html = html[:insert_at] + "\n" + inject + html[insert_at:]
    return HTMLResponse(html)


@app.post("/chat/send")
async def chat_send(request: Request):
    """Receive a message from the browser, write to inbox."""
    body = await request.json()
    text    = body.get("text", "").strip()
    context = body.get("context", "")
    if not text:
        return JSONResponse({"error": "empty message"}, status_code=400)

    msg_id = str(uuid.uuid4())[:8]
    entry = {
        "id":      msg_id,
        "text":    text,
        "context": context,
        "ts":      int(time.time()),
        "status":  "pending",
    }

    inbox = json.loads(INBOX_FILE.read_text(encoding="utf-8"))
    inbox.append(entry)
    INBOX_FILE.write_text(json.dumps(inbox, ensure_ascii=False, indent=2), encoding="utf-8")

    return JSONResponse({"id": msg_id, "ok": True})


@app.get("/events")
async def sse_events(request: Request):
    """Server-Sent Events stream — pushes replies and agent status."""
    q: asyncio.Queue = asyncio.Queue()
    _sse_queues.append(q)

    async def generator():
        try:
            # Send current status immediately on connect
            try:
                status = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
                yield f"data: {json.dumps({'type': 'status', 'data': status})}\n\n"
            except Exception:
                pass
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {event}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            _sse_queues.remove(q)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/status")
async def get_status():
    """Return current agent_status.json."""
    status = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    return JSONResponse(status)


@app.get("/outbox")
async def get_outbox():
    """Return full outbox (for reconnect/recovery)."""
    outbox = json.loads(OUTBOX_FILE.read_text(encoding="utf-8"))
    return JSONResponse(outbox)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
