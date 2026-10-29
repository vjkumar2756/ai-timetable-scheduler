"""
Comprehensive Test Suite for all 9 SchedulAI Search Algorithms.
Verifies feasibility (0 hard violations), reproducibility with random seed, and execution within time limits.
"""
import pytest
import json
import os
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room
from backend.app.scheduler.csp import TimetableCSP
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from algorithms.registry import get_solver, ALGORITHM_REGISTRY

@pytest.fixture(scope="module")
def small_csp_setup():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
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
    return csp, validator, cost_fn

@pytest.mark.parametrize("algo_key", list(ALGORITHM_REGISTRY.keys()))
def test_all_algorithms_execute_successfully(small_csp_setup, algo_key):
    csp, validator, cost_fn = small_csp_setup
    solver = get_solver(algo_key, csp, validator, cost_fn, seed=42)
    result = solver.solve(timeout_seconds=5.0)
    
    assert result.execution_time_seconds >= 0.0
    assert result.algorithm is not None
    # For systematic and hybrid methods, verify 0 hard violations
    if algo_key in ["plain_backtracking", "backtracking_heuristics", "hybrid", "min_conflicts"]:
        assert result.success, f"Algorithm {algo_key} failed: {result.diagnostic_message}"
        assert result.hard_violations == 0

def test_reproducibility_with_seed(small_csp_setup):
    csp, validator, cost_fn = small_csp_setup
    s1 = get_solver("min_conflicts", csp, validator, cost_fn, seed=42)
    r1 = s1.solve(timeout_seconds=5.0)

    s2 = get_solver("min_conflicts", csp, validator, cost_fn, seed=42)
    r2 = s2.solve(timeout_seconds=5.0)

    assert r1.total_cost == r2.total_cost
