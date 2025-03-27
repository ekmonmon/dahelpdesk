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

# Set page title and layout
st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")
st.markdown("""
    <style>
        .big-title {text-align: center; font-size: 40px; font-weight: bold; color: #2C3E50; margin-bottom: 15px; padding: 15px; background-color: #ECF0F1; border-radius: 10px;}
        .subheader {color: #555; font-size: 18px; margin-bottom: 20px;}
        .card {padding: 15px; margin: 10px 0; border-radius: 8px; background-color: #F4F4F4;}
        .button-container {display: flex; justify-content: flex-end; margin-top: 10px;}
        .status-circle {display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px;}
        .circle-open {background-color: red;}
        .circle-in-progress {background-color: orange;}
        .circle-resolved {background-color: green;}
        .circle-closed {background-color: grey;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">📌 Data Analyst Helpdesk System</p>', unsafe_allow_html=True)

# Load tickets from Supabase
tickets_response = supabase.table("tickets").select("*").execute()
df = pd.DataFrame(tickets_response.data)

if df.empty:
    st.warning("No tickets found in the database.")
else:
    # Sidebar for filtering
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
    
    # Ticket Overview Pie Chart with Summary
    st.subheader("Ticket Status Overview")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(status_counts, names="Status", values="Count", title="Ticket Status Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Status Summary")
        for index, row in status_counts.iterrows():
            st.markdown(f"**{row['Status']}:** {row['Count']} tickets")
    
    # Delete all closed tickets
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    if st.button("Delete All Closed Tickets", help="Removes all tickets marked as Closed"):
        supabase.table("tickets").delete().eq("status", "Closed").execute()
        st.success("All closed tickets have been deleted!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display update message if available
    if "update_message" in st.session_state:
        st.success(st.session_state["update_message"])
        del st.session_state["update_message"]
    
    # Ticket list
    st.subheader("Ticket List")
    for _, ticket in filtered_df.iterrows():
        ticket_number = ticket["ticket_number"]
        request_type = ticket["request"]
        priority = ticket["priority"]
        status = ticket["status"]
        submission_time = ticket["submission_time"].replace("T", " ")
        description = ticket["description"]
        attachment_url = ticket["attachment"]
        
        circle_class = "circle-open" if status == "Open" else "circle-in-progress" if status == "In Progress" else "circle-resolved" if status == "Resolved" else "circle-closed"
        
        st.markdown(f"<span class='status-circle {circle_class}'></span> Ticket #{ticket_number} - {request_type}", unsafe_allow_html=True)
        
        with st.expander("More Information"):
            st.markdown(f"""
                <div class="card">
                    <p><b>Priority:</b> {priority}</p>
                    <p><b>Status:</b> {status}</p>
                    <p><b>Date Submitted:</b> {submission_time}</p>
                    <p><b>Description:</b> {description}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if attachment_url:
                st.markdown(f"[Download Attachment]({attachment_url})")
