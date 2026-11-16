"""
tests/test_phase5_plain_backtracking.py
Verification test suite for Phase 5:
- Plain Backtracking solver on tiny instance
- Plain Backtracking solver on official Small Dataset (3C, 6T, 4R)
- Verification of zero hard violations on final solution
- Timeout and maximum node cutoff behavior
"""
import json
import pytest
from core.problem import TimetableProblem
from core.validator import ConstraintValidator
from core.backtracking import PlainBacktrackingSolver

def test_plain_backtracking_tiny_instance():
    """Verify Plain Backtracking finds conflict-free solution on tiny instance."""
    days = ["Mon", "Tue"]
    periods_per_day = 4
    default_lunch_period = 3

    classes = {
        "C1": {
            "id": "C1", "name": "Class 1", "strength": 30,
            "subject_requirements": {"MATH": 2, "AI_LAB": 2},
            "lunch_break_period": 3, "active": True
        }
    }
    subjects = {
        "MATH": {"id": "MATH", "code": "MATH", "name": "Mathematics", "weekly_hours": 2, "type": "theory", "lab_duration": 1},
        "AI_LAB": {"id": "AI_LAB", "code": "AI_LAB", "name": "AI Practical Lab", "weekly_hours": 2, "type": "lab", "lab_duration": 2}
    }
    teachers = {
        "T_MATH": {
            "id": "T_MATH", "name": "Dr. Euler", "subject_ids": ["MATH"],
            "unavailable_slots": [{"day": "Mon", "period": 1}],
            "preferred_slots": [{"day": "Tue", "period": 2}],
            "max_weekly_load": 10, "active": True
        },
        "T_LAB": {
            "id": "T_LAB", "name": "Prof. Lovelace", "subject_ids": ["AI_LAB"],
            "unavailable_slots": [], "preferred_slots": [],
            "max_weekly_load": 10, "active": True
        }
    }
    rooms = {
        "R_CLASS": {"id": "R_CLASS", "name": "Lecture Room 101", "capacity": 40, "type": "classroom", "active": True},
        "R_LAB": {"id": "R_LAB", "name": "Computing Lab 1", "capacity": 35, "type": "lab", "active": True}
    }

    problem = TimetableProblem(
        days=days,
        periods_per_day=periods_per_day,
        default_lunch_period=default_lunch_period,
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )
    validator = ConstraintValidator(
        days=days,
        periods_per_day=periods_per_day,
        default_lunch_period=default_lunch_period,
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )

    solver = PlainBacktrackingSolver(problem, validator)
    result = solver.solve(time_limit_seconds=5.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == 3
    assert result.nodes_expanded > 0

    # Cross-verify with validator
    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True
    assert val.hard_violations_count == 0

def test_plain_backtracking_small_dataset():
    """Verify Plain Backtracking solves the official Small Benchmark Dataset."""
    with open("data/small_dataset.json") as f:
        data = json.load(f)

    classes = {c["id"]: c for c in data["classes"]}
    subjects = {s["id"]: s for s in data["subjects"]}
    teachers = {t["id"]: t for t in data["teachers"]}
    rooms = {r["id"]: r for r in data["rooms"]}
    settings = data["settings"]

    problem = TimetableProblem(
        days=settings["days"],
        periods_per_day=settings["periods_per_day"],
        default_lunch_period=settings["default_lunch_period"],
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )
    validator = ConstraintValidator(
        days=settings["days"],
        periods_per_day=settings["periods_per_day"],
        default_lunch_period=settings["default_lunch_period"],
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )

    solver = PlainBacktrackingSolver(problem, validator)
    result = solver.solve(time_limit_seconds=10.0, max_nodes=50000)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == len(problem.variables)
    assert "Feasible" in result.diagnostic_message

    # Final independent verification
    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True
    assert val.hard_violations_count == 0

def test_plain_backtracking_cutoff_handling():
    """Verify that exceeding max nodes gracefully stops and reports cutoff."""
    with open("data/small_dataset.json") as f:
        data = json.load(f)

    classes = {c["id"]: c for c in data["classes"]}
    subjects = {s["id"]: s for s in data["subjects"]}
    teachers = {t["id"]: t for t in data["teachers"]}
    rooms = {r["id"]: r for r in data["rooms"]}
    settings = data["settings"]

    problem = TimetableProblem(
        days=settings["days"],
        periods_per_day=settings["periods_per_day"],
        default_lunch_period=settings["default_lunch_period"],
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )
    validator = ConstraintValidator(
        days=settings["days"],
        periods_per_day=settings["periods_per_day"],
        default_lunch_period=settings["default_lunch_period"],
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )

    solver = PlainBacktrackingSolver(problem, validator)
    # Set node limit to 2 (impossible to finish 39 variables)
    result = solver.solve(time_limit_seconds=5.0, max_nodes=2)

    assert result.success is False
    assert result.nodes_expanded >= 2
    assert "Search limit reached" in result.diagnostic_message
