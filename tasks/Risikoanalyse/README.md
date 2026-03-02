# Risikoanalyse (FMEA)

Jeder Unterordner entspricht einer konkreten Anlage/Projekt. Pro Ordner liegt die komplette Analyse: Input, Verarbeitungsdateien, Output.

## Struktur

```
Risikoanalyse/
├── Ethylacetatproduktion_20TA41/   # Ethylacetat-Anlage
├── Destillationskolonne_XY/        # (bei Bedarf anlegen)
└── Schwefelsaureherstellung/      # (bei Bedarf anlegen)
```

## Inhalt pro Projektordner

| Datei | Rolle |
|-------|-------|
| `anlagendaten.json` | Input: Anlagendaten |
| `fmea_explicit.py` | Output: FMEA-Definitionen (Agent schreibt hier) |
| `measures_explicit.py` | Output: Maßnahmen-Generator (Agent/Generator) |
| `workflow_state.json` | Fortschritt: Phasen, Komponenten-Status |
| `checklist.md` | Generiert aus DB |
| `FMEA_Bericht_*.pdf` | Report (optional) |

## Neue Analyse anlegen

```bash
python tools/init_fmea_fresh.py --reset --task-folder Risikoanalyse/NeuesProjekt
```

Dafür zuerst den Ordner `tasks/Risikoanalyse/NeuesProjekt/` anlegen und `anlagendaten.json` ablegen.
