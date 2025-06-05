# core/google_fairness_loader.py

import pandas as pd
from datetime import datetime
from collections import defaultdict
from core.algorithm import calculate_fairness_summary

def load_fairness_from_google_sheet(sheet):
    # 1. Veriyi çek
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    # 2. Tarihleri ayarla
    df["week_start"] = pd.to_datetime(df["week_start"])
    recent_weeks = sorted(df["week_start"].unique())[-4:]  # Son 4 hafta

    # 3. Bu haftalardaki verileri filtrele
    filtered_df = df[df["week_start"].isin(recent_weeks)]

    # 4. combined_assignments sözlüğünü oluştur
    combined_assignments = defaultdict(dict)
    for _, row in filtered_df.iterrows():
        key = f"{row['week_start'].strftime('%Y-%m-%d')}_{row['day']}"
        combined_assignments[key] = {
            "CAR1": row.get("CAR1", ""),
            "CAR2": row.get("CAR2", ""),
            "OFFAL": row.get("OFFAL", ""),
            "FCI": row.get("FCI", ""),
            "OFFLINE": row.get("OFFLINE", "")
        }

    # 5. En güncel haftayı bul
    latest_week = max(recent_weeks).strftime("%Y-%m-%d")

    # 6. Puanları hesapla
    return calculate_fairness_summary({}, latest_week, combined_assignments)
