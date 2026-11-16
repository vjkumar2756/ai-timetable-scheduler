"""
Min-Conflicts Local Search Algorithm (Algorithm 2).
Iterative repair heuristic with random walk and random restart plateau escapes.
"""
from typing import Dict, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.min_conflicts import MinConflictsSolver
from backend.app.scheduler.metrics import SolverResult

class MinConflictsWrapper(BaseSolver):
    """
    Min-Conflicts local search solver wrapper.
    Configurable parameters:
    - max_iterations (default 2000)
    - random_walk_prob (default 0.08)
    - max_restarts (default 5)
    - seed (default 42)
    """
    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        cfg = self.config
        max_iter = cfg.get("max_iterations", 2000)
        p_walk = cfg.get("random_walk_prob", 0.08)
        restarts = cfg.get("max_restarts", 5)

        solver = MinConflictsSolver(
            csp=self.csp,
            validator=self.validator,
            cost_fn=self.cost_fn,
            max_iterations=max_iter,
            random_walk_prob=p_walk,
            max_restarts=restarts,
            seed=self.seed
        )
        return solver.solve(seed=self.seed)
