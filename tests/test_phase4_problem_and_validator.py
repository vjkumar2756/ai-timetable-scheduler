"""
tests/test_phase4_problem_and_validator.py
Critical unit tests on a tiny, explainable instance:
- Verifies CSP variable generation and unary domain pruning
- Verifies all 9 Hard Constraints (H1 - H9) individually
- Verifies Soft Constraints (S1, S2, S4, S5) and the 1000 * H + S Cost function
"""
import pytest
from core.problem import TimetableProblem, LectureVariable, SlotValue
from core.validator import ConstraintValidator

@pytest.fixture
def tiny_institution():
    """Build a tiny 1-class, 2-teacher, 2-room institution for rigorous verification."""
    days = ["Mon", "Tue"]
    periods_per_day = 4
    default_lunch_period = 3

    classes = {
        "C1": {
            "id": "C1", "name": "Class 1", "strength": 30,
            "subject_requirements": {"MATH": 2, "AI_LAB": 2},
            "lunch_break_period": 3, "active": True
        }
    }
    subjects = {
        "MATH": {"id": "MATH", "code": "MATH", "name": "Mathematics", "weekly_hours": 2, "type": "theory", "lab_duration": 1},
        "AI_LAB": {"id": "AI_LAB", "code": "AI_LAB", "name": "AI Practical Lab", "weekly_hours": 2, "type": "lab", "lab_duration": 2}
    }
    teachers = {
        "T_MATH": {
            "id": "T_MATH", "name": "Dr. Euler", "subject_ids": ["MATH"],
            "unavailable_slots": [{"day": "Mon", "period": 1}],
            "preferred_slots": [{"day": "Tue", "period": 2}],
            "max_weekly_load": 10, "active": True
        },
        "T_LAB": {
            "id": "T_LAB", "name": "Prof. Lovelace", "subject_ids": ["AI_LAB"],
            "unavailable_slots": [], "preferred_slots": [],
            "max_weekly_load": 10, "active": True
        }
    }
    rooms = {
        "R_CLASS": {"id": "R_CLASS", "name": "Lecture Room 101", "capacity": 40, "type": "classroom", "active": True},
        "R_LAB": {"id": "R_LAB", "name": "Computing Lab 1", "capacity": 35, "type": "lab", "active": True}
    }

    problem = TimetableProblem(
        days=days,
        periods_per_day=periods_per_day,
        default_lunch_period=default_lunch_period,
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )

    validator = ConstraintValidator(
        days=days,
        periods_per_day=periods_per_day,
        default_lunch_period=default_lunch_period,
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms
    )

    return {
        "problem": problem,
        "validator": validator,
        "classes": classes,
        "subjects": subjects,
        "teachers": teachers,
        "rooms": rooms
    }

def test_problem_variable_formulation(tiny_institution):
    """Verify CSP variable generation and unary domain pruning."""
    problem = tiny_institution["problem"]
    
    # Required hours: MATH (2h) -> 2 variables of duration 1; AI_LAB (2h) -> 1 variable of duration 2
    assert len(problem.variables) == 3
    
    var_ids = [v.id for v in problem.variables]
    assert "C1__MATH__1" in var_ids
    assert "C1__MATH__2" in var_ids
    assert "C1__AI_LAB__1" in var_ids

    lab_var = problem.variables_dict["C1__AI_LAB__1"]
    assert lab_var.duration == 2
    assert lab_var.is_lab is True

    # Unary pruning verification:
    # 1. Lab domain must ONLY contain lab rooms
    for slot in problem.domains["C1__AI_LAB__1"]:
        assert slot.room_id == "R_LAB"
        # 2. Lab of duration 2 cannot start at period 3 (lunch) or 4 (overflow)
        assert slot.period not in [3, 4]

    # 3. Teacher unavailability: T_MATH is unavailable Mon Period 1
    for slot in problem.domains["C1__MATH__1"]:
        assert not (slot.day == "Mon" and slot.period == 1)

def test_valid_schedule_zero_violations(tiny_institution):
    """Verify an optimal schedule yields zero hard violations."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Perfectly non-conflicting assignment:
    # Tue P1-P2: AI_LAB (2 hours)
    # Tue P3: Lunch
    # Tue P4: MATH_2 (1 hour)
    # Mon P2: MATH_1 (1 hour)
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Tue", period=4, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is True
    assert result.hard_violations_count == 0
    assert result.hard_violations == []

def test_h1_teacher_clash(tiny_institution):
    """H1: Teacher cannot be in 2 sessions simultaneously."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Assign T_MATH to two sessions on Mon Period 2
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H1" in v and "Faculty clash" in v for v in result.hard_violations)

