# FMEA Standards — Fehlermodi-Vorlagen & Pflichtprüfungen

Kanonische Quelle für RPZ-Regeln, S/O/D-Skalen und Safety Overrides: `config/fmea_standards.py` + SKILL.md (inline).
Diese Datei enthält: FM-Vorlagen (9 Kategorien), ATEX-Validierung, Backflow-Prüfung, CCF-Prüfung.

---

## Fehlermodi-Vorlagen (Checkliste pro Komponente)

Für jede Komponente prüfen, welche Typen relevant sind. Keine generische Übernahme — S/O/D immer individuell bewerten.

**Dokumentationspflicht:** Alle 9 Kategorien müssen pro Komponente durchgegangen werden. Nicht-relevante Kategorien oder einzelne Typen darin sind explizit mit Begründung zu dokumentieren:
> "nicht relevant — [Begründung, z.B.: kein rotierendes Equipment / keine thermische Prozessführung / kein Druckbehälter]"

Kein Typ darf stillschweigend übergangen werden. Die Dokumentation nicht-relevanter Fehlermodi ist der Nachweis, dass man sich darüber Gedanken gemacht hat.

### Pflicht-Checkliste: Utility-Schnittstellen (Lesson Learned)

**Bei jeder Komponente explizit prüfen, welche externen Versorgungsmedien / Utilities angebunden sind:**

| Utility | Zu prüfende Fehlermodi |
|---|---|
| Thermostat / Heiz-Kühlsystem | Überhitzung (unkontrolliertes Heizen), Untertemperatur (Thermoschock), Totalausfall (kein Temperatursollwert) |
| Eiswasser / Kühlwasser | Ausfall → Kondensatverlust, Dampfaustritt, Druckaufbau |
| Stickstoff (N₂) | Ausfall → Verlust Inertisierung; Überdruck → Druckstoß; Unterschreitung Grenzdruck |
| Abluft | Ausfall / Verstopfung → Druckaufbau oder unkontrollierte Emission |
| Elektrische Versorgung | Ausfall → Stillstand aktiver Komponenten (Pumpen, Rührwerke, Regler) |

**Regel:** Jede Utility, die im `connectedSystems`-Feld oder in `utilities` der `anlagendaten.json` gelistet ist, muss als eigener Fehlermodus oder explizit als "nicht relevant — Begründung" dokumentiert werden.

### Prozess

| Typ | Beschreibung |
|---|---|
| Mehr Stoffstrom (High Flow) | Überschreitung der Auslegungskapazität, verringerte Verweilzeit oder Überfüllung nachgeschalteter Apparate. |
| Weniger Stoffstrom (Low Flow) | Unterschreitung der Mindestströmung, Gefahr von Ablagerungen oder unzureichender Durchmischung. |
| Kein Stoffstrom (No Flow) | Vollständiger Abriss der Versorgung, Trockenlauf von Pumpen oder Entstehen von gefährlichen Totvolumina. |
| Rückstrom (Reverse Flow) | Umkehrung der Fließrichtung durch Druckunterschiede, führt zu Kontamination oder Reaktionen in Zuleitungen. **→ Backflow-Pflichtprüfung** |
| Mehr Druck (High Pressure) | Überschreitung des zulässigen Betriebsdrucks (PS), Gefahr des Berstens oder Ansprechen von Sicherheitseinrichtungen. |
| Weniger Druck (Low Pressure/Vacuum) | Unterschreitung des Mindestdrucks, Gefahr der Kavitation oder Implosion bei nicht vakuumfesten Apparaten. |
| Konzentrationsabweichung | Falsches stöchiometrisches Verhältnis, führt zu Nebenreaktionen, Ausbeuteverlust oder thermischer Instabilität. |
| Phasentrennung / Entmischung | Ungewollte Bildung von Schichten, führt zu Fehlmessungen oder lokalen Reaktions-Hotspots. |
| Verschleppung / Kontamination | Eintrag von Fremdstoffen oder Rückständen aus Vorchargen, die als Katalysator oder Inhibitor wirken. |

**Gefahrenfelder-Prüfpunkte:** 1.1 Spezifikation/Verunreinigungen, 1.2 Präsenz Ausgangsstoffe, 1.4 Reaktionsbedingungen, 1.5 Druck, 1.7 Vermischung/Verwechslung, 1.9 Stoffströme/Rückströmung, 1.10 Füllstand/Überfüllung, 1.16 Pumpen/Transfer, 1.20 Evakuieren/Entlasten, 1.22 Prozessunterbruch

### Thermisch

