# 8216 ABP Yetminster Weekly Rota Planner

A professional rota assignment tool designed for fair weekly planning of inspector shifts. Built with Streamlit.

---

## ⚙️ Features

✅ 6 daily roles (CAR1, HEAD, CAR2, OFFAL, FCI, OFFLINE)  
✅ Manual selection of inspectors for each weekday  
✅ HEAD selected manually; others assigned fairly  
✅ Fairness rules based on weekly and historical participation  
✅ Priority given to those with higher workload  
✅ FCI/OFFLINE balancing across 4 weeks  
✅ 4+ day workers guaranteed one FCI or OFFLINE role  
✅ No same person same role in a week (if avoidable)  
✅ Auto-save of rota history in `rotas.json`

---

## 🚀 Live Demo

If deployed on Streamlit Cloud:  
📎 https://your-app-name.streamlit.app

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/8216-rota-planner.git
cd 8216-rota-planner
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New app**.
4. Connect your GitHub repo and choose `app.py` as the main file.
5. Click **Deploy**.

---

## 📁 File Structure

```
├── app.py                # Main Streamlit app
├── core/
│   ├── algorithm.py      # Role assignment logic
│   └── data_utils.py     # JSON and date helpers
├── inspectors.json       # List of inspectors
├── rotas.json            # Weekly rota history
├── assets/
│   └── logo.png          # Your company logo (optional)
├── requirements.txt
└── README.md
```

---

## 🧑‍💼 Author

Developed by **Doğukan Dağ (Marco)**  
MIT License — 2025
