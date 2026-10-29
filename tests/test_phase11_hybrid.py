"""
tests/test_phase11_hybrid.py
Verification test suite for Phase 11:
- Hybrid CSP + Simulated Annealing (+6 Bonus Marks)
- Stage 1: Systematic CSP Backtracking (MRV + Degree + FC) guaranteeing 0 hard violations
- Stage 2: Simulated Annealing soft-constraint polishing (preserving hard constraints)
- Verification on Tiny instance and Small Benchmark Dataset
- Soft penalty improvement tracking and seed reproducibility
"""
import json
import pytest
from core.problem import TimetableProblem
from core.validator import ConstraintValidator
from core.backtracking import ImprovedBacktrackingSolver
from core.hybrid import HybridCSPSASolver

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

def test_hybrid_solver_tiny_instance():
    """Verify Hybrid Solver successfully solves a tiny test instance to 100% feasibility."""
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

    solver = HybridCSPSASolver(problem, validator, sa_steps_per_temp=10, seed=42)
    result = solver.solve(time_limit_seconds=5.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert "Hybrid CSP + Simulated Annealing" in result.algorithm
    assert "Stage 1 (CSP)" in result.diagnostic_message
    assert "Stage 2 (SA)" in result.diagnostic_message

def test_hybrid_solver_small_dataset():
    """Verify Hybrid Solver on Small Benchmark Dataset maintains zero hard violations."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")
    solver = HybridCSPSASolver(
        problem=problem,
        validator=validator,
        sa_initial_temp=40.0,
        sa_cooling_rate=0.92,
        sa_min_temp=1.0,
        sa_steps_per_temp=20,
        seed=42
    )
    result = solver.solve(time_limit_seconds=10.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == len(problem.variables)
    assert result.runtime_seconds < 5.0

    # Ensure final authoritative check directly from validator
    final_val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert final_val.is_valid is True
    assert final_val.hard_violations_count == 0

def test_hybrid_solver_soft_cost_polish():
    """Verify Stage 2 SA strictly polishes or maintains soft quality compared to Stage 1 CSP alone."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")

    # Baseline Stage 1: Improved Backtracking CSP
    csp_solver = ImprovedBacktrackingSolver(problem, validator)
    csp_res = csp_solver.solve(time_limit_seconds=5.0)
    assert csp_res.success is True
    baseline_soft_cost = csp_res.total_cost

    # Hybrid Solver (CSP + SA polishing)
    hybrid_solver = HybridCSPSASolver(
        problem=problem,
        validator=validator,
        sa_initial_temp=30.0,
        sa_cooling_rate=0.93,
        sa_min_temp=0.5,
        sa_steps_per_temp=25,
        seed=42
    )
    hybrid_res = hybrid_solver.solve(time_limit_seconds=10.0)
    assert hybrid_res.success is True
    assert hybrid_res.hard_violations == 0

    # Hybrid total cost must be less than or equal to baseline CSP
    assert hybrid_res.total_cost <= baseline_soft_cost

def test_hybrid_solver_reproducibility():
    """Verify identical seed produces identical results."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")

    solver1 = HybridCSPSASolver(problem, validator, sa_steps_per_temp=15, seed=123)
    res1 = solver1.solve(time_limit_seconds=5.0, seed=123)

    solver2 = HybridCSPSASolver(problem, validator, sa_steps_per_temp=15, seed=123)
    res2 = solver2.solve(time_limit_seconds=5.0, seed=123)

    assert res1.total_cost == res2.total_cost
    assert res1.hard_violations == res2.hard_violations
    assert res1.cost_history == res2.cost_history
