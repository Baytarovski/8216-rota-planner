# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

from collections import defaultdict
from datetime import datetime, timedelta
import random

POSITIONS = ["CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DEFAULT_ATTEMPTS = 1000

# Calculates fairness scores using past 4 weeks + current week's partial assignments
def calculate_fairness_scores(rotas, current_week_key, current_week_assignments):
    position_weights = {
        "CAR1": 0.0, "CAR2": 0.0, "OFFAL": 0.0, "HEAD": 0.0, "FCI": 0.0, "OFFLINE": 0.0
    }
    past_shift_weight = defaultdict(float)
    past_fci_count = defaultdict(int)
    past_offline_count = defaultdict(int)
    past_day_count = defaultdict(int)
    current_shift_weight = defaultdict(float)

    current_date = datetime.strptime(current_week_key, "%Y-%m-%d")
    past_weeks = [(current_date - timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(1, 5)]

    for week_key in past_weeks:
        week_data = rotas.get(week_key, {})
        for day_data in week_data.values():
            unique_people = set(day_data.values())
            for person in unique_people:
                if person:
                    past_day_count[person] += 1
            for position, inspector in day_data.items():
                if inspector:
                    if position == "FCI":
                        past_fci_count[inspector] += 1
                    elif position == "OFFLINE":
                        past_offline_count[inspector] += 1
                    past_shift_weight[inspector] += position_weights.get(position, 0.0)

    # Current week's partial assignment weights (just non-FCI/OFFLINE)
    for day, assignments in current_week_assignments.items():
        for position, inspector in assignments.items():
            if inspector:
                current_shift_weight[inspector] += position_weights.get(position, 0.0)

    all_inspectors = set(past_shift_weight) | set(current_shift_weight) | set(past_fci_count) | set(past_offline_count) | set(past_day_count)
    fairness_scores = {}

    for inspector in all_inspectors:
        score_base = current_shift_weight[inspector] * 1.2
        score_past = past_shift_weight[inspector] * 0.8
        penalty_fci = past_fci_count[inspector] * 1.5
        penalty_offline = past_offline_count[inspector] * 1.5
        bonus_for_attendance = past_day_count[inspector] * 0.6
        fairness_scores[inspector] = {
            "FCI_score": score_base + score_past + bonus_for_attendance - penalty_fci,
            "OFFLINE_score": score_base + score_past + bonus_for_attendance - penalty_offline
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

    for attempt in range(DEFAULT_ATTEMPTS):
        used = defaultdict(list)
        rota_table = {}
        fci_offline_count = defaultdict(int)
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
                        break
                else:
                    success = False
                    break

            if not success:
                break

            rota_table[day] = assignments
            current_week_assignments[day] = assignments

        if success:
            return rota_table

    return {"error": f"Could not generate rota without conflicts after {DEFAULT_ATTEMPTS} attempts."}
