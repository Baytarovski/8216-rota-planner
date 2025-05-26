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
from app_texts import HOW_TO_USE, FAIR_ASSIGNMENT, WHATS_NEW, CHANGELOG_HISTORY
from admin_panel import render_admin_panel
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


@st.cache_data
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

from app_texts import HOW_TO_USE, FAIR_ASSIGNMENT

with st.sidebar.expander("📘 How to Use", expanded=False):
    st.markdown(HOW_TO_USE)

with st.sidebar.expander("⚖️ How Fair Assignment Works", expanded=False):
    st.markdown(FAIR_ASSIGNMENT)


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
        st.session_state["is_admin"] = True
    elif admin_input != "":
        st.error("Incorrect password.")
        st.session_state["is_admin"] = False

# ─────────────────────────────────────────────────────────────
# 🛠️ Admin Panel
# ─────────────────────────────────────────────────────────────

if st.session_state.get("is_admin", False):
    render_admin_panel(rotas, save_rotas, delete_rota)

# ─────────────────────────────────────────────────────────────
# 🛠️ Build Info and Creator
# ─────────────────────────────────────────────────────────────
    
st.markdown("<hr style='margin-top:0.5em; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<span style='font-size: 0.95rem;'>Version 1.2.0 Stable — © 2025 Doğukan Dağ</span>", unsafe_allow_html=True)

with st.sidebar.expander("📝 What's New in 1.2.0", expanded=False):
    st.markdown(WHATS_NEW)

with st.sidebar.expander("📚 Changelog History", expanded=False):
    st.markdown(CHANGELOG_HISTORY)

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
    if week_key != latest_week:
        st.warning(f"A rota already exists for the week starting {week_key}. Displaying saved rota:")
        existing_df = pd.DataFrame.from_dict(rotas[week_key], orient="index")

        display_days = [d for d in DAYS_FULL if d in rotas[week_key].keys() or d in DAYS_FULL[:5]]
        existing_df = existing_df.reindex(display_days)
        missing_cols = [c for c in POSITIONS if c not in existing_df.columns]
        if not missing_cols:
            existing_df = existing_df[POSITIONS]
        st.dataframe(existing_df)
    else:
        # 💡 Rota bugünkü hafta ve zaten yukarıda gösterildi
        st.info("ℹ️ A rota already exists for the selected week and is displayed at the top.")

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

        rota_df = pd.DataFrame.from_dict(rota_result, orient="index")
        rota_df = rota_df.reindex(days)
        if all(pos in rota_df.columns for pos in POSITIONS):
            rota_df = rota_df[POSITIONS]
        else:
            st.warning("⚠️ Missing positions in generated rota")

        st.dataframe(rota_df)
        st.markdown("</div>", unsafe_allow_html=True)

        # 💾 SAVE ROTAS
        rotas[week_key] = rota_result
        save_rotas(week_key, rota_result)

        # 🔄 CLEAR CACHE + RELOAD
        st.cache_data.clear()
        st.rerun()

    
