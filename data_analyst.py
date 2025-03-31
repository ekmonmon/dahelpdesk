import streamlit as st
import pandas as pd
import plotly.express as px
import pytz
from datetime import datetime
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")

# Load tickets from Supabase
tickets_response = supabase.table("tickets").select("*").execute()
df = pd.DataFrame(tickets_response.data)

if df.empty:
    st.warning("No tickets found in the database.")
else:
    # Sidebar filters
    st.sidebar.title("Ticket Filters")
    impact_filter = st.sidebar.selectbox("Filter by Impact:", ["ALL"] + df["impact"].dropna().unique().tolist(), index=0)
    request_filter = st.sidebar.selectbox("Filter by Request Type:", ["ALL"] + df["request"].dropna().unique().tolist(), index=0)
    status_filter = st.sidebar.selectbox("Filter by Status:", ["ALL"] + df["status"].dropna().unique().tolist(), index=0)
    priority_filter = st.sidebar.selectbox("Filter by Priority:", ["ALL"] + df["priority"].dropna().unique().tolist(), index=0)
    search_query = st.sidebar.text_input("Search Ticket Number:")
    
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
    if search_query:
        filtered_df = filtered_df[filtered_df["ticket_number"].astype(str).str.contains(search_query, case=False, na=False)]
    
    # Ticket Overview: Pie Chart and Status Summary
    st.subheader("Ticket Status Overview")
    
    # Define custom colors for each status
    status_colors = {"Open": "red", "In Progress": "orange", "Resolved": "green", "Closed": "grey"}
    
    # Count tickets per status (based on filtered data)
    status_counts = filtered_df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    total_tickets = status_counts["Count"].sum()
    
    # Create pie chart
    fig = px.pie(status_counts, names="Status", values="Count", hole=0.4, color="Status", color_discrete_map=status_colors)
    
    # Remove labels beside the pie chart
    fig.update_layout(showlegend=False, annotations=[
        dict(text=f"<b>{total_tickets} Total</b>", x=0.5, y=0.5, font_size=20, showarrow=False)
    ])
    
    # Display pie chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Status Summary Table (adapts to theme)
    st.subheader("Status Summary")
    summary_html = """
    <style>
        .summary-table { width: 100%; border-collapse: collapse; }
        .summary-table td { padding: 10px; border-bottom: 1px solid #ddd; }
    </style>
    <table class='summary-table'>
    <tr><td style='color: red;'><b>🟥 Open:</b></td><td>{open_count}</td></tr>
    <tr><td style='color: orange;'><b>🟧 In Progress:</b></td><td>{in_progress_count}</td></tr>
    <tr><td style='color: green;'><b>🟩 Resolved:</b></td><td>{resolved_count}</td></tr>
    <tr><td style='color: gray;'><b>⬜ Closed:</b></td><td>{closed_count}</td></tr>
    </table>
    """.format(
        open_count=status_counts.set_index("Status").get("Open", {}).get("Count", 0),
        in_progress_count=status_counts.set_index("Status").get("In Progress", {}).get("Count", 0),
        resolved_count=status_counts.set_index("Status").get("Resolved", {}).get("Count", 0),
        closed_count=status_counts.set_index("Status").get("Closed", {}).get("Count", 0)
    )
    st.markdown(summary_html, unsafe_allow_html=True)
    
    # Delete all closed tickets
    if st.button("Delete All Closed Tickets", help="Removes all tickets marked as Closed"):
        supabase.table("tickets").delete().eq("status", "Closed").execute()
        st.success("All closed tickets have been deleted!")
        st.rerun()
