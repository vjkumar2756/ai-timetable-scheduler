from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    algorithm: str = "improved_backtracking"  # "plain_backtracking", "improved_backtracking", "min_conflicts", "simulated_annealing", "hybrid"
    time_limit_seconds: float = 20.0
    random_seed: Optional[int] = 42

class ManualEditRequest(BaseModel):
    session_id: str
    target_day: str
    target_period: int
    target_room_id: Optional[str] = None
    target_teacher_id: Optional[str] = None
    apply_anyway: bool = False

class CancelSessionRequest(BaseModel):
    session_id: str
    reason: str = "Unavoidable emergency / faculty leave"

class CloseClassDayRequest(BaseModel):
    class_id: str
    day: str
    reason: str = "Department event or holiday"

class RescheduleQueryRequest(BaseModel):
    session_id: str
    alternative_teacher_id: Optional[str] = None

class ApplyRescheduleRequest(BaseModel):
    session_id: str
    target_day: str
    target_period: int
    target_room_id: str
    target_teacher_id: str
    reason: str = "Missed lecture rescheduled"

class SwapValidateRequest(BaseModel):
    session_1_id: str
    session_2_id: str

class SwapExecuteRequest(BaseModel):
    session_1_id: str
    session_2_id: str
    requester_teacher_id: str
    reason: str = "Teacher mutually agreed swap"

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, Any]]] = None
