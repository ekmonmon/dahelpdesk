import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client
import asyncio
import threading

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

# Create a placeholder to hold the UI that displays tickets
tickets_container = st.empty()

# Initialize session state with tickets data if not already set
if "tickets_df" not in st.session_state:
    st.session_state.tickets_df = fetch_tickets()

# Define a function that renders the main UI using a provided DataFrame
def display_ui(df: pd.DataFrame):
    if df.empty:
        st.warning("No tickets found in the database.")
        return

    # Sidebar for filtering
    st.sidebar.title("🎯 Ticket Filters")
    impact_options = ["ALL", "Campaign", "Data Analyst"]
    impact_filter = st.sidebar.selectbox("🏢 Filter by Impact:", impact_options, index=0)
    
    request_options = ["ALL"] + (df["request"].unique().tolist() if "request" in df.columns else [])
    request_filter = st.sidebar.selectbox("📜 Filter by Request Type:", request_options, index=0)
    
    status_options = ["ALL"] + df["status"].unique().tolist()
    status_filter = st.sidebar.selectbox("📌 Filter by Status:", status_options, index=0)
    
    priority_options = ["ALL"] + (df["priority"].unique().tolist() if "priority" in df.columns else [])
    priority_filter = st.sidebar.selectbox("🚀 Filter by Priority:", priority_options, index=0)

    # Apply filters
    filtered_df = df.copy()
    if impact_filter != "ALL":
        filtered_df = filtered_df[filtered_df["impact"] == impact_filter]
    if request_filter != "ALL" and "request" in df.columns:
        filtered_df = filtered_df[filtered_df["request"] == request_filter]
    if status_filter != "ALL":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]
    if priority_filter != "ALL" and "priority" in df.columns:
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
        fig = px.pie(status_counts, names="Status", values="Count", title="Ticket Status Distribution", 
                     color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"],
                     hole=0.4)
        fig.update_traces(textinfo='percent+label', pull=[0.1 if x == "Open" else 0 for x in status_counts["Status"]])
        st.plotly_chart(fig)
    
    with col2:
        st.markdown("### Ticket Summary")
        for index, row in status_counts.iterrows():
            st.write(f"**{row['Status']}:** {row['Count']}")

    # Button to delete all closed tickets
    if st.button("🗑️ Delete All Closed Tickets"):
        supabase.table("tickets").delete().match({"status": "Closed"}).execute()
        st.success("All closed tickets have been deleted!")
        # Update the tickets data without rerunning the app
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
        attachment_url = ticket.get("attachment", None)  # Assuming file URL stored in DB

        with st.expander(f"🔹 Ticket #{ticket_number} - {request_type} ({get_status_color(ticket['status'])})"):
            st.write(f"**Priority:** {priority}")
            st.write(f"**Date Submitted:** {submission_time}")
            st.write(f"**Description:** {description}")
            st.write(f"**Last Updated:** {updated_at}")

            # Display download button if there's an attachment URL
            if attachment_url:
                st.markdown(f"[📎 Download Attachment]({attachment_url})")

            # Allow status update within expander
            new_status = st.selectbox("🔄 Update Status:", ["Open", "In Progress", "Resolved", "Closed"], key=f"status_{ticket_number}")
            if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                supabase.table("tickets").update(
                    {"status": new_status, "updated_at": datetime.now().isoformat()}
                ).match({"ticket_number": ticket_number}).execute()
                st.success(f"Ticket {ticket_number} updated to '{new_status}'")
                update_ui()

# Define a function to refresh tickets and update the UI container
def update_ui():
    new_df = fetch_tickets()
    st.session_state.tickets_df = new_df
    tickets_container.empty()
    with tickets_container:
        display_ui(new_df)

# Initially render the UI using the stored tickets data
with tickets_container:
    display_ui(st.session_state.tickets_df)

# Define the realtime update callback (without calling rerun)
def handle_update(payload):
    # On receiving a realtime event, update only the ticket UI
    update_ui()

# Asynchronous function to subscribe to realtime updates
async def subscribe_realtime():
    channel = supabase.realtime.channel("database")
    channel.on_postgres_changes(
        "INSERT",
        schema="public",
        table="tickets",
        callback=handle_update
    ).subscribe()
    await supabase.realtime.listen()

# Run the asynchronous realtime listener in a background thread
def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(subscribe_realtime())

new_loop = asyncio.new_event_loop()
threading.Thread(target=run_asyncio_loop, args=(new_loop,), daemon=True).start()
