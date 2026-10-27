import json
import os
from typing import Dict, List, Optional
from backend.app.models.entities import (
    Subject, Teacher, ClassBatch, Room, WorkingSettings,
    TimetableSession, CancellationRecord, ReschedulingProposal,
    SwapRequest, InAppNotification
)

class DataStore:
    def __init__(self, data_file: Optional[str] = None):
        self.data_file = data_file
        self.settings: WorkingSettings = WorkingSettings()
        self.subjects: Dict[str, Subject] = {}
        self.teachers: Dict[str, Teacher] = {}
        self.classes: Dict[str, ClassBatch] = {}
        self.rooms: Dict[str, Room] = {}
        self.sessions: Dict[str, TimetableSession] = {}
        self.cancellations: List[CancellationRecord] = []
        self.rescheduling_proposals: List[ReschedulingProposal] = []
        self.swap_requests: List[SwapRequest] = []
        self.notifications: List[InAppNotification] = []
        self.current_schedule_metadata: Dict = {}

    def load_from_dict(self, data: dict):
        if "settings" in data:
            self.settings = WorkingSettings(**data["settings"])
        
        self.subjects = {s["id"]: Subject(**s) for s in data.get("subjects", [])}
        self.teachers = {t["id"]: Teacher(**t) for t in data.get("teachers", [])}
        self.classes = {c["id"]: ClassBatch(**c) for c in data.get("classes", [])}
        self.rooms = {r["id"]: Room(**r) for r in data.get("rooms", [])}
        
        if "sessions" in data:
            self.sessions = {s["id"]: TimetableSession(**s) for s in data.get("sessions", [])}
        else:
            self.sessions = {}

    def load_from_file(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.load_from_dict(data)

    def to_dict(self) -> dict:
        return {
            "settings": self.settings.model_dump(),
            "subjects": [s.model_dump() for s in self.subjects.values()],
            "teachers": [t.model_dump() for t in self.teachers.values()],
            "classes": [c.model_dump() for c in self.classes.values()],
            "rooms": [r.model_dump() for r in self.rooms.values()],
            "sessions": [s.model_dump() for s in self.sessions.values()],
            "cancellations": [c.model_dump() for c in self.cancellations],
            "rescheduling_proposals": [p.model_dump() for p in self.rescheduling_proposals],
            "swap_requests": [sr.model_dump() for sr in self.swap_requests],
            "notifications": [n.model_dump() for n in self.notifications],
            "metadata": self.current_schedule_metadata
        }

    def save_to_file(self, filepath: Optional[str] = None):
        target = filepath or self.data_file
        if target:
            os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
            with open(target, "w") as f:
                json.dump(self.to_dict(), f, indent=2)

# Global singleton store instance
db_store = DataStore()
