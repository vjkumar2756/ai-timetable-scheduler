"""
core/backtracking.py
Complete Backtracking CSP Solvers Suite:
1. PlainBacktrackingSolver (Baseline Algorithm 1)
2. ImprovedBacktrackingSolver (Heuristic Algorithm 2: MRV, Degree, Forward Checking, LCV, AC-3)

Pure Python module (zero web/DB/Streamlit dependencies).

Academic Notes (For Project Viva / Demo):
- MRV (Minimum Remaining Values): Selects the variable with the fewest remaining legal values
  ("most constrained variable" heuristic). Fails fast if a variable is near-impossible to satisfy.
- Degree Heuristic: Breaks ties in MRV by choosing the variable involved in the largest number of
  constraints on other unassigned variables ("most constraining variable" heuristic).
- Forward Checking (FC): Whenever variable X is assigned, prunes conflicting values from domains
  of all unassigned neighbors. If any neighbor's domain is wiped out (size 0), immediately backtracks.
- Domain Restoration: All domain changes made during Forward Checking are recorded on a stack
  and restored precisely when backtracking.
- LCV (Least Constraining Value): Tries values that leave the maximum flexibility for neighboring variables.
- AC-3 (Arc Consistency 3): Preprocessing step that eliminates values from domains that have no
  support in neighboring domains before search even begins.
"""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict, deque
from core.problem import TimetableProblem, LectureVariable, SlotValue
from core.validator import ConstraintValidator, ValidationResult

@dataclass
class SolverResult:
    """Standardized result returned by all SchedulAI solvers."""
    algorithm: str
    success: bool
    runtime_seconds: float
    nodes_expanded: int
    backtracks_count: int
    hard_violations: int
    soft_penalty: int
    total_cost: int
    assignment: Dict[str, SlotValue] = field(default_factory=dict)
    diagnostic_message: str = ""
    cost_history: List[int] = field(default_factory=list)

class PlainBacktrackingSolver:
    """
    Baseline Plain Backtracking CSP Solver.
    Uses natural chronological order without MRV, Degree, or Forward Checking.
    """
    def __init__(self, problem: TimetableProblem, validator: ConstraintValidator):
        self.problem = problem
        self.validator = validator
        self.nodes_expanded = 0
        self.backtracks_count = 0
        self.start_time = 0.0
        self.time_limit = 30.0
        self.max_nodes = 100000

    def solve(
        self,
        time_limit_seconds: float = 30.0,
        max_nodes: int = 100000
    ) -> SolverResult:
        """Executes systematic chronological depth-first search with backtracking."""
        self.nodes_expanded = 0
        self.backtracks_count = 0
        self.time_limit = time_limit_seconds
        self.max_nodes = max_nodes
        self.start_time = time.time()

        variables = self.problem.variables
        assignment: Dict[str, SlotValue] = {}

        teacher_busy: Set[Tuple[str, str, int]] = set()
        class_busy: Set[Tuple[str, str, int]] = set()
        room_busy: Set[Tuple[str, str, int]] = set()

        success = self._backtrack(0, variables, assignment, teacher_busy, class_busy, room_busy)
        elapsed = time.time() - self.start_time

        if success:
            val_res = self.validator.validate(assignment, self.problem.variables_dict, check_completeness=True)
            return SolverResult(
                algorithm="Plain Backtracking (Baseline)",
                success=val_res.is_valid,
                runtime_seconds=round(elapsed, 4),
                nodes_expanded=self.nodes_expanded,
                backtracks_count=self.backtracks_count,
                hard_violations=val_res.hard_violations_count,
                soft_penalty=val_res.soft_penalties_count,
                total_cost=val_res.total_cost,
                assignment=assignment,
                diagnostic_message=(
                    "Feasible conflict-free schedule found." if val_res.is_valid
                    else f"Completed with {val_res.hard_violations_count} violation(s)."
                )
            )
        else:
            timed_out = (time.time() - self.start_time) >= self.time_limit
            node_limit = self.nodes_expanded >= self.max_nodes
            msg = (
                "Search limit reached: Timeout cutoff exceeded." if timed_out
                else "Search limit reached: Maximum node expansion cutoff reached." if node_limit
                else "Search space exhausted: Infeasible under current formulation."
            )
            return SolverResult(
                algorithm="Plain Backtracking (Baseline)",
                success=False,
                runtime_seconds=round(elapsed, 4),
                nodes_expanded=self.nodes_expanded,
                backtracks_count=self.backtracks_count,
                hard_violations=len(variables),
                soft_penalty=0,
                total_cost=1000 * len(variables),
                assignment=assignment,
                diagnostic_message=msg
            )

    def _backtrack(
        self,
        var_idx: int,
        variables: List[LectureVariable],
        assignment: Dict[str, SlotValue],
        teacher_busy: Set[Tuple[str, str, int]],
        class_busy: Set[Tuple[str, str, int]],
        room_busy: Set[Tuple[str, str, int]]
    ) -> bool:
        """Recursive DFS step in natural variable order."""
        if var_idx >= len(variables):
            return True

        self.nodes_expanded += 1
        if self.nodes_expanded >= self.max_nodes or (time.time() - self.start_time) > self.time_limit:
            return False

        var = variables[var_idx]
        domain = self.problem.domains.get(var.id, [])

        for slot in domain:
            occupied = slot.occupied_periods(var.duration)

            if any((slot.teacher_id, slot.day, p) in teacher_busy for p in occupied):
                continue
            if any((var.class_id, slot.day, p) in class_busy for p in occupied):
                continue
            if any((slot.room_id, slot.day, p) in room_busy for p in occupied):
                continue

            assignment[var.id] = slot
            for p in occupied:
                teacher_busy.add((slot.teacher_id, slot.day, p))
                class_busy.add((var.class_id, slot.day, p))
                room_busy.add((slot.room_id, slot.day, p))

            if self._backtrack(var_idx + 1, variables, assignment, teacher_busy, class_busy, room_busy):
                return True

            self.backtracks_count += 1
            del assignment[var.id]
            for p in occupied:
                teacher_busy.remove((slot.teacher_id, slot.day, p))
                class_busy.remove((var.class_id, slot.day, p))
                room_busy.remove((slot.room_id, slot.day, p))

        return False

