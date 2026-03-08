# S/O/D Referenzkarte — FMEA Bewertungsskalen

RPZ = S × O × D

---

## S — Severity / Bedeutung (Schwere der Auswirkung)

| S | Stufe | Beschreibung |
|---|---|---|
| 1 | Keine Auswirkung | Keine Auswirkung auf Funktion oder Sicherheit |
| 2 | Sehr gering | Minimale Qualitätsabweichung, kaum merklich |
| 3 | Gering | Leichte Qualitätsminderung, Ausfall < 1 Stunde |
| 4 | Relativ gering | Deutliche Qualitätsminderung, < 1 Tag, < 1.000 € |
| 5 | Mäßig | Funktionseinschränkung, 1–7 Tage, 1.000–10.000 € |
| 6 | Hoch | Teilausfall, 1–4 Wochen, 10.000–50.000 € |
| 7 | Sehr hoch | Vollausfall, 1–3 Monate, 50.000–250.000 € |
| 8 | Extrem hoch | Vollausfall, > 3 Monate, 250.000–500.000 €, Verletzte |
| 9 | Kritisch | Katastrophal, > 500.000 €, Schwerverletzte |
| 10 | Gefährlich | Katastrophal, > 1 Mio. €, Todesfälle |

---

## O — Occurrence / Auftreten (Häufigkeit des Fehlers)

| O | Stufe | Beschreibung |
|---|---|---|
| 1 | Unwahrscheinlich | < 1 mal in 1.000 Jahren |
| 2 | Sehr gering | ~ 1 mal in 100 Jahren |
| 3 | Gering | ~ 1 mal in 10 Jahren |
| 4 | Relativ gering | ~ 1 mal in 2 Jahren |
| 5 | Gelegentlich | ~ 2–3 mal pro Jahr |
| 6 | Mäßig | ~ 10 mal pro Jahr |
| 7 | Häufig | ~ 50 mal pro Jahr |
| 8 | Sehr häufig | ~ 125 mal pro Jahr |
| 9 | Extrem häufig | ~ 300 mal pro Jahr |
| 10 | Sehr hoch | > 500 mal pro Jahr |

---

## D — Detection / Entdeckung (Erkennbarkeit vor Schadenseintritt)

| D | Stufe | Beschreibung |
|---|---|---|
| 1 | Fast sicher | Automatische Abschaltung, 100 % Erkennung |
| 2 | Sehr wahrscheinlich | Automatische Prüfung mit SPC, > 95 % |
| 3 | Wahrscheinlich | Automatische Prüfung ohne SPC, 80–95 % |
| 4 | Relativ wahrscheinlich | 100 % manuelle Prüfung, 70–80 % |
| 5 | Mäßig wahrscheinlich | Stichprobe mit SPC, 50–70 % |
| 6 | Unwahrscheinlich | Stichprobe ohne SPC, 30–50 % |
| 7 | Sehr unwahrscheinlich | Nur visuelle Prüfung, 10–30 % |
| 8 | Extrem unwahrscheinlich | Keine Prüfung, < 10 % |
| 9 | Absolut unsicher | Erst beim Kunden / nach Schaden erkannt, < 5 % |
| 10 | Nicht erkennbar | Nicht erkennbar, ca. 0 % |

---

## RPZ-Einstufung

| Stufe | RPZ-Bereich | Handlungsbedarf |
|---|---|---|
| Niedrig | < 100 | Monitoring — keine Sofortmaßnahme erforderlich |
| Mittel | 100 – 199 | Maßnahme planen |
| Hoch | 200 – 299 | Maßnahme zeitnah umsetzen |
| Kritisch | >= 300 | Sofortige Maßnahme |

---

## Sonderregeln (überschreiben RPZ-Einstufung)

| Regel | Bedingung | Ergebnis |
|---|---|---|
| Sicherheitsrelevanz | S >= 9 und Stufe nicht kritisch/hoch | Mindestens **hoch** |
| Schlechte Entdeckbarkeit | D >= 9 und S >= 7 | **Kritisch** |

---

## Safety Overrides (automatische S-Erhöhung)

| Kontext | Mindest-S |
|---|---|
| Explosionsschutz / ATEX (Zone 0, 1) | 10 |
| Gefahrstoff-Handling (toxisch, Säure, Chlor ...) | 9 |
| Sicherheitsgerichtetes Bauteil (PSV, BSV, Not-Aus) | 10 |

---

## Maßnahmen-Klassifizierung

**STOP** (Priorität): Substitution → Technisch → Organisatorisch → Persönlich

**ABE**: Abschaffend → Begrenzend → Entdeckend

**Zielwert:** RPZ_neu < 100 (akzeptables Restrisiko)
