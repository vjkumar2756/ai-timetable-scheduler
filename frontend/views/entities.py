"""
frontend/views/entities.py
Entity Management View for Subjects, Teachers, Classes, Rooms, and Time Structure.
"""
import streamlit as st
import json
import pandas as pd
from frontend.theme import page_header
from frontend.api_client import APIClient

def render_entities_page():
    page_header(
        title="Manage Institutional Entities",
        subtitle="Configure curriculum subjects, faculty availability, student cohorts, and classroom infrastructure"
    )

    st.warning("⚠️ Institutional Warning: Adding, updating, or deactivating entities will mark the active timetable outdated. Please regenerate after modifications.")

    tabs = st.tabs(["📚 Subjects", "👨‍🏫 Faculty", "🎓 Classes", "🏛️ Rooms & Labs", "⏱️ Time Structure", "📥 Import / Export"])

    # 1. Subjects Tab
    with tabs[0]:
        st.markdown("#### Course Curriculum & Modules")
        ok_s, subjects, _ = APIClient.get_subjects()
        if ok_s and subjects:
            df_s = pd.DataFrame(subjects)[["id", "code", "name", "weekly_hours", "type", "lab_duration"]]
            st.dataframe(df_s, use_container_width=True)

        with st.expander("➕ Register New Subject"):
            with st.form("create_subject_form"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    s_id = st.text_input("Subject ID / Code*", placeholder="e.g. CS201")
                    s_name = st.text_input("Subject Title*", placeholder="e.g. Artificial Intelligence")
                with sc2:
                    s_hours = st.number_input("Weekly Hours Required*", min_value=1, max_value=10, value=3)
                    s_type = st.selectbox("Subject Type", options=["theory", "lab"])
                    s_dur = 2 if s_type == "lab" else 1

                if st.form_submit_button("Create Subject"):
                    if s_id and s_name:
                        payload = {
                            "id": s_id.strip(), "code": s_id.strip(), "name": s_name.strip(),
                            "weekly_hours": int(s_hours), "type": s_type, "lab_duration": s_dur
                        }
                        ok, _, msg = APIClient.create_subject(payload)
                        if ok:
                            st.success(f"Subject '{s_id}' registered successfully.")
                            st.rerun()
                        else:
                            st.error(f"Failed to create subject: {msg}")
                    else:
                        st.error("Please fill in both Subject ID and Title.")

    # 2. Teachers Tab
    with tabs[1]:
        st.markdown("#### Faculty Members & Teaching Loads")
        ok_t, teachers, _ = APIClient.get_teachers()
        if ok_t and teachers:
            # Flatten subjects for table view
            t_data = []
            for t in teachers:
                t_data.append({
                    "ID": t.get("id"),
                    "Name": t.get("name"),
                    "Eligible Subjects": ", ".join(t.get("subject_ids", [])),
                    "Max Weekly Load": f"{t.get('max_weekly_load', 0)}h",
                    "Unavailable Slots": len(t.get("unavailable_slots", [])),
                    "Status": "Active" if t.get("active", True) else "Inactive"
                })
            st.dataframe(pd.DataFrame(t_data), use_container_width=True)

        with st.expander("➕ Register New Faculty Member"):
            with st.form("create_teacher_form"):
                tc1, tc2 = st.columns(2)
                with tc1:
                    t_id = st.text_input("Faculty ID*", placeholder="e.g. T07")
                    t_name = st.text_input("Full Name*", placeholder="e.g. Dr. Alan Turing")
                    t_subs = st.text_input("Eligible Subject IDs (comma-separated)", placeholder="e.g. CS101, CS104L")
                with tc2:
                    t_load = st.number_input("Max Weekly Teaching Load (Hours)", min_value=5, max_value=30, value=18)
                    t_unavail_day = st.selectbox("Unavailable Day", options=["None", "Mon", "Tue", "Wed", "Thu", "Fri"])
                    t_unavail_period = st.number_input("Unavailable Period", min_value=1, max_value=8, value=1)

                if st.form_submit_button("Register Faculty"):
                    if t_id and t_name:
                        unavail = []
                        if t_unavail_day != "None":
                            unavail.append({"day": t_unavail_day, "period": int(t_unavail_period)})

                        sub_list = [s.strip() for s in t_subs.split(",") if s.strip()]
                        payload = {
                            "id": t_id.strip(), "name": t_name.strip(),
                            "subject_ids": sub_list, "max_weekly_load": int(t_load),
                            "unavailable_slots": unavail, "preferred_slots": [], "active": True
                        }
                        ok, _, msg = APIClient.create_teacher(payload)
                        if ok:
                            st.success(f"Faculty member '{t_name}' registered successfully.")
                            st.rerun()
                        else:
                            st.error(f"Failed to register faculty: {msg}")
                    else:
                        st.error("Please provide Faculty ID and Name.")

    # 3. Classes Tab
    with tabs[2]:
        st.markdown("#### Student Cohorts & Curriculum Requirements")
        ok_c, classes, _ = APIClient.get_classes()
        if ok_c and classes:
            c_data = []
            for c in classes:
                reqs = ", ".join([f"{k}: {v}h" for k, v in c.get("subject_requirements", {}).items()])
                c_data.append({
                    "Class ID": c.get("id"),
                    "Cohort Name": c.get("name"),
                    "Strength": c.get("strength"),
                    "Lunch Period": f"Period {c.get('lunch_break_period', 4)}",
                    "Subject Requirements": reqs,
                    "Total Hours": sum(c.get("subject_requirements", {}).values())
                })
            st.dataframe(pd.DataFrame(c_data), use_container_width=True)

        with st.expander("➕ Register New Student Class"):
            with st.form("create_class_form"):
                cc1, cc2 = st.columns(2)
                with cc1:
                    cls_id = st.text_input("Class ID*", placeholder="e.g. CSE_4C")
                    cls_name = st.text_input("Cohort Name*", placeholder="e.g. B.Tech CSE 4th Sem (C)")
                    cls_strength = st.number_input("Student Strength (Students)", min_value=10, max_value=150, value=50)
                with cc2:
                    cls_lunch = st.number_input("Lunch Break Period*", min_value=1, max_value=7, value=4)
                    cls_reqs = st.text_input("Curriculum Requirements (e.g. CS101:3, CS104L:2)", placeholder="CS101:3, CS102:3")

                if st.form_submit_button("Register Class"):
                    if cls_id and cls_name:
                        req_dict = {}
                        if cls_reqs:
                            for pair in cls_reqs.split(","):
                                if ":" in pair:
                                    k, v = pair.split(":")
                                    req_dict[k.strip()] = int(v.strip())

                        payload = {
                            "id": cls_id.strip(), "name": cls_name.strip(),
                            "strength": int(cls_strength), "lunch_break_period": int(cls_lunch),
                            "subject_requirements": req_dict, "active": True
                        }
                        ok, _, msg = APIClient.create_class(payload)
                        if ok:
                            st.success(f"Class '{cls_name}' registered successfully.")
                            st.rerun()
                        else:
                            st.error(f"Failed to create class: {msg}")

    # 4. Rooms Tab
    with tabs[3]:
        st.markdown("#### Rooms, Lecture Halls & Practical Labs")
        ok_r, rooms, _ = APIClient.get_rooms()
        if ok_r and rooms:
            df_r = pd.DataFrame(rooms)[["id", "name", "capacity", "type", "active"]]
            st.dataframe(df_r, use_container_width=True)

        with st.expander("➕ Register New Room or Lab"):
            with st.form("create_room_form"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    r_id = st.text_input("Room ID*", placeholder="e.g. LT7")
                    r_name = st.text_input("Room Name*", placeholder="e.g. Lecture Theater 7")
                with rc2:
                    r_cap = st.number_input("Seating Capacity", min_value=10, max_value=300, value=65)
                    r_type = st.selectbox("Facility Type", options=["classroom", "lab"])

                if st.form_submit_button("Register Room"):
                    if r_id and r_name:
                        payload = {
                            "id": r_id.strip(), "name": r_name.strip(),
                            "capacity": int(r_cap), "type": r_type, "active": True
                        }
                        ok, _, msg = APIClient.create_room(payload)
                        if ok:
                            st.success(f"Room '{r_name}' registered successfully.")
                            st.rerun()
                        else:
                            st.error(f"Failed to create room: {msg}")

    # 5. Time Structure Tab
    with tabs[4]:
        st.markdown("#### Working Days & Period Structure")
        ok_set, settings_dict, _ = APIClient.get_settings()
        if ok_set and settings_dict:
            with st.form("settings_form"):
                s_days = st.multiselect("Working Days", options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], default=settings_dict.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri"]))
                s_periods = st.slider("Periods Per Day", min_value=4, max_value=10, value=settings_dict.get("periods_per_day", 6))
                s_lunch = st.number_input("Default Institutional Lunch Period", min_value=1, max_value=s_periods, value=settings_dict.get("default_lunch_period", 4))

                if st.form_submit_button("Update Institutional Settings"):
                    payload = {"days": s_days, "periods_per_day": s_periods, "default_lunch_period": s_lunch}
                    ok, _, msg = APIClient.update_settings(payload)
                    if ok:
                        st.success("Institutional settings updated.")
                        st.rerun()
                    else:
                        st.error(f"Failed to update settings: {msg}")

    # 6. Import / Export Tab
    with tabs[5]:
        st.markdown("#### Dataset Import & Export")
        st.write("Export your active institutional dataset as JSON, or upload a JSON file with full solvability pre-flight checks.")

        iec1, iec2 = st.columns(2)
        with iec1:
            st.markdown("##### Export Active Configuration")
            ok_exp, exp_data, _ = APIClient.export_dataset_json()
            if ok_exp and exp_data:
                json_str = json.dumps(exp_data, indent=2)
                st.download_button(
                    label="⬇️ Download Dataset (JSON)",
                    data=json_str,
                    file_name="schedulai_dataset.json",
                    mime="application/json",
                    use_container_width=True
                )

        with iec2:
            st.markdown("##### Import JSON Dataset")
            uploaded_file = st.file_uploader("Upload .json file", type=["json"])
            if uploaded_file is not None:
                try:
                    raw_data = json.load(uploaded_file)
                    if st.button("Apply & Import Uploaded JSON", type="primary"):
                        ok_imp, imp_res, imp_msg = APIClient.import_dataset_json(raw_data)
                        if ok_imp:
                            st.success(imp_msg)
                            st.rerun()
                        else:
                            st.error(f"Import Rejected: {imp_msg}")
                except Exception as e:
                    st.error(f"Invalid JSON syntax: {str(e)}")
