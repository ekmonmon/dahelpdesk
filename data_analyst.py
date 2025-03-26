import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client
import asyncio

# Supabase credentials
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set page title and layout
st.set_page_config(page_title="Data Analyst Helpdesk", page_icon="📊", layout="wide")
st.title("📊 Data Analyst Helpdesk")

# Function to fetch tickets from Supabase
def fetch_tickets():
    response = supabase.table("tickets").select("*").execute()
    return pd.DataFrame(response.data)

# Initialize session state with tickets data if not already set
if "tickets_df" not in st.session_state:
    st.session_state.tickets_df = fetch_tickets()

# Function to display the UI
def display_ui(df: pd.DataFrame):
    if df.empty:
        st.warning("No tickets found in the database.")
        return

    # Sidebar filters
    st.sidebar.title("🎯 Ticket Filters")
    impact_filter = st.sidebar.selectbox("🏢 Filter by Impact:", ["ALL", "Campaign", "Data Analyst"], index=0)
    request_filter = st.sidebar.selectbox("📜 Filter by Request Type:", ["ALL"] + df["request"].dropna().unique().tolist(), index=0)
    status_filter = st.sidebar.selectbox("📌 Filter by Status:", ["ALL"] + df["status"].dropna().unique().tolist(), index=0)
    priority_filter = st.sidebar.selectbox("🚀 Filter by Priority:", ["ALL"] + df["priority"].dropna().unique().tolist(), index=0)

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

    # Status Pie Chart
    st.subheader("📊 Ticket Status Overview")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.pie(status_counts, names="Status", values="Count", title="Ticket Status Distribution",
                     color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"], hole=0.4)
        st.plotly_chart(fig)
    
    with col2:
        st.markdown("### Ticket Summary")
        for index, row in status_counts.iterrows():
            st.write(f"**{row['Status']}:** {row['Count']}")

    # Delete closed tickets button
    if st.button("🗑️ Delete All Closed Tickets"):
        supabase.table("tickets").delete().match({"status": "Closed"}).execute()
        st.success("All closed tickets deleted!")
        update_ui()

    # Ticket list
    st.subheader("📋 Ticket List")
    for _, ticket in filtered_df.iterrows():
        ticket_number = ticket.get("ticket_number", "N/A")
        request_type = ticket.get("request", "No Request Type")
        priority = ticket.get("priority", "N/A")
        submission_time = ticket.get("submission_time", "N/A")
        description = ticket.get("description", "No description available")
        updated_at = ticket.get("updated_at", "None")
        attachment_url = ticket.get("attachment", None)

        with st.expander(f"🔹 Ticket #{ticket_number} - {request_type} ({ticket['status']})"):
            st.write(f"**Priority:** {priority}")
            st.write(f"**Date Submitted:** {submission_time}")
            st.write(f"**Description:** {description}")
            st.write(f"**Last Updated:** {updated_at}")

            if attachment_url:
                st.markdown(f"[📎 Download Attachment]({attachment_url})")

            new_status = st.selectbox("🔄 Update Status:", ["Open", "In Progress", "Resolved", "Closed"], key=f"status_{ticket_number}")
            if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                supabase.table("tickets").update({"status": new_status, "updated_at": datetime.now().isoformat()}).match({"ticket_number": ticket_number}).execute()
                st.success(f"Ticket {ticket_number} updated to '{new_status}'")
                update_ui()

# Function to update tickets UI
def update_ui():
    st.session_state.tickets_df = fetch_tickets()
    tickets_container.empty()
    with tickets_container:
        display_ui(st.session_state.tickets_df)

# Add a manual refresh button
if st.button("🔄 Refresh Tickets"):
    update_ui()

# Create a placeholder for UI updates
tickets_container = st.empty()
with tickets_container:
    display_ui(st.session_state.tickets_df)

# Function to handle real-time updates
def handle_update(payload):
    update_ui()

# Real-time subscription
async def subscribe_realtime():
    channel = supabase.realtime.channel("public:tickets")
    channel.on("postgres_changes", {"event": "*", "schema": "public", "table": "tickets"}, handle_update).subscribe()
    await supabase.realtime.listen()

# Start real-time listener
asyncio.run(subscribe_realtime())
