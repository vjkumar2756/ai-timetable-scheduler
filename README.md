<p align="center">
  <a href="#schedulai">
    <img src="assets/logo.png" alt="SchedulAI Logo" width="130" style="border-radius: 50%; background: #ffffff; padding: 6px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);" />
  </a>
</p>

<h1 align="center">SchedulAI</h1>

<p align="center">
  <strong>Autonomous Academic Timetable Optimization Engine & Decision Support System</strong><br>
  <em>Constraint Satisfaction Problem (CSP) Formulation &bull; Systematic Backtracking &bull; Heuristic Local Search &bull; Simulated Annealing</em>
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?style=flat-square&logo=python" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?style=flat-square&logo=fastapi" alt="FastAPI"></a>
  <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg?style=flat-square&logo=streamlit" alt="Streamlit"></a>
  <a href="#-constraint-traceability-matrix"><img src="https://img.shields.io/badge/Hard%20Constraints-H1--H9%20Strict%20Zero-059669.svg?style=flat-square" alt="Constraints"></a>
  <a href="#-empirical-benchmarks"><img src="https://img.shields.io/badge/Optimization-Hybrid%20CSP%2BSA-7C3AED.svg?style=flat-square" alt="Hybrid CSP+SA"></a>
  <a href="#-license"><img src="https://img.shields.io/badge/License-MIT-gray.svg?style=flat-square" alt="License"></a>
</p>

---

## 📑 Table of Contents

