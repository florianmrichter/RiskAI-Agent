"""
FMEA Export -- Generate Excel and JSON reports from the FMEA database.

Usage:
    python tools/export.py <project_id> [output_path]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.storage import FMEAStorage

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


RPZ_COLORS = {
    "kritisch": "FF0000",
    "hoch": "FF8C00",
    "mittel": "FFD700",
    "niedrig": "00B050",
}


def export_json(project_id: int, output_path: str, db_path: str = None) -> str:
    """Export full FMEA data as JSON."""
    db = FMEAStorage(db_path)
    project = db.get_project(project_id)
    data = db.get_full_fmea_data(project_id)
    stats = db.get_project_statistics(project_id)
    db.close()

    report = {
        "metadata": {
            "projekt": project["name"],
            "anlage": project["anlage_name"],
            "datum": project["datum"],
            "export_datum": datetime.now().isoformat(),
            "standard": "AIAG-VDA FMEA",
        },
        "statistik": stats,
        "fmea_data": data,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return output_path


def export_excel(project_id: int, output_path: str, db_path: str = None) -> str:
    """Export FMEA data as formatted Excel workbook."""
    if not HAS_OPENPYXL:
        raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")

    db = FMEAStorage(db_path)
    project = db.get_project(project_id)
    components = db.get_components(project_id)
    full_data = db.get_full_fmea_data(project_id)
    stats = db.get_project_statistics(project_id)
    db.close()

    wb = Workbook()

    _create_overview_sheet(wb, project, stats, components)
    _create_fmea_sheet(wb, full_data)
    _create_causes_sheet(wb, full_data)
    _create_measures_sheet(wb, full_data)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path


def _style_header(ws, row: int, max_col: int):
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )
    for col in range(1, max_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = thin_border


def _create_overview_sheet(wb, project, stats, components):
    ws = wb.active
    ws.title = "Übersicht"

    ws["A1"] = "FMEA-Report"
    ws["A1"].font = Font(bold=True, size=16)
    ws["A3"] = "Projekt:"
    ws["B3"] = project["name"]
    ws["A4"] = "Anlage:"
    ws["B4"] = project["anlage_name"] or "N/A"
    ws["A5"] = "Datum:"
    ws["B5"] = project["datum"]
    ws["A6"] = "Status:"
    ws["B6"] = project["status"]

    ws["A8"] = "Statistik"
    ws["A8"].font = Font(bold=True, size=13)
    ws["A9"] = "Komponenten:"
    ws["B9"] = stats["components"]
    ws["A10"] = "Funktionen:"
    ws["B10"] = stats["functions"]
    ws["A11"] = "Fehlermodi:"
    ws["B11"] = stats["failure_modes"]
    ws["A12"] = "Maßnahmen:"
    ws["B12"] = stats["measures"]

    row = 14
    ws.cell(row=row, column=1, value="RPZ-Verteilung").font = Font(bold=True, size=13)
    row += 1
    for status in ["kritisch", "hoch", "mittel", "niedrig"]:
        count = stats["rpz_distribution"].get(status, 0)
        ws.cell(row=row, column=1, value=status.capitalize())
        ws.cell(row=row, column=2, value=count)
        ws.cell(row=row, column=1).fill = PatternFill(
            start_color=RPZ_COLORS[status], end_color=RPZ_COLORS[status], fill_type="solid"
        )
        if status in ["kritisch", "hoch"]:
            ws.cell(row=row, column=1).font = Font(color="FFFFFF", bold=True)
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="Komponenten-Liste").font = Font(bold=True, size=13)
    row += 1
    headers = ["KOMP-ID", "Name", "Typ", "Kategorie", "System"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=row, column=i, value=h)
    _style_header(ws, row, len(headers))
    row += 1

    for comp in components:
        ws.cell(row=row, column=1, value=comp["komp_id"])
        ws.cell(row=row, column=2, value=comp["name"])
        ws.cell(row=row, column=3, value=comp["typ"])
        ws.cell(row=row, column=4, value=comp["kategorie"])
        ws.cell(row=row, column=5, value=comp["system_name"])
        row += 1

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 30


def _create_fmea_sheet(wb, full_data):
    ws = wb.create_sheet("FMEA-Analyse")

    headers = [
        "KOMP-ID", "Komponente", "System", "Typ",
        "Funktion-ID", "Funktion",
        "Fehler-ID", "Fehlermodus", "Fehlerart",
        "Mensch", "Umwelt", "Anlage", "Kosten",
        "S", "O", "D", "RPZ", "RPZ-Status",
        "Override"
    ]
    for i, h in enumerate(headers, 1):
        ws.cell(row=1, column=i, value=h)
    _style_header(ws, 1, len(headers))

    row = 2
    for entry in full_data:
        effects = entry.get("effects") or {}
        risk = entry.get("risk") or {}

        ws.cell(row=row, column=1, value=entry.get("komp_id", ""))
        ws.cell(row=row, column=2, value=entry.get("komponente", ""))
        ws.cell(row=row, column=3, value=entry.get("system_name", ""))
        ws.cell(row=row, column=4, value=entry.get("komponenten_typ", ""))
        ws.cell(row=row, column=5, value=entry.get("funktion_id", ""))
        ws.cell(row=row, column=6, value=entry.get("funktion_beschreibung", ""))
        ws.cell(row=row, column=7, value=entry.get("fehler_id", ""))
        ws.cell(row=row, column=8, value=entry.get("fehlermodus", ""))
        ws.cell(row=row, column=9, value=entry.get("fehlerart", ""))

        ws.cell(row=row, column=10, value=effects.get("mensch_beschreibung", ""))
        ws.cell(row=row, column=11, value=effects.get("umwelt_beschreibung", ""))
        ws.cell(row=row, column=12, value=effects.get("anlage_beschreibung", ""))
        ws.cell(row=row, column=13, value=effects.get("kosten_beschreibung", ""))

        S = risk.get("S", entry.get("S", ""))
        O = risk.get("O", entry.get("O", ""))
        D = risk.get("D", entry.get("D", ""))
        rpz = risk.get("rpz", entry.get("rpz", ""))
        rpz_status = risk.get("rpz_status", entry.get("rpz_status", ""))

        ws.cell(row=row, column=14, value=S)
        ws.cell(row=row, column=15, value=O)
        ws.cell(row=row, column=16, value=D)
        ws.cell(row=row, column=17, value=rpz)

        status_cell = ws.cell(row=row, column=18, value=rpz_status)
        if rpz_status in RPZ_COLORS:
            status_cell.fill = PatternFill(
                start_color=RPZ_COLORS[rpz_status],
                end_color=RPZ_COLORS[rpz_status],
                fill_type="solid"
            )
            if rpz_status in ["kritisch", "hoch"]:
                status_cell.font = Font(color="FFFFFF", bold=True)

        ws.cell(row=row, column=19, value=risk.get("override_applied", ""))
        row += 1

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["H"].width = 40


def _create_causes_sheet(wb, full_data):
    ws = wb.create_sheet("Fehlerursachen")

    headers = [
        "Fehler-ID", "Fehlermodus", "Komponente",
        "Ursache-ID", "Beschreibung", "Herkunft",
        "Präventionsphase", "Präventionshinweis"
    ]
    for i, h in enumerate(headers, 1):
        ws.cell(row=1, column=i, value=h)
    _style_header(ws, 1, len(headers))

    row = 2
    for entry in full_data:
        for cause in entry.get("causes", []):
            ws.cell(row=row, column=1, value=entry.get("fehler_id", ""))
            ws.cell(row=row, column=2, value=entry.get("fehlermodus", ""))
            ws.cell(row=row, column=3, value=entry.get("komponente", ""))
            ws.cell(row=row, column=4, value=cause.get("ursache_id", ""))
            ws.cell(row=row, column=5, value=cause.get("beschreibung", ""))
            ws.cell(row=row, column=6, value=cause.get("herkunft", ""))
            ws.cell(row=row, column=7, value=cause.get("praeventionsphase", ""))
            ws.cell(row=row, column=8, value=cause.get("praeventionshinweis", ""))
            row += 1

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 20
    ws.column_dimensions["E"].width = 50
    ws.column_dimensions["H"].width = 50


def _create_measures_sheet(wb, full_data):
    ws = wb.create_sheet("Maßnahmen")

    headers = [
        "Fehler-ID", "Fehlermodus", "Komponente",
        "RPZ vorher", "Status vorher",
        "Maßnahme", "ABE-Kategorie", "Beschreibung",
        "S neu", "O neu", "D neu", "RPZ neu", "Status neu",
        "Begründung"
    ]
    for i, h in enumerate(headers, 1):
        ws.cell(row=1, column=i, value=h)
    _style_header(ws, 1, len(headers))

    row = 2
    for entry in full_data:
        risk = entry.get("risk") or {}
        for measure in entry.get("measures", []):
            ws.cell(row=row, column=1, value=entry.get("fehler_id", ""))
            ws.cell(row=row, column=2, value=entry.get("fehlermodus", ""))
            ws.cell(row=row, column=3, value=entry.get("komponente", ""))
            ws.cell(row=row, column=4, value=risk.get("rpz", entry.get("rpz", "")))
            ws.cell(row=row, column=5, value=risk.get("rpz_status", entry.get("rpz_status", "")))
            ws.cell(row=row, column=6, value=measure.get("name", ""))
            ws.cell(row=row, column=7, value=measure.get("abe_kategorie", ""))
            ws.cell(row=row, column=8, value=measure.get("beschreibung", ""))
            ws.cell(row=row, column=9, value=measure.get("S_neu", ""))
            ws.cell(row=row, column=10, value=measure.get("O_neu", ""))
            ws.cell(row=row, column=11, value=measure.get("D_neu", ""))
            ws.cell(row=row, column=12, value=measure.get("rpz_neu", ""))

            rpz_status_neu = measure.get("rpz_status_neu", "")
            status_cell = ws.cell(row=row, column=13, value=rpz_status_neu)
            if rpz_status_neu in RPZ_COLORS:
                status_cell.fill = PatternFill(
                    start_color=RPZ_COLORS[rpz_status_neu],
                    end_color=RPZ_COLORS[rpz_status_neu],
                    fill_type="solid"
                )

            ws.cell(row=row, column=14, value=measure.get("begruendung", ""))
            row += 1

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18
    ws.column_dimensions["F"].width = 35
    ws.column_dimensions["H"].width = 50
    ws.column_dimensions["N"].width = 50


def export_fmea(project_id: int, output_path: str = None, db_path: str = None,
                format: str = "both") -> dict:
    """
    Export FMEA data. Returns dict with file paths.
    format: 'excel', 'json', or 'both'
    """
    if output_path is None:
        output_dir = Path(__file__).parent.parent / ".tmp"
        output_dir.mkdir(parents=True, exist_ok=True)
        base = f"fmea_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_path = str(output_dir / base)

    results = {}
    base = str(Path(output_path).with_suffix(""))

    if format in ("json", "both"):
        json_path = export_json(project_id, f"{base}.json", db_path)
        results["json"] = json_path

    if format in ("excel", "both"):
        excel_path = export_excel(project_id, f"{base}.xlsx", db_path)
        results["excel"] = excel_path

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/export.py <project_id> [output_path]")
        print("\nExports FMEA data as Excel (.xlsx) and JSON (.json)")
        sys.exit(1)

    pid = int(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else None
    result = export_fmea(pid, out)
    print(f"Export abgeschlossen:")
    for fmt, path in result.items():
        print(f"  {fmt}: {path}")
