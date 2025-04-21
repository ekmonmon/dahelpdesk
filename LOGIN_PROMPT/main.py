import streamlit as st
from supabase import create_client
from data_analyst_app import run as analyst_run
from agent_app import run as agent_run

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
st.markdown("""
    <style>
    div[data-testid='stToolbar'], 
    a[class='_profileContainer_gzau3_53'], 
    div[class='_viewerBadge_nim44_23'] {
        display:none;
    }
    </style>
""", unsafe_allow_html=True)
# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

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
            st.success("Login successful. Redirecting...")
            st.rerun()
        else:
            st.error("Invalid credentials. If error persist, please contact an admin.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.success("You have been logged out.")
    st.rerun()

def main():
    if not st.session_state.logged_in:
        login()
    else:
        # Add logout button at the top right
        with st.sidebar:
            st.markdown("### Settings")
            if st.button("Logout"):
                logout()

        # Run appropriate app based on role
        role = st.session_state.user_role
        if role == "analyst":
            analyst_run()
        elif role == "agent":
            agent_run()
        else:
            st.error("Unknown role.")

if __name__ == "__main__":
    main()
