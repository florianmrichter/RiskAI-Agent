"""
Explizite FMEA-Definitionen – Methanol-Lager- und Dosieranlage 10TA01.
Agent-Output: Jede Komponente wird einzeln analysiert und hier ergänzt.
"""


def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})


_FMEA = {

    # ─── KOMP-001: Lagertank T-101 ───
    # Erdtank, 10 m³, Stahl/EP-Beschichtung, Methanol, Ex-Zone 1, 12. BImSchV
    "KOMP-001": {
        "functions": [
            {
                "funktion_id": "KOMP-001-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Sicheres Lagern von Methanol (max. 9.000 L, WGK 2, leichtentzündlich)",
                "anforderungen": [
                    {"id": "KOMP-001-F1-A1", "parameter": "Füllvolumen", "sollwert": "Max. 9.000 L"},
                    {"id": "KOMP-001-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Medienfreisetzung"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Drucklose Lagerung sicherstellen (atmosphärisch ± 0,05 bar)",
                "anforderungen": [
                    {"id": "KOMP-001-F2-A1", "parameter": "Druck", "sollwert": "-0,05 bis +0,5 bar (relativ)"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Kontrollierte Entnahme und Befüllung ermöglichen",
                "anforderungen": [
                    {"id": "KOMP-001-F3-A1", "parameter": "Füllstandserfassung", "sollwert": "LIC-101 in Betrieb"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F4",
                "typ": "Nebenfunktion",
                "beschreibung": "Leckagefreiheit gegenüber Boden und Grundwasser gewährleisten",
                "anforderungen": [
                    {"id": "KOMP-001-F4-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage (WHG, 12. BImSchV)"},
                ],
            },
        ],
        "failure_modes": [
            # ── FM-1: Leckage ──
            {
                "funktion_id": "KOMP-001-F4",
                "fehler_id": "KOMP-001-F4-FM1",
                "fehlermodus": "Leckage – Methanol-Austritt an Tankmantel, Domschacht oder Rohranschlüssen",
                "fehlerart": "Mechanisch / Korrosion",
                "causes": [
                    {"ursache_id": "FM1-UC1", "beschreibung": "Innenkorrosion durch EP-Beschichtungsschaden (Alterung, mechanische Verletzung)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM1-UC2", "beschreibung": "Außenkorrosion durch aggressive Böden oder Streustrom", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM1-UC3", "beschreibung": "Ermüdungsrisse an Schweißnähten (Domschacht-Übergang)", "herkunft": "Fertigung", "phase": "Betrieb"},
                    {"ursache_id": "FM1-UC4", "beschreibung": "Flanschleckage am Domschacht durch Dichtungsversagen oder unzureichenden Anzug", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "FM1-UC5", "beschreibung": "Rohranschlussbruch durch Bodensetzung oder Erschütterung", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung möglich", "Methanol-Inhalation oder Hautkontakt; Zündgefahr in Ex-Zone 1 (LEL 6 %)"),
                    "umwelt": ("Boden- und Grundwasserschaden", "WGK 2, Meldepflicht nach 12. BImSchV, Sanierungskosten"),
                    "anlage": ("Betriebsunterbrechung", "Entleerung, Inspektion, Reparatur des Tanks"),
                    "kosten": ("Bis 500.000 € und mehr", "Sanierung, Bußgelder, Produktionsausfall"),
                },
                "controls": [
                    {"name": "GW-101", "typ": "Sensor", "wirkung": "E", "sil_level": "SIL-1",
                     "beschreibung": "Gasdetektor Methanol im Tankraum – erkennt Dampffreisetzung ab Schwellwert",
                     "beeinflusst": "D",
                     "einschraenkung": "Erkennt Dampf, nicht flüssige Bodenleckage; bei erdvergrabenen Tanks zeitverzögert."},
                    {"name": "Sichtprüfung", "typ": "Organisatorisch", "wirkung": "E",
                     "beschreibung": "Regelmäßige Sichtprüfung Domschacht und Rohranschlüsse durch Betreiber",
                     "beeinflusst": "D",
                     "einschraenkung": "Erkennt Mantel-Leckage bei Erdtank nicht; nur oberflächliche Bereiche kontrollierbar."},
                ],
                "S": 9, "O": 3, "D": 7,
                "begruendung_S": "Methanol-Austritt: WGK 2 → Boden-/Grundwasserschaden, Explosionsgefahr (Ex-Zone 1), Personengefährdung; 12. BImSchV-Meldepflicht",
                "begruendung_O": "Moderne EP-Beschichtung + Kathodenschutz; Erfahrungswerte Erdtankleckagen ca. 1 × in 10 Jahren",
                "begruendung_D": "Erdvergraben: Mantel-Leckage visuell nicht erkennbar; GW-101 erkennt nur Dampf; keine Doppelwand/Leckagesonde",
                "kontext_beschreibung": "Der Lagertank ist erdvergraben und enthält bis zu 9.000 L Methanol. Eine Leckage am Mantel oder an Anschlüssen ist besonders kritisch, weil sie lange unentdeckt bleiben kann – der Boden verdeckt den Tank. Methanol ist WGK 2 und kann bei Austritt Grundwasser kontaminieren. Dazu kommt die Brandgefahr: Methanol bildet ab 11 °C zündfähige Dampf-Luft-Gemische (LEL 6 %). GW-101 erkennt Dampf im Tankraum, jedoch keine langsame Bodenleckage.",
                "controls_einschraenkung": "Keine Doppelwand oder Leckagesonde vorhanden. GW-101 erkennt nur verdampfte Anteile. Bei schleichender Bodenleckage kann der Schaden sich über Monate aufbauen, bevor er entdeckt wird.",
            },
            # ── FM-2: Überfüllung (übersprungen, RPZ=42 niedrig) ──
            {
                "funktion_id": "KOMP-001-F3",
                "fehler_id": "KOMP-001-F3-FM2",
                "fehlermodus": "Überfüllung – Füllstand überschreitet 9.000 L",
                "fehlerart": "Betrieb",
                "causes": [
                    {"ursache_id": "FM2-UC1", "beschreibung": "LIC-101 defekt oder fehlkalibriert – kein Alarm bei Max-Annäherung", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM2-UC2", "beschreibung": "LSHH-101 nicht angesprochen oder falsch eingestellt", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "FM2-UC3", "beschreibung": "XV-101 schließt nicht bei Auslösung", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "FM2-UC4", "beschreibung": "Bedienfehler: falsche Befüllmenge manuell freigegeben", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Geringe Gefährdung bei gesichertem Bereich", "Methanol-Überlauf in Ex-Zone 1, Brandgefahr"),
                    "umwelt": ("Lokaler Austritt", "Methanol in Domschacht/Tankraum, WGK 2"),
                    "anlage": ("Notabschaltung", "GW-101 löst aus, Betrieb unterbrochen"),
                    "kosten": ("10–50k €", "Reinigung, Betriebsunterbrechung"),
                },
                "controls": [
                    {"name": "LIC-101", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Level Indicator Controller – Füllstandsanzeige und Alarm bei Max-Annäherung",
                     "beeinflusst": "D"},
                    {"name": "LSHH-101", "typ": "Sensor", "wirkung": "E", "sil_level": "SIL-1",
                     "beschreibung": "Level Switch High High – Überfüllsicherung, löst Schließbefehl an XV-101 aus",
                     "beeinflusst": "D"},
                    {"name": "XV-101", "typ": "Sicherheit", "wirkung": "B", "sil_level": "SIL-1",
                     "beschreibung": "Notabschaltventil Tankauslass, Federschluss – schließt bei LSHH-Auslösung oder Stromausfall",
                     "beeinflusst": "D"},
                ],
                "S": 7, "O": 3, "D": 2,
                "begruendung_S": "Methanol-Überlauf in Ex-Zone 1; Brandgefahr; erheblicher Sachschaden möglich",
                "begruendung_O": "LSHH-101 (SIL 1) + XV-101 als redundante Absicherung; Bedienfehler bei Automatikbetrieb gering",
                "begruendung_D": "LSHH-101 + GW-101 (SIL 1) erkennen Überfüllung mit hoher Sicherheit (> 95 %)",
                "kontext_beschreibung": "Beim Befüllen kann der maximale Füllstand überschritten werden. Die SIL-1-Kette LSHH-101 → XV-101 bietet robuste Absicherung. RPZ = 42 (niedrig), keine zwingenden Maßnahmen.",
                "controls_einschraenkung": "Wirksam nur wenn LSHH-101 und XV-101 regelmäßig geprüft und funktionsfähig sind.",
            },
            # ── FM-3: Druckabnormalie ──
            {
                "funktion_id": "KOMP-001-F2",
                "fehler_id": "KOMP-001-F2-FM3",
                "fehlermodus": "Druckabnormalie – Unter- oder Überdruck durch blockiertes Atemventil",
                "fehlerart": "Mechanisch / Betrieb",
                "causes": [
                    {"ursache_id": "FM3-UC1", "beschreibung": "Atemventil verstopft durch Schmutz, Eis oder Vogelkot", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM3-UC2", "beschreibung": "Atemventil klemmt geschlossen (Korrosion, Verklebung)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM3-UC3", "beschreibung": "Schnelles Entleeren ohne ausreichende Belüftung → Vakuumbildung", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Gefährdung durch Dampffreisetzung", "Methanol-Dampfaustritt über Atemventil in Ex-Zone 1 bei Überdruck"),
                    "umwelt": ("Lokale Dampfemission", "Methanol-Dampf im Tankraum, Ex-Zone 1"),
                    "anlage": ("Tankverformung oder -kollaps", "Bei Unterdruck: plastische Verformung des Mantels, Dichtheitsverlust"),
                    "kosten": ("50–250k €", "Tankaustausch oder -sanierung, Betriebsunterbrechung"),
                },
                "controls": [
                    {"name": "Atemventil", "typ": "Mechanisch", "wirkung": "B",
                     "beschreibung": "Druckausgleichsventil am Domschacht – verhindert Über-/Unterdruck bei Befüllung/Entleerung",
                     "beeinflusst": "O",
                     "einschraenkung": "Kein Sensor/Überwachung; Funktionsausfall nur bei Sichtprüfung erkennbar."},
                    {"name": "Sichtprüfung Atemventil", "typ": "Organisatorisch", "wirkung": "E",
                     "beschreibung": "Gelegentliche Sichtprüfung auf Verstopfung oder Vereisung",
                     "beeinflusst": "D",
                     "einschraenkung": "Keine definierte Prüffrequenz dokumentiert; Entdeckungswahrscheinlichkeit gering."},
                ],
                "S": 7, "O": 3, "D": 6,
                "begruendung_S": "Tankkollaps oder Dampffreisetzung in Ex-Zone 1; erheblicher Sachschaden, Brandgefahr",
                "begruendung_O": "Atemventil-Ausfall ca. 1 × in 10 Jahren bei fehlendem WKP; Vereisung saisonal möglich",
                "begruendung_D": "Kein Drucksensor vorhanden; nur Sichtprüfung ohne definierten Rhythmus (30–50 % Entdeckung)",
                "kontext_beschreibung": "Der Tank ist für atmosphärische Lagerung ausgelegt. Das Atemventil gleicht Druckschwankungen bei Befüllung, Entleerung und Temperaturwechseln aus. Fällt es aus, droht Vakuumkollaps oder Überdruckentlüftung von Methanol-Dampf in Ex-Zone 1. Kein Drucküberwachungssensor dokumentiert.",
                "controls_einschraenkung": "Kein Drucksensor am Tank. Atemventil-Ausfall wird nur bei Sichtprüfung erkannt; bei schnellem Entleerungsvorgang kann Unterdruck auftreten bevor Gegenmaßnahmen greifen.",
            },
            # ── FM-4: Methanol-Dampffreisetzung ──
            {
                "funktion_id": "KOMP-001-F1",
                "fehler_id": "KOMP-001-F1-FM4",
                "fehlermodus": "Methanol-Dampffreisetzung – Ausgasung im Domschacht, Zündgefahr Ex-Zone 1",
                "fehlerart": "Betrieb / Emission",
                "causes": [
                    {"ursache_id": "FM4-UC1", "beschreibung": "Erhöhte Temperatur im Sommer → verstärkte Verdampfung beim Öffnen des Domdeckels", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM4-UC2", "beschreibung": "Domschacht unzureichend belüftet → Dampfansammlung", "herkunft": "Design", "phase": "Betrieb"},
                    {"ursache_id": "FM4-UC3", "beschreibung": "Zündquelle im Domschacht (Werkzeug, Funken) trotz Ex-Zone 1", "herkunft": "Betrieb", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Akute Vergiftungsgefahr / Verpuffung", "Methanol-Inhalation bei Domöffnung; Zündung explosionsfähiger Atmosphäre (LEL 6–36,5 %)"),
                    "umwelt": ("Lokale Emission", "Methanol-Dampf in Tankraumatmosphäre"),
                    "anlage": ("Brand / Explosion", "Dombereich, Tankraum, Folgeschäden"),
                    "kosten": ("Bis 500k €", "Brand, Explosion, Sachschaden, Personenschaden"),
                },
                "controls": [
                    {"name": "GW-101", "typ": "Sensor", "wirkung": "E", "sil_level": "SIL-1",
                     "beschreibung": "Gasdetektor Methanol – erkennt Dampfkonzentration im Tankraum, löst Alarm aus",
                     "beeinflusst": "D"},
                    {"name": "Ex-Schutzkonzept Zone 1", "typ": "Organisatorisch", "wirkung": "B",
                     "beschreibung": "Ex-Zone 1 im Tankraum: nur Ex-geschützte Geräte und Werkzeuge, Zutrittsregelung",
                     "beeinflusst": "O"},
                    {"name": "PSA-Pflicht", "typ": "Organisatorisch", "wirkung": "B",
                     "beschreibung": "Persönliche Schutzausrüstung (Atemschutz, Chemikalienschutzanzug) bei Domarbeiten",
                     "beeinflusst": "O"},
                ],
                "S": 9, "O": 4, "D": 3,
                "begruendung_S": "Verpuffung/Brand in Ex-Zone 1; Methanol-Vergiftung; katastrophale Folgen für Personen und Anlage",
                "begruendung_O": "Methanol-Dampf im Domschacht bei Arbeiten regelmäßig vorhanden; O=4 (~alle 2 Jahre relevantes Ereignis)",
                "begruendung_D": "GW-101 (SIL 1) erkennt Dampf zuverlässig; Ex-Schutzkonzept reduziert Zündwahrscheinlichkeit; D=3",
                "kontext_beschreibung": "Methanol verdampft bereits bei Raumtemperatur (Siedepunkt 64,7 °C). Im Domschacht sammelt sich Dampf, besonders bei warmen Temperaturen oder nach Befüllung. Bei Domöffnungen (Wartung, Inspektion) besteht akute Vergiftungs- und Zündgefahr. GW-101 überwacht die Atmosphäre kontinuierlich. Ex-Zone 1 schreibt ex-geschützte Ausrüstung vor.",
                "controls_einschraenkung": "GW-101 schützt nur wenn kalibriert und funktionsfähig. PSA-Pflicht abhängig von Disziplin der Mitarbeiter.",
            },
            # ── FM-5: Kontamination ──
            {
                "funktion_id": "KOMP-001-F3",
                "fehler_id": "KOMP-001-F3-FM5",
                "fehlermodus": "Kontamination – Wassereintritt oder Fremdstoffeintrag in den Tank",
                "fehlerart": "Betrieb / Qualität",
                "causes": [
                    {"ursache_id": "FM5-UC1", "beschreibung": "Undichte Domschachtabdeckung → Regenwassereintrag", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM5-UC2", "beschreibung": "Falsche Befüllung (falscher Tankwagen / Stoff)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM5-UC3", "beschreibung": "Kondenswasserbildung im Tankinneren bei Temperaturschwankungen", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Geringe direkte Gefährdung", "Qualitätsfehler; bei Falschbefüllung mit reaktiven Stoffen Reaktionsgefahr"),
                    "umwelt": ("Gering", "Kontaminiertes Methanol bei Entsorgung"),
                    "anlage": ("Qualitätsverlust", "Methanol-Spezifikation unterschritten; Charge unbrauchbar"),
                    "kosten": ("1–50k €", "Tankleerung, Spülung, Chargenverlust"),
                },
                "controls": [
                    {"name": "Domschachtabdeckung", "typ": "Mechanisch", "wirkung": "B",
                     "beschreibung": "Abgedeckter Domschacht schützt vor Niederschlag",
                     "beeinflusst": "O"},
                    {"name": "Anlieferungskontrolle", "typ": "Organisatorisch", "wirkung": "B",
                     "beschreibung": "Lieferscheinprüfung und Produktidentifikation vor Befüllung",
                     "beeinflusst": "O"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Qualitätsverlust Methanol; bei Falschbefüllung mit inkompatiblem Stoff erhöhte Gefahr; S=5 mäßig",
                "begruendung_O": "Wassereintrag selten bei intaktem Domschacht; Falschbefüllung durch Lieferscheinkontrolle begrenzt",
                "begruendung_D": "Keine automatische Qualitätsmessung; Entdeckung erst bei Probennahme oder Prozessauffälligkeit",
                "kontext_beschreibung": "Wasser im Methanol-Tank senkt den Reinheitsgrad unter die Spezifikation (> 99 %). Bei Falschbefüllung mit reaktiven Stoffen kann es zur gefährlichen Reaktion kommen. Die Kontrolle beruht auf organisatorischen Maßnahmen und Sichtprüfung.",
                "controls_einschraenkung": "Keine automatische Qualitätsüberwachung im Tank. Kontamination wird erst bei externer Probenanalyse entdeckt.",
            },
        ],
    },

    # ─── KOMP-002: Dosierpumpe P-101 ───
    # Membranpumpe, 50 L/h, max. 4 bar, PTFE/Edelstahl, Ex-Zone 2, elektrisch
    "KOMP-002": {
        "functions": [
            {
                "funktion_id": "KOMP-002-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Methanol fördern und dosieren (Nenndurchfluss 50 L/h, max. 4 bar)",
                "anforderungen": [
                    {"id": "KOMP-002-F1-A1", "parameter": "Durchfluss", "sollwert": "50 L/h ± 5 %"},
                    {"id": "KOMP-002-F1-A2", "parameter": "Druck", "sollwert": "Max. 4 bar"},
                ],
            },
            {
                "funktion_id": "KOMP-002-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Mediendichte Förderung sicherstellen (PTFE-Membran, Ex-geschützt)",
                "anforderungen": [
                    {"id": "KOMP-002-F2-A1", "parameter": "Leckage", "sollwert": "Null-Leckage an Membran und Anschlüssen"},
                ],
            },
            {
                "funktion_id": "KOMP-002-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Förderung sicher abschalten (bei Notabschaltung über XV-101)",
                "anforderungen": [
                    {"id": "KOMP-002-F3-A1", "parameter": "Abschaltzeit", "sollwert": "< 5 s nach Abschaltsignal"},
                ],
            },
        ],
        "failure_modes": [
            # ── FM-1: Membranbruch ──
            {
                "funktion_id": "KOMP-002-F2",
                "fehler_id": "KOMP-002-F2-FM1",
                "fehlermodus": "Membranbruch – Methanol-Austritt in Ex-Zone 2",
                "fehlerart": "Mechanisch / Verschleiß",
                "causes": [
                    {"ursache_id": "K2-FM1-UC1", "beschreibung": "Membranverschleiß durch Alterung oder chemische Unverträglichkeit", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K2-FM1-UC2", "beschreibung": "Druckschlag / Wasserschlag bei schnellem Ventilschluss", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K2-FM1-UC3", "beschreibung": "Überschreitung des Maximaldrucks (> 4 bar) durch blockierte Leitung", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Gefährdung durch Methanol-Austritt", "Hautkontakt, Inhalation in Ex-Zone 2"),
                    "umwelt": ("Lokaler Austritt", "Methanol in Pumpenraum, WGK 2"),
                    "anlage": ("Pumpenausfall", "Förderung unterbrochen, Leckage in Pumpenraum"),
                    "kosten": ("1–10k €", "Membranaustausch, Reinigung, Betriebsunterbrechung"),
                },
                "controls": [
                    {"name": "PI-101", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Pressure Indicator – Druckanzeige Pumpenauslass; Druckanstieg bei Leitungsblockade erkennbar",
                     "beeinflusst": "D",
                     "einschraenkung": "Nur Anzeige, kein automatischer Alarm oder Abschaltung dokumentiert."},
                    {"name": "Membranbruch-Detektor", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Optionaler Membranbruch-Sensor (hydraulikseitig) – erkennt Druckabfall in Hydraulikraum",
                     "beeinflusst": "D",
                     "einschraenkung": "Nicht explizit in Anlagendaten dokumentiert; Status unklar."},
                    {"name": "Regelmäßiger Membranaustausch", "typ": "Organisatorisch", "wirkung": "B",
                     "beschreibung": "Präventiver Austausch gemäß Herstellervorgabe (typisch 2–5 Jahre)",
                     "beeinflusst": "O"},
                ],
                "S": 7, "O": 4, "D": 5,
                "begruendung_S": "Methanol-Austritt in Ex-Zone 2; Brandgefahr, Personengefährdung; S=7 (Vollausfall, 50–250k € inkl. Folgeschäden)",
                "begruendung_O": "Membranbruch bei Membranpumpen typisch alle 2–5 Jahre; O=4 (~alle 2 Jahre)",
                "begruendung_D": "PI-101 nur Anzeige; Membranbruch-Detektor Status unklar; keine automatische Abschaltung; D=5",
                "kontext_beschreibung": "Die PTFE-Membran ist die kritische Barriere zwischen Methanol und Pumpenantrieb. Bei Bruch tritt Methanol in Ex-Zone 2 aus. PI-101 zeigt den Druck an, schaltet aber nicht automatisch ab. Regelmäßiger präventiver Austausch reduziert das Risiko.",
                "controls_einschraenkung": "PI-101 hat keinen dokumentierten Hochdruckalarm. Membranbrucherkennung nur wenn optionaler Sensor verbaut.",
            },
            # ── FM-2: Förderausfall ──
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM2",
                "fehlermodus": "Förderausfall – Pumpe fördert nicht (kein oder zu geringer Durchfluss)",
                "fehlerart": "Elektrisch / Mechanisch",
                "causes": [
                    {"ursache_id": "K2-FM2-UC1", "beschreibung": "Elektromotor ausgefallen (Überlast, Wicklungsschaden)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K2-FM2-UC2", "beschreibung": "Saugventil oder Druckventil undicht / verstopft", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K2-FM2-UC3", "beschreibung": "Kavitation durch zu geringen Zulaufdruck (Tankstand niedrig)", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine direkte Gefährdung", "Prozessunterbrechung"),
                    "umwelt": ("Keine", "Prozessunterbrechung ohne Stoffaustritt"),
                    "anlage": ("Produktionsunterbrechung", "Nachgelagerte Prozesse ohne Methanol-Versorgung"),
                    "kosten": ("1–10k €", "Reparatur, Produktionsunterbrechung"),
                },
                "controls": [
                    {"name": "PI-101", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Druckanzeige Pumpenauslass – Druckabfall bei Förderausfall erkennbar",
                     "beeinflusst": "D"},
                    {"name": "LIC-101", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Füllstandsregler Tank – indirekter Hinweis auf Förderausfall bei ausbleibendem Füllstandsabfall",
                     "beeinflusst": "D"},
                ],
                "S": 4, "O": 4, "D": 4,
                "begruendung_S": "Prozessunterbrechung ohne Personengefahr; Kosten < 10k €; S=4",
                "begruendung_O": "Motorausfall und Ventilprobleme bei Membranpumpen gelegentlich; O=4 (~alle 2 Jahre)",
                "begruendung_D": "PI-101 erkennt Druckabfall; manuelle Überwachung möglich; D=4",
                "kontext_beschreibung": "Fördert die Pumpe nicht, werden nachgelagerte Prozesse nicht mit Methanol versorgt. Das ist betrieblich störend, aber ohne direkte Sicherheitsrelevanz. PI-101 zeigt den Druckabfall an.",
                "controls_einschraenkung": "Kein automatischer Fördermengen-Alarm; Erkennung nur durch Beobachtung von PI-101 oder Prozessauffälligkeiten.",
            },
            # ── FM-3: Überdruckereignis ──
            {
                "funktion_id": "KOMP-002-F1",
                "fehler_id": "KOMP-002-F1-FM3",
                "fehlermodus": "Überdruck – Leitungsdruck überschreitet 4 bar (blockierte Leitung, Ventil zu)",
                "fehlerart": "Betrieb / Mechanisch",
                "causes": [
                    {"ursache_id": "K2-FM3-UC1", "beschreibung": "Absperrventil im Druckbereich geschlossen während Pumpe läuft", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K2-FM3-UC2", "beschreibung": "Leitungsverengung oder Verstopfung im Druckbereich", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K2-FM3-UC3", "beschreibung": "Rückschlagventil klemmt → Druckschlag", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Gefährdung durch schlagartigen Medienaustritt", "Methanol-Jet bei Leitungsversagen"),
                    "umwelt": ("Lokaler Austritt", "Methanol in Pumpenraum"),
                    "anlage": ("Leitungsschaden, Pumpenversagen", "Membranbruch, Leitungsbersten"),
                    "kosten": ("5–50k €", "Reparatur, Reinigung, Betriebsunterbrechung"),
                },
                "controls": [
                    {"name": "PI-101", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Druckanzeige Pumpenauslass – Druckanstieg erkennbar",
                     "beeinflusst": "D",
                     "einschraenkung": "Kein automatischer Hochdruckalarm; nur visuelle Überwachung."},
                    {"name": "Überdruckventil (angenommen)", "typ": "Mechanisch", "wirkung": "B",
                     "beschreibung": "Sicherheitsventil oder Bypass am Pumpenauslass (Standard bei Membranpumpen)",
                     "beeinflusst": "O",
                     "einschraenkung": "Nicht explizit in Anlagendaten dokumentiert."},
                ],
                "S": 7, "O": 3, "D": 5,
                "begruendung_S": "Leitungsbersten / Membranbruch → Methanol-Austritt in Ex-Zone 2; S=7",
                "begruendung_O": "Druckschlag bei Membranpumpen möglich, aber durch Überdruckventil begrenzt; O=3",
                "begruendung_D": "PI-101 zeigt Druck an; kein automatischer Alarm; D=5",
                "kontext_beschreibung": "Wenn die Druckleitung blockiert ist und die Pumpe weiterläuft, steigt der Druck schnell über 4 bar. Ohne Überdruckabsicherung droht Membranbruch oder Leitungsversagen mit schlagartigem Methanol-Austritt.",
                "controls_einschraenkung": "Überdruckventil nicht explizit dokumentiert. PI-101 kein automatischer Alarm.",
            },
        ],
    },

    # ─── KOMP-003: MSR- und Sicherheitstechnik ───
    # LIC-101, LSHH-101 (SIL 1), XV-101 (SIL 1), GW-101 (SIL 1), PI-101
    "KOMP-003": {
        "functions": [
            {
                "funktion_id": "KOMP-003-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Überfüllschutz sicherstellen: LSHH-101 → XV-101 (SIL 1)",
                "anforderungen": [
                    {"id": "KOMP-003-F1-A1", "parameter": "SIL-Anforderung", "sollwert": "SIL 1 (PFD ≤ 0,1)"},
                    {"id": "KOMP-003-F1-A2", "parameter": "Reaktionszeit", "sollwert": "< 10 s"},
                ],
            },
            {
                "funktion_id": "KOMP-003-F2",
                "typ": "Hauptfunktion",
                "beschreibung": "Gasdetektion und Notabschaltung: GW-101 → Alarm/Abschaltung (SIL 1)",
                "anforderungen": [
                    {"id": "KOMP-003-F2-A1", "parameter": "Ansprechschwelle", "sollwert": "≤ 20 % UEG Methanol"},
                    {"id": "KOMP-003-F2-A2", "parameter": "Verfügbarkeit", "sollwert": "Kontinuierlich"},
                ],
            },
            {
                "funktion_id": "KOMP-003-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Füllstand überwachen und anzeigen: LIC-101",
                "anforderungen": [
                    {"id": "KOMP-003-F3-A1", "parameter": "Messgenauigkeit", "sollwert": "± 2 % vom Messbereich"},
                ],
            },
            {
                "funktion_id": "KOMP-003-F4",
                "typ": "Nebenfunktion",
                "beschreibung": "Druck überwachen: PI-101 (Pumpenauslass)",
                "anforderungen": [
                    {"id": "KOMP-003-F4-A1", "parameter": "Messbereich", "sollwert": "0–6 bar"},
                ],
            },
        ],
        "failure_modes": [
            # ── FM-1: Ausfall LSHH-101 / XV-101 (SIL-Funktion) ──
            {
                "funktion_id": "KOMP-003-F1",
                "fehler_id": "KOMP-003-F1-FM1",
                "fehlermodus": "Ausfall der SIL-1-Überfüllschutzfunktion (LSHH-101 oder XV-101 nicht funktionsfähig)",
                "fehlerart": "Elektrisch / Mechanisch",
                "causes": [
                    {"ursache_id": "K3-FM1-UC1", "beschreibung": "LSHH-101 (Level Switch High High) Sensor defekt oder Driftet aus Einstellpunkt", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K3-FM1-UC2", "beschreibung": "XV-101 Ventil mechanisch blockiert (klemmt auf)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K3-FM1-UC3", "beschreibung": "Kabelbruch oder Kurzschluss in der SIL-Schleife", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K3-FM1-UC4", "beschreibung": "Fehlende oder verspätete Wiederholungsprüfung (Proof Test)", "herkunft": "Wartung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Erhöhte Gefährdung bei Überfüllung", "Überfüllschutz nicht vorhanden → Methanol-Überlauf in Ex-Zone 1"),
                    "umwelt": ("Methanol-Austritt möglich", "WGK 2, Boden- und Grundwasserrisiko"),
                    "anlage": ("Schutzfunktion ausgefallen", "Anlage ungesichert bei Befüllvorgang"),
                    "kosten": ("10–250k €", "Überfüllschaden, Reparatur, Behördenmaßnahmen"),
                },
                "controls": [
                    {"name": "SIL-1-Proof-Test", "typ": "Organisatorisch", "wirkung": "E",
                     "beschreibung": "Regelmäßiger Wiederholungstest LSHH-101 + XV-101 gemäß SIL-1-Prüfplan (jährlich empfohlen)",
                     "beeinflusst": "D",
                     "einschraenkung": "Nur wirksam wenn Proof-Test-Plan etabliert und dokumentiert ist."},
                    {"name": "LIC-101", "typ": "Sensor", "wirkung": "E",
                     "beschreibung": "Füllstandsanzeige als unabhängige Überwachung; Bediener erkennt Annäherung an Max",
                     "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 4,
                "begruendung_S": "Überfüllschutz ausgefallen → Überfüllung möglich → Methanol in Ex-Zone 1; S=8 (Extrem hoch)",
                "begruendung_O": "SIL-1-Komponenten mit PFD ~0,01–0,1/Jahr; bei fehlendem Proof Test steigt O; O=3 bei regelmäßiger Prüfung",
                "begruendung_D": "Ausfall latent (Fail-Silent); LIC-101 nur sekundäre Erkennung; D=4",
                "kontext_beschreibung": "LSHH-101 und XV-101 bilden die SIL-1-Überfüllschutzfunktion. Fällt einer dieser Bausteine aus, ist der Überfüllschutz nicht mehr wirksam – ohne dass dies sofort auffällt (latenter Fehler). Regelmäßige Proof Tests sind für die SIL-1-Integrität zwingend.",
                "controls_einschraenkung": "Latenter Ausfall nicht sofort erkennbar. Proof-Test-Intervall und Dokumentation müssen etabliert sein.",
            },
            # ── FM-2: Ausfall GW-101 ──
            {
                "funktion_id": "KOMP-003-F2",
                "fehler_id": "KOMP-003-F2-FM2",
                "fehlermodus": "Ausfall GW-101 – Gasdetektor nicht funktionsfähig (Methanol-Dampf unerkannt)",
                "fehlerart": "Elektrisch / Sensor",
                "causes": [
                    {"ursache_id": "K3-FM2-UC1", "beschreibung": "Sensor verschmutzt oder vergiftet → Ansprechvermögen verloren", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K3-FM2-UC2", "beschreibung": "Kalibrierung abgelaufen → falsche Messwerte", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "K3-FM2-UC3", "beschreibung": "Stromversorgungsausfall oder Elektronikdefekt", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Erhöhte Gefährdung", "Methanol-Dampf im Tankraum ohne Alarm; Vergiftungs- und Explosionsgefahr"),
                    "umwelt": ("Indirekt", "Kein Alarm bei Leckage → verzögerte Reaktion"),
                    "anlage": ("Sicherheitsfunktion ausgefallen", "Gaswarnung nicht verfügbar"),
                    "kosten": ("10–500k €", "Je nach Folgeereignis ohne Gasdetektion"),
                },
                "controls": [
                    {"name": "Regelmäßige Kalibrierung GW-101", "typ": "Organisatorisch", "wirkung": "E",
                     "beschreibung": "Jährliche Kalibrierung und Funktionsprüfung des Gasdetektors",
                     "beeinflusst": "D",
                     "einschraenkung": "Zwischen den Kalibrierungen kann unerkannter Drift auftreten."},
                    {"name": "Störmeldung bei Ausfall", "typ": "Technisch", "wirkung": "E",
                     "beschreibung": "GW-101 meldet Geräteausfall an Leitstand (Fail-Safe-Konzept)",
                     "beeinflusst": "D"},
                ],
                "S": 8, "O": 3, "D": 3,
                "begruendung_S": "Ohne Gasdetektion können Leckagen und gefährliche Atmosphären unerkannt bleiben; S=8",
                "begruendung_O": "Sensordrift oder Ausfall bei jährlicher Kalibrierung selten; O=3",
                "begruendung_D": "Fail-Safe-Meldung und Kalibrierplan erhöhen Entdeckungswahrscheinlichkeit; D=3",
                "kontext_beschreibung": "GW-101 ist die zentrale Sicherheitsbarriere gegen unerkannte Methanol-Dampf-Atmosphären im Tankraum. Ein ausgefallener Detektor ist besonders gefährlich, weil der Betreiber sich in falscher Sicherheit wiegt. Regelmäßige Kalibrierung und Fail-Safe-Betrieb sind essenziell.",
                "controls_einschraenkung": "Drift zwischen Kalibrierungen möglich. Fail-Safe-Meldung nur wirksam wenn Leitstand überwacht wird.",
            },
            # ── FM-3: Ausfall LIC-101 ──
            {
                "funktion_id": "KOMP-003-F3",
                "fehler_id": "KOMP-003-F3-FM3",
                "fehlermodus": "Ausfall LIC-101 – Füllstand nicht messbar oder falsch angezeigt",
                "fehlerart": "Sensor / Elektronisch",
                "causes": [
                    {"ursache_id": "K3-FM3-UC1", "beschreibung": "Sensor verschmutzt oder mechanisch beschädigt", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "K3-FM3-UC2", "beschreibung": "Kalibrierungsfehler → falscher Anzeigewert", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "K3-FM3-UC3", "beschreibung": "Leitungsbruch oder Elektronikdefekt", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Indirekte Gefährdung", "Fehlentscheidungen bei Befüllung durch falschen Füllstand"),
                    "umwelt": ("Indirekt", "Überfüllung möglich bei falschem Anzeigewert"),
                    "anlage": ("Füllstandsüberwachung verloren", "Abhängigkeit von LSHH-101 steigt"),
                    "kosten": ("1–10k €", "Sensortausch, Betriebseinschränkung"),
                },
                "controls": [
                    {"name": "LSHH-101", "typ": "Sensor", "wirkung": "B", "sil_level": "SIL-1",
                     "beschreibung": "Unabhängige Überfüllsicherung – greift auch bei LIC-101-Ausfall",
                     "beeinflusst": "O"},
                    {"name": "Störmeldung LIC-101", "typ": "Technisch", "wirkung": "E",
                     "beschreibung": "Ausfall- oder Grenzwertmeldung an Leitstand",
                     "beeinflusst": "D"},
                ],
                "S": 5, "O": 4, "D": 3,
                "begruendung_S": "LIC-101-Ausfall allein nicht katastrophal (LSHH-101 als Backup); S=5 mäßig",
                "begruendung_O": "Sensor-/Elektronikausfälle gelegentlich; O=4",
                "begruendung_D": "Störmeldung an Leitstand; LSHH-101 als unabhängige Sicherheit; D=3",
                "kontext_beschreibung": "LIC-101 ist die primäre Füllstandsanzeige. Fällt sie aus, ist die Betriebsführung blind – aber LSHH-101 (SIL 1) greift als unabhängige letzte Barriere. Störmeldung am Leitstand ermöglicht schnelle Reaktion.",
                "controls_einschraenkung": "Bei gleichzeitigem Ausfall von LIC-101 und LSHH-101 kein Füllstandsschutz mehr vorhanden.",
            },
        ],
    },
}
