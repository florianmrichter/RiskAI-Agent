# FMEA Standards — Referenz

Kanonische Quelle: `config/fmea_standards.py`. Diese Datei ist eine lesbare Kopie für die Skill.

---

## RPZ-Klassifizierung

RPZ = S × O × D

| Stufe | RPZ-Bereich | Maßnahme | Farbe |
|---|---|---|---|
| kritisch | ≥ 300 | Sofortige Maßnahme | #F5004F |
| hoch | 200 ≤ RPZ < 300 | Maßnahme zeitnah umsetzen | #FD7E14 |
| mittel | 100 ≤ RPZ < 200 | Maßnahme planen | #E8C547 |
| niedrig | RPZ < 100 | Monitoring | #00A389 |

**Klassifizierungsregel:** Die Stufe ist diejenige, deren Bereich den berechneten RPZ-Wert enthält.

**Beispiele:**

- RPZ = 168 → **mittel** (100 ≤ 168 < 200)
- RPZ = 200 → **hoch** (200 ≤ 200 < 300)
- RPZ = 84 → **niedrig** (84 < 100)
- RPZ = 315 → **kritisch** (315 ≥ 300)

**Zielwert:** RPZ < 100 gilt als akzeptables Restrisiko.

---

## Sonderregeln (AIAG-VDA Overrides)

Diese Regeln überschreiben die RPZ-Einstufung unabhängig vom berechneten Wert:

| Regel | Bedingung | Ergebnis |
|---|---|---|
| Sicherheitsrelevanz | S ≥ 9 und Stufe nicht kritisch/hoch | → mindestens **hoch** |
| Schlechte Entdeckbarkeit | D ≥ 9 und S ≥ 7 | → **kritisch** |

## Safety Overrides (kontext-basierte S-Erhöhung)

| Kontext | Schlüsselwörter | Min. S |
|---|---|---|
| Explosionsschutz | ex-schutz, explosionsschutz, zone 0, zone 1, atex | 10 |
| Gefahrstoff-Handling | säure, lauge, toxisch, giftig, chlor, schwefelsäure, essigsäure | 9 |
| Sicherheitsgerichtetes Bauteil | berstscheibe, psv, sicherheitsventil, not-aus, not-halt | 10 |

---

## S — Severity / Bedeutung (1–10)

| S | Stufe | Beschreibung |
|---|---|---|
| 1 | Keine Auswirkung | Keine Auswirkung auf Funktion/Sicherheit |
| 2 | Sehr gering | Minimale Qualitätsabweichung |
| 3 | Gering | Leichte Qualitätsminderung, Ausfall < 1h |
| 4 | Relativ gering | Deutliche Qualitätsminderung, < 1 Tag, < 1k € |
| 5 | Mäßig | Funktionseinschränkung, 1–7 Tage, 1–10k € |
| 6 | Hoch | Teilausfall, 1–4 Wochen, 10–50k € |
| 7 | Sehr hoch | Vollausfall, 1–3 Monate, 50–250k € |
| 8 | Extrem hoch | Vollausfall, > 3 Mon., 250–500k €, Verletzte |
| 9 | Kritisch | Katastrophal, > 500k €, Schwerverletzte |
| 10 | Gefährlich | Katastrophal, > 1 Mio €, Todesfälle |

---

## O — Occurrence / Auftreten (1–10)

| O | Stufe | Beschreibung |
|---|---|---|
| 1 | Unwahrscheinlich | < 1 mal in 1.000 Jahren |
| 2 | Sehr gering | ~1 mal in 100 Jahren |
| 3 | Gering | ~1 mal in 10 Jahren |
| 4 | Relativ gering | ~1 mal in 2 Jahren |
| 5 | Gelegentlich | ~2–3 mal/Jahr |
| 6 | Mäßig | ~10 mal/Jahr |
| 7 | Häufig | ~50 mal/Jahr |
| 8 | Sehr häufig | ~125 mal/Jahr |
| 9 | Extrem häufig | ~300 mal/Jahr |
| 10 | Sehr hoch | > 500 mal/Jahr |

---

## D — Detection / Entdeckung (1–10)

