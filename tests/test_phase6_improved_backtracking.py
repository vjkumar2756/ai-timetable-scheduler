"""
tests/test_phase6_improved_backtracking.py
Verification test suite for Phase 6:
- Improved Backtracking with MRV + Degree + Forward Checking
- Solves Small Benchmark Dataset (3C, 6T, 4R)
- Solves Large Benchmark Dataset (8C, 16T, 8R)
- Independent heuristic toggle validation (LCV, AC-3)
- Verification of zero hard constraint violations (H1 - H9)
"""
import json
import pytest
from core.problem import TimetableProblem
from core.validator import ConstraintValidator
from core.backtracking import ImprovedBacktrackingSolver

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

def test_improved_backtracking_small_dataset():
    """Verify Improved Backtracking (MRV+Degree+FC) solves Small Dataset."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")
    solver = ImprovedBacktrackingSolver(
        problem, validator,
        use_mrv=True, use_degree=True, use_forward_checking=True
    )
    result = solver.solve(time_limit_seconds=10.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == len(problem.variables)
    assert result.runtime_seconds < 2.0

    # Cross-verify with centralized validator
    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True
    assert val.hard_violations_count == 0

def test_improved_backtracking_large_dataset():
    """Verify Improved Backtracking (MRV+Degree+FC) solves Large Dataset (8 Classes, 16 Teachers, 8 Rooms)."""
    problem, validator = get_problem_and_validator("data/large_dataset.json")
    solver = ImprovedBacktrackingSolver(
        problem, validator,
        use_mrv=True, use_degree=True, use_forward_checking=True
    )
    result = solver.solve(time_limit_seconds=15.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert len(result.assignment) == len(problem.variables)
    assert result.runtime_seconds < 5.0

    # Cross-verify with centralized validator
    val = validator.validate(result.assignment, problem.variables_dict, check_completeness=True)
    assert val.is_valid is True
    assert val.hard_violations_count == 0

def test_improved_backtracking_with_lcv_and_ac3():
    """Verify Improved Backtracking runs smoothly with LCV and AC-3 enabled."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")
    solver = ImprovedBacktrackingSolver(
        problem, validator,
        use_mrv=True, use_degree=True, use_forward_checking=True,
        use_lcv=True, use_ac3=True
    )
    result = solver.solve(time_limit_seconds=10.0)

    assert result.success is True
    assert result.hard_violations == 0
    assert "AC-3" in result.algorithm
    assert "LCV" in result.algorithm

def test_domain_restoration_integrity():
    """Verify domain sizes remain consistent after solving."""
    problem, validator = get_problem_and_validator("data/small_dataset.json")
    initial_sizes = {v_id: len(domain) for v_id, domain in problem.domains.items()}

    solver = ImprovedBacktrackingSolver(
        problem, validator,
        use_mrv=True, use_degree=True, use_forward_checking=True
    )
    res = solver.solve(time_limit_seconds=5.0)
    assert res.success is True

    # Check problem domain definitions were never mutated in place
    for v_id, domain in problem.domains.items():
        assert len(domain) == initial_sizes[v_id]
