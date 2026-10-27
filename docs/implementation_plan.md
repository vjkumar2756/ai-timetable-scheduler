# SchedulAI — Implementation Plan & Architecture Roadmap

## 1. System Overview
SchedulAI is an academic AI-based college timetable scheduling system built with a Python (FastAPI) backend and a React (Vite) frontend. It formulates automated timetable generation as a Constraint Satisfaction Problem (CSP) and implements both exact and local search algorithms, complete with benchmark experiments, manual conflict-aware editing, workload analytics, and rescheduling workflows.

## 2. Directory Structure
```
AI_asinment/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── teachers.py
│   │   │   │   ├── classes.py
│   │   │   │   ├── subjects.py
│   │   │   │   ├── rooms.py
│   │   │   │   ├── schedule.py
│   │   │   │   ├── rescheduling.py
│   │   │   │   ├── swaps.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── io_routes.py
│   │   │   └── router.py
│   │   ├── models/
│   │   │   └── entities.py
│   │   ├── schemas/
│   │   │   └── api_schemas.py
│   │   ├── database/
│   │   │   ├── db.py
│   │   │   └── store.py
│   │   ├── scheduler/
│   │   │   ├── csp.py                 # Variable, domain, and session definitions
│   │   │   ├── constraints.py         # Authoritative Hard Constraint Validator (H1-H9)
│   │   │   ├── cost_function.py       # Soft Constraints (S1-S5) & Penalty Cost
│   │   │   ├── backtracking.py        # Plain BT & Improved BT (MRV, FC, Degree, LCV)
│   │   │   ├── min_conflicts.py       # Min-Conflicts Local Search + Plateau Escape
│   │   │   ├── simulated_annealing.py # Simulated Annealing Soft Optimizer
│   │   │   ├── hybrid.py              # Hybrid CSP + Simulated Annealing Solver
│   │   │   └── metrics.py             # Performance metric counters
│   │   ├── services/
│   │   │   ├── schedule_service.py
│   │   │   ├── cancellation_service.py
│   │   │   ├── rescheduling_service.py
│   │   │   ├── swap_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── io_service.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_constraints.py
│   │   ├── test_solvers.py
│   │   └── test_api.py
│   └── requirements.txt
├── datasets/
│   ├── small_dataset.json
│   └── large_dataset.json
├── experiments/
│   ├── run_benchmarks.py
│   └── results/
│       ├── benchmark_results.json
│       └── min_conflicts_convergence.png
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── TimetableGrid.jsx
│   │   │   ├── EditSessionModal.jsx
│   │   │   ├── RescheduleModal.jsx
│   │   │   ├── SwapRequestModal.jsx
│   │   │   └── WorkloadChart.jsx
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── TimetableViewPage.jsx
│   │   │   ├── ManageEntitiesPage.jsx
│   │   │   ├── GeneratePage.jsx
│   │   │   ├── OperationsPage.jsx
│   │   │   ├── WorkloadPage.jsx
│   │   │   └── BenchmarkPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── requirements.md
│   ├── implementation_plan.md
│   └── report.md
└── README.md
```

## 3. CSP Formulation Details
- **Variables**: Each required lecture session `(class_id, subject_id, session_index)` generated from `class.subjects[subject_id].weekly_hours`. For a 2-hour lab, represented as consecutive 2-period atomic blocks or single multi-period slot variables with duration.
- **Domains**: Cartesian product of valid `(day, period, room, teacher)`. Domain pre-filtering excludes:
  - Rooms with capacity < class strength
  - Theory sessions in labs / Lab sessions in non-labs
  - Teachers not qualified for the subject
  - Lunch break period for the class
- **Authoritative Validator**: Checks all 9 hard constraints (H1 to H9) and produces human-readable diagnostic messages on violation.
- **Cost Function**: `Cost = 1000 * (hard_violations) + (soft_penalties)` where soft penalties evaluate gaps (S1), day dispersion (S2), lab continuity (S3), teacher preferences (S4), and max consecutive teacher lectures (S5).

## 4. Phased Execution Roadmap
- **Phase 1**: Inspection & Plan (Completed)
- **Phase 2 & 3**: Project Structure, Data Models, Database Store, Schemas
- **Phase 4**: Verified Sample Datasets (Small & Large)
- **Phase 5 & 6**: CSP Formulation & Authoritative Constraint Validator (H1-H9) + Soft Cost (S1-S5)
- **Phase 7**: Mandatory AI Solvers:
  - Plain Backtracking CSP
  - Improved Backtracking (MRV + Forward Checking + Degree + LCV)
  - Min-Conflicts Local Search + Plateau Escape
- **Phase 8 & 9**: Bonus Algorithms:
  - Simulated Annealing
  - Hybrid CSP + Simulated Annealing
- **Phase 10 & 20**: FastAPI Backend Services & Endpoints
- **Phase 11-17**: Extended Operations:
  - Conflict-aware Manual Editing
  - Class Cancellation & In-app Notifications
  - Missed Lecture Rescheduling Engine
  - Teacher Swap Validation Engine
  - Teacher Workload Analytics
  - CSV / Excel Export & Import
- **Phase 18**: Benchmark Suite & Experimental Execution (10 trials, stats, plots)
- **Phase 21**: Pytest Test Suite verifying all constraints and edge cases
- **Phase 22**: React Frontend Dashboard with day-by-period visual grid, filters, charts, and interactive workflows
- **Phase 23-25**: Academic Report, README, and Final Acceptance Checklist Verification