| D | Stufe | Beschreibung |
|---|---|---|
| 1 | Fast sicher | Automatische Abschaltung, 100% |
| 2 | Sehr wahrscheinlich | Autom. Prüfung mit SPC, > 95% |
| 3 | Wahrscheinlich | Autom. Prüfung ohne SPC, 80–95% |
| 4 | Relativ wahrscheinlich | 100% manuelle Prüfung, 70–80% |
| 5 | Mäßig wahrscheinlich | Stichprobe mit SPC, 50–70% |
| 6 | Unwahrscheinlich | Stichprobe ohne SPC, 30–50% |
| 7 | Sehr unwahrscheinlich | Nur visuelle Prüfung, 10–30% |
| 8 | Extrem unwahrscheinlich | Keine Prüfung, < 10% |
| 9 | Absolut unsicher | Erst beim Kunden erkannt, < 5% |
| 10 | Absolut unsicher | Nicht erkennbar, ≈ 0% |

---

## Fehlermodi-Vorlagen (Checkliste pro Komponente)

Für jede Komponente prüfen, welche Typen relevant sind. Keine generische Übernahme — S/O/D immer individuell bewerten.

**Dokumentationspflicht:** Alle 9 Kategorien müssen pro Komponente durchgegangen werden. Nicht-relevante Kategorien oder einzelne Typen darin sind explizit mit Begründung zu dokumentieren:
> „nicht relevant — [Begründung, z.B.: kein rotierendes Equipment / keine thermische Prozessführung / kein Druckbehälter]"

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

**Regel:** Jede Utility, die im `connectedSystems`-Feld (upstream/downstream) oder in `utilities` der `anlagendaten.json` gelistet ist, muss als eigener Fehlermodus oder explizit als "nicht relevant — Begründung" dokumentiert werden. Kein Utility darf ohne Prüfung übergangen werden.

**Hintergrund:** Temperaturfehler wurden bei der Confidence-Anlage (20TA24) initial nicht erfasst, weil der Lauda-Thermostat als internes PU-Element betrachtet wurde — obwohl er eine externe Utility-Schnittstelle darstellt (analog zu Eiswasser am Kondensator).

### Prozess
| Typ | Beschreibung |
|---|---|
| Mehr Stoffstrom (High Flow) | Überschreitung der Auslegungskapazität, verringerte Verweilzeit oder Überfüllung nachgeschalteter Apparate. |
| Weniger Stoffstrom (Low Flow) | Unterschreitung der Mindestströmung, Gefahr von Ablagerungen oder unzureichender Durchmischung. |
| Kein Stoffstrom (No Flow) | Vollständiger Abriss der Versorgung, Trockenlauf von Pumpen oder Entstehen von gefährlichen Totvolumina. |
| Rückstrom (Reverse Flow) | Umkehrung der Fließrichtung durch Druckunterschiede, führt zu Kontamination von Vorlagen oder Reaktionen in Zuleitungen. |
| Mehr Druck (High Pressure) | Überschreitung des zulässigen Betriebsdrucks (PS), Gefahr des Berstens oder Ansprechen von Sicherheitseinrichtungen. |
| Weniger Druck (Low Pressure/Vacuum) | Unterschreitung des Mindestdrucks, Gefahr der Kavitation oder Implosion bei nicht vakuumfesten Apparaten. |
| Konzentrationsabweichung | Falsches stöchiometrisches Verhältnis, führt zu Nebenreaktionen, Ausbeuteverlust oder thermischer Instabilität. |
| Phasentrennung / Entmischung | Ungewollte Bildung von Schichten (z.B. Emulsionsbruch), führt zu Fehlmessungen oder lokalen Reaktions-Hotspots. |
| Verschleppung / Kontamination | Eintrag von Fremdstoffen oder Rückständen aus Vorchargen, die als Katalysator oder Inhibitor wirken. |

