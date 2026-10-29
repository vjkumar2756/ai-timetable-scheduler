"""
Simulated Annealing Local Search Solver (+6 Bonus Marks).
Probabilistic metaheuristic optimizing soft constraint quality while preserving hard feasibility.
"""
import time
import math
import random
from typing import Dict, Any, Optional
from algorithms.base import BaseSolver
from backend.app.scheduler.simulated_annealing import SimulatedAnnealingSolver
from backend.app.scheduler.metrics import SolverResult

class SimulatedAnnealingWrapper(BaseSolver):
    """
    Simulated Annealing algorithm wrapper.
    Configurable parameters:
    - initial_temp (default 100.0)
    - cooling_rate (default 0.96)
    - steps_per_temp (default 40)
    - min_temp (default 0.1)
    """
    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        cfg = self.config
        i_temp = cfg.get("initial_temp", 100.0)
        c_rate = cfg.get("cooling_rate", 0.96)
        steps = cfg.get("steps_per_temp", 40)
        m_temp = cfg.get("min_temp", 0.1)

        solver = SimulatedAnnealingSolver(
            csp=self.csp,
            validator=self.validator,
            cost_fn=self.cost_fn,
            initial_temp=i_temp,
            cooling_rate=c_rate,
            min_temp=m_temp,
            steps_per_temp=steps,
            seed=self.seed
        )
        return solver.solve(seed=self.seed)
