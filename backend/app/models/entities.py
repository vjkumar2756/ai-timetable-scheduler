from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class Subject(BaseModel):
    id: str
    code: str
    name: str
    weekly_hours: int
    type: str = "theory"  # "theory" or "lab"
    lab_duration: int = 1  # For labs: typically 2 (consecutive periods); for theory: 1

class Teacher(BaseModel):
    id: str
    name: str
    subject_ids: List[str] = Field(default_factory=list)
    unavailable_slots: List[Dict[str, Any]] = Field(default_factory=list)  # [{"day": "Mon", "period": 1}]
    max_weekly_load: int = 20
    preferred_slots: List[Dict[str, Any]] = Field(default_factory=list)  # Soft preference [{"day": "Tue", "period": 2}]
    active: bool = True

class ClassBatch(BaseModel):
    id: str
    name: str
    strength: int
    subject_requirements: Dict[str, int] = Field(default_factory=dict)  # subject_id -> weekly_hours
    lunch_break_period: int = 4  # 1-indexed period number reserved for lunch
    active: bool = True

class Room(BaseModel):
    id: str
    name: str
    capacity: int
    type: str = "classroom"  # "classroom" or "lab"
    active: bool = True

class WorkingSettings(BaseModel):
    days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    periods_per_day: int = 6
    default_lunch_period: int = 4

class TimetableSession(BaseModel):
    id: str
    class_id: str
    subject_id: str
    teacher_id: str
    room_id: str
    day: str
    period: int  # 1-indexed starting period
    duration: int = 1  # 1 for 1 hour, 2 for 2-hour lab
    status: str = "scheduled"  # "scheduled", "cancelled", "rescheduled"
    original_slot: Optional[Dict[str, Any]] = None  # To retain history if rescheduled

class CancellationRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    scope: str = "session"  # "session" or "full_class_day"
    class_id: Optional[str] = None
    session_id: Optional[str] = None
    day: Optional[str] = None
    period: Optional[int] = None
    reason: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    affected_session_ids: List[str] = Field(default_factory=list)

class ReschedulingProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    missed_session_id: str
    proposed_teacher_id: str
    proposed_room_id: str
    proposed_day: str
    proposed_period: int
    status: str = "pending"  # "pending", "approved", "rejected"
    reason: str = "Rescheduling missed class"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class SwapRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    requester_teacher_id: str
    session_1_id: str
    session_2_id: str
    target_teacher_id: str
    status: str = "pending"  # "pending", "approved", "rejected"
    reason: str = "Schedule clash or personal preference"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class InAppNotification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    recipient: str  # Teacher ID, Class ID, or "ALL"
    title: str
    message: str
    category: str = "cancellation"  # "cancellation", "reschedule", "swap", "system"
    read: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