| Typ | Beschreibung |
|---|---|
| Mehr Temperatur (High Temperature) | Beschleunigung exothermer Reaktionen (Runaway-Gefahr), thermische Zersetzung oder Materialerweichung. |
| Weniger Temperatur (Low Temperature) | Einfrieren, Auskristallisation, Viskositätsanstieg oder Sprödbruch. |
| Thermischer Schock | Extreme Temperaturgradienten → Spannungsrisse in Emaille oder Schweißnähten. |
| Verlust der Wärmeabfuhr | Ausfall Kühlmedium oder Fouling → unkontrollierter Temperaturanstieg. |
| Lokale Überhitzung (Hot Spot) | Ungleichmäßige Wärmeverteilung durch defekte Rührwerke oder Beläge. |

**Gefahrenfelder-Prüfpunkte:** 1.6 Temperatur, 1.13 Reaktion mit Wärmeträger, 1.17 Heizen/Kühlen, 2.2 Heiz-/Kühlmedien

### Mechanisch

| Typ | Beschreibung |
|---|---|
| Erosion / Abrasion | Materialabtrag durch feststoffhaltige Medien → Wandstärkenunterschreitung. |
| Kavitation | Dampfblasenbildung und Kondensation → Materialzerstörung an Laufrädern. |
| Vibration / Resonanz | Schwingungen → Ermüdungsbrüche an Stutzen und Verschraubungen. |
| Äußere Leckage | Versagen von Flanschdichtungen oder Stopfbuchsen, Medienaustritt. |
| Innere Leckage (Bypass) | Durchbruch an Wärmetauscherrohren, prozessinterne Vermischung. |
| Materialermüdung | Rissbildung durch zyklische Druck-/Temperaturbelastungen. |

**Gefahrenfelder-Prüfpunkte:** 1.11 Rührung, 1.16 Pumpen/Transfer, 1.23 Chemikalienaustritt, 2.4 Integrität

### Equipment

| Typ | Beschreibung |
|---|---|
| Fouling / Belagbildung | Feststoffschichten reduzieren Wärmeübergang oder verengen Querschnitte. |
| Verstopfung / Blockade | Verschluss von Filtern, Sieben oder Rohrleitungen. |
| Gleitringdichtungsversagen | Ausfall der Wellenabdichtung. |
| Innere Beschädigung (Einbauten) | Bruch von Stromstörern, Füllkörpern oder Filterkerzen. |
| Vakuumverlust | Falschluft → beeinträchtigt Siedepunkte oder führt zu explosiven Gemischen. |

**Gefahrenfelder-Prüfpunkte:** 1.15 Filtrieren/Abtrennen, 1.18 Reinigung, 2.4 Integrität

### Elektrisch

| Typ | Beschreibung |
|---|---|
| Vollständiger Spannungsausfall (Blackout) | Absturz aller aktiven Komponenten, undefinierter Zustand. |
| Spannungseinbruch (Brownout) | Unkontrollierte Resets oder Abfallen von Schützen. |
| Phasenausfall / Asymmetrie | Überhitzung und Wicklungsschäden bei Drehstrommotoren. |
| EMV-Einkopplung | Störsignale → sporadische Fehlmessungen. |
| Erdschluss / Isolationsfehler | Fehlerstrom → Personengefahr oder Schutzauslösung. |

**Gefahrenfelder-Prüfpunkte:** 1.12 Elektrostatische Aufladung, 2.1 Hilfsenergien

### MSR

| Typ | Beschreibung |
|---|---|
| Eingefrorener Messwert (Frozen Value) | Sensor liefert konstanten Wert, Regelung reagiert nicht. |
| Messwertdrift | Schleichende Kalibrierungsabweichung. |
| Signalrauschen / Spikes | Instabile Signale, hohe Aktorbelastung. |
| Aktor-Blockade (Stuck-at) | Stellventil klemmt, Reglerausgang ohne Wirkung. |
| Logikfehler / Software-Bug | Fehlerhafte Verriegelungen oder Schrittketten. |
| Kommunikationsabriss (Busfehler) | Verlust E/A-Verbindung, Aktoren gehen in Fail-Safe. |
| Antivalenzfehler | Widersprüchliche Endlagenschalter-Rückmeldungen. |

**Gefahrenfelder-Prüfpunkte:** 1.19 Kontrolle/Überwachung, 2.3 PLT-Einrichtungen, 2.6 Cyber Security

### Sicherheit

| Typ | Beschreibung |
|---|---|
| Nicht-Öffnen (Safety Valve) | PSV klemmt, unzulässiger Druckaufbau. |
| Frühzeitiges Ansprechen | PSV/BSV löst unterhalb Ansprechdruck aus. |
| Ausfall der Inertisierung | Verlust N₂-Polster → explosionsfähige Atmosphäre. |
| Flammendurchschlag | Defekt an Deflagrationssicherungen. |
| Fehlauslösung Not-Halt | Plötzlicher Stillstand → instabile Zustände. |

**Gefahrenfelder-Prüfpunkte:** 1.8 Explosionsfähige Atmosphäre (→ ATEX-Pflicht), 1.12 Elektrostatische Aufladung, 1.21 Abluft/Ableitung, 1.24 Manuelle Tätigkeiten, 1.26 Offenes Stoffhandling, 2.5 CE-Konformität

