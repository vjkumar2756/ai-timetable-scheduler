import os
import json
from fastapi import APIRouter, Response, HTTPException
from backend.app.schemas.api_schemas import APIResponse
from backend.app.services.io_service import IOService
from backend.app.database.store import db_store

router = APIRouter(prefix="/api/io", tags=["Import / Export & Datasets"])

@router.get("/export-csv")
def export_timetable_csv():
    csv_content = IOService.export_timetable_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=schedulai_timetable.csv"}
    )

@router.post("/import-json", response_model=APIResponse)
def import_dataset(payload: dict):
    success, msg = IOService.import_dataset_json(payload)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return APIResponse(success=True, message=msg)

@router.post("/load-dataset/{dataset_name}", response_model=APIResponse)
def load_preset_dataset(dataset_name: str):
    name = dataset_name.lower().strip()
    # Find datasets directory relative to root workspace
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 4 levels to root: routes -> api -> app -> backend -> root
    root_dir = os.path.abspath(os.path.join(current_dir, "../../../../"))
    datasets_dir = os.path.join(root_dir, "datasets")
    if not os.path.exists(datasets_dir):
        # Alternative fallback
        datasets_dir = os.path.abspath(os.path.join(current_dir, "../../../datasets"))

    if name in ["small", "small_dataset"]:
        filepath = os.path.join(datasets_dir, "small_dataset.json")
    elif name in ["large", "large_dataset"]:
        filepath = os.path.join(datasets_dir, "large_dataset.json")
    else:
        raise HTTPException(status_code=404, detail="Unknown dataset name. Choose 'small' or 'large'")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=500, detail=f"Dataset file {filepath} not found")

    with open(filepath, "r") as f:
        data = json.load(f)

    db_store.load_from_dict(data)
    return APIResponse(
        success=True,
        message=f"Preset dataset '{dataset_name}' loaded successfully into active memory",
        data={
            "classes": len(db_store.classes),
            "teachers": len(db_store.teachers),
            "subjects": len(db_store.subjects),
            "rooms": len(db_store.rooms)
        }
    )
