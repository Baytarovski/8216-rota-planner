# app.py
# Main Streamlit Application Entry Point

import streamlit as st
from datetime import datetime, timedelta
from core.algorithm import generate_rota
from core.data_utils import load_json, save_json, get_week_start_date
import os
import json
import pandas as pd
import random

# Page setup
st.set_page_config(page_title="8216 ABP Yetminster Weekly Rota Planner", layout="wide")
st.title("8216 ABP Yetminster Weekly Rota Planner")

# Load inspectors
inspectors = load_json("inspectors.json", default=[])
inspectors = sorted(inspectors)

# Load existing rotas
rotas = load_json("rotas.json", default={})

# Sidebar layout
st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.markdown("---")

with st.sidebar.expander("📘 How to Use", expanded=False):
    st.markdown("""
1. Select the **Friday** before the week you want to plan.  
2. For each weekday, choose exactly **6 unique inspectors**, one of whom is the **HEAD**.  
3. Click **Generate Rota** to assign positions fairly.  
4. The rota will be saved automatically.
""")

with st.sidebar.expander("⚖️ How Fair Assignment Works", expanded=False):
    st.markdown("""
- **Different Role Daily**: No one gets the same position twice in a week (unless unavoidable).  
- **4+ Days Rule**: Workers scheduled for 4+ days **must** get at least 1 FCI or OFFLINE.  
- **FCI/OFFLINE Priority**: Preference given to those:  
   1. Worked more (last 4 weeks + this week)  
   2. Worked more this week (if tied)  
   3. Had fewer FCI/OFFLINE roles in the past 4 weeks (if still tied)  
- **Dual FCI/OFFLINE Allowed**: Same person may be assigned both if no better alternative exists.
""")

# Admin Panel Access
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

st.sidebar.markdown("---")
st.sidebar.caption("Version 0.1.5 Beta — © 2025 Doğukan Dağ")

# Date selection
st.subheader("1️⃣ Select Friday Before the Target Week")
selected_friday = st.date_input("Select Friday before target week", value=datetime.today())
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
week_start = get_week_start_date(selected_friday)

st.markdown(f"**Rota Week Starting:** `{week_start.strftime('%A, %d %B %Y')}`")

# Check for existing rota
week_key = week_start.strftime("%Y-%m-%d")
if week_key in rotas:
    st.warning(f"A rota already exists for the week starting {week_key}. Displaying saved rota:")
    existing_df = pd.DataFrame.from_dict(rotas[week_key], orient="index")
    existing_df = existing_df.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    expected_columns = ["HEAD", "CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]
    missing_cols = [c for c in expected_columns if c not in existing_df.columns]
    if not missing_cols:
        existing_df = existing_df[expected_columns]
    st.dataframe(existing_df)
    st.stop()

# Daily selection
st.subheader("2️⃣ Select Inspectors for Each Day")
daily_workers = {}
daily_heads = {}

for i, day in enumerate(days):
    st.markdown(f"### {day} — { (week_start + timedelta(days=i)).strftime('%d %b %Y') }")
    cols = st.columns(2)
    with cols[0]:
        selected = st.multiselect(f"Select 6 inspectors for {day}", inspectors, key=day)
    with cols[1]:
        head = st.selectbox(f"Select HEAD for {day}", options=selected if len(selected) == 6 else [], key=day+"_head")

    if len(set(selected)) != 6:
        st.error("❌ Exactly 6 unique inspectors must be selected.")
    elif head not in selected:
        st.error("❌ HEAD must be one of the 6 selected inspectors.")
    else:
        daily_workers[day] = [w for w in selected if w != head]
        daily_heads[day] = head

# Validation
validation_passed = all(
    len(daily_workers.get(day, [])) == 5 and daily_heads.get(day)
    for day in days
)

# Generate Rota
st.markdown("---")
st.subheader("3️⃣ Generate the Weekly Rota")

if st.button("Generate Rota", disabled=not validation_passed):
    rota_result = generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key)
    st.success("Rota generated successfully!")

    # Display rota
    rota_df = pd.DataFrame.from_dict(rota_result, orient="index")
    rota_df = rota_df.reindex(days)
    expected_columns = ["HEAD", "CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]
    missing_columns = [col for col in expected_columns if col not in rota_df.columns]
    if missing_columns:
        st.warning(f"⚠️ Missing positions in generated rota: {', '.join(missing_columns)}")
    else:
        rota_df = rota_df[expected_columns]

    st.dataframe(rota_df)

    rotas[week_key] = rota_result
    save_json("rotas.json", rotas)
