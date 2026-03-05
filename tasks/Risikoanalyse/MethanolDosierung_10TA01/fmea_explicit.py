"""
Explizite FMEA-Definitionen – Methanol-Lager- und Dosieranlage 10TA01.
Agent-Output: Jede Komponente wird einzeln analysiert und hier ergänzt.
"""


def get_fmea_for_component(komp_id: str) -> dict:
    """Liefert explizite FMEA-Daten für die Komponente. {} wenn nicht definiert."""
    return _FMEA.get(komp_id, {})


# ─── KOMP-001: Lagertank T-101 ───
# Erdtank, 10 m³, Stahl/EP-Beschichtung, Methanol, Ex-Zone 1, 12. BImSchV
_FMEA = {
    "KOMP-001": {
        "functions": [
            {
                "funktion_id": "KOMP-001-F1",
                "typ": "Hauptfunktion",
                "beschreibung": "Sicheres Lagern von Methanol (max. 9.000 L, WGK 2, leichtentzündlich)",
                "anforderungen": [
                    {"id": "KOMP-001-F1-A1", "parameter": "Füllvolumen", "sollwert": "Max. 9.000 L"},
                    {"id": "KOMP-001-F1-A2", "parameter": "Dichtheit", "sollwert": "Keine Medienfreisetzung"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F2",
                "typ": "Nebenfunktion",
                "beschreibung": "Drucklose Lagerung sicherstellen (atmosphärisch ± 0,05 bar)",
                "anforderungen": [
                    {"id": "KOMP-001-F2-A1", "parameter": "Druck", "sollwert": "-0,05 bis +0,5 bar (relativ)"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F3",
                "typ": "Nebenfunktion",
                "beschreibung": "Kontrollierte Entnahme und Befüllung ermöglichen",
                "anforderungen": [
                    {"id": "KOMP-001-F3-A1", "parameter": "Füllstandserfassung", "sollwert": "LIC-101 in Betrieb"},
                ],
            },
            {
                "funktion_id": "KOMP-001-F4",
                "typ": "Nebenfunktion",
                "beschreibung": "Leckagefreiheit gegenüber Boden und Grundwasser gewährleisten",
                "anforderungen": [
                    {"id": "KOMP-001-F4-A1", "parameter": "Leckagerate", "sollwert": "Null-Leckage (WHG, 12. BImSchV)"},
                ],
            },
        ],
        "failure_modes": [
            # ── FM-1: Leckage ──
            {
                "funktion_id": "KOMP-001-F4",
                "fehler_id": "KOMP-001-F4-FM1",
                "fehlermodus": "Leckage – Methanol-Austritt an Tankmantel, Domschacht oder Rohranschlüssen",
                "fehlerart": "Mechanisch / Korrosion",
                "causes": [
                    {"ursache_id": "FM1-UC1", "beschreibung": "Innenkorrosion durch EP-Beschichtungsschaden (Alterung, mechanische Verletzung)", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM1-UC2", "beschreibung": "Außenkorrosion durch aggressive Böden oder Streustrom", "herkunft": "Betrieb", "phase": "Betrieb"},
                    {"ursache_id": "FM1-UC3", "beschreibung": "Ermüdungsrisse an Schweißnähten (Domschacht-Übergang)", "herkunft": "Fertigung", "phase": "Betrieb"},
                    {"ursache_id": "FM1-UC4", "beschreibung": "Flanschleckage am Domschacht durch Dichtungsversagen oder unzureichenden Anzug", "herkunft": "Betrieb", "phase": "Wartung"},
                    {"ursache_id": "FM1-UC5", "beschreibung": "Rohranschlussbruch durch Bodensetzung oder Erschütterung", "herkunft": "Betrieb", "phase": "Betrieb"},
                ],
                "effects": {
                    "mensch": ("Schwere Verletzung möglich", "Methanol-Inhalation oder Hautkontakt; Zündgefahr in Ex-Zone 1 (LEL 6 %)"),
                    "umwelt": ("Boden- und Grundwasserschaden", "WGK 2, Meldepflicht nach 12. BImSchV, Sanierungskosten"),
                    "anlage": ("Betriebsunterbrechung", "Entleerung, Inspektion, Reparatur des Tanks"),
                    "kosten": ("Bis 500.000 € und mehr", "Sanierung, Bußgelder, Produktionsausfall"),
                },
                "controls": [
                    {
                        "name": "GW-101",
                        "typ": "Sensor",
                        "wirkung": "E",
                        "sil_level": "SIL-1",
                        "beschreibung": "Gasdetektor Methanol im Tankraum – erkennt Dampffreisetzung ab Schwellwert",
                        "beeinflusst": "D",
                        "einschraenkung": "Erkennt Dampf, nicht flüssige Bodenleckage; bei erdvergrabenen Tanks zeitverzögert.",
                    },
                    {
                        "name": "Sichtprüfung",
                        "typ": "Organisatorisch",
                        "wirkung": "E",
                        "beschreibung": "Regelmäßige Sichtprüfung Domschacht und Rohranschlüsse durch Betreiber",
                        "beeinflusst": "D",
                        "einschraenkung": "Erkennt Mantel-Leckage bei Erdtank nicht; nur oberflächliche Bereiche kontrollierbar.",
                    },
                ],
                "S": 9, "O": 3, "D": 7,
                "begruendung_S": "Methanol-Austritt: WGK 2 → Boden-/Grundwasserschaden, Explosionsgefahr (Ex-Zone 1), Personengefährdung; 12. BImSchV-Meldepflicht",
                "begruendung_O": "Moderne EP-Beschichtung + Kathodenschutz; Erfahrungswerte Erdtankleckagen ca. 1 × in 10 Jahren",
                "begruendung_D": "Erdvergraben: Mantel-Leckage visuell nicht erkennbar; GW-101 erkennt nur Dampf; keine Doppelwand/Leckagesonde",
                "kontext_beschreibung": "Der Lagertank ist erdvergraben und enthält bis zu 9.000 L Methanol. Eine Leckage am Mantel oder an Anschlüssen ist besonders kritisch, weil sie lange unentdeckt bleiben kann – der Boden verdeckt den Tank. Methanol ist WGK 2 und kann bei Austritt Grundwasser kontaminieren. Dazu kommt die Brandgefahr: Methanol bildet ab 11 °C zündfähige Dampf-Luft-Gemische (LEL 6 %). Die vorhandene Gaswarnung (GW-101) erkennt Dampf im Tankraum, jedoch keine langsame Bodenleckage.",
                "controls_einschraenkung": "Keine Doppelwand oder Leckagesonde vorhanden. GW-101 erkennt nur verdampfte Anteile. Bei schleichender Bodenleckage kann der Schaden sich über Monate aufbauen, bevor er entdeckt wird.",
            },
        ],
    },
}
