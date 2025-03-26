import streamlit as st
import datetime
import os
from supabase import create_client

# Load Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        # Show the confirmation dialog
        st.session_state.confirm_submission = True

# Show confirmation pop-up
if st.session_state.get("confirm_submission", False):
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

        # Save file if uploaded
        attachment_url = None
        if attachment:
            attachment_dir = "attachments"
            os.makedirs(attachment_dir, exist_ok=True)

            # Avoid duplicate file names
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{attachment.name}"
            attachment_path = os.path.join(attachment_dir, filename)
            
            with open(attachment_path, "wb") as f:
                f.write(attachment.getbuffer())

            attachment_url = attachment_path  # (For now, storing locally; consider uploading to Supabase Storage)

        # Get submission time
        submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert ticket into Supabase
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

        if response[1] is None:
            st.success("✅ Ticket Submitted!")
            st.write("📌 Please wait for a moment, a Data Analyst will come back to you soon.")
            st.write(f"🎫 Your Ticket Number: **{ticket_number}**")
        else:
            st.error("❌ Failed to submit ticket. Please try again.")

        # Reset confirmation state
        st.session_state.confirm_submission = False
    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
