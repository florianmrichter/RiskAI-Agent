# scripts/

Kopien der Python-Tools aus `tools/` und `config/fmea_standards.py`.

**Wichtig:** Diese Skripte müssen vom Projekt-Root ausgeführt werden, da sie sich gegenseitig
importieren (`from tools.storage import FMEAStorage`, `from config.fmea_standards import ...`).
Die Originaldateien in `tools/` und `config/` bleiben die kanonische Quelle.

## Voraussetzungen (einmalig nach Clone)

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # Passwort anpassen falls gewünscht
```
