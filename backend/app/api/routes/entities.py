"""
backend/app/api/routes/entities.py
REST API endpoints for institutional entities CRUD and Feasibility Precheck.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from backend.app.database.store import db_store
from backend.app.models.entities import Teacher, ClassBatch, Subject, Room, WorkingSettings
from backend.app.schemas.api_schemas import APIResponse
from core.feasibility import feasibility_check

router = APIRouter(prefix="/api", tags=["Entities Management"])

# --- Institutional Solvability Feasibility Precheck ---
@router.get("/feasibility", response_model=APIResponse)
@router.post("/feasibility", response_model=APIResponse)
def get_feasibility_report(payload: Optional[dict] = None):
    """
    Runs multi-factor solvability feasibility precheck on active entities or supplied payload.
    Checks total hours vs. slots, lab room constraints, teacher load, and room capacity.
    """
    data = payload if payload else db_store.to_dict()
    report = feasibility_check(data)
    return APIResponse(
        success=report["feasible"],
        message=report["summary"],
        data=report,
        errors=[{"error": e} for e in report["errors"]] if report["errors"] else None
    )

# --- Settings ---
@router.get("/settings", response_model=APIResponse)
def get_settings():
    return APIResponse(success=True, message="Working settings", data=db_store.settings.model_dump())

@router.put("/settings", response_model=APIResponse)
def update_settings(settings: WorkingSettings):
    db_store.settings = settings
    return APIResponse(
        success=True,
        message="Working settings updated. Note: Current timetable should be regenerated.",
        data=db_store.settings.model_dump()
    )

# --- Teachers ---
@router.get("/teachers", response_model=APIResponse)
def get_teachers():
    return APIResponse(success=True, message="Teachers list", data=[t.model_dump() for t in db_store.teachers.values()])

@router.get("/teachers/{teacher_id}", response_model=APIResponse)
def get_teacher(teacher_id: str):
    if teacher_id not in db_store.teachers:
        raise HTTPException(status_code=404, detail=f"Teacher '{teacher_id}' not found")
    return APIResponse(success=True, message="Teacher details", data=db_store.teachers[teacher_id].model_dump())

@router.post("/teachers", response_model=APIResponse)
def create_teacher(teacher: Teacher):
    if teacher.id in db_store.teachers:
        raise HTTPException(status_code=400, detail=f"Teacher ID '{teacher.id}' already exists")
    db_store.teachers[teacher.id] = teacher
    return APIResponse(
        success=True,
        message="Teacher created successfully",
        data=teacher.model_dump()
    )

@router.put("/teachers/{teacher_id}", response_model=APIResponse)
def update_teacher(teacher_id: str, teacher: Teacher):
    if teacher_id not in db_store.teachers:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher.id = teacher_id
    db_store.teachers[teacher_id] = teacher
    return APIResponse(
        success=True,
        message="Teacher updated successfully. Note: Existing timetable may be outdated.",
        data=teacher.model_dump()
    )

@router.delete("/teachers/{teacher_id}", response_model=APIResponse)
def delete_teacher(teacher_id: str):
    if teacher_id not in db_store.teachers:
        raise HTTPException(status_code=404, detail="Teacher not found")
    # Soft deactivate
    db_store.teachers[teacher_id].active = False
    return APIResponse(success=True, message=f"Teacher '{teacher_id}' deactivated successfully")

# --- Classes ---
@router.get("/classes", response_model=APIResponse)
def get_classes():
    return APIResponse(success=True, message="Classes list", data=[c.model_dump() for c in db_store.classes.values()])

@router.get("/classes/{class_id}", response_model=APIResponse)
def get_class(class_id: str):
    if class_id not in db_store.classes:
        raise HTTPException(status_code=404, detail=f"Class '{class_id}' not found")
    return APIResponse(success=True, message="Class details", data=db_store.classes[class_id].model_dump())

@router.post("/classes", response_model=APIResponse)
def create_class(cls: ClassBatch):
    if cls.id in db_store.classes:
        raise HTTPException(status_code=400, detail=f"Class ID '{cls.id}' already exists")
    db_store.classes[cls.id] = cls
    return APIResponse(success=True, message="Class created successfully", data=cls.model_dump())

@router.put("/classes/{class_id}", response_model=APIResponse)
def update_class(class_id: str, cls: ClassBatch):
    if class_id not in db_store.classes:
        raise HTTPException(status_code=404, detail="Class not found")
    cls.id = class_id
    db_store.classes[class_id] = cls
    return APIResponse(
        success=True,
        message="Class updated successfully. Note: Existing timetable may be outdated.",
        data=cls.model_dump()
    )

@router.delete("/classes/{class_id}", response_model=APIResponse)
def delete_class(class_id: str):
    if class_id not in db_store.classes:
        raise HTTPException(status_code=404, detail="Class not found")
    db_store.classes[class_id].active = False
    return APIResponse(success=True, message=f"Class '{class_id}' deactivated successfully")

# --- Subjects ---
@router.get("/subjects", response_model=APIResponse)
def get_subjects():
    return APIResponse(success=True, message="Subjects list", data=[s.model_dump() for s in db_store.subjects.values()])

@router.get("/subjects/{subject_id}", response_model=APIResponse)
def get_subject(subject_id: str):
    if subject_id not in db_store.subjects:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_id}' not found")
    return APIResponse(success=True, message="Subject details", data=db_store.subjects[subject_id].model_dump())

@router.post("/subjects", response_model=APIResponse)
def create_subject(sub: Subject):
    if sub.id in db_store.subjects:
        raise HTTPException(status_code=400, detail=f"Subject ID '{sub.id}' already exists")
    db_store.subjects[sub.id] = sub
    return APIResponse(success=True, message="Subject created successfully", data=sub.model_dump())

@router.put("/subjects/{subject_id}", response_model=APIResponse)
def update_subject(subject_id: str, sub: Subject):
    if subject_id not in db_store.subjects:
        raise HTTPException(status_code=404, detail="Subject not found")
    sub.id = subject_id
    db_store.subjects[subject_id] = sub
    return APIResponse(
        success=True,
        message="Subject updated successfully. Note: Existing timetable may be outdated.",
        data=sub.model_dump()
    )

@router.delete("/subjects/{subject_id}", response_model=APIResponse)
def delete_subject(subject_id: str):
    if subject_id not in db_store.subjects:
        raise HTTPException(status_code=404, detail="Subject not found")
    del db_store.subjects[subject_id]
    return APIResponse(success=True, message=f"Subject '{subject_id}' deleted successfully")

# --- Rooms ---
@router.get("/rooms", response_model=APIResponse)
def get_rooms():
    return APIResponse(success=True, message="Rooms list", data=[r.model_dump() for r in db_store.rooms.values()])

@router.get("/rooms/{room_id}", response_model=APIResponse)
def get_room(room_id: str):
    if room_id not in db_store.rooms:
        raise HTTPException(status_code=404, detail=f"Room '{room_id}' not found")
    return APIResponse(success=True, message="Room details", data=db_store.rooms[room_id].model_dump())

@router.post("/rooms", response_model=APIResponse)
def create_room(room: Room):
    if room.id in db_store.rooms:
        raise HTTPException(status_code=400, detail=f"Room ID '{room.id}' already exists")
    db_store.rooms[room.id] = room
    return APIResponse(success=True, message="Room created successfully", data=room.model_dump())

@router.put("/rooms/{room_id}", response_model=APIResponse)
def update_room(room_id: str, room: Room):
    if room_id not in db_store.rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    room.id = room_id
    db_store.rooms[room_id] = room
    return APIResponse(
        success=True,
        message="Room updated successfully. Note: Existing timetable may be outdated.",
        data=room.model_dump()
    )

@router.delete("/rooms/{room_id}", response_model=APIResponse)
def delete_room(room_id: str):
    if room_id not in db_store.rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    db_store.rooms[room_id].active = False
    return APIResponse(success=True, message=f"Room '{room_id}' deactivated successfully")
