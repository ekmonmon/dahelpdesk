import streamlit as st
import datetime
import os
from supabase import create_client, Client
import datetime
import pytz

# Set timezone to Philippines (UTC+8)
ph_tz = pytz.timezone('Asia/Manila')

# Get current time in PH timezone


# Supabase configuration
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state for confirmation pop-up
if "confirm_submission" not in st.session_state:
    st.session_state.confirm_submission = False

st.title("🎛 Agent Helpdesk - Submit a Ticket")

# Form for submitting a ticket
with st.form("ticket_form"):
    st.subheader("🗙 Submit a Ticket")
    
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
            
            # Upload to Supabase Storage (Ensure you have a bucket named "attachments")
            with open(attachment_path, "rb") as f:
                res = supabase.storage.from_("attachments").upload(filename, f)
            
            attachment_url = f"{SUPABASE_URL}/storage/v1/object/public/attachments/{filename}"
            st.write(f"✅ File uploaded to: {attachment_url}")

        submission_time = datetime.datetime.now(ph_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Insert into Supabase
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
            "submission_time": submission_time,
        }
        response = supabase.table("tickets").insert(data).execute()
        
        if response.get("status_code", 200) < 300:
            st.success("✅ Ticket Submitted!")
            st.write("📌 Please wait for a moment, a Data Analyst will come back to you soon.")
            st.write(f"🎫 Your Ticket Number: **{ticket_number}**")
        else:
            st.error("❌ Error submitting ticket. Please try again.")
            st.write(response)
        
        st.session_state.confirm_submission = False
    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
