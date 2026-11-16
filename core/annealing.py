"""
core/annealing.py
Simulated Annealing Local Search Algorithm (+6 Bonus Marks).
Pure Python module (zero web/DB/Streamlit dependencies).

Academic Notes (For Project Viva / Demo):
- Origin: Kirkpatrick et al. (1983), inspired by annealing in metallurgy where a material
  is heated and slowly cooled to minimize crystalline defects (energy).
- Acceptance Criterion (Metropolis-Hastings):
  - If a neighboring state has lower cost (ΔE < 0), ALWAYS accept it.
  - If a neighboring state has higher cost (ΔE >= 0), accept with Boltzmann probability:
    P = exp(-ΔE / T)
- Cooling Schedule: Geometric cooling T_{k+1} = alpha * T_k, where alpha is typically 0.94 - 0.98.
- Neighborhood Operators:
  1. Single Move: Relocate a variable to a different valid slot in its domain.
  2. Session Swap: Swap the assigned time slots of two compatible sessions.
  3. Room Change: Change only the room of a session without modifying its day or period.
- Standalone vs. Hybrid:
  Can run from scratch (random complete assignment) or polish a pre-existing 100% hard-valid
  schedule to aggressively optimize soft constraints (S1-S5).
"""
import time
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from core.problem import TimetableProblem, LectureVariable, SlotValue
from core.validator import ConstraintValidator, ValidationResult
from core.backtracking import SolverResult

class SimulatedAnnealingSolver:
    """
    Simulated Annealing local search solver with geometric cooling.
    """
    def __init__(
        self,
        problem: TimetableProblem,
        validator: ConstraintValidator,
        initial_temp: float = 80.0,
        cooling_rate: float = 0.95,
        min_temp: float = 0.5,
        steps_per_temp: int = 25,
        seed: Optional[int] = 42
    ):
        self.problem = problem
        self.validator = validator
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.steps_per_temp = steps_per_temp
        self.seed = seed

    def solve(
        self,
        initial_assignment: Optional[Dict[str, SlotValue]] = None,
        time_limit_seconds: float = 30.0,
        preserve_hard_constraints: bool = False,
        seed: Optional[int] = None
    ) -> SolverResult:
        """
        Executes Simulated Annealing optimization.
        If preserve_hard_constraints is True, strictly rejects moves that introduce hard clashes.
        """
        run_seed = seed if seed is not None else self.seed
        if run_seed is not None:
            random.seed(run_seed)

        start_time = time.time()
        variables = self.problem.variables
        variables_dict = self.problem.variables_dict

        # 1. Initialize assignment
        if initial_assignment:
            current = dict(initial_assignment)
        else:
            current = {v.id: random.choice(self.problem.domains[v.id]) for v in variables}

        # Initial evaluation
        curr_val = self.validator.validate(current, variables_dict, check_completeness=True)
        current_cost = curr_val.total_cost

        best_assignment = dict(current)
        best_cost = current_cost
        best_hard = curr_val.hard_violations_count

        cost_history: List[int] = [current_cost]
        T = self.initial_temp
        total_iterations = 0

        # 2. Annealing Loop
        while T > self.min_temp:
            if (time.time() - start_time) > time_limit_seconds:
                break

            for _ in range(self.steps_per_temp):
                if (time.time() - start_time) > time_limit_seconds:
                    break
                total_iterations += 1

                # Generate neighborhood candidate move
                candidate = dict(current)
                move_type = random.random()

                if move_type < 0.70 or len(variables) < 2:
                    # Move 1: Single session relocation
                    v = random.choice(variables)
                    domain = self.problem.domains.get(v.id, [])
                    if len(domain) > 1:
                        new_slot = random.choice(domain)
                        candidate[v.id] = new_slot
                else:
                    # Move 2: Swap two compatible sessions
                    v1, v2 = random.sample(variables, 2)
                    if v1.duration == v2.duration:
                        # Swap time components
                        slot1 = candidate[v1.id]
                        slot2 = candidate[v2.id]
                        # Verify slots exist in respective domains
                        dom1_slots = {(s.day, s.period, s.room_id) for s in self.problem.domains.get(v1.id, [])}
                        dom2_slots = {(s.day, s.period, s.room_id) for s in self.problem.domains.get(v2.id, [])}

                        can_swap_1 = (slot2.day, slot2.period, slot2.room_id) in dom1_slots
                        can_swap_2 = (slot1.day, slot1.period, slot1.room_id) in dom2_slots

                        if can_swap_1 and can_swap_2:
                            candidate[v1.id] = SlotValue(
                                day=slot2.day, period=slot2.period,
                                room_id=slot2.room_id, teacher_id=slot1.teacher_id
                            )
                            candidate[v2.id] = SlotValue(
                                day=slot1.day, period=slot1.period,
                                room_id=slot1.room_id, teacher_id=slot2.teacher_id
                            )

                # Evaluate candidate move
                cand_val = self.validator.validate(candidate, variables_dict, check_completeness=True)
                
                # If preserving hard constraints (Stage 2 polishing mode), reject any hard breach
                if preserve_hard_constraints and cand_val.hard_violations_count > 0:
                    continue

                delta_e = cand_val.total_cost - current_cost

                # Metropolis acceptance criterion
                if delta_e < 0:
                    # Downhill move: Always accept
                    current = candidate
                    current_cost = cand_val.total_cost
                    if current_cost < best_cost:
                        best_cost = current_cost
                        best_hard = cand_val.hard_violations_count
                        best_assignment = dict(candidate)
                else:
                    # Uphill move: Accept with Boltzmann probability
                    p_accept = math.exp(-delta_e / max(0.01, T))
                    if random.random() < p_accept:
                        current = candidate
                        current_cost = cand_val.total_cost

            # Record cost after temperature step
            cost_history.append(current_cost)
            # Geometric cooling
            T *= self.cooling_rate

        elapsed = time.time() - start_time
        final_val = self.validator.validate(best_assignment, variables_dict, check_completeness=True)

        return SolverResult(
            algorithm="Simulated Annealing (+6 Bonus)",
            success=final_val.is_valid,
            runtime_seconds=round(elapsed, 4),
            nodes_expanded=total_iterations,
            backtracks_count=0,
            hard_violations=final_val.hard_violations_count,
            soft_penalty=final_val.soft_penalties_count,
            total_cost=final_val.total_cost,
            assignment=best_assignment,
            diagnostic_message=(
                f"Simulated Annealing completed in {total_iterations} iterations. "
                f"Final Cost: {final_val.total_cost} ({'Valid' if final_val.is_valid else 'Violations Detected'})."
            ),
            cost_history=cost_history
        )
