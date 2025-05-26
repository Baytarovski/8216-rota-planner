# © 2025 Doğukan Dağ. All rights reserved.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

# app.py — Main Streamlit Application Entry Point

import os
import json
import base64
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.algorithm import generate_rota
from core.data_utils import load_rotas, save_rotas, delete_rota, get_saved_week_keys
from app_texts import HOW_TO_USE, FAIR_ASSIGNMENT, WHATS_NEW, CHANGELOG_HISTORY
from admin_panel import render_admin_panel
from weekly_rota_generation import (
    select_week,
    select_daily_inspectors,
    validate_selection,
    generate_and_display_rota
)

# ─────────────────────────────────────────────
# 🌐 App Setup
# ─────────────────────────────────────────────
st.set_page_config(page_title="8216 ABP Yetminster Weekly Rota Planner", layout="wide")

st.markdown("""
<div style='background-color:#e9f1f7; border:2px solid #c7d8e2; border-radius:12px; padding:1.5em; text-align:center; margin-bottom:2em;'>
    <h1 style='margin-bottom:0.2em; font-size:2.4em; color:#1a2b44;'>Weekly Rota Management</h1>
    <p style='font-size:1.15em; color:#3c4c5d;'>8216 ABP Yetminster • Fair & Automated Inspector Scheduling</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🧑‍💼 Load Inspectors & Rotas
# ─────────────────────────────────────────────
def get_inspectors():
    inspectors_file = "inspectors.json"
    if os.path.exists(inspectors_file):
        with open(inspectors_file, "r") as f:
            return sorted(json.load(f))
    return []

@st.cache_data
def cached_load_rotas():
    return load_rotas()

inspectors = get_inspectors()
rotas = cached_load_rotas()

# ─────────────────────────────────────────────
# 📚 Sidebar
# ─────────────────────────────────────────────
def render_sidebar():
    def get_base64_image(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    logo_b64 = get_base64_image("assets/logo.png")
    st.sidebar.markdown(f"<div style='text-align:center; padding:0.5em 0;'><img src='data:image/png;base64,{logo_b64}' width='160'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    with st.sidebar.expander("📘 How to Use", expanded=False):
        st.markdown(HOW_TO_USE)
    with st.sidebar.expander("⚖️ How Fair Assignment Works", expanded=False):
        st.markdown(FAIR_ASSIGNMENT)
    st.sidebar.markdown("---")
    st.sidebar.markdown("<span style='font-size:0.95rem;'>Version 1.2.1 Stable — © 2025 Doğukan Dağ</span>", unsafe_allow_html=True)
    with st.sidebar.expander("📝 What's New in 1.2.0", expanded=False):
        st.markdown(WHATS_NEW)
    with st.sidebar.expander("📚 Changelog History", expanded=False):
        st.markdown(CHANGELOG_HISTORY)

# 📌 Admin Login Block

def admin_login():
    with st.sidebar.expander("🔐 Admin Access", expanded=False):
        admin_input = st.text_input("Enter admin password:", type="password", key="admin_password_input_sidebar")
        if admin_input == "1234":
            st.success("Access granted. Admin panel is now visible.")
            st.session_state["is_admin"] = True
        elif admin_input:
            st.error("Incorrect password.")
            st.session_state["is_admin"] = False


# ─────────────────────────────────────────────
# 🔄 Display Latest Rota
# ─────────────────────────────────────────────
def display_latest_rota(rotas):
    DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
    latest_week = max(rotas.keys()) if rotas else None
    today = datetime.today().date()

    if latest_week and datetime.strptime(latest_week, "%Y-%m-%d").date() >= today and "selected_monday" not in st.session_state:
        latest_week_start = datetime.strptime(latest_week, "%Y-%m-%d")
        week_label = f"{latest_week_start.strftime('%d %b')} – {(latest_week_start + timedelta(days=4)).strftime('%d %b %Y')}"

        st.markdown(f"""
        <div style='border:1px solid #d1e7dd; background:#f1fdf7; padding:1em; border-radius:10px; margin-bottom:1.5em;'>
            <p style='margin:0 0 0.5em; font-weight:500;'>📋 <strong>{week_label} Weekly Rota</strong></p>
        """, unsafe_allow_html=True)
        summary_df = pd.DataFrame.from_dict(rotas[latest_week], orient="index")
        summary_df = summary_df.reindex(DAYS_FULL)[POSITIONS].fillna("")
        st.dataframe(summary_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🚀 App Entry
# ─────────────────────────────────────────────
render_sidebar()
admin_login()

if st.session_state.get("is_admin", False):
    render_admin_panel(rotas, save_rotas, delete_rota)

display_latest_rota(rotas)

if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))

# 🚀 App Entry (devamı)
render_sidebar()
admin_login()

if st.session_state.get("is_admin", False):
    render_admin_panel(rotas, save_rotas, delete_rota)

display_latest_rota(rotas)

if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))

# 🔁 Weekly Rota Planning
from weekly_rota_generation import (
    select_week,
    select_daily_inspectors,
    validate_selection,
    generate_and_display_rota,
    check_existing_rota
)

selected_monday, days = select_week()
week_key = selected_monday.strftime("%Y-%m-%d")

rota_already_exists = check_existing_rota(
    week_key=week_key,
    rotas=rotas,
    selected_monday=selected_monday,
    is_admin=st.session_state.get("is_admin", False),
    all_days=days,
    positions=POSITIONS
)

if not rota_already_exists:
    daily_workers, daily_heads, raw_selected, raw_head = select_daily_inspectors(selected_monday, days, inspectors)
    valid_days, invalid_days = validate_selection(days, raw_selected, raw_head)

    if invalid_days:
        st.warning(f"⚠️ Incomplete or invalid selections for: {', '.join(invalid_days)}")

    if valid_days and not invalid_days:
        generate_and_display_rota(valid_days, daily_workers, daily_heads, rotas, inspectors, week_key, days)


# 🔁 Weekly Rota Planning
selected_monday, days = select_week()
week_key = selected_monday.strftime("%Y-%m-%d")

if week_key in rotas and week_key != max(rotas.keys()):
    st.warning(f"A rota already exists for the week starting {week_key}. Displaying saved rota:")
    existing_df = pd.DataFrame.from_dict(rotas[week_key], orient="index")
    existing_df = existing_df.reindex(days)
    if all(col in existing_df.columns for col in POSITIONS):
        existing_df = existing_df[POSITIONS]
    st.dataframe(existing_df)
    if not st.session_state.get("is_admin", False):
        st.stop()

daily_workers, daily_heads, raw_selected, raw_head = select_daily_inspectors(selected_monday, days, inspectors)
valid_days, invalid_days = validate_selection(days, raw_selected, raw_head)

if invalid_days:
    st.warning(f"⚠️ Incomplete or invalid selections for: {', '.join(invalid_days)}")

if valid_days and not invalid_days:
    generate_and_display_rota(valid_days, daily_workers, daily_heads, rotas, inspectors, week_key, days)
