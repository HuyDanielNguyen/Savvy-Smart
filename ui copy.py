import streamlit as st
import pandas as pd
import plotly.express as px
from logic import User, generate_uuid
from database import supabase # Import the supabase client
import bcrypt
from datetime import date  # Import date
from statsmodels.tsa.arima.model import ARIMA
import io


class AuthPage:
    def render(self):
        # Default to "Sign In" if no tab is selected
        if "auth_tab" not in st.session_state:
            st.session_state.auth_tab = "Sign In"

        # Auth Section (Sign In / Sign Up)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In"):
                st.session_state.auth_tab = "Sign In"
        with col2:
            if st.button("Sign Up"):
                st.session_state.auth_tab = "Sign Up"

        # Add a horizontal line
        st.markdown("---")

        # Render the selected tab
        if st.session_state.auth_tab == "Sign In":
            st.subheader("Sign In")
            email = st.text_input("Email", key="sign_in_email")
            password = st.text_input("Password", type="password", key="sign_in_password")
            if st.button("Login"):
                try:
                    # Sign in with Supabase
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if res.user:
                        if res.user.email_confirmed_at is None:
                            st.error("Email chưa được xác nhận. Vui lòng kiểm tra hộp thư của bạn và xác nhận email.")
                            # Resend confirmation email if not confirmed
                            supabase.auth.resend_confirmation_email(email)
                            st.info("Đã gửi lại email xác nhận.")
                        else:
                            st.success("Logged in")
                            user_id = res.user.id
                            # Get user data from 'users' table
                            user_data = supabase.table("users").select("*").eq("id", user_id).single().execute().data
                            st.session_state.user = user_data
                            st.session_state.page = "Dashboard"  # Set the page to Dashboard after login
                            st.rerun() 
                    else:
                        st.error("Login failed")
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

        elif st.session_state.auth_tab == "Sign Up":
            st.subheader("Sign Up")
            username = st.text_input("Username", key="sign_up_username")
            email = st.text_input("Email", key="sign_up_email")
            password = st.text_input("Password", type="password", key="sign_up_password")
            if st.button("Register"):
                try:
                    # Register user with Supabase
                    res = supabase.auth.sign_up({"email": email, "password": password})

                    if res.user:
                        # Hash the password before storing it
                        salt = bcrypt.gensalt()
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

                        # Convert created_at to ISO 8601 string format
                        created_at_iso = res.user.created_at.isoformat() if res.user.created_at else None

                        # Insert user data into the 'users' table
                        supabase.table("users").insert({
                            "id": res.user.id,
                            "email": email,
                            "username": username,
                            "avatar_url": DashboardPage.LINKS["default_avatar"],
                            "password": hashed_password,
                            "created_at": created_at_iso
                        }).execute()
                        st.success("Registration successful. Please check your email to confirm your account.")
                    else:
                        st.error("Registration failed. Please try again.")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

        # Add a horizontal line
        st.markdown("---")

