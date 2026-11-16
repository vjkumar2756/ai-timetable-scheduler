"""
Centralized Constraint Validation and Solvability Analysis for SchedulAI.
Enforces all 9 Hard Constraints (H1-H9) and performs pre-flight solvability checks.
"""
from typing import Dict, List, Tuple, Any
from backend.app.models.entities import WorkingSettings, Subject, Teacher, ClassBatch, Room
from backend.app.scheduler.constraints import ConstraintValidator

def perform_solvability_precheck(
    settings: WorkingSettings,
    classes: Dict[str, ClassBatch],
    subjects: Dict[str, Subject],
    teachers: Dict[str, Teacher],
    rooms: Dict[str, Room]
) -> Dict[str, Any]:
    """
    Solvability Pre-check (Phase 3 Requirement):
    Verifies institutional capacity prior to search:
    1. Total required class hours vs total usable room slots
    2. Lab hours vs Lab room capacity
    3. Teacher teaching capacity vs demanded subject hours
    4. Room capacity vs class cohort strength
    """
    total_required = sum(
        sum(c.subject_requirements.values())
        for c in classes.values() if c.active
    )
    
    active_rooms = [r for r in rooms.values() if r.active]
    num_rooms = len(active_rooms)
    lab_rooms = [r for r in active_rooms if r.type == "lab"]
    classrooms = [r for r in active_rooms if r.type == "classroom"]
    
    working_days = len(settings.days)
    usable_periods = max(1, settings.periods_per_day - 1)  # subtracting lunch
    total_room_slots = num_rooms * working_days * usable_periods
    total_lab_slots = len(lab_rooms) * working_days * usable_periods
    
    # Calculate required lab hours
    required_lab_hours = 0
    for c in classes.values():
        if not c.active:
            continue
        for s_id, hrs in c.subject_requirements.items():
            sub = subjects.get(s_id)
            if sub and sub.type == "lab":
                required_lab_hours += hrs

    # Teacher capacity
    total_teacher_capacity = sum(t.max_weekly_load for t in teachers.values() if t.active)

    issues = []
    if total_required > total_room_slots:
        issues.append(
            f"Over-subscribed room capacity: Required teaching hours ({total_required}h) exceed available room slots ({total_room_slots}). Add more rooms or reduce curriculum hours."
        )

    if required_lab_hours > total_lab_slots:
        issues.append(
            f"Over-subscribed lab capacity: Required practical lab hours ({required_lab_hours}h) exceed lab room slots ({total_lab_slots}). Register additional lab rooms."
        )

    if total_required > total_teacher_capacity:
        issues.append(
            f"Insufficient faculty load capacity: Total demanded hours ({total_required}h) exceed total faculty weekly limit ({total_teacher_capacity}h)."
        )

    # Class strength vs room capacity check
    for c in classes.values():
        if not c.active:
            continue
        valid_classrooms = [r for r in classrooms if r.capacity >= c.strength]
        if not valid_classrooms:
            issues.append(
                f"Cohort {c.name} has strength {c.strength}, but no standard classroom has capacity >= {c.strength}."
            )

    is_solvable = len(issues) == 0
    utilization_rate = round((total_required / max(1, total_room_slots)) * 100, 1)

    return {
        "is_solvable": is_solvable,
        "total_required_hours": total_required,
        "total_room_slots": total_room_slots,
        "required_lab_hours": required_lab_hours,
        "total_lab_slots": total_lab_slots,
        "total_teacher_capacity": total_teacher_capacity,
        "utilization_rate_percent": utilization_rate,
        "issues": issues
    }

__all__ = ["ConstraintValidator", "perform_solvability_precheck"]
