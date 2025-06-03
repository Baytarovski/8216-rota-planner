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

Our rota planner uses a **smart rule-based engine** to fairly assign lighter roles like **FCI** and **OFFLINE**.

It considers:
- 📆 Who is scheduled to work more days this week
- 📊 Who worked more in the past 4 weeks
- 🔁 Who had recent access to FCI or OFFLINE

---

### 📋 Weekly Assignment Rules
- Each inspector can only hold **one position per day**
- Each day must include **6 different inspectors**, including 1 **HEAD**
- **HEAD** is manually assigned and excluded from fairness scoring

---

### 🟢 FCI & OFFLINE – Fair Rotation Roles
These are limited, desirable positions. They are assigned to ensure everyone gets a fair share, based on:

1. **This Week's Schedule**  
   → Inspectors already working more days are less likely to receive FCI or OFFLINE again.

2. **Recent 4-Week History**  
   → Those with a heavier recent workload are prioritised to receive these roles.

3. **Recent Usage Penalty**  
   → If someone had FCI or OFFLINE frequently in the past few weeks, their chance is lowered temporarily.

---

### 🚫 No Repeating Roles
To keep things balanced:
> Inspectors **won’t be assigned the same role on the same weekday** as in the previous week.  
> _(e.g., if AK had CAR2 on Tuesday last week, they won’t get CAR2 on Tuesday this week.)_

---

✅ The system ensures that FCI and OFFLINE roles are **rotated fairly** — not randomly — across the team.
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
