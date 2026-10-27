from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.app.database.store import db_store
from backend.app.models.entities import Teacher, ClassBatch, Subject, Room, WorkingSettings
from backend.app.schemas.api_schemas import APIResponse

router = APIRouter(prefix="/api", tags=["Entities Management"])

# --- Settings ---
@router.get("/settings", response_model=APIResponse)
def get_settings():
    return APIResponse(success=True, message="Working settings", data=db_store.settings.model_dump())

@router.put("/settings", response_model=APIResponse)
def update_settings(settings: WorkingSettings):
    db_store.settings = settings
    return APIResponse(success=True, message="Working settings updated", data=db_store.settings.model_dump())

# --- Teachers ---
@router.get("/teachers", response_model=APIResponse)
def get_teachers():
    return APIResponse(success=True, message="Teachers list", data=[t.model_dump() for t in db_store.teachers.values()])

@router.post("/teachers", response_model=APIResponse)
def create_teacher(teacher: Teacher):
    if teacher.id in db_store.teachers:
        raise HTTPException(status_code=400, detail=f"Teacher ID '{teacher.id}' already exists")
    db_store.teachers[teacher.id] = teacher
    return APIResponse(success=True, message="Teacher created successfully", data=teacher.model_dump())

@router.put("/teachers/{teacher_id}", response_model=APIResponse)
def update_teacher(teacher_id: str, teacher: Teacher):
    if teacher_id not in db_store.teachers:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher.id = teacher_id
    db_store.teachers[teacher_id] = teacher
    return APIResponse(success=True, message="Teacher updated successfully", data=teacher.model_dump())

@router.delete("/teachers/{teacher_id}", response_model=APIResponse)
def delete_or_deactivate_teacher(teacher_id: str):
    if teacher_id not in db_store.teachers:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db_store.teachers[teacher_id].active = False
    return APIResponse(success=True, message="Teacher deactivated")

# --- Classes ---
@router.get("/classes", response_model=APIResponse)
def get_classes():
    return APIResponse(success=True, message="Classes list", data=[c.model_dump() for c in db_store.classes.values()])

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
    return APIResponse(success=True, message="Class updated successfully", data=cls.model_dump())

# --- Subjects ---
@router.get("/subjects", response_model=APIResponse)
def get_subjects():
    return APIResponse(success=True, message="Subjects list", data=[s.model_dump() for s in db_store.subjects.values()])

@router.post("/subjects", response_model=APIResponse)
def create_subject(sub: Subject):
    if sub.id in db_store.subjects:
        raise HTTPException(status_code=400, detail=f"Subject ID '{sub.id}' already exists")
    db_store.subjects[sub.id] = sub
    return APIResponse(success=True, message="Subject created successfully", data=sub.model_dump())

# --- Rooms ---
@router.get("/rooms", response_model=APIResponse)
def get_rooms():
    return APIResponse(success=True, message="Rooms list", data=[r.model_dump() for r in db_store.rooms.values()])

@router.post("/rooms", response_model=APIResponse)
def create_room(room: Room):
    if room.id in db_store.rooms:
        raise HTTPException(status_code=400, detail=f"Room ID '{room.id}' already exists")
    db_store.rooms[room.id] = room
    return APIResponse(success=True, message="Room created successfully", data=room.model_dump())
