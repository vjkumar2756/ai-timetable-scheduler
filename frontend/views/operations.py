"""
frontend/views/operations.py
Academic Operations & Dynamic Rescheduling View.
- Tab 1: Manual Session Edit with Live Constraint Impact Analysis (H1 - H9).
- Tab 2: Class Cancellation (Single Session or Full Class Day Closure).
- Tab 3: Automated Collision-Free Missed Lecture Rescheduling Recommender.
- Tab 4: Teacher Swap Requests (Phase 13).
- Tab 5: In-App Operational Notification Center.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from frontend.theme import page_header
from frontend.api_client import APIClient

def render_operations_page():
    page_header(
        title="Operations & Rescheduling",
        subtitle="Manage dynamic academic operations: manual edits, class cancellations, collision-free rescheduling, and notifications"
    )

    # 1. Fetch live system entities and active timetable
    ok_c, classes_list, _ = APIClient.get_classes()
    ok_t, teachers_list, _ = APIClient.get_teachers()
    ok_r, rooms_list, _ = APIClient.get_rooms()
    ok_s, settings_obj, _ = APIClient.get_settings()
    ok_sched, sched_data, _ = APIClient.get_active_schedule()

    classes_dict = {c["id"]: c for c in (classes_list or [])}
    teachers_dict = {t["id"]: t for t in (teachers_list or [])}
    rooms_dict = {r["id"]: r for r in (rooms_list or [])}
    settings = settings_obj or {"days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "periods_per_day": 6}
    days = settings.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    periods_count = settings.get("periods_per_day", 6)

    sessions = sched_data.get("sessions", []) if (ok_sched and sched_data) else []

    tabs = st.tabs([
        "✏️ Manual Edit & Live Validation",
        "🚫 Class Cancellation",
        "🔄 Missed Lecture Rescheduling",
        "🤝 Teacher Swap Requests",
        "🔔 Notifications & Alerts"
    ])

    # =========================================================================
    # TAB 1: MANUAL EDIT WITH LIVE CONSTRAINT IMPACT ANALYSIS
    # =========================================================================
    with tabs[0]:
        st.markdown("#### Move Session with Live Constraint Validation")
        st.write("Relocate any lecture or lab session to a new time or facility. The system immediately simulates the move and checks all 9 institutional hard constraints (H1–H9).")

        if not sessions:
            st.warning("No active timetable found. Please load a dataset or generate a schedule first.")
        else:
            c1, c2 = st.columns([1.2, 1.0])

            with c1:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 1. Select Session to Relocate")
                
                class_options = ["All Classes"] + list(classes_dict.keys())
                sel_class = st.selectbox(
                    "Filter by Class",
                    options=class_options,
                    format_func=lambda x: classes_dict[x].get("name", x) if x != "All Classes" else "All Classes",
                    key="man_edit_class_filter"
                )

                filtered_sessions = [s for s in sessions if s.get("status") != "cancelled"]
                if sel_class != "All Classes":
                    filtered_sessions = [s for s in filtered_sessions if s.get("class_id") == sel_class]

                if not filtered_sessions:
                    st.info("No active (non-cancelled) sessions available for the selected class.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    selected_sess = None
                else:
                    def session_format(s):
                        c_name = classes_dict.get(s.get("class_id"), {}).get("name", s.get("class_id"))
                        t_name = teachers_dict.get(s.get("teacher_id"), {}).get("name", s.get("teacher_id"))
                        r_name = rooms_dict.get(s.get("room_id"), {}).get("name", s.get("room_id"))
                        return f"{c_name} | {s.get('subject_code', s.get('subject_id'))} | {s.get('day')} P{s.get('period')} | {t_name} | {r_name}"

                    selected_sess = st.selectbox(
                        "Choose Session",
                        options=filtered_sessions,
                        format_func=session_format,
                        key="man_edit_sess_select"
                    )

                    st.markdown("---")
                    st.markdown(
                        f"""
                        <div style="font-size: 0.85rem; line-height: 1.6; color: #cbd5e1;">
                            <b>Selected:</b> {session_format(selected_sess)}<br/>
                            <b>Duration:</b> {selected_sess.get('duration', 1)} period(s) | <b>Status:</b> {selected_sess.get('status', 'scheduled').title()}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                if selected_sess:
                    st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                    st.markdown("##### 2. Choose Target Slot & Facility")

                    target_day = st.selectbox(
                        "Target Day",
                        options=days,
                        index=days.index(selected_sess.get("day")) if selected_sess.get("day") in days else 0,
                        key="man_edit_target_day"
                    )
                    target_period = st.number_input(
                        "Target Starting Period",
                        min_value=1,
                        max_value=periods_count,
                        value=selected_sess.get("period", 1),
                        key="man_edit_target_period"
                    )
                    
                    room_keys = list(rooms_dict.keys())
                    def_room_idx = room_keys.index(selected_sess.get("room_id")) if selected_sess.get("room_id") in room_keys else 0
                    target_room = st.selectbox(
                        "Target Room / Lab",
                        options=room_keys,
                        index=def_room_idx,
                        format_func=lambda r: f"{rooms_dict[r].get('name', r)} ({rooms_dict[r].get('type', '').title()}, Cap: {rooms_dict[r].get('capacity', 0)})",
                        key="man_edit_target_room"
                    )

                    teacher_keys = list(teachers_dict.keys())
                    def_tea_idx = teacher_keys.index(selected_sess.get("teacher_id")) if selected_sess.get("teacher_id") in teacher_keys else 0
                    target_teacher = st.selectbox(
                        "Target Faculty",
                        options=teacher_keys,
                        index=def_tea_idx,
                        format_func=lambda t: teachers_dict[t].get("name", t),
                        key="man_edit_target_teacher"
                    )

                    st.markdown("</div>", unsafe_allow_html=True)

            # 3. Live Validation Check
            if selected_sess:
                validate_payload = {
                    "session_id": selected_sess["id"],
                    "target_day": target_day,
                    "target_period": int(target_period),
                    "target_room_id": target_room,
                    "target_teacher_id": target_teacher
                }

                ok_val, val_data, val_msg = APIClient.validate_manual_edit(validate_payload)

                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 3. Live Constraint Impact Analysis")

                if ok_val:
                    st.success(f"✅ Conflict-Free Move: Proposed slot satisfies all 9 Hard Constraints (H1–H9). Soft Penalty: {val_data.get('soft_penalty', 0)} pts.")
                    if st.button("Apply Move to Schedule", type="primary", key="btn_apply_valid_move"):
                        apply_payload = {**validate_payload, "apply_anyway": False}
                        ok_app, app_data, app_msg = APIClient.apply_manual_edit(apply_payload)
                        if ok_app:
                            st.toast("Session moved successfully!", icon="✅")
                            st.rerun()
                        else:
                            st.error(app_msg)
                else:
                    violations = val_data.get("violations", []) if val_data else []
                    v_count = len(violations)
                    st.error(f"❌ Hard Constraint Violations Detected ({v_count} conflict(s)):")
                    for v in violations:
                        msg = v.get("message", str(v))
                        st.markdown(f"- 🛑 **{msg}**")

                    st.markdown("<p style='font-size: 0.82rem; color: #94a3b8; margin-top: 0.5rem;'>Per academic requirements, you may optionally force this move; the system will flag the resulting hard conflict on the dashboard and timetable views.</p>", unsafe_allow_html=True)
                    
                    if st.button("⚠️ Apply Anyway (Save with Flagged Conflicts)", key="btn_apply_forced_move"):
                        apply_payload = {**validate_payload, "apply_anyway": True}
                        ok_app, app_data, app_msg = APIClient.apply_manual_edit(apply_payload)
                        if ok_app:
                            st.toast("Session moved with flagged conflicts!", icon="⚠️")
                            st.rerun()
                        else:
                            st.error(app_msg)

                st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: CLASS CANCELLATION (SINGLE SESSION OR FULL DAY CLOSURE)
    # =========================================================================
    with tabs[1]:
        st.markdown("#### Dynamic Class & Session Cancellation")
        st.write("Cancel an individual lecture session (due to faculty leave or emergency) or suspend all classes for a cohort on a given day (e.g. department symposium or college holiday).")

        if not sessions:
            st.warning("No active timetable found to cancel sessions from. Please load or generate a timetable first.")
        else:
            cancel_mode = st.radio(
                "Cancellation Scope",
                options=["Single Lecture / Lab Session", "Close Full Day for Class Cohort"],
                horizontal=True,
                key="cancel_mode_radio"
            )

            if cancel_mode == "Single Lecture / Lab Session":
                c_col1, c_col2 = st.columns([1.2, 1.0])
                
                with c_col1:
                    st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                    st.markdown("##### 1. Select Active Session to Cancel")

                    # Filter by Class
                    class_keys = list(classes_dict.keys())
                    sel_c_class = st.selectbox(
                        "Class Cohort",
                        options=class_keys,
                        format_func=lambda x: classes_dict[x].get("name", x),
                        key="cancel_class_filter"
                    )

                    active_class_sessions = [
                        s for s in sessions
                        if s.get("class_id") == sel_c_class and s.get("status") != "cancelled"
                    ]

                    if not active_class_sessions:
                        st.info(f"No active sessions found for {classes_dict.get(sel_c_class, {}).get('name', sel_c_class)}.")
                        st.markdown("</div>", unsafe_allow_html=True)
                        sel_cancel_sess = None
                    else:
                        def cancel_sess_fmt(s):
                            t_name = teachers_dict.get(s.get("teacher_id"), {}).get("name", s.get("teacher_id"))
                            return f"{s.get('subject_name', s.get('subject_code'))} | {s.get('day')} Period {s.get('period')} | {t_name}"

                        sel_cancel_sess = st.selectbox(
                            "Choose Scheduled Session",
                            options=active_class_sessions,
                            format_func=cancel_sess_fmt,
                            key="cancel_sess_select"
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                with c_col2:
                    if sel_cancel_sess:
                        st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                        st.markdown("##### 2. Cancellation Details & Reason")
                        cancel_reason = st.text_input(
                            "Official Reason",
                            value="Faculty medical leave / emergency",
                            key="cancel_reason_input"
                        )

                        st.markdown(
                            f"""
                            <div style="font-size: 0.82rem; color: #94a3b8; margin: 0.5rem 0;">
                                ⚠️ Cancelling will mark this session as <b>cancelled</b>, notify student batch <b>{classes_dict.get(sel_cancel_sess.get('class_id'), {}).get('name')}</b>, and make it available in the Rescheduling Recommender.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button("🚫 Confirm Session Cancellation", type="primary", key="btn_confirm_cancel_sess"):
                            ok_can, can_data, can_msg = APIClient.cancel_session(sel_cancel_sess["id"], cancel_reason)
                            if ok_can:
                                st.toast("Lecture session cancelled and notifications dispatched!", icon="🚫")
                                st.rerun()
                            else:
                                st.error(can_msg)
                        st.markdown("</div>", unsafe_allow_html=True)

            else:
                # Full day closure mode
                d_col1, d_col2 = st.columns([1.1, 1.1])
                with d_col1:
                    st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                    st.markdown("##### 1. Cohort & Day")
                    class_keys = list(classes_dict.keys())
                    close_class_id = st.selectbox(
                        "Class Cohort",
                        options=class_keys,
                        format_func=lambda x: classes_dict[x].get("name", x),
                        key="close_day_class_select"
                    )
                    close_day = st.selectbox("Day of Week to Suspend", options=days, key="close_day_select")
                    st.markdown("</div>", unsafe_allow_html=True)

                with d_col2:
                    st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                    st.markdown("##### 2. Reason & Confirmation")
                    close_reason = st.text_input(
                        "Reason for Suspension",
                        value="Department symposium / Institutional holiday",
                        key="close_day_reason_input"
                    )

                    # Preview affected sessions count
                    affected_count = len([
                        s for s in sessions
                        if s.get("class_id") == close_class_id and s.get("day") == close_day and s.get("status") != "cancelled"
                    ])
                    st.markdown(f"<div style='font-size:0.85rem; color:#cbd5e1; margin-bottom:0.5rem;'>Active sessions to be cancelled: <b>{affected_count}</b></div>", unsafe_allow_html=True)

                    if st.button("🚫 Close Class for Full Day", type="primary", key="btn_close_class_day"):
                        ok_close, close_data, close_msg = APIClient.close_class_day(close_class_id, close_day, close_reason)
                        if ok_close:
                            st.toast(close_msg, icon="🚫")
                            st.rerun()
                        else:
                            st.error(close_msg)
                    st.markdown("</div>", unsafe_allow_html=True)

            # Cancellation Audit Log
            st.markdown("<div class='schedulai-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("##### Cancellation Audit Trail")
            ok_hist, hist_data, _ = APIClient.get_cancellations()
            cancellations = hist_data if (ok_hist and hist_data) else []

            if not cancellations:
                st.info("No cancellations recorded in this session yet.")
            else:
                table_rows = []
                for c in reversed(cancellations):
                    table_rows.append({
                        "Timestamp": c.get("timestamp", "")[:19].replace("T", " "),
                        "Scope": c.get("scope", "").replace("_", " ").title(),
                        "Class": classes_dict.get(c.get("class_id"), {}).get("name", c.get("class_id")),
                        "Day": c.get("day", "N/A"),
                        "Period": f"P{c.get('period')}" if c.get("period") else "Full Day",
                        "Reason": c.get("reason", ""),
                        "Sessions Affected": len(c.get("affected_session_ids", []))
                    })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 3: MISSED LECTURE RESCHEDULING RECOMMENDER
    # =========================================================================
    with tabs[2]:
        st.markdown("#### Automated Collision-Free Rescheduling Recommender")
        st.write("Intelligently recommends the best open slots to recover missed/cancelled lectures without violating any of the 9 hard constraints (H1–H9). Ranked by minimal soft penalties (S1–S5).")

        # Find cancelled sessions
        cancelled_sessions = [s for s in sessions if s.get("status") == "cancelled"]

        if not cancelled_sessions:
            st.info("💡 There are currently no cancelled sessions requiring rescheduling. Cancel a session in the 'Class Cancellation' tab to test the automated recommender.")
        else:
            r_col1, r_col2 = st.columns([1.1, 1.1])

            with r_col1:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 1. Select Missed / Cancelled Session")

                def missed_fmt(s):
                    c_name = classes_dict.get(s.get("class_id"), {}).get("name", s.get("class_id"))
                    sub_name = s.get("subject_name", s.get("subject_code"))
                    t_name = teachers_dict.get(s.get("teacher_id"), {}).get("name", s.get("teacher_id"))
                    return f"{c_name} — {sub_name} (Originally: {s.get('day')} P{s.get('period')} by {t_name})"

                sel_missed = st.selectbox(
                    "Cancelled Lecture",
                    options=cancelled_sessions,
                    format_func=missed_fmt,
                    key="select_missed_session"
                )

                st.markdown("##### 2. Instructor Assignment")
                # Qualified teachers for this subject
                sub_id = sel_missed.get("subject_id")
                qualified_teachers = [
                    t for t in teachers_list
                    if sub_id in t.get("subject_ids", [])
                ]
                
                # Default to original teacher
                orig_teacher_id = sel_missed.get("teacher_id")
                teacher_choice_options = ["Original Faculty"] + [
                    f"Substitute: {t.get('name')} ({t.get('id')})"
                    for t in qualified_teachers if t.get("id") != orig_teacher_id
                ]

                chosen_teacher_mode = st.selectbox(
                    "Faculty Assignment",
                    options=teacher_choice_options,
                    key="reschedule_teacher_mode"
                )

                if chosen_teacher_mode == "Original Faculty":
                    target_resched_teacher = orig_teacher_id
                else:
                    target_resched_teacher = chosen_teacher_mode.split("(")[-1].rstrip(")")

                st.markdown("</div>", unsafe_allow_html=True)

            with r_col2:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 3. AI Conflict-Free Search")
                st.write(f"Searching available slots for **{sel_missed.get('subject_name')}** ({sel_missed.get('duration', 1)} hr) taught by **{teachers_dict.get(target_resched_teacher, {}).get('name', target_resched_teacher)}**.")

                run_search = st.button("🔍 Search Collision-Free Slots", type="primary", key="btn_run_reschedule_search")

                if run_search or "cached_resched_options" in st.session_state:
                    if run_search:
                        with st.spinner("Simulating all timetable slots against H1–H9 and ranking by S1–S5 soft costs..."):
                            ok_opt, opt_data, opt_msg = APIClient.find_reschedule_slots(
                                session_id=sel_missed["id"],
                                alternative_teacher_id=target_resched_teacher
                            )
                            if ok_opt:
                                st.session_state["cached_resched_options"] = opt_data.get("options", [])
                                st.session_state["cached_resched_msg"] = opt_msg
                            else:
                                st.error(opt_msg)
                                st.session_state["cached_resched_options"] = []

                    options = st.session_state.get("cached_resched_options", [])
                    if not options:
                        st.warning("⚠️ No clash-free slots available across institutional schedule. Consider testing with an alternative substitute teacher or relaxing room constraints.")
                    else:
                        st.success(f"Found **{len(options)}** 100% collision-free alternative slot(s) satisfying all 9 Hard Constraints:")
                        
                        for idx, opt in enumerate(options):
                            is_top = (idx == 0)
                            card_border = "#6366f1" if is_top else "#334155"
                            badge_html = "<span class='schedulai-badge badge-success' style='margin-left:0.5rem;'>🌟 AI Recommended</span>" if is_top else ""
                            
                            st.markdown(
                                f"""
                                <div style="border: 1px solid {card_border}; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.6rem; background: #0f172a;">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <b style="color:#ffffff;">Slot #{idx+1}: {opt['day']} Period {opt['period']} {badge_html}</b>
                                        <span style="font-size:0.78rem; color:#94a3b8;">Soft Penalty: <b>{opt.get('soft_penalty', 0)} pts</b></span>
                                    </div>
                                    <div style="font-size:0.82rem; color:#cbd5e1; margin-top:0.4rem;">
                                        Facility: <b>{opt.get('room_name')}</b> | Faculty: <b>{opt.get('teacher_name')}</b>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            btn_key = f"btn_book_slot_{idx}_{opt['day']}_{opt['period']}"
                            if st.button(f"Book & Reschedule to {opt['day']} P{opt['period']}", key=btn_key):
                                apply_resched_payload = {
                                    "session_id": sel_missed["id"],
                                    "target_day": opt["day"],
                                    "target_period": opt["period"],
                                    "target_room_id": opt["room_id"],
                                    "target_teacher_id": opt["teacher_id"],
                                    "reason": "Recovering missed lecture via AI Rescheduling Recommender"
                                }
                                ok_apply, apply_res, apply_msg = APIClient.apply_reschedule(apply_resched_payload)
                                if ok_apply:
                                    st.toast("Lecture successfully rescheduled! Updated timetable.", icon="✅")
                                    if "cached_resched_options" in st.session_state:
                                        del st.session_state["cached_resched_options"]
                                    st.rerun()
                                else:
                                    st.error(apply_msg)
                st.markdown("</div>", unsafe_allow_html=True)

            # Rescheduled History Log
            st.markdown("<div class='schedulai-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("##### Approved Rescheduling History")
            ok_prop, prop_data, _ = APIClient.get_reschedule_proposals()
            proposals = prop_data if (ok_prop and prop_data) else []

            if not proposals:
                st.info("No lectures have been rescheduled yet.")
            else:
                p_rows = []
                for p in reversed(proposals):
                    p_rows.append({
                        "Created At": p.get("created_at", "")[:19].replace("T", " "),
                        "Missed Session ID": p.get("missed_session_id"),
                        "Rescheduled Slot": f"{p.get('proposed_day')} P{p.get('proposed_period')}",
                        "Assigned Faculty": teachers_dict.get(p.get("proposed_teacher_id"), {}).get("name", p.get("proposed_teacher_id")),
                        "Assigned Room": rooms_dict.get(p.get("proposed_room_id"), {}).get("name", p.get("proposed_room_id")),
                        "Status": p.get("status", "approved").upper(),
                        "Reason": p.get("reason", "")
                    })
                st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 4: TEACHER SWAP REQUESTS (PHASE 13)
    # =========================================================================
    with tabs[3]:
        st.markdown("#### Mutual Teacher Swap Requests")
        st.write("Facilitates bilateral lecture slot exchanges between faculty members. Swapping exchanges the times and days of two sessions, and is only executed after mathematical zero-clash verification (H1–H9).")

        if not sessions:
            st.warning("No active timetable found to perform swaps. Please load or generate a timetable first.")
        else:
            s_col1, s_col2 = st.columns([1.1, 1.1])

            # Session 1 Selection (Requester)
            with s_col1:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 1. First Faculty & Session (Requester)")

                teacher_keys = list(teachers_dict.keys())
                sel_t1 = st.selectbox(
                    "Requester Faculty",
                    options=teacher_keys,
                    format_func=lambda t: teachers_dict[t].get("name", t),
                    key="swap_teacher_1"
                )

                t1_sessions = [
                    s for s in sessions
                    if s.get("teacher_id") == sel_t1 and s.get("status") != "cancelled"
                ]

                if not t1_sessions:
                    st.info(f"No active sessions found for {teachers_dict.get(sel_t1, {}).get('name')}.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    sel_s1 = None
                else:
                    def s1_fmt(s):
                        c_name = classes_dict.get(s.get("class_id"), {}).get("name", s.get("class_id"))
                        return f"{c_name} — {s.get('subject_name', s.get('subject_code'))} ({s.get('day')} P{s.get('period')}, {s.get('duration', 1)}h)"

                    sel_s1 = st.selectbox(
                        "Session to Swap Out",
                        options=t1_sessions,
                        format_func=s1_fmt,
                        key="swap_session_1"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

            # Session 2 Selection (Exchange Partner)
            with s_col2:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 2. Second Faculty & Session (Partner)")

                partner_options = ["all_compatible"] + teacher_keys
                def partner_fmt(t):
                    if t == "all_compatible":
                        return "🌟 All Compatible Faculty (Auto-Filter)"
                    return teachers_dict[t].get("name", t)

                sel_t2 = st.selectbox(
                    "Partner Faculty",
                    options=partner_options,
                    index=0,
                    format_func=partner_fmt,
                    key="swap_teacher_2"
                )

                only_possible = st.checkbox(
                    "Show only feasible clash-free swaps (0 Clashes Guaranteed)",
                    value=True,
                    key="swap_filter_possible_only"
                )

                req_duration = sel_s1.get("duration", 1) if sel_s1 else 1

                # Filter pool based on selected faculty
                if sel_t2 == "all_compatible":
                    candidate_pool = [
                        s for s in sessions
                        if s.get("status") != "cancelled" and (sel_s1 is None or s.get("id") != sel_s1.get("id")) and s.get("duration", 1) == req_duration
                    ]
                else:
                    candidate_pool = [
                        s for s in sessions
                        if s.get("teacher_id") == sel_t2 and s.get("status") != "cancelled" and (sel_s1 is None or s.get("id") != sel_s1.get("id")) and s.get("duration", 1) == req_duration
                    ]

                # Filter to only feasible options if checked
                if only_possible and sel_s1:
                    feasible_pool = []
                    for cand in candidate_pool:
                        ok_v, _, _ = APIClient.validate_swap(sel_s1["id"], cand["id"])
                        if ok_v:
                            feasible_pool.append(cand)
                    t2_sessions = feasible_pool
                else:
                    t2_sessions = candidate_pool

                if not t2_sessions:
                    partner_label = "any faculty member" if sel_t2 == "all_compatible" else teachers_dict.get(sel_t2, {}).get("name", sel_t2)
                    st.warning(f"⚠️ No clash-free {req_duration}-hour swap options found with {partner_label} for this session.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    sel_s2 = None
                else:
                    def s2_fmt(s):
                        c_name = classes_dict.get(s.get("class_id"), {}).get("name", s.get("class_id"))
                        t_name = teachers_dict.get(s.get("teacher_id"), {}).get("name", s.get("teacher_id"))
                        return f"✅ {c_name} — {s.get('subject_name', s.get('subject_code'))} | {t_name} ({s.get('day')} P{s.get('period')})"

                    sel_s2 = st.selectbox(
                        f"Session to Swap With ({len(t2_sessions)} Feasible Option{'s' if len(t2_sessions) != 1 else ''})",
                        options=t2_sessions,
                        format_func=s2_fmt,
                        key="swap_session_2"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

            # 3. Swap Validation & Execution
            if sel_s1 and sel_s2:
                st.markdown("<div class='schedulai-card'>", unsafe_allow_html=True)
                st.markdown("##### 3. Bilateral Feasibility Check & Confirmation")

                swap_reason = st.text_input(
                    "Mutual Swap Reason",
                    value="Mutually agreed faculty schedule exchange",
                    key="swap_reason_input"
                )

                # Validate Swap
                ok_val, val_data, val_msg = APIClient.validate_swap(sel_s1["id"], sel_s2["id"])

                if ok_val:
                    st.success(f"✅ Swap Feasible: Exchanging {sel_s1['day']} P{sel_s1['period']} ↔ {sel_s2['day']} P{sel_s2['period']} creates 0 clashes across teacher loads, student classes, and room allocations.")
                    if st.button("🤝 Execute Mutual Swap", type="primary", key="btn_execute_swap"):
                        swap_payload = {
                            "session_1_id": sel_s1["id"],
                            "session_2_id": sel_s2["id"],
                            "requester_teacher_id": sel_t1,
                            "reason": swap_reason
                        }
                        ok_exec, exec_data, exec_msg = APIClient.execute_swap(swap_payload)
                        if ok_exec:
                            st.toast("Swap executed successfully! Timetable updated and notifications dispatched.", icon="🤝")
                            st.rerun()
                        else:
                            st.error(exec_msg)
                else:
                    violations = val_data.get("violations", []) if val_data else []
                    st.error(f"❌ Swap Rejected: {val_msg}")
                    for v in violations:
                        st.markdown(f"- 🛑 {v.get('message', str(v))}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Swap Audit Trail Log
            st.markdown("<div class='schedulai-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            st.markdown("##### Faculty Swap Audit Trail")
            ok_swaps, swaps_data, _ = APIClient.get_swaps()
            swaps_list = swaps_data if (ok_swaps and swaps_data) else []

            if not swaps_list:
                st.info("No teacher swaps recorded yet.")
            else:
                sw_rows = []
                for sw in reversed(swaps_list):
                    t1_n = teachers_dict.get(sw.get("requester_teacher_id"), {}).get("name", sw.get("requester_teacher_id"))
                    t2_n = teachers_dict.get(sw.get("target_teacher_id"), {}).get("name", sw.get("target_teacher_id"))
                    sw_rows.append({
                        "Timestamp": sw.get("created_at", "")[:19].replace("T", " "),
                        "Requester Faculty": t1_n,
                        "Partner Faculty": t2_n,
                        "Session 1": sw.get("session_1_id"),
                        "Session 2": sw.get("session_2_id"),
                        "Status": sw.get("status", "approved").upper(),
                        "Reason": sw.get("reason", "")
                    })
                st.dataframe(pd.DataFrame(sw_rows), use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 5: IN-APP OPERATIONAL NOTIFICATION CENTER
    # =========================================================================
    with tabs[4]:
        st.markdown("#### Institutional Notification Feed")
        st.write("Audit log of real-time alerts dispatched to faculty cohorts and student batches upon lecture cancellations, manual relocations, and AI reschedulings.")

        ok_notif, notif_data, _ = APIClient.get_notifications()
        notifications = notif_data if (ok_notif and notif_data) else []

        if not notifications:
            st.info("🔕 No notifications recorded yet. Cancellations and reschedulings will post notifications here automatically.")
        else:
            cat_filter = st.selectbox(
                "Filter by Category",
                options=["All Categories", "Cancellation", "Reschedule", "Swap", "System"],
                key="notif_cat_filter"
            )

            filtered_notifs = notifications
            if cat_filter != "All Categories":
                filtered_notifs = [n for n in notifications if n.get("category") == cat_filter.lower()]

            st.write(f"Displaying **{len(filtered_notifs)}** notification(s):")

            for n in filtered_notifs:
                cat = n.get("category", "system").lower()
                if cat == "cancellation":
                    badge_class = "badge-danger"
                    icon = "🚫"
                elif cat == "reschedule":
                    badge_class = "badge-success"
                    icon = "🔄"
                elif cat == "swap":
                    badge_class = "badge-warning"
                    icon = "🤝"
                else:
                    badge_class = "badge-neutral"
                    icon = "⚙️"

                # Recipient Name Resolution
                recip = n.get("recipient", "ALL")
                recip_name = recip
                if recip in teachers_dict:
                    recip_name = f"Faculty: {teachers_dict[recip].get('name')}"
                elif recip in classes_dict:
                    recip_name = f"Cohort: {classes_dict[recip].get('name')}"

                st.markdown(
                    f"""
                    <div class="schedulai-card" style="margin-bottom: 0.75rem; padding: 0.85rem 1.1rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="display:flex; align-items:center; gap:0.5rem;">
                                <span class="schedulai-badge {badge_class}">{icon} {cat.title()}</span>
                                <b style="color:#ffffff; font-size:0.92rem;">{n.get('title')}</b>
                            </div>
                            <span style="font-size:0.75rem; color:#94a3b8;">{n.get('timestamp', '')[:19].replace('T', ' ')}</span>
                        </div>
                        <div style="font-size:0.84rem; color:#cbd5e1; margin-top:0.4rem; line-height:1.5;">
                            {n.get('message')}
                        </div>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:0.3rem;">
                            Recipient: <span style="color:#94a3b8;">{recip_name}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # =========================================================================
    # ON-DEMAND LIVE TIMETABLE GRID (Revealed only on button click)
    # =========================================================================
    if "show_ops_timetable" not in st.session_state:
        st.session_state["show_ops_timetable"] = False

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
    ops_btn_label = "🙈 Hide Timetable Grid" if st.session_state["show_ops_timetable"] else "📅 View Updated Timetable Grid"
    ops_btn_type = "secondary" if st.session_state["show_ops_timetable"] else "primary"

    col_btn, _ = st.columns([1.5, 2.5])
    with col_btn:
        if st.button(ops_btn_label, key="btn_toggle_ops_timetable", type=ops_btn_type, use_container_width=True):
            st.session_state["show_ops_timetable"] = not st.session_state["show_ops_timetable"]
            st.rerun()

    if st.session_state["show_ops_timetable"]:
        from frontend.views.timetable_grid import render_timetable_grid
        render_timetable_grid(embedded=True, key_prefix="ops_")
