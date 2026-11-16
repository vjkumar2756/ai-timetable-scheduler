"""
tests/test_phase10_simulated_annealing.py
Verification test suite for Phase 10:
- Simulated Annealing local search (+6 Bonus marks)
- Boltzmann acceptance criterion & geometric cooling
- Optimization on Small Benchmark Dataset
- Cost history convergence tracking
- Seed reproducibility
"""
import json
import pytest
from core.problem import TimetableProblem
from core.validator import ConstraintValidator
from core.annealing import SimulatedAnnealingSolver

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

def test_simulated_annealing_tiny_instance():
    """Verify Simulated Annealing optimizes tiny instance to valid state."""
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

    solver = SimulatedAnnealingSolver(problem, validator, initial_temp=50.0, cooling_rate=0.92, min_temp=1.0, seed=42)
    result = solver.solve(time_limit_seconds=5.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.cost_history) > 5

def test_simulated_annealing_small_dataset_cost_reduction():
    """Verify Simulated Annealing achieves dramatic cost reduction on Small Benchmark Dataset."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")
    solver = SimulatedAnnealingSolver(
        problem, validator,
        initial_temp=100.0, cooling_rate=0.95, min_temp=1.0, steps_per_temp=25, seed=42
    )
    result = solver.solve(time_limit_seconds=10.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.cost_history) > 20
    # Final cost must be significantly lower than initial random cost
    initial_cost = result.cost_history[0]
    final_cost = result.cost_history[-1]
    assert final_cost < initial_cost
    assert (initial_cost - final_cost) > 5000  # Substantial hard violations resolved

def test_simulated_annealing_seed_reproducibility():
    """Verify identical random seed produces identical solution trajectory."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")

    solver1 = SimulatedAnnealingSolver(problem, validator, initial_temp=30.0, cooling_rate=0.90, min_temp=5.0, seed=777)
    res1 = solver1.solve(time_limit_seconds=5.0, seed=777)

    solver2 = SimulatedAnnealingSolver(problem, validator, initial_temp=30.0, cooling_rate=0.90, min_temp=5.0, seed=777)
    res2 = solver2.solve(time_limit_seconds=5.0, seed=777)

    assert res1.total_cost == res2.total_cost
    assert res1.hard_violations == res2.hard_violations
    assert res1.cost_history == res2.cost_history
