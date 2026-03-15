"""
Failure Templates -- Catalog of typical failure modes per component type.

Extracted from the n8n workflow's "Fehlermatrix u. -zuordnung" node.
Used to prime the Agent with relevant failure patterns during analysis.

Usage:
    from tools.failure_templates import get_templates, get_templates_for_component
    templates = get_templates("prozess")
    templates = get_templates_for_component("KOMP-001", "prozess", "Synthese Reaktor")
"""

TEMPLATES = {
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
    "cyber_sabotage": [
        {"typ": "Unbefugter Fernzugriff", "beschreibung": "Zugriff auf Prozesssteuerung über Netzwerk/VPN, Manipulation von Sollwerten oder Verriegelungen."},
        {"typ": "Malware / Ransomware auf OT-System", "beschreibung": "Schadsoftware befällt SPS/SCADA, führt zu Ausfall oder unkontrolliertem Betrieb."},
        {"typ": "Manipulation vor Ort (Sabotage)", "beschreibung": "Absichtliche Fehlbedienung oder Manipulation durch Personen mit physischem Zugang."},
        {"typ": "Datenmanipulation / Logikänderung", "beschreibung": "Unerkannte Änderung von SPS-Programm oder Alarmschwellen."},
    ],
}

KEYWORD_MAPPING = [
    # Prozess
    {"keyword": "synthese", "category": "prozess"},
    {"keyword": "reaktion", "category": "prozess"},
    {"keyword": "lösemittel", "category": "prozess"},
    {"keyword": "reinig", "category": "prozess"},
    # Thermisch
    {"keyword": "heizung", "category": "thermisch"},
    {"keyword": "kühlung", "category": "thermisch"},
    {"keyword": "temperatur", "category": "thermisch"},
    # Mechanisch
    {"keyword": "druck", "category": "mechanisch"},
    {"keyword": "dichtheit", "category": "mechanisch"},
    {"keyword": "pumpe", "category": "mechanisch"},
    # Sicherheit
    {"keyword": "emergency", "category": "sicherheit"},
    {"keyword": "schutz", "category": "sicherheit"},
    {"keyword": "ventil", "category": "sicherheit"},
    {"keyword": "abluft", "category": "sicherheit"},
    {"keyword": "stickstoff", "category": "sicherheit"},
    {"keyword": "n2", "category": "sicherheit"},
    {"keyword": "handloch", "category": "sicherheit"},
    # Dosierung
    {"keyword": "dosier", "category": "dosierung"},
    {"keyword": "befüll", "category": "dosierung"},
    # MSR
    {"keyword": "sensor", "category": "msr"},
    {"keyword": "mess", "category": "msr"},
    {"keyword": "regel", "category": "msr"},
    {"keyword": "sps", "category": "msr"},
    {"keyword": "scada", "category": "msr"},
    {"keyword": "fernzugriff", "category": "msr"},
    # Utility/Interface (→ Prozess, da Rückströmung dort definiert)
    {"keyword": "vakuum", "category": "prozess"},
    {"keyword": "rückfluss", "category": "prozess"},
    {"keyword": "kühlwasser", "category": "prozess"},
    {"keyword": "eiswasser", "category": "prozess"},
    {"keyword": "schnittstelle", "category": "prozess"},
    # Sonstiges
    {"keyword": "manuell", "category": "sonstiges"},
]


def get_templates(component_type: str) -> list:
    """Get failure templates for a specific component type."""
    return TEMPLATES.get(component_type, TEMPLATES.get("sonstiges", []))


def get_templates_for_component(komp_id: str, component_type: str,
                                 search_text: str = "") -> dict:
    """
    Get relevant failure templates based on component type AND keyword matching.
    Returns dict with identified categories and their templates.
    """
    categories = set()

    if component_type in TEMPLATES:
        categories.add(component_type)

    search_lower = search_text.lower()
    for mapping in KEYWORD_MAPPING:
        if mapping["keyword"] in search_lower:
            categories.add(mapping["category"])

    # "sonstiges" is always included as a baseline
    categories.add("sonstiges")

    result = {}
    for cat in categories:
        if cat in TEMPLATES:
            result[cat] = TEMPLATES[cat]

    return result


def format_templates_for_prompt(templates: dict) -> str:
    """Format templates dict into readable text for LLM prompts."""
    lines = []
    for category, items in templates.items():
        lines.append(f"\n[{category.upper()}]")
        for item in items:
            lines.append(f"  - {item['typ']}: {item['beschreibung']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("=== Failure Templates Katalog ===\n")
    for cat, items in TEMPLATES.items():
        print(f"{cat}: {len(items)} Vorlagen")

    print(f"\nGesamt: {sum(len(v) for v in TEMPLATES.values())} Vorlagen")

    print("\n--- Beispiel: Templates für 'prozess' + Keyword 'temperatur' ---")
    result = get_templates_for_component("KOMP-001", "prozess", "Temperatur regeln im Reaktor")
    print(format_templates_for_prompt(result))
