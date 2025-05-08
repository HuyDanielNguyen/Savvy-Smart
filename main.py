import streamlit as st
from database import supabase
from ui import AuthPage, DashboardPage, TransactionPage, AnalysisPage, ProfilePage
from logic import User

def main():
    st.set_page_config(page_title="SavvySmart", layout="wide")

    if "page" not in st.session_state:
        st.session_state.page = "Auth"

    user = User.from_session()

    # Sidebar navigation
    with st.sidebar:
        # Display avatar and app title
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
        st.markdown("---")  # Add a separator

        if st.session_state.page == "Auth":
            # Navigation panel for Auth page
            st.markdown("### About Savvy Smart")
            st.markdown(
                """
                <p style="text-align: justify; font-size: 14px; color: gray;">
                    <b>SavvySmart</b> is a smart personal finance management app that helps you track your income and expenses, analyze spending habits, and set savings goals in a clear and intuitive way. <br> With <b>SavvySmart</b>, you can easily monitor transactions by category, type, and date; visualize your financial data through dynamic income-expense charts; and stay on top of your financial goals every day.
                </p>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("---")  # Add a horizontal line

            # Contributor Section
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
                            <img src="https://media.licdn.com/dms/image/v2/D4D03AQFNk4o4ArY_7Q/profile-displayphoto-shrink_800_800/B4DZajxX4pH0Ac-/0/1746504353060?e=1752105600&v=beta&t=KyR7OCC_qJDRNAXqqXt8RBiMC--Wx97AV8TFfsIFtWA" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <p style="margin: 5px 0 0; font-size: 12px; color: gray;">Lap Nguyen 2</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Navigation panel for other pages
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
            st.markdown("---")  # Add another separator

            # Logout and Change Account buttons
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

            # Contributor Section
            st.markdown("---")  # Add a horizontal line
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
                            <img src="https://media.licdn.com/dms/image/v2/D4D03AQFNk4o4ArY_7Q/profile-displayphoto-shrink_800_800/B4DZajxX4pH0Ac-/0/1746504353060?e=1752105600&v=beta&t=KyR7OCC_qJDRNAXqqXt8RBiMC--Wx97AV8TFfsIFtWA" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                        </a>
                        <p style="margin: 5px 0 0; font-size: 12px; color: gray;">Lap Huynh</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Render the selected page
    if st.session_state.page == "Auth":
        AuthPage().render()
    elif user:
        if st.session_state.page == "Dashboard":
            DashboardPage().render(user)
        elif st.session_state.page == "Transactions":
            TransactionPage().render(user)
        elif st.session_state.page == "Analysis":
            AnalysisPage().render(user)
        elif st.session_state.page == "Profile":
            ProfilePage().render(user)

if __name__ == "__main__":
    main()
