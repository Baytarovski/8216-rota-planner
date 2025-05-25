# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

# app.py
# Main Streamlit Application Entry Point

import streamlit as st
from datetime import datetime, timedelta
from core.algorithm import generate_rota
from core.data_utils import load_rotas, save_rotas, delete_rota, get_saved_week_keys
import os
import json
import pandas as pd

# Page setup
st.set_page_config(page_title="8216 ABP Yetminster Weekly Rota Planner", layout="wide")
st.markdown("""
<div style='
    background-color: #e9f1f7;
    border: 2px solid #c7d8e2;
    border-radius: 12px;
    padding: 1.5em;
    text-align:center;
    margin-bottom: 2em;
'>
    <h1 style='margin-bottom: 0.2em; font-size: 2.4em; color: #1a2b44;'>Weekly Rota Management</h1>
    <p style='font-size: 1.15em; color: #3c4c5d;'>8216 ABP Yetminster • Fair & Automated Inspector Scheduling</p>
</div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def cached_load_rotas():
    return load_rotas()

# Load inspectors
inspectors_file = "inspectors.json"
if os.path.exists(inspectors_file):
    with open(inspectors_file, "r") as f:
        inspectors = json.load(f)
else:
    inspectors = []
inspectors = sorted(inspectors)



# ─────────────────────────────────────────────────────────────
# 📚 Sidebar Layout
# ─────────────────────────────────────────────────────────────
import base64

def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_b64 = get_base64_image("assets/logo.png")
st.sidebar.markdown(
    f"<div style='text-align: center; padding: 0.5em 0;'>"
    f"<img src='data:image/png;base64,{logo_b64}' width='160'>"
    f"</div>",
    unsafe_allow_html=True
)


st.sidebar.markdown("---")

with st.sidebar.expander("📘 How to Use", expanded=False):
    st.markdown("""
1. Select the **Monday** of the week you want to plan.  
2. For each weekday, choose exactly **6 unique inspectors**, one of whom is the **HEAD**.  
3. Press **Generate Rota** to assign roles fairly and save the rota automatically.  
4. You can view the current week's rota summary directly on the homepage.  
""")

with st.sidebar.expander("⚖️ How Fair Assignment Works", expanded=False):
    st.markdown("""
- **Different Role Daily**: No one gets the same position twice in a week (unless unavoidable).
- **FCI/OFFLINE Priority**: These roles are assigned fairly using:
   1. Total recent workload (past 4 weeks + current week)
   2. Weekly workload (this week)
   3. Fewer past FCI/OFFLINE roles (if tied)
- **FCI & OFFLINE Combination Allowed**: One person may be given both roles in the same week if needed.
- **Flexible Rule**: Workers with heavier weekly shifts are more likely to get FCI or OFFLINE, but it's not mandatory.
""")

if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))

DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
rotas = cached_load_rotas()

# ─────────────────────────────────────────────────────────────
# 🔐 Admin Panel Access
# ─────────────────────────────────────────────────────────────
with st.sidebar.expander("🔐 Admin Access", expanded=False):
    admin_input = st.text_input("Enter admin password:", type="password")
    if admin_input == "1234":
        st.success("Access granted. Admin panel is now visible.")
        is_admin = True
    elif admin_input != "":
        st.error("Incorrect password.")
        is_admin = False
    else:
        is_admin = False

      

# ─────────────────────────────────────────────────────────────
# 🛠️ Build Info and Creator
# ─────────────────────────────────────────────────────────────

if is_admin:
    st.markdown("<h3 style='margin-bottom:0;'>🛠️ Admin Panel</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)
    
    st.markdown("<h4 style='margin-top:0;'>📅 Saved Weekly Rotas</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)
    week_list = sorted(rotas.keys())
    for wk in week_list:
        with st.expander(f"📆 {wk}"):
            rota_data = rotas[wk]
            rota_df = pd.DataFrame.from_dict(rota_data, orient="index")
            display_days = [d for d in DAYS_FULL if d in rota_df.index or d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]]
            rota_df = rota_df.reindex(display_days)
            rota_df = rota_df[POSITIONS].fillna("")
            edited_df = st.data_editor(rota_df, key=f"edit_{wk}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Save Changes", key=f"save_{wk}"):
                    rotas[wk] = edited_df.to_dict(orient="index")
                    save_rotas(wk, rotas[wk])
                    st.session_state["feedback"] = f"✅ Rota for {wk} updated."
                    st.cache_data.clear()
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Rota", key=f"delete_{wk}_final_unique"):
                    rotas.pop(wk)
                    delete_rota(wk)
                    st.session_state["feedback"] = f"🗑️ Rota for {wk} deleted."
                    st.cache_data.clear()
                    st.rerun()

    st.markdown("<hr style='margin-top:2em; margin-bottom:2em; border: 2px solid #999;'>", unsafe_allow_html=True)

    with st.expander("📈 Monthly FCI/OFFLINE Overview", expanded=False):
        st.markdown("<hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)

        available_months = sorted({datetime.strptime(w, "%Y-%m-%d").strftime("%B %Y") for w in rotas.keys()}, reverse=True)
        selected_month = st.selectbox("📅 Select Month for Summary", available_months)

        summary = {}
        for week_key, week_data in rotas.items():
            week_dt = datetime.strptime(week_key, "%Y-%m-%d")
            if week_dt.strftime("%B %Y") != selected_month:
                continue
            for day, roles in week_data.items():
                for role, person in roles.items():
                    if person == "Not Working":
                        continue
                    if person not in summary:
                        summary[person] = {"Total Days": 0, "FCI": 0, "OFFLINE": 0}
                    summary[person]["Total Days"] += 1
                    if role == "FCI":
                        summary[person]["FCI"] += 1
                    elif role == "OFFLINE":
                        summary[person]["OFFLINE"] += 1
    
        if summary:
            df_summary = pd.DataFrame.from_dict(summary, orient="index")
            df_summary = df_summary.sort_values(by="Total Days", ascending=False)
            st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("<hr style='margin-top:0.5em; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<span style='font-size: 0.95rem;'>Version 1.2.0 Stable — © 2025 Doğukan Dağ</span>", unsafe_allow_html=True)

with st.sidebar.expander("📝 What's New in 1.2.0", expanded=False):
    st.markdown("""
**🔄 Cloud Integration**
- All rota records are now stored and retrieved from **Google Sheets** instead of local files.
- Automatic caching added to minimize Google API quota usage.

**🧠 Algorithm Improvements**
- One person can now be assigned both **FCI** and **OFFLINE** in the same week if needed.
- Removed mandatory rule for 4+ day workers to receive FCI/OFFLINE.
- Increased rota generation attempts from 100 → 500.

**📋 Weekly Rota Summary**
- Automatically shows the latest rota on homepage.
- Hides when user selects a different week.

**📈 Monthly Overview**
- Monthly view of FCI and OFFLINE counts per inspector.
- Collapsible interface under the admin panel.

**🗂️ Saved Weekly Rotas**
- Each week is now collapsible.
- Editable directly from the panel.

**🎨 Design Enhancements**
- Stylish header and cleaner overall layout.
- Weekday planner dates displayed more clearly.
- Dividers improved for better visual structure.

**📘 Instruction Updates**
- Sidebar "How to Use" and "Fair Assignment" updated.
- Reflects new logic and week selection starting from Monday.
""")

with st.sidebar.expander("📚 Changelog History", expanded=False):
    st.markdown("""

### 📝 Version 1.2.0 Stable
- Google Sheets integration for live rota saving
- Algorithm updated (more flexible FCI/OFFLINE rules)
- Automatic rota summary on homepage
- Monthly FCI/OFFLINE overview panel
- Redesigned UI with improved layout and spacing
- Updated instructions and weekly planning logic

### 📝 Version 1.1.0 Stable
**Features:**
- Admin panel with rota editing, backup, and warning system
- Editable rota tables with inline data editor

**Fixes & Improvements:**
- Improved error messages when inspector selection is incomplete
- Prevented duplicate rota generation for existing weeks

**UX Enhancements:**
- Sidebar changelog and version info display
- Conditional hiding of input sections when rota exists

---

### 📝 Version 1.0.0 Beta
**Features:**
- First working rota generation algorithm
- Inspector selection and HEAD assignment UI
- Position assignment logic, validation, and saving system
- Initial stable interface with calendar-based selection
""")

# ─────────────────────────────────────────────────────────────
# ⬇️ Show Latest Rota
# ─────────────────────────────────────────────────────────────
latest_week = max(rotas.keys()) if rotas else None
today = datetime.today().date()

if (
    latest_week
    and datetime.strptime(latest_week, "%Y-%m-%d").date() >= today
    and "selected_monday" not in st.session_state
):
    latest_week_start = datetime.strptime(latest_week, "%Y-%m-%d")
    week_label = f"{latest_week_start.strftime('%d %b')} – {(latest_week_start + timedelta(days=4)).strftime('%d %b %Y')}"

    st.markdown(f"""
    <div style='border:1px solid #d1e7dd; background:#f1fdf7; padding:1em; border-radius:10px; margin-bottom:1.5em;'>
        <p style='margin:0 0 0.5em; font-weight:500;'>📋 <strong>{week_label} Weekly Rota</strong></p>
    """, unsafe_allow_html=True)

    summary_df = pd.DataFrame.from_dict(rotas[latest_week], orient="index")
    summary_df = summary_df.reindex(DAYS_FULL[:5])  # Mon–Fri
    summary_df = summary_df[POSITIONS].fillna("")
    st.dataframe(summary_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# 🔹 Step 1: Select the Week to Plan
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
<h4>1️⃣ Select the Week to Plan</h4>
""", unsafe_allow_html=True)
selected_monday = st.date_input("Select the Monday of the week you want to plan", value=datetime.today())
include_weekend = st.checkbox("Include Saturday and Sunday in this week's rota", value=False)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
if include_weekend:
        days.extend(["Saturday", "Sunday"])
