"""
Synthetic Dataset Generator for SchedulAI.
Generates guaranteed solvable institutional instances for scaling and benchmark tests.
"""
import random
from typing import Dict, Any, List

def generate_synthetic_dataset(
    num_classes: int = 4,
    num_teachers: int = 8,
    num_rooms: int = 5,
    num_subjects: int = 8,
    periods_per_day: int = 6,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Constructs a solvable academic institutional configuration.
    """
    random.seed(seed)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    default_lunch = 4 if periods_per_day >= 5 else 3

    settings = {
        "days": days,
        "periods_per_day": periods_per_day,
        "default_lunch_period": default_lunch
    }

    # Generate Subjects (mixture of theory and labs)
    subjects = []
    subject_names = [
        "Data Structures", "Computer Networks", "Database Systems", "Machine Learning",
        "Operating Systems", "Discrete Mathematics", "Software Engineering", "Cyber Security",
        "Cloud Computing", "Computer Architecture", "Artificial Intelligence", "Web Technologies"
    ]
    for i in range(num_subjects):
        s_id = f"SUB_{i+1}"
        is_lab = (i % 4 == 0) # 25% labs
        name = subject_names[i % len(subject_names)] + (" Lab" if is_lab else "")
        subjects.append({
            "id": s_id,
            "code": f"CS{200 + i}",
            "name": name,
            "weekly_hours": 2 if is_lab else 3,
            "type": "lab" if is_lab else "theory",
            "lab_duration": 2 if is_lab else 1
        })

    # Generate Rooms (at least 1 lab per 3 classrooms)
    rooms = []
    num_labs = max(1, num_rooms // 3)
    num_classrooms = num_rooms - num_labs
    for i in range(num_classrooms):
        rooms.append({
            "id": f"R_CR_{i+1}",
            "name": f"Lecture Hall {101 + i}",
            "capacity": 60,
            "type": "classroom",
            "active": True
        })
    for i in range(num_labs):
        rooms.append({
            "id": f"R_LAB_{i+1}",
            "name": f"Computer Lab {i+1}",
            "capacity": 45,
            "type": "lab",
            "active": True
        })

    # Generate Teachers (each can teach 2-3 subjects)
    teachers = []
    faculty_names = [
        "Dr. Turing", "Prof. Lovelace", "Dr. Shannon", "Prof. Hopper", "Dr. Neumann",
        "Prof. Knuth", "Dr. Dijkstra", "Prof. Ritchie", "Dr. Lamport", "Prof. Berners-Lee"
    ]
    sub_ids = [s["id"] for s in subjects]
    for i in range(num_teachers):
        t_id = f"T_{i+1}"
        assigned_subs = random.sample(sub_ids, min(3, len(sub_ids)))
        # Occasional unavailable slot
        unavail = []
        if random.random() < 0.35:
            unavail.append({
                "day": random.choice(days),
                "period": random.choice([1, periods_per_day])
            })
        teachers.append({
            "id": t_id,
            "name": faculty_names[i % len(faculty_names)] + f" ({t_id})",
            "subject_ids": assigned_subs,
            "unavailable_slots": unavail,
            "max_weekly_load": 18,
            "preferred_slots": [{"day": random.choice(days), "period": 2}],
            "active": True
        })

    # Ensure every subject is teachable by at least one teacher
    covered_subs = {s for t in teachers for s in t["subject_ids"]}
    uncovered = set(sub_ids) - covered_subs
    for s in uncovered:
        teachers[0]["subject_ids"].append(s)

    # Generate Classes
    classes = []
    for i in range(num_classes):
        c_id = f"CLASS_{i+1}"
        # Pick 4-5 subjects per class
        chosen_subs = random.sample(subjects, min(5, len(subjects)))
        reqs = {s["id"]: s["weekly_hours"] for s in chosen_subs}
        classes.append({
            "id": c_id,
            "name": f"Cohort {chr(65 + i)} (Year {1 + (i % 4)})",
            "strength": 40,
            "subject_requirements": reqs,
            "lunch_break_period": default_lunch,
            "active": True
        })

    return {
        "settings": settings,
        "subjects": subjects,
        "teachers": teachers,
        "classes": classes,
        "rooms": rooms
    }