### Thermisch
| Typ | Beschreibung |
|---|---|
| Mehr Temperatur (High Temperature) | Beschleunigung exothermer Reaktionen (Runaway-Gefahr), thermische Zersetzung des Mediums oder Materialerweichung. |
| Weniger Temperatur (Low Temperature) | Einfrieren von Medien, Auskristallisation (Blockade), Viskositätsanstieg (Pumpenüberlastung) oder Sprödbruch von Werkstoffen. |
| Thermischer Schock | Extreme Temperaturgradienten führen zu Spannungsrissen in Emaille-Auskleidungen oder Schweißnähten. |
| Verlust der Wärmeabfuhr | Ausfall des Kühlmediums oder Fouling, führt zu unkontrolliertem Temperaturanstieg. |
| Lokale Überhitzung (Hot Spot) | Ungleichmäßige Wärmeverteilung, z.B. durch defekte Rührwerke oder Wandbeläge, führt zu lokalem Materialversagen. |

### Mechanisch
| Typ | Beschreibung |
|---|---|
| Erosion / Abrasion | Materialabtrag durch feststoffhaltige Medien oder hohe Strömungsgeschwindigkeiten, führt zu Wandstärkenunterschreitung. |
| Kavitation | Dampfblasenbildung und schlagartige Kondensation, führt zu Materialzerstörung an Laufrädern und Ventilsitzen. |
| Vibration / Resonanz | Mechanische Schwingungen führen zu Ermüdungsbrüchen an Kleinstutzen und Verschraubungen. |
| Äußere Leckage (Integritätsverlust) | Versagen von Flanschdichtungen oder Stopfbuchsen, Medienaustritt in die Umwelt. |
| Innere Leckage (Bypass) | Durchbruch an Wärmetauscherrohren oder defekte Ventilsitze, prozessinterne Vermischung. |
| Materialermüdung | Rissbildung durch zyklische Druck- oder Temperaturbelastungen. |

### Equipment
| Typ | Beschreibung |
|---|---|
| Fouling / Belagbildung | Feststoffschichten auf Funktionsflächen, reduziert Wärmeübergang oder verengt Querschnitte. |
| Verstopfung / Blockade | Verschluss von Filtern, Sieben oder Rohrleitungen. |
| Gleitringdichtungsversagen | Ausfall der Wellenabdichtung an rotierendem Equipment. |
| Innere Beschädigung (Einbauten) | Bruch von Stromstörern, Füllkörpern oder Filterkerzen. |
| Vakuumverlust | Eindringen von Falschluft in evakuierte Systeme, beeinträchtigt Siedepunkte oder führt zu explosiven Gemischen. |

### Elektrisch
| Typ | Beschreibung |
|---|---|
| Vollständiger Spannungsausfall (Blackout) | Absturz aller aktiven Komponenten, Übergang der Anlage in den undefinierten Zustand. |
| Spannungseinbruch (Brownout) | Kurzzeitige Unterspannung, unkontrollierte Resets oder Abfallen von Schützen. |
| Phasenausfall / Asymmetrie | Unregelmäßige Versorgung von Drehstrommotoren, Überhitzung und Wicklungsschäden. |
| EMV-Einkopplung | Elektromagnetische Störsignale auf Signalleitungen, sporadische Fehlmessungen. |
| Erdschluss / Isolationsfehler | Fehlerstrom gegen Gehäuse, Auslösung von Schutzeinrichtungen oder Personengefahr. |

### MSR
| Typ | Beschreibung |
|---|---|
| Eingefrorener Messwert (Frozen Value) | Sensor liefert konstanten Wert trotz Prozessänderung (z.B. durch verstopfte Impulsleitung), Regelung reagiert nicht. |
| Messwertdrift | Schleichende Kalibrierungsabweichung, unbemerktes Verlassen des optimalen Betriebspunkts. |
| Signalrauschen / Spikes | Instabile Signale, hohe mechanische Belastung der Aktoren. |
| Aktor-Blockade (Stuck-at) | Stellventil oder Klappe klemmt mechanisch, Reglerausgang ohne Wirkung. |
| Logikfehler / Software-Bug | Fehlerhafte Verriegelungen oder Schrittketten, falsche Fahrweise. |
| Kommunikationsabriss (Busfehler) | Verlust Verbindung E/A-Ebene zu CPU, Aktoren gehen in Fail-Safe. |
| Antivalenzfehler | Widersprüchliche Rückmeldungen von Endlagenschaltern. |

