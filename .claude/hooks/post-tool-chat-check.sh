#!/bin/bash
# PostToolUse hook — checks chat_inbox.json for pending browser messages
# and prints them as context for Claude Code to pick up.

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TASK_FOLDER_FILE="$REPO_ROOT/.active_task_folder"

if [ ! -f "$TASK_FOLDER_FILE" ]; then
  exit 0
fi

TASK_FOLDER="$REPO_ROOT/$(cat "$TASK_FOLDER_FILE" 2>/dev/null)"
INBOX="$TASK_FOLDER/chat_inbox.json"

if [ ! -f "$INBOX" ]; then
  exit 0
fi

python3 -c "
import json, sys

try:
    inbox = json.load(open('$INBOX'))
except Exception:
    sys.exit(0)

pending = [m for m in inbox if m.get('status') == 'pending']
if not pending:
    sys.exit(0)

msg = pending[0]
ctx = f' [Kontext: {msg[\"context\"]}]' if msg.get('context') else ''
print(f'📩 Browser-Chat-Nachricht eingegangen (ID: {msg[\"id\"]}): {msg[\"text\"]}{ctx}')
print('Bitte antworte auf diese Nachricht und schreibe deine Antwort in die chat_outbox.json.')
print(f'Format: {{\"id\": \"<neueUUID>\", \"reply_to\": \"{msg[\"id\"]}\", \"text\": \"<deine Antwort>\", \"ts\": <unix-timestamp>}}')
print('Markiere danach den Eintrag in chat_inbox.json als status: \"answered\".')
" 2>/dev/null

exit 0
