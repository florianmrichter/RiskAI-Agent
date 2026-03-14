# Gefahrenfelder — Erweiterte Prüfpunkte für FMEA-Analyse

Diese Prüfpunkte ergänzen die 9 FM-Kategorien aus `fmea-standards.md`. Sie dienen als systematische Checkliste, damit keine Gefahrenaspekte übersehen werden.

---

## Kategorie 1 — Prozessbedingungen (Standard-Prüfpunkte)

Diese Felder werden bei **jeder** Analyse als Pflicht-Prüfpunkte abgearbeitet.

| ID | Name | FM-Kategorie | Prüffrage |
|---|---|---|---|
| 1.1 | Spezifikation / Verunreinigungen | Prozess | Qualität der Ausgangsstoffe? Verunreinigungen möglich? |
| 1.2 | Präsenz der Ausgangsstoffe | Prozess, Dosierung | Fehlen von Ausgangsstoffen? Versorgungsunterbrechung? |
| 1.3 | Dosierung / Menge / Reihenfolge | Dosierung | Korrekte Zugabe (Menge, Reihenfolge, Geschwindigkeit)? |
| 1.4 | Reaktionsbedingungen (pH etc.) | Prozess | pH-Wert, Konzentration, Reaktionsparameter korrekt? |
| 1.5 | Druck | Prozess | Über-/Unterdruck-Szenarien? Vakuumfestigkeit? |
| 1.6 | Temperatur | Thermisch | Temperaturabweichungen? Runaway? Thermischer Schock? |
| 1.7 | Vermischung / Verwechslung | Prozess, Sonstiges | Falsche Stoffe gemischt? Verwechslung von Leitungen? |
| 1.8 | Explosionsfähige Atmosphäre | Sicherheit | Ex-Zone? Zündquellen? ATEX-Konformität? |
| 1.9 | Stoffströme / Rückströmung | Prozess | Rückfluss? Falschströme? Förderwege blockiert? → **Backflow-Pflichtprüfung** |
| 1.10 | Füllstand / Überfüllung | Prozess | Überlaufszenarien? Füllstandsüberwachung? |
| 1.11 | Rührung / Rührgeschwindigkeit | Mechanisch, Equipment | Trockenlauf? Überdrehzahl? Vibration? Wellendichtung? |
| 1.12 | Elektrostatische Aufladung | Sicherheit, Elektrisch | Erdung? Ableitfähige Materialien? Schüttgut/Pulver? |
| 1.13 | Reaktion mit Wärmeträger | Thermisch | Vermischung Produkt/Wärmeträger? Doppelmantelbruch? |
| 1.14 | Katalysator / Inhibitor | Prozess, Dosierung | Deaktivierung? Falscher Katalysator? Inhibitor verbraucht? |
| 1.15 | Filtrieren / Abtrennen / Dekantieren | Equipment | Filterdurchbruch? Verstopfung? Feststoffaustrag? |
| 1.16 | Pumpen / Leeren / Transfer | Mechanisch, Prozess | Trockenlauf? Kavitation? Leckage beim Transfer? |
| 1.17 | Heizen / Kühlen | Thermisch | Kühlungsausfall? Unkontrolliertes Heizen? Fouling? |
| 1.18 | Reinigung | Prozess, Sicherheit | Brennbare Lösemittel bei Reinigung? Restmengen? Exposition? |
| 1.19 | Kontrolle / Überwachung / Detektion | MSR | Sensorausfall? Fehlende Redundanz? Alarmkette? |
| 1.20 | Evakuieren / Entlasten | Prozess, Sicherheit | Druckentlastung funktionsfähig? Inertisierung bei Evakuierung? |
| 1.21 | Abluft / Ableitung | Sicherheit, Prozess | Abluftleitung verstopft? Sicherheitsventile korrekt dimensioniert? |
| 1.22 | Prozessunterbruch | Prozess, Elektrisch | Not-Halt-Folgen? Störungsreaktion? Wiederanfahren? |
| 1.23 | Stoff-/Chemikalienaustritt | Mechanisch, Sicherheit | Leckage? Flanschdichtungen? Gleitringdichtung? |
| 1.24 | Manuelle Tätigkeiten | Sonstiges, Sicherheit | Mannloch/Handloch offen? Probenahme? Filterwechsel? Exposition? |
| 1.25 | Wartungs-/Reparaturarbeiten | Sonstiges | Freigabeverfahren? Restenergie? Isolation? |
| 1.26 | Offenes Stoffhandling (K1-Gefahrstoffe) | Sicherheit, Sonstiges | Exposition bei Befüllung/Entleerung? Absaugung? PSA? |

