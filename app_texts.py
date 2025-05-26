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
- **Different Role Daily**: No one gets the same position twice in a week (unless unavoidable).
- **FCI/OFFLINE Priority**: These roles are assigned fairly using:
   1. Total recent workload (past 4 weeks + current week)
   2. Weekly workload (this week)
   3. Fewer past FCI/OFFLINE roles (if tied)
- **FCI & OFFLINE Combination Allowed**: One person may be given both roles in the same week if needed.
- **Flexible Rule**: Workers with heavier weekly shifts are more likely to get FCI or OFFLINE, but it's not mandatory.
"""

WHATS_NEW = """
**🔄 Cloud Integration**
- All rota records are now stored and retrieved from **Google Sheets** instead of local files.
- Automatic caching added to minimize Google API quota usage.

**🧠 Algorithm Improvements**
- One person can now be assigned both **FCI** and **OFFLINE** in the same week if needed.
- Removed mandatory rule for 4+ day workers to receive FCI/OFFLINE.
- Increased rota generation attempts from 100 → 500.

**📋 Weekly Rota Summary**
- Automatically shows the latest rota on homepage.
- Hides when user selects a different week.

**📈 Monthly Overview**
- Monthly view of FCI and OFFLINE counts per inspector.
- Collapsible interface under the admin panel.

**🗂️ Saved Weekly Rotas**
- Each week is now collapsible.
- Editable directly from the panel.

**🎨 Design Enhancements**
- Stylish header and cleaner overall layout.
- Weekday planner dates displayed more clearly.
- Dividers improved for better visual structure.

**📘 Instruction Updates**
- Sidebar "How to Use" and "Fair Assignment" updated.
- Reflects new logic and week selection starting from Monday.
"""

CHANGELOG_HISTORY = """
### 📝 Version 1.2.0 Stable
- Google Sheets integration for live rota saving
- Algorithm updated (more flexible FCI/OFFLINE rules)
- Automatic rota summary on homepage
- Monthly FCI/OFFLINE overview panel
- Redesigned UI with improved layout and spacing
- Updated instructions and weekly planning logic

### 📝 Version 1.1.0 Stable
**Features:**
- Admin panel with rota editing, backup, and warning system
- Editable rota tables with inline data editor

**Fixes & Improvements:**
- Improved error messages when inspector selection is incomplete
- Prevented duplicate rota generation for existing weeks

**UX Enhancements:**
- Sidebar changelog and version info display
- Conditional hiding of input sections when rota exists

---

### 📝 Version 1.0.0 Beta
**Features:**
- First working rota generation algorithm
- Inspector selection and HEAD assignment UI
- Position assignment logic, validation, and saving system
- Initial stable interface with calendar-based selection
"""

