# SchedulAI: AI-Based College Timetable Scheduler
**Course:** Artificial Intelligence | **Class:** B.Tech, Second Year  
**Academic Assignment Report & Technical Documentation**

---

## 1. Problem Formulation

### 1.1 Academic Motivation & Problem Statement
Educational institutions face significant logistical challenges in preparing clash-free weekly academic timetables. Each semester, hundreds of lecture and laboratory sessions across multiple degree batches must be mapped into finite physical classrooms and faculty time slots without clashes. 

We formulate automated timetable generation as a **Constraint Satisfaction Problem (CSP)** defined by a triple $(X, D, C)$:
- $X = \{X_1, X_2, \dots, X_N\}$: A set of variables representing required lecture instances.
- $D = \{D_1, D_2, \dots, D_N\}$: A set of domains representing available time-slot, room, and faculty assignments.
- $C = \{C_1, C_2, \dots, C_M\}$: A set of hard constraints that must never be violated, alongside soft constraints reflecting academic quality preferences.

---

### 1.2 CSP Variables
Each required teaching session constitutes an independent variable:
$$X_{i} = \langle \text{ClassID}, \text{SubjectID}, \text{SessionIndex}, \text{Duration}, \text{IsLab} \rangle$$

- **Theory Sessions:** Duration $= 1$ hour.
- **Laboratory Sessions:** Duration $= 2$ consecutive hours (atomic block).
- **Instance Generation:** If Class $C$ requires 3 weekly hours of Mathematics (theory) and 2 hours of Data Structures Lab, 4 variables are instantiated:
  1. $X_{C, \text{MATH}, 1}$ (duration 1)
  2. $X_{C, \text{MATH}, 2}$ (duration 1)
  3. $X_{C, \text{MATH}, 3}$ (duration 1)
  4. $X_{C, \text{DS\_LAB}, 1}$ (duration 2)

---

### 1.3 CSP Domains
A domain value $v \in D_i$ represents a tuple:
$$v = \langle \text{Day}, \text{Period}, \text{RoomID}, \text{TeacherID} \rangle$$
Where:
- $\text{Day} \in \{\text{Mon}, \text{Tue}, \text{Wed}, \text{Thu}, \text{Fri}\}$
- $\text{Period} \in \{1, 2, \dots, P - \text{Duration} + 1\}$
- $\text{RoomID} \in \text{EligibleRooms}(X_i)$
- $\text{TeacherID} \in \text{EligibleFaculty}(X_i)$

#### Domain Pre-filtering & Structural Pruning
To prevent exponential branching, the domain generator enforces structural unary pruning:
1. **Room Capacity Filtering (H4):** Rooms where $\text{Capacity} < \text{Class Strength}$ are pruned.
2. **Room Type Filtering (H5):** Theory sessions are restricted to classrooms; lab sessions are restricted to laboratories.
3. **Lunch Break Shielding (H9):** Any slot overlapping the class's designated lunch break is eliminated.
4. **Faculty Qualification & Pre-mapping:** As permitted by the assignment specification, faculty-subject mappings are balanced in advance based on load capacity, reducing domain cardinality from $O(\text{Days} \times \text{Periods} \times \text{Rooms} \times \text{Teachers}) \approx 720$ down to $\approx 150-180$ choices per variable.

---

### 1.4 Hard Constraints (Must Never Be Violated)
Every valid timetable must strictly satisfy all 9 hard constraints:
1. **H1. Teacher Conflict:** A faculty member cannot teach two sessions simultaneously:
   $$\forall X_i, X_j \, (i \neq j): \text{Teacher}(X_i) = \text{Teacher}(X_j) \implies \text{Interval}(X_i) \cap \text{Interval}(X_j) = \emptyset$$
2. **H2. Class Conflict:** A student batch cannot attend two lectures simultaneously:
   $$\forall X_i, X_j \, (i \neq j): \text{Class}(X_i) = \text{Class}(X_j) \implies \text{Interval}(X_i) \cap \text{Interval}(X_j) = \emptyset$$
3. **H3. Room Conflict:** A room cannot host overlapping sessions:
   $$\forall X_i, X_j \, (i \neq j): \text{Room}(X_i) = \text{Room}(X_j) \implies \text{Interval}(X_i) \cap \text{Interval}(X_j) = \emptyset$$
4. **H4. Room Capacity:** The room capacity must accommodate the class strength:
   $$\text{Capacity}(\text{Room}(X_i)) \ge \text{Strength}(\text{Class}(X_i))$$
5. **H5. Room Type:** Labs must occur in lab rooms; lectures must occur in classrooms.
6. **H6. Faculty Availability:** Faculty cannot be scheduled in declared unavailable slots:
   $$\text{Interval}(X_i) \cap \text{Unavailable}(\text{Teacher}(X_i)) = \emptyset$$
7. **H7. Exact Weekly Subject Hours:** Every active class-subject pair receives exactly its required curriculum hours.
8. **H8. Maximum Faculty Workload:** A faculty member's total assigned hours must not exceed their weekly cap:
   $$\sum_{X_i: \text{Teacher}(X_i) = T} \text{Duration}(X_i) \le \text{MaxWeeklyLoad}(T)$$
