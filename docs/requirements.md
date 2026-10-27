# SchedulAI — Requirement Traceability & Verification Checklist

## Academic Assignment & Extended Product Requirements

| Req ID | Category | Description | Target Module / File | Verification Method | Status |
|---|---|---|---|---|---|
| **CSP-FORM** | CSP Formulation | Exact CSP model: Variables (lecture session instances), Domains (day, period, room, teacher), Constraints (unary, binary, global) | `backend/app/scheduler/csp.py` | Pytest & solver domain generation checks | **Completed (Verified)** |
| **H1** | Hard Constraint | Teacher Conflict: Teacher cannot teach 2 sessions at the same time | `backend/app/scheduler/constraints.py` | Pytest: `test_h1_teacher_conflict` | **Completed (Verified)** |
| **H2** | Hard Constraint | Class Conflict: Class cannot have 2 sessions at the same time | `backend/app/scheduler/constraints.py` | Pytest: `test_h2_class_conflict` | **Completed (Verified)** |
| **H3** | Hard Constraint | Room Conflict: Room cannot host 2 sessions at the same time | `backend/app/scheduler/constraints.py` | Pytest: `test_h3_room_conflict` | **Completed (Verified)** |
| **H4** | Hard Constraint | Room Capacity: Assigned room capacity >= class strength | `backend/app/scheduler/constraints.py` | Pytest: `test_h4_room_capacity` | **Completed (Verified)** |
| **H5** | Hard Constraint | Room Type: Lab sessions in lab rooms; Theory sessions in classrooms | `backend/app/scheduler/constraints.py` | Pytest: `test_h5_room_type` | **Completed (Verified)** |
| **H6** | Hard Constraint | Teacher Availability: Scheduled only in declared available slots | `backend/app/scheduler/constraints.py` | Pytest: `test_h6_teacher_availability` | **Completed (Verified)** |
| **H7** | Hard Constraint | Exact Weekly Hours: Every class-subject gets exact required weekly hours | `backend/app/scheduler/constraints.py` | Authoritative validation check (104/104 vars verified) | **Completed (Verified)** |
| **H8** | Hard Constraint | Teacher Max Workload: Assigned hours <= maximum weekly teaching load | `backend/app/scheduler/constraints.py` | Workload analytics & constraint validator | **Completed (Verified)** |
| **H9** | Hard Constraint | Lunch Break: Configured class lunch slot must have no scheduled sessions | `backend/app/scheduler/constraints.py` | Pytest: `test_h9_lunch_break` | **Completed (Verified)** |
| **S1** | Soft Constraint | Minimize free periods / gaps in class day | `backend/app/scheduler/cost_function.py` | Evaluated across all benchmark runs | **Completed (Verified)** |
| **S2** | Soft Constraint | Spread subject lectures across different days (avoid duplicate per day unless lab) | `backend/app/scheduler/cost_function.py` | Cost function penalty evaluation | **Completed (Verified)** |
| **S3** | Soft Constraint | Multi-period labs in consecutive periods | `backend/app/scheduler/cost_function.py` | Lab duration = 2 atomic consecutive slot domain mapping | **Completed (Verified)** |
| **S4** | Soft Constraint | Respect teacher preferences (e.g. avoid period 1 or specific preference slots) | `backend/app/scheduler/cost_function.py` | Evaluated in soft penalty score | **Completed (Verified)** |
| **S5** | Soft Constraint | Avoid more than 2 consecutive lectures for a teacher | `backend/app/scheduler/cost_function.py` | Consecutive lecture penalty evaluation | **Completed (Verified)** |
| **ALG-BT** | Algorithm 1 | Plain Backtracking CSP (baseline systematic search, node tracking, time limit) | `backend/app/scheduler/backtracking.py` | Benchmark run: 0.0021s on Small, 0.0313s on Large | **Completed (Verified)** |
| **ALG-IBT** | Algorithm 1 | Improved Backtracking CSP (MRV + Forward Checking + Degree Heuristic + LCV) | `backend/app/scheduler/backtracking.py` | Benchmark run: 0.1099s on Small, 3.4456s on Large (0 hard viol) | **Completed (Verified)** |
| **ALG-MC** | Algorithm 2 | Min-Conflicts Local Search (complete initial assignment, conflicted var pick, min-conflict val, tie-breaking, plateau escape via random walk/restart, seed, cost history) | `backend/app/scheduler/min_conflicts.py` | 10 trials, 100% success rate, convergence plot generated | **Completed (Verified)** |
| **ALG-SA** | Bonus (+6) | Simulated Annealing (neighborhood moves: session move/swap, temp schedule, cooling, seed) | `backend/app/scheduler/simulated_annealing.py` | 10 trials evaluated on small and large datasets | **Completed (Verified)** |
| **ALG-HYB** | Bonus (+6) | Hybrid CSP + Simulated Annealing (CSP finds 100% feasible schedule, SA refines soft quality) | `backend/app/scheduler/hybrid.py` | Reduced penalty from 571 to 354 on small, 1482 to 1083 on large | **Completed (Verified)** |
| **DATA-SM** | Benchmark Data | Small Dataset: 3 classes, 6 teachers, 4 rooms, 5 days x 6 periods (solvable verified) | `datasets/small_dataset.json` | 100% solved in benchmarks and tests | **Completed (Verified)** |
| **DATA-LG** | Benchmark Data | Large Dataset: 8+ classes, 15+ teachers, 8+ rooms, 5 days x 7 periods (solvable verified) | `datasets/large_dataset.json` | 100% solved with 104 variables | **Completed (Verified)** |
| **EXP-BENCH** | Experiments | Benchmark suite: 10 trials per randomized algorithm, recording runtime, nodes/iters, violations, soft score, success rate, cost history graph | `experiments/run_benchmarks.py` | Ran in `.venv`, produced JSON + PNG charts | **Completed (Verified)** |
| **API-CORE** | Backend API | FastAPI REST endpoints for teachers, classes, subjects, rooms, timetable generation, manual edit validation | `backend/app/api/routes/` | Verified via curl, TestClient & live server | **Completed (Verified)** |
| **PROD-MAN** | Feature | Manual timetable editing with instant hard-constraint conflict detection & explanation | `backend/app/services/schedule_service.py`, `EditSessionModal.jsx` | Tested in UI & backend service | **Completed (Verified)** |
| **PROD-DYN** | Feature | Dynamic extra teachers, classes, subjects, rooms without code edits | UI Forms & DB persistence | Verified in ManageEntitiesPage and API | **Completed (Verified)** |
| **PROD-CANCEL**| Feature | Class cancellation / temporary blocking with affected session tracking & in-app notifications | `backend/app/services/cancellation_service.py` | Tested session & day cancellation | **Completed (Verified)** |
| **PROD-RESCH** | Feature | Missed lecture rescheduling engine proposing valid alternative slots | `backend/app/services/rescheduling_service.py` | Tested feasible clash-free slot suggestions | **Completed (Verified)** |
| **PROD-SWAP** | Feature | Teacher class-swap request & multi-constraint validation workflow | `backend/app/services/swap_service.py` | Tested swap conflict validation & execution | **Completed (Verified)** |
| **PROD-WORK** | Feature | Teacher workload analytics (max, assigned, remaining, utilization %, subject breakdown) | `backend/app/services/analytics_service.py` | Chart.js visual chart & table live | **Completed (Verified)** |
| **PROD-IO** | Feature | CSV & Excel timetable export, JSON/CSV dataset import | `backend/app/services/io_service.py` | Tested `/api/io/export-csv` | **Completed (Verified)** |
| **UI-DASH** | Frontend UI | React + Vite dashboard: Day x Period grid, Class/Teacher/Room views, Generation modal, Analytics, Rescheduling, Swaps | `frontend/src/` | Production build verified (`npm run build`) & running | **Completed (Verified)** |
| **DOC-REP** | Deliverable | Academic Report (Markdown/PDF format) covering CSP formulation, algorithms, cost function, experiments, comparison table, viva prep | `docs/report.md` | Comprehensive 8-section report written | **Completed (Verified)** |
