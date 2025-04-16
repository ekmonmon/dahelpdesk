import streamlit as st
from supabase import create_client
from agent_app import run as agent_run
from data_analyst_app import run as analyst_run

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login():
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        user_data = res.data

        if user_data:
            st.session_state.logged_in = True
            st.session_state.user_role = user_data[0]["role"]
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    if not st.session_state.logged_in:
        login()
    else:
        if st.session_state.user_role == "agent":
            agent_run()
        elif st.session_state.user_role == "analyst":
            analyst_run()
        else:
            st.warning("Unknown role")

if __name__ == "__main__":
    main()
