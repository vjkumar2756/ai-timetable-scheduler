import time
import copy
from typing import Dict, List, Optional, Set
from backend.app.scheduler.csp import TimetableCSP, LectureVariable, SlotValue
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.metrics import SolverResult

class PlainBacktrackingSolver:
    """
    Baseline CSP Backtracking Solver.
    Uses chronological variable ordering and static domain values without heuristics.
    """
    def __init__(self, csp: TimetableCSP, validator: ConstraintValidator, cost_fn: CostFunction):
        self.csp = csp
        self.validator = validator
        self.cost_fn = cost_fn
        self.nodes_expanded = 0
        self.start_time = 0.0
        self.time_limit = 30.0

    def solve(self, time_limit_seconds: float = 30.0) -> SolverResult:
        self.nodes_expanded = 0
        self.time_limit = time_limit_seconds
        self.start_time = time.time()
        var_map = self.csp.get_variable_map()
        variables = self.csp.variables
        assignment: Dict[str, SlotValue] = {}

        success = self._backtrack(0, variables, assignment, var_map)
        elapsed = time.time() - self.start_time

        if success:
            is_valid, hard_count, violations = self.validator.validate_assignment(assignment, var_map)
            soft_pen, _, _ = self.cost_fn.evaluate_soft_penalties(assignment, var_map)
            total_cost = self.cost_fn.compute_total_cost(hard_count, soft_pen)
            return SolverResult(
                algorithm="Plain Backtracking (Baseline)",
                success=is_valid,
                execution_time_seconds=elapsed,
                nodes_expanded=self.nodes_expanded,
                hard_violations=hard_count,
                soft_penalty=soft_pen,
                total_cost=total_cost,
                assignment=assignment,
                diagnostic_message="Feasible timetable found by plain backtracking" if is_valid else "Violations detected"
            )
        else:
            elapsed = time.time() - self.start_time
            timed_out = elapsed >= self.time_limit
            msg = "Search limit reached (timeout)" if timed_out else "Infeasible: search space exhausted"
            return SolverResult(
                algorithm="Plain Backtracking (Baseline)",
                success=False,
                execution_time_seconds=elapsed,
                nodes_expanded=self.nodes_expanded,
                hard_violations=len(variables),
                diagnostic_message=msg
            )

    def _backtrack(
        self,
        var_idx: int,
        variables: List[LectureVariable],
        assignment: Dict[str, SlotValue],
        var_map: Dict[str, LectureVariable]
    ) -> bool:
        if time.time() - self.start_time > self.time_limit:
            return False

        if var_idx == len(variables):
            return True

        var = variables[var_idx]
        self.nodes_expanded += 1

        for val in self.csp.domains[var.id]:
            if self.validator.is_consistent(var, val, assignment, var_map):
                assignment[var.id] = val
                if self._backtrack(var_idx + 1, variables, assignment, var_map):
                    return True
                del assignment[var.id]

        return False


