import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from supabase import create_client, Client

# Supabase Credentials
SUPABASE_URL = "https://zqycetikgrqgzbzrxzok.supabase.co"  # Replace with your actual Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxeWNldGlrZ3JxZ3pienJ4em9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5NTMzOTMsImV4cCI6MjA1ODUyOTM5M30.uNYXbCjTJJS2spGuq4EMPdUxAcQGeekEwAG2AGb1Yt4"  # Replace with your actual Supabase key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set page title and layout
st.set_page_config(page_title="Data Analyst Helpdesk", page_icon="📊", layout="wide")
st.title("📊 Data Analyst Helpdesk")

# Load tickets from Supabase
@st.cache_data(ttl=60)
def load_tickets():
    response = supabase.table("tickets").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

df = load_tickets()

# Ensure DataFrame is not empty
if df.empty:
    st.warning("⚠️ No tickets found in the database.")
    st.stop()

# Sidebar for filtering
st.sidebar.title("🎯 Ticket Filters")

impact_options = ["ALL", "Campaign", "Data Analyst"]
impact_filter = st.sidebar.selectbox("🏢 Filter by Impact:", impact_options, index=0)

request_options = ["ALL"] + df["request"].dropna().unique().tolist() if "request" in df.columns else ["ALL"]
request_filter = st.sidebar.selectbox("📜 Filter by Request Type:", request_options, index=0)

status_options = ["ALL"] + df["status"].dropna().unique().tolist()
status_filter = st.sidebar.selectbox("📌 Filter by Status:", status_options, index=0)

priority_options = ["ALL"] + df["priority"].dropna().unique().tolist() if "priority" in df.columns else ["ALL"]
priority_filter = st.sidebar.selectbox("🚀 Filter by Priority:", priority_options, index=0)

# Apply filters
filtered_df = df.copy()
if impact_filter != "ALL":
    filtered_df = filtered_df[filtered_df["impact"] == impact_filter]
if request_filter != "ALL":
    filtered_df = filtered_df[filtered_df["request"] == request_filter]
if status_filter != "ALL":
    filtered_df = filtered_df[filtered_df["status"] == status_filter]
if priority_filter != "ALL":
    filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

# Status color mapping
def get_status_color(status):
    colors = {"Open": "🔴 Open", "In Progress": "🟠 In Progress", "Resolved": "🟢 Resolved", "Closed": "⚫ Closed"}
    return colors.get(status, "⚪ Unknown")

# Ticket Overview Pie Chart with Count Summary
st.subheader("📊 Ticket Status Overview")
status_counts = df["status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.pie(
        status_counts, names="Status", values="Count", title="Ticket Status Distribution",
        color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"], hole=0.4
    )
    fig.update_traces(textinfo='percent+label', pull=[0.1 if x == "Open" else 0 for x in status_counts["Status"]])
    st.plotly_chart(fig)

with col2:
    st.markdown("### Ticket Summary")
    for _, row in status_counts.iterrows():
        st.write(f"**{row['Status']}:** {row['Count']}")

# Delete all closed tickets button
if st.button("🗑️ Delete All Closed Tickets"):
    response = supabase.table("tickets").delete().eq("status", "Closed").execute()
    if response.status_code == 204:
        st.success("✅ All closed tickets have been deleted!")
        st.rerun()
    else:
        st.error(f"❌ Error deleting tickets: {response}")

# Ticket list
st.subheader("📋 Ticket List")
for _, ticket in filtered_df.iterrows():
    ticket_number = ticket.get("ticket_number", "N/A")
    request_type = ticket.get("request", "No Request Type")
    priority = ticket.get("priority", "N/A")
    submission_time = ticket.get("submission_time", "N/A")
    description = ticket.get("description", "No description available")
    updated_at = ticket.get("updated_at", "None")
    attachment_path = ticket.get("attachment", None)

    with st.expander(f"🔹 Ticket #{ticket_number} - {request_type} ({get_status_color(ticket['status'])})"):
        st.write(f"**Priority:** {priority}")
        st.write(f"**Date Submitted:** {submission_time}")
        st.write(f"**Description:** {description}")
        st.write(f"**Last Updated:** {updated_at}")

        # Attachment Download (from Supabase storage)
        if attachment_path:
            file_url = f"https://your-supabase-bucket-url/{attachment_path}"  # Replace with actual Supabase storage URL
            st.markdown(f"[📎 Download Attachment]({file_url})", unsafe_allow_html=True)

        # Status Update
        new_status = st.selectbox(
            "🔄 Update Status:",
            ["Open", "In Progress", "Resolved", "Closed"],
            index=["Open", "In Progress", "Resolved", "Closed"].index(ticket["status"]),
            key=f"status_{ticket_number}",
        )

        if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
            response = supabase.table("tickets").update(
                {"status": new_status, "updated_at": datetime.utcnow().isoformat()}
            ).eq("ticket_number", ticket_number).execute()

            if response.status_code == 200:
                st.success(f"✅ Ticket {ticket_number} updated to '{new_status}'")
                st.rerun()
            else:
                st.error(f"❌ Error updating ticket {ticket_number}: {response}")
