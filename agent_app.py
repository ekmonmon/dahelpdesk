import streamlit as st
from supabase import create_client, Client
import datetime
import os

# Load Supabase credentials securely from Streamlit secrets
SUPABASE_URL = st.secrets["https://twyoryuxgvskitkvauyx.supabase.co"]
SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state for confirmation pop-up
if "confirm_submission" not in st.session_state:
    st.session_state.confirm_submission = False

st.title("🎫 Agent Helpdesk - Submit a Ticket")

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

    # If user confirms, process the submission
    if confirm:
        ticket_number = f"DAH-{datetime.datetime.now().strftime('%H%M%S')}"
        
        # Save file if uploaded
        attachment_url = None
        if attachment:
            attachment_bytes = attachment.getvalue()
            filename = f"attachments/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{attachment.name}"
            response = supabase.storage.from_("attachments").upload(filename, attachment_bytes)
            if response.status_code == 200:
                attachment_url = response.json().get("publicURL")
                st.write(f"✅ File uploaded successfully: {attachment_url}")
            else:
                st.error("❌ File upload failed.")
                attachment_url = None
        
        submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert ticket into Supabase
        data = {
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
        response = supabase.table("tickets").insert(data).execute()
        
        if response.status_code == 201:
            st.success("✅ Ticket Submitted!")
            st.write("📌 A Data Analyst will review your request soon.")
            st.write(f"🎫 Your Ticket Number: **{ticket_number}**")
        else:
            st.error("❌ Ticket submission failed. Please try again.")
        
        st.session_state.confirm_submission = False

    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
