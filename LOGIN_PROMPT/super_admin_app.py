import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase config
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run():
    st.set_page_config(page_title="Super Admin Panel", layout="wide")
    st.title("🛡️ Super Admin Panel")

    # Load ticket data
    tickets_response = supabase.table("tickets").select("*").execute()
    df = pd.DataFrame(tickets_response.data)

    if df.empty:
        st.warning("No tickets available.")
    else:
        st.subheader("📊 Ticket Overview")
        status_counts = df["status"].value_counts()
        st.dataframe(status_counts.rename_axis("Status").reset_index(name="Count"), use_container_width=True)

        # Delete closed tickets
        st.subheader("🗑️ Delete Closed Tickets")
        closed_count = df[df["status"] == "Closed"].shape[0]
        if closed_count == 0:
            st.info("There are no closed tickets to delete.")
        else:
            st.warning(f"You are about to delete **{closed_count}** closed tickets.")
            confirm = st.checkbox("I confirm I want to delete all closed tickets.")
            if st.button("Delete Closed Tickets") and confirm:
                try:
                    response = supabase.table("tickets").delete().eq("status", "Closed").execute()
                    if response.data:
                        st.success(f"✅ Deleted {len(response.data)} closed tickets.")
                        st.rerun()
                    else:
                        st.warning("No tickets deleted.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Optional: Users Table
    st.subheader("👥 User Overview")
    users_response = supabase.table("users").select("id, email, role").execute()
    user_df = pd.DataFrame(users_response.data)
    if not user_df.empty:
        st.dataframe(user_df, use_container_width=True)
    else:
        st.info("No users found.")
