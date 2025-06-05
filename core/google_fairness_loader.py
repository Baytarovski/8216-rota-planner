import pandas as pd
from datetime import datetime
from collections import defaultdict
from core.algorithm import calculate_fairness_summary

def load_fairness_from_google_sheet(sheet):
    """
    Loads rota assignments from a Google Sheet and calculates fairness scores
    based on the most recent 4 weeks of data.

    Parameters:
        sheet (gspread.models.Spreadsheet): The Google Sheet containing rota data.

    Returns:
        dict: A dictionary of fairness scores per person.
    """
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    # Convert 'week_start' to datetime and sort
    df["week_start"] = pd.to_datetime(df["week_start"])
    recent_weeks = sorted(df["week_start"].unique())[-4:]
    filtered_df = df[df["week_start"].isin(recent_weeks)]

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

    latest_week = max(recent_weeks).strftime("%Y-%m-%d")
    return calculate_fairness_summary({}, latest_week, combined_assignments)
