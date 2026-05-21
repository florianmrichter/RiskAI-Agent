# S/O/D Referenzkarte — FMEA-Bewertungsskalen

## S — Severity (Bedeutung)

| S | Stufe | Beschreibung |
|---|---|---|
| 1 | Keine Auswirkung | Keine Auswirkung auf Funktion/Sicherheit |
| 2 | Sehr gering | Minimale Qualitätsabweichung |
| 3 | Gering | Leichte Qualitätsminderung, Ausfall < 1h |
| 4 | Relativ gering | Deutliche Qualitätsminderung, < 1 Tag, < 1k EUR |
| 5 | Mäßig | Funktionseinschränkung, 1-7 Tage, 1-10k EUR |
| 6 | Hoch | Teilausfall, 1-4 Wochen, 10-50k EUR |
| 7 | Sehr hoch | Vollausfall, 1-3 Monate, 50-250k EUR |
| 8 | Extrem hoch | Vollausfall, > 3 Mon., 250-500k EUR, Verletzte |
| 9 | Kritisch | Katastrophal, > 500k EUR, Schwerverletzte |
| 10 | Gefährlich | Katastrophal, > 1 Mio EUR, Todesfälle |

## O — Occurrence (Auftreten)

| O | Stufe | Häufigkeit |
|---|---|---|
| 1 | Unwahrscheinlich | < 1 mal in 1.000 Jahren |
| 2 | Sehr gering | ~1 mal in 100 Jahren |
| 3 | Gering | ~1 mal in 10 Jahren |
| 4 | Relativ gering | ~1 mal in 2 Jahren |
| 5 | Gelegentlich | ~2-3 mal/Jahr |
| 6 | Mäßig | ~10 mal/Jahr |
| 7 | Häufig | ~50 mal/Jahr |
| 8 | Sehr häufig | ~125 mal/Jahr |
| 9 | Extrem häufig | ~300 mal/Jahr |
| 10 | Sehr hoch | > 500 mal/Jahr |

## D — Detection (Entdeckung)

| D | Stufe | Erkennungswahrscheinlichkeit |
|---|---|---|
| 1 | Fast sicher | Automatische Abschaltung, 100% |
| 2 | Sehr wahrscheinlich | Autom. Prüfung mit SPC, > 95% |
| 3 | Wahrscheinlich | Autom. Prüfung ohne SPC, 80-95% |
| 4 | Relativ wahrscheinlich | 100% manuelle Prüfung, 70-80% |
| 5 | Mäßig wahrscheinlich | Stichprobe mit SPC, 50-70% |
| 6 | Unwahrscheinlich | Stichprobe ohne SPC, 30-50% |
| 7 | Sehr unwahrscheinlich | Nur visuelle Prüfung, 10-30% |
| 8 | Extrem unwahrscheinlich | Keine Prüfung, < 10% |
| 9 | Absolut unsicher | Erst beim Kunden erkannt, < 5% |
| 10 | Absolut unsicher | Nicht erkennbar, ca. 0% |

## RPZ-Klassifizierung

RPZ = S x O x D

| Stufe | RPZ-Bereich | Maßnahme |
|---|---|---|
| kritisch | >= 300 | Sofortige Maßnahme |
| hoch | 200-299 | Maßnahme zeitnah umsetzen |
| mittel | 100-199 | Maßnahme planen |
| niedrig | < 100 | Monitoring |

## Sonderregeln

| Bedingung | Ergebnis |
|---|---|
| S >= 9 und Stufe nicht kritisch/hoch | Mindestens **hoch** |
| D >= 9 und S >= 7 | **kritisch** |

## Safety Overrides

| Kontext | Min. S |
|---|---|
| Explosionsschutz (ATEX, Zone 0/1) | 10 |
| Gefahrstoff (Säure, Lauge, toxisch) | 9 |
| Sicherheitsbauteil (PSV, Berstscheibe, Not-Aus) | 10 |
