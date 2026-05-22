"""Eval-Tests für die drei FMEA-Skills.

Prüft drei Dimensionen:
1. Referenz-Auflösung: Alle in SKILL.md referenzierten Dateien existieren
2. API-Äquivalenz: Training-Skill API-Aufrufe liefern gleiche Daten wie alte SQL-Queries
3. Description-Triggering: Erwartete Begriffe triggern den richtigen Skill
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJ_ROOT = Path(__file__).parent.parent.resolve()
SKILLS_DIR = PROJ_ROOT / ".claude" / "skills"


# ═══════════════════════════════════════════════════════════════
# 1. Referenz-Auflösung
# ═══════════════════════════════════════════════════════════════

class TestSkillReferences(unittest.TestCase):
    """Jeder in SKILL.md referenzierte Pfad muss im Projekt existieren."""

    def _extract_references(self, skill_name: str) -> list[tuple[str, str]]:
        """Parse alle Datei-Referenzen aus einer SKILL.md.

        Returns: [(raw_ref, resolved_path), ...]
        """
        skill_dir = SKILLS_DIR / skill_name
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        refs = []
        # Backtick-Referenzen: `path/to/file.ext`
        for match in re.finditer(r'`([^`]+\.\w{1,5})`', content):
            ref = match.group(1)
            # Skip Python-Ausdrücke, Methoden, Variablen
            if any(skip in ref for skip in ['(', ')', '=', ' ', '{', '}', '$', 'interview_status']):
                continue
            # Skip inline code wie "S_SCALE" oder "RPZ_neu"
            if ref.isupper() or '_' in ref and '/' not in ref and '.' not in ref.split('/')[-1]:
                continue

            # Resolve: relativ zum Skill-Dir oder zum Projekt-Root
            if ref.startswith('references/'):
                resolved = skill_dir / ref
            elif ref.startswith('.claude/'):
                resolved = PROJ_ROOT / ref
            elif ref.startswith('workflows/') or ref.startswith('config/') or ref.startswith('tools/') or ref.startswith('templates/'):
                resolved = PROJ_ROOT / ref
            elif ref.startswith('tasks/') or ref.startswith('data/'):
                continue  # Laufzeit-/dynamische Pfade (gitignored), nicht prüfbar
            else:
                continue  # Unbekanntes Muster

            refs.append((ref, str(resolved)))

        return refs

    def test_fmea_risikoanalyse_references(self):
        """Alle Referenzen in fmea-risikoanalyse/SKILL.md existieren."""
        refs = self._extract_references("fmea-risikoanalyse")
        self.assertTrue(len(refs) > 0, "Keine Referenzen gefunden")
        for ref, resolved in refs:
            self.assertTrue(
                os.path.exists(resolved),
                f"Referenz '{ref}' nicht gefunden: {resolved}"
            )

    def test_anlagendaten_interview_references(self):
        """Alle Referenzen in anlagendaten-interview/SKILL.md existieren."""
        refs = self._extract_references("anlagendaten-interview")
        self.assertTrue(len(refs) > 0, "Keine Referenzen gefunden")
        for ref, resolved in refs:
            self.assertTrue(
                os.path.exists(resolved),
                f"Referenz '{ref}' nicht gefunden: {resolved}"
            )

    def test_fmea_training_references(self):
        """Alle Referenzen in fmea-training/SKILL.md existieren."""
        refs = self._extract_references("fmea-training")
        for ref, resolved in refs:
            self.assertTrue(
                os.path.exists(resolved),
                f"Referenz '{ref}' nicht gefunden: {resolved}"
            )

    def test_workflow_references_in_fmea_workflow(self):
        """Kanonische fmea-workflow.md referenziert nur existierende Dateien."""
        workflow = PROJ_ROOT / "workflows" / "fmea-workflow.md"
        content = workflow.read_text(encoding="utf-8")
        for match in re.finditer(r'`(config/[^`]+)`', content):
            ref = match.group(1)
            if '(' in ref or '{' in ref:
                continue
            # Skip Python-Attribut-Zugriffe wie config/fmea_standards.FEHLERMODI_VORLAGEN
            if re.search(r'\.\w+$', ref) and not ref.endswith(('.md', '.py', '.json', '.yaml', '.yml')):
                continue
            resolved = PROJ_ROOT / ref
            self.assertTrue(
                os.path.exists(resolved),
                f"Workflow referenziert '{ref}', existiert nicht: {resolved}"
            )


# ═══════════════════════════════════════════════════════════════
# 2. Training-Skill API-Äquivalenz
# ═══════════════════════════════════════════════════════════════

class TestTrainingSkillAPI(unittest.TestCase):
    """Die FMEAStorage-API liefert äquivalente Daten wie die alten SQL-Queries."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        from tools.storage import FMEAStorage
        self.db = FMEAStorage(self.db_path)

        # Testdaten aufbauen
        self.project_id = self.db.create_project("Test-Projekt", "Testanlage")
        self.comp_id = self.db.insert_component(
            self.project_id, "K-001", "Pumpe P-201", "Pumpe",
            "Mechanisch", system_name="Dosiersystem",
        )
        self.func_id = self.db.insert_function(
            self.comp_id, "F-001", "Haupt", "Fördert Medium",
        )
        self.fm_id = self.db.insert_failure_mode(
            self.func_id, "FM-001", "Pumpe fördert nicht",
            fehlerart="Equipment",
            kontext_beschreibung="Die Pumpe P-201 fördert Ethylacetat.",
            controls_einschraenkung="Kein Bypass vorhanden.",
        )
        self.db.insert_failure_cause(
            self.fm_id, "U-001", "Laufrad verschlissen",
            herkunft="Betrieb", praeventionsphase="Betrieb",
        )
        self.db.insert_failure_cause(
            self.fm_id, "U-002", "Kavitation",
            herkunft="Design", praeventionsphase="Konzept",
        )
        self.db.insert_failure_effect(
            self.fm_id,
            mensch_stufe="gering", mensch_beschreibung="Keine Verletzung",
            umwelt_stufe="keine", umwelt_beschreibung="Kein Austritt",
            anlage_stufe="mittel", anlage_beschreibung="Produktionsstillstand",
            kosten_stufe="mittel", kosten_beschreibung="~10k Reparatur",
        )
        self.db.insert_current_control(
            self.fm_id, "Drucküberwachung", "detection", "D",
            beschreibung="PIC-201 misst Förderdruck",
            beeinflusst="D",
        )
        self.ra_id = self.db.insert_risk_assessment(
            self.fm_id, S=5, O=4, D=3,
            begruendung_S="Produktionsausfall, moderate Kosten",
            begruendung_O="Verschleiß alle 2 Jahre",
            begruendung_D="Automatische Drucküberwachung",
            daten_konfidenz="mittel",
            agent_konfidenz="hoch",
            daten_quelle="Betriebserfahrung",
        )

    def tearDown(self):
        self.db.close()
        for suffix in ("", "-shm", "-wal"):
            try:
                os.unlink(self.db_path + suffix)
            except FileNotFoundError:
                pass

    def test_get_failure_causes_returns_all(self):
        """API liefert alle Ursachen wie die alte SQL-Query."""
        causes = self.db.get_failure_causes(self.fm_id)
        self.assertEqual(len(causes), 2)
        descriptions = {c["beschreibung"] for c in causes}
        self.assertIn("Laufrad verschlissen", descriptions)
        self.assertIn("Kavitation", descriptions)

    def test_get_failure_effect_returns_all_dimensions(self):
        """API liefert alle 4 Folgen-Dimensionen."""
        effect = self.db.get_failure_effect(self.fm_id)
        self.assertIsNotNone(effect)
        self.assertEqual(effect["mensch_beschreibung"], "Keine Verletzung")
        self.assertEqual(effect["umwelt_beschreibung"], "Kein Austritt")
        self.assertEqual(effect["anlage_beschreibung"], "Produktionsstillstand")
        self.assertEqual(effect["kosten_beschreibung"], "~10k Reparatur")

    def test_get_current_controls_returns_all(self):
        """API liefert alle Controls mit Typ und Wirkung."""
        controls = self.db.get_current_controls(self.fm_id)
        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0]["name"], "Drucküberwachung")
        self.assertEqual(controls[0]["typ"], "detection")
        self.assertEqual(controls[0]["beeinflusst"], "D")

    def test_get_risk_assessment_returns_sod_with_reasoning(self):
        """API liefert S/O/D mit Begründungen und Konfidenz."""
        ra = self.db.get_risk_assessment(self.fm_id)
        self.assertIsNotNone(ra)
        self.assertEqual(ra["S"], 5)
        self.assertEqual(ra["O"], 4)
        self.assertEqual(ra["D"], 3)
        self.assertEqual(ra["rpz"], 60)
        self.assertEqual(ra["begruendung_S"], "Produktionsausfall, moderate Kosten")
        self.assertEqual(ra["daten_konfidenz"], "mittel")
        self.assertEqual(ra["daten_quelle"], "Betriebserfahrung")

    def test_select_training_candidates_includes_context(self):
        """select_training_candidates liefert FM-Kontext (komp_id, typ etc.)."""
        from tools.calibration import select_training_candidates
        candidates = select_training_candidates(db_path=self.db_path, n=5)
        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c["komp_id"], "K-001")
        self.assertEqual(c["fehlermodus"], "Pumpe fördert nicht")
        self.assertEqual(c["S"], 5)
        self.assertEqual(c["O"], 4)
        self.assertEqual(c["D"], 3)

    def test_context_manager_works(self):
        """FMEAStorage funktioniert als Context-Manager (wie in SKILL.md beschrieben)."""
        from tools.storage import FMEAStorage
        with FMEAStorage(self.db_path) as db:
            causes = db.get_failure_causes(self.fm_id)
            self.assertEqual(len(causes), 2)
        # Nach with-Block: DB ist geschlossen, keine Exception


