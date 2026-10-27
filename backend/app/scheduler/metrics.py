from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class SolverResult:
    algorithm: str
    success: bool
    execution_time_seconds: float
    nodes_expanded: int = 0
    iterations: int = 0
    restarts: int = 0
    hard_violations: int = 0
    soft_penalty: int = 0
    total_cost: int = 0
    cost_history: List[int] = field(default_factory=list)
    assignment: Dict[str, Any] = field(default_factory=dict)
    diagnostic_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "success": self.success,
            "execution_time_seconds": round(self.execution_time_seconds, 4),
            "nodes_expanded": self.nodes_expanded,
            "iterations": self.iterations,
            "restarts": self.restarts,
            "hard_violations": self.hard_violations,
            "soft_penalty": self.soft_penalty,
            "total_cost": self.total_cost,
            "cost_history": self.cost_history,
            "diagnostic_message": self.diagnostic_message
        }
