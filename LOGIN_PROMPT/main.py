import streamlit as st
from supabase import create_client
from data_analyst_app import run as analyst_run
from agent_app import run as agent_run
from super_admin_app import run as super_admin_run

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hide Streamlit default UI elements
st.markdown("""
    <style>
    div[data-testid="stToolbar"] { display: none !important; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stTextInput>div>div>input {
        background-color: #f5f5f5;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 4rem;
    }
    .login-box {
        background-color: #ffffffdd;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
    }
    </style>
""", unsafe_allow_html=True)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

def login():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown("### 🔐 Login to Helpdesk System")
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("🔓 Login", use_container_width=True):
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        user_data = res.data
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user_role = user_data[0]["role"]
            st.success("✅ Login successful. Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.success("✅ You have been logged out.")
    st.rerun()

def main():
    if not st.session_state.logged_in:
        login()
    else:
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("🚪 Logout", use_container_width=True):
                logout()

        st.markdown("### 🧭 Redirecting based on role...")
        role = st.session_state.user_role

        if role == "analyst":
            analyst_run()
        elif role == "agent":
            agent_run()
        elif role == "super_admin":
            super_admin_run()
        else:
            st.error("Unknown role detected.")

if __name__ == "__main__":
    main()