# ═══════════════════════════════════════════════════════════════
# 3. Description Trigger-Coverage
# ═══════════════════════════════════════════════════════════════

class TestSkillDescriptionTriggers(unittest.TestCase):
    """Prüft ob erwartete Trigger-Begriffe in den Skill-Descriptions enthalten sind."""

    def _load_description(self, skill_name: str) -> str:
        skill_md = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        # YAML-Frontmatter extrahieren
        match = re.search(r'description:\s*>\s*\n(.*?)(?=^---|\n\w+:)', content, re.DOTALL | re.MULTILINE)
        return match.group(1).lower() if match else ""

    def test_fmea_risikoanalyse_core_triggers(self):
        desc = self._load_description("fmea-risikoanalyse")
        for trigger in ["fmea", "risikoanalyse", "rpz", "fehlermodi", "report generieren"]:
            self.assertIn(trigger, desc, f"Trigger '{trigger}' fehlt in fmea-risikoanalyse description")

    def test_fmea_risikoanalyse_casual_triggers(self):
        desc = self._load_description("fmea-risikoanalyse")
        for trigger in ["risiken bewerten", "gefahrenanalyse", "was kann schiefgehen"]:
            self.assertIn(trigger, desc, f"Casual-Trigger '{trigger}' fehlt")

    def test_fmea_risikoanalyse_continuation_triggers(self):
        desc = self._load_description("fmea-risikoanalyse")
        for trigger in ["weiter machen", "nächste komponente", "wo waren wir"]:
            self.assertIn(trigger, desc, f"Fortführungs-Trigger '{trigger}' fehlt")

    def test_anlagendaten_interview_core_triggers(self):
        desc = self._load_description("anlagendaten-interview")
        for trigger in ["anlage erfassen", "anlagendaten", "interview starten", "fmea vorbereiten"]:
            self.assertIn(trigger, desc, f"Trigger '{trigger}' fehlt in anlagendaten-interview description")

    def test_anlagendaten_interview_extended_triggers(self):
        desc = self._load_description("anlagendaten-interview")
        for trigger in ["daten eingeben", "anlage beschreiben", "stoffdaten"]:
            self.assertIn(trigger, desc, f"Erweiterter Trigger '{trigger}' fehlt")

    def test_fmea_training_core_triggers(self):
        desc = self._load_description("fmea-training")
        for trigger in ["fmea trainieren", "bewertungen überprüfen", "agent kalibrieren", "training starten"]:
            self.assertIn(trigger, desc, f"Trigger '{trigger}' fehlt in fmea-training description")

    def test_fmea_training_extended_triggers(self):
        desc = self._load_description("fmea-training")
        for trigger in ["bewertungen checken", "wo lag ich falsch", "qualität verbessern",
                         "feedback geben", "korrekturen einpflegen"]:
            self.assertIn(trigger, desc, f"Erweiterter Trigger '{trigger}' fehlt")

    def test_no_skill_has_empty_description(self):
        for skill_name in ["fmea-risikoanalyse", "anlagendaten-interview", "fmea-training"]:
            desc = self._load_description(skill_name)
            self.assertTrue(len(desc) > 50, f"{skill_name} hat zu kurze Description")


