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

# Set page layout
st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .header-title {text-align: center; font-size: 32px; font-weight: bold; color: #2C3E50;}
        .summary-box {padding: 15px; border-radius: 8px; background-color: #2C3E50; color: white; margin-bottom: 20px; text-align: center; font-size: 20px;}
        .sidebar-title {font-size: 18px; font-weight: bold;}
        .status-box {display: flex; justify-content: space-between; margin-top: 20px;}
        .status-item {padding: 15px; background-color: #34495E; color: white; border-radius: 8px; text-align: center; width: 23%;}
        .button-container {text-align: center; margin-top: 20px;}
        .status-circle {display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px;}
        .circle-open {background-color: red;}
        .circle-in-progress {background-color: orange;}
        .circle-resolved {background-color: green;}
        .circle-closed {background-color: grey;}
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="header-title">📌 Data Analyst Helpdesk System</p>', unsafe_allow_html=True)

# Load tickets from Supabase
tickets_response = supabase.table("tickets").select("*").execute()
df = pd.DataFrame(tickets_response.data)

if df.empty:
    st.warning("No tickets found in the database.")
else:
    # Sidebar Filters
    st.sidebar.markdown("<p class='sidebar-title'>Ticket Filters</p>", unsafe_allow_html=True)
    impact_filter = st.sidebar.selectbox("Impact", ["ALL"] + df["impact"].dropna().unique().tolist())
    request_filter = st.sidebar.selectbox("Request Type", ["ALL"] + df["request"].dropna().unique().tolist())
    status_filter = st.sidebar.selectbox("Status", ["ALL"] + df["status"].dropna().unique().tolist())
    priority_filter = st.sidebar.selectbox("Priority", ["ALL"] + df["priority"].dropna().unique().tolist())
    
    # Apply Filters
    filtered_df = df.copy()
    if impact_filter != "ALL":
        filtered_df = filtered_df[filtered_df["impact"] == impact_filter]
    if request_filter != "ALL":
        filtered_df = filtered_df[filtered_df["request"] == request_filter]
    if status_filter != "ALL":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]
    if priority_filter != "ALL":
        filtered_df = filtered_df[filtered_df["priority"] == priority_filter]
    
    # Ticket Status Overview
    st.subheader("Status Overview")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.pie(status_counts, names="Status", values="Count", hole=0.4, color="Status",
                  color_discrete_map={"Open": "#E74C3C", "In Progress": "#F39C12", "Resolved": "#2ECC71", "Closed": "#95A5A6"})
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
        for _, row in status_counts.iterrows():
            st.markdown(f"{row['Count']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Delete Closed Tickets Button
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    if st.button("Delete All Closed Tickets"):
        supabase.table("tickets").delete().eq("status", "Closed").execute()
        st.success("All closed tickets deleted!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Ticket List
    st.subheader("Ticket List")
    for _, ticket in filtered_df.iterrows():
        ticket_number = ticket["ticket_number"]
        request_type = ticket["request"]
        status = ticket["status"]
        description = ticket["description"]
        submission_time = ticket["submission_time"].replace("T", " ")
        
        circle_class = "circle-open" if status == "Open" else "circle-in-progress" if status == "In Progress" else "circle-resolved" if status == "Resolved" else "circle-closed"
        
        st.markdown(f"<span class='status-circle {circle_class}'></span> **#{ticket_number} - {request_type}**", unsafe_allow_html=True)
        
        with st.expander("More Information"):
            st.markdown(f"""
                <div class="summary-box">
                    <p><b>Status:</b> {status}</p>
                    <p><b>Date Submitted:</b> {submission_time}</p>
                    <p><b>Description:</b> {description}</p>
                </div>
            """, unsafe_allow_html=True)
            
            new_status = st.selectbox("Update Status", ["Open", "In Progress", "Resolved", "Closed"],
                                      index=["Open", "In Progress", "Resolved", "Closed"].index(status), key=f"status_{ticket_number}")
            
            if st.button(f"Update #{ticket_number}", key=f"update_{ticket_number}"):
                ph_timezone = pytz.timezone("Asia/Manila")
                formatted_time = datetime.now(pytz.utc).astimezone(ph_timezone).strftime("%Y-%m-%d %H:%M:%S")
                supabase.table("tickets").update({"status": new_status, "updated_at": formatted_time}).eq("ticket_number", ticket_number).execute()
                st.success(f"#{ticket_number} updated to '{new_status}'")
                st.rerun()
