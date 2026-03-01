"""
FMEA Standards Configuration -- Single Source of Truth

All FMEA parameters (RPZ thresholds, S/O/D scales, colors, special rules)
are defined here. Every other module imports from this file.

To change thresholds or scales, edit ONLY this file.
"""

# ═══════════════════════════════════════════════════════════════
# RPZ Classification Thresholds
# ═══════════════════════════════════════════════════════════════

RPZ_THRESHOLDS = {
    "kritisch": 300,
    "hoch": 200,
    "mittel": 100,
}

RPZ_COLORS = {
    "kritisch": "#dc3545",
    "hoch":     "#ff9800",
    "mittel":   "#ffc107",
    "niedrig":  "#28a745",
}

RPZ_LABELS = {
    "kritisch": "Sofortige Maßnahme",
    "hoch":     "Maßnahme zeitnah umsetzen",
    "mittel":   "Maßnahme planen",
    "niedrig":  "Monitoring",
}


def classify_rpz(rpz: int) -> str:
    """Classify an RPZ value into a risk category."""
    if rpz >= RPZ_THRESHOLDS["kritisch"]:
        return "kritisch"
    if rpz >= RPZ_THRESHOLDS["hoch"]:
        return "hoch"
    if rpz >= RPZ_THRESHOLDS["mittel"]:
        return "mittel"
    return "niedrig"


# ═══════════════════════════════════════════════════════════════
# FMEA Special Rules (AIAG-VDA Overrides)
# ═══════════════════════════════════════════════════════════════

SPECIAL_RULES = [
    {
        "id": "severity_override",
        "description": "B >= 9 → mindestens 'hoch' (Sicherheitsrelevanz erzwingt Maßnahme)",
        "condition": lambda S, O, D, rpz_status: S >= 9 and rpz_status not in ("kritisch", "hoch"),
        "override_status": "hoch",
    },
    {
        "id": "detection_severity_override",
        "description": "D >= 9 und B >= 7 → 'kritisch' (schlechte Entdeckbarkeit bei hoher Bedeutung)",
        "condition": lambda S, O, D, rpz_status: D >= 9 and S >= 7 and rpz_status != "kritisch",
        "override_status": "kritisch",
    },
]


def apply_special_rules(S: int, O: int, D: int, rpz_status: str) -> tuple:
    """
    Apply FMEA special rules. Returns (new_status, applied_rule_description) or
    (original_status, None) if no rule applies.
    """
    for rule in SPECIAL_RULES:
        if rule["condition"](S, O, D, rpz_status):
            return rule["override_status"], rule["description"]
    return rpz_status, None


# ═══════════════════════════════════════════════════════════════
# Safety Guard Overrides (context-based S elevation)
# ═══════════════════════════════════════════════════════════════

SAFETY_OVERRIDES = [
    {
        "keywords": ["ex-schutz", "explosionsschutz", "zone 0", "zone 1", "atex"],
        "min_S": 10,
        "label": "Explosionsschutz-Spezifikation",
    },
    {
        "keywords": ["säure", "lauge", "toxisch", "giftig", "chlor", "schwefelsäure", "essigsäure"],
        "min_S": 9,
        "label": "Gefahrstoff-Handling",
    },
    {
        "keywords": ["berstscheibe", "psv", "sicherheitsventil", "not-aus", "not-halt"],
        "min_S": 10,
        "label": "Sicherheitsgerichtetes Bauteil",
    },
]


# ═══════════════════════════════════════════════════════════════
# Severity Scale (S = Bedeutung, 1-10)
# ═══════════════════════════════════════════════════════════════

S_SCALE = {
    1:  ("Keine Auswirkung",  "Keine Auswirkung auf Funktion/Sicherheit"),
    2:  ("Sehr gering",       "Minimale Qualitätsabweichung"),
    3:  ("Gering",            "Leichte Qualitätsminderung, Ausfall < 1h"),
    4:  ("Relativ gering",    "Deutliche Qualitätsminderung, < 1 Tag, < 1k €"),
    5:  ("Mäßig",             "Funktionseinschränkung, 1–7 Tage, 1–10k €"),
    6:  ("Hoch",              "Teilausfall, 1–4 Wochen, 10–50k €"),
    7:  ("Sehr hoch",         "Vollausfall, 1–3 Monate, 50–250k €"),
    8:  ("Extrem hoch",       "Vollausfall, > 3 Mon., 250–500k €, Verletzte"),
    9:  ("Kritisch",          "Katastrophal, > 500k €, Schwerverletzte"),
    10: ("Gefährlich",        "Katastrophal, > 1 Mio €, Todesfälle"),
}


