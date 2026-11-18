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
- [🧠 Deep-Dive Technical Explanation Notes](#-deep-dive-technical-explanation-notes)
  - [Note 1: The Timetabling Problem as a Formal CSP](#note-1-the-timetabling-problem-as-a-formal-csp)
  - [Note 2: Systematic Search & The Heuristics (MRV, Degree, FC, LCV)](#note-2-systematic-search--the-heuristics-mrv-degree-fc-lcv)
  - [Note 3: Heuristic Local Search (Min-Conflicts with Plateau Escape)](#note-3-heuristic-local-search-min-conflicts-with-plateau-escape)
  - [Note 4: Metaheuristics & Simulated Annealing (Metropolis-Hastings)](#note-4-metaheuristics--simulated-annealing-metropolis-hastings)
  - [Note 5: The Two-Stage Decoupled Hybrid CSP + SA Engine](#note-5-the-two-stage-decoupled-hybrid-csp--sa-engine)
  - [Note 6: Atomic 2-Hour Practical Lab Modeling](#note-6-atomic-2-hour-practical-lab-modeling)
  - [Note 7: Operational Rescheduling & In-Memory Mutation Safety](#note-7-operational-rescheduling--in-memory-mutation-safety)
- [🏆 Empirical Benchmarks](#-empirical-benchmarks)
- [📡 API Reference](#-api-reference)
- [📂 Repository Structure](#-repository-structure)
- [🎓 Viva Defense & Interview Master Q&A](#-viva-defense--interview-master-qa)
- [🧪 Testing & Verification](#-testing--verification)
- [🔧 Troubleshooting & FAQ](#-troubleshooting--faq)
- [👨‍💻 Author & License](#-author--license)

---

## 💡 Executive Overview & The Problem

### ❌ The Real-World Timetabling Problem
Creating conflict-free university timetables is a notoriously difficult **$\mathcal{NP}$-complete combinatorial scheduling problem**. In traditional academic administration, coordinators spend 2 to 3 weeks using manual spreadsheets, frequently resulting in:
- **Teacher & Room Collisions:** Simultaneous double-booking of instructors or lecture halls.
- **Capacity & Facility Mismatches:** Placing a 70-student class into a 40-seat tutorial room, or placing computer programming practicals in ordinary theory classrooms with no workstations.
- **Pedagogical Degradation & Fatigue:** Students suffer disjointed 2–3 hour idle gaps between classes; teachers are assigned $>3$ back-to-back lecture periods without recovery time.
- **Mid-Semester Fragility:** When faculty take unplanned leave or a room requires maintenance, attempting manual make-up sessions creates a ripple of new clashes across the institution.

### 🌟 The SchedulAI Solution
**SchedulAI** models university timetabling as a formal **Constraint Satisfaction Problem (CSP)** with soft penalty optimization. By coupling exact systematic search heuristics with stochastic local search metaheuristics (Simulated Annealing):
1. **Guarantees Zero Hard Conflicts ($H = 0$):** Eliminates 100% of teacher, class, and room clashes in $<4$ seconds.
2. **Maximizes Human Comfort:** Minimizes student idle windows, guarantees protected lunch breaks, preserves 2-hour practical lab continuity, and balances teacher workloads.
3. **Provides an Operational Web Decision Support System:** Features 1-click lecture cancellations, conflict-free make-up slot discovery with substitute matching, bilateral faculty swaps, and multi-format exports (PDF, Excel, CSV).

---

## ⚡ Key Capabilities

| Capability | What It Does | Why It Matters |
| :--- | :--- | :--- |
| **Instant Conflict-Free Generation** | Uses Backtracking with MRV, Degree Heuristic, Forward Checking, and LCV. | Replaces 2 weeks of manual spreadsheet planning with a verified schedule in $<4$s. |
| **Two-Stage Hybrid Optimization** | Stage 1 solves all hard constraints ($H=0$); Stage 2 polishes soft criteria ($S$) via Simulated Annealing. | Delivers a **53.1% reduction in soft penalties** without ever violating institutional rules. |
| **3-Way Master Grid Matrix** | Dynamically renders schedules **By Class Cohort**, **By Faculty Member**, or **By Physical Room**. | Instant clarity for department deans, individual professors, and campus facility managers. |
| **Operational Rescheduling Suite** | Single-click lecture cancellation, automatic make-up slot discovery, substitute teacher matching, and bilateral swaps. | Handles faculty leaves and room maintenance dynamically without disrupting the rest of the college. |
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

## 🧠 Deep-Dive Technical Explanation Notes

> [!NOTE]
> This section contains rigorous mathematical formulations, algorithmic execution mechanics, and design explanations. Ideal for academic review, project defense, and architectural understanding.

### Note 1: The Timetabling Problem as a Formal CSP

A formal **Constraint Satisfaction Problem (CSP)** is defined as a triplet:

$$\langle \mathcal{X}, \mathcal{D}, \mathcal{C} \rangle$$

1. **Variables ($\mathcal{X}$):**
   Let $\mathcal{C}$ be the set of student class cohorts, $\mathcal{S}$ the set of subjects, and $\mathcal{T}$ the set of teachers.
   Each required course contact block is modeled as an individual decision variable:
   $$\mathcal{X} = \{ X_{c, s, k} \mid c \in \mathcal{C},\, s \in \mathcal{S},\, k \in \{1, \dots, \lceil \text{weekly\_hours}(c, s) / \text{duration}(s) \rceil\} \}$$
   For example, if CS-Year2 needs 4 hours of Data Structures (theory, duration=1), it generates 4 discrete variables: $X_{CS2, DS, 1}, X_{CS2, DS, 2}, X_{CS2, DS, 3}, X_{CS2, DS, 4}$.

2. **Domains ($\mathcal{D}$):**
   The domain $\mathcal{D}(X)$ of each variable $X$ is the set of legal candidate assignments:
   $$\mathcal{D}(X) = \{ \langle \text{day}, \text{period}, \text{room}, \text{teacher} \rangle \} \subseteq \text{Days} \times \text{Periods} \times \mathcal{R} \times \mathcal{T}$$
   For a standard 5-day week with 7 periods per day, 8 rooms, and 16 teachers, the raw Cartesian space is:
   $$5 \times 7 \times 8 \times 16 = 4,480 \text{ choices per variable}$$
   With 40 variables, total combinations reach $4480^{40} \approx 10^{146}$ states.

3. **Constraints ($\mathcal{C}$):**
   The set of hard relational predicates ($H_1$ to $H_9$) that must strictly evaluate to `True`.

---

### Note 2: Systematic Search & The Heuristics (MRV, Degree, FC, LCV)

Pure chronological Depth-First Search explores paths blindly and experiences severe **thrashing**—repeatedly exploring subtrees doomed by an early mistake made near the root. SchedulAI equips backtracking with four classical AI heuristics:

#### 1. Minimum Remaining Values (MRV / "Fail-First" Principle)
- **Problem:** In standard search, variables are assigned in an arbitrary static order. If variable $X_{35}$ has only 1 legal value left due to constraints, picking $X_1$ first wastes time branching on thousands of useless choices before discovering that $X_{35}$ cannot be satisfied.
- **MRV Solution:** At each decision step, MRV dynamically inspects all remaining unassigned variables and chooses:
  $$X^* = \arg\min_{X \in \mathcal{X}_{\text{unassigned}}} |\mathcal{D}(X)|$$
- **Effect:** If any branch leads to a dead end, it fails immediately at the current level, drastically reducing tree depth.

#### 2. Degree Heuristic (Constraint Graph Density Tie-Breaker)
- **Problem:** At the beginning of search, many variables have equal domain sizes. MRV cannot distinguish between them.
- **Degree Solution:** Selects the variable involved in the largest number of constraints with other *unassigned* variables:
  $$X^* = \arg\max_{X \in \text{Ties(MRV)}} |\{ Y \in \mathcal{X}_{\text{unassigned}} \mid (X, Y) \in \text{ConstraintGraph} \}|$$
- **Effect:** Instantiating the most connected variable prunes the maximum number of values from future domains, effectively shrinking the future branching factor.

#### 3. Forward Checking (FC / Proactive Pruning)
- **Problem:** Backtracking only checks if the *current* assignment violates constraints. It does not look ahead to see if the assignment starves future variables.
- **FC Solution:** Whenever variable $X$ is assigned slot $\langle d, p, r, t \rangle$:
  1. For every unassigned variable $Y$ sharing teacher $t$, class $c$, or room $r$, prune overlapping slots from $\mathcal{D}(Y)$.
  2. If any unassigned variable's domain becomes empty ($\mathcal{D}(Y) = \emptyset$), the assignment is **immediately aborted** without expanding further child nodes.
  3. A restoration stack records all pruned values so that when backtracking occurs, domains are restored in $O(1)$ time.

#### 4. Least Constraining Value (LCV / "Succeed-First" Value Ordering)
- **Problem:** Once variable $X$ is selected, in what order should its domain values $v \in \mathcal{D}(X)$ be attempted?
- **LCV Solution:** Ranks candidate values $v$ by the number of choices they eliminate from other unassigned variables:
  $$v^* = \arg\min_{v \in \mathcal{D}(X)} \sum_{Y \in \text{Neighbors}(X)} \mathbb{I}(v \text{ conflicts with } u \in \mathcal{D}(Y))$$
- **Effect:** Maximizes the likelihood that the first tried value successfully extends to a complete conflict-free solution.

---

### Note 3: Heuristic Local Search (Min-Conflicts with Plateau Escape)

Unlike systematic search which works with partial assignments, **Local Search** operates on complete states that may contain conflicts.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      Min-Conflicts Algorithm Step-by-Step                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. Initialize: Assign every lecture variable a slot (e.g. random or greedy).   │
│ 2. Evaluate: Identify all variables currently involved in clashes (H > 0).     │
│ 3. Termination: If conflicts == 0, return current feasible schedule.            │
│ 4. Variable Selection: Randomly pick one conflicted variable X_conflict.        │
│ 5. Value Selection (Heuristic Repair):                                          │
│    With probability (1 - p):                                                    │
│        Assign X_conflict the value v that minimizes total schedule conflicts.   │
│    With probability p = 0.08 (Random Walk):                                     │
│        Assign X_conflict a random legal slot (breaks out of plateaus).          │
│ 6. Restart Check: If iterations > max_steps without progress, perform random    │
│    restart to escape deep local minima traps.                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### Note 4: Metaheuristics & Simulated Annealing (Metropolis-Hastings)

Simulated Annealing is a stochastic optimization metaheuristic derived from physical metallurgy (slow cooling of metals to reach minimum crystalline energy states).

1. **State & Energy:**
   - **State ($S$):** A candidate complete timetable.
   - **Energy ($E$):** $\text{Cost}(S) = 1000 \times H + S$.

2. **Metropolis-Hastings Acceptance Criterion:**
   Given current state $S$ and neighbor state $S'$, calculate energy differential:
   $$\Delta E = \text{Cost}(S') - \text{Cost}(S)$$
   - If $\Delta E < 0$ (the neighbor improves the schedule), the transition is **always accepted**.
   - If $\Delta E \ge 0$ (the neighbor is worse), the transition is accepted probabilistically with:
     $$P(\text{accept}) = \exp\left(-\frac{\Delta E}{T}\right)$$
     where $T$ is the current temperature.

3. **Geometric Cooling Schedule:**
   After every epoch of $L$ moves, temperature drops:
   $$T_{k+1} = \alpha \cdot T_k \quad (\text{with } \alpha \approx 0.95)$$
   - **Early phase ($T$ is high):** Solver accepts worse moves frequently, freely jumping out of local optima and exploring wide topological regions.
   - **Late phase ($T \to 0$):** Solver becomes greedy, accepting almost exclusively downhill moves to polish fine details.

---

### Note 5: The Two-Stage Decoupled Hybrid CSP + SA Engine

Why is a decoupled two-stage architecture superior to single algorithms?

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                   Stage 1: CSP Improved Backtracking (Exact)                   │
│   • Variable ordering via MRV + Degree Heuristic                                │
│   • Forward Checking domain pruning                                             │
│   • Target: Strict Zero Hard Clashes (H = 0)                                    │
│   • Execution Time: < 0.20 seconds                                              │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ Guaranteed Feasible Seed Schedule (H = 0)
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                   Stage 2: Simulated Annealing (Soft Polishing)                 │
│   • Hard Constraint Invariant Guard: Only moves preserving H = 0 are evaluated  │
│   • Focuses 100% of iterations on minimizing Soft Penalty (S1–S5)               │
│   • Results in lowest soft penalties (1,083 pts vs 2,310 baseline)              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

- **Limitation of Pure CSP:** Backtracking stops at the *first* leaf node satisfying $H = 0$. That solution typically has poor soft quality (awkward student gaps, bad teacher hours) because it never optimizes soft costs.
- **Limitation of Pure SA:** SA starting from a random state wastes thousands of iterations struggling to resolve basic hard clashes ($H_1$–$H_9$), frequently getting trapped at $H=1$ or $H=2$.
- **Hybrid Solution:** Stage 1 guarantees mathematical feasibility ($H = 0$) in sub-seconds. Stage 2 takes this clean seed and polishes human comfort ($S_1$–$S_5$), delivering a **53.1% reduction in soft penalties**.

---

### Note 6: Atomic 2-Hour Practical Lab Modeling

In engineering curricula, lab courses require 2 continuous contact hours. A naive implementation creates two 1-hour variables $L_1$ and $L_2$ and adds an explicit adjacency constraint $| \text{period}(L_1) - \text{period}(L_2) | = 1$.

**Why Naive Adjacency Fails:**
- Doubles the variable search space.
- Induces domain thrashing: $L_1$ may get placed in Period 7 (end of day) where $L_2$ cannot follow, or $L_1$ gets placed before lunch and $L_2$ after lunch.

**SchedulAI's Atomic Block Solution:**
1. A practical lab is formulated as a single variable with property `duration = 2`.
2. During domain generation, its valid start periods are restricted upfront:
   $$\text{ValidPeriods} = \{ p \in \{1, \dots, \text{periods\_per\_day} - 1\} \mid p \ne \text{lunch\_period} \land (p + 1) \ne \text{lunch\_period} \}$$
3. Assigning this variable atomically claims both period $p$ and period $p+1$ simultaneously across the room, class, and teacher occupancy matrices.
4. **Result:** Lab continuity ($S_3$) and lunch break protection ($H_9$) are guaranteed **by construction** without generating extra search variables.

---

### Note 7: Operational Rescheduling & In-Memory Mutation Safety

Academic schedules are living documents that change mid-semester due to teacher sick leave, facility repairs, or sports events.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Operational Mutation Validation Pipeline                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. Client Request: Cancel lecture, reschedule session, or bilateral swap.       │
│ 2. In-Memory Shadow Clone: Clone active session dictionary in DataStore.        │
│ 3. Dry-Run Mutation: Apply proposed change to the shadow dictionary.            │
│ 4. Full Constraint Pass: Pass shadow state through ConstraintValidator.         │
│    • Checks H1 (Teacher), H2 (Class), H3 (Room), H4 (Capacity), H5 (RoomType)   │
│    • Checks H6 (TeacherAvailability), H8 (TeacherMaxLoad), H9 (LunchProtection) │
│ 5. Decision Gate:                                                               │
│    • If Violations == 0: Commit mutation to master store and return HTTP 200.   │
│    • If Violations > 0: Discard clone, return HTTP 400 with exact clash reason. │
└─────────────────────────────────────────────────────────────────────────────────┘
```
This guarantees that **no manual edit can ever corrupt the master schedule** or introduce a hidden clash.

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
| `GET` | `/api/schedule/current` | Retrieves active timetable sessions, KPI metrics, and soft penalty scores. |
| `POST` | `/api/operations/cancel` | Cancels a specific lecture session and releases its occupied room. |
| `POST` | `/api/operations/reschedule` | Finds and reserves conflict-free slots for a cancelled class with substitute matching. |
| `POST` | `/api/operations/swap` | Performs atomic pre-validation and swap between two scheduled sessions. |
| `GET` | `/api/analytics/overview` | Returns institutional KPIs (total classes, teacher load, room capacity stats). |
| `GET` | `/api/analytics/workload` | Returns individual teacher teaching hours against contractual caps. |
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

## 🎓 Viva Defense & Interview Master Q&A

### Q1: Why does Plain Chronological Backtracking struggle on large timetable problems?
> **Answer:** Plain backtracking selects variables and values in arbitrary static order. If an early assignment introduces an unavoidable clash deeper in the search tree, it blindly explores all downstream subtrees before finally backtracking ($O(d^n)$ complexity). It lacks forward-looking intelligence and performs zero domain pruning.

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
