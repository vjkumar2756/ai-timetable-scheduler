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
    def get_institutional_overview() -> Dict[str, Any]:
        total_classes = len([c for c in db_store.classes.values() if c.active])
        total_teachers = len([t for t in db_store.teachers.values() if t.active])
        total_rooms = len([r for r in db_store.rooms.values() if r.active])
        total_subjects = len(db_store.subjects)
        
        active_sessions = [s for s in db_store.sessions.values() if s.status != "cancelled"]
        cancelled_sessions = [s for s in db_store.sessions.values() if s.status == "cancelled"]
        total_teaching_hours = sum(s.duration for s in active_sessions)

        # Room utilization
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