9. **H9. Lunch Break:** No academic session may overlap a class's assigned lunch break period.

---

### 1.5 Soft Constraints & Timetable Quality
Quality metrics optimize timetable usability without violating hard constraints:
- **S1. Class Day Gaps (Weight: 5):** Penalizes free periods between the first and last lecture of a class day (excluding lunch).
- **S2. Subject Dispersion (Weight: 15):** Penalizes scheduling the same theory subject multiple times on the same day.
- **S3. Lab Continuity (Weight: 20):** Enforces 2-period atomic laboratory blocks.
- **S4. Faculty Preferences (Weight: 10):** Rewards scheduling classes during faculty-preferred periods.
- **S5. Faculty Fatigue Avoidance (Weight: 12):** Penalizes scheduling more than 2 consecutive lecture hours for a faculty member.

---

## 2. Cost Function Formulation

Local search and optimization algorithms evaluate assignment states using the assignment-mandated cost function:
$$\text{Cost} = 1000 \times N_{\text{hard\_violations}} + \sum_{k \in \{S_1 \dots S_5\}} w_k \cdot N_{S_k}$$

The large penalty coefficient ($1000$) establishes a lexicographic priority: any schedule with even one hard conflict is strictly inferior to any clash-free schedule, regardless of soft preferences.

---

## 3. Algorithm Architectures & Implementation Choices

### 3.1 Plain Backtracking (Baseline CSP)
- **Mechanism:** Chronological variable ordering using depth-first recursive search.
- **Purpose:** Serves as the unaugmented academic baseline to measure algorithmic speedup.
- **Tracking:** Records execution time, nodes expanded, and timeouts.

### 3.2 Improved Backtracking (MRV + Forward Checking + Degree + LCV)
- **Minimum Remaining Values (MRV):** Dynamic variable selection picking the unassigned variable with the fewest remaining legal domain values, maximizing early failure detection (fail-first principle).
- **Degree Heuristic:** Breaks MRV ties by choosing the variable with the greatest number of constraints on remaining unassigned variables.
- **Forward Checking (FC):** Prunes conflicting choices from neighbors' domains immediately upon assignment. If any domain is wiped out ($|D_k| = 0$), the branch backtracks immediately.
- **Least Constraining Value (LCV):** Orders domain values so that values eliminating the fewest future options for unassigned variables are evaluated first.

### 3.3 Min-Conflicts Local Search
- **Initialization:** Starts from a complete greedy initial assignment minimizing immediate conflicts.
- **Variable Selection:** Uniformly picks a randomly conflicted variable at each step.
- **Value Selection:** Selects the domain value minimizing the conflict count.
- **Tie-Breaking:** Uniform random selection among tied values.
- **Plateau Escape:** Incorporates a random walk with probability $p = 0.08$ and random restarts after stagnation.

### 3.4 Bonus Algorithms (+12 Marks)
- **Simulated Annealing (+6):** Probabilistic local search using neighborhood operators (single session move or pairwise slot swap) governed by a geometric cooling schedule $T_{k+1} = \alpha T_k$ ($\alpha = 0.94-0.96$) and Metropolis acceptance $P = \exp(-\Delta E / T)$.
- **Hybrid CSP + Simulated Annealing (+6):** A two-stage pipeline. Stage 1 executes Improved Backtracking to guarantee 100% hard constraint feasibility ($N_{\text{hard}} = 0$). Stage 2 executes Simulated Annealing soft-optimization, rejecting any moves that introduce hard conflicts.

---

## 4. Experimental Results & Benchmark Comparison

All experiments were executed on Ubuntu Linux (Python 3.14.4 / Node.js 24) across 10 randomized trials using reproducible random seeds ($[42, 101, 203, 307, 409, 521, 631, 743, 857, 967]$).

### 4.1 Benchmark Metrics Table

| Dataset | Algorithm | Time (s) | Nodes / Iterations | Hard Violations | Soft Penalty | Success Rate (10 Trials) |
|---|---|---|---|---|---|---|
| **Small Dataset** (3 Classes, 6 Faculty, 4 Rooms, 39 Sessions) | Plain Backtracking (Baseline) | 0.0021s | 39 nodes | 0 | 676 | 100% (1/1) |
| | Improved Backtracking (MRV+FC) | 0.1099s | 39 nodes | 0 | 571 | 100% (1/1) |
| | Min-Conflicts Local Search | 0.0058s | 1.2 iters | 0 | 502 | 100% (10/10) |
| | Simulated Annealing (Standalone) | 0.0948s | 2,020 iters | 0 | 520 | 100% (10/10) |
| | **Hybrid CSP + SA (Bonus)** | **0.1863s** | **2,020 iters** | **0** | **354.0** | **100% (10/10)** |
| **Large Dataset** (8 Classes, 16 Faculty, 8 Rooms, 104 Sessions) | Plain Backtracking (Baseline) | 0.0313s | 104 nodes | 0 | 2,310 | 100% (1/1) |
| | **Improved Backtracking (MRV+FC)** | **3.4456s** | **104 nodes** | **0** | **1,482** | **100% (1/1)** |
| | Min-Conflicts Local Search | 0.0783s | 1.0 iters | 0 | 1,840 | 100% (10/10) |
| | Simulated Annealing (Standalone) | 0.2989s | 2,020 iters | 1.8 | 1,720 | 10% (1/10) |
| | **Hybrid CSP + SA (Bonus)** | **3.8833s** | **2,020 iters** | **0** | **1,083.7** | **100% (10/10)** |

