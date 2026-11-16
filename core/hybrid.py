"""
core/hybrid.py
Hybrid CSP + Simulated Annealing Solver (+6 Bonus Marks).
Pure Python module (zero web/DB/Streamlit dependencies).

Academic Notes (For Project Viva / Demo):
- Two-Stage Decoupled Optimization:
  - Stage 1 (Hard Feasibility): Improved Backtracking CSP (MRV+Degree+FC) systematically
    identifies a 100% hard-constraint conflict-free schedule (Hard Violations = 0).
  - Stage 2 (Soft Quality Optimization): Simulated Annealing takes the valid Stage 1 timetable
    as initial state and explores the neighborhood to minimize soft penalties (S1 - S5),
    strictly rejecting any candidate move that would violate hard feasibility.
- Why Hybrid is Superior:
  - Pure Backtracking stops at the first feasible solution (often with sub-optimal soft penalties).
  - Pure SA starting from random can take long to resolve all hard constraints.
  - Hybrid combines the guaranteed satisfiability of CSP with the global soft-optimization power of SA.
"""
import time
from typing import Dict, Optional, Tuple, Any, List
from core.problem import TimetableProblem, LectureVariable, SlotValue
from core.validator import ConstraintValidator, ValidationResult
from core.backtracking import ImprovedBacktrackingSolver, SolverResult
from core.annealing import SimulatedAnnealingSolver

class HybridCSPSASolver:
    """
    Two-stage Hybrid Solver:
    Stage 1: CSP Backtracking -> 100% Feasible Solution (H1-H9 = 0)
    Stage 2: Simulated Annealing -> Soft Constraint Minimization (S1-S5)
    """
    def __init__(
        self,
        problem: TimetableProblem,
        validator: ConstraintValidator,
        sa_initial_temp: float = 50.0,
        sa_cooling_rate: float = 0.94,
        sa_min_temp: float = 0.5,
        sa_steps_per_temp: int = 25,
        seed: Optional[int] = 42
    ):
        self.problem = problem
        self.validator = validator
        self.seed = seed

        self.csp_solver = ImprovedBacktrackingSolver(
            problem=problem,
            validator=validator,
            use_mrv=True,
            use_degree=True,
            use_forward_checking=True
        )

        self.sa_solver = SimulatedAnnealingSolver(
            problem=problem,
            validator=validator,
            initial_temp=sa_initial_temp,
            cooling_rate=sa_cooling_rate,
            min_temp=sa_min_temp,
            steps_per_temp=sa_steps_per_temp,
            seed=seed
        )

    def solve(
        self,
        time_limit_seconds: float = 30.0,
        seed: Optional[int] = None
    ) -> SolverResult:
        """
        Executes two-stage Hybrid optimization with before/after soft quality comparison.
        """
        start_time = time.time()
        run_seed = seed if seed is not None else self.seed

        # STAGE 1: Systematic CSP Backtracking for Hard Feasibility
        csp_time_limit = min(15.0, time_limit_seconds * 0.5)
        stage1_res = self.csp_solver.solve(time_limit_seconds=csp_time_limit)

        if not stage1_res.success:
            return SolverResult(
                algorithm="Hybrid CSP + Simulated Annealing (+6 Bonus)",
                success=False,
                runtime_seconds=round(time.time() - start_time, 4),
                nodes_expanded=stage1_res.nodes_expanded,
                backtracks_count=stage1_res.backtracks_count,
                hard_violations=stage1_res.hard_violations,
                soft_penalty=stage1_res.soft_penalty,
                total_cost=stage1_res.total_cost,
                assignment={},
                diagnostic_message=f"Hybrid Stage 1 (CSP) failed to find feasible baseline: {stage1_res.diagnostic_message}"
            )

        stage1_assignment = stage1_res.assignment
        stage1_val = self.validator.validate(stage1_assignment, self.problem.variables_dict, check_completeness=True)
        stage1_soft = stage1_val.soft_penalties_count
        stage1_cost = stage1_val.total_cost

        # STAGE 2: Simulated Annealing Soft Quality Polishing
        remaining_time = max(5.0, time_limit_seconds - (time.time() - start_time))
        stage2_res = self.sa_solver.solve(
            initial_assignment=stage1_assignment,
            time_limit_seconds=remaining_time,
            preserve_hard_constraints=True,
            seed=run_seed
        )

        total_runtime = time.time() - start_time

        # Final independent validation check
        final_val = self.validator.validate(stage2_res.assignment, self.problem.variables_dict, check_completeness=True)
        stage2_soft = final_val.soft_penalties_count
        stage2_cost = final_val.total_cost

        # Before vs. After comparison metrics
        soft_improved = stage1_cost - stage2_cost
        pct_improvement = round((soft_improved / max(1, stage1_cost)) * 100, 1) if soft_improved > 0 else 0.0

        diagnostic_msg = (
            f"Stage 1 (CSP): 100% Feasible ({stage1_res.nodes_expanded} nodes, Cost: {stage1_cost}) -> "
            f"Stage 2 (SA): Polished ({stage2_res.nodes_expanded} iters, Cost: {stage2_cost}). "
            f"Soft Cost Reduced by {soft_improved} pts ({pct_improvement}% improvement)."
        )

        return SolverResult(
            algorithm="Hybrid CSP + Simulated Annealing (+6 Bonus)",
            success=final_val.is_valid,
            runtime_seconds=round(total_runtime, 4),
            nodes_expanded=stage1_res.nodes_expanded + stage2_res.nodes_expanded,
            backtracks_count=stage1_res.backtracks_count,
            hard_violations=final_val.hard_violations_count,
            soft_penalty=final_val.soft_penalties_count,
            total_cost=final_val.total_cost,
            assignment=stage2_res.assignment,
            diagnostic_message=diagnostic_msg,
            cost_history=stage2_res.cost_history
        )