# ═══════════════════════════════════════════════════════════════
# 4. Skill-Struktur-Validierung
# ═══════════════════════════════════════════════════════════════

class TestSkillStructure(unittest.TestCase):
    """Grundlegende Struktur-Checks für alle Skills."""

    SKILLS = ["fmea-risikoanalyse", "anlagendaten-interview", "fmea-training"]

    def test_all_skills_have_skill_md(self):
        for skill in self.SKILLS:
            path = SKILLS_DIR / skill / "SKILL.md"
            self.assertTrue(path.exists(), f"{skill}/SKILL.md fehlt")

    def test_all_skills_have_name_in_frontmatter(self):
        for skill in self.SKILLS:
            content = (SKILLS_DIR / skill / "SKILL.md").read_text()
            self.assertIn(f"name: {skill}", content, f"{skill} hat falschen/fehlenden name")

    def test_all_skills_have_model_directive(self):
        for skill in self.SKILLS:
            content = (SKILLS_DIR / skill / "SKILL.md").read_text()
            self.assertRegex(content, r"model:\s*(opus|sonnet|haiku)", f"{skill} hat keine model-Direktive")

    def test_skill_line_counts_within_limits(self):
        # Pro-Skill-Obergrenzen. fmea-risikoanalyse ist der umfangreichste Skill
        # (vollständige Moderation Startup→Export), daher höheres Limit.
        limits = {
            "fmea-risikoanalyse": 210,
            "anlagendaten-interview": 160,
            "fmea-training": 180,
        }
        for skill, max_lines in limits.items():
            content = (SKILLS_DIR / skill / "SKILL.md").read_text()
            lines = len(content.splitlines())
            self.assertLessEqual(
                lines, max_lines,
                f"{skill} hat {lines} Zeilen, Limit ist {max_lines}"
            )

    def test_no_raw_sql_in_training_skill(self):
        """Training-Skill darf kein raw SQL mehr enthalten."""
        content = (SKILLS_DIR / "fmea-training" / "SKILL.md").read_text()
        self.assertNotIn("db.conn.execute", content, "Raw SQL noch in fmea-training SKILL.md")
        self.assertNotIn("SELECT", content, "SQL SELECT noch in fmea-training SKILL.md")
        self.assertNotIn("FROM failure_modes", content, "SQL FROM noch in fmea-training SKILL.md")

    def test_training_skill_uses_context_manager(self):
        """Training-Skill nutzt with-Statement statt manuelles close()."""
        content = (SKILLS_DIR / "fmea-training" / "SKILL.md").read_text()
        self.assertIn("with FMEAStorage()", content, "Context-Manager fehlt in fmea-training")
        self.assertNotIn("db.close()", content, "Manuelles db.close() noch in fmea-training")


