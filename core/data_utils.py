# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from typing import Dict
from datetime import datetime

# Google Sheets bağlantısı
SHEET_NAME = "rota_data"
DELETED_SHEET_NAME = "deleted_rota"

POSITIONS = ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    gc = gspread.authorize(credentials)
    return gc.open(SHEET_NAME).sheet1

def get_deleted_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    gc = gspread.authorize(credentials)
    return gc.open(DELETED_SHEET_NAME).sheet1

def save_rotas(week_key: str, rota_dict: Dict[str, Dict[str, str]]):
    sheet = get_sheet()
    existing = sheet.get_all_values()
    header = ["week_start", "day"] + POSITIONS

    # Header yoksa ekle
    if not existing:
        sheet.append_row(header)

    # Eski haftayı sil
    rows_to_keep = [row for row in existing if len(row) >= 1 and (row[0] != week_key or row[0] == "week_start")]
    sheet.clear()
    for row in rows_to_keep:
        sheet.append_row(row)

    # Yeni haftayı ekle
    for day, roles in rota_dict.items():
        row = [week_key, day] + [roles.get(pos, "") for pos in POSITIONS]
        sheet.append_row(row)

from datetime import datetime

def load_rotas():
    sheet = get_sheet()
    rows = sheet.get_all_values()
    all_rotas = {}

    if not rows or rows[0][:2] != ["week_start", "day"]:
        return all_rotas

    for row in rows[1:]:
        if len(row) < 3:
            continue
        week, day, *assignments = row
        try:
            # Normalize week format
            parsed_week = datetime.strptime(week.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            parsed_week = week.strip()
        if parsed_week not in all_rotas:
            all_rotas[parsed_week] = {}
        all_rotas[parsed_week][day] = dict(zip(["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"], assignments))

    return all_rotas

def delete_rota(week_key: str):
    sheet = get_sheet()
    rows = sheet.get_all_values()
    deleted_data = {}
    for row in rows:
        if len(row) >= 2 and row[0] == week_key and row[0] != "week_start":
            day = row[1]
            roles = dict(zip(POSITIONS, row[2:2 + len(POSITIONS)]))
            deleted_data[day] = roles

    rows_to_keep = [row for row in rows if row[0] != week_key or row[0] == "week_start"]
    sheet.clear()
    for row in rows_to_keep:
        sheet.append_row(row)

    return deleted_data

def archive_deleted_rota(week_key: str, rota_dict: Dict[str, Dict[str, str]], admin_user: str):
    sheet = get_deleted_sheet()
    existing = sheet.get_all_values()
    header = ["week_start", "day"] + POSITIONS + ["admin_users"]
    if not existing:
        sheet.append_row(header)
    for day, roles in rota_dict.items():
        row = [week_key, day] + [roles.get(pos, "") for pos in POSITIONS] + [admin_user]
        sheet.append_row(row)

def get_saved_week_keys():
    rotas = load_rotas()
    return list(rotas.keys())
