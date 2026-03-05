# MSR-Stellenbezeichnungen (ISA / Prozessleittechnik)

Referenz für korrekte Beschreibung von MSR-Komponenten in der Risikoanalyse.
Beim ersten Vorkommen immer ausgeschrieben und mit Funktion erläutern.

## Indication + Control (I + C) – Anzeige und Regelung

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| **PIC** | Pressure Indicator Controller | Druckanzeige und -regler – misst Druck, zeigt an, regelt (z.B. über Ventil) |
| **TIC** | Temperature Indicator Controller | Temperaturanzeige und -regler – misst Temperatur, zeigt an, regelt (z.B. Heizung/Kühlung) |
| **LIC** | Level Indicator Controller | Füllstandsanzeige und -regler – misst Füllstand, zeigt an, regelt (z.B. Dosierung) |
| **FIC** | Flow Indicator Controller | Durchflussanzeige und -regler – misst Durchfluss, zeigt an, regelt |
| **SIC** | Speed Indicator Controller | Drehzahlanzeige und -regler – misst Drehzahl, zeigt an, regelt (z.B. Rührwerk) |

## Nur Anzeige (I) – Indication

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| **PI** | Pressure Indicator | Druckanzeige – misst und zeigt Druck, keine Regelung |
| **TI** | Temperature Indicator | Temperaturanzeige – misst und zeigt Temperatur, keine Regelung |
| **LI** | Level Indicator | Füllstandsanzeige – misst und zeigt Füllstand, keine Regelung |
| **FI** | Flow Indicator | Durchflussanzeige – misst und zeigt Durchfluss, keine Regelung |

## Schalter (S) – Switch

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| **LSH** | Level Switch High | Füllstandsschalter hoch – schaltet bei hohem Füllstand (Alarm oder Abschaltung) |
| **LSHH** | Level Switch High High | Füllstandsschalter sehr hoch – Überfüllsicherung, harte Abschaltung |
| **LSL** | Level Switch Low | Füllstandsschalter niedrig |
| **LSLL** | Level Switch Low Low | Füllstandsschalter sehr niedrig |
| **PSH** | Pressure Switch High | Druckschalter hoch – schaltet bei Überdruck |
| **PSL** | Pressure Switch Low | Druckschalter niedrig – schaltet bei Unterdruck |
| **TSH** | Temperature Switch High | Temperaturschalter hoch |
| **TSL** | Temperature Switch Low | Temperaturschalter niedrig |

## Transmitter (T) – Übertragung

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| **PT** | Pressure Transmitter | Druckmessumformer – misst Druck, liefert Signal (z.B. 4–20 mA) |
| **TT** | Temperature Transmitter | Temperaturmessumformer |
| **LT** | Level Transmitter | Füllstandsmessumformer |
| **FT** | Flow Transmitter | Durchflussmessumformer |

## Sicherheitstechnik

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| **PSV** | Pressure Safety Valve | Sicherheitsventil – öffnet bei Überdruck, entlastet |
| **BSV** | Bursting Disc / Berstscheibe | Berstscheibe – bricht bei Überdruck, letzte Absicherung |
| **VSV** | Vacuum Safety Valve | Vakuumsicherheitsventil – verhindert Unterdruck (Vakuumbrecher) |

## Beispiel für korrekte Formulierung

❌ „PIC-402 – Drucksensor im Reaktor“  
✅ „PIC-402 – Druckanzeige und -regler im Reaktor (misst Druck, regelt z.B. über Abblaseventil)“

❌ „LSHH-403 – Füllstandsschalter“  
✅ „LSHH-403 – Füllstandsschalter sehr hoch (LSHH), Überfüllsicherung bei 480 L – schaltet bei Überschreitung ab“