### Sicherheit
| Typ | Beschreibung |
|---|---|
| Nicht-Öffnen (Safety Valve) | Sicherheitsventil klemmt, unzulässiger Druckaufbau wird nicht begrenzt. |
| Frühzeitiges Ansprechen | Sicherheitsventil/Berstscheibe löst unterhalb Ansprechdruck aus. |
| Ausfall der Inertisierung | Verlust des Stickstoffpolsters, explosionsfähige Atmosphäre im Behälter. |
| Flammendurchschlag | Defekt an Deflagrationssicherungen, Brandübertragung in andere Anlagenteile. |
| Fehlauslösung Not-Halt | Unberechtigtes Auslösen der Schutzkette, instabile Zustände durch plötzlichen Stillstand. |

### Dosierung
| Typ | Beschreibung |
|---|---|
| Überdosierung (Single Point Failure) | Zuviel Komponente A, unkontrollierte Exothermie oder Produktverlust. |
| Unterdosierung | Zuwenig Katalysator/Reaktant, Reaktionsstart verhindert (Akkumulationsgefahr). |
| Falsche Dosierreihenfolge | Abweichung vom Rezept, gefährliche Zwischenprodukte oder Feststoffausfall. |
| Gasblasen im Dosierstrom | Inhomogenität im Medium, massive Volumenstromfehler bei Verdrängerpumpen. |

### Sonstiges
| Typ | Beschreibung |
|---|---|
| Bedienfehler (Human Error) | Falsche Sollwertvorgabe oder Fehlinterpretation von Alarmen. |
| Kennzeichnungsfehler | Falsche Beschriftung von Leitungen oder Handventilen. |
| Externe Einwirkung | Beschädigung von Rohrleitungen durch Staplerverkehr oder herabfallende Lasten. |

---

## Konfidenz-Dokumentation (Pflicht bei jeder Bewertung)

### daten_konfidenz — Qualität der Eingangsdaten

| Stufe | Bedeutung |
|---|---|
| hoch | CCPS/OREDA-Referenzdaten, IEC 61508-Datenbank, publizierte Ausfallraten |
| mittel | Betriebserfahrung des Kunden, interne Störfalldaten, Herstellerangaben |
| niedrig | KI-Schätzung, grobe Analogie, keine belastbaren Daten verfügbar |

### agent_konfidenz — Selbsteinschätzung des Agenten

| Stufe | Bedeutung |
|---|---|
| hoch | Klare Datenlage, Standardfall, Skalenbedeutung eindeutig anwendbar |
| mittel | Leichte Unsicherheit bei O-Wert oder D-Wert; kein Review-Flag nötig |
| niedrig | Unklare Datenlage, stark domänenspezifisch, menschliche Überprüfung empfohlen |

**Regel:** Bei `agent_konfidenz = niedrig` → `agent_konfidenz_begruendung` ist Pflichtfeld + explizit im Dialog ansprechen + Review-Flag im Report.

### daten_quelle — Herkunft der O-Bewertung

| Quelle | Beschreibung |
|---|---|
| CCPS | Center for Chemical Process Safety — Guidelines for CPQRA |
| OREDA | Offshore and Onshore Reliability Data Handbook |
| Betriebserfahrung | Kundeneigene Störfalldaten, Wartungsprotokolle |
| Expertenschätzung | Einschätzung durch Fachingenieur ohne Datenbankreferenz |
| KI-Vorschlag | Agent-Schätzung ohne externe Referenz — immer niedrige daten_konfidenz |

---

## Maßnahmen-Klassifizierung

**STOP-Prinzip** (Priorität): Substitution → Technisch → Organisatorisch → Persönlich

**ABE-Hierarchie**: Abschaffend → Begrenzend → Entdeckend

**Umsetzbarkeit**: schnell · mittelfristig · langfristig

**Kosten**: gering · mittel · hoch

**Empfehlungsmethode**: lexicographic (Grenzwert → Reduktion → Kosten → Zeit)
