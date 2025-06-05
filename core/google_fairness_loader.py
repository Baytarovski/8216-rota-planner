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

# ─── Load and Compute Fairness from Google Sheet ───
def calculate_fairness_summary_from_google_sheet():
    if gspread_client is None:
        st.warning("Google Sheets client not initialized.")
        return {}

    try:
        sheet = gspread_client.open("rota_data").sheet1
        records = sheet.get_all_records()
        df = pd.DataFrame(records)

        df["week_start"] = pd.to_datetime(df["week_start"])
        recent_weeks = sorted(df["week_start"].dt.strftime("%Y-%m-%d").unique())[-4:]
        latest_week = recent_weeks[-1]

        filtered_df = df[df["week_start"].dt.strftime("%Y-%m-%d").isin(recent_weeks)]

        combined_assignments = defaultdict(dict)
        current_week_assignments = defaultdict(dict)

        for _, row in filtered_df.iterrows():
            week_str = row["week_start"].strftime("%Y-%m-%d")
            day_id = f"{week_str}_{row['day']}"

            for role in POSITIONS:
                person = row.get(role, "")
                if person and person.strip() and person != "Not Working":
                    combined_assignments[day_id][role] = person.strip()
                    if week_str == latest_week:
                        current_week_assignments[day_id][role] = person.strip()

        summary = calculate_fairness_scores(current_week_assignments, combined_assignments)
        return summary

    except Exception as e:
        st.error(f"❌ Failed to fetch fairness data from Google Sheets: {e}")
        return {}

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

# ─── Fetch Log Records ───
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
