import streamlit as st
from database import supabase, generate_uuid, get_user_by_id, insert_transaction, fetch_transactions, delete_transaction
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
import bcrypt
from io import BytesIO
from fpdf import FPDF
import plotly.graph_objects as go
import numpy as np

class User:
    def __init__(self, id, email, username, password=None, avatar_url=None, created_at=None):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = None
        self.avatar_url = avatar_url or "https://icons.iconarchive.com/icons/iconarchive/wild-camping/512/Bird-Owl-icon.png"
        self.created_at = created_at
        if password:
            self.password_hash = self.hash_password(password)

    def hash_password(self, password: str) -> str:
        # Hash the password with bcrypt and return the hashed value
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        # Compare the entered password with the hashed one
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @classmethod
    def from_session(cls):
        # Check session and load user data
        if "user" in st.session_state:
            return cls(**st.session_state.user)
        return None
    @staticmethod
    def render_analysis(user):
        st.markdown("<h2 style='text-align: center; color: #2A7B9B;'>📊 Financial Analysis</h2>", unsafe_allow_html=True)
        st.markdown("---")

        # Filters for date range and category
        st.markdown("### Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        with col3:
            selected_category = st.selectbox("Category", ["All", "Food", "Transport", "Entertainment", "Utilities", "Health", "Education", "Salary", "Investment", "Other"])

        # Fetch and filter data
        res = fetch_transactions(user.id)
        df = pd.DataFrame(res)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))]
            if selected_category != "All":
                df = df[df['category'] == selected_category]

        # Display key insights
        st.markdown("### Key Insights")
        if not df.empty:
            total_income = df[df["transaction_type"] == "income"]["amount"].sum()
            total_expense = df[df["transaction_type"] == "expense"]["amount"].sum()
            net_balance = total_income - total_expense

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Income", f"${total_income:,.2f}")
            with col2:
                st.metric("Total Expense", f"${total_expense:,.2f}")
            with col3:
                st.metric("Net Balance", f"${net_balance:,.2f}", delta=f"{net_balance:,.2f}")

        else:
            st.info("No data available for the selected filters.")
            return

        # Visualize income vs expense trends with Plotly
        st.markdown("---")
        st.markdown("### Income vs Expense Trends")
        df_grouped = df.groupby(["date", "transaction_type"])["amount"].sum().reset_index()
        fig = go.Figure()
        for transaction_type in df_grouped["transaction_type"].unique():
            filtered_data = df_grouped[df_grouped["transaction_type"] == transaction_type]
            fig.add_trace(go.Scatter(
                x=filtered_data["date"],
                y=filtered_data["amount"],
                mode="lines+markers",
                name=transaction_type.capitalize(),
                line=dict(width=2),
                marker=dict(size=6)
            ))
        fig.update_layout(
            title="Income vs Expense Trends",
            xaxis_title="Date",
            yaxis_title="Amount",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(title="Transaction Type"),
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed table
        st.markdown("---")
        st.markdown("### Detailed Transactions Table")
        df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df[['date', 'category', 'transaction_type', 'amount', 'detail']])

        # Forecasting Section
        st.markdown("---")
        st.markdown("<h3 style='text-align: center; color: #2A7B9B;'>📈 Forecasting</h3>", unsafe_allow_html=True)

        # Aggregation level and forecast period selection
        st.markdown("### Forecast Settings")
        col1, col2 = st.columns(2)
        with col1:
            aggregation_level = st.selectbox("Aggregation Level", ["Daily", "Weekly", "Monthly", "Yearly"])
        with col2:
            forecast_period = st.slider("Forecast Period (in units of aggregation)", 1, 30, 7)

        # Resample data based on aggregation level
        if aggregation_level == "Daily":
            resample_rule = 'D'
        elif aggregation_level == "Weekly":
            resample_rule = 'W'
        elif aggregation_level == "Monthly":
            resample_rule = 'M'
        elif aggregation_level == "Yearly":
            resample_rule = 'Y'

        # Fetch and process data
        res = fetch_transactions(user.id)
        df = pd.DataFrame(res)
        if df.empty:
            st.info("No transaction data available for forecasting.")
            return

        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()

        # Resample income and expense data
        income_data = df[df['transaction_type'] == 'income'].resample(resample_rule)['amount'].sum()
        expense_data = df[df['transaction_type'] == 'expense'].resample(resample_rule)['amount'].sum()

        # Forecast income and expense
        st.markdown("### Forecast Results")
        col1, col2 = st.columns(2)
        with col1:
            if len(income_data) >= 2:
                st.subheader("Income Forecast")
                income_model = ARIMA(income_data, order=(1, 1, 1)).fit()
                income_forecast = income_model.forecast(steps=forecast_period)
                forecast_dates = pd.date_range(start=income_data.index[-1], periods=forecast_period + 1, freq=resample_rule)[1:]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=income_data.index,
                    y=income_data,
                    mode="lines+markers",
                    name="Historical Income",
                    line=dict(color="#57C785", width=2),
                    marker=dict(size=6)
                ))
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=income_forecast,
                    mode="lines+markers",
                    name="Forecasted Income",
                    line=dict(color="#2A7B9B", dash="dash", width=2),
                    marker=dict(size=6)
                ))
                fig.update_layout(
                    title="Income Forecast",
                    xaxis_title="Date",
                    yaxis_title="Amount",
                    template="plotly_white",
                    hovermode="x unified",
                    legend=dict(title="Income Data"),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data to forecast income.")

        with col2:
            if len(expense_data) >= 2:
                st.subheader("Expense Forecast")
                expense_model = ARIMA(expense_data, order=(1, 1, 1)).fit()
                expense_forecast = expense_model.forecast(steps=forecast_period)
                forecast_dates = pd.date_range(start=expense_data.index[-1], periods=forecast_period + 1, freq=resample_rule)[1:]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=expense_data.index,
                    y=expense_data,
                    mode="lines+markers",
                    name="Historical Expense",
                    line=dict(color="#FD1D1D", width=2),
                    marker=dict(size=6)
                ))
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=expense_forecast,
                    mode="lines+markers",
                    name="Forecasted Expense",
                    line=dict(color="#833AB4", dash="dash", width=2),
                    marker=dict(size=6)
                ))
                fig.update_layout(
                    title="Expense Forecast",
                    xaxis_title="Date",
                    yaxis_title="Amount",
                    template="plotly_white",
                    hovermode="x unified",
                    legend=dict(title="Expense Data"),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data to forecast expense.")

        # Export forecast results
        st.markdown("---")
        st.markdown("### Export Forecast Data")
        if st.button("Export Forecast as CSV"):
            forecast_data = pd.DataFrame({
                "Date": pd.date_range(start=income_data.index[-1], periods=forecast_period, freq=resample_rule),
                "Forecasted Income": income_forecast if len(income_data) >= 2 else [],
                "Forecasted Expense": expense_forecast if len(expense_data) >= 2 else []
            })
            csv = forecast_data.to_csv(index=False)
            st.download_button(
                label="Download Forecast CSV",
                data=csv,
                file_name="forecast_data.csv",
                mime="text/csv"
            )

class ProfileLogic:
    @staticmethod
    def render_profile(user):
        # Add a styled header with an image
        st.markdown(
            """
            <div style="text-align: center; padding: 20px;">
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="Profile" style="width: 80px; height: 80px; margin-bottom: 10px;">
                <h2 style="color: #2A7B9B;">👤 User Profile</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Display user details
        col1, col2 = st.columns([1, 3])
        with col1:
            # st.image(user.avatar_url, width=100)
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="{user.avatar_url}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover;">
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(f"""
                <div>
                    <h3>{user.username}</h3>
                    <p>{user.email}</p>
                    <p>Joined: {user.created_at if user.created_at else "N/A"}</p>
                </div>
            """, unsafe_allow_html=True)

        # Update Avatar Section
        st.markdown("---")
        st.markdown("### Update Avatar")
        new_url = st.text_input("New Avatar URL")
        if st.button("Update Avatar"):
            supabase.table("users").update({"avatar_url": new_url}).eq("id", user.id).execute()
            st.success("Avatar updated successfully!")
            st.session_state.user["avatar_url"] = new_url
            st.rerun()

        # Update Username Section
        st.markdown("---")
        st.markdown("### Update Username")
        new_username = st.text_input("New Username", value=user.username)
        if st.button("Update Username"):
            supabase.table("users").update({"username": new_username}).eq("id", user.id).execute()
            st.success("Username updated successfully!")
            st.session_state.user["username"] = new_username
            st.rerun()

        # Update Email Section
        st.markdown("---")
        st.markdown("### Update Email")
        new_email = st.text_input("New Email", value=user.email)
        if st.button("Update Email"):
            supabase.table("users").update({"email": new_email}).eq("id", user.id).execute()
            st.success("Email updated successfully!")
            st.session_state.user["email"] = new_email
            st.rerun()

        # Delete Account Section
        st.markdown("---")
        st.markdown("### Delete Account")
        if st.button("Delete Account", key="delete_account"):
            confirm = st.checkbox("I confirm that I want to delete my account.")
            if confirm:
                supabase.table("users").delete().eq("id", user.id).execute()
                st.success("Account deleted successfully!")
                st.session_state.clear()
                st.rerun()

def main():
    st.set_page_config(page_title="SavvySmart", layout="wide")

    if "page" not in st.session_state:
        st.session_state.page = "Auth"

    user = User.from_session()

    # Sidebar navigation
    with st.sidebar:
        avatar_url = user.avatar_url if user else "https://icons.iconarchive.com/icons/iconarchive/wild-camping/512/Bird-Owl-icon.png"
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px;">
                <img src="{avatar_url}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; margin-bottom: 10px;">
                <h1 style="margin: 0; color: #2A7B9B; text-transform: uppercase">Savvy Smart</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        # Navigation panel
        if st.session_state.page == "Auth":
            st.markdown("### About Savvy Smart")
            st.markdown(
                """
                <p style="text-align: justify; font-size: 14px; color: gray;">
                    <b>SavvySmart</b> is a smart personal finance management app that helps you track your income and expenses, analyze spending habits, and set savings goals in a clear and intuitive way. <br> With <b>SavvySmart</b>, you can easily monitor transactions by category, type, and date; visualize your financial data through dynamic income-expense charts; and stay on top of your financial goals every day.
                </p>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("---")
            st.markdown("### Contributor")
            st.markdown(
                """
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px;">
                    <div style="text-align: center;">
                        <a href="https://www.linkedin.com/in/danielnguyennn/" target="_blank">
                            <img src="https://avatars.githubusercontent.com/u/142137222?s=400&u=97a89baf879da0dd92c078ff42fc8a90ff72fcf5&v=4" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <p style="margin: 5px 0 0; font-size: 12px; color: gray;">Daniel Nguyen</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="https://www.linkedin.com/in/l%E1%BA%ADp-hu%E1%BB%B3nh-c%C3%B4ng-189505364/" target="_blank">
                            <img src="https://media.licdn.com/dms/image/v2/D4D03AQFNk4o4ArY_7Q/profile-displayphoto-shrink_200_200/B4DZajxX4pH0AY-/0/1746504353060?e=2147483647&v=beta&t=ciQt30GhjK7nZdvsSnDodGBlaDX74n-feTC4MNTfcO8" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <p style="margin: 5px 0 0; font-size: 12px; color: gray;">Lap Nguyen</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown("### Navigation")
            st.markdown(
                """
                <style>
                .nav-link {
                    display: block;
                    padding: 10px;
                    text-align: center;
                    text-decoration: none;
                    color: black;
                    font-size: 16px;
                    border-radius: 5px;
                    transition: background-color 0.3s, color 0.3s;
                }
                .nav-link:hover {
                    background-color: #57C785;
                    color: white;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            for page in ["Dashboard", "Transactions", "Analysis", "Profile"]:
                if st.session_state.page == page:
                    st.markdown(
                        f'<a href="#" class="nav-link" style="background-color: #57C785; color: white;" onclick="window.location.reload();">{page.capitalize()}</a>',
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(page.capitalize(), key=f"nav_{page}"):
                        st.session_state.page = page
                        st.rerun()
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if "logout_confirm" not in st.session_state:
                    st.session_state.logout_confirm = False

                if st.session_state.logout_confirm:
                    st.warning("Are you sure you want to log out?")
                    if st.button("Yes, Log out"):
                        st.session_state.clear()
                        st.rerun()
                    if st.button("Cancel"):
                        st.session_state.logout_confirm = False
                else:
                    if st.button("Log out"):
                        st.session_state.logout_confirm = True

            with col2:
                if "change_account_confirm" not in st.session_state:
                    st.session_state.change_account_confirm = False

                if st.session_state.change_account_confirm:
                    st.warning("Are you sure you want to change the account?")
                    if st.button("Yes, Change Account"):
                        st.session_state.clear()
                        st.session_state.page = "Auth"
                        st.rerun()
                    if st.button("Cancel"):
                        st.session_state.change_account_confirm = False
                else:
                    if st.button("Change Account"):
                        st.session_state.change_account_confirm = True

            st.markdown("---")
            st.markdown("### Contributor")
            st.markdown(
                """
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px;">
                    <div style="text-align: center;">
                        <a href="https://www.linkedin.com/in/danielnguyennn/" target="_blank">
                            <img src="https://avatars.githubusercontent.com/u/142137222?s=400&u=97a89baf879da0dd92c078ff42fc8a90ff72fcf5&v=4" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <p style="margin: 5px 0 0; font-size: 12px; color: gray;">Daniel Nguyen</p>
                    </div>
                    <div style="text-align: center;">
                        <a href="https://www.linkedin.com/in/l%E1%BA%ADp-hu%E1%BB%B3nh-c%C3%B4ng-189505364/" target="_blank">
                            <img src="https://media.licdn.com/dms/image/v2/D4D03AQFNk4o4ArY_7Q/profile-displayphoto-shrink_200_200/B4DZajxX4pH0AY-/0/1746504353060?e=2147483647&v=beta&t=ciQt30GhjK7nZdvsSnDodGBlaDX74n-feTC4MNTfcO8" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <p style="margin: 5px 0 0; font-size: 12px; color: gray;">Lap Nguyen</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Debug current page
    st.write(f"Current Page: {st.session_state.page}")

    # Render page
    if st.session_state.page == "Auth":
        from ui import AuthPage
        AuthPage().render()
    elif user:
        if st.session_state.page == "Dashboard":
            DashboardLogic.render_dashboard(user)
        elif st.session_state.page == "Transactions":
            TransactionLogic.render_transactions(user)
        elif st.session_state.page == "Analysis":
            AnalysisLogic.render_analysis(user)
        elif st.session_state.page == "Profile":
            ProfileLogic.render_profile(user)

if __name__ == "__main__":
    main()
