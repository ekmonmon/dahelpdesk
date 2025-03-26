import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Set page title and layout
st.set_page_config(page_title="Data Analyst Helpdesk", page_icon="📊", layout="wide")

st.title("📊 Data Analyst Helpdesk")

# Connect to the SQLite database
conn = sqlite3.connect("helpdesk.db", check_same_thread=False)
cursor = conn.cursor()

# Load tickets into a DataFrame
query = "SELECT * FROM tickets"
df = pd.read_sql(query, conn)

# Ensure the DataFrame is not empty
if df.empty:
    st.warning("No tickets found in the database.")
else:
    # Sidebar for filtering
    st.sidebar.title("🎯 Ticket Filters")

    impact_options = ["ALL", "Campaign", "Data Analyst"]
    impact_filter = st.sidebar.selectbox("🏢 Filter by Impact:", impact_options, index=0)
    
    request_options = ["ALL"] + df["request"].unique().tolist() if "request" in df.columns else ["ALL"]
    request_filter = st.sidebar.selectbox("📜 Filter by Request Type:", request_options, index=0)
    
    status_options = ["ALL"] + df["status"].unique().tolist()
    status_filter = st.sidebar.selectbox("📌 Filter by Status:", status_options, index=0)
    
    priority_options = ["ALL"] + df["priority"].unique().tolist() if "priority" in df.columns else ["ALL"]
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

    # Delete all closed tickets button
    if st.button("🗑️ Delete All Closed Tickets"):
        cursor.execute("DELETE FROM tickets WHERE status = 'Closed'")
        conn.commit()
        st.success("All closed tickets have been deleted!")
        st.rerun()

    # Ticket list
    st.subheader("📋 Ticket List")
    for _, ticket in filtered_df.iterrows():
        ticket_number = ticket.get("ticket_number", "N/A")
        request_type = ticket.get("request", "No Request Type")
        priority = ticket.get("priority", "N/A")
        submission_time = ticket.get("submission_time", "N/A")
        description = ticket.get("description", "No description available")
        updated_at = ticket.get("updated_at", "None")
        attachment_path = ticket.get("attachment", None)  # Get the attachment path

        with st.expander(f"🔹 Ticket #{ticket_number} - {request_type} ({get_status_color(ticket['status'])})"):
            st.write(f"**Priority:** {priority}")
            st.write(f"**Date Submitted:** {submission_time}")
            st.write(f"**Description:** {description}")
            st.write(f"**Last Updated:** {updated_at}")

            # Display the download button if there's an attachment
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as file:
                    st.download_button(
                        label="📎 Download Attachment",
                        data=file,
                        file_name=os.path.basename(attachment_path),
                        mime="application/octet-stream",
                    )

            # Allow status update within expander
            new_status = st.selectbox("🔄 Update Status:", ["Open", "In Progress", "Resolved", "Closed"], key=f"status_{ticket_number}")
            if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                cursor.execute("UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_number = ?", 
                               (new_status, datetime.now(), ticket_number))
                conn.commit()
                st.success(f"Ticket {ticket_number} updated to '{new_status}'")
                st.rerun()  # Auto-refresh the page

# Close DB connection
conn.close()
