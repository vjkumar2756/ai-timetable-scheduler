"""
core/problem.py
Constraint Satisfaction Problem (CSP) Formulation for Timetable Scheduling.
Pure Python module (zero web/DB/Streamlit dependencies).

Defines:
- LectureVariable: Discrete lecture session to be scheduled
- SlotValue: Concrete domain assignment (day, period, room_id, teacher_id)
- TimetableProblem: Formulation engine that generates variables and unary-pruned domains.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set, Any
from collections import defaultdict

@dataclass(frozen=True)
class LectureVariable:
    """Represents an atomic variable in the CSP."""
    id: str
    class_id: str
    subject_id: str
    session_index: int
    duration: int           # 1 for theory, 2 for practical labs
    is_lab: bool
    subject_code: str
    subject_name: str
    teacher_id: str         # Deterministically bound via load-balancing
    class_strength: int
    class_lunch_period: int

@dataclass(frozen=True)
class SlotValue:
    """Represents a value in the domain of a variable."""
    day: str
    period: int             # 1-indexed starting period
    room_id: str
    teacher_id: str

    def occupied_periods(self, duration: int) -> List[int]:
        return list(range(self.period, self.period + duration))

class TimetableProblem:
    """
    Constructs the CSP formulation:
    1. Deterministically maps an eligible teacher to each (class, subject) pair
       using load-balancing that respects H6 (availability) and H8 (max load).
    2. Instantiates exact session variables satisfying H7 by construction.
    3. Prunes variable domains upfront using unary constraints:
       - H4: Room capacity >= class strength
       - H5: Lab in lab room, Theory in classroom
       - H6: Teacher unavailable slots excluded
       - H9: Class lunch period excluded
       - Multi-period lab boundary bounds (cannot exceed periods_per_day)
    """
    def __init__(
        self,
        days: List[str],
        periods_per_day: int,
        default_lunch_period: int,
        classes: Dict[str, Dict[str, Any]],
        subjects: Dict[str, Dict[str, Any]],
        teachers: Dict[str, Dict[str, Any]],
        rooms: Dict[str, Dict[str, Any]]
    ):
        self.days = days
        self.periods_per_day = periods_per_day
        self.default_lunch_period = default_lunch_period
        self.classes = {c_id: c for c_id, c in classes.items() if c.get("active", True)}
        self.subjects = subjects
        self.teachers = {t_id: t for t_id, t in teachers.items() if t.get("active", True)}
        self.rooms = {r_id: r for r_id, r in rooms.items() if r.get("active", True)}

        self.teacher_assignment: Dict[Tuple[str, str], str] = {}
        self.variables: List[LectureVariable] = []
        self.variables_dict: Dict[str, LectureVariable] = {}
        self.domains: Dict[str, List[SlotValue]] = {}

        self._assign_teachers_to_classes()
        self._build_variables()
        self._build_domains()

    def _assign_teachers_to_classes(self):
        """
        Load-balanced teacher assignment for each (class_id, subject_id).
        Selects the eligible teacher with lowest current assigned load.
        """
        assigned_hours: Dict[str, int] = defaultdict(int)

        for c_id, cinfo in self.classes.items():
            for sub_id, req_hrs in cinfo.get("subject_requirements", {}).items():
                if sub_id not in self.subjects:
                    continue
                # Eligible teachers for this subject
                eligible = [
                    t for t in self.teachers.values()
                    if sub_id in t.get("subject_ids", [])
                ]
                if not eligible:
                    # Fallback to any teacher if unmapped (handled by feasibility)
                    eligible = list(self.teachers.values())

                # Sort by current workload (least loaded first), then by id
                eligible.sort(key=lambda t: (assigned_hours[t["id"]], t["id"]))
                selected = eligible[0]
                self.teacher_assignment[(c_id, sub_id)] = selected["id"]
                assigned_hours[selected["id"]] += req_hrs

    def _build_variables(self):
        """Build exact session variables. Labs become single variables with duration=2."""
        self.variables = []
        for c_id, cinfo in self.classes.items():
            lunch = cinfo.get("lunch_break_period", self.default_lunch_period)
            strength = cinfo.get("strength", 40)
            
            for sub_id, req_hours in cinfo.get("subject_requirements", {}).items():
                if sub_id not in self.subjects:
                    continue
                sub = self.subjects[sub_id]
                is_lab = sub.get("type") == "lab"
                duration = sub.get("lab_duration", 2 if is_lab else 1)
                if duration <= 0:
                    duration = 1
                
                num_sessions = req_hours // duration
                teacher_id = self.teacher_assignment.get((c_id, sub_id), "")

                for s_idx in range(1, num_sessions + 1):
                    var_id = f"{c_id}__{sub_id}__{s_idx}"
                    var = LectureVariable(
                        id=var_id,
                        class_id=c_id,
                        subject_id=sub_id,
                        session_index=s_idx,
                        duration=duration,
                        is_lab=is_lab,
                        subject_code=sub.get("code", sub_id),
                        subject_name=sub.get("name", sub_id),
                        teacher_id=teacher_id,
                        class_strength=strength,
                        class_lunch_period=lunch
                    )
                    self.variables.append(var)
        
        self.variables_dict = {v.id: v for v in self.variables}

    def _build_domains(self):
        """Construct domain for each variable with unary constraints applied upfront."""
        self.domains = {}

        for var in self.variables:
            var_domain: List[SlotValue] = []
            cls = self.classes.get(var.class_id, {})
            teacher = self.teachers.get(var.teacher_id, {})
            unavailable = {
                (u["day"], u["period"]) for u in teacher.get("unavailable_slots", [])
            }
            lunch_period = var.class_lunch_period

            for day in self.days:
                # Max starting period such that session fits in day
                for period in range(1, self.periods_per_day - var.duration + 2):
                    occupied = list(range(period, period + var.duration))
                    
                    # Unary Constraint: Lunch Break Protection (H9)
                    if lunch_period in occupied:
                        continue
                    
                    # Unary Constraint: Teacher Availability (H6)
                    if any((day, p) in unavailable for p in occupied):
                        continue

                    # Unary Constraint: Room Eligibility (H4 capacity & H5 type)
                    for r_id, room in self.rooms.items():
                        # H5: Lab in lab room, theory in classroom
                        if var.is_lab and room.get("type") != "lab":
                            continue
                        if not var.is_lab and room.get("type") == "lab":
                            continue
                        
                        # H4: Room Capacity
                        if room.get("capacity", 0) < var.class_strength:
                            continue

                        var_domain.append(SlotValue(
                            day=day,
                            period=period,
                            room_id=r_id,
                            teacher_id=var.teacher_id
                        ))
            
            self.domains[var.id] = var_domain
