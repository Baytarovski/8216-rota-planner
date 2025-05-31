# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

import streamlit as st
import gspread
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from google.oauth2.service_account import Credentials
from io import BytesIO
from core.algorithm import calculate_fairness_scores
import matplotlib.pyplot as plt

# ─── Constants ───
POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DAYS_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ─── Google Sheets Authorization ───
try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    gspread_client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Google Sheets authorization failed: {e}")
    gspread_client = None

# ─── Table Image Generator ───
def generate_table_image(df):
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.6 + 1))
    ax.axis('off')
    tbl = ax.table(cellText=df.values,
                   colLabels=df.columns,
                   rowLabels=df.index,
                   loc='center',
                   cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.2)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf

# ─── Google Sheet Log Functions ───
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

# ─── Admin Panel ───
def render_admin_panel(rotas, save_rotas, delete_rota):
    if not st.session_state.get("is_admin", False):
        return

    st.markdown("<h3 style='margin-bottom:0;'>🛠️ Admin Panel</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)

    if st.button("🔄 Clear Cached Data"):
        st.cache_data.clear()
        st.success("✅ Cache cleared. Please refresh the page manually.")

    st.markdown("<h4 style='margin-top:0;'>📁 Saved Weekly Rotas</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)
    week_list = sorted(rotas.keys())

    for wk in week_list:
        with st.expander(f"🔗️ {wk}"):
            rota_data = rotas[wk]
            rota_df = pd.DataFrame.from_dict(rota_data, orient="index")

            saturday_exists = "Saturday" in rota_df.index and rota_df.loc["Saturday"].replace("", pd.NA).dropna().any()
            display_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            if saturday_exists:
                display_days.append("Saturday")

            rota_df = rota_df.reindex(display_days)[POSITIONS].fillna("")

            image_buf = generate_table_image(rota_df)
            st.image(image_buf, caption=f"📸 Rota Table for the week of {wk}", use_container_width=True)
            st.download_button(
                label="📥 Download Rota",
                data=image_buf,
                file_name=f"rota_{wk}.png",
                mime="image/png",
                key=f"download_{wk}"
            )

            edited_df = st.data_editor(rota_df, key=f"edit_{wk}")
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("📂 Save Changes", key=f"save_{wk}"):
                    original = rota_df.fillna("")
                    new = edited_df.fillna("")
                    for day in display_days:
                        for pos in POSITIONS:
                            old_val = original.at[day, pos]
                            new_val = new.at[day, pos]
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
                    rotas[wk] = new.to_dict(orient="index")
                    save_rotas(wk, rotas[wk])
                    st.session_state["feedback"] = f"✅ Rota for {wk} updated."
                    st.cache_data.clear()
                    st.rerun()

            with col2:
                if st.button("🗑️ Delete Rota", key=f"delete_{wk}_final_unique"):
                    append_to_google_sheet({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "admin_id": "admin",
                        "week_start": wk,
                        "day": "-",
                        "position": "-",
                        "old_value": "Full rota deleted",
                        "new_value": "-"
                    })
                    rotas.pop(wk)
                    delete_rota(wk)
                    st.session_state["feedback"] = f"🗑️ Rota for {wk} deleted."
                    st.cache_data.clear()
                    st.rerun()

    # Monthly Summary Section
    st.markdown("<hr style='margin-top:2em; margin-bottom:2em; border: 2px solid #999;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0;'>📊 Monthly Assignment Summary</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)

    with st.expander("📈 Monthly FCI/OFFLINE Overview", expanded=False):
        available_months = sorted({datetime.strptime(w, "%Y-%m-%d").strftime("%B %Y") for w in rotas.keys()}, reverse=True)
        selected_month = st.selectbox("🗕️ Select a Month", available_months)

        summary = {}
        month_week_keys = [
            wk for wk in rotas.keys()
            if datetime.strptime(wk, "%Y-%m-%d").strftime("%B %Y") == selected_month
        ]

        if month_week_keys:
            first_month_date = min(datetime.strptime(wk, "%Y-%m-%d") for wk in month_week_keys)
            additional_weeks = [
                (first_month_date - timedelta(weeks=i)).strftime("%Y-%m-%d")
                for i in range(1, 4)
            ]
            combined_weeks = additional_weeks + month_week_keys
        else:
            combined_weeks = []

        combined_assignments = defaultdict(dict)
        for wk in combined_weeks:
            week_data = rotas.get(wk, {})
            for day, roles in week_data.items():
                for role, person in roles.items():
                   if person and person != "Not Working":
                        if person not in summary:
                            summary[person] = {"Total Days": 0, "FCI": 0, "OFFLINE": 0}
                        summary[person]["Total Days"] += 1
                        if role == "FCI":
                            summary[person]["FCI"] += 1
                        elif role == "OFFLINE":
                            summary[person]["OFFLINE"] += 1

                        unique_day = f"{wk}_{day}"
                        combined_assignments[unique_day][role] = person

        if summary and month_week_keys:
            latest_week = max(month_week_keys)
            fairness_scores = calculate_fairness_scores(rotas, latest_week, combined_assignments)

            df_summary = pd.DataFrame.from_dict(summary, orient="index")
            df_summary["FCI Score"] = df_summary.index.map(lambda name: round(fairness_scores.get(name, {}).get("FCI_score", 0), 2))
            df_summary["OFFLINE Score"] = df_summary.index.map(lambda name: round(fairness_scores.get(name, {}).get("OFFLINE_score", 0), 2))
            df_summary["Total Weighted Score"] = df_summary["FCI Score"] + df_summary["OFFLINE Score"]
            df_summary = df_summary.sort_values(by="Total Weighted Score", ascending=False)

            st.dataframe(df_summary, use_container_width=True)

    # Logs Section
    st.markdown("<hr style='margin-top:2em; margin-bottom:2em; border: 2px solid #999;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0;'>🗓️ System Activity & Logs</h4><hr style='margin-top:0.3em; margin-bottom:1em;'>", unsafe_allow_html=True)

    logs = fetch_logs_from_google_sheet()
    if not logs:
        st.info("No manual edits recorded.")
        return
        
    st.markdown("<hr style='margin-top:0; margin-bottom:1em; border: 2px solid black;'>", unsafe_allow_html=True)

    df = pd.DataFrame(logs)
    week_options = sorted(df["week_start"].unique(), reverse=True)
    selected_week = st.selectbox("Select Week", week_options)
    filtered = df[df["week_start"] == selected_week]
    st.dataframe(filtered[["timestamp", "day", "position", "old_value", "new_value"]])

