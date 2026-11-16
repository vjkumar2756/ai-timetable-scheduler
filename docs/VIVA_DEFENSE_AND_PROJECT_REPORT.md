# SchedulAI: Project Report Outline & Project Viva Defense Guide
**Course:** B.Tech (2nd Year) Artificial Intelligence / Computer Science & Engineering  
**Project Title:** SchedulAI — Intelligent College Timetable Scheduling System via CSP & Metaheuristics  
**Components:** Pure Python Core Algorithms (`core/`), FastAPI REST Backend (`backend/app/`), Streamlit UI (`frontend/`)

---

## 1. Executive Project Abstract

The automated university course timetabling problem is an **NP-complete combinatorial optimization problem** subject to severe multidimensional resource constraints. In a typical engineering institution, conflicting faculty availability, specialized laboratory requirements, student cohort curriculum quotas, and physical room capacities create an exponential search space ($|\mathcal{D}|^{|\mathcal{X}|}$) where chronological depth-first search exhibits severe thrashing.

**SchedulAI** models the institutional scheduling challenge as a formal **Constraint Satisfaction Problem (CSP)** with weighted soft-optimization objectives. We implemented, benchmarked, and verified five distinct algorithmic approaches:
1. **Plain Backtracking (Baseline):** Exhaustive chronological DFS.
2. **Improved Backtracking:** Heuristic variable ordering (MRV + Degree), domain pruning (Forward Checking), and value ordering (LCV).
3. **Min-Conflicts Local Search:** Iterative repair heuristic with random-walk ($p=0.08$) plateau escape.
4. **Simulated Annealing (+6 Bonus Marks):** Stochastic optimization exploring non-improving neighborhood states via the Metropolis-Hastings criterion ($P = e^{-\Delta E / T}$).
5. **Hybrid CSP + SA (+6 Bonus Marks):** Decoupled two-stage metaheuristic combining guaranteed CSP hard feasibility with metaheuristic soft-constraint polishing.

All solvers and interactive operational features are validated against a single authoritative constraint engine enforcing **9 Hard Constraints ($H_1\text{--}H_9$)** and **5 Soft Constraints ($S_1\text{--}S_5$)**. The system was verified across both synthetic datasets and independently cross-checked against the standard third-party `python-constraint` library with 100% satisfiability agreement.

---

## 2. Formal Mathematical Formulation

### 2.1 Variables and Domains
Let $\mathcal{C}$ be the set of student class batches, $\mathcal{S}$ the set of curriculum subjects, $\mathcal{T}$ the set of faculty members, and $\mathcal{R}$ the set of rooms.
Each required lecture instance is modeled as a discrete decision variable:
$$X_{c, s, i} \quad \text{where } c \in \mathcal{C},\, s \in \mathcal{S},\, i \in \{1, \dots, \lceil \text{weekly\_hours}(c, s) / \text{duration}(s) \rceil\}$$

A value assigned to variable $X$ is a 4-tuple:
$$v = \langle \text{day}, \text{period}, \text{room}, \text{teacher} \rangle \in \text{Days} \times \text{Periods} \times \mathcal{R} \times \mathcal{T}$$

### 2.2 Hard Constraints ($H_1\text{--}H_9$ — Strictly Required)
A schedule is feasible if and only if total hard violations $H = 0$:

1. **$H_1$ — Teacher Clash Avoidance:**  
   No faculty member can instruct more than one lecture simultaneously:
   $$\forall X_a, X_b \, (a \ne b): \text{teacher}(X_a) = \text{teacher}(X_b) \implies \text{Slots}(X_a) \cap \text{Slots}(X_b) = \emptyset$$

2. **$H_2$ — Class Cohort Clash Avoidance:**  
   No student cohort can attend two concurrent sessions:
   $$\forall X_a, X_b \, (a \ne b): \text{class}(X_a) = \text{class}(X_b) \implies \text{Slots}(X_a) \cap \text{Slots}(X_b) = \emptyset$$

3. **$H_3$ — Room Occupancy Clash Avoidance:**  
   No physical room can host multiple simultaneous sessions:
   $$\forall X_a, X_b \, (a \ne b): \text{room}(X_a) = \text{room}(X_b) \implies \text{Slots}(X_a) \cap \text{Slots}(X_b) = \emptyset$$