if selected_monday.weekday() != 0:
    st.stop()
week_start = selected_monday

st.markdown("</div>", unsafe_allow_html=True)

# Check for existing rota
week_key = week_start.strftime("%Y-%m-%d")
rota_already_exists = False
if week_key in rotas:
    st.warning(f"A rota already exists for the week starting {week_key}. Displaying saved rota:")
    existing_df = pd.DataFrame.from_dict(rotas[week_key], orient="index")
    
    display_days = [d for d in DAYS_FULL if d in rotas[week_key].keys() or d in DAYS_FULL[:5]]
    existing_df = existing_df.reindex(display_days)
    missing_cols = [c for c in POSITIONS if c not in existing_df.columns]
    if not missing_cols:
        existing_df = existing_df[POSITIONS]
    st.dataframe(existing_df)

    if not is_admin:
        st.stop()
    else:
        rota_already_exists = True



# ─────────────────────────────────────────────────────────────
# 🔹 Step 2: Select Inspectors for Each Day
# ─────────────────────────────────────────────────────────────
if not rota_already_exists:
    st.markdown("""
<div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
<h4>2️⃣ Select Inspectors for Each Day</h4>
""", unsafe_allow_html=True)
    week_range = f"{week_start.strftime('%d %b')} – {(week_start + timedelta(days=4)).strftime('%d %b %Y')}"
    st.markdown(f"<div style='text-align:right; color:#444; font-size:1.05em; margin-top:0.5em; margin-bottom:1em;'>🗓️ Planning Week: <strong>{week_range}</strong></div>", unsafe_allow_html=True)
    daily_workers = {}
    daily_heads = {}
    daily_raw_selected = {}
    daily_raw_head = {}

    for i, day in enumerate(days):
        date_str = (week_start + timedelta(days=i)).strftime('%d %b %Y')
        date_str = (week_start + timedelta(days=i)).strftime('%d %b %Y')
        st.markdown(f"<span style='font-size:1.05em;'>🔹 <strong>{day}</strong> <span style='color:#666; font-size:0.9em;'>({date_str})</span></span>", unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            selected = st.multiselect(f"Select 6 inspectors for {day}", inspectors, key=day)
        with cols[1]:
            head = st.selectbox(f"Select HEAD for {day}", options=selected if len(selected) == 6 else [], key=day+"_head")
        daily_raw_selected[day] = selected
        daily_raw_head[day] = head
        st.markdown("<div style='margin-bottom: 1em;'></div>", unsafe_allow_html=True)
        if len(set(selected)) == 6 and head in selected:
            daily_workers[day] = [w for w in selected if w != head]
            daily_heads[day] = head

    st.markdown("</div>", unsafe_allow_html=True)

    # Validation
    valid_days = []
    invalid_days = []

    for day in days:
        selected = daily_raw_selected.get(day, [])
        head = daily_raw_head.get(day)
        if len(set(selected)) == 6 and head and head in selected:
            valid_days.append(day)
        elif len(selected) > 0 or head:
            invalid_days.append(day)

    active_days = valid_days
    validation_passed = len(valid_days) > 0 and len(invalid_days) == 0
    if invalid_days:
        st.warning(f"⚠️ Incomplete or invalid selections for: {', '.join(invalid_days)}")

# ─────────────────────────────────────────────────────────────
# 🔹 Step 3: Generate the Weekly Rota
# ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
<div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
<h4>3️⃣ Generate the Weekly Rota</h4>
""", unsafe_allow_html=True)

    if validation_passed:
        st.info("✅ Ready to generate rota!")

    if st.button("Generate Rota", disabled=not validation_passed):
        rota_result = generate_rota(
            {day: daily_workers[day] for day in active_days},
            {day: daily_heads[day] for day in active_days},
            rotas, inspectors, week_key
        )
        if isinstance(rota_result, dict) and "error" in rota_result:
            st.error(f"❌ {rota_result['error']}")
            st.stop()
        if not rota_result or not isinstance(rota_result, dict):
            st.error("❌ Rota could not be generated. Please review your selections.")
            st.stop()

        rota_result = {day: roles for day, roles in rota_result.items() if isinstance(roles, dict)}

        for day in days:
            if day not in rota_result:
                rota_result[day] = {
                    "CAR1": "Not Working",
                    "HEAD": "Not Working",
                    "CAR2": "Not Working",
                    "OFFAL": "Not Working",
                    "FCI": "Not Working",
                    "OFFLINE": "Not Working"
                }
        st.success("🎉 Rota saved successfully and added to rota history.")
        

        # Display rota
        
        rota_df = pd.DataFrame.from_dict(rota_result, orient="index")
        rota_df = rota_df.reindex(days)
        missing_columns = [col for col in POSITIONS if col not in rota_df.columns]
        if missing_columns:
            st.warning(f"⚠️ Missing positions in generated rota: {', '.join(missing_columns)}")
        else:
            rota_df = rota_df[POSITIONS]

        st.dataframe(rota_df)
        st.markdown("</div>", unsafe_allow_html=True)

        rota_result = {day: roles for day, roles in rota_result.items() if isinstance(roles, dict)}
        rotas[week_key] = rota_result
        save_rotas(week_key, rota_result)

        
    
