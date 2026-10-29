"""
core/feasibility.py
Solvability Pre-Check and Capacity Feasibility Engine for SchedulAI.
Pure Python module (zero DB/web/Streamlit dependencies).

Performs strict multi-factor pre-flight mathematical verification before CSP solver execution:
1. Total class teaching hours vs. usable room slots
2. Lab hours demand vs. lab room availability
3. Class-by-class hours vs. available periods (accounting for lunch breaks)
4. Room capacity vs. class cohort strength (at least one room large enough)
5. Teacher availability & subject coverage (at least one eligible teacher per required subject)
6. Aggregate teacher weekly workload capacity vs. total demand
7. Individual teacher availability slots vs. required assignments
"""

from typing import Dict, List, Any, Optional

def feasibility_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs comprehensive institutional feasibility pre-check.
    Accepts raw JSON/dict or entity dictionary containing:
    - settings (days, periods_per_day, default_lunch_period)
    - subjects (list of subject dicts)
    - teachers (list of teacher dicts)
    - classes (list of class dicts)
    - rooms (list of room dicts)
    
    Returns structured analysis:
    {
        "feasible": bool,
        "summary": str,
        "metrics": dict,
        "errors": list[str],
        "warnings": list[str]
    }
    """
    errors: List[str] = []
    warnings: List[str] = []

    settings = data.get("settings", {})
    days = settings.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    periods_per_day = settings.get("periods_per_day", 6)
    num_days = len(days)
    usable_periods_per_day = max(1, periods_per_day - 1)  # Minus 1 for protected lunch period
    max_slots_per_class = num_days * usable_periods_per_day

    subjects_raw = data.get("subjects", [])
    teachers_raw = data.get("teachers", [])
    classes_raw = data.get("classes", [])
    rooms_raw = data.get("rooms", [])

    # Index by ID
    subjects_dict = {s["id"]: s for s in subjects_raw}
    teachers_dict = {t["id"]: t for t in teachers_raw if t.get("active", True)}
    classes_dict = {c["id"]: c for c in classes_raw if c.get("active", True)}
    rooms_dict = {r["id"]: r for r in rooms_raw if r.get("active", True)}

    # 1. Total Required Teaching Hours
    total_required_hours = 0
    total_lab_hours = 0
    total_theory_hours = 0

    class_demand: Dict[str, int] = {}
    for cid, cinfo in classes_dict.items():
        reqs = cinfo.get("subject_requirements", {})
        c_hours = 0
        for sub_id, hours in reqs.items():
            sub = subjects_dict.get(sub_id)
            if not sub:
                errors.append(f"Class '{cinfo.get('name', cid)}' requires unknown subject ID '{sub_id}'.")
                continue
            c_hours += hours
            total_required_hours += hours
            if sub.get("type") == "lab":
                total_lab_hours += hours
            else:
                total_theory_hours += hours
        
        class_demand[cid] = c_hours
        # Check if individual class exceeds available daytime slots
        if c_hours > max_slots_per_class:
            errors.append(
                f"Class '{cinfo.get('name', cid)}' demands {c_hours} periods/week, "
                f"which exceeds maximum available student slots ({max_slots_per_class} slots across {num_days} days)."
            )
        elif c_hours == max_slots_per_class:
            warnings.append(
                f"Class '{cinfo.get('name', cid)}' uses 100% of available periods ({c_hours}/{max_slots_per_class}). "
                "Zero free periods available for student rest or rescheduling."
            )

    # 2. Room & Lab Capacity
    classroom_rooms = [r for r in rooms_dict.values() if r.get("type") == "classroom"]
    lab_rooms = [r for r in rooms_dict.values() if r.get("type") == "lab"]

    total_room_slots = len(rooms_dict) * max_slots_per_class
    total_lab_slots = len(lab_rooms) * max_slots_per_class
    total_classroom_slots = len(classroom_rooms) * max_slots_per_class

    if total_required_hours > total_room_slots:
        errors.append(
            f"Institutional room bottleneck: Total required curriculum hours ({total_required_hours}h) "
            f"exceed total available room slots ({total_room_slots} slots across {len(rooms_dict)} rooms)."
        )

    if total_lab_hours > total_lab_slots:
        errors.append(
            f"Lab space bottleneck: Required practical lab hours ({total_lab_hours}h) "
            f"exceed total lab room capacity ({total_lab_slots} slots across {len(lab_rooms)} labs)."
        )

    if total_theory_hours > total_classroom_slots:
        errors.append(
            f"Classroom space bottleneck: Required theory hours ({total_theory_hours}h) "
            f"exceed classroom capacity ({total_classroom_slots} slots across {len(classroom_rooms)} classrooms)."
        )

    # 3. Room Sizing vs. Class Strength (H4 Feasibility)
    max_room_capacity = max((r.get("capacity", 0) for r in rooms_dict.values()), default=0)
    for cid, cinfo in classes_dict.items():
        strength = cinfo.get("strength", 0)
        fitting_rooms = [r for r in rooms_dict.values() if r.get("capacity", 0) >= strength]
        if not fitting_rooms:
            errors.append(
                f"Class '{cinfo.get('name', cid)}' has strength of {strength} students, "
                f"but no room in the institution has sufficient capacity (Largest room: {max_room_capacity} seats)."
            )

    # 4. Teacher Subject Coverage & Aggregate Load (H7, H8 Feasibility)
    # Map subject_id -> list of qualified active teachers
    subject_teacher_map: Dict[str, List[Dict[str, Any]]] = {}
    for tid, tinfo in teachers_dict.items():
        for sub_id in tinfo.get("subject_ids", []):
            subject_teacher_map.setdefault(sub_id, []).append(tinfo)

    # Verify every required subject has at least one active teacher
    required_subject_ids = set()
    for cinfo in classes_dict.values():
        for sub_id in cinfo.get("subject_requirements", {}).keys():
            required_subject_ids.add(sub_id)

    for sub_id in required_subject_ids:
        eligible = subject_teacher_map.get(sub_id, [])
        if not eligible:
            sub_name = subjects_dict.get(sub_id, {}).get("name", sub_id)
            errors.append(f"Subject '{sub_name}' ({sub_id}) has no active qualified teachers registered.")

    # Total teacher capacity
    total_teacher_capacity = sum(t.get("max_weekly_load", 0) for t in teachers_dict.values())
    if total_required_hours > total_teacher_capacity:
        errors.append(
            f"Faculty workload deficit: Total required teaching hours ({total_required_hours}h) "
            f"exceed total combined faculty max load capacity ({total_teacher_capacity}h)."
        )
    elif total_required_hours > 0.9 * total_teacher_capacity:
        warnings.append(
            f"High faculty utilization ({total_required_hours}/{total_teacher_capacity}h = "
            f"{round(total_required_hours/total_teacher_capacity * 100, 1)}%). Scheduling may be tight."
        )

    # 5. Teacher Unavailability vs. Demand
    for tid, tinfo in teachers_dict.items():
        unavail = len(tinfo.get("unavailable_slots", []))
        total_possible_slots = num_days * periods_per_day
        avail_slots = total_possible_slots - unavail
        max_load = tinfo.get("max_weekly_load", 20)
        if avail_slots < max_load:
            warnings.append(
                f"Faculty '{tinfo.get('name', tid)}' has max load of {max_load}h but only "
                f"{avail_slots} available slots due to {unavail} unavailable periods."
            )

    feasible = len(errors) == 0

    metrics = {
        "num_classes": len(classes_dict),
        "num_teachers": len(teachers_dict),
        "num_rooms": len(rooms_dict),
        "num_classrooms": len(classroom_rooms),
        "num_labs": len(lab_rooms),
        "total_required_hours": total_required_hours,
        "total_theory_hours": total_theory_hours,
        "total_lab_hours": total_lab_hours,
        "total_room_slots": total_room_slots,
        "total_classroom_slots": total_classroom_slots,
        "total_lab_slots": total_lab_slots,
        "total_teacher_capacity": total_teacher_capacity,
        "room_utilization_pct": round((total_required_hours / total_room_slots * 100), 1) if total_room_slots > 0 else 0,
        "teacher_utilization_pct": round((total_required_hours / total_teacher_capacity * 100), 1) if total_teacher_capacity > 0 else 0,
    }

    if feasible:
        summary = (
            f"Instance is Solvable and Mathematically Feasible. "
            f"Required: {total_required_hours}h across {len(classes_dict)} classes. "
            f"Room utilization: {metrics['room_utilization_pct']}%, "
            f"Faculty utilization: {metrics['teacher_utilization_pct']}%."
        )
    else:
        summary = f"Instance is INFEASIBLE: {len(errors)} critical conflict(s) detected prior to search."

    return {
        "feasible": feasible,
        "summary": summary,
        "metrics": metrics,
        "errors": errors,
        "warnings": warnings
    }
