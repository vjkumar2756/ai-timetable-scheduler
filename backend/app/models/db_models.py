"""
backend/app/models/db_models.py
SQLAlchemy ORM models for SchedulAI database persistence.
Persists entities, timetables, sessions, operational workflows, and experiment history.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())[:8]

class SubjectModel(Base):
    __tablename__ = "subjects"
    id = Column(String(50), primary_key=True)
    code = Column(String(50), nullable=False)
    name = Column(String(150), nullable=False)
    weekly_hours = Column(Integer, nullable=False, default=3)
    type = Column(String(20), nullable=False, default="theory")  # "theory" | "lab"
    lab_duration = Column(Integer, default=1)  # 1 for theory, 2 for 2-hour lab

class TeacherModel(Base):
    __tablename__ = "teachers"
    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    subject_ids = Column(JSON, default=list)  # List[str] of subject IDs
    unavailable_slots = Column(JSON, default=list)  # List[{"day": str, "period": int}]
    max_weekly_load = Column(Integer, default=20)
    preferred_slots = Column(JSON, default=list)  # List[{"day": str, "period": int}]
    active = Column(Boolean, default=True)

class ClassGroupModel(Base):
    __tablename__ = "class_groups"
    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    strength = Column(Integer, nullable=False, default=40)
    subject_requirements = Column(JSON, default=dict)  # {"subject_id": weekly_hours}
    lunch_break_period = Column(Integer, default=4)
    active = Column(Boolean, default=True)

class RoomModel(Base):
    __tablename__ = "rooms"
    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    capacity = Column(Integer, nullable=False, default=50)
    type = Column(String(20), nullable=False, default="classroom")  # "classroom" | "lab"
    active = Column(Boolean, default=True)

class TimeConfigModel(Base):
    __tablename__ = "time_config"
    id = Column(String(50), primary_key=True, default="default")
    days = Column(JSON, default=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri"])
    periods_per_day = Column(Integer, default=6)
    default_lunch_period = Column(Integer, default=4)

class TimetableModel(Base):
    __tablename__ = "timetables"
    id = Column(String(50), primary_key=True, default=generate_uuid)
    version = Column(Integer, default=1)
    algorithm = Column(String(50), nullable=False)
    seed = Column(Integer, default=42)
    runtime_seconds = Column(Float, default=0.0)
    nodes_expanded = Column(Integer, default=0)
    hard_violations = Column(Integer, default=0)
    soft_penalty = Column(Integer, default=0)
    total_cost = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    cost_history = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("SessionModel", back_populates="timetable", cascade="all, delete-orphan")

class SessionModel(Base):
    __tablename__ = "timetable_sessions"
    id = Column(String(50), primary_key=True, default=generate_uuid)
    timetable_id = Column(String(50), ForeignKey("timetables.id"), nullable=False)
    class_id = Column(String(50), nullable=False)
    subject_id = Column(String(50), nullable=False)
    teacher_id = Column(String(50), nullable=False)
    room_id = Column(String(50), nullable=False)
    day = Column(String(10), nullable=False)
    period = Column(Integer, nullable=False)
    duration = Column(Integer, default=1)
    status = Column(String(20), default="scheduled")  # "scheduled", "cancelled", "rescheduled"
    original_slot = Column(JSON, nullable=True)

    timetable = relationship("TimetableModel", back_populates="sessions")

class CancellationModel(Base):
    __tablename__ = "cancellations"
    id = Column(String(50), primary_key=True, default=generate_uuid)
    scope = Column(String(20), default="session")  # "session" or "full_class_day"
    class_id = Column(String(50), nullable=True)
    session_id = Column(String(50), nullable=True)
    day = Column(String(10), nullable=True)
    period = Column(Integer, nullable=True)
    reason = Column(Text, default="Faculty absence")
    created_at = Column(DateTime, default=datetime.utcnow)

class SwapRequestModel(Base):
    __tablename__ = "swap_requests"
    id = Column(String(50), primary_key=True, default=generate_uuid)
    session_1_id = Column(String(50), nullable=False)
    session_2_id = Column(String(50), nullable=False)
    requester_teacher_id = Column(String(50), nullable=True)
    status = Column(String(20), default="approved")  # "pending", "approved", "rejected"
    reason = Column(Text, default="Mutual faculty agreement")
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationModel(Base):
    __tablename__ = "notifications"
    id = Column(String(50), primary_key=True, default=generate_uuid)
    type = Column(String(50), default="info")
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # "info", "warning", "error", "success"
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExperimentRecordModel(Base):
    __tablename__ = "experiment_records"
    id = Column(String(50), primary_key=True, default=generate_uuid)
    algorithm = Column(String(50), nullable=False)
    dataset_name = Column(String(50), nullable=False)
    run_index = Column(Integer, default=1)
    seed = Column(Integer, default=42)
    runtime_seconds = Column(Float, default=0.0)
    nodes_expanded = Column(Integer, default=0)
    hard_violations = Column(Integer, default=0)
    soft_penalty = Column(Integer, default=0)
    total_cost = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
