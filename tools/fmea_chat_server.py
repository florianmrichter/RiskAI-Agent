"""
FMEA Chat Server — FastAPI + SSE File-Bridge

Connects the FMEA HTML report (browser) to the running Claude Code agent
via JSON files acting as an inbox/outbox bridge.

Usage:
    python3 tools/fmea_chat_server.py <task_folder>
    # e.g.: python3 tools/fmea_chat_server.py tasks/Risikoanalyse/Ethylacetatproduktion_20TA41

The server picks a free port and writes it to {task_folder}/.chat_server_port
"""

from __future__ import annotations

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

def _inline_file_uris(html: str) -> str:
    """Replace file:// CSS <link> tags with inline <style> blocks.
    Also replaces file:// image src with base64 data URIs."""
    import re, base64
    from urllib.parse import unquote

    def _uri_to_path(raw: str) -> str | None:
        if raw.startswith("file:///"):
            return unquote(raw[7:])
        if raw.startswith("file://"):
            return unquote(raw[6:])
        return None

    # Inline CSS — handles both attribute orderings and URL-encoded paths
    def replace_css(m):
        fpath = _uri_to_path(m.group(1))
        if not fpath:
            return m.group(0)
        try:
            css_text = Path(fpath).read_text(encoding="utf-8")
            return f"<style>{css_text}</style>"
        except Exception:
            return m.group(0)

    html = re.sub(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>',
                  replace_css, html)
    html = re.sub(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\'][^>]*/?>',
                  replace_css, html)

    # Inline images
    def replace_img(m):
        fpath = _uri_to_path(m.group(1))
        if not fpath:
            return m.group(0)
        try:
            data = Path(fpath).read_bytes()
            b64 = base64.b64encode(data).decode()
            return f'src="data:image/png;base64,{b64}"'
        except Exception:
            return m.group(0)

    html = re.sub(r'src="(file://[^"]+)"', replace_img, html)
    return html


_CHAT_PANEL_CSS = """
<style>
#chat-toggle{position:fixed;top:20px;right:20px;z-index:1100;width:44px;height:44px;border-radius:50%;border:none;background:#2C2C54;color:white;font-size:20px;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;transition:background 0.2s,transform 0.15s;}
#chat-toggle:hover{background:#F5004F;transform:scale(1.08);}
.chat-panel{position:fixed;top:0;right:-420px;width:390px;height:100vh;background:#fff;border-left:1px solid #E5E7EB;box-shadow:-4px 0 24px rgba(0,0,0,0.12);z-index:1050;display:flex;flex-direction:column;transition:right 0.3s cubic-bezier(0.4,0,0.2,1);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
.chat-panel--open{right:0;}
.chat-header{background:#2C2C54;color:white;padding:14px 16px;display:flex;align-items:center;gap:10px;font-weight:700;font-size:15px;flex-shrink:0;}
.chat-header span:first-child{flex:1;}
.chat-header button{background:none;border:none;color:rgba(255,255,255,0.7);font-size:18px;cursor:pointer;padding:2px 6px;border-radius:4px;line-height:1;}
.chat-header button:hover{color:white;background:rgba(255,255,255,0.1);}
.agent-status-chip{font-size:11px;font-weight:400;color:rgba(255,255,255,0.8);background:rgba(255,255,255,0.12);padding:2px 8px;border-radius:20px;max-width:160px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.agent-status-chip:empty{display:none;}
.agent-status-chip.done{color:#4ade80;}
.chat-messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;}
.chat-message{max-width:86%;padding:10px 13px;border-radius:14px;font-size:13.5px;line-height:1.5;word-break:break-word;white-space:pre-wrap;}
.chat-message.user{background:#2C2C54;color:white;align-self:flex-end;border-bottom-right-radius:4px;}
.chat-message.assistant{background:#F3F4F6;color:#1F2937;align-self:flex-start;border-bottom-left-radius:4px;}
.chat-message.assistant.thinking{color:#9CA3AF;font-style:italic;}
#context-chip-area{padding:0 12px 6px;display:flex;flex-wrap:wrap;gap:6px;flex-shrink:0;}
.context-chip{background:#EEF2FF;color:#4338CA;border:1px solid #C7D2FE;border-radius:20px;padding:3px 10px;font-size:12px;display:flex;align-items:center;gap:5px;max-width:240px;overflow:hidden;}
.context-chip span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.context-chip button{background:none;border:none;cursor:pointer;color:#6366F1;font-size:13px;padding:0;line-height:1;flex-shrink:0;}
.chat-input-row{display:flex;gap:8px;padding:10px 12px 14px;border-top:1px solid #E5E7EB;flex-shrink:0;align-items:flex-end;}
#chat-input{flex:1;border:1px solid #D1D5DB;border-radius:10px;padding:8px 12px;font-size:13.5px;font-family:inherit;resize:none;outline:none;min-height:38px;max-height:120px;overflow-y:auto;}
#chat-input:focus{border-color:#2C2C54;}
.chat-input-row button{background:#F5004F;color:white;border:none;border-radius:10px;width:38px;height:38px;font-size:17px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.chat-input-row button:hover{background:#d4003e;}
.chat-input-row button:disabled{background:#9CA3AF;cursor:not-allowed;}
.selection-popover{position:fixed;z-index:1200;background:#2C2C54;color:white;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.2);white-space:nowrap;pointer-events:all;user-select:none;}
.selection-popover:hover{background:#F5004F;}
@media print{#chat-toggle,#chat-panel{display:none!important;}}
</style>
"""

