"""
Plain Backtracking Solver (Baseline Algorithm 1).
Performs chronological systematic depth-first search without heuristic ordering.
"""
from typing import Dict, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.backtracking import PlainBacktrackingSolver
from backend.app.scheduler.metrics import SolverResult

class PlainBacktrackingWrapper(BaseSolver):
    """Systematic baseline backtracking without heuristic optimization."""
    
    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        solver = PlainBacktrackingSolver(self.csp, self.validator, self.cost_fn)
        return solver.solve(time_limit_seconds=timeout_seconds)
