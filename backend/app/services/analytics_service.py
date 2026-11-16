from typing import Dict, List, Any
from collections import defaultdict
from backend.app.database.store import db_store

class AnalyticsService:
    @staticmethod
    def get_teacher_workload_analytics() -> List[Dict[str, Any]]:
        teacher_hours = defaultdict(int)
        teacher_sessions = defaultdict(int)
        teacher_subjects = defaultdict(lambda: defaultdict(int))

        for sess in db_store.sessions.values():
            if sess.status != "cancelled":
                teacher_hours[sess.teacher_id] += sess.duration
                teacher_sessions[sess.teacher_id] += 1
                sub = db_store.subjects.get(sess.subject_id)
                sub_label = sub.code if sub else sess.subject_id
                teacher_subjects[sess.teacher_id][sub_label] += sess.duration

        analytics = []
        for t_id, teacher in db_store.teachers.items():
            assigned = teacher_hours[t_id]
            max_load = teacher.max_weekly_load
            remaining = max(0, max_load - assigned)
            util_pct = round((assigned / max_load * 100), 1) if max_load > 0 else 0.0

            analytics.append({
                "teacher_id": t_id,
                "teacher_name": teacher.name,
                "max_weekly_load": max_load,
                "assigned_hours": assigned,
                "remaining_capacity": remaining,
                "utilization_percentage": util_pct,
                "session_count": teacher_sessions[t_id],
                "subject_distribution": dict(teacher_subjects[t_id]),
                "unavailable_slots_count": len(teacher.unavailable_slots),
                "is_overloaded": (assigned > max_load),
                "active": teacher.active
            })

        analytics.sort(key=lambda x: x["utilization_percentage"], reverse=True)
        return analytics

    @staticmethod
    def get_room_analytics() -> List[Dict[str, Any]]:
        room_hours = defaultdict(int)
        room_sessions = defaultdict(int)
        working_days = len(db_store.settings.days)
        usable_periods = max(1, db_store.settings.periods_per_day - 1)  # excluding lunch
        total_possible = working_days * usable_periods

        for sess in db_store.sessions.values():
            if sess.status != "cancelled":
                room_hours[sess.room_id] += sess.duration
                room_sessions[sess.room_id] += 1

        analytics = []
        for r_id, room in db_store.rooms.items():
            occupied = room_hours[r_id]
            util_pct = round((occupied / max(1, total_possible)) * 100, 1)
            analytics.append({
                "room_id": r_id,
                "room_name": room.name,
                "capacity": room.capacity,
                "type": room.type,
                "occupied_hours": occupied,
                "total_available_hours": total_possible,
                "utilization_percentage": util_pct,
                "session_count": room_sessions[r_id],
                "active": room.active
            })
        analytics.sort(key=lambda x: x["utilization_percentage"], reverse=True)
        return analytics

    @staticmethod
    def get_constraint_quality_analytics() -> Dict[str, Any]:
        from backend.app.scheduler.csp import TimetableCSP, SlotValue, LectureVariable
        from backend.app.scheduler.constraints import ConstraintValidator
        from backend.app.scheduler.cost_function import CostFunction

        active_sessions = {s_id: s for s_id, s in db_store.sessions.items() if s.status != "cancelled"}
        if not active_sessions:
            return {
                "has_schedule": False,
                "is_valid": True,
                "hard_violations_count": 0,
                "violations": [],
                "soft_penalty": 0,
                "penalty_breakdown": {},
                "compliance_score": 100.0,
                "explanations": []
            }

        csp = TimetableCSP(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        validator = ConstraintValidator(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        cost_fn = CostFunction(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        var_map = csp.get_variable_map()

        for s_id, sess in active_sessions.items():
            if s_id not in var_map:
                sub = db_store.subjects.get(sess.subject_id)
                var_map[s_id] = LectureVariable(
                    id=s_id,
                    class_id=sess.class_id,
                    subject_id=sess.subject_id,
                    session_index=1,
                    duration=sess.duration,
                    is_lab=(sub.type == "lab" if sub else False),
                    subject_code=sub.code if sub else sess.subject_id,
                    subject_name=sub.name if sub else sess.subject_id
                )

        assignment = {
            s_id: SlotValue(day=s.day, period=s.period, room_id=s.room_id, teacher_id=s.teacher_id)
            for s_id, s in active_sessions.items()
        }

        is_valid, hard_count, violations = validator.validate_assignment(assignment, var_map, check_completeness=False)
        soft_pen, breakdown, explanations = cost_fn.evaluate_soft_penalties(assignment, var_map)

        max_possible_penalty = max(100, len(active_sessions) * 15)
        raw_score = 100.0 - (soft_pen / max_possible_penalty * 100.0)
        compliance_score = max(0.0, round(raw_score, 1)) if is_valid else 0.0

        return {
            "has_schedule": True,
            "is_valid": is_valid,
            "hard_violations_count": hard_count,
            "violations": violations,
            "soft_penalty": soft_pen,
            "penalty_breakdown": breakdown,
            "compliance_score": compliance_score,
            "explanations": explanations[:15]
        }

    @staticmethod
    def get_institutional_overview() -> Dict[str, Any]:
        total_classes = len([c for c in db_store.classes.values() if c.active])
        total_teachers = len([t for t in db_store.teachers.values() if t.active])
        total_rooms = len([r for r in db_store.rooms.values() if r.active])
        total_subjects = len(db_store.subjects)
        
        active_sessions = [s for s in db_store.sessions.values() if s.status != "cancelled"]
        cancelled_sessions = [s for s in db_store.sessions.values() if s.status == "cancelled"]
        total_teaching_hours = sum(s.duration for s in active_sessions)

        working_days = len(db_store.settings.days)
        periods_per_day = db_store.settings.periods_per_day
        total_room_slots = total_rooms * working_days * periods_per_day
        room_utilization_pct = round((total_teaching_hours / max(1, total_room_slots)) * 100, 1)

        return {
            "total_classes": total_classes,
            "total_teachers": total_teachers,
            "total_rooms": total_rooms,
            "total_subjects": total_subjects,
            "scheduled_sessions": len(active_sessions),
            "cancelled_sessions": len(cancelled_sessions),
            "total_teaching_hours": total_teaching_hours,
            "room_utilization_pct": room_utilization_pct,
            "notifications_count": len(db_store.notifications),
            "schedule_metadata": db_store.current_schedule_metadata
        }
