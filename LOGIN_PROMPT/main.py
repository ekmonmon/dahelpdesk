import streamlit as st
from supabase import create_client

# --- Supabase config ---
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# --- Login Form ---
def login():
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        user = res.data

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[0]["role"]
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. If error persist, please contact an admin.")

# --- Load appropriate page based on role ---
def main():
    if not st.session_state.logged_in:
        login()
    else:
        role = st.session_state.role

        st.sidebar.title("Navigation")
        if role == "analyst":
            st.sidebar.write("Data Analyst")
            from data_analyst import run as analyst_run
            analyst_run()
        elif role == "agent":
            st.sidebar.write("Agent")
            from agent import run as agent_run
            agent_run()

# Run the app
main()