- [💡 Executive Overview & The Problem](#-executive-overview--the-problem)
- [⚡ Key Capabilities](#-key-capabilities)
- [🏛️ System Architecture](#-system-architecture)
- [🚀 Quick Start Guide (Windows & Linux/macOS)](#-quick-start-guide)
- [🖥️ Interactive Features & UI Walkthrough](#️-interactive-features--ui-walkthrough)
- [📋 Constraint System Explained](#-constraint-system-explained)
  - [1. Hard Constraints (H1–H9) — Zero Clashes ($H = 0$)](#1-hard-constraints-h1h9--zero-clashes-h--0)
  - [2. Soft Constraints (S1–S5) — Quality Tuning](#2-soft-constraints-s1s5--quality-tuning)
- [🧠 The AI Algorithms Explained in Plain English](#-the-ai-algorithms-explained-in-plain-english)
- [🏆 Empirical Benchmarks](#-empirical-benchmarks)
- [📡 API Reference](#-api-reference)
- [📂 Repository Structure](#-repository-structure)
- [🎓 Viva Defense & Interview Cheat Sheet](#-viva-defense--interview-cheat-sheet)
- [🧪 Testing & Verification](#-testing--verification)
- [🔧 Troubleshooting & FAQ](#-troubleshooting--faq)
- [👨‍💻 Author & License](#-author--license)

---

## 💡 Executive Overview & The Problem

### ❌ The Real-World Timetabling Problem
Creating a university timetable is a notoriously difficult **$\mathcal{NP}$-complete combinatorial scheduling problem**. In any university or college:
- **Teachers get double-booked:** Professor A is mistakenly assigned to two different classes at 10:00 AM.
- **Room collisions occur:** Two sections try to enter the same lecture hall at the same time.
- **Capacity mismatches happen:** A class of 70 students is allocated to a small 40-seat tutorial room.
- **Laboratory mismatches:** A practical Computer Lab course gets assigned to an ordinary chalkboard classroom with no computers.
- **Student & Faculty Burnout:** Students suffer 3-hour idle gaps between lectures, or professors are forced to lecture 4 hours back-to-back without a break.
- **Mid-Semester Chaos:** When a faculty member goes on emergency leave or a class is cancelled, coordinators spend days manually rescheduling make-up sessions in spreadsheets.

###  The SchedulAI Solution
**SchedulAI** models university timetabling as a formal **Constraint Satisfaction Problem (CSP)**. By combining exact systematic search heuristics with stochastic local search (Simulated Annealing):
1. **Guarantees Zero Hard Conflicts ($H = 0$):** Eliminates all room, class, and teacher collisions in $<4$ seconds.
2. **Optimizes Human Comfort:** Minimizes student idle gaps, protects lunch breaks, ensures 2-hour lab continuity, and prevents faculty fatigue.
3. **Provides a Live Decision Support Dashboard:** Enables 1-click lecture cancellations, conflict-free make-up slot recommendations, faculty swaps, and multi-format exports (PDF, Excel, CSV).

---

## ⚡ Key Capabilities

| Capability | What It Does | Why It Matters |
| :--- | :--- | :--- |
| **Instant Conflict-Free Generation** | Uses Backtracking with MRV, Degree Heuristic, Forward Checking, and LCV. | Replaces 2 weeks of error-prone manual spreadsheet planning with a verified schedule in $<4$s. |
| **Two-Stage Hybrid Optimization** | Stage 1 solves all hard constraints ($H=0$); Stage 2 polishes soft criteria ($S$) via Simulated Annealing. | Delivers a **53.1% reduction in soft penalties** without ever violating institutional rules. |
| **3-Way Master Grid Matrix** | Dynamically render schedules **By Class Cohort**, **By Faculty Member**, or **By Physical Room**. | Instant visibility for department deans, individual professors, and campus facility managers. |
| **Operational Rescheduling Suite** | Single-click lecture cancellation, automatic make-up slot discovery, substitute teacher matching, and bilateral swaps. | Handles faculty leaves and room maintenance dynamically without throwing off the rest of the college. |
| **Institutional Workload Analytics** | Interactive Plotly visual charts auditing faculty teaching hours and facility capacity utilization. | Provides deans immediate oversight into unallocated hours and under-utilized campus infrastructure. |
| **Enterprise Multi-Format Export** | 1-click export to printable **PDF** reports, structured **Excel (.xlsx)** workbooks, and raw **CSV** sheets. | Ready for immediate distribution on notice boards, faculty portals, and student apps. |

---

## 🏛️ System Architecture

SchedulAI is engineered with strict separation of concerns across three decoupled tiers:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Streamlit Frontend (Port 8501)                        │
│   • Dark Navy & Light Theme Design System       • 3-Way Master Timetable Matrix │
│   • Operations & Rescheduling Suite             • Faculty & Room Analytics      │
│   • Algorithm Benchmark Visualizer              • Multi-Format Export UI        │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ HTTP REST (JSON)
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                            FastAPI Backend (Port 8000)                          │
│   • OpenAPI / Swagger Documentation             • Session & Schedule State Store│
│   • Cancellation & Swap Services                • PDF / Excel / CSV Exporters   │
│   • Real-Time Conflict Validator                • Workload Aggregation Engine   │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Pure Python Call
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                        Pure Python Algorithmic Core                             │
│       (Zero web/database framework dependencies — 100% portable & testable)     │
│                                                                                 │
│   ┌───────────────────────────┐             ┌───────────────────────────────┐   │
│   │   TimetableProblem (CSP)  │             │    ConstraintValidator        │   │
│   │  • Variables: X = {L_i}   │◄───────────►│  • Hard Constraints H1–H9     │   │
│   │  • Domains: D(X) = {(s,r)}│             │  • Soft Penalties S1–S5       │   │
│   └─────────────┬─────────────┘             └───────────────┬───────────────┘   │
│                 │                                           │                   │
│   ┌─────────────▼───────────────────────────────────────────▼───────────────┐   │
│   │                         Scheduling Algorithms                           │   │
│   │  1. Plain Backtracking               (Systematic Depth-First Baseline)  │   │
│   │  2. Improved Backtracking            (MRV + Degree + FC + LCV)          │   │
│   │  3. Min-Conflicts Local Search       (Random Walk & Plateau Breaker)    │   │
│   │  4. Simulated Annealing              (Metropolis-Hastings Metaheuristic)│   │
│   │  5. Hybrid Two-Stage CSP + SA        (Hard Feasibility + Soft Tuning)   │   │
│   │  6. Tabu Search, Genetic Algorithm, LNS, Hill Climbing                  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 📋 Prerequisites
- **Python:** 3.10, 3.11, 3.12, or 3.13
- **Operating System:** Windows, macOS, or Linux

---

### Step 1: Clone the Repository & Set Up Environment

#### On Windows (PowerShell):
```powershell
# Navigate into the project folder
cd ai-timetable-scheduler

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### On Linux / macOS (Bash / Zsh):
```bash
# Navigate into the project folder
cd ai-timetable-scheduler

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Start the FastAPI Backend Server
In your first terminal (with `venv` activated), start the REST API:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend API is live at: `http://localhost:8000`
* Interactive Swagger Docs: [`http://localhost:8000/docs`](http://localhost:8000/docs)

---

### Step 3: Start the Streamlit Web Application
In a **second terminal** (with `venv` activated):

```bash
python -m streamlit run streamlit_app.py --server.port 8501
```

🎉 Open your browser and navigate to:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🖥️ Interactive Features & UI Walkthrough

| Tab / View | Key Features & Actions |
| :--- | :--- |
| **🏠 Dashboard** | Instant executive summary showing active classes, total weekly lecture hours, room utilization %, faculty load balance, and backend connectivity indicator. |
| **📅 Timetable Grid** | **3 dynamic viewing perspectives:**<br>• **By Class Cohort:** (e.g. CS-Year2-A weekly schedule)<br>• **By Faculty Member:** (e.g. Prof. Alan Turing's personal teaching schedule)<br>• **By Room:** (e.g. Lab 101 occupancy across all periods)<br>• Features protected lunch periods ($H_9$) and **1-Click Export to PDF, Excel (.xlsx), and CSV**. |
| **⚙️ Generate Schedule** | Trigger schedule generation using any of the 9 solvers. Includes an **Auto-Recommend mode** that automatically chooses the best solver based on problem size. Inspect real-time solve duration, node expansions, and soft penalty scores. |
| **🔄 Operations & Rescheduling** | **Decision support suite:**<br>• **Cancel Class:** Mark a session cancelled due to teacher leave; room is instantly liberated.<br>• **Reschedule Missed Lecture:** Search collision-free make-up slots; matches available slots and substitute teachers automatically.<br>• **Faculty Swap:** Bilaterally swap two scheduled lectures with instant dry-run validation. |
| **📊 Workload Analytics** | Interactive charts auditing faculty weekly teaching hours against contractual limits, facility occupancy, and under-utilized classrooms. Viewports are locked against accidental zooming. |
| **🧪 Algorithm Comparison** | Side-by-side empirical benchmark analytics showing runtime (log scale), nodes expanded, and soft penalty convergence curves. |
| **👥 Manage Entities** | Inspect and manage student classes, faculty member profiles, rooms, and subject curriculum hour quotas. |

---

## 📋 Constraint System Explained

### 1. Hard Constraints ($H_1$–$H_9$) — Zero Clashes ($H = 0$)
Every valid schedule must **strictly satisfy all 9 hard institutional constraints**. Any candidate timetable with $H > 0$ is considered invalid and rejected.

| ID | Constraint Name | Plain-English Explanation | Enforcement Mechanism |
| :---: | :--- | :--- | :--- |
| **$H_1$** | **Teacher Clash** | No teacher can be scheduled to teach two different classes at the same time. | Timeslot-to-teacher collision hash map |
| **$H_2$** | **Class Cohort Clash** | A student batch cannot be in two different subjects/rooms at the same time. | Cohort timeslot index lookup |
| **$H_3$** | **Room Clash** | A physical room cannot host multiple classes simultaneously. | Facility occupancy matrix |
| **$H_4$** | **Room Capacity** | Room seating capacity must be greater than or equal to student class size. | Unary domain pre-pruning during problem init |
| **$H_5$** | **Room Type Match** | Theory classes must be in classrooms; practical lab sessions must be in dedicated laboratories. | Unary domain classification filter |
| **$H_6$** | **Teacher Availability** | Teachers are never assigned during their declared blackout/leave windows. | Domain pruning against teacher availability mask |
| **$H_7$** | **Curriculum Quota** | All required weekly contact hours for every subject must be scheduled exactly. | Variable instantiation check |
| **$H_8$** | **Teacher Max Load** | Total weekly teaching load assigned to an instructor cannot exceed their contract maximum. | Active workload accumulator audit |
| **$H_9$** | **Lunch Break Protection** | Period 4 is systematically protected as a lunch break for all student cohorts. | Systematic period exclusion during domain generation |

---

### 2. Soft Constraints ($S_1$–$S_5$) — Quality Tuning
Once a schedule is 100% collision-free ($H=0$), SchedulAI minimizes soft penalties to maximize student comfort and teacher satisfaction:

$$\text{Soft Penalty } (S) = 5 \cdot S_1 + 15 \cdot S_2 + 20 \cdot S_3 + 10 \cdot S_4 + 12 \cdot S_5$$

$$\text{Total Objective Cost} = 1000 \times H + S$$

- **$S_1$ — Free Period Gaps ($w=5$):** Eliminates awkward 1–2 hour idle gaps between classes on a student's weekday.
- **$S_2$ — Daily Subject Repeat ($w=15$):** Distributes subjects across different weekdays instead of bunching them on a single day.
- **$S_3$ — Lab Session Continuity ($w=20$):** Guarantees that 2-hour practical labs run as an uninterrupted consecutive block (enforced by modeling labs as atomic 2-period decision variables).
- **$S_4$ — Teacher Slot Preferences ($w=10$):** Prioritizes teachers' preferred working hours (e.g., morning vs. afternoon preference).
- **$S_5$ — Excessive Consecutive Teaching ($w=12$):** Penalizes assigning $>2$ back-to-back lecture periods to any single instructor to prevent fatigue.

---

## 🧠 The AI Algorithms Explained in Plain English

SchedulAI implements five primary scheduling algorithms, each with distinct trade-offs:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               AI Algorithm Spectrum                             │
├──────────────────────────┬──────────────────────────┬───────────────────────────┤
│ Systematic CSP (Exact)   │ Local Search (Heuristic) │ Decoupled Hybrid (Best)   │
│ • Plain Backtracking     │ • Min-Conflicts          │ • Hybrid CSP + SA         │
│ • Improved Backtracking  │ • Simulated Annealing    │   Stage 1: CSP (H = 0)    │
│   (MRV + FC + Deg + LCV) │ • Tabu Search, GA, LNS   │   Stage 2: SA  (Min S)    │
└──────────────────────────┴──────────────────────────┴───────────────────────────┘
```

### 1. Plain Backtracking (Baseline)
- **Concept:** Depth-First Search (DFS) that assigns slots one by one and backtracks when a collision occurs.
- **Analogy:** Trying to find your way out of a huge maze blindly—if you hit a wall, you step back one step and try the next door.
- **Limitation:** Suffers from severe *thrashing* (exponential slowdown $O(d^n)$) on large schedules because it doesn't look ahead.

### 2. Improved Backtracking (MRV + Degree + FC + LCV)
- **MRV (Minimum Remaining Values / "Fail-First"):** Always picks the most constrained class next (the one with the fewest available legal slots). If an assignment is doomed, it fails immediately rather than wasting millions of search steps.
- **Degree Heuristic:** Tie-breaker that picks the variable involved in the largest number of constraints with other unassigned classes.
- **Forward Checking (FC):** As soon as a slot is assigned, it immediately crosses off conflicting options from all related future variables. If any variable has 0 options left, it backtracks instantly.
- **LCV (Least Constraining Value):** Picks the slot that leaves the maximum flexibility for neighboring classes.

### 3. Min-Conflicts Local Search
- **Concept:** Starts with a complete schedule (which may have clashes) and iteratively moves the most conflicted class to the slot that creates the fewest clashes.
- **Plateau Escape:** Includes an **8% random-walk probability ($p = 0.08$)** and random restarts to break out of local optima and avoid infinite loops.

### 4. Simulated Annealing (Metaheuristic)
- **Concept:** Inspired by the annealing process in metallurgy. Explores neighboring schedule variations.
- **Metropolis-Hastings Criterion:** Improvements ($\Delta E < 0$) are always accepted. Worse moves ($\Delta E > 0$) are accepted probabilistically:
  $$P(\text{accept}) = \exp\left(-\frac{\Delta E}{T}\right)$$
  As the temperature $T$ cools geometrically ($T_{k+1} = \alpha T_k$), the algorithm gradually shifts from broad exploration to fine-tuning.

### 5. Two-Stage Hybrid CSP + SA (The Champion Engine)
- **Why It's the Best:** Pure CSP backtracking finds a valid schedule quickly but stops at the first feasible solution with poor soft scores. Pure SA can struggle to satisfy all 9 hard constraints from scratch.
- **How It Works:**
  - **Stage 1 (CSP):** Runs Improved Backtracking to achieve **strict zero hard clashes ($H = 0$)** in milliseconds.
  - **Stage 2 (Simulated Annealing):** Freezes all hard constraints and applies SA moves that exclusively optimize soft penalties ($S_1$–$S_5$).
  - **Outcome:** Lowest possible soft penalty score (highest quality schedule) with a 100% guarantee of zero hard clashes.

---

## 🏆 Empirical Benchmarks

Benchmarked across real seeded runs ([`experiments/results/benchmark_results.json`](experiments/results/benchmark_results.json)):

| Algorithm | Category | Small Dataset (3C, 6T, 4R)<br>Runtime (s) | Large Dataset (8C, 16T, 8R)<br>Runtime (s) | Hard Clashes ($H$) | Soft Penalty ($S$)<br>(Large Dataset) | Feasibility Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Plain Backtracking** | Baseline Search | 0.0021s | 0.0313s | **0** | 2,310 pts | 100% |
| **Improved Backtracking** | MRV + FC + Degree + LCV | 0.1099s | 3.4456s | **0** | 1,482 pts | 100% |
| **Min-Conflicts** | Heuristic Local Search | 0.0058s | 0.0783s | **0** | 1,438 pts | 100% |
| **Simulated Annealing** | Metaheuristic | 0.0948s | 0.2989s | $\le 1$ | 1,096 pts | 10% |
| **Hybrid CSP + SA** | Two-Stage Decoupled Engine | 0.1863s | 3.8833s | **0** | **1,083 pts** | **100%** |

> 💡 **Key Takeaway:** The **Two-Stage Hybrid CSP + SA** achieves the absolute highest schedule quality (**53.1% reduction in soft penalties** compared to baseline) while mathematically guaranteeing 0 hard clashes.

---

## 📡 API Reference

The backend exposes a fully documented, asynchronous REST API:

| Method | Endpoint | Description |
| :---: | :--- | :--- |
| `GET` | `/api/health` | Health check endpoint returning active classes, teachers, and session count. |
| `GET` | `/api/entities/all` | Returns all classes, teachers, rooms, subjects, and settings. |
| `POST` | `/api/schedule/generate` | Generates a timetable via specified algorithm (`hybrid`, `improved_backtracking`, `min_conflicts`). |
| `GET` | `/api/schedule/current` | Retrieves the active timetable sessions, KPI metrics, and soft penalty scores. |
| `POST` | `/api/operations/cancel` | Cancels a specific lecture session and releases its occupied room. |
| `POST` | `/api/operations/reschedule` | Finds and reserves conflict-free slots for a cancelled class with substitute matching. |
| `POST` | `/api/operations/swap` | Performs atomic pre-validation and swap between two scheduled sessions. |
| `GET` | `/api/analytics/overview` | Returns institutional KPIs (total classes, teacher load, room capacity stats). |
| `GET` | `/api/analytics/workload` | Returns individual teacher teaching hours against maximum contractual caps. |
| `GET` | `/api/analytics/rooms` | Returns room utilization statistics across days and periods. |
| `GET` | `/api/io/export/{format}` | Exports active timetable (`pdf`, `xlsx`, `csv`). |

---

## 📂 Repository Structure

```
ai-timetable-scheduler/
├── assets/                         # Application branding & SchedulAI logo
├── algorithms/                     # Central Algorithm Implementations & Registry
│   ├── base.py                     # BaseSolver abstract class & performance metrics
│   ├── backtracking_plain.py       # Plain depth-first search baseline
│   ├── backtracking_heuristics.py  # Improved Backtracking (MRV + FC + Degree + LCV)
│   ├── min_conflicts.py            # Min-Conflicts with random walk plateau escape
│   ├── simulated_annealing.py      # Simulated Annealing with Metropolis-Hastings
│   ├── hybrid.py                   # Two-stage Hybrid CSP + SA solver
│   ├── tabu_search.py              # Tabu Search solver
│   ├── genetic_algorithm.py        # Genetic Algorithm solver
│   ├── hill_climbing.py            # Steepest-ascent hill climbing with restarts
│   ├── large_neighbourhood_search.py # LNS destroy-and-repair solver
│   └── registry.py                 # Unified algorithm registry & auto-recommender
├── backend/app/                    # FastAPI Production REST Application
│   ├── api/routes/                 # REST controllers (entities, schedule, operations, analytics, io)
│   ├── database/                   # In-memory DataStore & state management
│   ├── models/                     # Domain entity schemas
│   ├── schemas/                    # Pydantic API response models
│   ├── services/                   # Schedule generation, rescheduling, swap, and export services
│   └── main.py                     # FastAPI entry point & startup data loader
├── core/                           # Pure Algorithmic CSP & Constraint Engine
│   ├── problem.py                  # Discrete CSP formulation (Variables, Domains, SlotValues)
│   └── validator.py                # Authoritative ConstraintValidator (H1–H9 and S1–S5)
├── frontend/                       # Streamlit Web Application
│   ├── app.py                      # Main Streamlit layout & dynamic routing
│   ├── api_client.py               # Typed HTTP client communicating with FastAPI
│   ├── theme.py                    # Dark Navy & Light Mode CSS design system
│   └── views/                      # Dashboard, timetable_grid, generate, operations, analytics, benchmarks, entities
├── data/                           # Verified Datasets
│   ├── small_dataset.json          # 3 Classes, 6 Teachers, 4 Rooms (5d x 6p)
│   └── large_dataset.json          # 8 Classes, 16 Teachers, 8 Rooms (5d x 7p)
├── docs/                           # Extended Project Documentation & Reports
│   ├── VIVA_DEFENSE_AND_PROJECT_REPORT.md  # Comprehensive Viva preparation guide
│   ├── report.md                   # Academic project report
│   └── requirements.md             # Functional & Non-functional requirements
├── experiments/                    # Benchmarking & Verification Suite
│   ├── run_benchmarks.py           # Automated empirical evaluation script
│   ├── cross_check.py              # Independent verification with python-constraint
│   └── results/                    # Seeded JSON benchmark outputs & metrics
├── tests/                          # Automated Pytest Test Suite
│   ├── test_all_algorithms.py      # End-to-end verification of all 9 solvers
│   ├── test_phase4_problem_and_validator.py # Strict verification of H1-H9 & S1-S5
│   ├── test_phase12_cancellation_and_reschedule.py # Operational workflow tests
│   └── ...                         # Comprehensive phase-by-phase test suites
├── requirements.txt                # Production Python dependencies
├── streamlit_app.py                # Streamlit entry point wrapper
└── README.md                       # Comprehensive Project Documentation
```

---

## 🎓 Viva Defense & Interview Cheat Sheet

### Q1: Why does Plain Chronological Backtracking struggle on large timetable problems?
> **Answer:** Plain backtracking selects variables and values in arbitrary order. If an early assignment introduces an unavoidable clash deeper in the search tree, it blindly explores all downstream subtrees before finally backtracking ($O(d^n)$ complexity). It lacks forward-looking intelligence and performs no domain pruning.

### Q2: How do MRV and Forward Checking prevent thrashing?
> **Answer:** 
> - **MRV (Minimum Remaining Values):** Implements the *fail-first principle*. By choosing the variable with the smallest legal domain, any dead-end is encountered and aborted immediately at the current level.
> - **Forward Checking (FC):** Whenever a slot is assigned, it immediately filters conflicting values from all related unassigned variables. If any variable's domain becomes empty ($\mathcal{D}_Y = \emptyset$), the branch is aborted before wasting time.

### Q3: Why is the Two-Stage Hybrid CSP + SA better than pure Simulated Annealing?
> **Answer:** Pure Simulated Annealing starting from a random assignment can spend thousands of iterations struggling to resolve basic hard clashes ($H_1$–$H_9$). Our **Two-Stage Hybrid** uses CSP Backtracking to guarantee $H=0$ in milliseconds, and then lets Simulated Annealing focus 100% on polishing human soft preferences ($S_1$–$S_5$), yielding a **53% better schedule quality**.

### Q4: How does SchedulAI guarantee that 2-hour practical labs are never split?
> **Answer:** Rather than modeling a 2-hour lab as two separate 1-hour variables connected by tricky distance constraints, SchedulAI models the lab as an **atomic block variable** (`duration=2`). Its domain is pruned upfront so it can only start in periods where neither period nor period+1 overlaps with lunch. This eliminates fragmentation and satisfies continuity by construction.

### Q5: How do live cancellations and swaps prevent creating new clashes?
> **Answer:** Every proposed manual edit, cancellation, or bilateral teacher swap is passed through the centralized `ConstraintValidator`. The engine creates a virtual simulated assignment in-memory, executes all 9 hard constraint checks, and only commits the move if it is 100% conflict-free.

---

## 🧪 Testing & Verification

Run the automated pytest test suite:

```bash
# Activate your virtual environment
pytest tests/test_all_algorithms.py -v
```

Expected output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.x, pytest-9.x.x
collected 10 items

tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[hybrid] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[backtracking_heuristics] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[min_conflicts] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[simulated_annealing] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[tabu_search] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[genetic_algorithm] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[lns] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[hill_climbing] PASSED
tests/test_all_algorithms.py::test_all_algorithms_execute_successfully[plain_backtracking] PASSED
tests/test_all_algorithms.py::test_reproducibility_with_seed PASSED

============================= 10 passed in ~16s =============================
```

To run third-party cross-validation against `python-constraint`:
```bash
python experiments/cross_check.py
```

---

## 🔧 Troubleshooting & FAQ

<details>
<summary><strong>1. "Backend Disconnected" red banner in Streamlit</strong></summary>

Ensure the FastAPI server is running in a separate terminal:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Verify backend health directly by opening [http://localhost:8000/api/health](http://localhost:8000/api/health) in your browser.
</details>

<details>
<summary><strong>2. Port 8000 or 8501 is already in use</strong></summary>

You can specify custom ports for either service:
```bash
# Run backend on port 8001:
python -m uvicorn backend.app.main:app --port 8001

# In frontend terminal, point to port 8001 and run Streamlit on port 8502:
set BACKEND_URL=http://localhost:8001
python -m streamlit run streamlit_app.py --server.port 8502
```
</details>

<details>
<summary><strong>3. Windows "python.exe: The file cannot be accessed by the system"</strong></summary>

This occurs when Windows redirects `python` to the Microsoft Store. Ensure your Python path is configured, or use the virtual environment binary directly:
```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
</details>

---

## 👨‍💻 Author & License

- **Author:** Suraj Meena
- **Email:** [surajbyadwal.08@gmail.com](mailto:surajbyadwal.08@gmail.com)
- **Repository:** [AI Timetable Scheduler](https://github.com/)
- **License:** Open-source under the [MIT License](LICENSE).
