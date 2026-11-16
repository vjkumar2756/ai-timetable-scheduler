"""
Constraint Satisfaction Problem (CSP) formulation for Timetable Scheduling.
Defines variables, values, and binary/unary constraint structures.
"""
from backend.app.scheduler.csp import LectureVariable, SlotValue, TimetableCSP

__all__ = ["LectureVariable", "SlotValue", "TimetableCSP"]