class DashboardPage:
    COLORS = {
        "income_card": "#2A7B9B",
        "expense_card": "#833AB4",
        "positive_balance": "#57C785",
        "negative_balance": "#FF6F61",
    }

    LINKS = {
        "default_avatar": "https://icons.iconarchive.com/icons/iconarchive/wild-camping/512/Bird-Owl-icon.png",
    }

    def render(self, user: User):
        # Page style markdown
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://cdn-icons-png.flaticon.com/512/1828/1828817.png" style="width: 30px; height: 30px;">
                <h2 style="margin: 0;">Dashboard</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader(f"Welcome, {user.username}!")

        # Get transactions
        res = supabase.table("transactions").select("*").eq("user_id", user.id).execute()
        df = pd.DataFrame(res.data)

        if df.empty:
            st.info("No transactions yet.")
            return

        # Total income & expense
        income = df[df["transaction_type"] == "income"]["amount"].sum()
        expense = df[df["transaction_type"] == "expense"]["amount"].sum()

        # Display metrics in minimalist cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div style="background: {self.COLORS['income_card']}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                    <h3>Total Income</h3>
                    <p style="font-size: 24px; font-weight: bold;">${income:,.2f}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div style="background: {self.COLORS['expense_card']}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                    <h3>Total Expense</h3>
                    <p style="font-size: 24px; font-weight: bold;">${expense:,.2f}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Add a horizontal line
        st.markdown("---")

        # Interactive summary table with colored net balance
        st.markdown("### Summary Table")
        net_balance = income - expense
        balance_color = self.COLORS['positive_balance'] if net_balance >= 0 else self.COLORS['negative_balance']
        summary_data = {
            "Metric": ["Total Income", "Total Expense", "Net Balance"],
            "Amount": [f"${income:,.2f}", f"${expense:,.2f}", f"<span style='color: {balance_color};'>${net_balance:,.2f}</span>"]
        }
        st.markdown(
            pd.DataFrame(summary_data).to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

        # Add another horizontal line
        st.markdown("---")

        # Interactive line chart for income and expense trends using Plotly
        df['date'] = pd.to_datetime(df['date'])
        df_grouped = df.groupby(["date", "transaction_type"])["amount"].sum().reset_index()
        st.markdown("### Income and Expense Trends")
        fig = px.line(
            df_grouped, x="date", y="amount", color="transaction_type",
            labels={"amount": "Amount", "date": "Date", "transaction_type": "Transaction Type"},
            title="Income and Expense Trends"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add another horizontal line
        st.markdown("---")

        # Heatmaps for total income and expense using Plotly
        st.markdown("### Heatmaps")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Income Heatmap")
            income_heatmap = df[df["transaction_type"] == "income"].pivot_table(
                index="category", columns="date", values="amount", aggfunc="sum", fill_value=0
            )
            fig = px.imshow(
                income_heatmap, labels=dict(x="Date", y="Category", color="Amount"),
                title="Income Heatmap", color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.markdown("#### Expense Heatmap")
            expense_heatmap = df[df["transaction_type"] == "expense"].pivot_table(
                index="category", columns="date", values="amount", aggfunc="sum", fill_value=0
            )
            fig = px.imshow(
                expense_heatmap, labels=dict(x="Date", y="Category", color="Amount"),
                title="Expense Heatmap", color_continuous_scale="Reds"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Add another horizontal line
        st.markdown("---")

        # Interactive bar chart for category-wise comparison using Plotly
        st.markdown("### Category-wise Comparison")
        category_comparison = df.groupby(["category", "transaction_type"])["amount"].sum().reset_index()
        fig = px.bar(
            category_comparison, x="category", y="amount", color="transaction_type",
            labels={"amount": "Amount", "category": "Category", "transaction_type": "Transaction Type"},
            title="Category-wise Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add another horizontal line
        st.markdown("---")

        # Category Trends
        st.markdown("### Category Trends")
        category_trends = df.groupby(["date", "category"])["amount"].sum().reset_index()
        fig = px.line(
            category_trends, x="date", y="amount", color="category",
            labels={"amount": "Amount", "date": "Date", "category": "Category"},
            title="Category Trends Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add another horizontal line
        st.markdown("---")

class TransactionPage:
    def render(self, user: User):
        st.subheader("Transaction Management")

        # Add Transaction
        st.markdown("### Add a New Transaction")
        with st.form("add_tx"):
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Health", "Education", "Salary", "Investment", "Other"])
            detail = st.text_input("Detail")
            t_type = st.selectbox("Type", ["income", "expense"])
            t_date = st.date_input("Date", value=date.today())
            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                supabase.table("transactions").insert({
                    "id": generate_uuid(),
                    "user_id": user.id,
                    "amount": amount,
                    "category": category,
                    "detail": detail,
                    "transaction_type": t_type,
                    "date": t_date.isoformat()
                }).execute()
                st.success("Transaction Added")

        # Add a horizontal line
        st.markdown("---")

        # Filter Transactions
        st.markdown("### Filter Transactions")
        start_date = st.date_input("Start Date", value=date.today().replace(day=1))
        end_date = st.date_input("End Date", value=date.today())
        selected_category = st.selectbox("Filter by Category", ["All"] + ["Food", "Transport", "Entertainment", "Utilities", "Health", "Education", "Salary", "Investment", "Other"])
        selected_type = st.selectbox("Filter by Type", ["All", "income", "expense"])

        # Fetch transactions
        res = supabase.table("transactions").select("*").eq("user_id", user.id).execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            # Apply filters
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))]
            if selected_category != "All":
                df = df[df['category'] == selected_category]
            if selected_type != "All":
                df = df[df['transaction_type'] == selected_type]

            # Display filtered transactions with the 'id' column
            st.markdown("### Transactions")
            if df.empty:
                st.info("No transactions found for the selected filters.")
            else:
                df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(df[['id', 'date', 'category', 'transaction_type', 'amount', 'detail']])

            # Add a horizontal line
            st.markdown("---")

            # Select and delete transaction using 'id'
            st.markdown("### Delete Transaction")
            selected_id = st.selectbox("Select Transaction ID to Delete", ["None"] + df["id"].tolist())
            if selected_id != "None":
                selected_row = df[df["id"] == selected_id]
                st.write("Selected Transaction:")
                st.dataframe(selected_row)

                if st.button("Delete"):
                    supabase.table("transactions").delete().eq("id", selected_id).execute()
                    st.success("Transaction Deleted")
                    st.rerun()  # Refresh the page to update the table

        else:
            st.info("No transactions available.")

        # Add a horizontal line
        st.markdown("---")

        # New Functionality: Export Transactions
        st.markdown("### Export Transactions")
        if not df.empty:
            export_format = st.selectbox("Select Export Format", ["CSV", "Excel"])
            if st.button("Export"):
                if export_format == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="transactions.csv",
                        mime="text/csv",
                    )
                elif export_format == "Excel":
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Transactions")
                    st.download_button(
                        label="Download Excel",
                        data=excel_buffer,
                        file_name="transactions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

class AnalysisPage:
    def render(self, user: User):
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://cdn-icons-png.flaticon.com/512/1828/1828817.png" style="width: 30px; height: 30px;">
                <h2 style="margin: 0;">Analysis</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Fetch transactions
        res = supabase.table("transactions").select("*").eq("user_id", user.id).execute()
        df = pd.DataFrame(res.data)

        if df.empty:
            st.info("No transaction data.")
            return

        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()

        # Add a horizontal line
        st.markdown("---")

        # User interface for filtering
        st.markdown("### Filter Transactions for Analysis")
        transaction_types = df['transaction_type'].unique().tolist()
        selected_type = st.selectbox("Select Transaction Type", ["All"] + transaction_types)
        categories = df['category'].unique().tolist()
        selected_category = st.selectbox("Select Category", ["All"] + categories)
        start_date = st.date_input("Start Date", value=df.index.min().date())
        end_date = st.date_input("End Date", value=df.index.max().date())

        # Apply filters
        filtered_df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
        if selected_type != "All":
            filtered_df = filtered_df[filtered_df['transaction_type'] == selected_type]
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['category'] == selected_category]

        if filtered_df.empty:
            st.warning("No data available for the selected filters.")
            return

        # Add a horizontal line
        st.markdown("---")

        # Aggregate and display trends
        st.markdown("### Transaction Trends")
        daily = filtered_df.resample('D').sum(numeric_only=True)['amount']
        if len(daily) < 2:
            st.warning("Not enough data to display transaction trends.")
        else:
            daily_df = daily.reset_index()  # Reset index to get 'date' as a column
            fig = px.line(
                daily_df,  # Use the daily DataFrame
                x='date', 
                y='amount',
                labels={"date": "Date", "amount": "Amount"},
                title="Transaction Trends"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Add a horizontal line
        st.markdown("---")

        # Compare income and expense trends
        st.markdown("### Compare Income and Expense Trends")
        income_expense_df = df.groupby(['date', 'transaction_type'])['amount'].sum().unstack(fill_value=0)

        # Ensure the index is a date range to avoid length mismatch
        all_dates = pd.date_range(start=start_date, end=end_date)
        income_expense_df = income_expense_df.reindex(all_dates, fill_value=0)

        if income_expense_df.empty:
            st.warning("Not enough data to display income vs expense trends.")
        else:
            # Treat missing income/expense as 0
            if 'income' not in income_expense_df.columns:
                income_expense_df['income'] = 0
            if 'expense' not in income_expense_df.columns:
                income_expense_df['expense'] = 0

            # Fix: assign name to index so reset_index gives column 'date'
            income_expense_df.index.name = "date"
            income_expense_df = income_expense_df.reset_index()

            fig = px.line(
                income_expense_df,
                x='date',
                y=["income", "expense"],
                labels={"value": "Amount", "date": "Date", "variable": "Transaction Type"},
                title="Income vs Expense Trends"
            )
            st.plotly_chart(fig, use_container_width=True)


        # Add a horizontal line
        st.markdown("---")

        # Forecasting for income and expense
        st.markdown("### Forecasting")
        aggregation_level = st.selectbox("Aggregation Level", ["Daily", "Weekly", "Monthly"], key="aggregation_level")

        # Adjust the maximum forecast days based on the aggregation level
        if aggregation_level == "Daily":
            max_forecast_days = 30
        elif aggregation_level == "Weekly":
            max_forecast_days = 12  # Approximately 3 months
        else:  # Monthly
            max_forecast_days = 6  # Approximately 6 months

        forecast_days = st.slider("Days to Forecast", 1, max_forecast_days, 7, key="forecast_days")

        # Resample data based on aggregation level
        if aggregation_level == "Weekly":
            resampled_income = df[df['transaction_type'] == 'income'].resample('W').sum(numeric_only=True)['amount']
            resampled_expense = df[df['transaction_type'] == 'expense'].resample('W').sum(numeric_only=True)['amount']
        elif aggregation_level == "Monthly":
            resampled_income = df[df['transaction_type'] == 'income'].resample('M').sum(numeric_only=True)['amount']
            resampled_expense = df[df['transaction_type'] == 'expense'].resample('M').sum(numeric_only=True)['amount']
        else:  # Daily
            resampled_income = df[df['transaction_type'] == 'income'].resample('D').sum(numeric_only=True)['amount']
            resampled_expense = df[df['transaction_type'] == 'expense'].resample('D').sum(numeric_only=True)['amount']

        col1, col2 = st.columns(2)

        # Forecast for income
        with col1:
            st.markdown("#### Income Forecast")
            if len(resampled_income) < 2:
                st.warning("Not enough income data to perform forecasting.")
            else:
                try:
                    model_income = ARIMA(resampled_income, order=(1, 1, 1))
                    model_fit_income = model_income.fit()
                    forecast_income = model_fit_income.forecast(steps=forecast_days)
                    forecast_income.index = pd.date_range(resampled_income.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')

                    # Plot forecast
                    fig = px.line()
                    fig.add_scatter(x=resampled_income.index, y=resampled_income.values, mode='lines', name='Historical Income')
                    fig.add_scatter(x=forecast_income.index, y=forecast_income.values, mode='lines', name='Forecast Income', line=dict(dash='dot'))
                    fig.update_layout(title="Income Forecast", xaxis_title="Date", yaxis_title="Amount")
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Income Forecasting failed: {e}")

        # Forecast for expense
        with col2:
            st.markdown("#### Expense Forecast")
            if len(resampled_expense) < 2:
                st.warning("Not enough expense data to perform forecasting.")
            else:
                try:
                    model_expense = ARIMA(resampled_expense, order=(1, 1, 1))
                    model_fit_expense = model_expense.fit()
                    forecast_expense = model_fit_expense.forecast(steps=forecast_days)
                    forecast_expense.index = pd.date_range(resampled_expense.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='D')

                    # Plot forecast
                    fig = px.line()
                    fig.add_scatter(x=resampled_expense.index, y=resampled_expense.values, mode='lines', name='Historical Expense')
                    fig.add_scatter(x=forecast_expense.index, y=forecast_expense.values, mode='lines', name='Forecast Expense', line=dict(dash='dot'))
                    fig.update_layout(title="Expense Forecast", xaxis_title="Date", yaxis_title="Amount")
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Expense Forecasting failed: {e}")

        # Add a horizontal line
        st.markdown("---")

        # Pie Chart for Transaction Distribution
        st.markdown("### Transaction Distribution")
        transaction_distribution = df.groupby("transaction_type")["amount"].sum().reset_index()
        fig = px.pie(
            transaction_distribution, values="amount", names="transaction_type",
            title="Transaction Distribution by Type",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add a horizontal line
        st.markdown("---")

        # Detailed Table for Transactions
        st.markdown("### Detailed Transactions Table")
        st.dataframe(df, use_container_width=True)

        # Add a horizontal line
        st.markdown("---")

        # Comparison of Income and Expense by Category
        st.markdown("### Income vs Expense by Category")

        category_comparison = df.groupby(["category", "transaction_type"])["amount"].sum().unstack(fill_value=0).reset_index()

        if 'income' in category_comparison.columns and 'expense' in category_comparison.columns:
            category_comparison["Net"] = category_comparison["income"] - category_comparison["expense"]
        elif 'expense' in category_comparison.columns:
            category_comparison["Net"] = -category_comparison["expense"]
        elif 'income' in category_comparison.columns:
            category_comparison["Net"] = category_comparison["income"]
        else:
            numeric_cols = category_comparison.select_dtypes(include='number').columns
            category_comparison["Net"] = category_comparison[numeric_cols].sum(axis=1)

        st.dataframe(category_comparison, use_container_width=True)

        # Add a horizontal line
        st.markdown("---")

        # Bar Chart for Net Balance by Category
        st.markdown("### Net Balance by Category")
        fig = px.bar(
            category_comparison, x="category", y="Net",
            labels={"Net": "Net Balance", "category": "Category"},
            title="Net Balance by Category",
            color="Net",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig, use_container_width=True)


class ProfilePage:
    def render(self, user: User):
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://cdn-icons-png.flaticon.com/512/1828/1828817.png" style="width: 30px; height: 30px;">
                <h2 style="margin: 0;">Profile</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add a horizontal line
        st.markdown("---")

        st.subheader("Profile")

        # Display avatar and user information
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(user.avatar_url, width=100)
        with col2:
            st.markdown(f"""
                <div style="padding: 10px;">
                    <h3 style="margin: 0;">{user.username}</h3>
                    <p style="margin: 0; color: gray;">{user.email}</p>
                    <p style="margin: 0; color: gray;">Joined: {user.created_at if user.created_at else "N/A"}</p>
                </div>
            """, unsafe_allow_html=True)

        # Add a horizontal line
        st.markdown("---")

        # Allow user to update avatar URL
        st.markdown("### Update Avatar")
        new_url = st.text_input("New Avatar URL", placeholder="Enter a new avatar URL")
        if st.button("Update Avatar"):
            if new_url:
                supabase.table("users").update({"avatar_url": new_url}).eq("id", user.id).execute()
                st.success("Avatar updated successfully!")
                st.session_state.user["avatar_url"] = new_url
                st.rerun()
            else:
                st.warning("Please enter a valid URL.")

        # Add a horizontal line
        st.markdown("---")

        # New Functionality: Update Name
        st.markdown("### Update Name")
        new_name = st.text_input("New Name", placeholder="Enter your new name")
        if st.button("Update Name"):
            if new_name:
                supabase.table("users").update({"username": new_name}).eq("id", user.id).execute()
                st.success("Name updated successfully!")
                st.session_state.user["username"] = new_name
                st.rerun()
            else:
                st.warning("Please enter a valid name.")
