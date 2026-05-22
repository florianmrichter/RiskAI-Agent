"""
FMEA Storage Layer -- SQLite CRUD for all 9 entities.

Usage:
    from tools.storage import FMEAStorage
    db = FMEAStorage("path/to/fmea.db")
    project_id = db.create_project("Beispiel-Anlage", "20TA42", task_folder="Risikoanalyse/Beispielprojekt")
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

DEFAULT_DB_DIR = Path(__file__).parent.parent / "data"


class FMEAStorage:
    """SQLite-backed storage for FMEA projects with full CRUD for all entities."""

    # Schema version: 15 = all migrations applied
    CURRENT_SCHEMA_VERSION = 15

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
            db_path = str(DEFAULT_DB_DIR / "fmea.db")
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()
        self._run_migrations_if_needed()

    # ═══════════════════════════════════════════════════════════════════
    # ── Internal: Schema & Migrations ──
    # ═══════════════════════════════════════════════════════════════════

    def _create_tables(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            anlage_name TEXT,
            datum TEXT NOT NULL,
            status TEXT DEFAULT 'in_progress',
            task_folder TEXT
        );

        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            komp_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            typ TEXT NOT NULL,
            kategorie TEXT NOT NULL,
            system_name TEXT,
            beschreibung TEXT,
            parameters_json TEXT DEFAULT '{}',
            kontext_json TEXT DEFAULT '{}',
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id INTEGER NOT NULL,
            funktion_id TEXT NOT NULL UNIQUE,
            typ TEXT NOT NULL,
            beschreibung TEXT NOT NULL,
            anforderungen_json TEXT DEFAULT '[]',
            FOREIGN KEY (component_id) REFERENCES components(id)
        );

        CREATE TABLE IF NOT EXISTS failure_modes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function_id INTEGER NOT NULL,
            fehler_id TEXT NOT NULL UNIQUE,
            fehlermodus TEXT NOT NULL,
            fehlerart TEXT NOT NULL,
            FOREIGN KEY (function_id) REFERENCES functions(id)
        );

        CREATE TABLE IF NOT EXISTS failure_causes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            failure_mode_id INTEGER NOT NULL,
            ursache_id TEXT NOT NULL UNIQUE,
            beschreibung TEXT NOT NULL,
            herkunft TEXT NOT NULL,
            praeventionsphase TEXT NOT NULL,
            praeventionshinweis TEXT,
            FOREIGN KEY (failure_mode_id) REFERENCES failure_modes(id)
        );

        CREATE TABLE IF NOT EXISTS failure_effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            failure_mode_id INTEGER NOT NULL UNIQUE,
            mensch_stufe TEXT,
            mensch_beschreibung TEXT,
            umwelt_stufe TEXT,
            umwelt_beschreibung TEXT,
            anlage_stufe TEXT,
            anlage_beschreibung TEXT,
            kosten_stufe TEXT,
            kosten_beschreibung TEXT,
            FOREIGN KEY (failure_mode_id) REFERENCES failure_modes(id)
        );

        CREATE TABLE IF NOT EXISTS risk_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            failure_mode_id INTEGER NOT NULL UNIQUE,
            S INTEGER NOT NULL CHECK(S BETWEEN 1 AND 10),
            O INTEGER NOT NULL CHECK(O BETWEEN 1 AND 10),
            D INTEGER NOT NULL CHECK(D BETWEEN 1 AND 10),
            begruendung_S TEXT,
            begruendung_O TEXT,
            begruendung_D TEXT,
            rpz INTEGER NOT NULL,
            rpz_status TEXT NOT NULL,
            override_applied TEXT,
            FOREIGN KEY (failure_mode_id) REFERENCES failure_modes(id)
        );

        CREATE TABLE IF NOT EXISTS current_controls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            failure_mode_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            typ TEXT NOT NULL,
            wirkung TEXT NOT NULL,
            sil_level TEXT,
            beschreibung TEXT,
            beeinflusst TEXT,
            FOREIGN KEY (failure_mode_id) REFERENCES failure_modes(id)
        );

        CREATE TABLE IF NOT EXISTS measures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            failure_mode_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            abe_kategorie TEXT NOT NULL,
            stop_kategorie TEXT CHECK(stop_kategorie IN ('S','T','O','P')),
            beschreibung TEXT NOT NULL,
            ziel TEXT,
            S_neu INTEGER CHECK(S_neu BETWEEN 1 AND 10),
            O_neu INTEGER CHECK(O_neu BETWEEN 1 AND 10),
            D_neu INTEGER CHECK(D_neu BETWEEN 1 AND 10),
            rpz_neu INTEGER,
            rpz_status_neu TEXT,
            begruendung TEXT,
            iteration INTEGER DEFAULT 1,
            FOREIGN KEY (failure_mode_id) REFERENCES failure_modes(id)
        );
        """)
        self.conn.commit()

    def _run_migrations_if_needed(self):
        """Run migrations only if schema is outdated. Uses schema_version table to skip already-applied migrations."""
        self.conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
        row = self.conn.execute("SELECT version FROM schema_version").fetchone()
        current = row[0] if row else 0

        if current >= self.CURRENT_SCHEMA_VERSION:
            return  # All migrations already applied

        # Run all migrations (each is idempotent -- safe to re-run)
        from tools.storage_migrations import run_all
        run_all(self.conn)

        # Update version
        if row:
            self.conn.execute("UPDATE schema_version SET version = ?", (self.CURRENT_SCHEMA_VERSION,))
        else:
            self.conn.execute("INSERT INTO schema_version (version) VALUES (?)", (self.CURRENT_SCHEMA_VERSION,))
        self.conn.commit()

    @staticmethod
    def _classify_rpz(rpz: int) -> str:
        """Classify an RPZ value into a risk category using project standards."""
        from config.fmea_standards import classify_rpz
        return classify_rpz(rpz)

    @staticmethod
    def _normalize_text(text: str | None) -> str | None:
        """Normalize text before storage: strip, collapse whitespace, fix encoding."""
        if text is None:
            return None
        text = text.replace('\u00a0', ' ').replace('\u200b', '').replace('\u00ad', '')
        text = text.strip()
        text = re.sub(r'[ \t]+', ' ', text)
        return text if text else None

    # ═══════════════════════════════════════════════════════════════════
    # ── Project CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def create_project(self, name: str, anlage_name: str | None = None, task_folder: str | None = None,
                       version: str = "1.0", parent_version_id: int | None = None,
                       version_beschreibung: str | None = None, erstellt_von: str | None = None,
                       geprueft_von: str | None = None) -> int:
        """Create a new FMEA project. Returns the project ID."""
        cur = self.conn.execute(
            """INSERT INTO projects
               (name, anlage_name, datum, task_folder,
                version, parent_version_id, version_beschreibung, erstellt_von, geprueft_von)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, anlage_name, datetime.now().isoformat(), task_folder,
             version, parent_version_id, version_beschreibung, erstellt_von, geprueft_von)
        )
        self.conn.commit()
        return cur.lastrowid

    def freeze_project(self, project_id: int) -> bool:
        """Freeze a project (no further changes allowed)."""
        self.conn.execute("UPDATE projects SET frozen = 1 WHERE id = ?", (project_id,))
        self.conn.commit()
        return self.conn.total_changes > 0

    def get_project(self, project_id: int) -> dict | None:
        """Return a single project by ID, or None if not found."""
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None

    def get_project_by_task_folder(self, task_folder: str) -> dict | None:
        """Return the latest project for a given task_folder, or None."""
        row = self.conn.execute(
            "SELECT * FROM projects WHERE task_folder = ? ORDER BY id DESC LIMIT 1",
            (task_folder,)
        ).fetchone()
        return dict(row) if row else None

    def get_project_versions(self, task_folder: str) -> list[dict]:
        """Return all versions of a project ordered by id."""
        rows = self.conn.execute(
            "SELECT * FROM projects WHERE task_folder = ? ORDER BY id",
            (task_folder,)
        ).fetchall()
        return [dict(r) for r in rows]

    def update_project_status(self, project_id: int, status: str):
        """Update the status field of a project."""
        self.conn.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
        self.conn.commit()

    # ═══════════════════════════════════════════════════════════════════
    # ── Component CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_component(self, project_id: int, komp_id: str, name: str, typ: str,
                         kategorie: str, system_name: str | None = None, beschreibung: str | None = None,
                         parameters: dict | None = None, kontext: dict | None = None) -> int:
        """Insert a component into the project. Returns the component ID."""
        name = self._normalize_text(name) or name
        beschreibung = self._normalize_text(beschreibung)
        cur = self.conn.execute(
            """INSERT INTO components
               (project_id, komp_id, name, typ, kategorie, system_name, beschreibung,
                parameters_json, kontext_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, komp_id, name, typ, kategorie, system_name, beschreibung,
             json.dumps(parameters or {}, ensure_ascii=False),
             json.dumps(kontext or {}, ensure_ascii=False))
        )
        self.conn.commit()
        return cur.lastrowid

    def get_components(self, project_id: int) -> list[dict]:
        """Return all components for a project, ordered by komp_id."""
        rows = self.conn.execute(
            "SELECT * FROM components WHERE project_id = ? ORDER BY komp_id", (project_id,)
        ).fetchall()
        return [self._parse_component(r) for r in rows]

    def get_component_by_komp_id(self, komp_id: str, project_id: int | None = None) -> dict | None:
        """Look up a component by its komp_id. Optionally scope to a project."""
        if project_id is not None:
            row = self.conn.execute(
                "SELECT * FROM components WHERE komp_id = ? AND project_id = ?", (komp_id, project_id)
            ).fetchone()
        else:
            row = self.conn.execute("SELECT * FROM components WHERE komp_id = ?", (komp_id,)).fetchone()
        return self._parse_component(row) if row else None

    def _parse_component(self, row) -> dict:
        d = dict(row)
        d["parameters"] = json.loads(d.pop("parameters_json"))
        d["kontext"] = json.loads(d.pop("kontext_json"))
        return d

    # ═══════════════════════════════════════════════════════════════════
    # ── Function CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_function(self, component_id: int, funktion_id: str, typ: str,
                        beschreibung: str, anforderungen: list | None = None) -> int:
        """Insert a function for a component. Uses INSERT OR IGNORE for idempotency. Returns the function ID."""
        cur = self.conn.execute(
            """INSERT OR IGNORE INTO functions (component_id, funktion_id, typ, beschreibung, anforderungen_json)
               VALUES (?, ?, ?, ?, ?)""",
            (component_id, funktion_id, typ, beschreibung,
             json.dumps(anforderungen or [], ensure_ascii=False))
        )
        self.conn.commit()
        if cur.lastrowid:
            return cur.lastrowid
        row = self.conn.execute("SELECT id FROM functions WHERE funktion_id = ?", (funktion_id,)).fetchone()
        return row[0] if row else None

    def get_functions(self, component_id: int) -> list[dict]:
        """Return all functions for a component, ordered by funktion_id."""
        rows = self.conn.execute(
            "SELECT * FROM functions WHERE component_id = ? ORDER BY funktion_id", (component_id,)
        ).fetchall()
        return [self._parse_function(r) for r in rows]

    def get_function_by_funktion_id(self, funktion_id: str) -> dict | None:
        """Look up a function by its funktion_id."""
        row = self.conn.execute("SELECT * FROM functions WHERE funktion_id = ?", (funktion_id,)).fetchone()
        return self._parse_function(row) if row else None

    def _parse_function(self, row) -> dict:
        d = dict(row)
        d["anforderungen"] = json.loads(d.pop("anforderungen_json"))
        return d

    # ═══════════════════════════════════════════════════════════════════
    # ── FailureMode CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_failure_mode(self, function_id: int, fehler_id: str,
                            fehlermodus: str, fehlerart: str,
                            kontext_beschreibung: str | None = None,
                            controls_einschraenkung: str | None = None) -> int:
        """Insert a failure mode. Uses INSERT OR IGNORE for idempotency. Returns the failure mode ID."""
        fehlermodus = self._normalize_text(fehlermodus) or fehlermodus
        kontext_beschreibung = self._normalize_text(kontext_beschreibung)
        controls_einschraenkung = self._normalize_text(controls_einschraenkung)
        cur = self.conn.execute(
            """INSERT OR IGNORE INTO failure_modes
               (function_id, fehler_id, fehlermodus, fehlerart, kontext_beschreibung, controls_einschraenkung)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (function_id, fehler_id, fehlermodus, fehlerart, kontext_beschreibung, controls_einschraenkung)
        )
        self.conn.commit()
        if cur.lastrowid:
            return cur.lastrowid
        row = self.conn.execute("SELECT id FROM failure_modes WHERE fehler_id = ?", (fehler_id,)).fetchone()
        return row[0] if row else None

    def get_failure_modes(self, function_id: int) -> list[dict]:
        """Return all failure modes for a function, ordered by fehler_id."""
        rows = self.conn.execute(
            "SELECT * FROM failure_modes WHERE function_id = ? ORDER BY fehler_id", (function_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_failure_mode_by_fehler_id(self, fehler_id: str) -> dict | None:
        """Look up a failure mode by its fehler_id."""
        row = self.conn.execute("SELECT * FROM failure_modes WHERE fehler_id = ?", (fehler_id,)).fetchone()
        return dict(row) if row else None

    # ═══════════════════════════════════════════════════════════════════
    # ── FailureCause CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_failure_cause(self, failure_mode_id: int, ursache_id: str, beschreibung: str,
                             herkunft: str, praeventionsphase: str,
                             praeventionshinweis: str | None = None) -> int:
        """Insert a failure cause. Validates herkunft and praeventionsphase. Returns the cause ID."""
        valid_herkunft = {"Design", "Fertigung", "Betrieb", "Wartung"}
        valid_phase = {"Konzept", "Detaildesign", "Fertigung", "Inbetriebnahme", "Betrieb", "Wartung"}
        if herkunft not in valid_herkunft:
            raise ValueError(f"herkunft must be one of {valid_herkunft}, got '{herkunft}'")
        if praeventionsphase not in valid_phase:
            raise ValueError(f"praeventionsphase must be one of {valid_phase}, got '{praeventionsphase}'")
        beschreibung = self._normalize_text(beschreibung) or beschreibung
        praeventionshinweis = self._normalize_text(praeventionshinweis)
        cur = self.conn.execute(
            """INSERT INTO failure_causes
               (failure_mode_id, ursache_id, beschreibung, herkunft, praeventionsphase, praeventionshinweis)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, ursache_id, beschreibung, herkunft, praeventionsphase, praeventionshinweis)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_failure_causes(self, failure_mode_id: int) -> list[dict]:
        """Return all failure causes for a failure mode, ordered by ursache_id."""
        rows = self.conn.execute(
            "SELECT * FROM failure_causes WHERE failure_mode_id = ? ORDER BY ursache_id",
            (failure_mode_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ═══════════════════════════════════════════════════════════════════
    # ── FailureEffect CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_failure_effect(self, failure_mode_id: int,
                              mensch_stufe: str | None = None, mensch_beschreibung: str | None = None,
                              umwelt_stufe: str | None = None, umwelt_beschreibung: str | None = None,
                              anlage_stufe: str | None = None, anlage_beschreibung: str | None = None,
                              kosten_stufe: str | None = None, kosten_beschreibung: str | None = None) -> int:
        """Insert failure effects (human, environment, plant, cost) for a failure mode. Returns the effect ID."""
        mensch_beschreibung = self._normalize_text(mensch_beschreibung)
        umwelt_beschreibung = self._normalize_text(umwelt_beschreibung)
        anlage_beschreibung = self._normalize_text(anlage_beschreibung)
        kosten_beschreibung = self._normalize_text(kosten_beschreibung)
        cur = self.conn.execute(
            """INSERT INTO failure_effects
               (failure_mode_id, mensch_stufe, mensch_beschreibung,
                umwelt_stufe, umwelt_beschreibung, anlage_stufe, anlage_beschreibung,
                kosten_stufe, kosten_beschreibung)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, mensch_stufe, mensch_beschreibung,
             umwelt_stufe, umwelt_beschreibung, anlage_stufe, anlage_beschreibung,
             kosten_stufe, kosten_beschreibung)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_failure_effect(self, failure_mode_id: int) -> dict | None:
        """Return the failure effect for a failure mode, or None."""
        row = self.conn.execute(
            "SELECT * FROM failure_effects WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchone()
        return dict(row) if row else None

    # ═══════════════════════════════════════════════════════════════════
    # ── RiskAssessment CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_risk_assessment(self, failure_mode_id: int, S: int, O: int, D: int,
                               begruendung_S: str | None = None, begruendung_O: str | None = None,
                               begruendung_D: str | None = None, rpz: int | None = None,
                               rpz_status: str | None = None, override_applied: str | None = None,
                               daten_konfidenz: str = "mittel", agent_konfidenz: str = "mittel",
                               agent_konfidenz_begruendung: str | None = None,
                               daten_quelle: str | None = None) -> int:
        """Insert a risk assessment (S, O, D) for a failure mode. Auto-calculates RPZ if not provided."""
        begruendung_S = self._normalize_text(begruendung_S)
        begruendung_O = self._normalize_text(begruendung_O)
        begruendung_D = self._normalize_text(begruendung_D)
        if rpz is None:
            rpz = S * O * D
        if rpz_status is None:
            rpz_status = self._classify_rpz(rpz)
        cur = self.conn.execute(
            """INSERT INTO risk_assessments
               (failure_mode_id, S, O, D, begruendung_S, begruendung_O, begruendung_D,
                rpz, rpz_status, override_applied,
                daten_konfidenz, agent_konfidenz, agent_konfidenz_begruendung, daten_quelle)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, S, O, D, begruendung_S, begruendung_O, begruendung_D,
             rpz, rpz_status, override_applied,
             daten_konfidenz, agent_konfidenz, agent_konfidenz_begruendung, daten_quelle)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_risk_assessment(self, failure_mode_id: int, **kwargs) -> None:
        """Update specific fields of an existing risk assessment. Only allowed fields are written."""
        allowed = {"S", "O", "D", "begruendung_S", "begruendung_O", "begruendung_D",
                    "rpz", "rpz_status", "override_applied",
                    "daten_konfidenz", "agent_konfidenz", "agent_konfidenz_begruendung", "daten_quelle",
                    "original_S", "original_O", "original_D", "human_corrected", "correction_count"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [failure_mode_id]
        self.conn.execute(
            f"UPDATE risk_assessments SET {set_clause} WHERE failure_mode_id = ?", values
        )
        self.conn.commit()

    def get_risk_assessment(self, failure_mode_id: int) -> dict | None:
        """Return the risk assessment for a failure mode, or None."""
        row = self.conn.execute(
            "SELECT * FROM risk_assessments WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchone()
        return dict(row) if row else None

    # ═══════════════════════════════════════════════════════════════════
    # ── CurrentControl CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_current_control(self, failure_mode_id: int, name: str, typ: str,
                               wirkung: str, sil_level: str | None = None,
                               beschreibung: str | None = None, beeinflusst: str | None = None,
                               einschraenkung: str | None = None) -> int:
        """Insert a current control for a failure mode. Returns the control ID."""
        name = self._normalize_text(name) or name
        beschreibung = self._normalize_text(beschreibung)
        cur = self.conn.execute(
            """INSERT INTO current_controls
               (failure_mode_id, name, typ, wirkung, sil_level, beschreibung, beeinflusst, einschraenkung)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, name, typ, wirkung, sil_level, beschreibung, beeinflusst, einschraenkung)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_current_controls(self, failure_mode_id: int) -> list[dict]:
        """Return all current controls for a failure mode."""
        rows = self.conn.execute(
            "SELECT * FROM current_controls WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ═══════════════════════════════════════════════════════════════════
    # ── Measures CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def insert_measure(self, failure_mode_id: int, name: str, abe_kategorie: str,
                       beschreibung: str, stop_kategorie: str | None = None,
                       ziel: str | None = None,
                       S_neu: int | None = None, O_neu: int | None = None, D_neu: int | None = None,
                       rpz_neu: int | None = None, rpz_status_neu: str | None = None,
                       begruendung: str | None = None, hinweis: str | None = None, iteration: int = 1,
                       prioritaet: str = "empfohlen", aufwand: str | None = None,
                       kosten_klasse: str | None = None, assigned_to: str | None = None,
                       target_date: str | None = None,
                       implementation_status: str = "geplant") -> int:
        """Insert a measure for a failure mode. Auto-calculates rpz_neu if S/O/D_neu are all provided."""
        name = self._normalize_text(name) or name
        beschreibung = self._normalize_text(beschreibung) or beschreibung
        begruendung = self._normalize_text(begruendung)
        hinweis = self._normalize_text(hinweis)
        if rpz_neu is None and all(v is not None for v in [S_neu, O_neu, D_neu]):
            rpz_neu = S_neu * O_neu * D_neu
        if rpz_status_neu is None and rpz_neu is not None:
            rpz_status_neu = self._classify_rpz(rpz_neu)
        cur = self.conn.execute(
            """INSERT INTO measures
               (failure_mode_id, name, abe_kategorie, stop_kategorie, beschreibung, ziel,
                S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu, begruendung, hinweis, iteration,
                prioritaet, aufwand, kosten_klasse, assigned_to, target_date, implementation_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, name, abe_kategorie, stop_kategorie, beschreibung, ziel,
             S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu, begruendung, hinweis, iteration,
             prioritaet, aufwand, kosten_klasse, assigned_to, target_date, implementation_status)
        )
        self.conn.commit()
        return cur.lastrowid

    def insert_measures_batch(self, failure_mode_id: int, measures: list[dict]) -> list[int]:
        """Insert multiple measures for a single failure mode. Returns list of IDs."""
        ids = []
        for m in measures:
            mid = self.insert_measure(
                failure_mode_id=failure_mode_id,
                name=m["name"],
                abe_kategorie=m["abe_kategorie"],
                stop_kategorie=m.get("stop_kategorie"),
                beschreibung=m["beschreibung"],
                ziel=m.get("ziel"),
                S_neu=m.get("S_neu"),
                O_neu=m.get("O_neu"),
                D_neu=m.get("D_neu"),
                rpz_neu=m.get("rpz_neu"),
                rpz_status_neu=m.get("rpz_status_neu"),
                begruendung=m.get("begruendung"),
                hinweis=m.get("hinweis"),
                iteration=m.get("iteration", 1),
                prioritaet=m.get("prioritaet", "empfohlen"),
                aufwand=m.get("aufwand"),
                kosten_klasse=m.get("kosten_klasse"),
                assigned_to=m.get("assigned_to"),
                target_date=m.get("target_date"),
                implementation_status=m.get("implementation_status", "geplant"),
            )
            ids.append(mid)
        return ids

    def get_measures(self, failure_mode_id: int) -> list[dict]:
        """Return all measures for a failure mode."""
        rows = self.conn.execute(
            "SELECT * FROM measures WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def update_measure_hinweis(self, failure_mode_id: int, name: str, hinweis: str) -> bool:
        """Update hinweis for a measure by failure_mode_id and name."""
        self.conn.execute(
            "UPDATE measures SET hinweis = ? WHERE failure_mode_id = ? AND name = ?",
            (hinweis, failure_mode_id, name)
        )
        self.conn.commit()
        return self.conn.total_changes > 0

    # ═══════════════════════════════════════════════════════════════════
    # ── Report Fields ──
    # ═══════════════════════════════════════════════════════════════════

    def update_failure_mode_report_fields(self, fehler_id: str,
                                          kontext_beschreibung: str | None = None,
                                          controls_einschraenkung: str | None = None) -> bool:
        """Update kontext_beschreibung and/or controls_einschraenkung for existing failure mode."""
        updates = []
        values = []
        if kontext_beschreibung is not None:
            updates.append("kontext_beschreibung = ?")
            values.append(kontext_beschreibung)
        if controls_einschraenkung is not None:
            updates.append("controls_einschraenkung = ?")
            values.append(controls_einschraenkung)
        if not updates:
            return False
        values.append(fehler_id)
        self.conn.execute(
            f"UPDATE failure_modes SET {', '.join(updates)} WHERE fehler_id = ?",
            values
        )
        self.conn.commit()
        return self.conn.total_changes > 0

    # ═══════════════════════════════════════════════════════════════════
    # ── Assessment Feedback CRUD ──
    # ═══════════════════════════════════════════════════════════════════

    def record_feedback(self, failure_mode_id: int, project_id: int,
                        feedback_type: str, field: str,
                        agent_value: int, final_value: int,
                        reason: str | None = None, context: dict | None = None,
                        source: str = "workflow") -> int:
        """Record expert feedback (correction or confirmation) for an S/O/D value."""
        delta = final_value - agent_value
        cur = self.conn.execute(
            """INSERT INTO assessment_feedback
               (failure_mode_id, project_id, feedback_type, field,
                agent_value, final_value, delta, reason, context_json, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, project_id, feedback_type, field,
             agent_value, final_value, delta, reason,
             json.dumps(context or {}, ensure_ascii=False), source,
             datetime.now().isoformat())
        )
        self.conn.commit()
        return cur.lastrowid

    def record_correction(self, failure_mode_id: int, project_id: int,
                          field: str, original: int, corrected: int,
                          reason: str, context: dict | None = None,
                          source: str = "workflow") -> int:
        """Record a human correction with full context. Updates risk_assessments too."""
        fb_id = self.record_feedback(
            failure_mode_id, project_id, "correction", field,
            original, corrected, reason, context, source
        )
        # Update original values and correction flag on risk_assessments
        ra = self.get_risk_assessment(failure_mode_id)
        if ra:
            updates = {"human_corrected": 1}
            orig_field = f"original_{field}"
            if ra.get(orig_field) is None:
                updates[orig_field] = original
            updates["correction_count"] = (ra.get("correction_count") or 0) + 1
            updates[field] = corrected
            # Recalculate RPZ
            S = updates.get("S", ra["S"])
            O = updates.get("O", ra["O"])
            D = updates.get("D", ra["D"])
            rpz = S * O * D
            updates["rpz"] = rpz
            updates["rpz_status"] = self._classify_rpz(rpz)
            self.update_risk_assessment(failure_mode_id, **updates)
        return fb_id

    def record_confirmation(self, failure_mode_id: int, project_id: int,
                            field: str, value: int,
                            reason: str | None = None, context: dict | None = None,
                            source: str = "workflow") -> int:
        """Record expert confirmation (agent value was correct)."""
        return self.record_feedback(
            failure_mode_id, project_id, "confirmation", field,
            value, value, reason, context, source
        )

    def get_feedback_history(self, project_id: int | None = None,
                             feedback_type: str | None = None) -> list[dict]:
        """Get all feedback, optionally filtered by project and type."""
        query = "SELECT * FROM assessment_feedback WHERE 1=1"
        params = []
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if feedback_type is not None:
            query += " AND feedback_type = ?"
            params.append(feedback_type)
        query += " ORDER BY created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["context"] = json.loads(d.pop("context_json"))
            result.append(d)
        return result

    # ═══════════════════════════════════════════════════════════════════
    # ── Queries & Analytics ──
    # ═══════════════════════════════════════════════════════════════════

    def get_all_failure_modes_with_rpz(self, project_id: int, min_rpz: int = 0) -> list[dict]:
        """Return all failure modes for a project with their risk assessment, filtered by min RPZ."""
        rows = self.conn.execute("""
            SELECT fm.*, ra.S, ra.O, ra.D, ra.rpz, ra.rpz_status,
                   f.funktion_id, f.beschreibung as funktion_beschreibung,
                   c.komp_id, c.name as komponente, c.typ as komponenten_typ, c.system_name
            FROM failure_modes fm
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            JOIN risk_assessments ra ON ra.failure_mode_id = fm.id
            WHERE c.project_id = ? AND ra.rpz >= ?
            ORDER BY ra.rpz DESC
        """, (project_id, min_rpz)).fetchall()
        return [dict(r) for r in rows]

    def get_failure_modes_needing_measures(self, project_id: int) -> list[dict]:
        """Return failure modes that need measures: RPZ >= 100 OR rpz_status in ('hoch', 'kritisch').
        Ensures Sonderregel cases (e.g. S>=9 -> hoch despite RPZ<100) are included."""
        rows = self.conn.execute("""
            SELECT fm.*, ra.S, ra.O, ra.D, ra.rpz, ra.rpz_status,
                   f.funktion_id, f.beschreibung as funktion_beschreibung,
                   c.komp_id, c.name as komponente, c.typ as komponenten_typ, c.system_name
            FROM failure_modes fm
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            JOIN risk_assessments ra ON ra.failure_mode_id = fm.id
            WHERE c.project_id = ?
              AND (ra.rpz >= 100 OR ra.rpz_status IN ('hoch', 'kritisch'))
            ORDER BY ra.rpz DESC, ra.rpz_status DESC
        """, (project_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_full_fmea_data(self, project_id: int) -> list[dict]:
        """Return the complete FMEA dataset for export, with nested causes/effects/controls/measures/risk."""
        failure_modes = self.get_all_failure_modes_with_rpz(project_id)
        result = []
        for fm in failure_modes:
            fm_id = fm["id"]
            entry = {
                **fm,
                "causes": self.get_failure_causes(fm_id),
                "effects": self.get_failure_effect(fm_id),
                "controls": self.get_current_controls(fm_id),
                "measures": self.get_measures(fm_id),
                "risk": self.get_risk_assessment(fm_id),
            }
            result.append(entry)
        return result

    def get_project_statistics(self, project_id: int) -> dict:
        """Return summary statistics for a project (counts + RPZ distribution)."""
        stats = {}
        stats["components"] = self.conn.execute(
            "SELECT COUNT(*) FROM components WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
        stats["functions"] = self.conn.execute(
            """SELECT COUNT(*) FROM functions f
               JOIN components c ON f.component_id = c.id
               WHERE c.project_id = ?""", (project_id,)
        ).fetchone()[0]
        stats["failure_modes"] = self.conn.execute(
            """SELECT COUNT(*) FROM failure_modes fm
               JOIN functions f ON fm.function_id = f.id
               JOIN components c ON f.component_id = c.id
               WHERE c.project_id = ?""", (project_id,)
        ).fetchone()[0]

        rpz_rows = self.conn.execute("""
            SELECT ra.rpz_status, COUNT(*) as cnt FROM risk_assessments ra
            JOIN failure_modes fm ON ra.failure_mode_id = fm.id
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            WHERE c.project_id = ?
            GROUP BY ra.rpz_status
        """, (project_id,)).fetchall()
        stats["rpz_distribution"] = {row["rpz_status"]: row["cnt"] for row in rpz_rows}

        measures_count = self.conn.execute("""
            SELECT COUNT(*) FROM measures m
            JOIN failure_modes fm ON m.failure_mode_id = fm.id
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            WHERE c.project_id = ?
        """, (project_id,)).fetchone()[0]
        stats["measures"] = measures_count

        return stats

    def get_feedback_patterns(self) -> dict:
        """Return aggregated correction patterns across all projects for calibration."""
        corrections = self.conn.execute("""
            SELECT af.field, af.delta, af.context_json,
                   c.typ as komponenten_typ, fm.fehlerart
            FROM assessment_feedback af
            JOIN failure_modes fm ON af.failure_mode_id = fm.id
            JOIN functions f ON fm.function_id = f.id
            JOIN components c ON f.component_id = c.id
            WHERE af.feedback_type = 'correction'
        """).fetchall()

        if not corrections:
            return {"total_corrections": 0, "field_bias": {}, "patterns": []}

        # Field bias
        field_deltas = {}
        for row in corrections:
            field = row["field"]
            if field not in field_deltas:
                field_deltas[field] = []
            field_deltas[field].append(row["delta"])

        field_bias = {}
        for field, deltas in field_deltas.items():
            avg = sum(deltas) / len(deltas)
            field_bias[field] = {
                "avg_delta": round(avg, 1),
                "count": len(deltas),
                "direction": "zu_niedrig" if avg > 0 else "zu_hoch" if avg < 0 else "neutral",
            }

        # Patterns by komponenten_typ + fehlerart + field
        pattern_groups = {}
        for row in corrections:
            ctx = json.loads(row["context_json"]) if row["context_json"] else {}
            key = (row["komponenten_typ"] or ctx.get("komponenten_typ", "unbekannt"),
                   row["fehlerart"] or ctx.get("fehlerart", "unbekannt"),
                   row["field"])
            if key not in pattern_groups:
                pattern_groups[key] = []
            pattern_groups[key].append(row["delta"])

        patterns = []
        for (komp_typ, fehlerart, field), deltas in pattern_groups.items():
            if len(deltas) >= 2:  # Minimum 2 occurrences for a pattern
                avg_delta = sum(deltas) / len(deltas)
                patterns.append({
                    "komponenten_typ": komp_typ,
                    "fehlerart": fehlerart,
                    "field": field,
                    "avg_delta": round(avg_delta, 1),
                    "occurrences": len(deltas),
                    "confidence": "hoch" if len(deltas) >= 5 else "mittel" if len(deltas) >= 3 else "niedrig",
                })

        patterns.sort(key=lambda p: p["occurrences"], reverse=True)

        return {
            "total_corrections": len(corrections),
            "field_bias": field_bias,
            "patterns": patterns,
        }

    def get_correction_rate(self, project_id: int) -> dict:
        """Return correction rate for a specific project."""
        total = self.conn.execute(
            "SELECT COUNT(*) FROM assessment_feedback WHERE project_id = ?",
            (project_id,)
        ).fetchone()[0]
        corrections = self.conn.execute(
            "SELECT COUNT(*) FROM assessment_feedback WHERE project_id = ? AND feedback_type = 'correction'",
            (project_id,)
        ).fetchone()[0]
        confirmations = total - corrections
        return {
            "total": total,
            "corrections": corrections,
            "confirmations": confirmations,
            "correction_rate": round(corrections / total, 2) if total > 0 else 0.0,
        }

    # ═══════════════════════════════════════════════════════════════════
    # ── Utilities ──
    # ═══════════════════════════════════════════════════════════════════

    def backup(self) -> str:
        """Create a timestamped backup of the database. Returns the backup path."""
        import shutil
        backup_dir = Path(self.db_path).parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"fmea_{timestamp}.db"
        # Flush WAL to main DB before copying
        self.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        shutil.copy2(self.db_path, backup_path)
        # Keep only last 10 backups
        backups = sorted(backup_dir.glob("fmea_*.db"))
        for old in backups[:-10]:
            old.unlink()
        return str(backup_path)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == "__main__":
    db = FMEAStorage()
    pid = db.create_project("Test-Projekt", "Testanlage")
    print(f"Project created: {db.get_project(pid)}")
    print(f"DB path: {db.db_path}")
    db.close()