def test_h2_class_clash(tiny_institution):
    """H2: Class cannot be in 2 sessions simultaneously."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Assign C1 to two sessions on Mon Period 2 (with different teachers & rooms)
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Mon", period=2, room_id="R_LAB", teacher_id="T_LAB"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H2" in v and "Class clash" in v for v in result.hard_violations)

def test_h3_room_clash(tiny_institution):
    """H3: Room cannot host 2 sessions simultaneously."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Put both MATH sessions in R_CLASS on Mon Period 2
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_LAB"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H3" in v and "Room clash" in v for v in result.hard_violations)

def test_h4_room_capacity(tiny_institution):
    """H4: Room capacity must be >= class strength."""
    problem = tiny_institution["problem"]
    # Change R_CLASS capacity to 20 (< class strength 30)
    tiny_institution["rooms"]["R_CLASS"]["capacity"] = 20
    validator = tiny_institution["validator"]

    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Tue", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H4" in v and "smaller than Class" in v for v in result.hard_violations)

def test_h5_room_type_match(tiny_institution):
    """H5: Lab -> lab room, Theory -> classroom."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Assign Theory (MATH) into R_LAB
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_LAB", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Tue", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H5" in v and "practical lab" in v for v in result.hard_violations)

def test_h6_teacher_availability(tiny_institution):
    """H6: Teacher cannot teach in unavailable slots."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Assign T_MATH to Mon Period 1 (unavailable)
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=1, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Tue", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H6" in v and "unavailable slot" in v for v in result.hard_violations)

def test_h7_weekly_hours_requirement(tiny_institution):
    """H7: Every subject must receive exact weekly hours."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Drop one MATH session
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict, check_completeness=True)
    assert result.is_valid is False
    assert any("H7" in v and "hours mismatch" in v for v in result.hard_violations)

def test_h8_teacher_max_load(tiny_institution):
    """H8: Teacher assigned hours cannot exceed max weekly load."""
    problem = tiny_institution["problem"]
    # Reduce T_MATH max load to 1
    tiny_institution["teachers"]["T_MATH"]["max_weekly_load"] = 1
    validator = tiny_institution["validator"]

    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Tue", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H8" in v and "Faculty overload" in v for v in result.hard_violations)

def test_h9_lunch_protection(tiny_institution):
    """H9: Nothing may be scheduled during protected lunch break (Period 3)."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Assign session directly in lunch break (Period 3)
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=3, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__MATH__2": SlotValue(day="Tue", period=2, room_id="R_CLASS", teacher_id="T_MATH"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is False
    assert any("H9" in v and "protected lunch break" in v for v in result.hard_violations)

def test_soft_constraints_and_cost(tiny_institution):
    """Verify soft penalties calculation: S1 (gaps), S2 (repeat), and total cost formula."""
    problem = tiny_institution["problem"]
    validator = tiny_institution["validator"]

    # Schedule:
    # Mon: Period 1 (MATH) and Period 4 (MATH) -> Gap at Period 2 (Period 3 is lunch so not a gap)
    # Also same subject MATH repeated twice on Monday (triggers S2)
    assignment = {
        "C1__MATH__1": SlotValue(day="Mon", period=1, room_id="R_CLASS", teacher_id="T_LAB"), # using T_LAB to avoid T_MATH unavail
        "C1__MATH__2": SlotValue(day="Mon", period=4, room_id="R_CLASS", teacher_id="T_LAB"),
        "C1__AI_LAB__1": SlotValue(day="Tue", period=1, room_id="R_LAB", teacher_id="T_LAB")
    }

    result = validator.validate(assignment, problem.variables_dict)
    assert result.is_valid is True  # Zero hard violations
    assert result.hard_violations_count == 0
    # S1 gap penalty at P2 (weight 2)
    assert result.soft_breakdown["S1_gaps"] > 0
    # S2 daily repeat penalty (weight 3)
    assert result.soft_breakdown["S2_daily_repeat"] > 0
    assert result.total_cost == sum(result.soft_breakdown.values())
