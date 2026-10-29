"""
backend/app/api/routes/io_routes.py
REST API endpoints for preset dataset loading, JSON import/export, and multi-format reports.
"""
import os
import json
from fastapi import APIRouter, Response, HTTPException, Body
from backend.app.schemas.api_schemas import APIResponse
from backend.app.services.io_service import IOService
from backend.app.database.store import db_store
from core.feasibility import feasibility_check

router = APIRouter(prefix="/api", tags=["Import / Export & Datasets"])

@router.get("/io/export", response_model=APIResponse)
@router.get("/export", response_model=APIResponse)
def export_dataset_json():
    """Export complete institutional entities and current schedule configuration as JSON."""
    return APIResponse(
        success=True,
        message="Active dataset exported successfully",
        data=db_store.to_dict()
    )

@router.post("/io/import", response_model=APIResponse)
@router.post("/import", response_model=APIResponse)
def import_dataset_json(payload: dict = Body(...)):
    """
    Import institutional entities from JSON payload with schema & feasibility validation.
    Performs immediate solvability precheck and reports errors if unfeasible.
    """
    # 1. Structural schema verification
    required_sections = ["subjects", "teachers", "classes", "rooms"]
    missing = [sec for sec in required_sections if sec not in payload or not isinstance(payload[sec], list)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid schema: Missing or non-list section(s): {', '.join(missing)}"
        )

    # 2. Solvability precheck
    feasibility = feasibility_check(payload)
    if not feasibility["feasible"]:
        return APIResponse(
            success=False,
            message=f"Import rejected: Dataset is mathematically infeasible ({len(feasibility['errors'])} errors).",
            data=feasibility,
            errors=[{"error": e} for e in feasibility["errors"]]
        )

    # 3. Load into store
    db_store.load_from_dict(payload)
    return APIResponse(
        success=True,
        message=(
            f"Dataset successfully imported: {len(db_store.classes)} classes, "
            f"{len(db_store.teachers)} teachers, {len(db_store.rooms)} rooms. "
            "Feasibility check PASSED."
        ),
        data={
            "classes": len(db_store.classes),
            "teachers": len(db_store.teachers),
            "subjects": len(db_store.subjects),
            "rooms": len(db_store.rooms),
            "feasibility": feasibility["metrics"]
        }
    )

@router.post("/datasets/load/{dataset_name}", response_model=APIResponse)
@router.post("/io/load-dataset/{dataset_name}", response_model=APIResponse)
def load_preset_dataset(dataset_name: str):
    """
    Load official preset benchmark datasets:
    - 'small': 3 classes, 6 teachers, 4 rooms (5 days x 6 periods)
    - 'large': 8 classes, 16 teachers, 8 rooms (5 days x 7 periods)
    """
    name = dataset_name.lower().strip()
    
    # Locate dataset files in data/ or datasets/ directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../../"))
    
    candidates = [
        os.path.join(root_dir, "data"),
        os.path.join(root_dir, "datasets"),
    ]
    
    filename = "small_dataset.json" if "small" in name else "large_dataset.json" if "large" in name else None
    if not filename:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown preset dataset '{dataset_name}'. Allowed: 'small', 'large'"
        )

    filepath = None
    for c_dir in candidates:
        candidate_path = os.path.join(c_dir, filename)
        if os.path.exists(candidate_path):
            filepath = candidate_path
            break

    if not filepath:
        raise HTTPException(status_code=500, detail=f"Preset dataset file '{filename}' not found.")

    with open(filepath, "r") as f:
        data = json.load(f)

    # Validate feasibility
    feasibility = feasibility_check(data)
    db_store.load_from_dict(data)

    return APIResponse(
        success=True,
        message=f"Preset dataset '{dataset_name}' successfully loaded into active memory.",
        data={
            "dataset": dataset_name,
            "classes": len(db_store.classes),
            "teachers": len(db_store.teachers),
            "subjects": len(db_store.subjects),
            "rooms": len(db_store.rooms),
            "feasibility": feasibility["metrics"]
        }
    )

@router.get("/io/export-csv")
@router.get("/export/csv")
def export_timetable_csv():
    csv_content = IOService.export_timetable_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=schedulai_timetable.csv"}
    )

@router.get("/io/export-excel")
@router.get("/export/excel")
def export_timetable_excel():
    excel_bytes = IOService.export_timetable_excel()
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=schedulai_timetable.xlsx"}
    )

@router.get("/io/export-pdf")
@router.get("/export/pdf")
def export_timetable_pdf():
    pdf_bytes = IOService.export_timetable_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=schedulai_timetable.pdf"}
    )
