<p align="center">
  <a href="#schedulai">
    <img src="assets/logo.png" alt="SchedulAI Logo" width="140" style="border-radius: 50%; background: #ffffff; padding: 4px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);" />
  </a>
</p>

<h1 align="center">SchedulAI</h1>

<p align="center">
  <strong>Autonomous Academic Timetable Optimization Engine & Decision Support System</strong><br>
  <em>Constraint Satisfaction Problem (CSP) Formulation &bull; Systematic Backtracking &bull; Heuristic Local Search &bull; Simulated Annealing</em>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg?style=flat-square&logo=python" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg?style=flat-square&logo=fastapi" alt="FastAPI"></a>
  <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B.svg?style=flat-square&logo=streamlit" alt="Streamlit"></a>
  <a href="#-verification--testing"><img src="https://img.shields.io/badge/Tests-85%20Passing-10B981.svg?style=flat-square&logo=pytest" alt="Pytest"></a>
  <a href="#-constraint-traceability-matrix"><img src="https://img.shields.io/badge/Hard%20Constraints-H1--H9%20Strict%20Zero-059669.svg?style=flat-square" alt="Constraints"></a>
  <a href="#-empirical-benchmarks"><img src="https://img.shields.io/badge/Optimization-Hybrid%20CSP%2BSA-7C3AED.svg?style=flat-square" alt="Hybrid CSP+SA"></a>
  <a href="#-license"><img src="https://img.shields.io/badge/License-MIT-gray.svg?style=flat-square" alt="License"></a>
</p>

---

## 📑 Table of Contents

