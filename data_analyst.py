import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://zqycetikgrqgzbzrxzok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxeWNldGlrZ3JxZ3pienJ4em9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5NTMzOTMsImV4cCI6MjA1ODUyOTM5M30.uNYXbCjTJJS2spGuq4EMPdUxAcQGeekEwAG2AGb1Yt4"  # Replace with your actual key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set page title and layout
st.set_page_config(page_title="Data Analyst Helpdesk", page_icon="📊", layout="wide")
st.title("📊 Data Analyst Helpdesk")

# Load tickets from Supabase
try:
    tickets_response = supabase.table("tickets").select("*").execute()
    if not tickets_response.data:
        st.warning("⚠️ No tickets found in the database.")
        st.stop()
    df = pd.DataFrame(tickets_response.data)
except Exception as e:
    st.error(f"❌ Failed to load tickets: {str(e)}")
    st.stop()

# Check if 'updated_at' column exists
updated_at_exists = "updated_at" in df.columns

# Ticket List
st.subheader("📋 Ticket List")
for _, ticket in df.iterrows():
    ticket_number = ticket.get("ticket_number", "N/A")
    request_type = ticket.get("request", "Unknown")
    priority = ticket.get("priority", "Unknown")
    submission_time = ticket.get("submission_time", "Unknown")
    description = ticket.get("description", "No Description")
    attachment_url = ticket.get("attachment", None)

    with st.expander(f"🔹 Ticket #{ticket_number} - {request_type}"):
        st.write(f"**Priority:** {priority}")
        st.write(f"**Date Submitted:** {submission_time}")
        st.write(f"**Description:** {description}")

        if attachment_url:
            st.markdown(f"[📎 Download Attachment]({attachment_url})")

        # Status Update
        current_status = ticket.get("status", "Open")
        new_status = st.selectbox(
            "🔄 Update Status:",
            ["Open", "In Progress", "Resolved", "Closed"],
            index=["Open", "In Progress", "Resolved", "Closed"].index(current_status),
            key=f"status_{ticket_number}",
        )

        if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
            try:
                # Prepare the update data
                update_data = {"status": new_status}
                if updated_at_exists:
                    update_data["updated_at"] = datetime.now().isoformat()

                # Execute update query
                update_response = supabase.table("tickets").update(update_data).eq("ticket_number", ticket_number).execute()

                if update_response.data:
                    st.success(f"✅ Ticket {ticket_number} updated to '{new_status}'")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update ticket {ticket_number}. No matching record found.")
            except Exception as e:
                st.error(f"❌ Error updating ticket {ticket_number}: {str(e)}")
