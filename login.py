import streamlit as st
from supabase import create_client

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 Login Page")

# Check if already logged in
query_params = st.experimental_get_query_params()
if "role" in query_params:
    role = query_params["role"][0]
    if role == "analyst":
        st.success("You are already logged in as Data Analyst.")
        st.markdown("[Go to Analyst App](https://daappdesk-gmpsthfyqkuabyb7zd3ln6.streamlit.app/)", unsafe_allow_html=True)
    elif role == "agent":
        st.success("You are already logged in as Agent.")
        st.markdown("[Go to Agent App](https://daappdesk-6nbmyk5jvqmwcsd36tuapz.streamlit.app/)", unsafe_allow_html=True)
    st.stop()

# Login form
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not email or not password:
        st.error("Please fill in all fields.")
    else:
        res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
        user_data = res.data

        if user_data:
            role = user_data[0]["role"]
            st.success(f"Welcome, {email}!")

            # Add role as query param so we don't re-auth every time
            st.experimental_set_query_params(role=role)

            if role == "analyst":
                st.markdown("[👉 Go to Analyst App](https://daappdesk-gmpsthfyqkuabyb7zd3ln6.streamlit.app/)", unsafe_allow_html=True)
            elif role == "agent":
                st.markdown("[👉 Go to Agent App](https://daappdesk-6nbmyk5jvqmwcsd36tuapz.streamlit.app/)", unsafe_allow_html=True)
            else:
                st.warning("Role not recognized.")
        else:
            st.error("Invalid email or password.")
