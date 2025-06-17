# dashboard_swetcha_helpline

# 📞 Exotel Call Dashboard

A Streamlit-based dashboard for analyzing Exotel call logs. This tool allows users to upload multiple CSVs, visualize call data day-wise and week-wise, view detailed summaries, generate heatmaps, and export data.

---

## ✅ Features

- 🔐 User authentication with secure login
- 📁 Upload and store multiple CSV files
- 🗓️ Toggle between daily and weekly views
- 📅 Interactive calendar for date filtering
- 📊 Bar and pie charts for call statuses
- 📈 Stacked bar chart for answered/missed calls by day
- 🌡️ Heatmap of call volume (hour vs day)
- 🏆 Leaderboards for answered and missed calls
- 🔍 Search by volunteer name
- 📤 Export filtered data to CSV
- ❌ One-click clear all uploaded files

---

## 📂 How to Run

### 1. Clone the Repo

```bash
git clone : https://github.com/Rounak885/dashboard_swetcha
cd exotel-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.streamlit/secrets.toml`

```toml
COOKIE_SIGNING_KEY = "yoursecretkey"

[credentials]
usernames = ["admin"]
admin = {name="Admin", password="1234", email="admin@example.com"}
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## 📊 Required CSV Columns

Ensure each CSV file contains:

- `StartTime` — Timestamp of call
- `Status` — Call status (`completed`, `missed-call`, etc.)
- `Leg1Status` — Call leg status
- `ToName` — Volunteer name
- `ConversationDuration` — Duration in seconds

---

## 🖼️ Visualizations

- Call status distribution (Bar + Pie)
- Daily/weekly call summary
- Stacked bar chart: Answered vs Missed
- Hourly heatmap of call volume
- Leaderboards by volunteer

---

## 🧪 Example Usage

1. Login with credentials (`admin` / `1234`)
2. Upload multiple Exotel CSV files
3. Use calendar to filter by date
4. View summaries and charts
5. Export filtered data as CSV
6. Clear all uploaded data with one click

---

## 📦 Dependencies

- `streamlit`
- `pandas`
- `matplotlib`
- `seaborn`
- `pyyaml`
- `streamlit-authenticator`

---

## 👨‍💻 Built By

**Rounak Bhandari**  
Intern @ Swetcha Helpline  
Made with ❤️ using Streamlit

---

## 📌 Note

For deployment to [Streamlit Cloud](https://streamlit.io/cloud), make sure your repo is public and secrets are added under **Settings > Secrets**.

---


