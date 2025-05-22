# app.py
# Main Streamlit Application Entry Point

import streamlit as st
from datetime import datetime, timedelta
from core.algorithm import generate_rota
from core.data_utils import load_json, save_json, get_week_start_date
import os
import json

# Page setup
st.set_page_config(page_title="8216 ABP Yetminster Weekly Rota Planner", layout="wide")
st.title("8216 ABP Yetminster Weekly Rota Planner")

# Load inspectors
inspectors = load_json("inspectors.json", default=[])
inspectors = sorted(inspectors)

# Load existing rotas
rotas = load_json("rotas.json", default={})

# Sidebar layout
st.sidebar.image("assets/logo.png", use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.subheader("📘 How to Use")
st.sidebar.markdown("1. Select the **Friday** before the week you want to plan.\n2. For each weekday, choose exactly **6 unique inspectors**, one of whom is the **HEAD**.\n3. Click **Generate Rota** to assign positions fairly.\n4. The rota will be saved automatically.")
st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ How Fair Assignment Works")
st.sidebar.markdown("""
- **Different Role Daily**: No one gets the same position twice in a week (unless unavoidable).  
- **4+ Days Rule**: Workers scheduled for 4+ days **must** get at least 1 FCI or OFFLINE.  
- **FCI/OFFLINE Priority**: Preference given to those who:
   1. Worked more (last 4 weeks + this week)
   2. Worked more this week (if tied)
   3. Had fewer FCI/OFFLINE roles in the past 4 weeks (if still tied)  
- **Some Repeat Allowed**: FCI and OFFLINE can be given to the same person in one week only if all other rules are satisfied.
""")
st.sidebar.markdown("---")
st.sidebar.caption("Version 0.1.5 Beta — © 2025 Doğukan Dağ")

# --- Date selection ---
st.subheader("1️⃣ Select Friday Before the Target Week")
selected_friday = st.date_input("Select Friday before target week", value=datetime.today())
week_start = get_week_start_date(selected_friday)
st.markdown(f"**Rota Week Starting:** `{week_start.strftime('%A, %d %B %Y')}`")

# --- Existing rota check ---
week_key = week_start.strftime("%Y-%m-%d")
if week_key in rotas:
    st.warning(f"A rota already exists for the week starting {week_key}. Displaying saved rota:")
    st.dataframe(rotas[week_key])
    st.stop()

# --- Daily inspector selection ---
st.subheader("2️⃣ Select Inspectors for Each Day")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
daily_workers = {}
daily_heads = {}
validation_passed = True

for i, day in enumerate(days):
    st.markdown(f"### {day} — { (week_start + timedelta(days=i)).strftime('%d %b %Y') }")
    cols = st.columns(2)
    with cols[0]:
        selected = st.multiselect(f"Select 6 inspectors for {day}", inspectors, key=day)
    with cols[1]:
        head = st.selectbox(f"Select HEAD for {day}", options=selected if len(selected) == 6 else [], key=day+"_head")

    if len(set(selected)) != 6:
        st.error(f"❌ {day}: Exactly 6 unique inspectors must be selected.")
        validation_passed = False
    elif head not in selected:
        st.error(f"❌ {day}: HEAD must be one of the 6 selected inspectors.")
        validation_passed = False
    else:
        daily_workers[day] = selected
        daily_heads[day] = head

# --- Generate Rota ---
st.markdown("---")
st.subheader("3️⃣ Generate the Weekly Rota")
if st.button("Generate Rota") and validation_passed:
    rota_result = generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key)
    st.success("Rota generated successfully!")
    st.dataframe(rota_result)
    # Save rota to history
    rotas[week_key] = rota_result
    save_json("rotas.json", rotas)
