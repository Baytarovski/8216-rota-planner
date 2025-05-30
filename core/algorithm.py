# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

from collections import defaultdict
from datetime import datetime, timedelta
import random
import streamlit as st

st.cache_data.clear()

POSITIONS = ["CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DEFAULT_ATTEMPTS = 1000
MIN_REQUIRED_DAYS_FOR_FCI_OFFLINE = 2

FCI_PENALTY = 1.5
OFFLINE_PENALTY = 1.5
ATTENDANCE_BONUS = 0.6

# Calculates fairness scores using past 4 weeks + current week's partial assignments
def calculate_fairness_scores(rotas, current_week_key, current_week_assignments):
    past_fci_count = defaultdict(int)
    past_offline_count = defaultdict(int)
    past_day_count = defaultdict(int)

    all_weeks = sorted(rotas.keys(), reverse=True)
    current_date = datetime.strptime(current_week_key, "%Y-%m-%d")
    parsed_weeks = [w for w in all_weeks if datetime.strptime(w, "%Y-%m-%d") <= current_date]
    past_weeks = parsed_weeks[:4]

    
    for week_key in past_weeks:
        week_data = rotas.get(week_key, {})
        for day_data in week_data.values():
            for role, person in day_data.items():
                if person and person != "Not Working":
                    past_day_count[person] += 1
                    if role == "FCI":
                        past_fci_count[person] += 1
                    elif role == "OFFLINE":
                        past_offline_count[person] += 1

    # 🔁 INCLUDE CURRENT WEEK
    for day, assignments in current_week_assignments.items():
        for role, person in assignments.items():
            if person and person != "Not Working":
                past_day_count[person] += 1
                if role == "FCI":
                    past_fci_count[person] += 1
                elif role == "OFFLINE":
                    past_offline_count[person] += 1

    all_inspectors = set(past_day_count) | set(past_fci_count) | set(past_offline_count)
    fairness_scores = {}

    for inspector in all_inspectors:
        bonus = past_day_count[inspector] * ATTENDANCE_BONUS
        penalty_fci = past_fci_count[inspector] * FCI_PENALTY
        penalty_offline = past_offline_count[inspector] * OFFLINE_PENALTY


        fairness_scores[inspector] = {
            "FCI_score": bonus - penalty_fci,
            "OFFLINE_score": bonus - penalty_offline
        }

    return fairness_scores

# Prevents same-day repeat of role from last week

def get_last_week_same_day_restrictions(rotas, current_week_key):
    restrictions = defaultdict(dict)
    current_date = datetime.strptime(current_week_key, "%Y-%m-%d")
    last_week_key = (current_date - timedelta(weeks=1)).strftime("%Y-%m-%d")
    last_week_data = rotas.get(last_week_key, {})

    for day, positions in last_week_data.items():
        for pos, person in positions.items():
            if person:
                restrictions[day][pos] = person

    return restrictions

# Main rota generator
def generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key):
    all_days = list(daily_workers.keys())
    worker_days = defaultdict(int)
    current_week_assignments = {}

    for day in all_days:
        current_week_assignments[day] = {"HEAD": daily_heads[day]}
        for worker in daily_workers[day]:
            worker_days[worker] += 1

    fairness_scores = calculate_fairness_scores(rotas, week_key, current_week_assignments)
    same_day_block = get_last_week_same_day_restrictions(rotas, week_key)

    # En iyi 3 FCI/Offline skoruna sahip kişileri belirle
    all_scores = defaultdict(float)
    for person in fairness_scores:
        all_scores[person] = fairness_scores[person].get("FCI_score", 0) + fairness_scores[person].get("OFFLINE_score", 0)
    top3 = sorted(all_scores, key=all_scores.get, reverse=True)[:3]
    top3 = [p for p in top3 if worker_days[p] > 0]

    for attempt in range(DEFAULT_ATTEMPTS):
        used = defaultdict(list)
        rota_table = {}
        fci_offline_count = defaultdict(int)
        assigned_top3 = set()
        success = True

        for day in all_days:
            day_workers = daily_workers[day][:]
            head = daily_heads[day]
            if head in day_workers:
                day_workers.remove(head)
            random.shuffle(day_workers)

            assignments = {"HEAD": head}
            current_week_assignments[day].update(assignments)
            available = set(day_workers)

            for pos in POSITIONS:
                eligible = [w for w in day_workers if pos not in used[w]]
                if pos in ["FCI", "OFFLINE"]:
                    eligible = [w for w in eligible if worker_days[w] >= MIN_REQUIRED_DAYS_FOR_FCI_OFFLINE]
                    eligible = sorted(
                        eligible,
                        key=lambda w: -fairness_scores.get(w, {}).get(f"{pos}_score", 0) + random.random() * 0.01
                    )
                else:
                    random.shuffle(eligible)

                for candidate in eligible:
                    if candidate in available:
                        if pos in ["FCI", "OFFLINE"] and fci_offline_count[candidate] >= 2:
                            continue
                        if same_day_block.get(day, {}).get(pos) == candidate:
                            continue
                        assignments[pos] = candidate
                        used[candidate].append(pos)
                        if pos in ["FCI", "OFFLINE"]:
                            fci_offline_count[candidate] += 1
                        available.remove(candidate)
                        if candidate in top3:
                            assigned_top3.add(candidate)
                        break
                else:
                    success = False
                    break

            if not success:
                break

            rota_table[day] = assignments
            current_week_assignments[day] = assignments

        if success and assigned_top3.issuperset(top3):
            return rota_table

    return {"error": f"Could not generate rota without conflicts after {DEFAULT_ATTEMPTS} attempts."}