class ImprovedBacktrackingSolver:
    """
    Improved Backtracking CSP Solver with modular heuristic controls:
    - MRV: Minimum Remaining Values variable selection
    - Degree Heuristic: Tie-breaker for MRV
    - Forward Checking (FC): Domain reduction with complete restoration
    - LCV: Least Constraining Value value ordering
    - AC-3: Arc Consistency 3 preprocessing
    """
    def __init__(
        self,
        problem: TimetableProblem,
        validator: ConstraintValidator,
        use_mrv: bool = True,
        use_degree: bool = True,
        use_forward_checking: bool = True,
        use_lcv: bool = False,
        use_ac3: bool = False
    ):
        self.problem = problem
        self.validator = validator
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_fc = use_forward_checking
        self.use_lcv = use_lcv
        self.use_ac3 = use_ac3

        self.nodes_expanded = 0
        self.backtracks_count = 0
        self.start_time = 0.0
        self.time_limit = 30.0
        self.max_nodes = 100000

        # Precompute constraint graph: var_id -> list of neighboring var_ids
        self.neighbors: Dict[str, List[str]] = defaultdict(list)
        self._build_constraint_graph()

    def _build_constraint_graph(self):
        """Constructs adjacency graph where an edge exists if two sessions share a class or teacher."""
        variables = self.problem.variables
        for i in range(len(variables)):
            v1 = variables[i]
            for j in range(i + 1, len(variables)):
                v2 = variables[j]
                # Direct binary clash if they share class_id or teacher_id
                if v1.class_id == v2.class_id or v1.teacher_id == v2.teacher_id:
                    self.neighbors[v1.id].append(v2.id)
                    self.neighbors[v2.id].append(v1.id)

    def solve(
        self,
        time_limit_seconds: float = 30.0,
        max_nodes: int = 100000
    ) -> SolverResult:
        """Executes heuristic-guided depth-first search."""
        self.nodes_expanded = 0
        self.backtracks_count = 0
        self.time_limit = time_limit_seconds
        self.max_nodes = max_nodes
        self.start_time = time.time()

        # Copy initial domains
        current_domains = {v.id: list(self.problem.domains[v.id]) for v in self.problem.variables}

        # Optional AC-3 Preprocessing
        if self.use_ac3:
            current_domains = self._run_ac3(current_domains)

        assignment: Dict[str, SlotValue] = {}
        unassigned: Set[str] = {v.id for v in self.problem.variables}

        # Track period occupancy for fast clash checks: (entity_id, day, period)
        teacher_busy: Set[Tuple[str, str, int]] = set()
        class_busy: Set[Tuple[str, str, int]] = set()
        room_busy: Set[Tuple[str, str, int]] = set()

        success = self._backtrack(
            assignment, unassigned, current_domains,
            teacher_busy, class_busy, room_busy
        )
        elapsed = time.time() - self.start_time

        heuristics_used = []
        if self.use_mrv: heuristics_used.append("MRV")
        if self.use_degree: heuristics_used.append("Degree")
        if self.use_fc: heuristics_used.append("FC")
        if self.use_lcv: heuristics_used.append("LCV")
        if self.use_ac3: heuristics_used.append("AC-3")
        label = f"Improved Backtracking ({'+'.join(heuristics_used) if heuristics_used else 'Basic'})"

        if success:
            val_res = self.validator.validate(assignment, self.problem.variables_dict, check_completeness=True)
            return SolverResult(
                algorithm=label,
                success=val_res.is_valid,
                runtime_seconds=round(elapsed, 4),
                nodes_expanded=self.nodes_expanded,
                backtracks_count=self.backtracks_count,
                hard_violations=val_res.hard_violations_count,
                soft_penalty=val_res.soft_penalties_count,
                total_cost=val_res.total_cost,
                assignment=assignment,
                diagnostic_message=(
                    "Optimal conflict-free schedule found." if val_res.is_valid
                    else f"Completed with {val_res.hard_violations_count} violation(s)."
                )
            )
        else:
            timed_out = (time.time() - self.start_time) >= self.time_limit
            node_limit = self.nodes_expanded >= self.max_nodes
            msg = (
                "Search limit reached: Timeout cutoff exceeded." if timed_out
                else "Search limit reached: Maximum node expansion cutoff reached." if node_limit
                else "Search space exhausted: Infeasible under current formulation."
            )
            return SolverResult(
                algorithm=label,
                success=False,
                runtime_seconds=round(elapsed, 4),
                nodes_expanded=self.nodes_expanded,
                backtracks_count=self.backtracks_count,
                hard_violations=len(self.problem.variables),
                soft_penalty=0,
                total_cost=1000 * len(self.problem.variables),
                assignment=assignment,
                diagnostic_message=msg
            )

    def _select_variable(self, unassigned: Set[str], current_domains: Dict[str, List[SlotValue]]) -> str:
        """
        Variable selection using MRV (Minimum Remaining Values)
        with Degree Heuristic as tie-breaker.
        """
        if not self.use_mrv:
            return next(iter(unassigned))

        # MRV: Find minimum domain size
        min_size = float("inf")
        candidates: List[str] = []

        for v_id in unassigned:
            size = len(current_domains[v_id])
            if size < min_size:
                min_size = size
                candidates = [v_id]
            elif size == min_size:
                candidates.append(v_id)

        if len(candidates) == 1 or not self.use_degree:
            return candidates[0]

        # Degree Heuristic tie-breaker: Variable with most unassigned neighbors
        def degree(v_id: str) -> int:
            return sum(1 for nbr in self.neighbors[v_id] if nbr in unassigned)

        return max(candidates, key=degree)

    def _order_domain_values(
        self,
        var_id: str,
        current_domains: Dict[str, List[SlotValue]],
        unassigned: Set[str]
    ) -> List[SlotValue]:
        """
        Value ordering using LCV (Least Constraining Value) or standard order.
        """
        domain = current_domains[var_id]
        if not self.use_lcv or len(domain) <= 1:
            return domain

        var = self.problem.variables_dict[var_id]

        def count_conflicts(slot: SlotValue) -> int:
            occupied = slot.occupied_periods(var.duration)
            conflicts = 0
            for nbr_id in self.neighbors[var_id]:
                if nbr_id in unassigned:
                    nbr_var = self.problem.variables_dict[nbr_id]
                    for nbr_slot in current_domains[nbr_id]:
                        nbr_occ = nbr_slot.occupied_periods(nbr_var.duration)
                        # Check day and overlapping periods
                        if slot.day == nbr_slot.day and any(p in nbr_occ for p in occupied):
                            if (var.class_id == nbr_var.class_id or
                                slot.teacher_id == nbr_slot.teacher_id or
                                slot.room_id == nbr_slot.room_id):
                                conflicts += 1
            return conflicts

        return sorted(domain, key=count_conflicts)

    def _backtrack(
        self,
        assignment: Dict[str, SlotValue],
        unassigned: Set[str],
        current_domains: Dict[str, List[SlotValue]],
        teacher_busy: Set[Tuple[str, str, int]],
        class_busy: Set[Tuple[str, str, int]],
        room_busy: Set[Tuple[str, str, int]]
    ) -> bool:
        """Recursive backtracking step with MRV, Degree, and Forward Checking."""
        if not unassigned:
            return True

        self.nodes_expanded += 1
        if self.nodes_expanded >= self.max_nodes or (time.time() - self.start_time) > self.time_limit:
            return False

        var_id = self._select_variable(unassigned, current_domains)
        var = self.problem.variables_dict[var_id]
        ordered_values = self._order_domain_values(var_id, current_domains, unassigned)

        for slot in ordered_values:
            occupied = slot.occupied_periods(var.duration)

            # Local binary consistency check
            if any((slot.teacher_id, slot.day, p) in teacher_busy for p in occupied):
                continue
            if any((var.class_id, slot.day, p) in class_busy for p in occupied):
                continue
            if any((slot.room_id, slot.day, p) in room_busy for p in occupied):
                continue

            # Assign
            assignment[var_id] = slot
            unassigned.remove(var_id)
            for p in occupied:
                teacher_busy.add((slot.teacher_id, slot.day, p))
                class_busy.add((var.class_id, slot.day, p))
                room_busy.add((slot.room_id, slot.day, p))

            # Forward Checking: prune incompatible slots from unassigned variables
            pruned: Dict[str, List[SlotValue]] = defaultdict(list)
            wipeout = False

            if self.use_fc:
                for nbr_id in self.neighbors[var_id]:
                    if nbr_id in unassigned:
                        nbr_var = self.problem.variables_dict[nbr_id]
                        new_nbr_domain = []
                        for nbr_slot in current_domains[nbr_id]:
                            nbr_occ = nbr_slot.occupied_periods(nbr_var.duration)
                            clash = (
                                slot.day == nbr_slot.day and
                                any(p in nbr_occ for p in occupied) and
                                (var.class_id == nbr_var.class_id or
                                 slot.teacher_id == nbr_slot.teacher_id or
                                 slot.room_id == nbr_slot.room_id)
                            )
                            if clash:
                                pruned[nbr_id].append(nbr_slot)
                            else:
                                new_nbr_domain.append(nbr_slot)

                        current_domains[nbr_id] = new_nbr_domain
                        if len(new_nbr_domain) == 0:
                            wipeout = True
                            break

            if not wipeout:
                if self._backtrack(assignment, unassigned, current_domains, teacher_busy, class_busy, room_busy):
                    return True

            # Backtrack & restore state
            self.backtracks_count += 1
            if self.use_fc:
                for nbr_id, removed_slots in pruned.items():
                    current_domains[nbr_id].extend(removed_slots)

            del assignment[var_id]
            unassigned.add(var_id)
            for p in occupied:
                teacher_busy.remove((slot.teacher_id, slot.day, p))
                class_busy.remove((var.class_id, slot.day, p))
                room_busy.remove((slot.room_id, slot.day, p))

        return False

    def _run_ac3(self, domains: Dict[str, List[SlotValue]]) -> Dict[str, List[SlotValue]]:
        """AC-3 Arc Consistency Preprocessing."""
        queue = deque()
        for v1_id in self.problem.variables_dict:
            for v2_id in self.neighbors[v1_id]:
                queue.append((v1_id, v2_id))

        while queue:
            xi_id, xj_id = queue.popleft()
            if self._revise(domains, xi_id, xj_id):
                if len(domains[xi_id]) == 0:
                    return domains  # Inconsistency detected
                for xk_id in self.neighbors[xi_id]:
                    if xk_id != xj_id:
                        queue.append((xk_id, xi_id))
        return domains

    def _revise(self, domains: Dict[str, List[SlotValue]], xi_id: str, xj_id: str) -> bool:
        """Removes values from D(xi) that have no consistent partner in D(xj)."""
        revised = False
        v_i = self.problem.variables_dict[xi_id]
        v_j = self.problem.variables_dict[xj_id]
        new_domain = []

        for slot_i in domains[xi_id]:
            occ_i = slot_i.occupied_periods(v_i.duration)
            has_support = False
            for slot_j in domains[xj_id]:
                occ_j = slot_j.occupied_periods(v_j.duration)
                clash = (
                    slot_i.day == slot_j.day and
                    any(p in occ_j for p in occ_i) and
                    (v_i.class_id == v_j.class_id or
                     slot_i.teacher_id == slot_j.teacher_id or
                     slot_i.room_id == slot_j.room_id)
                )
                if not clash:
                    has_support = True
                    break
            if has_support:
                new_domain.append(slot_i)
            else:
                revised = True

        domains[xi_id] = new_domain
        return revised
