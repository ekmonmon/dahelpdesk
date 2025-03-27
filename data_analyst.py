import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set page layout
st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")

# Title
st.title("📌 Data Analyst Helpdesk System")

# Load tickets from Supabase
tickets_response = supabase.table("tickets").select("*").execute()
df = pd.DataFrame(tickets_response.data)

if df.empty:
    st.warning("No tickets found in the database.")
else:
    # Sidebar Filters
    st.sidebar.header("Filters")
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
    
    # Status Overview
    st.subheader("Status Overview")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    st.dataframe(status_counts)
    
    # Delete Closed Tickets Button
    if st.button("Delete All Closed Tickets"):
        supabase.table("tickets").delete().eq("status", "Closed").execute()
        st.success("All closed tickets deleted!")
        st.rerun()
    
    # Ticket List
    st.subheader("Ticket List")
    for _, ticket in filtered_df.iterrows():
        ticket_number = ticket["ticket_number"]
        request_type = ticket["request"]
        status = ticket["status"]
        description = ticket["description"]
        submission_time = ticket["submission_time"].replace("T", " ")
        
        st.markdown(f"**#{ticket_number} - {request_type}**")
        with st.expander("More Information"):
            st.write(f"**Status:** {status}")
            st.write(f"**Date Submitted:** {submission_time}")
            st.write(f"**Description:** {description}")
            
            new_status = st.selectbox("Update Status", ["Open", "In Progress", "Resolved", "Closed"],
                                      index=["Open", "In Progress", "Resolved", "Closed"].index(status), key=f"status_{ticket_number}")
            
            if st.button(f"Update #{ticket_number}", key=f"update_{ticket_number}"):
                ph_timezone = pytz.timezone("Asia/Manila")
                formatted_time = datetime.now(pytz.utc).astimezone(ph_timezone).strftime("%Y-%m-%d %H:%M:%S")
                supabase.table("tickets").update({"status": new_status, "updated_at": formatted_time}).eq("ticket_number", ticket_number).execute()
                st.success(f"#{ticket_number} updated to '{new_status}'")
                st.rerun()
