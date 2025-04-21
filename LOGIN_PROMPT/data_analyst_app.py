import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from supabase import create_client, Client

st.set_page_config(page_title="Data Analyst Helpdesk", layout="wide")


def run():
# Custom CSS for better UI
    st.markdown("""
        <style>
        .logout-button {
            position: fixed;
            top: 10px;
            right: 20px;
            z-index: 9999;
        }
        .badge {
            display: inline-block;
            padding: 0.35em 0.65em;
            font-size: 0.75em;
            font-weight: 600;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.375rem;
        }
        .badge-red { background-color: #e74c3c; color: white; }
        .badge-orange { background-color: #f39c12; color: white; }
        .badge-green { background-color: #2ecc71; color: white; }
        .badge-gray { background-color: #bdc3c7; color: white; }
        </style>
        <div class="logout-button">
            <form action="/logout">
                <input type="submit" value="Logout" style="padding: 6px 12px; border-radius: 5px; background-color: #e74c3c; color: white; border: none;">
            </form>
        </div>
    """, unsafe_allow_html=True)
    
    st.title("📊 Data Analyst Helpdesk")
    
    # Supabase config
    SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
    SUPABASE_KEY = "YOUR_SUPABASE_KEY"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    LARK_WEBHOOK_URL = "https://open.larksuite.com/open-apis/bot/v2/hook/b6ca6862-ee42-454a-ad5a-c5b34e5fceda"
    
    # Load data
    tickets_response = supabase.table("tickets").select("*").execute()
    df = pd.DataFrame(tickets_response.data)
    
    if df.empty:
        st.warning("No tickets found.")
    else:
        # Organize tabs by status
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
                    badge_color = {
                        "High": "badge-red", 
                        "Medium": "badge-orange", 
                        "Low": "badge-green"
                    }.get(priority, "badge-gray")
    
                    with st.container():
                        st.markdown(f"### {status_icon} Ticket #{ticket_number} - *{request_type}*")
    
                        with st.expander("ℹ️ View Details"):
                            st.markdown(f"**🕒 Submitted:** {submission_time}")
                            st.markdown(f"**🧾 Description:** {description}")
                            if attachment_url:
                                st.markdown(f"[📎 Download Attachment]({attachment_url})")
    
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown(
                                    f"**🎯 Priority:** <span class='badge {badge_color}'>{priority}</span>", 
                                    unsafe_allow_html=True
                                )
                                st.markdown(
                                    f"**📌 Status:** <span class='badge badge-gray'>{status}</span>", 
                                    unsafe_allow_html=True
                                )
    
                            with col2:
                                new_status = st.selectbox(
                                    "Update Status:",
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
                                            st.success(f"✅ Ticket updated to '{new_status}' at {formatted_time} (PH Time)")
    
                                            supabase.table("status_notifications").insert({
                                                "ticket_number": ticket_number,
                                                "status": new_status
                                            }).execute()
    
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
