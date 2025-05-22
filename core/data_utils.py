import json
from datetime import timedelta

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_week_start_date(selected_friday):
    # Calculate the next Monday after the selected Friday
    days_to_next_monday = (7 - selected_friday.weekday() + 0) % 7
    if days_to_next_monday == 0:
        days_to_next_monday = 7  # If Friday is selected (weekday = 4), then +3 days → Monday
    return selected_friday + timedelta(days=days_to_next_monday)
