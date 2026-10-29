from typing import List, Optional, Tuple
from datetime import datetime
from backend.app.database.store import db_store
from backend.app.models.entities import CancellationRecord, InAppNotification

class CancellationService:
    @staticmethod
    def cancel_session(session_id: str, reason: str) -> Tuple[bool, str, Optional[CancellationRecord]]:
        if session_id not in db_store.sessions:
            return False, f"Session {session_id} not found", None

        sess = db_store.sessions[session_id]
        sess.status = "cancelled"
        if not sess.original_slot:
            sess.original_slot = {}
        sess.original_slot["cancellation_reason"] = reason
        
        record = CancellationRecord(
            scope="session",
            class_id=sess.class_id,
            session_id=session_id,
            day=sess.day,
            period=sess.period,
            reason=reason,
            affected_session_ids=[session_id]
        )
        db_store.cancellations.append(record)

        # Generate in-app notifications
        teacher = db_store.teachers.get(sess.teacher_id)
        cls = db_store.classes.get(sess.class_id)
        sub = db_store.subjects.get(sess.subject_id)
        sub_name = sub.name if sub else sess.subject_id
        t_name = teacher.name if teacher else sess.teacher_id
        c_name = cls.name if cls else sess.class_id

        # Notification for teacher
        db_store.notifications.append(InAppNotification(
            recipient=sess.teacher_id,
            title="Class Session Cancelled",
            message=f"Your lecture for '{sub_name}' with {c_name} on {sess.day} (Period {sess.period}) was cancelled. Reason: {reason}",
            category="cancellation"
        ))

        # Notification for class
        db_store.notifications.append(InAppNotification(
            recipient=sess.class_id,
            title="Lecture Cancelled",
            message=f"Lecture '{sub_name}' by {t_name} on {sess.day} (Period {sess.period}) has been cancelled. Reason: {reason}",
            category="cancellation"
        ))

        return True, "Session cancelled and in-app notifications recorded", record

    @staticmethod
    def close_class_day(class_id: str, day: str, reason: str) -> Tuple[bool, str, Optional[CancellationRecord]]:
        if class_id not in db_store.classes:
            return False, f"Class {class_id} not found", None

        affected = []
        for s_id, sess in db_store.sessions.items():
            if sess.class_id == class_id and sess.day == day and sess.status != "cancelled":
                sess.status = "cancelled"
                affected.append(s_id)

        record = CancellationRecord(
            scope="full_class_day",
            class_id=class_id,
            day=day,
            reason=reason,
            affected_session_ids=affected
        )
        db_store.cancellations.append(record)

        cls = db_store.classes.get(class_id)
        c_name = cls.name if cls else class_id

        db_store.notifications.append(InAppNotification(
            recipient=class_id,
            title=f"All Classes Cancelled for {c_name} on {day}",
            message=f"Classes suspended on {day} ({len(affected)} sessions affected). Reason: {reason}",
            category="cancellation"
        ))

        return True, f"Class closed for {day}: {len(affected)} sessions cancelled", record
