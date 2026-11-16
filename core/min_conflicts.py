"""
core/min_conflicts.py
Min-Conflicts Local Search Algorithm (Algorithm 3 in SchedulAI).
Pure Python module (zero web/DB/Streamlit dependencies).

Academic Notes (For Project Viva / Demo):
- Paradigm: Local search / Iterative Repair.
- Initial State: Complete assignment of all variables (unlike backtracking which builds partial assignments).
- Variable Selection: Chooses randomly from among currently conflicted variables.
- Value Selection: Chooses the value that minimizes conflicts (ties broken randomly).
- Plateau Escape:
  1. Random Walk: With probability p ~ 0.08, picks a uniformly random domain value instead of the min-conflict value.
  2. Random Restart: Reinitializes complete assignment if search remains stagnant.
- Convergence: Tracks cost_history across iterations for Plotly convergence visualization.
"""
import time
import random
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict
from core.problem import TimetableProblem, LectureVariable, SlotValue
from core.validator import ConstraintValidator, ValidationResult
from core.backtracking import SolverResult

class MinConflictsSolver:
    """
    Min-Conflicts local search solver with random walk and random restart plateau escapes.
    """
    def __init__(
        self,
        problem: TimetableProblem,
        validator: ConstraintValidator,
        max_iterations: int = 1500,
        random_walk_prob: float = 0.08,
        max_restarts: int = 3,
        seed: Optional[int] = 42
    ):
        self.problem = problem
        self.validator = validator
        self.max_iterations = max_iterations
        self.random_walk_prob = random_walk_prob
        self.max_restarts = max_restarts
        self.seed = seed

    def solve(
        self,
        time_limit_seconds: float = 30.0,
        seed: Optional[int] = None
    ) -> SolverResult:
        """
        Executes Min-Conflicts iterative repair search.
        Returns SolverResult with full cost_history for convergence plotting.
        """
        run_seed = seed if seed is not None else self.seed
        if run_seed is not None:
            random.seed(run_seed)

        start_time = time.time()
        variables = self.problem.variables
        variables_dict = self.problem.variables_dict

        best_assignment: Dict[str, SlotValue] = {}
        best_cost = float("inf")
        best_hard_violations = float("inf")
        cost_history: List[int] = []
        total_iterations = 0

        for restart_idx in range(self.max_restarts + 1):
            if (time.time() - start_time) > time_limit_seconds:
                break

            # 1. Complete Initial Assignment (greedy min-conflict initialization)
            current_assignment = self._initialize_assignment()

            for step in range(self.max_iterations):
                if (time.time() - start_time) > time_limit_seconds:
                    break
                total_iterations += 1

                # 2. Count conflicts per variable
                conflicted_vars = self._get_conflicted_variables(current_assignment)

                # Authoritative full evaluation
                val_res = self.validator.validate(current_assignment, variables_dict, check_completeness=True)
                cost_history.append(val_res.total_cost)

                if val_res.total_cost < best_cost:
                    best_cost = val_res.total_cost
                    best_hard_violations = val_res.hard_violations_count
                    best_assignment = dict(current_assignment)

                # Goal test: Zero hard violations reached!
                if val_res.is_valid:
                    elapsed = time.time() - start_time
                    return SolverResult(
                        algorithm="Min-Conflicts Local Search",
                        success=True,
                        runtime_seconds=round(elapsed, 4),
                        nodes_expanded=total_iterations,
                        backtracks_count=restart_idx,
                        hard_violations=0,
                        soft_penalty=val_res.soft_penalties_count,
                        total_cost=val_res.total_cost,
                        assignment=current_assignment,
                        diagnostic_message=f"Conflict-free schedule found in {total_iterations} iterations (Restart #{restart_idx}).",
                        cost_history=cost_history
                    )

                if not conflicted_vars:
                    break

                # 3. Pick a random conflicted variable
                chosen_var = random.choice(conflicted_vars)
                domain = self.problem.domains.get(chosen_var.id, [])
                if not domain:
                    continue

                # 4. Plateau Escape: Random Walk with probability p
                if random.random() < self.random_walk_prob:
                    current_assignment[chosen_var.id] = random.choice(domain)
                else:
                    # 5. Min-Conflict Value Selection (with random tie-breaking)
                    min_conf = float("inf")
                    best_slots = []
                    for slot in domain:
                        c = self._count_conflicts_for_variable(chosen_var, slot, current_assignment)
                        if c < min_conf:
                            min_conf = c
                            best_slots = [slot]
                        elif c == min_conf:
                            best_slots.append(slot)

                    current_assignment[chosen_var.id] = random.choice(best_slots)

        elapsed = time.time() - start_time
        is_success = (best_hard_violations == 0)

        # Cross-validate best assignment
        final_val = self.validator.validate(best_assignment, variables_dict, check_completeness=True)

        return SolverResult(
            algorithm="Min-Conflicts Local Search",
            success=is_success,
            runtime_seconds=round(elapsed, 4),
            nodes_expanded=total_iterations,
            backtracks_count=self.max_restarts,
            hard_violations=final_val.hard_violations_count,
            soft_penalty=final_val.soft_penalties_count,
            total_cost=final_val.total_cost,
            assignment=best_assignment,
            diagnostic_message=(
                f"Completed {total_iterations} iterations across {self.max_restarts} restarts. "
                f"Best hard violations: {final_val.hard_violations_count}."
            ),
            cost_history=cost_history
        )

    def _initialize_assignment(self) -> Dict[str, SlotValue]:
        """Greedy complete assignment that picks domain values minimizing initial clash."""
        assignment: Dict[str, SlotValue] = {}
        for var in self.problem.variables:
            domain = self.problem.domains.get(var.id, [])
            if not domain:
                continue
            min_c = float("inf")
            best_candidates = []
            for slot in domain:
                c = self._count_conflicts_for_variable(var, slot, assignment)
                if c < min_c:
                    min_c = c
                    best_candidates = [slot]
                elif c == min_c:
                    best_candidates.append(slot)
            assignment[var.id] = random.choice(best_candidates) if best_candidates else domain[0]
        return assignment

    def _get_conflicted_variables(self, assignment: Dict[str, SlotValue]) -> List[LectureVariable]:
        """Finds all variables currently involved in at least one hard clash."""
        conflicted: List[LectureVariable] = []
        for var in self.problem.variables:
            slot = assignment.get(var.id)
            if slot and self._count_conflicts_for_variable(var, slot, assignment, exclude_self=True) > 0:
                conflicted.append(var)
        return conflicted

    def _count_conflicts_for_variable(
        self,
        var: LectureVariable,
        slot: SlotValue,
        assignment: Dict[str, SlotValue],
        exclude_self: bool = False
    ) -> int:
        """Fast conflict counter for candidate slot assignment."""
        occupied = slot.occupied_periods(var.duration)
        conflicts = 0

        for other_id, other_slot in assignment.items():
            if exclude_self and other_id == var.id:
                continue
            if other_id == var.id:
                continue

            other_var = self.problem.variables_dict[other_id]
            if slot.day != other_slot.day:
                continue

            other_occ = other_slot.occupied_periods(other_var.duration)
            overlap = any(p in other_occ for p in occupied)
            if not overlap:
                continue

            # H1: Same teacher overlap
            if slot.teacher_id == other_slot.teacher_id:
                conflicts += 1
            # H2: Same class overlap
            if var.class_id == other_var.class_id:
                conflicts += 1
            # H3: Same room overlap
            if slot.room_id == other_slot.room_id:
                conflicts += 1

        return conflicts
