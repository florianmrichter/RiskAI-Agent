# Farbkonzept: "NexaVerse" Design-System

Datum: 2026-03-01
Status: Entwurf (Extrahiert aus NexaVerse UI Image)

## 1. Analyse der visuellen Identität (NexaVerse)

Das Dashboard-Design "NexaVerse" zeichnet sich durch einen mutigen, energiegeladenen Look aus, der eine **vibrante Primärfarbe** mit einem sehr **cleanen, hellen Content-Bereich** kombiniert.

### Kern-Farben (Extrahiert)

| Rolle | Farbe | Hex (Geschätzt) | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Primary / Brand** | ![#F5004F](https://placehold.co/15x15/F5004F/F5004F.png) **Vivid Pink/Red** | `#F5004F` | Die dominante Farbe der Sidebar und Logo-Elemente. Mutig, aktiv, modern. |
| **Primary Dark** | ![#C0003A](https://placehold.co/15x15/C0003A/C0003A.png) **Deep Rose** | `#C0003A` | Für Hover-States oder dunklere Akzente. |
| **Background** | ![#F5F6FA](https://placehold.co/15x15/F5F6FA/F5F6FA.png) **Soft Grey** | `#F5F6FA` | Sehr heller, kühler Grauton für den Hauptbereich. |
| **Surface** | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) **White** | `#FFFFFF` | Reine weiße Karten (Cards) für maximalen Kontrast. |
| **Text Primary** | ![#111827](https://placehold.co/15x15/111827/111827.png) **Deep Navy/Black**| `#111827` | Fast schwarz, hoher Kontrast für Lesbarkeit. |

### Daten-Visualisierung / Status

| Rolle | Farbe | Hex | Nutzung im Bild |
| :--- | :--- | :--- | :--- |
| **Accent 1 (Success)** | ![#00A389](https://placehold.co/15x15/00A389/00A389.png) **Teal Green** | `#00A389` | "Active Customers", positive Trends. |
| **Accent 2 (Info)** | ![#2C2C54](https://placehold.co/15x15/2C2C54/2C2C54.png) **Dark Navy** | `#2C2C54` | "Current Customers", dunkle UI-Elemente. |
| **Accent 3 (Warning)** | ![#E8C547](https://placehold.co/15x15/E8C547/E8C547.png) **Mustard Yellow**| `#E8C547` | "Churn Rate", Warnhinweise. |
| **Accent 4 (Danger)** | ![#F5004F](https://placehold.co/15x15/F5004F/F5004F.png) **Brand Red** | `#F5004F` | Negative Trends ("Churn"), kritische Fehler. |

## 2. Mapping auf RiskAI-Agent (FMEA Styles)

Um dieses Design auf unseren FMEA-Report (`fmea_style.css`) zu übertragen, schlage ich folgende Variablen-Anpassungen vor:

```css
:root {
  /* ── Primary Palette (NexaVerse) ── */
  /* Ersetzt das bisherige Standard-Blau */
  --color-primary: #F5004F;      /* Vivid Pink/Red */
  --color-primary-dark: #C0003A; /* Darker shade */
  --color-indigo: #2C2C54;       /* Dark Navy (als Sekundär-Akzent) */
  --color-secondary: #64748B;    /* Slate Gray (für Nebentexte) */

  /* ── Status Colors ── */
  --color-success: #00A389;      /* Teal statt Standard-Grün */
  --color-warning: #E8C547;      /* Muted Yellow statt Orange */
  --color-error: #F5004F;        /* Brand Color für Fehler */

  /* ── Surfaces ── */
  --color-bg: #F5F6FA;           /* Hellerer, kühlerer Hintergrund */
  --color-surface: #FFFFFF;      /* Bleibt Weiß */
  --color-border: #E2E8F0;       /* Leichterer Border */

  /* ── Risk Status (FMEA-Spezifisch) ── */
  /* Anpassung der RPZ-Ampel an das neue Schema */
  --rpz-kritisch: #F5004F;       /* Brand Red */
  --rpz-kritisch-bg: #FFF0F5;    /* Very Light Pink */
  --rpz-hoch: #FD7E14;           /* Orange (bleibt ähnlich) */
  --rpz-mittel: #E8C547;         /* Nexa Yellow */
  --rpz-niedrig: #00A389;        /* Nexa Teal */
}
```

## 3. Design-Implikationen
1.  **Header:** Sollte nun entweder weiß mit pinkem Logo/Akzenten sein ODER vollflächig Pink (`#F5004F`) mit weißem Text (wie die Sidebar im Bild).
2.  **Typografie:** Die Schriftart `Inter` passt weiterhin sehr gut. Überschriften sollten **Bold** und in `#111827` (Deep Navy) gesetzt werden.
3.  **Charts:** Die Donut-Charts und Balkendiagramme im Report müssen die neuen Farben (`#00A389`, `#2C2C54`, `#E8C547`, `#F5004F`) nutzen.

## 4. Nächste Schritte
1.  Soll ich diese Farben direkt in die `templates/fmea_style.css` übernehmen?
2.  Soll das Logo-Briefing (Prompt) angepasst werden, um explizit diese Farben (`#F5004F`, `#2C2C54`) zu nennen?
