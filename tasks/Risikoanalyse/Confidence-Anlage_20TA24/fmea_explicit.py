"""
Explizite FMEA-Definitionen – Confidence-Anlage 20TA24 (Roche, Penzberg)
Agent-Output: Semi-Batch-Polymersynthese + Ultrafiltration in ethanolischer Lösung.

Scope: KOMP-001 (Synthesereaktor Schnittstellen), KOMP-002 (UF-Anlage 1 Schnittstellen),
       KOMP-003 (UF-Anlage 2 Schnittstellen).
ATEX: Technikum Zone 2, Handloch/Zugabestellen Zone 1, Reaktor innen Zone 1.
Reaktion: NICHT exotherm, kein Runaway-Risiko (Polymersynthese in EtOH).
Package Units: Interne Technik nicht im FMEA-Scope — nur Schnittstellen/Übergabepunkte.
"""


def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente."""
    return _FMEA.get(komp_id, {})


_FMEA = {

    # ─────────────────────────────────────────────────────────────────────────
    # KOMP-001: Synthesereaktor (Schnittstellen)
    # Büchi Glas Uster, 50 L Borosilikatglas, PSV/BSV 0.5 bar → Blowdown
    # Zone 1 innen, Zone 2 außen. Lauda-Thermostat extern.
    # ─────────────────────────────────────────────────────────────────────────
    "KOMP-001": {
        "functions": [
            {
                "funktion_id": "20TA24-KOMP-001-F1",
                "typ": "Sicherheitsfunktion",
                "beschreibung": "Druckabsicherung über PSV (Pressure Safety Valve) und BSV (Berstscheibe) "
                                "bei Überdruck; Abblaseleitung in Blowdown-System.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-001-F1-A1", "parameter": "PSV Ansprechdruck", "sollwert": "0,5 bar"},
                    {"id": "20TA24-KOMP-001-F1-A2", "parameter": "BSV Ansprechdruck", "sollwert": "0,5 bar"},
                    {"id": "20TA24-KOMP-001-F1-A3", "parameter": "Prüfintervall PSV/BSV", "sollwert": "12 Monate"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-001-F2",
                "typ": "Betriebsfunktion",
                "beschreibung": "Vakuumbetrieb (bis -0,9 bar) über externe Vakuumversorgung; Rückschlagventile "
                                "in Vakuumleitungen verhindern Rückstrom. System ist gasdicht ausgelegt.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-001-F2-A1", "parameter": "Min. Betriebsdruck", "sollwert": "-0,9 bar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-001-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Kondensation von Lösemitteldämpfen (Ethanol) am Kopfkondensator "
                                "mit Eiswasser (max. 1 bar, druckreduziert, SV 1 bar eiswasserseitig).",
                "anforderungen": [
                    {"id": "20TA24-KOMP-001-F3-A1", "parameter": "Eiswasser Betriebsdruck Kondensator", "sollwert": "≤ 1 bar"},
                    {"id": "20TA24-KOMP-001-F3-A2", "parameter": "Auslegung Kondensator Eiswasserseite", "sollwert": "3 bar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-001-F4",
                "typ": "Sicherheitsfunktion",
                "beschreibung": "Inertisierung des Reaktorkopfraums und der Rührwerk-Wellendichtung "
                                "mit Stickstoff (N₂). Verhindert O₂-Eintrag und schützt Produktqualität.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-001-F4-A1", "parameter": "N₂-Versorgungsdruck", "sollwert": "300–2500 mbar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-001-F5",
                "typ": "Nebenfunktion",
                "beschreibung": "Ableitung von Lösemitteldämpfen über Abluftsystem (leichter Unterdruck "
                                "-9 bis -17 Pa) zur Abluftreinigungsanlage. Geschlossenes System verhindert "
                                "Rückströmung ins Technikum.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-001-F6",
                "typ": "Grundfunktion",
                "beschreibung": "Mechanische Integrität aller Schnittstellen: Flansche, Schlauchanschlüsse, "
                                "Wellendurchführung Rührwerk, Probenahme-Anschlüsse. Dichtigkeitstest vor "
                                "jeder Produktion im Rahmen der Inertisierungsüberprüfung.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-001-F6-A1", "parameter": "Dichtigkeitstest", "sollwert": "Vor jeder Charge"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-001-F7",
                "typ": "Betriebsfunktion",
                "beschreibung": "Temperierung des Reaktorinhalts über Lauda-Thermostat und Heiz-/Kühlmantel. "
                                "Externe Utility-Schnittstelle. Reaktion NICHT exotherm, kein Runaway-Risiko.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-001-F7-A1", "parameter": "Temperatur-Messung", "sollwert": "TI am Reaktor (lokal)"},
                ]
            },
        ],

        "failure_modes": [

            # FM-1: Druckabsicherungsversagen (PSV/BSV Nicht-Öffnen)
            {
                "fehler_id": "20TA24-K001-FM1",
                "funktion_id": "20TA24-KOMP-001-F1",
                "fehlermodus": "Druckabsicherungsversagen — PSV (Sicherheitsventil) oder BSV (Berstscheibe) öffnen nicht bei Überdruck",
                "fehlerart": "Sicherheit",
                "kontext_beschreibung": (
                    "PSV und BSV sind die letzte Verteidigungslinie gegen Überdruckereignisse im Reaktor. "
                    "Beide sind sicherheitsgerichtete Bauteile (Safety Override: Min. S = 10). "
                    "Sie leiten in das Blowdown-System ein. Jährliche Prüfung nach Herstellervorgabe. "
                    "Die Zone-1-Auslegung innen und Zone-2-Auslegung außen schützen gegen Zündquellen."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM1-U1", "beschreibung": "PSV klemmt (Korrosion, Ablagerung, zu hoher Anpressdruck)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM1-U2", "beschreibung": "BSV falsch eingebaut oder bereits vorbelastet (Ermüdung durch Druckwechsel)", "herkunft": "Fertigung", "phase": "Wartung"},
                    {"ursache_id": "20TA24-K001-FM1-U3", "beschreibung": "Blowdown-Leitung verstopft → Gegendruck verhindert Öffnen", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Kritisch", "Versagen der letzten Druckabsicherung → Behälterbersten möglich → Todesfälle"),
                    "umwelt": ("Hoch", "Austritt von Lösemittel/Reaktionsgemisch in Technikum"),
                    "anlage": ("Katastrophal", "Zerstörung Reaktor (Borosilikatglas), Folgeschäden im Technikum"),
                    "kosten": ("Sehr hoch", "> 250.000 € (Reaktor + Technikumschäden)"),
                },
                "controls": [
                    {"name": "PSV (Sicherheitsventil)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Pressure Safety Valve (Sicherheitsventil) am Reaktorkopf, Ansprechdruck 0,5 bar, Prüfintervall 12 Monate",
                     "beeinflusst": "D", "einschraenkung": "Jährliche Prüfung erforderlich; klemmt bei Korrosion oder Ablagerung"},
                    {"name": "BSV (Berstscheibe)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Bursting Disc (Berstscheibe) am Reaktorkopf, Ansprechdruck 0,5 bar, redundant zu PSV",
                     "beeinflusst": "D", "einschraenkung": "Einmalbauteil; muss nach Auslösung ersetzt werden"},
                    {"name": "Blowdown-System", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Gemeinsame Abblaseleitung für PSV/BSV von Reaktor und UF-Anlagen. Enthält Lösemitteldämpfe kontrolliert.",
                     "beeinflusst": "D", "einschraenkung": "Verstopfung der Blowdown-Leitung würde PSV/BSV-Wirkung aufheben"},
                ],
                "S": 10, "O": 2, "D": 4,
                "begruendung_S": "Safety Override: PSV und BSV sind sicherheitsgerichtete Bauteile → Mindest-S = 10. Versagen → Behälterbersten bei Borosilikatglas → katastrophale Folgen.",
                "begruendung_O": "Sehr gering (~1/100 Jahre): PSV und BSV werden jährlich geprüft. Ausfallwahrscheinlichkeit durch regelmäßige Wartung sehr gering.",
                "begruendung_D": "Relativ wahrscheinlich: Jährliche 100%-Prüfung (Dichtigkeits- und Ansprechtest). Funktionsversagen zwischen Prüfterminen nicht sofort erkennbar.",
                "controls_einschraenkung": "PSV und BSV sichern ab, wenn sie funktionieren. Der Fehlermodus beschreibt deren Versagen — kein weiteres redundantes System vorhanden außer dem Blowdown.",
            },

            # FM-2: Vakuumkollaps / Lufteintrag durch defekte Vakuumleitungen
            {
                "fehler_id": "20TA24-K001-FM2",
                "funktion_id": "20TA24-KOMP-001-F2",
                "fehlermodus": "Vakuumkollaps — Lufteintrag durch defekte Vakuumschläuche oder Leitungen",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "Der Reaktor wird zeitweise unter Vakuum (bis -0,9 bar) betrieben. Vakuumschläuche und "
                    "-leitungen können altern oder mechanisch beschädigt werden. Rückschlagventile in den "
                    "Vakuumleitungen verhindern Lösemittelrückstrom. Zone 1 innen: Alle internen Bauteile für "
                    "gelegentlich explosive Atmosphäre ausgelegt. Zone 2 außen. "
                    "Explosionsschutzdokument bewertet dieses Szenario formal als ausreichend gesichert."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM2-U1", "beschreibung": "Alterung/Rissbildung in Vakuumschläuchen durch Lösemittelkontakt und Druckwechselermüdung", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM2-U2", "beschreibung": "Mechanische Beschädigung durch äußere Einwirkung (Knicken, Quetschen)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM2-U3", "beschreibung": "Lockere Schlauchklemme oder fehlerhafter Anschluss nach Wartungsarbeiten", "herkunft": "Fertigung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Lösemitteldämpfe (Ethanol) könnten austreten; Zone-2-Auslegung Technikum mitigiert Explosionsrisiko"),
                    "umwelt": ("Gering", "Ethanol-Emission möglich, unterhalb Emissionsgrenzwert bei kleinem Leck"),
                    "anlage": ("Mäßig", "Prozessunterbrechung; Produktverlust durch Schlauchversagen"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Produktverlust, Reinigung, Schlauchwechsel)"),
                },
                "controls": [
                    {"name": "Rückschlagventile Vakuumleitungen", "typ": "Mechanisches Sicherheitselement", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Verhindert Rückstrom von Lösemittel in Vakuumsystem bei Druckumkehr",
                     "beeinflusst": "D", "einschraenkung": "Schützt Vakuumsystem, nicht gegen Lufteintrag in Reaktor"},
                    {"name": "Jährliche Schlauchwartung", "typ": "Organisatorisch", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Einmal jährlich: Sichtprüfung und Funktionsprüfung aller Vakuumschläuche",
                     "beeinflusst": "O", "einschraenkung": "Jährliches Intervall — Schlauchschäden zwischen Prüfterminen nicht erkannt"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator anwesend; visuell erkennbare Schäden werden bemerkt",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm; Entdeckung abhängig von aktivem Beobachten"},
                    {"name": "Explosionsschutzdokument (ExSchDoc)", "typ": "Design", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Formale ATEX-Bewertung: Lufteintrag in Zone 1 als Szenario bewertet und als ausreichend gesichert eingestuft (Zone-1-Auslegung innen)",
                     "beeinflusst": "D", "einschraenkung": "Dokument muss aktuell gehalten werden; gilt für Normalbetrieb, nicht für grobe Schäden"},
                ],
                "S": 7, "O": 2, "D": 5,
                "begruendung_S": "Zone-1-Auslegung innen mitigiert Sofortgefahr. Hauptrisiko: Lösemittelaustritt und Prozessunterbrechung. Vollausfall 1-3 Monate, 50-250k € möglich bei schwerem Schlauchversagen.",
                "begruendung_O": "Sehr gering: Jährliche Schlauchwartung + Rückschlagventile. Schwere Vakuumschläden sind bei gut gewarteten Systemen selten (~1/100 Jahre).",
                "begruendung_D": "Mäßig wahrscheinlich: Sichtbare Schäden erkennbar, aber kein automatischer Vakuumdruck-Alarm. Operator muss aktiv beobachten.",
            },

            # FM-3a: Eiswasserausfall am Kondensator
            {
                "fehler_id": "20TA24-K001-FM3a",
                "funktion_id": "20TA24-KOMP-001-F3",
                "fehlermodus": "Eiswasserausfall — Kondensation fällt aus, Lösemitteldämpfe unkondensiert",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "Der Kopfkondensator kühlt Ethanoldämpfe mit Eiswasser (ca. 4 °C, max. 1 bar, "
                    "druckreduziert). Fällt die Eiswasserversorgung aus, kondensieren Ethanol-Dämpfe nicht "
                    "mehr und gelangen ungekühlt ins Abluftsystem. Kein unmittelbares Sicherheitsrisiko da "
                    "Abluftsystem intakt und Technikum Zone 2 ausgelegt."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM3a-U1", "beschreibung": "Ausfall der Werks-Eiswasserversorgung (Pumpe, Rohrbruch im Werksnetz)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM3a-U2", "beschreibung": "Versehentliches Absperren der Eiswasserzuleitung zum Kondensator", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM3a-U3", "beschreibung": "Fouling/Verstopfung im Kondensator-Eiswasserpfad (Kalkbelag)", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein direktes Personenrisiko; Ethanol-Dämpfe gehen ins Abluftsystem"),
                    "umwelt": ("Gering", "Erhöhter Lösemitteleintrag ins Abluftsystem, Abluftreinigung belastet"),
                    "anlage": ("Mäßig", "Produktverlust durch Lösemittelverdampfung; Prozessunterbrechung erforderlich"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Produktverlust, Prozessabbruch)"),
                },
                "controls": [
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt fehlende Kühlung (Temperatursanstieg am Kondensator-Ablauf sichtbar)",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm für Eiswasserausfall"},
                    {"name": "SV Eiswasserseite (1 bar)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Sicherheitsventil auf Eiswasserseite, begrenzt Eiswasserdruck auf max. 1 bar am Kondensator",
                     "beeinflusst": "D", "einschraenkung": "Schützt gegen Überdruck, nicht gegen Ausfall"},
                ],
                "S": 6, "O": 3, "D": 4,
                "begruendung_S": "Hoch: Prozessunterbrechung, Produktverlust, erhöhte Abluftemission. Kein direktes Sicherheitsrisiko bei intaktem Abluftsystem.",
                "begruendung_O": "Gering (~1/10 Jahre): Werksversorgung selten ausgefallen; Handventile selten versehentlich betätigt.",
                "begruendung_D": "Relativ wahrscheinlich: Temperaturerhöhung am Kondensatoraustritt sichtbar; Personenüberwachung erkennt Ausfall mit hoher Wahrscheinlichkeit.",
            },

            # FM-3b: Innere Leckage Kondensator
            {
                "fehler_id": "20TA24-K001-FM3b",
                "funktion_id": "20TA24-KOMP-001-F3",
                "fehlermodus": "Innere Leckage Kondensator — Durchbruch zwischen Eiswasser- und Produktseite",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "Produktseite: Auslegung -1 bis 0,5 bar. Eiswasserseite: druckreduziert max. 1 bar, "
                    "Auslegung 3 bar. Eiswasserdruck (max. 1 bar) übersteigt Produktseiten-PSV-Ansprechdruck (0,5 bar). "
                    "Bei innerer Leckage würde Eiswasser in Produktseite drücken → PSV/BSV sprechen bei 0,5 bar an "
                    "und leiten sicher in Blowdown. Betreiber entschieden: bestehende Controls ausreichend. "
                    "Safety Override S≥9 → mindestens hoch."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM3b-U1", "beschreibung": "Korrosion oder Riss im Kondensatorrohr durch Lösemittelkontakt", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM3b-U2", "beschreibung": "Thermischer Schock durch schnellen Temperaturwechsel (Eiswasser vs. heiße Dämpfe)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM3b-U3", "beschreibung": "Materialermüdung durch zyklische Druckbelastung (Vakuum ↔ leichter Überdruck)", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Kritisch", "Produktkontamination; Druckstoß durch Eiswasser → PSV/BSV Auslösung; kontrolliertes Szenario durch Druckabsicherung"),
                    "umwelt": ("Mäßig", "Unkontrollierter Austritt von Reaktionsgemisch möglich wenn PSV/BSV ansprechen"),
                    "anlage": ("Sehr hoch", "Produktverlust, Kontamination, Kondensatortausch, Reinigung des Blowdown-Systems"),
                    "kosten": ("Sehr hoch", "50.000–250.000 € (Produktverlust + Anlagenschäden)"),
                },
                "controls": [
                    {"name": "PSV (Sicherheitsventil)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Öffnet bei 0,5 bar → begrenzt Druck auf Produktseite, auch wenn Eiswasser eindringt (max. 1 bar Eiswasser → PSV/BSV öffnen bei 0,5 bar)",
                     "beeinflusst": "D", "einschraenkung": "PSV/BSV selbst könnten gleichzeitig versagen (FM-1 Szenario)"},
                    {"name": "BSV (Berstscheibe)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Redundante Druckabsicherung bei 0,5 bar, parallel zu PSV",
                     "beeinflusst": "D", "einschraenkung": "Einmalbauteil"},
                    {"name": "SV Eiswasserseite (1 bar)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Begrenzt Eiswasserdruck am Kondensator auf max. 1 bar (Auslegung Eiswasserseite: 3 bar)",
                     "beeinflusst": "D", "einschraenkung": "Verhindert Überschreitung der 3-bar-Auslegung, Eiswasser bleibt jedoch unter 1 bar"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt Druckanstieg an PI, Produktkontamination durch Trübung",
                     "beeinflusst": "D", "einschraenkung": "Innere Leckage initial schwer erkennbar"},
                ],
                "S": 9, "O": 2, "D": 6,
                "begruendung_S": "Kritisch: Druckstoß durch Eiswasser (1 bar > PSV 0,5 bar) → PSV/BSV-Aktivierung. Sicherheitsgerichtete Bauteile involviert. Safety Override: S≥9 → mindestens hoch. Betreiber-Entscheidung: bestehende Controls ausreichend.",
                "begruendung_O": "Sehr gering (~1/100 Jahre): Kondensator-Durchbrüche sind bei gut gewartetem Equipment sehr selten. Kein mechanisch beanspruchtes Bauteil (kein Druck außer Betriebsdruck).",
                "begruendung_D": "Unwahrscheinlich: Innere Leckage nicht direkt erkennbar ohne Produktkontaminationsanalyse. PI zeigt Druckanstieg, aber erst nach einiger Zeit.",
                "controls_einschraenkung": "Betreiber-Entscheidung (FMEA-Sitzung): bestehende Druckabsicherung PSV/BSV + SV Eiswasserseite ausreichend. Keine zusätzlichen Maßnahmen.",
            },

            # FM-4: N₂-Ausfall / Inertisierungsverlust
            {
                "fehler_id": "20TA24-K001-FM4",
                "funktion_id": "20TA24-KOMP-001-F4",
                "fehlermodus": "Stickstoffausfall — Verlust der Inertisierung und des N₂-Druckpolsters",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "Stickstoff (N₂) inertisiert den Reaktorkopfraum und die Wellendichtung des Rührwerks. "
                    "Reaktor innen Zone 1: alle internen Bauteile für gelegentlich explosive Atmosphäre ausgelegt. "
                    "Reaktor außen Zone 2: gesamte Außenausrüstung Ex-zertifiziert. "
                    "N₂-Ausfall bedeutet daher primär Prozessrisiko (O₂-Eintrag → Produktqualität) "
                    "und kein unkontrolliertes ATEX-Risiko (Design berücksichtigt Zone 1 innen bereits). "
                    "Kein automatischer N₂-Alarm vorhanden. Manometer (PI) am N₂-Anschluss (lokal, kalibriert jährlich). "
                    "N₂-Check vor jeder Charge in Herstellvorschrift integriert."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM4-U1", "beschreibung": "Ausfall der Werks-N₂-Versorgung (Druckabfall im Werksnetz)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM4-U2", "beschreibung": "Versehentliches Schließen des Kugelhahns (manuelle N₂-Absperrung)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM4-U3", "beschreibung": "Leckage in N₂-Zuleitung → schleichender Druckverlust", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM4-U4", "beschreibung": "Defekt am Druckminderer → falscher N₂-Druck (zu niedrig)", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein direktes Personenrisiko: Zone-1-Auslegung innen, Zone-2-Auslegung außen mitigieren ATEX-Risiko"),
                    "umwelt": ("Keine", "Kein Umweltrisiko durch N₂-Ausfall"),
                    "anlage": ("Mäßig", "O₂-Eintrag → Produktqualitätsverlust; Prozessunterbrechung, Charge möglicherweise verworfen"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Chargenverlust, Reinigung)"),
                },
                "controls": [
                    {"name": "PI (Manometer) N₂-Anschluss", "typ": "Messinstrument", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Pressure Indicator (Druckanzeige) am N₂-Anschluss, lokal ablesbar. Jährlich kalibriert.",
                     "beeinflusst": "D", "einschraenkung": "Nur lokale Anzeige, kein Alarm; Operator muss aktiv ablesen. Jährliche Kalibrierung sichert Anzeigegenauigkeit."},
                    {"name": "Kugelhahn N₂-Absperrung (manuell)", "typ": "Mechanisches Sicherheitselement", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Manuelle Absperrung N₂-Versorgung für Notfall-Abtrennung. Kein Überwachungselement.",
                     "beeinflusst": "O", "einschraenkung": "Nur für Notfall-Isolation vorgesehen, keine Monitoringfunktion"},
                ],
                "S": 5, "O": 3, "D": 7,
                "begruendung_S": "Mäßig: Zone-1-/Zone-2-Auslegung macht N₂-Ausfall zu keinem unkontrollierten ATEX-Risiko. Primäres Risiko ist Prozessqualität (O₂-Eintrag in empfindliche Polymersynthese).",
                "begruendung_O": "Gering (~1/10 Jahre): Werks-N₂-Versorgung selten ausgefallen. Kugelhahn-Fehler durch Personenüberwachung begrenzt.",
                "begruendung_D": "Sehr unwahrscheinlich: Kein automatischer N₂-Alarm. Operator muss PI aktiv ablesen. D=7 (Nur visuelle Prüfung, 10–30% Erkennungswahrscheinlichkeit ohne gezielten Check).",
            },

            # FM-5: Abluftsystem-Ausfall
            {
                "fehler_id": "20TA24-K001-FM5",
                "funktion_id": "20TA24-KOMP-001-F5",
                "fehlermodus": "Abluftsystem-Ausfall — Verlust des Unterdrucks (-9 bis -17 Pa), Dampfableitung gestört",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Das Abluftsystem erzeugt leichten Unterdruck (-9 bis -17 Pa) für gerichtete Dampfströmung. "
                    "Kein lokales Gebläse — zentrale Werksversorgung. Bei Ausfall: geschlossene Systeme verhindern "
                    "Dampfrückströmung ins Technikum. Ausfall wird werkszentral erkannt (Alarm). "
                    "SOP für Abluftreinigungsanlage-Ausfall existiert. Niedrig-Risiko-Szenario."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM5-U1", "beschreibung": "Ausfall des zentralen Abluftgebläses im Werk", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM5-U2", "beschreibung": "Verstopfung der Abluftleitung (Produktablagerungen)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM5-U3", "beschreibung": "Wartungsarbeiten am Abluftsystem ohne vorherige Prozessabsicherung", "herkunft": "Wartung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Keine", "Geschlossenes System: kein Dampfrückstrom ins Technikum bei Abluftverlust"),
                    "umwelt": ("Gering", "Dampfableitung vorübergehend nicht möglich; Abluftreinigung ausgefallen"),
                    "anlage": ("Relativ gering", "Prozessstopp erforderlich; Produktion unterbrochen"),
                    "kosten": ("Relativ gering", "< 1.000 € (Produktionsstopp, kein Schaden an Anlage)"),
                },
                "controls": [
                    {"name": "Werkszentraler Alarm (Abluftausfall)", "typ": "Automatisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Zentrales Werkssystem erkennt Abluftausfall und generiert automatisch Alarm",
                     "beeinflusst": "D", "einschraenkung": "Alarm geht an Werkstechnik — Reaktionszeit abhängig von Verfügbarkeit"},
                    {"name": "SOP Abluftreinigungsanlage-Ausfall", "typ": "Organisatorisch", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Definiertes Vorgehen bei Abluftsystem-Ausfall: Prozess stoppen, Dosierung unterbrechen",
                     "beeinflusst": "D", "einschraenkung": "SOP muss aktuell und bekannt sein; Schulung der Operatoren erforderlich"},
                    {"name": "Geschlossenes System", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Anlage ist geschlossen — bei Abluftverlust kein Dampfrückstrom ins Technikum",
                     "beeinflusst": "D", "einschraenkung": "Gilt für Normalbetrieb; bei geöffnetem Handloch anders"},
                ],
                "S": 4, "O": 4, "D": 2,
                "begruendung_S": "Relativ gering: Geschlossenes System verhindert Dampfrückstrom ins Technikum. Nur Prozessunterbrechung, kein direktes Sicherheitsrisiko.",
                "begruendung_O": "Relativ gering (~1/2 Jahre): Gebäudesysteme können ausfallen; kleiner Unterdruck (-9 bis -17 Pa) anfällig für Druckschwankungen.",
                "begruendung_D": "Sehr wahrscheinlich: Automatischer zentraler Alarm bei Ausfall. Frühzeitige Erkennung durch Werkstechnik.",
            },

            # FM-6: Leckage / Integritätsverlust
            {
                "fehler_id": "20TA24-K001-FM6",
                "funktion_id": "20TA24-KOMP-001-F6",
                "fehlermodus": "Äußere Leckage — Undichtigkeit an Flansch, Schlauchanschluss oder Wellendurchführung",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "Flanschverbindungen, Schlauchanschlüsse und Wellendurchführung des Rührwerks sind potenzielle "
                    "Leckagepunkte für Ethanol/Polymer-Reaktionsmasse. "
                    "Dichtigkeitstest vor JEDER Produktion im Rahmen der Inertisierungsüberprüfung ist ein starker "
                    "präventiver Control. Technikum dient als Auffangwanne (Volumen ≥ 1 m³). "
                    "AwSV-Relevanz: 1 m³ Ethanol im Technikum. Zone-2-Auslegung mitigiert Dampfrisiko."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM6-U1", "beschreibung": "Flanschdichtung defekt (Setzen, chemischer Angriff durch Ethanol, falscher Anzugsdrehmoment)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM6-U2", "beschreibung": "Schlauchanschluss undicht (Alterung, mechanische Belastung während Betrieb, Vibration durch Rührwerk)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM6-U3", "beschreibung": "Wellendurchführung Rührwerk verschlissen (Gleitringdichtung oder N₂-Spüldichtung defekt)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM6-U4", "beschreibung": "Probenahme-Anschluss nicht korrekt geschlossen oder undicht nach Entnahme", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol-Kontakt (Haut, Augen), Ausrutschen auf nasser Fläche; Zone-2-Auslegung mitigiert Explosionsrisiko"),
                    "umwelt": ("Mäßig", "Flüssigkeitsaustritt AwSV-relevant; Technikum als Auffangwanne vorhanden"),
                    "anlage": ("Hoch", "Produktverlust, Reinigungsaufwand, Materialschaden an Dichtungen/Schläuchen"),
                    "kosten": ("Hoch", "10.000–50.000 € (Produktverlust + Reinigung + Instandsetzung)"),
                },
                "controls": [
                    {"name": "Dichtigkeitstest vor jeder Produktion", "typ": "Organisatorisch (Prüfung)", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Druckhalteprüfung im Rahmen der Inertisierungsüberprüfung vor jeder Charge. Erkennt vorhandene Lecks vor Betriebsstart.",
                     "beeinflusst": "O", "einschraenkung": "Erfasst nur Lecks vor Betriebsstart; Lecks die sich WÄHREND der Produktion bilden (Vibration, Thermik) werden nicht erkannt"},
                    {"name": "Zone-2-Auslegung Technikum (Auffangwanne)", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Technikum dient als Auffangwanne mit Volumen ≥ 1 m³. AwSV-Containment. Zone-2-Equipment verhindert Zündquellen.",
                     "beeinflusst": "D", "einschraenkung": "Containment verhindert Umwelteintrag; schützt nicht gegen Personenkontakt"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt sichtbare Flüssigkeits- oder Dampfleckagen",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Leckage-Alarm; Entdeckung durch Beobachtung oder Geruch"},
                ],
                "S": 6, "O": 3, "D": 6,
                "begruendung_S": "Hoch: Produktverlust, AwSV-Relevanz bei Flüssigleckage, Personengefährdung durch Ethanol. Zone-2-Auslegung und Auffangwanne mitigieren, aber Teilausfall wahrscheinlich.",
                "begruendung_O": "Gering (~1/10 Jahre): Dichtigkeitstest vor jeder Charge ist starker präventiver Control. Restrisiko: Leckagen die sich erst WÄHREND Produktion entwickeln.",
                "begruendung_D": "Unwahrscheinlich: Keine automatische Leckageerkennung. Flüssige Leckagen visuell sichtbar, Dampfleckagen durch Geruch, aber kein Alarm. 30–50% Erkennungswahrscheinlichkeit.",
            },

            # FM-7: Thermostat-Fehlfunktion (Lauda)
            {
                "fehler_id": "20TA24-K001-FM7",
                "funktion_id": "20TA24-KOMP-001-F7",
                "fehlermodus": "Thermostat-Fehlfunktion — unkontrollierte Temperaturabweichung (Überhitzung oder Untertemperatur)",
                "fehlerart": "Thermisch",
                "kontext_beschreibung": (
                    "Der Lauda-Thermostat ist eine externe Utility-Schnittstelle (nicht interne PU-Technik). "
                    "Wichtig: Die Reaktion ist NICHT exotherm und birgt KEIN Runaway-Risiko (Polymersynthese). "
                    "Überhitzung durch Lauda → Dampfdruckanstieg → PSV/BSV schützen gegen Überdruck. "
                    "TI (Temperaturanzeige) am Reaktor ist lokal und kalibriert. Personenüberwachung aktiv. "
                    "Zone-1-Auslegung innen schützt gegen ATEX-Risiko bei erhöhter Verdampfung."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K001-FM7-U1", "beschreibung": "Defekt am Lauda-Thermostat (Heizung bleibt aktiv, Regelventil klemmt auf 'Heizen')", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM7-U2", "beschreibung": "Falscher Temperatursollwert eingegeben (Bedienfehler)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM7-U3", "beschreibung": "Thermostat-Totalausfall (Kein Heizen/Kühlen möglich) → Reaktion läuft bei Raumtemperatur", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K001-FM7-U4", "beschreibung": "Thermoschock durch plötzlichen Temperaturwechsel → mechanische Spannung im Borosilikatglas", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Überhitzung → erhöhte Dampfentwicklung, PSV/BSV können ansprechen → kontrollierter Druckabbau in Blowdown"),
                    "umwelt": ("Keine", "Kein direkter Umwelteintrag; PSV/BSV leiten in Blowdown"),
                    "anlage": ("Mäßig", "Produktqualitätsverlust (Temperaturabweichung beeinträchtigt Polymerisation), ggf. Chargenverlust"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Chargenverlust, Thermostat-Reparatur)"),
                },
                "controls": [
                    {"name": "TI (Temperaturanzeige) am Reaktor", "typ": "Messinstrument", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Temperature Indicator (Temperaturanzeige) am Reaktor, lokal ablesbar. Zeigt Reaktortemperatur unabhängig vom Lauda-Display.",
                     "beeinflusst": "D", "einschraenkung": "Nur lokale Anzeige, kein automatischer Alarm; Operator muss aktiv ablesen"},
                    {"name": "PSV + BSV (Druckabsicherung)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Schützen gegen Überdruck bei übermäßiger Verdampfung durch Überhitzung. Ansprechen bei 0,5 bar → Blowdown.",
                     "beeinflusst": "D", "einschraenkung": "Schützt gegen Druckfolgen, nicht gegen Produktschäden durch Temperaturabweichung"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator überwacht Reaktortemperatur am TI und Lauda-Display; erkennt Abweichungen",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm; abhängig von aktivem Monitoring durch Operator"},
                ],
                "S": 5, "O": 3, "D": 4,
                "begruendung_S": "Mäßig: Kein Runaway-Risiko (nicht-exotherme Reaktion). Überhitzung → PSV/BSV schützen. Hauptrisiko: Produktqualitätsverlust. Thermoschock → Glasrisiko (Borosilikat widerstandsfähig bis 200°C).",
                "begruendung_O": "Gering (~1/10 Jahre): Lauda-Thermostaten sind zuverlässige Industriegeräte. Fehler treten selten auf.",
                "begruendung_D": "Relativ wahrscheinlich: TI am Reaktor zeigt Temperatur unabhängig vom Lauda-Display. Operator + Personenüberwachung erkennen Abweichungen. 70–80% Erkennungswahrscheinlichkeit.",
            },
        ],
    },  # Ende KOMP-001

    # ─────────────────────────────────────────────────────────────────────────
    # KOMP-002: UF-Anlage 1 (Schnittstellen)
    # Package Unit – Ultrafiltration, identisch mit UF-Anlage 2.
    # Scope: nur Übergabepunkte. PSV/BSV → Blowdown. N₂ max. 1 bar.
    # ─────────────────────────────────────────────────────────────────────────
    "KOMP-002": {
        "functions": [
            {
                "funktion_id": "20TA24-KOMP-002-F1",
                "typ": "Sicherheitsfunktion",
                "beschreibung": "Druckabsicherung über PSV und BSV an UF-Anlage 1; Abblaseleitung in Blowdown-System.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-002-F1-A1", "parameter": "PSV/BSV Ansprechdruck", "sollwert": "projektspezifisch (PU-Daten vertraulich)"},
                    {"id": "20TA24-KOMP-002-F1-A2", "parameter": "Prüfintervall", "sollwert": "12 Monate (Annahme analog Reaktor)"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-002-F2",
                "typ": "Betriebsfunktion",
                "beschreibung": "N₂-Versorgung für UF-Anlage 1 (max. 1 bar). Druckhaltung, ggf. Inertisierung der Membranseite.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-002-F2-A1", "parameter": "Max. N₂-Zuführdruck", "sollwert": "1 bar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-002-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Abluftsystem-Anbindung für gerichtete Dampfableitung aus UF-Anlage 1.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-002-F4",
                "typ": "Betriebsfunktion",
                "beschreibung": "Thermostat-Anbindung für Temperaturkontrolle der UF-Membranseite/-umgebung.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-002-F5",
                "typ": "Grundfunktion",
                "beschreibung": "Schnittstellendichtigkeit aller Transferleitungen: Synthesereaktor → UF-Anlage 1, "
                                "UF-Anlage 1 → Poolingbehälter, Eluentenbehälter-Kreislauf-Anschlüsse.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-002-F5-A1", "parameter": "Dichtigkeitstest", "sollwert": "Vor jeder Charge (Gesamtanlage)"},
                ]
            },
        ],

        "failure_modes": [

            # FM-1: Druckabsicherungsversagen
            {
                "fehler_id": "20TA24-K002-FM1",
                "funktion_id": "20TA24-KOMP-002-F1",
                "fehlermodus": "Druckabsicherungsversagen — PSV oder BSV an UF-Anlage 1 öffnen nicht bei Überdruck",
                "fehlerart": "Sicherheit",
                "kontext_beschreibung": (
                    "Analog zu KOMP-001 FM-1: PSV und BSV sind sicherheitsgerichtete Bauteile (Safety Override: S=10). "
                    "Beide leiten in das gemeinsame Blowdown-System ein (wie Reaktor). "
                    "Interne Druckauslegungsdaten der UF-Anlage (PU) sind vertraulich — jährliche Prüfung als Standard. "
                    "Ethanol/Polymer-Lösung als Prozessmedium."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K002-FM1-U1", "beschreibung": "PSV klemmt durch Ablagerungen oder Korrosion", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM1-U2", "beschreibung": "BSV vorbelastet oder falsch eingebaut nach Wartung", "herkunft": "Fertigung", "phase": "Wartung"},
                    {"ursache_id": "20TA24-K002-FM1-U3", "beschreibung": "Blowdown-Leitung verstopft → Gegendruck verhindert PSV-Öffnen", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Kritisch", "Versagen Druckabsicherung → Behälter-/Apparateversagen möglich → Personengefährdung"),
                    "umwelt": ("Hoch", "Unkontrollierter Austritt von Ethanol/Polymerlösung"),
                    "anlage": ("Katastrophal", "Zerstörung UF-Anlage, Folgeschäden im Technikum"),
                    "kosten": ("Sehr hoch", "> 250.000 € (Anlage + Technikumschäden)"),
                },
                "controls": [
                    {"name": "PSV UF-Anlage 1", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Pressure Safety Valve an UF-Anlage 1, leitet in Blowdown. Prüfintervall 12 Monate.",
                     "beeinflusst": "D", "einschraenkung": "Jährliche Prüfung erforderlich; PU-interne Auslegungsdrücke vertraulich"},
                    {"name": "BSV UF-Anlage 1", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Bursting Disc an UF-Anlage 1, redundant zu PSV, in Blowdown.",
                     "beeinflusst": "D", "einschraenkung": "Einmalbauteil; Ersatz nach Auslösung erforderlich"},
                    {"name": "Blowdown-System", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Gemeinsame Abblaseleitung für alle Druckabsicherungen (Reaktor + UF-Anlagen).",
                     "beeinflusst": "D", "einschraenkung": "Verstopfung der gemeinsamen Leitung würde alle Druckabsicherungen beeinträchtigen"},
                ],
                "S": 10, "O": 2, "D": 4,
                "begruendung_S": "Safety Override: PSV und BSV sind sicherheitsgerichtete Bauteile → Mindest-S = 10.",
                "begruendung_O": "Sehr gering: Jährliche Prüfung. Analoges Ausfallrisiko wie Reaktor-PSV/BSV.",
                "begruendung_D": "Relativ wahrscheinlich: Jährliche 100%-Prüfung. Versagen zwischen Prüfterminen nicht sofort erkennbar.",
            },

            # FM-2: N₂-Versorgungsabweichung
            {
                "fehler_id": "20TA24-K002-FM2",
                "funktion_id": "20TA24-KOMP-002-F2",
                "fehlermodus": "N₂-Versorgungsabweichung — Ausfall oder Überdruck an UF-Anlage 1 (max. 1 bar)",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "N₂ wird mit max. 1 bar an UF-Anlage 1 geführt (Druckreduzierung aus Werksnetz 6-8 bar). "
                    "PSV/BSV an UF-Anlage schützen gegen Überdruckereignisse (N₂-Druckregler-Defekt). "
                    "Bei N₂-Ausfall: Druckabfall, möglicher O₂-Eintrag in Membranumgebung → Produktqualitätsrisiko. "
                    "Zone 2 außen. Interner Aufbau der UF-PU nicht im Scope."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K002-FM2-U1", "beschreibung": "N₂-Versorgungsausfall (Werksnetz)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM2-U2", "beschreibung": "N₂-Druckregler-Defekt → Überdruck > 1 bar oder Druckabfall", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM2-U3", "beschreibung": "Absperrventil N₂-Zuleitung versehentlich geschlossen", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Zone-2-Auslegung schützt; N₂-Ausfall bei max. 1 bar kein direktes Personenrisiko"),
                    "umwelt": ("Keine", "Kein Umweltrisiko durch N₂-Druckabweichung"),
                    "anlage": ("Mäßig", "Prozessunterbrechung; bei Überdruck greift PSV/BSV; bei Ausfall: O₂-Eintrag → Produktqualität"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Chargenverlust, Prozessabbruch)"),
                },
                "controls": [
                    {"name": "PSV + BSV UF-Anlage 1 (Überdruckschutz)", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Bei Druckregler-Defekt (Überdruck > 1 bar) schützen PSV/BSV gegen Druckereignis → Blowdown",
                     "beeinflusst": "D", "einschraenkung": "Schützt gegen Überdruck; kein Schutz gegen N₂-Ausfall (Druckabfall)"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt N₂-Druckabfall an lokalem Manometer oder Prozessanzeige",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm für N₂-Druckabfall an UF-Anlage"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Mäßig: PSV/BSV schützen gegen Überdruck. Hauptrisiko bei Ausfall: Produktqualität. Kein Runaway-Risiko.",
                "begruendung_O": "Gering (~1/10 Jahre): Druckregler-Defekte und N₂-Ausfälle selten bei regelmäßiger Wartung.",
                "begruendung_D": "Mäßig wahrscheinlich: Lokale Druckanzeige vorhanden (Annahme PU); Personenüberwachung. Kein automatischer Alarm.",
            },

            # FM-3: Abluftsystem-Ausfall (analog KOMP-001 FM-5)
            {
                "fehler_id": "20TA24-K002-FM3",
                "funktion_id": "20TA24-KOMP-002-F3",
                "fehlermodus": "Abluftsystem-Ausfall — gerichtete Dampfableitung von UF-Anlage 1 gestört",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Analog zu KOMP-001 FM-5: Werkszentraler Alarm bei Abluftausfall, SOP vorhanden. "
                    "Geschlossenes System: kein Dampfrückstrom ins Technikum. Niedrig-Risiko-Szenario. "
                    "UF-Anlage verarbeitet Ethanol-Eluent im kontinuierlichen Betrieb — mehr Prozesszeit "
                    "als Reaktor, daher leicht höheres Expositionsrisiko bei Abluftverlust."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K002-FM3-U1", "beschreibung": "Ausfall des zentralen Abluftgebläses", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM3-U2", "beschreibung": "Verstopfung der Abluftleitung", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Geschlossenes System; kein Dampfrückstrom ins Technikum"),
                    "umwelt": ("Gering", "Abluftreinigung ausgefallen; erhöhte Emissionen bei Öffnung von Anlagenteilen"),
                    "anlage": ("Relativ gering", "Prozessstopp; keine Anlageschäden"),
                    "kosten": ("Relativ gering", "< 1.000 €"),
                },
                "controls": [
                    {"name": "Werkszentraler Alarm (Abluftausfall)", "typ": "Automatisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Automatische Alarmmeldung bei Abluftsystem-Ausfall. Gilt für gesamtes Technikum.",
                     "beeinflusst": "D", "einschraenkung": "Reaktionszeit Werkstechnik variabel"},
                    {"name": "SOP Abluftreinigungsanlage-Ausfall", "typ": "Organisatorisch", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Definiertes Vorgehen: Prozess stoppen, Dosierung unterbrechen.",
                     "beeinflusst": "D", "einschraenkung": "Schulung und Aktualität der SOP erforderlich"},
                ],
                "S": 4, "O": 4, "D": 2,
                "begruendung_S": "Relativ gering: Analog KOMP-001 FM-5. Geschlossenes System verhindert Dampfrückstrom.",
                "begruendung_O": "Relativ gering (~1/2 Jahre): Zentrales Gebäudesystem, gelegentliche Ausfälle möglich.",
                "begruendung_D": "Sehr wahrscheinlich: Automatischer zentraler Alarm. Frühzeitige Erkennung.",
            },

            # FM-4: Thermostat-Fehlfunktion an UF-Anlage 1
            {
                "fehler_id": "20TA24-K002-FM4",
                "funktion_id": "20TA24-KOMP-002-F4",
                "fehlermodus": "Thermostat-Fehlfunktion — Temperaturabweichung an UF-Anlage 1",
                "fehlerart": "Thermisch",
                "kontext_beschreibung": (
                    "UF-Anlage 1 hat einen angeschlossenen Thermostat (Heiz-/Kühlsystem). "
                    "Ultrafiltration ist ein physikalischer Trennprozess ohne exotherme Reaktion — "
                    "kein Runaway-Risiko. Temperaturabweichung betrifft primär Membranintegrität "
                    "(Membranen sind temperaturempfindlich) und Produktqualität. "
                    "Interne Thermostat-Details (PU) sind nicht bekannt; Schnittstelle wird betrachtet."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K002-FM4-U1", "beschreibung": "Defekt am Thermostat (Heizung oder Kühlung versagt)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM4-U2", "beschreibung": "Falscher Temperatursollwert → Überhitzung oder Untertemperatur der Membran", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM4-U3", "beschreibung": "Thermostat-Totalausfall → keine Temperaturregelung", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein direktes Personenrisiko; UF ist physikalischer Prozess ohne gefährliche Exothermie"),
                    "umwelt": ("Keine", "Kein Umweltrisiko durch Temperaturabweichung"),
                    "anlage": ("Mäßig", "Membranschäden bei extremer Überhitzung; Produktqualitätsverlust; Chargenverlust"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Membrantausch + Chargenverlust)"),
                },
                "controls": [
                    {"name": "Temperaturüberwachung (PU-intern)", "typ": "Messinstrument", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Thermostat hat eigene Temperaturanzeige und -regelung (PU-interne Technik, Details vertraulich)",
                     "beeinflusst": "D", "einschraenkung": "PU-interne Details nicht im FMEA-Scope; Annahme: Thermostat hat eigene Alarmfunktion"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator überwacht Prozesstemperatur, bemerkt Abweichungen",
                     "beeinflusst": "D", "einschraenkung": "Kein separater unabhängiger Temperaturalarm bekannt"},
                ],
                "S": 4, "O": 3, "D": 5,
                "begruendung_S": "Relativ gering: Kein Runaway-Risiko. Hauptschaden: Membranintegrität und Produktqualität.",
                "begruendung_O": "Gering (~1/10 Jahre): Thermostaten sind zuverlässige Industriegeräte.",
                "begruendung_D": "Mäßig wahrscheinlich: PU-interner Temperaturmonitor vorhanden (Annahme). Personenüberwachung als Backup.",
            },

            # FM-5: Leckage an Schnittstellenpunkten (Transferleitungen)
            {
                "fehler_id": "20TA24-K002-FM5",
                "funktion_id": "20TA24-KOMP-002-F5",
                "fehlermodus": "Leckage an Transferleitungen — Undichtigkeit an Anschlüssen zu/von UF-Anlage 1",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "Transferleitungen verbinden Synthesereaktor → UF-Anlage 1, UF-Anlage 1 → Poolingbehälter "
                    "und Eluentenbehälter-Kreislauf. Ethanol/Polymerlösung als Medium. "
                    "Dichtigkeitstest vor jeder Produktion (Gesamtanlage) als präventiver Control. "
                    "Technikum = Auffangwanne (AwSV, ≥ 1 m³). Zone-2-Auslegung. "
                    "Kontinuierlicher UF-Betrieb erhöht Exposition gegenüber Reaktor-Batch-Betrieb."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K002-FM5-U1", "beschreibung": "Schlauchanschluss undicht (Alterung, mechanische Belastung durch Pumpenbetrieb)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM5-U2", "beschreibung": "Flanschdichtung defekt (Setzungseffekte, Vibrationen durch Kreislaufpumpe)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K002-FM5-U3", "beschreibung": "Fehlerhafter Anschluss nach Batch-Wechsel oder Reinigung", "herkunft": "Fertigung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol-Kontakt, Rutschgefahr; Zone-2-Auslegung mitigiert Explosionsrisiko"),
                    "umwelt": ("Mäßig", "Flüssigkeitsaustritt AwSV-relevant; Auffangwanne vorhanden"),
                    "anlage": ("Hoch", "Produktverlust, Reinigungsaufwand, Betriebsunterbrechung (kontinuierlicher Betrieb)"),
                    "kosten": ("Hoch", "10.000–50.000 € (Produktverlust + Reinigung bei längerem Betrieb)"),
                },
                "controls": [
                    {"name": "Dichtigkeitstest vor jeder Produktion (Gesamtanlage)", "typ": "Organisatorisch (Prüfung)", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Dichtigkeitsprüfung der Gesamtanlage inkl. Transferleitungen vor jeder Charge.",
                     "beeinflusst": "O", "einschraenkung": "Erfasst Lecks vor Betriebsstart; während kontinuierlichem UF-Betrieb entstehende Lecks nicht abgedeckt"},
                    {"name": "Zone-2-Auslegung + Auffangwanne", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Technikum als AwSV-konforme Auffangwanne; Zone-2-Equipment verhindert Zündquellen.",
                     "beeinflusst": "D", "einschraenkung": "Containment verhindert Umwelteintrag; schützt nicht gegen Personenkontakt"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt sichtbare Leckagen, Ethanol-Geruch",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Leckage-Alarm"},
                ],
                "S": 5, "O": 3, "D": 6,
                "begruendung_S": "Mäßig: Ethanol-Leckage mit AwSV-Relevanz. Auffangwanne und Zone-2-Auslegung mitigieren Sofortgefahr. Kontinuierlicher Betrieb erhöht kumulatives Risiko.",
                "begruendung_O": "Gering: Dichtigkeitstest vor Charge ist stark präventiver Control. Kontinuierlicher Betrieb vs. Reaktor-Batch.",
                "begruendung_D": "Unwahrscheinlich: Keine automatische Leckageerkennung. Visuell/olfaktorisch erkennbar, aber kein Alarm.",
            },
        ],
    },  # Ende KOMP-002

    # ─────────────────────────────────────────────────────────────────────────
    # KOMP-003: UF-Anlage 2 (Schnittstellen)
    # Identisch aufgebaut wie UF-Anlage 1 (KOMP-002).
    # Alle Fehlermodi analog — eigene fehler_ids für DB-Eindeutigkeit.
    # ─────────────────────────────────────────────────────────────────────────
    "KOMP-003": {
        "functions": [
            {
                "funktion_id": "20TA24-KOMP-003-F1",
                "typ": "Sicherheitsfunktion",
                "beschreibung": "Druckabsicherung über PSV und BSV an UF-Anlage 2; Abblaseleitung in Blowdown-System. Identisch wie UF-Anlage 1.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-003-F1-A1", "parameter": "PSV/BSV Ansprechdruck", "sollwert": "projektspezifisch (PU-Daten vertraulich)"},
                    {"id": "20TA24-KOMP-003-F1-A2", "parameter": "Prüfintervall", "sollwert": "12 Monate (Annahme analog Reaktor)"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-003-F2",
                "typ": "Betriebsfunktion",
                "beschreibung": "N₂-Versorgung für UF-Anlage 2 (max. 1 bar). Identisch wie UF-Anlage 1.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-003-F2-A1", "parameter": "Max. N₂-Zuführdruck", "sollwert": "1 bar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-003-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Abluftsystem-Anbindung für gerichtete Dampfableitung aus UF-Anlage 2.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-003-F4",
                "typ": "Betriebsfunktion",
                "beschreibung": "Thermostat-Anbindung für Temperaturkontrolle der UF-Membranseite. Identisch wie UF-Anlage 1.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-003-F5",
                "typ": "Grundfunktion",
                "beschreibung": "Schnittstellendichtigkeit aller Transferleitungen zu/von UF-Anlage 2. Identisch wie UF-Anlage 1.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-003-F5-A1", "parameter": "Dichtigkeitstest", "sollwert": "Vor jeder Charge (Gesamtanlage)"},
                ]
            },
        ],

        "failure_modes": [

            {
                "fehler_id": "20TA24-K003-FM1",
                "funktion_id": "20TA24-KOMP-003-F1",
                "fehlermodus": "Druckabsicherungsversagen — PSV oder BSV an UF-Anlage 2 öffnen nicht bei Überdruck",
                "fehlerart": "Sicherheit",
                "kontext_beschreibung": "Identisch wie UF-Anlage 1 (KOMP-002 FM-1). Separate Anlage mit eigenem PSV/BSV → Blowdown.",
                "causes": [
                    {"ursache_id": "20TA24-K003-FM1-U1", "beschreibung": "PSV klemmt durch Ablagerungen oder Korrosion", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K003-FM1-U2", "beschreibung": "BSV vorbelastet oder falsch eingebaut", "herkunft": "Fertigung", "phase": "Wartung"},
                    {"ursache_id": "20TA24-K003-FM1-U3", "beschreibung": "Blowdown-Leitung verstopft", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Kritisch", "Versagen Druckabsicherung → Apparateversagen möglich → Personengefährdung"),
                    "umwelt": ("Hoch", "Unkontrollierter Austritt von Ethanol/Polymerlösung"),
                    "anlage": ("Katastrophal", "Zerstörung UF-Anlage 2, Folgeschäden im Technikum"),
                    "kosten": ("Sehr hoch", "> 250.000 €"),
                },
                "controls": [
                    {"name": "PSV UF-Anlage 2", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "PSV an UF-Anlage 2, leitet in Blowdown. Prüfintervall 12 Monate.",
                     "beeinflusst": "D", "einschraenkung": "Jährliche Prüfung erforderlich"},
                    {"name": "BSV UF-Anlage 2", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "BSV an UF-Anlage 2, redundant zu PSV, in Blowdown.",
                     "beeinflusst": "D", "einschraenkung": "Einmalbauteil"},
                    {"name": "Blowdown-System", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Gemeinsame Abblaseleitung (Reaktor + beide UF-Anlagen).",
                     "beeinflusst": "D", "einschraenkung": "Verstopfung betrifft alle angeschlossenen Druckabsicherungen"},
                ],
                "S": 10, "O": 2, "D": 4,
                "begruendung_S": "Safety Override: PSV und BSV sind sicherheitsgerichtete Bauteile → S = 10.",
                "begruendung_O": "Identisch UF-Anlage 1: Sehr gering durch jährliche Prüfung.",
                "begruendung_D": "Identisch UF-Anlage 1: Jährliche Prüfung, Versagen dazwischen nicht sofort erkennbar.",
            },

            {
                "fehler_id": "20TA24-K003-FM2",
                "funktion_id": "20TA24-KOMP-003-F2",
                "fehlermodus": "N₂-Versorgungsabweichung — Ausfall oder Überdruck an UF-Anlage 2",
                "fehlerart": "Prozess",
                "kontext_beschreibung": "Identisch wie UF-Anlage 1 (KOMP-002 FM-2). Gleiche N₂-Versorgung (max. 1 bar). PSV/BSV schützen gegen Überdruck.",
                "causes": [
                    {"ursache_id": "20TA24-K003-FM2-U1", "beschreibung": "N₂-Versorgungsausfall (Werksnetz)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K003-FM2-U2", "beschreibung": "N₂-Druckregler-Defekt → Überdruck oder Druckabfall", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Zone-2-Auslegung schützt; N₂ max. 1 bar kein direktes Personenrisiko"),
                    "umwelt": ("Keine", "Kein Umweltrisiko"),
                    "anlage": ("Mäßig", "Prozessunterbrechung; O₂-Eintrag → Produktqualität"),
                    "kosten": ("Mäßig", "1.000–10.000 €"),
                },
                "controls": [
                    {"name": "PSV + BSV UF-Anlage 2", "typ": "Sicherheitseinrichtung", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Schützen gegen Überdruck (Druckregler-Defekt) → Blowdown.",
                     "beeinflusst": "D", "einschraenkung": "Schützt gegen Überdruck, nicht gegen N₂-Ausfall"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt N₂-Druckabfall am lokalen Manometer.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Identisch UF-Anlage 1: Mäßig. PSV/BSV schützen. Hauptrisiko Produktqualität.",
                "begruendung_O": "Identisch: Gering (~1/10 Jahre).",
                "begruendung_D": "Identisch: Mäßig wahrscheinlich (lokale Anzeige + Personenüberwachung).",
            },

            {
                "fehler_id": "20TA24-K003-FM3",
                "funktion_id": "20TA24-KOMP-003-F3",
                "fehlermodus": "Abluftsystem-Ausfall — Dampfableitung von UF-Anlage 2 gestört",
                "fehlerart": "Equipment",
                "kontext_beschreibung": "Identisch wie UF-Anlage 1 (KOMP-002 FM-3). Werkszentraler Alarm, SOP vorhanden. Geschlossenes System.",
                "causes": [
                    {"ursache_id": "20TA24-K003-FM3-U1", "beschreibung": "Ausfall des zentralen Abluftgebläses", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K003-FM3-U2", "beschreibung": "Verstopfung der Abluftleitung", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Geschlossenes System; kein Dampfrückstrom"),
                    "umwelt": ("Gering", "Abluftreinigung ausgefallen"),
                    "anlage": ("Relativ gering", "Prozessstopp"),
                    "kosten": ("Relativ gering", "< 1.000 €"),
                },
                "controls": [
                    {"name": "Werkszentraler Alarm", "typ": "Automatisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Automatische Alarmmeldung bei Abluftsystem-Ausfall.",
                     "beeinflusst": "D", "einschraenkung": "Reaktionszeit Werkstechnik variabel"},
                    {"name": "SOP Abluftreinigungsanlage-Ausfall", "typ": "Organisatorisch", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Definiertes Vorgehen: Prozess stoppen.",
                     "beeinflusst": "D", "einschraenkung": "Schulung und Aktualität erforderlich"},
                ],
                "S": 4, "O": 4, "D": 2,
                "begruendung_S": "Identisch UF-Anlage 1.",
                "begruendung_O": "Identisch.",
                "begruendung_D": "Identisch: Automatischer zentraler Alarm.",
            },

            {
                "fehler_id": "20TA24-K003-FM4",
                "funktion_id": "20TA24-KOMP-003-F4",
                "fehlermodus": "Thermostat-Fehlfunktion — Temperaturabweichung an UF-Anlage 2",
                "fehlerart": "Thermisch",
                "kontext_beschreibung": "Identisch wie UF-Anlage 1 (KOMP-002 FM-4). Keine exotherme Reaktion. Membranschäden bei Extremtemperatur.",
                "causes": [
                    {"ursache_id": "20TA24-K003-FM4-U1", "beschreibung": "Thermostat-Defekt (Heizung oder Kühlung)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K003-FM4-U2", "beschreibung": "Falscher Temperatursollwert", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein Personenrisiko; physikalischer Prozess"),
                    "umwelt": ("Keine", "Kein Umweltrisiko"),
                    "anlage": ("Mäßig", "Membranschäden; Produktqualitätsverlust"),
                    "kosten": ("Mäßig", "1.000–10.000 €"),
                },
                "controls": [
                    {"name": "Temperaturüberwachung (PU-intern)", "typ": "Messinstrument", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Thermostat hat eigene Regelung und Anzeige (PU-intern, Details vertraulich).",
                     "beeinflusst": "D", "einschraenkung": "PU-interne Details nicht im Scope"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator überwacht Prozesstemperatur.",
                     "beeinflusst": "D", "einschraenkung": "Kein unabhängiger externer Alarm"},
                ],
                "S": 4, "O": 3, "D": 5,
                "begruendung_S": "Identisch UF-Anlage 1.",
                "begruendung_O": "Identisch.",
                "begruendung_D": "Identisch.",
            },

            {
                "fehler_id": "20TA24-K003-FM5",
                "funktion_id": "20TA24-KOMP-003-F5",
                "fehlermodus": "Leckage an Transferleitungen — Undichtigkeit an Anschlüssen zu/von UF-Anlage 2",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": "Identisch wie UF-Anlage 1 (KOMP-002 FM-5). Dichtigkeitstest vor Charge, Auffangwanne, Zone-2-Auslegung.",
                "causes": [
                    {"ursache_id": "20TA24-K003-FM5-U1", "beschreibung": "Schlauchanschluss undicht (Alterung, Pumpenbetrieb)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K003-FM5-U2", "beschreibung": "Flanschdichtung defekt (Vibrationen, Setzungseffekte)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K003-FM5-U3", "beschreibung": "Fehlerhafter Anschluss nach Reinigung oder Chargenwechsel", "herkunft": "Fertigung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol-Kontakt, Rutschgefahr; Zone-2-Auslegung mitigiert"),
                    "umwelt": ("Mäßig", "AwSV-relevant; Auffangwanne vorhanden"),
                    "anlage": ("Hoch", "Produktverlust, Betriebsunterbrechung"),
                    "kosten": ("Hoch", "10.000–50.000 €"),
                },
                "controls": [
                    {"name": "Dichtigkeitstest vor jeder Produktion", "typ": "Organisatorisch (Prüfung)", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Gesamtanlagen-Dichtigkeitsprüfung vor jeder Charge.",
                     "beeinflusst": "O", "einschraenkung": "Während Betrieb entstehende Lecks nicht abgedeckt"},
                    {"name": "Zone-2-Auslegung + Auffangwanne", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "AwSV-konforme Auffangwanne; Zone-2-Equipment.",
                     "beeinflusst": "D", "einschraenkung": "Containment vorhanden; Personenkontakt nicht ausgeschlossen"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator erkennt sichtbare Leckagen.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm"},
                ],
                "S": 5, "O": 3, "D": 6,
                "begruendung_S": "Identisch UF-Anlage 1.",
                "begruendung_O": "Identisch.",
                "begruendung_D": "Identisch.",
            },
        ],
    },  # Ende KOMP-003

    # ─────────────────────────────────────────────────────────────────────────
    # KOMP-004: Eluentenbehälter (KTC-Container)
    # 1000 L Edelstahl, atmosphärisch, Zone 2, AwSV (1 m³ Ethanol).
    # Kreislaufpumpe (Peripheralradpumpe, FU-gesteuert, Liquiphant-Trockenlaufschutz).
    # SV 100 mbar; Auffangwanne = Technikum (≥ 1 m³).
    # ─────────────────────────────────────────────────────────────────────────
    "KOMP-004": {
        "functions": [
            {
                "funktion_id": "20TA24-KOMP-004-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Eluentvorrat (Ethanol, 1000 L) für UF-Kreislauf bereitstellen. "
                                "Kreislaufpumpe fördert kontinuierlich; UF-Anlagen zweigen Bedarf ab.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-004-F1-A1", "parameter": "Nennvolumen", "sollwert": "1000 L"},
                    {"id": "20TA24-KOMP-004-F1-A2", "parameter": "Betriebsdruck", "sollwert": "atmosphärisch"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-004-F2",
                "typ": "Betriebsfunktion",
                "beschreibung": "Kreislaufpumpe (Peripheralradpumpe, max. 9 m WS) fördert Eluent kontinuierlich. "
                                "Drehzahlregelung über Frequenzumrichter. Trockenlaufschutz via Liquiphant "
                                "(Füllstandsschalter → Pumpenabschaltung bei Unterschreitung).",
                "anforderungen": [
                    {"id": "20TA24-KOMP-004-F2-A1", "parameter": "Max. Förderhöhe", "sollwert": "9 m WS"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-004-F3",
                "typ": "Sicherheitsfunktion",
                "beschreibung": "N₂-Überlagerung schützt Ethanol-Oberfläche vor O₂-Zutritt und verhindert "
                                "Bildung explosionsfähiger Atmosphäre im Behälterinneren. SV 100 mbar.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-004-F3-A1", "parameter": "SV Ansprechdruck", "sollwert": "100 mbar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-004-F4",
                "typ": "Nebenfunktion",
                "beschreibung": "Abluftsystem-Anbindung bei Befüllung: Ethanol-Dämpfe werden über Abluftsystem "
                                "(Unterdruck) abgeleitet. Ausfallszenarien sind im FMEA-Scope.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-004-F5",
                "typ": "Grundfunktion",
                "beschreibung": "Mechanische Integrität des Edelstahlbehälters und aller Rohrleitungsanschlüsse. "
                                "AwSV-konformes Containment durch Technikum als Auffangwanne (≥ 1 m³).",
                "anforderungen": [
                    {"id": "20TA24-KOMP-004-F5-A1", "parameter": "Containment", "sollwert": "Technikum ≥ 1 m³"},
                ]
            },
        ],
        "failure_modes": [

            # FM-1: Überfüllung KTC-Container
            {
                "fehler_id": "20TA24-K004-FM1",
                "funktion_id": "20TA24-KOMP-004-F1",
                "fehlermodus": "Überfüllung KTC-Container — Ethanol-Überlauf durch fehlende Überfüllsicherung",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "1000-L-KTC-Container wird manuell oder halbautomatisch befüllt (Lösemittelzuführung). "
                    "Liquiphant schützt nur gegen Trockenlauf der Kreislaufpumpe (unten), nicht gegen Überfüllung (oben). "
                    "Kein LSH-Alarm für Überfüllschutz vorhanden. Zone 2, AwSV: 1 m³ Ethanol ≙ gesamtes Technikum-Auffangvolumen."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K004-FM1-U1", "beschreibung": "Befüllung ohne korrekte Füllstandsüberwachung (kein LSH-Alarm)", "herkunft": "Design", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM1-U2", "beschreibung": "Bedienfehler: Befüllventil zu lange offen / falsche Mengenvorgabe", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM1-U3", "beschreibung": "Liquiphant-Fehlfunktion (Trockenlaufschalter ≠ Überfüllschalter)", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol-Austritt auf Technikumsboden; Rutschgefahr, Dämpfe (Flammpunkt 13 °C); Zone-2-Auslegung mitigiert"),
                    "umwelt": ("Hoch", "AwSV: Ethanol WGK 1; 1 m³ Vollüberlauf belastet Auffangwanne vollständig"),
                    "anlage": ("Hoch", "Produktionsstopp; AwSV-Meldepflicht; Reinigung Technikum"),
                    "kosten": ("Hoch", "10.000–50.000 € (Reinigung, Produktionsverlust, Behördenmeldung)"),
                },
                "controls": [
                    {"name": "Liquiphant (Trockenlaufschutz Pumpe)", "typ": "Füllstandsschalter", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Schützt Kreislaufpumpe gegen Trockenlauf (unten). Kein Schutz gegen Überfüllung.",
                     "beeinflusst": "D", "einschraenkung": "Ausgelegt als Unterfüllschutz — keine Überfüllfunktion"},
                    {"name": "Auffangwanne (Technikum, ≥ 1 m³)", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "AwSV-konforme Auffangwanne; aufnimmt Vollinhalt KTC bei Leckage/Überlauf.",
                     "beeinflusst": "D", "einschraenkung": "Sekundärcontainment; Primärereignis (Überlauf) wird nicht verhindert"},
                    {"name": "Personenüberwachungsbetrieb (Befüllung)", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator überwacht Füllstand visuell während Befüllung.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Füllstandsalarm; visuelle Überwachung fehleranfällig"},
                ],
                "S": 6, "O": 4, "D": 6,
                "begruendung_S": "Hoch: Ethanol-Überlauf 1 m³ belegt Auffangwanne vollständig; AwSV-Meldepflicht; Kosten 10–50k€. Kein Personenschaden erwartet durch Zone-2-Auslegung.",
                "begruendung_O": "Relativ gering (~1/2 Jahre): Manuelle Befüllung mehrmals/Jahr; kein LSH-Alarm erhöht Fehlerwahrscheinlichkeit gegenüber automatisierten Systemen.",
                "begruendung_D": "Unwahrscheinlich: Kein automatischer Füllstandsalarm. Nur visuelle Überwachung + Auffangwanne als Entdeckungssystem.",
            },

            # FM-2: Kreislaufpumpe Ausfall
            {
                "fehler_id": "20TA24-K004-FM2",
                "funktion_id": "20TA24-KOMP-004-F2",
                "fehlermodus": "Kreislaufpumpe Ausfall — kein Eluentstrom zu UF-Anlagen",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Peripheralradpumpe mit FU-Steuerung. Ausfall durch Motordefekt, FU-Fehler oder elektrische Störung. "
                    "Liquiphant schaltet Pumpe bei Unterschreitung des Min-Füllstands ab (Schutzabschaltung). "
                    "Ausfall führt zu Prozessunterbrechung der UF-Anlagen (kein Eluent)."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K004-FM2-U1", "beschreibung": "FU-Defekt oder elektrische Störung", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM2-U2", "beschreibung": "Pumpenversagen (mechanisch: Lager, Gleitring)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM2-U3", "beschreibung": "Liquiphant-Schutzabschaltung bei zu niedrigem Füllstand", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein Personenrisiko; rein prozesstechnischer Ausfall"),
                    "umwelt": ("Keine", "Kein Umweltrisiko durch Pumpenausfall"),
                    "anlage": ("Mäßig", "UF-Betrieb gestoppt; Prozessunterbrechung; Charge gefährdet"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Ausfallzeit, Chargenverlust)"),
                },
                "controls": [
                    {"name": "Liquiphant (Trockenlaufschutz)", "typ": "Füllstandsschalter", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Schutzabschaltung Pumpe bei Min-Füllstand → verhindert Trockenlaufschäden.",
                     "beeinflusst": "D", "einschraenkung": "Verhindert Pumpenschaden; stoppt aber auch Prozess"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator bemerkt Ausfall durch Druckabfall oder Flowsignal der UF-Anlage.",
                     "beeinflusst": "D", "einschraenkung": "Kein eigener Pumpenalarm; Erkennung indirekt über UF-Anlagenreaktion"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Mäßig: Prozessunterbrechung, Chargenverlust möglich. Kein Sicherheitsrisiko.",
                "begruendung_O": "Gering (~1/10 Jahre): FU-gesteuerte Pumpen selten. Liquiphant-Schutzabschaltung erhöht scheinbare Häufigkeit, aber nicht das Risiko.",
                "begruendung_D": "Mäßig wahrscheinlich: Kein Pumpenalarm; Erkennung über UF-Anlagenreaktion oder Bedienerbeobachtung.",
            },

            # FM-3: N₂-Überlagerung Ausfall
            {
                "fehler_id": "20TA24-K004-FM3",
                "funktion_id": "20TA24-KOMP-004-F3",
                "fehlermodus": "N₂-Überlagerung Ausfall — Verlust Inertisierung über Ethanol im KTC-Container",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "N₂ überlagert Ethanol im KTC-Container. Ausfall → Luft-Eintrag → O₂-Ethanol-Dampf-Gemisch möglich. "
                    "Zone 2 außen; Equipment ATEX-ausgelegt. Analog KOMP-001 FM-4: kein Zone-1-Interior im KTC; "
                    "atmosphärischer Behälter, oben offen über Abluft. N₂-Ausfall primär Produktqualitätsrisiko."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K004-FM3-U1", "beschreibung": "N₂-Versorgungsausfall (Werksnetz)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM3-U2", "beschreibung": "N₂-Druckregler-Defekt oder Absperrventil geschlossen", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Zone-2-Auslegung; N₂-Ausfall bei atmosphärischem Behälter kein direktes Personenrisiko"),
                    "umwelt": ("Keine", "Kein Umweltrisiko durch N₂-Ausfall"),
                    "anlage": ("Mäßig", "O₂-Eintrag; mögliche Produktkontamination; Prozessqualität beeinträchtigt"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Chargenverlust, Qualitätsprüfung)"),
                },
                "controls": [
                    {"name": "SV 100 mbar (Überdruckschutz KTC)", "typ": "Sicherheitsventil", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Absicherung gegen N₂-Überdruck. Kein Schutz gegen N₂-Ausfall.",
                     "beeinflusst": "D", "einschraenkung": "Schützt gegen Überdruck, nicht gegen Druckabfall/Ausfall"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator prüft N₂-Versorgung regelmäßig (Manometer oder Sichtkontrolle).",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer N₂-Druckalarm am KTC; Erkennung nur manuell"},
                ],
                "S": 5, "O": 3, "D": 6,
                "begruendung_S": "Mäßig: Analog KOMP-001 FM-4. Hauptrisiko Produktqualität. Zone-2-Auslegung; kein Personenrisiko.",
                "begruendung_O": "Gering (~1/10 Jahre): N₂-Ausfälle im Werksnetz selten; Druckregler gelegentlich defekt.",
                "begruendung_D": "Unwahrscheinlich: Kein automatischer N₂-Alarm am KTC. Nur manuelle Prüfung.",
            },

            # FM-4: Abluftsystem-Ausfall (Befüllung)
            {
                "fehler_id": "20TA24-K004-FM4",
                "funktion_id": "20TA24-KOMP-004-F4",
                "fehlermodus": "Abluftsystem-Ausfall — Ethanol-Dämpfe bei KTC-Befüllung nicht abgeleitet",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Abluftsystem zieht Ethanol-Dämpfe bei Befüllung des KTC-Containers ab. "
                    "Analog KOMP-001 FM-5: Werkszentraler Alarm + SOP. Behälter bleibt geschlossen außerhalb Befüllphase. "
                    "Niedrig-Risiko-Szenario durch organisatorische Absicherung."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K004-FM4-U1", "beschreibung": "Ausfall des zentralen Abluftgebläses", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM4-U2", "beschreibung": "Verstopfung der Abluftleitung am KTC-Anschluss", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein Rückstrom ins Technikum; Dämpfe bei Befüllung unkontrolliert — aber Zone-2-Auslegung"),
                    "umwelt": ("Gering", "Erhöhte Ethanol-Emissionen ins Technikum bei Befüllung; AGW Ethanol 200 ppm"),
                    "anlage": ("Relativ gering", "Befüllungsstopp erforderlich; keine Anlagenschäden"),
                    "kosten": ("Relativ gering", "< 1.000 €"),
                },
                "controls": [
                    {"name": "Werkszentraler Alarm (Abluftausfall)", "typ": "Automatisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Automatische Alarmmeldung bei Abluftsystem-Ausfall. Gilt für gesamtes Technikum.",
                     "beeinflusst": "D", "einschraenkung": "Reaktionszeit Werkstechnik variabel"},
                    {"name": "SOP Abluftreinigungsanlage-Ausfall", "typ": "Organisatorisch", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Definiertes Vorgehen: Befüllung stoppen, Dosierung unterbrechen.",
                     "beeinflusst": "D", "einschraenkung": "Schulung und Aktualität der SOP erforderlich"},
                ],
                "S": 4, "O": 4, "D": 2,
                "begruendung_S": "Relativ gering: Analog KOMP-001 FM-5. Zone-2-Auslegung. Kein Rückstrom; nur Befüllungsphase betroffen.",
                "begruendung_O": "Relativ gering (~1/2 Jahre): Zentrales Gebäudesystem; gelegentliche Ausfälle möglich.",
                "begruendung_D": "Sehr wahrscheinlich: Automatischer zentraler Alarm. Frühzeitige Erkennung.",
            },

            # FM-5: Leckage KTC-Behälter / Kreislaufleitungen
            {
                "fehler_id": "20TA24-K004-FM5",
                "funktion_id": "20TA24-KOMP-004-F5",
                "fehlermodus": "Leckage KTC-Behälter oder Kreislaufleitungen — Ethanol-Austritt (AwSV)",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "Edelstahlbehälter (1000 L) mit Kreislaufleitung zur Pumpe und UF-Anlagen. "
                    "Leckage an Flansch, Schweiß naht oder Schlauchanschluss möglich. "
                    "AwSV: 1 m³ Ethanol → Technikum als Auffangwanne (≥ 1 m³). Leckagesensor am Technikumsboden."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K004-FM5-U1", "beschreibung": "Flanschdichtung defekt (Setzung, Korrosion)", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM5-U2", "beschreibung": "Schlauchleitung undicht (Alterung, Vibration der Pumpe)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K004-FM5-U3", "beschreibung": "Externe mechanische Einwirkung (Staplerverkehr im Technikum)", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol auf Technikumsboden; Rutschgefahr, Dämpfe; Zone-2-Auslegung"),
                    "umwelt": ("Mäßig", "AwSV-relevant; Auffangwanne vorhanden; WGK 1"),
                    "anlage": ("Hoch", "Produktionsstopp; Behälterentleerung; Reinigung"),
                    "kosten": ("Hoch", "10.000–50.000 € (Instandsetzung, Produktionsverlust)"),
                },
                "controls": [
                    {"name": "Leckagesensor Technikumsboden", "typ": "Sensor", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Erkennt Flüssigkeit auf Technikumsboden → Alarm.",
                     "beeinflusst": "D", "einschraenkung": "Erkennt erst bei größerer Leckage (Sensor am Boden)"},
                    {"name": "Auffangwanne (Technikum, ≥ 1 m³)", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "AwSV-konforme Auffangwanne; aufnimmt Vollinhalt KTC.",
                     "beeinflusst": "D", "einschraenkung": "Sekundärcontainment; Primärleckage wird nicht verhindert"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator erkennt sichtbare Leckagen oder Feuchtigkeitsflecken.",
                     "beeinflusst": "D", "einschraenkung": "Kleine Leckagen zunächst nicht sichtbar"},
                ],
                "S": 6, "O": 2, "D": 4,
                "begruendung_S": "Hoch: Edelstahlbehälter robust; aber 1000 L Ethanol (AwSV) → signifikanter Umwelt- und Betriebsschaden.",
                "begruendung_O": "Sehr gering (~1/100 Jahre): Edelstahlbehälter langlebig; regelmäßige Inspektion.",
                "begruendung_D": "Relativ wahrscheinlich: Leckagesensor + Personenüberwachung + Auffangwanne als kombiniertes Detektionssystem.",
            },
        ],
    },  # Ende KOMP-004

    # ─────────────────────────────────────────────────────────────────────────
    # KOMP-005: Poolingbehälter
    # ~200 L Edelstahl, Auslegung 6 bar. Zone 2.
    # KRITISCH: Kein SV / BSV — Überdruckschutz NUR über N₂-Druckreduzierung.
    # Rührwerk vorhanden. N₂ mehrere Druckstufen. Abluft mehrere Druckstufen.
    # ─────────────────────────────────────────────────────────────────────────
    "KOMP-005": {
        "functions": [
            {
                "funktion_id": "20TA24-KOMP-005-F1",
                "typ": "Sicherheitsfunktion",
                "beschreibung": "Überdruckschutz — ausschließlich über N₂-Druckreduzierung (begrenzte N₂-Zuführdrücke). "
                                "KEIN Sicherheitsventil, KEINE Berstscheibe vorhanden. Auslegungsdruck: 6 bar.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-005-F1-A1", "parameter": "Max. Auslegungsdruck", "sollwert": "6 bar"},
                    {"id": "20TA24-KOMP-005-F1-A2", "parameter": "N₂-Zuführdruck max.", "sollwert": "Druckreduzierer gemäß Druckstufen"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-005-F2",
                "typ": "Hauptfunktion",
                "beschreibung": "Zwischenlagerung des aufgereinigten Polymers in ethanolischer Lösung (ca. 200 L). "
                                "Produktübergabe an Transfer-System downstream. Probenahme möglich.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-005-F2-A1", "parameter": "Nennvolumen", "sollwert": "ca. 200 L"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-005-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "N₂-Überlagerung und Druckhaltung (mehrere Druckstufen: 40 mbar, 300 mbar, 2,5 bar). "
                                "Gleichzeitig einziger Überdruckschutz — Druckreduzierer als primäre Barriere.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-005-F3-A1", "parameter": "N₂-Druckstufen", "sollwert": "40 mbar / 300 mbar / 2,5 bar"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-005-F4",
                "typ": "Nebenfunktion",
                "beschreibung": "Abluftsystem-Anbindung (mehrere Druckstufen) zur kontrollierten Ableitung "
                                "von Ethanol-Dämpfen. Werkszentraler Alarm bei Abluftsystem-Ausfall.",
                "anforderungen": []
            },
            {
                "funktion_id": "20TA24-KOMP-005-F5",
                "typ": "Grundfunktion",
                "beschreibung": "Mechanische Integrität des Edelstahlbehälters, Rührwerksdurchführung "
                                "und aller Schlauchanschlüsse downstream (Transfer-System).",
                "anforderungen": []
            },
        ],
        "failure_modes": [

            # FM-1: Überdruck — N₂-Druckregler-Defekt ohne SV-Schutz
            {
                "fehler_id": "20TA24-K005-FM1",
                "funktion_id": "20TA24-KOMP-005-F1",
                "fehlermodus": "Überdruck — N₂-Druckregler-Defekt bei fehlendem Sicherheitsventil",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "Poolingbehälter hat KEIN SV und KEINE BSV. Einziger Überdruckschutz = N₂-Druckreduzierung. "
                    "N₂-Werksnetz: 6–8 bar; Druckminderer auf 40 mbar / 300 mbar / 2,5 bar. "
                    "Bei Druckregler-Defekt (Vollöffnung) → Werksnetz-Druck → Behälterauslegung 6 bar am Limit. "
                    "Kein MSR mit Druckalarm am Poolingbehälter vorhanden. Single-Point-Failure: Druckreduzierer."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K005-FM1-U1", "beschreibung": "N₂-Druckregler-Defekt (mechanisch, federbelastet) → Vollöffnung → Werksnetz-Druck", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K005-FM1-U2", "beschreibung": "Verschmutzter/blockierter Druckregler → plötzliches Versagen", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K005-FM1-U3", "beschreibung": "Falscher Druckregler verbaut (falsche Einstellung)", "herkunft": "Design", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Katastrophal", "Behälterbersten möglich bei Überschreitung 6 bar; Splitter, Druckwelle, Ethanol-Dampf-Explosion (Zone 2); Schwerverletzte"),
                    "umwelt": ("Sehr hoch", "unkontrollierter Ethanol-Austritt; explosionsfähige Atmosphäre im Technikum"),
                    "anlage": ("Katastrophal", "Zerstörung Poolingbehälter + umliegende Ausrüstung; weitreichende Technikumsschäden"),
                    "kosten": ("Sehr hoch", "> 500.000 € (Behälterzerstörung, Technikumsschäden, Personenschäden)"),
                },
                "controls": [
                    {"name": "N₂-Druckreduzierer (primäre Barriere)", "typ": "Druckreduzierung (passiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Begrenzt N₂-Druck auf eingestellten Wert. Einzige aktive Schutzbarriere.",
                     "beeinflusst": "D", "einschraenkung": "Single-Point-Failure: kein redundantes Schutzsystem; kein SV/BSV als Rückfall"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator könnte anormalen Druckaufbau am lokalen Manometer (falls vorhanden) erkennen.",
                     "beeinflusst": "D", "einschraenkung": "Kein explizites PI/PSI am Poolingbehälter dokumentiert; Erkennung nicht zuverlässig"},
                ],
                "S": 9, "O": 2, "D": 7,
                "begruendung_S": "Kritisch (S=9): Bei Vollöffnung Druckregler → Werksnetz-Druck → Behälter 6-bar-Grenze → Bersten möglich. Kein SV/BSV als Rückfall. Schwerverletzte nicht auszuschließen.",
                "begruendung_O": "Sehr gering (~1/100 Jahre): N₂-Druckregler robust; Vollversagen selten. Aber kein Redundanzsystem.",
                "begruendung_D": "Sehr unwahrscheinlich: Kein automatischer Druckalarm; kein PI/PSI am Behälter dokumentiert. Versagen erst erkennbar wenn Schaden eintritt.",
                "controls_einschraenkung": "Single-Point-Failure Druckreduzierer ohne Rückfall-Sicherheitsventil — sicherheitsrelevanter Befund (Safety Gap)."
            },

            # FM-2: N₂-Ausfall → Verlust Inertisierung
            {
                "fehler_id": "20TA24-K005-FM2",
                "funktion_id": "20TA24-KOMP-005-F3",
                "fehlermodus": "N₂-Ausfall — Verlust Inertisierung im Poolingbehälter",
                "fehlerart": "Prozess",
                "kontext_beschreibung": (
                    "Analog KOMP-001 FM-4 und KOMP-004 FM-3. N₂-Druckabfall → O₂-Eintrag → mögliche "
                    "Produktkontamination (Oxidation Polymer). Zone-2-Auslegung. Kein Runaway-Risiko. "
                    "Hauptfolge: Produktqualitätsverlust."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K005-FM2-U1", "beschreibung": "N₂-Versorgungsausfall (Werksnetz)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K005-FM2-U2", "beschreibung": "N₂-Druckregler-Defekt → Druckabfall (Unterversorgung)", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein Personenrisiko; Zone-2-Auslegung"),
                    "umwelt": ("Keine", "Kein Umweltrisiko"),
                    "anlage": ("Mäßig", "Produktkontamination (Oxidation); Chargenverlust"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Qualitätsprüfung, Chargenverlust)"),
                },
                "controls": [
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator prüft N₂-Versorgung bei Chargenstart.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer N₂-Druckalarm am Poolingbehälter"},
                ],
                "S": 5, "O": 3, "D": 6,
                "begruendung_S": "Mäßig: Hauptrisiko Produktqualität. Zone-2-Auslegung. Kein Runaway-Risiko.",
                "begruendung_O": "Gering (~1/10 Jahre): N₂-Ausfälle selten; Druckregler gelegentlich defekt.",
                "begruendung_D": "Unwahrscheinlich: Kein automatischer Alarm. Nur manuelle Prüfung.",
            },

            # FM-3: Abluftsystem-Ausfall
            {
                "fehler_id": "20TA24-K005-FM3",
                "funktion_id": "20TA24-KOMP-005-F4",
                "fehlermodus": "Abluftsystem-Ausfall — Dämpfableitung vom Poolingbehälter gestört",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Analog KOMP-001 FM-5: Werkszentraler Alarm + SOP. Geschlossenes System außer Betriebsöffnungen. "
                    "Niedrig-Risiko-Szenario durch organisatorische Absicherung."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K005-FM3-U1", "beschreibung": "Ausfall des zentralen Abluftgebläses", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K005-FM3-U2", "beschreibung": "Verstopfung Abluftleitung", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Keine", "Geschlossenes System; werkszentraler Alarm + SOP"),
                    "umwelt": ("Gering", "Erhöhte Emissionen bei Öffnung; Abluftreinigung ausgefallen"),
                    "anlage": ("Relativ gering", "Prozessstopp; keine Anlagenschäden"),
                    "kosten": ("Relativ gering", "< 1.000 €"),
                },
                "controls": [
                    {"name": "Werkszentraler Alarm (Abluftausfall)", "typ": "Automatisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Automatische Alarmmeldung bei Abluftsystem-Ausfall.",
                     "beeinflusst": "D", "einschraenkung": "Reaktionszeit Werkstechnik variabel"},
                    {"name": "SOP Abluftreinigungsanlage-Ausfall", "typ": "Organisatorisch", "wirkung": "B", "sil_level": None,
                     "beschreibung": "Definiertes Vorgehen bei Abluftausfall.",
                     "beeinflusst": "D", "einschraenkung": "Schulung und Aktualität erforderlich"},
                ],
                "S": 4, "O": 4, "D": 2,
                "begruendung_S": "Identisch KOMP-001 FM-5.",
                "begruendung_O": "Identisch.",
                "begruendung_D": "Identisch: Automatischer zentraler Alarm.",
            },

            # FM-4: Leckage Poolingbehälter
            {
                "fehler_id": "20TA24-K005-FM4",
                "funktion_id": "20TA24-KOMP-005-F5",
                "fehlermodus": "Leckage Poolingbehälter oder Schlauchanschlüsse downstream",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "200-L-Edelstahlbehälter mit Schlauchanschlüssen downstream (Transfer-System). "
                    "Leckage bei Flansch, Rührwerksdurchführung oder Schlauchanschluss. "
                    "Auffangwanne (Technikum) vorhanden; Dichtigkeitstest vor jeder Produktion."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K005-FM4-U1", "beschreibung": "Flanschdichtung defekt", "herkunft": "Wartung", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K005-FM4-U2", "beschreibung": "Schlauchleitung downstream undicht (Alterung)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K005-FM4-U3", "beschreibung": "Fehlerhafter Anschluss nach Reinigung", "herkunft": "Fertigung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol-Kontakt, Rutschgefahr; Zone-2-Auslegung; Auffangwanne"),
                    "umwelt": ("Mäßig", "AwSV-relevant; kleinerer Behälter (200 L) als KTC"),
                    "anlage": ("Hoch", "Produktverlust (wertvolles aufgereinigtes Polymer), Betriebsunterbrechung"),
                    "kosten": ("Hoch", "10.000–50.000 € (Polymer-Chargenverlust, Instandsetzung)"),
                },
                "controls": [
                    {"name": "Dichtigkeitstest vor jeder Produktion", "typ": "Organisatorisch (Prüfung)", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Gesamtanlagen-Dichtigkeitsprüfung vor jeder Charge.",
                     "beeinflusst": "O", "einschraenkung": "Während Betrieb entstehende Lecks nicht abgedeckt"},
                    {"name": "Auffangwanne (Technikum)", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "AwSV-konformes Sekundärcontainment.",
                     "beeinflusst": "D", "einschraenkung": "Containment vorhanden; Primärleckage nicht verhindert"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator erkennt sichtbare Leckagen.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm"},
                ],
                "S": 5, "O": 3, "D": 6,
                "begruendung_S": "Mäßig: 200 L < 1000 L KTC; Auffangwanne vorhanden. Polymer-Chargenverlust ist aber kostenintensiv.",
                "begruendung_O": "Gering (~1/10 Jahre): Edelstahlbehälter robust; Dichtigkeitstest vor jeder Charge reduziert Häufigkeit.",
                "begruendung_D": "Unwahrscheinlich: Kein automatischer Alarm; Personenüberwachung + Auffangwanne.",
            },
        ],
    },  # Ende KOMP-005

    # ─────────────────────────────────────────────────────────────────────────
    # KOMP-006: Transfersystem (Rohrleitungen + Schlauchanschlüsse)
    # Verbindet: Reaktor ↔ UF 1/2 ↔ Poolingbehälter ↔ KTC-Kreislauf.
    # Flexible Schlauchleitungen. Keine eigene MSR / kein eigenes SV.
    # ─────────────────────────────────────────────────────────────────────────
    "KOMP-006": {
        "functions": [
            {
                "funktion_id": "20TA24-KOMP-006-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Produkttransfer zwischen allen Anlagenteilen "
                                "(Synthesereaktor → UF 1/2 → Poolingbehälter → Kreislauf). "
                                "Rohrleitungen fest; Anbindung über flexible Schlauchleitungen.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-006-F1-A1", "parameter": "Verbindungen", "sollwert": "7 Transferstrecken (laut anlagendaten.json)"},
                ]
            },
            {
                "funktion_id": "20TA24-KOMP-006-F2",
                "typ": "Grundfunktion",
                "beschreibung": "Mechanische Integrität und Dichtigkeit aller Transferleitungen. "
                                "Dichtigkeitstest vor jeder Produktion. Zone-2-Auslegung; AwSV-Containment.",
                "anforderungen": [
                    {"id": "20TA24-KOMP-006-F2-A1", "parameter": "Dichtigkeitsprüfung", "sollwert": "vor jeder Produktion"},
                ]
            },
        ],
        "failure_modes": [

            # FM-1: Leckage Schlauchanschlüsse
            {
                "fehler_id": "20TA24-K006-FM1",
                "funktion_id": "20TA24-KOMP-006-F1",
                "fehlermodus": "Leckage an Schlauchanschlüssen — Ethanol-Austritt an Transferleitungen",
                "fehlerart": "Mechanisch",
                "kontext_beschreibung": (
                    "Mehrere flexible Schlauchanschlüsse zwischen Anlagenteilen; regelmäßiges Trennen/Wiederverbinden "
                    "bei Chargenwechsel und Reinigung erhöht Leckagerisiko gegenüber fixen Rohrleitungen. "
                    "Dichtigkeitstest vor Produktion als bestehende Kontrolle; Zone 2, Auffangwanne."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K006-FM1-U1", "beschreibung": "Schlauchwandung porös oder gerissen (Alterung, Ethanol-Angriff)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K006-FM1-U2", "beschreibung": "Schlauchkupplung unvollständig eingerastet nach Chargenwechsel", "herkunft": "Fertigung", "phase": "Wartung"},
                    {"ursache_id": "20TA24-K006-FM1-U3", "beschreibung": "Schlauchschelle oder Klemmverbindung zu lose (Vibration, Setzen)", "herkunft": "Wartung", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Mäßig", "Ethanol auf Technikumsboden; Rutschgefahr, Dämpfe (Flammpunkt 13 °C); Zone-2-Auslegung"),
                    "umwelt": ("Mäßig", "AwSV-relevant; Auffangwanne vorhanden; WGK 1"),
                    "anlage": ("Hoch", "Produktionsstopp; Schlauchtausch; Chargenverlust möglich"),
                    "kosten": ("Hoch", "10.000–50.000 € (Instandsetzung, Chargenverlust, AwSV-Kosten)"),
                },
                "controls": [
                    {"name": "Dichtigkeitstest vor jeder Produktion", "typ": "Organisatorisch (Prüfung)", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Gesamtanlagen-Dichtigkeitsprüfung vor jeder Charge.",
                     "beeinflusst": "O", "einschraenkung": "Während Betrieb entstehende Lecks (Schlauchermüdung) nicht abgedeckt"},
                    {"name": "Auffangwanne (Technikum)", "typ": "Technisch (konstruktiv)", "wirkung": "B", "sil_level": None,
                     "beschreibung": "AwSV-konformes Sekundärcontainment für gesamtes Technikum.",
                     "beeinflusst": "D", "einschraenkung": "Sekundärcontainment; Primärleckage nicht verhindert"},
                    {"name": "Personenüberwachungsbetrieb", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator erkennt sichtbare Leckagen.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm; kleine Lecks zunächst nicht sichtbar"},
                ],
                "S": 6, "O": 4, "D": 5,
                "begruendung_S": "Hoch: Ethanol-Leckage (Zone 2, AwSV); Kosten 10–50k€. Auffangwanne mitigiert Umweltschaden.",
                "begruendung_O": "Relativ gering (~1/2 Jahre): Flexible Schläuche mit regelmäßigem Trennen/Verbinden; höheres Leckagerisiko als fixe Rohrleitungen.",
                "begruendung_D": "Mäßig wahrscheinlich: Dichtigkeitstest vor Produktion + Personenüberwachung; aber keine automatische Leckageerkennung.",
            },

            # FM-2: Fehlkopplung / Falschverbindung
            {
                "fehler_id": "20TA24-K006-FM2",
                "funktion_id": "20TA24-KOMP-006-F1",
                "fehlermodus": "Fehlkopplung — falscher Schlauchanschluss nach Chargenwechsel oder Reinigung",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Bei Chargenwechsel, Reinigung oder Wartung werden Schläuche getrennt und wieder verbunden. "
                    "Fehlkopplung möglich wenn Kennzeichnung unzureichend → Produktkontamination, Fehldosierung "
                    "oder Rückstrom in falsche Anlage. Mehrere ähnlich aussehende Schlauchanschlüsse vorhanden."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K006-FM2-U1", "beschreibung": "Fehlende oder unzureichende Schlauchanschluss-Kennzeichnung", "herkunft": "Design", "phase": "Wartung"},
                    {"ursache_id": "20TA24-K006-FM2-U2", "beschreibung": "Verwechslung ähnlich aussehender Kupplungen nach Reinigung", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "20TA24-K006-FM2-U3", "beschreibung": "Zeitdruck bei Chargenübergabe → fehlerhafte Wiederverbindung", "herkunft": "Betrieb", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein direktes Personenrisiko durch Fehlkopplung"),
                    "umwelt": ("Mäßig", "Produktaustritt an Fehlstelle möglich; AwSV-relevant"),
                    "anlage": ("Hoch", "Produktkontamination; Chargenverlust; Prozessunterbrechung; Qualitätssicherungs-Aufwand"),
                    "kosten": ("Hoch", "10.000–50.000 € (Chargenverlust aufgereinigtes Polymer)"),
                },
                "controls": [
                    {"name": "Personenüberwachungsbetrieb (Sichtkontrolle)", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator prüft Anschlüsse nach Verbindung (4-Augen-Prinzip im GMP-Betrieb möglich).",
                     "beeinflusst": "D", "einschraenkung": "Kein formalisiertes Gegenkontrollsystem; keine Farbcodierung"},
                ],
                "S": 5, "O": 4, "D": 6,
                "begruendung_S": "Mäßig: Hauptfolge Produktkontamination und Chargenverlust. Kein direktes Personenrisiko.",
                "begruendung_O": "Relativ gering (~1/2 Jahre): Mehrere Schlauchwechsel pro Charge-Zyklus; Fehlkopplungen bei unzureichender Kennzeichnung möglich.",
                "begruendung_D": "Unwahrscheinlich: Keine formalisierte Gegenkontrolle; keine Farbcodierung der Kupplungen.",
            },

            # FM-3: Blockade / Verstopfung Transferleitung
            {
                "fehler_id": "20TA24-K006-FM3",
                "funktion_id": "20TA24-KOMP-006-F2",
                "fehlermodus": "Blockade / Verstopfung — Polymer-Ausfall in Transferleitung",
                "fehlerart": "Equipment",
                "kontext_beschreibung": (
                    "Polymer in ethanolischer Lösung kann bei Konzentrations- oder Temperaturabweichungen ausfallen "
                    "und Leitungen blockieren. Bei Pumpenbetrieb → Druckaufbau upstream. "
                    "Schlauchleitungen flexibel; Reinigung erforderlich."
                ),
                "causes": [
                    {"ursache_id": "20TA24-K006-FM3-U1", "beschreibung": "Polymer-Ausfall bei Temperaturabweichung oder Ethanolverdampfung", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "20TA24-K006-FM3-U2", "beschreibung": "Unvollständige Reinigung → Rückstände verstopfen Leitung", "herkunft": "Wartung", "phase": "Wartung"},
                ],
                "effects": {
                    "mensch": ("Keine", "Kein Personenrisiko; mechanische Blockade"),
                    "umwelt": ("Keine", "Kein Umweltrisiko bei geschlossenem System"),
                    "anlage": ("Mäßig", "Prozessunterbrechung; Druckaufbau upstream; Leitungsspülung erforderlich"),
                    "kosten": ("Mäßig", "1.000–10.000 € (Instandsetzung, Chargen-Zeitverlust)"),
                },
                "controls": [
                    {"name": "Personenüberwachungsbetrieb (Drucküberwachung)", "typ": "Organisatorisch", "wirkung": "D", "sil_level": None,
                     "beschreibung": "Operator erkennt Druckaufbau oder Flowabnahme an UF-Anlage oder Pumpe.",
                     "beeinflusst": "D", "einschraenkung": "Kein automatischer Alarm; indirekte Erkennung"},
                    {"name": "Reinigungsprotokoll (Spülung vor/nach Charge)", "typ": "Organisatorisch", "wirkung": "P", "sil_level": None,
                     "beschreibung": "Definiertes Spülprotokoll verhindert Rückstandsaufbau.",
                     "beeinflusst": "O", "einschraenkung": "Protokoll muss konsequent eingehalten werden"},
                ],
                "S": 5, "O": 3, "D": 5,
                "begruendung_S": "Mäßig: Prozessunterbrechung; kein Sicherheitsrisiko bei druckloser Transferleitung.",
                "begruendung_O": "Gering (~1/10 Jahre): Polymer in Ethanol bei Raumtemperatur stabil; Ausfällung bei Betriebsabweichungen.",
                "begruendung_D": "Mäßig wahrscheinlich: Indirekte Erkennung über Druckaufbau oder Flow-Abnahme.",
            },
        ],
    },  # Ende KOMP-006

}
