"""
FMEA Storage Layer -- SQLite CRUD for all 9 entities.

Usage:
    from tools.storage import FMEAStorage
    db = FMEAStorage("path/to/fmea.db")
    project_id = db.create_project("Beispiel-Anlage", "20TA42", task_folder="Risikoanalyse/Beispielprojekt")
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DEFAULT_DB_DIR = Path(__file__).parent.parent / "data"


class FMEAStorage:
    def __init__(self, db_path: str = None):
        if db_path is None:
            DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
            db_path = str(DEFAULT_DB_DIR / "fmea.db")
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()
        self._migrate_measures_table()
        self._migrate_projects_task_folder()
        self._migrate_failure_modes_extended()
        self._migrate_current_controls_einschraenkung()
        self._migrate_measures_hinweis()

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

    def _migrate_measures_table(self):
        """Add stop_kategorie and iteration columns to existing measures tables."""
        cursor = self.conn.execute("PRAGMA table_info(measures)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "stop_kategorie" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE measures ADD COLUMN stop_kategorie TEXT "
                "CHECK(stop_kategorie IN ('S','T','O','P'))"
            )
        if "iteration" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE measures ADD COLUMN iteration INTEGER DEFAULT 1"
            )
        self.conn.commit()

    def _migrate_projects_task_folder(self):
        """Add task_folder column to projects table."""
        cursor = self.conn.execute("PRAGMA table_info(projects)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "task_folder" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE projects ADD COLUMN task_folder TEXT"
            )
        self.conn.commit()

    def _migrate_failure_modes_extended(self):
        """Add kontext_beschreibung and controls_einschraenkung to failure_modes."""
        cursor = self.conn.execute("PRAGMA table_info(failure_modes)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "kontext_beschreibung" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE failure_modes ADD COLUMN kontext_beschreibung TEXT"
            )
        if "controls_einschraenkung" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE failure_modes ADD COLUMN controls_einschraenkung TEXT"
            )
        self.conn.commit()

    def _migrate_current_controls_einschraenkung(self):
        """Add einschraenkung column to current_controls."""
        cursor = self.conn.execute("PRAGMA table_info(current_controls)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "einschraenkung" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE current_controls ADD COLUMN einschraenkung TEXT"
            )
        self.conn.commit()

    def _migrate_measures_hinweis(self):
        """Add hinweis column to measures."""
        cursor = self.conn.execute("PRAGMA table_info(measures)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        if "hinweis" not in existing_cols:
            self.conn.execute(
                "ALTER TABLE measures ADD COLUMN hinweis TEXT"
            )
        self.conn.commit()

    # ── Project CRUD ──

    def create_project(self, name: str, anlage_name: str = None, task_folder: str = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO projects (name, anlage_name, datum, task_folder) VALUES (?, ?, ?, ?)",
            (name, anlage_name, datetime.now().isoformat(), task_folder)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_project(self, project_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None

    def get_project_by_task_folder(self, task_folder: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM projects WHERE task_folder = ? ORDER BY id DESC LIMIT 1",
            (task_folder,)
        ).fetchone()
        return dict(row) if row else None

    def update_project_status(self, project_id: int, status: str):
        self.conn.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
        self.conn.commit()

    # ── Component CRUD ──

    def insert_component(self, project_id: int, komp_id: str, name: str, typ: str,
                         kategorie: str, system_name: str = None, beschreibung: str = None,
                         parameters: dict = None, kontext: dict = None) -> int:
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

    def get_components(self, project_id: int) -> list:
        rows = self.conn.execute(
            "SELECT * FROM components WHERE project_id = ? ORDER BY komp_id", (project_id,)
        ).fetchall()
        return [self._parse_component(r) for r in rows]

    def get_component_by_komp_id(self, komp_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM components WHERE komp_id = ?", (komp_id,)).fetchone()
        return self._parse_component(row) if row else None

    def _parse_component(self, row) -> dict:
        d = dict(row)
        d["parameters"] = json.loads(d.pop("parameters_json"))
        d["kontext"] = json.loads(d.pop("kontext_json"))
        return d

    # ── Function CRUD ──

    def insert_function(self, component_id: int, funktion_id: str, typ: str,
                        beschreibung: str, anforderungen: list = None) -> int:
        cur = self.conn.execute(
            """INSERT INTO functions (component_id, funktion_id, typ, beschreibung, anforderungen_json)
               VALUES (?, ?, ?, ?, ?)""",
            (component_id, funktion_id, typ, beschreibung,
             json.dumps(anforderungen or [], ensure_ascii=False))
        )
        self.conn.commit()
        return cur.lastrowid

    def get_functions(self, component_id: int) -> list:
        rows = self.conn.execute(
            "SELECT * FROM functions WHERE component_id = ? ORDER BY funktion_id", (component_id,)
        ).fetchall()
        return [self._parse_function(r) for r in rows]

    def get_function_by_funktion_id(self, funktion_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM functions WHERE funktion_id = ?", (funktion_id,)).fetchone()
        return self._parse_function(row) if row else None

    def _parse_function(self, row) -> dict:
        d = dict(row)
        d["anforderungen"] = json.loads(d.pop("anforderungen_json"))
        return d

    # ── FailureMode CRUD ──

    def insert_failure_mode(self, function_id: int, fehler_id: str,
                            fehlermodus: str, fehlerart: str,
                            kontext_beschreibung: str = None,
                            controls_einschraenkung: str = None) -> int:
        cur = self.conn.execute(
            """INSERT INTO failure_modes
               (function_id, fehler_id, fehlermodus, fehlerart, kontext_beschreibung, controls_einschraenkung)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (function_id, fehler_id, fehlermodus, fehlerart, kontext_beschreibung, controls_einschraenkung)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_failure_modes(self, function_id: int) -> list:
        rows = self.conn.execute(
            "SELECT * FROM failure_modes WHERE function_id = ? ORDER BY fehler_id", (function_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_failure_mode_by_fehler_id(self, fehler_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM failure_modes WHERE fehler_id = ?", (fehler_id,)).fetchone()
        return dict(row) if row else None

    def update_failure_mode_report_fields(self, fehler_id: str,
                                          kontext_beschreibung: str = None,
                                          controls_einschraenkung: str = None) -> bool:
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

    # ── FailureCause CRUD ──

    def insert_failure_cause(self, failure_mode_id: int, ursache_id: str, beschreibung: str,
                             herkunft: str, praeventionsphase: str,
                             praeventionshinweis: str = None) -> int:
        valid_herkunft = {"Design", "Fertigung", "Betrieb", "Wartung"}
        valid_phase = {"Konzept", "Detaildesign", "Fertigung", "Inbetriebnahme", "Betrieb", "Wartung"}
        if herkunft not in valid_herkunft:
            raise ValueError(f"herkunft must be one of {valid_herkunft}, got '{herkunft}'")
        if praeventionsphase not in valid_phase:
            raise ValueError(f"praeventionsphase must be one of {valid_phase}, got '{praeventionsphase}'")
        cur = self.conn.execute(
            """INSERT INTO failure_causes 
               (failure_mode_id, ursache_id, beschreibung, herkunft, praeventionsphase, praeventionshinweis)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, ursache_id, beschreibung, herkunft, praeventionsphase, praeventionshinweis)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_failure_causes(self, failure_mode_id: int) -> list:
        rows = self.conn.execute(
            "SELECT * FROM failure_causes WHERE failure_mode_id = ? ORDER BY ursache_id",
            (failure_mode_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── FailureEffect CRUD ──

    def insert_failure_effect(self, failure_mode_id: int,
                              mensch_stufe: str = None, mensch_beschreibung: str = None,
                              umwelt_stufe: str = None, umwelt_beschreibung: str = None,
                              anlage_stufe: str = None, anlage_beschreibung: str = None,
                              kosten_stufe: str = None, kosten_beschreibung: str = None) -> int:
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

    def get_failure_effect(self, failure_mode_id: int) -> dict:
        row = self.conn.execute(
            "SELECT * FROM failure_effects WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchone()
        return dict(row) if row else None

    # ── RiskAssessment CRUD ──

    def insert_risk_assessment(self, failure_mode_id: int, S: int, O: int, D: int,
                               begruendung_S: str = None, begruendung_O: str = None,
                               begruendung_D: str = None, rpz: int = None,
                               rpz_status: str = None, override_applied: str = None) -> int:
        if rpz is None:
            rpz = S * O * D
        if rpz_status is None:
            rpz_status = self._classify_rpz(rpz)
        cur = self.conn.execute(
            """INSERT INTO risk_assessments 
               (failure_mode_id, S, O, D, begruendung_S, begruendung_O, begruendung_D,
                rpz, rpz_status, override_applied)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, S, O, D, begruendung_S, begruendung_O, begruendung_D,
             rpz, rpz_status, override_applied)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_risk_assessment(self, failure_mode_id: int, **kwargs):
        allowed = {"S", "O", "D", "begruendung_S", "begruendung_O", "begruendung_D",
                    "rpz", "rpz_status", "override_applied"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [failure_mode_id]
        self.conn.execute(
            f"UPDATE risk_assessments SET {set_clause} WHERE failure_mode_id = ?", values
        )
        self.conn.commit()

    def get_risk_assessment(self, failure_mode_id: int) -> dict:
        row = self.conn.execute(
            "SELECT * FROM risk_assessments WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def _classify_rpz(rpz: int) -> str:
        from config.fmea_standards import classify_rpz
        return classify_rpz(rpz)

    # ── CurrentControl CRUD ──

    def insert_current_control(self, failure_mode_id: int, name: str, typ: str,
                               wirkung: str, sil_level: str = None,
                               beschreibung: str = None, beeinflusst: str = None,
                               einschraenkung: str = None) -> int:
        cur = self.conn.execute(
            """INSERT INTO current_controls 
               (failure_mode_id, name, typ, wirkung, sil_level, beschreibung, beeinflusst, einschraenkung)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, name, typ, wirkung, sil_level, beschreibung, beeinflusst, einschraenkung)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_current_controls(self, failure_mode_id: int) -> list:
        rows = self.conn.execute(
            "SELECT * FROM current_controls WHERE failure_mode_id = ?", (failure_mode_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Measure CRUD ──

    def insert_measure(self, failure_mode_id: int, name: str, abe_kategorie: str,
                       beschreibung: str, stop_kategorie: str = None,
                       ziel: str = None,
                       S_neu: int = None, O_neu: int = None, D_neu: int = None,
                       rpz_neu: int = None, rpz_status_neu: str = None,
                       begruendung: str = None, hinweis: str = None, iteration: int = 1) -> int:
        if rpz_neu is None and all(v is not None for v in [S_neu, O_neu, D_neu]):
            rpz_neu = S_neu * O_neu * D_neu
        if rpz_status_neu is None and rpz_neu is not None:
            rpz_status_neu = self._classify_rpz(rpz_neu)
        cur = self.conn.execute(
            """INSERT INTO measures 
               (failure_mode_id, name, abe_kategorie, stop_kategorie, beschreibung, ziel,
                S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu, begruendung, hinweis, iteration)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (failure_mode_id, name, abe_kategorie, stop_kategorie, beschreibung, ziel,
             S_neu, O_neu, D_neu, rpz_neu, rpz_status_neu, begruendung, hinweis, iteration)
        )
        self.conn.commit()
        return cur.lastrowid

    def insert_measures_batch(self, failure_mode_id: int, measures: list) -> list:
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
            )
            ids.append(mid)
        return ids

    def get_measures(self, failure_mode_id: int) -> list:
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

    # ── Query Helpers ──

    def get_all_failure_modes_with_rpz(self, project_id: int, min_rpz: int = 0) -> list:
        """Returns all failure modes for a project with their risk assessment, filtered by min RPZ."""
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

    def get_failure_modes_needing_measures(self, project_id: int) -> list:
        """
        Returns failure modes that need measures: RPZ >= 100 OR rpz_status in ('hoch', 'kritisch').
        Ensures Sonderregel-Fälle (z.B. S>=9 → hoch trotz RPZ<100) werden berücksichtigt.
        """
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

    def get_full_fmea_data(self, project_id: int) -> list:
        """Returns the complete FMEA dataset for export."""
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
        """Returns summary statistics for a project."""
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

    def close(self):
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
