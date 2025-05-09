# 💰 SavvySmart – Personal Finance Management App

**SavvySmart** is a powerful and user-friendly personal finance tracking application built using **Streamlit**, **Supabase**, and **Plotly**. It helps users track income and expenses, visualize financial patterns, and make smarter decisions through analytics and forecasting. It supports user authentication, transaction management, profile updates, and ARIMA-based time-series forecasting.

---

## 🧠 Overview

SavvySmart is designed for individuals who want to manage their finances effectively. It offers real-time visualization, category-based insights, historical tracking, and predictive analytics to make financial planning smarter and easier.

---

## 🔧 Tech Stack

| Layer         | Technology                      |
|---------------|----------------------------------|
| Frontend      | [Streamlit](https://streamlit.io/) |
| Backend       | [Supabase](https://supabase.com/) |
| Database      | Supabase Postgres               |
| Authentication| Supabase Auth (Email + Password)|
| File Storage  | Supabase Storage (for Face ID, Avatar) |
| Data Analysis | [Pandas](https://pandas.pydata.org/), [Plotly](https://plotly.com/) |
| Forecasting   | [ARIMA model](https://www.statsmodels.org/) via `statsmodels` |

---

## ✨ Features

### 🔐 Authentication
- Sign up with email & password
- Email confirmation check + automatic resend
- Secure login
- Session management with `st.session_state`

### 📊 Dashboard
- Welcome message + user avatar
- Total **income**, **expense**, and **net balance**
- Line chart: income vs. expense trend
- Heatmaps for income & expense by category/date
- Bar chart: category-wise comparison
- Line chart: category trends over time

### 🧾 Transaction Page
- Add new transaction (amount, type, category, date, note)
- Filter by date range, category, and type
- View and delete specific transactions
- Export data to **CSV** or **Excel**

### 📈 Analysis Page
- Transaction trends (daily resampled)
- Income vs. expense comparison over time
- Forecasting with ARIMA (daily, weekly, monthly)
- Pie chart: transaction type distribution
- Table: income vs. expense per category
- Bar chart: net balance per category

### 👤 Profile Page
- View profile: avatar, name, email, join date
- Update avatar (via URL)
- Update username

### ⚙️ Planned Features
- 🔓 Face ID login (via camera and image verification)
- 🧠 AI-based budgeting insights
- 💬 Notifications and goal setting

---

## 🖼️ Application Preview

> Add a screenshot or screen recording of your app in this section.

```
![SavvySmart Preview](path/to/your/screenshot.png)
```

---

## 📂 Project Structure

```
savvysmart/
├── main.py              # App entry point, handles navigation and routing
├── ui.py                # UI components for each page (Dashboard, Auth, etc.)
├── logic.py             # Business logic: User and Transaction models
├── database.py          # Supabase client and environment variable setup
├── .env                 # Environment secrets (not included in version control)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## ⚙️ Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HuyDanielNguyen/Savvy-Smart.git
   cd Savvy-Smart
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file at the project root with:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-api-key
   ```

4. **Run the app locally:**
   ```bash
   streamlit run main.py
   ```

---

## 🔒 Supabase Database Schema (Required)

### Table: `users`
| Column       | Type    |
|--------------|---------|
| id           | UUID    |
| email        | Text    |
| username     | Text    |
| password     | Text    |
| avatar_url   | Text    |
| created_at   | Timestamp |

### Table: `transactions`
| Column         | Type     |
|----------------|----------|
| id             | UUID     |
| user_id        | UUID     |
| amount         | Float    |
| category       | Text     |
| detail         | Text     |
| transaction_type | Text   |
| date           | Date     |

---

## 🧪 Testing Tips

- Use a dummy Supabase project for development
- Set up some test users with confirmed emails
- Populate transaction data for each test account to evaluate charts and forecasts

---

## 🚀 Deployment on Streamlit Cloud

To deploy:

1. Push your project to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your repo and set environment variables (`SUPABASE_URL`, `SUPABASE_KEY`)
4. ✅ **Note**: After pushing to GitHub, manually click **“Rerun”** or **“Restart”** in Streamlit Cloud (auto-deploy is not always reliable)

---

## 👥 Authors

| Avatar | Name & Role |
|--------|-------------|
| <img src="https://avatars.githubusercontent.com/u/142137222?s=100" width="80" style="border-radius: 50%;" /> | **Daniel Nguyen**<br>Swift Developer & Senior Data Analyst<br>[LinkedIn](https://www.linkedin.com/in/danielnguyennn/) |
| <img src="https://media.licdn.com/dms/image/v2/D4D03AQFNk4o4ArY_7Q/profile-displayphoto-shrink_200_200/B4DZajxX4pH0AY-/0/1746504353060?e=2147483647&v=beta&t=ciQt30GhjK7nZdvsSnDodGBlaDX74n-feTC4MNTfcO8" width="80" style="border-radius: 50%;" /> | **Lap Nguyen**<br>Developer<br>[LinkedIn](https://www.linkedin.com/in/l%E1%BA%ADp-hu%E1%BB%B3nh-c%C3%B4ng-189505364/) |

---

## 🪪 License

MIT License © 2025 Daniel Nguyen & Contributors