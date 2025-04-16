import streamlit as st
import pandas as pd
import plotly.express as px
import pytz
import requests
import json
from datetime import datetime
from supabase import create_client, Client

def data_analyst_dashboard():
    st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")

    # Supabase configuration
    SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    LARK_WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/b6ca6862-ee42-454a-ad5a-c5b34e5fceda"

    # This is for testing the bot
    #
    #if st.button("Send Test Lark Message"):
    #    test_message = {
    #        "msg_type": "text",
    #        "content": {
    #            "text": "✅ Hello from Streamlit! If you see this, the webhook works!"
    #       }
    #    }
    #    r = requests.post(LARK_WEBHOOK_URL, json=test_message)
    #    st.text(f"Lark Test Status Code: {r.status_code}")
    #    st.text(f"Response: {r.text}")
    #---

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
                    
                        # Update ticket
                        response = supabase.table("tickets").update({
                            "status": new_status,
                            "updated_at": formatted_time
                        }).eq("ticket_number", ticket_number_casted).execute()
                    
                        if response.data:
                            st.success(f"Ticket {ticket_number} updated to '{new_status}' at {formatted_time} (PH Time)")
                    
                            # Logging into status_notifications
                            try:
                                log_response = supabase.table("status_notifications").insert({
                                    "ticket_number": ticket_number,
                                    "status": new_status
                                }).execute()
                            
                            except Exception as insert_error:
                                import traceback
                                st.error("🚨 Failed to insert into status_notifications:")
                                st.code(traceback.format_exc())
                    
                            # Send Lark message
                            lark_message = {
                                "msg_type": "interactive",
                                "card": {
                                    "elements": [
                                        {
                                            "tag": "hr"
                                        },
                                        {
                                            "tag": "div",
                                            "text": {
                                                "content": f"Ticket Number: **{ticket_number}**\n"
                                                        f"Updated Status: **{new_status}**\n"
                                                        f"Timestamp: {formatted_time} (PH Time)",
                                                "tag": "lark_md"
                                            }
                                        }
                                    ],
                                    "header": {
                                        "title": {
                                            "tag": "plain_text",
                                            "content": f"📢 Ticket Status Update",
                                        }
                                    }
                                }
                            }

                    
                            lark_response = requests.post(LARK_WEBHOOK_URL, json=lark_message)
                    
                            if lark_response.status_code == 200:
                                st.success("📤 Lark notification sent!")
                            else:
                                st.warning(f"⚠️ Lark webhook failed (status {lark_response.status_code})")
                    
                            st.rerun()
                        else:
                            st.warning(f"❗ No matching ticket found with ticket_number = {ticket_number_casted}")
                    
                    except Exception as e:
                        import traceback
                        error_trace = traceback.format_exc()
                        st.error(f"🚨 Error updating ticket #{ticket_number}:\n\n```\n{error_trace}\n```")
