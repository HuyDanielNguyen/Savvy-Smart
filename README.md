# 💰 SavvySmart – Personal Finance Dashboard

**SavvySmart** is a finance tracking app built using **Streamlit**, **Supabase**, and **Plotly**. It helps users register, log in, and visualize their income and expenses through dynamic dashboards.

---

## 🚀 Features

- 🔐 User Authentication (Sign Up / Sign In via Supabase)
- 🧑 Profile Avatar Support
- 💵 Track Income and Expenses
- 📊 Interactive Dashboards (Plotly charts, metrics)
- 🗂️ Filter transactions by date, category, type
- 🔥 Heatmaps to visualize spending/income patterns

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Supabase (Auth, DB)
- **Database**: Supabase PostgreSQL
- **Visualization**: Plotly, Seaborn, Matplotlib
- **PDF Export**: FPDF (planned feature)
- **Security**: bcrypt password hashing

---

## 📁 Project Structure

```bash
.
├── database.py        # Supabase interaction (auth, CRUD)
├── logic.py           # Core app logic and UI rendering
├── ui.py              # Streamlit UI components
└── README.md          # You're here!
```

---

## 🔧 Setup Instructions

1. **Install Dependencies**

```bash
pip install streamlit supabase seaborn matplotlib plotly bcrypt fpdf httpx
```

2. **Configure Supabase**

Update the `SUPABASE_URL` and `SUPABASE_KEY` in `database.py` with your own project credentials.

3. **Run the App**

```bash
streamlit run logic.py
```

---

## 📸 Avatar & UI Tips

To display a **round profile image** in Streamlit:

```python
st.image(user.avatar_url, width=100)
st.markdown("<style>img {border-radius: 50%;}</style>", unsafe_allow_html=True)
```

---

## 🔐 Security Notes

- Passwords are hashed using bcrypt.
- Make sure not to expose your Supabase secret key in production.

---

## 📌 To-Do

- [ ] Add user profile editing
- [ ] Add transaction editing
- [ ] Add PDF export for reports
- [ ] Deploy to Streamlit Cloud or similar

---

## 👥 Authors

| Avatar | Name & Role |
|--------|-------------|
| <img src="https://avatars.githubusercontent.com/u/142137222?s=100" width="80" style="border-radius: 50%;" /> | **Daniel Nguyen**<br>Swift Developer & Senior Data Analyst<br>[LinkedIn](https://www.linkedin.com/in/danielnguyennn/) |
| <img src="https://media.licdn.com/dms/image/v2/D4D03AQFNk4o4ArY_7Q/profile-displayphoto-shrink_200_200/B4DZajxX4pH0AY-/0/1746504353060?e=2147483647&v=beta&t=ciQt30GhjK7nZdvsSnDodGBlaDX74n-feTC4MNTfcO8" width="80" style="border-radius: 50%;" /> | **Lap Nguyen**<br>Developer<br>[LinkedIn](https://www.linkedin.com/in/l%E1%BA%ADp-hu%E1%BB%B3nh-c%C3%B4ng-189505364/) |

---
