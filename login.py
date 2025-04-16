import streamlit as st
from supabase import create_client
import os

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 Login Page")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not email or not password:
        st.error("Please enter both email and password.")
    else:
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        user_data = res.data

        if user_data:
            role = user_data[0]["role"]
            st.success(f"Welcome, {email}!")

            # Redirect based on role
            if role == "analyst":
                st.markdown(
                    """<meta http-equiv="refresh" content="1; URL='https://daappdesk-gmpsthfyqkuabyb7zd3ln6.streamlit.app/" />""",
                    unsafe_allow_html=True
                )
            elif role == "agent":
                st.markdown(
                    """<meta http-equiv="refresh" content="1; URL='https://daappdesk-6nbmyk5jvqmwcsd36tuapz.streamlit.app/" />""",
                    unsafe_allow_html=True
                )
            else:
                st.warning("Unrecognized role in system.")
        else:
            st.error("Invalid email or password.")