4. **$H_4$ — Room Capacity Compliance:**  
   A room's seating capacity must accommodate the class strength:
   $$\forall X: \text{capacity}(\text{room}(X)) \ge \text{strength}(\text{class}(X))$$

5. **$H_5$ — Room Type & Laboratory Matching:**  
   Practical labs require lab-type facilities; theory lectures require classrooms:
   $$\forall X: \text{type}(\text{subject}(X)) = \text{lab} \iff \text{type}(\text{room}(X)) = \text{lab}$$

6. **$H_6$ — Teacher Availability Windows:**  
   No faculty member is assigned during declared unavailable periods:
   $$\forall X: \langle \text{day}(X), \text{period}(X) \rangle \notin \text{unavailable\_slots}(\text{teacher}(X))$$

7. **$H_7$ — Curriculum Quota Preservation:**  
   Every subject's required weekly contact hours are scheduled exactly:
   $$\sum_{X \in \text{Sessions}(c, s)} \text{duration}(X) = \text{weekly\_hours}(c, s)$$

8. **$H_8$ — Faculty Maximum Workload Limits:**  
   No instructor exceeds their contractual weekly teaching load:
   $$\forall t \in \mathcal{T}: \sum_{X: \text{teacher}(X) = t} \text{duration}(X) \le \text{max\_weekly\_load}(t)$$

9. **$H_9$ — Institutional Lunch Break Protection:**  
   No session overlaps with the cohort's designated lunch break:
   $$\forall X: \text{lunch\_period}(\text{class}(X)) \notin \text{Periods}(X)$$

### 2.3 Soft Constraints ($S_1\text{--}S_5$ — Penalty Optimization)
Soft penalty function $S$:
$$S = w_1 S_1 + w_2 S_2 + w_3 S_3 + w_4 S_4 + w_5 S_5$$
- **$S_1$ — Free Period Gaps ($w_1 = 5$):** Minimizes idle windows between lectures on student class days.
- **$S_2$ — Daily Subject Repeat ($w_2 = 15$):** Distributes lectures across days rather than grouping on a single day.
- **$S_3$ — Lab Continuity ($w_3 = 20$):** Multi-period lab sessions must run consecutively. Guaranteed by modeling labs as atomic blocks.
- **$S_4$ — Teacher Slot Preferences ($w_4 = 10$):** Penalizes assigning teachers to non-preferred hours.
- **$S_5$ — Excessive Consecutive Teaching ($w_5 = 12$):** Penalizes assigning $>2$ consecutive lecture periods to an instructor.

Total Cost Function:
$$\text{Cost} = 1000 \times H + S$$

---

## 3. High-Yield Project Viva Defense Q&A

### Q1: Why does Plain Chronological Backtracking fail or thrash on large timetable graphs?
> **Answer:** Plain backtracking selects variables and values in arbitrary static order. When an early assignment introduces an unavoidable clash deeper in the search tree, plain DFS continues exhaustively searching all downstream subtrees before finally backtracking to the root mistake ($O(d^n)$ complexity). It possesses zero "fail-first" intelligence and performs no domain pruning.

### Q2: How do MRV and the Degree Heuristic speed up CSP search?
> **Answer:** 
> - **Minimum Remaining Values (MRV):** Implements the *fail-first principle*. By picking the variable with the smallest legal domain, if an assignment is doomed to fail, it fails immediately at the current level rather than after branching down thousands of leaf paths.
> - **Degree Heuristic:** Serves as an effective tie-breaker when multiple variables have identical domain sizes. It selects the variable with the highest number of constraints on remaining unassigned variables, actively reducing future branching factor.

### Q3: How does Forward Checking prevent thrashing and how is domain restoration handled?
> **Answer:** Whenever variable $X$ is assigned value $v$, Forward Checking immediately filters value choices from the domains of all unassigned variables that share a constraint with $X$ (same teacher, same class, same room). If any unassigned variable's domain becomes empty ($\mathcal{D}_Y = \emptyset$), the assignment is aborted immediately. On backtrack, a domain stack restores the pruned values, preserving mathematical completeness.

