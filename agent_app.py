import streamlit as st
from supabase import create_client, Client
import datetime
import os

# Supabase credentials
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🎫 Agent Helpdesk - Submit a Ticket")

# Initialize session state for confirmation pop-up
if "confirm_submission" not in st.session_state:
    st.session_state.confirm_submission = False

# Form for submitting a ticket
with st.form("ticket_form"):
    st.subheader("📝 Submit a Ticket")

    lark_email = st.text_input("📧 Lark Email:")
    campaign = st.text_input("📢 Campaign:")

    impact = st.selectbox("❌ Impact:", ["Data Analyst", "Campaign"])

    request = st.selectbox("🛠 Request Type:", [
        "Data Extraction", "Report Issue", "New Report Request",
        "Dashboard Update", "System Issue", "Other"
    ])

    description = st.text_area("🗒 Description:")

    priority = st.selectbox("⚡ Priority:", ["Critical", "High", "Medium", "Low"])

    attachment = st.file_uploader("📎 Attachment (if any):", type=["png", "jpg", "pdf", "csv", "xlsx", "txt"])

    submit_button = st.form_submit_button("🚀 Submit Ticket")

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
        # Generate a unique ticket number
        ticket_number = f"DAH-{datetime.datetime.now().strftime('%H%M%S')}"

        # Upload file if provided
        attachment_url = None
        if attachment:
            file_content = attachment.read()
            file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{attachment.name}"
            
            response = supabase.storage.from_("attachments").upload(file_name, file_content, content_type=attachment.type)
            if response:
                attachment_url = f"{SUPABASE_URL}/storage/v1/object/public/attachments/{file_name}"

        # Get submission time
        submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert ticket into Supabase
        ticket_data = {
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
        }

        response = supabase.table("tickets").insert(ticket_data).execute()
        if response:
            st.success("✅ Ticket Submitted!")
            st.write(f"🎫 Your Ticket Number: **{ticket_number}**")

        # Reset confirmation state
        st.session_state.confirm_submission = False

    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
