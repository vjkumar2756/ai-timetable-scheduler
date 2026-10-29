"""
core/validator.py
Unified Authoritative Constraint Validation and Cost Function Engine.
Pure Python module (zero web/DB/Streamlit dependencies).

Enforces:
- Hard Constraints H1 - H9 (Zero tolerance: 1000 penalty per violation)
- Soft Constraints S1 - S5 (Quality penalties with configurable weights)
- Cost = 1000 * (Hard Violations) + (Soft Penalties)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict
from core.problem import LectureVariable, SlotValue

@dataclass
class ValidationResult:
    """Detailed report produced by the centralized validator."""
    is_valid: bool
    hard_violations_count: int
    hard_violations: List[str]
    soft_penalties_count: int
    soft_penalties: List[str]
    soft_breakdown: Dict[str, int]
    total_cost: int

class ConstraintValidator:
    """
    Centralized validation engine. Reused by:
    - All solvers (Backtracking, Min-Conflicts, SA, Hybrid)
    - Manual edit live checking
    - Swap and Rescheduling validation
    - Automated unit tests
    """
    def __init__(
        self,
        days: List[str],
        periods_per_day: int,
        default_lunch_period: int,
        classes: Dict[str, Dict[str, Any]],
        subjects: Dict[str, Dict[str, Any]],
        teachers: Dict[str, Dict[str, Any]],
        rooms: Dict[str, Dict[str, Any]],
        weights: Optional[Dict[str, int]] = None
    ):
        self.days = days
        self.periods_per_day = periods_per_day
        self.default_lunch_period = default_lunch_period
        self.classes = {c_id: c for c_id, c in classes.items() if c.get("active", True)}
        self.subjects = subjects
        self.teachers = {t_id: t for t_id, t in teachers.items() if t.get("active", True)}
        self.rooms = {r_id: r for r_id, r in rooms.items() if r.get("active", True)}

        # Configurable soft weights
        self.weights = {
            "S1_gaps": 2,
            "S2_daily_repeat": 3,
            "S3_consecutive_lab": 5,
            "S4_teacher_pref": 2,
            "S5_consecutive_teacher": 2
        }
        if weights:
            self.weights.update(weights)

    def validate(
        self,
        assignment: Dict[str, SlotValue],
        variables: Dict[str, LectureVariable],
        check_completeness: bool = True
    ) -> ValidationResult:
        """
        Authoritatively validates any complete or partial timetable assignment.
        """
        hard_violations: List[str] = []
        soft_penalties: List[str] = []
        soft_breakdown: Dict[str, int] = {
            "S1_gaps": 0,
            "S2_daily_repeat": 0,
            "S3_consecutive_lab": 0,
            "S4_teacher_pref": 0,
            "S5_consecutive_teacher": 0
        }

        # Track period occupancy for H1, H2, H3: (day, period) -> list of var_ids
        teacher_occupancy: Dict[Tuple[str, str, int], List[str]] = defaultdict(list)  # (teacher_id, day, period) -> var_ids
        class_occupancy: Dict[Tuple[str, str, int], List[str]] = defaultdict(list)    # (class_id, day, period) -> var_ids
        room_occupancy: Dict[Tuple[str, str, int], List[str]] = defaultdict(list)     # (room_id, day, period) -> var_ids

        # Track hours for H7, H8
        assigned_teacher_hours: Dict[str, int] = defaultdict(int)
        class_subject_hours: Dict[Tuple[str, str], int] = defaultdict(int)

        # Track schedule structure for S1, S2, S5
        # class_id -> day -> list of periods
        class_day_periods: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        # class_id -> day -> list of subject_ids
        class_day_subjects: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        # teacher_id -> day -> list of periods
        teacher_day_periods: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))

        for var_id, slot in assignment.items():
            if var_id not in variables:
                continue
            var = variables[var_id]
            cls = self.classes.get(var.class_id, {})
            sub = self.subjects.get(var.subject_id, {})
            teacher = self.teachers.get(slot.teacher_id, {})
            room = self.rooms.get(slot.room_id, {})

            occupied = list(range(slot.period, slot.period + var.duration))
            assigned_teacher_hours[slot.teacher_id] += var.duration
            class_subject_hours[(var.class_id, var.subject_id)] += var.duration

            # Register occupancy for conflict checking
            for p in occupied:
                teacher_occupancy[(slot.teacher_id, slot.day, p)].append(var_id)
                class_occupancy[(var.class_id, slot.day, p)].append(var_id)
                room_occupancy[(slot.room_id, slot.day, p)].append(var_id)

                class_day_periods[var.class_id][slot.day].append(p)
                class_day_subjects[var.class_id][slot.day].append(var.subject_id)
                teacher_day_periods[slot.teacher_id][slot.day].append(p)

            # H4: Room Capacity (room capacity >= class strength)
            if room.get("capacity", 0) < var.class_strength:
                hard_violations.append(
                    f"H4: Room '{room.get('name', slot.room_id)}' capacity ({room.get('capacity', 0)}) "
                    f"is smaller than Class '{cls.get('name', var.class_id)}' strength ({var.class_strength})."
                )

            # H5: Room Type (lab -> lab, theory -> classroom)
            if var.is_lab and room.get("type") != "lab":
                hard_violations.append(
                    f"H5: Practical lab '{sub.get('name', var.subject_id)}' assigned to non-lab room '{room.get('name', slot.room_id)}'."
                )
            elif not var.is_lab and room.get("type") == "lab":
                hard_violations.append(
                    f"H5: Theory lecture '{sub.get('name', var.subject_id)}' assigned to practical lab '{room.get('name', slot.room_id)}'."
                )

            # H6: Teacher Availability
            unavail = {
                (u["day"], u["period"]) for u in teacher.get("unavailable_slots", [])
            }
            for p in occupied:
                if (slot.day, p) in unavail:
                    hard_violations.append(
                        f"H6: Teacher '{teacher.get('name', slot.teacher_id)}' scheduled during unavailable slot "
                        f"on {slot.day} Period {p} for {sub.get('code', var.subject_id)}."
                    )

            # H9: Lunch Break Protection
            lunch_period = var.class_lunch_period
            if lunch_period in occupied:
                hard_violations.append(
                    f"H9: Class '{cls.get('name', var.class_id)}' scheduled during protected lunch break (Period {lunch_period}) on {slot.day}."
                )

            # S4: Teacher Preference Penalty
            preferred = {
                (pref["day"], pref["period"]) for pref in teacher.get("preferred_slots", [])
            }
            if preferred and not any((slot.day, p) in preferred for p in occupied):
                soft_penalties.append(
                    f"S4: Faculty '{teacher.get('name', slot.teacher_id)}' assigned to non-preferred slot ({slot.day} P{slot.period})."
                )
                soft_breakdown["S4_teacher_pref"] += self.weights["S4_teacher_pref"]

        # H1: Teacher Clash Check (teacher in 2 sessions in same slot)
        for (t_id, day, p), v_list in teacher_occupancy.items():
            if len(v_list) > 1:
                t_name = self.teachers.get(t_id, {}).get("name", t_id)
                hard_violations.append(
                    f"H1: Faculty clash - '{t_name}' assigned to {len(v_list)} sessions simultaneously on {day} Period {p}."
                )

        # H2: Class Clash Check (class in 2 sessions in same slot)
        for (c_id, day, p), v_list in class_occupancy.items():
            if len(v_list) > 1:
                c_name = self.classes.get(c_id, {}).get("name", c_id)
                hard_violations.append(
                    f"H2: Class clash - '{c_name}' assigned to {len(v_list)} sessions simultaneously on {day} Period {p}."
                )

        # H3: Room Clash Check (room hosting 2 sessions in same slot)
        for (r_id, day, p), v_list in room_occupancy.items():
            if len(v_list) > 1:
                r_name = self.rooms.get(r_id, {}).get("name", r_id)
                hard_violations.append(
                    f"H3: Room clash - '{r_name}' booked for {len(v_list)} sessions simultaneously on {day} Period {p}."
                )

        # H8: Teacher Max Weekly Load
        for t_id, assigned_hrs in assigned_teacher_hours.items():
            max_load = self.teachers.get(t_id, {}).get("max_weekly_load", 20)
            if assigned_hrs > max_load:
                t_name = self.teachers.get(t_id, {}).get("name", t_id)
                hard_violations.append(
                    f"H8: Faculty overload - '{t_name}' assigned {assigned_hrs}h (Max allowed: {max_load}h)."
                )

        # H7: Exact Weekly Hours per Subject
        if check_completeness:
            for c_id, cinfo in self.classes.items():
                for sub_id, req_hrs in cinfo.get("subject_requirements", {}).items():
                    actual_hrs = class_subject_hours.get((c_id, sub_id), 0)
                    if actual_hrs != req_hrs:
                        sub_name = self.subjects.get(sub_id, {}).get("name", sub_id)
                        hard_violations.append(
                            f"H7: Weekly hours mismatch for Class '{cinfo.get('name', c_id)}' - "
                            f"Subject '{sub_name}' has {actual_hrs}h scheduled, required: {req_hrs}h."
                        )

        # S1: Gaps in student class's day
        for c_id, day_dict in class_day_periods.items():
            lunch = self.classes.get(c_id, {}).get("lunch_break_period", self.default_lunch_period)
            for day, periods in day_dict.items():
                if len(periods) >= 2:
                    sorted_p = sorted(set(periods))
                    first_p = sorted_p[0]
                    last_p = sorted_p[-1]
                    for gap_p in range(first_p, last_p + 1):
                        if gap_p not in sorted_p and gap_p != lunch:
                            soft_penalties.append(
                                f"S1: Student gap in {c_id} schedule on {day} at Period {gap_p}."
                            )
                            soft_breakdown["S1_gaps"] += self.weights["S1_gaps"]

        # S2: Daily Subject Spread (no same theory subject twice in one day)
        for c_id, day_subs in class_day_subjects.items():
            for day, sub_list in day_subs.items():
                counts = defaultdict(int)
                for s_id in sub_list:
                    # Only check theory subjects
                    if self.subjects.get(s_id, {}).get("type") == "theory":
                        counts[s_id] += 1
                for s_id, count in counts.items():
                    if count > 1:
                        sub_code = self.subjects.get(s_id, {}).get("code", s_id)
                        soft_penalties.append(
                            f"S2: Subject '{sub_code}' repeated {count} times on {day} for class {c_id}."
                        )
                        soft_breakdown["S2_daily_repeat"] += (count - 1) * self.weights["S2_daily_repeat"]

        # S5: Teacher Fatigue (>2 consecutive lectures)
        for t_id, day_dict in teacher_day_periods.items():
            for day, periods in day_dict.items():
                sorted_p = sorted(set(periods))
                consecutive = 1
                for i in range(1, len(sorted_p)):
                    if sorted_p[i] == sorted_p[i-1] + 1:
                        consecutive += 1
                        if consecutive > 2:
                            t_name = self.teachers.get(t_id, {}).get("name", t_id)
                            soft_penalties.append(
                                f"S5: Faculty '{t_name}' has >2 consecutive periods ({consecutive}) on {day} at Period {sorted_p[i]}."
                            )
                            soft_breakdown["S5_consecutive_teacher"] += self.weights["S5_consecutive_teacher"]
                    else:
                        consecutive = 1

        hard_count = len(hard_violations)
        soft_cost = sum(soft_breakdown.values())
        total_cost = (1000 * hard_count) + soft_cost

        return ValidationResult(
            is_valid=(hard_count == 0),
            hard_violations_count=hard_count,
            hard_violations=hard_violations,
            soft_penalties_count=len(soft_penalties),
            soft_penalties=soft_penalties,
            soft_breakdown=soft_breakdown,
            total_cost=total_cost
        )
