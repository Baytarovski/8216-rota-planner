# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

import json
from datetime import datetime
import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

LOG_FILE = "data/change_logs.json"
POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "service_account.json"
SHEET_NAME = "change_logs"

def append_to_google_sheet(log_entry):
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        sheet.append_row([
            log_entry["timestamp"],
            log_entry["admin_id"],
            log_entry["week_start"],
            log_entry["day"],
            log_entry["position"],
            log_entry["old_value"],
            log_entry["new_value"]
        ])
    except Exception as e:
        st.warning(f"Google Sheets error: {e}")

def fetch_logs_from_google_sheet():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        records = sheet.get_all_records()
        return records
    except Exception as e:
        st.warning(f"Google Sheets read error: {e}")
        return []

def render_admin_panel(rotas, save_rotas, delete_rota):
    st.markdown("<h3 style='margin-bottom:0;'>🛠️ Admin Panel</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)

    st.markdown("<h4 style='margin-top:0;'>🗕️ Saved Weekly Rotas</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)
    week_list = sorted(rotas.keys())
    for wk in week_list:
        with st.expander(f"🗖️ {wk}"):
            rota_data = rotas[wk]
            rota_df = pd.DataFrame.from_dict(rota_data, orient="index")
            display_days = [d for d in DAYS_FULL if d in rota_df.index or d in DAYS_FULL]
            rota_df = rota_df.reindex(display_days)
            rota_df = rota_df[POSITIONS].fillna("")
            edited_df = st.data_editor(rota_df, key=f"edit_{wk}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📂 Save Changes", key=f"save_{wk}"):
                    original = pd.DataFrame.from_dict(rota_data, orient="index").reindex(display_days).fillna("")
                    new = edited_df.fillna("")

                    for day in DAYS_FULL:
                        if day not in new.index or day not in original.index:
                            continue
                        for pos in POSITIONS:
                            old_val = original.at[day, pos] if pos in original.columns else ""
                            new_val = new.at[day, pos] if pos in new.columns else ""
                            if old_val != new_val:
                                append_to_google_sheet({
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "admin_id": "admin",
                                    "week_start": wk,
                                    "day": day,
                                    "position": pos,
                                    "old_value": old_val,
                                    "new_value": new_val
                                })

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
        selected_month = st.selectbox("🗕️ Select Month for Summary", available_months)

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

    st.subheader("📋 Change History (Manual Edits)")
    logs = fetch_logs_from_google_sheet()
    if not logs:
        st.info("No manual edits recorded.")
        return

    df = pd.DataFrame(logs)
    week_options = sorted(df["week_start"].unique(), reverse=True)
    selected_week = st.selectbox("Select Week", week_options)
    filtered = df[df["week_start"] == selected_week]
    st.dataframe(filtered[["timestamp", "day", "position", "old_value", "new_value"]])
