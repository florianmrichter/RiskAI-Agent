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

## Phase 1b — Bestehende Risikobetrachtungen und Dokumentation

### Bestehende Risikobetrachtungen

Frage gezielt nach bereits existierenden Risikoanalysen:

1. **Explosionsschutzdokument** — Gibt es ein bestehendes Ex-Schutzdokument?
   → Wenn ja: Welche Ex-Zonen sind definiert? Welche Zündquellenbewertung liegt vor?

2. **Prozessstufenrisikoanalyse** — Wurde bereits eine Gefahrenanalyse durchgeführt
   (HAZOP, PAAG, What-If, Checkliste)?
   → Wenn ja: Ergebnisse als Input verwenden, nicht doppelt bewerten

3. **Scope der aktuellen Analyse** — Soll die FMEA explizit auf bestimmte
   Risikobereiche fokussiert werden?
   - [E] Explosionsschutzrisiken (ATEX, Zündquellen, Inertisierung)
   - [P] Prozessrisiken (Temperatur, Druck, Stoffströme, Dosierung)
   - [B] Beides (vollständige Analyse)
   → Standard: Beides. Nutzer kann einschränken.

Bestehende Dokumente in den Anlagendaten referenzieren:
`processDescription.bestehende_risikobetrachtungen[]` mit Feldern:
`typ`, `datum`, `ersteller`, `wesentliche_ergebnisse`, `referenz_dokument`

### Dokumentation und Datenquellen

Frage nach vorhandener Anlagendokumentation:

1. **Herstellerdokumentation** — Gibt es Datenblätter, Betriebsanleitungen,
   technische Zeichnungen des Reaktors/der Anlage?
   > "Wenn du ein PDF oder einen Link hast, kann ich die Daten daraus extrahieren
   > und automatisch in die Anlagendaten übernehmen."

2. **R&I-Fließbild (P&ID)** — Gibt es ein R&I-Schema?
   → Daraus lassen sich Systeme, MSR-Stellen, Sicherheitseinrichtungen und
   Verbindungen systematisch ableiten.

3. **Sicherheitsdatenblätter (SDB)** — Für die eingesetzten Stoffe?
   → Ergänzt/validiert PubChem-Daten.

4. **Web-Recherche** — "Soll ich im Internet nach technischen Daten des
   Herstellers/Typs suchen, um die Datenlage zu verbessern?"
   → Bei Bestätigung: Herstellerseite, Datenblätter, technische Spezifikationen

**Verhalten bei Dokument-Upload:**
- PDF/Link erhalten → Daten extrahieren → mit bisherigen Anlagendaten abgleichen
- Neue Informationen in `anlagendaten.json` ergänzen
- Widersprüche explizit ansprechen: "Im Datenblatt steht X, du hast Y gesagt — was stimmt?"
- Quelle in den Anlagendaten dokumentieren (z.B. "Datenblatt Büchi Mini Pilot")

---

## Phase 2 — Prozessbeschreibung

1. Was macht die Anlage? (Prozesszweck in 2–3 Sätzen)
2. Betriebsweise: Batch / Kontinuierlich / Semi-Batch?
3. Besondere Rahmenbedingungen? (12. BImSchV? Ex-Zone? Genehmigungspflichtig?)
4. **Betriebszustände** *(FMEA-kritisch)*:
   > "Welche Betriebszustände durchläuft die Anlage?"
   > Typisch: Vorbereitung/Inertisierung → Befüllung → Anfahren/Aufheizen →
   > Normalbetrieb → Abkühlen/Entleerung → Reinigung → Wartung/Stillstand
   >
   > Für jeden Zustand: Was ist offen/geschlossen? Was läuft/steht?
   > Besonders kritisch: Zustände mit offenem Handloch, Zustände mit
   > gleichzeitiger Bewegung + Entleerung, Reinigung mit brennbaren Stoffen.

   Speichern unter `processDescription.betriebszustaende[]` mit Feldern:
   `name`, `beschreibung`, `handloch_offen`, `ruehrwerk_aktiv`, `heizung_aktiv`,
   `inertisierung_aktiv`, `stoffe_im_einsatz`

5. **Bekannte Störfälle / Betriebserfahrungen** *(FMEA-kritisch für O-Werte):*
   > "Gibt es bekannte Störfälle, Beinaheunfälle oder häufige Betriebsstörungen an dieser Anlage?
   > Wenn ja: Was ist passiert, wie oft, was war die Ursache?
   > (Diese Information hilft mir, die Häufigkeitsbewertung der FMEA realistisch zu gestalten)"

   Speichern unter `betriebserfahrungen[]` mit Feldern: `datum`, `beschreibung`, `ursache`, `konsequenz`, `massnahme`

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

