"""
backend/app/schemas/__init__.py
Centralized exports for Pydantic validation schemas.
"""
from backend.app.schemas.common import APIResponse
from backend.app.schemas.entities import (
    TimeSlot,
    SubjectCreate, SubjectRead,
    TeacherCreate, TeacherRead,
    ClassGroupCreate, ClassGroupRead,
    RoomCreate, RoomRead,
    TimeConfigCreate, TimeConfigRead
)
from backend.app.schemas.timetable import (
    GenerateRequest, SessionRead, ManualEditRequest, ManualEditResponse,
    CancelSessionRequest, CloseClassDayRequest, RescheduleQueryRequest,
    RescheduleCandidate, ApplyRescheduleRequest, SwapValidateRequest,
    SwapExecuteRequest, TimetableRead
)
