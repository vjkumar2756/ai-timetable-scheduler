import time
import random
from typing import Dict, List, Optional, Tuple
from backend.app.scheduler.csp import TimetableCSP, LectureVariable, SlotValue
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.metrics import SolverResult

class MinConflictsSolver:
    """
    Min-Conflicts Local Search Algorithm.
    Features:
    1. Complete initial assignment (greedy min-conflict initialization)
    2. Random selection from among currently conflicted variables
    3. Value selection that minimizes hard conflicts (with tie-breaking)
    4. Plateau escape via Random Walk (p=0.08) and Random Restarts
    5. Cost history tracking for convergence graphs
    6. Seed control for deterministic reproducibility
    """
    def __init__(
        self,
        csp: TimetableCSP,
        validator: ConstraintValidator,
        cost_fn: CostFunction,
        max_iterations: int = 2000,
        random_walk_prob: float = 0.08,
        max_restarts: int = 5,
        seed: Optional[int] = 42
    ):
        self.csp = csp
        self.validator = validator
        self.cost_fn = cost_fn
        self.max_iterations = max_iterations
        self.random_walk_prob = random_walk_prob
        self.max_restarts = max_restarts
        self.seed = seed

    def solve(self, seed: Optional[int] = None) -> SolverResult:
        run_seed = seed if seed is not None else self.seed
        if run_seed is not None:
            random.seed(run_seed)

        start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables

        best_assignment: Dict[str, SlotValue] = {}
        best_cost = float("inf")
        best_hard_violations = float("inf")
        cost_history: List[int] = []
        total_iterations = 0

        for restart_idx in range(self.max_restarts + 1):
            # 1. Complete Initial Assignment (Greedy min-conflict)
            current_assignment = self._initialize_assignment(variables, var_map)

            for step in range(self.max_iterations):
                total_iterations += 1

                # Identify all conflicted variables
                conflicted_vars = []
                for var in variables:
                    c = self.validator.count_conflicts(var, current_assignment[var.id], current_assignment, var_map)
                    if c > 0:
                        conflicted_vars.append(var)

                # Authoritative validation check
                is_valid, hard_count, violations = self.validator.validate_assignment(
                    current_assignment, var_map, check_completeness=True
                )
                soft_pen, _, _ = self.cost_fn.evaluate_soft_penalties(current_assignment, var_map)
                current_cost = self.cost_fn.compute_total_cost(hard_count, soft_pen)
                cost_history.append(current_cost)

                if current_cost < best_cost:
                    best_cost = current_cost
                    best_hard_violations = hard_count
                    best_assignment = dict(current_assignment)

                # Goal test: Zero hard violations found!
                if is_valid:
                    elapsed = time.time() - start_time
                    return SolverResult(
                        algorithm="Min-Conflicts Local Search",
                        success=True,
                        execution_time_seconds=elapsed,
                        iterations=total_iterations,
                        restarts=restart_idx,
                        hard_violations=0,
                        soft_penalty=soft_pen,
                        total_cost=current_cost,
                        cost_history=cost_history,
                        assignment=current_assignment,
                        diagnostic_message=f"Feasible schedule found in {total_iterations} iterations"
                    )

                if not conflicted_vars:
                    break

                # 2. Pick a random conflicted variable
                chosen_var = random.choice(conflicted_vars)
                domain = self.csp.domains[chosen_var.id]
                if not domain:
                    continue

                # 3. Plateau Escape: Random Walk with probability p
                if random.random() < self.random_walk_prob:
                    current_assignment[chosen_var.id] = random.choice(domain)
                else:
                    # 4. Choose value that minimizes conflicts (with tie-breaking)
                    min_conflicts = float("inf")
                    best_vals = []
                    for val in domain:
                        conf = self.validator.count_conflicts(chosen_var, val, current_assignment, var_map)
                        if conf < min_conflicts:
                            min_conflicts = conf
                            best_vals = [val]
                        elif conf == min_conflicts:
                            best_vals.append(val)

                    # Random tie-breaking among best values
                    current_assignment[chosen_var.id] = random.choice(best_vals)

        # If loop finishes without 100% feasibility, report honestly
        elapsed = time.time() - start_time
        return SolverResult(
            algorithm="Min-Conflicts Local Search",
            success=(best_hard_violations == 0),
            execution_time_seconds=elapsed,
            iterations=total_iterations,
            restarts=self.max_restarts,
            hard_violations=int(best_hard_violations),
            soft_penalty=best_cost - (1000 * int(best_hard_violations)),
            total_cost=int(best_cost),
            cost_history=cost_history,
            assignment=best_assignment,
            diagnostic_message=f"Completed {total_iterations} iterations across {self.max_restarts} restarts. Best hard violations: {best_hard_violations}"
        )

    def _initialize_assignment(
        self,
        variables: List[LectureVariable],
        var_map: Dict[str, LectureVariable]
    ) -> Dict[str, SlotValue]:
        assignment: Dict[str, SlotValue] = {}
        for var in variables:
            domain = self.csp.domains[var.id]
            if not domain:
                continue
            # Greedy pick: choose domain value with lowest immediate conflicts
            min_c = float("inf")
            best_candidates = []
            for val in domain:
                c = self.validator.count_conflicts(var, val, assignment, var_map)
                if c < min_c:
                    min_c = c
                    best_candidates = [val]
                elif c == min_c:
                    best_candidates.append(val)
            assignment[var.id] = random.choice(best_candidates) if best_candidates else domain[0]
        return assignment
