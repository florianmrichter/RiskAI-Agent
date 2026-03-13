"""
FMEA Database Migration Tool

Safe ALTER TABLE migrations with IF NOT EXISTS checks.
Runs all pending migrations on an existing fmea.db.

Usage:
    python tools/migrate_db.py
    python tools/migrate_db.py --db path/to/custom.db
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage


def run_migrations(db_path: str = None):
    """Run all pending migrations and report results."""
    print("=== FMEA DB Migration ===")
    if db_path:
        print(f"DB: {db_path}")
    else:
        print(f"DB: data/fmea.db (default)")

    db = FMEAStorage(db_path)

    # Verify new columns are present
    checks = [
        ("risk_assessments", ["daten_konfidenz", "agent_konfidenz", "agent_konfidenz_begruendung", "daten_quelle"]),
        ("measures", ["prioritaet", "aufwand", "kosten_klasse", "assigned_to", "target_date", "implementation_status"]),
        ("projects", ["version", "parent_version_id", "version_beschreibung", "erstellt_von", "geprueft_von", "frozen"]),
        ("failure_modes", ["moc_status", "moc_herkunft_version"]),
    ]

    all_ok = True
    for table, cols in checks:
        cursor = db.conn.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cursor.fetchall()}
        missing = [c for c in cols if c not in existing]
        if missing:
            print(f"  ERROR: {table} — fehlende Spalten: {missing}")
            all_ok = False
        else:
            print(f"  OK: {table} — alle {len(cols)} neuen Spalten vorhanden")

    db.close()

    if all_ok:
        print("\nMigration erfolgreich — alle Felder vorhanden.")
    else:
        print("\nFEHLER: Einige Migrationen sind nicht vollständig.")
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="FMEA DB Migration")
    ap.add_argument("--db", help="Pfad zur SQLite-Datei (optional, default: data/fmea.db)")
    args = ap.parse_args()
    run_migrations(args.db)