_CHAT_PANEL_HTML = """
<button id="chat-toggle" onclick="toggleChat()" title="Chat öffnen/schließen">💬</button>
<div id="chat-panel" class="chat-panel">
  <div class="chat-header">
    <span>Risk AI Agent</span>
    <div id="agent-status-chip" class="agent-status-chip"></div>
    <button onclick="toggleChat()" title="Schließen">✕</button>
  </div>
  <div id="chat-messages" class="chat-messages"></div>
  <div id="context-chip-area"></div>
  <div class="chat-input-row">
    <textarea id="chat-input" placeholder="Frage zum Bericht stellen…" rows="2" onkeydown="handleInputKey(event)"></textarea>
    <button id="send-btn" onclick="sendMessage()" title="Senden">➤</button>
  </div>
</div>
<div id="selection-popover" class="selection-popover" style="display:none" onclick="addSelectionToContext()">💬 Im Chat besprechen</div>
<script>
var _PORT=typeof CHAT_SERVER_PORT!=='undefined'?CHAT_SERVER_PORT:null;
var BASE=_PORT?'http://localhost:'+_PORT:null;
var _chatOpen=false,_pendingContext=[],_eventSource=null,_selectedText='';
function toggleChat(){_chatOpen=!_chatOpen;var p=document.getElementById('chat-panel');var btn=document.getElementById('chat-toggle');var shell=document.querySelector('.app-shell')||document.body;p.classList.toggle('chat-panel--open',_chatOpen);btn.style.display=_chatOpen?'none':'flex';shell.style.transition='margin-right 0.3s cubic-bezier(0.4,0,0.2,1)';shell.style.marginRight=_chatOpen?'390px':'0';if(_chatOpen&&!_eventSource){_connectSSE();_recoverOutbox();}if(_chatOpen)setTimeout(function(){document.getElementById('chat-input').focus();},300);}
function _appendMessage(role,text,msgId){var box=document.getElementById('chat-messages');var prev=msgId?box.querySelector('[data-msgid="'+msgId+'"]'):null;if(prev){prev.textContent=text;prev.classList.remove('thinking');return;}var div=document.createElement('div');div.className='chat-message '+role;div.textContent=text;if(msgId)div.dataset.msgid=msgId;box.appendChild(div);box.scrollTop=box.scrollHeight;}
async function sendMessage(){if(!BASE){_appendMessage('assistant','Chat-Server nicht verfügbar.');return;}var input=document.getElementById('chat-input');var text=input.value.trim();if(!text)return;var context=_pendingContext.map(function(c){return c.text;}).join(' | ');_appendMessage('user',text+(context?'\\n[Kontext: '+context+']':''));input.value='';_clearContextChips();var thinkId='thinking-'+Date.now();_appendMessage('assistant thinking','Warte auf Antwort…',thinkId);document.getElementById('send-btn').disabled=true;try{await fetch(BASE+'/chat/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:text,context:context})});}catch(e){_appendMessage('assistant','Fehler: '+e.message,thinkId);}finally{document.getElementById('send-btn').disabled=false;}}
function handleInputKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}}
function _connectSSE(){if(!BASE)return;if(_eventSource)_eventSource.close();_eventSource=new EventSource(BASE+'/events');_eventSource.onmessage=function(e){try{var p=JSON.parse(e.data);if(p.type==='reply'){var box=document.getElementById('chat-messages');var t=box.querySelector('.chat-message.thinking');if(t)t.parentNode.removeChild(t);_appendMessage('assistant',p.data.text);}else if(p.type==='status'){_updateStatusChip(p.data);}}catch(err){}};_eventSource.onerror=function(){setTimeout(_connectSSE,3000);};}
async function _recoverOutbox(){if(!BASE)return;try{var res=await fetch(BASE+'/outbox');var msgs=await res.json();var box=document.getElementById('chat-messages');if(box.children.length===0&&msgs.length>0)msgs.forEach(function(m){_appendMessage('assistant',m.text);});}catch(err){}}
function _updateStatusChip(status){var chip=document.getElementById('agent-status-chip');if(!status||!status.text||status.text==='done'){chip.textContent=(status&&status.done)?'Bereit':'';chip.className='agent-status-chip'+((status&&status.done)?' done':'');}else{chip.textContent=status.text;chip.className='agent-status-chip';}}
document.addEventListener('mouseup',_onTextSelect);document.addEventListener('keyup',_onTextSelect);
function _onTextSelect(){var sel=window.getSelection();var txt=sel?sel.toString().trim():'';if(txt.length<10){_hidePopover();return;}_selectedText=txt;var r=sel.getRangeAt(0).getBoundingClientRect();_showPopover(r.left+r.width/2,r.top+window.scrollY-52);}
function _showPopover(x,y){var pop=document.getElementById('selection-popover');pop.style.display='block';pop.style.left=Math.min(x,window.innerWidth-220)+'px';pop.style.top=y+'px';}
function _hidePopover(){document.getElementById('selection-popover').style.display='none';_selectedText='';}
document.addEventListener('mousedown',function(e){if(!e.target.closest('#selection-popover'))_hidePopover();});
function addSelectionToContext(){if(!_selectedText)return;var id='ctx-'+Date.now();_pendingContext.push({id:id,text:_selectedText});_renderContextChips();_hidePopover();window.getSelection().removeAllRanges();if(!_chatOpen)toggleChat();}
function _renderContextChips(){var area=document.getElementById('context-chip-area');while(area.firstChild)area.removeChild(area.firstChild);_pendingContext.forEach(function(c){var chip=document.createElement('div');chip.className='context-chip';var label=document.createElement('span');label.textContent='"'+(c.text.length>40?c.text.slice(0,40)+'…':c.text)+'"';label.title=c.text;var btn=document.createElement('button');btn.textContent='✕';(function(id){btn.addEventListener('click',function(){_removeContextChip(id);});})(c.id);chip.appendChild(label);chip.appendChild(btn);area.appendChild(chip);});}
function _removeContextChip(id){_pendingContext=_pendingContext.filter(function(c){return c.id!==id;});_renderContextChips();}
function _clearContextChips(){_pendingContext=[];_renderContextChips();}
</script>
"""


