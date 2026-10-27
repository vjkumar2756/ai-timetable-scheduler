# SchedulAI — AI-Based College Timetable Scheduler

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.3-purple.svg)](https://vitejs.dev)
[![Status](https://img.shields.io/badge/Constraints-H1--H9%20Strict%20Zero-emerald.svg)]()

> **Academic AI Assignment (B.Tech, Second Year):** Automated Constraint Satisfaction Problem (CSP) Timetable Generation and Local Search Engine with +12 Bonus Marks for Simulated Annealing & Hybrid Optimization.

---

## 🌟 Key Highlights & Features

### 1. Mandatory AI Search Algorithms (Python)
- **Plain Backtracking (Baseline):** Chronological depth-first CSP search tracking node expansions and runtimes.
- **Improved Backtracking (MRV + Forward Checking + Degree + LCV):**
  - **MRV (Minimum Remaining Values):** Dynamic variable selection (fail-first principle).
  - **Forward Checking:** Domain filtering upon assignment to prune dead-ends before recursive branching.
  - **Degree Heuristic:** Tie-breaker prioritizing variables with the most constraints on unassigned variables.
  - **LCV (Least Constraining Value):** Value ordering minimizing eliminated choices for future variables.
- **Min-Conflicts Local Search:**
  - Complete greedy initial assignment.
  - Conflicted variable selection with min-conflict value choices and uniform tie-breaking.
  - Plateau escape via Random Walk ($p = 0.08$) and Random Restarts.
  - Iteration tracking and Cost History generation.

### 2. Bonus Algorithms (+12 Marks)
- **Simulated Annealing (+6):** Probabilistic local search with geometric temperature cooling ($T_{k+1} = \alpha T_k$) and single-move / pairwise session swap neighborhood operators.
- **Hybrid CSP + Simulated Annealing (+6):** Two-stage pipeline where Improved Backtracking CSP first guarantees 100% hard feasibility ($N_{\text{hard}} = 0$), followed by Simulated Annealing soft-constraint refinement (reducing penalties by up to $38\%$).

### 3. Strict Constraint Enforcement
- **All 9 Hard Constraints (H1–H9):**
  - `H1` Teacher Conflict (no faculty double-booking)
  - `H2` Class Conflict (no student batch double-booking)
  - `H3` Room Conflict (no room overlap)
  - `H4` Room Capacity ($\text{Room Capacity} \ge \text{Class Strength}$)
  - `H5` Room Type (Labs in labs; Lectures in classrooms)
  - `H6` Teacher Availability (respects declared unavailable day/period slots)
  - `H7` Exact Weekly Subject Hours (exact curriculum hours preserved)
  - `H8` Maximum Teacher Workload ($\text{Assigned Hours} \le \text{Max Weekly Load}$)
  - `H9` Lunch Break (class-configured lunch slot kept completely free)
- **All 5 Soft Constraints (S1–S5):**
  - `S1` Minimizing class day gaps
  - `S2` Subject dispersion across days
  - `S3` Multi-period consecutive lab continuity
  - `S4` Faculty preference satisfaction
  - `S5` Faculty fatigue avoidance (preventing $>2$ consecutive lecture hours)

### 4. Enterprise Academic Dashboard (React + Chart.js)
- **Visual Timetable Matrix:** Day-by-period grid with filters by Class, Teacher, Room, and Day.
- **Real-Time Conflict-Aware Slot Editor:** Immediate backend verification flagging any constraint conflicts before saving.
- **Missed Lecture Rescheduling Engine:** Auto-scans and ranks clash-free replacement slots.
- **Faculty Class-Swap Workflow:** Validates proposed lecture exchanges between faculty members.
- **Workload Analytics:** Faculty capacity utilization percentages, overload alerts, and Chart.js bar graphs.
- **CSV Timetable Export:** Instant export of scheduled institutional sessions.

---

## 📁 Repository Structure

```
AI_asinment/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST route handlers (schedule, operations, analytics, entities, io)
│   │   ├── database/store.py    # In-memory + JSON DataStore
│   │   ├── models/entities.py   # Domain entities (Teacher, Class, Subject, Room, Session)
│   │   ├── scheduler/           # Pure Python AI scheduling engine
│   │   │   ├── csp.py           # CSP Formulation & Domain Pruner
│   │   │   ├── constraints.py   # Authoritative H1-H9 Constraint Validator
│   │   │   ├── cost_function.py # Soft Constraints S1-S5 & Total Cost Function
│   │   │   ├── backtracking.py  # Plain BT & Improved BT (MRV+FC+Degree+LCV)
│   │   │   ├── min_conflicts.py # Min-Conflicts Local Search + Plateau Escape
│   │   │   ├── simulated_annealing.py # Standalone Simulated Annealing
│   │   │   ├── hybrid.py        # Hybrid CSP + Simulated Annealing Solver
│   │   │   └── metrics.py       # Performance metric counters
│   │   ├── services/            # Business logic (schedule, cancel, reschedule, swap, analytics)
│   │   └── main.py              # FastAPI entry point with CORS and startup loader
│   ├── tests/                   # Pytest test suite for H1-H9 & solvers
│   └── requirements.txt
├── datasets/
│   ├── small_dataset.json       # 3 classes, 6 teachers, 4 rooms, 5 days x 6 periods
│   └── large_dataset.json       # 8 classes, 16 teachers, 8 rooms, 5 days x 7 periods
├── experiments/
│   ├── run_benchmarks.py        # 10-trial automated benchmark suite
│   └── results/
│       ├── benchmark_results.json
│       ├── min_conflicts_convergence.png
│       └── algorithm_comparison.png
├── frontend/
│   ├── src/                     # React components, pages, design system
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── requirements.md          # Traceability & verification checklist
│   ├── implementation_plan.md   # Architectural blueprint
│   └── report.md                # 8-section Academic Project Report
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend API will be accessible at `http://localhost:8000` with Swagger OpenAPI docs at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend

# Install node dependencies
npm install

# Run the Vite development server
npm run dev
```
Frontend will be accessible at `http://localhost:5173`.

---

## 🧪 Running Automated Tests

Run the Pytest suite verifying all 9 hard constraints, integrity checks, and solvers:
```bash
PYTHONPATH=. pytest backend/tests/test_constraints_and_solvers.py -v
```

---

## 📊 Running the Experimental Benchmark Suite

To reproduce the 10-trial benchmark comparison across both datasets and generate the convergence and comparison plots:
```bash
.venv/bin/python experiments/run_benchmarks.py
```
Outputs generated in `experiments/results/`:
- `benchmark_results.json`
- `min_conflicts_convergence.png`
- `algorithm_comparison.png`

---

## 📈 Benchmark Results Summary

| Dataset | Algorithm | Time (s) | Nodes / Iters | Hard Violations | Soft Penalty | Success Rate (10 Trials) |
|---|---|---|---|---|---|---|
| **Small Dataset** | Plain Backtracking (Baseline) | 0.0021s | 39 nodes | 0 | 676 | 100% |
| | Improved Backtracking (MRV+FC) | 0.1099s | 39 nodes | 0 | 571 | 100% |
| | Min-Conflicts Local Search | 0.0058s | 1.2 iters | 0 | 502 | 100% |
| | Simulated Annealing (Standalone) | 0.0948s | 2,020 iters | 0 | 520 | 100% |
| | **Hybrid CSP + SA (Bonus)** | **0.1863s** | **2,020 iters** | **0** | **354.0** | **100%** |
| **Large Dataset** | Plain Backtracking (Baseline) | 0.0313s | 104 nodes | 0 | 2,310 | 100% |
| | **Improved Backtracking (MRV+FC)** | **3.4456s** | **104 nodes** | **0** | **1,482** | **100%** |
| | Min-Conflicts Local Search | 0.0783s | 1.0 iters | 0 | 1,840 | 100% |
| | Simulated Annealing (Standalone) | 0.2989s | 2,020 iters | 1.8 | 1,720 | 10% |
| | **Hybrid CSP + SA (Bonus)** | **3.8833s** | **2,020 iters** | **0** | **1,083.7** | **100%** |

---

## 🎓 Viva Demonstration Walkthrough

1. **Dashboard Overview:** Navigate to `http://localhost:5173` to view live infrastructure stats, active faculty count, and health counters.
2. **Preset Switching:** Click `Small (3C)` or `Large (8C)` in the sidebar to switch datasets in memory.
3. **Automated Generation:**
   - Go to **Generate Schedule**.
   - Select **Improved Backtracking** or **Hybrid CSP + SA**.
   - Click **Generate Timetable Now** to witness sub-second/multi-second solving with 0 hard violations.
4. **Timetable Matrix Exploration:**
   - Switch between **By Class**, **By Faculty**, and **By Room** views.
   - Note the designated lunch break column and 2-hour laboratory consecutive blocks.
5. **Conflict-Aware Manual Editing:**
   - Click any session box to open the editor.
   - Attempt to move the session to an occupied slot; observe immediate hard conflict diagnostics.
   - Select a free slot and save; observe immediate timetable grid updates.
6. **Operations & Rescheduling:**
   - Go to **Operations & Rescheduling**.
   - Cancel a session with a reason and view the audit notification.
   - Click **Find Feasible Replacement Slots** to see conflict-free alternatives ranked by soft penalty.
   - Test a **Teacher Class Swap** and review validation feedback.
7. **Faculty Workload:** Open **Workload Analytics** to inspect capacity utilization progress bars and Chart.js distribution graphs.
8. **Algorithm Benchmarks:** Open **Algorithm Comparison** to inspect the 10-trial comparison table, runtime bar charts, and the Min-Conflicts cost-vs-iterations convergence curve.
9. **Export Timetable:** Click **Export CSV** in the Timetable Grid to download the schedule spreadsheet.
