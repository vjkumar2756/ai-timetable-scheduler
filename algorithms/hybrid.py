"""
Hybrid CSP + Simulated Annealing Solver (+6 Bonus Marks).
Two-phase optimization:
Phase 1: Systematic CSP backtracking guarantees 0 hard violations.
Phase 2: Local search SA explores feasible neighborhood to minimize soft constraint penalties.
"""
from typing import Dict, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.hybrid import HybridCSPSASolver
from backend.app.scheduler.metrics import SolverResult

class HybridCSPSAWrapper(BaseSolver):
    """
    Hybrid solver: Systematic Backtracking (feasibility) + Simulated Annealing (soft optimization).
    """
    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        solver = HybridCSPSASolver(
            csp=self.csp,
            validator=self.validator,
            cost_fn=self.cost_fn,
            seed=self.seed
        )
        return solver.solve(seed=self.seed)
