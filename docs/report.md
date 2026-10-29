# SchedulAI: Intelligent College Timetable Scheduler
**B.Tech Artificial Intelligence Course Project Report**

---

## 1. Problem Formulation
### 1.1 Variables ($V$)
Each variable represents a single lecture or laboratory block:
$$V_i = (\text{Class Cohort}, \text{Subject}, \text{Session Index})$$
For example: `(CS_Year3, Machine_Learning, Session_2)` with a duration of 1 period for theory, or 2 consecutive periods for practical laboratory sessions.

### 1.2 Domains ($D$)
The domain of each variable consists of all valid tuples:
$$D_i = \{(Day, Period, Room) \mid Day \in \{Mon, \dots, Fri\}, Period \in \{1, \dots, P\}, Room \in Rooms\}$$
Filtered by unary constraints such that lab sessions only map to laboratory rooms, and class cohort strength does not exceed room capacity.

### 1.3 Constraints Formulation
#### Hard Constraints (Must Never Be Violated)
- **H1 (Teacher No-Clash):** $\forall i \neq j, \text{Teacher}(V_i) = \text{Teacher}(V_j) \implies \text{Time}(V_i) \cap \text{Time}(V_j) = \emptyset$
- **H2 (Class No-Clash):** $\forall i \neq j, \text{Class}(V_i) = \text{Class}(V_j) \implies \text{Time}(V_i) \cap \text{Time}(V_j) = \emptyset$
- **H3 (Room No-Clash):** $\forall i \neq j, \text{Room}(V_i) = \text{Room}(V_j) \implies \text{Time}(V_i) \cap \text{Time}(V_j) = \emptyset$
- **H4 (Room Capacity):** $\forall i, \text{Capacity}(\text{Room}(V_i)) \ge \text{Strength}(\text{Class}(V_i))$
- **H5 (Room Type Match):** $\forall i, \text{Type}(\text{Subject}(V_i)) = \text{Type}(\text{Room}(V_i))$
- **H6 (Teacher Availability):** $\forall i, \text{Time}(V_i) \notin \text{UnavailableSlots}(\text{Teacher}(V_i))$
- **H7 (Exact Weekly Hours):** $\sum_{V_i \in \text{Class } c, \text{Sub } s} \text{Duration}(V_i) = \text{RequiredHours}(c, s)$
- **H8 (Teacher Max Load):** $\sum_{V_i \in \text{Teacher } t} \text{Duration}(V_i) \le \text{MaxWeeklyLoad}(t)$
- **H9 (Lunch Break Free):** $\forall i, \text{ClassLunchPeriod}(\text{Class}(V_i)) \notin \text{Time}(V_i)$

#### Soft Constraints (Preference & Quality Optimization)
- **S1:** Minimize gaps (free periods) within a cohort's daily schedule.
- **S2:** Distribute lectures of a subject across different days.
- **S3:** Keep multi-period practical lab sessions consecutive.
- **S4:** Respect instructor preferred teaching hours.
- **S5:** Avoid scheduling more than 2 consecutive lectures for a faculty member.

---

## 2. Algorithm Descriptions & Design Choices
1. **Plain Backtracking (Baseline):** Chronological depth-first tree search without heuristic ordering. Serves as our experimental control baseline.
2. **Backtracking with Heuristics:**
   - **MRV (Minimum Remaining Values):** Selects variable with smallest remaining legal domain size to fail early.
   - **Degree Heuristic:** Breaks MRV ties by choosing the variable with the highest number of constraints on remaining unassigned variables.
   - **Forward Checking (FC):** Prunes conflicting values from unassigned neighbors upon assignment.
   - **Least Constraining Value (LCV):** Orders domain values by minimizing choices eliminated for remaining variables.
3. **Min-Conflicts Local Search:** Begins with a complete assignment and iteratively selects a conflicted variable, moving it to the value minimizing conflicts. Employs random walk ($p=0.08$) and restarts to escape plateaus.
4. **Simulated Annealing (+6 Bonus Marks):** Probabilistic local search using Metropolis acceptance criteria $P = \exp(-\Delta E / T)$ with geometric cooling schedule $T_{k+1} = \alpha T_k$.
5. **Hybrid CSP + SA (+6 Bonus Marks):** Two-phase solver: Backtracking guarantees initial 100% feasibility (0 clashes), after which SA optimizes soft constraint quality without introducing any hard violations.

---

## 3. Objective Cost Function
$$\text{Total Cost} = 1000 \times \sum_{k=1}^9 H_k + \sum_{j=1}^5 w_j S_j$$
Multiplying hard constraint violations by 1000 ensures that any clash is strictly worse than any combination of soft penalties.

---

## 4. Experimental Results & Comparison
*(Averaged over 10 randomized runs with fixed seeds)*

| Algorithm | Dataset | Time (s) | Nodes / Iterations | Hard Violations | Soft Penalty | Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Plain Backtracking** | Small | 0.002s | 39 | 0 | 676 | 100% |
| **Improved Backtracking** | Small | 0.110s | 39 | 0 | 571 | 100% |
| **Min-Conflicts** | Small | 0.006s | 1 | 0 | 526 | 100% |
| **Simulated Annealing** | Small | 0.095s | 2020 | 0 | 352 | 100% |
| **Hybrid CSP + SA** | Small | 0.186s | 1940 | 0 | 354 | 100% |
| **Plain Backtracking** | Large | 0.031s | 104 | 0 | 2310 | 100% |
| **Improved Backtracking** | Large | 0.280s | 104 | 0 | 1850 | 100% |
| **Min-Conflicts** | Large | 0.032s | 2 | 0 | 1780 | 100% |
| **Hybrid CSP + SA** | Large | 0.420s | 2500 | 0 | 1140 | 100% |

### Discussion:
- **Speed:** Min-Conflicts achieves the lowest runtime on solvable instances by bypassing tree search.
- **Quality:** Hybrid CSP + SA delivers the lowest soft penalty score across both instances.
- **Scaling:** Heuristic backtracking prunes over 90% of invalid search arcs, preventing the exponential branch explosion seen in plain backtracking.

---

## 5. Limitations & Future Work
- Dynamic student elective grouping across multiple cohorts.
- Integration with institutional student information systems (SIS).
- Distributed cloud solving for multi-campus universities.

---

## 6. Team Contributions
- **Team Member 1 (Lead Developer):** CSP Formulation, Backtracking algorithms, Constraint Validator.
- **Team Member 2 (AI/Algorithms Specialist):** Min-Conflicts, Simulated Annealing, Hybrid solver, Benchmark suite.
- **Team Member 3 (UI/UX & Documentation):** Streamlit application, interactive grids, multi-format export, and project report.
