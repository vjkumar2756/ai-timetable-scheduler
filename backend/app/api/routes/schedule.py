from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from backend.app.database.store import db_store
from backend.app.schemas.api_schemas import GenerateRequest, ManualEditRequest, APIResponse
from backend.app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/api/schedule", tags=["Timetable & Scheduling"])

def enrich_session(sess) -> dict:
    cls = db_store.classes.get(sess.class_id)
    sub = db_store.subjects.get(sess.subject_id)
    teacher = db_store.teachers.get(sess.teacher_id)
    room = db_store.rooms.get(sess.room_id)
    return {
        **sess.model_dump(),
        "class_name": cls.name if cls else sess.class_id,
        "subject_code": sub.code if sub else sess.subject_id,
        "subject_name": sub.name if sub else sess.subject_id,
        "subject_type": sub.type if sub else "theory",
        "teacher_name": teacher.name if teacher else sess.teacher_id,
        "room_name": room.name if room else sess.room_id,
        "room_type": room.type if room else "classroom"
    }

@router.post("/generate", response_model=APIResponse)
def generate_schedule(req: GenerateRequest):
    result = ScheduleService.generate_timetable(
        algorithm=req.algorithm,
        time_limit_seconds=req.time_limit_seconds,
        random_seed=req.random_seed
    )
    if not result.success:
        return APIResponse(
            success=False,
            message=result.diagnostic_message or "Timetable generation failed",
            data=result.to_dict()
        )
    return APIResponse(
        success=True,
        message=f"Timetable generated successfully using {result.algorithm}",
        data={
            **result.to_dict(),
            "sessions": [enrich_session(s) for s in db_store.sessions.values()],
            "classes": [c.model_dump() for c in db_store.classes.values()],
            "teachers": [t.model_dump() for t in db_store.teachers.values()],
            "rooms": [r.model_dump() for r in db_store.rooms.values()],
            "subjects": [s.model_dump() for s in db_store.subjects.values()],
            "settings": db_store.settings.model_dump() if db_store.settings else {}
        }
    )

@router.get("", response_model=APIResponse)
def get_current_schedule(
    class_id: Optional[str] = None,
    teacher_id: Optional[str] = None,
    room_id: Optional[str] = None,
    day: Optional[str] = None
):
    sessions = list(db_store.sessions.values())
    if class_id:
        sessions = [s for s in sessions if s.class_id == class_id]
    if teacher_id:
        sessions = [s for s in sessions if s.teacher_id == teacher_id]
    if room_id:
        sessions = [s for s in sessions if s.room_id == room_id]
    if day:
        sessions = [s for s in sessions if s.day == day]

    return APIResponse(
        success=True,
        message="Current timetable sessions",
        data={
            "metadata": db_store.current_schedule_metadata,
            "total_sessions": len(sessions),
            "sessions": [enrich_session(s) for s in sessions],
            "classes": [c.model_dump() for c in db_store.classes.values()],
            "teachers": [t.model_dump() for t in db_store.teachers.values()],
            "rooms": [r.model_dump() for r in db_store.rooms.values()],
            "subjects": [s.model_dump() for s in db_store.subjects.values()],
            "settings": db_store.settings.model_dump() if db_store.settings else {}
        }
    )

@router.post("/validate-edit", response_model=APIResponse)
def validate_manual_edit(req: ManualEditRequest):
    is_valid, violations, hard_count, soft_pen, total_cost = ScheduleService.validate_manual_edit(
        session_id=req.session_id,
        target_day=req.target_day,
        target_period=req.target_period,
        target_room_id=req.target_room_id,
        target_teacher_id=req.target_teacher_id
    )
    return APIResponse(
        success=is_valid,
        message="Move is clash-free and satisfies all 9 hard constraints" if is_valid else f"Move violates {hard_count} hard constraint(s)",
        data={
            "is_valid": is_valid,
            "violations": violations,
            "hard_violations_count": hard_count,
            "soft_penalty": soft_pen,
            "total_cost": total_cost
        }
    )

@router.post("/manual-edit", response_model=APIResponse)
@router.patch("/sessions/{session_id}", response_model=APIResponse)
def apply_manual_edit(req: ManualEditRequest, session_id: Optional[str] = None):
    target_sid = session_id or req.session_id
    success, msg, violations = ScheduleService.apply_manual_edit(
        session_id=target_sid,
        target_day=req.target_day,
        target_period=req.target_period,
        target_room_id=req.target_room_id,
        target_teacher_id=req.target_teacher_id,
        apply_anyway=req.apply_anyway
    )
    if not success:
        return APIResponse(
            success=False,
            message=msg,
            data={"violations": violations}
        )
    
    updated_sess = db_store.sessions[target_sid]
    return APIResponse(
        success=True,
        message=msg,
        data={
            "session": enrich_session(updated_sess),
            "violations": violations
        }
    )
