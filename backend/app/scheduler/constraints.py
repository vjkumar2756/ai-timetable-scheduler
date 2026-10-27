from typing import List, Dict, Tuple, Optional, Any, Set
from collections import defaultdict
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room, TimetableSession
from backend.app.scheduler.csp import LectureVariable, SlotValue

class ConstraintValidator:
    """
    Authoritative validator enforcing all 9 Hard Constraints (H1-H9).
    Can validate:
    1. Complete timetable sessions (list of TimetableSession or Dict[str, SlotValue])
    2. Partial assignments during CSP search
    3. Proposed manual edits, swaps, and rescheduling proposals
    """
    def __init__(
        self,
        settings: WorkingSettings,
        classes: Dict[str, ClassBatch],
        subjects: Dict[str, Subject],
        teachers: Dict[str, Teacher],
        rooms: Dict[str, Room]
    ):
        self.settings = settings
        self.classes = classes
        self.subjects = subjects
        self.teachers = teachers
        self.rooms = rooms

    def validate_assignment(
        self,
        assignment: Dict[str, SlotValue],
        variables: Dict[str, LectureVariable],
        check_completeness: bool = True
    ) -> Tuple[bool, int, List[Dict[str, Any]]]:
        """
        Validates an assignment mapping var_id -> SlotValue.
        Returns: (is_valid, violation_count, list_of_violations)
        """
        violations: List[Dict[str, Any]] = []

        # Maps to detect overlapping time slots: (day, period) -> list of (var_id, entity_id)
        teacher_slots = defaultdict(list)
        class_slots = defaultdict(list)
        room_slots = defaultdict(list)
        teacher_hours = defaultdict(int)
        class_subject_hours = defaultdict(int)

        for var_id, slot in assignment.items():
            if var_id not in variables:
                continue
            var = variables[var_id]
            cls = self.classes.get(var.class_id)
            sub = self.subjects.get(var.subject_id)
            teacher = self.teachers.get(slot.teacher_id)
            room = self.rooms.get(slot.room_id)

            if not cls or not sub or not teacher or not room:
                violations.append({
                    "constraint": "INTEGRITY",
                    "code": "H_REF",
                    "message": f"Session references missing entity: class={var.class_id}, sub={var.subject_id}, teacher={slot.teacher_id}, room={slot.room_id}",
                    "var_ids": [var_id]
                })
                continue

            occupied_periods = list(range(slot.period, slot.period + var.duration))

            # H4: Room Capacity
            if room.capacity < cls.strength:
                violations.append({
                    "constraint": "Room Capacity",
                    "code": "H4",
                    "message": f"Room {room.name} (cap: {room.capacity}) smaller than class {cls.name} (strength: {cls.strength})",
                    "var_ids": [var_id]
                })

            # H5: Room Type
            if var.is_lab and room.type != "lab":
                violations.append({
                    "constraint": "Room Type",
                    "code": "H5",
                    "message": f"Lab session '{sub.name}' scheduled in non-lab room '{room.name}'",
                    "var_ids": [var_id]
                })
            elif not var.is_lab and room.type != "classroom":
                violations.append({
                    "constraint": "Room Type",
                    "code": "H5",
                    "message": f"Theory session '{sub.name}' scheduled in lab room '{room.name}'",
                    "var_ids": [var_id]
                })

            # H6: Teacher Availability
            for p in occupied_periods:
                for unavail in teacher.unavailable_slots:
                    if unavail.get("day") == slot.day and unavail.get("period") == p:
                        violations.append({
                            "constraint": "Teacher Availability",
                            "code": "H6",
                            "message": f"Teacher {teacher.name} is unavailable on {slot.day} period {p}",
                            "var_ids": [var_id]
                        })

            # H9: Lunch Break
            for p in occupied_periods:
                if p == cls.lunch_break_period:
                    violations.append({
                        "constraint": "Lunch Break",
                        "code": "H9",
                        "message": f"Class {cls.name} has lunch break on period {p}, but lecture '{sub.name}' was scheduled",
                        "var_ids": [var_id]
                    })

            # Track teacher hours
            teacher_hours[slot.teacher_id] += var.duration
            class_subject_hours[(var.class_id, var.subject_id)] += var.duration

            # Register slots for conflict detection (H1, H2, H3)
            for p in occupied_periods:
                teacher_slots[(slot.teacher_id, slot.day, p)].append(var_id)
                class_slots[(var.class_id, slot.day, p)].append(var_id)
                room_slots[(slot.room_id, slot.day, p)].append(var_id)

        # H1: Teacher Conflict
        for (teacher_id, day, p), v_ids in teacher_slots.items():
            if len(v_ids) > 1:
                t_name = self.teachers[teacher_id].name if teacher_id in self.teachers else teacher_id
                violations.append({
                    "constraint": "Teacher Conflict",
                    "code": "H1",
                    "message": f"Teacher {t_name} is double-booked on {day} period {p} across {len(v_ids)} sessions",
                    "var_ids": v_ids
                })

        # H2: Class Conflict
        for (class_id, day, p), v_ids in class_slots.items():
            if len(v_ids) > 1:
                c_name = self.classes[class_id].name if class_id in self.classes else class_id
                violations.append({
                    "constraint": "Class Conflict",
                    "code": "H2",
                    "message": f"Class {c_name} has {len(v_ids)} overlapping sessions on {day} period {p}",
                    "var_ids": v_ids
                })

        # H3: Room Conflict
        for (room_id, day, p), v_ids in room_slots.items():
            if len(v_ids) > 1:
                r_name = self.rooms[room_id].name if room_id in self.rooms else room_id
                violations.append({
                    "constraint": "Room Conflict",
                    "code": "H3",
                    "message": f"Room {r_name} has {len(v_ids)} overlapping sessions on {day} period {p}",
                    "var_ids": v_ids
                })

        # H8: Maximum Teacher Workload
        for teacher_id, hours in teacher_hours.items():
            t = self.teachers.get(teacher_id)
            if t and hours > t.max_weekly_load:
                violations.append({
                    "constraint": "Teacher Max Workload",
                    "code": "H8",
                    "message": f"Teacher {t.name} scheduled for {hours} hours, exceeding maximum weekly load of {t.max_weekly_load}",
                    "var_ids": []
                })

        # H7: Exact Weekly Subject Hours (if checking completeness)
        if check_completeness:
            # Check if all variables assigned
            missing_vars = [vid for vid in variables if vid not in assignment]
            if missing_vars:
                violations.append({
                    "constraint": "Completeness",
                    "code": "H7_MISSING",
                    "message": f"{len(missing_vars)} required lecture sessions are unassigned",
                    "var_ids": missing_vars
                })
            
            for (class_id, sub_id), actual_hours in class_subject_hours.items():
                cls = self.classes.get(class_id)
                if cls:
                    expected_hours = cls.subject_requirements.get(sub_id, 0)
                    if actual_hours != expected_hours:
                        sub = self.subjects.get(sub_id)
                        sub_name = sub.name if sub else sub_id
                        violations.append({
                            "constraint": "Exact Weekly Hours",
                            "code": "H7",
                            "message": f"Class {cls.name} received {actual_hours}h for {sub_name}, expected {expected_hours}h",
                            "var_ids": []
                        })

        return (len(violations) == 0, len(violations), violations)

    def is_consistent(
        self,
        var: LectureVariable,
        val: SlotValue,
        assignment: Dict[str, SlotValue],
        variables: Dict[str, LectureVariable]
    ) -> bool:
        """
        Fast binary/unary constraint consistency check for Backtracking search.
        Checks if assigning var = val is consistent with current partial assignment.
        """
        cls = self.classes.get(var.class_id)
        sub = self.subjects.get(var.subject_id)
        room = self.rooms.get(val.room_id)
        teacher = self.teachers.get(val.teacher_id)

        if not cls or not sub or not room or not teacher:
            return False

        occupied = range(val.period, val.period + var.duration)

        # Unary checks
        if room.capacity < cls.strength:
            return False
        if var.is_lab and room.type != "lab":
            return False
        if not var.is_lab and room.type != "classroom":
            return False
        if cls.lunch_break_period in occupied:
            return False

        # Teacher unavailable slots
        for un in teacher.unavailable_slots:
            if un.get("day") == val.day and un.get("period") in occupied:
                return False

        # Workload check
        current_t_hours = sum(
            variables[other_id].duration
            for other_id, other_val in assignment.items()
            if other_val.teacher_id == val.teacher_id
        )
        if current_t_hours + var.duration > teacher.max_weekly_load:
            return False

        # Binary checks against already assigned variables
        for other_id, other_val in assignment.items():
            if other_val.day != val.day:
                continue
            other_var = variables[other_id]
            other_occupied = range(other_val.period, other_val.period + other_var.duration)

            # Check period overlap
            overlap = any(p in other_occupied for p in occupied)
            if not overlap:
                continue

            # H1: Teacher conflict
            if other_val.teacher_id == val.teacher_id:
                return False

            # H2: Class conflict
            if other_var.class_id == var.class_id:
                return False

            # H3: Room conflict
            if other_val.room_id == val.room_id:
                return False

        return True

    def count_conflicts(
        self,
        var: LectureVariable,
        val: SlotValue,
        assignment: Dict[str, SlotValue],
        variables: Dict[str, LectureVariable]
    ) -> int:
        """
        Counts number of hard constraint violations caused by assigning var = val
        in a complete or partial assignment (used by Min-Conflicts).
        """
        conflicts = 0
        cls = self.classes.get(var.class_id)
        sub = self.subjects.get(var.subject_id)
        room = self.rooms.get(val.room_id)
        teacher = self.teachers.get(val.teacher_id)

        if not cls or not sub or not room or not teacher:
            return 999

        occupied = range(val.period, val.period + var.duration)

        # Unary conflicts
        if room.capacity < cls.strength:
            conflicts += 1
        if var.is_lab and room.type != "lab":
            conflicts += 1
        if not var.is_lab and room.type != "classroom":
            conflicts += 1
        if cls.lunch_break_period in occupied:
            conflicts += 1

        for un in teacher.unavailable_slots:
            if un.get("day") == val.day and un.get("period") in occupied:
                conflicts += 1

        # Binary conflicts with other variables
        for other_id, other_val in assignment.items():
            if other_id == var.id:
                continue
            if other_val.day != val.day:
                continue
            other_var = variables[other_id]
            other_occupied = range(other_val.period, other_val.period + other_var.duration)

            if not any(p in other_occupied for p in occupied):
                continue

            if other_val.teacher_id == val.teacher_id:
                conflicts += 1
            if other_var.class_id == var.class_id:
                conflicts += 1
            if other_val.room_id == val.room_id:
                conflicts += 1

        return conflicts
