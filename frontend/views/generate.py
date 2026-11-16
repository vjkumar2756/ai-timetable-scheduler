"""
frontend/views/generate.py
Schedule Generation & Solver Controls View.
"""
import streamlit as st
import plotly.graph_objects as go
from frontend.theme import page_header
from frontend.api_client import APIClient

def render_generate_page():
    page_header(
        title="Generate Institutional Schedule",
        subtitle="Select CSP algorithms, tune heuristic parameters, verify feasibility, and solve"
    )

    # 1. Pre-Run Feasibility Check Card
    ok_feas, feas, _ = APIClient.get_feasibility()
    if ok_feas and feas:
        is_feas = feas.get("feasible", False)
        metrics = feas.get("metrics", {})
        
        st.markdown(
            f"""
            <div class="schedulai-card" style="border-left: 4px solid {'#10b981' if is_feas else '#f43f5e'};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: #ffffff;">Pre-Flight Solvability Analysis</h4>
                    <span class="schedulai-badge badge-{'success' if is_feas else 'danger'}">
                        {'Feasible & Solvable' if is_feas else 'Capacity Infeasible'}
                    </span>
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    {feas.get('summary', '')}
                </div>
                <div style="display: flex; gap: 1.5rem; margin-top: 0.6rem; font-size: 0.78rem; color: #94a3b8;">
                    <div>Curriculum Demand: <b>{metrics.get('total_required_hours', 0)}h</b></div>
                    <div>Usable Room Slots: <b>{metrics.get('total_room_slots', 0)}</b></div>
                    <div>Room Utilization: <b>{metrics.get('room_utilization_pct', 0)}%</b></div>
                    <div>Faculty Utilization: <b>{metrics.get('teacher_utilization_pct', 0)}%</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Algorithm Selector & Parameters Form
    col_algo, col_params = st.columns([1.1, 0.9])

    with col_algo:
        st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
        st.markdown("#### Solver Selection")
        
        algo_choice = st.selectbox(
            "Scheduling Algorithm",
            options=[
                ("improved_backtracking", "Improved Backtracking (MRV + Degree + FC) [Recommended]"),
                ("min_conflicts", "Min-Conflicts Local Search (Iterative Repair + Plateau Escape)"),
                ("plain_backtracking", "Plain Backtracking (Baseline CSP)"),
                ("simulated_annealing", "Simulated Annealing (Stochastic Local Search)"),
                ("hybrid", "Hybrid CSP + SA (Two-Stage Optimal Search)")
            ],
            format_func=lambda x: x[1]
        )[0]

        # Algorithm Explanations
        algo_explanations = {
            "improved_backtracking": (
                "**Improved Backtracking CSP:** Uses Minimum Remaining Values (MRV) to pick the most constrained variable, "
                "Degree heuristic as a tie-breaker, and Forward Checking (FC) to prune domain clashes early. Guarantees finding a "
                "valid solution without exploring redundant branches."
            ),
            "min_conflicts": (
                "**Min-Conflicts Local Search:** Starts with a complete greedy assignment and iteratively repairs conflicting sessions. "
                "Escapes local plateaus using random walk (p=0.08) and random restarts. Exceptional scaling performance on large problem sets."
            ),
            "plain_backtracking": (
                "**Plain Backtracking (Baseline):** Standard recursive depth-first search in static chronological order without heuristics. "
                "Serves as the theoretical baseline to measure speedups gained from MRV and Forward Checking."
            ),
            "simulated_annealing": (
                "**Simulated Annealing:** Probabilistic local search inspired by statistical physics. Accepts worsening moves with Boltzmann probability "
                "exp(-ΔE/T) to escape deep local minima, gradually cooling down."
            ),
            "hybrid": (
                "**Hybrid Two-Stage Solver:** Stage 1 uses CSP Backtracking/Min-Conflicts to find an initial 100% hard-constraint valid schedule. "
                "Stage 2 uses Simulated Annealing to aggressively minimize soft quality penalties without breaking hard constraints."
            )
        }
        st.info(algo_explanations.get(algo_choice, ""))
        st.markdown("</div>", unsafe_allow_html=True)

    with col_params:
        st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
        st.markdown("#### Hyperparameters & Heuristics")
        
        seed = st.number_input("Random Seed (Reproducibility)", min_value=1, max_value=999999, value=42)
        timeout = st.slider("Time Limit (Seconds)", min_value=5.0, max_value=60.0, value=25.0, step=5.0)

        use_mrv = True
        use_degree = True
        use_fc = True
        use_lcv = False
        use_ac3 = False

        if "backtracking" in algo_choice:
            st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-top: 0.5rem;'>Heuristic Toggles</p>", unsafe_allow_html=True)
            use_mrv = st.checkbox("Minimum Remaining Values (MRV)", value=("improved" in algo_choice))
            use_degree = st.checkbox("Degree Heuristic (Tie-Breaker)", value=("improved" in algo_choice))
            use_fc = st.checkbox("Forward Checking (FC)", value=("improved" in algo_choice))
            use_lcv = st.checkbox("Least Constraining Value (LCV)", value=False)
            use_ac3 = st.checkbox("AC-3 Arc Consistency Preprocessing", value=False)

        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Execution Action
    generate_clicked = st.button("🚀 Run Scheduler", type="primary", use_container_width=True)

    if generate_clicked:
        payload = {
            "algorithm": algo_choice,
            "random_seed": int(seed),
            "time_limit_seconds": float(timeout),
            "use_mrv": use_mrv,
            "use_degree": use_degree,
            "use_forward_checking": use_fc,
            "use_lcv": use_lcv,
            "use_ac3": use_ac3
        }

        with st.spinner(f"Running {algo_choice.replace('_', ' ').title()} solver..."):
            ok, res_data, msg = APIClient.generate_schedule(payload)

        st.session_state["last_generation"] = {
            "ok": ok,
            "data": res_data if ok else None,
            "msg": msg
        }

    # Render generation results if available
    last_gen = st.session_state.get("last_generation")
    if last_gen:
        if last_gen.get("ok") and last_gen.get("data"):
            res_data = last_gen["data"]
            msg = last_gen.get("msg", "Success")
            st.success(f"Schedule Generation Complete: {msg}")
            
            # Key Results
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Execution Time", f"{res_data.get('execution_time_seconds', 0.0):.4f} s")
            with m2:
                st.metric("Nodes / Iterations", str(res_data.get("nodes_expanded", res_data.get("iterations", 0))))
            with m3:
                hard_v = res_data.get("hard_violations", 0)
                st.metric("Hard Violations", f"{hard_v} (H1-H9)", delta="-0" if hard_v == 0 else f"+{hard_v}", delta_color="inverse")
            with m4:
                st.metric("Total Cost", str(res_data.get("total_cost", 0)))

            # Convergence Chart for Local Search
            cost_history = res_data.get("cost_history", [])
            if cost_history and len(cost_history) > 1:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("#### Cost Convergence Trajectory")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=cost_history,
                    mode="lines+markers",
                    name="Total Cost",
                    line=dict(color="#6366f1", width=2),
                    marker=dict(size=4)
                ))
                fig.update_layout(
                    paper_bgcolor="#121a30",
                    plot_bgcolor="#121a30",
                    font=dict(color="#f8fafc"),
                    margin=dict(l=40, r=20, t=30, b=40),
                    xaxis=dict(title="Iteration Step", fixedrange=True),
                    yaxis=dict(title="Institutional Cost Function", fixedrange=True),
                    height=320,
                    dragmode=False
                )
                st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            # Link to Timetable View
            def navigate_to_timetable():
                st.session_state["active_tab"] = "timetable"
                st.query_params["tab"] = "timetable"

            # On-Demand Timetable Grid Toggle
            if "show_gen_timetable" not in st.session_state:
                st.session_state["show_gen_timetable"] = False

            col_g1, col_g2 = st.columns([1.5, 1.5])
            with col_g1:
                g_btn_label = "🙈 Hide Generated Timetable" if st.session_state["show_gen_timetable"] else "📅 View Generated Timetable Grid"
                g_btn_type = "secondary" if st.session_state["show_gen_timetable"] else "primary"
                if st.button(g_btn_label, key="btn_toggle_gen_timetable", type=g_btn_type, use_container_width=True):
                    st.session_state["show_gen_timetable"] = not st.session_state["show_gen_timetable"]
                    st.rerun()

            with col_g2:
                st.button(
                    "👉 Open Dedicated Timetable View",
                    key="btn_view_generated_timetable_grid",
                    type="secondary",
                    use_container_width=True,
                    on_click=navigate_to_timetable
                )

            if st.session_state["show_gen_timetable"]:
                from frontend.views.timetable_grid import render_timetable_grid
                render_timetable_grid(embedded=True, key_prefix="gen_")
        else:
            st.error(f"Generation Failed: {last_gen.get('msg', 'Unknown error')}")
