"""
backend/app/schemas/entities.py
Pydantic v2 schemas for entity validation and data interchange.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class TimeSlot(BaseModel):
    day: str
    period: int

class SubjectCreate(BaseModel):
    id: str
    code: str
    name: str
    weekly_hours: int = 3
    type: str = "theory"  # "theory" | "lab"
    lab_duration: int = 1

class SubjectRead(SubjectCreate):
    pass

class TeacherCreate(BaseModel):
    id: str
    name: str
    subject_ids: List[str] = Field(default_factory=list)
    unavailable_slots: List[TimeSlot] = Field(default_factory=list)
    max_weekly_load: int = 20
    preferred_slots: List[TimeSlot] = Field(default_factory=list)
    active: bool = True

class TeacherRead(TeacherCreate):
    pass

class ClassGroupCreate(BaseModel):
    id: str
    name: str
    strength: int = 40
    subject_requirements: Dict[str, int] = Field(default_factory=dict)
    lunch_break_period: int = 4
    active: bool = True

class ClassGroupRead(ClassGroupCreate):
    pass

class RoomCreate(BaseModel):
    id: str
    name: str
    capacity: int = 50
    type: str = "classroom"  # "classroom" | "lab"
    active: bool = True

class RoomRead(RoomCreate):
    pass

class TimeConfigCreate(BaseModel):
    days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    periods_per_day: int = 6
    default_lunch_period: int = 4

class TimeConfigRead(TimeConfigCreate):
    id: str = "default"