# ═══════════════════════════════════════════════════════════════
# 5. Vollständigkeits-Features (Gefahrenfelder, Keywords, Schema)
# ═══════════════════════════════════════════════════════════════

class TestCompletenessFeatures(unittest.TestCase):
    """Prüft die neuen Vollständigkeits-Features aus dem Upgrade."""

    def test_workflow_has_gefahrenfelder_checkliste(self):
        """Workflow muss Gefahrenfelder-Checkliste in Phase 1 referenzieren."""
        content = (PROJ_ROOT / "workflows" / "fmea-workflow.md").read_text()
        self.assertIn("Gefahrenfelder-Checkliste", content)
        self.assertIn("26 Pflicht-Gefahrenfelder", content)

    def test_workflow_has_gate_vor_report(self):
        """Workflow muss Gesamtprüfung als Gate vor Report enthalten."""
        content = (PROJ_ROOT / "workflows" / "fmea-workflow.md").read_text()
        self.assertIn("Gesamtprüfung (Pflicht vor Report-Generierung)", content)
        self.assertIn("CCF-Prüfung", content)

    def test_keyword_mapping_has_utility_keywords(self):
        """Keyword-Mapping muss Utility-Keywords enthalten."""
        from tools.failure_templates import KEYWORD_MAPPING
        keywords = {m["keyword"] for m in KEYWORD_MAPPING}
        required = {"vakuum", "eiswasser", "abluft", "stickstoff", "n2", "kühlwasser", "manuell"}
        missing = required - keywords
        self.assertEqual(missing, set(), f"Fehlende Keywords: {missing}")

    def test_templates_have_cyber_sabotage(self):
        """Failure Templates müssen cyber_sabotage Kategorie enthalten."""
        from tools.failure_templates import TEMPLATES
        self.assertIn("cyber_sabotage", TEMPLATES)
        self.assertGreaterEqual(len(TEMPLATES["cyber_sabotage"]), 3)

    def test_fmea_standards_have_cyber_sabotage(self):
        """FEHLERMODI_VORLAGEN muss cyber_sabotage enthalten."""
        from config.fmea_standards import FEHLERMODI_VORLAGEN
        self.assertIn("cyber_sabotage", FEHLERMODI_VORLAGEN)

    def test_validate_completeness_importable(self):
        """validate_completeness muss importierbar sein."""
        from tools.validate_completeness import validate_completeness, format_report
        self.assertTrue(callable(validate_completeness))
        self.assertTrue(callable(format_report))

    def test_fmea_standards_md_has_awsv(self):
        """fmea-standards.md muss AwSV-Pflichtprüfung enthalten."""
        content = (SKILLS_DIR / "fmea-risikoanalyse" / "references" / "fmea-standards.md").read_text()
        self.assertIn("AwSV-Pflichtprüfung", content)
        self.assertIn("Rückhaltevolumen", content)

    def test_fmea_standards_md_has_erstickung(self):
        """fmea-standards.md muss Erstickungsgefahr-Pflichtprüfung enthalten."""
        content = (SKILLS_DIR / "fmea-risikoanalyse" / "references" / "fmea-standards.md").read_text()
        self.assertIn("Erstickungsgefahr-Pflichtprüfung", content)
        self.assertIn("O₂-Verdrängung", content)

    def test_fmea_standards_md_has_backflow_examples(self):
        """fmea-standards.md muss Rückströmungs-Szenarien enthalten."""
        content = (SKILLS_DIR / "fmea-risikoanalyse" / "references" / "fmea-standards.md").read_text()
        self.assertIn("Typische Rückströmungs-Szenarien", content)
        self.assertIn("Vakuumpumpe", content)

    def test_schema_has_new_fields(self):
        """Anlagendaten-Schema muss alle neuen Felder enthalten."""
        import json
        schema = json.loads((SKILLS_DIR / "anlagendaten-interview" / "references" / "anlagendaten-schema.json").read_text())
        required = ["processDetails", "processSteps", "psa", "sops", "notfallinfrastruktur",
                     "personalQualifikation", "raumkontext", "awsv", "erstickungsgefahr"]
        for field in required:
            self.assertIn(field, schema, f"Feld '{field}' fehlt im Schema")

    def test_interview_phasen_has_new_phases(self):
        """Interview-Phasen muss neue Sub-Phasen enthalten."""
        content = (SKILLS_DIR / "anlagendaten-interview" / "references" / "interview-phasen.md").read_text()
        required = ["Phase 4b", "Phase 5b", "Phase 5c", "Phase 5f", "Phase 5g", "Phase 7b"]
        for phase in required:
            self.assertIn(phase, content, f"{phase} fehlt in interview-phasen.md")

    def test_skill_md_references_gate(self):
        """FMEA SKILL.md muss Gate vor Report referenzieren."""
        content = (SKILLS_DIR / "fmea-risikoanalyse" / "SKILL.md").read_text()
        self.assertIn("Gesamtprüfung vor Report", content)
        self.assertIn("validate_completeness", content)


if __name__ == "__main__":
    unittest.main()