class ImprovedBacktrackingSolver:
    """
    Optimized Backtracking CSP Solver featuring:
    1. Minimum Remaining Values (MRV) heuristic for variable selection
    2. Degree Heuristic for breaking MRV ties
    3. Forward Checking (FC) to prune domains of unassigned variables
    4. Least Constraining Value (LCV) heuristic for value ordering
    """
    def __init__(self, csp: TimetableCSP, validator: ConstraintValidator, cost_fn: CostFunction):
        self.csp = csp
        self.validator = validator
        self.cost_fn = cost_fn
        self.nodes_expanded = 0
        self.start_time = 0.0
        self.time_limit = 30.0

    def solve(self, time_limit_seconds: float = 30.0) -> SolverResult:
        self.nodes_expanded = 0
        self.time_limit = time_limit_seconds
        self.start_time = time.time()
        var_map = self.csp.get_variable_map()
        
        # Deepcopy domains so forward checking can prune and restore safely
        current_domains = {v.id: list(self.csp.domains[v.id]) for v in self.csp.variables}
        assignment: Dict[str, SlotValue] = {}

        success = self._backtrack_improved(assignment, current_domains, var_map)
        elapsed = time.time() - self.start_time

        if success:
            is_valid, hard_count, violations = self.validator.validate_assignment(assignment, var_map)
            soft_pen, _, _ = self.cost_fn.evaluate_soft_penalties(assignment, var_map)
            total_cost = self.cost_fn.compute_total_cost(hard_count, soft_pen)
            return SolverResult(
                algorithm="Improved Backtracking (MRV+FC+Degree+LCV)",
                success=is_valid,
                execution_time_seconds=elapsed,
                nodes_expanded=self.nodes_expanded,
                hard_violations=hard_count,
                soft_penalty=soft_pen,
                total_cost=total_cost,
                assignment=assignment,
                diagnostic_message="Optimal feasible timetable found with heuristics"
            )
        else:
            timed_out = elapsed >= self.time_limit
            msg = "Search limit reached (timeout)" if timed_out else "Infeasible: search space exhausted"
            return SolverResult(
                algorithm="Improved Backtracking (MRV+FC+Degree+LCV)",
                success=False,
                execution_time_seconds=elapsed,
                nodes_expanded=self.nodes_expanded,
                hard_violations=len(self.csp.variables),
                diagnostic_message=msg
            )

    def _select_unassigned_variable(
        self,
        assignment: Dict[str, SlotValue],
        domains: Dict[str, List[SlotValue]],
        var_map: Dict[str, LectureVariable]
    ) -> Optional[LectureVariable]:
        """
        MRV + Degree Heuristic:
        Picks unassigned variable with smallest domain size; breaks ties with degree heuristic.
        """
        unassigned = [v for v in self.csp.variables if v.id not in assignment]
        if not unassigned:
            return None

        # MRV: sort primarily by domain length
        min_domain_len = min(len(domains[v.id]) for v in unassigned)
        candidates = [v for v in unassigned if len(domains[v.id]) == min_domain_len]

        if len(candidates) == 1:
            return candidates[0]

        # Degree heuristic: break ties by number of constraints on remaining unassigned variables
        def calculate_degree(v: LectureVariable) -> int:
            deg = 0
            for other in unassigned:
                if other.id == v.id:
                    continue
                # Connected if same class, or common teachers
                if other.class_id == v.class_id:
                    deg += 1
            return deg

        return max(candidates, key=calculate_degree)

    def _order_domain_values(
        self,
        var: LectureVariable,
        domains: Dict[str, List[SlotValue]],
        assignment: Dict[str, SlotValue],
        var_map: Dict[str, LectureVariable]
    ) -> List[SlotValue]:
        """
        Soft-Aware Least Constraining Value (LCV) heuristic:
        1. Strictly optimizes S2: Prioritizes days where this subject is not yet scheduled for this class.
        2. Orders by fewest ruled-out choices for remaining unassigned variables.
        """
        values = domains[var.id]
        if len(values) <= 1:
            return values

        # S2: Track days where this class already has this non-lab subject scheduled
        occupied_days = set()
        if not var.is_lab:
            for aid, aslot in assignment.items():
                avar = var_map[aid]
                if avar.class_id == var.class_id and avar.subject_id == var.subject_id:
                    occupied_days.add(aslot.day)

        unassigned = [v for v in self.csp.variables if v.id not in assignment and v.id != var.id]
        var_occupied = lambda val: range(val.period, val.period + var.duration)

        def count_conflicts_caused(val: SlotValue) -> int:
            occ = var_occupied(val)
            eliminated = 0
            for u in unassigned:
                u_occ_test = lambda u_val: range(u_val.period, u_val.period + u.duration)
                for u_val in domains[u.id]:
                    if u_val.day == val.day:
                        if (u_val.teacher_id == val.teacher_id or 
                            u.class_id == var.class_id or 
                            u_val.room_id == val.room_id):
                            if any(p in occ for p in u_occ_test(u_val)):
                                eliminated += 1
            return eliminated

        def value_rank(val: SlotValue):
            # Day repeat penalty (S2: avoid same subject twice on same day unless lab)
            day_pen = 1 if val.day in occupied_days else 0
            return (day_pen, count_conflicts_caused(val))

        return sorted(values, key=value_rank)

    def _forward_check(
        self,
        var: LectureVariable,
        val: SlotValue,
        domains: Dict[str, List[SlotValue]],
        assignment: Dict[str, SlotValue],
        var_map: Dict[str, LectureVariable]
    ) -> Optional[Dict[str, List[SlotValue]]]:
        """
        Prunes values from remaining unassigned variables that conflict with var = val.
        Returns pruned values dict for restoration, or None if domain wipeout occurs.
        """
        pruned: Dict[str, List[SlotValue]] = {}
        occupied = range(val.period, val.period + var.duration)

        for other in self.csp.variables:
            if other.id in assignment or other.id == var.id:
                continue

            removed_for_other = []
            remaining_for_other = []

            for u_val in domains[other.id]:
                conflict = False
                if u_val.day == val.day:
                    u_occupied = range(u_val.period, u_val.period + other.duration)
                    if any(p in occupied for p in u_occupied):
                        if (u_val.teacher_id == val.teacher_id or
                            other.class_id == var.class_id or
                            u_val.room_id == val.room_id):
                            conflict = True

                if conflict:
                    removed_for_other.append(u_val)
                else:
                    remaining_for_other.append(u_val)

            if removed_for_other:
                pruned[other.id] = removed_for_other
                domains[other.id] = remaining_for_other
                if len(remaining_for_other) == 0:
                    # Domain wipeout! Restore and fail branch
                    self._restore_domains(domains, pruned)
                    return None

        return pruned

    def _restore_domains(
        self,
        domains: Dict[str, List[SlotValue]],
        pruned: Dict[str, List[SlotValue]]
    ):
        for vid, vals in pruned.items():
            domains[vid].extend(vals)

    def _backtrack_improved(
        self,
        assignment: Dict[str, SlotValue],
        domains: Dict[str, List[SlotValue]],
        var_map: Dict[str, LectureVariable]
    ) -> bool:
        if time.time() - self.start_time > self.time_limit:
            return False

        if len(assignment) == len(self.csp.variables):
            return True

        var = self._select_unassigned_variable(assignment, domains, var_map)
        if not var:
            return True

        self.nodes_expanded += 1
        ordered_values = self._order_domain_values(var, domains, assignment, var_map)

        for val in ordered_values:
            if self.validator.is_consistent(var, val, assignment, var_map):
                assignment[var.id] = val
                pruned = self._forward_check(var, val, domains, assignment, var_map)

                if pruned is not None:
                    if self._backtrack_improved(assignment, domains, var_map):
                        return True
                    self._restore_domains(domains, pruned)

                del assignment[var.id]

        return False
