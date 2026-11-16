"""
tests/test_phase2_foundation.py
Comprehensive verification test for Phase 2:
1. Pydantic schema validation
2. SQLAlchemy DB tables creation
3. Pure Python feasibility check engine on Small and Large datasets
"""
import os
import json
import pytest
from sqlalchemy import create_engine
from backend.app.database import Base
from backend.app.models.db_models import (
    SubjectModel, TeacherModel, ClassGroupModel, RoomModel,
    TimeConfigModel, TimetableModel, SessionModel
)
from backend.app.schemas import (
    SubjectCreate, TeacherCreate, ClassGroupCreate, RoomCreate,
    GenerateRequest, APIResponse
)
from core.feasibility import feasibility_check

def test_pydantic_schemas():
    """Verify Pydantic schemas validate correctly."""
    subj = SubjectCreate(id="CS101", code="CS101", name="AI Principles", weekly_hours=3, type="theory")
    assert subj.code == "CS101"
    assert subj.type == "theory"

    teacher = TeacherCreate(
        id="T1", name="Dr. Turing",
        subject_ids=["CS101"],
        unavailable_slots=[{"day": "Mon", "period": 1}],
        max_weekly_load=15
    )
    assert len(teacher.unavailable_slots) == 1
    assert teacher.unavailable_slots[0].day == "Mon"

    room = RoomCreate(id="R101", name="Lecture Hall 1", capacity=60, type="classroom")
    assert room.capacity == 60

    req = GenerateRequest(algorithm="improved_backtracking", time_limit_seconds=25.0)
    assert req.use_mrv is True

    envelope = APIResponse[dict](success=True, data={"status": "ok"})
    assert envelope.success is True
    assert envelope.data["status"] == "ok"

def test_database_table_creation(tmp_path):
    """Verify SQLAlchemy creates all tables without error in SQLite."""
    db_file = tmp_path / "test.db"
    test_engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(bind=test_engine)

    # Check table names
    table_names = Base.metadata.tables.keys()
    assert "subjects" in table_names
    assert "teachers" in table_names
    assert "class_groups" in table_names
    assert "rooms" in table_names
    assert "timetables" in table_names
    assert "timetable_sessions" in table_names
    assert "cancellations" in table_names
    assert "swap_requests" in table_names
    assert "notifications" in table_names

def test_small_dataset_feasibility():
    """Verify Small dataset passes comprehensive mathematical feasibility."""
    with open("data/small_dataset.json", "r") as f:
        data = json.load(f)
    report = feasibility_check(data)
    assert report["feasible"] is True, f"Small dataset infeasible: {report['errors']}"
    assert report["errors"] == []
    assert report["metrics"]["num_classes"] == 3
    assert report["metrics"]["num_teachers"] == 6
    assert report["metrics"]["num_rooms"] == 4
    assert report["metrics"]["total_required_hours"] == 42
    assert report["metrics"]["room_utilization_pct"] < 60.0

def test_large_dataset_feasibility():
    """Verify Large dataset passes comprehensive mathematical feasibility."""
    with open("data/large_dataset.json", "r") as f:
        data = json.load(f)
    report = feasibility_check(data)
    assert report["feasible"] is True, f"Large dataset infeasible: {report['errors']}"
    assert report["errors"] == []
    assert report["metrics"]["num_classes"] == 8
    assert report["metrics"]["num_teachers"] == 16
    assert report["metrics"]["num_rooms"] == 8
    assert report["metrics"]["total_required_hours"] == 112
    assert report["metrics"]["room_utilization_pct"] < 60.0
