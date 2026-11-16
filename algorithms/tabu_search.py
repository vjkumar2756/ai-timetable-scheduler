"""
Tabu Search Metaheuristic Solver for Timetable Scheduling.
Employs short-term memory (tabu list), aspiration criteria, and diversification mechanisms.
"""
import time
import random
from collections import deque
from typing import Dict, List, Tuple, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.csp import LectureVariable, SlotValue
from backend.app.scheduler.metrics import SolverResult

class TabuSearchSolver(BaseSolver):
    """
    Tabu Search with configurable tenure, aspiration, and diversification.
    """
    def __init__(self, csp, validator, cost_fn, config=None, seed=42):
        super().__init__(csp, validator, cost_fn, config, seed)
        cfg = self.config
        self.max_iterations = cfg.get("max_iterations", 500)
        self.tabu_tenure = cfg.get("tabu_tenure", 10)
        self.diversify_threshold = cfg.get("diversify_threshold", 40)

    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        if self.seed is not None:
            random.seed(self.seed)

        start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables

        # 1. Greedy initial assignment
        current_assignment: Dict[str, SlotValue] = {}
        for var in variables:
            best_val = min(
                self.csp.domains[var.id],
                key=lambda val: sum(1 for _, ov in current_assignment.items()
                                    if ov.day == val.day and ov.period == val.period and
                                    (ov.room_id == val.room_id or ov.teacher_id == val.teacher_id))
            )
            current_assignment[var.id] = best_val

        # Evaluate initial state
        _, hard_c, _ = self.validator.validate_assignment(current_assignment, var_map, check_completeness=False)
        soft_p, _, _ = self.cost_fn.evaluate_soft_penalties(current_assignment, var_map)
        current_cost = self.cost_fn.compute_total_cost(hard_c, soft_p)

        best_assignment = dict(current_assignment)
        best_cost = current_cost
        best_hard = hard_c
        best_soft = soft_p

        # Tabu structure: deque of (var_id, SlotValue)
        tabu_list = deque(maxlen=self.tabu_tenure)
        cost_history = [current_cost]
        iterations_without_improvement = 0
        nodes_expanded = 0

        for it in range(self.max_iterations):
            if time.time() - start_time > timeout_seconds:
                break
            if best_hard == 0 and best_soft < 300:
                break

            nodes_expanded += 1
            # Generate candidate neighborhood moves
            candidate_moves = []
            sample_vars = random.sample(variables, min(8, len(variables)))

            for v in sample_vars:
                # Sample 3 candidate alternative values
                sample_vals = random.sample(self.csp.domains[v.id], min(3, len(self.csp.domains[v.id])))
                for val in sample_vals:
                    if val != current_assignment[v.id]:
                        # Simulate move
                        old_val = current_assignment[v.id]
                        current_assignment[v.id] = val
                        _, h, _ = self.validator.validate_assignment(current_assignment, var_map, check_completeness=False)
                        s, _, _ = self.cost_fn.evaluate_soft_penalties(current_assignment, var_map)
                        cand_cost = self.cost_fn.compute_total_cost(h, s)
                        current_assignment[v.id] = old_val

                        candidate_moves.append((cand_cost, v.id, val, old_val, h, s))

            if not candidate_moves:
                continue

            # Sort by cost ascending
            candidate_moves.sort(key=lambda x: x[0])

            # Select best non-tabu or aspirational move
            chosen_move = None
            for c_cost, v_id, new_val, prev_val, h, s in candidate_moves:
                move_signature = (v_id, new_val.day, new_val.period, new_val.room_id)
                # Aspiration criterion: allow if improves global best
                if c_cost < best_cost or move_signature not in tabu_list:
                    chosen_move = (c_cost, v_id, new_val, prev_val, h, s, move_signature)
                    break

            if chosen_move is None:
                chosen_move = candidate_moves[0] + (None,)

            c_cost, v_id, new_val, prev_val, h, s, sig = chosen_move
            current_assignment[v_id] = new_val
            current_cost = c_cost
            if sig:
                tabu_list.append(sig)

            cost_history.append(current_cost)

            if current_cost < best_cost:
                best_cost = current_cost
                best_assignment = dict(current_assignment)
                best_hard = h
                best_soft = s
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

            # Diversification if stuck in local optimum
            if iterations_without_improvement >= self.diversify_threshold:
                diversify_vars = random.sample(variables, min(3, len(variables)))
                for dv in diversify_vars:
                    current_assignment[dv.id] = random.choice(self.csp.domains[dv.id])
                iterations_without_improvement = 0

        elapsed = time.time() - start_time
        is_valid, final_hard, _ = self.validator.validate_assignment(best_assignment, var_map, check_completeness=True)
        final_soft, _, _ = self.cost_fn.evaluate_soft_penalties(best_assignment, var_map)

        return SolverResult(
            algorithm="Tabu Search",
            success=is_valid,
            execution_time_seconds=elapsed,
            nodes_expanded=nodes_expanded,
            iterations=nodes_expanded,
            hard_violations=final_hard,
            soft_penalty=final_soft,
            total_cost=self.cost_fn.compute_total_cost(final_hard, final_soft),
            cost_history=cost_history,
            assignment=best_assignment,
            diagnostic_message="Feasible schedule discovered via Tabu Search" if is_valid else f"Tabu Search stopped with {final_hard} conflicts"
        )
