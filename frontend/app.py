"""
frontend/app.py
SchedulAI: AI-Based College Timetable Scheduler — Main Streamlit Application.
Pure Python + Streamlit frontend. Communicates with FastAPI backend over HTTP/JSON.
"""
import streamlit as st
from frontend.theme import apply_theme
from frontend.api_client import APIClient
from frontend.views.dashboard import render_dashboard
from frontend.views.generate import render_generate_page
from frontend.views.timetable_grid import render_timetable_grid
from frontend.views.entities import render_entities_page

# Configure Page Setting
st.set_page_config(
    page_title="SchedulAI — AI College Timetable Scheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Theme State (default dark, persists via query params)
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = st.query_params.get("theme", "dark")

# Apply Dynamic Custom Theme (Dark or Light)
apply_theme(st.session_state["theme_mode"])

# Initialize Session State & Query Param Sync
valid_tabs = ["dashboard", "timetable", "generate", "operations", "workload", "benchmarks", "entities"]
query_tab = st.query_params.get("tab", None)

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = query_tab if query_tab in valid_tabs else "dashboard"

# Keep query params in sync with active tab and theme
st.query_params["tab"] = st.session_state["active_tab"]
st.query_params["theme"] = st.session_state["theme_mode"]

# --- Sidebar ---
with st.sidebar:
    # 1. Brand Logo & Title
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.75rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--border-subtle); margin-bottom: 1.25rem;">
            <div style="width: 38px; height: 38px; background: linear-gradient(135deg, #6366f1, #06b6d4); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 0 15px rgba(99,102,241,0.35);">
                📅
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 0.35rem;">
                    <span style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; color: var(--text-main);">SchedulAI</span>
                    <span class="schedulai-badge badge-primary">CSP Engine</span>
                </div>
                <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: 500;">AI College Scheduler</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Theme Mode Switcher (Dark / Light)
    st.markdown(
        """<div style="font-size: 0.72rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.35rem; letter-spacing: 0.05em;">APPEARANCE / THEME</div>""",
        unsafe_allow_html=True
    )
    current_theme = st.session_state.get("theme_mode", "dark")
    theme_choice = st.segmented_control(
        "Theme Mode",
        options=["🌙 Dark", "☀️ Light"],
        default="☀️ Light" if current_theme == "light" else "🌙 Dark",
        label_visibility="collapsed",
        key="app_theme_mode_switch"
    )
    new_theme = "light" if "Light" in (theme_choice or "") else "dark"
    if new_theme != current_theme:
        st.session_state["theme_mode"] = new_theme
        st.query_params["theme"] = new_theme
        st.rerun()

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # 3. Navigation Items

    nav_items = [
        ("dashboard", "📊 Dashboard"),
        ("timetable", "📅 Timetable Grid"),
        ("generate", "⚙️ Generate Schedule"),
        ("operations", "🔄 Operations & Rescheduling"),
        ("workload", "📈 Workload Analytics"),
        ("benchmarks", "🏆 Algorithm Comparison"),
        ("entities", "🗄️ Manage Entities"),
    ]

    for tab_id, tab_label in nav_items:
        is_active = (st.session_state["active_tab"] == tab_id)
        # Highlight active button
        btn_type = "primary" if is_active else "secondary"
        if st.button(tab_label, key=f"nav_btn_{tab_id}", type=btn_type, use_container_width=True):
            st.session_state["active_tab"] = tab_id
            st.query_params["tab"] = tab_id
            st.rerun()


    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Preset Dataset Loaders Box (Assignment Requirement)
    st.markdown(
        """
        <div style="background: var(--stat-sub-bg, rgba(255,255,255,0.02)); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 0.85rem; margin-top: auto;">
            <div style="font-size: 0.72rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; letter-spacing: 0.05em;">
                DATASET PRESETS
            </div>
        """,
        unsafe_allow_html=True
    )

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("Small (3C)", key="load_preset_small", help="3 Classes, 6 Teachers, 4 Rooms (5d x 6p)", use_container_width=True):
            with st.spinner("Loading Small Preset..."):
                ok, _, msg = APIClient.load_preset("small")
            if ok:
                st.toast("Small Dataset (3 Classes, 6 Teachers) loaded!", icon="✅")
                st.rerun()
            else:
                st.error(msg)

    with d_col2:
        if st.button("Large (8C)", key="load_preset_large", help="8 Classes, 16 Teachers, 8 Rooms (5d x 7p)", use_container_width=True):
            with st.spinner("Loading Large Preset..."):
                ok, _, msg = APIClient.load_preset("large")
            if ok:
                st.toast("Large Dataset (8 Classes, 16 Teachers) loaded!", icon="✅")
                st.rerun()
            else:
                st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Backend Health Status
    ok_health, health_info, _ = APIClient.check_health()
    if ok_health:
        st.markdown(
            """
            <div style="margin-top: 1rem; font-size: 0.72rem; color: #10b981; display: flex; align-items: center; gap: 0.35rem;">
                <span style="font-size: 0.6rem;">🟢</span> Backend API Connected (Port 8000)
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="margin-top: 1rem; font-size: 0.72rem; color: #f43f5e; display: flex; align-items: center; gap: 0.35rem;">
                <span style="font-size: 0.6rem;">🔴</span> Backend Disconnected (Start FastAPI on 8000)
            </div>
            """,
            unsafe_allow_html=True
        )

from frontend.views.operations import render_operations_page
from frontend.views.analytics import render_analytics_page
from frontend.views.benchmarks import render_benchmarks_page

# --- Main App Routing ---
active_tab = st.session_state["active_tab"]

# Global Top Back Navigation Bar for all non-dashboard sub-pages
if active_tab != "dashboard":
    nav_col1, nav_col2 = st.columns([0.24, 0.76])
    with nav_col1:
        if st.button("⬅️ Back to Dashboard", key="global_top_back_btn", help="Return to Academic Operations Dashboard", use_container_width=True):
            st.session_state["active_tab"] = "dashboard"
            st.rerun()
    with nav_col2:
        tab_names = {
            "timetable": "Timetable Grid View",
            "generate": "Generate Schedule",
            "operations": "Operations & Rescheduling",
            "workload": "Faculty Workload Analytics",
            "benchmarks": "Algorithm Comparison & Viva Defense",
            "entities": "Manage Entities"
        }
        current_name = tab_names.get(active_tab, active_tab.title())
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.5rem; font-size: 0.85rem; color: #94a3b8; padding: 0.45rem 0;">
                <span style="color: #64748b;">Current Location:</span>
                <span style="color: #6366f1; font-weight: 600;">🏠 Dashboard</span>
                <span style="color: #64748b;">/</span>
                <span style="color: #ffffff; font-weight: 700;">{current_name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("<hr style='margin: 0.25rem 0 1.25rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

if active_tab == "dashboard":
    render_dashboard()
elif active_tab == "timetable":
    render_timetable_grid()
elif active_tab == "generate":
    render_generate_page()
elif active_tab == "entities":
    render_entities_page()
elif active_tab == "operations":
    render_operations_page()
elif active_tab == "workload":
    render_analytics_page()
elif active_tab == "benchmarks":
    render_benchmarks_page()
