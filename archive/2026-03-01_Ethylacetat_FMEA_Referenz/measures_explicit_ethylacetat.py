"""
Explizite Maßnahmen pro Fehlermodus – Einzelfall-Analyse.

Jede Maßnahme ist für den konkreten Fehlermodus und die konkrete Komponente
formuliert. Keine generische Keyword-Logik.

Basis für Fehlertypen: config.fmea_standards.FEHLERMODI_VORLAGEN – Katalog der
Fehlertypen pro Kategorie. Bei der Maßnahmenentwicklung kann der Agent den
Fehlertyp (z.B. "Erosion/Abrasions", "Frozen Value") nutzen, um passende
Maßnahmen nach STOP-Prinzip und ABE-Hierarchie abzuleiten.

Erweiterung: Bei neuen Fehlermodi mit RPZ >= 100 muss der Agent eine
Einzelfall-Analyse durchführen und die Maßnahmen hier ergänzen.
"""

# Format: fehler_id -> list of measure dicts
# Jede Maßnahme: name, stop_kategorie, abe_kategorie, beschreibung, ziel, S_neu, O_neu, D_neu, begruendung

MEASURES_BY_FEHLER_ID = {}

# ─── Synthesereaktor (Rührwerksdichtung, Mannloch, Flansch, Schlag-Reaktion) ───
def _ruehrwerksdichtung():
    return [
        {"name": "Umstellung auf Doppel-Gleitringdichtung (DGS) mit Sperrmedium", "stop_kategorie": "S", "abe_kategorie": "A",
         "beschreibung": "Ersatz der Stopfbuchse/Gleitringdichtung durch Doppel-Gleitringdichtung mit Sperrmedium (Barrier-Fluid). Sperrmedium steht unter höherem Druck als Reaktor, sodass Leckage nur nach außen erfolgt – keine Medienfreisetzung in Ex-Zone.",
         "ziel": "O", "S_neu": 10, "O_neu": 2, "D_neu": 5, "begruendung": "O sinkt von 5 auf 2: DGS mit Sperrmedium eliminiert die Hauptursache (Wellenabdichtung) durch inhärent sicheres Design.", "iteration": 1},
        {"name": "Leckageüberwachung an Wellenabdichtung (Drucksensor Dichtungskammer)", "stop_kategorie": "T", "abe_kategorie": "B",
         "beschreibung": "Installation eines Drucksensors in der Dichtungskammer mit Alarm bei Druckänderung. Ex-geschützt (Zone 1), Anbindung an DCS mit Abschaltlogik bei Leckage-Erkennung.",
         "ziel": "D", "S_neu": 10, "O_neu": 5, "D_neu": 2, "begruendung": "D sinkt von 5 auf 2: Direkte Leckageüberwachung erkennt Undichtheit vor Medienfreisetzung.", "iteration": 1},
        {"name": "Dichtungswechsel-Intervall nach Hersteller + Checkliste", "stop_kategorie": "O", "abe_kategorie": "A",
         "beschreibung": "Festlegung eines präventiven Dichtungswechsels gemäß Herstellerempfehlung. Checkliste mit Drehmoment, Dichtungsprüfung und Vier-Augen-Abnahme vor Wiederinbetriebnahme.",
         "ziel": "O", "S_neu": 10, "O_neu": 4, "D_neu": 5, "begruendung": "O sinkt von 5 auf 4: Planmäßiger Wechsel vor Ermüdung reduziert Eintrittswahrscheinlichkeit.", "iteration": 1},
        {"name": "PSA-Pflicht im Reaktorbereich (Chemikalienschutz)", "stop_kategorie": "P", "abe_kategorie": "E",
         "beschreibung": "Tragepflicht von chemikalienbeständiger Schutzkleidung (EN 14605), Gesichtsschutzschild und Chemikalienschutzhandschuhen im Reaktorbereich.",
         "ziel": "S", "S_neu": 6, "O_neu": 5, "D_neu": 5, "begruendung": "S sinkt von 10 auf 6: PSA schwächt die persönlichen Folgen einer Medienfreisetzung ab.", "iteration": 1},
    ]

