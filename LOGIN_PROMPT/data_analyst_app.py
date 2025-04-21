import streamlit as st
import pandas as pd
import plotly.express as px
import pytz
import requests
import json
from datetime import datetime
from supabase import create_client, Client

def run():
    st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")
    st.title("📊 Data Analyst Helpdesk")

    SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    LARK_WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/b6ca6862-ee42-454a-ad5a-c5b34e5fceda"

    tickets_response = supabase.table("tickets").select("*").execute()
    df = pd.DataFrame(tickets_response.data)

    if df.empty:
        st.warning("No tickets found in the database.")
        return

    # Sidebar Filters
    with st.sidebar:
        st.title("Filters")
        impact_filter = st.selectbox("Filter by Impact:", ["ALL"] + df["impact"].dropna().unique().tolist(), index=0)
        request_filter = st.selectbox("Filter by Request Type:", ["ALL"] + df["request"].dropna().unique().tolist(), index=0)
        status_filter = st.selectbox("Filter by Status:", ["ALL"] + df["status"].dropna().unique().tolist(), index=0)
        priority_filter = st.selectbox("Filter by Priority:", ["ALL"] + df["priority"].dropna().unique().tolist(), index=0)
        search_query = st.text_input("🔎 Search Ticket Number:")

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

    # Tabs for better structure
    tab1, tab2 = st.tabs(["📈 Overview", "Ticket List"])

    with tab1:
        st.subheader("Ticket Status Overview")
        status_colors = {"Open": "red", "In Progress": "orange", "Resolved": "green", "Closed": "grey"}
        status_counts = filtered_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        total_tickets = status_counts["Count"].sum()

        fig = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.4,
            color="Status",
            color_discrete_map=status_colors
        )
        fig.update_layout(showlegend=False, annotations=[dict(text=f"<b>{total_tickets} Total</b>", x=0.5, y=0.5, font_size=20, showarrow=False)])

        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Status Summary")
            status_dict = status_counts.set_index("Status")["Count"].to_dict()
            summary_html = """
            <style>
                .summary-table { width: 100%; border-collapse: collapse; }
                .summary-table td { padding: 10px; border-bottom: 1px solid #ddd; }
            </style>
            <table class='summary-table'>
            <tr><td style='color: red;'><b>🟥 Open:</b></td><td>{open}</td></tr>
            <tr><td style='color: orange;'><b>🟧 In Progress:</b></td><td>{progress}</td></tr>
            <tr><td style='color: green;'><b>🟩 Resolved:</b></td><td>{resolved}</td></tr>
            <tr><td style='color: gray;'><b>⬜ Closed:</b></td><td>{closed}</td></tr>
            </table>
            """.format(
                open=status_dict.get("Open", 0),
                progress=status_dict.get("In Progress", 0),
                resolved=status_dict.get("Resolved", 0),
                closed=status_dict.get("Closed", 0)
            )
            st.markdown(summary_html, unsafe_allow_html=True)

        with st.expander("Maintenance"):
            if st.button("Delete All Closed Tickets", help="Removes all tickets marked as Closed"):
                supabase.table("tickets").delete().eq("status", "Closed").execute()
                st.success("✅ All closed tickets have been deleted!")
                st.rerun()

    with tab2:
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
            with st.container():
                st.markdown(f"### {status_icon} Ticket #{ticket_number} - {request_type}")
                with st.expander("Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Priority:** {priority}")
                        st.markdown(f"**Submitted:** {submission_time}")
                        st.markdown(f"**Description:**\n{description}")
                    with col2:
                        st.markdown(f"**Status:** {status}")
                        if attachment_url:
                            st.markdown(f"📎 [Download Attachment]({attachment_url})")

                    new_status = st.selectbox(
                        "🛠️ Update Status:",
                        ["Open", "In Progress", "Resolved", "Closed"],
                        index=["Open", "In Progress", "Resolved", "Closed"].index(status),
                        key=f"status_{ticket_number}"
                    )

                    if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                        try:
                            ph_timezone = pytz.timezone("Asia/Manila")
                            formatted_time = datetime.now(pytz.utc).astimezone(ph_timezone).strftime("%Y-%m-%d %H:%M:%S")
                            ticket_number_casted = int(ticket_number) if str(ticket_number).isdigit() else ticket_number

                            # Update ticket
                            response = supabase.table("tickets").update({
                                "status": new_status,
                                "updated_at": formatted_time
                            }).eq("ticket_number", ticket_number_casted).execute()

                            if response.data:
                                st.success(f"🎉 Ticket {ticket_number} updated to '{new_status}'")

                                # Log to status_notifications
                                try:
                                    supabase.table("status_notifications").insert({
                                        "ticket_number": ticket_number,
                                        "status": new_status
                                    }).execute()
                                except Exception as log_error:
                                    st.error("Error logging notification.")
                                    st.code(str(log_error))

                                # Notify via Lark
                                lark_message = {
                                    "msg_type": "interactive",
                                    "card": {
                                        "elements": [
                                            {"tag": "hr"},
                                            {
                                                "tag": "div",
                                                "text": {
                                                    "content": f"**Ticket #{ticket_number}** status updated to **{new_status}** at {formatted_time}",
                                                    "tag": "lark_md"
                                                }
                                            }
                                        ],
                                        "header": {
                                            "title": {
                                                "tag": "plain_text",
                                                "content": "📢Ticket Status Update"
                                            }
                                        }
                                    }
                                }
                                lark_response = requests.post(LARK_WEBHOOK_URL, json=lark_message)
                                if lark_response.status_code == 200:
                                    st.success("📤 Lark notification sent!")
                                else:
                                    st.warning("⚠️ Failed to notify Lark")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating ticket #{ticket_number}")
                            st.code(str(e))
