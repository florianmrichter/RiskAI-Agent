# Archiv: Proof-of-Concept-Skripte (2026-03-02)

Diese Skripte wurden archiviert, da sie nicht mehr benötigt werden.

- **setup_poc.py** – Legte Projekt „Ethylacetat-Anlage 20TA41“ an und lud Anlagendaten
- **poc_run.py** – Füllte FMEA-Daten (Funktionen, Fehlermodi, Maßnahmen) hardcodiert für KOMP-001, KOMP-013, KOMP-017

**Grund:** Der aktuelle Ablauf nutzt `init_fmea_fresh.py` → Agent → `fmea_explicit.py` → `insert_fmea_explicit.py`. Die PoC-Skripte waren historische Demos für die erste Ethylacetat-Analyse und werden von keinem Workflow oder Tool referenziert.