---

## Kategorie 2 — Energie / Medien (Standard-Prüfpunkte)

Diese Felder werden bei **jeder** Analyse als Pflicht-Prüfpunkte abgearbeitet.

| ID | Name | FM-Kategorie | Prüffrage |
|---|---|---|---|
| 2.1 | Hilfsenergien | Elektrisch, Prozess | Stromausfall? Druckluft-/Steuerluftausfall? N₂-Versorgung? Vakuumverlust? |
| 2.2 | Heiz-/Kühlmedien | Thermisch | Dampfausfall? Kühlwassermangel? Sole-Leckage? |
| 2.3 | PLT-Einrichtungen | MSR | SPS-Ausfall? Regelung? Automatisierung? |
| 2.4 | Integrität der Bauteile | Mechanisch, Equipment | Korrosion? Materialermüdung? Werkstoffverträglichkeit? |
| 2.5 | CE-Konformität (Produktsicherheitsgesetz) | Sicherheit | Konformitätsbewertung aktuell? Dokumentation vorhanden? |
| 2.6 | Cyber Security | MSR, Elektrisch | Netzwerk? Fernwartung? SCADA-Anbindung? Zugriffsschutz? |

---

## Kategorie 3 — Sonstige Einflüsse (optional)

Diese Felder werden **nur bei Außenanlagen** oder auf **explizite Anfrage** des Nutzers geprüft. Bei Innenanlagen: mit Begründung überspringen.

| ID | Name | FM-Kategorie | Prüffrage |
|---|---|---|---|
| 3.1 | Hagel | Mechanisch | Beschädigung von Außenkomponenten? Glas? Rohrleitungen? |
| 3.2 | Blitzschlag | Elektrisch, Sicherheit | Blitzschutz? Überspannungsschutz? Erdung? |
| 3.3 | Erdabsenkung | Mechanisch | Fundamentverschiebung? Rohrleitungsbruch? |
| 3.4 | Starkregenereignis | Prozess | Überflutung? Rückhaltebecken? Auffangwannen? |
| 3.5 | Umgebungstemperaturen | Thermisch | Einfrieren von Leitungen? Kondensation? |
| 3.6 | Sabotage | Sicherheit, Sonstiges | Zugangskontrolle? Manipulationsschutz? |
| 3.7 | Sturm / Tornado | Mechanisch | Windlast auf Aufbauten? Lose Teile? |
| 3.8 | Erdbeben | Mechanisch | Seismische Auslegung? Verankerung? |
| 3.9 | Brand | Sicherheit | Brandlast? Brandmeldeanlage? Löscheinrichtungen? Brandausbreitung? |

---

## Nutzung in der FMEA-Analyse

1. Beim Durchgehen der 9 FM-Kategorien die zugehörigen Gefahrenfelder als **zusätzliche Prüfpunkte** heranziehen
2. Jedes Gefahrenfeld, das für die aktuelle Komponente relevant ist, muss zu einem Fehlermodus führen oder explizit als "nicht relevant" dokumentiert werden
3. Kategorie 3 nur bei Außenanlagen oder auf Anfrage prüfen — Begründung dokumentieren
4. Keine Referenz auf "ZHA" oder "Gefahrenfeldanalyse" im Output — nur als interne Prüfpunkte verwenden
