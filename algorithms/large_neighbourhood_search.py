"""
Large Neighbourhood Search (LNS) Metaheuristic Solver.
Combines destruction operators (relaxing a cohort or a whole day) with exact CSP repair.
"""
import time
import random
from typing import Dict, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.backtracking import ImprovedBacktrackingSolver
from backend.app.scheduler.csp import SlotValue
from backend.app.scheduler.metrics import SolverResult

class LargeNeighbourhoodSearchSolver(BaseSolver):
    """
    LNS: Destroys a subproblem (cohort or day) and repairs using heuristic backtracking.
    """
    def __init__(self, csp, validator, cost_fn, config=None, seed=42):
        super().__init__(csp, validator, cost_fn, config, seed)
        cfg = self.config
        self.max_destroy_iterations = cfg.get("max_iterations", 25)
        self.destroy_fraction = cfg.get("destroy_fraction", 0.25)

    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        if self.seed is not None:
            random.seed(self.seed)

        start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables

        # 1. Generate initial feasible schedule using Improved Backtracking
        init_solver = ImprovedBacktrackingSolver(self.csp, self.validator, self.cost_fn)
        base_result = init_solver.solve(time_limit_seconds=min(15.0, timeout_seconds * 0.4))

        if not base_result.success or not base_result.assignment:
            # Fallback if initial construction fails
            return base_result

        current = dict(base_result.assignment)
        _, curr_h, _ = self.validator.validate_assignment(current, var_map, check_completeness=True)
        curr_s, _, _ = self.cost_fn.evaluate_soft_penalties(current, var_map)
        curr_cost = self.cost_fn.compute_total_cost(curr_h, curr_s)

        best_assignment = dict(current)
        best_cost = curr_cost
        best_h = curr_h
        best_s = curr_s
        cost_history = [curr_cost]
        evaluations = base_result.nodes_expanded

        classes = list(self.csp.classes.keys())
        days = list(self.csp.settings.days)

        # 2. Destroy and Repair Loop
        for it in range(self.max_destroy_iterations):
            if time.time() - start_time > timeout_seconds:
                break
            evaluations += 1

            # Destroy operator: pick a class or a day to unassign
            destroy_by = random.choice(["class", "day"])
            if destroy_by == "class":
                target_cls = random.choice(classes)
                destroyed_vars = [v for v in variables if v.class_id == target_cls]
            else:
                target_day = random.choice(days)
                destroyed_vars = [v for v in variables if current[v.id].day == target_day]

            destroyed_ids = {v.id for v in destroyed_vars}
            partial_assignment = {vid: val for vid, val in current.items() if vid not in destroyed_ids}

            # Repair operator: greedily or systematically reassign destroyed variables
            repaired = dict(partial_assignment)
            repair_success = True

            for dv in destroyed_vars:
                valid_vals = [
                    val for val in self.csp.domains[dv.id]
                    if self.validator.is_consistent(dv, val, repaired, var_map)
                ]
                if valid_vals:
                    # Pick value with minimum soft penalty
                    best_v = min(
                        valid_vals,
                        key=lambda val: self.cost_fn.compute_total_cost(
                            0, self.cost_fn.evaluate_soft_penalties({**repaired, dv.id: val}, var_map)[0]
                        )
                    )
                    repaired[dv.id] = best_v
                else:
                    repair_success = False
                    break

            if repair_success and len(repaired) == len(variables):
                _, rep_h, _ = self.validator.validate_assignment(repaired, var_map, check_completeness=True)
                rep_s, _, _ = self.cost_fn.evaluate_soft_penalties(repaired, var_map)
                rep_cost = self.cost_fn.compute_total_cost(rep_h, rep_s)

                if rep_h == 0 and rep_cost <= curr_cost:
                    current = repaired
                    curr_cost = rep_cost
                    curr_h = rep_h
                    curr_s = rep_s

                    if rep_cost < best_cost:
                        best_cost = rep_cost
                        best_assignment = dict(repaired)
                        best_h = rep_h
                        best_s = rep_s

            cost_history.append(best_cost)

        elapsed = time.time() - start_time
        is_valid, final_h, _ = self.validator.validate_assignment(best_assignment, var_map, check_completeness=True)
        final_s, _, _ = self.cost_fn.evaluate_soft_penalties(best_assignment, var_map)

        return SolverResult(
            algorithm="Large Neighbourhood Search (LNS)",
            success=is_valid,
            execution_time_seconds=elapsed,
            nodes_expanded=evaluations,
            iterations=evaluations,
            hard_violations=final_h,
            soft_penalty=final_s,
            total_cost=self.cost_fn.compute_total_cost(final_h, final_s),
            cost_history=cost_history,
            assignment=best_assignment,
            diagnostic_message="Feasible schedule optimized via LNS" if is_valid else f"LNS stopped with {final_h} conflicts"
        )
