import streamlit as st
import datetime
import os
from supabase import create_client, Client

# Load Supabase credentials from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

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
        # Show the confirmation dialog
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
            file_path = os.path.join(attachment_dir, filename)

            with open(file_path, "wb") as f:
                f.write(attachment.getbuffer())

            # Upload to Supabase Storage (optional)
            try:
                supabase.storage.from_("ticket_attachments").upload(file_path, filename)
                attachment_url = f"{SUPABASE_URL}/storage/v1/object/public/ticket_attachments/{filename}"
            except Exception as e:
                st.error(f"🚨 File upload failed: {str(e)}")

        # Get submission time
        submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert ticket into Supabase
        try:
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

            # Debugging Step: Print API response
            st.write("🔍 API Response:", response)

            # Check for errors in response
            if "error" in response and response["error"]:
                st.error(f"🚨 Submission Failed: {response['error']['message']}")
            else:
                st.success("✅ Ticket Submitted!")
                st.write(f"🎫 Your Ticket Number: **{ticket_number}**")

        except Exception as e:
            st.error(f"🚨 Submission Failed: {str(e)}")

        # Reset confirmation state
        st.session_state.confirm_submission = False

    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
