from fastapi import APIRouter, HTTPException
from typing import List, Optional
from backend.app.database.store import db_store
from backend.app.schemas.api_schemas import (
    CancelSessionRequest, CloseClassDayRequest, RescheduleQueryRequest,
    ApplyRescheduleRequest, SwapValidateRequest, SwapExecuteRequest, APIResponse
)
from backend.app.services.cancellation_service import CancellationService
from backend.app.services.rescheduling_service import ReschedulingService
from backend.app.services.swap_service import SwapService

router = APIRouter(prefix="/api/operations", tags=["Academic Operations & Workflows"])

# --- Cancellations ---
@router.post("/cancel-session", response_model=APIResponse)
def cancel_session(req: CancelSessionRequest):
    success, msg, record = CancellationService.cancel_session(req.session_id, req.reason)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return APIResponse(success=True, message=msg, data=record.model_dump())

@router.post("/close-class-day", response_model=APIResponse)
def close_class_day(req: CloseClassDayRequest):
    success, msg, record = CancellationService.close_class_day(req.class_id, req.day, req.reason)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return APIResponse(success=True, message=msg, data=record.model_dump())

@router.get("/cancellations", response_model=APIResponse)
def get_cancellations():
    return APIResponse(success=True, message="Cancellations history", data=[c.model_dump() for c in db_store.cancellations])

# --- Rescheduling ---
@router.post("/reschedule/find-slots", response_model=APIResponse)
def find_reschedule_slots(req: RescheduleQueryRequest):
    success, msg, options = ReschedulingService.find_reschedule_options(
        req.session_id, alternative_teacher_id=req.alternative_teacher_id
    )
    return APIResponse(success=success, message=msg, data={"options": options})

@router.post("/reschedule/apply", response_model=APIResponse)
def apply_reschedule(req: ApplyRescheduleRequest):
    success, msg, proposal = ReschedulingService.apply_reschedule(
        session_id=req.session_id,
        target_day=req.target_day,
        target_period=req.target_period,
        target_room_id=req.target_room_id,
        target_teacher_id=req.target_teacher_id,
        reason=req.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return APIResponse(success=True, message=msg, data=proposal.model_dump())

@router.get("/reschedule/proposals", response_model=APIResponse)
def get_reschedule_proposals():
    return APIResponse(success=True, message="Rescheduling proposals", data=[p.model_dump() for p in db_store.rescheduling_proposals])

# --- Swaps ---
@router.post("/swap/validate", response_model=APIResponse)
def validate_swap(req: SwapValidateRequest):
    is_valid, msg, violations = SwapService.validate_swap(req.session_1_id, req.session_2_id)
    return APIResponse(success=is_valid, message=msg, data={"is_valid": is_valid, "violations": violations})

@router.post("/swap/execute", response_model=APIResponse)
def execute_swap(req: SwapExecuteRequest):
    success, msg, swap_req = SwapService.execute_swap(
        session_1_id=req.session_1_id,
        session_2_id=req.session_2_id,
        requester_teacher_id=req.requester_teacher_id,
        reason=req.reason
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return APIResponse(success=True, message=msg, data=swap_req.model_dump())

@router.get("/swaps", response_model=APIResponse)
def get_swaps():
    return APIResponse(success=True, message="Teacher swap requests", data=[s.model_dump() for s in db_store.swap_requests])

# --- Notifications ---
@router.get("/notifications", response_model=APIResponse)
def get_notifications():
    return APIResponse(success=True, message="In-app notifications", data=[n.model_dump() for n in reversed(db_store.notifications)])
