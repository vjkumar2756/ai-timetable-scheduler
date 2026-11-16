"""
Core Domain Entities and Pydantic Models for SchedulAI Timetable Scheduler.
Shared across all search algorithms, constraint evaluators, and UI views.
"""
from backend.app.models.entities import (
    WorkingSettings,
    Subject,
    Teacher,
    ClassBatch,
    Room,
    TimetableSession,
    SwapRequest,
    CancellationRecord,
    InAppNotification,
    ReschedulingProposal
)

__all__ = [
    "WorkingSettings",
    "Subject",
    "Teacher",
    "ClassBatch",
    "Room",
    "TimetableSession",
    "SwapRequest",
    "CancellationRecord",
    "InAppNotification",
    "ReschedulingProposal"
]
