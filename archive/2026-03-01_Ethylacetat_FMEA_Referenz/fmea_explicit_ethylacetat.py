"""
Explizite FMEA-Definitionen pro Komponente – Einzelfall-Analyse.

Jede Komponente wird einzeln analysiert. Keine Templates, keine generische Logik.
Erweiterung: Bei neuen Komponenten muss der Agent die Analyse durchführen und
die Definition hier ergänzen.

Basis für Fehlermodi: config.fmea_standards.FEHLERMODI_VORLAGEN – Katalog nach
Kategorien (prozess, thermisch, mechanisch, equipment, msr, sicherheit, dosierung,
sonstiges). Der Agent nutzt ihn als Checkliste, welche Fehlertypen pro Komponente
relevant sind. Keine blinde Übernahme – jede S/O/D-Bewertung einzeln.

Format: get_fmea_for_component(komp_id) -> dict mit functions und failure_modes.
"""


def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})


# ─── KOMP-002: Heizmantel HM-101 ───
# Dampfmantel, 6 bar, Heizfläche 2.5 m², Sattdampf. Kontext: Reaktor R-101, Essigsäure/Ethanol,
# Ex-Zone 1. Controls: TIC-401 (Prozess), TI-401a/b (Mantel).
_FMEA = {
    "KOMP-002": {
        "functions": [
            {
                "funktion_id": "KOMP-002-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Überträgt Wärme vom Sattdampf (6 bar) an den Reaktorprozess",
                "anforderungen": [
                    {"id": "KOMP-002-F1-A1", "parameter": "Heizleistung", "sollwert": "Heizfläche 2.5 m², Dampfdruck 6 bar"},
                    {"id": "KOMP-002-F1-A2", "parameter": "Manteltemperatur", "sollwert": "Max 160 °C, TI-401a/b Überwachung"},
                ],
            },
            {
                "funktion_id": "KOMP-002-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Gewährleistet Dichtheit zwischen Dampfmantel und Prozessraum",
                "anforderungen": [
                    {"id": "KOMP-002-F2-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage (Dampf/Prozess-Trennung)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM1",
                "fehlermodus": "Dampfventil klemmt offen: Unkontrollierte Dampfzufuhr führt zu Überhitzung und Runaway-Gefahr",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM1-UC1", "beschreibung": "Ventilspindel verklebt oder Dichtung beschädigt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Regelmäßige Stellungsprüfung"},
                    {"ursache_id": "KOMP-002-F1-FM1-UC2", "beschreibung": "Stellungsregler defekt oder falsch parametriert", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "SIL-Anforderung prüfen"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Verätzungs-/Verbrennungsgefahr durch heiße Essigsäure in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medien in Auffangwanne"),
                    "anlage": ("Totalausfall", "Reaktorüberhitzung, ggf. Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Prozesstemperatur, Alarm bei Überschreitung", "beeinflusst": "D"},
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "Mantel Ein-/Ausgang", "beeinflusst": "D"},
                ],
                "S": 9,
                "O": 2,
                "D": 3,
                "begruendung_S": "S=9: Runaway mit heißer Säure in Ex-Zone, Personengefährdung hoch",
                "begruendung_O": "O=2: Dampfventil selten klemmend, Stellungsüberwachung vorhanden",
                "begruendung_D": "D=3: TIC-401 und TI-401a/b erkennen Temperaturanstieg vor Runaway",
            },
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM2",
                "fehlermodus": "Kondensat staut sich im Mantel: Schlechte Wärmeübertragung, Reaktion verlangsamt",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM2-UC1", "beschreibung": "Kondensatablauf (Trap) verstopft", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Trap-Inspektion bei Revision"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktion läuft nicht optimal, Chargenqualität"),
                    "kosten": ("Bis 10.000 €", "Chargenverlust, Nacharbeit"),
                },
                "controls": [
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturdifferenz Ein-/Ausgang deutet auf Stau hin", "beeinflusst": "D"},
                ],
                "S": 5,
                "O": 3,
                "D": 4,
                "begruendung_S": "S=5: Keine Personengefährdung, Qualitäts-/Produktionsauswirkung",
                "begruendung_O": "O=3: Trap-Verstopfung gelegentlich bei Dampfsystemen",
                "begruendung_D": "D=4: Temperaturgradient-Monitoring erkennt Abweichung",
            },
            {
                "funktion_id": "KOMP-002-F2",
                "fehler_id": "KOMP-002-F2-FM1",
                "fehlermodus": "Rohrleckage im Heizmantel: Dampf dringt in Prozess oder Prozess in Mantel",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-002-F2-FM1-UC1", "beschreibung": "Korrosion oder Rissbildung an Mantelrohr", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-002-F2-FM1-UC2", "beschreibung": "Thermische Spannungen durch Temperaturgradienten", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Berechnung thermischer Spannungen"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Dampf/Prozess-Freisetzung, Verätzungsgefahr in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Reaktor stilllegen, Leckage beheben"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druckänderung bei größerer Leckage indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 2,
                "D": 5,
                "begruendung_S": "S=8: Medienfreisetzung in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "O=2: Mantelleckage bei Druckbehältern selten (Reliability-DB)",
                "begruendung_D": "D=5: Keine direkte Leckageüberwachung am Mantel",
            },
        ],
    },

    # ─── KOMP-003: Kühlmantel KM-101 ───
    # Kühlwassermantel, 500 L/h, Kühlfläche 2.5 m², Min 10 °C, Notkühlung Sole -10 °C.
    # Kontext: Reaktor R-101, Essigsäure/Ethanol, Ex-Zone 1. Controls: TIC-401 (Prozess).
    "KOMP-003": {
        "functions": [
            {
                "funktion_id": "KOMP-003-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Führt Wärme vom Reaktorprozess an das Kühlwasser (500 L/h) ab",
                "anforderungen": [
                    {"id": "KOMP-003-F1-A1", "parameter": "Kühlleistung", "sollwert": "Kühlfläche 2.5 m², Durchfluss 500 L/h"},
                    {"id": "KOMP-003-F1-A2", "parameter": "Kühlwassertemperatur", "sollwert": "Min 10 °C (Vereisung vermeiden), Notkühlung Sole -10 °C"},
                ],
            },
            {
                "funktion_id": "KOMP-003-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Gewährleistet Dichtheit zwischen Kühlmantel und Prozessraum",
                "anforderungen": [
                    {"id": "KOMP-003-F2-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage (Produkt/Kühlwasser-Trennung)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-003-F1",
                "fehler_id": "KOMP-003-F1-FM1",
                "fehlermodus": "Kühlwasserdurchfluss fällt aus: Keine Wärmeabfuhr, Runaway-Gefahr bei exothermer Reaktion",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-003-F1-FM1-UC1", "beschreibung": "Kühlwasserpumpe ausgefallen oder Leitung verstopft", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Durchflussüberwachung"},
                    {"ursache_id": "KOMP-003-F1-FM1-UC2", "beschreibung": "Ventil am Kühlwassereinlauf geschlossen oder fehlbedient", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Stellungsüberwachung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Runaway mit heißer Essigsäure in Ex-Zone 1, Verätzungs-/Verbrennungsgefahr"),
                    "umwelt": ("Betriebsbereich", "Medien in Auffangwanne"),
                    "anlage": ("Totalausfall", "Reaktorüberhitzung, ggf. Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Prozesstemperatur, Alarm bei Überschreitung", "beeinflusst": "D"},
                ],
                "S": 9,
                "O": 2,
                "D": 4,
                "begruendung_S": "S=9: Runaway mit heißer Säure in Ex-Zone, Personengefährdung hoch",
                "begruendung_O": "O=2: Kühlwasserdurchfluss-Ausfall selten, TIC-401 vorhanden",
                "begruendung_D": "D=4: TIC-401 erkennt Temperaturanstieg, aber kein direkter Durchfluss-Sensor",
            },
            {
                "funktion_id": "KOMP-003-F1",
                "fehler_id": "KOMP-003-F1-FM2",
                "fehlermodus": "Kühlwassertemperatur zu niedrig: Vereisung im Mantel, Rohrbruch möglich",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-003-F1-FM2-UC1", "beschreibung": "Kühlwasser zu kalt (Winterbetrieb, Sole-Notkühlung versehentlich aktiv)", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Minimaltemperatur-Überwachung Rücklauf"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung bei Vereisung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch durch Eisbildung, Leckage"),
                    "kosten": ("Bis 50.000 €", "Mantelreparatur, Stillstand"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Prozesstemperatur indirekt – Vereisung erst bei Ausfall erkennbar", "beeinflusst": "D"},
                ],
                "S": 6,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=6: Rohrbruch kann zu Leckage führen, Ex-Zone",
                "begruendung_O": "O=3: Vereisung bei Kühlwassersystemen gelegentlich",
                "begruendung_D": "D=5: Keine direkte Kühlwassertemperatur-Überwachung am Ein-/Auslauf",
            },
            {
                "funktion_id": "KOMP-003-F2",
                "fehler_id": "KOMP-003-F2-FM1",
                "fehlermodus": "Rohrleckage im Kühlmantel: Kühlwasser dringt in Prozess oder Prozess in Kühlwasser",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-003-F2-FM1-UC1", "beschreibung": "Korrosion oder Rissbildung an Mantelrohr", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-003-F2-FM1-UC2", "beschreibung": "Vereisungsschaden oder thermische Spannungen", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Minimaltemperatur einhalten"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung in Ex-Zone, Verätzungsgefahr"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne, Kühlwasserkreislauf kontaminiert"),
                    "anlage": ("Teilausfall", "Reaktor stilllegen, Leckage beheben"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung, Kühlwasseraufbereitung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druckänderung bei größerer Leckage indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 2,
                "D": 5,
                "begruendung_S": "S=8: Medienfreisetzung in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "O=2: Mantelleckage selten (Reliability-DB)",
                "begruendung_D": "D=5: Keine direkte Leckageüberwachung am Kühlmantel",
            },
        ],
    },

    # ─── KOMP-004: Rührwerk RW-101 ───
    # Ankerrührer, 10–200 U/min, 5 kW, ATEX Zone 1, Wellendurchmesser 60 mm.
    # Kontext: Reaktor R-101, Essigsäure/Ethanol, Ex-Zone 1. Controls: LIC-403, SIC-404.
    "KOMP-004": {
        "functions": [
            {
                "funktion_id": "KOMP-004-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Erzeugt Durchmischung im Reaktor für homogene Reaktionsführung",
                "anforderungen": [
                    {"id": "KOMP-004-F1-A1", "parameter": "Drehzahl", "sollwert": "10–200 U/min, SIC-404 Überwachung"},
                    {"id": "KOMP-004-F1-A2", "parameter": "Ex-Schutz", "sollwert": "ATEX Zone 1"},
                ],
            },
            {
                "funktion_id": "KOMP-004-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Gewährleistet Dichtheit der Wellenabdichtung gegen Prozessmedien",
                "anforderungen": [
                    {"id": "KOMP-004-F2-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage an Stopfbuchse/Gleitringdichtung"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-004-F1",
                "fehler_id": "KOMP-004-F1-FM1",
                "fehlermodus": "Rührwerk fällt aus (Lager, Antrieb, Rührerblatt): Keine Durchmischung, Hotspots, unvollständige Reaktion",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-004-F1-FM1-UC1", "beschreibung": "Lagerausfall durch Verschleiß oder Überlastung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-004-F1-FM1-UC2", "beschreibung": "Abrasion am Rührerblatt durch Feststoffe im Prozess", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Feststoffgehalt begrenzen"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Bei Reaktionsrunaway durch fehlende Durchmischung – heiße Säure in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand, Chargenverlust, ggf. Reaktorüberhitzung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "SIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "Drehzahlüberwachung, erkennt Stillstand", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Temperaturanstieg bei fehlender Durchmischung indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 3,
                "D": 3,
                "begruendung_S": "S=8: Runaway-Gefahr bei fehlender Durchmischung, Ex-Zone",
                "begruendung_O": "O=3: Lager-/Rührwerkausfall bei Batch-Betrieb gelegentlich",
                "begruendung_D": "D=3: SIC-404 und TIC-401 erkennen Ausfall bzw. Temperaturanstieg",
            },
            {
                "funktion_id": "KOMP-004-F1",
                "fehler_id": "KOMP-004-F1-FM2",
                "fehlermodus": "Kavitation: Rührer läuft bei zu niedrigem Füllstand oder zu hoher Drehzahl trocken",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-004-F1-FM2-UC1", "beschreibung": "Füllstand unter Mindesthöhe (LIC-403 fehlt oder falsch parametriert)", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL Trockenlaufschutz"},
                    {"ursache_id": "KOMP-004-F1-FM2-UC2", "beschreibung": "Drehzahl zu hoch bei niedrigem Füllstand", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Drehzahlbegrenzung SIC-404"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Lager- und Dichtungsschaden, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Rührwerkreparatur"),
                },
                "controls": [
                    {"name": "LIC-403", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Füllstand, LSLL für Trockenlaufschutz", "beeinflusst": "D"},
                    {"name": "SIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "Drehzahlbegrenzung", "beeinflusst": "D"},
                ],
                "S": 6,
                "O": 3,
                "D": 4,
                "begruendung_S": "S=6: Mechanischer Schaden, indirekt Ex-Zone bei Leckage",
                "begruendung_O": "O=3: Kavitation bei Füllstandsfehlern gelegentlich",
                "begruendung_D": "D=4: LIC-403/SIC-404 vorhanden, aber keine direkte Kavitationserkennung",
            },
            {
                "funktion_id": "KOMP-004-F2",
                "fehler_id": "KOMP-004-F2-FM1",
                "fehlermodus": "Wellenabdichtung undicht: Leckage an Stopfbuchse oder Gleitringdichtung",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-004-F2-FM1-UC1", "beschreibung": "Verschleiß der Dichtung durch abrasive Medien oder falsche Montage", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-004-F2-FM1-UC2", "beschreibung": "Thermische Schädigung durch Überhitzung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Temperaturüberwachung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung Essigsäure/Ethanol in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Reaktor stilllegen, Dichtung wechseln"),
                    "kosten": ("Bis 50.000 €", "Dichtungswechsel, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "Visuelle Prüfung", "typ": "Prüfung", "wirkung": "D", "beschreibung": "Regelmäßige Sichtprüfung auf Tropfen an der Welle", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=8: Essigsäure/Ethanol in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "O=3: Dichtungsausfall bei Rührwerken in Säureumgebung gelegentlich",
                "begruendung_D": "D=5: Keine kontinuierliche Leckageüberwachung, nur Sichtprüfung",
            },
        ],
    },

    # ─── KOMP-005: Destillationskolonne K-101 ───
    # Packungskolonne, 10 Böden, 3 m Höhe, 200 mm Ø, Mellapak 250Y.
    # Kontext: Azeotrope Destillation, Ethylacetat/Wasser, Ex-Zone 1.
    "KOMP-005": {
        "functions": [
            {
                "funktion_id": "KOMP-005-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Stellt Trennleistung für azeotrope Destillation (Ethylacetat/Wasser) bereit",
                "anforderungen": [
                    {"id": "KOMP-005-F1-A1", "parameter": "Trennstufen", "sollwert": "10 theoretische Böden, Packung Mellapak 250Y"},
                    {"id": "KOMP-005-F1-A2", "parameter": "Durchsatz", "sollwert": "200 mm Ø, 3 m Höhe"},
                ],
            },
            {
                "funktion_id": "KOMP-005-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Gewährleistet Dichtheit an Flanschen und Stutzen",
                "anforderungen": [
                    {"id": "KOMP-005-F2-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage (Dämpfe Ethylacetat/Essigsäure)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-005-F1",
                "fehler_id": "KOMP-005-F1-FM1",
                "fehlermodus": "Fouling/Verstopfung der Packung: Trennleistung vermindert, Produktqualität beeinträchtigt",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-005-F1-FM1-UC1", "beschreibung": "Ablagerungen durch Polymerisation oder Feststoffe", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Reinigungsspülung"},
                    {"ursache_id": "KOMP-005-F1-FM1-UC2", "beschreibung": "Falsche Betriebsparameter (Temperatur, Rücklauf)", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Prozessüberwachung"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenqualität, Nacharbeit, ggf. Stillstand"),
                    "kosten": ("Bis 20.000 €", "Chargenverlust, Reinigung"),
                },
                "controls": [
                    {"name": "Differenzdruck", "typ": "Sensor", "wirkung": "B", "beschreibung": "Δp über Packung deutet auf Verstopfung hin", "beeinflusst": "D"},
                ],
                "S": 5,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=5: Qualitätsauswirkung, keine Personengefährdung",
                "begruendung_O": "O=3: Fouling bei Destillation gelegentlich",
                "begruendung_D": "D=5: Kein kontinuierliches Δp-Monitoring vorhanden",
            },
            {
                "funktion_id": "KOMP-005-F1",
                "fehler_id": "KOMP-005-F1-FM2",
                "fehlermodus": "Überdruck in Kolonne: Kondensatorausfall oder Rücklaufunterbrechung",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-005-F1-FM2-UC1", "beschreibung": "Kondensator KD-101/102 fällt aus, Dämpfe kondensieren nicht", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Kühlwasserüberwachung"},
                    {"ursache_id": "KOMP-005-F1-FM2-UC2", "beschreibung": "Rücklaufventil blockiert, Flutungsgefahr", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Stellungsüberwachung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Überdruck kann zu Leckage/Bersten, Medien in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Kolonnen- oder Kondensatorschaden"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druck am Reaktor, Kolonne indirekt", "beeinflusst": "D"},
                    {"name": "PSV-410", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Druckbegrenzung 6 bar", "beeinflusst": "O"},
                ],
                "S": 8,
                "O": 2,
                "D": 4,
                "begruendung_S": "S=8: Überdruck mit brennbaren/ätzenden Medien in Ex-Zone",
                "begruendung_O": "O=2: PSV und Kondensator redundant",
                "begruendung_D": "D=4: PIC-402 erkennt Druckanstieg, aber Kolonne nicht direkt überwacht",
            },
            {
                "funktion_id": "KOMP-005-F2",
                "fehler_id": "KOMP-005-F2-FM1",
                "fehlermodus": "Leckage an Flanschen oder Stutzen: Dämpfe freigesetzt",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-005-F2-FM1-UC1", "beschreibung": "Dichtung beschädigt oder falsch montiert", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Dichtheitsprüfung bei Revision"},
                    {"ursache_id": "KOMP-005-F2-FM1-UC2", "beschreibung": "Thermische Spannungen, Flansch undicht", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Temperaturgradienten begrenzen"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ethylacetat/Essigsäure-Dämpfe in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand, Leckage beheben"),
                    "kosten": ("Bis 50.000 €", "Dichtungswechsel, Charge"),
                },
                "controls": [
                    {"name": "Visuelle Prüfung", "typ": "Prüfung", "wirkung": "D", "beschreibung": "Sichtprüfung bei Begehung", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 2,
                "D": 5,
                "begruendung_S": "S=8: Brennbare/ätzende Dämpfe in Ex-Zone",
                "begruendung_O": "O=2: Flanschleckage bei Edelstahl selten",
                "begruendung_D": "D=5: Keine kontinuierliche Leckageüberwachung",
            },
        ],
    },

    # ─── KOMP-006: Kondensator KD-101 ───
    # Rohrbündel-WT, 5 m², Rohrseitig Produkt, Mantelseitig Kühlwasser.
    "KOMP-006": {
        "functions": [
            {
                "funktion_id": "KOMP-006-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Kondensiert Destillatdämpfe (Ethylacetat/Wasser) durch Kühlwasser",
                "anforderungen": [
                    {"id": "KOMP-006-F1-A1", "parameter": "Wärmeübertragung", "sollwert": "Fläche 5 m², Rohrseitig Produkt, Mantelseitig Kühlwasser"},
                    {"id": "KOMP-006-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Rohrleckage (Produkt/Kühlwasser-Vermischung)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM1",
                "fehlermodus": "Fouling/Verstopfung Rohrbündel: Kondensationsleistung vermindert, Überdruck in Kolonne",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM1-UC1", "beschreibung": "Ablagerungen Rohrseite oder Kühlwasserseite", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Reinigung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Überdruck kann zu Leckage, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Kolonne überdruck, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Reinigung, Charge"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druckanstieg bei Kondensatorausfall", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 3,
                "D": 4,
                "begruendung_S": "S=8: Überdruck mit Medien in Ex-Zone",
                "begruendung_O": "O=3: Fouling bei Kondensatoren gelegentlich",
                "begruendung_D": "D=4: Drucküberwachung erkennt indirekt",
            },
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM2",
                "fehlermodus": "Kühlwassertemperatur zu niedrig: Vereisung im Rohrbündel, Rohrbruch",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM2-UC1", "beschreibung": "Kühlwasser zu kalt (Winter)", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Minimaltemperatur Rücklauf"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch, Leckage"),
                    "kosten": ("Bis 50.000 €", "Kondensatorreparatur"),
                },
                "controls": [],
                "S": 6,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=6: Rohrbruch kann zu Leckage führen",
                "begruendung_O": "O=3: Vereisung gelegentlich",
                "begruendung_D": "D=5: Keine Kühlwassertemperatur-Überwachung",
            },
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM3",
                "fehlermodus": "Rohrleckage: Produkt in Kühlwasser oder Kühlwasser in Produkt",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM3-UC1", "beschreibung": "Korrosion oder Rissbildung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Kühlwasserkreislauf kontaminiert"),
                    "anlage": ("Teilausfall", "Stillstand, Reinigung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Kühlwasseraufbereitung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druckänderung bei Leckage indirekt", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 2,
                "D": 5,
                "begruendung_S": "S=8: Medienfreisetzung Ex-Zone",
                "begruendung_O": "O=2: Rohrleckage selten",
                "begruendung_D": "D=5: Keine direkte Leckageüberwachung",
            },
        ],
    },

    # ─── KOMP-007: Kondensator KD-102 ───
    # Rohrbündel-WT, 8 m², gleiche Funktion wie KD-101.
    "KOMP-007": {
        "functions": [
            {
                "funktion_id": "KOMP-007-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Kondensiert Destillatdämpfe (Ethylacetat/Wasser) durch Kühlwasser",
                "anforderungen": [
                    {"id": "KOMP-007-F1-A1", "parameter": "Wärmeübertragung", "sollwert": "Fläche 8 m², Rohrseitig Produkt, Mantelseitig Kühlwasser"},
                    {"id": "KOMP-007-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Rohrleckage"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM1",
                "fehlermodus": "Fouling/Verstopfung Rohrbündel: Kondensationsleistung vermindert",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM1-UC1", "beschreibung": "Ablagerungen", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Reinigung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Überdruck Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand"),
                    "kosten": ("Bis 50.000 €", "Reinigung"),
                },
                "controls": [{"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druckanstieg", "beeinflusst": "D"}],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "S=8: Überdruck Ex-Zone",
                "begruendung_O": "O=3: Fouling gelegentlich",
                "begruendung_D": "D=4: Druck indirekt",
            },
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM2",
                "fehlermodus": "Kühlwassertemperatur zu niedrig: Vereisung",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM2-UC1", "beschreibung": "Kühlwasser zu kalt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Minimaltemperatur"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch"),
                    "kosten": ("Bis 50.000 €", "Reparatur"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "S=6: Rohrbruch",
                "begruendung_O": "O=3: Vereisung gelegentlich",
                "begruendung_D": "D=5: Keine Überwachung",
            },
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM3",
                "fehlermodus": "Rohrleckage: Produkt/Kühlwasser-Vermischung",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM3-UC1", "beschreibung": "Korrosion/Riss", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Kühlwasser"),
                    "anlage": ("Teilausfall", "Stillstand"),
                    "kosten": ("Bis 100.000 €", "Reparatur"),
                },
                "controls": [{"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druck", "beeinflusst": "D"}],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "S=8: Ex-Zone",
                "begruendung_O": "O=2: Selten",
                "begruendung_D": "D=5: Keine direkte Überwachung",
            },
        ],
    },

    # ─── KOMP-008: Destillatvorlage DV-101 ───
    # 50 L, Inhalt Ethylacetat, Material 1.4571. Kontext: Ex-Zone 1.
    "KOMP-008": {
        "functions": [
            {
                "funktion_id": "KOMP-008-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Speichert Destillat (Ethylacetat) zwischen Kolonne und Weiterverarbeitung",
                "anforderungen": [
                    {"id": "KOMP-008-F1-A1", "parameter": "Volumen", "sollwert": "50 L Nennvolumen"},
                    {"id": "KOMP-008-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage, Material 1.4571 beständig"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-008-F1",
                "fehler_id": "KOMP-008-F1-FM1",
                "fehlermodus": "Überfüllung: Vorlage läuft über, Ethylacetat freigesetzt",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-008-F1-FM1-UC1", "beschreibung": "Zulauf nicht gestoppt, Füllstand nicht überwacht", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Füllstand LAH/LSHH"},
                    {"ursache_id": "KOMP-008-F1-FM1-UC2", "beschreibung": "Ablaufpumpe ausgefallen, Vorlage füllt sich", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Pumpenüberwachung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ethylacetat brennbar, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand, Reinigung"),
                    "kosten": ("Bis 30.000 €", "Reinigung, Produktverlust"),
                },
                "controls": [],
                "S": 8,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=8: Brennbare Flüssigkeit in Ex-Zone",
                "begruendung_O": "O=3: Überfüllung bei manueller Überwachung gelegentlich",
                "begruendung_D": "D=5: Keine Füllstandüberwachung an Vorlage dokumentiert",
            },
            {
                "funktion_id": "KOMP-008-F1",
                "fehler_id": "KOMP-008-F1-FM2",
                "fehlermodus": "Unterfüllung: Ablaufpumpe läuft trocken",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-008-F1-FM2-UC1", "beschreibung": "Kondensatstrom unterbrochen, Vorlage leer", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL Trockenlaufschutz"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Pumpenschaden, Stillstand"),
                    "kosten": ("Bis 10.000 €", "Pumpenreparatur"),
                },
                "controls": [],
                "S": 5,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=5: Mechanischer Schaden, keine Personengefährdung",
                "begruendung_O": "O=3: Trockenlauf bei Pumpen gelegentlich",
                "begruendung_D": "D=5: Kein LSLL an Vorlage dokumentiert",
            },
            {
                "funktion_id": "KOMP-008-F1",
                "fehler_id": "KOMP-008-F1-FM3",
                "fehlermodus": "Leckage an Flanschen oder Stutzen: Ethylacetat freigesetzt",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-008-F1-FM3-UC1", "beschreibung": "Dichtung beschädigt oder falsch montiert", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Dichtheitsprüfung bei Revision"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ethylacetat in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand, Leckage beheben"),
                    "kosten": ("Bis 20.000 €", "Dichtungswechsel, Reinigung"),
                },
                "controls": [
                    {"name": "Visuelle Prüfung", "typ": "Prüfung", "wirkung": "D", "beschreibung": "Sichtprüfung bei Begehung", "beeinflusst": "D"},
                ],
                "S": 8,
                "O": 2,
                "D": 5,
                "begruendung_S": "S=8: Brennbare Flüssigkeit Ex-Zone",
                "begruendung_O": "O=2: Flanschleckage bei Edelstahl selten",
                "begruendung_D": "D=5: Keine kontinuierliche Leckageüberwachung",
            },
        ],
    },

    # ─── KOMP-009: Destillatvorlage DV-102 ───
    # 50 L, Inhalt Wasser, Material 1.4571. Weniger kritisch als DV-101 (Ethylacetat).
    "KOMP-009": {
        "functions": [
            {
                "funktion_id": "KOMP-009-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Speichert Wasserphase aus azeotroper Destillation zwischen",
                "anforderungen": [
                    {"id": "KOMP-009-F1-A1", "parameter": "Volumen", "sollwert": "50 L Nennvolumen"},
                    {"id": "KOMP-009-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-009-F1",
                "fehler_id": "KOMP-009-F1-FM1",
                "fehlermodus": "Überfüllung: Vorlage läuft über",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-009-F1-FM1-UC1", "beschreibung": "Zulauf nicht gestoppt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Füllstand LAH"},
                ],
                "effects": {
                    "mensch": ("Keine", "Wasser weniger kritisch"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Reinigung"),
                    "kosten": ("Bis 5.000 €", "Reinigung"),
                },
                "controls": [],
                "S": 5,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=5: Wasser, geringere Personengefährdung",
                "begruendung_O": "O=3: Überfüllung gelegentlich",
                "begruendung_D": "D=5: Keine Füllstandüberwachung dokumentiert",
            },
            {
                "funktion_id": "KOMP-009-F1",
                "fehler_id": "KOMP-009-F1-FM2",
                "fehlermodus": "Unterfüllung: Ablaufpumpe trocken",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-009-F1-FM2-UC1", "beschreibung": "Vorlage leer, Pumpe läuft trocken", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Pumpenschaden"),
                    "kosten": ("Bis 10.000 €", "Reparatur"),
                },
                "controls": [],
                "S": 4,
                "O": 3,
                "D": 5,
                "begruendung_S": "S=4: Mechanischer Schaden",
                "begruendung_O": "O=3: Trockenlauf gelegentlich",
                "begruendung_D": "D=5: Kein LSLL",
            },
            {
                "funktion_id": "KOMP-009-F1",
                "fehler_id": "KOMP-009-F1-FM3",
                "fehlermodus": "Leckage an Flanschen: Wasser freigesetzt",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-009-F1-FM3-UC1", "beschreibung": "Dichtung beschädigt", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "Wasser ungiftig"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Leckage beheben"),
                    "kosten": ("Bis 10.000 €", "Dichtungswechsel"),
                },
                "controls": [
                    {"name": "Visuelle Prüfung", "typ": "Prüfung", "wirkung": "D", "beschreibung": "Sichtprüfung", "beeinflusst": "D"},
                ],
                "S": 5,
                "O": 2,
                "D": 5,
                "begruendung_S": "S=5: Ex-Zone, aber Wasser weniger kritisch",
                "begruendung_O": "O=2: Selten",
                "begruendung_D": "D=5: Keine kontinuierliche Überwachung",
            },
        ],
    },

    # ─── KOMP-010: TIC-401 (Temperaturregelung Prozess, SIL-1) ───
    "KOMP-010": {
        "functions": [{"funktion_id": "KOMP-010-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Prozesstemperatur und liefert Signal für Regelung/Sicherheitsabschaltung", "anforderungen": [{"id": "KOMP-010-F1-A1", "parameter": "Messbereich", "sollwert": "-30 bis 180 °C, ±0.5 °C"}, {"id": "KOMP-010-F1-A2", "parameter": "SIL", "sollwert": "SIL-1"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-010-F1", "fehler_id": "KOMP-010-F1-FM1", "fehlermodus": "Frozen Value: Messwert eingefroren, Regler reagiert nicht", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-010-F1-FM1-UC1", "beschreibung": "Impulsleitungsverstopfung oder Elektronikdefekt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilitätsprüfung"}], "effects": {"mensch": ("Schwere Verletzung", "Runaway unerkannt, Ex-Zone"), "umwelt": ("Betriebsbereich", "Auffangwanne"), "anlage": ("Totalausfall", "Reaktorüberhitzung"), "kosten": ("Bis 500.000 €", "Reaktor, Charge")}, "controls": [{"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vergleichsmessung Mantel", "beeinflusst": "D"}], "S": 8, "O": 4, "D": 4, "begruendung_S": "S=8: Runaway-Gefahr, Ex-Zone", "begruendung_O": "O=4: Frozen Value bei Batch bekannt", "begruendung_D": "D=4: Kein Plausibilitätscheck im DCS"},
            {"funktion_id": "KOMP-010-F1", "fehler_id": "KOMP-010-F1-FM2", "fehlermodus": "Messwertdrift: Anzeige weicht von Istwert ab", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-010-F1-FM2-UC1", "beschreibung": "Alterung, Kontamination", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Verletzungsgefahr", "Regelabweichung, ggf. Runaway"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "Chargenqualität"), "kosten": ("Bis 50.000 €", "Charge")}, "controls": [], "S": 7, "O": 3, "D": 5, "begruendung_S": "S=7: Indirekt Runaway", "begruendung_O": "O=3: Drift gelegentlich", "begruendung_D": "D=5: Keine automatische Drifterkennung"},
            {"funktion_id": "KOMP-010-F1", "fehler_id": "KOMP-010-F1-FM3", "fehlermodus": "Signalausfall: Leitungsunterbrechung oder Sensor defekt", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-010-F1-FM3-UC1", "beschreibung": "Kabelbruch, Stecker", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring-Check"}], "effects": {"mensch": ("Schwere Verletzung", "Blinder Regler"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "4-20 mA", "typ": "System", "wirkung": "D", "beschreibung": "Außerbereich bei Unterbrechung", "beeinflusst": "D"}], "S": 8, "O": 3, "D": 4, "begruendung_S": "S=8: Runaway", "begruendung_O": "O=3: Ausfall selten", "begruendung_D": "D=4: Außerbereich erkennbar"},
        ],
    },
    # ─── KOMP-011: TI-401a, KOMP-012: TI-401b (Temperatur Mantel, ohne SIL) ───
    "KOMP-011": {
        "functions": [{"funktion_id": "KOMP-011-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Manteltemperatur Einlauf (Vergleichsmessung)", "anforderungen": [{"id": "KOMP-011-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 200 °C, ±1 °C"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-011-F1", "fehler_id": "KOMP-011-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-011-F1-FM1-UC1", "beschreibung": "Impulsleitung/Sensor", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Keine", "Vergleichsmessung, kein SIL"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Einschränkung Diagnose"), "kosten": ("Bis 10.000 €", "-")}, "controls": [], "S": 5, "O": 4, "D": 5, "begruendung_S": "S=5: Kein SIL, nur Vergleich", "begruendung_O": "O=4: Gelegentlich", "begruendung_D": "D=5: Keine Prüfung"},
            {"funktion_id": "KOMP-011-F1", "fehler_id": "KOMP-011-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-011-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Keine", "Diagnose eingeschränkt"), "kosten": ("Bis 5.000 €", "-")}, "controls": [], "S": 4, "O": 3, "D": 5, "begruendung_S": "S=4: Gering", "begruendung_O": "O=3: Drift", "begruendung_D": "D=5: Keine"},
            {"funktion_id": "KOMP-011-F1", "fehler_id": "KOMP-011-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-011-F1-FM3-UC1", "beschreibung": "Leitung/Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Vergleich fehlt"), "kosten": ("Bis 5.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 4, "begruendung_S": "S=5: Ex-Zone", "begruendung_O": "O=3: Selten", "begruendung_D": "D=4: Außerbereich"},
        ],
    },
    "KOMP-012": {
        "functions": [{"funktion_id": "KOMP-012-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Manteltemperatur Auslauf (Vergleichsmessung)", "anforderungen": [{"id": "KOMP-012-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 200 °C"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-012-F1", "fehler_id": "KOMP-012-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-012-F1-FM1-UC1", "beschreibung": "Sensor/Leitung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Diagnose"), "kosten": ("Bis 10.000 €", "-")}, "controls": [], "S": 5, "O": 4, "D": 5, "begruendung_S": "S=5: Kein SIL", "begruendung_O": "O=4", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-012-F1", "fehler_id": "KOMP-012-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-012-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Keine", "-"), "kosten": ("Bis 5.000 €", "-")}, "controls": [], "S": 4, "O": 3, "D": 5, "begruendung_S": "S=4", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-012-F1", "fehler_id": "KOMP-012-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-012-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 5.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 4, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-013: PIC-402 (Druck, SIL-1) ───
    "KOMP-013": {
        "functions": [{"funktion_id": "KOMP-013-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Prozessdruck und liefert Signal für Regelung/Sicherheitsabschaltung", "anforderungen": [{"id": "KOMP-013-F1-A1", "parameter": "Messbereich", "sollwert": "-1 bis 8 bar, ±0.1 bar"}, {"id": "KOMP-013-F1-A2", "parameter": "SIL", "sollwert": "SIL-1"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-013-F1", "fehler_id": "KOMP-013-F1-FM1", "fehlermodus": "Frozen Value: Druckanstieg unerkannt, sekundäres Berst-Risiko", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-013-F1-FM1-UC1", "beschreibung": "Impulsleitungsverstopfung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Schwere Verletzung", "Bersten, Ex-Zone"), "umwelt": ("Betriebsbereich", "Auffangwanne"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "PSV-410", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Mechanische Druckbegrenzung", "beeinflusst": "O"}], "S": 8, "O": 4, "D": 4, "begruendung_S": "S=8: Berst-Gefahr", "begruendung_O": "O=4: PSV vorhanden", "begruendung_D": "D=4: Kein Plausibilitätscheck"},
            {"funktion_id": "KOMP-013-F1", "fehler_id": "KOMP-013-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-013-F1-FM2-UC1", "beschreibung": "Alterung, Essigsäure", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Verletzungsgefahr", "Druck unerkannt"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 7, "O": 3, "D": 5, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-013-F1", "fehler_id": "KOMP-013-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-013-F1-FM3-UC1", "beschreibung": "Leitung/Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "Blinder Regler"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "4-20 mA", "typ": "System", "wirkung": "D", "beschreibung": "Außerbereich", "beeinflusst": "D"}], "S": 8, "O": 3, "D": 4, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-014: LIC-403 (Füllstand, SIL-1), KOMP-015: LSHH-403 (Überfüllsicherung SIL-2) ───
    "KOMP-014": {
        "functions": [{"funktion_id": "KOMP-014-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Füllstand und liefert Signal für Regelung/Überfüllsicherung", "anforderungen": [{"id": "KOMP-014-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 500 L, Radar"}, {"id": "KOMP-014-F1-A2", "parameter": "SIL", "sollwert": "SIL-1"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-014-F1", "fehler_id": "KOMP-014-F1-FM1", "fehlermodus": "Frozen Value: Überfüllung unerkannt", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-014-F1-FM1-UC1", "beschreibung": "Radar-Störung, Schaum", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSHH redundant"}], "effects": {"mensch": ("Schwere Verletzung", "Überfüllung, Ex-Zone"), "umwelt": ("Betriebsbereich", "Auffangwanne"), "anlage": ("Teilausfall", "Reaktor"), "kosten": ("Bis 100.000 €", "-")}, "controls": [{"name": "LSHH-403", "typ": "Sensor", "wirkung": "O", "sil_level": "SIL-2", "beschreibung": "Unabhängige Überfüllsicherung 480 L", "beeinflusst": "O"}], "S": 8, "O": 3, "D": 4, "begruendung_S": "S=8: Überfüllung", "begruendung_O": "O=3: LSHH redundant", "begruendung_D": "D=4: Kein Plausibilitätscheck"},
            {"funktion_id": "KOMP-014-F1", "fehler_id": "KOMP-014-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-014-F1-FM2-UC1", "beschreibung": "Radar-Kalibrierung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Verletzungsgefahr", "Falsche Füllstandsanzeige"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Chargenqualität"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 6, "O": 3, "D": 5, "begruendung_S": "S=6", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-014-F1", "fehler_id": "KOMP-014-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-014-F1-FM3-UC1", "beschreibung": "Leitung/Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "Blinder Regler"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 100.000 €", "-")}, "controls": [{"name": "LSHH-403", "typ": "Sensor", "wirkung": "O", "beschreibung": "Redundant", "beeinflusst": "O"}], "S": 8, "O": 3, "D": 4, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    "KOMP-015": {
        "functions": [{"funktion_id": "KOMP-015-F1", "typ": "Hauptfunktion", "beschreibung": "Überfüllsicherung bei 480 L (SIL-2), unabhängig von LIC-403", "anforderungen": [{"id": "KOMP-015-F1-A1", "parameter": "Schaltpunkt", "sollwert": "480 L, Vibration"}, {"id": "KOMP-015-F1-A2", "parameter": "SIL", "sollwert": "SIL-2"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-015-F1", "fehler_id": "KOMP-015-F1-FM1", "fehlermodus": "Fail-to-trip: Öffnet nicht bei 480 L – letzte Barriere versagt", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-015-F1-FM1-UC1", "beschreibung": "Vibrationsschalter verklebt, Verkabelung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Funktionsprüfung"}], "effects": {"mensch": ("Schwere Verletzung", "Überfüllung bis Überlauf, Ex-Zone"), "umwelt": ("Betriebsbereich", "Auffangwanne"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 3, "D": 5, "begruendung_S": "S=9: Letzte Barriere", "begruendung_O": "O=3: SIL-2", "begruendung_D": "D=5: Keine Prüfung"},
            {"funktion_id": "KOMP-015-F1", "fehler_id": "KOMP-015-F1-FM2", "fehlermodus": "Frühzeitiges Ansprechen: Stoppt bei korrektem Füllstand", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-015-F1-FM2-UC1", "beschreibung": "Falsche Kalibrierung, Verschmutzung", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Prüfung"}], "effects": {"mensch": ("Keine", "Keine Gefährdung"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Chargenabbruch"), "kosten": ("Bis 20.000 €", "Charge")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5: Nur Produktionsausfall", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-015-F1", "fehler_id": "KOMP-015-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-015-F1-FM3-UC1", "beschreibung": "Leitung/Relais", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "Sicherheit ausgefallen"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 2, "D": 5, "begruendung_S": "S=9: Sicherheitsfunktion", "begruendung_O": "O=2: Selten", "begruendung_D": "D=5: Fail-safe prüfen"},
        ],
    },
    # ─── KOMP-016: SIC-404 (Drehzahlregler) ───
    "KOMP-016": {
        "functions": [{"funktion_id": "KOMP-016-F1", "typ": "Hauptfunktion", "beschreibung": "Misst und regelt Rührwerksdrehzahl (0–250 U/min)", "anforderungen": [{"id": "KOMP-016-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 250 U/min, VFD 5.5 kW"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-016-F1", "fehler_id": "KOMP-016-F1-FM1", "fehlermodus": "Frozen Value: Drehzahl falsch angezeigt", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-016-F1-FM1-UC1", "beschreibung": "VFD/Sensor", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Verletzungsgefahr", "Keine Durchmischung bei Stillstand"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "Runaway möglich"), "kosten": ("Bis 100.000 €", "-")}, "controls": [{"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperatur indirekt", "beeinflusst": "D"}], "S": 7, "O": 4, "D": 4, "begruendung_S": "S=7: Runaway indirekt", "begruendung_O": "O=4", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-016-F1", "fehler_id": "KOMP-016-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-016-F1-FM2-UC1", "beschreibung": "VFD Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Durchmischung"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-016-F1", "fehler_id": "KOMP-016-F1-FM3", "fehlermodus": "Signalausfall: Rührwerk stoppt", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-016-F1-FM3-UC1", "beschreibung": "VFD, Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Verletzungsgefahr", "Keine Durchmischung"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "Runaway"), "kosten": ("Bis 100.000 €", "-")}, "controls": [{"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperatur", "beeinflusst": "D"}], "S": 7, "O": 3, "D": 4, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-017: PSV-410 (Sicherheitsventil 6 bar, DN50) ───
    "KOMP-017": {
        "functions": [{"funktion_id": "KOMP-017-F1", "typ": "Hauptfunktion", "beschreibung": "Begrenzt Druck durch Öffnen bei 6 bar, Abblaseleitung Fackel", "anforderungen": [{"id": "KOMP-017-F1-A1", "parameter": "Ansprechdruck", "sollwert": "6 bar, DN50"}, {"id": "KOMP-017-F1-A2", "parameter": "Prüfintervall", "sollwert": "1 Jahr"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-017-F1", "fehler_id": "KOMP-017-F1-FM1", "fehlermodus": "Fail-to-open: Öffnet nicht bei Ansprechdruck – Berstgefahr", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-017-F1-FM1-UC1", "beschreibung": "Verklebung durch Korrosion (Essigsäure)", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Jährliche Prüfung"}, {"ursache_id": "KOMP-017-F1-FM1-UC2", "beschreibung": "Fremdkörper im Sitz", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Abnahme prüfen"}], "effects": {"mensch": ("Lebensgefahr", "Bersten, Ex-Zone"), "umwelt": ("Betriebsbereich", "Medienfreisetzung"), "anlage": ("Totalausfall", "Reaktor zerstört"), "kosten": ("Bis 1 Mio €", "-")}, "controls": [{"name": "BSV-411", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Redundant 6.5 bar", "beeinflusst": "O"}, {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Alarm bei Druckanstieg", "beeinflusst": "D"}], "S": 10, "O": 3, "D": 3, "begruendung_S": "S=10: Lebensgefahr", "begruendung_O": "O=3: Jährliche Prüfung, korrosive Medien", "begruendung_D": "D=3: BSV redundant, PIC alarmiert"},
            {"funktion_id": "KOMP-017-F1", "fehler_id": "KOMP-017-F1-FM2", "fehlermodus": "Erosion/Kavitation am Sitz (bei Abblasen)", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-017-F1-FM2-UC1", "beschreibung": "Verschleiß bei Abblasvorgang", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Sichtprüfung Abnahme"}], "effects": {"mensch": ("Lebensgefahr", "Nächstes Mal Fail-to-open"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "PSV defekt"), "kosten": ("Bis 50.000 €", "Ventilwechsel")}, "controls": [], "S": 10, "O": 4, "D": 4, "begruendung_S": "S=10: Indirekt Berst", "begruendung_O": "O=4: Selten", "begruendung_D": "D=4: Bei Abnahme"},
        ],
    },
    # ─── KOMP-018: BSV-411 (Berstscheibe 6.5 bar, DN50) ───
    "KOMP-018": {
        "functions": [{"funktion_id": "KOMP-018-F1", "typ": "Hauptfunktion", "beschreibung": "Letzte Druckbarriere bei 6.5 bar, Hastelloy C276", "anforderungen": [{"id": "KOMP-018-F1-A1", "parameter": "Ansprechdruck", "sollwert": "6.5 bar, DN50"}, {"id": "KOMP-018-F1-A2", "parameter": "Material", "sollwert": "Hastelloy C276"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-018-F1", "fehler_id": "KOMP-018-F1-FM1", "fehlermodus": "Fail-to-open: Berstscheibe öffnet nicht bei 6.5 bar", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-018-F1-FM1-UC1", "beschreibung": "Alterung, falsche Dimensionierung", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Berechnung"}, {"ursache_id": "KOMP-018-F1-FM1-UC2", "beschreibung": "Korrosion durch Medien", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Lebensgefahr", "Bersten"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 1 Mio €", "-")}, "controls": [{"name": "PSV-410", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Primär 6 bar", "beeinflusst": "O"}], "S": 10, "O": 2, "D": 5, "begruendung_S": "S=10: Lebensgefahr", "begruendung_O": "O=2: PSV primär, BSV Backup", "begruendung_D": "D=5: Keine Prüfung möglich"},
            {"funktion_id": "KOMP-018-F1", "fehler_id": "KOMP-018-F1-FM2", "fehlermodus": "Frühzeitiges Bersten: Öffnet unter Betriebsdruck", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-018-F1-FM2-UC1", "beschreibung": "Materialfehler, Ermüdung", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Qualitätssicherung"}], "effects": {"mensch": ("Schwere Verletzung", "Medienfreisetzung"), "umwelt": ("Betriebsbereich", "Fackel"), "anlage": ("Teilausfall", "Stillstand"), "kosten": ("Bis 100.000 €", "Scheibenwechsel")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8: Ex-Zone", "begruendung_O": "O=2: Selten", "begruendung_D": "D=5: Keine"},
        ],
    },
    # ─── KOMP-019: VSV-412 (Vakuum-Sicherheitsventil -0.8 bar) ───
    "KOMP-019": {
        "functions": [{"funktion_id": "KOMP-019-F1", "typ": "Hauptfunktion", "beschreibung": "Vakuumbrecher: Verhindert Unterdruck unter -0.8 bar, DN25", "anforderungen": [{"id": "KOMP-019-F1-A1", "parameter": "Ansprechdruck", "sollwert": "-0.8 bar"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-019-F1", "fehler_id": "KOMP-019-F1-FM1", "fehlermodus": "Fail-to-open: Öffnet nicht bei Unterdruck – Implosionsgefahr", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-019-F1-FM1-UC1", "beschreibung": "Verklebung, Korrosion", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Jährliche Prüfung"}], "effects": {"mensch": ("Schwere Verletzung", "Implosion, Ex-Zone"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 3, "D": 5, "begruendung_S": "S=9: Implosion", "begruendung_O": "O=3: Korrosion", "begruendung_D": "D=5: Keine Prüfung"},
            {"funktion_id": "KOMP-019-F1", "fehler_id": "KOMP-019-F1-FM2", "fehlermodus": "Leckage: Luft dringt bei Normalbetrieb ein", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-019-F1-FM2-UC1", "beschreibung": "Dichtung undicht", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Keine", "Keine Gefährdung"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Sauerstoff in Prozess"), "kosten": ("Bis 20.000 €", "Dichtung")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5: Qualität", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-020: NOT-AUS-R101 ───
    "KOMP-020": {
        "functions": [{"funktion_id": "KOMP-020-F1", "typ": "Hauptfunktion", "beschreibung": "Schaltet Anlage bei Betätigung sicher ab (Antriebe, Ventile)", "anforderungen": [{"id": "KOMP-020-F1-A1", "parameter": "Reaktionszeit", "sollwert": "< 1 s"}, {"id": "KOMP-020-F1-A2", "parameter": "Rückstellung", "sollwert": "Manuell vor Ort"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-020-F1", "fehler_id": "KOMP-020-F1-FM1", "fehlermodus": "Fail-to-trip: NOT-AUS schaltet nicht ab", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-020-F1-FM1-UC1", "beschreibung": "Verkabelung, Relais defekt", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Funktionsprüfung"}, {"ursache_id": "KOMP-020-F1-FM1-UC2", "beschreibung": "Falsche Parametrierung", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Abnahme"}], "effects": {"mensch": ("Lebensgefahr", "Keine Abschaltung bei Notfall"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Eskalation"), "kosten": ("Bis 1 Mio €", "-")}, "controls": [], "S": 10, "O": 2, "D": 5, "begruendung_S": "S=10: Lebensgefahr", "begruendung_O": "O=2: Selten", "begruendung_D": "D=5: Keine Prüfung"},
            {"funktion_id": "KOMP-020-F1", "fehler_id": "KOMP-020-F1-FM2", "fehlermodus": "Fehlbedienung: NOT-AUS nicht betätigt obwohl nötig", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-020-F1-FM2-UC1", "beschreibung": "Unterweisung fehlt, Panik", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Schulung"}, {"ursache_id": "KOMP-020-F1-FM2-UC2", "beschreibung": "Schalter nicht erreichbar", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Ergonomie"}], "effects": {"mensch": ("Lebensgefahr", "Eskalation"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 1 Mio €", "-")}, "controls": [], "S": 10, "O": 3, "D": 5, "begruendung_S": "S=10: Lebensgefahr", "begruendung_O": "O=3: Human Factor", "begruendung_D": "D=5: Keine"},
            {"funktion_id": "KOMP-020-F1", "fehler_id": "KOMP-020-F1-FM3", "fehlermodus": "Kennzeichnungsfehler: Verwechslung mit anderem Schalter", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-020-F1-FM3-UC1", "beschreibung": "Schlechte Beschriftung", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Begehung"}], "effects": {"mensch": ("Lebensgefahr", "Falscher Schalter"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 100.000 €", "-")}, "controls": [], "S": 10, "O": 3, "D": 5, "begruendung_S": "S=10", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-021: Dosiersystem DS-200 (System) ───
    "KOMP-021": {
        "functions": [{"funktion_id": "KOMP-021-F1", "typ": "Hauptfunktion", "beschreibung": "Vollautomatische Dosierung von Ethanol, Essigsäure und Katalysator (Schwefelsäure) für Synthesereaktor R-101", "anforderungen": [{"id": "KOMP-021-F1-A1", "parameter": "Flow-Regelung", "sollwert": "DCS-Integration, FIC-404/405"}, {"id": "KOMP-021-F1-A2", "parameter": "Verfügbarkeit", "sollwert": "Ex-Zone 1, 2×200 L Vorlagen"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-021-F1", "fehler_id": "KOMP-021-F1-FM1", "fehlermodus": "Verkettung: Mehrere Dosierausfälle oder -fehler gleichzeitig", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-021-F1-FM1-UC1", "beschreibung": "Stromausfall, DCS-Ausfall, Wartungsfehler, LSLL + Pumpe", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Redundanz, Sollmengenüberwachung"}], "effects": {"mensch": ("Schwere Verletzung", "Überdosierung Katalysator + fehlende Erkennung → Runaway"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Exothermie, Charge verloren"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "FIC-404/405", "typ": "Regler", "wirkung": "B", "beschreibung": "Flow-Regelung", "beeinflusst": "D"}, {"name": "LSLL-201/202", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz", "beeinflusst": "D"}], "S": 9, "O": 4, "D": 4, "begruendung_S": "S=9: Runaway bei Verkettung", "begruendung_O": "O=4: Selten", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-022: Vorlagebehälter VB-201 (Ethanol, 200 L) ───
    "KOMP-022": {
        "functions": [{"funktion_id": "KOMP-022-F1", "typ": "Hauptfunktion", "beschreibung": "Speichert Ethanol für Dosierung (200 L)", "anforderungen": [{"id": "KOMP-022-F1-A1", "parameter": "Volumen", "sollwert": "200 L"}, {"id": "KOMP-022-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-022-F1", "fehler_id": "KOMP-022-F1-FM1", "fehlermodus": "Überfüllung: Vorlage läuft über", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-022-F1-FM1-UC1", "beschreibung": "Zulauf nicht gestoppt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Füllstand LAH"}], "effects": {"mensch": ("Schwere Verletzung", "Ethanol brennbar, Ex-Zone"), "umwelt": ("Betriebsbereich", "Auffangwanne"), "anlage": ("Teilausfall", "Reinigung"), "kosten": ("Bis 30.000 €", "-")}, "controls": [{"name": "LI-201", "typ": "Sensor", "wirkung": "B", "beschreibung": "Füllstand", "beeinflusst": "D"}], "S": 8, "O": 3, "D": 4, "begruendung_S": "S=8: Brennbar Ex-Zone", "begruendung_O": "O=3", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-022-F1", "fehler_id": "KOMP-022-F1-FM2", "fehlermodus": "Unterfüllung: Pumpe läuft trocken", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-022-F1-FM2-UC1", "beschreibung": "Vorlage leer", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL-201"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Pumpenschaden"), "kosten": ("Bis 10.000 €", "-")}, "controls": [{"name": "LSLL-201", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Trockenlaufschutz 20 L", "beeinflusst": "D"}], "S": 5, "O": 3, "D": 3, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=3: LSLL"},
            {"funktion_id": "KOMP-022-F1", "fehler_id": "KOMP-022-F1-FM3", "fehlermodus": "Leckage an Flanschen", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-022-F1-FM3-UC1", "beschreibung": "Dichtung beschädigt", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Schwere Verletzung", "Ethanol Ex-Zone"), "umwelt": ("Betriebsbereich", "AW-200"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-023: Vorlagebehälter VB-202 (Essigsäure, 200 L) ───
    "KOMP-023": {
        "functions": [{"funktion_id": "KOMP-023-F1", "typ": "Hauptfunktion", "beschreibung": "Speichert Essigsäure für Dosierung (200 L)", "anforderungen": [{"id": "KOMP-023-F1-A1", "parameter": "Volumen", "sollwert": "200 L"}, {"id": "KOMP-023-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-023-F1", "fehler_id": "KOMP-023-F1-FM1", "fehlermodus": "Überfüllung", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-023-F1-FM1-UC1", "beschreibung": "Zulauf nicht gestoppt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LAH"}], "effects": {"mensch": ("Schwere Verletzung", "Essigsäure ätzend, Ex-Zone"), "umwelt": ("Betriebsbereich", "AW-200"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 30.000 €", "-")}, "controls": [{"name": "LI-202", "typ": "Sensor", "wirkung": "B", "beschreibung": "Füllstand", "beeinflusst": "D"}], "S": 8, "O": 3, "D": 4, "begruendung_S": "S=8: Ätzend Ex-Zone", "begruendung_O": "O=3", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-023-F1", "fehler_id": "KOMP-023-F1-FM2", "fehlermodus": "Unterfüllung: Pumpe trocken", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-023-F1-FM2-UC1", "beschreibung": "Vorlage leer", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL-202"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Pumpenschaden"), "kosten": ("Bis 10.000 €", "-")}, "controls": [{"name": "LSLL-202", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Trockenlaufschutz", "beeinflusst": "D"}], "S": 5, "O": 3, "D": 3, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=3"},
            {"funktion_id": "KOMP-023-F1", "fehler_id": "KOMP-023-F1-FM3", "fehlermodus": "Leckage", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-023-F1-FM3-UC1", "beschreibung": "Dichtung", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Schwere Verletzung", "Essigsäure Ex-Zone"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-024: Dosierpumpe P-201 (Ethanol, 5–50 L/h) ───
    "KOMP-024": {
        "functions": [{"funktion_id": "KOMP-024-F1", "typ": "Hauptfunktion", "beschreibung": "Fördert Ethanol mit definierter Dosierrate (5–50 L/h) in Reaktor", "anforderungen": [{"id": "KOMP-024-F1-A1", "parameter": "Durchfluss", "sollwert": "5–50 L/h, FIC-404"}, {"id": "KOMP-024-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage Membran"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-024-F1", "fehler_id": "KOMP-024-F1-FM1", "fehlermodus": "Überdosierung: Mehr Ethanol als Soll", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-024-F1-FM1-UC1", "beschreibung": "FIC-404 Drift, Regelungsfehler", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Totalizer"}, {"ursache_id": "KOMP-024-F1-FM1-UC2", "beschreibung": "Membran undicht, Bypass", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Schwere Verletzung", "Exothermie, Ex-Zone"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "FIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "Coriolis Durchfluss", "beeinflusst": "D"}], "S": 9, "O": 4, "D": 4, "begruendung_S": "S=9: Exothermie", "begruendung_O": "O=4: Dosierfehler bekannt", "begruendung_D": "D=4: FIC vorhanden"},
            {"funktion_id": "KOMP-024-F1", "fehler_id": "KOMP-024-F1-FM2", "fehlermodus": "Unterdosierung: Weniger Ethanol, Akkumulation", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-024-F1-FM2-UC1", "beschreibung": "Pumpe defekt, Leitung verstopft", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL, Sollmenge"}], "effects": {"mensch": ("Verletzungsgefahr", "Spätere Exothermie bei Nachdosierung"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Chargenqualität"), "kosten": ("Bis 50.000 €", "-")}, "controls": [{"name": "LSLL-201", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz", "beeinflusst": "D"}], "S": 7, "O": 4, "D": 4, "begruendung_S": "S=7: Akkumulation", "begruendung_O": "O=4", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-024-F1", "fehler_id": "KOMP-024-F1-FM3", "fehlermodus": "Membranbruch: Leckage an Pumpenkopf", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-024-F1-FM3-UC1", "beschreibung": "Verschleiß, chemische Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Membranwechsel"}], "effects": {"mensch": ("Schwere Verletzung", "Ethanol Ex-Zone"), "umwelt": ("Betriebsbereich", "AW-200"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8: Brennbar", "begruendung_O": "O=3: Membran", "begruendung_D": "D=5: Keine Überwachung"},
        ],
    },
    # ─── KOMP-025: Dosierpumpe P-202 (Essigsäure, 5–50 L/h) ───
    "KOMP-025": {
        "functions": [{"funktion_id": "KOMP-025-F1", "typ": "Hauptfunktion", "beschreibung": "Fördert Essigsäure mit definierter Dosierrate (5–50 L/h)", "anforderungen": [{"id": "KOMP-025-F1-A1", "parameter": "Durchfluss", "sollwert": "5–50 L/h, FIC-405"}, {"id": "KOMP-025-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-025-F1", "fehler_id": "KOMP-025-F1-FM1", "fehlermodus": "Überdosierung: Mehr Essigsäure als Soll", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-025-F1-FM1-UC1", "beschreibung": "FIC-405, Regelung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Totalizer"}], "effects": {"mensch": ("Schwere Verletzung", "Exothermie, Ex-Zone"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "FIC-405", "typ": "Sensor", "wirkung": "B", "beschreibung": "Durchfluss", "beeinflusst": "D"}], "S": 9, "O": 4, "D": 4, "begruendung_S": "S=9: Exothermie", "begruendung_O": "O=4", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-025-F1", "fehler_id": "KOMP-025-F1-FM2", "fehlermodus": "Unterdosierung", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-025-F1-FM2-UC1", "beschreibung": "Pumpe, Leitung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "LSLL-202"}], "effects": {"mensch": ("Verletzungsgefahr", "Akkumulation"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [{"name": "LSLL-202", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz", "beeinflusst": "D"}], "S": 7, "O": 4, "D": 4, "begruendung_S": "S=7", "begruendung_O": "O=4", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-025-F1", "fehler_id": "KOMP-025-F1-FM3", "fehlermodus": "Membranbruch: Leckage an Pumpenkopf", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-025-F1-FM3-UC1", "beschreibung": "Verschleiß, Essigsäure", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Membranwechsel"}], "effects": {"mensch": ("Schwere Verletzung", "Essigsäure ätzend Ex-Zone"), "umwelt": ("Betriebsbereich", "AW-200"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8: Ätzend", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-026: Katalysatordosierung KD-203 (Schwefelsäure 98 %) ───
    "KOMP-026": {
        "functions": [{"funktion_id": "KOMP-026-F1", "typ": "Hauptfunktion", "beschreibung": "Dosiert Schwefelsäure 98 % (0.1–1 L/h) als Katalysator", "anforderungen": [{"id": "KOMP-026-F1-A1", "parameter": "Durchfluss", "sollwert": "0.1–1 L/h"}, {"id": "KOMP-026-F1-A2", "parameter": "Dichtheit", "sollwert": "Null-Leckage, hochkorrosiv"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-026-F1", "fehler_id": "KOMP-026-F1-FM1", "fehlermodus": "Überdosierung: Zu viel Schwefelsäure – starke Exothermie", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-026-F1-FM1-UC1", "beschreibung": "Dosierrate falsch, Ventil klemmt offen", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Totalizer"}], "effects": {"mensch": ("Lebensgefahr", "Starke Exothermie, Schwefelsäure Ex-Zone"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Reaktor"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 4, "D": 5, "begruendung_S": "S=9: Schwefelsäure + Exothermie", "begruendung_O": "O=4: Kleine Dosierung", "begruendung_D": "D=5: Kein Totalizer"},
            {"funktion_id": "KOMP-026-F1", "fehler_id": "KOMP-026-F1-FM2", "fehlermodus": "Unterdosierung: Weniger Katalysator – unvollständige Reaktion", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-026-F1-FM2-UC1", "beschreibung": "Leitung verstopft, Dosierstation defekt", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Sollmenge"}], "effects": {"mensch": ("Verletzungsgefahr", "Akkumulation, spätere Exothermie"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Chargenqualität"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 7, "O": 4, "D": 5, "begruendung_S": "S=7: Akkumulation", "begruendung_O": "O=4", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-026-F1", "fehler_id": "KOMP-026-F1-FM3", "fehlermodus": "Leckage: Schwefelsäure 98 % freigesetzt", "fehlerart": "Dosierung", "causes": [{"ursache_id": "KOMP-026-F1-FM3-UC1", "beschreibung": "Korrosion, Dichtung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Lebensgefahr", "Schwefelsäure ätzend Ex-Zone"), "umwelt": ("Betriebsbereich", "AW-200"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 100.000 €", "-")}, "controls": [{"name": "AW-200", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Auffangwanne", "beeinflusst": "O"}], "S": 9, "O": 3, "D": 5, "begruendung_S": "S=9: Schwefelsäure", "begruendung_O": "O=3: Korrosion", "begruendung_D": "D=5: Keine Überwachung"},
        ],
    },
    # ─── KOMP-027: FIC-404, KOMP-028: FIC-405 (Durchfluss Coriolis, Dosierung) ───
    "KOMP-027": {"functions": [{"funktion_id": "KOMP-027-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Durchfluss Ethanol (0–100 L/h) für Regelung", "anforderungen": [{"id": "KOMP-027-F1-A1", "parameter": "Messbereich", "sollwert": "0–100 L/h, Coriolis ±0.1 %"}]}], "failure_modes": [
        {"funktion_id": "KOMP-027-F1", "fehler_id": "KOMP-027-F1-FM1", "fehlermodus": "Frozen Value: Überdosierung unerkannt", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-027-F1-FM1-UC1", "beschreibung": "Coriolis verstopft, Elektronik", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Schwere Verletzung", "Exothermie"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 4, "D": 5, "begruendung_S": "S=9", "begruendung_O": "O=4", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-027-F1", "fehler_id": "KOMP-027-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-027-F1-FM2-UC1", "beschreibung": "Kalibrierung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Verletzungsgefahr", "Dosierfehler"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 7, "O": 3, "D": 5, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-027-F1", "fehler_id": "KOMP-027-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-027-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "Blinder Regler"), "umwelt": ("Keine", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 3, "D": 4, "begruendung_S": "S=9", "begruendung_O": "O=3", "begruendung_D": "D=4"},
    ]},
    "KOMP-028": {"functions": [{"funktion_id": "KOMP-028-F1", "typ": "Hauptfunktion", "beschreibung": "Misst Durchfluss Essigsäure (0–100 L/h) für Regelung", "anforderungen": [{"id": "KOMP-028-F1-A1", "parameter": "Messbereich", "sollwert": "0–100 L/h, Coriolis"}]}], "failure_modes": [
        {"funktion_id": "KOMP-028-F1", "fehler_id": "KOMP-028-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-028-F1-FM1-UC1", "beschreibung": "Sensor/Leitung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Schwere Verletzung", "Exothermie"), "umwelt": ("Keine", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 4, "D": 5, "begruendung_S": "S=9", "begruendung_O": "O=4", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-028-F1", "fehler_id": "KOMP-028-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-028-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Verletzungsgefahr", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 7, "O": 3, "D": 5, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-028-F1", "fehler_id": "KOMP-028-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-028-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 3, "D": 4, "begruendung_S": "S=9", "begruendung_O": "O=3", "begruendung_D": "D=4"},
    ]},
    # ─── KOMP-029: LI-201, KOMP-030: LI-202 (Füllstandsanzeige) ───
    "KOMP-029": {"functions": [{"funktion_id": "KOMP-029-F1", "typ": "Hauptfunktion", "beschreibung": "Zeigt Füllstand VB-201 (0–200 L) an", "anforderungen": [{"id": "KOMP-029-F1-A1", "parameter": "Messbereich", "sollwert": "0–200 L, Hydrostatisch"}]}], "failure_modes": [
        {"funktion_id": "KOMP-029-F1", "fehler_id": "KOMP-029-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-029-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Verletzungsgefahr", "Überfüllung/Trockenlauf"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 30.000 €", "-")}, "controls": [{"name": "LSLL-201", "typ": "Sensor", "wirkung": "O", "beschreibung": "Trockenlaufschutz", "beeinflusst": "O"}], "S": 7, "O": 4, "D": 4, "begruendung_S": "S=7", "begruendung_O": "O=4", "begruendung_D": "D=4"},
        {"funktion_id": "KOMP-029-F1", "fehler_id": "KOMP-029-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-029-F1-FM2-UC1", "beschreibung": "Kalibrierung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Falsche Anzeige"), "kosten": ("Bis 10.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-029-F1", "fehler_id": "KOMP-029-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-029-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Verletzungsgefahr", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [{"name": "LSLL-201", "typ": "Sensor", "wirkung": "O", "beschreibung": "Redundant", "beeinflusst": "O"}], "S": 7, "O": 3, "D": 4, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=4"},
    ]},
    "KOMP-030": {"functions": [{"funktion_id": "KOMP-030-F1", "typ": "Hauptfunktion", "beschreibung": "Zeigt Füllstand VB-202 (0–200 L) an", "anforderungen": [{"id": "KOMP-030-F1-A1", "parameter": "Messbereich", "sollwert": "0–200 L"}]}], "failure_modes": [
        {"funktion_id": "KOMP-030-F1", "fehler_id": "KOMP-030-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-030-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Plausibilität"}], "effects": {"mensch": ("Verletzungsgefahr", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 30.000 €", "-")}, "controls": [{"name": "LSLL-202", "typ": "Sensor", "wirkung": "O", "beschreibung": "Trockenlaufschutz", "beeinflusst": "O"}], "S": 7, "O": 4, "D": 4, "begruendung_S": "S=7", "begruendung_O": "O=4", "begruendung_D": "D=4"},
        {"funktion_id": "KOMP-030-F1", "fehler_id": "KOMP-030-F1-FM2", "fehlermodus": "Messwertdrift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-030-F1-FM2-UC1", "beschreibung": "Kalibrierung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 10.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-030-F1", "fehler_id": "KOMP-030-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-030-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Verletzungsgefahr", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [{"name": "LSLL-202", "typ": "Sensor", "wirkung": "O", "beschreibung": "Redundant", "beeinflusst": "O"}], "S": 7, "O": 3, "D": 4, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=4"},
    ]},
    # ─── KOMP-031: LSLL-201, KOMP-032: LSLL-202 (Trockenlaufschutz SIL-1) ───
    "KOMP-031": {"functions": [{"funktion_id": "KOMP-031-F1", "typ": "Hauptfunktion", "beschreibung": "Trockenlaufschutz P-201 bei 20 L (SIL-1)", "anforderungen": [{"id": "KOMP-031-F1-A1", "parameter": "Schaltpunkt", "sollwert": "20 L, Vibration"}, {"id": "KOMP-031-F1-A2", "parameter": "SIL", "sollwert": "SIL-1"}]}], "failure_modes": [
        {"funktion_id": "KOMP-031-F1", "fehler_id": "KOMP-031-F1-FM1", "fehlermodus": "Fail-to-trip: Stoppt Pumpe nicht bei 20 L", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-031-F1-FM1-UC1", "beschreibung": "Schalter verklebt, Verkabelung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Funktionsprüfung"}], "effects": {"mensch": ("Schwere Verletzung", "Pumpe trocken, Leckage"), "umwelt": ("Betriebsbereich", "AW-200"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8: Ethanol Ex-Zone", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-031-F1", "fehler_id": "KOMP-031-F1-FM2", "fehlermodus": "Frühzeitiges Ansprechen", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-031-F1-FM2-UC1", "beschreibung": "Falsche Kalibrierung", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Prüfung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Chargenabbruch"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-031-F1", "fehler_id": "KOMP-031-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-031-F1-FM3-UC1", "beschreibung": "Leitung/Relais", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "Trockenlaufschutz ausgefallen"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    "KOMP-032": {"functions": [{"funktion_id": "KOMP-032-F1", "typ": "Hauptfunktion", "beschreibung": "Trockenlaufschutz P-202 bei 20 L (SIL-1)", "anforderungen": [{"id": "KOMP-032-F1-A1", "parameter": "Schaltpunkt", "sollwert": "20 L"}, {"id": "KOMP-032-F1-A2", "parameter": "SIL", "sollwert": "SIL-1"}]}], "failure_modes": [
        {"funktion_id": "KOMP-032-F1", "fehler_id": "KOMP-032-F1-FM1", "fehlermodus": "Fail-to-trip", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-032-F1-FM1-UC1", "beschreibung": "Schalter, Verkabelung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Funktionsprüfung"}], "effects": {"mensch": ("Schwere Verletzung", "Essigsäure Pumpe trocken"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-032-F1", "fehler_id": "KOMP-032-F1-FM2", "fehlermodus": "Frühzeitiges Ansprechen", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-032-F1-FM2-UC1", "beschreibung": "Kalibrierung", "herkunft": "Wartung", "praeventionsphase": "Wartung", "praeventionshinweis": "Prüfung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-032-F1", "fehler_id": "KOMP-032-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-032-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    # ─── KOMP-033: Auffangwanne AW-200 (500 L, Leckagesensor) ───
    "KOMP-033": {
        "functions": [{"funktion_id": "KOMP-033-F1", "typ": "Hauptfunktion", "beschreibung": "Auffängt Leckagen aus Dosierbereich (Ethanol, Essigsäure, Schwefelsäure)", "anforderungen": [{"id": "KOMP-033-F1-A1", "parameter": "Volumen", "sollwert": "500 L"}, {"id": "KOMP-033-F1-A2", "parameter": "Leckagesensor", "sollwert": "Alarm bei Leckage"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-033-F1", "fehler_id": "KOMP-033-F1-FM1", "fehlermodus": "Bedienfehler: Leckagealarm nicht richtig interpretiert", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-033-F1-FM1-UC1", "beschreibung": "Unterweisung fehlt, Fehlinterpretation", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "SOP"}], "effects": {"mensch": ("Schwere Verletzung", "Leckage eskaliert, Ex-Zone"), "umwelt": ("Betriebsbereich", "Ausbreitung"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 100.000 €", "-")}, "controls": [{"name": "Leckagesensor", "typ": "Sensor", "wirkung": "B", "beschreibung": "Alarm", "beeinflusst": "D"}], "S": 9, "O": 4, "D": 4, "begruendung_S": "S=9: Gefahrstoffe", "begruendung_O": "O=4: Human Factor", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-033-F1", "fehler_id": "KOMP-033-F1-FM2", "fehlermodus": "Kennzeichnungsfehler: Verwechslung mit anderer Wanne", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-033-F1-FM2-UC1", "beschreibung": "Schlechte Beschriftung", "herkunft": "Design", "praeventionsphase": "Detaildesign", "praeventionshinweis": "Begehung"}], "effects": {"mensch": ("Schwere Verletzung", "Falsche Wanne geleert"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 9, "O": 3, "D": 5, "begruendung_S": "S=9", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-033-F1", "fehler_id": "KOMP-033-F1-FM3", "fehlermodus": "Wannendichtheit versagt: Leckage aus Auffangwanne", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-033-F1-FM3-UC1", "beschreibung": "Riss, Korrosion", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Lebensgefahr", "Gefahrstoffe in Boden/Abwasser"), "umwelt": ("Umwelt", "Kontamination"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "Leckagesensor", "typ": "Sensor", "wirkung": "B", "beschreibung": "Erkennt Leckage", "beeinflusst": "D"}], "S": 9, "O": 3, "D": 4, "begruendung_S": "S=9: Sekundärleckage", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-034: Mediensystem MS-300 (System) ───
    "KOMP-034": {
        "functions": [{"funktion_id": "KOMP-034-F1", "typ": "Hauptfunktion", "beschreibung": "Zentrale Medienversorgung für Synthesereaktor R-101 (Dampf, Kühlwasser, Notkühlung, Vakuum, Stickstoff)", "anforderungen": [{"id": "KOMP-034-F1-A1", "parameter": "Verfügbarkeit", "sollwert": "Kontinuierlich"}, {"id": "KOMP-034-F1-A2", "parameter": "Koordination", "sollwert": "PI/TI Überwachung"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-034-F1", "fehler_id": "KOMP-034-F1-FM1", "fehlermodus": "Verkettung: Mehrere Medienausfälle gleichzeitig", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-034-F1-FM1-UC1", "beschreibung": "Stromausfall, Wartungsfehler, externe Versorgung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Redundanz prüfen"}], "effects": {"mensch": ("Schwere Verletzung", "Reaktor ohne Kühlung"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Runaway möglich"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 4, "D": 5, "begruendung_S": "S=9: Runaway", "begruendung_O": "O=4: Selten", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-035: Dampfversorgung DV-301 (6 bar, 160 °C, 500 kg/h) ───
    "KOMP-035": {
        "functions": [{"funktion_id": "KOMP-035-F1", "typ": "Hauptfunktion", "beschreibung": "Liefert Sattdampf (6 bar, 160 °C) an Dampfverteiler DV-302", "anforderungen": [{"id": "KOMP-035-F1-A1", "parameter": "Druck", "sollwert": "6 bar"}, {"id": "KOMP-035-F1-A2", "parameter": "Durchsatz", "sollwert": "Max 500 kg/h"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-035-F1", "fehler_id": "KOMP-035-F1-FM1", "fehlermodus": "Druckverlust: Dampfversorgung fällt aus oder reduziert", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-035-F1-FM1-UC1", "beschreibung": "Dampfkessel, Leitung, Absperrung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "PI-301 Überwachung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Reaktion verlangsamt"), "kosten": ("Bis 50.000 €", "-")}, "controls": [{"name": "PI-301", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druckanzeige Dampfeingang", "beeinflusst": "D"}], "S": 6, "O": 3, "D": 4, "begruendung_S": "S=6", "begruendung_O": "O=3", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-035-F1", "fehler_id": "KOMP-035-F1-FM2", "fehlermodus": "Leckage: Dampfaustritt an Leitung oder Flansch", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-035-F1-FM2-UC1", "beschreibung": "Korrosion, Dichtung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Schwere Verletzung", "Verbrennung"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 7, "O": 3, "D": 5, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-036: Dampfverteiler DV-302 (4× DN25, Kondensatableiter) ───
    "KOMP-036": {
        "functions": [{"funktion_id": "KOMP-036-F1", "typ": "Hauptfunktion", "beschreibung": "Verteilt Sattdampf an Heizmantel und weitere Verbraucher", "anforderungen": [{"id": "KOMP-036-F1-A1", "parameter": "Druck", "sollwert": "6 bar"}, {"id": "KOMP-036-F1-A2", "parameter": "Kondensatablauf", "sollwert": "Thermodynamische Traps"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-036-F1", "fehler_id": "KOMP-036-F1-FM1", "fehlermodus": "Kondensatstau: Traps verstopft, schlechte Wärmeübertragung", "fehlerart": "Thermisch", "causes": [{"ursache_id": "KOMP-036-F1-FM1-UC1", "beschreibung": "Trap defekt, Verschmutzung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Trap-Inspektion"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Heizleistung reduziert"), "kosten": ("Bis 30.000 €", "-")}, "controls": [], "S": 6, "O": 3, "D": 4, "begruendung_S": "S=6", "begruendung_O": "O=3", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-036-F1", "fehler_id": "KOMP-036-F1-FM2", "fehlermodus": "Leckage am Verteiler: Dampf-/Kondensataustritt", "fehlerart": "Thermisch", "causes": [{"ursache_id": "KOMP-036-F1-FM2-UC1", "beschreibung": "Flansch, Stutzen, Korrosion", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Inspektion"}], "effects": {"mensch": ("Schwere Verletzung", "Verbrennung"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 7, "O": 3, "D": 5, "begruendung_S": "S=7", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-037: Kühlwasserversorgung KW-301 (15–25 °C, 3 bar, 10 m³/h) ───
    "KOMP-037": {
        "functions": [{"funktion_id": "KOMP-037-F1", "typ": "Hauptfunktion", "beschreibung": "Liefert Kühlwasser (Vorlauf 15 °C, Rücklauf 25 °C) an Kühlmantel und Kondensatoren", "anforderungen": [{"id": "KOMP-037-F1-A1", "parameter": "Durchfluss", "sollwert": "Max 10 m³/h"}, {"id": "KOMP-037-F1-A2", "parameter": "Druck", "sollwert": "3 bar"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-037-F1", "fehler_id": "KOMP-037-F1-FM1", "fehlermodus": "Durchflussausfall: Kühlwasser fehlt oder stark reduziert", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-037-F1-FM1-UC1", "beschreibung": "Pumpe, Leitung, Verstopfung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "PI-302, TI-302/303"}], "effects": {"mensch": ("Schwere Verletzung", "Reaktor Runaway ohne Kühlung"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Exothermie"), "kosten": ("Bis 500.000 €", "-")}, "controls": [{"name": "PI-302", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druck Kühlwasser", "beeinflusst": "D"}, {"name": "TI-302/303", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vor-/Rücklauf", "beeinflusst": "D"}], "S": 9, "O": 3, "D": 3, "begruendung_S": "S=9: Runaway", "begruendung_O": "O=3", "begruendung_D": "D=3"},
            {"funktion_id": "KOMP-037-F1", "fehler_id": "KOMP-037-F1-FM2", "fehlermodus": "Temperatur zu hoch: Kühlleistung unzureichend", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-037-F1-FM2-UC1", "beschreibung": "Kältezentrale, Rücklauftemperatur", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "TI-302/303"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Reaktion verlangsamt"), "kosten": ("Bis 30.000 €", "-")}, "controls": [], "S": 6, "O": 3, "D": 4, "begruendung_S": "S=6", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-038: Notkühlsystem NK-301 (Sole -10 °C, Ethylenglykol 30 %) ───
    "KOMP-038": {
        "functions": [{"funktion_id": "KOMP-038-F1", "typ": "Hauptfunktion", "beschreibung": "Backup-Kühlung bei Ausfall KW-301 (Sole -10 °C, 5 m³/h)", "anforderungen": [{"id": "KOMP-038-F1-A1", "parameter": "Durchfluss", "sollwert": "5 m³/h"}, {"id": "KOMP-038-F1-A2", "parameter": "Temperatur", "sollwert": "-10 °C"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-038-F1", "fehler_id": "KOMP-038-F1-FM1", "fehlermodus": "Soleausfall: Notkühlung liefert nicht bei Bedarf", "fehlerart": "Thermisch", "causes": [{"ursache_id": "KOMP-038-F1-FM1-UC1", "beschreibung": "Pumpe, Solekreislauf, Vereisung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Funktionsprüfung"}], "effects": {"mensch": ("Schwere Verletzung", "Kein Backup bei KW-Ausfall"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Totalausfall", "Runaway wenn KW ausfällt"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 9, "O": 4, "D": 5, "begruendung_S": "S=9", "begruendung_O": "O=4", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-038-F1", "fehler_id": "KOMP-038-F1-FM2", "fehlermodus": "Sole-Temperatur zu hoch: Kühlleistung reduziert", "fehlerart": "Thermisch", "causes": [{"ursache_id": "KOMP-038-F1-FM2-UC1", "beschreibung": "Kälteanlage, Glykolgehalt", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Temperaturüberwachung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Backup schwächer"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 6, "O": 3, "D": 4, "begruendung_S": "S=6", "begruendung_O": "O=3", "begruendung_D": "D=4"},
        ],
    },
    # ─── KOMP-039: Vakuumpumpe VP-301 (Flüssigkeitsring, 0.1 bar abs, 100 m³/h) ───
    "KOMP-039": {
        "functions": [{"funktion_id": "KOMP-039-F1", "typ": "Hauptfunktion", "beschreibung": "Erzeugt Vakuum (0.1 bar abs) für Destillationskolonne und Vakuumnetz", "anforderungen": [{"id": "KOMP-039-F1-A1", "parameter": "Enddruck", "sollwert": "0.1 bar abs"}, {"id": "KOMP-039-F1-A2", "parameter": "Saugleistung", "sollwert": "100 m³/h"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-039-F1", "fehler_id": "KOMP-039-F1-FM1", "fehlermodus": "Pumpenausfall: Vakuum bricht zusammen", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-039-F1-FM1-UC1", "beschreibung": "Motor, Lager, Sperrflüssigkeit", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Ölwechsel 3000 h, PI-304"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Destillation gestört"), "kosten": ("Bis 50.000 €", "-")}, "controls": [{"name": "PI-304", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vakuumanzeige", "beeinflusst": "D"}], "S": 6, "O": 3, "D": 4, "begruendung_S": "S=6", "begruendung_O": "O=3", "begruendung_D": "D=4"},
            {"funktion_id": "KOMP-039-F1", "fehler_id": "KOMP-039-F1-FM2", "fehlermodus": "Sperrflüssigkeit verbraucht: Pumpe trocken, Schaden", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-039-F1-FM2-UC1", "beschreibung": "Leckage, Nachspeisung fehlt", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Füllstand prüfen"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Pumpenschaden"), "kosten": ("Bis 30.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-040: Stickstoffversorgung N2-301 (5 bar, 99.9 %, 50 Nm³/h) ───
    "KOMP-040": {
        "functions": [{"funktion_id": "KOMP-040-F1", "typ": "Hauptfunktion", "beschreibung": "Liefert Inertgas (5 bar, 99.9 %) für Spülung und Inertisierung", "anforderungen": [{"id": "KOMP-040-F1-A1", "parameter": "Druck", "sollwert": "5 bar"}, {"id": "KOMP-040-F1-A2", "parameter": "Reinheit", "sollwert": "99.9 %"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-040-F1", "fehler_id": "KOMP-040-F1-FM1", "fehlermodus": "Druckverlust: Stickstoffversorgung fällt aus", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-040-F1-FM1-UC1", "beschreibung": "Tank leer, Leitung, Absperrung", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Tanküberwachung"}], "effects": {"mensch": ("Schwere Verletzung", "Ex-Zone ohne Inertisierung"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "Explosionsgefahr erhöht"), "kosten": ("Bis 100.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8: Ex-Zone", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-040-F1", "fehler_id": "KOMP-040-F1-FM2", "fehlermodus": "Verunreinigung: Sauerstoffgehalt zu hoch", "fehlerart": "Prozess", "causes": [{"ursache_id": "KOMP-040-F1-FM2-UC1", "beschreibung": "Tank, Leitung, falsches Medium", "herkunft": "Betrieb", "praeventionsphase": "Betrieb", "praeventionshinweis": "Zertifikat prüfen"}], "effects": {"mensch": ("Schwere Verletzung", "Inertisierung unwirksam"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "Explosionsgefahr"), "kosten": ("Bis 100.000 €", "-")}, "controls": [], "S": 8, "O": 4, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=4", "begruendung_D": "D=5"},
        ],
    },
    # ─── KOMP-041 bis KOMP-045: PI-301, TI-301, PI-302, TI-302, TI-303 (MSR Mediensystem) ───
    "KOMP-041": {"functions": [{"funktion_id": "KOMP-041-F1", "typ": "Hauptfunktion", "beschreibung": "Druckanzeige Dampfeingang (0–10 bar)", "anforderungen": [{"id": "KOMP-041-F1-A1", "parameter": "Messbereich", "sollwert": "0–10 bar"}]}], "failure_modes": [
        {"funktion_id": "KOMP-041-F1", "fehler_id": "KOMP-041-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-041-F1-FM1-UC1", "beschreibung": "Sensor, Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Schwere Verletzung", "Falsche Anzeige Dampfdruck"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-041-F1", "fehler_id": "KOMP-041-F1-FM2", "fehlermodus": "Drift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-041-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-041-F1", "fehler_id": "KOMP-041-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-041-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    "KOMP-042": {"functions": [{"funktion_id": "KOMP-042-F1", "typ": "Hauptfunktion", "beschreibung": "Temperaturanzeige Dampfeingang (0–200 °C)", "anforderungen": [{"id": "KOMP-042-F1-A1", "parameter": "Messbereich", "sollwert": "0–200 °C"}]}], "failure_modes": [
        {"funktion_id": "KOMP-042-F1", "fehler_id": "KOMP-042-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-042-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Schwere Verletzung", "Falsche Anzeige Dampftemperatur"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-042-F1", "fehler_id": "KOMP-042-F1-FM2", "fehlermodus": "Drift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-042-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-042-F1", "fehler_id": "KOMP-042-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-042-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    "KOMP-043": {"functions": [{"funktion_id": "KOMP-043-F1", "typ": "Hauptfunktion", "beschreibung": "Druckanzeige Kühlwasser (0–6 bar)", "anforderungen": [{"id": "KOMP-043-F1-A1", "parameter": "Messbereich", "sollwert": "0–6 bar"}]}], "failure_modes": [
        {"funktion_id": "KOMP-043-F1", "fehler_id": "KOMP-043-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-043-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Schwere Verletzung", "Falsche Anzeige KW-Druck, Runaway-Risiko"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 9, "O": 3, "D": 5, "begruendung_S": "S=9", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-043-F1", "fehler_id": "KOMP-043-F1-FM2", "fehlermodus": "Drift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-043-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-043-F1", "fehler_id": "KOMP-043-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-043-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 9, "O": 2, "D": 5, "begruendung_S": "S=9", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    "KOMP-044": {"functions": [{"funktion_id": "KOMP-044-F1", "typ": "Hauptfunktion", "beschreibung": "Temperaturanzeige Kühlwasser Vorlauf (0–50 °C)", "anforderungen": [{"id": "KOMP-044-F1-A1", "parameter": "Messbereich", "sollwert": "0–50 °C"}]}], "failure_modes": [
        {"funktion_id": "KOMP-044-F1", "fehler_id": "KOMP-044-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-044-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Schwere Verletzung", "Falsche Anzeige KW-Temp"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-044-F1", "fehler_id": "KOMP-044-F1-FM2", "fehlermodus": "Drift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-044-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-044-F1", "fehler_id": "KOMP-044-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-044-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    "KOMP-045": {"functions": [{"funktion_id": "KOMP-045-F1", "typ": "Hauptfunktion", "beschreibung": "Temperaturanzeige Kühlwasser Rücklauf (0–50 °C)", "anforderungen": [{"id": "KOMP-045-F1-A1", "parameter": "Messbereich", "sollwert": "0–50 °C"}]}], "failure_modes": [
        {"funktion_id": "KOMP-045-F1", "fehler_id": "KOMP-045-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-045-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Schwere Verletzung", "Falsche Anzeige KW-Rücklauf"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 3, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-045-F1", "fehler_id": "KOMP-045-F1-FM2", "fehlermodus": "Drift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-045-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-045-F1", "fehler_id": "KOMP-045-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-045-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Schwere Verletzung", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 50.000 €", "-")}, "controls": [], "S": 8, "O": 2, "D": 5, "begruendung_S": "S=8", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    # ─── KOMP-046: PI-304 Vakuumanzeige ───
    "KOMP-046": {"functions": [{"funktion_id": "KOMP-046-F1", "typ": "Hauptfunktion", "beschreibung": "Vakuumanzeige Vakuumnetz (0–1 bar abs)", "anforderungen": [{"id": "KOMP-046-F1-A1", "parameter": "Messbereich", "sollwert": "0–1 bar abs"}]}], "failure_modes": [
        {"funktion_id": "KOMP-046-F1", "fehler_id": "KOMP-046-F1-FM1", "fehlermodus": "Frozen Value", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-046-F1-FM1-UC1", "beschreibung": "Sensor", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "Destillation gestört"), "kosten": ("Bis 30.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-046-F1", "fehler_id": "KOMP-046-F1-FM2", "fehlermodus": "Drift", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-046-F1-FM2-UC1", "beschreibung": "Alterung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Kalibrierung"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 20.000 €", "-")}, "controls": [], "S": 5, "O": 3, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=3", "begruendung_D": "D=5"},
        {"funktion_id": "KOMP-046-F1", "fehler_id": "KOMP-046-F1-FM3", "fehlermodus": "Signalausfall", "fehlerart": "MSR", "causes": [{"ursache_id": "KOMP-046-F1-FM3-UC1", "beschreibung": "Leitung", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Wiring"}], "effects": {"mensch": ("Keine", "-"), "umwelt": ("Keine", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 30.000 €", "-")}, "controls": [], "S": 5, "O": 2, "D": 5, "begruendung_S": "S=5", "begruendung_O": "O=2", "begruendung_D": "D=5"},
    ]},
    # ─── KOMP-047: PSV-310 Sicherheitsventil Dampfverteiler (7 bar, DN25) ───
    "KOMP-047": {
        "functions": [{"funktion_id": "KOMP-047-F1", "typ": "Hauptfunktion", "beschreibung": "Schützt Dampfverteiler vor Überdruck (Ansprechdruck 7 bar)", "anforderungen": [{"id": "KOMP-047-F1-A1", "parameter": "Ansprechdruck", "sollwert": "7 bar"}, {"id": "KOMP-047-F1-A2", "parameter": "Nenndurchmesser", "sollwert": "DN25"}]}],
        "failure_modes": [
            {"funktion_id": "KOMP-047-F1", "fehler_id": "KOMP-047-F1-FM1", "fehlermodus": "Nicht öffnen bei Überdruck", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-047-F1-FM1-UC1", "beschreibung": "Verklebung, Korrosion, Fremdkörper", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Jährliche Prüfung"}], "effects": {"mensch": ("Lebensgefahr", "Bersten Dampfverteiler"), "umwelt": ("Betriebsbereich", "Dampfstrahl"), "anlage": ("Totalausfall", "-"), "kosten": ("Bis 500.000 €", "-")}, "controls": [], "S": 10, "O": 3, "D": 5, "begruendung_S": "S=10: Druckbehälter", "begruendung_O": "O=3", "begruendung_D": "D=5"},
            {"funktion_id": "KOMP-047-F1", "fehler_id": "KOMP-047-F1-FM2", "fehlermodus": "Erosion/Kavitation am Sitz", "fehlerart": "Sicherheit", "causes": [{"ursache_id": "KOMP-047-F1-FM2-UC1", "beschreibung": "Wiederholtes Ansprechen, Dampf", "herkunft": "Betrieb", "praeventionsphase": "Wartung", "praeventionshinweis": "Abnahme prüfen"}], "effects": {"mensch": ("Lebensgefahr", "Leckage nach Ansprechen"), "umwelt": ("Betriebsbereich", "-"), "anlage": ("Teilausfall", "-"), "kosten": ("Bis 100.000 €", "-")}, "controls": [], "S": 10, "O": 4, "D": 4, "begruendung_S": "S=10", "begruendung_O": "O=4", "begruendung_D": "D=4"},
        ],
    },
}
