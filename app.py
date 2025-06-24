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
from core.utils import generate_table_image
from weekly_rota_generation import (
    select_week,
    select_daily_inspectors,
    validate_selection,
    generate_and_display_rota,
    check_existing_rota
)

# ─────────────────────────────────────────────
# 🌐 App Setup
# ─────────────────────────────────────────────
st.set_page_config(page_title="8216 ABP Yetminster Weekly Rota Planner", layout="wide")

st.session_state.setdefault("is_admin", False)

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
POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]

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
    st.sidebar.markdown("<span style='font-size:0.95rem;'>Version 1.3.5 Stable — © 2025 Doğukan Dağ</span>", unsafe_allow_html=True)
    with st.sidebar.expander("📝 What's New in 1.3.0", expanded=False):
        st.markdown(WHATS_NEW)
    with st.sidebar.expander("📚 Changelog History", expanded=False):
        st.markdown(CHANGELOG_HISTORY)

# ─────────────────────────────────────────────
# 🔐 Admin Login
# ─────────────────────────────────────────────
def admin_login():
    if st.session_state.get("is_admin"):
        return

    st.info("🔐 Enter the access code below to unlock rota planning tools.")
    code_input = st.text_input("Access Code:", type="password", key="access_code")

    if code_input == "17500#":
        st.session_state["is_admin"] = True
        st.success("Access granted. Planning tools unlocked.")
    elif code_input:
        st.session_state["is_admin"] = False
        st.error("Incorrect code.")

# ─────────────────────────────────────────────
# 🔄 Display Latest Rota
# ─────────────────────────────────────────────

def display_latest_rota(rotas):
    from datetime import datetime, timedelta
    import pandas as pd
    import streamlit as st

    rotas = cached_load_rotas()

    DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
    today = datetime.today().date()

    future_rotas = {
        date_str: rota for date_str, rota in rotas.items()
        if datetime.strptime(date_str, "%Y-%m-%d").date() + timedelta(days=4) >= today
    }

    latest_week = max(future_rotas.keys()) if future_rotas else None

    if latest_week:
        latest_week_start = datetime.strptime(latest_week, "%Y-%m-%d")
        week_label = f"{latest_week_start.strftime('%d %b')} – {(latest_week_start + timedelta(days=4)).strftime('%d %b %Y')}"

        summary_df = pd.DataFrame.from_dict(future_rotas[latest_week], orient="index")
        saturday_exists = "Saturday" in summary_df.index and summary_df.loc["Saturday"].replace("", pd.NA).dropna().any()

        display_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if saturday_exists:
            display_days.append("Saturday")

        summary_df = summary_df.reindex(display_days)[POSITIONS].fillna("")


              # 📸 PNG Image + Download Button
        image_buf = generate_table_image(summary_df, title=f"{week_label} Weekly Rota")
        st.image(image_buf, use_container_width=True)
        st.download_button(
            label="📥 Download Rota",
            data=image_buf,
            file_name=f"rota_{latest_week}.png",
            mime="image/png"
        )
    else:
        st.info("📭 No rota available for this week or upcoming weeks.")


# ─────────────────────────────────────────────
# 🚀 App Entry
# ─────────────────────────────────────────────
render_sidebar()
display_latest_rota(rotas)
admin_login()

if not st.session_state.get("is_admin", False):
    st.stop()

# 🔁 Weekly Rota Planning
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

