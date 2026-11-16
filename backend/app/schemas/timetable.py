"""
backend/app/schemas/timetable.py
Pydantic schemas for timetable generation, manual editing, and operations.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    algorithm: str = "improved_backtracking"
    time_limit_seconds: float = 30.0
    random_seed: Optional[int] = 42
    # Heuristic toggles for Improved Backtracking
    use_mrv: bool = True
    use_degree: bool = True
    use_forward_checking: bool = True
    use_lcv: bool = False
    use_ac3: bool = False

class SessionRead(BaseModel):
    id: str
    timetable_id: Optional[str] = None
    class_id: str
    subject_id: str
    teacher_id: str
    room_id: str
    day: str
    period: int
    duration: int = 1
    status: str = "scheduled"
    original_slot: Optional[Dict[str, Any]] = None

class ManualEditRequest(BaseModel):
    session_id: str
    target_day: str
    target_period: int
    target_room_id: Optional[str] = None
    target_teacher_id: Optional[str] = None
    apply_anyway: bool = False  # If True, saves even with hard conflicts flagged

class ManualEditResponse(BaseModel):
    valid: bool
    violations: List[str]
    soft_penalties: List[str]
    total_cost: int
    updated_session: Optional[SessionRead] = None

class CancelSessionRequest(BaseModel):
    session_id: str
    reason: str = "Faculty emergency / sick leave"

class CloseClassDayRequest(BaseModel):
    class_id: str
    day: str
    reason: str = "Institutional event / holiday"

class RescheduleQueryRequest(BaseModel):
    session_id: str
    preferred_teacher_id: Optional[str] = None

class RescheduleCandidate(BaseModel):
    day: str
    period: int
    room_id: str
    room_name: str
    teacher_id: str
    teacher_name: str
    hard_violations_count: int
    soft_penalty: int
    explanation: str

class ApplyRescheduleRequest(BaseModel):
    session_id: str
    target_day: str
    target_period: int
    target_room_id: str
    target_teacher_id: str
    reason: str = "Rescheduled missed lecture"

class SwapValidateRequest(BaseModel):
    session_1_id: str
    session_2_id: str

class SwapExecuteRequest(BaseModel):
    session_1_id: str
    session_2_id: str
    requester_teacher_id: Optional[str] = None
    reason: str = "Mutual faculty swap"

class TimetableRead(BaseModel):
    id: str
    version: int
    algorithm: str
    seed: int
    runtime_seconds: float
    nodes_expanded: int
    hard_violations: int
    soft_penalty: int
    total_cost: int
    is_active: bool
    cost_history: List[int] = Field(default_factory=list)
    sessions: List[SessionRead] = Field(default_factory=list)