> ⚠️ **Druckeinheiten-Pflicht (gilt für alle Druckangaben):**
> Jedes „bar" ohne Qualifizierung ist **nachzufragen**. Speicherung immer mit explizitem Typ:
>
> - `barg` = Überdruck (relativ zur Atmosphäre) — Standard bei Behältern, Reaktoren, Leitungen
> - `bara` = Absolutdruck (relativ zum Vakuum) — bei Vakuumanwendungen
>
> **Entscheidungshilfe beim Nachfragen:**
>
> - Positiver Wert (z. B. „0,5 bar") → wahrscheinlich barg: *„Meinen Sie 0,5 barg Überdruck?"*
> - Negativer Wert (z. B. „-0,8 bar") → meist barg (Unterdruck/Vakuum): *„Meinen Sie -0,8 barg, also Unterdruck gegenüber Atmosphäre?"*
> - Vakuumanlage: *„Arbeiten Sie mit Absolutdruck — z. B. 0,2 bara?"*
>
> Gilt analog für: mbar, MPa, kPa, psi — immer Typ klären und explizit speichern.

### 4c — Ausrüstung (Equipment)
- Welche Apparate, Pumpen, Wärmetauscher, Armaturen, Antriebe?
- Für jeden: Name/Bezeichnung, Typ, Position, Antriebsart (elektrisch/pneumatisch/–), wichtige Parameter

### 4d — MSR-Ausrüstung ⚠ FMEA-KRITISCH

> **FMEA-KRITISCH** — Diese Felder blockieren die FMEA wenn leer:
> SIL-Einstufung aller sicherheitsrelevanten MSR-Kreise.
> Ohne SIL kann D-Wert für Sicherheitskreise nicht korrekt bewertet werden.

- Welche Messgeräte und Regler? (Druck, Temperatur, Füllstand, Durchfluss, ...)
- Für jedes Gerät: MSR-Kennzeichen (z. B. TIC-101), Typ, Position, Signalart (4-20 mA / Relais / Lokal), ATEX-Zone, **SIL-Einstufung** (falls vorhanden)

**ATEX-Pflichtfragen (bei Ex-Zone ≥ 1):**
- **ATEX-Gerätekategorie** explizit abfragen — Gas (1G/2G/3G), Staub (1D/2D/3D), oder beides?
- **Staubexplosionsschutz** — werden brennbare Stäube verarbeitet? Kst-Wert? Glimmtemperatur?
- **Hybridgemische** — können Gas/Dampf + Staub gleichzeitig auftreten?
- **Inertisierung vorhanden?** ⚠ Pflichtfrage wenn Ex-Zone ≥ 1 (Gas oder Staub)
  > "Ist eine N₂-Inertisierung vorhanden? Wenn ja: Wie wird der O₂-Grenzwert überwacht?"

### 4e — Sicherheitseinrichtungen ⚠ FMEA-KRITISCH

> **FMEA-KRITISCH** — Alle PSV, Berstscheiben, Notstopp-Einrichtungen müssen vollständig erfasst sein.
> Diese bestimmen den D-Wert für alle druckführenden Fehlermodi.

- Sicherheitsventile (PSV): Bezeichnung, **Ansprechdruck**, DN, Prüfintervall
- Berstscheiben: Bezeichnung, Berstdruck, DN
- NOT-AUS / NOT-HALT: Auslösebedingungen, Abschaltumfang
- Gaswarnung, Auffangwannen, weitere Schutzeinrichtungen

### 4f — Verbundene Systeme
- Welche Systeme liefern zu (upstream)?
- Welche nehmen ab (downstream)?

### 4g — Hersteller-, Stamm- und Kostendaten *(empfohlen)*

- Hersteller, Typ, Seriennummer, Baujahr
- **Technischer Platz** (SAP/ERP-Kennung, z.B. "DE-PROD-B-R1-001")
- **Equipment-Nummer** (z.B. "EQ-10045892")
- **Inventar-/Asset-Nummer** (z.B. "A-2019-0234")
- Wartungsgruppe / Instandhaltungsbereich
- Letzter TÜV / nächste Prüfung, Inbetriebnahmedatum
- **Investitionskosten / Wiederbeschaffungskosten** *(FMEA-relevant!)*
  > "Was hat die Anlage gekostet bzw. was würde eine Ersatzbeschaffung kosten?"
  > Wichtig für die Kostenbewertung bei Totalschaden (S-Wert Dimension 'Kosten').
  > Größenordnung reicht: < 10k € / 10–50k € / 50–250k € / 250k–1M € / > 1M €

Speichern unter `systems[].manufacturerData` und `systems[].masterData`.

### Phasen-Checkpoint (bei mehr als 2 Systemen)

Nach Abschluss jedes Systems in Phase 4 expliziten Checkpoint ausgeben:

```
[System {NAME} — vollständig erfasst]
Sub-Phasen 4a–4g abgeschlossen.
FMEA-kritische Felder: {SIL vorhanden? ATEX-Zone? PSV?}
→ Weiter mit System {NÄCHSTES_SYSTEM}?
```

---

## Phase 5 — Medien und Betriebsstoffe ⚠ FMEA-KRITISCH (Notkühlung)

> **FMEA-KRITISCH** — Utility-Ausfall ist eine eigenständige Fehlermodus-Kategorie in der FMEA.
> Diese Daten werden später für Fehlermodi-Kategorien wie "Kühlwasserausfall" oder "N2-Ausfall" benötigt.
> Erkläre dem Nutzer diesen Zusammenhang explizit.

Frage nach Hilfsmedien:

- **Dampf:** Druck, Temperatur?
- **Kühlwasser:** Vor-/Rücklauftemperatur, Druck?
- **Notkühlung** vorhanden? ⚠ FMEA-KRITISCH (Medium, Temperatur, Auslösebedingung)
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
