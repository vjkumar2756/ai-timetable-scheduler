import pytest
import json
import os
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room
from backend.app.scheduler.csp import TimetableCSP, SlotValue, LectureVariable
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.backtracking import PlainBacktrackingSolver, ImprovedBacktrackingSolver
from backend.app.scheduler.min_conflicts import MinConflictsSolver
from backend.app.scheduler.hybrid import HybridCSPSASolver
from backend.app.services.schedule_service import ScheduleService
from backend.app.services.rescheduling_service import ReschedulingService
from backend.app.services.swap_service import SwapService
from backend.app.database.store import db_store

@pytest.fixture
def test_setup():
    settings = WorkingSettings(days=["Mon", "Tue", "Wed"], periods_per_day=5, default_lunch_period=3)
    subjects = {
        "SUB1": Subject(id="SUB1", code="S101", name="Theory Course", weekly_hours=2, type="theory", lab_duration=1),
        "LAB1": Subject(id="LAB1", code="L101", name="Practical Lab", weekly_hours=2, type="lab", lab_duration=2)
    }
    teachers = {
        "T1": Teacher(id="T1", name="Prof. Alpha", subject_ids=["SUB1", "LAB1"], unavailable_slots=[{"day": "Mon", "period": 1}], max_weekly_load=6),
        "T2": Teacher(id="T2", name="Prof. Beta", subject_ids=["SUB1"], unavailable_slots=[], max_weekly_load=6)
    }
    classes = {
        "C1": ClassBatch(id="C1", name="Batch 1", strength=30, subject_requirements={"SUB1": 2, "LAB1": 2}, lunch_break_period=3),
        "C2": ClassBatch(id="C2", name="Batch 2", strength=50, subject_requirements={"SUB1": 2}, lunch_break_period=3)
    }
    rooms = {
        "R_CLASS": Room(id="R_CLASS", name="Lecture Room 101", capacity=40, type="classroom"),
        "R_LARGE": Room(id="R_LARGE", name="Auditorium", capacity=60, type="classroom"),
        "R_LAB": Room(id="R_LAB", name="Lab Room", capacity=40, type="lab")
    }
    validator = ConstraintValidator(settings, classes, subjects, teachers, rooms)
    cost_fn = CostFunction(settings, classes, subjects, teachers, rooms)
    return settings, classes, subjects, teachers, rooms, validator, cost_fn

def test_h1_teacher_conflict(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    v1 = LectureVariable("V1", "C1", "SUB1", 1, 1, False, "S101", "Theory")
    v2 = LectureVariable("V2", "C2", "SUB1", 1, 1, False, "S101", "Theory")
    var_map = {"V1": v1, "V2": v2}
    
    # Both assigned to Teacher T1 on Mon period 2
    assignment = {
        "V1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T1"),
        "V2": SlotValue(day="Mon", period=2, room_id="R_LARGE", teacher_id="T1")
    }
    is_valid, count, viols = validator.validate_assignment(assignment, var_map, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H1" for v in viols)

def test_h2_class_conflict(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    v1 = LectureVariable("V1", "C1", "SUB1", 1, 1, False, "S101", "Theory")
    v2 = LectureVariable("V2", "C1", "SUB1", 2, 1, False, "S101", "Theory")
    var_map = {"V1": v1, "V2": v2}
    
    # Class C1 attending 2 sessions at the same time
    assignment = {
        "V1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T1"),
        "V2": SlotValue(day="Mon", period=2, room_id="R_LARGE", teacher_id="T2")
    }
    is_valid, count, viols = validator.validate_assignment(assignment, var_map, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H2" for v in viols)

def test_h3_room_conflict(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    v1 = LectureVariable("V1", "C1", "SUB1", 1, 1, False, "S101", "Theory")
    v2 = LectureVariable("V2", "C2", "SUB1", 1, 1, False, "S101", "Theory")
    var_map = {"V1": v1, "V2": v2}
    
    # Same room R_CLASS used at the same time
    assignment = {
        "V1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T1"),
        "V2": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T2")
    }
    is_valid, count, viols = validator.validate_assignment(assignment, var_map, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H3" for v in viols)

def test_h4_room_capacity(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    # C2 has strength 50, R_CLASS capacity is only 40
    v = LectureVariable("V2", "C2", "SUB1", 1, 1, False, "S101", "Theory")
    assignment = {"V2": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T2")}
    is_valid, count, viols = validator.validate_assignment(assignment, {"V2": v}, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H4" for v in viols)

def test_h5_room_type(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    # Lab session scheduled in a theory classroom
    v_lab = LectureVariable("V_LAB", "C1", "LAB1", 1, 2, True, "L101", "Lab")
    assignment = {"V_LAB": SlotValue(day="Tue", period=1, room_id="R_CLASS", teacher_id="T1")}
    is_valid, count, viols = validator.validate_assignment(assignment, {"V_LAB": v_lab}, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H5" for v in viols)

def test_h6_teacher_availability(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    # T1 declared unavailable on Mon period 1
    v = LectureVariable("V1", "C1", "SUB1", 1, 1, False, "S101", "Theory")
    assignment = {"V1": SlotValue(day="Mon", period=1, room_id="R_CLASS", teacher_id="T1")}
    is_valid, count, viols = validator.validate_assignment(assignment, {"V1": v}, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H6" for v in viols)

def test_h9_lunch_break(test_setup):
    settings, classes, subjects, teachers, rooms, validator, _ = test_setup
    # C1 lunch break is period 3
    v = LectureVariable("V1", "C1", "SUB1", 1, 1, False, "S101", "Theory")
    assignment = {"V1": SlotValue(day="Mon", period=3, room_id="R_CLASS", teacher_id="T1")}
    is_valid, count, viols = validator.validate_assignment(assignment, {"V1": v}, check_completeness=False)
    assert not is_valid
    assert any(v["code"] == "H9" for v in viols)

def test_solvers_end_to_end_on_small_dataset():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    with open(os.path.join(base_dir, "datasets/small_dataset.json")) as f:
        data = json.load(f)
    settings = WorkingSettings(**data["settings"])
    subs = {s["id"]: Subject(**s) for s in data["subjects"]}
    teachers = {t["id"]: Teacher(**t) for t in data["teachers"]}
    classes = {c["id"]: ClassBatch(**c) for c in data["classes"]}
    rooms = {r["id"]: Room(**r) for r in data["rooms"]}

    csp = TimetableCSP(settings, classes, subs, teachers, rooms)
    validator = ConstraintValidator(settings, classes, subs, teachers, rooms)
    cost_fn = CostFunction(settings, classes, subs, teachers, rooms)

    # 1. Improved Backtracking
    res_ibt = ImprovedBacktrackingSolver(csp, validator, cost_fn).solve(time_limit_seconds=10)
    assert res_ibt.success
    assert res_ibt.hard_violations == 0

    # 2. Plain Backtracking
    res_pbt = PlainBacktrackingSolver(csp, validator, cost_fn).solve(time_limit_seconds=10)
    assert res_pbt.success
    assert res_pbt.hard_violations == 0

    # 3. Min-Conflicts
    res_mc = MinConflictsSolver(csp, validator, cost_fn, max_iterations=500, seed=42).solve()
    assert res_mc.success
    assert res_mc.hard_violations == 0

    # 4. Hybrid CSP + SA
    res_hyb = HybridCSPSASolver(csp, validator, cost_fn, seed=42).solve()
    assert res_hyb.success
    assert res_hyb.hard_violations == 0
    assert res_hyb.soft_penalty <= res_ibt.soft_penalty
