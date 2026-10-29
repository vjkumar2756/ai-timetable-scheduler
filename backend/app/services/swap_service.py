from typing import List, Dict, Optional, Tuple, Any
from backend.app.database.store import db_store
from backend.app.models.entities import SwapRequest, InAppNotification, TimetableSession
from backend.app.scheduler.csp import TimetableCSP, SlotValue, LectureVariable
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction

class SwapService:
    @staticmethod
    def validate_swap(session_1_id: str, session_2_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        if session_1_id not in db_store.sessions or session_2_id not in db_store.sessions:
            return False, "One or both session IDs not found in active schedule", []

        s1 = db_store.sessions[session_1_id]
        s2 = db_store.sessions[session_2_id]

        if s1.status == "cancelled" or s2.status == "cancelled":
            return False, "Cannot swap cancelled sessions. Please reschedule them instead.", []

        if s1.duration != s2.duration:
            return False, f"Cannot swap sessions of differing durations ({s1.duration}h vs {s2.duration}h). Both sessions must have identical durations.", []

        if s1.day == s2.day and s1.period == s2.period:
            return False, "Sessions are already scheduled in the exact same time slot.", []

        csp = TimetableCSP(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        validator = ConstraintValidator(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        var_map = csp.get_variable_map()

        # Ensure all sessions have variable entries in var_map
        for s_id, sess in db_store.sessions.items():
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

        # Build simulated assignment swapping the time-slots of s1 and s2
        simulated: Dict[str, SlotValue] = {}
        for s_id, sess in db_store.sessions.items():
            if sess.status == "cancelled":
                continue
            if s_id == session_1_id:
                # s1 gets s2's time slot
                simulated[s_id] = SlotValue(
                    day=s2.day,
                    period=s2.period,
                    room_id=s1.room_id,
                    teacher_id=s1.teacher_id
                )
            elif s_id == session_2_id:
                # s2 gets s1's time slot
                simulated[s_id] = SlotValue(
                    day=s1.day,
                    period=s1.period,
                    room_id=s2.room_id,
                    teacher_id=s2.teacher_id
                )
            else:
                simulated[s_id] = SlotValue(
                    day=sess.day,
                    period=sess.period,
                    room_id=sess.room_id,
                    teacher_id=sess.teacher_id
                )

        is_valid, hard_count, violations = validator.validate_assignment(
            simulated, var_map, check_completeness=False
        )

        if not is_valid:
            reasons = "; ".join(v.get("message", str(v)) for v in violations)
            return False, f"Swap violates institutional constraints: {reasons}", violations

        return True, "Swap is collision-free and satisfies all 9 Hard Constraints (H1–H9)", []

    @classmethod
    def execute_swap(
        cls,
        session_1_id: str,
        session_2_id: str,
        requester_teacher_id: str,
        reason: str = "Teacher schedule exchange"
    ) -> Tuple[bool, str, Optional[SwapRequest]]:
        is_valid, msg, violations = cls.validate_swap(session_1_id, session_2_id)
        if not is_valid:
            return False, msg, None

        s1 = db_store.sessions[session_1_id]
        s2 = db_store.sessions[session_2_id]

        # Exchange time slots
        temp_day, temp_period = s1.day, s1.period
        s1.day, s1.period = s2.day, s2.period
        s2.day, s2.period = temp_day, temp_period

        target_teacher_id = s2.teacher_id if requester_teacher_id == s1.teacher_id else s1.teacher_id

        req = SwapRequest(
            requester_teacher_id=requester_teacher_id,
            session_1_id=session_1_id,
            session_2_id=session_2_id,
            target_teacher_id=target_teacher_id,
            status="approved",
            reason=reason
        )
        db_store.swap_requests.append(req)

        # Notify both teachers
        t1 = db_store.teachers.get(s1.teacher_id)
        t2 = db_store.teachers.get(s2.teacher_id)
        t1_name = t1.name if t1 else s1.teacher_id
        t2_name = t2.name if t2 else s2.teacher_id

        db_store.notifications.append(InAppNotification(
            recipient=s1.teacher_id,
            title="Lecture Swap Approved",
            message=f"Swap approved with {t2_name}. Your session moved to {s1.day} Period {s1.period}.",
            category="swap"
        ))
        if s2.teacher_id != s1.teacher_id:
            db_store.notifications.append(InAppNotification(
                recipient=s2.teacher_id,
                title="Lecture Swap Approved",
                message=f"Swap approved with {t1_name}. Your session moved to {s2.day} Period {s2.period}.",
                category="swap"
            ))

        return True, "Swap successfully executed and timetable updated", req
