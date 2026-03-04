"""
Explizite FMEA-Definitionen pro Komponente – Agent-Output.

Der Agent analysiert jede Komponente einzeln und ergänzt diese Datei.
get_fmea_for_component(komp_id) liefert die Definition für insert_fmea_for_component.
"""

def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})


# ─── KOMP-001: Synthesereaktor R-101 ───
# Edelstahl Batch-Reaktor, 500 L, Fischer-Veresterung, Ex-Zone 1.
# Ethanol, Essigsäure, Schwefelsäure, Ethylacetat.
_FMEA = {
    "KOMP-001": {
        "functions": [
            {
                "funktion_id": "KOMP-001-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Reaktionsraum bereitstellen – Containment für Ethanol, Essigsäure, Schwefelsäure (Fischer-Veresterung)",
                "anforderungen": [
                    {"id": "KOMP-001-F1-A1", "parameter": "Volumen", "sollwert": "Max 400 L Füllvolumen"},
                    {"id": "KOMP-001-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Medienfreisetzung"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F2",
                "typ": "Hauptfunktion",
                "beschreibung": "Druck- und Temperaturgrenzen einhalten (Design -0.9 bis 6 bar, -20 bis 180 °C)",
                "anforderungen": [
                    {"id": "KOMP-001-F2-A1", "parameter": "Druck", "sollwert": "-0.9 bis 6 bar"},
                    {"id": "KOMP-001-F2-A2", "parameter": "Temperatur", "sollwert": "-20 bis 180 °C"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Dichtheit gewährleisten – keine Medienfreisetzung in Ex-Zone 1",
                "anforderungen": [
                    {"id": "KOMP-001-F3-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-001-F2",
                "fehler_id": "KOMP-001-F2-FM1",
                "fehlermodus": "Runaway / Überhitzung – Unkontrollierter Temperatur- und Druckanstieg bei exothermer Reaktion",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "FM1-UC1", "beschreibung": "Kühlwasserdurchfluss fällt aus (Pumpe, Leitung)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Durchflussüberwachung"},
                    {"ursache_id": "FM1-UC2", "beschreibung": "Dampfventil klemmt offen – unkontrollierte Heizung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Stellungsprüfung"},
                    {"ursache_id": "FM1-UC3", "beschreibung": "PSV/BSV verstopft oder nicht funktionsfähig", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfintervall"},
                    {"ursache_id": "FM1-UC4", "beschreibung": "Schwefelsäure zu schnell dosiert – lokale Überhitzung", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Dosierrate"},
                    {"ursache_id": "FM1-UC5", "beschreibung": "TIC-401 (Temperaturregler) defekt oder falsch parametriert", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Verätzungs-/Verbrennungsgefahr durch heiße Essigsäure in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medien in Auffangwanne"),
                    "anlage": ("Totalausfall", "Reaktorüberhitzung, ggf. Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Temperaturanzeige und -regler, Alarm bei Überschreitung", "beeinflusst": "D"},
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druckanzeige und -regler", "beeinflusst": "D"},
                    {"name": "PSV-410", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Sicherheitsventil 6 bar", "beeinflusst": "D"},
                    {"name": "BSV-411", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Berstscheibe 6.5 bar", "beeinflusst": "D"},
                ],
                "S": 9, "O": 3, "D": 3,
                "begruendung_S": "Essigsäure in Ex-Zone 1, Verätzungs- und Brandgefahr",
                "begruendung_O": "Runaway bei Säurekatalyse möglich, aber nicht häufig",
                "begruendung_D": "TIC-401 und PIC-402 erkennen Anstieg, PSV/BSV als letzte Absicherung",
                "kontext_beschreibung": "Der Synthesereaktor führt die Fischer-Veresterung exotherm durch. Wenn Kühlung ausfällt oder die Heizung nicht abgeregelt wird, steigt Temperatur und Druck unkontrolliert. Folge: Runaway, Überdruck, mögliches Bersten in Ex-Zone 1 mit Verätzungs- und Brandgefahr.",
                "controls_einschraenkung": "TIC-401 und PIC-402 erkennen Anstieg erst bei Überschreitung. Keine direkte Durchflussüberwachung am Kühlwasser. PSV/BSV als letzte mechanische Barriere.",
            },
            {
                "funktion_id": "KOMP-001-F2",
                "fehler_id": "KOMP-001-F2-FM2",
                "fehlermodus": "Unterdruck / Vakuum – Unzulässiger Unterdruck bei Abkühlung oder fehlerhafter Vakuumführung",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "FM2-UC1", "beschreibung": "Schnelle Abkühlung nach Reaktion (Kondensatbildung)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Abkühlvorgabe"},
                    {"ursache_id": "FM2-UC2", "beschreibung": "VSV-412 (Vakuumbrecher) nicht funktionsfähig", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfintervall"},
                    {"ursache_id": "FM2-UC3", "beschreibung": "Fehlerhafte Vakuumführung bei Destillation", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Verfahrensanweisung"},
                    {"ursache_id": "FM2-UC4", "beschreibung": "PIC-402 defekt – Unterdruck wird nicht erkannt", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Implosion eher selten, Behälter ausgelegt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Behälterdeformation oder Riss"),
                    "kosten": ("Bis 50.000 €", "Reparatur, Stillstand"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druckanzeige und -regler, erkennt Unterdruck", "beeinflusst": "D"},
                    {"name": "VSV-412", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Vakuum-Sicherheitsventil, öffnet bei -0.8 bar", "beeinflusst": "O"},
                ],
                "S": 6, "O": 2, "D": 4,
                "begruendung_S": "Behälter für -0.9 bar ausgelegt, VSV-412 reduziert Risiko",
                "begruendung_O": "Unterdruck bei Batch-Reaktoren selten",
                "begruendung_D": "PIC-402 erkennt Unterdruck",
                "kontext_beschreibung": "Bei schneller Abkühlung oder fehlerhafter Vakuumführung kann Unterdruck entstehen. Folge: Behälterdeformation, Riss oder Implosion. Der Behälter ist für -0.9 bar ausgelegt.",
                "controls_einschraenkung": "PIC-402 erkennt Unterdruck. VSV-412 öffnet bei -0.8 bar. Keine Überwachung der Abkühlrate.",
            },
            {
                "funktion_id": "KOMP-001-F1",
                "fehler_id": "KOMP-001-F1-FM3",
                "fehlermodus": "Überfüllung – Füllstand über MaxFüllvolumen (400 L)",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "FM3-UC1", "beschreibung": "LIC-403 (Füllstandsmessung) fehlerhaft oder falsch kalibriert", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                    {"ursache_id": "FM3-UC2", "beschreibung": "Fehlbedienung bei Dosierung (Reihenfolge, Menge)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Verfahrensanweisung"},
                    {"ursache_id": "FM3-UC3", "beschreibung": "LSHH-403 (Überfüllsicherung) nicht funktionsfähig", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfung"},
                    {"ursache_id": "FM3-UC4", "beschreibung": "Dosierpumpe läuft weiter trotz Stopp-Signal", "herkunft": "Design", "phase": "Detaildesign", "hinweis": "SIL-Anforderung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Medienfreisetzung, Verätzungsgefahr"),
                    "umwelt": ("Betriebsbereich", "Überlauf"),
                    "anlage": ("Teilausfall", "Überdruck, Überlauf"),
                    "kosten": ("Bis 250.000 €", "Reinigung, Stillstand"),
                },
                "controls": [
                    {"name": "LIC-403", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Füllstandsanzeige und -regler", "beeinflusst": "D"},
                    {"name": "LSHH-403", "typ": "Schalter", "wirkung": "B", "sil_level": "SIL-2", "beschreibung": "Füllstandsschalter sehr hoch, Überfüllsicherung bei 480 L", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Überfüllung kann Überdruck und Personengefährdung verursachen",
                "begruendung_O": "LSHH-403 als harte Abschaltung reduziert O",
                "begruendung_D": "Ohne zweite unabhängige Füllstandsmessung bleibt D bei 4",
                "kontext_beschreibung": "Über das MaxFüllvolumen (400 L) hinausgehende Dosierung führt zu Überfüllung. Folge: Überdruck, Überlauf, Medienfreisetzung in Ex-Zone 1 mit Verätzungsgefahr.",
                "controls_einschraenkung": "LIC-403 als Regelmessung, LSHH-403 als Überfüllsicherung. Keine redundante Füllstandsmessung. LSHH-403 muss funktionsfähig sein.",
            },
            {
                "funktion_id": "KOMP-001-F1",
                "fehler_id": "KOMP-001-F1-FM4",
                "fehlermodus": "Falsche Zusammensetzung / Kontamination – Falsches Eduktverhältnis oder Rückstände aus Vorcharge",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "FM4-UC1", "beschreibung": "Falsche Dosierung (Menge, Reihenfolge)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Verfahrensanweisung"},
                    {"ursache_id": "FM4-UC2", "beschreibung": "Kontamination aus Vorcharge (Rückstände, falsches Produkt)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Chargenfreigabe"},
                    {"ursache_id": "FM4-UC3", "beschreibung": "Edukte verunreinigt (Lieferqualität)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Qualitätsprüfung"},
                    {"ursache_id": "FM4-UC4", "beschreibung": "Dosierpumpen falsch kalibriert", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Nebenreaktionen, Runaway möglich"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Vollausfall", "Chargenverlust, Qualitätsabweichung"),
                    "kosten": ("Bis 250.000 €", "Nacharbeit, Ausschuss"),
                },
                "controls": [
                    {"name": "LIC-403", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Füllstandsanzeige und -regler", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Temperaturanzeige und -regler, erkennt Anstieg", "beeinflusst": "D"},
                ],
                "S": 7, "O": 4, "D": 5,
                "begruendung_S": "Falsche Zusammensetzung kann Runaway oder Qualitätsverlust auslösen",
                "begruendung_O": "Dosierfehler kommen vor",
                "begruendung_D": "Chargenprüfung erkennt Abweichungen oft erst spät",
                "kontext_beschreibung": "Falsches Eduktverhältnis oder Kontamination aus Vorcharge führt zu Nebenreaktionen, Runaway oder Chargenverlust. Die Fischer-Veresterung ist empfindlich gegenüber Stöchiometrie und Reinheit.",
                "controls_einschraenkung": "LIC-403 und TIC-401 erkennen indirekt. Keine Inline-Qualitätsprüfung der Edukte vor Dosierung. Chargenfreigabe manuell.",
            },
            {
                "funktion_id": "KOMP-001-F2",
                "fehler_id": "KOMP-001-F2-FM5",
                "fehlermodus": "Thermische Fehlfunktion (Kälte/Schock) – Zu niedrige Temperatur oder thermischer Schock",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "FM5-UC1", "beschreibung": "Kühlwasser zu kalt (Winter, Sole-Notkühlung versehentlich aktiv)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Minimaltemperatur-Überwachung"},
                    {"ursache_id": "FM5-UC2", "beschreibung": "Essigsäure kristallisiert bei ca. 17 °C", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Temperaturführung"},
                    {"ursache_id": "FM5-UC3", "beschreibung": "Thermischer Schock – extreme Temperaturgradienten", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Langsames Abkühlen"},
                ],
                "effects": {
                    "mensch": ("Keine", "Vereisung ohne direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch, Riss, Verstopfung"),
                    "kosten": ("Bis 50.000 €", "Mantelreparatur, Stillstand"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Prozesstemperatur", "beeinflusst": "D"},
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturgradienten am Mantel", "beeinflusst": "D"},
                ],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Rohrbruch oder Riss kann zu Leckage führen",
                "begruendung_O": "Vereisung und thermischer Schock bei Batch-Reaktoren gelegentlich",
                "begruendung_D": "Keine direkte Kühlwassertemperatur-Überwachung",
                "kontext_beschreibung": "Zu kaltes Kühlwasser oder thermischer Schock kann Rohrbruch, Riss oder Verstopfung (Essigsäure kristallisiert bei ca. 17 °C) verursachen. Folge: Mantelschaden, Stillstand.",
                "controls_einschraenkung": "TIC-401 und TI-401a/b überwachen Prozesstemperatur und Mantelgradienten. Keine direkte Kühlwassertemperatur am Ein-/Auslauf. Vereisung erst bei Ausfall erkennbar.",
            },
            {
                "funktion_id": "KOMP-001-F3",
                "fehler_id": "KOMP-001-F3-FM6",
                "fehlermodus": "Undichtheit / Materialversagen – Korrosion, Riss, Flanschleckage, Erosion",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "FM6-UC1", "beschreibung": "Korrosion – Säureangriff auf Material", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "FM6-UC2", "beschreibung": "Rissbildung durch thermische Spannungen oder Materialfehler", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "FM6-UC3", "beschreibung": "Flanschleckage an Verbindungsstellen", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Flanschprüfung"},
                    {"ursache_id": "FM6-UC4", "beschreibung": "Erosion – Materialabtrag durch Strömung oder Feststoffe", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wanddickenmessung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Medienfreisetzung in Ex-Zone 1, Verätzungsgefahr"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Vollausfall", "Reaktor stilllegen, Reparatur"),
                    "kosten": ("Bis 500.000 €", "Reparatur, Reinigung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druckänderung bei größerer Leckage indirekt erkennbar", "beeinflusst": "D"},
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Regelmäßig vor Ort, erkennt Leckagen frühzeitig (Geruch, Sicht, Tropfen)", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 4,
                "begruendung_S": "Essigsäure/Schwefelsäure in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "Edelstahl 1.4571 geeignet, Leckagen selten",
                "begruendung_D": "Personal regelmäßig vor Ort, PIC-402 indirekt – keine technische Leckageüberwachung",
                "kontext_beschreibung": "Korrosion, Riss, Flanschleckage oder Erosion können zu Medienfreisetzung führen. Essigsäure, Ethanol und Schwefelsäure in Ex-Zone 1 bedeuten Verätzungs- und Brandgefahr.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung bei größerer Leckage. Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung am Mantel.",
            },
        ],
    },

    # ─── KOMP-002: Heizmantel HM-101 ───
    # Dampfmantel, 6 bar Sattdampf, Heizfläche 2.5 m², Max 160 °C.
    # Kontext: Reaktor R-101, Fischer-Veresterung, Essigsäure/Ethanol, Ex-Zone 1.
    # Controls: TIC-401 (Prozesstemperatur), TI-401a/b (Mantel Ein-/Ausgang), PIC-402 (Reaktordruck).
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
                "fehlermodus": "Dampfventil klemmt offen – Unkontrollierte Dampfzufuhr führt zu Überhitzung und Runaway-Gefahr",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM1-UC1", "beschreibung": "Ventilspindel verklebt oder Dichtung beschädigt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Regelmäßige Stellungsprüfung"},
                    {"ursache_id": "KOMP-002-F1-FM1-UC2", "beschreibung": "Stellungsregler defekt oder falsch parametriert", "herkunft": "Design", "phase": "Detaildesign", "hinweis": "SIL-Anforderung prüfen"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Verätzungs-/Verbrennungsgefahr durch heiße Essigsäure in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medien in Auffangwanne"),
                    "anlage": ("Totalausfall", "Reaktorüberhitzung, ggf. Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 (Temperaturanzeige und -regler) – Prozesstemperatur, Alarm bei Überschreitung", "beeinflusst": "D"},
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "TI-401a/b – Mantel Ein-/Ausgang, Temperaturgradient-Monitoring", "beeinflusst": "D"},
                ],
                "S": 9, "O": 2, "D": 3,
                "begruendung_S": "Runaway mit heißer Säure in Ex-Zone, Personengefährdung hoch",
                "begruendung_O": "Dampfventil selten klemmend, Stellungsüberwachung vorhanden",
                "begruendung_D": "TIC-401 und TI-401a/b erkennen Temperaturanstieg vor Runaway",
                "kontext_beschreibung": "Wenn das Dampfventil klemmt offen, strömt unkontrolliert Dampf in den Heizmantel. Folge: Überhitzung des Reaktors, Runaway-Gefahr, Bersten in Ex-Zone 1.",
                "controls_einschraenkung": "TIC-401 und TI-401a/b erkennen Temperaturanstieg. Keine Stellungsüberwachung am Dampfventil dokumentiert.",
            },
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM2",
                "fehlermodus": "Kondensat staut sich im Mantel – Schlechte Wärmeübertragung, Reaktion verlangsamt",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM2-UC1", "beschreibung": "Kondensatablauf (Trap) verstopft", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Trap-Inspektion bei Revision"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktion läuft nicht optimal, Chargenqualität"),
                    "kosten": ("Bis 10.000 €", "Chargenverlust, Nacharbeit"),
                },
                "controls": [
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "TI-401a/b – Temperaturdifferenz Ein-/Ausgang deutet auf Stau hin", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Keine Personengefährdung, Qualitäts-/Produktionsauswirkung",
                "begruendung_O": "Trap-Verstopfung gelegentlich bei Dampfsystemen",
                "begruendung_D": "Temperaturgradient-Monitoring erkennt Abweichung",
                "kontext_beschreibung": "Verstopfter Kondensatablauf (Trap) führt zu Kondensatstau im Mantel. Folge: Schlechte Wärmeübertragung, Reaktion verlangsamt, Chargenqualität beeinträchtigt.",
                "controls_einschraenkung": "TI-401a/b Temperaturdifferenz deutet auf Stau hin. Keine direkte Trap-Überwachung.",
            },
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM3",
                "fehlermodus": "Dampfdruck zu niedrig – Unzureichende Heizleistung, Reaktion verlangsamt oder blockiert",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM3-UC1", "beschreibung": "Dampfnetz-Druck fällt ab (Verbrauchsspitze, Leckage)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Dampfdruck-Überwachung"},
                    {"ursache_id": "KOMP-002-F1-FM3-UC2", "beschreibung": "Drosselventil oder Regelventil falsch eingestellt", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Einstellprotokoll"},
                    {"ursache_id": "KOMP-002-F1-FM3-UC3", "beschreibung": "Kondensatrückführung verstopft – Dampfqualität beeinträchtigt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Trap-Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenverlängerung, Qualitätsabweichung"),
                    "kosten": ("Bis 10.000 €", "Chargenverlust, Nacharbeit"),
                },
                "controls": [
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "TI-401a/b – Manteltemperatur unter Soll erkennbar", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 – Prozesstemperatur unter Soll erkennbar", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Keine Personengefährdung, Produktionsauswirkung",
                "begruendung_O": "Dampfdruck-Schwankungen gelegentlich",
                "begruendung_D": "TIC-401 und TI-401a/b erkennen Abweichung",
                "kontext_beschreibung": "Zu niedriger Dampfdruck im Mantel liefert unzureichende Heizleistung. Folge: Reaktion verlangsamt oder blockiert, Chargenverlängerung.",
                "controls_einschraenkung": "TIC-401 und TI-401a/b erkennen Temperaturabweichung. Keine direkte Dampfdruck-Überwachung am Mantel.",
            },
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM4",
                "fehlermodus": "Dampfzufuhr fällt aus – Keine Heizung, Reaktion startet nicht oder stockt",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM4-UC1", "beschreibung": "Dampfventil klemmt geschlossen oder schließt fehlerhaft", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Stellungsprüfung"},
                    {"ursache_id": "KOMP-002-F1-FM4-UC2", "beschreibung": "Dampfnetz-Abschaltung (Störung, Wartung)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Koordination mit Dampfversorgung"},
                    {"ursache_id": "KOMP-002-F1-FM4-UC3", "beschreibung": "Leitung oder Armatur blockiert (Fremdkörper, Vereisung)", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktion stockt, Charge nicht fertig"),
                    "kosten": ("Bis 50.000 €", "Chargenverlust, Stillstand"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 – Temperaturanstieg fehlt erkennbar", "beeinflusst": "D"},
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "TI-401a/b – Manteltemperatur fehlt erkennbar", "beeinflusst": "D"},
                ],
                "S": 6, "O": 2, "D": 3,
                "begruendung_S": "Chargenverlust, kein Runaway – geringere Bedeutung als Überhitzung",
                "kontext_beschreibung": "Wenn das Dampfventil klemmt geschlossen oder Dampf ausfällt, fehlt Heizung. Folge: Reaktion startet nicht oder stockt, Chargenverlust.",
                "controls_einschraenkung": "TIC-401 und TI-401a/b erkennen fehlenden Temperaturanstieg. Keine Stellungsüberwachung am Dampfventil.",
                "begruendung_O": "Vollständiger Dampfausfall selten",
                "begruendung_D": "TIC-401 und TI-401a/b erkennen fehlende Heizung schnell",
            },
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM5",
                "fehlermodus": "Dampfdruck zu hoch – Überdruck im Mantel, thermische Überlastung, Materialbeanspruchung",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-002-F1-FM5-UC1", "beschreibung": "Dampfnetz-Druck über Nennwert (6 bar) – Regelventil öffnet zu weit", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Dampfdruck-Überwachung am Mantel"},
                    {"ursache_id": "KOMP-002-F1-FM5-UC2", "beschreibung": "Druckregler am Dampfmantel defekt oder falsch parametriert", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-002-F1-FM5-UC3", "beschreibung": "Kondensatablauf blockiert – Druckaufbau im Mantel", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Trap-Inspektion"},
                    {"ursache_id": "KOMP-002-F1-FM5-UC4", "beschreibung": "Falsche Dampfquelle angeschlossen (Hochdruck statt Niederdruck)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Kennzeichnung, Freigabeprotokoll"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Bersten des Mantels, Dampf-/Medienfreisetzung in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Vollausfall", "Mantel beschädigt, Reaktor stilllegen"),
                    "kosten": ("Bis 250.000 €", "Reparatur, Stillstand, Charge"),
                },
                "controls": [
                    {"name": "TI-401a/b", "typ": "Sensor", "wirkung": "B", "beschreibung": "TI-401a/b – Überhöhte Manteltemperatur deutet auf Überdruck hin", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 – Prozesstemperatur steigt bei Überhitzung", "beeinflusst": "D"},
                    {"name": "PSV-410", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "PSV-410 – Sicherheitsventil Reaktor 6 bar, begrenzt indirekt Druckkette", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 4,
                "begruendung_S": "Bersten möglich, Medienfreisetzung in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "Dampfdruck-Überschreitung selten bei ordnungsgemäßer Auslegung",
                "begruendung_D": "Keine direkte Manteldruck-Überwachung, TI-401a/b indirekt",
                "kontext_beschreibung": "Überdruck im Dampfmantel über 6 bar kann zu Bersten führen. Folge: Dampf- und Medienfreisetzung in Ex-Zone 1, Verätzungsgefahr.",
                "controls_einschraenkung": "TI-401a/b und TIC-401 erkennen Überhitzung indirekt. Keine direkte Drucküberwachung am Mantel. PSV-410 begrenzt Reaktor, nicht Mantel.",
            },
            {
                "funktion_id": "KOMP-002-F2",
                "fehler_id": "KOMP-002-F2-FM6",
                "fehlermodus": "Undichtheit / Materialversagen – Rohrleckage: Dampf dringt in Prozess oder Prozess in Mantel",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-002-F2-FM6-UC1", "beschreibung": "Korrosion oder Rissbildung an Mantelrohr", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-002-F2-FM6-UC2", "beschreibung": "Thermische Spannungen durch Temperaturgradienten", "herkunft": "Design", "phase": "Detaildesign", "hinweis": "Berechnung thermischer Spannungen"},
                    {"ursache_id": "KOMP-002-F2-FM6-UC3", "beschreibung": "Erosion – Materialabtrag durch Kondensatströmung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wanddickenmessung"},
                    {"ursache_id": "KOMP-002-F2-FM6-UC4", "beschreibung": "Materialermüdung durch zyklische Druck-/Temperaturbelastung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Dampf/Prozess-Freisetzung, Verätzungsgefahr in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Vollausfall", "Reaktor stilllegen, Leckage beheben"),
                    "kosten": ("Bis 250.000 €", "Reparatur, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 (Druckanzeige und -regler) – Druckänderung bei größerer Leckage indirekt erkennbar", "beeinflusst": "D"},
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Regelmäßig vor Ort, erkennt Leckagen frühzeitig (Geruch, Sicht, Tropfen)", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "Medienfreisetzung in Ex-Zone, Verätzungsgefahr Essigsäure/Schwefelsäure",
                "begruendung_O": "Mantelleckage bei Druckbehältern selten",
                "begruendung_D": "Keine direkte Leckageüberwachung am Mantel",
                "kontext_beschreibung": "Rohrleckage im Heizmantel: Dampf dringt in Prozess oder Prozess in Mantel. Folge: Medienfreisetzung in Ex-Zone 1, Verätzungsgefahr.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung bei größerer Leckage. Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung am Mantel.",
            },
        ],
    },

    # ─── KOMP-003: Kühlmantel KM-101 ───
    # Kühlwassermantel, 500 L/h, Kühlfläche 2.5 m², Min 10 °C, Notkühlung Sole -10 °C.
    # Kontext: Reaktor R-101, Fischer-Veresterung, Essigsäure/Ethanol, Ex-Zone 1.
    # Controls: TIC-401 (Prozesstemperatur), PIC-402 (Reaktordruck).
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
                "fehlermodus": "Kühlwasserdurchfluss fällt aus oder zu niedrig – Keine/unzureichende Wärmeabfuhr, Runaway-Gefahr bei exothermer Reaktion",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-003-F1-FM1-UC1", "beschreibung": "Kühlwasserpumpe ausgefallen oder Leitung verstopft", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Durchflussüberwachung"},
                    {"ursache_id": "KOMP-003-F1-FM1-UC2", "beschreibung": "Ventil am Kühlwassereinlauf geschlossen oder fehlbedient", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Stellungsüberwachung"},
                    {"ursache_id": "KOMP-003-F1-FM1-UC3", "beschreibung": "Durchfluss reduziert durch Verstopfung oder Leckage", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "FI am Kühlwasser"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Runaway mit heißer Essigsäure in Ex-Zone 1, Verätzungs-/Verbrennungsgefahr"),
                    "umwelt": ("Betriebsbereich", "Medien in Auffangwanne"),
                    "anlage": ("Totalausfall", "Reaktorüberhitzung, ggf. Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 (Temperaturanzeige und -regler) – Prozesstemperatur, Alarm bei Überschreitung", "beeinflusst": "D"},
                ],
                "S": 9, "O": 2, "D": 4,
                "begruendung_S": "Runaway mit heißer Säure in Ex-Zone, Personengefährdung hoch",
                "begruendung_O": "Kühlwasserdurchfluss-Ausfall selten, TIC-401 vorhanden",
                "begruendung_D": "TIC-401 erkennt Temperaturanstieg, aber kein direkter Durchfluss-Sensor",
                "kontext_beschreibung": "Der Kühlmantel führt Wärme ab. Wenn Kühlwasserdurchfluss ausfällt oder zu niedrig ist, steigt die Reaktortemperatur unkontrolliert. Folge: Runaway in Ex-Zone 1.",
                "controls_einschraenkung": "TIC-401 erkennt Temperaturanstieg. Keine direkte Durchflussüberwachung am Kühlwasser. PIC-402 reagiert erst auf Druckänderung.",
            },
            {
                "funktion_id": "KOMP-003-F1",
                "fehler_id": "KOMP-003-F1-FM2",
                "fehlermodus": "Kühlwassertemperatur zu niedrig – Vereisung im Mantel, Rohrbruch möglich",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-003-F1-FM2-UC1", "beschreibung": "Kühlwasser zu kalt (Winterbetrieb, Sole-Notkühlung versehentlich aktiv)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Minimaltemperatur-Überwachung Rücklauf"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung bei Vereisung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch durch Eisbildung, Leckage"),
                    "kosten": ("Bis 50.000 €", "Mantelreparatur, Stillstand"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "TIC-401 – Prozesstemperatur indirekt, Vereisung erst bei Ausfall erkennbar", "beeinflusst": "D"},
                ],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Rohrbruch kann zu Leckage führen, Ex-Zone",
                "begruendung_O": "Vereisung bei Kühlwassersystemen gelegentlich",
                "begruendung_D": "Keine direkte Kühlwassertemperatur-Überwachung am Ein-/Auslauf",
                "kontext_beschreibung": "Zu kaltes Kühlwasser (Winter, Sole-Notkühlung) kann Vereisung im Mantel verursachen. Folge: Rohrbruch, Leckage, Medienfreisetzung in Ex-Zone.",
                "controls_einschraenkung": "TIC-401 überwacht Prozesstemperatur. Keine Kühlwassertemperatur-Überwachung am Ein-/Auslauf. Vereisung erst bei Ausfall erkennbar.",
            },
            {
                "funktion_id": "KOMP-003-F1",
                "fehler_id": "KOMP-003-F1-FM3",
                "fehlermodus": "Fouling oder Verstopfung – Schlechter Wärmeübergang, Durchfluss reduziert",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-003-F1-FM3-UC1", "beschreibung": "Fouling/Belagbildung auf Kühlwasserseite", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Revisionsintervall"},
                    {"ursache_id": "KOMP-003-F1-FM3-UC2", "beschreibung": "Verstopfung in Kühlwasserleitung oder Armatur", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktion verlangsamt, Chargenqualität"),
                    "kosten": ("Bis 10.000 €", "Chargenverlust, Nacharbeit"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 – Temperaturanstieg bei schlechter Kühlung erkennbar", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Keine Personengefährdung, Qualitäts-/Produktionsauswirkung",
                "begruendung_O": "Fouling/Verstopfung gelegentlich",
                "begruendung_D": "TIC-401 erkennt Abweichung",
                "kontext_beschreibung": "Fouling oder Verstopfung reduziert Kühlleistung. Folge: Reaktion verlangsamt, Chargenqualität beeinträchtigt.",
                "controls_einschraenkung": "TIC-401 erkennt Temperaturabweichung. Keine Durchfluss- oder Δp-Überwachung am Kühlmantel.",
            },
            {
                "funktion_id": "KOMP-003-F2",
                "fehler_id": "KOMP-003-F2-FM4",
                "fehlermodus": "Rohrleckage im Kühlmantel – Kühlwasser dringt in Prozess oder Prozess in Kühlwasser",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-003-F2-FM4-UC1", "beschreibung": "Korrosion oder Rissbildung an Mantelrohr", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-003-F2-FM4-UC2", "beschreibung": "Vereisungsschaden oder thermische Spannungen", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Minimaltemperatur einhalten"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung in Ex-Zone, Verätzungsgefahr"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne, Kühlwasserkreislauf kontaminiert"),
                    "anlage": ("Vollausfall", "Reaktor stilllegen, Leckage beheben"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung, Kühlwasseraufbereitung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 (Druckanzeige und -regler) – Druckänderung bei größerer Leckage indirekt erkennbar", "beeinflusst": "D"},
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Regelmäßig vor Ort, erkennt Leckagen frühzeitig", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "Medienfreisetzung in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "Mantelleckage selten",
                "begruendung_D": "Keine direkte Leckageüberwachung am Kühlmantel",
                "kontext_beschreibung": "Rohrleckage im Kühlmantel: Kühlwasser dringt in Prozess oder Prozess in Kühlwasser. Folge: Medienfreisetzung in Ex-Zone 1, Kontamination des Kühlwasserkreislaufs.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung bei größerer Leckage. Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung am Mantel.",
            },
        ],
    },

    # ─── KOMP-004: Rührwerk RW-101 ───
    # Ankerrührer, 10–200 U/min, 5 kW, ATEX Zone 1, Wellendurchmesser 60 mm.
    # Kontext: Reaktor R-101, Fischer-Veresterung, Essigsäure/Ethanol, Ex-Zone 1.
    # Controls: LIC-403 (Füllstand), SIC-404 (Drehzahl), TIC-401 (Temperatur).
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
                "fehlermodus": "Rührwerk fällt aus – Keine Durchmischung, Hotspots, unvollständige Reaktion, Runaway-Gefahr",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-004-F1-FM1-UC1", "beschreibung": "Lagerausfall durch Verschleiß oder Überlastung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-004-F1-FM1-UC2", "beschreibung": "Antriebsausfall (Motor, Frequenzumrichter)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "SIC-404 Überwachung"},
                    {"ursache_id": "KOMP-004-F1-FM1-UC3", "beschreibung": "Abrasion am Rührerblatt durch Feststoffe", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Feststoffgehalt begrenzen"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Runaway durch fehlende Durchmischung – heiße Säure in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand, Chargenverlust, ggf. Reaktorüberhitzung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "SIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "SIC-404 (Speed Indicator Controller) – Drehzahlüberwachung, erkennt Stillstand", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "TIC-401 – Temperaturanstieg bei fehlender Durchmischung indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 3,
                "begruendung_S": "Runaway-Gefahr bei fehlender Durchmischung, Ex-Zone",
                "begruendung_O": "Lager-/Rührwerkausfall bei Batch-Betrieb gelegentlich",
                "begruendung_D": "SIC-404 und TIC-401 erkennen Ausfall bzw. Temperaturanstieg",
                "kontext_beschreibung": "Ohne Rührwerk keine Durchmischung. Folge: Hotspots, unvollständige Reaktion, Runaway mit heißer Essigsäure in Ex-Zone 1.",
                "controls_einschraenkung": "SIC-404 erkennt Stillstand. TIC-401 erkennt Temperaturanstieg indirekt. Keine direkte Überwachung der Durchmischungsqualität.",
            },
            {
                "funktion_id": "KOMP-004-F1",
                "fehler_id": "KOMP-004-F1-FM2",
                "fehlermodus": "Kavitation – Rührer läuft bei zu niedrigem Füllstand oder zu hoher Drehzahl trocken",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-004-F1-FM2-UC1", "beschreibung": "Füllstand unter Mindesthöhe (LIC-403 fehlt oder falsch parametriert)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "LSLL Trockenlaufschutz"},
                    {"ursache_id": "KOMP-004-F1-FM2-UC2", "beschreibung": "Drehzahl zu hoch bei niedrigem Füllstand", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Drehzahlbegrenzung SIC-404"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Lager- und Dichtungsschaden, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Rührwerkreparatur"),
                },
                "controls": [
                    {"name": "LIC-403", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "LIC-403 (Level Indicator Controller) – Füllstand, LSLL für Trockenlaufschutz", "beeinflusst": "D"},
                    {"name": "SIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "SIC-404 – Drehzahlbegrenzung", "beeinflusst": "D"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "Mechanischer Schaden, indirekt Ex-Zone bei Leckage",
                "begruendung_O": "Kavitation bei Füllstandsfehlern gelegentlich",
                "begruendung_D": "LIC-403/SIC-404 vorhanden, aber keine direkte Kavitationserkennung",
                "kontext_beschreibung": "Bei zu niedrigem Füllstand oder zu hoher Drehzahl läuft der Rührer kavitationsartig. Folge: Lager- und Dichtungsschaden, Stillstand.",
                "controls_einschraenkung": "LIC-403 und SIC-404 begrenzen Füllstand und Drehzahl. Keine direkte Kavitationserkennung (z.B. Vibration).",
            },
            {
                "funktion_id": "KOMP-004-F2",
                "fehler_id": "KOMP-004-F2-FM3",
                "fehlermodus": "Wellenabdichtung undicht – Leckage an Stopfbuchse oder Gleitringdichtung",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-004-F2-FM3-UC1", "beschreibung": "Verschleiß der Dichtung durch abrasive Medien oder falsche Montage", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion bei Revision"},
                    {"ursache_id": "KOMP-004-F2-FM3-UC2", "beschreibung": "Thermische Schädigung durch Überhitzung", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Temperaturüberwachung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung Essigsäure/Ethanol in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Reaktor stilllegen, Dichtung wechseln"),
                    "kosten": ("Bis 50.000 €", "Dichtungswechsel, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Regelmäßige Sichtprüfung auf Tropfen an der Welle", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 5,
                "begruendung_S": "Essigsäure/Ethanol in Ex-Zone, Verätzungsgefahr",
                "begruendung_O": "Dichtungsausfall bei Rührwerken in Säureumgebung gelegentlich",
                "begruendung_D": "Keine kontinuierliche Leckageüberwachung, nur Sichtprüfung",
                "kontext_beschreibung": "Undichte Stopfbuchse oder Gleitringdichtung führt zu Tropfen an der Welle. Folge: Medienfreisetzung Essigsäure/Ethanol in Ex-Zone 1.",
                "controls_einschraenkung": "Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung an der Wellenabdichtung.",
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
                "fehlermodus": "Fouling/Verstopfung der Packung – Trennleistung vermindert, Produktqualität beeinträchtigt",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-005-F1-FM1-UC1", "beschreibung": "Ablagerungen durch Polymerisation oder Feststoffe", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Reinigungsspülung"},
                    {"ursache_id": "KOMP-005-F1-FM1-UC2", "beschreibung": "Falsche Betriebsparameter (Temperatur, Rücklauf)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Prozessüberwachung"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenqualität, Nacharbeit, ggf. Stillstand"),
                    "kosten": ("Bis 20.000 €", "Chargenverlust, Reinigung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druckänderung deutet auf Verstopfung hin", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Qualitätsauswirkung, keine Personengefährdung",
                "begruendung_O": "Fouling bei Destillation gelegentlich",
                "begruendung_D": "Kein kontinuierliches Δp-Monitoring vorhanden",
                "kontext_beschreibung": "Ablagerungen oder Verstopfung in der Packung reduzieren Trennleistung. Folge: Produktqualität beeinträchtigt, Chargenverlust.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung bei Verstopfung. Kein kontinuierliches Δp-Monitoring an der Kolonne.",
            },
            {
                "funktion_id": "KOMP-005-F1",
                "fehler_id": "KOMP-005-F1-FM2",
                "fehlermodus": "Überdruck in Kolonne – Kondensatorausfall oder Rücklaufunterbrechung",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-005-F1-FM2-UC1", "beschreibung": "Kondensator KD-101/102 fällt aus, Dämpfe kondensieren nicht", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Kühlwasserüberwachung"},
                    {"ursache_id": "KOMP-005-F1-FM2-UC2", "beschreibung": "Rücklaufventil blockiert, Flutungsgefahr", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Stellungsüberwachung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Überdruck kann zu Leckage/Bersten, Medien in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Kolonnen- oder Kondensatorschaden"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druck am Reaktor, Kolonne indirekt", "beeinflusst": "D"},
                    {"name": "PSV-410", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "PSV-410 – Druckbegrenzung 6 bar", "beeinflusst": "O"},
                ],
                "S": 8, "O": 2, "D": 4,
                "begruendung_S": "Überdruck mit brennbaren/ätzenden Medien in Ex-Zone",
                "begruendung_O": "PSV und Kondensator redundant",
                "begruendung_D": "PIC-402 erkennt Druckanstieg, Kolonne nicht direkt überwacht",
                "kontext_beschreibung": "Kondensatorausfall oder Rücklaufunterbrechung führt zu Überdruck in der Kolonne. Folge: Leckage, Bersten, Medienfreisetzung in Ex-Zone 1.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung am Reaktor. PSV-410 begrenzt Reaktor, nicht direkt Kolonne. Keine direkte Kolonne-Drucküberwachung.",
            },
            {
                "funktion_id": "KOMP-005-F2",
                "fehler_id": "KOMP-005-F2-FM3",
                "fehlermodus": "Leckage an Flanschen oder Stutzen – Dämpfe freigesetzt",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-005-F2-FM3-UC1", "beschreibung": "Dichtung beschädigt oder falsch montiert", "herkunft": "Wartung", "phase": "Wartung", "hinweis": "Dichtheitsprüfung bei Revision"},
                    {"ursache_id": "KOMP-005-F2-FM3-UC2", "beschreibung": "Thermische Spannungen, Flansch undicht", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Temperaturgradienten begrenzen"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ethylacetat/Essigsäure-Dämpfe in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand, Leckage beheben"),
                    "kosten": ("Bis 50.000 €", "Dichtungswechsel, Charge"),
                },
                "controls": [
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Sichtprüfung bei Begehung", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "Brennbare/ätzende Dämpfe in Ex-Zone",
                "begruendung_O": "Flanschleckage bei Edelstahl selten",
                "begruendung_D": "Keine kontinuierliche Leckageüberwachung",
                "kontext_beschreibung": "Leckage an Flanschen oder Stutzen setzt Ethylacetat-/Essigsäure-Dämpfe frei. Folge: Medienfreisetzung in Ex-Zone 1, Verätzungs- und Brandgefahr.",
                "controls_einschraenkung": "Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung an Flanschen.",
            },
        ],
    },

    # ─── KOMP-006: Kondensator KD-101 ───
    # Rohrbündel-WT, 5 m², Rohrseitig Produkt (Ethylacetat/Wasser), Mantelseitig Kühlwasser.
    # Kontext: Kolonnenkopf, Ex-Zone 1. Controls: PIC-402 (Druck).
    "KOMP-006": {
        "functions": [
            {
                "funktion_id": "KOMP-006-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Kondensiert Destillatdämpfe (Ethylacetat/Wasser) durch Kühlwasser",
                "anforderungen": [
                    {"id": "KOMP-006-F1-A1", "parameter": "Wärmeübertragung", "sollwert": "Fläche 5 m², Rohrseitig Produkt, Mantelseitig Kühlwasser"},
                    {"id": "KOMP-006-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Rohrleckage (Produkt/Kühlwasser-Trennung)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM1",
                "fehlermodus": "Kühlwasserdurchfluss fällt aus oder zu niedrig – Keine/unzureichende Kondensation, Überdruck in Kolonne",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM1-UC1", "beschreibung": "Kühlwasserpumpe ausgefallen oder Leitung verstopft", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Durchflussüberwachung"},
                    {"ursache_id": "KOMP-006-F1-FM1-UC2", "beschreibung": "Ventil am Kühlwassereinlauf geschlossen oder fehlbedient", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Stellungsüberwachung"},
                    {"ursache_id": "KOMP-006-F1-FM1-UC3", "beschreibung": "Durchfluss reduziert durch Fouling oder Leckage", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "FI am Kühlwasser"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Überdruck kann zu Leckage/Bersten, Medien in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Überdruck in Kolonne, Stillstand"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druck am Reaktor, Druckanstieg bei Kondensatorausfall erkennbar", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 4,
                "begruendung_S": "Überdruck mit Medien in Ex-Zone",
                "begruendung_O": "Kühlwasserdurchfluss-Ausfall selten",
                "begruendung_D": "PIC-402 erkennt Druckanstieg, aber kein direkter Durchfluss-Sensor",
                "kontext_beschreibung": "Ohne Kühlwasserdurchfluss kondensieren Destillatdämpfe nicht. Folge: Überdruck in Kolonne, Leckage oder Bersten, Medienfreisetzung in Ex-Zone 1.",
                "controls_einschraenkung": "PIC-402 erkennt Druckanstieg, Kolonne indirekt. Keine direkte Durchflussüberwachung am Kondensator.",
            },
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM2",
                "fehlermodus": "Fouling/Verstopfung Rohrbündel – Kondensationsleistung vermindert, Überdruck",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM2-UC1", "beschreibung": "Ablagerungen Rohrseite oder Kühlwasserseite", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Reinigung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Überdruck kann zu Leckage, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Kolonne überdruck, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Reinigung, Charge"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druckanstieg bei Kondensatorausfall indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Überdruck mit Medien in Ex-Zone",
                "begruendung_O": "Fouling bei Kondensatoren gelegentlich",
                "begruendung_D": "Drucküberwachung erkennt indirekt",
                "kontext_beschreibung": "Fouling oder Verstopfung reduziert Kondensationsleistung. Folge: Überdruck in Kolonne, Leckage, Medienfreisetzung in Ex-Zone 1.",
                "controls_einschraenkung": "PIC-402 erkennt Druckanstieg indirekt. Keine direkte Kondensationsleistungs-Überwachung.",
            },
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM3",
                "fehlermodus": "Kühlwassertemperatur zu niedrig – Vereisung im Rohrbündel, Rohrbruch",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM3-UC1", "beschreibung": "Kühlwasser zu kalt (Winterbetrieb)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Minimaltemperatur Rücklauf"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch, Leckage"),
                    "kosten": ("Bis 50.000 €", "Kondensatorreparatur"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Rohrbruch kann zu Leckage führen",
                "begruendung_O": "Vereisung gelegentlich",
                "begruendung_D": "Keine Kühlwassertemperatur-Überwachung",
                "kontext_beschreibung": "Zu kaltes Kühlwasser (Winter) kann Vereisung im Rohrbündel verursachen. Folge: Rohrbruch, Leckage, Medienfreisetzung in Ex-Zone.",
                "controls_einschraenkung": "Keine Kühlwassertemperatur-Überwachung am Ein-/Auslauf. Vereisung erst bei Ausfall erkennbar.",
            },
            {
                "funktion_id": "KOMP-006-F1",
                "fehler_id": "KOMP-006-F1-FM4",
                "fehlermodus": "Rohrleckage – Produkt in Kühlwasser oder Kühlwasser in Produkt",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-006-F1-FM4-UC1", "beschreibung": "Korrosion oder Rissbildung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "KOMP-006-F1-FM4-UC2", "beschreibung": "Vereisungsschaden oder thermische Spannungen", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Minimaltemperatur einhalten"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Kühlwasserkreislauf kontaminiert"),
                    "anlage": ("Teilausfall", "Stillstand, Reinigung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Kühlwasseraufbereitung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druckänderung bei Leckage indirekt erkennbar", "beeinflusst": "D"},
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Regelmäßig vor Ort, erkennt Leckagen frühzeitig", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "Medienfreisetzung Ex-Zone",
                "begruendung_O": "Rohrleckage selten",
                "begruendung_D": "Keine direkte Leckageüberwachung",
                "kontext_beschreibung": "Rohrleckage im Kondensator: Produkt dringt in Kühlwasser oder Kühlwasser in Produkt. Folge: Medienfreisetzung in Ex-Zone 1, Kontamination des Kühlwasserkreislaufs.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung bei größerer Leckage. Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung am Rohrbündel.",
            },
        ],
    },

    # ─── KOMP-007: Kondensator KD-102 ───
    # Rohrbündel-WT, 8 m², Rohrseitig Produkt, Mantelseitig Kühlwasser. Gleiche Funktion wie KD-101.
    "KOMP-007": {
        "functions": [
            {
                "funktion_id": "KOMP-007-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Kondensiert Destillatdämpfe (Ethylacetat/Wasser) durch Kühlwasser",
                "anforderungen": [
                    {"id": "KOMP-007-F1-A1", "parameter": "Wärmeübertragung", "sollwert": "Fläche 8 m², Rohrseitig Produkt, Mantelseitig Kühlwasser"},
                    {"id": "KOMP-007-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Rohrleckage (Produkt/Kühlwasser-Trennung)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM1",
                "fehlermodus": "Kühlwasserdurchfluss fällt aus oder zu niedrig – Keine/unzureichende Kondensation, Überdruck in Kolonne",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM1-UC1", "beschreibung": "Kühlwasserpumpe ausgefallen oder Leitung verstopft", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Durchflussüberwachung"},
                    {"ursache_id": "KOMP-007-F1-FM1-UC2", "beschreibung": "Ventil am Kühlwassereinlauf geschlossen oder fehlbedient", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Stellungsüberwachung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Überdruck kann zu Leckage/Bersten, Medien in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Überdruck in Kolonne, Stillstand"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Charge, Reinigung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druckanstieg bei Kondensatorausfall erkennbar", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 4,
                "begruendung_S": "Überdruck mit Medien in Ex-Zone",
                "begruendung_O": "Kühlwasserdurchfluss-Ausfall selten",
                "begruendung_D": "PIC-402 erkennt Druckanstieg, aber kein direkter Durchfluss-Sensor",
                "kontext_beschreibung": "Ohne Kühlwasserdurchfluss kondensieren Destillatdämpfe nicht. Folge: Überdruck in Kolonne, Leckage oder Bersten, Medienfreisetzung in Ex-Zone 1.",
                "controls_einschraenkung": "PIC-402 erkennt Druckanstieg, Kolonne indirekt. Keine direkte Durchflussüberwachung am Kondensator.",
            },
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM2",
                "fehlermodus": "Fouling/Verstopfung Rohrbündel – Kondensationsleistung vermindert",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM2-UC1", "beschreibung": "Ablagerungen Rohrseite oder Kühlwasserseite", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Reinigung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Überdruck kann zu Leckage, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Kolonne überdruck, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Reinigung, Charge"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druckanstieg indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Überdruck mit Medien in Ex-Zone",
                "begruendung_O": "Fouling bei Kondensatoren gelegentlich",
                "begruendung_D": "Drucküberwachung erkennt indirekt",
                "kontext_beschreibung": "Fouling oder Verstopfung reduziert Kondensationsleistung. Folge: Überdruck in Kolonne, Leckage, Medienfreisetzung in Ex-Zone 1.",
                "controls_einschraenkung": "PIC-402 erkennt Druckanstieg indirekt. Keine direkte Kondensationsleistungs-Überwachung.",
            },
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM3",
                "fehlermodus": "Kühlwassertemperatur zu niedrig – Vereisung im Rohrbündel, Rohrbruch",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM3-UC1", "beschreibung": "Kühlwasser zu kalt (Winterbetrieb)", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Minimaltemperatur Rücklauf"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine direkte Personengefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Rohrbruch, Leckage"),
                    "kosten": ("Bis 50.000 €", "Kondensatorreparatur"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Rohrbruch kann zu Leckage führen",
                "begruendung_O": "Vereisung gelegentlich",
                "begruendung_D": "Keine Kühlwassertemperatur-Überwachung",
                "kontext_beschreibung": "Zu kaltes Kühlwasser (Winter) kann Vereisung im Rohrbündel verursachen. Folge: Rohrbruch, Leckage, Medienfreisetzung in Ex-Zone.",
                "controls_einschraenkung": "Keine Kühlwassertemperatur-Überwachung am Ein-/Auslauf. Vereisung erst bei Ausfall erkennbar.",
            },
            {
                "funktion_id": "KOMP-007-F1",
                "fehler_id": "KOMP-007-F1-FM4",
                "fehlermodus": "Rohrleckage – Produkt in Kühlwasser oder Kühlwasser in Produkt",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-007-F1-FM4-UC1", "beschreibung": "Korrosion oder Rissbildung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Kühlwasserkreislauf kontaminiert"),
                    "anlage": ("Teilausfall", "Stillstand, Reinigung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Kühlwasseraufbereitung"),
                },
                "controls": [
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "PIC-402 – Druckänderung bei Leckage indirekt erkennbar", "beeinflusst": "D"},
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Regelmäßig vor Ort, erkennt Leckagen frühzeitig", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "Medienfreisetzung Ex-Zone",
                "begruendung_O": "Rohrleckage selten",
                "begruendung_D": "Keine direkte Leckageüberwachung",
                "kontext_beschreibung": "Rohrleckage im Kondensator: Produkt dringt in Kühlwasser oder Kühlwasser in Produkt. Folge: Medienfreisetzung in Ex-Zone 1, Kontamination des Kühlwasserkreislaufs.",
                "controls_einschraenkung": "PIC-402 erkennt Druckänderung bei größerer Leckage. Sichtprüfung bei Begehung. Keine kontinuierliche Leckageüberwachung am Rohrbündel.",
            },
        ],
    },

    # ─── KOMP-008: Destillatvorlage DV-101 ───
    # Behälter zur Aufnahme des Kondensats aus KD-101 (Kolonne K-101). Ex-Zone 1, Ethylacetat/Wasser.
    "KOMP-008": {
        "functions": [
            {
                "funktion_id": "KOMP-008-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Destillat (Ethylacetat/Wasser-Gemisch) aus Kondensator KD-101 aufnehmen und für Weiternutzung/Ablauf bereitstellen",
                "anforderungen": [
                    {"id": "KOMP-008-F1-A1", "parameter": "Fassungsvermögen", "sollwert": "Auslegung für Kondensatstrom aus KD-101"},
                    {"id": "KOMP-008-F1-A2", "parameter": "Füllstand", "sollwert": "Betrieb zwischen Min und Max, keine Überfüllung"},
                    {"id": "KOMP-008-F1-A3", "parameter": "Dichtheit", "sollwert": "Keine Medienfreisetzung in Ex-Zone 1"},
                ],
            },
            {
                "funktion_id": "KOMP-008-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Dichtheit gewährleisten – keine Leckage in Ex-Zone 1",
                "anforderungen": [
                    {"id": "KOMP-008-F2-A1", "parameter": "Integrität", "sollwert": "Behälter und Anschlüsse dicht"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-008-F1",
                "fehler_id": "KOMP-008-F1-FM1",
                "fehlermodus": "Überfüllung – Füllstand über Maximalhöhe, Überlauf",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-008-F1-FM1-UC1", "beschreibung": "LIC (Füllstandsmessung) fehlerhaft, eingefroren oder falsch kalibriert", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-008-F1-FM1-UC2", "beschreibung": "Abnahme/Weiterleitung gestoppt oder blockiert bei laufender Kondensation", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Verfahrensanweisung"},
                    {"ursache_id": "KOMP-008-F1-FM1-UC3", "beschreibung": "LSHH (Überfüllsicherung) nicht funktionsfähig oder nicht vorhanden", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfintervall"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Medienfreisetzung bei Überlauf, Verätzungsgefahr in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Überlauf in Auffangwanne, ggf. Boden"),
                    "anlage": ("Teilausfall", "Überlauf, Kontamination, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Reinigung, Stillstand, ggf. Umweltschaden"),
                },
                "controls": [
                    {"name": "LIC", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Füllstandsanzeige und -regelung, begrenzt Zufluss/Abnahme", "beeinflusst": "D"},
                    {"name": "LSHH", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Überfüllsicherung, Abschaltung bei Max-Füllstand", "beeinflusst": "O"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Medien (Ethylacetat/Essigsäure-Reste) in Ex-Zone 1, Verätzungsgefahr bei Überlauf.",
                "begruendung_O": "Überfüllung bei Fehlbedienung oder LIC-Ausfall möglich, LSHH reduziert O.",
                "begruendung_D": "LIC erkennt Füllstand; bei eingefrorenem Wert erst bei Überlauf erkennbar.",
                "kontext_beschreibung": "Die Destillatvorlage nimmt das Kondensat aus KD-101 auf. Läuft die Kondensation weiter, ohne dass Destillat abgenommen wird, steigt der Füllstand. Ohne funktionierende Füllstandsbegrenzung oder Überfüllsicherung kommt es zum Überlauf in Ex-Zone 1 mit Verätzungs- und Brandgefahr.",
                "controls_einschraenkung": "LIC kann eingefrieren (Frozen Value). LSHH muss regelmäßig geprüft werden.",
            },
            {
                "funktion_id": "KOMP-008-F1",
                "fehler_id": "KOMP-008-F1-FM2",
                "fehlermodus": "Unterdruck / Vakuum – Unzulässiger Unterdruck bei Abkühlung",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-008-F1-FM2-UC1", "beschreibung": "Schnelle Abkühlung, Kondensatbildung im Kopfraum", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Abkühlvorgabe"},
                    {"ursache_id": "KOMP-008-F1-FM2-UC2", "beschreibung": "Vakuumbrecher (falls vorhanden) nicht funktionsfähig", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfintervall"},
                    {"ursache_id": "KOMP-008-F1-FM2-UC3", "beschreibung": "Abnahme zu schnell, Behälter nicht für Vakuum ausgelegt", "herkunft": "Design", "phase": "Betrieb", "hinweis": "Betriebsgrenzen"},
                ],
                "effects": {
                    "mensch": ("Gering", "Implosion eher selten, Behälter meist ausgelegt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Behälterdeformation, Riss, Leckage"),
                    "kosten": ("Bis 50.000 €", "Reparatur, Stillstand"),
                },
                "controls": [
                    {"name": "Drucküberwachung", "typ": "Sensor", "wirkung": "B", "beschreibung": "PIC o.ä. erkennt Unterdruck, falls vorhanden", "beeinflusst": "D"},
                    {"name": "Vakuumbrecher", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Öffnet bei Unterdruck, verhindert Implosion", "beeinflusst": "O"},
                ],
                "S": 6, "O": 2, "D": 4,
                "begruendung_S": "Behälter üblicherweise für leichten Unterdruck ausgelegt; bei Implosion Verletzungsgefahr.",
                "begruendung_O": "Unterdruck bei Vorlagebehältern seltener als Überdruck.",
                "begruendung_D": "Drucküberwachung oder Vakuumbrecher-Prüfung.",
                "kontext_beschreibung": "Bei schneller Abkühlung oder zu starker Abnahme kann Unterdruck entstehen. Folge: Behälterdeformation, Riss oder Implosion. Behälter sind oft für leichten Unterdruck ausgelegt; Vakuumbrecher begrenzen das Risiko.",
                "controls_einschraenkung": "Nicht alle Vorlagen haben Drucküberwachung. Vakuumbrecher müssen funktionsfähig sein.",
            },
            {
                "funktion_id": "KOMP-008-F2",
                "fehler_id": "KOMP-008-F2-FM3",
                "fehlermodus": "Äußere Leckage – Integritätsverlust, Medienaustritt",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-008-F2-FM3-UC1", "beschreibung": "Flanschdichtung defekt oder nicht angezogen", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "KOMP-008-F2-FM3-UC2", "beschreibung": "Korrosion oder Riss am Behälter", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Druckprüfung, Inspektion"},
                    {"ursache_id": "KOMP-008-F2-FM3-UC3", "beschreibung": "Stutzen oder Armatur undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Dichtheitsprüfung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Verätzungsgefahr durch Ethylacetat/Essigsäure in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medien in Auffangwanne oder Boden"),
                    "anlage": ("Teilausfall", "Stillstand, Reinigung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Reinigung, ggf. Umweltschaden"),
                },
                "controls": [
                    {"name": "Auffangwanne", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Begrenzt Ausbreitung bei Leckage", "beeinflusst": "S"},
                    {"name": "Produktionspersonal", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Begehungen, erkennt Leckagen früh", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 5,
                "begruendung_S": "Medien in Ex-Zone 1, Verätzungs- und Brandgefahr.",
                "begruendung_O": "Leckage an Behältern gelegentlich (Dichtungen, Korrosion).",
                "begruendung_D": "Keine kontinuierliche Leckageüberwachung, Sichtprüfung bei Begehung.",
                "kontext_beschreibung": "Leckage an der Destillatvorlage führt zu Austritt von Ethylacetat/Wasser-Gemisch in Ex-Zone 1. Folge: Verätzungsgefahr, Auffangwanne wird genutzt; ohne Wanne Ausbreitung und höheres Risiko.",
                "controls_einschraenkung": "Auffangwanne begrenzt Folgen, verhindert Leckage nicht. Früherkennung durch Personal abhängig von Begehungsintervall.",
            },
            {
                "funktion_id": "KOMP-008-F1",
                "fehler_id": "KOMP-008-F1-FM4",
                "fehlermodus": "Kein Ablauf / Abnahme blockiert – Destillat staut sich, Rückwirkung auf Kolonne",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-008-F1-FM4-UC1", "beschreibung": "Pumpe oder Ablaufventil ausgefallen/geschlossen", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Durchflussüberwachung"},
                    {"ursache_id": "KOMP-008-F1-FM4-UC2", "beschreibung": "Leitung oder Filter verstopft", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Reinigung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Überfüllung möglich, dann Medienfreisetzung in Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Bei Überfüllung Überlauf"),
                    "anlage": ("Teilausfall", "Stau, Überfüllung, Druckaufbau in Kolonne, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Stillstand, Reinigung"),
                },
                "controls": [
                    {"name": "LIC", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Füllstandserkennung, Alarm bei Hochstand", "beeinflusst": "D"},
                    {"name": "LSHH", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Überfüllsicherung, Abschaltung", "beeinflusst": "O"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Stau führt zu Überfüllung, Medien in Ex-Zone 1.",
                "begruendung_O": "Ablaufausfall oder Verstopfung gelegentlich.",
                "begruendung_D": "LIC und LSHH erkennen hohen Füllstand.",
                "kontext_beschreibung": "Wenn die Abnahme aus der Destillatvorlage ausfällt oder blockiert, staut sich das Kondensat. Die Vorlage läuft über, mit Folgen für Kolonne und Ex-Zone. LIC und LSHH begrenzen das Risiko.",
                "controls_einschraenkung": "LIC kann eingefrieren; LSHH muss ansprechen.",
            },
        ],
    },

    # ─── KOMP-009: Destillatvorlage DV-102 ───
    # Zweite Destillatvorlage (z.B. zweite Kolonnenstufe oder Rücklauf). Ex-Zone 1, Ethylacetat/Wasser.
    "KOMP-009": {
        "functions": [
            {
                "funktion_id": "KOMP-009-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Destillat aus zweiter Stufe/Kondensator aufnehmen und für Ablauf/Rücklauf bereitstellen",
                "anforderungen": [
                    {"id": "KOMP-009-F1-A1", "parameter": "Fassungsvermögen", "sollwert": "Auslegung für Kondensatstrom"},
                    {"id": "KOMP-009-F1-A2", "parameter": "Füllstand", "sollwert": "Betrieb zwischen Min und Max, keine Überfüllung"},
                    {"id": "KOMP-009-F1-A3", "parameter": "Dichtheit", "sollwert": "Keine Medienfreisetzung in Ex-Zone 1"},
                ],
            },
            {
                "funktion_id": "KOMP-009-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Dichtheit gewährleisten – keine Leckage in Ex-Zone 1",
                "anforderungen": [
                    {"id": "KOMP-009-F2-A1", "parameter": "Integrität", "sollwert": "Behälter und Anschlüsse dicht"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-009-F1",
                "fehler_id": "KOMP-009-F1-FM1",
                "fehlermodus": "Überfüllung – Füllstand über Maximalhöhe, Überlauf",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-009-F1-FM1-UC1", "beschreibung": "Füllstandsmessung (LIC) fehlerhaft oder falsch kalibriert", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-009-F1-FM1-UC2", "beschreibung": "Abnahme gestoppt bei laufender Kondensation", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Verfahrensanweisung"},
                    {"ursache_id": "KOMP-009-F1-FM1-UC3", "beschreibung": "LSHH nicht funktionsfähig", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfintervall"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Medienfreisetzung bei Überlauf, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Überlauf Auffangwanne"),
                    "anlage": ("Teilausfall", "Überlauf, Stillstand"),
                    "kosten": ("Bis 50.000 €", "Reinigung, Stillstand"),
                },
                "controls": [
                    {"name": "LIC", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Füllstandsanzeige und -regelung", "beeinflusst": "D"},
                    {"name": "LSHH", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Überfüllsicherung", "beeinflusst": "O"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Medien in Ex-Zone 1, Verätzungsgefahr.",
                "begruendung_O": "Überfüllung bei Fehlbedienung oder LIC-Ausfall möglich.",
                "begruendung_D": "LIC erkennt Füllstand.",
                "kontext_beschreibung": "Zweite Destillatvorlage; Überfüllung bei Ausfall der Abnahme oder Fehlmessung – gleiche Risiken wie DV-101 in Ex-Zone 1.",
                "controls_einschraenkung": "LIC kann eingefrieren; LSHH-Prüfung erforderlich.",
            },
            {
                "funktion_id": "KOMP-009-F1",
                "fehler_id": "KOMP-009-F1-FM2",
                "fehlermodus": "Unterdruck – Behälter nicht vakuumfest belastet",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-009-F1-FM2-UC1", "beschreibung": "Schnelle Abkühlung, Kondensatbildung", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Betriebsvorgabe"},
                    {"ursache_id": "KOMP-009-F1-FM2-UC2", "beschreibung": "Vakuumbrecher nicht funktionsfähig", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Prüfung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Implosion selten"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Behälterdeformation"),
                    "kosten": ("Bis 25.000 €", "Reparatur"),
                },
                "controls": [
                    {"name": "Drucküberwachung/Vakuumbrecher", "typ": "Sensor/Sicherheit", "wirkung": "B/E", "beschreibung": "Erkennung oder Begrenzung Unterdruck", "beeinflusst": "D/O"},
                ],
                "S": 6, "O": 2, "D": 4,
                "begruendung_S": "Behälter ausgelegt, Vakuumbrecher reduziert Risiko.",
                "begruendung_O": "Unterdruck seltener.",
                "begruendung_D": "Erkennbar durch Überwachung.",
                "kontext_beschreibung": "Unterdruck bei schneller Abkühlung möglich; Behälter und Vakuumbrecher begrenzen Risiko.",
                "controls_einschraenkung": "Nicht alle Vorlagen haben Drucküberwachung.",
            },
            {
                "funktion_id": "KOMP-009-F2",
                "fehler_id": "KOMP-009-F2-FM3",
                "fehlermodus": "Äußere Leckage – Medienaustritt in Ex-Zone 1",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-009-F2-FM3-UC1", "beschreibung": "Flanschdichtung oder Stutzen undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "KOMP-009-F2-FM3-UC2", "beschreibung": "Korrosion oder Riss", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Druckprüfung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Verätzungsgefahr in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne"),
                    "anlage": ("Teilausfall", "Stillstand"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Reinigung"),
                },
                "controls": [
                    {"name": "Auffangwanne", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Begrenzt Ausbreitung", "beeinflusst": "S"},
                    {"name": "Begehungen", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Früherkennung Leckage", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 5,
                "begruendung_S": "Medien in Ex-Zone 1.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Sichtprüfung, keine kontinuierliche Überwachung.",
                "kontext_beschreibung": "Leckage an DV-102 – gleiche Bewertung wie DV-101, Medien in Ex-Zone 1.",
                "controls_einschraenkung": "Früherkennung abhängig von Begehungen.",
            },
        ],
    },

    # ─── KOMP-010: TIC-401 (Temperature Indicator Controller) ───
    # Temperaturanzeige und -regler Reaktor R-101. Misst Prozesstemperatur, regelt Heizung/Kühlung. Kritisch für Runaway-Vermeidung.
    "KOMP-010": {
        "functions": [
            {
                "funktion_id": "KOMP-010-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "TIC-401 – Prozesstemperatur im Synthesereaktor erfassen, anzeigen und regeln (Heizung/Kühlung)",
                "anforderungen": [
                    {"id": "KOMP-010-F1-A1", "parameter": "Messbereich", "sollwert": "Betriebstemperatur 80–100 °C abdeckend"},
                    {"id": "KOMP-010-F1-A2", "parameter": "Regelung", "sollwert": "Sollwertführung, Alarm bei Abweichung"},
                    {"id": "KOMP-010-F1-A3", "parameter": "Verfügbarkeit", "sollwert": "Signal für DCS und Abschaltlogik"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-010-F1",
                "fehler_id": "KOMP-010-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert (Frozen Value) – Anzeige konstant, reale Temperatur steigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-010-F1-FM1-UC1", "beschreibung": "Sensor oder Messumformer defekt, liefert konstanten Wert", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-010-F1-FM1-UC2", "beschreibung": "Impulsleitung verstopft oder abgeklemmt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "KOMP-010-F1-FM1-UC3", "beschreibung": "Bus/DCS-Kommunikation ausgefallen, letzter Wert bleibt stehen", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Redundanz"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Runaway nicht erkannt, Überdruck, Bersten, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medienfreisetzung"),
                    "anlage": ("Totalausfall", "Reaktorüberhitzung, ggf. Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge, Personenschaden"),
                },
                "controls": [
                    {"name": "TI-401a / TI-401b", "typ": "Sensor", "wirkung": "B", "beschreibung": "Redundante Temperaturmessung, Abweichungsalarm", "beeinflusst": "D"},
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1", "beschreibung": "Druckanstieg bei Runaway indirekt erkennbar", "beeinflusst": "D"},
                    {"name": "PSV-410 / BSV-411", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Letzte mechanische Absicherung", "beeinflusst": "S"},
                ],
                "S": 9, "O": 3, "D": 5,
                "begruendung_S": "Runaway in Ex-Zone 1, Verätzungs- und Brandgefahr, katastrophale Folgen.",
                "begruendung_O": "Frozen Value bei MSR gelegentlich (Sensor, Leitung, Bus).",
                "begruendung_D": "Redundante TI-401a/b und PIC-402 können Abweichung erkennen; bei allen ausgefallen sehr schlecht.",
                "kontext_beschreibung": "TIC-401 ist die zentrale Temperaturregelung des Reaktors. Zeigt der TIC einen konstanten (eingefrorenen) Wert, während die reale Temperatur steigt, reagiert die Regelung nicht – Runaway-Gefahr. Redundante Temperaturmessung und Drucküberwachung sind entscheidend.",
                "controls_einschraenkung": "TI-401a/b müssen Abweichung melden. PIC-402 erkennt Runaway erst bei Druckanstieg. PSV/BSV letzte Barriere.",
            },
            {
                "funktion_id": "KOMP-010-F1",
                "fehler_id": "KOMP-010-F1-FM2",
                "fehlermodus": "Messwertdrift – Schleichende Fehlanzeige, Regelung arbeitet mit falschem Soll",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-010-F1-FM2-UC1", "beschreibung": "Sensor altert oder verschmutzt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierintervall"},
                    {"ursache_id": "KOMP-010-F1-FM2-UC2", "beschreibung": "Falsche Kalibrierung bei Instandhaltung", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Rückführung"},
                ],
                "effects": {
                    "mensch": ("Verletzte", "Unter- oder Übertemperatur, ggf. Runaway bei Überschreitung"),
                    "umwelt": ("Betriebsbereich", "Bei Folgeschaden"),
                    "anlage": ("Teilausfall", "Falsche Reaktionsführung, Qualität oder Sicherheit"),
                    "kosten": ("Bis 250.000 €", "Charge, Reparatur"),
                },
                "controls": [
                    {"name": "Kalibrierung", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Periodische Kalibrierung mit Rückführung", "beeinflusst": "O"},
                    {"name": "TI-401a/b Abweichungsprüfung", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vergleich der Messstellen, Alarm bei Abweichung", "beeinflusst": "D"},
                ],
                "S": 7, "O": 4, "D": 5,
                "begruendung_S": "Drift kann zu Übertemperatur und Runaway führen.",
                "begruendung_O": "Drift bei Temperatursensoren im Laufe der Zeit möglich.",
                "begruendung_D": "Kalibrierung und Abweichungsprüfung erkennen Drift mit Verzögerung.",
                "kontext_beschreibung": "Schleichende Messwertdrift führt dazu, dass die Regelung mit falschem Istwert arbeitet. Folge: Untertemperatur (Qualität) oder Überschreitung (Runaway-Risiko).",
                "controls_einschraenkung": "Kalibrierung nur periodisch; Drift zwischen Terminen möglich.",
            },
            {
                "funktion_id": "KOMP-010-F1",
                "fehler_id": "KOMP-010-F1-FM3",
                "fehlermodus": "Aktor-Blockade (Stuck-at) – Stellglied (Heizung/Kühlung) reagiert nicht auf Reglerausgang",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-010-F1-FM3-UC1", "beschreibung": "Stellventil klemmt in einer Stellung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Stellungsüberwachung"},
                    {"ursache_id": "KOMP-010-F1-FM3-UC2", "beschreibung": "Stellungsrückmeldung fehlerhaft, DCS erkennt Stellung nicht", "herkunft": "Betrieb", "phase": "Inbetriebnahme", "hinweis": "Rückmeldung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Heizung klemmt auf – Runaway; Kühlung klemmt zu – Überhitzung"),
                    "umwelt": ("Betriebsbereich", "Bei Runaway"),
                    "anlage": ("Totalausfall", "Reaktor außer Kontrolle"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Charge"),
                },
                "controls": [
                    {"name": "Stellungsüberwachung", "typ": "Sensor", "wirkung": "B", "beschreibung": "Stellungsrückmeldung Ventil, Abweichungsalarm", "beeinflusst": "D"},
                    {"name": "PIC-402 / TIC-Abweichung", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druck/Temperatur zeigen Fehlstellung an", "beeinflusst": "D"},
                    {"name": "PSV-410 / BSV-411", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Letzte Absicherung", "beeinflusst": "S"},
                ],
                "S": 9, "O": 3, "D": 5,
                "begruendung_S": "Stellglied blockiert bei Runaway-Gefahr katastrophal.",
                "begruendung_O": "Ventilklemmen gelegentlich.",
                "begruendung_D": "Stellungsrückmeldung und Prozessgrößen können erkennen.",
                "kontext_beschreibung": "Wenn das Stellventil für Heizung oder Kühlung klemmt, folgt die Regelung nicht. Heizung „auf“ bei Ausfall der Kühlung oder Kühlung „zu“ – Runaway. Stellungsüberwachung und Prozessüberwachung sind erforderlich.",
                "controls_einschraenkung": "Stellungsrückmeldung kann ebenfalls fehlerhaft sein. PSV/BSV letzte Barriere.",
            },
        ],
    },

    # ─── KOMP-011: TI-401a (Temperature Indicator) ───
    # Redundante Temperaturanzeige Reaktor R-101. Nur Anzeige, keine Regelung. Dient Abweichungsprüfung zu TIC-401.
    "KOMP-011": {
        "functions": [
            {
                "funktion_id": "KOMP-011-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "TI-401a – Prozesstemperatur anzeigen, für Abweichungsprüfung zu TIC-401 (Redundanz)",
                "anforderungen": [
                    {"id": "KOMP-011-F1-A1", "parameter": "Messbereich", "sollwert": "Betriebstemperatur abdeckend"},
                    {"id": "KOMP-011-F1-A2", "parameter": "Genauigkeit", "sollwert": "Vergleichbar TIC-401 für Abweichungsalarm"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-011-F1",
                "fehler_id": "KOMP-011-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Anzeige konstant, Abweichungsalarm greift nicht",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-011-F1-FM1-UC1", "beschreibung": "Sensor oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-011-F1-FM1-UC2", "beschreibung": "Impulsleitung oder Bus defekt", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Redundanz fehlt; bei TIC-401 auch ausgefallen Runaway nicht erkennbar"),
                    "umwelt": ("Betriebsbereich", "Bei Runaway"),
                    "anlage": ("Teilausfall", "Redundanz verloren"),
                    "kosten": ("Bis 500.000 €", "Bei Folgeschaden"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Primäre Regelung bleibt aktiv", "beeinflusst": "D"},
                    {"name": "TI-401b", "typ": "Sensor", "wirkung": "B", "beschreibung": "Dritte Messstelle, Abweichungsprüfung", "beeinflusst": "D"},
                    {"name": "PIC-402 / PSV-410", "typ": "Sensor/Sicherheit", "wirkung": "B/E", "beschreibung": "Druck/mechanische Absicherung", "beeinflusst": "D/S"},
                ],
                "S": 8, "O": 3, "D": 5,
                "begruendung_S": "Verlust der Redundanz; bei Doppelausfall mit TIC-401 Runaway-Risiko.",
                "begruendung_O": "Sensorausfall gelegentlich.",
                "begruendung_D": "Abweichungsalarm TIC-401 vs. TI-401a fällt aus; TI-401b und PIC-402 bleiben.",
                "kontext_beschreibung": "TI-401a ist Redundanz zu TIC-401. Fällt TI-401a ein (Frozen Value), fehlt eine Vergleichsmessung. Bei gleichzeitigem TIC-401-Ausfall wäre Runaway nicht mehr erkennbar.",
                "controls_einschraenkung": "Dritte Messstelle (TI-401b) und PIC-402 bleiben; Risiko steigt bei mehrfachem Ausfall.",
            },
            {
                "funktion_id": "KOMP-011-F1",
                "fehler_id": "KOMP-011-F1-FM2",
                "fehlermodus": "Messwertdrift – Falsche Anzeige, Abweichungsalarm unnötig oder fehlt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-011-F1-FM2-UC1", "beschreibung": "Sensor altert, Kalibrierung abgelaufen", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierintervall"},
                ],
                "effects": {
                    "mensch": ("Gering", "Fehlalarm oder fehlender Alarm, indirekt Risiko"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Redundanz unzuverlässig"),
                    "kosten": ("Bis 50.000 €", "Reparatur, Stillstand bei Fehlalarm"),
                },
                "controls": [
                    {"name": "Kalibrierung", "typ": "Organisatorisch", "wirkung": "B", "beschreibung": "Periodische Kalibrierung", "beeinflusst": "O"},
                ],
                "S": 5, "O": 4, "D": 5,
                "begruendung_S": "Drift allein an TI-401a reduziert nur Redundanz.",
                "begruendung_O": "Drift möglich.",
                "begruendung_D": "Kalibrierung erkennt mit Verzögerung.",
                "kontext_beschreibung": "Drift an TI-401a führt zu falscher Abweichungsprüfung – Fehlalarm oder fehlender Alarm bei TIC-401-Fehler.",
                "controls_einschraenkung": "Kalibrierung periodisch.",
            },
        ],
    },

    # ─── KOMP-012: TI-401b (Temperature Indicator) ───
    # Zweite redundante Temperaturanzeige Reaktor R-101. Abweichungsprüfung zu TIC-401 und TI-401a.
    "KOMP-012": {
        "functions": [
            {
                "funktion_id": "KOMP-012-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "TI-401b – Prozesstemperatur anzeigen, Redundanz und Abweichungsprüfung",
                "anforderungen": [
                    {"id": "KOMP-012-F1-A1", "parameter": "Messbereich", "sollwert": "Betriebstemperatur abdeckend"},
                    {"id": "KOMP-012-F1-A2", "parameter": "Genauigkeit", "sollwert": "Vergleichbar TIC-401/TI-401a"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-012-F1",
                "fehler_id": "KOMP-012-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Redundanz verloren",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-012-F1-FM1-UC1", "beschreibung": "Sensor oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-012-F1-FM1-UC2", "beschreibung": "Leitung oder Bus defekt", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Hoch", "Bei Ausfall von TIC-401 und TI-401a Runaway nicht erkennbar"),
                    "umwelt": ("Betriebsbereich", "Bei Runaway"),
                    "anlage": ("Teilausfall", "Redundanz reduziert"),
                    "kosten": ("Bis 500.000 €", "Bei Folgeschaden"),
                },
                "controls": [
                    {"name": "TIC-401 / TI-401a", "typ": "Sensor", "wirkung": "B", "beschreibung": "Weitere Messstellen", "beeinflusst": "D"},
                    {"name": "PIC-402 / PSV-410", "typ": "Sensor/Sicherheit", "wirkung": "B/E", "beschreibung": "Druck/mechanische Absicherung", "beeinflusst": "D/S"},
                ],
                "S": 8, "O": 3, "D": 5,
                "begruendung_S": "Verlust einer Redundanzstelle; 2-of-3 bleibt erhalten.",
                "begruendung_O": "Sensorausfall gelegentlich.",
                "begruendung_D": "TIC-401 und TI-401a bleiben für Abweichung.",
                "kontext_beschreibung": "TI-401b ist dritte Temperaturmessstelle. Ausfall reduziert Redundanz; bei zwei ausgefallenen Messungen (z.B. TIC-401 + TI-401b) bleibt TI-401a.",
                "controls_einschraenkung": "Risiko steigt bei mehrfachem Ausfall.",
            },
        ],
    },

    # ─── KOMP-013: PIC-402 (Pressure Indicator Controller) ───
    # Druckanzeige und -regler Reaktor R-101. Misst Druck, regelt z.B. Abblaseventil. Kritisch für Überdruck/Unterdruck.
    "KOMP-013": {
        "functions": [
            {
                "funktion_id": "KOMP-013-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "PIC-402 – Reaktordruck erfassen, anzeigen und regeln (Über-/Unterdruckbegrenzung)",
                "anforderungen": [
                    {"id": "KOMP-013-F1-A1", "parameter": "Messbereich", "sollwert": "Betriebsdruck bis Design (z.B. -0.9 bis 6 bar)"},
                    {"id": "KOMP-013-F1-A2", "parameter": "Regelung/Alarm", "sollwert": "Alarm bei Abweichung, ggf. Stellventil"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-013-F1",
                "fehler_id": "KOMP-013-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Druckanstieg (Runaway) wird nicht erkannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-013-F1-FM1-UC1", "beschreibung": "Druckmessumformer oder Impulsleitung defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-013-F1-FM1-UC2", "beschreibung": "Impulsleitung verstopft", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Überdruck nicht erkannt, Bersten in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medienfreisetzung"),
                    "anlage": ("Totalausfall", "Reaktorüberdruck, Bersten"),
                    "kosten": ("Bis 500.000 €", "Reaktor, Personenschaden"),
                },
                "controls": [
                    {"name": "PSV-410", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Sicherheitsventil 6 bar", "beeinflusst": "S"},
                    {"name": "BSV-411", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Berstscheibe 6.5 bar", "beeinflusst": "S"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturanstieg bei Runaway indirekt", "beeinflusst": "D"},
                ],
                "S": 9, "O": 3, "D": 5,
                "begruendung_S": "Überdruck nicht erkannt, Reaktor in Ex-Zone 1, katastrophal.",
                "begruendung_O": "Frozen Value bei Druckmessung gelegentlich.",
                "begruendung_D": "PSV/BSV als letzte Barriere; TIC-401 erkennt Runaway indirekt.",
                "kontext_beschreibung": "PIC-402 ist zentrale Drucküberwachung. Eingefrorener Wert bei steigendem Druck bedeutet: Regelung und Alarm greifen nicht. PSV und BSV sind letzte mechanische Absicherung.",
                "controls_einschraenkung": "PSV/BSV müssen funktionsfähig sein. TIC-401 erkennt erst bei Temperaturanstieg.",
            },
            {
                "funktion_id": "KOMP-013-F1",
                "fehler_id": "KOMP-013-F1-FM2",
                "fehlermodus": "Unterdruck nicht erkannt – PIC zeigt falsch, VSV (Vakuumbrecher) nicht getriggert",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-013-F1-FM2-UC1", "beschreibung": "Messwert eingefroren oder Drift nach oben", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Implosion selten, Behälter ausgelegt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Behälterdeformation bei Unterdruck"),
                    "kosten": ("Bis 50.000 €", "Reparatur"),
                },
                "controls": [
                    {"name": "VSV-412", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Vakuum-Sicherheitsventil, öffnet bei -0.8 bar", "beeinflusst": "O"},
                ],
                "S": 6, "O": 2, "D": 5,
                "begruendung_S": "Behälter für -0.9 bar ausgelegt, VSV-412 reduziert Risiko.",
                "begruendung_O": "Unterdruck seltener.",
                "begruendung_D": "VSV öffnet unabhängig von PIC; PIC-Fehler beeinflusst nur Anzeige/Alarm.",
                "kontext_beschreibung": "Bei Unterdruck (z.B. schnelle Abkühlung) muss VSV-412 ansprechen. PIC-402-Fehler verhindert das nicht, aber Anzeige/Alarm fehlen.",
                "controls_einschraenkung": "VSV muss regelmäßig geprüft werden.",
            },
        ],
    },

    # ─── KOMP-014: LIC-403 (Level Indicator Controller – Füllstand Reaktor) ───
    # Füllstandsanzeige und -regler, Radar 0–500 L, SIL-1. Liefert Signal für Regelung und Überfüllsicherung.
    "KOMP-014": {
        "functions": [
            {
                "funktion_id": "KOMP-014-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "LIC-403 – Füllstand im Reaktor erfassen, anzeigen und regeln (0–500 L, Radar, SIL-1)",
                "anforderungen": [
                    {"id": "KOMP-014-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 500 L, Radar"},
                    {"id": "KOMP-014-F1-A2", "parameter": "SIL", "sollwert": "SIL-1"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-014-F1",
                "fehler_id": "KOMP-014-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Überfüllung wird nicht erkannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-014-F1-FM1-UC1", "beschreibung": "Radar-Störung, Schaum oder Verschmutzung", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "LSHH-403 redundant"},
                    {"ursache_id": "KOMP-014-F1-FM1-UC2", "beschreibung": "Leitung oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Überfüllung bis Überlauf in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne, Medienfreisetzung"),
                    "anlage": ("Teilausfall", "Reaktor überfüllt"),
                    "kosten": ("Bis 100.000 €", "Folgeschaden, Stillstand"),
                },
                "controls": [
                    {"name": "LSHH-403", "typ": "Sensor", "wirkung": "O", "sil_level": "SIL-2", "beschreibung": "Unabhängige Überfüllsicherung bei 480 L (Level Switch High High)", "beeinflusst": "O"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Überfüllung in Ex-Zone, Gefahr von Überlauf und Freisetzung.",
                "begruendung_O": "Frozen Value bei Füllstand gelegentlich; LSHH reduziert O.",
                "begruendung_D": "LSHH unabhängig; kein Plausibilitätscheck zwischen LIC und LSHH.",
                "kontext_beschreibung": "LIC-403 ist die kontinuierliche Füllstandsmessung für Regelung. Bei eingefrorenem Wert kann Überfüllung unerkannt bleiben; LSHH-403 ist die letzte Barriere.",
                "controls_einschraenkung": "LSHH-403 muss funktionsfähig und unabhängig geprüft werden.",
            },
            {
                "funktion_id": "KOMP-014-F1",
                "fehler_id": "KOMP-014-F1-FM2",
                "fehlermodus": "Messwertdrift – Füllstand falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-014-F1-FM2-UC1", "beschreibung": "Radar-Kalibrierung oder Umgebungsänderung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Falsche Füllstandsanzeige kann zu Fehlbedienung führen"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenqualität, ggf. Überfüllung"),
                    "kosten": ("Bis 20.000 €", "Charge, Nacharbeit"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Ohne Überfüllung: moderate Folgen; mit Überfüllung LSHH greift.",
                "begruendung_O": "Drift gelegentlich.",
                "begruendung_D": "Keine automatische Plausibilitätsprüfung.",
                "kontext_beschreibung": "Drift beeinträchtigt Regelung und Anzeige; LSHH-403 begrenzt Überfüllrisiko.",
            },
            {
                "funktion_id": "KOMP-014-F1",
                "fehler_id": "KOMP-014-F1-FM3",
                "fehlermodus": "Signalausfall – Regler blind, Füllstand unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-014-F1-FM3-UC1", "beschreibung": "Leitung, Steckverbinder oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring, Diagnose"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Blinder Regler, Überfüllung möglich"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Regelung ausgefallen"),
                    "kosten": ("Bis 100.000 €", "Bei Überfüllung"),
                },
                "controls": [
                    {"name": "LSHH-403", "typ": "Sensor", "wirkung": "O", "beschreibung": "Redundante Überfüllsicherung unabhängig von LIC", "beeinflusst": "O"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Ohne LSHH katastrophal; mit LSHH Überfüllung begrenzt.",
                "begruendung_O": "Signalausfall gelegentlich.",
                "begruendung_D": "LSHH erkennt Überfüllung; LIC-Ausfall oft erst bei Abweichung sichtbar.",
                "kontext_beschreibung": "Bei LIC-Ausfall ist die Regelung blind; LSHH-403 schaltet bei 480 L ab.",
            },
        ],
    },

    # ─── KOMP-015: LSHH-403 (Level Switch High High – Überfüllsicherung) ───
    # Füllstandsschalter sehr hoch bei 480 L, SIL-2, letzte Barriere gegen Überfüllung.
    "KOMP-015": {
        "functions": [
            {
                "funktion_id": "KOMP-015-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "LSHH-403 – Überfüllsicherung bei 480 L (SIL-2), unabhängig von LIC-403, schaltet bei Überschreitung ab",
                "anforderungen": [
                    {"id": "KOMP-015-F1-A1", "parameter": "Schaltpunkt", "sollwert": "480 L, Vibration"},
                    {"id": "KOMP-015-F1-A2", "parameter": "SIL", "sollwert": "SIL-2"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-015-F1",
                "fehler_id": "KOMP-015-F1-FM1",
                "fehlermodus": "Fail-to-trip – öffnet/schaltet nicht bei 480 L (letzte Barriere versagt)",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-015-F1-FM1-UC1", "beschreibung": "Vibrationsschalter verklebt oder verschmutzt", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Funktionsprüfung"},
                    {"ursache_id": "KOMP-015-F1-FM1-UC2", "beschreibung": "Verkabelung oder Relais defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Überfüllung bis Überlauf, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne, Medienfreisetzung"),
                    "anlage": ("Totalausfall", "Reaktor überfüllt, Folgeschaden"),
                    "kosten": ("Bis 500.000 €", "Stillstand, Personenschaden"),
                },
                "controls": [],
                "S": 9, "O": 3, "D": 5,
                "begruendung_S": "Letzte Barriere gegen Überfüllung; Versagen katastrophal.",
                "begruendung_O": "SIL-2, regelmäßige Prüfung reduziert O.",
                "begruendung_D": "Keine Online-Prüfung des Schaltpunktes; nur periodische Funktionsprüfung.",
                "kontext_beschreibung": "LSHH-403 ist die Überfüllsicherung (Level Switch High High). Fail-to-trip bedeutet: bei 480 L wird nicht abgeschaltet.",
                "controls_einschraenkung": "Keine redundante Überfüllsicherung; LIC-403 ist keine Sicherheitsfunktion.",
            },
            {
                "funktion_id": "KOMP-015-F1",
                "fehler_id": "KOMP-015-F1-FM2",
                "fehlermodus": "Frühzeitiges Ansprechen – schaltet bei korrektem Füllstand ab",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-015-F1-FM2-UC1", "beschreibung": "Falsche Kalibrierung oder Verschmutzung", "herkunft": "Wartung", "phase": "Wartung", "hinweis": "Prüfung Schaltpunkt"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine Gefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenabbruch, Produktionsausfall"),
                    "kosten": ("Bis 20.000 €", "Charge verloren"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Nur Produktionsausfall, keine Überfüllung.",
                "begruendung_O": "Gelegentlich durch Drift/Kalibrierung.",
                "begruendung_D": "Erst bei Abschaltung erkennbar.",
                "kontext_beschreibung": "LSHH spricht zu früh an und stoppt die Charge unnötig.",
            },
            {
                "funktion_id": "KOMP-015-F1",
                "fehler_id": "KOMP-015-F1-FM3",
                "fehlermodus": "Signalausfall – Sicherheitsfunktion ausgefallen",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-015-F1-FM3-UC1", "beschreibung": "Leitung, Relais oder Schalter defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Fail-safe prüfen"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Überfüllsicherung nicht verfügbar"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Totalausfall", "Sicherheit ausgefallen"),
                    "kosten": ("Bis 500.000 €", "Bei Überfüllung"),
                },
                "controls": [],
                "S": 9, "O": 2, "D": 5,
                "begruendung_S": "Sicherheitsfunktion ausgefallen.",
                "begruendung_O": "Signalausfall selten; oft fail-safe (Abschaltung bei Leitungsbruch).",
                "begruendung_D": "Keine Prüfung ob Signal ankommt außer periodisch.",
                "kontext_beschreibung": "Bei Signalausfall muss Anlage in sicheren Zustand (z.B. Abschaltung) gehen; sonst Überfüllung unerkannt.",
            },
        ],
    },

    # ─── KOMP-016: SIC-404 (Speed Indicator Controller – Rührwerk) ───
    # Drehzahlanzeige und -regler, 0–250 U/min, VFD 5.5 kW. Kritisch für Durchmischung und Runaway-Vermeidung.
    "KOMP-016": {
        "functions": [
            {
                "funktion_id": "KOMP-016-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "SIC-404 – Rührwerksdrehzahl messen, anzeigen und regeln (0–250 U/min, Frequenzumrichter 5.5 kW)",
                "anforderungen": [
                    {"id": "KOMP-016-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 250 U/min"},
                    {"id": "KOMP-016-F1-A2", "parameter": "Regelung", "sollwert": "PID, VFD"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-016-F1",
                "fehler_id": "KOMP-016-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Drehzahl falsch angezeigt, Stillstand unerkannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-016-F1-FM1-UC1", "beschreibung": "VFD oder Drehzahlsensor liefert konstanten Wert", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Plausibilität TIC"},
                    {"ursache_id": "KOMP-016-F1-FM1-UC2", "beschreibung": "Leitung oder Rückmeldung defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Keine Durchmischung bei Stillstand, Runaway möglich"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Lokale Überhitzung, Runaway"),
                    "kosten": ("Bis 100.000 €", "Reaktor, Charge"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturanstieg bei fehlender Durchmischung indirekt erkennbar", "beeinflusst": "D"},
                ],
                "S": 7, "O": 4, "D": 4,
                "begruendung_S": "Runaway indirekt über Temperatur; ohne TIC katastrophal.",
                "begruendung_O": "Frozen Value bei Drehzahl gelegentlich.",
                "begruendung_D": "TIC-401 erkennt Anstieg mit Verzögerung; 100% manuelle Prüfung.",
                "kontext_beschreibung": "SIC-404 regelt die Rührwerksdrehzahl. Eingefrorener Wert kann Stillstand vortäuschen oder echten Stillstand verschleiern; TIC-401 ist indirekte Absicherung.",
                "controls_einschraenkung": "TIC reagiert erst bei Temperaturanstieg, nicht sofort bei Stillstand.",
            },
            {
                "funktion_id": "KOMP-016-F1",
                "fehler_id": "KOMP-016-F1-FM2",
                "fehlermodus": "Messwertdrift – Drehzahl angezeigt, aber ungenau",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-016-F1-FM2-UC1", "beschreibung": "VFD-Alterung oder Kalibrierung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Durchmischung suboptimal, Chargenqualität"),
                    "kosten": ("Bis 20.000 €", "Charge"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Kein unmittelbarer Sicherheitsverlust.",
                "begruendung_O": "Drift gelegentlich.",
                "begruendung_D": "Ohne Referenzmessung schwer erkennbar.",
                "kontext_beschreibung": "Drift beeinträchtigt Regelgüte, nicht primär Sicherheit.",
            },
            {
                "funktion_id": "KOMP-016-F1",
                "fehler_id": "KOMP-016-F1-FM3",
                "fehlermodus": "Signalausfall – Rührwerk stoppt oder Regler blind",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-016-F1-FM3-UC1", "beschreibung": "VFD-Fehler, Leitung oder Stromausfall", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring, VFD-Diagnose"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Keine Durchmischung, Runaway möglich"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Rührwerk steht, Runaway-Risiko"),
                    "kosten": ("Bis 100.000 €", "Reaktor, Charge"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturüberwachung erkennt Runaway indirekt", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Runaway-Risiko; TIC begrenzt Folgen.",
                "begruendung_O": "VFD/Leitung gelegentlich.",
                "begruendung_D": "Temperatur steigt mit Verzögerung; Alarm möglich.",
                "kontext_beschreibung": "Bei Rührwerk-Stillstand muss schnell erkannt werden; TIC-401 ist Rückfallebene.",
            },
        ],
    },

    # ─── KOMP-017: PSV-410 (Pressure Safety Valve – Sicherheitsventil 6 bar, DN50) ───
    "KOMP-017": {
        "functions": [
            {
                "funktion_id": "KOMP-017-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "PSV-410 – Druckentlastung bei 6 bar, Abblaseleitung Fackel, DN50",
                "anforderungen": [
                    {"id": "KOMP-017-F1-A1", "parameter": "Ansprechdruck", "sollwert": "6 bar, DN50"},
                    {"id": "KOMP-017-F1-A2", "parameter": "Prüfintervall", "sollwert": "1 Jahr"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-017-F1",
                "fehler_id": "KOMP-017-F1-FM1",
                "fehlermodus": "Fail-to-open – öffnet nicht bei Ansprechdruck (Berstgefahr)",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-017-F1-FM1-UC1", "beschreibung": "Verklebung durch Korrosion (Essigsäure, Medien)", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Jährliche Prüfung"},
                    {"ursache_id": "KOMP-017-F1-FM1-UC2", "beschreibung": "Fremdkörper im Sitz oder Ablagerungen", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Abnahme prüfen"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Bersten Reaktor, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Medienfreisetzung"),
                    "anlage": ("Totalausfall", "Reaktor zerstört"),
                    "kosten": ("Bis 1 Mio €", "Reaktor, Personenschaden"),
                },
                "controls": [
                    {"name": "BSV-411", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Berstscheibe redundant bei 6.5 bar", "beeinflusst": "O"},
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Alarm bei Druckanstieg", "beeinflusst": "D"},
                ],
                "S": 10, "O": 3, "D": 5,
                "begruendung_S": "Fail-to-open bei Überdruck katastrophal; BSV Backup.",
                "begruendung_O": "Verklebung/Korrosion in saurer Umgebung gelegentlich.",
                "begruendung_D": "Keine Online-Prüfung; nur jährliche Prüfung.",
                "kontext_beschreibung": "PSV-410 ist erste Druckentlastung. Versagen bedeutet: bei Überdruck öffnet Ventil nicht; BSV-411 ist letzte mechanische Barriere.",
                "controls_einschraenkung": "BSV-411 muss funktionsfähig sein; PIC erkennt nur indirekt.",
            },
            {
                "funktion_id": "KOMP-017-F1",
                "fehler_id": "KOMP-017-F1-FM2",
                "fehlermodus": "Erosion/Kavitation am Sitz (bei Abblasen)",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-017-F1-FM2-UC1", "beschreibung": "Verschleiß bei Abblasvorgang (Medien, Dampf)", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Sichtprüfung Abnahme"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Nächstes Mal Fail-to-open möglich"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "PSV undicht oder nicht mehr ansprechbar"),
                    "kosten": ("Bis 50.000 €", "Ventilwechsel"),
                },
                "controls": [],
                "S": 10, "O": 4, "D": 4,
                "begruendung_S": "Indirekt Berstgefahr bei nächstem Überdruck.",
                "begruendung_O": "Verschleiß bei Abblasen selten aber möglich.",
                "begruendung_D": "Bei Abnahme sichtbar; keine Online-Überwachung.",
                "kontext_beschreibung": "Erosion verschlechtert Sitz; bei nächstem Ansprechen kann Ventil versagen.",
            },
        ],
    },

    # ─── KOMP-018: BSV-411 (Berstscheibe 6.5 bar, DN50, Hastelloy C276) ───
    "KOMP-018": {
        "functions": [
            {
                "funktion_id": "KOMP-018-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "BSV-411 – Letzte Druckbarriere bei 6.5 bar, DN50, Hastelloy C276, Abblaseleitung Fackel",
                "anforderungen": [
                    {"id": "KOMP-018-F1-A1", "parameter": "Ansprechdruck", "sollwert": "6.5 bar, DN50"},
                    {"id": "KOMP-018-F1-A2", "parameter": "Material", "sollwert": "Hastelloy C276"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-018-F1",
                "fehler_id": "KOMP-018-F1-FM1",
                "fehlermodus": "Fail-to-open – Berstscheibe öffnet nicht bei 6.5 bar",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-018-F1-FM1-UC1", "beschreibung": "Alterung, falsche Dimensionierung oder Materialfehler", "herkunft": "Design", "phase": "Detaildesign", "hinweis": "Berechnung, Qualitätssicherung"},
                    {"ursache_id": "KOMP-018-F1-FM1-UC2", "beschreibung": "Korrosion durch Medien", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Bersten Reaktor"),
                    "umwelt": ("Betriebsbereich", "Medienfreisetzung"),
                    "anlage": ("Totalausfall", "Reaktor zerstört"),
                    "kosten": ("Bis 1 Mio €", "-"),
                },
                "controls": [
                    {"name": "PSV-410", "typ": "Sicherheit", "wirkung": "O", "beschreibung": "Primäre Druckentlastung bei 6 bar", "beeinflusst": "O"},
                ],
                "S": 10, "O": 2, "D": 5,
                "begruendung_S": "Letzte Barriere; Versagen lebensgefährlich.",
                "begruendung_O": "PSV primär; BSV nur bei PSV-Versagen.",
                "begruendung_D": "Keine Prüfung möglich ohne Ersatz; nur Inspektion/Wechselintervall.",
                "kontext_beschreibung": "BSV-411 ist Backup zur PSV-410. Fail-to-open bedeutet Bersten, wenn auch PSV versagt.",
                "controls_einschraenkung": "PSV muss zuverlässig sein; BSV ist letzte Linie.",
            },
            {
                "funktion_id": "KOMP-018-F1",
                "fehler_id": "KOMP-018-F1-FM2",
                "fehlermodus": "Frühzeitiges Bersten – öffnet unter Betriebsdruck",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-018-F1-FM2-UC1", "beschreibung": "Materialfehler, Ermüdung oder mechanische Beschädigung", "herkunft": "Design", "phase": "Detaildesign", "hinweis": "Qualitätssicherung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Medienfreisetzung, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Fackel, Leckage"),
                    "anlage": ("Teilausfall", "Stillstand, Scheibenwechsel"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Stillstand"),
                },
                "controls": [],
                "S": 8, "O": 2, "D": 5,
                "begruendung_S": "Medienfreisetzung in Ex-Zone, keine Berstkatastrophe.",
                "begruendung_O": "Frühzeitiges Bersten selten.",
                "begruendung_D": "Keine Vorhersage möglich.",
                "kontext_beschreibung": "Berstscheibe bricht vor Erreichen des Ansprechdrucks; Folge ist Leckage, nicht Bersten des Reaktors.",
            },
        ],
    },

    # ─── KOMP-019: VSV-412 (Vakuum-Sicherheitsventil / Vakuumbrecher -0.8 bar, DN25) ───
    "KOMP-019": {
        "functions": [
            {
                "funktion_id": "KOMP-019-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "VSV-412 – Vakuumbrecher: verhindert Unterdruck unter -0.8 bar, DN25",
                "anforderungen": [
                    {"id": "KOMP-019-F1-A1", "parameter": "Ansprechdruck", "sollwert": "-0.8 bar"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-019-F1",
                "fehler_id": "KOMP-019-F1-FM1",
                "fehlermodus": "Fail-to-open – öffnet nicht bei Unterdruck (Implosionsgefahr)",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-019-F1-FM1-UC1", "beschreibung": "Verklebung, Korrosion oder Vereisung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Jährliche Prüfung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Implosion, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Totalausfall", "Reaktor implodiert"),
                    "kosten": ("Bis 500.000 €", "-"),
                },
                "controls": [],
                "S": 9, "O": 3, "D": 5,
                "begruendung_S": "Implosion lebensgefährlich; Behälter für -0.9 bar ausgelegt, VSV soll darunter verhindern.",
                "begruendung_O": "Korrosion/Verklebung in Prozessumgebung gelegentlich.",
                "begruendung_D": "Keine Online-Prüfung; nur periodische Prüfung.",
                "kontext_beschreibung": "VSV-412 (Vacuum Safety Valve) verhindert Unterdruck unter -0.8 bar. Fail-to-open bedeutet Implosionsgefahr.",
            },
            {
                "funktion_id": "KOMP-019-F1",
                "fehler_id": "KOMP-019-F1-FM2",
                "fehlermodus": "Leckage – Luft dringt bei Normalbetrieb ein",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-019-F1-FM2-UC1", "beschreibung": "Dichtung undicht oder Sitz beschädigt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine unmittelbare Gefährdung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Sauerstoffeintritt, Chargenqualität"),
                    "kosten": ("Bis 20.000 €", "Dichtung, Charge"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Nur Qualitäts- und Prozessauswirkung.",
                "begruendung_O": "Dichtung gelegentlich.",
                "begruendung_D": "Oft erst bei Qualitätsabweichung erkennbar.",
                "kontext_beschreibung": "Luftleckage beeinträchtigt Prozess, nicht primär Sicherheit.",
            },
        ],
    },

    # ─── KOMP-020: NOT-AUS-R101 ───
    "KOMP-020": {
        "functions": [
            {
                "funktion_id": "KOMP-020-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "NOT-AUS-R101 – Bei Betätigung Abschaltung aller Antriebe und Schließen der Eingangsventile, Reaktionszeit < 1 s, Rückstellung manuell vor Ort",
                "anforderungen": [
                    {"id": "KOMP-020-F1-A1", "parameter": "Reaktionszeit", "sollwert": "< 1 s"},
                    {"id": "KOMP-020-F1-A2", "parameter": "Rückstellung", "sollwert": "Manuell vor Ort"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-020-F1",
                "fehler_id": "KOMP-020-F1-FM1",
                "fehlermodus": "Fail-to-trip – NOT-AUS schaltet nicht ab",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-020-F1-FM1-UC1", "beschreibung": "Verkabelung, Relais oder Schaltkreis defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Funktionsprüfung"},
                    {"ursache_id": "KOMP-020-F1-FM1-UC2", "beschreibung": "Falsche Parametrierung oder Bypass im DCS", "herkunft": "Design", "phase": "Detaildesign", "hinweis": "Abnahme"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Keine Abschaltung bei Notfall"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Totalausfall", "Eskalation möglich"),
                    "kosten": ("Bis 1 Mio €", "-"),
                },
                "controls": [],
                "S": 10, "O": 2, "D": 5,
                "begruendung_S": "NOT-AUS ist letzte manuelle Sicherheit; Versagen lebensgefährlich.",
                "begruendung_O": "Fail-to-trip selten bei richtiger Wartung.",
                "begruendung_D": "Keine Prüfung außer periodischer Funktionsprüfung.",
                "kontext_beschreibung": "NOT-AUS-R101 schaltet Anlage sicher ab. Fail-to-trip bedeutet: im Notfall reagiert die Anlage nicht.",
                "controls_einschraenkung": "Keine redundante NOT-AUS-Ebene; regelmäßige Prüfung zwingend.",
            },
        ],
    },

    # ─── KOMP-021: Dosiersystem DS-200 (System) ───
    "KOMP-021": {
        "functions": [
            {
                "funktion_id": "KOMP-021-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Dosiersystem DS-200 – Vollautomatische Dosierung von Ethanol, Essigsäure und Katalysator (Schwefelsäure) in den Reaktor, DCS-Integration, Ex-Zone 1",
                "anforderungen": [
                    {"id": "KOMP-021-F1-A1", "parameter": "Automation", "sollwert": "Vollautomatisch (DCS)"},
                    {"id": "KOMP-021-F1-A2", "parameter": "ExZone", "sollwert": "Zone 1"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-021-F1",
                "fehler_id": "KOMP-021-F1-FM1",
                "fehlermodus": "Falsches stöchiometrisches Verhältnis – Konzentrationsabweichung",
                "fehlerart": "Dosierung",
                "causes": [
                    {"ursache_id": "KOMP-021-F1-FM1-UC1", "beschreibung": "FIC-404/FIC-405 Drift oder Kalibrierfehler", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-021-F1-FM1-UC2", "beschreibung": "Pumpen P-201/P-202 unterschiedlicher Verschleiß", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Membranwechsel"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Nebenreaktionen, Runaway bei falschem Verhältnis"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Chargenqualität, ggf. Überdruck"),
                    "kosten": ("Bis 100.000 €", "Charge, Reaktor"),
                },
                "controls": [
                    {"name": "FIC-404 / FIC-405", "typ": "Sensor", "wirkung": "B", "beschreibung": "Durchflussmessung und Regelung", "beeinflusst": "D"},
                    {"name": "TIC-401 / PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperatur/Druck im Reaktor", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Falsches Verhältnis kann Runaway begünstigen.",
                "begruendung_O": "Drift/Kalibrierung gelegentlich.",
                "begruendung_D": "TIC/PIC erkennen Abweichung mit Verzögerung.",
                "kontext_beschreibung": "Dosiersystem liefert Edukte. Falsches Verhältnis beeinträchtigt Reaktion und kann zu Überhitzung führen.",
            },
            {
                "funktion_id": "KOMP-021-F1",
                "fehler_id": "KOMP-021-F1-FM2",
                "fehlermodus": "Kein Stoffstrom (eine oder mehrere Dosierungen ausgefallen)",
                "fehlerart": "Dosierung",
                "causes": [
                    {"ursache_id": "KOMP-021-F1-FM2-UC1", "beschreibung": "Pumpe ausgefallen, Leitung blockiert oder LSLL ausgelöst", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "LSLL-201/LSLL-202 Trockenlaufschutz"},
                    {"ursache_id": "KOMP-021-F1-FM2-UC2", "beschreibung": "Ventil geschlossen oder DCS-Fehler", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Abnahme"},
                ],
                "effects": {
                    "mensch": ("Gering", "Unvollständige Reaktion, ggf. Nachdosierung manuell"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Charge unbrauchbar oder Nacharbeit"),
                    "kosten": ("Bis 50.000 €", "Charge"),
                },
                "controls": [
                    {"name": "LSLL-201 / LSLL-202", "typ": "Sensor", "wirkung": "O", "beschreibung": "Trockenlaufschutz Pumpe bei niedrigem Füllstand", "beeinflusst": "O"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Kein unmittelbarer Sicherheitsverlust; Charge betroffen.",
                "begruendung_O": "Pumpenausfall gelegentlich.",
                "begruendung_D": "Durchflussmessung erkennt No Flow.",
                "kontext_beschreibung": "Ausfall einer Dosierleitung führt zu unvollständiger Charge; LSLL schützt vor Trockenlauf.",
            },
        ],
    },

    # ─── KOMP-022: Vorlagebehälter VB-201 (Ethanol, 200 L) ───
    "KOMP-022": {
        "functions": [
            {
                "funktion_id": "KOMP-022-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Vorlagebehälter VB-201 – Ethanol-Vorlage 200 L, Edelstahl 1.4571, atmosphärisch, für Dosierpumpe P-201",
                "anforderungen": [
                    {"id": "KOMP-022-F1-A1", "parameter": "Volumen", "sollwert": "200 L"},
                    {"id": "KOMP-022-F1-A2", "parameter": "Inhalt", "sollwert": "Ethanol"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-022-F1",
                "fehler_id": "KOMP-022-F1-FM1",
                "fehlermodus": "Äußere Leckage – Integritätsverlust",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-022-F1-FM1-UC1", "beschreibung": "Flanschdichtung, Schweißnaht oder Anschluss undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "KOMP-022-F1-FM1-UC2", "beschreibung": "Korrosion oder mechanische Beschädigung", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Auffangwanne"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ethanol in Ex-Zone 1, Brandgefahr"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne AW-200"),
                    "anlage": ("Teilausfall", "Vorlage leer, Dosierung gestoppt"),
                    "kosten": ("Bis 100.000 €", "Stillstand, Reinigung"),
                },
                "controls": [
                    {"name": "Auffangwanne AW-200", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Leckagesensor, 500 L", "beeinflusst": "S"},
                    {"name": "LSLL-201", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz P-201", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Ethanol brennbar, Ex-Zone; Auffangwanne begrenzt Ausbreitung.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Leckagesensor in AW-200; LSLL erkennt Füllstand.",
                "kontext_beschreibung": "VB-201 enthält Ethanol. Leckage muss erkannt und aufgefangen werden.",
            },
            {
                "funktion_id": "KOMP-022-F1",
                "fehler_id": "KOMP-022-F1-FM2",
                "fehlermodus": "Verstopfung / Blockade – Auslauf nicht förderbar",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-022-F1-FM2-UC1", "beschreibung": "Verschmutzung, Fremdkörper oder Ablagerung im Auslauf", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Filter, Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Dosierung P-201 gestoppt, Charge betroffen"),
                    "kosten": ("Bis 20.000 €", "Charge"),
                },
                "controls": [
                    {"name": "LSLL-201", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Nur Produktionsausfall.",
                "begruendung_O": "Verstopfung gelegentlich.",
                "begruendung_D": "Durchflussabfall erkennbar.",
                "kontext_beschreibung": "Blockade verhindert Dosierung; LSLL schützt Pumpe.",
            },
        ],
    },

    # ─── KOMP-023: Vorlagebehälter VB-202 (Essigsäure, 200 L) ───
    "KOMP-023": {
        "functions": [
            {
                "funktion_id": "KOMP-023-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Vorlagebehälter VB-202 – Essigsäure-Vorlage 200 L, Edelstahl 1.4571, atmosphärisch, für Dosierpumpe P-202",
                "anforderungen": [
                    {"id": "KOMP-023-F1-A1", "parameter": "Volumen", "sollwert": "200 L"},
                    {"id": "KOMP-023-F1-A2", "parameter": "Inhalt", "sollwert": "Essigsäure"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-023-F1",
                "fehler_id": "KOMP-023-F1-FM1",
                "fehlermodus": "Äußere Leckage – Integritätsverlust",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-023-F1-FM1-UC1", "beschreibung": "Flanschdichtung, Schweißnaht oder Anschluss undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                    {"ursache_id": "KOMP-023-F1-FM1-UC2", "beschreibung": "Korrosion durch Essigsäure", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Auffangwanne"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Essigsäure ätzend, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne AW-200"),
                    "anlage": ("Teilausfall", "Vorlage leer, Dosierung gestoppt"),
                    "kosten": ("Bis 100.000 €", "Stillstand, Reinigung"),
                },
                "controls": [
                    {"name": "Auffangwanne AW-200", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Leckagesensor, 500 L", "beeinflusst": "S"},
                    {"name": "LSLL-202", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz P-202", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Essigsäure ätzend; Auffangwanne begrenzt.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Leckagesensor; LSLL erkennt Füllstand.",
                "kontext_beschreibung": "VB-202 enthält Essigsäure. Leckage muss aufgefangen werden.",
            },
            {
                "funktion_id": "KOMP-023-F1",
                "fehler_id": "KOMP-023-F1-FM2",
                "fehlermodus": "Verstopfung / Blockade – Auslauf nicht förderbar",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-023-F1-FM2-UC1", "beschreibung": "Verschmutzung, Ablagerung oder Fremdkörper im Auslauf", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Dosierung P-202 gestoppt"),
                    "kosten": ("Bis 20.000 €", "Charge"),
                },
                "controls": [
                    {"name": "LSLL-202", "typ": "Sensor", "wirkung": "B", "beschreibung": "Trockenlaufschutz", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Nur Produktionsausfall.",
                "begruendung_O": "Verstopfung gelegentlich.",
                "begruendung_D": "Durchflussabfall erkennbar.",
                "kontext_beschreibung": "Blockade verhindert Dosierung; LSLL schützt Pumpe.",
            },
        ],
    },

    # ─── KOMP-024: Dosierpumpe P-201 (Ethanol, Membranpumpe, 50 L/h, ATEX Zone 1) ───
    "KOMP-024": {
        "functions": [
            {
                "funktion_id": "KOMP-024-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Dosierpumpe P-201 – Ethanol von VB-201 zum Reaktor fördern, 5–50 L/h, Membranpumpe 0.75 kW, ATEX Zone 1",
                "anforderungen": [
                    {"id": "KOMP-024-F1-A1", "parameter": "Durchfluss", "sollwert": "5 bis 50 L/h"},
                    {"id": "KOMP-024-F1-A2", "parameter": "Förderdruck", "sollwert": "6 bar"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-024-F1",
                "fehler_id": "KOMP-024-F1-FM1",
                "fehlermodus": "Kein Stoffstrom (No Flow) – Pumpe fördert nicht",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-024-F1-FM1-UC1", "beschreibung": "Membran gerissen oder undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Membranwechsel 2000 h"},
                    {"ursache_id": "KOMP-024-F1-FM1-UC2", "beschreibung": "Trockenlauf durch LSLL-201 (Vorlage leer) oder Antrieb defekt", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "LSLL-201"},
                ],
                "effects": {
                    "mensch": ("Gering", "Falsches Verhältnis im Reaktor bei weiterer Dosierung Essigsäure"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Charge unbrauchbar, Pumpe beschädigt bei Trockenlauf"),
                    "kosten": ("Bis 50.000 €", "Charge, Pumpe"),
                },
                "controls": [
                    {"name": "LSLL-201", "typ": "Sensor", "wirkung": "O", "sil_level": "SIL-1", "beschreibung": "Trockenlaufschutz bei 20 L", "beeinflusst": "O"},
                    {"name": "FIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "Durchflussmessung erkennt No Flow", "beeinflusst": "D"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "Charge und ggf. Pumpe; kein unmittelbarer Personenschaden.",
                "begruendung_O": "Membranverschleiß gelegentlich.",
                "begruendung_D": "FIC-404 erkennt fehlenden Durchfluss.",
                "kontext_beschreibung": "P-201 fördert Ethanol. No Flow führt zu falschem Rezept; LSLL verhindert Trockenlauf.",
            },
            {
                "funktion_id": "KOMP-024-F1",
                "fehler_id": "KOMP-024-F1-FM2",
                "fehlermodus": "Äußere Leckage – Gleitringdichtung oder Anschluss",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-024-F1-FM2-UC1", "beschreibung": "Membran undicht oder Flanschdichtung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Ethanol in Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "Auffangwanne AW-200"),
                    "anlage": ("Teilausfall", "Pumpe außer Betrieb"),
                    "kosten": ("Bis 50.000 €", "Reparatur, Stillstand"),
                },
                "controls": [
                    {"name": "Auffangwanne AW-200", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Leckagesensor", "beeinflusst": "S"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Ethanol brennbar, Ex-Zone.",
                "begruendung_O": "Dichtung gelegentlich.",
                "begruendung_D": "Leckagesensor in Auffangwanne.",
                "kontext_beschreibung": "Leckage an Pumpe muss aufgefangen werden.",
            },
        ],
    },

    # ─── KOMP-025: Dosierpumpe P-202 (Essigsäure, Membranpumpe) ───
    "KOMP-025": {
        "functions": [
            {
                "funktion_id": "KOMP-025-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Dosierpumpe P-202 – Essigsäure von VB-202 zum Reaktor fördern, 5–50 L/h, Membranpumpe 0.75 kW, ATEX Zone 1",
                "anforderungen": [
                    {"id": "KOMP-025-F1-A1", "parameter": "Durchfluss", "sollwert": "5 bis 50 L/h"},
                    {"id": "KOMP-025-F1-A2", "parameter": "Förderdruck", "sollwert": "6 bar"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-025-F1",
                "fehler_id": "KOMP-025-F1-FM1",
                "fehlermodus": "Kein Stoffstrom (No Flow) – Pumpe fördert nicht",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-025-F1-FM1-UC1", "beschreibung": "Membran gerissen oder Trockenlauf (LSLL-202)", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Membranwechsel"},
                    {"ursache_id": "KOMP-025-F1-FM1-UC2", "beschreibung": "Antrieb oder Ventil defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Gering", "Falsches Verhältnis im Reaktor"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Charge, Pumpe bei Trockenlauf"),
                    "kosten": ("Bis 50.000 €", "Charge, Pumpe"),
                },
                "controls": [
                    {"name": "LSLL-202", "typ": "Sensor", "wirkung": "O", "sil_level": "SIL-1", "beschreibung": "Trockenlaufschutz bei 20 L", "beeinflusst": "O"},
                    {"name": "FIC-405", "typ": "Sensor", "wirkung": "B", "beschreibung": "Durchflussmessung", "beeinflusst": "D"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "Charge und Pumpe betroffen.",
                "begruendung_O": "Membranverschleiß gelegentlich.",
                "begruendung_D": "FIC-405 erkennt No Flow.",
                "kontext_beschreibung": "P-202 fördert Essigsäure. LSLL-202 schützt vor Trockenlauf.",
            },
            {
                "funktion_id": "KOMP-025-F1",
                "fehler_id": "KOMP-025-F1-FM2",
                "fehlermodus": "Äußere Leckage – Essigsäure austretend",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-025-F1-FM2-UC1", "beschreibung": "Membran oder Flanschdichtung undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Essigsäure ätzend, Ex-Zone 1"),
                    "umwelt": ("Betriebsbereich", "AW-200"),
                    "anlage": ("Teilausfall", "Pumpe außer Betrieb"),
                    "kosten": ("Bis 50.000 €", "Reparatur"),
                },
                "controls": [
                    {"name": "Auffangwanne AW-200", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Leckagesensor", "beeinflusst": "S"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Essigsäure ätzend.",
                "begruendung_O": "Dichtung gelegentlich.",
                "begruendung_D": "Leckagesensor.",
                "kontext_beschreibung": "Leckage an P-202; Auffangwanne erforderlich.",
            },
        ],
    },

    # ─── KOMP-026: Katalysatordosierung KD-203 (Schwefelsäure 98 %) ───
    "KOMP-026": {
        "functions": [
            {
                "funktion_id": "KOMP-026-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Katalysatordosierung KD-203 – Schwefelsäure 98 % dosieren, 0.1–1 L/h, pneumatisch, Förderdruck 3 bar",
                "anforderungen": [
                    {"id": "KOMP-026-F1-A1", "parameter": "Durchfluss", "sollwert": "0.1 bis 1 L/h"},
                    {"id": "KOMP-026-F1-A2", "parameter": "Inhalt", "sollwert": "Schwefelsäure 98 %"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-026-F1",
                "fehler_id": "KOMP-026-F1-FM1",
                "fehlermodus": "Mehr Stoffstrom – Überdosierung Katalysator",
                "fehlerart": "Dosierung",
                "causes": [
                    {"ursache_id": "KOMP-026-F1-FM1-UC1", "beschreibung": "Ventil klemmt offen oder Regelungsfehler", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Stärkere Katalyse, Runaway möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Überhitzung, Charge, Korrosion"),
                    "kosten": ("Bis 100.000 €", "Reaktor, Charge"),
                },
                "controls": [
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturüberwachung Reaktor", "beeinflusst": "D"},
                    {"name": "PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Drucküberwachung", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 5,
                "begruendung_S": "Überdosierung kann Runaway begünstigen.",
                "begruendung_O": "Ventilfehler gelegentlich.",
                "begruendung_D": "Keine direkte Katalysator-Durchflussmessung; TIC/PIC indirekt.",
                "kontext_beschreibung": "KD-203 dosiert Schwefelsäure. Überdosierung erhöht Reaktionsgeschwindigkeit und Risiko.",
            },
            {
                "funktion_id": "KOMP-026-F1",
                "fehler_id": "KOMP-026-F1-FM2",
                "fehlermodus": "Äußere Leckage – Schwefelsäure austretend",
                "fehlerart": "Dosierung",
                "causes": [
                    {"ursache_id": "KOMP-026-F1-FM2-UC1", "beschreibung": "Dichtung, Schlauch oder Anschluss undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Schwefelsäure ätzend, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "AW-200"),
                    "anlage": ("Teilausfall", "Dosierung gestoppt"),
                    "kosten": ("Bis 50.000 €", "Reparatur, Stillstand"),
                },
                "controls": [
                    {"name": "Auffangwanne AW-200", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Leckagesensor", "beeinflusst": "S"},
                ],
                "S": 9, "O": 3, "D": 4,
                "begruendung_S": "Schwefelsäure stark ätzend (Gefahrstoff).",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Leckagesensor in Auffangwanne.",
                "kontext_beschreibung": "Schwefelsäure 98 % ist gefährlicher Stoff; Leckage muss sofort erkannt werden.",
            },
        ],
    },

    # ─── KOMP-027: FIC-404 (Flow Indicator Controller – Ethanol-Durchfluss, Coriolis) ───
    "KOMP-027": {
        "functions": [
            {
                "funktion_id": "KOMP-027-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "FIC-404 – Durchfluss Ethanol (P-201) messen, anzeigen und regeln, 0–100 L/h, Coriolis, PID, Ex-Zone 1",
                "anforderungen": [
                    {"id": "KOMP-027-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 100 L/h"},
                    {"id": "KOMP-027-F1-A2", "parameter": "Messprinzip", "sollwert": "Coriolis, ±0.1 %"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-027-F1",
                "fehler_id": "KOMP-027-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Durchfluss falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-027-F1-FM1-UC1", "beschreibung": "Sensor oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-027-F1-FM1-UC2", "beschreibung": "Leitung oder Bus defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Falsches stöchiometrisches Verhältnis, Runaway möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenqualität, Überhitzung"),
                    "kosten": ("Bis 100.000 €", "Charge, Reaktor"),
                },
                "controls": [
                    {"name": "FIC-405", "typ": "Sensor", "wirkung": "B", "beschreibung": "Essigsäure-Durchfluss unabhängig; Verhältnis plausibel prüfbar", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperatur Reaktor", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Falsches Verhältnis kann Runaway begünstigen.",
                "begruendung_O": "Frozen Value gelegentlich.",
                "begruendung_D": "FIC-405 und TIC indirekt; kein direkter Plausibilitätscheck.",
                "kontext_beschreibung": "FIC-404 (Flow Indicator Controller) misst Ethanol-Durchfluss. Eingefrorener Wert führt zu falscher Dosierung.",
            },
            {
                "funktion_id": "KOMP-027-F1",
                "fehler_id": "KOMP-027-F1-FM2",
                "fehlermodus": "Signalausfall – Regler blind, Dosierung unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-027-F1-FM2-UC1", "beschreibung": "Leitung, Stecker oder Messumformer", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Unkontrollierte oder keine Dosierung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Charge, ggf. Reaktor"),
                    "kosten": ("Bis 100.000 €", "-"),
                },
                "controls": [
                    {"name": "TIC-401 / PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperatur/Druck Abweichung", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Dosierung unbekannt; TIC/PIC begrenzen Folgen.",
                "begruendung_O": "Signalausfall gelegentlich.",
                "begruendung_D": "TIC/PIC mit Verzögerung.",
                "kontext_beschreibung": "Bei FIC-Ausfall sollte Dosierung sicherheitshalber gestoppt oder TIC-Alarm auslösen.",
            },
        ],
    },

    # ─── KOMP-028: FIC-405 (Flow Indicator Controller – Essigsäure-Durchfluss) ───
    "KOMP-028": {
        "functions": [
            {
                "funktion_id": "KOMP-028-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "FIC-405 – Durchfluss Essigsäure (P-202) messen, anzeigen und regeln, 0–100 L/h, Coriolis, PID, Ex-Zone 1",
                "anforderungen": [
                    {"id": "KOMP-028-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 100 L/h"},
                    {"id": "KOMP-028-F1-A2", "parameter": "Messprinzip", "sollwert": "Coriolis, ±0.1 %"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-028-F1",
                "fehler_id": "KOMP-028-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert – Durchfluss falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-028-F1-FM1-UC1", "beschreibung": "Sensor oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                    {"ursache_id": "KOMP-028-F1-FM1-UC2", "beschreibung": "Leitung oder Bus defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Diagnose"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Falsches Verhältnis, Runaway möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Chargenqualität"),
                    "kosten": ("Bis 100.000 €", "Charge, Reaktor"),
                },
                "controls": [
                    {"name": "FIC-404", "typ": "Sensor", "wirkung": "B", "beschreibung": "Ethanol-Durchfluss; Verhältnis plausibel", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperatur Reaktor", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Falsches Verhältnis kann Runaway begünstigen.",
                "begruendung_O": "Frozen Value gelegentlich.",
                "begruendung_D": "FIC-404 und TIC indirekt.",
                "kontext_beschreibung": "FIC-405 misst Essigsäure-Durchfluss. Eingefrorener Wert führt zu falscher Dosierung.",
            },
            {
                "funktion_id": "KOMP-028-F1",
                "fehler_id": "KOMP-028-F1-FM2",
                "fehlermodus": "Signalausfall – Regler blind",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-028-F1-FM2-UC1", "beschreibung": "Leitung oder Messumformer", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Unkontrollierte Dosierung"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Charge"),
                    "kosten": ("Bis 100.000 €", "-"),
                },
                "controls": [
                    {"name": "TIC-401 / PIC-402", "typ": "Sensor", "wirkung": "B", "beschreibung": "Abweichung erkennbar", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Dosierung unbekannt.",
                "begruendung_O": "Signalausfall gelegentlich.",
                "begruendung_D": "TIC/PIC mit Verzögerung.",
                "kontext_beschreibung": "FIC-405-Ausfall; TIC/PIC als Rückfallebene.",
            },
        ],
    },

    # ─── KOMP-029: LI-201 (Level Indicator – Füllstand VB-201, hydrostatisch) ───
    "KOMP-029": {
        "functions": [
            {
                "funktion_id": "KOMP-029-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "LI-201 – Füllstand Vorlagebehälter VB-201 (Ethanol) anzeigen, 0–200 L, hydrostatisch, 4–20 mA",
                "anforderungen": [
                    {"id": "KOMP-029-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 200 L"},
                    {"id": "KOMP-029-F1-A2", "parameter": "Messprinzip", "sollwert": "Hydrostatisch"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-029-F1",
                "fehler_id": "KOMP-029-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Drift – Füllstand falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-029-F1-FM1-UC1", "beschreibung": "Sensor, Druckleitung oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Trockenlauf P-201 möglich bei leerem Behälter unerkannt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Pumpe, Charge"),
                    "kosten": ("Bis 20.000 €", "Pumpe, Charge"),
                },
                "controls": [
                    {"name": "LSLL-201", "typ": "Sensor", "wirkung": "O", "sil_level": "SIL-1", "beschreibung": "Trockenlaufschutz bei 20 L unabhängig von LI", "beeinflusst": "O"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "LSLL schützt Pumpe; ohne LSLL höher.",
                "begruendung_O": "Drift/Frozen Value gelegentlich.",
                "begruendung_D": "Keine Plausibilitätsprüfung.",
                "kontext_beschreibung": "LI-201 (Level Indicator) zeigt Füllstand VB-201. LSLL-201 ist Sicherheitsebene für Trockenlauf.",
            },
            {
                "funktion_id": "KOMP-029-F1",
                "fehler_id": "KOMP-029-F1-FM2",
                "fehlermodus": "Signalausfall – Füllstand unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-029-F1-FM2-UC1", "beschreibung": "Leitung oder Messumformer", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Gering", "Blinde Dosierung; LSLL schützt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Betrieb unsicher ohne Anzeige"),
                    "kosten": ("Bis 20.000 €", "Charge bei Fehlbedienung"),
                },
                "controls": [
                    {"name": "LSLL-201", "typ": "Sensor", "wirkung": "O", "beschreibung": "Trockenlaufschutz", "beeinflusst": "O"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "LSLL verhindert Trockenlauf.",
                "begruendung_O": "Signalausfall gelegentlich.",
                "begruendung_D": "Ausfall oft erkennbar (Anzeige fehlt).",
                "kontext_beschreibung": "LI-Ausfall; LSLL-201 bleibt wirksam.",
            },
        ],
    },

    # ─── KOMP-030: LI-202 (Level Indicator – Füllstand VB-202) ───
    "KOMP-030": {
        "functions": [
            {
                "funktion_id": "KOMP-030-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "LI-202 – Füllstand Vorlagebehälter VB-202 (Essigsäure) anzeigen, 0–200 L, hydrostatisch",
                "anforderungen": [
                    {"id": "KOMP-030-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 200 L"},
                    {"id": "KOMP-030-F1-A2", "parameter": "Messprinzip", "sollwert": "Hydrostatisch"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-030-F1",
                "fehler_id": "KOMP-030-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Drift – Füllstand falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-030-F1-FM1-UC1", "beschreibung": "Sensor oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Trockenlauf P-202 möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Pumpe, Charge"),
                    "kosten": ("Bis 20.000 €", "Pumpe, Charge"),
                },
                "controls": [
                    {"name": "LSLL-202", "typ": "Sensor", "wirkung": "O", "sil_level": "SIL-1", "beschreibung": "Trockenlaufschutz bei 20 L", "beeinflusst": "O"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "LSLL schützt Pumpe.",
                "begruendung_O": "Drift gelegentlich.",
                "begruendung_D": "Keine Plausibilitätsprüfung.",
                "kontext_beschreibung": "LI-202 zeigt Füllstand VB-202; LSLL-202 ist Sicherheitsebene.",
            },
            {
                "funktion_id": "KOMP-030-F1",
                "fehler_id": "KOMP-030-F1-FM2",
                "fehlermodus": "Signalausfall – Füllstand unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-030-F1-FM2-UC1", "beschreibung": "Leitung oder Messumformer", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Gering", "LSLL schützt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Betrieb ohne Anzeige"),
                    "kosten": ("Bis 20.000 €", "-"),
                },
                "controls": [
                    {"name": "LSLL-202", "typ": "Sensor", "wirkung": "O", "beschreibung": "Trockenlaufschutz", "beeinflusst": "O"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "LSLL verhindert Trockenlauf.",
                "begruendung_O": "Signalausfall gelegentlich.",
                "begruendung_D": "Ausfall erkennbar.",
                "kontext_beschreibung": "LI-202-Ausfall; LSLL-202 bleibt wirksam.",
            },
        ],
    },

    # ─── KOMP-031: LSLL-201 (Level Switch Low Low – Trockenlaufschutz VB-201, SIL-1) ───
    "KOMP-031": {
        "functions": [
            {
                "funktion_id": "KOMP-031-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "LSLL-201 – Trockenlaufschutz Pumpe P-201 bei 20 L Füllstand VB-201, Schaltpunkt 20 L, Vibration, SIL-1",
                "anforderungen": [
                    {"id": "KOMP-031-F1-A1", "parameter": "Schaltpunkt", "sollwert": "20 L"},
                    {"id": "KOMP-031-F1-A2", "parameter": "Funktion", "sollwert": "Trockenlaufschutz Pumpe"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-031-F1",
                "fehler_id": "KOMP-031-F1-FM1",
                "fehlermodus": "Fail-to-trip – schaltet nicht bei 20 L (Pumpe läuft trocken)",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-031-F1-FM1-UC1", "beschreibung": "Vibrationsschalter verklebt oder falsch kalibriert", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Funktionsprüfung"},
                    {"ursache_id": "KOMP-031-F1-FM1-UC2", "beschreibung": "Verkabelung oder Relais defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Gering", "Pumpe beschädigt, Ethanol-Dosierung ausgefallen"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "P-201 Trockenlauf, Membran/Antrieb"),
                    "kosten": ("Bis 50.000 €", "Pumpe, Charge"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Pumpe und Charge; kein Personenschaden.",
                "begruendung_O": "Fail-to-trip gelegentlich.",
                "begruendung_D": "Keine Online-Prüfung; nur periodische Prüfung.",
                "kontext_beschreibung": "LSLL-201 (Level Switch Low Low) schützt P-201 vor Trockenlauf. Versagen bedeutet Pumpe kann trocken laufen.",
            },
            {
                "funktion_id": "KOMP-031-F1",
                "fehler_id": "KOMP-031-F1-FM2",
                "fehlermodus": "Frühzeitiges Ansprechen – schaltet bei ausreichendem Füllstand ab",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-031-F1-FM2-UC1", "beschreibung": "Falsche Kalibrierung oder Verschmutzung", "herkunft": "Wartung", "phase": "Wartung", "hinweis": "Prüfung Schaltpunkt"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Dosierung gestoppt unnötig, Charge"),
                    "kosten": ("Bis 20.000 €", "Charge"),
                },
                "controls": [],
                "S": 4, "O": 3, "D": 5,
                "begruendung_S": "Nur Produktionsausfall.",
                "begruendung_O": "Gelegentlich.",
                "begruendung_D": "Erst bei Abschaltung erkennbar.",
                "kontext_beschreibung": "LSLL spricht zu früh an; Dosierung stoppt obwohl Vorlage voll.",
            },
        ],
    },

    # ─── KOMP-032: LSLL-202 (Level Switch Low Low – Trockenlaufschutz VB-202, SIL-1) ───
    "KOMP-032": {
        "functions": [
            {
                "funktion_id": "KOMP-032-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "LSLL-202 – Trockenlaufschutz Pumpe P-202 bei 20 L Füllstand VB-202, Schaltpunkt 20 L, Vibration, SIL-1",
                "anforderungen": [
                    {"id": "KOMP-032-F1-A1", "parameter": "Schaltpunkt", "sollwert": "20 L"},
                    {"id": "KOMP-032-F1-A2", "parameter": "Funktion", "sollwert": "Trockenlaufschutz Pumpe"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-032-F1",
                "fehler_id": "KOMP-032-F1-FM1",
                "fehlermodus": "Fail-to-trip – schaltet nicht bei 20 L (Pumpe läuft trocken)",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-032-F1-FM1-UC1", "beschreibung": "Vibrationsschalter verklebt oder falsch kalibriert", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Funktionsprüfung"},
                    {"ursache_id": "KOMP-032-F1-FM1-UC2", "beschreibung": "Verkabelung oder Relais defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wiring"},
                ],
                "effects": {
                    "mensch": ("Gering", "Pumpe P-202 beschädigt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "P-202 Trockenlauf"),
                    "kosten": ("Bis 50.000 €", "Pumpe, Charge"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "Pumpe und Charge.",
                "begruendung_O": "Fail-to-trip gelegentlich.",
                "begruendung_D": "Keine Online-Prüfung.",
                "kontext_beschreibung": "LSLL-202 schützt P-202 vor Trockenlauf.",
            },
            {
                "funktion_id": "KOMP-032-F1",
                "fehler_id": "KOMP-032-F1-FM2",
                "fehlermodus": "Frühzeitiges Ansprechen – schaltet bei ausreichendem Füllstand ab",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-032-F1-FM2-UC1", "beschreibung": "Falsche Kalibrierung oder Verschmutzung", "herkunft": "Wartung", "phase": "Wartung", "hinweis": "Prüfung"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Dosierung gestoppt unnötig"),
                    "kosten": ("Bis 20.000 €", "Charge"),
                },
                "controls": [],
                "S": 4, "O": 3, "D": 5,
                "begruendung_S": "Nur Produktionsausfall.",
                "begruendung_O": "Gelegentlich.",
                "begruendung_D": "Bei Abschaltung erkennbar.",
                "kontext_beschreibung": "LSLL spricht zu früh an.",
            },
        ],
    },

    # ─── KOMP-033: Auffangwanne AW-200 (500 L, Leckagesensor) ───
    "KOMP-033": {
        "functions": [
            {
                "funktion_id": "KOMP-033-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Auffangwanne AW-200 – Leckagen unter Dosiersystem auffangen, 500 L, Edelstahl 1.4571, Leckagesensor",
                "anforderungen": [
                    {"id": "KOMP-033-F1-A1", "parameter": "Volumen", "sollwert": "500 L"},
                    {"id": "KOMP-033-F1-A2", "parameter": "Leckagesensor", "sollwert": "Ja"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-033-F1",
                "fehler_id": "KOMP-033-F1-FM1",
                "fehlermodus": "Leckagesensor ausgefallen – Leckage unerkannt",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-033-F1-FM1-UC1", "beschreibung": "Sensor defekt, Verkabelung oder Auswertefehler", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Funktionsprüfung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Leckage (Ethanol/Essigsäure/Schwefelsäure) unerkannt, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Ausbreitung außerhalb Wanne möglich"),
                    "anlage": ("Teilausfall", "Sicherheit reduziert"),
                    "kosten": ("Bis 100.000 €", "Folgeschaden"),
                },
                "controls": [],
                "S": 8, "O": 3, "D": 5,
                "begruendung_S": "Gefahrstoffe in Ex-Zone; ohne Alarm Ausbreitung möglich.",
                "begruendung_O": "Sensorausfall gelegentlich.",
                "begruendung_D": "Keine Prüfung ob Sensor anspricht außer periodisch.",
                "kontext_beschreibung": "AW-200 fängt Leckagen auf; Leckagesensor muss Alarm auslösen. Sensorausfall bedeutet Leckage kann unerkannt bleiben.",
            },
            {
                "funktion_id": "KOMP-033-F1",
                "fehler_id": "KOMP-033-F1-FM2",
                "fehlermodus": "Überfüllung Auffangwanne – 500 L überschritten",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-033-F1-FM2-UC1", "beschreibung": "Große Leckage oder mehrere Leckagen, Wanne nicht rechtzeitig geleert", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Betriebsanweisung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Überlauf, Gefahrstoffe in Halle"),
                    "umwelt": ("Betriebsbereich", "Kontamination"),
                    "anlage": ("Teilausfall", "Reinigung, Stillstand"),
                    "kosten": ("Bis 100.000 €", "Reinigung, Stillstand"),
                },
                "controls": [
                    {"name": "Leckagesensor", "typ": "Sensor", "wirkung": "B", "beschreibung": "Alarm bei Füllstand in Wanne", "beeinflusst": "D"},
                ],
                "S": 8, "O": 2, "D": 4,
                "begruendung_S": "Überlauf in Ex-Zone mit Gefahrstoffen.",
                "begruendung_O": "Große Leckage selten.",
                "begruendung_D": "Leckagesensor und Betriebsüberwachung.",
                "kontext_beschreibung": "Auffangwanne hat begrenztes Volumen; Überfüllung muss verhindert werden.",
            },
        ],
    },

    # ─── KOMP-034: Mediensystem MS-300 (System – Dampf, Kühlwasser, Vakuum, Stickstoff) ───
    "KOMP-034": {
        "functions": [
            {
                "funktion_id": "KOMP-034-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Mediensystem MS-300 – Versorgung Synthesereaktor R-101 mit Dampf (6 bar), Kühlwasser (15 °C), Vakuum (0.1 bar abs), Stickstoff (5 bar)",
                "anforderungen": [
                    {"id": "KOMP-034-F1-A1", "parameter": "Dampf", "sollwert": "Sattdampf 6 bar"},
                    {"id": "KOMP-034-F1-A2", "parameter": "Kühlwasser", "sollwert": "Kreislauf 15 °C"},
                    {"id": "KOMP-034-F1-A3", "parameter": "Stickstoff", "sollwert": "Rohrnetz 5 bar"},
                    {"id": "KOMP-034-F1-A4", "parameter": "Vakuum", "sollwert": "0.1 bar abs"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-034-F1",
                "fehler_id": "KOMP-034-F1-FM1",
                "fehlermodus": "Verlust Kühlwasserversorgung – Reaktor nicht kühlbar",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-034-F1-FM1-UC1", "beschreibung": "KW-301 Ausfall, Leitung oder Pumpe", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Notkühlung NK-301"},
                    {"ursache_id": "KOMP-034-F1-FM1-UC2", "beschreibung": "Fouling, Verstopfung Kühlkreislauf", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wasseraufbereitung"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Runaway, Überdruck, Ex-Zone"),
                    "umwelt": ("Betriebsbereich", "Medienfreisetzung"),
                    "anlage": ("Totalausfall", "Reaktor überhitzt, Bersten möglich"),
                    "kosten": ("Bis 1 Mio €", "-"),
                },
                "controls": [
                    {"name": "Notkühlsystem NK-301", "typ": "Thermisch", "wirkung": "O", "beschreibung": "Sole -10 °C Backup", "beeinflusst": "O"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturalarm Reaktor", "beeinflusst": "D"},
                    {"name": "PSV-410 / BSV-411", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Druckentlastung", "beeinflusst": "S"},
                ],
                "S": 10, "O": 2, "D": 3,
                "begruendung_S": "Verlust Kühlung kann Runaway auslösen.",
                "begruendung_O": "Komplettausfall Kühlung selten; NK-301 Backup.",
                "begruendung_D": "TIC-401 und Drucküberwachung erkennen Abweichung.",
                "kontext_beschreibung": "MS-300 versorgt Reaktor. Kühlwasserausfall ist kritisch; NK-301 ist Rückfallebene.",
            },
            {
                "funktion_id": "KOMP-034-F1",
                "fehler_id": "KOMP-034-F1-FM2",
                "fehlermodus": "Dampfversorgung ausgefallen – Heizung Reaktor nicht verfügbar",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-034-F1-FM2-UC1", "beschreibung": "DV-301 oder DV-302 Störung, Leckage", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kondensatableiter"},
                ],
                "effects": {
                    "mensch": ("Keine", "Keine unmittelbare Gefahr"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Charge nicht auf Temperatur, Produktionsausfall"),
                    "kosten": ("Bis 50.000 €", "Charge, Stillstand"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Nur Produktionsausfall.",
                "begruendung_O": "Dampfausfall gelegentlich.",
                "begruendung_D": "Temperatur bleibt niedrig, erkennbar.",
                "kontext_beschreibung": "Dampfausfall verhindert Aufheizen; keine Sicherheitsfolge.",
            },
        ],
    },

    # ─── KOMP-035: Dampfversorgung DV-301 (Dampfnetz 6 bar, 160 °C, 500 kg/h) ───
    "KOMP-035": {
        "functions": [
            {
                "funktion_id": "KOMP-035-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Dampfversorgung DV-301 – Sattdampf 6 bar, 160 °C, max. 500 kg/h, für Heizmantel R-101",
                "anforderungen": [
                    {"id": "KOMP-035-F1-A1", "parameter": "Druck", "sollwert": "6 bar"},
                    {"id": "KOMP-035-F1-A2", "parameter": "Temperatur", "sollwert": "160 °C"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-035-F1",
                "fehler_id": "KOMP-035-F1-FM1",
                "fehlermodus": "Kein Stoffstrom (No Flow) – Dampf unterbrochen",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-035-F1-FM1-UC1", "beschreibung": "Leitung, Ventil oder Dampferzeuger", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "PI-301, TI-301"},
                ],
                "effects": {
                    "mensch": ("Keine", "-"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktor nicht heizbar, Charge"),
                    "kosten": ("Bis 50.000 €", "Charge"),
                },
                "controls": [
                    {"name": "PI-301 / TI-301", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druck/Temperatur Dampfeingang", "beeinflusst": "D"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Nur Produktionsausfall.",
                "begruendung_O": "Dampfausfall gelegentlich.",
                "begruendung_D": "PI/TI zeigen Abweichung.",
                "kontext_beschreibung": "DV-301 liefert Dampf für R-101. Ausfall = keine Heizung.",
            },
            {
                "funktion_id": "KOMP-035-F1",
                "fehler_id": "KOMP-035-F1-FM2",
                "fehlermodus": "Mehr Druck (High Pressure) – Überdruck Dampfleitung",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-035-F1-FM2-UC1", "beschreibung": "Regelventil oder Dampferzeuger", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "PSV-310"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Dampfleitung, Verbrennungsgefahr"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Leitung, DV-302"),
                    "kosten": ("Bis 100.000 €", "Reparatur"),
                },
                "controls": [
                    {"name": "PSV-310", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Sicherheitsventil Dampfverteiler 7 bar", "beeinflusst": "S"},
                    {"name": "PI-301", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druckanzeige", "beeinflusst": "D"},
                ],
                "S": 7, "O": 2, "D": 4,
                "begruendung_S": "Überdruck Dampf gefährlich.",
                "begruendung_O": "Überdruck selten.",
                "begruendung_D": "PI-301 und PSV-310.",
                "kontext_beschreibung": "PSV-310 entlastet bei Überdruck; PI-301 überwacht.",
            },
        ],
    },

    # ─── KOMP-036: Dampfverteiler DV-302 (4× DN25, Kondensatableiter) ───
    "KOMP-036": {
        "functions": [
            {
                "funktion_id": "KOMP-036-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Dampfverteiler DV-302 – Verteilung Sattdampf an Verbraucher, 4× DN25, kondensatableiter thermodynamisch",
                "anforderungen": [
                    {"id": "KOMP-036-F1-A1", "parameter": "Anschlüsse", "sollwert": "4 x DN25"},
                    {"id": "KOMP-036-F1-A2", "parameter": "Kondensatableiter", "sollwert": "Thermodynamisch"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-036-F1",
                "fehler_id": "KOMP-036-F1-FM1",
                "fehlermodus": "Leckage – Dampf oder Kondensat austretend",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-036-F1-FM1-UC1", "beschreibung": "Flansch, Kondensatableiter oder Rohr undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Verbrennung durch Dampf"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Druckverlust, Heizung beeinträchtigt"),
                    "kosten": ("Bis 50.000 €", "Reparatur"),
                },
                "controls": [
                    {"name": "PI-301", "typ": "Sensor", "wirkung": "B", "beschreibung": "Drucküberwachung", "beeinflusst": "D"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "Dampf verbrennungsgefährlich.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Druckabfall erkennbar.",
                "kontext_beschreibung": "DV-302 verteilt Dampf; Leckage muss erkannt werden.",
            },
            {
                "funktion_id": "KOMP-036-F1",
                "fehler_id": "KOMP-036-F1-FM2",
                "fehlermodus": "Verstopfung Kondensatableiter – Dampf entweicht mit Kondensat",
                "fehlerart": "Equipment",
                "causes": [
                    {"ursache_id": "KOMP-036-F1-FM2-UC1", "beschreibung": "Ablagerungen, Verschmutzung", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Wartung Kondensatableiter"},
                ],
                "effects": {
                    "mensch": ("Gering", "Wirkungsgradverlust"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Heizleistung reduziert"),
                    "kosten": ("Bis 20.000 €", "Energie, Nacharbeit"),
                },
                "controls": [],
                "S": 4, "O": 4, "D": 5,
                "begruendung_S": "Nur Leistungsverlust.",
                "begruendung_O": "Verstopfung gelegentlich.",
                "begruendung_D": "Schlecht erkennbar.",
                "kontext_beschreibung": "Kondensatableiter müssen Kondensat abführen; Verstopfung reduziert Wärmeübergang.",
            },
        ],
    },

    # ─── KOMP-037: Kühlwasserversorgung KW-301 (15 °C Vorlauf, 25 °C Rücklauf, 3 bar, 10 m³/h) ───
    "KOMP-037": {
        "functions": [
            {
                "funktion_id": "KOMP-037-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Kühlwasserversorgung KW-301 – Vorlauf 15 °C, Rücklauf 25 °C, 3 bar, max. 10 m³/h für Reaktor/Kondensatoren",
                "anforderungen": [
                    {"id": "KOMP-037-F1-A1", "parameter": "Vorlauf", "sollwert": "15 °C"},
                    {"id": "KOMP-037-F1-A2", "parameter": "Druck", "sollwert": "3 bar"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-037-F1",
                "fehler_id": "KOMP-037-F1-FM1",
                "fehlermodus": "Kein Stoffstrom (No Flow) – Kühlwasser ausgefallen",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-037-F1-FM1-UC1", "beschreibung": "Pumpe, Leitung oder Verstopfung", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "NK-301 Backup"},
                    {"ursache_id": "KOMP-037-F1-FM1-UC2", "beschreibung": "Wasseraufbereitung, Fouling", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Monatlich prüfen"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Reaktor nicht kühlbar, Runaway"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Totalausfall", "Reaktor überhitzt"),
                    "kosten": ("Bis 1 Mio €", "-"),
                },
                "controls": [
                    {"name": "Notkühlsystem NK-301", "typ": "Thermisch", "wirkung": "O", "beschreibung": "Sole -10 °C Backup", "beeinflusst": "O"},
                    {"name": "TI-302 / TI-303", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vorlauf/Rücklauf Temperatur", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Reaktortemperatur", "beeinflusst": "D"},
                ],
                "S": 10, "O": 2, "D": 3,
                "begruendung_S": "Kühlausfall kann Runaway auslösen.",
                "begruendung_O": "NK-301 reduziert O.",
                "begruendung_D": "TI-302/303 und TIC-401 erkennen.",
                "kontext_beschreibung": "KW-301 ist primäre Kühlung; NK-301 Backup.",
            },
            {
                "funktion_id": "KOMP-037-F1",
                "fehler_id": "KOMP-037-F1-FM2",
                "fehlermodus": "Weniger Durchfluss / höhere Rücklauftemperatur",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-037-F1-FM2-UC1", "beschreibung": "Fouling, Verstopfung, Pumpe defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "TI-302, TI-303"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Reduzierte Kühlleistung, Runaway möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktor schwerer kühlbar"),
                    "kosten": ("Bis 100.000 €", "Reaktor, Charge"),
                },
                "controls": [
                    {"name": "TI-302 / TI-303", "typ": "Sensor", "wirkung": "B", "beschreibung": "Temperaturüberwachung", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Reaktortemperatur", "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Reduzierte Kühlung erhöht Runaway-Risiko.",
                "begruendung_O": "Fouling/Verstopfung gelegentlich.",
                "begruendung_D": "Temperaturanstieg erkennbar.",
                "kontext_beschreibung": "Durchfluss/Temperatur werden überwacht.",
            },
        ],
    },

    # ─── KOMP-038: Notkühlsystem NK-301 (Sole -10 °C, Ethylenglykol 30 %, 5 m³/h) ───
    "KOMP-038": {
        "functions": [
            {
                "funktion_id": "KOMP-038-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Notkühlsystem NK-301 – Solekreislauf -10 °C, Ethylenglykol 30 %, 3 bar, max. 5 m³/h, Backup bei KW-301-Ausfall",
                "anforderungen": [
                    {"id": "KOMP-038-F1-A1", "parameter": "Temperatur", "sollwert": "-10 °C"},
                    {"id": "KOMP-038-F1-A2", "parameter": "MaxDurchsatz", "sollwert": "5 m³/h"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-038-F1",
                "fehler_id": "KOMP-038-F1-FM1",
                "fehlermodus": "Fail-to-start / No Flow – Notkühlung schaltet nicht zu oder fördert nicht",
                "fehlerart": "Thermisch",
                "causes": [
                    {"ursache_id": "KOMP-038-F1-FM1-UC1", "beschreibung": "Pumpe, Ventil oder Steuerung defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Funktionsprüfung"},
                    {"ursache_id": "KOMP-038-F1-FM1-UC2", "beschreibung": "Sole zu warm oder Leckage", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Regelmäßige Prüfung"},
                ],
                "effects": {
                    "mensch": ("Lebensgefahr", "Bei KW-301-Ausfall keine Backup-Kühlung, Runaway"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Totalausfall", "Reaktor nicht kühlbar"),
                    "kosten": ("Bis 1 Mio €", "-"),
                },
                "controls": [
                    {"name": "KW-301", "typ": "Prozess", "wirkung": "O", "beschreibung": "Primäre Kühlung", "beeinflusst": "O"},
                    {"name": "TIC-401 / PSV-410", "typ": "Sensor/Sicherheit", "wirkung": "B/E", "beschreibung": "Temperatur/Druck", "beeinflusst": "D/S"},
                ],
                "S": 10, "O": 2, "D": 5,
                "begruendung_S": "Notkühlung ist letzte Kühlebene bei KW-Ausfall.",
                "begruendung_O": "NK nur bei KW-Ausfall gefordert; Fail-to-start selten.",
                "begruendung_D": "Keine Online-Prüfung ob NK anläuft; nur periodische Prüfung.",
                "kontext_beschreibung": "NK-301 ist Backup für KW-301. Versagen bei Bedarf katastrophal.",
                "controls_einschraenkung": "Periodische Funktionsprüfung zwingend.",
            },
            {
                "funktion_id": "KOMP-038-F1",
                "fehler_id": "KOMP-038-F1-FM2",
                "fehlermodus": "Leckage – Sole austretend",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-038-F1-FM2-UC1", "beschreibung": "Dichtung, Schlauch oder Flansch", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Gering", "Ethylenglykol umweltrelevant, rutschig"),
                    "umwelt": ("Betriebsbereich", "Auffang"),
                    "anlage": ("Teilausfall", "NK nicht einsatzbereit"),
                    "kosten": ("Bis 50.000 €", "Nachfüllung, Reparatur"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Kein Personenschaden; NK-Verlust kritisch für Backup.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Oft erst bei Prüfung erkennbar.",
                "kontext_beschreibung": "Leckage reduziert Solemenge; NK kann bei Bedarf versagen.",
            },
        ],
    },

    # ─── KOMP-039: Vakuumpumpe VP-301 (Flüssigkeitsring, 0.1 bar abs, 100 m³/h, 4 kW) ───
    "KOMP-039": {
        "functions": [
            {
                "funktion_id": "KOMP-039-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Vakuumpumpe VP-301 – Flüssigkeitsring-Vakuumpumpe, Enddruck 0.1 bar (abs), 100 m³/h, 4 kW, Sperrflüssigkeit Wasser",
                "anforderungen": [
                    {"id": "KOMP-039-F1-A1", "parameter": "Enddruck", "sollwert": "0.1 bar (abs)"},
                    {"id": "KOMP-039-F1-A2", "parameter": "Saugleistung", "sollwert": "100 m³/h"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-039-F1",
                "fehler_id": "KOMP-039-F1-FM1",
                "fehlermodus": "Vakuumverlust – Enddruck nicht erreichbar oder Anstieg",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-039-F1-FM1-UC1", "beschreibung": "Pumpe verschlissen, Sperrflüssigkeit mangelhaft", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Ölwechsel 3000 h"},
                    {"ursache_id": "KOMP-039-F1-FM1-UC2", "beschreibung": "Leckage in Saugleitung oder Behälter", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "PI-304"},
                ],
                "effects": {
                    "mensch": ("Gering", "Unterdruck im Reaktor ggf. nicht möglich, Implosion bei VSV-Ausfall"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Destillation beeinträchtigt, Siedepunkt"),
                    "kosten": ("Bis 50.000 €", "Charge, Pumpe"),
                },
                "controls": [
                    {"name": "PI-304", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vakuumanzeige 0–1 bar (abs)", "beeinflusst": "D"},
                    {"name": "VSV-412", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Vakuumbrecher -0.8 bar", "beeinflusst": "S"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "VSV schützt vor Implosion; Vakuumverlust vor allem Prozess.",
                "begruendung_O": "Verschleiß gelegentlich.",
                "begruendung_D": "PI-304 zeigt Vakuum.",
                "kontext_beschreibung": "VP-301 erzeugt Vakuum für Destillation. PI-304 überwacht; VSV-412 schützt Reaktor.",
            },
            {
                "funktion_id": "KOMP-039-F1",
                "fehler_id": "KOMP-039-F1-FM2",
                "fehlermodus": "Äußere Leckage – Sperrflüssigkeit oder Prozessgas",
                "fehlerart": "Mechanisch",
                "causes": [
                    {"ursache_id": "KOMP-039-F1-FM2-UC1", "beschreibung": "Wellendichtung, Flansch oder Schlauch", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Gering", "Kontamination, Geruch"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Pumpe außer Betrieb"),
                    "kosten": ("Bis 30.000 €", "Reparatur"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Kein schwerer Personenschaden.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Oft erst bei Inspektion.",
                "kontext_beschreibung": "Leckage an VP-301; Betrieb muss sichern.",
            },
        ],
    },

    # ─── KOMP-040: Stickstoffversorgung N2-301 (5 bar, 99.9 %, 50 Nm³/h) ───
    "KOMP-040": {
        "functions": [
            {
                "funktion_id": "KOMP-040-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Stickstoffversorgung N2-301 – Inertgas 5 bar, 99.9 % Reinheit, max. 50 Nm³/h für Spülung/Blanketing",
                "anforderungen": [
                    {"id": "KOMP-040-F1-A1", "parameter": "Druck", "sollwert": "5 bar"},
                    {"id": "KOMP-040-F1-A2", "parameter": "Reinheit", "sollwert": "99.9 %"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-040-F1",
                "fehler_id": "KOMP-040-F1-FM1",
                "fehlermodus": "Kein Stoffstrom (No Flow) – Stickstoff nicht verfügbar",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-040-F1-FM1-UC1", "beschreibung": "Leitung, Ventil oder Tank leer", "herkunft": "Betrieb", "phase": "Betrieb", "hinweis": "Bestandsüberwachung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Sauerstoffeintritt, ggf. explosive Atmosphäre"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Spülung/Blanketing nicht möglich"),
                    "kosten": ("Bis 100.000 €", "Bei Folgeschaden"),
                },
                "controls": [
                    {"name": "Drucküberwachung N2", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druck im Rohrnetz", "beeinflusst": "D"},
                ],
                "S": 7, "O": 2, "D": 4,
                "begruendung_S": "Inertisierung kann fehlen; Explosionsrisiko in Ex-Zone.",
                "begruendung_O": "N2-Ausfall selten.",
                "begruendung_D": "Druckabfall erkennbar.",
                "kontext_beschreibung": "N2-301 versorgt Inertgas; Ausfall kann Sauerstoffeintritt bedeuten.",
            },
            {
                "funktion_id": "KOMP-040-F1",
                "fehler_id": "KOMP-040-F1-FM2",
                "fehlermodus": "Leckage – Stickstoff entweicht",
                "fehlerart": "Prozess",
                "causes": [
                    {"ursache_id": "KOMP-040-F1-FM2-UC1", "beschreibung": "Ventil, Flansch oder Schlauch undicht", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Inspektion"},
                ],
                "effects": {
                    "mensch": ("Gering", "Erstickungsgefahr nur in geschlossenen Räumen bei großer Leckage"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Druckverlust, Inertisierung beeinträchtigt"),
                    "kosten": ("Bis 20.000 €", "Verlust, Nachfüllung"),
                },
                "controls": [],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "N2 nicht toxisch; Erstickung nur lokal möglich.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Druckabfall erkennbar.",
                "kontext_beschreibung": "Leckage reduziert N2-Druck; Betrieb überwacht.",
            },
        ],
    },

    # ─── KOMP-041: PI-301 (Druckanzeige Dampfeingang, 0–10 bar, lokal) ───
    "KOMP-041": {
        "functions": [
            {
                "funktion_id": "KOMP-041-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "PI-301 – Druckanzeige Dampfeingang MS-300, 0–10 bar, lokale Anzeige",
                "anforderungen": [
                    {"id": "KOMP-041-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 10 bar"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-041-F1",
                "fehler_id": "KOMP-041-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Drift – Druck falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-041-F1-FM1-UC1", "beschreibung": "Instrument defekt oder Impulsleitung verstopft", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Überdruck unerkannt möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Dampfleitung, DV-302"),
                    "kosten": ("Bis 50.000 €", "Bei Überdruckfolge"),
                },
                "controls": [
                    {"name": "PSV-310", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Sicherheitsventil 7 bar", "beeinflusst": "S"},
                ],
                "S": 6, "O": 3, "D": 5,
                "begruendung_S": "PSV-310 schützt; PI nur Anzeige.",
                "begruendung_O": "Drift gelegentlich.",
                "begruendung_D": "Lokal, keine automatische Plausibilität.",
                "kontext_beschreibung": "PI-301 (Pressure Indicator) zeigt Dampfdruck; PSV-310 ist Sicherheit.",
            },
            {
                "funktion_id": "KOMP-041-F1",
                "fehler_id": "KOMP-041-F1-FM2",
                "fehlermodus": "Signalausfall – Druck unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-041-F1-FM2-UC1", "beschreibung": "Instrument oder Anzeige defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Ersatz"},
                ],
                "effects": {
                    "mensch": ("Gering", "Blinde Leitung; PSV schützt"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Betrieb ohne lokale Anzeige"),
                    "kosten": ("Bis 10.000 €", "Instrument"),
                },
                "controls": [
                    {"name": "PSV-310", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Druckentlastung", "beeinflusst": "S"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "PSV bleibt wirksam.",
                "begruendung_O": "Ausfall gelegentlich.",
                "begruendung_D": "Ausfall sichtbar (Anzeige fehlt).",
                "kontext_beschreibung": "PI-Ausfall; PSV-310 unabhängig.",
            },
        ],
    },

    # ─── KOMP-042: TI-301 (Temperaturanzeige Dampfeingang, 0–200 °C, lokal) ───
    "KOMP-042": {
        "functions": [
            {
                "funktion_id": "KOMP-042-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "TI-301 – Temperaturanzeige Dampfeingang MS-300, 0–200 °C, lokale Anzeige",
                "anforderungen": [
                    {"id": "KOMP-042-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 200 °C"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-042-F1",
                "fehler_id": "KOMP-042-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Drift – Temperatur falsch angezeigt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-042-F1-FM1-UC1", "beschreibung": "Fühler oder Anzeige defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Dampfqualität unerkannt, Verbrennungsgefahr unverändert"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Heizleistung ggf. falsch eingeschätzt"),
                    "kosten": ("Bis 20.000 €", "Charge"),
                },
                "controls": [],
                "S": 4, "O": 3, "D": 5,
                "begruendung_S": "Nur Anzeige; Dampf bleibt heiß.",
                "begruendung_O": "Drift gelegentlich.",
                "begruendung_D": "Keine Plausibilität.",
                "kontext_beschreibung": "TI-301 zeigt Dampftemperatur; Ausfall betrifft nur Anzeige.",
            },
        ],
    },

    # ─── KOMP-043: PI-302 (Druckanzeige Kühlwasser, 0–6 bar, 4–20 mA) ───
    "KOMP-043": {
        "functions": [
            {
                "funktion_id": "KOMP-043-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "PI-302 – Druckanzeige Kühlwasser MS-300, 0–6 bar, 4–20 mA",
                "anforderungen": [
                    {"id": "KOMP-043-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 6 bar"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-043-F1",
                "fehler_id": "KOMP-043-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Signalausfall – Kühlwasserdruck unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-043-F1-FM1-UC1", "beschreibung": "Messumformer oder Leitung defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Kühlausfall unerkannt, Runaway möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "KW-301, Reaktor"),
                    "kosten": ("Bis 100.000 €", "Reaktor"),
                },
                "controls": [
                    {"name": "TI-302 / TI-303", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vorlauf/Rücklauf Temperatur", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Reaktortemperatur", "beeinflusst": "D"},
                    {"name": "NK-301", "typ": "Thermisch", "wirkung": "O", "beschreibung": "Notkühlung Backup", "beeinflusst": "O"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Druckabfall = Kühlausfall möglich; TI und TIC erkennen Temperatur.",
                "begruendung_O": "PI-Ausfall gelegentlich.",
                "begruendung_D": "TI-302/303 und TIC-401 indirekt.",
                "kontext_beschreibung": "PI-302 überwacht Kühlwasserdruck; Ausfall kann Kühlverlust verschleiern.",
            },
        ],
    },

    # ─── KOMP-044: TI-302 (Temperaturanzeige Kühlwasser Vorlauf, 0–50 °C, 4–20 mA) ───
    "KOMP-044": {
        "functions": [
            {
                "funktion_id": "KOMP-044-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "TI-302 – Temperaturanzeige Kühlwasser Vorlauf, 0–50 °C, 4–20 mA",
                "anforderungen": [
                    {"id": "KOMP-044-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 50 °C"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-044-F1",
                "fehler_id": "KOMP-044-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Signalausfall – Vorlauftemperatur unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-044-F1-FM1-UC1", "beschreibung": "Fühler oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Kühlleistung unerkannt reduziert, Runaway möglich"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Reaktor schwerer kühlbar"),
                    "kosten": ("Bis 100.000 €", "Reaktor"),
                },
                "controls": [
                    {"name": "TI-303", "typ": "Sensor", "wirkung": "B", "beschreibung": "Rücklauftemperatur", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Reaktortemperatur", "beeinflusst": "D"},
                    {"name": "NK-301", "typ": "Thermisch", "wirkung": "O", "beschreibung": "Notkühlung", "beeinflusst": "O"},
                ],
                "S": 7, "O": 3, "D": 4,
                "begruendung_S": "Kühlung kritisch; TIC und NK begrenzen.",
                "begruendung_O": "TI-Ausfall gelegentlich.",
                "begruendung_D": "TI-303 und TIC-401 indirekt.",
                "kontext_beschreibung": "TI-302 zeigt Kühlwasservorlauf; Ausfall verschleiert Kühlprobleme.",
            },
        ],
    },

    # ─── KOMP-045: TI-303 (Temperaturanzeige Kühlwasser Rücklauf) ───
    "KOMP-045": {
        "functions": [
            {
                "funktion_id": "KOMP-045-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "TI-303 – Temperaturanzeige Kühlwasser Rücklauf, 0–50 °C, 4–20 mA",
                "anforderungen": [
                    {"id": "KOMP-045-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 50 °C"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-045-F1",
                "fehler_id": "KOMP-045-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Signalausfall – Rücklauftemperatur unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-045-F1-FM1-UC1", "beschreibung": "Fühler oder Messumformer defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Kühlleistung unerkannt; TIC erkennt Reaktor"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "KW-301 Überwachung reduziert"),
                    "kosten": ("Bis 100.000 €", "Bei Runaway"),
                },
                "controls": [
                    {"name": "TI-302", "typ": "Sensor", "wirkung": "B", "beschreibung": "Vorlauftemperatur", "beeinflusst": "D"},
                    {"name": "TIC-401", "typ": "Sensor", "wirkung": "B", "beschreibung": "Reaktortemperatur", "beeinflusst": "D"},
                    {"name": "NK-301", "typ": "Thermisch", "wirkung": "O", "beschreibung": "Notkühlung", "beeinflusst": "O"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "TIC-401 und NK-301 begrenzen Folgen.",
                "begruendung_O": "TI-Ausfall gelegentlich.",
                "begruendung_D": "TI-302 und TIC indirekt.",
                "kontext_beschreibung": "TI-303 zeigt Rücklauf; Ausfall reduziert Überwachung, TIC bleibt.",
            },
        ],
    },

    # ─── KOMP-046: PI-304 (Vakuumanzeige, 0–1 bar abs, 4–20 mA) ───
    "KOMP-046": {
        "functions": [
            {
                "funktion_id": "KOMP-046-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "PI-304 – Vakuumanzeige Vakuumnetz MS-300, 0–1 bar (abs), 4–20 mA",
                "anforderungen": [
                    {"id": "KOMP-046-F1-A1", "parameter": "Messbereich", "sollwert": "0 bis 1 bar (abs)"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-046-F1",
                "fehler_id": "KOMP-046-F1-FM1",
                "fehlermodus": "Eingefrorener Messwert oder Signalausfall – Vakuum unbekannt",
                "fehlerart": "MSR",
                "causes": [
                    {"ursache_id": "KOMP-046-F1-FM1-UC1", "beschreibung": "Messumformer oder Leitung defekt", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Kalibrierung"},
                ],
                "effects": {
                    "mensch": ("Gering", "Vakuumverlust unerkannt; VSV-412 schützt vor Implosion"),
                    "umwelt": ("Keine", "-"),
                    "anlage": ("Teilausfall", "Destillation, VP-301"),
                    "kosten": ("Bis 50.000 €", "Charge"),
                },
                "controls": [
                    {"name": "VSV-412", "typ": "Sicherheit", "wirkung": "E", "beschreibung": "Vakuumbrecher -0.8 bar Reaktor", "beeinflusst": "S"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "VSV schützt Reaktor; PI nur Prozessüberwachung.",
                "begruendung_O": "PI-Ausfall gelegentlich.",
                "begruendung_D": "Keine Plausibilität.",
                "kontext_beschreibung": "PI-304 zeigt Vakuum im Netz; VSV-412 schützt Reaktor unabhängig.",
            },
        ],
    },

    # ─── KOMP-047: PSV-310 (Sicherheitsventil Dampfverteiler, 7 bar, DN25) ───
    "KOMP-047": {
        "functions": [
            {
                "funktion_id": "KOMP-047-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "PSV-310 – Druckentlastung Dampfverteiler DV-302 bei 7 bar, DN25",
                "anforderungen": [
                    {"id": "KOMP-047-F1-A1", "parameter": "Ansprechdruck", "sollwert": "7 bar"},
                    {"id": "KOMP-047-F1-A2", "parameter": "Nenndurchmesser", "sollwert": "DN25"},
                ],
            },
        ],
        "failure_modes": [
            {
                "funktion_id": "KOMP-047-F1",
                "fehler_id": "KOMP-047-F1-FM1",
                "fehlermodus": "Fail-to-open – öffnet nicht bei 7 bar (Überdruck Dampfleitung)",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-047-F1-FM1-UC1", "beschreibung": "Verklebung, Korrosion oder Fremdkörper", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Jährliche Prüfung"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung", "Bersten Dampfleitung, Verbrennung"),
                    "umwelt": ("Betriebsbereich", "Dampffreisetzung"),
                    "anlage": ("Totalausfall", "DV-302, Leitung"),
                    "kosten": ("Bis 100.000 €", "Reparatur, Stillstand"),
                },
                "controls": [
                    {"name": "PI-301", "typ": "Sensor", "wirkung": "B", "beschreibung": "Druckanzeige Dampf", "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 5,
                "begruendung_S": "Überdruck Dampf gefährlich; keine zweite mechanische Barriere.",
                "begruendung_O": "Verklebung in Dampfumgebung gelegentlich.",
                "begruendung_D": "Keine Online-Prüfung; nur periodische Prüfung.",
                "kontext_beschreibung": "PSV-310 schützt Dampfverteiler. Fail-to-open bedeutet Überdruck bis Bersten.",
                "controls_einschraenkung": "PI-301 nur Anzeige; regelmäßige PSV-Prüfung zwingend.",
            },
            {
                "funktion_id": "KOMP-047-F1",
                "fehler_id": "KOMP-047-F1-FM2",
                "fehlermodus": "Leckage / Dampf entweicht bei Normaldruck",
                "fehlerart": "Sicherheit",
                "causes": [
                    {"ursache_id": "KOMP-047-F1-FM2-UC1", "beschreibung": "Sitz undicht nach Abblasen oder Verschleiß", "herkunft": "Betrieb", "phase": "Wartung", "hinweis": "Sichtprüfung"},
                ],
                "effects": {
                    "mensch": ("Verletzungsgefahr", "Dampf austretend, Verbrennungsgefahr"),
                    "umwelt": ("Betriebsbereich", "-"),
                    "anlage": ("Teilausfall", "Druckverlust, Energieverlust"),
                    "kosten": ("Bis 30.000 €", "Reparatur, Wechsel"),
                },
                "controls": [],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "Dampf gefährlich; kein Bersten.",
                "begruendung_O": "Leckage gelegentlich.",
                "begruendung_D": "Druckverlust/Verbrauch erkennbar.",
                "kontext_beschreibung": "PSV leckt bei Normalbetrieb; muss gewechselt werden.",
            },
        ],
    },
}
