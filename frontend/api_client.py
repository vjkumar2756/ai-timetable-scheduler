"""
frontend/api_client.py
Resilient HTTP Client communicating between Streamlit and FastAPI backend.
Pure JSON/HTTP layer. Never exposes raw Python tracebacks to the UI.
"""
import os
import requests
from typing import Tuple, Dict, Any, Optional, List

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

class APIClient:
    @staticmethod
    def _get(endpoint: str, timeout: float = 10.0) -> Tuple[bool, Any, str]:
        url = f"{BACKEND_URL}{endpoint}"
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("success", True), data.get("data", data), data.get("message", "Success")
            return False, None, f"HTTP Error {r.status_code}: {r.text}"
        except Exception as e:
            return False, None, f"Backend connection failed: {str(e)}"

    @staticmethod
    def _post(endpoint: str, payload: Any = None, timeout: float = 35.0) -> Tuple[bool, Any, str]:
        url = f"{BACKEND_URL}{endpoint}"
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("success", True), data.get("data", data), data.get("message", "Success")
            return False, None, f"HTTP Error {r.status_code}: {r.text}"
        except Exception as e:
            return False, None, f"Backend connection failed: {str(e)}"

    @staticmethod
    def _put(endpoint: str, payload: Any = None, timeout: float = 10.0) -> Tuple[bool, Any, str]:
        url = f"{BACKEND_URL}{endpoint}"
        try:
            r = requests.put(url, json=payload, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("success", True), data.get("data", data), data.get("message", "Success")
            return False, None, f"HTTP Error {r.status_code}: {r.text}"
        except Exception as e:
            return False, None, f"Backend connection failed: {str(e)}"

    @staticmethod
    def _delete(endpoint: str, timeout: float = 10.0) -> Tuple[bool, Any, str]:
        url = f"{BACKEND_URL}{endpoint}"
        try:
            r = requests.delete(url, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data.get("success", True), data.get("data", data), data.get("message", "Success")
            return False, None, f"HTTP Error {r.status_code}: {r.text}"
        except Exception as e:
            return False, None, f"Backend connection failed: {str(e)}"

    # --- System & Datasets ---
    @classmethod
    def check_health(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/health", timeout=3.0)

    @classmethod
    def load_preset(cls, name: str) -> Tuple[bool, Any, str]:
        return cls._post(f"/api/datasets/load/{name}")

    @classmethod
    def get_feasibility(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/feasibility")

    # --- Entities ---
    @classmethod
    def get_settings(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/settings")

    @classmethod
    def update_settings(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._put("/api/settings", payload)

    @classmethod
    def get_teachers(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/teachers")

    @classmethod
    def create_teacher(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/teachers", payload)

    @classmethod
    def update_teacher(cls, teacher_id: str, payload: dict) -> Tuple[bool, Any, str]:
        return cls._put(f"/api/teachers/{teacher_id}", payload)

    @classmethod
    def delete_teacher(cls, teacher_id: str) -> Tuple[bool, Any, str]:
        return cls._delete(f"/api/teachers/{teacher_id}")

    @classmethod
    def get_classes(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/classes")

    @classmethod
    def create_class(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/classes", payload)

    @classmethod
    def update_class(cls, class_id: str, payload: dict) -> Tuple[bool, Any, str]:
        return cls._put(f"/api/classes/{class_id}", payload)

    @classmethod
    def delete_class(cls, class_id: str) -> Tuple[bool, Any, str]:
        return cls._delete(f"/api/classes/{class_id}")

    @classmethod
    def get_subjects(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/subjects")

    @classmethod
    def create_subject(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/subjects", payload)

    @classmethod
    def update_subject(cls, subject_id: str, payload: dict) -> Tuple[bool, Any, str]:
        return cls._put(f"/api/subjects/{subject_id}", payload)

    @classmethod
    def delete_subject(cls, subject_id: str) -> Tuple[bool, Any, str]:
        return cls._delete(f"/api/subjects/{subject_id}")

    @classmethod
    def get_rooms(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/rooms")

    @classmethod
    def create_room(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/rooms", payload)

    @classmethod
    def update_room(cls, room_id: str, payload: dict) -> Tuple[bool, Any, str]:
        return cls._put(f"/api/rooms/{room_id}", payload)

    @classmethod
    def delete_room(cls, room_id: str) -> Tuple[bool, Any, str]:
        return cls._delete(f"/api/rooms/{room_id}")

    # --- Schedule & Solvers ---
    @classmethod
    def generate_schedule(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/schedule/generate", payload, timeout=60.0)

    @classmethod
    def get_active_schedule(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/schedule")

    @classmethod
    def validate_manual_edit(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/schedule/validate-edit", payload)

    @classmethod
    def apply_manual_edit(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/schedule/manual-edit", payload)

    @classmethod
    def manual_edit(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/schedule/manual-edit", payload)

    # --- Analytics & Operations ---
    @classmethod
    def get_dashboard_summary(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/analytics/overview")

    @classmethod
    def get_workload_analytics(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/analytics/workload")

    @classmethod
    def get_room_analytics(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/analytics/rooms")

    @classmethod
    def get_quality_analytics(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/analytics/quality")

    @classmethod
    def get_notifications(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/operations/notifications")

    @classmethod
    def cancel_session(cls, session_id: str, reason: str) -> Tuple[bool, Any, str]:
        return cls._post("/api/operations/cancel-session", {"session_id": session_id, "reason": reason})

    @classmethod
    def close_class_day(cls, class_id: str, day: str, reason: str) -> Tuple[bool, Any, str]:
        return cls._post("/api/operations/close-class-day", {"class_id": class_id, "day": day, "reason": reason})

    @classmethod
    def get_cancellations(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/operations/cancellations")

    @classmethod
    def find_reschedule_slots(cls, session_id: str, alternative_teacher_id: Optional[str] = None) -> Tuple[bool, Any, str]:
        payload = {"session_id": session_id}
        if alternative_teacher_id:
            payload["alternative_teacher_id"] = alternative_teacher_id
        return cls._post("/api/operations/reschedule/find-slots", payload)

    @classmethod
    def apply_reschedule(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/operations/reschedule/apply", payload)

    @classmethod
    def get_reschedule_proposals(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/operations/reschedule/proposals")

    @classmethod
    def validate_swap(cls, session_1_id: str, session_2_id: str) -> Tuple[bool, Any, str]:
        return cls._post("/api/operations/swap/validate", {"session_1_id": session_1_id, "session_2_id": session_2_id})

    @classmethod
    def execute_swap(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/operations/swap/execute", payload)

    @classmethod
    def get_swaps(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/operations/swaps")

    # --- Import / Export ---
    @classmethod
    def export_dataset_json(cls) -> Tuple[bool, Any, str]:
        return cls._get("/api/io/export")

    @classmethod
    def import_dataset_json(cls, payload: dict) -> Tuple[bool, Any, str]:
        return cls._post("/api/io/import", payload)

    @staticmethod
    def get_csv_download_url() -> str:
        return f"{BACKEND_URL}/api/io/export-csv"

    @staticmethod
    def get_excel_download_url() -> str:
        return f"{BACKEND_URL}/api/io/export-excel"

    @staticmethod
    def get_pdf_download_url() -> str:
        return f"{BACKEND_URL}/api/io/export-pdf"

    @classmethod
    def get_csv_bytes(cls) -> bytes:
        try:
            r = requests.get(f"{BACKEND_URL}/api/io/export-csv", timeout=15.0)
            if r.status_code == 200:
                return r.content
        except Exception:
            pass
        return b""

    @classmethod
    def get_excel_bytes(cls) -> bytes:
        try:
            r = requests.get(f"{BACKEND_URL}/api/io/export-excel", timeout=15.0)
            if r.status_code == 200:
                return r.content
        except Exception:
            pass
        return b""

    @classmethod
    def get_pdf_bytes(cls) -> bytes:
        try:
            r = requests.get(f"{BACKEND_URL}/api/io/export-pdf", timeout=15.0)
            if r.status_code == 200:
                return r.content
        except Exception:
            pass
        return b""
