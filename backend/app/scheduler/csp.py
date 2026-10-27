from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room, TimetableSession

@dataclass(frozen=True)
class LectureVariable:
    id: str
    class_id: str
    subject_id: str
    session_index: int
    duration: int
    is_lab: bool
    subject_code: str
    subject_name: str

@dataclass(frozen=True)
class SlotValue:
    day: str
    period: int  # 1-indexed starting period
    room_id: str
    teacher_id: str

    def occupied_periods(self, duration: int) -> List[int]:
        return list(range(self.period, self.period + duration))

class TimetableCSP:
    def __init__(
        self,
        settings: WorkingSettings,
        classes: Dict[str, ClassBatch],
        subjects: Dict[str, Subject],
        teachers: Dict[str, Teacher],
        rooms: Dict[str, Room]
    ):
        self.settings = settings
        self.classes = {c_id: c for c_id, c in classes.items() if c.active}
        self.subjects = subjects
        self.teachers = {t_id: t for t_id, t in teachers.items() if t.active}
        self.rooms = {r_id: r for r_id, r in rooms.items() if r.active}
        
        self.variables: List[LectureVariable] = []
        self.domains: Dict[str, List[SlotValue]] = {}
        self._build_variables_and_domains()

    def _build_variables_and_domains(self):
        self.variables = []
        self.domains = {}

        # 1. Create variables for each class-subject requirement
        for c_id, cls in self.classes.items():
            for sub_id, req_hours in cls.subject_requirements.items():
                if sub_id not in self.subjects:
                    continue
                sub = self.subjects[sub_id]
                duration = sub.lab_duration if sub.type == "lab" else 1
                
                # Number of session instances
                # e.g., if req_hours = 2 and duration = 2, instances = 1 session of 2 hrs
                # if req_hours = 3 and duration = 1, instances = 3 sessions of 1 hr
                num_sessions = req_hours // duration
                for s_idx in range(1, num_sessions + 1):
                    var_id = f"{c_id}__{sub_id}__{s_idx}"
                    var = LectureVariable(
                        id=var_id,
                        class_id=c_id,
                        subject_id=sub_id,
                        session_index=s_idx,
                        duration=duration,
                        is_lab=(sub.type == "lab"),
                        subject_code=sub.code,
                        subject_name=sub.name
                    )
                    self.variables.append(var)

        # 2. Assign balanced qualified teacher for each (class_id, subject_id)
        # As permitted and recommended by the assignment PDF ("You may fix the teacher in advance to keep the domain small")
        teacher_loads = defaultdict(int)
        class_sub_teacher: Dict[Tuple[str, str], str] = {}
        
        # Sort class requirements so labs and heavy subjects get assigned first
        for cls in self.classes.values():
            for sub_id, req_hours in cls.subject_requirements.items():
                if sub_id not in self.subjects:
                    continue
                eligible = [t for t in self.teachers.values() if sub_id in t.subject_ids]
                if not eligible:
                    continue
                # Pick teacher with minimum current assigned load who has room under max_weekly_load
                eligible.sort(key=lambda t: (teacher_loads[t.id] + req_hours > t.max_weekly_load, teacher_loads[t.id]))
                chosen = eligible[0]
                teacher_loads[chosen.id] += req_hours
                class_sub_teacher[(cls.id, sub_id)] = chosen.id

        # 3. Pre-filter domains for each variable
        days = self.settings.days
        periods_per_day = self.settings.periods_per_day

        for var in self.variables:
            cls = self.classes[var.class_id]
            sub = self.subjects[var.subject_id]
            lunch_period = cls.lunch_break_period
            
            # Eligible rooms: capacity >= class strength & matching room type (H4, H5)
            eligible_rooms = [
                r for r in self.rooms.values()
                if r.capacity >= cls.strength and (
                    (var.is_lab and r.type == "lab") or
                    (not var.is_lab and r.type == "classroom")
                )
            ]

            assigned_teacher_id = class_sub_teacher.get((var.class_id, var.subject_id))
            eligible_teachers = [self.teachers[assigned_teacher_id]] if assigned_teacher_id in self.teachers else [
                t for t in self.teachers.values() if var.subject_id in t.subject_ids
            ]

            domain_values: List[SlotValue] = []
            for day in days:
                for period in range(1, periods_per_day - var.duration + 2):
                    occupied = range(period, period + var.duration)
                    if lunch_period in occupied:
                        continue

                    for room in eligible_rooms:
                        for teacher in eligible_teachers:
                            unavail = False
                            for un in teacher.unavailable_slots:
                                if un.get("day") == day and un.get("period") in occupied:
                                    unavail = True
                                    break
                            if unavail:
                                continue

                            domain_values.append(SlotValue(
                                day=day,
                                period=period,
                                room_id=room.id,
                                teacher_id=teacher.id
                            ))
            self.domains[var.id] = domain_values

    def get_variable_map(self) -> Dict[str, LectureVariable]:
        return {v.id: v for v in self.variables}
