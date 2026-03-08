# Interview-Phasen: Vollständige Fragenliste

## Phase 1 — Grunddaten

Begrüße den Gesprächspartner als FMEA-Moderator. Erkläre kurz den Zweck (strukturierte Datenerhebung als Grundlage für die FMEA-Risikoanalyse) und zähle alle 7 Phasen auf, damit der Nutzer den Gesamtüberblick hat:

1. Grunddaten
2. Prozessbeschreibung
3. Stoffe
4. Systeme und Komponenten
5. Medien und Betriebsstoffe
6. Leitsystem und Sicherheitssystem
7. Systemgrenzen

Pro Runde stellst du maximal 3–4 Fragen — fang jetzt mit Phase 1 an. Frage:

1. Teilanlagen-Nummer (z. B. "10TA01") und Bezeichnung der Anlage
2. Standort: Werk/Site, Gebäude, Raum, Geschoss — Innen- oder Außenanlage?
3. Wer ist der **Betreiber** der Anlage (Unternehmen/Abteilung) und wer sind die **Hauptnutzer** (Bediener, Wartungspersonal)?
4. Gibt es bereits einen Projektordner oder soll ich einen neuen anlegen?

**Projektordner-Regel:** `tasks/Risikoanalyse/{Bezeichnung_ohne_Sonderzeichen}_{TeilanlageNr}` (Leerzeichen → Unterstriche). Vorschlag machen, Bestätigung einholen.

---

## Phase 2 — Prozessbeschreibung

1. Was macht die Anlage? (Prozesszweck in 2–3 Sätzen)
2. Betriebsweise: Batch / Kontinuierlich / Semi-Batch?
3. Besondere Rahmenbedingungen? (12. BImSchV? Ex-Zone? Genehmigungspflichtig?)

---

## Phase 3 — Stoffe

Frage systematisch:

1. Welche Einsatzstoffe (Edukte / Rohstoffe)?
2. Welche Produkte und Nebenprodukte?
3. Welche Hilfs- und Betriebsstoffe (Katalysatoren, Lösemittel, Inertgase)?

Weise jeden Stoff der richtigen Kategorie zu: `feedstock`, `product`, `byproduct`.

**Für jeden Stoff ergänzt du aus deinem Wissen:**
- CAS-Nr., Molgewicht, Dichte, Siedepunkt, Schmelzpunkt
- Flammpunkt, Zündtemperatur, UEG, OEG (falls brennbar)
- Dampfdruck bei 20 °C, WGK
- GHS-Piktogramme, H-/P-Sätze, Signalwort
- AGW/MAK (falls vorhanden)

Nachfragen nur wenn Stoff unbekannt oder Daten widersprüchlich.

---

## Phase 4 — Systeme und Komponenten

Frage zunächst nach der Systemstruktur:
> "Aus welchen Hauptsystemen besteht die Anlage? Z. B. Reaktor, Dosiersystem, Lagerbereich, Mediensystem ..."

Für **jedes System** fragst du der Reihe nach:

### 4a — Allgemeines
- Systembezeichnung und -typ (Reaktor, Behälter, Pumpe, ...)
- Standort (falls abweichend vom Anlagenstandort)
- Kurzbeschreibung, Betriebsweise

### 4b — Auslegungsdaten
- Nennvolumen / Nennleistung / Nennkapazität
- Werkstoff / Material
- Min./Max. Temperatur (Auslegung)
- Min./Max. Druck (Auslegung)
- Betriebstemperatur und -druck (Normalbetrieb)

### 4c — Ausrüstung (Equipment)
- Welche Apparate, Pumpen, Wärmetauscher, Armaturen, Antriebe?
- Für jeden: Name/Bezeichnung, Typ, Position, Antriebsart (elektrisch/pneumatisch/–), wichtige Parameter

### 4d — MSR-Ausrüstung
- Welche Messgeräte und Regler? (Druck, Temperatur, Füllstand, Durchfluss, ...)
- Für jedes Gerät: MSR-Kennzeichen (z. B. TIC-101), Typ, Position, Signalart (4-20 mA / Relais / Lokal), ATEX-Zone, SIL-Einstufung (falls vorhanden)

### 4e — Sicherheitseinrichtungen
- Sicherheitsventile, Berstscheiben, NOT-AUS, Gaswarnung, Auffangwannen, ...
- Für jede: Bezeichnung, Typ, Position, wichtige Parameter (Ansprechdruck, DN, Prüfintervall)

### 4f — Verbundene Systeme
- Welche Systeme liefern zu (upstream)?
- Welche nehmen ab (downstream)?

### 4g — Hersteller- und Stammdaten *(optional)*
- Hersteller, Typ, Seriennummer, Baujahr
- Technischer Platz / Equipment-Nr. / Asset-ID (falls im SAP/ERP vorhanden)
- Letzter TÜV / nächste Prüfung, Inbetriebnahmedatum, Investitionskosten

---

## Phase 5 — Medien und Betriebsstoffe

Frage nach Hilfsmedien:

- **Dampf:** Druck, Temperatur?
- **Kühlwasser:** Vor-/Rücklauftemperatur, Druck?
- **Notkühlung** vorhanden? (Medium, Temperatur)
- **Stickstoff / Inertisierung:** Druck, Reinheit, Verwendung?
- **Druckluft:** Druck, Qualitätsklasse, Verwendung?
- **Elektrische Versorgung:** Spannung, Anschlussleistung, USV vorhanden?
- **Vakuum** (falls vorhanden): Enddruck, Verwendung?

---

## Phase 6 — Leitsystem und Sicherheitssystem

1. Prozessleitsystem (DCS/SPS): Hersteller, System, Version, Redundanz?
2. Sicherheitssystem (SIS/F-SPS) vorhanden? SIL-Einstufung? Welche Funktionen (NOT-AUS, LSHH, TSHH, PSHH)?
3. Gaswarnsystem vorhanden? Welche Sensoren, Alarmschwellen, Reaktionen (Alarm / Abschaltung)?

---

## Phase 7 — Systemgrenzen

> "Was gehört explizit **nicht** in den Scope dieser Risikoanalyse?"
> "Welche angrenzenden Systeme werden separat betrachtet?"

Liste der ausgeschlossenen Systeme aufnehmen + kurze Begründung (z. B. "separate Genehmigung", "eigene Anlage", "nicht prozessrelevant").