def _mannlochdichtung():
    return [
        {"name": "Leckage-Detektor am Mannlochflansch", "stop_kategorie": "T", "abe_kategorie": "B",
         "beschreibung": "Installation eines Leckage-Detektors unter dem Mannlochflansch. Ex-geschützt (Zone 1), Alarm bei Feuchtigkeit/Leckage mit Anzeige im DCS.",
         "ziel": "D", "S_neu": 8, "O_neu": 4, "D_neu": 3, "begruendung": "D sinkt von 6 auf 3: Direkte Leckageüberwachung am Mannloch erkennt Undichtheit früh.", "iteration": 1},
        {"name": "Dichtungswechsel bei jeder Revision + Drehmoment-Checkliste", "stop_kategorie": "O", "abe_kategorie": "A",
         "beschreibung": "Mannlochdichtung wird bei jeder planmäßigen Revision gewechselt. Checkliste mit vorgeschriebenem Anzugsmoment (DIN EN 1591), Reihenfolge und Vier-Augen-Abnahme.",
         "ziel": "O", "S_neu": 8, "O_neu": 3, "D_neu": 6, "begruendung": "O sinkt von 4 auf 3: Regelmäßiger Wechsel und kontrollierte Montage reduzieren Eintrittswahrscheinlichkeit.", "iteration": 1},
        {"name": "PSA-Pflicht bei Arbeiten am Reaktor", "stop_kategorie": "P", "abe_kategorie": "E",
         "beschreibung": "Tragepflicht von chemikalienbeständiger Schutzkleidung, Gesichtsschutz und Handschuhen bei allen Arbeiten im Reaktorbereich.",
         "ziel": "S", "S_neu": 5, "O_neu": 4, "D_neu": 6, "begruendung": "S sinkt von 8 auf 5: PSA schwächt Verätzungs- und Verbrennungsfolgen ab.", "iteration": 1},
    ]

