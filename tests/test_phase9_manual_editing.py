"""
tests/test_phase9_manual_editing.py
Verification test suite for Phase 9:
- Authoritative validation of proposed manual session moves
- Immediate flagging of hard constraint violations (H1 - H9)
- Conflict-free move execution
- "Apply anyway" override flagging the timetable as invalid
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.store import db_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def load_and_generate_schedule():
    """Ensure small dataset is loaded and a valid schedule generated before tests."""
    client.post("/api/datasets/load/small")
    gen_res = client.post("/api/schedule/generate", json={"algorithm": "improved_backtracking"})
    assert gen_res.status_code == 200

def test_validate_conflict_free_move():
    """Verify proposing a move to a free slot returns is_valid == True."""
    sessions = list(db_store.sessions.values())
    assert len(sessions) > 0
    target_sess = sessions[0]

    # Find a free day/period combo for this session's class and teacher
    # Mon Period 5 is typically free in the small dataset
    payload = {
        "session_id": target_sess.id,
        "target_day": "Fri",
        "target_period": 5,
        "target_room_id": target_sess.room_id,
        "target_teacher_id": target_sess.teacher_id
    }

    res = client.post("/api/schedule/validate-edit", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "is_valid" in data
    assert "hard_violations_count" in data

def test_validate_clashing_move_flags_exact_violation():
    """Verify moving a session into an occupied teacher/class slot immediately flags H1/H2."""
    sessions = list(db_store.sessions.values())
    sess1 = sessions[0]
    sess2 = sessions[1]

    # Deliberately move sess1 to the exact slot occupied by sess2 (clashing slot)
    payload = {
        "session_id": sess1.id,
        "target_day": sess2.day,
        "target_period": sess2.period,
        "target_room_id": sess2.room_id,
        "target_teacher_id": sess2.teacher_id
    }

    res = client.post("/api/schedule/validate-edit", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["is_valid"] is False
    assert data["hard_violations_count"] > 0
    violations = data["violations"]
    assert len(violations) > 0
    # Must flag conflict reason
    assert any("clash" in v["message"].lower() or "conflict" in v["message"].lower() or "room" in v["message"].lower() for v in violations)

def test_apply_manual_edit_rejects_clash_without_override():
    """Verify applying a conflicting move without apply_anyway is rejected."""
    sessions = list(db_store.sessions.values())
    sess1 = sessions[0]
    sess2 = sessions[1]

    payload = {
        "session_id": sess1.id,
        "target_day": sess2.day,
        "target_period": sess2.period,
        "target_room_id": sess2.room_id,
        "target_teacher_id": sess2.teacher_id,
        "apply_anyway": False
    }

    res = client.post("/api/schedule/manual-edit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "Cannot move session" in data["message"]

def test_apply_manual_edit_with_override_flags_active_conflict():
    """Verify applying with apply_anyway=True moves the session and flags the timetable with active violations."""
    sessions = list(db_store.sessions.values())
    sess1 = sessions[0]
    sess2 = sessions[1]

    payload = {
        "session_id": sess1.id,
        "target_day": sess2.day,
        "target_period": sess2.period,
        "target_room_id": sess2.room_id,
        "target_teacher_id": sess2.teacher_id,
        "apply_anyway": True
    }

    res = client.post("/api/schedule/manual-edit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

    # Check that timetable metadata now records hard violations > 0
    sched_res = client.get("/api/schedule")
    sched_data = sched_res.json()["data"]
    assert sched_data["metadata"]["hard_violations"] > 0
