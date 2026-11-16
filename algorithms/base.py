"""
Base Solver Interface and Standard Execution Contract for all Search Algorithms.
Ensures uniform signatures, metrics collection, seed control, and timeout handling.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.app.scheduler.csp import TimetableCSP, SlotValue
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction
from backend.app.scheduler.metrics import SolverResult

class BaseSolver(ABC):
    """
    Abstract base class for all SchedulAI timetable search algorithms.
    """
    def __init__(
        self,
        csp: TimetableCSP,
        validator: ConstraintValidator,
        cost_fn: CostFunction,
        config: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = 42
    ):
        self.csp = csp
        self.validator = validator
        self.cost_fn = cost_fn
        self.config = config or {}
        self.seed = seed

    @abstractmethod
    def solve(self, timeout_seconds: float = 30.0) -> SolverResult:
        """
        Executes the search algorithm under the configured timeout.
        Returns a populated SolverResult object.
        """
        pass
