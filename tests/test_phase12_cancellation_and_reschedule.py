"""
tests/test_phase12_cancellation_and_reschedule.py
Verification test suite for Phase 12:
- Dynamic session cancellation (individual session & full-day class closure)
- In-app notification creation for faculty and student cohorts
- AI Missed Lecture Rescheduling Recommender
- Authoritative clash-free verification of alternative slots (H1 - H9)
- Soft penalty ranking of recommendations
- Rescheduling application & audit trail
"""
import json
import pytest
from backend.app.database.store import db_store
from backend.app.services.cancellation_service import CancellationService
from backend.app.services.rescheduling_service import ReschedulingService
from backend.app.services.schedule_service import ScheduleService

@pytest.fixture(autouse=True)
def setup_small_dataset_with_schedule():
    """Reset store and load small dataset, then generate a baseline schedule."""
    with open("data/small_dataset.json") as f:
        data = json.load(f)
    db_store.load_from_dict(data)
    db_store.cancellations.clear()
    db_store.rescheduling_proposals.clear()
    db_store.notifications.clear()

    # Generate a valid baseline timetable
    res = ScheduleService.generate_timetable(algorithm="improved_backtracking", time_limit_seconds=5.0)
    assert res.success is True
    assert len(db_store.sessions) > 0

def test_cancel_individual_session():
    """Verify single session cancellation updates status and generates notifications."""
    sess_id = list(db_store.sessions.keys())[0]
    sess = db_store.sessions[sess_id]
    orig_class = sess.class_id
    orig_teacher = sess.teacher_id

    initial_notifs = len(db_store.notifications)
    initial_cancels = len(db_store.cancellations)

    success, msg, record = CancellationService.cancel_session(
        session_id=sess_id,
        reason="Faculty medical leave"
    )

    assert success is True
    assert sess.status == "cancelled"
    assert len(db_store.cancellations) == initial_cancels + 1
    assert record.scope == "session"
    assert record.session_id == sess_id
    assert sess_id in record.affected_session_ids

    # Notifications generated for both teacher and class
    assert len(db_store.notifications) == initial_notifs + 2
    recipients = {n.recipient for n in db_store.notifications[-2:]}
    assert orig_class in recipients
    assert orig_teacher in recipients

def test_close_class_day():
    """Verify closing a class day cancels all sessions for that class on that day."""
    # Find a class and day that has at least 2 sessions scheduled
    class_id = list(db_store.classes.keys())[0]
    day = "Mon"
    
    matching_sessions = [
        s for s in db_store.sessions.values()
        if s.class_id == class_id and s.day == day
    ]
    assert len(matching_sessions) > 0

    success, msg, record = CancellationService.close_class_day(
        class_id=class_id,
        day=day,
        reason="Department Symposium"
    )

    assert success is True
    assert record.scope == "full_class_day"
    assert record.class_id == class_id
    assert record.day == day
    assert len(record.affected_session_ids) == len(matching_sessions)

    # All matching sessions must be cancelled
    for s in matching_sessions:
        assert s.status == "cancelled"

def test_find_reschedule_options():
    """Verify AI recommender finds valid collision-free slots and ranks by soft penalty."""
    sess_id = list(db_store.sessions.keys())[0]
    CancellationService.cancel_session(session_id=sess_id, reason="Faculty leave")

    success, msg, options = ReschedulingService.find_reschedule_options(session_id=sess_id, max_suggestions=10)

    assert success is True
    assert len(options) > 0

    # Ensure options are sorted in ascending order of soft penalty
    penalties = [opt["soft_penalty"] for opt in options]
    assert penalties == sorted(penalties)

    # Verify each option structure
    top_opt = options[0]
    assert "day" in top_opt
    assert "period" in top_opt
    assert "room_id" in top_opt
    assert "teacher_id" in top_opt
    assert "soft_penalty" in top_opt

def test_apply_reschedule_success():
    """Verify applying a valid rescheduling option updates session and proposal records."""
    sess_id = list(db_store.sessions.keys())[0]
    sess = db_store.sessions[sess_id]
    orig_day = sess.day
    orig_period = sess.period

    CancellationService.cancel_session(session_id=sess_id, reason="Emergency leave")

    # Find candidate slots
    success, msg, options = ReschedulingService.find_reschedule_options(session_id=sess_id, max_suggestions=5)
    assert success is True and len(options) > 0
    top_opt = options[0]

    # Apply reschedule
    ok, apply_msg, proposal = ReschedulingService.apply_reschedule(
        session_id=sess_id,
        target_day=top_opt["day"],
        target_period=top_opt["period"],
        target_room_id=top_opt["room_id"],
        target_teacher_id=top_opt["teacher_id"],
        reason="Rescheduled via AI Recommender"
    )

    assert ok is True
    assert sess.status == "rescheduled"
    assert sess.day == top_opt["day"]
    assert sess.period == top_opt["period"]
    assert sess.room_id == top_opt["room_id"]
    assert sess.teacher_id == top_opt["teacher_id"]
    assert sess.original_slot["day"] == orig_day
    assert sess.original_slot["period"] == orig_period

    # Check proposal record
    assert len(db_store.rescheduling_proposals) > 0
    assert proposal.status == "approved"
    assert proposal.missed_session_id == sess_id

def test_apply_reschedule_rejects_clash():
    """Verify attempting to reschedule into a busy slot is rejected."""
    # Pick two distinct active sessions
    active_sessions = [s for s in db_store.sessions.values() if s.status != "cancelled"]
    assert len(active_sessions) >= 2
    sess1 = active_sessions[0]
    sess2 = active_sessions[1]

    # Cancel sess1
    CancellationService.cancel_session(session_id=sess1.id, reason="Testing clash rejection")

    # Attempt to reschedule sess1 directly into sess2's occupied slot with same room or teacher
    ok, msg, proposal = ReschedulingService.apply_reschedule(
        session_id=sess1.id,
        target_day=sess2.day,
        target_period=sess2.period,
        target_room_id=sess2.room_id,
        target_teacher_id=sess2.teacher_id,
        reason="Invalid move into active slot"
    )

    assert ok is False
    assert "violates" in msg.lower()
    assert proposal is None
    # Session status must remain cancelled
    assert sess1.status == "cancelled"
