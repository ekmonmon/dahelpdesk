import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from supabase import create_client, Client

# Page config
st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")


def run():
# Custom CSS for logout button and general UI
    st.markdown("""
        <style>
        .logout-button {
            position: fixed;
            top: 15px;
            right: 30px;
            z-index: 1001;
        }
        .logout-button button {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .ticket-container {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        }
        </style>
        <div class="logout-button">
            <form action="/logout" method="get">
                <button type="submit">Logout</button>
            </form>
        </div>
    """, unsafe_allow_html=True)
    
    st.title("📊 Data Analyst Helpdesk")
    
    # Supabase config
    SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    LARK_WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"
    
    # Load ticket data
    tickets_response = supabase.table("tickets").select("*").execute()
    df = pd.DataFrame(tickets_response.data)
    
    if df.empty:
        st.warning("No tickets found.")
        st.stop()
    
    # Define status tabs
    status_tabs = ["Open", "In Progress", "Resolved", "Closed"]
    tab_objs = st.tabs([f"📌 {status}" for status in status_tabs])
    
    for idx, status in enumerate(status_tabs):
        with tab_objs[idx]:
            status_df = df[df["status"] == status]
    
            if status_df.empty:
                st.info(f"No tickets currently marked as **{status}**.")
                continue
    
            for _, ticket in status_df.iterrows():
                ticket_number = ticket["ticket_number"]
                request_type = ticket["request"]
                priority = ticket["priority"]
                status = ticket["status"]
                submission_time = ticket["submission_time"].replace("T", " ")
                description = ticket["description"]
                attachment_url = ticket["attachment"]
    
                status_icon = {"Open": "🟥", "In Progress": "🟧", "Resolved": "🟩", "Closed": "⬜"}.get(status, "⬜")
                badge_color = {"High": "red", "Medium": "orange", "Low": "green"}.get(priority, "gray")
    
                with st.container():
                    st.markdown(f"""
                        <div class="ticket-container">
                            <h4>{status_icon} Ticket #{ticket_number} - <em>{request_type}</em></h4>
                            <details>
                                <summary>ℹ️ Information</summary>
                                <p><strong>🕒 Submitted:</strong> {submission_time}</p>
                                <p><strong>🧾 Description:</strong> {description}</p>
                                {'<p><a href="' + attachment_url + '">📎 Download Attachment</a></p>' if attachment_url else ''}
                                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                    <div>
                                        <p><strong>🎯 Priority:</strong> <span style="color:{badge_color}; font-weight:bold">{priority}</span></p>
                                        <p><strong>📌 Status:</strong> <strong>{status}</strong></p>
                                    </div>
                                    <div>
                    """, unsafe_allow_html=True)
    
                    new_status = st.selectbox(
                        f"Update Status (Ticket #{ticket_number}):",
                        status_tabs,
                        index=status_tabs.index(status),
                        key=f"status_{ticket_number}"
                    )
    
                    if st.button(f"✅ Update Ticket #{ticket_number}", key=f"update_{ticket_number}"):
                        try:
                            ph_timezone = pytz.timezone("Asia/Manila")
                            formatted_time = datetime.now(pytz.utc).astimezone(ph_timezone).strftime("%Y-%m-%d %H:%M:%S")
    
                            ticket_number_casted = int(ticket_number) if str(ticket_number).isdigit() else ticket_number
    
                            response = supabase.table("tickets").update({
                                "status": new_status,
                                "updated_at": formatted_time
                            }).eq("ticket_number", ticket_number_casted).execute()
    
                            if response.data:
                                st.success(f"Ticket {ticket_number} updated to '{new_status}' at {formatted_time} (PH Time)")
    
                                # Log update
                                supabase.table("status_notifications").insert({
                                    "ticket_number": ticket_number,
                                    "status": new_status
                                }).execute()
    
                                # Lark Notification
                                lark_message = {
                                    "msg_type": "interactive",
                                    "card": {
                                        "elements": [
                                            {"tag": "hr"},
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
                                st.warning(f"❗ Ticket {ticket_number} not found.")
                        except Exception as e:
                            import traceback
                            st.error(f"🚨 Error:\n```\n{traceback.format_exc()}\n```")
    
                    st.markdown("</div></div></details></div>", unsafe_allow_html=True)
