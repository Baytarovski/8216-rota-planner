# © 2025 Doğukan Dağ. All rights reserved.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com
# weekly_rota_generation.py

# 📅 Weekly Rota Selection & Generation

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.algorithm import generate_rota
from core.data_utils import save_rotas
import matplotlib.pyplot as plt
from io import BytesIO
from core.utils import generate_table_image


DAYS_ALL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]

def select_week():
    st.markdown("""
    <div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
    <h4>1️⃣ Select the Week to Plan</h4>
    """, unsafe_allow_html=True)

    selected_monday = st.date_input("Select the Monday of the week you want to plan", value=datetime.today())
    include_weekend = st.checkbox("Include Saturday and Sunday in this week's rota", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

    if selected_monday.weekday() != 0:
        st.warning("Please select a Monday.")
        st.stop()

    week_days = DAYS_ALL[:5] + DAYS_ALL[5:] if include_weekend else DAYS_ALL[:5]
    return selected_monday, week_days

def select_daily_inspectors(week_start, days, inspectors):
    st.markdown("""
    <div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
    <h4>2️⃣ Select Inspectors for Each Day</h4>
    """, unsafe_allow_html=True)

    week_range = f"{week_start.strftime('%d %b')} – {(week_start + timedelta(days=4)).strftime('%d %b %Y')}"
    st.markdown(f"<div style='text-align:right; color:#444; font-size:1.05em; margin-top:0.5em; margin-bottom:1em;'>🗓️ Planning Week: <strong>{week_range}</strong></div>", unsafe_allow_html=True)

    daily_workers, daily_heads = {}, {}
    daily_raw_selected, daily_raw_head = {}, {}

    for i, day in enumerate(days):
        date_str = (week_start + timedelta(days=i)).strftime('%d %b %Y')
        st.markdown(f"<span style='font-size:1.05em;'>🔹 <strong>{day}</strong> <span style='color:#666; font-size:0.9em;'>({date_str})</span></span>", unsafe_allow_html=True)

        cols = st.columns(2)

        with cols[0]:
            selected = st.session_state.get(day, [])
            available_options = [i for i in inspectors if i in selected or len(selected) < 6]

            updated_selected = st.multiselect(
                f"Select up to 6 inspectors for {day}",
                options=available_options,
                default=selected,
                key=f"{day}_select"
            )

            if updated_selected != selected:
                st.session_state[day] = updated_selected

            if len(updated_selected) == 6:
                st.info("✅ You have selected 6 inspectors. To change, remove one first.")
            elif len(updated_selected) > 6:
                st.warning("⚠️ Please select only 6 inspectors.")

        with cols[1]:
            head = st.selectbox(f"Select HEAD for {day}", options=selected if len(selected) == 6 else [], key=day+"_head")

        daily_raw_selected[day] = updated_selected
        daily_raw_head[day] = head

        if updated_selected and head and len(set(updated_selected)) == 6 and head in updated_selected:
            daily_workers[day] = [w for w in selected if w != head]
            daily_heads[day] = head

        st.markdown("<div style='margin-bottom: 1em;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    return daily_workers, daily_heads, daily_raw_selected, daily_raw_head

def validate_selection(days, raw_selected, raw_head):
    valid_days, invalid_days = [], []
    for day in days:
        selected = raw_selected.get(day, [])
        head = raw_head.get(day)
        if len(set(selected)) == 6 and head and head in selected:
            valid_days.append(day)
        elif selected or head:
            invalid_days.append(day)
    return valid_days, invalid_days

def generate_and_display_rota(valid_days, daily_workers, daily_heads, rotas, inspectors, week_key, full_day_list):
    st.markdown("---")
    st.markdown("""
    <div style='border:1px solid #ccc; border-radius:10px; padding:1em; background:#f9f9f9; margin-bottom:1.5em;'>
    <h4>3️⃣ Generate the Weekly Rota</h4>
    """, unsafe_allow_html=True)

    st.info("✅ Ready to generate rota!")

    if st.button("Generate Rota"):
        rota_result = generate_rota(
            {day: daily_workers[day] for day in valid_days},
            {day: daily_heads[day] for day in valid_days},
            rotas, inspectors, week_key
        )

        if isinstance(rota_result, dict) and "error" in rota_result:
            st.error(f"❌ {rota_result['error']}")
            st.stop()

        if not rota_result or not isinstance(rota_result, dict):
            st.error("❌ Rota could not be generated. Please review your selections.")
            st.stop()

        for day in full_day_list:
            if day not in rota_result:
                rota_result[day] = {pos: "Not Working" for pos in POSITIONS}

        st.success("🎉 Rota saved successfully and added to rota history.")

        rota_df = pd.DataFrame.from_dict(rota_result, orient="index")
        rota_df = rota_df.reindex(full_day_list)
        if all(pos in rota_df.columns for pos in POSITIONS):
            rota_df = rota_df[POSITIONS]
        else:
            st.warning("⚠️ Missing positions in generated rota")

        st.dataframe(rota_df)
        st.markdown("</div>", unsafe_allow_html=True)

        # 🔽 PNG olarak indirme bölümü
        image_buf = generate_table_image(rota_df)
        st.image(image_buf, caption="📸 Oluşturulan Rota Tablosu (PNG)", use_container_width=True)
        st.download_button(
            label="📥 Rota Tablosunu PNG Olarak İndir",
            data=image_buf,
            file_name=f"rota_{week_key}.png",
            mime="image/png"
        )

        # Verileri kaydet
        rotas[week_key] = rota_result
        save_rotas(week_key, rota_result)

        st.cache_data.clear()
        st.rerun()

def check_existing_rota(week_key, rotas, selected_monday, is_admin, all_days, positions):
    rota_exists = False
    latest_week = max(rotas.keys()) if rotas else None
    latest_week_date = datetime.strptime(latest_week, "%Y-%m-%d").date() if latest_week else None

    if week_key in rotas:
        if selected_monday == latest_week_date:
            st.info("ℹ️ A rota already exists for the selected week and is displayed at the top.")
        else:
            st.warning(f"A rota already exists for the week starting {week_key}. Displaying saved rota:")
            existing_df = pd.DataFrame.from_dict(rotas[week_key], orient="index")
            display_days = [d for d in all_days if d in rotas[week_key].keys() or d in all_days[:5]]
            existing_df = existing_df.reindex(display_days)

            for col in positions:
                if col not in existing_df.columns:
                    existing_df[col] = ""

            existing_df = existing_df[positions]
            st.dataframe(existing_df)

        if not is_admin:
            st.stop()
        else:
            rota_exists = True
    return rota_exists