# ═══════════════════════════════════════════════════════════════
# Occurrence Scale (O = Auftreten, 1-10)
# ═══════════════════════════════════════════════════════════════

O_SCALE = {
    1:  ("Unwahrscheinlich",  "< 1 mal in 1.000 Jahren"),
    2:  ("Sehr gering",       "~1 mal in 100 Jahren"),
    3:  ("Gering",            "~1 mal in 10 Jahren"),
    4:  ("Relativ gering",    "~1 mal in 2 Jahren"),
    5:  ("Gelegentlich",      "~2–3 mal/Jahr"),
    6:  ("Mäßig",             "~10 mal/Jahr"),
    7:  ("Häufig",            "~50 mal/Jahr"),
    8:  ("Sehr häufig",       "~125 mal/Jahr"),
    9:  ("Extrem häufig",     "~300 mal/Jahr"),
    10: ("Sehr hoch",         "> 500 mal/Jahr"),
}


# ═══════════════════════════════════════════════════════════════
# Detection Scale (D = Entdeckung, 1-10)
# ═══════════════════════════════════════════════════════════════

D_SCALE = {
    1:  ("Fast sicher",            "Automatische Abschaltung, 100%"),
    2:  ("Sehr wahrscheinlich",    "Autom. Prüfung mit SPC, > 95%"),
    3:  ("Wahrscheinlich",         "Autom. Prüfung ohne SPC, 80–95%"),
    4:  ("Relativ wahrscheinlich", "100% manuelle Prüfung, 70–80%"),
    5:  ("Mäßig wahrscheinlich",   "Stichprobe mit SPC, 50–70%"),
    6:  ("Unwahrscheinlich",       "Stichprobe ohne SPC, 30–50%"),
    7:  ("Sehr unwahrscheinlich",  "Nur visuelle Prüfung, 10–30%"),
    8:  ("Extrem unwahrscheinl.",  "Keine Prüfung, < 10%"),
    9:  ("Absolut unsicher",       "Erst beim Kunden erkannt, < 5%"),
    10: ("Absolut unsicher",       "Nicht erkennbar, ≈ 0%"),
}


# ═══════════════════════════════════════════════════════════════
# Failure Type Categories
# ═══════════════════════════════════════════════════════════════

FAILURE_TYPES = [
    "Prozess",
    "Thermisch",
    "Mechanisch",
    "Equipment",
    "Elektrisch",
    "MSR",
    "Sicherheit",
    "Dosierung",
]


# ═══════════════════════════════════════════════════════════════
# Cause Origin & Prevention Phase Categories
# ═══════════════════════════════════════════════════════════════

CAUSE_ORIGINS = ["Design", "Fertigung", "Betrieb", "Wartung"]

PREVENTION_PHASES = [
    "Konzept",
    "Detaildesign",
    "Fertigung",
    "Inbetriebnahme",
    "Betrieb",
    "Wartung",
]


# ═══════════════════════════════════════════════════════════════
# Bundled Config Object (for convenient import)
# ═══════════════════════════════════════════════════════════════

FMEA_CONFIG = {
    "rpz_thresholds": RPZ_THRESHOLDS,
    "rpz_colors": RPZ_COLORS,
    "rpz_labels": RPZ_LABELS,
    "special_rules": SPECIAL_RULES,
    "safety_overrides": SAFETY_OVERRIDES,
    "scales": {
        "S": S_SCALE,
        "O": O_SCALE,
        "D": D_SCALE,
    },
    "failure_types": FAILURE_TYPES,
    "cause_origins": CAUSE_ORIGINS,
    "prevention_phases": PREVENTION_PHASES,
}
