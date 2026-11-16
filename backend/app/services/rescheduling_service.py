from typing import List, Dict, Optional, Tuple, Any
from backend.app.database.store import db_store
from backend.app.models.entities import ReschedulingProposal, InAppNotification, TimetableSession
from backend.app.scheduler.csp import TimetableCSP, SlotValue, LectureVariable
from backend.app.scheduler.constraints import ConstraintValidator
from backend.app.scheduler.cost_function import CostFunction

class ReschedulingService:
    @staticmethod
    def find_reschedule_options(
        session_id: str,
        alternative_teacher_id: Optional[str] = None,
        max_suggestions: int = 5
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        if session_id not in db_store.sessions:
            return False, f"Session {session_id} not found", []

        sess = db_store.sessions[session_id]
        cls = db_store.classes.get(sess.class_id)
        sub = db_store.subjects.get(sess.subject_id)
        if not cls or not sub:
            return False, "Referenced class or subject missing", []

        # Qualified teachers
        target_teacher_id = alternative_teacher_id or sess.teacher_id
        teacher = db_store.teachers.get(target_teacher_id)
        if not teacher or sess.subject_id not in teacher.subject_ids:
            return False, f"Teacher {target_teacher_id} is not qualified for subject {sub.name}", []

        csp = TimetableCSP(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        validator = ConstraintValidator(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        cost_fn = CostFunction(db_store.settings, db_store.classes, db_store.subjects, db_store.teachers, db_store.rooms)
        var_map = csp.get_variable_map()

        duration = sess.duration
        is_lab = (sub.type == "lab")
        eligible_rooms = [
            r for r in db_store.rooms.values()
            if r.active and r.capacity >= cls.strength and (
                (is_lab and r.type == "lab") or
                (not is_lab and r.type == "classroom")
            )
        ]

        # Ensure all existing sessions have a corresponding variable in var_map
        for s_id, other_s in db_store.sessions.items():
            if s_id not in var_map:
                o_sub = db_store.subjects.get(other_s.subject_id)
                var_map[s_id] = LectureVariable(
                    id=s_id,
                    class_id=other_s.class_id,
                    subject_id=other_s.subject_id,
                    session_index=1,
                    duration=other_s.duration,
                    is_lab=(o_sub.type == "lab" if o_sub else False),
                    subject_code=o_sub.code if o_sub else other_s.subject_id,
                    subject_name=o_sub.name if o_sub else other_s.subject_id
                )

        if session_id not in var_map:
            var_map[session_id] = LectureVariable(
                id=session_id,
                class_id=sess.class_id,
                subject_id=sess.subject_id,
                session_index=1,
                duration=sess.duration,
                is_lab=is_lab,
                subject_code=sub.code,
                subject_name=sub.name
            )

        # Precompute base assignment without the cancelled slot
        simulated_base: Dict[str, SlotValue] = {}
        for s_id, other_s in db_store.sessions.items():
            if s_id == session_id:
                continue
            if other_s.status != "cancelled":
                simulated_base[s_id] = SlotValue(
                    day=other_s.day,
                    period=other_s.period,
                    room_id=other_s.room_id,
                    teacher_id=other_s.teacher_id
                )

        valid_options = []

        # Check candidate slots across working schedule
        for day in db_store.settings.days:
            for period in range(1, db_store.settings.periods_per_day - duration + 2):
                occupied = range(period, period + duration)
                # H9: Lunch break
                if cls.lunch_break_period in occupied:
                    continue

                # H6: Teacher unavailable slots
                teacher_unavail = any(
                    un.get("day") == day and un.get("period") in occupied
                    for un in teacher.unavailable_slots
                )
                if teacher_unavail:
                    continue

                for room in eligible_rooms:
                    candidate_slot = SlotValue(day=day, period=period, room_id=room.id, teacher_id=teacher.id)
                    simulated = dict(simulated_base)
                    simulated[session_id] = candidate_slot

                    # Validate hard constraints (H1 - H9)
                    is_valid, hard_count, _ = validator.validate_assignment(
                        simulated, var_map, check_completeness=False
                    )

                    if is_valid:
                        soft_pen, _, _ = cost_fn.evaluate_soft_penalties(simulated, var_map)
                        valid_options.append({
                            "day": day,
                            "period": period,
                            "room_id": room.id,
                            "room_name": room.name,
                            "teacher_id": teacher.id,
                            "teacher_name": teacher.name,
                            "soft_penalty": soft_pen
                        })

        if not valid_options:
            return True, "No clash-free slot found matching all 9 hard constraints", []

        # Rank suggestions by best (lowest) soft penalty score
        valid_options.sort(key=lambda x: x["soft_penalty"])
        return True, f"Found {len(valid_options)} feasible alternative slots", valid_options[:max_suggestions]

    @staticmethod
    def apply_reschedule(
        session_id: str,
        target_day: str,
        target_period: int,
        target_room_id: str,
        target_teacher_id: str,
        reason: str = "Missed lecture rescheduled"
    ) -> Tuple[bool, str, Optional[ReschedulingProposal]]:
        if session_id not in db_store.sessions:
            return False, f"Session {session_id} not found", None

        sess = db_store.sessions[session_id]
        
        # Verify slot feasibility
        _, _, options = ReschedulingService.find_reschedule_options(
            session_id, alternative_teacher_id=target_teacher_id, max_suggestions=100
        )
        match = any(
            opt["day"] == target_day and opt["period"] == target_period and
            opt["room_id"] == target_room_id and opt["teacher_id"] == target_teacher_id
            for opt in options
        )
        if not match:
            return False, "Target slot violates one or more hard constraints (clash, capacity, or teacher availability)", None

        # Apply rescheduling
        sess.original_slot = {"day": sess.day, "period": sess.period, "room_id": sess.room_id, "teacher_id": sess.teacher_id}
        sess.day = target_day
        sess.period = target_period
        sess.room_id = target_room_id
        sess.teacher_id = target_teacher_id
        sess.status = "rescheduled"

        proposal = ReschedulingProposal(
            missed_session_id=session_id,
            proposed_teacher_id=target_teacher_id,
            proposed_room_id=target_room_id,
            proposed_day=target_day,
            proposed_period=target_period,
            status="approved",
            reason=reason
        )
        db_store.rescheduling_proposals.append(proposal)

        # Notify affected parties
        sub = db_store.subjects.get(sess.subject_id)
        sub_name = sub.name if sub else sess.subject_id
        db_store.notifications.append(InAppNotification(
            recipient=sess.teacher_id,
            title="Lecture Rescheduled",
            message=f"Lecture for '{sub_name}' has been rescheduled to {target_day} period {target_period}.",
            category="reschedule"
        ))
        db_store.notifications.append(InAppNotification(
            recipient=sess.class_id,
            title="Lecture Rescheduled",
            message=f"Lecture for '{sub_name}' has been rescheduled to {target_day} period {target_period}.",
            category="reschedule"
        ))

        return True, "Lecture successfully rescheduled to feasible slot", proposal
