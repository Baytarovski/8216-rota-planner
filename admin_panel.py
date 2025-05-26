# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────
# 🔧 Constants
# ─────────────────────────────────────────────
POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ─────────────────────────────────────────────
# 🔐 Google Sheets Authorization
# ─────────────────────────────────────────────
try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    gspread_client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Google Sheets authorization failed: {e}")
    gspread_client = None

# ─────────────────────────────────────────────
# 📤 Append Change to Google Sheet
# ─────────────────────────────────────────────
def append_to_google_sheet(log_entry):
    if gspread_client is None:
        return
    try:
        sheet = gspread_client.open("change_logs").sheet1
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

# ─────────────────────────────────────────────
# 📥 Fetch Logs from Google Sheet
# ─────────────────────────────────────────────
def fetch_logs_from_google_sheet():
    if gspread_client is None:
        return []
    try:
        sheet = gspread_client.open("change_logs").sheet1
        records = sheet.get_all_records()
        return records
    except Exception as e:
        st.warning(f"Google Sheets read error: {e}")
        return []

# ─────────────────────────────────────────────
# 🛠️ Admin Panel Renderer
# ─────────────────────────────────────────────
def render_admin_panel(rotas, save_rotas, delete_rota):
    if not st.session_state.get("is_admin", False):
        return

    # ── Header
    st.markdown("<h3 style='margin-bottom:0;'>🛠️ Admin Panel</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)

    # ── Section: Saved Weekly Rotas
    st.markdown("<h4 style='margin-top:0;'>📅 Saved Weekly Rotas</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)
    week_list = sorted(rotas.keys())
    for wk in week_list:
        with st.expander(f"🗖️ {wk}"):
            rota_data = rotas[wk]
            rota_df = pd.DataFrame.from_dict(rota_data, orient="index")
            display_days = [d for d in DAYS_FULL if d in rota_df.index or d in DAYS_FULL]
            rota_df = rota_df.reindex(display_days)[POSITIONS].fillna("")

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

    # ── Section: Monthly Assignment Summary
    st.markdown("<h4 style='margin-top:0;'>📊 Monthly Assignment Summary</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)
    with st.expander("📈 Monthly FCI/OFFLINE Overview", expanded=False):
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

    st.markdown("<hr style='margin-top:2em; margin-bottom:2em; border: 2px solid #999;'>", unsafe_allow_html=True)

    # ── Section: Logs
    st.markdown("<h4 style='margin-top:0;'>🗃️ System Activity & Logs</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)
    logs = fetch_logs_from_google_sheet()
    if not logs:
        st.info("No manual edits recorded.")
        return

    df = pd.DataFrame(logs)
    week_options = sorted(df["week_start"].unique(), reverse=True)
    selected_week = st.selectbox("Select Week", week_options)
    filtered = df[df["week_start"] == selected_week]
    st.dataframe(filtered[["timestamp", "day", "position", "old_value", "new_value"]])
