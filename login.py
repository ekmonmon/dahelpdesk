import streamlit as st
from supabase import create_client
import webbrowser

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Login Page")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
    user_data = res.data

    if user_data:
        role = user_data[0]["role"]
        if role == "analyst":
            st.success("Redirecting to Data Analyst app...")
            webbrowser.open("https://daappdesk-gmpsthfyqkuabyb7zd3ln6.streamlit.app/")  # or hosted URL of data analyst app
        elif role == "agent":
            st.success("Redirecting to Agent app...")
            webbrowser.open("https://daappdesk-6nbmyk5jvqmwcsd36tuapz.streamlit.app/")  # or hosted URL of agent app
        else:
            st.warning("Unknown role.")
    else:
        st.error("Invalid credentials.")
