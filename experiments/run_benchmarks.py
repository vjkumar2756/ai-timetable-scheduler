import os
import json
import time
from typing import Dict, List, Any
import numpy as np

# Use local imports
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room
from backend.app.scheduler.csp import TimetableCSP
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.backtracking import PlainBacktrackingSolver, ImprovedBacktrackingSolver
from backend.app.scheduler.min_conflicts import MinConflictsSolver
from backend.app.scheduler.simulated_annealing import SimulatedAnnealingSolver
from backend.app.scheduler.hybrid import HybridCSPSASolver

RESULTS_DIR = os.path.join(BASE_DIR, "experiments/results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_data(dataset_filename: str):
    path = os.path.join(BASE_DIR, "datasets", dataset_filename)
    with open(path, "r") as f:
        data = json.load(f)
    settings = WorkingSettings(**data["settings"])
    subs = {s["id"]: Subject(**s) for s in data["subjects"]}
    teachers = {t["id"]: Teacher(**t) for t in data["teachers"]}
    classes = {c["id"]: ClassBatch(**c) for c in data["classes"]}
    rooms = {r["id"]: Room(**r) for r in data["rooms"]}
    return settings, classes, subs, teachers, rooms

def run_benchmarks():
    print("="*70)
    print("        SchedulAI — Automated Experimental Benchmark Suite       ")
    print("="*70)

    datasets = [
        ("Small Dataset (3 Classes, 6 Teachers, 4 Rooms)", "small_dataset.json"),
        ("Large Dataset (8 Classes, 16 Teachers, 8 Rooms)", "large_dataset.json")
    ]

    seeds = [42, 101, 203, 307, 409, 521, 631, 743, 857, 967]
    all_results = {}
    sample_cost_history = []

    for ds_label, ds_file in datasets:
        print(f"\n>>> Running Experiments on: {ds_label}")
        settings, classes, subs, teachers, rooms = load_data(ds_file)
        csp = TimetableCSP(settings, classes, subs, teachers, rooms)
        validator = ConstraintValidator(settings, classes, subs, teachers, rooms)
        cost_fn = CostFunction(settings, classes, subs, teachers, rooms)

        ds_key = "small" if "small" in ds_file else "large"
        all_results[ds_key] = {}

        # 1. Plain Backtracking (Deterministic baseline)
        print("  [1/5] Running Plain Backtracking...")
        pbt_solver = PlainBacktrackingSolver(csp, validator, cost_fn)
        # Timeout after 15s if baseline takes too long on large dataset
        pbt_res = pbt_solver.solve(time_limit_seconds=15.0)
        all_results[ds_key]["plain_backtracking"] = {
            "algorithm": "Plain Backtracking (Baseline)",
            "time_taken_seconds": round(pbt_res.execution_time_seconds, 4),
            "nodes_expanded": pbt_res.nodes_expanded,
            "hard_violations": pbt_res.hard_violations,
            "soft_penalty": pbt_res.soft_penalty,
            "success_rate": 1.0 if pbt_res.success else 0.0,
            "success": pbt_res.success,
            "trials": 1
        }
        print(f"        -> Time: {pbt_res.execution_time_seconds:.4f}s, Nodes: {pbt_res.nodes_expanded}, Violations: {pbt_res.hard_violations}, Soft: {pbt_res.soft_penalty}")

        # 2. Improved Backtracking (MRV + FC + Degree + LCV)
        print("  [2/5] Running Improved Backtracking...")
        ibt_solver = ImprovedBacktrackingSolver(csp, validator, cost_fn)
        ibt_res = ibt_solver.solve(time_limit_seconds=20.0)
        all_results[ds_key]["improved_backtracking"] = {
            "algorithm": "Improved Backtracking (MRV+FC+Degree+LCV)",
            "time_taken_seconds": round(ibt_res.execution_time_seconds, 4),
            "nodes_expanded": ibt_res.nodes_expanded,
            "hard_violations": ibt_res.hard_violations,
            "soft_penalty": ibt_res.soft_penalty,
            "success_rate": 1.0 if ibt_res.success else 0.0,
            "success": ibt_res.success,
            "trials": 1
        }
        print(f"        -> Time: {ibt_res.execution_time_seconds:.4f}s, Nodes: {ibt_res.nodes_expanded}, Violations: {ibt_res.hard_violations}, Soft: {ibt_res.soft_penalty}")

        # 3. Min-Conflicts (10 randomized runs)
        print("  [3/5] Running Min-Conflicts Local Search (10 Trials)...")
        mc_times, mc_iters, mc_viols, mc_softs, mc_successes = [], [], [], [], []
        for i, s in enumerate(seeds):
            mc_solver = MinConflictsSolver(csp, validator, cost_fn, max_iterations=600, seed=s)
            res = mc_solver.solve(seed=s)
            mc_times.append(res.execution_time_seconds)
            mc_iters.append(res.iterations)
            mc_viols.append(res.hard_violations)
            mc_softs.append(res.soft_penalty)
            mc_successes.append(1 if res.success else 0)
            if ds_key == "small" and i == 0 and res.cost_history:
                sample_cost_history = res.cost_history

        all_results[ds_key]["min_conflicts"] = {
            "algorithm": "Min-Conflicts Local Search",
            "time_taken_seconds": round(float(np.mean(mc_times)), 4),
            "nodes_expanded": int(np.mean(mc_iters)),
            "hard_violations": int(np.mean(mc_viols)),
            "soft_penalty": round(float(np.mean(mc_softs)), 1),
            "success_rate": round(sum(mc_successes) / len(mc_successes), 2),
            "success": sum(mc_successes) > 0,
            "trials": len(seeds)
        }
        print(f"        -> Mean Time: {np.mean(mc_times):.4f}s, Mean Iters: {np.mean(mc_iters):.1f}, Success Rate: {sum(mc_successes)}/10")

        # 4. Simulated Annealing (10 randomized runs)
        print("  [4/5] Running Simulated Annealing (+6 Bonus, 10 Trials)...")
        sa_times, sa_iters, sa_viols, sa_softs, sa_successes = [], [], [], [], []
        for s in seeds:
            sa_solver = SimulatedAnnealingSolver(csp, validator, cost_fn, initial_temp=50.0, cooling_rate=0.94, steps_per_temp=20, seed=s)
            res = sa_solver.solve(seed=s)
            sa_times.append(res.execution_time_seconds)
            sa_iters.append(res.iterations)
            sa_viols.append(res.hard_violations)
            sa_softs.append(res.soft_penalty)
            sa_successes.append(1 if res.success else 0)

        all_results[ds_key]["simulated_annealing"] = {
            "algorithm": "Simulated Annealing (Bonus)",
            "time_taken_seconds": round(float(np.mean(sa_times)), 4),
            "nodes_expanded": int(np.mean(sa_iters)),
            "hard_violations": int(np.mean(sa_viols)),
            "soft_penalty": round(float(np.mean(sa_softs)), 1),
            "success_rate": round(sum(sa_successes) / len(sa_successes), 2),
            "success": sum(sa_successes) > 0,
            "trials": len(seeds)
        }
        print(f"        -> Mean Time: {np.mean(sa_times):.4f}s, Mean Iters: {np.mean(sa_iters):.1f}, Success Rate: {sum(sa_successes)}/10")

        # 5. Hybrid CSP + Simulated Annealing (10 randomized runs)
        print("  [5/5] Running Hybrid CSP + Simulated Annealing (+6 Bonus, 10 Trials)...")
        hyb_times, hyb_iters, hyb_viols, hyb_softs, hyb_successes = [], [], [], [], []
        for s in seeds:
            hyb_solver = HybridCSPSASolver(csp, validator, cost_fn, sa_initial_temp=40.0, sa_cooling_rate=0.94, sa_steps_per_temp=20, seed=s)
            res = hyb_solver.solve(seed=s)
            hyb_times.append(res.execution_time_seconds)
            hyb_iters.append(res.iterations)
            hyb_viols.append(res.hard_violations)
            hyb_softs.append(res.soft_penalty)
            hyb_successes.append(1 if res.success else 0)

        all_results[ds_key]["hybrid"] = {
            "algorithm": "Hybrid CSP + SA (Bonus)",
            "time_taken_seconds": round(float(np.mean(hyb_times)), 4),
            "nodes_expanded": int(np.mean(hyb_iters)),
            "hard_violations": int(np.mean(hyb_viols)),
            "soft_penalty": round(float(np.mean(hyb_softs)), 1),
            "success_rate": round(sum(hyb_successes) / len(hyb_successes), 2),
            "success": sum(hyb_successes) > 0,
            "trials": len(seeds)
        }
        print(f"        -> Mean Time: {np.mean(hyb_times):.4f}s, Mean Soft Penalty: {np.mean(hyb_softs):.1f}, Success Rate: {sum(hyb_successes)}/10")

    # Add sample cost history for graphing
    all_results["min_conflicts_sample_cost_history"] = sample_cost_history

    # Save to JSON
    json_path = os.path.join(RESULTS_DIR, "benchmark_results.json")
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[OK] Benchmark results saved to: {json_path}")

    # Generate Matplotlib plots
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Plot 1: Min-Conflicts Cost vs Iterations
        if sample_cost_history:
            plt.figure(figsize=(9, 5))
            plt.plot(sample_cost_history, color="#4f46e5", linewidth=2, label="Total Cost (1000×Hard + Soft)")
            plt.title("Min-Conflicts Local Search: Cost vs Iterations (Small Dataset)", fontsize=13, fontweight="bold")
            plt.xlabel("Iteration", fontsize=11)
            plt.ylabel("Cost Function Value", fontsize=11)
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.legend()
            plt.tight_layout()
            plot1_path = os.path.join(RESULTS_DIR, "min_conflicts_convergence.png")
            plt.savefig(plot1_path, dpi=200)
            plt.close()
            print(f"[OK] Min-Conflicts convergence graph saved to: {plot1_path}")

        # Plot 2: Algorithm Comparison Runtimes & Soft Penalties
        algos = ["Plain BT", "Improved BT", "Min-Conflicts", "Hybrid CSP+SA"]
        small_times = [
            all_results["small"]["plain_backtracking"]["time_taken_seconds"],
            all_results["small"]["improved_backtracking"]["time_taken_seconds"],
            all_results["small"]["min_conflicts"]["time_taken_seconds"],
            all_results["small"]["hybrid"]["time_taken_seconds"],
        ]
        large_times = [
            all_results["large"]["plain_backtracking"]["time_taken_seconds"],
            all_results["large"]["improved_backtracking"]["time_taken_seconds"],
            all_results["large"]["min_conflicts"]["time_taken_seconds"],
            all_results["large"]["hybrid"]["time_taken_seconds"],
        ]

        x = np.arange(len(algos))
        width = 0.35

        plt.figure(figsize=(10, 5))
        plt.bar(x - width/2, small_times, width, label="Small Dataset", color="#3b82f6")
        plt.bar(x + width/2, large_times, width, label="Large Dataset", color="#10b981")
        plt.ylabel("Time Taken (seconds)", fontsize=11)
        plt.title("Algorithm Execution Time Comparison (Log Scale)", fontsize=13, fontweight="bold")
        plt.xticks(x, algos)
        plt.yscale("log")
        plt.grid(True, linestyle="--", alpha=0.5, axis="y")
        plt.legend()
        plt.tight_layout()
        plot2_path = os.path.join(RESULTS_DIR, "algorithm_comparison.png")
        plt.savefig(plot2_path, dpi=200)
        plt.close()
        print(f"[OK] Comparison bar chart saved to: {plot2_path}")

    except Exception as e:
        print(f"[Warning] Matplotlib plot generation skipped: {e}")

if __name__ == "__main__":
    run_benchmarks()