def _flanschleckage():
    return [
        {"name": "Leckageüberwachung an kritischen Flanschverbindungen", "stop_kategorie": "T", "abe_kategorie": "B",
         "beschreibung": "Installation von Leckage-Detektoren unter den kritischen Flanschverbindungen. Ex-geschützt, Alarm bei Feuchtigkeit.",
         "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3, "begruendung": "D sinkt von 5 auf 3: Direkte Überwachung an Flanschen erhöht Entdeckungswahrscheinlichkeit.", "iteration": 1},
        {"name": "Regelmäßige Flansch-Schauprüfung und Schraubkontrolle", "stop_kategorie": "O", "abe_kategorie": "B",
         "beschreibung": "Quartalsweise Schauprüfung aller Flanschverbindungen. Jährliche Schraubkontrolle mit Drehmomentschlüssel gemäß Hersteller.",
         "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 4, "begruendung": "D sinkt von 5 auf 4: Regelmäßige Prüfung erhöht Entdeckungswahrscheinlichkeit.", "iteration": 1},
        {"name": "PSA-Pflicht im Reaktorbereich", "stop_kategorie": "P", "abe_kategorie": "E",
         "beschreibung": "Chemikalienbeständige Schutzkleidung und Gesichtsschutz im Reaktorbereich.",
         "ziel": "S", "S_neu": 5, "O_neu": 3, "D_neu": 5, "begruendung": "S sinkt von 8 auf 5: PSA begrenzt Folgen bei Medienfreisetzung.", "iteration": 1},
    ]

def _schlag_reaktion():
    return [
        {"name": "SOP Rührwerk-Wiederanlauf: Langsames Anfahren + Temperaturüberwachung", "stop_kategorie": "O", "abe_kategorie": "A",
         "beschreibung": "Betriebsanweisung: Nach Stillstand Rührwerk langsam anfahren, Temperatur überwachen. Bei Temperaturanstieg > 2 °C/min sofort Stopp.",
         "ziel": "O", "S_neu": 9, "O_neu": 2, "D_neu": 3, "begruendung": "O sinkt: Kontrollierter Wiederanlauf reduziert Eintrittswahrscheinlichkeit.", "iteration": 1},
        {"name": "Temperatur-Gradienten-Alarm bei Rührwerk-Start", "stop_kategorie": "T", "abe_kategorie": "B",
         "beschreibung": "DCS-Logik: Bei Rührwerk-Start Temperaturanstieg überwachen. Alarm und ggf. Abschaltung wenn dT/dt > Schwellwert in den ersten 5 Minuten.",
         "ziel": "D", "S_neu": 9, "O_neu": 3, "D_neu": 2, "begruendung": "D sinkt: Schlag-Reaktion wird durch schnellen Temperaturanstieg erkannt.", "iteration": 1},
    ]

# ─── Heizmantel (Dampfmantel) ───
def _heizmantel_mehr_temp():
    return [{
        "name": "Dampfventil-Stellungsüberwachung + TIC-401 Hochtemperatur-Alarm",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Stellungsrückmeldung am Dampfeinlassventil. TIC-401 mit Alarm bei Überschreitung 95 °C (vor Runaway). TI-401a/b an Mantel-Ein-/Ausgang zur Früherkennung von Regelabweichung.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 2,
        "begruendung": "D sinkt: Automatische Temperaturüberwachung erkennt Überhitzung vor Runaway.",
    }]

def _heizmantel_weniger_temp():
    return [{
        "name": "Kondensatablauf-Überwachung am Dampfmantel",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Prüfung des Kondensatablaufs (Traps) bei Revision. Verstopfung führt zu schlechter Wärmeübertragung. Sichtprüfung TI-401a/b Differenz Ein-/Ausgang.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Temperaturgradient-Monitoring erkennt Wärmeübertragungsverlust.",
    }]

def _heizmantel_erosion():
    return [{
        "name": "Revision: Prüfung Mantel-Innenseite auf Korrosion/Kondensat",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Bei planmäßiger Revision Inspektion der Dampfmantel-Innenseite. Dampf enthält kein Feststoff – Erosion unwahrscheinlich; Fokus auf Korrosion durch Kondensat.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Regelmäßige Inspektion bei Revision.",
    }]

def _heizmantel_dichtheit():
    return [{
        "name": "Leckage-Detektor zwischen Dampfmantel und Prozessraum",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Dampf/Prozess-Leckage würde zu Druckanstieg oder Kondensat im Prozess führen. Differenzdruck-Monitoring oder Leitfähigkeitsprüfung am Prozessmedium.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Früherkennung von Mantelleckage.",
    }]

# ─── KOMP-003: Kühlmantel KM-101 ───
def _kuehlmantel_mehr_temp():
    return [{
        "name": "Kühlwasserdurchfluss-Überwachung (FI) am Kühlmantel",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Durchflussmesser am Kühlwassereinlauf mit Alarm bei Unterschreitung (z.B. < 400 L/h). Verlust der Wärmeabfuhr wird früh erkannt.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 2,
        "begruendung": "D sinkt: Durchflussüberwachung erkennt Kühlungsausfall.",
    }]

def _kuehlmantel_weniger_temp():
    return [{
        "name": "Minimaltemperatur-Überwachung Kühlwasserrücklauf",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "TI am Kühlwasserauslauf mit Alarm bei < 5 °C (Vereisungsgefahr). Sole-Notkühlung -10 °C nur im Notfall.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Vereisung wird vor Schaden erkannt.",
    }]

def _kuehlmantel_dichtheit():
    return [{
        "name": "Leckage-Erkennung Kühlmantel (Produkt/Kühlwasser-Vermischung)",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Rohrleckage im Kühlmantel: Kühlwasser in Prozess oder umgekehrt. Leitfähigkeitsprüfung Kühlwasser, Drucküberwachung Mantel.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Vermischung wird erkannt.",
    }]

# ─── KOMP-004: Rührwerk RW-101 ───
def _ruehrwerk_erosion():
    return [{
        "name": "Inspektionsintervall Rührwerk (Lager, Dichtung, Rührerblatt)",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Planmäßige Inspektion bei Revision: Rührerblatt auf Abrasion, Lager auf Spiel. Feststoffgehalt im Prozess begrenzen.",
        "ziel": "O", "S_neu": 8, "O_neu": 3, "D_neu": 5,
        "begruendung": "O sinkt: Präventive Inspektion reduziert Ausfallwahrscheinlichkeit.",
    }]

def _ruehrwerk_kavitation():
    return [{
        "name": "Mindestfüllstand LIC-403 + Drehzahlbegrenzung SIC-404",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "LIC-403 mit Alarm bei Unterschreitung Mindestfüllstand (Kavitationsgefahr). SIC-404 begrenzt Drehzahl auf sicheren Bereich. Rührer darf nicht trocken laufen.",
        "ziel": "D", "S_neu": 8, "O_neu": 4, "D_neu": 2,
        "begruendung": "D sinkt: Füllstand und Drehzahlüberwachung verhindern Kavitation.",
    }]

# ─── KOMP-005: Destillationskolonne K-101 ───
def _kolonne_fouling():
    return [{
        "name": "Differenzdruck-Monitoring Kolonne (Fouling/Verstopfung Packung)",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Differenzdruck über Packung überwachen. Fouling oder Verstopfung erhöht Δp. Alarm bei Überschreitung – Reinigung/Spülung auslösen.",
        "ziel": "D", "S_neu": 6, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Trennleistungsverlust wird erkannt.",
    }]

def _kolonne_ueberdruck():
    return [{
        "name": "Drucküberwachung Kolonnenkopf + Kondensator-Anbindung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "PIC am Kolonnenkopf. Bei Kondensatorausfall steigt Druck. Alarm und Abschaltung bei Überschreitung Design-Limit.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Überdruck wird erkannt.",
    }]

def _kolonne_dichtheit():
    return [{
        "name": "Regelmäßige Dichtheitsprüfung Flansche und Stutzen",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Bei Revision Dichtheitsprüfung an Flanschverbindungen Kolonne. Ethylacetat/Essigsäure-Dämpfe – Leckage gefährlich.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Inspektion bei Revision.",
    }]

# ─── KOMP-008, KOMP-009: Destillatvorlagen DV-101, DV-102 ───
def _vorlage_ueberfuellung():
    return [{
        "name": "Füllstandüberwachung Vorlage (LAH/LSHH)",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Füllstandssensor an Vorlage mit LAH (Überfüllalarm) und LSHH (Abschaltung Zulauf). 50 L Nennvolumen – Überlauf verhindern.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Überfüllung wird erkannt.",
    }]

def _vorlage_unterfuellung():
    return [{
        "name": "Mindestfüllstand (LSLL) für Ablaufpumpe",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "LSLL stoppt Ablaufpumpe bei Unterschreitung Mindestfüllstand. Trockenlauf der Pumpe verhindern.",
        "ziel": "D", "S_neu": 6, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Unterfüllung wird erkannt.",
    }]

def _vorlage_dichtheit():
    return [{
        "name": "Dichtheitsprüfung Flansche/Stutzen bei Revision",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Bei planmäßiger Revision Dichtheitsprüfung an Vorlagen. Ethylacetat brennbar, Wasser weniger kritisch.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Inspektion bei Revision.",
    }]

# ─── KOMP-006, KOMP-007: Kondensatoren KD-101, KD-102 ───
def _kondensator_mehr_temp():
    return [{
        "name": "Differenzdruck-Monitoring Rohrbündel (Fouling-Erkennung)",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Differenzdruck Ein-/Ausgang Rohrseite und Mantelseite. Fouling oder Verstopfung erhöht Δp. Alarm bei Überschreitung – Reinigung auslösen.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Fouling wird vor Totalausfall erkannt.",
    }]

def _kondensator_weniger_temp():
    return [{
        "name": "Kühlwassertemperatur-Minimum am Kondensatorauslauf",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "TI am Kühlwasserauslauf mit Alarm bei < 5 °C (Vereisungsgefahr im Rohrbündel).",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Vereisung wird erkannt.",
    }]

def _kondensator_rohrleckage():
    return [{
        "name": "Leitfähigkeitsprüfung Kühlwasser + Differenzdruck",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Rohrleckage: Produkt (Ethylacetat, Essigsäure) in Kühlwasser. Leitfähigkeitsänderung oder Öl-in-Wasser-Sensor am Kühlwasserrücklauf. Differenzdruck-Anomalie.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 2,
        "begruendung": "D sinkt: Rohrleckage wird früh erkannt.",
    }]

# ─── KOMP-010 bis KOMP-016: MSR (TIC, TI, PIC, LIC, LSHH, SIC) ───
def _msr_frozen_value():
    return [{
        "name": "Plausibilitätsprüfung im DCS + Redundanter Sensor (falls SIL)",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "DCS prüft Messwert auf Plausibilität (Rate-of-Change, Vergleich mit Prozessmodell). Bei SIL-Sensoren: Redundanz oder Voting.",
        "ziel": "D", "S_neu": 8, "O_neu": 4, "D_neu": 3,
        "begruendung": "D sinkt: Frozen Value wird erkannt.",
    }]

def _msr_drift():
    return [{
        "name": "Kalibrierintervall + Grenzwert-Alarm",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Planmäßige Kalibrierung (z.B. jährlich). Grenzwert-Alarm bei Überschreitung – Drift wird vor kritischem Fehler erkannt.",
        "ziel": "O", "S_neu": 8, "O_neu": 3, "D_neu": 4,
        "begruendung": "O sinkt: Kalibrierung reduziert Drift.",
    }]

def _msr_ausfall():
    return [{
        "name": "Wiring-Check + Unterbrechungsüberwachung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "4-20 mA: Unterbrechung führt zu Außerbereich (z.B. < 3.6 mA). DCS erkennt Signalausfall. Regelmäßiger Wiring-Check.",
        "ziel": "D", "S_neu": 8, "O_neu": 4, "D_neu": 3,
        "begruendung": "D sinkt: Signalausfall wird erkannt.",
    }]

def _msr_fail_to_trip():
    return [{
        "name": "Periodische Funktionsprüfung Sicherheits-Schalter (LSHH)",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Jährliche Funktionsprüfung LSHH-403: Füllstand simuliert, Abschaltung verifiziert. SIL-2 Nachweis.",
        "ziel": "O", "S_neu": 9, "O_neu": 2, "D_neu": 5,
        "begruendung": "O sinkt: Fail-to-trip wird durch Prüfung verhindert.",
    }]

def _msr_fruehzeitiges_ansprechen():
    return [{
        "name": "Kalibrierung und Sichtprüfung LSHH-Schaltpunkt",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Bei Revision Schaltpunkt prüfen. Verschmutzung am Vibrationsschalter vermeiden.",
        "ziel": "D", "S_neu": 5, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Frühzeitiges Ansprechen wird erkannt.",
    }]

# ─── KOMP-017, 018, 019, 047: Sicherheitsventile PSV, BSV, VSV ───
def _psv_nicht_oeffnen():
    return [{
        "name": "Jährliche Prüfung gemäß Druckgeräterichtlinie",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Prüfintervall 1 Jahr (PSV-410). Abnahme durch zugelassenen Prüfer, Dokumentation. Verhindert Verklebung/Korrosion.",
        "ziel": "O", "S_neu": 10, "O_neu": 2, "D_neu": 5,
        "begruendung": "O sinkt: Planmäßige Prüfung reduziert Fail-to-open.",
    }]

def _psv_erosion_kavitation():
    return [{
        "name": "Prüfung auf Korrosion/Verschleiß bei jährlicher Abnahme",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Erosion/Kavitation bei Sicherheitsventilen selten (kein Durchfluss im Normalbetrieb). Bei Abnahme Sitz und Dichtflächen prüfen.",
        "ziel": "D", "S_neu": 10, "O_neu": 4, "D_neu": 4,
        "begruendung": "D sinkt: Jährliche Sichtprüfung.",
    }]

# ─── KOMP-020: NOT-AUS-R101 ───
def _notaus_bedienfehler():
    return [{
        "name": "Schulung NOT-AUS-Betätigung + Klare Kennzeichnung",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Jährliche Unterweisung: Wann NOT-AUS betätigen, Rückstellung nur durch autorisiertes Personal. Rote Kennzeichnung, gut erreichbar.",
        "ziel": "O", "S_neu": 10, "O_neu": 3, "D_neu": 5,
        "begruendung": "O sinkt: Fehlbedienung wird reduziert.",
    }]

def _notaus_kennzeichnung():
    return [{
        "name": "Prüfung Kennzeichnung bei Sicherheitsbegehung",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Quartalsweise Begehung: NOT-AUS-Schalter korrekt beschriftet, keine Verwechslung mit anderen Schaltern.",
        "ziel": "D", "S_neu": 10, "O_neu": 4, "D_neu": 4,
        "begruendung": "D sinkt: Kennzeichnungsfehler werden erkannt.",
    }]

def _notaus_fail_to_trip():
    return [{
        "name": "Funktionsprüfung NOT-AUS-Kette (periodisch)",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Periodische Funktionsprüfung der NOT-AUS-Kette (z.B. jährlich): Betätigung simuliert, Abschaltung verifiziert. Dokumentation.",
        "ziel": "O", "S_neu": 10, "O_neu": 2, "D_neu": 5,
        "begruendung": "O sinkt: Fail-to-trip wird durch Prüfung verhindert.",
    }]

# ─── KOMP-021, 024, 025, 026: Dosierung ───
def _dosierung_ueberdosierung():
    return [{
        "name": "Flow-Totalizer mit Grenzwert-Alarm (FIC-404/405)",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Cumulative Flow-Überwachung: Alarm wenn Sollmenge pro Charge überschritten. FIC-404/405 bereits vorhanden – Totalizer-Funktion im DCS nutzen.",
        "ziel": "D", "S_neu": 8, "O_neu": 6, "D_neu": 2,
        "begruendung": "D sinkt: Überdosierung wird vor Exothermie erkannt.",
    }]

def _dosierung_unterdosierung():
    return [{
        "name": "LSLL Trockenlaufschutz + Sollmengenüberwachung pro Charge",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "LSLL-201/202 stoppt Pumpe bei Mindestfüllstand. Zusätzlich: Sollmenge pro Charge – Alarm bei Unterschreitung (Akkumulationsgefahr).",
        "ziel": "D", "S_neu": 8, "O_neu": 6, "D_neu": 2,
        "begruendung": "D sinkt: Unterdosierung und Trockenlauf werden erkannt.",
    }]

def _dosierung_membranbruch():
    return [{
        "name": "Inspektionsintervall Membran + Leckageerkennung",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Planmäßiger Membranwechsel (Herstellerangabe). Leckage an Pumpenkopf würde zu Tropfen führen – Sichtprüfung, ggf. Leckagesensor.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Leckage wird erkannt.",
    }]

def _katalysator_ueberdosierung():
    return [{
        "name": "Flow-Totalizer Katalysator + Grenzwert-Alarm",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Schwefelsäure 98 % – Überdosierung führt zu starker Exothermie. Cumulative Flow überwachen, Alarm bei Überschreitung Sollmenge.",
        "ziel": "D", "S_neu": 9, "O_neu": 4, "D_neu": 2,
        "begruendung": "D sinkt: Überdosierung wird erkannt.",
    }]

def _katalysator_unterdosierung():
    return [{
        "name": "Sollmengenüberwachung pro Charge",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Alarm bei Unterschreitung Sollmenge Schwefelsäure – unvollständige Reaktion, Akkumulation.",
        "ziel": "D", "S_neu": 8, "O_neu": 4, "D_neu": 3,
        "begruendung": "D sinkt: Unterdosierung wird erkannt.",
    }]

def _katalysator_leckage():
    return [{
        "name": "Leckageerkennung + Korrosionsschutz",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Schwefelsäure 98 % – Leckage hochgefährlich. Auffangwanne, Leckagesensor. Regelmäßige Inspektion Leitungen.",
        "ziel": "D", "S_neu": 9, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Leckage wird erkannt.",
    }]

# ─── KOMP-033: Auffangwanne AW-200 ───
def _auffangwanne_bedienfehler():
    return [{
        "name": "Leckagesensor prüfen + Anweisung bei Alarm",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Auffangwanne hat Leckagesensor. SOP: Bei Alarm sofort Prüfung, keine Fehlinterpretation. Regelmäßige Funktionsprüfung Sensor.",
        "ziel": "D", "S_neu": 9, "O_neu": 4, "D_neu": 3,
        "begruendung": "D sinkt: Klare Anweisung verhindert Fehlreaktion.",
    }]

def _auffangwanne_kennzeichnung():
    return [{
        "name": "Kennzeichnung Auffangwanne + Zuordnung zu Dosierbereich",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Klare Beschriftung: Auffangwanne Dosiersystem DS-200. Keine Verwechslung mit anderen Wannen. Bei Begehung prüfen.",
        "ziel": "D", "S_neu": 9, "O_neu": 4, "D_neu": 4,
        "begruendung": "D sinkt: Kennzeichnung reduziert Verwechslung.",
    }]

def _auffangwanne_safety_valve():
    return [{
        "name": "Regelmäßige Prüfung Wannendichtheit und Leckagesensor",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Quartalsweise Prüfung: Wannendichtheit (keine Risse), Leckagesensor funktionsfähig. Fehlermodus 'Nicht-Öffnen' aus Template passt nicht zur Auffangwanne – Fokus auf Integrität.",
        "ziel": "D", "S_neu": 9, "O_neu": 4, "D_neu": 4,
        "begruendung": "D sinkt: Regelmäßige Prüfung erkennt Schäden.",
    }]

# ─── KOMP-035: Dampfversorgung DV-301 ───
def _dampfversorgung_druck():
    return [{
        "name": "PI-301 Drucküberwachung + Alarm bei Unterschreitung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "PI-301 am Dampfeingang. Alarm wenn Druck unter Soll (6 bar). Regelmäßige Kalibrierung PI-301.",
        "ziel": "D", "S_neu": 6, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Druckverlust wird erkannt.",
    }]

def _dampfversorgung_leckage():
    return [{
        "name": "Regelmäßige Inspektion Dampfleitungen und Flansche",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Begehung: Dampfaustritt erkennen (Kondensat, Geräusch). Flanschdichtungen bei Revision prüfen.",
        "ziel": "D", "S_neu": 7, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Leckage wird erkannt.",
    }]

# ─── KOMP-036: Dampfverteiler DV-302 ───
def _dampfverteiler_thermisch():
    return [{
        "name": "Dampfdruck- und Temperaturüberwachung am Verteiler",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Druck- und Temperatursensor am Dampfverteiler. Alarm bei Abweichung vom Soll (6 bar Sattdampf). Kondensatablauf prüfen.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Abweichung wird erkannt.",
    }]

# ─── KOMP-037: Kühlwasserversorgung KW-301 ───
def _kuehlwasser_durchfluss():
    return [{
        "name": "PI-302/TI-302/303 Durchfluss- und Temperaturüberwachung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Alarm bei Druckabfall oder Temperaturanstieg Kühlwasser. Schnellabschaltung Reaktor bei KW-Ausfall.",
        "ziel": "D", "S_neu": 9, "O_neu": 3, "D_neu": 2,
        "begruendung": "D sinkt: Ausfall wird sofort erkannt.",
    }]

def _kuehlwasser_temp():
    return [{
        "name": "TI-302/303 Rücklauftemperaturüberwachung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Alarm bei Überschreitung Soll-Rücklauftemperatur. Kältezentrale prüfen.",
        "ziel": "D", "S_neu": 6, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Temperaturproblem wird erkannt.",
    }]

# ─── KOMP-038: Notkühlsystem NK-301 ───
def _notkuehl_thermisch():
    return [{
        "name": "Sole-Durchfluss und Temperaturüberwachung Notkühlung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Durchfluss und Temperatur (-10 °C Sole) überwachen. Alarm bei Ausfall. Notkühlung nur bei Bedarf – Funktionsprüfung periodisch.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Ausfall wird erkannt.",
    }]

def _notkuehl_soleausfall():
    return [{
        "name": "Funktionsprüfung Notkühlung periodisch",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Periodische Prüfung: Sole-Durchfluss und Temperatur. Notkühlung nur bei Bedarf – trotzdem Funktionsnachweis.",
        "ziel": "O", "S_neu": 9, "O_neu": 3, "D_neu": 4,
        "begruendung": "O sinkt: Ausfall wird durch Prüfung erkannt.",
    }]

# ─── KOMP-039: Vakuumpumpe VP-301 ───
def _vakuumpumpe_ausfall():
    return [{
        "name": "PI-304 Vakuumüberwachung + Ölwechsel 3000 h",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "PI-304 Alarm bei Vakuumverlust. Hersteller: Ölwechsel alle 3000 Betriebsstunden. Sperrflüssigkeitsstand prüfen.",
        "ziel": "D", "S_neu": 6, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Ausfall wird erkannt.",
    }]

def _vakuumpumpe_sperrfluessigkeit():
    return [{
        "name": "Füllstandüberwachung Sperrflüssigkeit + Wartungsplan",
        "stop_kategorie": "O", "abe_kategorie": "B",
        "beschreibung": "Sichtprüfung oder Füllstandssensor. Wartungsplan: Nachspeisung, Ölwechsel 3000 h.",
        "ziel": "D", "S_neu": 5, "O_neu": 3, "D_neu": 4,
        "begruendung": "D sinkt: Verbrauch wird erkannt.",
    }]

# ─── KOMP-040: Stickstoffversorgung N2-301 ───
def _stickstoff_druck():
    return [{
        "name": "Drucküberwachung N2-Tank + Alarm bei Unterschreitung",
        "stop_kategorie": "T", "abe_kategorie": "B",
        "beschreibung": "Tankfüllstand/Druck überwachen. Alarm bei Unterschreitung Mindestdruck. Wechselplan für leere Tanks.",
        "ziel": "D", "S_neu": 8, "O_neu": 3, "D_neu": 3,
        "begruendung": "D sinkt: Druckverlust wird erkannt.",
    }]

def _stickstoff_verunreinigung():
    return [{
        "name": "Zertifikat prüfen + ggf. O2-Analyse bei Anlieferung",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Stickstoff 99.9 % – Zertifikat bei Anlieferung prüfen. Bei Verdacht O2-Messung.",
        "ziel": "D", "S_neu": 8, "O_neu": 4, "D_neu": 4,
        "begruendung": "D sinkt: Verunreinigung wird erkannt.",
    }]

# ─── KOMP-021: Dosiersystem DS-200 (Verkettung) ───
def _dosiersystem_verkettung():
    return [{
        "name": "Störfallanalyse Dosier-Verkettung + Sollmengenüberwachung",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Störfallanalyse: Was wenn LSLL + Pumpe + FIC gleichzeitig ausfallen? Flow-Totalizer mit Grenzwert-Alarm pro Charge. Sollmengenüberwachung verhindert Über-/Unterdosierung trotz Einzelausfall.",
        "ziel": "O", "S_neu": 9, "O_neu": 3, "D_neu": 3,
        "begruendung": "O sinkt: Verkettung wird durch Analyse und Überwachung adressiert.",
    }]

# ─── KOMP-034: Mediensystem (Verkettung) ───
def _mediensystem_verkettung():
    return [{
        "name": "Redundanz prüfen + Störfallanalyse Verkettung",
        "stop_kategorie": "O", "abe_kategorie": "A",
        "beschreibung": "Störfallanalyse: Was wenn Dampf+KW gleichzeitig ausfallen? USV für MSR? Notkühlung automatisch zuschalten.",
        "ziel": "O", "S_neu": 9, "O_neu": 3, "D_neu": 4,
        "begruendung": "O sinkt: Verkettung wird durch Analyse adressiert.",
    }]


def get_measures_for_fehlermodus(fehler_id: str, fehlermodus: str, komponente: str) -> list:
    """
    Liefert explizite Maßnahmen für den Fehlermodus.
    Rückgabe: Liste von Maßnahme-Dicts oder [] wenn keine definiert.
    Projektspezifisch: Wird aus tasks/{task_folder}/measures_explicit.py oder config/measures_explicit.py geladen.
    """
    fehlermodus_lower = fehlermodus.lower()
    komp_lower = komponente.lower()

    # Synthesereaktor: Rührwerksdichtung, Mannloch, Flansch, Schlag-Reaktion
    if "rührwerksdichtung" in fehlermodus_lower or "wellenabdichtung" in fehlermodus_lower or "stopfbuchse" in fehlermodus_lower:
        return _ruehrwerksdichtung()
    if "mannloch" in fehlermodus_lower or "mannlochdichtung" in fehlermodus_lower:
        return _mannlochdichtung()
    if "flansch" in fehlermodus_lower and ("leckage" in fehlermodus_lower or "undicht" in fehlermodus_lower):
        return _flanschleckage()
    if "schlag" in fehlermodus_lower and "reaktion" in fehlermodus_lower:
        return _schlag_reaktion()

    # Heizmantel
    if fehler_id.startswith("KOMP-002"):
        if "mehr temperatur" in fehlermodus_lower or "high temperature" in fehlermodus_lower:
            return _heizmantel_mehr_temp()
        if "weniger temperatur" in fehlermodus_lower or "low temperature" in fehlermodus_lower:
            return _heizmantel_weniger_temp()
        if "erosion" in fehlermodus_lower or "abrasion" in fehlermodus_lower:
            return _heizmantel_erosion()
        return _heizmantel_dichtheit()

    # KOMP-003 Kühlmantel
    if fehler_id.startswith("KOMP-003"):
        if "mehr temperatur" in fehlermodus_lower:
            return _kuehlmantel_mehr_temp()
        if "weniger temperatur" in fehlermodus_lower:
            return _kuehlmantel_weniger_temp()
        if "erosion" in fehlermodus_lower:
            return _kuehlmantel_dichtheit()
        return _kuehlmantel_dichtheit()

    # KOMP-004 Rührwerk
    if fehler_id.startswith("KOMP-004"):
        if "erosion" in fehlermodus_lower or "abrasion" in fehlermodus_lower:
            return _ruehrwerk_erosion()
        if "kavitation" in fehlermodus_lower:
            return _ruehrwerk_kavitation()
        return _ruehrwerk_erosion()

    # KOMP-006, KOMP-007 Kondensatoren
    if fehler_id.startswith("KOMP-006") or fehler_id.startswith("KOMP-007"):
        if "mehr temperatur" in fehlermodus_lower:
            return _kondensator_mehr_temp()
        if "weniger temperatur" in fehlermodus_lower:
            return _kondensator_weniger_temp()
        if "erosion" in fehlermodus_lower or "abrasion" in fehlermodus_lower:
            return _kondensator_rohrleckage()
        return _kondensator_mehr_temp()

    # KOMP-017 PSV-410, KOMP-047 PSV-310
    if fehler_id.startswith("KOMP-017") or fehler_id.startswith("KOMP-047"):
        if "nicht-öffnen" in fehlermodus_lower or "safety valve" in fehlermodus_lower:
            return _psv_nicht_oeffnen()
        return _psv_erosion_kavitation()

    # KOMP-018 BSV-411, KOMP-019 VSV-412
    if fehler_id.startswith("KOMP-018") or fehler_id.startswith("KOMP-019"):
        if "nicht-öffnen" in fehlermodus_lower or "safety valve" in fehlermodus_lower:
            return _psv_nicht_oeffnen()
        return _psv_erosion_kavitation()

    # KOMP-020 NOT-AUS
    if fehler_id.startswith("KOMP-020"):
        if "bedienfehler" in fehlermodus_lower or "human error" in fehlermodus_lower:
            return _notaus_bedienfehler()
        if "kennzeichnung" in fehlermodus_lower:
            return _notaus_kennzeichnung()
        if "nicht-öffnen" in fehlermodus_lower or "safety" in fehlermodus_lower:
            return _notaus_fail_to_trip()
        return _notaus_bedienfehler()

    # KOMP-021, 024, 025, 026 Dosierung
    if fehler_id.startswith("KOMP-021") or fehler_id.startswith("KOMP-024") or fehler_id.startswith("KOMP-025") or fehler_id.startswith("KOMP-026"):
        if "überdosierung" in fehlermodus_lower or "overdosierung" in fehlermodus_lower:
            return _dosierung_ueberdosierung()
        if "unterdosierung" in fehlermodus_lower:
            return _dosierung_unterdosierung()
        return _dosierung_ueberdosierung()

    # KOMP-033 Auffangwanne
    if fehler_id.startswith("KOMP-033"):
        if "bedienfehler" in fehlermodus_lower:
            return _auffangwanne_bedienfehler()
        if "kennzeichnung" in fehlermodus_lower:
            return _auffangwanne_kennzeichnung()
        if "nicht-öffnen" in fehlermodus_lower or "safety" in fehlermodus_lower:
            return _auffangwanne_safety_valve()
        return _auffangwanne_bedienfehler()

    # KOMP-036 Dampfverteiler
    if fehler_id.startswith("KOMP-036"):
        return _dampfverteiler_thermisch()

    # KOMP-038 Notkühlsystem
    if fehler_id.startswith("KOMP-038"):
        return _notkuehl_thermisch()

    return []
