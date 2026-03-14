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
    "kritisch": "#F5004F",  # Vivid Pink / Brand Red
    "hoch":     "#FD7E14",  # Orange
    "mittel":   "#E8C547",  # Mustard Yellow
    "niedrig":  "#00A389",  # Teal Green
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
# Gefahrenfelder (erweiterte Prüfpunkte für FM-Kategorien)
# ═══════════════════════════════════════════════════════════════
# Zuordnung der 35 Gefahrenfelder zu FM-Kategorien.
# Kategorie 1+2: Standard-Prüfpunkte (immer prüfen)
# Kategorie 3: Optional (nur bei Außenanlagen oder auf Anfrage)

GEFAHRENFELDER = {
    # Kategorie 1 — Prozessbedingungen
    "1.1":  {"name": "Spezifikation / Verunreinigungen", "fm_kategorien": ["Prozess"], "pflicht": True},
    "1.2":  {"name": "Präsenz der Ausgangsstoffe", "fm_kategorien": ["Prozess", "Dosierung"], "pflicht": True},
    "1.3":  {"name": "Dosierung / Menge / Reihenfolge", "fm_kategorien": ["Dosierung"], "pflicht": True},
    "1.4":  {"name": "Reaktionsbedingungen (pH etc.)", "fm_kategorien": ["Prozess"], "pflicht": True},
    "1.5":  {"name": "Druck", "fm_kategorien": ["Prozess"], "pflicht": True},
    "1.6":  {"name": "Temperatur", "fm_kategorien": ["Thermisch"], "pflicht": True},
    "1.7":  {"name": "Vermischung / Verwechslung", "fm_kategorien": ["Prozess", "Sonstiges"], "pflicht": True},
    "1.8":  {"name": "Explosionsfähige Atmosphäre", "fm_kategorien": ["Sicherheit"], "pflicht": True},
    "1.9":  {"name": "Stoffströme / Rückströmung", "fm_kategorien": ["Prozess"], "pflicht": True},
    "1.10": {"name": "Füllstand / Überfüllung", "fm_kategorien": ["Prozess"], "pflicht": True},
    "1.11": {"name": "Rührung / Rührgeschwindigkeit", "fm_kategorien": ["Mechanisch", "Equipment"], "pflicht": True},
    "1.12": {"name": "Elektrostatische Aufladung", "fm_kategorien": ["Sicherheit", "Elektrisch"], "pflicht": True},
    "1.13": {"name": "Reaktion mit Wärmeträger", "fm_kategorien": ["Thermisch"], "pflicht": True},
    "1.14": {"name": "Katalysator / Inhibitor", "fm_kategorien": ["Prozess", "Dosierung"], "pflicht": True},
    "1.15": {"name": "Filtrieren / Abtrennen / Dekantieren", "fm_kategorien": ["Equipment"], "pflicht": True},
    "1.16": {"name": "Pumpen / Leeren / Transfer", "fm_kategorien": ["Mechanisch", "Prozess"], "pflicht": True},
    "1.17": {"name": "Heizen / Kühlen", "fm_kategorien": ["Thermisch"], "pflicht": True},
    "1.18": {"name": "Reinigung", "fm_kategorien": ["Prozess", "Sicherheit", "Equipment"], "pflicht": True},
    "1.19": {"name": "Kontrolle / Überwachung / Detektion", "fm_kategorien": ["MSR"], "pflicht": True},
    "1.20": {"name": "Evakuieren / Entlasten", "fm_kategorien": ["Prozess", "Sicherheit"], "pflicht": True},
    "1.21": {"name": "Abluft / Ableitung", "fm_kategorien": ["Sicherheit", "Prozess"], "pflicht": True},
    "1.22": {"name": "Prozessunterbruch", "fm_kategorien": ["Prozess", "Elektrisch"], "pflicht": True},
    "1.23": {"name": "Stoff-/Chemikalienaustritt", "fm_kategorien": ["Mechanisch", "Sicherheit"], "pflicht": True},
    "1.24": {"name": "Manuelle Tätigkeiten", "fm_kategorien": ["Sonstiges", "Sicherheit"], "pflicht": True},
    "1.25": {"name": "Wartungs-/Reparaturarbeiten", "fm_kategorien": ["Sonstiges"], "pflicht": True},
    "1.26": {"name": "Offenes Stoffhandling (K1-Gefahrstoffe)", "fm_kategorien": ["Sicherheit", "Sonstiges"], "pflicht": True},
    # Kategorie 2 — Energie / Medien
    "2.1":  {"name": "Hilfsenergien (Strom, Druckluft, N₂, Vakuum)", "fm_kategorien": ["Elektrisch", "Prozess"], "pflicht": True},
    "2.2":  {"name": "Heiz-/Kühlmedien (Dampf, Kühlwasser, Sole)", "fm_kategorien": ["Thermisch"], "pflicht": True},
    "2.3":  {"name": "PLT-Einrichtungen", "fm_kategorien": ["MSR"], "pflicht": True},
    "2.4":  {"name": "Integrität der Bauteile", "fm_kategorien": ["Mechanisch", "Equipment"], "pflicht": True},
    "2.5":  {"name": "CE-Konformität (Produktsicherheitsgesetz)", "fm_kategorien": ["Sicherheit"], "pflicht": True},
    "2.6":  {"name": "Cyber Security", "fm_kategorien": ["MSR", "Elektrisch"], "pflicht": True},
    # Kategorie 3 — Sonstige Einflüsse (optional, nur bei Außenanlagen)
    "3.1":  {"name": "Hagel", "fm_kategorien": ["Mechanisch"], "pflicht": False},
    "3.2":  {"name": "Blitzschlag", "fm_kategorien": ["Elektrisch", "Sicherheit"], "pflicht": False},
    "3.3":  {"name": "Erdabsenkung", "fm_kategorien": ["Mechanisch"], "pflicht": False},
    "3.4":  {"name": "Starkregenereignis", "fm_kategorien": ["Prozess"], "pflicht": False},
    "3.5":  {"name": "Umgebungstemperaturen", "fm_kategorien": ["Thermisch"], "pflicht": False},
    "3.6":  {"name": "Sabotage", "fm_kategorien": ["Sicherheit", "Sonstiges"], "pflicht": False},
    "3.7":  {"name": "Sturm / Tornado", "fm_kategorien": ["Mechanisch"], "pflicht": False},
    "3.8":  {"name": "Erdbeben", "fm_kategorien": ["Mechanisch"], "pflicht": False},
    "3.9":  {"name": "Brand", "fm_kategorien": ["Sicherheit"], "pflicht": False},
}

