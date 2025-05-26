# © 2025 Doğukan Dağ. All rights reserved.
# This file is protected by copyright law.
# Unauthorized use, copying, modification, or distribution is strictly prohibited.
# Contact: ticked.does-7c@icloud.com

# app_texts.py
# Text blocks for the Streamlit sidebar and UI elements

HOW_TO_USE = """
1. Select the **Monday** of the week you want to plan.  
2. For each weekday, choose exactly **6 unique inspectors**, one of whom is the **HEAD**.  
3. Press **Generate Rota** to assign roles fairly and save the rota automatically.  
4. You can view the current week's rota summary directly on the homepage.  
"""

FAIR_ASSIGNMENT = """
### ⚖️ How Fair Assignment Works

Our rota planner now includes a **semi-AI (rule-guided smart assignment)** engine to fairly distribute lighter reward roles like FCI and OFFLINE.

It analyses:
- Who worked more recently,
- Who has the heavier workload this week,
- And who deserves a break — all with built-in constraints.

This smart logic helps promote fairness without needing full AI.

---

#### 🔄 Weekly Rules:
- Each inspector can only be assigned to a specific position **once per week**
- Each day must have **exactly 6 different inspectors**, including 1 HEAD
- The **HEAD** position is manually assigned and excluded from auto-calculation

---

#### 🟢 FCI & OFFLINE — Reward Positions:
These are lighter, more desirable roles. They are assigned based on:

- **Weekly Load (This Week):** Inspectors who are scheduled to work more days or harder roles this week get priority
- **Historical Load (Last 4 Weeks):** Those who consistently worked more in recent weeks are prioritized
- **Recent Rewards Penalty:** If someone had FCI/OFFLINE too often, their chances decrease

---

#### 🚫 Anti-Repetition Logic:
To promote fairness:
- The system prevents assigning the **same person to the same position on the same weekday** as in the previous week  
  _(e.g., if CU was in CAR1 on Monday last week, they won’t be given CAR1 on Monday this week)_

---

This ensures a rotating, fair, and effort-based schedule — not just random!
"""

WHATS_NEW = """
### 🆕 What's New in Version 1.3.0

🚀 **Major Algorithm Upgrade: Now Semi-AI Powered**

- Our rota generator now uses **smart scoring** to assign FCI and OFFLINE roles more fairly.
- Inspectors with **heavier current workload** or **stronger recent contribution** are rewarded.
- Those who **already received rewards recently** have a lower chance this week.
- HEAD roles are still assigned manually and excluded from fairness scoring.

🧠 **Fairness Logic Improvements**

- The same inspector will no longer be placed in the **same position on the same weekday** two weeks in a row (e.g., no "CAR1 on Monday" two weeks back-to-back).
- The system ensures **no position is repeated within the same week** for any inspector.

🔁 **More Robust Assignment Engine**

- Increased rota generation attempts from **500 → 1000** for higher success rate in complex weeks.
- Improved internal balance between daily and historical workload.

📊 **Clearer Role Distribution**

- The algorithm favors a **rotation-based reward system**, reducing the chances of over-assigning light duties to the same people.

💡 Try generating a rota now — and see the difference in how smart it feels!
"""

CHANGELOG_HISTORY = """
### 🔄 Version History

---

#### 🧠 v1.3.0 — Fairness-Weighted AI Planner (May 2025)
- Introduced **semi-AI algorithm** for FCI & OFFLINE role assignment
- Prioritizes inspectors with higher current and historical workload
- Penalizes inspectors who recently received reward roles (FCI/OFFLINE)
- Prevents assigning the **same position to the same person on the same weekday** as in the previous week
- Ensures fair weekly balance — each position used only once per person per week
- Increased rota generation attempts from **500 → 1000** to improve success rate

---

#### ☁️ v1.2.1 — Google Sheets Integration & Manual Edits
- Full integration with Google Sheets for rota storage
- Editable saved rotas and changelogs in the admin panel
- Manual correction log system enabled

---

#### 🛠️ v1.2.0 — Saved Weekly Rotas & Admin Tools
- Local rota history saved by week
- Admin panel with rota editing, backup, and reset tools
- Redesigned homepage with live rota preview

---

#### 📊 v1.1.0 — Monthly Tracking System Added
- Monthly view for FCI/OFFLINE counts
- Clear overview of reward role fairness over time

---

#### 🎉 v1.0.0 — Initial Release
- Weekly rota planner with basic fair assignment logic
- Unique worker validation, HEAD selection, and CSV output
"""
