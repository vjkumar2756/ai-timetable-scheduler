<p align="center">
  <img src="assets/logo.png" alt="SchedulAI Logo" width="170" style="border-radius: 50%; background: #ffffff; box-shadow: 0 8px 30px rgba(0,0,0,0.25); border: 4px solid #ffffff;" />
</p>

# SchedulAI — AI-Based College Timetable Scheduler

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-FF4B4B.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Pytest](https://img.shields.io/badge/Tests-85%20Passing-brightgreen.svg)]()
[![Constraints](https://img.shields.io/badge/Constraints-H1--H9%20Strict%20Zero-emerald.svg)]()
[![Bonus](https://img.shields.io/badge/Bonus-Simulated%20Annealing%20%2B%20Hybrid-purple.svg)]()

> **Automated Constraint Satisfaction Problem (CSP) Timetable Generator & Optimization Engine:** Generates clash-free academic timetables in seconds using systematic search and local search heuristics, complete with an interactive web dashboard, Dark/Light modes, and instant 1-click PDF/Excel/CSV exports.

---

## 🎯 What Problem Does This Project Solve?

In universities and colleges, preparing a master weekly timetable manually is a slow, complex, and error-prone process. Academic coordinators typically spend weeks arranging lectures on spreadsheets while trying to balance teachers, student batches, rooms, and labs.

### The Real-World Challenges:
- **Clashes & Double-Bookings:** A faculty member or student class accidentally assigned to two different rooms at the same time.
- **Resource & Room Mismatches:** Large classes assigned to rooms that are too small, or specialized lab sessions scheduled in regular lecture halls without computers.
- **Academic Disruption:** Scattered timetables with 2-to-3-hour empty gaps for students, or faculty burdened with 4+ consecutive lecture hours.
- **Mid-Semester Changes:** When a teacher takes leave or a lecture is missed, finding a conflict-free replacement slot manually causes a domino effect of new clashes.

### How SchedulAI Solves It:
- **Zero Clashes Guaranteed:** Formulates timetabling as a formal **Constraint Satisfaction Problem (CSP)**, strictly enforcing all 9 institutional hard constraints ($H_1$–$H_9$).
- **Instant Generation:** Solves both small and large institutional timetables in seconds using AI search algorithms (Backtracking with MRV/FC, Min-Conflicts, and Hybrid Simulated Annealing).
- **Quality Optimization:** Optimizes 5 soft preferences ($S_1$–$S_5$) to eliminate student idle gaps, spread subjects evenly across the week, and prevent teacher burnout.
- **Operational Web Dashboard:** Provides real-time conflict-aware slot editing, automated missed-lecture rescheduling, faculty class-swap validation, dark/light mode toggle, and 1-click downloads.

---

## 🚀 Quick Start & How to Run

### 1. Installation
Clone or navigate to the repository and install all required production dependencies:
```bash
cd ai-timetable-scheduler
pip install -r requirements.txt
```

### 2. Start the Backend API (FastAPI)
Launch the asynchronous REST API server:
```bash
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation will be accessible at: **`http://localhost:8000/docs`**

### 3. Launch the Web Application (Streamlit)
In a separate terminal, launch the Streamlit frontend:
```bash
streamlit run streamlit_app.py --server.port 8501
```
Open **`http://localhost:8501`** in your browser.

### 4. Run Automated Test Verification
Run the comprehensive pytest suite covering all project phases:
```bash
pytest -v
```
*(All 85 unit and integration tests pass cleanly in ~8 seconds).*

---

## 🏛️ System Architecture

SchedulAI follows a clean, modular architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│   (Dashboard, Timetable Grid, Solvers, Operations, Analytics)│
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI REST Backend                     │
│    (CRUD Routes, Schedule Engine, Analytics, PDF/Excel IO)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Python API
┌──────────────────────────────▼──────────────────────────────┐
│                  Pure Python Algorithmic Core               │
│   ┌──────────────────────────┐  ┌────────────────────────┐  │
│   │   Timetable Problem CSP  │  │ Authoritative Validator │  │
│   │    (Variables & Domains) │  │  (H1–H9 & S1–S5 Cost)   │  │
│   └─────────────┬────────────┘  └───────────┬────────────┘  │
│                 │                           │               │
│   ┌─────────────▼───────────────────────────▼────────────┐  │
│   │                Algorithms & Solvers                  │  │
│   │  • Plain Backtracking (Baseline)                     │  │
│   │  • Improved Backtracking (MRV + Degree + FC + LCV)   │  │
│   │  • Min-Conflicts (Local Search + Random Walk)        │  │
│   │  • Simulated Annealing (+6 Bonus Marks)              │  │
│   │  • Hybrid CSP + SA (+6 Bonus Marks)                  │  │
│   └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Constraint Traceability Matrix

### Hard Constraints ($H_1\text{--}H_9$ — Zero Tolerance: $H = 0$)
Every generated schedule is verified against the authoritative `ConstraintValidator` before acceptance:

| Code | Constraint Name | Mathematical Formulation / Rule | Implementation Mechanism |
| :---: | :--- | :--- | :--- |
| **$H_1$** | **Teacher Clash** | No instructor assigned to $>1$ session at the same time | Slot collision hash map |
| **$H_2$** | **Class Clash** | No student class scheduled for $>1$ session at the same time | Cohort time-slot indexing |
| **$H_3$** | **Room Clash** | No room booked for $>1$ session at the same time | Facility occupancy map |
| **$H_4$** | **Room Capacity** | $\text{Room Capacity} \ge \text{Class Strength}$ | Domain unary pre-pruning |
| **$H_5$** | **Room Type Match** | Theory $\rightarrow$ Classroom; Practical Lab $\rightarrow$ Laboratory | Domain unary pre-pruning |
| **$H_6$** | **Teacher Availability** | Assigned slot $\notin \text{Teacher Unavailable Slots}$ | Upfront domain pruning |
| **$H_7$** | **Curriculum Hours** | Total scheduled hours equals prescribed weekly quota | Variable set completeness |
| **$H_8$** | **Teacher Max Load** | $\text{Assigned Hours} \le \text{Max Contractual Weekly Load}$ | Load-balanced assignment |
| **$H_9$** | **Lunch Break** | Cohort lunch break period is kept completely clear | Period exclusion pruning |

### Soft Constraints ($S_1\text{--}S_5$ — Penalty Minimization)
$$S = 5 \cdot S_1 + 15 \cdot S_2 + 20 \cdot S_3 + 10 \cdot S_4 + 12 \cdot S_5$$
- **$S_1$ — Free Period Gaps ($w=5$):** Minimizes idle windows between classes for student cohorts.
- **$S_2$ — Daily Subject Repeat ($w=15$):** Distributes lectures across different days of the week.
- **$S_3$ — Lab Continuity ($w=20$):** Multi-period lab sessions must run consecutively (guaranteed by atomic 2-period modeling).
- **$S_4$ — Teacher Slot Preferences ($w=10$):** Honors faculty declared preferred teaching windows.
- **$S_5$ — Consecutive Teaching Pacing ($w=12$):** Penalizes assigning $>2$ consecutive lecture periods to an instructor.

Total Cost Function:
$$\text{Cost} = 1000 \times H + S$$

---

## 🏆 Real Empirical Benchmark Results (10 Seeded Runs)

Empirical metrics recorded from [`experiments/results/benchmark_results.json`](experiments/results/benchmark_results.json):

| Algorithm | Category | Small Dataset (3C, 6T)<br/>Runtime (s) | Large Dataset (8C, 16T)<br/>Runtime (s) | Hard Clashes ($H$) | Soft Penalty (Large Dataset) | Success Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Plain Backtracking** | Baseline Systematic | 0.0021s | 0.0313s | **0** | 2,310 pts | 100% |
| **Improved Backtracking** | MRV + Degree + FC + LCV | 0.1099s | 3.4456s | **0** | 1,482 pts | 100% |
| **Min-Conflicts** | Local Search ($p=0.08$) | 0.0058s | 0.0783s | **0** | 1,438 pts | 100% |
| **Simulated Annealing** | Metaheuristic (+6 Bonus) | 0.0948s | 0.2989s | $\le 1$ | 1,096 pts | 10% |
| **Hybrid CSP + SA** | Two-Stage (+6 Bonus) | 0.1863s | 3.8833s | **0** | **1,083 pts** | **100%** |

*Takeaway:* **Hybrid CSP + SA** achieves the absolute best timetable quality (lowest soft penalty) while mathematically guaranteeing 0 hard violations.

---

## 📁 Repository Directory Layout

```
ai-timetable-scheduler/
├── backend/app/                 # FastAPI REST Application
│   ├── api/routes/              # entities, schedule, operations, analytics, io_routes
│   ├── database/                # SQLite engine & in-memory DataStore singleton
│   ├── models/                  # Domain Pydantic & SQLAlchemy models
│   ├── schemas/                 # Strict API request/response schemas
│   └── services/                # Schedule, Cancellation, Rescheduling, Swap, Analytics services
├── core/                        # Pure Python Algorithmic Core (Zero Web/DB Imports)
│   ├── problem.py               # LectureVariable, SlotValue, TimetableProblem
│   ├── validator.py             # Authoritative ConstraintValidator (H1-H9, S1-S5)
│   ├── backtracking.py          # PlainBacktrackingSolver & ImprovedBacktrackingSolver
│   ├── min_conflicts.py         # MinConflictsSolver with Random Walk plateau escape
│   ├── annealing.py             # SimulatedAnnealingSolver (Metropolis-Hastings)
│   └── hybrid.py                # HybridCSPSASolver (Two-Stage Decoupled Optimization)
├── frontend/                    # Streamlit Modern Web Application
│   ├── views/                   # dashboard, timetable_grid, generate, operations, analytics, benchmarks, entities
│   ├── api_client.py            # Resilient HTTP Client to FastAPI
│   └── theme.py                 # Custom Dark Navy & Light Mode CSS design system & card renderers
├── experiments/                 # Empirical Benchmarking Suite
│   ├── run_benchmarks.py        # 10-run seeded benchmark runner
│   ├── cross_check.py           # Independent verification against python-constraint
│   └── results/                 # benchmark_results.json & matplotlib convergence curves
├── data/                        # Benchmark Datasets
│   ├── small_dataset.json       # 3 Classes, 6 Teachers, 4 Rooms (5 days x 6 periods)
│   └── large_dataset.json       # 8 Classes, 16 Teachers, 8 Rooms (5 days x 7 periods)
├── docs/                        # Academic Deliverables
│   └── VIVA_DEFENSE_AND_PROJECT_REPORT.md # Viva defense guide & report outline
├── tests/                       # Pytest Automated Test Suite (85 Tests)
│   ├── test_phase2_foundation.py
│   ├── test_phase3_crud_and_io.py
│   ├── test_phase4_problem_and_validator.py
│   ├── test_phase5_plain_backtracking.py
│   ├── test_phase6_improved_backtracking.py
│   ├── test_phase7_min_conflicts.py
│   ├── test_phase8_streamlit_shell.py
│   ├── test_phase9_manual_editing.py
│   ├── test_phase10_simulated_annealing.py
│   ├── test_phase11_hybrid.py
│   ├── test_phase12_cancellation_and_reschedule.py
│   ├── test_phase13_swaps_and_analytics.py
│   └── test_phase14_experiments.py
├── requirements.txt             # Production Python Dependencies
├── streamlit_app.py             # Streamlit entry point
└── README.md                    # Project Documentation
```

---

## 🎯 Evaluator 5-Minute Demonstration Guide

1. **Dashboard (0:00 – 1:00):** Show the dark navy theme and light mode toggle, live KPI tiles, room utilization, and institutional health.
2. **Generating Schedules (1:00 – 2:00):** Open **Generate Schedule**, run **Improved Backtracking (MRV+FC)** in $<0.15$s with 0 violations. Then switch to **Hybrid CSP + SA** to demonstrate soft constraint optimization.
3. **Timetable Matrix (2:00 – 3:00):** Open **Timetable Grid**. Toggle between **Class**, **Faculty**, and **Room** views. Point out shaded lunch breaks ($H_9$), atomic consecutive lab blocks ($S_3$), and export a PDF, Excel, or CSV timetable.
4. **Operations & Rescheduling (3:00 – 4:00):** Open **Operations & Rescheduling**. Cancel a lecture session due to faculty leave. Move to **Missed Lecture Rescheduling**, search for collision-free slots with an alternative substitute teacher, and book the top recommendation.
5. **Benchmarks & Defense (4:00 – 5:00):** Open **Algorithm Comparison**. Present the empirical runtimes and Min-Conflicts convergence graph. Refer to `docs/VIVA_DEFENSE_AND_PROJECT_REPORT.md` for full viva Q&A answers.

---

## 📚 Academic Citations & AI Disclosure
- **Russell, S., & Norvig, P. (2020).** *Artificial Intelligence: A Modern Approach (4th ed.)*. Pearson. (Chapter 6: Constraint Satisfaction Problems, Chapter 4: Complex Local Search).
- **Minton, S., Philips, M. D., Johnston, M. D., & Laird, P. (1992).** Minimizing conflicts: a heuristic repair method for constraint satisfaction and scheduling problems. *Artificial Intelligence, 58*(1-3), 161-205.
- **Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P. (1983).** Optimization by simulated annealing. *Science, 220*(4598), 671-680.
- **AI Coding Disclosure:** An AI coding assistant (Antigravity by Google DeepMind) was used as a pair programming assistant. All CSP problem formulations, constraint logic, algorithms, and tests were verified and validated by the student engineering team.