# ═══════════════════════════════════════════════════════════════
# Fehlermodi-Vorlagen (Basis für Agent-Bewertung)
# ═══════════════════════════════════════════════════════════════
# Der Agent nutzt diesen Katalog als Checkliste: Für jede Komponente prüfen,
# welche Fehlertypen aus welcher Kategorie relevant sind. Keine generische
# Übernahme – jede Bewertung (S/O/D, Ursachen, Folgen) erfolgt einzeln.
# Siehe workflows/fehleranalyse.md.

FEHLERMODI_VORLAGEN = {
    "prozess": [
        {"typ": "Mehr Stoffstrom (High Flow)", "beschreibung": "Überschreitung der Auslegungskapazität, verringerte Verweilzeit oder Überfüllung nachgeschalteter Apparate."},
        {"typ": "Weniger Stoffstrom (Low Flow)", "beschreibung": "Unterschreitung der Mindestströmung, Gefahr von Ablagerungen oder unzureichender Durchmischung."},
        {"typ": "Kein Stoffstrom (No Flow)", "beschreibung": "Vollständiger Abriss der Versorgung, Trockenlauf von Pumpen oder Entstehen von gefährlichen Totvolumina."},
        {"typ": "Rückstrom (Reverse Flow)", "beschreibung": "Umkehrung der Fließrichtung durch Druckunterschiede, führt zu Kontamination von Vorlagen oder Reaktionen in Zuleitungen."},
        {"typ": "Mehr Druck (High Pressure)", "beschreibung": "Überschreitung des zulässigen Betriebsdrucks (PS), Gefahr des Berstens oder Ansprechen von Sicherheitseinrichtungen."},
        {"typ": "Weniger Druck (Low Pressure/Vacuum)", "beschreibung": "Unterschreitung des Mindestdrucks, Gefahr der Kavitation oder Implosion bei nicht vakuumfesten Apparaten."},
        {"typ": "Konzentrationsabweichung", "beschreibung": "Falsches stöchiometrisches Verhältnis, führt zu Nebenreaktionen, Ausbeuteverlust oder thermischer Instabilität."},
        {"typ": "Phasentrennung / Entmischung", "beschreibung": "Ungewollte Bildung von Schichten (z.B. Emulsionsbruch), führt zu Fehlmessungen oder lokalen Reaktions-Hotspots."},
        {"typ": "Verschleppung / Kontamination", "beschreibung": "Eintrag von Fremdstoffen oder Rückständen aus Vorchargen, die als Katalysator oder Inhibitor wirken."},
    ],
    "thermisch": [
        {"typ": "Mehr Temperatur (High Temperature)", "beschreibung": "Beschleunigung exothermer Reaktionen (Runaway-Gefahr), thermische Zersetzung des Mediums oder Materialerweichung."},
        {"typ": "Weniger Temperatur (Low Temperature)", "beschreibung": "Einfrieren von Medien, Auskristallisation (Blockade), Viskositätsanstieg (Pumpenüberlastung) oder Sprödbruch von Werkstoffen."},
        {"typ": "Thermischer Schock", "beschreibung": "Extreme Temperaturgradienten führen zu Spannungsrissen in Emaille-Auskleidungen oder Schweißnähten."},
        {"typ": "Verlust der Wärmeabfuhr", "beschreibung": "Ausfall des Kühlmediums oder Verschmutzung der Tauscherflächen (Fouling), führt zu unkontrolliertem Temperaturanstieg."},
        {"typ": "Lokale Überhitzung (Hot Spot)", "beschreibung": "Ungleichmäßige Wärmeverteilung, z.B. durch defekte Rührwerke oder Wandbeläge, führt zu lokalem Materialversagen."},
    ],
    "mechanisch": [
        {"typ": "Erosion / Abrasion", "beschreibung": "Materialabtrag durch feststoffhaltige Medien oder hohe Strömungsgeschwindigkeiten, führt zu Wandstärkenunterschreitung."},
        {"typ": "Kavitation", "beschreibung": "Dampfblasenbildung und schlagartige Kondensation, führt zu Materialzerstörung an Laufrädern und Ventilsitzen."},
        {"typ": "Vibration / Resonanz", "beschreibung": "Mechanische Schwingungen durch Pumpen oder Rührwerke, führen zu Ermüdungsbrüchen an Kleinstutzen und Verschraubungen."},
        {"typ": "Äußere Leckage (Integritätsverlust)", "beschreibung": "Versagen von Flanschdichtungen oder Stopfbuchsen, führt zu Medienaustritt in die Umwelt."},
        {"typ": "Innere Leckage (Bypass)", "beschreibung": "Durchbruch an Wärmetauscherrohren oder defekte Ventilsitze, führt zu prozessinterner Vermischung."},
        {"typ": "Materialermüdung", "beschreibung": "Rissbildung durch zyklische Druck- oder Temperaturbelastungen (Lastwechsel)."},
    ],
    "equipment": [
        {"typ": "Fouling / Belagbildung", "beschreibung": "Aufbau von Feststoffschichten auf Funktionsflächen, reduziert Wärmeübergang oder verengt Querschnitte."},
        {"typ": "Verstopfung / Blockade", "beschreibung": "Verschluss von Filtern, Sieben oder Rohrleitungen durch Fremdkörper oder Produktansammlungen."},
        {"typ": "Gleitringdichtungsversagen", "beschreibung": "Ausfall der Wellenabdichtung an rotierendem Equipment, oft verbunden mit dem Verlust des Sperrmediums."},
        {"typ": "Innere Beschädigung (Einbauten)", "beschreibung": "Bruch von Stromstörern, Füllkörpern oder Filterkerzen, beeinträchtigt Stoff- und Wärmeaustausch."},
        {"typ": "Vakuumverlust", "beschreibung": "Eindringen von Falschluft in evakuierte Systeme, beeinträchtigt Siedepunkte oder führt zu explosiven Gemischen."},
    ],
    "elektrisch": [
        {"typ": "Vollständiger Spannungsausfall (Blackout)", "beschreibung": "Absturz aller aktiven Komponenten, Übergang der Anlage in den undefinierten Zustand."},
        {"typ": "Spannungseinbruch (Brownout)", "beschreibung": "Kurzzeitige Unterspannung, führt zu unkontrollierten Resets von Steuerungen oder Abfallen von Schützen."},
        {"typ": "Phasenausfall / Asymmetrie", "beschreibung": "Unregelmäßige Versorgung von Drehstrommotoren, führt zu Überhitzung und Wicklungsschäden."},
        {"typ": "EMV-Einkopplung", "beschreibung": "Elektromagnetische Störsignale auf Signalleitungen, führen zu sporadischen Fehlmessungen oder CPU-Stopps."},
        {"typ": "Erdschluss / Isolationsfehler", "beschreibung": "Fehlerstrom gegen Gehäuse, führt zur Auslösung von Schutzeinrichtungen oder Personengefahr."},
    ],
    "msr": [
        {"typ": "Eingefrorener Messwert (Frozen Value)", "beschreibung": "Sensor liefert konstanten Wert trotz Prozessänderung (z.B. durch verstopfte Impulsleitung), Regelung reagiert nicht."},
        {"typ": "Messwertdrift", "beschreibung": "Schleichende Veränderung der Kalibrierung, führt zu unbemerktem Verlassen des optimalen Betriebspunkts."},
        {"typ": "Signalrauschen / Spikes", "beschreibung": "Instabile Signale führen zu hoher mechanischer Belastung der Aktoren (ständiges Nachregeln)."},
        {"typ": "Aktor-Blockade (Stuck-at)", "beschreibung": "Stellventil oder Klappe klemmt mechanisch, Reglerausgang bleibt ohne Wirkung."},
        {"typ": "Logikfehler / Software-Bug", "beschreibung": "Fehlerhafte Implementierung von Verriegelungen oder Schrittketten führt zu falscher Fahrweise."},
        {"typ": "Kommunikationsabriss (Busfehler)", "beschreibung": "Verlust der Verbindung zwischen E/A-Ebene und CPU, Aktoren gehen meist in Fail-Safe-Zustand."},
        {"typ": "Antivalenzfehler", "beschreibung": "Widersprüchliche Rückmeldungen von Endlagenschaltern (z.B. 'Offen' und 'Geschlossen' gleichzeitig)."},
    ],
    "sicherheit": [
        {"typ": "Nicht-Öffnen (Safety Valve)", "beschreibung": "Sicherheitsventil klemmt oder ist verklebt, unzulässiger Druckaufbau wird nicht begrenzt."},
        {"typ": "Frühzeitiges Ansprechen", "beschreibung": "Sicherheitsventil oder Berstscheibe löst unterhalb des Ansprechdrucks aus, führt zu Prozessunterbrechung und Medienaustritt."},
        {"typ": "Ausfall der Inertisierung", "beschreibung": "Verlust des Stickstoffpolsters, Entstehen einer explosionsfähigen Atmosphäre im Behälter."},
        {"typ": "Flammendurchschlag", "beschreibung": "Defekt an Deflagrationssicherungen, ermöglicht Brandübertragung in andere Anlagenteile."},
        {"typ": "Fehlauslösung Not-Halt", "beschreibung": "Unberechtigtes Auslösen der Schutzkette, führt zu instabilen Zuständen durch plötzlichen Stillstand."},
    ],
    "dosierung": [
        {"typ": "Überdosierung (Single Point Failure)", "beschreibung": "Zuviel Komponente A führt zu unkontrollierter Exothermie oder Produktverlust."},
        {"typ": "Unterdosierung", "beschreibung": "Zuwenig Katalysator oder Reaktant verhindert den Reaktionsstart (Akkumulationsgefahr)."},
        {"typ": "Falsche Dosierreihenfolge", "beschreibung": "Abweichung vom Rezept, kann zu gefährlichen Zwischenprodukten oder Feststoffausfall führen."},
        {"typ": "Gasblasen im Dosierstrom", "beschreibung": "Inhomogenität im Medium führt zu massiven Volumenstromfehlern bei Verdrängerpumpen."},
    ],
    "sonstiges": [
        {"typ": "Bedienfehler (Human Error)", "beschreibung": "Falsche Sollwertvorgabe oder Fehlinterpretation von Alarmen durch das Personal."},
        {"typ": "Kennzeichnungsfehler", "beschreibung": "Falsche Beschriftung von Leitungen oder Handventilen führt zu Verwechslungen bei Wartung/Betrieb."},
        {"typ": "Externe Einwirkung", "beschreibung": "Beschädigung von Rohrleitungen durch Staplerverkehr oder herabfallende Lasten."},
    ],
}


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
    "fehlermodi_vorlagen": FEHLERMODI_VORLAGEN,
    "cause_origins": CAUSE_ORIGINS,
    "prevention_phases": PREVENTION_PHASES,
    "gefahrenfelder": GEFAHRENFELDER,
}
