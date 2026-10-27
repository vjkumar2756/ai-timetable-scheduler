import time
import math
import random
from typing import Dict, List, Optional, Tuple
from backend.app.scheduler.csp import TimetableCSP, LectureVariable, SlotValue
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.metrics import SolverResult

class SimulatedAnnealingSolver:
    """
    Simulated Annealing Local Search Solver (+6 Bonus Marks).
    Features:
    1. Initial state (from initial assignment or passed-in feasible schedule)
    2. Defined neighborhood operators:
       - Move a session to a new valid slot in its domain
       - Swap slots of two sessions
    3. Geometric cooling schedule: T_k = alpha * T_{k-1}
    4. Metropolis acceptance criterion: P = exp(-dE / T)
    5. Feasibility preservation: Rejects any move that introduces hard violations
    6. Seed control for deterministic reproducibility
    """
    def __init__(
        self,
        csp: TimetableCSP,
        validator: ConstraintValidator,
        cost_fn: CostFunction,
        initial_temp: float = 100.0,
        cooling_rate: float = 0.96,
        min_temp: float = 0.1,
        steps_per_temp: int = 40,
        seed: Optional[int] = 42
    ):
        self.csp = csp
        self.validator = validator
        self.cost_fn = cost_fn
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.steps_per_temp = steps_per_temp
        self.seed = seed

    def solve(
        self,
        initial_assignment: Optional[Dict[str, SlotValue]] = None,
        preserve_hard_constraints: bool = True,
        seed: Optional[int] = None
    ) -> SolverResult:
        run_seed = seed if seed is not None else self.seed
        if run_seed is not None:
            random.seed(run_seed)

        start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables

        # 1. Initialize assignment
        if initial_assignment:
            current = dict(initial_assignment)
        else:
            current = {v.id: random.choice(self.csp.domains[v.id]) for v in variables}

        # Initial evaluation
        _, current_hard, _ = self.validator.validate_assignment(current, var_map, check_completeness=True)
        current_soft, _, _ = self.cost_fn.evaluate_soft_penalties(current, var_map)
        current_cost = self.cost_fn.compute_total_cost(current_hard, current_soft)

        best_assignment = dict(current)
        best_cost = current_cost
        best_hard = current_hard
        best_soft = current_soft

        cost_history: List[int] = [current_cost]
        temperature = self.initial_temp
        total_iterations = 0

        # Annealing Loop
        while temperature > self.min_temp:
            for _ in range(self.steps_per_temp):
                total_iterations += 1

                # Generate neighbor candidate
                neighbor = dict(current)
                move_type = random.choice(["move", "swap"])

                if move_type == "move" or len(variables) < 2:
                    var = random.choice(variables)
                    domain = self.csp.domains[var.id]
                    if domain:
                        new_val = random.choice(domain)
                        neighbor[var.id] = new_val
                else:
                    # Swap slots between two variables
                    v1, v2 = random.sample(variables, 2)
                    val1, val2 = neighbor[v1.id], neighbor[v2.id]
                    # Check if val2 is in domain of v1 and val1 is in domain of v2
                    if val2 in self.csp.domains[v1.id] and val1 in self.csp.domains[v2.id]:
                        neighbor[v1.id] = val2
                        neighbor[v2.id] = val1
                    else:
                        continue

                # Validate candidate
                _, cand_hard, _ = self.validator.validate_assignment(neighbor, var_map, check_completeness=True)

                # If requested to preserve hard constraints (e.g. in hybrid mode), reject any new hard violation
                if preserve_hard_constraints and current_hard == 0 and cand_hard > 0:
                    continue

                cand_soft, _, _ = self.cost_fn.evaluate_soft_penalties(neighbor, var_map)
                cand_cost = self.cost_fn.compute_total_cost(cand_hard, cand_soft)

                delta_e = cand_cost - current_cost

                # Metropolis Acceptance Criterion
                accept = False
                if delta_e <= 0:
                    accept = True
                else:
                    probability = math.exp(-delta_e / max(temperature, 1e-6))
                    if random.random() < probability:
                        accept = True

                if accept:
                    current = neighbor
                    current_cost = cand_cost
                    current_hard = cand_hard
                    current_soft = cand_soft

                    if current_cost < best_cost:
                        best_cost = current_cost
                        best_assignment = dict(current)
                        best_hard = current_hard
                        best_soft = current_soft

                cost_history.append(current_cost)

            temperature *= self.cooling_rate

        elapsed = time.time() - start_time
        is_feasible = (best_hard == 0)

        return SolverResult(
            algorithm="Simulated Annealing",
            success=is_feasible,
            execution_time_seconds=elapsed,
            iterations=total_iterations,
            hard_violations=best_hard,
            soft_penalty=best_soft,
            total_cost=best_cost,
            cost_history=cost_history,
            assignment=best_assignment,
            diagnostic_message=f"SA finished with cost {best_cost} (Hard violations: {best_hard}, Soft penalty: {best_soft})"
        )
