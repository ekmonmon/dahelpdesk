import streamlit as st
from supabase import create_client
from analyst_app import analyst_dashboard
from agent_app import agent_dashboard

# 🔐 Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Login", page_icon="🔐")

# 🔄 Keep track of login status
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None

# 🔍 Login function
def login(email, password):
    res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
    user_data = res.data
    if user_data:
        st.session_state.authenticated = True
        st.session_state.role = user_data[0]["role"]
        return True
    return False

# 🧾 Show login or dashboard
if not st.session_state.authenticated:
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(email, password):
            st.success("Login successful! Loading your dashboard...")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
else:
    if st.session_state.role == "analyst":
        analyst_dashboard()
    elif st.session_state.role == "agent":
        agent_dashboard()
    else:
        st.warning("Unknown role.")
