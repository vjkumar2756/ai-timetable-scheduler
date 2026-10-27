from typing import List, Dict, Optional, Tuple, Any
from backend.app.database.store import db_store
from backend.app.models.entities import SwapRequest, InAppNotification, TimetableSession
from backend.app.scheduler.csp import TimetableCSP, SlotValue
from backend.app.scheduler.constraints import ConstraintValidator

class SwapService:
    @staticmethod
    def validate_swap(session_1_id: str, session_2_id: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
        if session_1_id not in db_store.sessions or session_2_id not in db_store.sessions:
            return False, "One or both session IDs not found in active schedule", []

        s1 = db_store.sessions[session_1_id]
        s2 = db_store.sessions[session_2_id]

        csp = TimetableCSP(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        validator = ConstraintValidator(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        var_map = csp.get_variable_map()

        # Build simulated assignment swapping the time-slots of s1 and s2
        simulated: Dict[str, SlotValue] = {}
        for s_id, sess in db_store.sessions.items():
            if s_id == session_1_id:
                # s1 gets s2's slot
                simulated[s_id] = SlotValue(
                    day=s2.day,
                    period=s2.period,
                    room_id=s1.room_id,
                    teacher_id=s1.teacher_id
                )
            elif s_id == session_2_id:
                # s2 gets s1's slot
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
            simulated, var_map, check_completeness=True
        )

        if not is_valid:
            reasons = "; ".join(v["message"] for v in violations)
            return False, f"Swap invalid due to hard constraint clashes: {reasons}", violations

        return True, "Swap is valid and satisfies all hard constraints", []

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

        # Notify teachers
        db_store.notifications.append(InAppNotification(
            recipient=target_teacher_id,
            title="Class Swap Approved",
            message=f"Swap approved between sessions {session_1_id} and {session_2_id}. Reason: {reason}",
            category="swap"
        ))

        return True, "Swap successfully executed and timetable updated", req
