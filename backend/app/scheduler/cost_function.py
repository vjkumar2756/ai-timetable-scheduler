from typing import Dict, List, Tuple
from collections import defaultdict
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room
from backend.app.scheduler.csp import LectureVariable, SlotValue

class CostFunction:
    """
    Evaluates soft constraints (S1-S5) and computes the total assignment cost:
    Cost = 1000 * (hard_violations) + (soft_penalties)
    """
    def __init__(
        self,
        settings: WorkingSettings,
        classes: Dict[str, ClassBatch],
        subjects: Dict[str, Subject],
        teachers: Dict[str, Teacher],
        rooms: Dict[str, Room],
        weights: Dict[str, int] = None
    ):
        self.settings = settings
        self.classes = classes
        self.subjects = subjects
        self.teachers = teachers
        self.rooms = rooms
        
        # Configurable soft penalty weights
        self.weights = weights or {
            "S1_gap": 5,           # Free periods within a class day
            "S2_subject_repeat": 15, # Same subject twice on the same day (non-lab)
            "S3_lab_continuity": 20, # Lab sessions not consecutive
            "S4_teacher_pref": 10,  # Ignoring teacher preference / slot
            "S5_consecutive": 12    # > 2 consecutive lectures for a teacher
        }

    def evaluate_soft_penalties(
        self,
        assignment: Dict[str, SlotValue],
        variables: Dict[str, LectureVariable]
    ) -> Tuple[int, Dict[str, int], List[str]]:
        """
        Calculates soft penalties across S1 to S5.
        Returns: (total_penalty, penalty_breakdown, explanations)
        """
        breakdown = {k: 0 for k in self.weights}
        explanations: List[str] = []

        # Structures for analysis
        # class_day_periods[class_id][day] = list of occupied periods
        class_day_periods = defaultdict(lambda: defaultdict(list))
        # class_day_subjects[class_id][day] = list of (subject_id, is_lab)
        class_day_subjects = defaultdict(lambda: defaultdict(list))
        # teacher_day_periods[teacher_id][day] = list of occupied periods
        teacher_day_periods = defaultdict(lambda: defaultdict(list))

        for var_id, slot in assignment.items():
            if var_id not in variables:
                continue
            var = variables[var_id]
            teacher = self.teachers.get(slot.teacher_id)
            occupied = list(range(slot.period, slot.period + var.duration))

            class_day_periods[var.class_id][slot.day].extend(occupied)
            class_day_subjects[var.class_id][slot.day].append((var.subject_id, var.is_lab))
            teacher_day_periods[slot.teacher_id][slot.day].extend(occupied)

            # S4: Teacher Preferences (e.g. avoid period 1 or prefer certain slots)
            if teacher and teacher.preferred_slots:
                # If teacher has specified preferred slots, check if scheduled outside preferred or on non-preferred
                has_pref_match = any(
                    pref.get("day") == slot.day and pref.get("period") in occupied
                    for pref in teacher.preferred_slots
                )
                if not has_pref_match:
                    breakdown["S4_teacher_pref"] += self.weights["S4_teacher_pref"]

        # S1: Minimize Gaps in Class Day
        for class_id, day_dict in class_day_periods.items():
            cls = self.classes.get(class_id)
            c_name = cls.name if cls else class_id
            lunch_p = cls.lunch_break_period if cls else self.settings.default_lunch_period

            for day, periods in day_dict.items():
                if len(periods) <= 1:
                    continue
                sorted_p = sorted(set(periods))
                min_p, max_p = sorted_p[0], sorted_p[-1]
                # Check for gap periods between min and max that are NOT the lunch break
                for p in range(min_p, max_p + 1):
                    if p not in sorted_p and p != lunch_p:
                        breakdown["S1_gap"] += self.weights["S1_gap"]
                        explanations.append(f"S1: Gap period {p} on {day} for class {c_name}")

        # S2: Spread Subject Across Different Days (avoid duplicate non-lab on same day)
        for class_id, day_dict in class_day_subjects.items():
            for day, subs in day_dict.items():
                sub_counts = defaultdict(int)
                for sub_id, is_lab in subs:
                    if not is_lab:
                        sub_counts[sub_id] += 1
                for sub_id, count in sub_counts.items():
                    if count > 1:
                        excess = count - 1
                        pen = excess * self.weights["S2_subject_repeat"]
                        breakdown["S2_subject_repeat"] += pen
                        s_name = self.subjects[sub_id].name if sub_id in self.subjects else sub_id
                        explanations.append(f"S2: Subject {s_name} scheduled {count} times on {day}")

        # S5: Avoid > 2 Consecutive Lectures for a Teacher
        for teacher_id, day_dict in teacher_day_periods.items():
            t = self.teachers.get(teacher_id)
            t_name = t.name if t else teacher_id
            for day, periods in day_dict.items():
                sorted_p = sorted(set(periods))
                consecutive_run = 0
                prev = -1
                for p in sorted_p:
                    if prev != -1 and p == prev + 1:
                        consecutive_run += 1
                        if consecutive_run > 2:
                            breakdown["S5_consecutive"] += self.weights["S5_consecutive"]
                            explanations.append(f"S5: Teacher {t_name} has >2 consecutive lectures on {day} at period {p}")
                    else:
                        consecutive_run = 1
                    prev = p

        total_penalty = sum(breakdown.values())
        return total_penalty, breakdown, explanations

    def compute_total_cost(
        self,
        hard_violations: int,
        soft_penalty: int
    ) -> int:
        """
        Total Cost = 1000 * (hard_violations) + (soft_penalties)
        """
        return (1000 * hard_violations) + soft_penalty
