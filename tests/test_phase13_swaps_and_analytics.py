"""
tests/test_phase13_swaps_and_analytics.py
Verification test suite for Phase 13:
- Mutual teacher lecture swap validation & execution
- Hard constraint conflict detection during swaps (H1 - H9)
- Notification generation upon approved swaps
- Faculty workload analytics (H8 compliance, utilization %, overload alerts)
- Facility & room utilization metrics
- Constraint optimization quality score (S1 - S5)
"""
import json
import pytest
from backend.app.database.store import db_store
from backend.app.services.schedule_service import ScheduleService
from backend.app.services.swap_service import SwapService
from backend.app.services.analytics_service import AnalyticsService

@pytest.fixture(autouse=True)
def setup_small_dataset_with_schedule():
    """Reset store, load small dataset, and generate a baseline schedule."""
    with open("data/small_dataset.json") as f:
        data = json.load(f)
    db_store.load_from_dict(data)
    db_store.swap_requests.clear()
    db_store.notifications.clear()

    res = ScheduleService.generate_timetable(algorithm="improved_backtracking", time_limit_seconds=5.0)
    assert res.success is True
    assert len(db_store.sessions) > 0

def test_swap_validation_and_differing_durations():
    """Verify swap validation enforces equal session duration and constraint checks."""
    active_sessions = list(db_store.sessions.values())
    
    # Find a 1-hour session and a 2-hour lab session (if any)
    one_hr = [s for s in active_sessions if s.duration == 1]
    two_hr = [s for s in active_sessions if s.duration == 2]

    if one_hr and two_hr:
        is_valid, msg, violations = SwapService.validate_swap(one_hr[0].id, two_hr[0].id)
        assert is_valid is False
        assert "differing durations" in msg.lower()

def test_swap_execution_success():
    """Verify executing a valid swap exchanges time slots and records swap request."""
    # Find two 1-hour sessions with different teachers and different slots
    one_hr = [s for s in db_store.sessions.values() if s.duration == 1 and s.status != "cancelled"]
    assert len(one_hr) >= 2

    # Find a feasible swap pair
    feasible_pair = None
    for i in range(len(one_hr)):
        for j in range(i + 1, len(one_hr)):
            s1, s2 = one_hr[i], one_hr[j]
            if (s1.day, s1.period) != (s2.day, s2.period):
                is_valid, _, _ = SwapService.validate_swap(s1.id, s2.id)
                if is_valid:
                    feasible_pair = (s1, s2)
                    break
        if feasible_pair:
            break

    assert feasible_pair is not None, "At least one pair of 1-hour sessions should be swappable"
    s1, s2 = feasible_pair
    s1_orig_day, s1_orig_p = s1.day, s1.period
    s2_orig_day, s2_orig_p = s2.day, s2.period

    initial_swaps = len(db_store.swap_requests)
    initial_notifs = len(db_store.notifications)

    ok, msg, req = SwapService.execute_swap(
        session_1_id=s1.id,
        session_2_id=s2.id,
        requester_teacher_id=s1.teacher_id,
        reason="Mutual research conference swap"
    )

    assert ok is True
    assert s1.day == s2_orig_day and s1.period == s2_orig_p
    assert s2.day == s1_orig_day and s2.period == s1_orig_p
    assert len(db_store.swap_requests) == initial_swaps + 1
    assert req.status == "approved"
    assert len(db_store.notifications) > initial_notifs

def test_teacher_workload_analytics():
    """Verify teacher workload calculation, utilization %, and overload detection."""
    workload = AnalyticsService.get_teacher_workload_analytics()

    assert len(workload) == len(db_store.teachers)
    total_assigned_from_analytics = sum(t["assigned_hours"] for t in workload)
    total_duration_from_sessions = sum(s.duration for s in db_store.sessions.values() if s.status != "cancelled")

    assert total_assigned_from_analytics == total_duration_from_sessions

    for t in workload:
        assert "teacher_name" in t
        assert "max_weekly_load" in t
        assert "utilization_percentage" in t
        assert "is_overloaded" in t
        assert t["assigned_hours"] <= t["max_weekly_load"] or t["is_overloaded"]

def test_room_analytics():
    """Verify room and laboratory utilization statistics."""
    rooms = AnalyticsService.get_room_analytics()

    assert len(rooms) == len(db_store.rooms)
    for r in rooms:
        assert "room_name" in r
        assert "capacity" in r
        assert "type" in r
        assert "occupied_hours" in r
        assert "utilization_percentage" in r
        assert 0.0 <= r["utilization_percentage"] <= 100.0

def test_constraint_quality_analytics():
    """Verify constraint quality evaluation and soft penalty breakdown."""
    quality = AnalyticsService.get_constraint_quality_analytics()

    assert quality["has_schedule"] is True
    assert quality["is_valid"] is True
    assert quality["hard_violations_count"] == 0
    assert "soft_penalty" in quality
    assert "penalty_breakdown" in quality
    assert "compliance_score" in quality
    assert 0.0 <= quality["compliance_score"] <= 100.0
