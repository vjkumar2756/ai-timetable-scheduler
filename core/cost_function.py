"""
Cost Function and Soft Constraint Evaluator (S1-S5) for SchedulAI.
Calculates total objective penalty: Cost = 1000 * (hard_violations) + (soft_penalties).
"""
from backend.app.scheduler.cost_function import CostFunction

__all__ = ["CostFunction"]
