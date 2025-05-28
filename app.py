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
import uuid
import matplotlib.pyplot as plt
from io import BytesIO

def generate_table_image(df, title=None):
    
    fig_height = len(df) * 0.6 + 2 if title else len(df) * 0.6 + 1
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.axis('off')

    # ✅ Add title if provided
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)

    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        rowLabels=df.index,
        loc='center',
        cellLoc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.2)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf

from core.algorithm import generate_rota
from core.data_utils import load_rotas, save_rotas, delete_rota, get_saved_week_keys
from app_texts import HOW_TO_USE, FAIR_ASSIGNMENT, WHATS_NEW, CHANGELOG_HISTORY
from admin_panel import render_admin_panel
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
    st.sidebar.markdown("<span style='font-size:0.95rem;'>Version 1.3.0 Stable — © 2025 Doğukan Dağ</span>", unsafe_allow_html=True)
    with st.sidebar.expander("📝 What's New in 1.3.0", expanded=False):
        st.markdown(WHATS_NEW)
    with st.sidebar.expander("📚 Changelog History", expanded=False):
        st.markdown(CHANGELOG_HISTORY)

# ─────────────────────────────────────────────
# 🔐 Admin Login
# ─────────────────────────────────────────────
def admin_login():
    with st.sidebar.expander("🔐 Admin Access", expanded=False):
        admin_input = st.text_input("Enter admin password:", type="password", key="admin_password")
        if admin_input == "1234":
            st.session_state["is_admin"] = True
            st.success("Access granted. Admin panel is now visible.")
        elif admin_input:
            st.session_state["is_admin"] = False
            st.error("Incorrect password.")

# ─────────────────────────────────────────────
# 🔄 Display Latest Rota
# ─────────────────────────────────────────────

def display_latest_rota(rotas):
    from datetime import datetime, timedelta
    import pandas as pd
    import streamlit as st
    
    rotas = cached_load_rotas()

    DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
    today = datetime.today().date()

    future_rotas = {
        date_str: rota for date_str, rota in rotas.items()
        if datetime.strptime(date_str, "%Y-%m-%d").date() + timedelta(days=4) >= today
    }

    if st.session_state.get("is_admin", False):
        st.write("📦 Upcoming valid rotas:", list(future_rotas.keys()))

    latest_week = max(future_rotas.keys()) if future_rotas else None

    if latest_week:
        latest_week_start = datetime.strptime(latest_week, "%Y-%m-%d")
        week_label = f"{latest_week_start.strftime('%d %b')} – {(latest_week_start + timedelta(days=4)).strftime('%d %b %Y')}"

        summary_df = pd.DataFrame.from_dict(future_rotas[latest_week], orient="index")
        summary_df = summary_df.reindex(DAYS_FULL)[POSITIONS].fillna("")
        
              # 📸 PNG Image + Download Button
        image_buf = generate_table_image(summary_df)
        st.image(image_buf, caption=f"📸 {week_label} Weekly Rota Table", use_container_width=True)
        st.download_button(
            label="📥 Download Rota",
            data=image_buf,
            file_name=f"rota_{latest_week}.png",
            mime="image/png"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("📭 No rota available for this week or upcoming weeks.")


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
