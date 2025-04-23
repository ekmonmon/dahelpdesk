import streamlit as st
from supabase import create_client
from data_analyst_app import run as analyst_run
from agent_app import run as agent_run
from super_admin_app import run as super_admin_run


# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hide Streamlit toolbar
#st.markdown("""
    #<style>
    #div[data-testid="stToolbar"] {
       # display: none !important;
    #}
    #</style>
#""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

def login():
    st.markdown("""
        <style>
        input {
            padding: 10px !important;
            border-radius: 8px !important;
        }
        .stButton>button {
            width: 100%;
            background-color: #3366cc;
            color: white;
            padding: 10px;
            border-radius: 8px;
            border: none;
        }
        div[data-testid="stMainBlockContainer"]{
            max-width:575px
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="main">', unsafe_allow_html=True)

        st.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_TV_2015.png", width=100)
        st.markdown("## Welcome Back")
        st.markdown("Please log in to continue")

        email = st.text_input("Username")
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
                st.error("Invalid credentials. If error persists, please contact an admin.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.success("You have been logged out.")
    st.rerun()

def main():
    if not st.session_state.logged_in:
        login()
    else:
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            # Only use the Streamlit button for logout
            if st.button("Logout", use_container_width=True):
                logout()

        # Run appropriate app based on role
        role = st.session_state.user_role
        if role == "analyst":
            analyst_run()
        elif role == "agent":
            agent_run()
        elif role == "super_admin":
            super_admin_run()
        else:
            st.error("Unknown role.")


if __name__ == "__main__":
    main()
