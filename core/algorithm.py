import random
from collections import defaultdict

POSITIONS = ["CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]
DEFAULT_ATTEMPTS = 100

def generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key):
    all_days = list(daily_workers.keys())
    worker_days = defaultdict(int)
    week_roles = defaultdict(list)

    for day in all_days:
        for worker in daily_workers[day]:
            worker_days[worker] += 1

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

    for _ in range(DEFAULT_ATTEMPTS):
        used = defaultdict(list)
        rota_table = {}
        fci_offline_count = defaultdict(int)
        success = True

        for day in all_days:
            # Skip if it's a Bank Holiday / No Work day
            if daily_heads[day] is None and daily_workers[day] == []:
                rota_table[day] = {pos: "No Work" for pos in ["CAR1", "HEAD", "CAR2", "OFFAL", "FCI", "OFFLINE"]}
                continue

            day_workers = daily_workers[day][:]
            head = daily_heads[day]
            if head in day_workers:
                day_workers.remove(head)
            random.shuffle(day_workers)

            def sort_key(w):
                return (
                    -(worker_days[w] + recent_total[w]),
                    -worker_days[w],
                    recent_fci[w] + recent_offline[w],
                    random.random()
                )

            sorted_workers = sorted(day_workers, key=sort_key)
            assignments = {"HEAD": head}
            available = set(sorted_workers)

            for pos in POSITIONS:
                for candidate in sorted_workers:
                    if candidate in available and pos not in used[candidate]:
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

        for worker, days in worker_days.items():
            if days >= 4 and fci_offline_count[worker] == 0:
                success = False
                break

        if success:
            return rota_table

    return {"error": "Could not generate rota without conflicts after 100 attempts."}
