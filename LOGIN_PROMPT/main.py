import streamlit as st
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_campaigns = []

def login():
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Get user data from the database
        res = supabase.table("users").select("role", "assigned_campaign").eq("email", email).eq("password", password).execute()
        user_data = res.data

        if user_data:
            st.session_state.logged_in = True
            st.session_state.user_role = user_data[0]["role"]
            st.session_state.user_campaigns = user_data[0]["assigned_campaign"]  # Store the campaigns
            st.success("Login successful. Redirecting...")
            st.rerun()
        else:
            st.error("Invalid credentials. If error persists, please contact an admin.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_campaigns = []
    st.success("You have been logged out.")
    st.rerun()

def main():
    if not st.session_state.logged_in:
        login()
    else:
        # Top-right logout button
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            st.button("Logout", on_click=logout)

        # Run the appropriate app based on the user role
        if st.session_state.user_role == "analyst":
            import data_analyst_app
            data_analyst_app.run()  # Call the data analyst dashboard

if __name__ == "__main__":
    main()
