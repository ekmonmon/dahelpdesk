import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run():
    st.title("📊 Data Analyst Helpdesk")

    # Get the campaigns assigned to the current user (data analyst)
    assigned_campaigns = st.session_state.user_campaigns
    if not assigned_campaigns:
        st.error("You are not assigned to any campaigns.")
        return

    # Fetch tickets assigned to the user's campaigns
    tickets_response = supabase.table("tickets").select("*").in_("campaign", assigned_campaigns).execute()
    df = pd.DataFrame(tickets_response.data)

    if df.empty:
        st.warning("No tickets found for your campaigns.")
        return

    # Display tickets in a table
    st.dataframe(df)

    # Additional filtering, search, and ticket display code
    # Implementing the same logic you had for status filtering, etc.
    status_tabs = ["Open", "In Progress", "Resolved", "Closed"]
    status_icons = {"Open": "🟥", "In Progress": "🟧", "Resolved": "🟩", "Closed": "⬜"}

    tab_labels = [
        f"{status_icons[status]} {status} ({df[df['status'] == status].shape[0]})"
        for status in status_tabs
    ]
    
    # Render tabs
    tab_objs = st.tabs(tab_labels)

    for idx, status in enumerate(status_tabs):
        with tab_objs[idx]:
            status_df = df[df["status"] == status]
            if status_df.empty:
                st.info(f"No tickets currently marked as **{status}**.")
                continue

            # Render each ticket with relevant info
            for _, ticket in status_df.iterrows():
                st.markdown(f"### Ticket #{ticket['ticket_number']} - {ticket['request']}")
                with st.expander("ℹ️ Information"):
                    st.markdown(f"**Priority:** {ticket['priority']}")
                    st.markdown(f"**Status:** {ticket['status']}")
                    st.markdown(f"**Description:** {ticket['description']}")
                    if ticket['attachment']:
                        st.markdown(f"[📎 Download Attachment]({ticket['attachment']})")
