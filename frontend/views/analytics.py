"""
frontend/views/analytics.py
Faculty Workload, Facility Utilization, and Constraint Compliance Analytics View.
- Faculty Teaching Load monitoring (H8 constraint enforcement).
- Room & Laboratory capacity utilization.
- Soft constraint distribution (S1 - S5 penalties).
- Interactive Plotly visual charts and institutional health indicators.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.theme import page_header, stat_card
from frontend.api_client import APIClient

def render_analytics_page():
    page_header(
        title="Faculty Workload & Institutional Analytics",
        subtitle="Comprehensive capacity utilization, contractual load monitoring (H8), room usage heatmaps, and soft constraint compliance (S1–S5)"
    )

    # 1. Fetch live analytics from backend
    ok_wl, workload_data, _ = APIClient.get_workload_analytics()
    ok_rm, room_data, _ = APIClient.get_room_analytics()
    ok_ql, quality_data, _ = APIClient.get_quality_analytics()
    ok_ov, overview_data, _ = APIClient.get_dashboard_summary()

    teachers = workload_data if (ok_wl and workload_data) else []
    rooms = room_data if (ok_rm and room_data) else []
    quality = quality_data if (ok_ql and quality_data) else {}
    overview = overview_data if (ok_ov and overview_data) else {}

    # 2. Executive KPI Header Tiles
    avg_teacher_util = 0.0
    if teachers:
        avg_teacher_util = round(sum(t.get("utilization_percentage", 0) for t in teachers) / len(teachers), 1)

    avg_room_util = 0.0
    if rooms:
        avg_room_util = round(sum(r.get("utilization_percentage", 0) for r in rooms) / len(rooms), 1)

    comp_score = quality.get("compliance_score", 100.0)
    scheduled_hours = overview.get("total_teaching_hours", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Total Teaching Load", f"{scheduled_hours} hrs", "⏱️", "rgba(99, 102, 241, 0.18)", subtext="Active weekly sessions"), unsafe_allow_html=True)
    with c2:
        badge_cls = "rgba(16, 185, 129, 0.18)" if avg_teacher_util <= 85.0 else "rgba(245, 158, 11, 0.18)"
        st.markdown(stat_card("Avg Faculty Load", f"{avg_teacher_util}%", "👨‍🏫", badge_cls, subtext="Contractual capacity"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card("Avg Facility Usage", f"{avg_room_util}%", "🏛️", "rgba(56, 189, 248, 0.18)", subtext="Rooms & specialized labs"), unsafe_allow_html=True)
    with c4:
        q_badge = "rgba(16, 185, 129, 0.18)" if comp_score >= 80.0 else "rgba(245, 158, 11, 0.18)"
        st.markdown(stat_card("Schedule Quality", f"{comp_score}%", "🎯", q_badge, subtext="S1–S5 optimization index"), unsafe_allow_html=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # Check for Overloaded Teachers (H8 Violation Alert)
    overloaded_teachers = [t for t in teachers if t.get("is_overloaded")]
    if overloaded_teachers:
        st.error(f"⚠️ Critical Overload Alert (H8 Violation): {len(overloaded_teachers)} instructor(s) exceed their maximum contractual load!")
        for ot in overloaded_teachers:
            st.markdown(f"- 🛑 **{ot['teacher_name']}**: Assigned **{ot['assigned_hours']}h** (Contractual Limit: **{ot['max_weekly_load']}h**)")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Tabs for analytics categories
    tabs = st.tabs([
        "👨‍🏫 Faculty Teaching Loads (H8)",
        "🏛️ Room & Lab Utilization",
        "🎯 Constraint Quality & Soft Penalties (S1–S5)"
    ])

    # =========================================================================
    # TAB 1: FACULTY TEACHING LOADS (H8)
    # =========================================================================
    with tabs[0]:
        st.markdown("#### Faculty Workload & Contractual Capacity Analysis")
        st.write("Monitors weekly assigned teaching hours against each instructor's contractual maximum load limit ($H_8$).")

        if not teachers:
            st.info("No faculty data available. Load a dataset to display workload analytics.")
        else:
            df_teachers = pd.DataFrame(teachers)

            # Interactive Plotly Bar Chart: Assigned Hours vs Max Weekly Load
            fig_wl = go.Figure()
            fig_wl.add_trace(go.Bar(
                x=df_teachers["teacher_name"],
                y=df_teachers["assigned_hours"],
                name="Assigned Hours",
                marker_color="#6366f1",
                text=df_teachers["assigned_hours"].apply(lambda h: f"{h}h"),
                textposition="auto"
            ))
            fig_wl.add_trace(go.Bar(
                x=df_teachers["teacher_name"],
                y=df_teachers["max_weekly_load"],
                name="Max Weekly Load Limit (H8)",
                marker_color="rgba(255,255,255,0.15)",
                text=df_teachers["max_weekly_load"].apply(lambda h: f"Max: {h}h"),
                textposition="auto"
            ))

            fig_wl.update_layout(
                barmode="group",
                plot_bgcolor="#121a30",
                paper_bgcolor="#121a30",
                font=dict(color="#cbd5e1", family="Inter, sans-serif"),
                margin=dict(l=20, r=20, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickangle=-25),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Weekly Hours")
            )
            st.plotly_chart(fig_wl, use_container_width=True)

            # Faculty Workload Table
            st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
            st.markdown("##### Detailed Faculty Capacity Breakdown")

            t_table = []
            for t in teachers:
                subjects_str = ", ".join(f"{sub}: {hrs}h" for sub, hrs in t.get("subject_distribution", {}).items()) or "None"
                status_str = "🛑 Overloaded" if t.get("is_overloaded") else ("⚡ Full" if t.get("remaining_capacity") == 0 else f"{t.get('remaining_capacity')}h left")
                t_table.append({
                    "Faculty Name": t.get("teacher_name"),
                    "Assigned": f"{t.get('assigned_hours')}h",
                    "Max Load": f"{t.get('max_weekly_load')}h",
                    "Utilization": f"{t.get('utilization_percentage')}%",
                    "Sessions": t.get("session_count"),
                    "Available Capacity": status_str,
                    "Course Distribution": subjects_str
                })
            st.dataframe(pd.DataFrame(t_table), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: ROOM & LABORATORY FACILITY UTILIZATION
    # =========================================================================
    with tabs[1]:
        st.markdown("#### Facility & Laboratory Capacity Utilization")
        st.write("Analyzes the scheduling density across classrooms and specialized laboratories relative to total weekly slots.")

        if not rooms:
            st.info("No room data available. Load a dataset to display facility utilization.")
        else:
            df_rooms = pd.DataFrame(rooms)

            col_chart1, col_chart2 = st.columns([1.2, 0.8])

            with col_chart1:
                # Plotly Horizontal Bar Chart
                fig_rm = px.bar(
                    df_rooms,
                    x="utilization_percentage",
                    y="room_name",
                    orientation="h",
                    color="type",
                    color_discrete_map={"classroom": "#38bdf8", "lab": "#a855f7"},
                    text=df_rooms["utilization_percentage"].apply(lambda p: f"{p}%"),
                    labels={"utilization_percentage": "Utilization %", "room_name": "Facility", "type": "Facility Type"}
                )
                fig_rm.update_layout(
                    plot_bgcolor="#121a30",
                    paper_bgcolor="#121a30",
                    font=dict(color="#cbd5e1", family="Inter, sans-serif"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", range=[0, 100]),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.06)")
                )
                st.plotly_chart(fig_rm, use_container_width=True)

            with col_chart2:
                # Type Distribution Donut
                type_counts = df_rooms["type"].value_counts().reset_index()
                type_counts.columns = ["type", "count"]
                fig_donut = px.pie(
                    type_counts,
                    names="type",
                    values="count",
                    hole=0.55,
                    color="type",
                    color_discrete_map={"classroom": "#38bdf8", "lab": "#a855f7"}
                )
                fig_donut.update_layout(
                    plot_bgcolor="#121a30",
                    paper_bgcolor="#121a30",
                    font=dict(color="#cbd5e1"),
                    margin=dict(l=10, r=10, t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            # Facility Details Table
            st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
            st.markdown("##### Detailed Facility Inventory & Schedule Load")

            r_table = []
            for r in rooms:
                r_table.append({
                    "Facility Name": r.get("room_name"),
                    "Type": r.get("type", "").upper(),
                    "Seating Capacity": f"{r.get('capacity')} seats",
                    "Occupied Hours": f"{r.get('occupied_hours')}h",
                    "Available Usable Slots": f"{r.get('total_available_hours')} slots",
                    "Utilization": f"{r.get('utilization_percentage')}%",
                    "Scheduled Sessions": r.get("session_count")
                })
            st.dataframe(pd.DataFrame(r_table), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 3: CONSTRAINT QUALITY & SOFT PENALTIES (S1 - S5)
    # =========================================================================
    with tabs[2]:
        st.markdown("#### Schedule Optimization Quality & Soft Constraints (S1–S5)")
        st.write("Deconstructs timetable satisfaction across soft criteria: teacher idle gaps, preferred slots, laboratory continuity, and lecture pacing.")

        if not quality or not quality.get("has_schedule"):
            st.info("No active schedule found to evaluate quality. Generate a schedule to inspect soft constraint penalties.")
        else:
            q_col1, q_col2 = st.columns([1.1, 1.1])

            with q_col1:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### Soft Penalty Distribution (S1–S5)")

                breakdown = quality.get("penalty_breakdown", {})
                labels_map = {
                    "S1_gap": "S1: Free Period Gaps (Idle Time)",
                    "S2_subject_repeat": "S2: Same Subject Repeated Same Day",
                    "S3_lab_continuity": "S3: Non-Consecutive Lab Periods",
                    "S4_teacher_pref": "S4: Teacher Slot Preference Miss",
                    "S5_consecutive": "S5: Excessive Consecutive Lectures (>2)"
                }

                chart_data = []
                for k, v in breakdown.items():
                    if v > 0:
                        chart_data.append({"Constraint": labels_map.get(k, k), "Penalty Points": v})

                if not chart_data:
                    st.success("🎉 Perfect Soft Optimization! Zero soft constraint penalty points detected.")
                else:
                    df_penalties = pd.DataFrame(chart_data)
                    fig_pen = px.pie(
                        df_penalties,
                        names="Constraint",
                        values="Penalty Points",
                        hole=0.45,
                        color_discrete_sequence=["#f43f5e", "#f59e0b", "#38bdf8", "#a855f7", "#10b981"]
                    )
                    fig_pen.update_layout(
                        plot_bgcolor="#121a30",
                        paper_bgcolor="#121a30",
                        font=dict(color="#cbd5e1"),
                        margin=dict(l=10, r=10, t=10, b=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_pen, use_container_width=True)

                st.markdown("</div>", unsafe_allow_html=True)

            with q_col2:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### Constraint Metrics Summary")
                st.markdown(
                    f"""
                    <div style="font-size:0.88rem; line-height: 1.8; color: #cbd5e1;">
                        <div>Hard Constraint Status: <b style="color:{'#10b981' if quality.get('is_valid') else '#f43f5e'};">{'100% Conflict-Free (0 Violations)' if quality.get('is_valid') else f'{quality.get("hard_violations_count")} Hard Violations'}</b></div>
                        <div>Total Soft Penalty: <b style="color:#ffffff;">{quality.get('soft_penalty', 0)} pts</b></div>
                        <div>Optimization Compliance Index: <b style="color:#6366f1;">{quality.get('compliance_score', 100.0)}%</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                explanations = quality.get("explanations", [])
                if explanations:
                    st.markdown("<div style='margin-top:0.8rem; font-size:0.82rem; font-weight:700; color:#94a3b8;'>Active Soft Inefficiencies:</div>", unsafe_allow_html=True)
                    for exp in explanations[:8]:
                        st.markdown(f"- <span style='font-size:0.8rem; color:#cbd5e1;'>{exp}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
