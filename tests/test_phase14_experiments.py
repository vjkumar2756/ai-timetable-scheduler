"""
tests/test_phase14_experiments.py
Verification test suite for Phase 14:
- Empirical benchmark dataset execution and metrics structure
- Third-party CSP verification with python-constraint
- Benchmark results API endpoint
- Streamlit benchmark view data loading
"""
import os
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from experiments.cross_check import run_cross_validation
from frontend.views.benchmarks import load_benchmark_data

client = TestClient(app)

def test_benchmark_results_json_schema():
    """Verify benchmark_results.json exists and contains standardized metrics for all 5 algorithms."""
    results_path = "experiments/results/benchmark_results.json"
    assert os.path.exists(results_path), f"Benchmark results file not found at {results_path}"

    with open(results_path, "r") as f:
        data = json.load(f)

    for ds_key in ["small", "large"]:
        assert ds_key in data, f"Dataset '{ds_key}' missing from benchmark results"
        ds_results = data[ds_key]

        expected_algos = ["plain_backtracking", "improved_backtracking", "min_conflicts", "simulated_annealing", "hybrid"]
        for algo in expected_algos:
            assert algo in ds_results, f"Algorithm '{algo}' missing from {ds_key} benchmark results"
            algo_res = ds_results[algo]

            assert "algorithm" in algo_res
            assert "time_taken_seconds" in algo_res
            assert "nodes_expanded" in algo_res
            assert "hard_violations" in algo_res
            assert "soft_penalty" in algo_res
            assert "success_rate" in algo_res
            assert "trials" in algo_res

            assert algo_res["time_taken_seconds"] >= 0.0
            assert 0.0 <= algo_res["success_rate"] <= 1.0

def test_cross_check_python_constraint():
    """Verify independent cross-validation against python-constraint library passes."""
    success = run_cross_validation()
    assert success is True

def test_benchmarks_api_endpoint():
    """Verify GET /api/analytics/benchmarks returns full experimental dataset."""
    response = client.get("/api/analytics/benchmarks")
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["success"] is True
    data = res_data["data"]
    assert "small" in data
    assert "large" in data

def test_benchmarks_view_data_loading():
    """Verify frontend benchmarks loader correctly parses benchmark metrics."""
    data = load_benchmark_data()
    assert isinstance(data, dict)
    assert "small" in data
    assert "large" in data
    assert "improved_backtracking" in data["small"]
