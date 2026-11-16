"""
tests/test_phase3_crud_and_io.py
Comprehensive test suite for Phase 3:
- CRUD for Teachers, Subjects, Classes, Rooms, Settings
- Preset dataset loaders (small, large)
- Feasibility precheck endpoint
- JSON import with solvability validation
- Export endpoints (JSON, CSV, Excel, PDF)
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_load_small_dataset():
    """Verify loading Small preset dataset."""
    res = client.post("/api/datasets/load/small")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["classes"] == 3
    assert data["data"]["teachers"] == 6

def test_load_large_dataset():
    """Verify loading Large preset dataset."""
    res = client.post("/api/datasets/load/large")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["classes"] == 8
    assert data["data"]["teachers"] == 16

def test_feasibility_endpoint():
    """Verify feasibility precheck endpoint returns detailed report."""
    # First ensure small dataset is active
    client.post("/api/datasets/load/small")
    res = client.get("/api/feasibility")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "metrics" in data["data"]
    assert data["data"]["feasible"] is True

def test_teacher_crud():
    """Verify Teacher CRUD operations."""
    new_teacher = {
        "id": "T_TEST_1",
        "name": "Prof. Test Einstein",
        "subject_ids": ["CS101"],
        "unavailable_slots": [{"day": "Fri", "period": 5}],
        "max_weekly_load": 12,
        "preferred_slots": [{"day": "Mon", "period": 1}],
        "active": True
    }
    # Create
    res = client.post("/api/teachers", json=new_teacher)
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Get Single
    res = client.get("/api/teachers/T_TEST_1")
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Prof. Test Einstein"

    # Update
    new_teacher["max_weekly_load"] = 16
    res = client.put("/api/teachers/T_TEST_1", json=new_teacher)
    assert res.status_code == 200
    assert res.json()["data"]["max_weekly_load"] == 16

    # Deactivate
    res = client.delete("/api/teachers/T_TEST_1")
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Verify deactivated
    res = client.get("/api/teachers/T_TEST_1")
    assert res.json()["data"]["active"] is False

def test_subject_crud():
    """Verify Subject CRUD operations."""
    new_subj = {
        "id": "CS999",
        "code": "CS999",
        "name": "Quantum Computing",
        "weekly_hours": 3,
        "type": "theory",
        "lab_duration": 1
    }
    # Create
    res = client.post("/api/subjects", json=new_subj)
    assert res.status_code == 200

    # Get
    res = client.get("/api/subjects/CS999")
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Quantum Computing"

    # Update
    new_subj["weekly_hours"] = 4
    res = client.put("/api/subjects/CS999", json=new_subj)
    assert res.status_code == 200
    assert res.json()["data"]["weekly_hours"] == 4

    # Delete
    res = client.delete("/api/subjects/CS999")
    assert res.status_code == 200

def test_room_crud():
    """Verify Room CRUD operations."""
    new_room = {
        "id": "R_TEST",
        "name": "Robotics Arena",
        "capacity": 45,
        "type": "lab",
        "active": True
    }
    # Create
    res = client.post("/api/rooms", json=new_room)
    assert res.status_code == 200

    # Get
    res = client.get("/api/rooms/R_TEST")
    assert res.status_code == 200
    assert res.json()["data"]["capacity"] == 45

    # Deactivate
    res = client.delete("/api/rooms/R_TEST")
    assert res.status_code == 200

def test_export_endpoints():
    """Verify JSON, CSV, Excel, and PDF export endpoints."""
    # Ensure dataset is loaded
    client.post("/api/datasets/load/small")

    # JSON export
    res = client.get("/api/export")
    assert res.status_code == 200
    assert "subjects" in res.json()["data"]

    # CSV export
    res = client.get("/api/io/export-csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]

    # Excel export
    res = client.get("/api/io/export-excel")
    assert res.status_code == 200
    assert "openxmlformats" in res.headers["content-type"]

    # PDF export
    res = client.get("/api/io/export-pdf")
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]

def test_import_infeasible_dataset_rejection():
    """Verify importing an unfeasible dataset returns clear rejection with errors."""
    infeasible_payload = {
        "settings": {"days": ["Mon"], "periods_per_day": 2, "default_lunch_period": 2},
        "subjects": [{"id": "S1", "code": "S1", "name": "Heavy Math", "weekly_hours": 100, "type": "theory", "lab_duration": 1}],
        "teachers": [{"id": "T1", "name": "Prof. Solo", "subject_ids": ["S1"], "max_weekly_load": 5, "unavailable_slots": [], "preferred_slots": []}],
        "classes": [{"id": "C1", "name": "Batch 1", "strength": 100, "subject_requirements": {"S1": 100}, "lunch_break_period": 2}],
        "rooms": [{"id": "R1", "name": "Tiny Room", "capacity": 10, "type": "classroom"}]
    }
    res = client.post("/api/io/import", json=infeasible_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is False
    assert len(body["errors"]) > 0
    assert any("exceed" in e["error"] or "capacity" in e["error"] for e in body["errors"])
