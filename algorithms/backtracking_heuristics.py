"""
Backtracking with Heuristics Solver.
Supports independent toggle controls for:
1. Minimum Remaining Values (MRV)
2. Degree Heuristic
3. Forward Checking (FC)
4. Least Constraining Value (LCV)
5. AC-3 Domain Pruning Preprocessor
"""
import time
from typing import Dict, List, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.csp import LectureVariable, SlotValue
from backend.app.scheduler.metrics import SolverResult

class BacktrackingWithHeuristicsSolver(BaseSolver):
    """
    Backtracking solver with modular heuristic toggles (MRV, Degree, FC, LCV, AC-3).
    """
    def __init__(self, csp, validator, cost_fn, config=None, seed=42):
        super().__init__(csp, validator, cost_fn, config, seed)
        cfg = self.config
        self.use_mrv = cfg.get("use_mrv", True)
        self.use_degree = cfg.get("use_degree", True)
        self.use_fc = cfg.get("use_forward_checking", True)
        self.use_lcv = cfg.get("use_lcv", True)
        self.use_ac3 = cfg.get("use_ac3", False)
        self.nodes_expanded = 0
        self.start_time = 0.0
        self.time_limit = 30.0

    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        self.nodes_expanded = 0
        self.time_limit = timeout_seconds
        self.start_time = time.time()
        var_map = self.csp.get_variable_map()
        
        # Deepcopy domains
        current_domains = {v.id: list(self.csp.domains[v.id]) for v in self.csp.variables}

        # Optional AC-3 Preprocessing
        if self.use_ac3:
            current_domains = self._run_ac3_preprocessing(current_domains, var_map)

        assignment: Dict[str, SlotValue] = {}
        success = self._backtrack(assignment, current_domains, var_map)
        elapsed = time.time() - self.start_time

        active_heuristics = []
        if self.use_mrv: active_heuristics.append("MRV")
        if self.use_degree: active_heuristics.append("Degree")
        if self.use_fc: active_heuristics.append("FC")
        if self.use_lcv: active_heuristics.append("LCV")
        if self.use_ac3: active_heuristics.append("AC-3")
        label = f"Backtracking + Heuristics ({'+'.join(active_heuristics) if active_heuristics else 'None'})"

        if success:
            is_valid, hard_count, violations = self.validator.validate_assignment(assignment, var_map)
            soft_pen, _, _ = self.cost_fn.evaluate_soft_penalties(assignment, var_map)
            total_cost = self.cost_fn.compute_total_cost(hard_count, soft_pen)
            return SolverResult(
                algorithm=label,
                success=is_valid,
                execution_time_seconds=elapsed,
                nodes_expanded=self.nodes_expanded,
                hard_violations=hard_count,
                soft_penalty=soft_pen,
                total_cost=total_cost,
                assignment=assignment,
                diagnostic_message="Feasible timetable found" if is_valid else "Violations detected"
            )
        else:
            timed_out = elapsed >= self.time_limit
            msg = "Search limit reached (timeout)" if timed_out else "Infeasible: search space exhausted"
            return SolverResult(
                algorithm=label,
                success=False,
                execution_time_seconds=elapsed,
                nodes_expanded=self.nodes_expanded,
                hard_violations=len(self.csp.variables),
                diagnostic_message=msg
            )

    def _run_ac3_preprocessing(self, domains, var_map):
        """Simple AC-3 domain consistency arc pruning"""
        for v in self.csp.variables:
            valid_vals = []
            for val in domains[v.id]:
                if self.validator.is_consistent(v, val, {}, var_map):
                    valid_vals.append(val)
            domains[v.id] = valid_vals
        return domains

    def _select_unassigned_variable(self, assignment, domains, var_map):
        unassigned = [v for v in self.csp.variables if v.id not in assignment]
        if not unassigned:
            return None

        if not self.use_mrv:
            return unassigned[0]

        min_len = min(len(domains[v.id]) for v in unassigned)
        candidates = [v for v in unassigned if len(domains[v.id]) == min_len]
        if len(candidates) == 1 or not self.use_degree:
            return candidates[0]

        # Degree tie breaking
        def deg(v):
            return sum(1 for o in unassigned if o.id != v.id and (o.class_id == v.class_id or o.subject_id == v.subject_id))

        return max(candidates, key=deg)

    def _order_domain_values(self, var, domains, assignment, var_map):
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

        if not self.use_lcv:
            return sorted(values, key=lambda val: (1 if val.day in occupied_days else 0))

        unassigned = [v for v in self.csp.variables if v.id not in assignment and v.id != var.id]
        var_occ = lambda val: range(val.period, val.period + var.duration)

        def eliminated_choices(val):
            occ = var_occ(val)
            elim = 0
            for u in unassigned:
                for u_val in domains[u.id]:
                    if u_val.day == val.day:
                        if u_val.teacher_id == val.teacher_id or u.class_id == var.class_id or u_val.room_id == val.room_id:
                            if any(p in occ for p in range(u_val.period, u_val.period + u.duration)):
                                elim += 1
            return elim

        def value_rank(val):
            # Day repeat penalty (S2: avoid same subject twice on same day unless lab)
            day_pen = 1 if val.day in occupied_days else 0
            return (day_pen, eliminated_choices(val))

        return sorted(values, key=value_rank)

    def _forward_check(self, var, val, domains, assignment, var_map):
        if not self.use_fc:
            return domains

        pruned = {}
        var_occ = range(val.period, val.period + var.duration)

        for u in self.csp.variables:
            if u.id in assignment or u.id == var.id:
                continue

            valid_for_u = []
            for u_val in domains[u.id]:
                if u_val.day == val.day:
                    same_t = (u_val.teacher_id == val.teacher_id)
                    same_c = (u.class_id == var.class_id)
                    same_r = (u_val.room_id == val.room_id)
                    if same_t or same_c or same_r:
                        u_occ = range(u_val.period, u_val.period + u.duration)
                        if any(p in var_occ for p in u_occ):
                            continue
                valid_for_u.append(u_val)

            if not valid_for_u:
                return None  # Domain wipeout
            pruned[u.id] = valid_for_u

        return {k: pruned.get(k, domains[k]) for k in domains}

    def _backtrack(self, assignment, domains, var_map):
        if time.time() - self.start_time > self.time_limit:
            return False

        if len(assignment) == len(self.csp.variables):
            return True

        var = self._select_unassigned_variable(assignment, domains, var_map)
        if not var:
            return False

        self.nodes_expanded += 1
        ordered_vals = self._order_domain_values(var, domains, assignment, var_map)

        for val in ordered_vals:
            if self.validator.is_consistent(var, val, assignment, var_map):
                assignment[var.id] = val
                pruned_domains = self._forward_check(var, val, domains, assignment, var_map)
                if pruned_domains is not None:
                    if self._backtrack(assignment, pruned_domains, var_map):
                        return True
                del assignment[var.id]

        return False
