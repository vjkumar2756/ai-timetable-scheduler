import pytest
import json
import os
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room, TimetableSession
from backend.app.services.schedule_service import ScheduleService
from backend.app.services.swap_service import SwapService
from backend.app.database.store import db_store

@pytest.fixture(autouse=True)
def load_small_dataset():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    with open(os.path.join(base_dir, "datasets/small_dataset.json")) as f:
        data = json.load(f)
    db_store.load_from_dict(data)
    # Generate schedule
    res = ScheduleService.generate_timetable(algorithm="improved_backtracking", time_limit_seconds=10, random_seed=42)
    assert res.success
    assert len(db_store.sessions) > 0

def test_manual_edit_lunch_violation():
    """Dropping a session into lunch break period must be strictly rejected with H9 violation."""
    session_id = list(db_store.sessions.keys())[0]
    sess = db_store.sessions[session_id]
    cls = db_store.classes[sess.class_id]
    lunch_p = cls.lunch_break_period

    # Attempt to move to lunch slot
    is_valid, viols = ScheduleService.validate_manual_edit(
        session_id=session_id,
        target_day="Mon",
        target_period=lunch_p,
        target_room_id=sess.room_id,
        target_teacher_id=sess.teacher_id
    )
    assert not is_valid
    assert any(v["code"] == "H9" for v in viols)

    # Attempting to apply must fail
    success, msg = ScheduleService.apply_manual_edit(
        session_id=session_id,
        target_day="Mon",
        target_period=lunch_p,
        target_room_id=sess.room_id,
        target_teacher_id=sess.teacher_id
    )
    assert not success
    assert "hard constraint violations" in msg

def test_manual_edit_valid_move():
    """Moving a session to a completely free slot must succeed and update session state."""
    # Find a free slot for a theory session
    theory_sessions = [s for s in db_store.sessions.values() if s.duration == 1]
    assert len(theory_sessions) > 0
    target_session = theory_sessions[0]

    # Find a day and period where no session exists for this class, room, or teacher
    days = db_store.settings.days
    periods = range(1, db_store.settings.periods_per_day + 1)
    
    found_valid = False
    valid_day = None
    valid_period = None

    for d in days:
        for p in periods:
            if p == db_store.classes[target_session.class_id].lunch_break_period:
                continue
            is_valid, viols = ScheduleService.validate_manual_edit(
                session_id=target_session.id,
                target_day=d,
                target_period=p,
                target_room_id=target_session.room_id,
                target_teacher_id=target_session.teacher_id
            )
            if is_valid:
                found_valid = True
                valid_day = d
                valid_period = p
                break
        if found_valid:
            break

    assert found_valid, "Should find at least one valid slot in small dataset"

    # Apply edit
    success, msg = ScheduleService.apply_manual_edit(
        session_id=target_session.id,
        target_day=valid_day,
        target_period=valid_period,
        target_room_id=target_session.room_id,
        target_teacher_id=target_session.teacher_id
    )
    assert success
    assert db_store.sessions[target_session.id].day == valid_day
    assert db_store.sessions[target_session.id].period == valid_period

def test_swap_sessions_execution():
    """Swapping two sessions via drag-and-drop workflow must either succeed or produce clear violation reasons."""
    sessions = list(db_store.sessions.values())
    s1 = sessions[0]
    s2 = sessions[1]

    is_valid, msg, viols = SwapService.validate_swap(s1.id, s2.id)
    if is_valid:
        s1_day_orig, s1_p_orig = s1.day, s1.period
        s2_day_orig, s2_p_orig = s2.day, s2.period

        success, exec_msg, req = SwapService.execute_swap(
            session_1_id=s1.id,
            session_2_id=s2.id,
            requester_teacher_id=s1.teacher_id,
            reason="Test Drag & Drop Swap"
        )
        assert success
        assert s1.day == s2_day_orig and s1.period == s2_p_orig
        assert s2.day == s1_day_orig and s2.period == s1_p_orig
    else:
        assert len(viols) > 0 or "clash" in msg.lower()
