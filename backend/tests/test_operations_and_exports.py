import pytest
import json
import os
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room, TimetableSession
from backend.app.database.store import db_store
from backend.app.services.schedule_service import ScheduleService
from backend.app.services.swap_service import SwapService
from backend.app.services.cancellation_service import CancellationService
from backend.app.services.io_service import IOService
from backend.app.scheduler.cross_check import PythonConstraintChecker

@pytest.fixture(autouse=True)
def setup_dataset():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    with open(os.path.join(base_dir, "datasets/small_dataset.json")) as f:
        data = json.load(f)
    db_store.load_from_dict(data)
    # Generate schedule
    ScheduleService.generate_timetable(algorithm="hybrid", time_limit_seconds=10, random_seed=42)

def test_swap_service_validation():
    sessions = list(db_store.sessions.values())
    assert len(sessions) >= 2
    s1 = sessions[0]
    s2 = sessions[1]
    
    # Validation should succeed or fail without exception
    is_valid, msg, violations = SwapService.validate_swap(s1.id, s2.id)
    assert isinstance(is_valid, bool)
    assert isinstance(msg, str)

def test_cancellation_service():
    sessions = list(db_store.sessions.values())
    s1 = sessions[0]
    initial_status = s1.status
    
    success, msg, record = CancellationService.cancel_session(s1.id, "Faculty Leave")
    assert success
    assert s1.status == "cancelled"
    assert record.session_id == s1.id

def test_excel_and_pdf_exports():
    excel_bytes = IOService.export_timetable_excel()
    assert len(excel_bytes) > 1000
    pdf_bytes = IOService.export_timetable_pdf()
    assert len(pdf_bytes) > 1000

def test_python_constraint_checker():
    is_consistent, msg, details = PythonConstraintChecker.verify_schedule_with_cross_check()
    assert is_consistent
    assert details["checked_sessions"] > 0
