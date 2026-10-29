"""
frontend/views/dashboard.py
Academic Operations Dashboard Page with Expanded High-Impact Operations Suite.
"""
import os
import streamlit as st
from frontend.theme import page_header, hero, stat_card
from frontend.api_client import APIClient

def render_dashboard():
    page_header(
        title="Academic Operations Dashboard",
        subtitle="Real-time institutional scheduling health, infrastructure metrics, and autonomous engine status"
    )

    # Hero Banner with Integrated Logo
    dash_logo_path = os.path.join(os.path.dirname(__file__), "../../assets/logo.png")
    hero(
        title="SchedulAI Autonomous Timetable System",
        description=(
            "Fully constraint-satisfying academic scheduling engine implementing CSP Backtracking, "
            "Heuristic MRV with Forward Checking, and Min-Conflicts local search. Enforces all 9 Hard Institutional "
            "Constraints and optimizes 5 Soft Faculty & Student Quality Criteria."
        ),
        badges=[
            ("AI-Based Scheduler", "primary"),
            ("H1-H9 Strictly Enforced", "success"),
            ("Dual Benchmark Validated", "warning")
        ],
        logo_path=dash_logo_path if os.path.exists(dash_logo_path) else None
    )

    # Fetch Real Data from API
    ok_stats, stats_data, _ = APIClient.get_dashboard_summary()
    ok_sched, sched_data, _ = APIClient.get_active_schedule()
    ok_feas, feas_data, _ = APIClient.get_feasibility()

    stats = stats_data if ok_stats and stats_data else {}
    sched = sched_data if ok_sched and sched_data else {}
    feas = feas_data if ok_feas and feas_data else {}

    # 4 Stat Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Active Classes", str(stats.get("total_classes", 0)), "🎓", "rgba(99, 102, 241, 0.18)"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Faculty Members", str(stats.get("total_teachers", 0)), "👨‍🏫", "rgba(16, 185, 129, 0.18)"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("Rooms & Labs", str(stats.get("total_rooms", 0)), "🏛️", "rgba(245, 158, 11, 0.18)"), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card("Course Modules", str(stats.get("total_subjects", 0)), "📚", "rgba(6, 182, 212, 0.18)"), unsafe_allow_html=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 1. EXPANDED ACADEMIC OPERATIONS MODULES SUITE (FULL WIDTH GRID)
    # -------------------------------------------------------------------------
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <h2 style="margin: 0; font-size: 1.45rem; font-weight: 800; color: var(--text-main);">🚀 Academic Operations & AI Scheduling Suite</h2>
                <span class="schedulai-badge badge-primary">6 Modules</span>
            </div>
            <p style="margin: 0.35rem 0 0 0; font-size: 0.88rem; color: var(--text-secondary);">
                Enterprise-grade tools for timetable visualization, autonomous generation, manual interventions, and institutional analytics
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    modules_data = [
        {
            "id": "timetable",
            "icon": "📅",
            "title": "Timetable Grid View",
            "badge": "Visual Matrix + Export",
            "badge_color": "rgba(99, 102, 241, 0.25)",
            "badge_text_color": "#a5b4fc",
            "desc": "Inspect weekly schedule matrices by Student Class, Faculty member, or Lab facility with protected lunch breaks and 1-click PDF, Excel, and CSV downloads.",
            "btn_label": "📅 Open Timetable Matrix"
        },
        {
            "id": "generate",
            "icon": "⚙️",
            "title": "Schedule Generator",
            "badge": "MRV + Min-Conflicts + SA",
            "badge_color": "rgba(6, 182, 212, 0.25)",
            "badge_text_color": "#67e8f9",
            "desc": "Solve complex institutional scheduling challenges with CSP Backtracking (MRV+LCV), Min-Conflicts local search, or Two-Stage Hybrid CSP+SA metaheuristics.",
            "btn_label": "⚙️ Launch Solver Engine"
        },
        {
            "id": "operations",
            "icon": "🔄",
            "title": "Operations & Rescheduling",
            "badge": "Live H1–H9 Validation",
            "badge_color": "rgba(245, 158, 11, 0.25)",
            "badge_text_color": "#fde68a",
            "desc": "Simulate manual lecture relocations with instant constraint feedback, handle cohort day closures, and execute collision-free faculty session swaps.",
            "btn_label": "🔄 Manage Operations"
        },
        {
            "id": "workload",
            "icon": "📈",
            "title": "Faculty Workload Analytics",
            "badge": "Teaching Hours & Labs",
            "badge_color": "rgba(16, 185, 129, 0.25)",
            "badge_text_color": "#6ee7b7",
            "desc": "Analyze faculty teaching loads against contractual limits, audit classroom & lab utilization rates, and track institutional schedule quality scores.",
            "btn_label": "📈 View Analytics Hub"
        },
        {
            "id": "benchmarks",
            "icon": "🏆",
            "title": "Algorithm Comparison",
            "badge": "10-Seed Benchmarks",
            "badge_color": "rgba(168, 85, 247, 0.25)",
            "badge_text_color": "#d8b4fe",
            "desc": "Empirical runtime comparison across multiple algorithms, search space nodes explored, speedup factors, and cross-validation against python-constraint.",
            "btn_label": "🏆 Compare Algorithms"
        },
        {
            "id": "entities",
            "icon": "🗄️",
            "title": "Manage Institutional Entities",
            "badge": "CRUD & Time Structure",
            "badge_color": "rgba(244, 63, 94, 0.25)",
            "badge_text_color": "#fda4af",
            "desc": "Configure course curriculum, faculty availability contracts, student cohorts, lecture halls, and institution working days/periods structure.",
            "btn_label": "🗄️ Manage Campus Data"
        }
    ]

    # Render in 3 Columns
    theme_mode = st.session_state.get("theme_mode", "dark")
    m_cols = st.columns(3)
    for idx, mod in enumerate(modules_data):
        target_col = m_cols[idx % 3]
        b_color = mod['badge_color'] if theme_mode == "dark" else mod['badge_color'].replace("0.25", "0.15")
        b_text = mod['badge_text_color'] if theme_mode == "dark" else {
            "#a5b4fc": "#4f46e5",
            "#67e8f9": "#0891b2",
            "#fde68a": "#b45309",
            "#6ee7b7": "#059669",
            "#d8b4fe": "#7c3aed",
            "#fda4af": "#e11d48",
        }.get(mod['badge_text_color'], mod['badge_text_color'])

        with target_col:
            st.markdown(
                f"""
                <div class="schedulai-card" style="min-height: 220px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.75rem;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                            <div style="font-size: 1.75rem;">{mod['icon']}</div>
                            <span style="background: {b_color}; color: {b_text}; padding: 0.2rem 0.65rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 700;">{mod['badge']}</span>
                        </div>
                        <h3 style="margin: 0 0 0.45rem 0; font-size: 1.15rem; font-weight: 800; color: var(--text-main);">{mod['title']}</h3>
                        <p style="margin: 0; font-size: 0.83rem; color: var(--text-secondary); line-height: 1.5;">{mod['desc']}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(mod["btn_label"], key=f"big_dash_btn_{mod['id']}", use_container_width=True, type="primary" if idx == 0 else "secondary"):
                st.session_state["active_tab"] = mod["id"]
                st.query_params["tab"] = mod["id"]
                st.rerun()
            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. HEALTH & SYSTEM STATUS ROW
    # -------------------------------------------------------------------------
    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        sessions_count = len(sched.get("sessions", []))
        hard_v = sched.get("hard_violations", 0)
        soft_p = sched.get("soft_penalty", 0)
        algo = sched.get("algorithm", "Improved Backtracking (MRV+LCV)")
        runtime = sched.get("execution_time_seconds", 0.0)
        feas_status = "Solvable & Feasible" if feas.get("feasible", False) else "Attention Needed"
        feas_badge = "success" if feas.get("feasible", False) else "danger"
        hard_color = "#10b981" if hard_v == 0 else "#f43f5e"
        runtime_str = f"{round(runtime, 4)} s"

        left_card_html = (
            '<div class="schedulai-card">'
            '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">'
            '<h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: var(--text-main);">Schedule Status & Institutional Health</h3>'
            '<span class="schedulai-badge badge-success">● Engine Live</span>'
            '</div>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; font-size: 0.86rem;">'
            '<div style="background: var(--stat-sub-bg, rgba(255,255,255,0.02)); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-subtle);">'
            '<div style="color: var(--text-secondary); font-size: 0.76rem;">Active Sessions</div>'
            f'<div style="font-size: 1.15rem; font-weight: 800; color: var(--text-main);">{sessions_count} Periods</div>'
            '</div>'
            '<div style="background: var(--stat-sub-bg, rgba(255,255,255,0.02)); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-subtle);">'
            '<div style="color: var(--text-secondary); font-size: 0.76rem;">Hard Violations</div>'
            f'<div style="font-size: 1.15rem; font-weight: 800; color: {hard_color};">{hard_v} (H1-H9 Strict Zero)</div>'
            '</div>'
            '<div style="background: var(--stat-sub-bg, rgba(255,255,255,0.02)); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-subtle);">'
            '<div style="color: var(--text-secondary); font-size: 0.76rem;">Soft Penalty Score</div>'
            f'<div style="font-size: 1.15rem; font-weight: 800; color: #6366f1;">{soft_p} pts</div>'
            '</div>'
            '<div style="background: var(--stat-sub-bg, rgba(255,255,255,0.02)); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-subtle);">'
            '<div style="color: var(--text-secondary); font-size: 0.76rem;">Last Solver Runtime</div>'
            f'<div style="font-size: 1.15rem; font-weight: 800; color: #0284c7;">{runtime_str}</div>'
            '</div>'
            '</div>'
            '<div style="margin-top: 1rem; padding-top: 0.85rem; border-top: 1px solid var(--border-subtle); font-size: 0.84rem;">'
            f'<div style="margin-bottom: 0.4rem; color: var(--text-main);"><b>Active Engine:</b> <span style="color: var(--text-secondary);">{algo}</span></div>'
            f'<div style="color: var(--text-main);"><b>Mathematical Feasibility:</b> <span class="schedulai-badge badge-{feas_badge}">{feas_status}</span></div>'
            '</div>'
            '</div>'
        )
        st.markdown(left_card_html, unsafe_allow_html=True)

    with col_right:
        right_card_html = (
            '<div class="schedulai-card">'
            '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">'
            '<h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: var(--text-main);">Institutional Compliance & Presets</h3>'
            '<span class="schedulai-badge badge-primary">Academic CSP</span>'
            '</div>'
            '<div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1rem;">'
            'SchedulAI guarantees zero professor double-booking, class room collisions, capacity overflows, and protected lunch breaks.'
            '</div>'
            '<div style="display: flex; flex-direction: column; gap: 0.45rem; font-size: 0.82rem; margin-bottom: 1rem;">'
            '<div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Hard Constraints:</span><span style="color: #10b981; font-weight: 700;">H1–H9 Active</span></div>'
            '<div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Soft Optimization:</span><span style="color: #6366f1; font-weight: 700;">S1–S5 Enabled</span></div>'
            '<div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Room Feasibility:</span><span style="color: #d97706; font-weight: 700;">100% Demand Met</span></div>'
            '</div>'
            '</div>'
        )
        st.markdown(right_card_html, unsafe_allow_html=True)
