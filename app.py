# app.py
# Main Streamlit Application Entry Point

import streamlit as st
from datetime import datetime, timedelta
from core.algorithm import generate_rota
from core.data_utils import load_json, save_json, get_week_start_date
import os
import json
import pandas as pd

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
- **FCI/OFFLINE Priority**: Preference given to those who:  
   1. Worked more (last 4 weeks + this week)  
   2. Worked more this week (if tied)  
   3. Had fewer FCI/OFFLINE roles in the past 4 weeks (if still tied)  
- **Dual FCI/OFFLINE Allowed**: Same person may be assigned both if no better alternative exists.
""")

# --- Admin Panel Access ---
with st.sidebar.expander("🔐 Admin Access", expanded=False):
    admin_input = st.text_input("Enter admin password:", type="password")
    if admin_input == "1234":  # Sabit admin şifresi
        st.success("Access granted. Admin panel is now visible.")
        is_admin = True
    elif admin_input != "":
        st.error("Incorrect password.")
        is_admin = False
    else:
        is_admin = False

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

    existing_rota = rotas[week_key]
    existing_df = pd.DataFrame.from_dict(existing_rota, orient="index")
    existing_df = existing_df.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    existing_df = existing_df[["HEAD", "CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]]

    st.dataframe(existing_df)
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

# --- Validation ---
validation_passed = True
validation_errors = []

for day in days:
    workers = daily_workers.get(day, [])
    head = daily_heads.get(day)

    if len(workers) != 6:
        validation_passed = False
        validation_errors.append(f"{day}: Exactly 6 workers must be selected.")

    if not head or head.strip() == "":
        validation_passed = False
        validation_errors.append(f"{day}: HEAD must be selected.")

# Hataları kullanıcıya göster
if not validation_passed:
    for err in validation_errors:
        st.error(err)

# --- Buton ve rota üretimi ---
if st.button("Generate Rota", disabled=not validation_passed):
    rota_result = generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key)
    st.success("Rota generated successfully!")

    # Rota'yı günler satırda, pozisyonlar sütunda olacak şekilde düzenle
    rota_df = pd.DataFrame.from_dict(rota_result, orient="index")
    rota_df = rota_df.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    rota_df = rota_df[["HEAD", "CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]]

    st.dataframe(rota_df)

    # Kaydet
    rotas[week_key] = rota_result
    save_json("rotas.json", rotas)