### Dosierung

| Typ | Beschreibung |
|---|---|
| Überdosierung (Single Point Failure) | Unkontrollierte Exothermie oder Produktverlust. |
| Unterdosierung | Reaktionsstart verhindert (Akkumulationsgefahr). |
| Falsche Dosierreihenfolge | Gefährliche Zwischenprodukte oder Feststoffausfall. |
| Gasblasen im Dosierstrom | Massive Volumenstromfehler bei Verdrängerpumpen. |

**Gefahrenfelder-Prüfpunkte:** 1.3 Dosierung/Menge/Reihenfolge, 1.14 Katalysator/Inhibitor

### Sonstiges

| Typ | Beschreibung |
|---|---|
| Bedienfehler (Human Error) | Falsche Sollwertvorgabe oder Fehlinterpretation von Alarmen. |
| Kennzeichnungsfehler | Falsche Beschriftung von Leitungen oder Handventilen. |
| Externe Einwirkung | Beschädigung durch Staplerverkehr oder herabfallende Lasten. |

**Gefahrenfelder-Prüfpunkte:** 1.24 Manuelle Tätigkeiten, 1.25 Wartung/Reparatur, 1.26 Offenes Stoffhandling

---

## ATEX-Validierung (Pflichtprüfung bei Ex-Zone)

Bei jeder Komponente mit Ex-Zone-Einstufung MUSS geprüft werden:

### Gas-Ex (Gruppe II G)

| Bedingung | Pflichtmaßnahme |
|---|---|
| Zone 0 + brennbare Gase/Dämpfe | Geräte-Kategorie 1G erforderlich. Falls 2G/3G: Inertisierung PFLICHT |
| Zone 1 + brennbare Gase/Dämpfe | Geräte-Kategorie 2G erforderlich. Falls 3G: Inertisierung oder Upgrade |
| Zone 0/1 + keine Inertisierung | ATEX-Lücke! Explizit ansprechen |

### Staub-Ex (Gruppe II D)

| Bedingung | Pflichtmaßnahme |
|---|---|
| Zone 20 + brennbarer Staub | Geräte-Kategorie 1D erforderlich. Falls 2D/3D: Inertisierung PFLICHT |
| Zone 21 + brennbarer Staub | Geräte-Kategorie 2D erforderlich |
| Staubablagerungen auf heißen Oberflächen | Max. Oberflächentemperatur < 2/3 Glimmtemperatur |

### Hybride Gemische (Gas + Staub gleichzeitig)

| Bedingung | Pflichtmaßnahme |
|---|---|
| Gas + Staub gleichzeitig möglich | Strengere Zone gilt. UEG sinkt bei Hybridgemischen → konservativ bewerten |
| Zone G + Zone D überlappen | Geräte müssen beide Anforderungen erfüllen |

### Entscheidungsbaum

1. Brennbare Stoffe im System? Gase/Dämpfe (Flammpunkt < Betriebstemp?) → Gas-Ex. Stäube (Kst > 0?) → Staub-Ex. Beides? → Hybrid.
2. Welche Ex-Zone (innen / Raum)?
3. Welche ATEX-Gerätekategorie? (G, D, oder beides?)
4. Inertisierung vorhanden? Wenn nein: als PFLICHTMASSNAHME vorschlagen.

**WICHTIG:** Der Agent MUSS diese Prüfung proaktiv durchführen. Immer ALLE drei Fälle (Gas, Staub, Hybrid) prüfen.

---

## Pflicht-Checkliste: Rückströmung (pro Schnittstelle)

Für JEDE Verbindung in `connectedSystems.upstream` und `connectedSystems.downstream`:

1. Gibt es ein Druckgefälle, das sich umkehren kann?
2. Gibt es Rückschlagklappen oder andere Rückflusssperren?
3. Was passiert bei Rückströmung? (Kontamination, gefährliche Reaktion, Druckaufbau?)

Bei Vakuumbetrieb: Auch Falschluft-Eintrag als Rückströmungs-Variante betrachten.

---

## Common Cause Failure (CCF) Prüfung

Nach Abschluss aller Einzel-Fehlermodi MUSS eine CCF-Prüfung durchgeführt werden:

1. Welche Fehlermodi haben **gemeinsame Ursachen**? (z.B. Stromausfall betrifft Rührwerk + Thermostat + Anzeigen)
2. Welche **Schutzschichten sind voneinander abhängig**? (z.B. DHV und PSV am selben Stutzen)
3. Gibt es **Kaskaden-Szenarien**? (z.B. Kühlungsausfall → Übertemperatur → Druckaufbau → Glasbruch)

Für jede identifizierte CCF: Eigenen Fehlermodus anlegen oder bestehenden FM um CCF-Ursache erweitern. S/O/D separat bewerten.
