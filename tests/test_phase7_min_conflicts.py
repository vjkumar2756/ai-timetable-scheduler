"""
tests/test_phase7_min_conflicts.py
Verification test suite for Phase 7:
- Min-Conflicts local search on tiny instance
- Min-Conflicts on Small Benchmark Dataset (3C, 6T, 4R)
- Min-Conflicts on Large Benchmark Dataset (8C, 16T, 8R)
- Cost history tracking for convergence graphs
- Reproducibility with random seeds
"""
import json
import pytest
from core.problem import TimetableProblem
from core.validator import ConstraintValidator
from core.min_conflicts import MinConflictsSolver

def get_problem_and_validator(dataset_path: str):
    with open(dataset_path) as f:
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
        classes=classes, subjects=subjects, teachers=teachers, rooms=rooms
    )
    validator = ConstraintValidator(
        days=settings["days"],
        periods_per_day=settings["periods_per_day"],
        default_lunch_period=settings["default_lunch_period"],
        classes=classes, subjects=subjects, teachers=teachers, rooms=rooms
    )
    return problem, validator

def test_min_conflicts_tiny_instance():
    """Verify Min-Conflicts finds conflict-free schedule on tiny instance."""
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
        days=days, periods_per_day=periods_per_day, default_lunch_period=default_lunch_period,
        classes=classes, subjects=subjects, teachers=teachers, rooms=rooms
    )
    validator = ConstraintValidator(
        days=days, periods_per_day=periods_per_day, default_lunch_period=default_lunch_period,
        classes=classes, subjects=subjects, teachers=teachers, rooms=rooms
    )

    solver = MinConflictsSolver(problem, validator, max_iterations=300, seed=42)
    result = solver.solve(time_limit_seconds=5.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.cost_history) > 0

    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True

def test_min_conflicts_small_dataset():
    """Verify Min-Conflicts solves Small Benchmark Dataset with cost history logged."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")
    solver = MinConflictsSolver(problem, validator, max_iterations=500, random_walk_prob=0.08, seed=42)
    result = solver.solve(time_limit_seconds=10.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == len(problem.variables)
    assert len(result.cost_history) >= 1
    assert all(isinstance(c, int) for c in result.cost_history)

    # Validate independent correctness
    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True
    assert val.hard_violations_count == 0

def test_min_conflicts_large_dataset():
    """Verify Min-Conflicts solves Large Benchmark Dataset."""
    problem, validator = get_problem_and_validator("data/large_dataset.json")
    solver = MinConflictsSolver(problem, validator, max_iterations=500, random_walk_prob=0.08, seed=42)
    result = solver.solve(time_limit_seconds=15.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == len(problem.variables)
    assert len(result.cost_history) >= 1

    # Validate independent correctness
    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True
    assert val.hard_violations_count == 0

def test_min_conflicts_seed_reproducibility():
    """Verify identical random seed produces identical solution and cost curve."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")

    solver1 = MinConflictsSolver(problem, validator, max_iterations=300, seed=123)
    res1 = solver1.solve(time_limit_seconds=5.0, seed=123)

    solver2 = MinConflictsSolver(problem, validator, max_iterations=300, seed=123)
    res2 = solver2.solve(time_limit_seconds=5.0, seed=123)

    assert res1.hard_violations == res2.hard_violations
    assert res1.total_cost == res2.total_cost
    assert res1.cost_history == res2.cost_history