@app.get("/", response_class=HTMLResponse)
async def serve_report():
    """Serve the FMEA HTML report, injecting chat panel and inlining CSS."""
    import re
    html_path = _find_html_report()
    if not html_path:
        return HTMLResponse("<h2>Kein HTML-Report gefunden in " + str(task_folder) + "</h2>", status_code=404)

    html = html_path.read_text(encoding="utf-8")

    # Inline file:// CSS and images so they work over HTTP
    html = _inline_file_uris(html)

    # Inject chat server port
    port_script = f"<script>const CHAT_SERVER_PORT = {PORT};</script>\n"
    if "const CHAT_SERVER_PORT" in html:
        html = re.sub(r'<script>const CHAT_SERVER_PORT\s*=\s*[^<]+</script>', port_script.strip(), html)
    elif "</head>" in html:
        html = html.replace("</head>", port_script + "</head>", 1)

    # Inject chat panel CSS (if not already present from template)
    if "chat-panel" not in html and "</head>" in html:
        html = html.replace("</head>", _CHAT_PANEL_CSS + "</head>", 1)

    # Inject chat panel HTML + JS (if not already present from template)
    if "id=\"chat-toggle\"" not in html and "</body>" in html:
        html = html.replace("</body>", _CHAT_PANEL_HTML + "\n</body>", 1)

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
