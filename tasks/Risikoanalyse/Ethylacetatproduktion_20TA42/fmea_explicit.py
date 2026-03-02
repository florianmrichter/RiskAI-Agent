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
}