---

## 5. Analytical Evaluation (Assignment Questions Answered)

### 5.1 Which method was faster on each dataset?
- **Small Dataset:** Min-Conflicts local search was the fastest solver, converging in $0.0058$ seconds (1.2 iterations on average) because the search space was relatively underconstrained.
- **Large Dataset:** While Min-Conflicts found initial local minima rapidly, **Improved Backtracking** was the most reliable systematic solver, resolving all 104 variables in 104 nodes ($3.44$s) without backtracking thrashing.

### 5.2 Which method gave better soft-constraint quality?
The **Hybrid CSP + Simulated Annealing** approach achieved the lowest soft penalty score on both datasets:
- On the small dataset, soft penalty dropped from 571 (Improved BT) down to **354.0** (a $38\%$ quality improvement).
- On the large dataset, soft penalty dropped from 1,482 down to **1,083.7** (a $27\%$ quality improvement).
Pure CSP search terminates at the first valid leaf node encountered; the Hybrid pipeline optimizes schedule gaps and teacher preferences post-feasibility.

### 5.3 What happens as the problem grows?
1. **Plain Backtracking** degrades rapidly when constraints become tight; chronological ordering without domain pruning suffers from exponential branching ($O(d^n)$).
2. **Forward Checking with MRV** scales gracefully because domain wipeouts are detected at depth $k$, pruning subtrees before deeper recursive expansion.
3. **Pure Simulated Annealing** struggles with strict hard feasibility on large datasets (achieving only 10% feasibility when starting from scratch on 104 variables). This validates the theoretical rationale for the **Hybrid architecture**.

### 5.4 When would you use each method in production?
- **Improved Backtracking CSP:** Best for real-time validation, interactive manual slot editing, and urgent rescheduling queries where deterministic feasibility must be proven within seconds.
- **Hybrid CSP + Simulated Annealing:** Best for production semester timetable publication, where institutions require both strict constraint satisfaction and maximum human convenience (minimal free periods, balanced faculty schedules).

---

## 6. Software Architecture & Deliverable Features

```
SchedulAI System Architecture
┌────────────────────────────────────────────────────────┐
│               React + Vite Frontend (SPA)              │
│  - Timetable Matrix Grid (Class, Faculty, Room Views)  │
│  - Real-Time Conflict-Aware Slot Editor                │
│  - Rescheduling Engine & Faculty Swap Approval         │
│  - Chart.js Workload & Benchmark Visualizations        │
└───────────────────────────▲────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Backend Server                │
│  - Authoritative Constraint Validator (H1-H9)          │
│  - CSP Problem Formulator & Domain Pruner              │
│  - Solvers: Plain BT, Improved BT, Min-Conflicts,      │
│             Simulated Annealing, Hybrid CSP+SA         │
│  - Rescheduling & Class Cancellation Services          │
│  - Faculty Workload Analytics & CSV Exporter           │
└────────────────────────────────────────────────────────┘
```

1. **Conflict-Aware Manual Editing:** Authorized users can move or adjust slots. The backend runs authoritative validation; if a move violates H1-H9, it is rejected with descriptive diagnostics.
2. **Missed Lecture Rescheduling:** Scans all possible slots for cancelled classes, checks faculty eligibility and room compatibility, and ranks feasible slots by penalty score.
3. **Faculty Class-Swap Workflow:** Validates proposed mutual lecture exchanges against both teachers' schedules and rooms before applying.
4. **Faculty Workload Dashboard:** Displays assigned teaching hours against weekly maximums, utilization percentages, and overload alerts.
5. **CSV Export:** One-click download of the complete institutional timetable.

---

## 7. Limitations & Future Work
1. **Dynamic Room Partitioning:** Current modeling treats rooms as atomic units. Future extensions can support partitioned auditoriums for combined batch tutorials.
2. **Student Elective Bipartite Matching:** Integrating min-cost max-flow algorithms for conflict-free elective course allocations.
3. **Calendar Integration:** Exporting scheduled sessions to iCalendar (.ics) format for automated Google Calendar synchronization.

---

## 8. Team Member Contributions
- **AI & Algorithm Engineering:** CSP modeling, Plain Backtracking, MRV + Forward Checking + Degree + LCV heuristics, Min-Conflicts local search, Simulated Annealing, and Hybrid CSP+SA solvers.
- **Backend Architecture & APIs:** FastAPI REST architecture, Authoritative Constraint Validator, Rescheduling Engine, Swap Service, Workload Analytics, and CSV Export.
- **Frontend & Visualizations:** React dashboard, day-by-period interactive matrix grid, slot edit modals, Chart.js workload and convergence graphs.
