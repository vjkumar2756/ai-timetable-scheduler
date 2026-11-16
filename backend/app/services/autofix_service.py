"""
Auto-Fix and Absence / Substitute Helper Service for SchedulAI.
Provides:
1. Targeted local repair (Min-Conflicts / LNS) on conflicting slots without rebuilding entire timetable.
2. Faculty absence helper: lists affected sessions and ranks qualified available substitutes.
"""
from typing import Dict, List, Tuple, Any, Optional
from backend.app.database.store import db_store
from backend.app.models.entities import TimetableSession, Teacher
from backend.app.scheduler.csp import TimetableCSP, SlotValue
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction

class AutoFixService:
    @staticmethod
    def autofix_schedule(max_iterations: int = 300) -> Tuple[bool, str, int]:
        """
        Runs targeted iterative repair to eliminate clashes in the active timetable.
        Returns: (success, message, remaining_violations)
        """
        if not db_store.sessions:
            return False, "No active schedule to fix.", 0

        csp = TimetableCSP(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        validator = ConstraintValidator(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        var_map = csp.get_variable_map()

        current_assignment = {
            s_id: SlotValue(day=s.day, period=s.period, room_id=s.room_id, teacher_id=s.teacher_id)
            for s_id, s in db_store.sessions.items()
        }

        is_valid, initial_viols, viols_list = validator.validate_assignment(current_assignment, var_map, check_completeness=False)
        if is_valid:
            return True, "Schedule already has 0 hard constraint violations.", 0

        # Run local repair on conflicting variables
        for step in range(max_iterations):
            is_valid, current_h, v_list = validator.validate_assignment(current_assignment, var_map, check_completeness=False)
            if is_valid:
                # Update db_store sessions
                for vid, slot in current_assignment.items():
                    if vid in db_store.sessions:
                        db_store.sessions[vid].day = slot.day
                        db_store.sessions[vid].period = slot.period
                        db_store.sessions[vid].room_id = slot.room_id
                        db_store.sessions[vid].teacher_id = slot.teacher_id
                return True, f"Auto-Fix successfully eliminated all {initial_viols} clashes in {step+1} iterations!", 0

            # Collect conflicting var IDs
            conflicted_ids = set()
            for v in v_list:
                conflicted_ids.update(v.get("var_ids", []))

            if not conflicted_ids:
                break

            target_var_id = list(conflicted_ids)[0]
            var = var_map.get(target_var_id)
            if not var:
                continue

            # Find best slot minimizing clashes
            best_val = current_assignment[target_var_id]
            best_conflicts = float("inf")
            for cand_val in csp.domains[target_var_id]:
                current_assignment[target_var_id] = cand_val
                _, h_cnt, _ = validator.validate_assignment(current_assignment, var_map, check_completeness=False)
                if h_cnt < best_conflicts:
                    best_conflicts = h_cnt
                    best_val = cand_val

            current_assignment[target_var_id] = best_val

        # Final check
        is_valid, final_h, _ = validator.validate_assignment(current_assignment, var_map, check_completeness=False)
        if is_valid:
            for vid, slot in current_assignment.items():
                if vid in db_store.sessions:
                    db_store.sessions[vid].day = slot.day
                    db_store.sessions[vid].period = slot.period
                    db_store.sessions[vid].room_id = slot.room_id
                    db_store.sessions[vid].teacher_id = slot.teacher_id
            return True, f"Auto-Fix resolved all clashes!", 0
        else:
            return False, f"Auto-Fix reduced conflicts from {initial_viols} to {final_h}.", final_h

    @staticmethod
    def get_absence_and_substitutes(teacher_id: str, day: str) -> List[Dict[str, Any]]:
        """
        Identifies sessions affected by teacher absence on a day and suggests
        available qualified substitutes.
        """
        affected = [
            s for s in db_store.sessions.values()
            if s.teacher_id == teacher_id and s.day == day and s.status != "cancelled"
        ]

        results = []
        for sess in affected:
            cls = db_store.classes.get(sess.class_id)
            sub = db_store.subjects.get(sess.subject_id)
            rm = db_store.rooms.get(sess.room_id)

            # Find qualified substitutes
            qualified = [
                t for t in db_store.teachers.values()
                if t.id != teacher_id and t.active and sess.subject_id in t.subject_ids
            ]

            # Check who is free at this (day, period)
            available_subs = []
            for t in qualified:
                # Check teacher clash
                busy = any(
                    s.teacher_id == t.id and s.day == day and
                    s.period <= sess.period < (s.period + s.duration) and
                    s.status != "cancelled"
                    for s in db_store.sessions.values()
                )
                # Check unavailability
                unavail = any(
                    u.get("day") == day and u.get("period") == sess.period
                    for u in t.unavailable_slots
                )
                if not busy and not unavail:
                    available_subs.append({
                        "teacher_id": t.id,
                        "teacher_name": t.name,
                        "max_load": t.max_weekly_load
                    })

            results.append({
                "session_id": sess.id,
                "period": sess.period,
                "duration": sess.duration,
                "class_name": cls.name if cls else sess.class_id,
                "subject_name": sub.name if sub else sess.subject_id,
                "room_name": rm.name if rm else sess.room_id,
                "available_substitutes": available_subs
            })

        return results
