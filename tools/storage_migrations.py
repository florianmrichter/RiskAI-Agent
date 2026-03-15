"""
Schema-Migrations für die FMEA-Datenbank.

Jede Migration ist idempotent — kann mehrfach ausgeführt werden ohne Fehler.
Wird von FMEAStorage._run_migrations_if_needed() aufgerufen.
"""

from __future__ import annotations

import sqlite3


def run_all(conn: sqlite3.Connection) -> None:
    """Run all migrations in order."""
    _migrate_measures_table(conn)
    _migrate_projects_task_folder(conn)
    _migrate_failure_modes_extended(conn)
    _migrate_current_controls_einschraenkung(conn)
    _migrate_measures_hinweis(conn)
    _migrate_risk_assessments_konfidenz(conn)
    _migrate_measures_new_fields(conn)
    _migrate_projects_version(conn)
    _migrate_failure_modes_moc(conn)
    _migrate_failure_modes_empfehlung(conn)
    _migrate_risk_assessments_akzeptanz(conn)
    _migrate_measures_implementation_status(conn)
    _migrate_assessment_feedback_table(conn)
    _migrate_risk_assessments_feedback_fields(conn)


def _add_columns_if_missing(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    """Helper: Add columns to a table if they don't exist yet."""
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    for col, definition in columns.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
    conn.commit()


def _migrate_measures_table(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "measures", {
        "stop_kategorie": "TEXT CHECK(stop_kategorie IN ('S','T','O','P'))",
        "iteration": "INTEGER DEFAULT 1",
    })


def _migrate_projects_task_folder(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "projects", {"task_folder": "TEXT"})


def _migrate_failure_modes_extended(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "failure_modes", {
        "kontext_beschreibung": "TEXT",
        "controls_einschraenkung": "TEXT",
    })


def _migrate_current_controls_einschraenkung(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "current_controls", {"einschraenkung": "TEXT"})


def _migrate_measures_hinweis(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "measures", {"hinweis": "TEXT"})


def _migrate_risk_assessments_konfidenz(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "risk_assessments", {
        "daten_konfidenz": "TEXT DEFAULT 'mittel'",
        "agent_konfidenz": "TEXT DEFAULT 'mittel'",
        "agent_konfidenz_begruendung": "TEXT",
        "daten_quelle": "TEXT",
    })


def _migrate_measures_new_fields(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "measures", {
        "prioritaet": "TEXT DEFAULT 'empfohlen'",
        "aufwand": "TEXT",
        "kosten_klasse": "TEXT",
        "assigned_to": "TEXT",
        "target_date": "TEXT",
        "implementation_status": "TEXT DEFAULT 'geplant'",
    })


def _migrate_projects_version(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "projects", {
        "version": "TEXT DEFAULT '1.0'",
        "parent_version_id": "INTEGER",
        "version_beschreibung": "TEXT",
        "erstellt_von": "TEXT",
        "geprueft_von": "TEXT",
        "frozen": "INTEGER DEFAULT 0",
    })


def _migrate_failure_modes_moc(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "failure_modes", {
        "moc_status": "TEXT DEFAULT 'original'",
        "moc_herkunft_version": "TEXT",
    })


def _migrate_failure_modes_empfehlung(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "failure_modes", {"empfehlung": "TEXT"})


def _migrate_risk_assessments_akzeptanz(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "risk_assessments", {
        "risiko_akzeptiert": "BOOLEAN DEFAULT 0",
        "akzeptiert_von": "TEXT",
        "akzeptiert_datum": "TEXT",
        "akzeptanz_bedingungen": "TEXT",
        "revalidierung_datum": "TEXT",
    })


def _migrate_measures_implementation_status(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "measures", {"implementation_status": "TEXT DEFAULT 'geplant'"})


def _migrate_assessment_feedback_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS assessment_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        failure_mode_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        feedback_type TEXT NOT NULL CHECK(feedback_type IN ('correction', 'confirmation')),
        field TEXT NOT NULL CHECK(field IN ('S', 'O', 'D')),
        agent_value INTEGER NOT NULL,
        final_value INTEGER NOT NULL,
        delta INTEGER NOT NULL,
        reason TEXT,
        context_json TEXT DEFAULT '{}',
        source TEXT DEFAULT 'workflow' CHECK(source IN ('workflow', 'training')),
        created_at TEXT NOT NULL,
        FOREIGN KEY (failure_mode_id) REFERENCES failure_modes(id),
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    """)
    conn.commit()


def _migrate_risk_assessments_feedback_fields(conn: sqlite3.Connection) -> None:
    _add_columns_if_missing(conn, "risk_assessments", {
        "original_S": "INTEGER",
        "original_O": "INTEGER",
        "original_D": "INTEGER",
        "human_corrected": "BOOLEAN DEFAULT 0",
        "correction_count": "INTEGER DEFAULT 0",
    })
