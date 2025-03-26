import streamlit as st
import datetime
import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://zqycetikgrqgzbzrxzok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpxeWNldGlrZ3JxZ3pienJ4em9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5NTMzOTMsImV4cCI6MjA1ODUyOTM5M30.uNYXbCjTJJS2spGuq4EMPdUxAcQGeekEwAG2AGb1Yt4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state for confirmation pop-up
if "confirm_submission" not in st.session_state:
    st.session_state.confirm_submission = False

st.title("\U0001F39B Agent Helpdesk - Submit a Ticket")

# Form for submitting a ticket
with st.form("ticket_form"):
    st.subheader("\U0001F4DD Submit a Ticket")
    lark_email = st.text_input("\U0001F4E7 Lark Email:")
    campaign = st.text_input("\U0001F4E2 Campaign:")
    impact = st.selectbox("\u274C Impact:", ["Data Analyst", "Campaign"])
    request = st.selectbox("\U0001F6E0 Request Type:", [
        "Data Extraction", "Report Issue", "New Report Request",
        "Dashboard Update", "System Issue", "Other"
    ])
    description = st.text_area("\U0001F5D2 Description:")
    priority = st.selectbox("\u26A1 Priority:", ["Critical", "High", "Medium", "Low"])
    attachment = st.file_uploader("\U0001F4CE Attachment (if any):", type=["png", "jpg", "pdf", "csv", "xlsx", "txt"])
    submit_button = st.form_submit_button("\U0001F680 Submit Ticket")

# When Submit is clicked, trigger confirmation pop-up
if submit_button:
    if not lark_email or not campaign or not request or not description:
        st.error("⚠️ Please fill in all required fields.")
    else:
        st.session_state.confirm_submission = True

# Show confirmation pop-up
if st.session_state.confirm_submission:
    st.warning("⚠️ Please confirm your submission before proceeding:")
    st.write(f"📧 **Lark Email:** {lark_email}")
    st.write(f"📢 **Campaign:** {campaign}")
    st.write(f"❌ **Impact:** {impact}")
    st.write(f"🛠 **Request Type:** {request}")
    st.write(f"⚡ **Priority:** {priority}")
    st.write(f"🗒 **Description:** {description}")
    
    confirm = st.button("✅ Confirm Submission")
    cancel = st.button("❌ Cancel")
    
    if confirm:
        ticket_number = f"DAH-{datetime.datetime.now().strftime('%H%M%S')}"
        attachment_url = None

        if attachment:
            attachment_dir = "attachments"
            os.makedirs(attachment_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{attachment.name}"
            attachment_path = os.path.join(attachment_dir, filename)
            with open(attachment_path, "wb") as f:
                f.write(attachment.getbuffer())
            attachment_url = attachment_path  # Modify this to store in cloud storage if needed

        submission_time = datetime.datetime.now().isoformat()

        response = supabase.table("tickets").insert({
            "ticket_number": ticket_number,
            "lark_email": lark_email,
            "campaign": campaign,
            "impact": impact,
            "request": request,
            "description": description,
            "priority": priority,
            "attachment": attachment_url,
            "status": "Open",
            "submission_time": submission_time
        }).execute()

        if response and not response.get("error"):
            st.success("✅ Ticket Submitted!")
            st.write("📌 Please wait for a moment, a Data Analyst will come back to you soon.")
            st.write(f"🎫 Your Ticket Number: **{ticket_number}**")
        else:
            st.error(f"❌ Failed to submit ticket. Error: {response.get('error', 'Unknown error')}")

        st.session_state.confirm_submission = False
    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
