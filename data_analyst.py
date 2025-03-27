import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set page title and layout
st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")

st.title("📌 Data Analyst Helpdesk System")

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
    
    # Ticket Overview Section
    st.subheader("Ticket Status Overview")
    
    col1, col2 = st.columns([2, 1])  # Create two columns: 2/3 width for pie chart, 1/3 for summary

    with col1:
        # Define custom colors for each status
        status_colors = {
            "Open": "red",
            "In Progress": "orange",
            "Resolved": "green",
            "Closed": "grey"
        }

        # Count tickets per status
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        # Create pie chart with custom colors
        fig = px.pie(
            status_counts, 
            names="Status", 
            values="Count", 
            title="Ticket Status Distribution", 
            hole=0.4,
            color="Status",
            color_discrete_map=status_colors
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Summary Statistics
        total_tickets = len(df)
        open_tickets = len(df[df["status"] == "Open"])
        in_progress_tickets = len(df[df["status"] == "In Progress"])
        resolved_tickets = len(df[df["status"] == "Resolved"])
        closed_tickets = len(df[df["status"] == "Closed"])

        st.write("### Ticket Summary")
        st.write(f"🟢 **Total Tickets:** {total_tickets}")
        st.write(f"🔴 **Open Tickets:** {open_tickets}")
        st.write(f"🟠 **In Progress Tickets:** {in_progress_tickets}")
        st.write(f"🟢 **Resolved Tickets:** {resolved_tickets}")
        st.write(f"⚫ **Closed Tickets:** {closed_tickets}")

    # Delete all closed tickets
    if st.button("Delete All Closed Tickets", help="Removes all tickets marked as Closed"):
        supabase.table("tickets").delete().eq("status", "Closed").execute()
        st.success("All closed tickets have been deleted!")
        st.rerun()
    
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
        
        status_color = status_colors.get(status, "black")  # Get color for the status
        st.markdown(f"<b style='color:{status_color}'>■ Ticket #{ticket_number} - {request_type}</b>", unsafe_allow_html=True)
        
        with st.expander("More Information"):
            st.write(f"**Priority:** {priority}")
            st.write(f"**Status:** {status}")
            st.write(f"**Date Submitted:** {submission_time}")
            st.write(f"**Description:** {description}")
            
            if attachment_url:
                st.markdown(f"[Download Attachment]({attachment_url})")
            
            new_status = st.selectbox("Update Status:", ["Open", "In Progress", "Resolved", "Closed"], index=["Open", "In Progress", "Resolved", "Closed"].index(status), key=f"status_{ticket_number}")
            
            if st.button(f"Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                supabase.table("tickets").update({"status": new_status}).eq("ticket_number", ticket_number).execute()
                st.success(f"Ticket {ticket_number} updated to '{new_status}'")
                st.rerun()