- [Executive Overview](#-executive-overview)
- [Key Capabilities](#-key-capabilities)
- [System Architecture](#-system-architecture)
- [Constraint Traceability Matrix](#-constraint-traceability-matrix)
- [Empirical Benchmarks](#-empirical-benchmarks)
- [Interactive Features & Workflows](#-interactive-features--workflows)
- [Quick Start Guide](#-quick-start-guide)
- [API Reference](#-api-reference)
- [Repository Structure](#-repository-structure)
- [Verification & Testing](#-verification--testing)
- [Academic Foundations & Citations](#-academic-foundations--citations)
- [License](#-license)

---

## 💡 Executive Overview

Creating conflict-free university timetables is a notoriously difficult, $\mathcal{NP}$-complete combinatorial scheduling problem. Traditional manual scheduling takes academic coordinators weeks of trial-and-error across spreadsheets, frequently resulting in:
- **Teacher & Room Clashes:** Simultaneous double-booking of instructors or lecture halls.
- **Capacity & Facility Mismatches:** Placing high-enrollment classes in undersized rooms or scheduling computer-aided laboratory sessions in theory classrooms.
- **Poor Academic Quality:** Extended idle periods (2–3 hour gaps) for students, unbalanced distribution of subjects across weekdays, and consecutive multi-hour fatigue for teachers.
- **Mid-Semester Fragility:** Unplanned faculty absences or cancelled classes cause a cascade of scheduling conflicts when attempting manual make-ups.

**SchedulAI** models university timetabling as a formal **Constraint Satisfaction Problem (CSP)** and couples exact systematic search heuristics with stochastic local search metaheuristics. It guarantees **zero hard constraint violations ($H=0$)** in sub-second to low-second runtimes, while optimizing pedagogical soft criteria and providing an operational web dashboard for administrators.

---

## ⚡ Key Capabilities

| Capability | Technical Realization | Institutional Value |
| :--- | :--- | :--- |
| **Instant Conflict-Free Scheduling** | Backtracking with Minimum Remaining Values (MRV), Degree Heuristic, Forward Checking (FC), and Least Constraining Value (LCV). | Replaces weeks of manual scheduling with a verified master schedule generated in $<4$ seconds. |
| **Two-Stage Hybrid Optimization** | Stage 1 solves hard constraints ($H_1$–$H_9$) via CSP search; Stage 2 minimizes soft penalties ($S_1$–$S_5$) via Simulated Annealing with Metropolis-Hastings acceptance. | Achieves the lowest soft penalty score (highest quality schedule) without ever violating hard institutional rules. |
| **3-Way Master Grid Matrix** | Dynamic multi-view timetable rendering: **By Class Cohort**, **By Faculty Member**, or **By Physical Room**. | Instant clarity for department heads, individual instructors, and facility managers alike. |
| **Operational Rescheduling Suite** | Real-time lecture cancellation, automated conflict-free make-up slot recommendation with substitute teacher matching, and bilateral faculty swap validation. | Resolves unplanned faculty leaves and room maintenance without disrupting the rest of the institution. |
| **Fixed-View Workload Analytics** | Plotly analytics for faculty teaching quotas and facility utilization, configured with fixed non-zooming viewports for consistent readability. | Provides dean-level oversight into faculty teaching distributions and underutilized infrastructure. |
| **Enterprise Multi-Format Export** | 1-click generation of formatted, printable **PDF** reports, structured **Excel (.xlsx)** workbooks, and raw **CSV** matrices. | Ready for notice boards, faculty intranet distribution, and external academic record systems. |

---

## 🏛️ System Architecture

SchedulAI is engineered with strict separation of concerns across three decoupled tiers:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Streamlit Frontend (Port 8501)                        │
│   • Dark Navy / Light Theme Design System       • On-Demand Grid Inspection     │
│   • Multi-View Interactive Timetable Matrix    • Operations & Rescheduling UI   │
│   • Workload & Facility Analytics Dashboard     • Algorithm Comparison Suite    │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ HTTP REST (JSON)
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                            FastAPI Backend (Port 8000)                          │
│   • OpenAPI / Swagger Documentation             • Session & Schedule State Store│
│   • Operational Cancellation & Swap Services   • PDF / Excel / CSV Exporters   │
│   • Real-Time Conflict & Pre-Pruning Validator  • Analytics Aggregation Engine  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Python In-Memory API
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                        Pure Python Algorithmic Core                             │
│       (Zero web/database framework dependencies — 100% testable & portable)     │
│                                                                                 │
│   ┌───────────────────────────┐             ┌───────────────────────────────┐   │
│   │   TimetableProblem (CSP)  │             │    ConstraintValidator        │   │
│   │  • Variables: X = {L_i}   │◄───────────►│  • Hard Constraints H1–H9     │   │
│   │  • Domains: D(X) = {(s,r)}│             │  • Soft Penalties S1–S5       │   │
│   └─────────────┬─────────────┘             └───────────────┬───────────────┘   │
│                 │                                           │                   │
│   ┌─────────────▼───────────────────────────────────────────▼───────────────┐   │
│   │                         Scheduling Solvers                              │   │
│   │  1. Plain Backtracking               (Systematic Depth-First Baseline)  │   │
│   │  2. Improved Backtracking            (MRV + Degree + FC + LCV)          │   │
│   │  3. Min-Conflicts Local Search       (Random Walk & Plateau Breaker)    │   │
│   │  4. Simulated Annealing              (Geometric Cooling Metaheuristic)  │   │
│   │  5. Hybrid Two-Stage CSP + SA        (Exact Feasibility + Soft Tuning)  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Constraint Traceability Matrix

### 1. Hard Constraints ($H_1$–$H_9$) — Strict Zero Violations ($H = 0$)
Every candidate schedule must strictly satisfy all institutional hard constraints:

| ID | Constraint Name | Formulation & Rule | Operational Verification Mechanism |
| :---: | :--- | :--- | :--- |
| **$H_1$** | **Teacher Clash** | $\forall t \in T, s \in S: \sum_{L} \mathbb{I}(\text{teacher}(L)=t \land \text{slot}(L)=s) \le 1$ | Slot-to-teacher collision hash map |
| **$H_2$** | **Class Clash** | $\forall c \in C, s \in S: \sum_{L} \mathbb{I}(\text{class}(L)=c \land \text{slot}(L)=s) \le 1$ | Cohort timeslot index lookup |
| **$H_3$** | **Room Clash** | $\forall r \in R, s \in S: \sum_{L} \mathbb{I}(\text{room}(L)=r \land \text{slot}(L)=s) \le 1$ | Facility occupancy tracking matrix |
| **$H_4$** | **Room Capacity** | $\forall L: \text{Capacity}(\text{room}(L)) \ge \text{Enrollment}(\text{class}(L))$ | Unary domain pre-pruning during init |
| **$H_5$** | **Room Type Match** | Theory $\rightarrow$ Classroom; Practical Lab $\rightarrow$ Lab Facility | Unary domain filtering by room classification |
| **$H_6$** | **Teacher Availability** | $\forall L: \text{slot}(L) \notin \text{UnavailableSlots}(\text{teacher}(L))$ | Domain pruning against instructor blackout windows |
| **$H_7$** | **Curriculum Quota** | Weekly scheduled hours $\equiv$ Prescribed subject curriculum quota | Complete variable domain instantiation |
| **$H_8$** | **Teacher Max Load** | Total weekly teaching load $\le$ Contractual maximum workload | Active load accumulator check |
| **$H_9$** | **Lunch Break Protection** | Designated lunch period (Period 4) kept clear for all student cohorts | Systematic period exclusion during domain generation |

### 2. Soft Constraints ($S_1$–$S_5$) — Pedagogical Quality Tuning
The overall quality penalty score is evaluated as a weighted linear combination:

$$\text{Soft Penalty } (S) = 5 \cdot S_1 + 15 \cdot S_2 + 20 \cdot S_3 + 10 \cdot S_4 + 12 \cdot S_5$$

- **$S_1$ — Student Free Period Gaps ($w=5$):** Minimizes idle gaps between classes within the same academic day.
- **$S_2$ — Daily Subject Repeat ($w=15$):** Encourages subjects to be distributed evenly across different weekdays rather than stacked on a single day.
- **$S_3$ — Lab Session Continuity ($w=20$):** Multi-period lab sessions must run consecutively without interruptions (guaranteed via atomic two-period block modeling).
- **$S_4$ — Teacher Slot Preferences ($w=10$):** Maximizes assignment to faculty-preferred teaching hours (e.g. morning vs. afternoon preference).
- **$S_5$ — Consecutive Lecture Pacing ($w=12$):** Penalizes assigning $>2$ back-to-back lecture periods to any instructor without a recovery window.

$$\text{Objective Cost Function} = 1000 \times H + S$$

---

## 🏆 Empirical Benchmarks

Extracted from real seeded benchmark evaluations ([`experiments/results/benchmark_results.json`](experiments/results/benchmark_results.json)):

| Algorithm | Category | Small Dataset (3C, 6T, 4R)<br>Runtime (s) | Large Dataset (8C, 16T, 8R)<br>Runtime (s) | Hard Clashes ($H$) | Soft Penalty ($S$) (Large Dataset) | Feasibility Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Plain Backtracking** | Baseline Search | 0.0021s | 0.0313s | **0** | 2,310 pts | 100% |
| **Improved Backtracking** | MRV + FC + Degree + LCV | 0.1099s | 3.4456s | **0** | 1,482 pts | 100% |
| **Min-Conflicts** | Heuristic Local Search | 0.0058s | 0.0783s | **0** | 1,438 pts | 100% |
| **Simulated Annealing** | Metaheuristic | 0.0948s | 0.2989s | $\le 1$ | 1,096 pts | 10% |
| **Hybrid CSP + SA** | Two-Stage Decoupled Engine | 0.1863s | 3.8833s | **0** | **1,083 pts** | **100%** |

> **Key Takeaway:** While Plain Backtracking finds *a* solution quickly, it yields poor pedagogical quality ($S = 2,310$). The **Two-Stage Hybrid CSP+SA** achieves the absolute best schedule quality ($S = 1,083$ — a **53.1% reduction in soft penalties**) while mathematically guaranteeing zero hard clashes.

---

## 🖥️ Interactive Features & Workflows

### 1. Operations & Decision Support
- **Single-Click Lecture Cancellation:** Mark any class as cancelled due to instructor leave, instantly freeing up the occupied room and updating the master schedule.
- **Automated Rescheduling with Substitute Matching:** Enter subject, cohort, and target teacher; the engine evaluates all available slots, verifies zero conflicts for both students and faculty, calculates available substitutes, and presents ranked recommendations.
- **Faculty Lecture Swaps:** Propose a bilateral swap between two faculty slots; the system dry-runs validation across all 9 hard constraints before committing.
- **On-Demand Timetable Inspection:** Workflows in both *Operations* and *Generate Schedule* feature expandable on-demand timetable viewers so administrators can verify schedule changes immediately without page navigation.

### 2. Multi-Dimensional Master Timetable Grid
- **Student Cohort View:** Complete weekly view for each class section with distinct subject tags and classroom badges.
- **Faculty Member View:** Personalized weekly timetable for individual professors, detailing assigned lecture rooms and student cohorts.
- **Room Facility View:** Spatial view displaying room occupancy across all periods to audit facility utilization.
- **One-Click Export:** Download clean, high-resolution PDF schedules, multi-tab Excel sheets, or standard CSV files.

### 3. Institutional Health & Workload Analytics
- **Faculty Teaching Distribution:** Clear horizontal bar chart displaying weekly assigned hours against maximum contractual caps.
- **Room Capacity Utilization:** Facility usage breakdown highlighting under-utilized and heavily-scheduled halls.
- **Fixed-Range Viewports:** All Plotly analytical charts are fixed to prevent unintentional click-and-drag zooming.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python:** 3.10, 3.11, 3.12, or 3.14
- **Operating System:** Linux, macOS, or Windows

### Step 1: Clone & Install Dependencies
```bash
git clone https://github.com/your-username/ai-timetable-scheduler.git
cd ai-timetable-scheduler

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2: Launch the FastAPI Backend
Start the REST API server:
```bash
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation will be live at:
- **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

### Step 3: Launch the Streamlit Web Application
In a separate terminal, launch the Streamlit dashboard:
```bash
streamlit run streamlit_app.py --server.port 8501
```
Open [`http://localhost:8501`](http://localhost:8501) in your browser.

---

## 📡 API Reference

The backend exposes a fully documented, asynchronous REST API:

| Method | Endpoint | Description |
| :---: | :--- | :--- |
| `GET` | `/api/entities/all` | Returns all classes, teachers, rooms, and subjects. |
| `POST` | `/api/schedule/generate` | Generates a new schedule using the specified algorithm (`improved_backtracking`, `min_conflicts`, `hybrid_csp_sa`). |
| `GET` | `/api/schedule/current` | Retrieves the active master timetable with metrics. |
| `POST` | `/api/operations/cancel` | Cancels a specific lecture session. |
| `POST` | `/api/operations/reschedule` | Finds and reserves conflict-free slots for missed classes. |
| `POST` | `/api/operations/swap` | Performs atomic validation and swap between two scheduled sessions. |
| `GET` | `/api/analytics/summary` | Returns institutional KPIs, faculty workloads, and room utilization stats. |
| `GET` | `/api/io/export/{format}` | Exports the active timetable (`pdf`, `xlsx`, `csv`). |

---

## 📂 Repository Structure

```
ai-timetable-scheduler/
├── assets/                      # Application assets (SchedulAI logo, diagrams)
├── backend/app/                 # Enterprise FastAPI REST Application
│   ├── api/routes/              # REST controllers (entities, schedule, operations, analytics, io)
│   ├── database/                # SQLite connection & in-memory DataStore state
│   ├── models/                  # Domain entity Pydantic & SQLAlchemy models
│   ├── schemas/                 # Strict request and response schemas
│   └── services/                # Schedule generation, rescheduling, swap, and export services
├── core/                        # Pure Python Algorithmic Core (Zero Web Dependencies)
│   ├── problem.py               # LectureVariable, SlotValue, and TimetableProblem CSP formulation
│   ├── validator.py             # Authoritative ConstraintValidator (H1–H9 and S1–S5)
│   ├── backtracking.py          # PlainBacktrackingSolver & ImprovedBacktrackingSolver (MRV+FC+LCV)
│   ├── min_conflicts.py         # MinConflictsSolver with random walk heuristic
│   ├── annealing.py             # SimulatedAnnealingSolver (Metropolis-Hastings metaheuristic)
│   └── hybrid.py                # HybridCSPSASolver (Two-stage decoupled search engine)
├── frontend/                    # Streamlit Modern Web Application
│   ├── views/                   # Views: dashboard, timetable_grid, generate, operations, analytics, benchmarks, entities
│   ├── api_client.py            # Typed HTTP client communicating with backend
│   └── theme.py                 # Custom Dark Navy & Light Theme CSS design system
├── experiments/                 # Empirical Benchmarking Suite
│   ├── run_benchmarks.py        # Automated multi-run statistical evaluation script
│   ├── cross_check.py           # Independent verification against python-constraint solver
│   └── results/                 # Seeded benchmark JSON results & convergence plots
├── data/                        # Verified Benchmark Datasets
│   ├── small_dataset.json       # 3 Classes, 6 Teachers, 4 Rooms (5 days × 6 periods)
│   └── large_dataset.json       # 8 Classes, 16 Teachers, 8 Rooms (5 days × 7 periods)
├── tests/                       # Complete Pytest Automated Test Suite (85 Tests)
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
├── requirements.txt             # Production Python dependencies
├── streamlit_app.py             # Streamlit web entry point
└── README.md                    # Project Documentation
```

---

## 🧪 Verification & Testing

The project maintains **100% test pass rate** across its test suite:

```bash
pytest -v
```

```
============================== test session starts ==============================
platform linux -- Python 3.14.x, pytest-8.x.x
rootdir: /home/vijay/Desktop/ai system/ai-timetable-scheduler
collected 85 items

tests/test_phase2_foundation.py ................                         [ 18%]
tests/test_phase3_crud_and_io.py ...........                             [ 31%]
tests/test_phase4_problem_and_validator.py .........                     [ 42%]
tests/test_phase5_plain_backtracking.py .....                            [ 48%]
tests/test_phase6_improved_backtracking.py ......                        [ 55%]
tests/test_phase7_min_conflicts.py ......                                [ 62%]
tests/test_phase8_streamlit_shell.py ....                                [ 67%]
tests/test_phase9_manual_editing.py ...                                  [ 70%]
tests/test_phase10_simulated_annealing.py ......                         [ 77%]
tests/test_phase11_hybrid.py ......                                      [ 84%]
tests/test_phase12_cancellation_and_reschedule.py ....                   [ 89%]
tests/test_phase13_swaps_and_analytics.py ....                           [ 94%]
tests/test_phase14_experiments.py .....                                 [100%]

============================== 85 passed in 7.91s ==============================
```

---

## 📚 Academic Foundations & Citations

The algorithmic design of SchedulAI is grounded in foundational Artificial Intelligence literature:

1. **Russell, S., & Norvig, P. (2020).** *Artificial Intelligence: A Modern Approach (4th ed.)*. Pearson.
   - *Chapter 6: Constraint Satisfaction Problems* (MRV heuristic, Degree heuristic, Forward Checking, LCV).
   - *Chapter 4: Complex Local Search* (Local search heuristics, Hill Climbing, Simulated Annealing).
2. **Minton, S., Philips, M. D., Johnston, M. D., & Laird, P. (1992).** Minimizing conflicts: a heuristic repair method for constraint satisfaction and scheduling problems. *Artificial Intelligence, 58*(1-3), 161–205.
3. **Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P. (1983).** Optimization by simulated annealing. *Science, 220*(4598), 671–680.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
