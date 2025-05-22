# 8216 ABP Yetminster Weekly Rota Planner

A fair and structured rota planning tool for weekly inspector scheduling. Designed using Python and Streamlit.

---

## 📦 Features

- Assigns inspectors to 6 positions (CAR1, HEAD, CAR2, OFFAL, FCI, OFFLINE)
- Prioritizes fairness based on:
  - Last 4 weeks + current week participation
  - FCI/OFFLINE balancing
  - 4+ day workload guarantees
- Prevents same-person same-role repetition in a week
- Allows manual worker selection per day
- Simple interface with auto-saving to history

---

## 🛠 Installation

### Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/8216-rota-planner.git
cd 8216-rota-planner

