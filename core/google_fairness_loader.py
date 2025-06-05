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

# ─── Load Fairness Data from Google Sheet ───
def load_fairness_from_google_sheet(sheet):
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    if "Inspector" in df.columns:
        df.set_index("Inspector", inplace=True)
    else:
        df.set_index(df.columns[0], inplace=True)  # fallback
    df.index = df.index.str.strip()  # Remove any trailing spaces in names
    return df

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