### Q4: Why can Min-Conflicts get stuck on local optima, and how did your team resolve this?
> **Answer:** Min-Conflicts is a greedy local search heuristic that moves one conflicted variable to the value minimizing total conflicts. On dense constraint networks with high room occupancy ($>80\%$), moving a variable often introduces another conflict elsewhere, creating a cycle or plateau where all neighboring states have equal cost. We addressed this by integrating **random-walk transitions ($p = 0.08$)** (allowing a random legal move with probability 8%) and **random restarts**, enabling reliable escape from local minima.

### Q5: What is the Metropolis-Hastings criterion in Simulated Annealing, and why is the Hybrid CSP+SA approach superior?
> **Answer:** 
> - **Metropolis-Hastings Criterion:** When exploring a neighbor state with cost change $\Delta E$, downhill moves ($\Delta E < 0$) are always accepted. Uphill moves ($\Delta E > 0$) are accepted probabilistically with:
>   $$P(\text{accept}) = \exp\left(-\frac{\Delta E}{T}\right)$$
>   As temperature $T$ cools geometrically ($T_{k+1} = \alpha T_k$), the solver shifts from broad exploration to fine greedy exploitation.
> - **Why Hybrid is Superior:** Pure backtracking stops as soon as $H=0$ with poor soft penalty scores ($>1,400$). Pure SA from random initialization can spend thousands of iterations struggling to resolve hard constraints. Our **two-stage Hybrid CSP+SA** uses CSP Backtracking to guarantee $H=0$ in milliseconds, then uses SA with hard-constraint preservation to polish soft penalties by $>30\%$.

### Q6: How does SchedulAI guarantee that 2-hour practical labs are never split?
> **Answer:** Rather than modeling a 2-hour lab as two separate 1-hour variables that must be synchronized via binary distance constraints ($|p_1 - p_2| = 1$), SchedulAI models the lab as an **atomic block variable** with `duration=2`. Its domain is pruned upfront so it can only be placed in periods $p \le (\text{periods\_per\_day} - 1)$ where neither $p$ nor $p+1$ overlaps with lunch. This eliminates domain fragmentation and satisfies constraint $S_3$ by construction.

### Q7: How does the live manual editing and missed-lecture rescheduling engine prevent invalid schedules?
> **Answer:** Every proposed manual relocation, class cancellation, or mutual teacher swap is passed through the centralized `ConstraintValidator`. The engine creates a virtual simulated assignment in-memory, executes all 9 hard constraint checks, and returns exact clash explanations if violated. Only verified collision-free moves are committed to the data store.

---

## 4. Evaluator 5-Minute Demonstration Script

| Time | Action | What to Explain to Professor / Examiner |
| :---: | :--- | :--- |
| **0:00 – 1:00** | **System Overview & Dashboard** | Show the Streamlit dark navy dashboard. Highlight live KPI tiles (Total Teaching Hours, Room Utilization, Faculty Capacity, Constraint Compliance). Explain the two-tier architecture: pure Python algorithmic core (`core/`), FastAPI backend (`backend/app/`), and Streamlit UI. |
| **1:00 – 2:00** | **Solver Generation & Heuristics** | Navigate to **Generate Schedule**. Run **Improved Backtracking (MRV + FC)** on the Small Dataset. Show that it finds a 100% collision-free schedule in $<0.15$s. Then select **Hybrid CSP + SA** and demonstrate how soft penalty is reduced from baseline. |
| **2:00 – 3:00** | **Multi-Matrix Timetable Grid** | Open **Timetable Grid**. Switch between **Class View**, **Faculty View**, and **Room View**. Point out: shaded lunch periods ($H_9$), atomic consecutive lab blocks ($S_3$), and export buttons for CSV, Excel (`.xlsx`), and PDF. |
| **3:00 – 4:00** | **Operations: Cancellations & Rescheduling** | Open **Operations & Rescheduling**. Cancel a lecture session due to faculty leave; show the in-app notification. Go to **Missed Lecture Rescheduling**, select the cancelled session, and click "Search Collision-Free Slots". Show the top ranked recommendations and book one. |
| **4:00 – 5:00** | **Benchmarks & Third-Party Cross-Check** | Open **Algorithm Comparison**. Show the logarithmic execution time chart and Min-Conflicts convergence curve. Mention that [`experiments/cross_check.py`](file:///home/vijay/Desktop/ai%20system/ai-timetable-scheduler/experiments/cross_check.py) was run against `python-constraint` with 100% mathematical agreement. Show that **73/73 pytest tests pass**. |
