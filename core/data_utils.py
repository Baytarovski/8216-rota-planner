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
    return selected_friday - timedelta(days=4)  # Friday -> Monday
