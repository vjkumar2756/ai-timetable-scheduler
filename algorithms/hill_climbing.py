"""
Hill Climbing (Steepest Ascent with Random Restarts).
Iterative local search baseline for comparison against Min-Conflicts and Simulated Annealing.
"""
import time
import random
from typing import Dict, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.csp import SlotValue
from backend.app.scheduler.metrics import SolverResult

class HillClimbingSolver(BaseSolver):
    """
    Steepest descent local search with random restarts.
    """
    def __init__(self, csp, validator, cost_fn, config=None, seed=42):
        super().__init__(csp, validator, cost_fn, config, seed)
        cfg = self.config
        self.max_steps_per_restart = cfg.get("max_steps", 150)
        self.max_restarts = cfg.get("max_restarts", 5)

    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        if self.seed is not None:
            random.seed(self.seed)

        start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables

        best_assignment: Dict[str, SlotValue] = {}
        best_cost = float("inf")
        best_hard = float("inf")
        best_soft = float("inf")
        cost_history = []
        evaluations = 0

        for r in range(self.max_restarts + 1):
            if time.time() - start_time > timeout_seconds:
                break
            if best_hard == 0 and best_soft < 300:
                break

            # Random restart initial state
            current = {v.id: random.choice(self.csp.domains[v.id]) for v in variables}
            _, h, _ = self.validator.validate_assignment(current, var_map, check_completeness=False)
            s, _, _ = self.cost_fn.evaluate_soft_penalties(current, var_map)
            curr_cost = self.cost_fn.compute_total_cost(h, s)

            for step in range(self.max_steps_per_restart):
                if time.time() - start_time > timeout_seconds:
                    break
                evaluations += 1
                cost_history.append(curr_cost)

                if curr_cost < best_cost:
                    best_cost = curr_cost
                    best_hard = h
                    best_soft = s
                    best_assignment = dict(current)

                if curr_cost == 0:
                    break

                # Generate neighborhood: test changing one variable at a time
                best_neighbor = None
                best_neighbor_cost = curr_cost
                best_nh = h
                best_ns = s

                sample_vars = random.sample(variables, min(10, len(variables)))
                for v in sample_vars:
                    old_v = current[v.id]
                    sample_vals = random.sample(self.csp.domains[v.id], min(4, len(self.csp.domains[v.id])))
                    for cand_val in sample_vals:
                        if cand_val != old_v:
                            current[v.id] = cand_val
                            _, nh, _ = self.validator.validate_assignment(current, var_map, check_completeness=False)
                            ns, _, _ = self.cost_fn.evaluate_soft_penalties(current, var_map)
                            nc = self.cost_fn.compute_total_cost(nh, ns)
                            if nc < best_neighbor_cost:
                                best_neighbor_cost = nc
                                best_neighbor = (v.id, cand_val)
                                best_nh = nh
                                best_ns = ns
                            current[v.id] = old_v

                # If no strictly improving neighbor exists (local optimum reached) -> restart
                if best_neighbor is None or best_neighbor_cost >= curr_cost:
                    break
                else:
                    v_id, new_val = best_neighbor
                    current[v_id] = new_val
                    curr_cost = best_neighbor_cost
                    h = best_nh
                    s = best_ns

        elapsed = time.time() - start_time
        if not best_assignment:
            best_assignment = {v.id: self.csp.domains[v.id][0] for v in variables}

        is_valid, final_h, _ = self.validator.validate_assignment(best_assignment, var_map, check_completeness=True)
        final_s, _, _ = self.cost_fn.evaluate_soft_penalties(best_assignment, var_map)

        return SolverResult(
            algorithm="Hill Climbing (Steepest Ascent + Restarts)",
            success=is_valid,
            execution_time_seconds=elapsed,
            nodes_expanded=evaluations,
            iterations=evaluations,
            hard_violations=final_h,
            soft_penalty=final_s,
            total_cost=self.cost_fn.compute_total_cost(final_h, final_s),
            cost_history=cost_history,
            assignment=best_assignment,
            diagnostic_message="Feasible timetable found by Hill Climbing" if is_valid else f"Hill Climbing stopped with {final_h} conflicts"
        )
