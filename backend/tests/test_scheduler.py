from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from .database import get_connection


def export_project_schedule_to_excel(project_id: str) -> str:
    conn = get_connection()
    activities = conn.execute(
        "SELECT * FROM activities WHERE project_id = ? ORDER BY code",
        (project_id,),
    ).fetchall()
    conn.close()

    export_dir = Path(__file__).resolve().parent.parent / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    file_path = export_dir / f"{project_id}_schedule.xlsx"

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Schedule"
    sheet.append([
        "Activity ID",
        "Activity Name",
        "Duration (days)",
        "Status",
        "Percent Complete",
        "Planned Start",
        "Planned Finish",
    ])

    for activity in activities:
        sheet.append([
            activity["code"],
            activity["name"],
            activity["duration_days"],
            activity["status"],
            activity["percent_complete"],
            activity["planned_start"],
            activity["planned_finish"],
        ])

    workbook.save(file_path)
    return str(file_path)
