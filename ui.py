import streamlit as st
from logic import AuthLogic, DashboardLogic, TransactionLogic, AnalysisLogic, ProfileLogic

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
                AuthLogic.sign_in(email, password)

        elif st.session_state.auth_tab == "Sign Up":
            st.subheader("Sign Up")
            username = st.text_input("Username", key="sign_up_username")
            email = st.text_input("Email", key="sign_up_email")
            password = st.text_input("Password", type="password", key="sign_up_password")
            if st.button("Register"):
                AuthLogic.sign_up(username, email, password)

        # Add a horizontal line
        st.markdown("---")

class DashboardPage:
    def render(self, user):
        st.subheader(f"Welcome, {user.username}!")
        DashboardLogic.render_dashboard(user)

class TransactionPage:
    def render(self, user):
        st.subheader("Transaction Management")
        TransactionLogic.render_transactions(user)

class AnalysisPage:
    def render(self, user):
        st.subheader("Analysis")
        AnalysisLogic.render_analysis(user)

class ProfilePage:
    def render(self, user):
        st.subheader("Profile")
        ProfileLogic.render_profile(user)
