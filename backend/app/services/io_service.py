import csv
import io
import json
from typing import Tuple, Dict, Any, List
from backend.app.database.store import db_store
from backend.app.models.entities import TimetableSession

class IOService:
    @staticmethod
    def export_timetable_csv() -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Session ID", "Class ID", "Class Name", "Subject Code",
            "Subject Name", "Teacher ID", "Teacher Name", "Room ID",
            "Room Name", "Day", "Period", "Duration", "Status"
        ])

        for sess in db_store.sessions.values():
            cls = db_store.classes.get(sess.class_id)
            sub = db_store.subjects.get(sess.subject_id)
            teacher = db_store.teachers.get(sess.teacher_id)
            room = db_store.rooms.get(sess.room_id)

            writer.writerow([
                sess.id,
                sess.class_id,
                cls.name if cls else sess.class_id,
                sub.code if sub else sess.subject_id,
                sub.name if sub else sess.subject_id,
                sess.teacher_id,
                teacher.name if teacher else sess.teacher_id,
                sess.room_id,
                room.name if room else sess.room_id,
                sess.day,
                sess.period,
                sess.duration,
                sess.status
            ])

        return output.getvalue()

    @staticmethod
    def import_dataset_json(data: dict) -> Tuple[bool, str]:
        try:
            # Validate required top-level keys
            for key in ["subjects", "teachers", "classes", "rooms"]:
                if key not in data or not isinstance(data[key], list):
                    return False, f"Missing or invalid section: '{key}'"

            # Validate non-empty
            if len(data["classes"]) == 0 or len(data["teachers"]) == 0 or len(data["rooms"]) == 0:
                return False, "Dataset must contain at least one class, teacher, and room"

            # Load into store
            db_store.load_from_dict(data)
            return True, f"Successfully imported {len(db_store.classes)} classes, {len(db_store.teachers)} teachers, {len(db_store.rooms)} rooms."
        except Exception as e:
            return False, f"Failed to parse and import dataset: {str(e)}"
