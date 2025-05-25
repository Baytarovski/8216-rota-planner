# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

import random
from collections import defaultdict

POSITIONS = ["CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DEFAULT_ATTEMPTS = 500

def generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key):
    all_days = list(daily_workers.keys())
    worker_days = defaultdict(int)
    week_roles = defaultdict(list)

    # Count how many days each worker is scheduled this week
    for day in all_days:
        for worker in daily_workers[day]:
            worker_days[worker] += 1

    # Analyze recent rota history to count past FCI/OFFLINE roles
    recent_fci = defaultdict(int)
    recent_offline = defaultdict(int)
    recent_total = defaultdict(int)

    for prev_week, rota in rotas.items():
        for day, roles in rota.items():
            for pos, name in roles.items():
                if name not in inspectors:
                    continue
                recent_total[name] += 1
                if pos == "FCI":
                    recent_fci[name] += 1
                elif pos == "OFFLINE":
                    recent_offline[name] += 1

    # Determine the dynamic threshold: e.g., 80% of total available days
    total_days = len(all_days)
    threshold = max(1, int(total_days * 0.8))

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

            # Sort candidates with dynamic priority
            def sort_key(w):
                return (
                    -int(worker_days[w] >= threshold and fci_offline_count[w] == 0),  # prioritized if meeting threshold and didn't get FCI/OFFLINE yet
                    recent_fci[w] + recent_offline[w],
                    worker_days[w],
                    random.random()
                )

            sorted_workers = sorted(day_workers, key=sort_key)
            assignments = {"HEAD": head}
            available = set(sorted_workers)

            for pos in POSITIONS:
                for candidate in sorted_workers:
                    if candidate in available and pos not in used[candidate]:
                        if pos in ["FCI", "OFFLINE"] and fci_offline_count[candidate] >= 1:
                            continue  # soft constraint: max one of FCI/OFFLINE per week
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

        if success:
            return rota_table

    return {"error": f"Could not generate rota without conflicts after {DEFAULT_ATTEMPTS} attempts."}
