"""
frontend/views/timetable_grid.py
Institutional Timetable Matrix View:
- View By: Class / Batch, Teacher / Faculty, Room / Lab
- Rich Visual Card Grid rendered through components.html (100% visual, zero markdown code block formatting)
- Direct 1-Click native downloads for CSV, Excel, and PDF
"""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from frontend.theme import page_header
from frontend.api_client import APIClient

def render_timetable_grid(embedded: bool = False, key_prefix: str = ""):
    if not embedded:
        page_header(
            title="Institutional Timetable Matrix",
            subtitle="Multi-dimensional schedule visualization with protected lunch periods and export options"
        )
    else:
        st.markdown(
            """
            <div style="margin-top: 2rem; padding-top: 1.25rem; border-top: 1px solid var(--border-subtle); margin-bottom: 0.75rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                        <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: var(--text-main);">📅 Live Timetable Schedule Matrix</h3>
                        <span class="schedulai-badge badge-primary">Auto-Sync</span>
                    </div>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">Instantly reflects any cancellations, rescheduled slots, moves, or faculty swaps</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 1. Fetch current active timetable and metadata
    ok_sched, sched_data, msg = APIClient.get_active_schedule()
    if not ok_sched or not sched_data:
        sched_data = {}

    sessions = sched_data.get("sessions", [])

    # Robust fallback for entities
    classes_list = sched_data.get("classes") or []
    if not classes_list:
        _, c_res, _ = APIClient.get_classes()
        classes_list = c_res or []
    classes_dict = {c["id"]: c for c in classes_list}

    teachers_list = sched_data.get("teachers") or []
    if not teachers_list:
        _, t_res, _ = APIClient.get_teachers()
        teachers_list = t_res or []
    teachers_dict = {t["id"]: t for t in teachers_list}

    subjects_list = sched_data.get("subjects") or []
    if not subjects_list:
        _, s_res, _ = APIClient.get_subjects()
        subjects_list = s_res or []
    subjects_dict = {s["id"]: s for s in subjects_list}

    rooms_list = sched_data.get("rooms") or []
    if not rooms_list:
        _, r_res, _ = APIClient.get_rooms()
        rooms_list = r_res or []
    rooms_dict = {r["id"]: r for r in rooms_list}

    settings = sched_data.get("settings") or {}
    if not settings:
        _, set_res, _ = APIClient.get_settings()
        settings = set_res or {}

    days = settings.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    periods_count = settings.get("periods_per_day", 6)
    periods = list(range(1, periods_count + 1))
    default_lunch = settings.get("default_lunch_period", 4)

    # Empty State with instant 1-click generator
    if not sessions:
        st.warning("⚠️ No active timetable sessions found in memory. Please generate a schedule or load preset data to view the timetable.")
        c_gen1, c_gen2 = st.columns(2)
        with c_gen1:
            if st.button("⚡ Generate AI Timetable (Backtracking Solver)", key=f"{key_prefix}btn_empty_gen", type="primary", use_container_width=True):
                with st.spinner("Generating clash-free timetable..."):
                    ok, res, g_msg = APIClient.generate_schedule({"algorithm": "improved_backtracking"})
                    if ok:
                        st.success("Timetable generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {g_msg}")
        with c_gen2:
            if st.button("📦 Load Preset & Generate Timetable", key=f"{key_prefix}btn_empty_preset", use_container_width=True):
                with st.spinner("Loading preset..."):
                    ok, _, _ = APIClient.load_preset("small")
                    if ok:
                        APIClient.generate_schedule({"algorithm": "improved_backtracking"})
                        st.success("Loaded preset and scheduled timetable!")
                        st.rerun()
        return

    # Metadata & Quality
    meta = sched_data.get("metadata") or {}
    algo_name = meta.get("algorithm", "Backtracking + Heuristics (MRV+Degree+FC+LCV)")
    hard_v = sched_data.get("hard_violations", 0)
    soft_score = meta.get("soft_penalty", meta.get("quality_score", 609))

    # Conflict Banner if any
    if hard_v > 0:
        st.error(f"⚠️ Schedule Conflict Alert: Current timetable contains {hard_v} unresolved Hard Constraint violation(s) (H1-H9).")

    # -------------------------------------------------------------------------
    # Top Action Toolbar: View By Selector + Entity Selector + Direct Downloads
    # -------------------------------------------------------------------------
    t_row1, t_row2 = st.columns([2.2, 0.8])
    
    with t_row1:
        view_mode = st.segmented_control(
            "View Perspective:",
            options=["Class / Batch", "Teacher / Faculty", "Room / Lab"],
            default="Room / Lab" if st.session_state.get(f"{key_prefix}last_view_mode") == "Room / Lab" else "Class / Batch",
            key=f"{key_prefix}view_mode_control"
        ) or "Class / Batch"
        st.session_state[f"{key_prefix}last_view_mode"] = view_mode

    with t_row2:
        st.markdown("<p style='font-size: 0.8rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.25rem;'>📥 Export Options</p>", unsafe_allow_html=True)
        e_c1, e_c2, e_c3 = st.columns(3)
        with e_c1:
            csv_bytes = APIClient.get_csv_bytes()
            st.download_button(
                label="📄 CSV",
                data=csv_bytes,
                file_name="schedulai_timetable.csv",
                mime="text/csv",
                key=f"{key_prefix}dl_csv",
                use_container_width=True,
                help="Download full CSV"
            )
        with e_c2:
            excel_bytes = APIClient.get_excel_bytes()
            st.download_button(
                label="📊 Excel",
                data=excel_bytes,
                file_name="schedulai_timetable.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key_prefix}dl_excel",
                use_container_width=True,
                help="Download multi-sheet Excel file"
            )
        with e_c3:
            pdf_bytes = APIClient.get_pdf_bytes()
            st.download_button(
                label="📕 PDF",
                data=pdf_bytes,
                file_name="schedulai_timetable.pdf",
                mime="application/pdf",
                key=f"{key_prefix}dl_pdf",
                use_container_width=True,
                help="Download printable landscape PDF"
            )

    # Fixed Pill Buttons Selection (100% Non-Editable / Read-Only Clickable Pills)
    if view_mode == "Class / Batch":
        class_options = list(classes_dict.keys())
        selected_id = st.pills(
            "Select Student Class / Cohort 🔒 (Fixed / Click to View):",
            options=class_options,
            default=class_options[0] if class_options else None,
            format_func=lambda cid: f"🎓 {classes_dict[cid].get('name', cid)} ({classes_dict[cid].get('strength', 0)} Students)",
            key=f"{key_prefix}pills_class"
        ) or (class_options[0] if class_options else None)
    elif view_mode == "Teacher / Faculty":
        teacher_options = list(teachers_dict.keys())
        selected_id = st.pills(
            "Select Faculty Member 🔒 (Fixed / Click to View):",
            options=teacher_options,
            default=teacher_options[0] if teacher_options else None,
            format_func=lambda tid: f"👨‍🏫 {teachers_dict[tid].get('name', tid)} ({teachers_dict[tid].get('max_weekly_load', 0)}h/wk)",
            key=f"{key_prefix}pills_teacher"
        ) or (teacher_options[0] if teacher_options else None)
    else:
        room_options = list(rooms_dict.keys())
        selected_id = st.pills(
            "Select Room or Lab 🔒 (Fixed / Click to View):",
            options=room_options,
            default=room_options[0] if room_options else None,
            format_func=lambda rid: f"🏛️ {rooms_dict[rid].get('name', rid)} ({rooms_dict[rid].get('type', 'classroom').title()}, Cap: {rooms_dict[rid].get('capacity', 0)})",
            key=f"{key_prefix}pills_room"
        ) or (room_options[0] if room_options else None)

    # -------------------------------------------------------------------------
    # Entity Title Banner with Badges
    # -------------------------------------------------------------------------
    if view_mode == "Class / Batch":
        curr_entity = classes_dict.get(selected_id, {})
        title_text = f"{curr_entity.get('name', selected_id)} ({curr_entity.get('strength', 0)} Students)"
        lunch_period = curr_entity.get("lunch_break_period", default_lunch)
        filter_fn = lambda s: s.get("class_id") == selected_id
    elif view_mode == "Teacher / Faculty":
        curr_entity = teachers_dict.get(selected_id, {})
        title_text = f"{curr_entity.get('name', selected_id)} (Max Load: {curr_entity.get('max_weekly_load', 0)}h/week)"
        lunch_period = default_lunch
        filter_fn = lambda s: s.get("teacher_id") == selected_id
    else:
        curr_entity = rooms_dict.get(selected_id, {})
        title_text = f"{curr_entity.get('name', selected_id)} ({curr_entity.get('type', 'classroom').title()}, Capacity: {curr_entity.get('capacity', 0)})"
        lunch_period = default_lunch
        filter_fn = lambda s: s.get("room_id") == selected_id

    # Filter sessions for selected entity (both active and cancelled)
    all_entity_sessions = [s for s in sessions if filter_fn(s)]
    active_sessions = [s for s in all_entity_sessions if s.get("status") != "cancelled"]
    cancelled_sessions = [s for s in all_entity_sessions if s.get("status") == "cancelled"]
    session_count = len(active_sessions)
    cancelled_count = len(cancelled_sessions)

    # Banner displayed via columns to keep it cleanly in Streamlit layout
    b_col1, b_col2 = st.columns([1.5, 1.5])
    with b_col1:
        st.markdown(f"### {title_text}")
        status_note = f"Showing {session_count} scheduled sessions"
        if cancelled_count > 0:
            status_note += f" • <span style='color: #ef4444; font-weight: 700;'>{cancelled_count} Cancelled Session(s)</span>"
        st.caption(f"{status_note} • Protected lunch period (Period {lunch_period})", unsafe_allow_html=True)
    with b_col2:
        st.markdown(
            f"""
            <div style="display: flex; gap: 0.45rem; justify-content: flex-end; align-items: center; margin-top: 0.6rem; flex-wrap: wrap;">
                <span class="schedulai-badge badge-primary">{algo_name}</span>
                <span class="schedulai-badge badge-success">{hard_v} Hard Violations</span>
                <span class="schedulai-badge badge-warning">Soft Score: {soft_score}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # Build Slot Map: gridMap[day][period] = session_info
    # -------------------------------------------------------------------------
    grid_map = {d: {} for d in days}
    # 1. Place active sessions first
    for s in active_sessions:
        day = s.get("day")
        p_start = s.get("period")
        dur = s.get("duration", 1)
        if day in grid_map and p_start:
            grid_map[day][p_start] = {**s, "is_extension": False}
            if dur > 1:
                for off in range(1, dur):
                    grid_map[day][p_start + off] = {**s, "is_extension": True}

    # 2. Place cancelled sessions if slot is free
    for s in cancelled_sessions:
        day = s.get("day")
        p_start = s.get("period")
        dur = s.get("duration", 1)
        if day in grid_map and p_start:
            if p_start not in grid_map[day]:
                grid_map[day][p_start] = {**s, "is_extension": False}
                if dur > 1:
                    for off in range(1, dur):
                        if (p_start + off) not in grid_map[day]:
                            grid_map[day][p_start + off] = {**s, "is_extension": True}

    # -------------------------------------------------------------------------
    # Build Matrix Grid HTML for components.html (100% Isolated Visual Webpage)
    # -------------------------------------------------------------------------
    header_th = ""
    for p in periods:
        if p == lunch_period:
            header_th += '<th class="lunch-col">LUNCH</th>'
        else:
            header_th += f"<th>PERIOD {p}</th>"

    table_rows = ""
    for day in days:
        row_tds = f'<td class="day-cell">{day}</td>'
        for p in periods:
            # 1. Lunch Slot
            if p == lunch_period:
                row_tds += '<td class="lunch-slot">LUNCH<br>BREAK</td>'
                continue

            item = grid_map[day].get(p)
            # 2. Free Slot
            if not item:
                row_tds += '<td class="slot-cell"><div class="free-slot">Free Period</div></td>'
                continue

            # 3. Session Slot
            sub_id = item.get("subject_id")
            sub_obj = subjects_dict.get(sub_id, {})
            sub_code = sub_obj.get("code", item.get("subject_code", sub_id))
            sub_name = sub_obj.get("name", item.get("subject_name", sub_id))
            is_lab = (sub_obj.get("type") == "lab") or (item.get("subject_type") == "lab")
            is_cancelled = (item.get("status") == "cancelled")

            tea_obj = teachers_dict.get(item.get("teacher_id"), {})
            tea_name = tea_obj.get("name", item.get("teacher_name", item.get("teacher_id")))
            tea_short = tea_name.split()[0] if tea_name else "Faculty"

            cls_obj = classes_dict.get(item.get("class_id"), {})
            cls_name = cls_obj.get("name", item.get("class_name", item.get("class_id")))

            rm_obj = rooms_dict.get(item.get("room_id"), {})
            rm_name = rm_obj.get("name", item.get("room_name", item.get("room_id")))
            rm_short = rm_name.split("(")[0].strip() if rm_name else "Room"

            # Check if this is a cancelled session
            if is_cancelled:
                cancel_reason = item.get("cancellation_reason") or (item.get("original_slot", {}).get("cancellation_reason") if isinstance(item.get("original_slot"), dict) else None) or "Faculty Leave"
                card_html = f"""<div class="session-box cancelled" title="Cancelled: {cancel_reason}"><div class="session-header"><span class="session-code" style="text-decoration: line-through; opacity: 0.65;">{sub_code}</span><span class="badge badge-cancelled">🚫 CANCELLED</span></div><div class="session-name" style="text-decoration: line-through; opacity: 0.75;" title="{sub_name}">{sub_name}</div><div class="session-faculty" style="text-decoration: line-through; opacity: 0.65;">👨‍🏫 {tea_name}</div><div class="session-footer"><span style="color: #ef4444; font-weight: 600; font-size: 0.65rem;">🚫 {cancel_reason[:18]}</span><span>🏛️ {rm_short}</span></div></div>"""
            # Check if this is the multi-period continuation
            elif item.get("is_extension"):
                card_html = f"""<div class="session-box lab" style="opacity: 0.88;"><div class="session-header"><span class="session-code">{sub_code} (Cont.)</span><span class="badge badge-lab">Lab 2/2</span></div><div class="session-name" title="{sub_name}">{sub_name}</div><div class="session-faculty">👨‍🏫 {tea_name}</div><div class="session-footer"><span>🏛️ {rm_short}</span><span style="font-size: 0.65rem; color: #67e8f9; font-weight: 600;">Continuation</span></div></div>"""
            else:
                box_cls = "lab" if is_lab else "theory"
                badge_cls = "badge-lab" if is_lab else "badge-theory"
                badge_lbl = "LAB (2h)" if is_lab else "THEORY"

                if view_mode == "Teacher / Faculty":
                    fac_line = f"""<div class="session-faculty" title="Class: {cls_name}">👥 {cls_name}</div>"""
                    foot_extra = f"""<span>👥 {cls_name}</span>"""
                else:
                    fac_line = f"""<div class="session-faculty" title="Faculty: {tea_name}">👨‍🏫 {tea_name}</div>"""
                    foot_extra = ""

                card_html = f"""<div class="session-box {box_cls}"><div class="session-header"><span class="session-code">{sub_code}</span><span class="badge {badge_cls}">{badge_lbl}</span></div><div class="session-name" title="{sub_name}">{sub_name}</div>{fac_line}<div class="session-footer"><span>🏛️ {rm_name}</span>{foot_extra}</div></div>"""

            row_tds += f'<td class="slot-cell">{card_html}</td>'

        table_rows += f"<tr>{row_tds}</tr>"

    theme_mode = st.session_state.get("theme_mode", "dark")
    is_light = (theme_mode == "light")

    if is_light:
        grid_css = """
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: transparent; color: #0f172a; padding: 4px; margin: 0; }
        .timetable-wrapper { width: 100%; overflow-x: auto; border-radius: 12px; border: 1px solid rgba(0, 0, 0, 0.08); background: #ffffff; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06); }
        .timetable-grid { width: 100%; border-collapse: collapse; table-layout: fixed; min-width: 860px; }
        .timetable-grid th { background: #f8fafc; color: #475569; font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; padding: 12px 10px; border: 1px solid rgba(0, 0, 0, 0.07); text-align: center; }
        .timetable-grid th.day-col { width: 85px; background: #f1f5f9; color: #0f172a; font-weight: 800; }
        .timetable-grid th.lunch-col { width: 95px; color: #b45309; }
        .day-cell { width: 85px; background: #f8fafc; color: #0f172a; font-weight: 800; text-align: center; vertical-align: middle; font-size: 0.88rem; border: 1px solid rgba(0, 0, 0, 0.07); }
        .slot-cell { border: 1px solid rgba(0, 0, 0, 0.07); padding: 6px; vertical-align: top; height: 120px; background: #ffffff; transition: background 0.15s ease; }
        .slot-cell:hover { background: #f8fafc; }
        .session-box { height: 100%; border-radius: 8px; padding: 7px 9px; display: flex; flex-direction: column; justify-content: space-between; background: linear-gradient(145deg, #ffffff, #f8fafc); border: 1px solid rgba(0, 0, 0, 0.09); transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: default; }
        .session-box:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08); }
        .session-box.theory { border-left: 3.5px solid #4f46e5; background: linear-gradient(145deg, #eef2ff, #ffffff); }
        .session-box.lab { border-left: 3.5px solid #0891b2; background: linear-gradient(145deg, #ecfeff, #ffffff); }
        .session-box.cancelled { border-left: 3.5px solid #ef4444; border: 1px dashed rgba(239, 68, 68, 0.45); background: linear-gradient(145deg, #fef2f2, #ffffff); opacity: 0.92; }
        .session-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
        .session-code { font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 0.82rem; color: #0f172a; }
        .badge { font-size: 0.65rem; font-weight: 700; padding: 1.5px 6px; border-radius: 9999px; text-transform: uppercase; }
        .badge-theory { background: rgba(79, 70, 229, 0.12); color: #4338ca; border: 1px solid rgba(79, 70, 229, 0.3); }
        .badge-lab { background: rgba(8, 145, 178, 0.12); color: #0e7490; border: 1px solid rgba(8, 145, 178, 0.3); }
        .badge-cancelled { background: rgba(239, 68, 68, 0.12); color: #dc2626; border: 1px solid rgba(239, 68, 68, 0.35); }
        .session-name { font-size: 0.74rem; color: #334155; font-weight: 700; line-height: 1.25; margin: 2px 0 1px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .session-faculty { font-size: 0.72rem; color: #0284c7; font-weight: 600; margin-bottom: 3px; display: flex; align-items: center; gap: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .session-footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: #64748b; margin-top: auto; padding-top: 3px; border-top: 1px solid rgba(0, 0, 0, 0.06); }
        .lunch-slot { width: 95px; border: 1px dashed rgba(245, 158, 11, 0.4); background: repeating-linear-gradient(-45deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.1) 8px, rgba(245, 158, 11, 0.03) 8px, rgba(245, 158, 11, 0.03) 16px); color: #b45309; font-weight: 700; font-size: 0.76rem; text-align: center; vertical-align: middle; letter-spacing: 0.06em; padding: 6px; line-height: 1.4; }
        .free-slot { height: 100%; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 0.72rem; font-style: italic; }
        """
    else:
        grid_css = """
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: transparent; color: #e2e8f0; padding: 4px; margin: 0; }
        .timetable-wrapper { width: 100%; overflow-x: auto; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08); background: #0f172a; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4); }
        .timetable-grid { width: 100%; border-collapse: collapse; table-layout: fixed; min-width: 860px; }
        .timetable-grid th { background: #090d16; color: #94a3b8; font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; padding: 12px 10px; border: 1px solid rgba(255, 255, 255, 0.07); text-align: center; }
        .timetable-grid th.day-col { width: 85px; background: #060911; color: #f1f5f9; font-weight: 800; }
        .timetable-grid th.lunch-col { width: 95px; color: #fbbf24; }
        .day-cell { width: 85px; background: #090d16; color: #f8fafc; font-weight: 800; text-align: center; vertical-align: middle; font-size: 0.88rem; border: 1px solid rgba(255, 255, 255, 0.07); }
        .slot-cell { border: 1px solid rgba(255, 255, 255, 0.07); padding: 6px; vertical-align: top; height: 120px; background: rgba(15, 23, 42, 0.6); transition: background 0.15s ease; }
        .slot-cell:hover { background: rgba(30, 41, 59, 0.45); }
        .session-box { height: 100%; border-radius: 8px; padding: 7px 9px; display: flex; flex-direction: column; justify-content: space-between; background: linear-gradient(145deg, #1e293b, #111827); border: 1px solid rgba(255, 255, 255, 0.08); transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: default; }
        .session-box:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5); }
        .session-box.theory { border-left: 3.5px solid #6366f1; background: linear-gradient(145deg, rgba(30, 41, 69, 0.9), rgba(17, 24, 39, 0.95)); }
        .session-box.lab { border-left: 3.5px solid #06b6d4; background: linear-gradient(145deg, rgba(14, 53, 73, 0.9), rgba(17, 24, 39, 0.95)); }
        .session-box.cancelled { border-left: 3.5px solid #ef4444; border: 1px dashed rgba(239, 68, 68, 0.45); background: linear-gradient(145deg, rgba(80, 15, 15, 0.4), rgba(20, 24, 39, 0.95)); opacity: 0.92; }
        .session-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
        .session-code { font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 0.82rem; color: #ffffff; }
        .badge { font-size: 0.65rem; font-weight: 700; padding: 1.5px 6px; border-radius: 9999px; text-transform: uppercase; }
        .badge-theory { background: rgba(99, 102, 241, 0.18); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.35); }
        .badge-lab { background: rgba(6, 182, 212, 0.18); color: #67e8f9; border: 1px solid rgba(6, 182, 212, 0.35); }
        .badge-cancelled { background: rgba(239, 68, 68, 0.22); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.45); }
        .session-name { font-size: 0.74rem; color: #cbd5e1; font-weight: 700; line-height: 1.25; margin: 2px 0 1px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .session-faculty { font-size: 0.72rem; color: #38bdf8; font-weight: 600; margin-bottom: 3px; display: flex; align-items: center; gap: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .session-footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; color: #94a3b8; margin-top: auto; padding-top: 3px; border-top: 1px solid rgba(255, 255, 255, 0.06); }
        .lunch-slot { width: 95px; border: 1px dashed rgba(245, 158, 11, 0.35); background: repeating-linear-gradient(-45deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.08) 8px, rgba(245, 158, 11, 0.02) 8px, rgba(245, 158, 11, 0.02) 16px); color: #fbbf24; font-weight: 700; font-size: 0.76rem; text-align: center; vertical-align: middle; letter-spacing: 0.06em; padding: 6px; line-height: 1.4; }
        .free-slot { height: 100%; display: flex; align-items: center; justify-content: center; color: rgba(255, 255, 255, 0.18); font-size: 0.72rem; font-style: italic; }
        """

    full_html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600;800&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  {grid_css}
</style>
</head>

<body>
<div class="timetable-wrapper">
  <table class="timetable-grid">
    <thead>
      <tr>
        <th class="day-col">DAY</th>
        {header_th}
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</div>
</body>
</html>
"""
    # Render through components.html with exact pixel height - zero markdown parser interference!
    grid_height = 65 + (len(days) * 126)
    components.html(full_html_doc, height=grid_height, scrolling=False)
