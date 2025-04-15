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
    fig.update_layout(showlegend=False, annotations=[dict(text=f"<b>{total_tickets} Total</b>", x=0.5, y=0.5, font_size=20, showarrow=False)])

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Status Summary Table (adapts to theme)
        st.subheader("Status Summary")
        status_dict = status_counts.set_index("Status")["Count"].to_dict()
        summary_html = f"""
        <style>
            .summary-table {{ width: 100%; border-collapse: collapse; }}
            .summary-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        </style>
        <table class='summary-table'>
        <tr><td style='color: red;'><b>🟥 Open:</b></td><td>{status_dict.get("Open", 0)}</td></tr>
        <tr><td style='color: orange;'><b>🟧 In Progress:</b></td><td>{status_dict.get("In Progress", 0)}</td></tr>
        <tr><td style='color: green;'><b>🟩 Resolved:</b></td><td>{status_dict.get("Resolved", 0)}</td></tr>
        <tr><td style='color: gray;'><b>⬜ Closed:</b></td><td>{status_dict.get("Closed", 0)}</td></tr>
        </table>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

    # Delete all closed tickets
    if st.button("Delete All Closed Tickets", help="Removes all tickets marked as Closed"):
        supabase.table("tickets").delete().eq("status", "Closed").execute()
        st.success("All closed tickets have been deleted! ")
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

        status_icon = {"Open": "🟥", "In Progress": "🟧", "Resolved": "🟩", "Closed": "⬜"}.get(status, "⬜")
        st.markdown(f"**{status_icon} Ticket #{ticket_number} - {request_type}**")

        with st.expander("More Information"):
            st.write(f"**Priority:** {priority}")
            st.write(f"**Status:** {status}")
            st.write(f"**Date Submitted:** {submission_time}")
            st.write(f"**Description:** {description}")

            if attachment_url:
                st.markdown(f"[Download Attachment]({attachment_url})")

            new_status = st.selectbox(
                "Update Status:",
                ["Open", "In Progress", "Resolved", "Closed"],
                index=["Open", "In Progress", "Resolved", "Closed"].index(status),
                key=f"status_{ticket_number}"
            )

            if st.button(f"Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                try:
                    ph_timezone = pytz.timezone("Asia/Manila")
                    formatted_time = datetime.now(pytz.utc).astimezone(ph_timezone).strftime("%Y-%m-%d %H:%M:%S")

                    ticket_number_casted = int(ticket_number) if isinstance(ticket_number, (int, float, str)) and str(ticket_number).isdigit() else ticket_number

                    # Update ticket status in the tickets table
                    response = supabase.table("tickets").update({
                        "status": new_status,
                        "updated_at": formatted_time
                    }).eq("ticket_number", ticket_number_casted).execute()

                    if response.data:
                        st.success(f"Ticket {ticket_number} updated to '{new_status}' at {formatted_time} (PH Time)")

                        # Insert a row into the status_notifications table to trigger Edge Function
                        notification_response = supabase.table("status_notifications").insert({
                            "ticket_number": ticket_number,
                            "status": new_status
                        }).execute()

                        if notification_response.status_code == 200:
                            st.success(f"Notification sent for ticket {ticket_number} status update.")
                        else:
                            st.error("Failed to trigger notification.")

                        st.rerun()
                    else:
                        st.warning(f"No matching ticket found with ticket_number {ticket_number}.")
                except Exception as e:
                    import json
                    error_msg = json.dumps(e.args[0], indent=2) if hasattr(e, 'args') and e.args else str(e)
                    st.error(f"🚨 Error updating ticket #{ticket_number}:\n\n```\n{error_msg}\n```")
