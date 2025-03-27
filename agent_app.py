import streamlit as st
import datetime
from supabase import create_client, Client
import pytz

# Set timezone to Philippines (UTC+8)
ph_tz = pytz.timezone('Asia/Manila')

# Supabase configuration
SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize session state for form freeze
if "form_frozen" not in st.session_state:
    st.session_state.form_frozen = False

if "confirm_submission" not in st.session_state:
    st.session_state.confirm_submission = False

# UI Styling
st.markdown(
    """
    <style>
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-size: 16px;
        }
        .stTextInput, .stSelectbox, .stTextArea, .stFileUploader {
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Agent Helpdesk - Submit a Ticket")
st.markdown("---")

# Form for submitting a ticket
with st.form("ticket_form"):
    st.subheader("Submit a Ticket")
    
    lark_email = st.text_input("Lark Email:", disabled=st.session_state.form_frozen)
    campaign = st.text_input("Campaign:", disabled=st.session_state.form_frozen)
    
    impact = st.selectbox("Impact:", ["Data Analyst", "Campaign"], disabled=st.session_state.form_frozen)
    
    request = st.selectbox("Request Type:", [
        "Data Extraction", "Report Issue", "New Report Request",
        "Dashboard Update", "System Issue", "Other"
    ], disabled=st.session_state.form_frozen)
    
    description = st.text_area("Description:", disabled=st.session_state.form_frozen)
    
    priority = st.selectbox("Priority:", ["Critical", "High", "Medium", "Low"], disabled=st.session_state.form_frozen)
    
    attachment = st.file_uploader("📎 Attachment (if any):", type=["png", "jpg", "pdf", "csv", "xlsx", "txt"], disabled=st.session_state.form_frozen)
    
    submit_button = st.form_submit_button("Submit Ticket", disabled=st.session_state.form_frozen)

# When Submit is clicked, trigger confirmation pop-up
if submit_button and not st.session_state.form_frozen:
    if not lark_email or not campaign or not request or not description:
        st.error("⚠️ Please fill in all required fields.")
    else:
        st.session_state.confirm_submission = True

# Show confirmation pop-up
if st.session_state.confirm_submission:
    st.warning("⚠️ Please confirm your submission before proceeding:")
    
    st.write(f" **Lark Email:** {lark_email}")
    st.write(f" **Campaign:** {campaign}")
    st.write(f" **Impact:** {impact}")
    st.write(f" **Request Type:** {request}")
    st.write(f" **Priority:** {priority}")
    st.write(f" **Description:** {description}")
    
    confirm = st.button("✅ Confirm Submission")
    cancel = st.button("❌ Cancel")

    if confirm:
        ticket_number = f"DAH-{datetime.datetime.now().strftime('%H%M%S')}"

        attachment_url = None
        if attachment:
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{attachment.name}"

            try:
                # Read file content
                file_bytes = attachment.read()

                # Upload file directly to Supabase Storage
                res = supabase.storage.from_("attachments").upload(filename, file_bytes)

                # Generate public URL for the uploaded file
                attachment_url = f"{SUPABASE_URL}/storage/v1/object/public/attachments/{filename}"
            
            except Exception as e:
                st.error(f"❌ File upload failed: {str(e)}")
                attachment_url = None

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
        
        try:
            response = supabase.table("tickets").insert(data).execute()
            
            if response and "error" not in response:
                st.success("✅ Ticket Submitted!")
                st.write("Please wait for a moment, a Data Analyst will come back to you soon.")
                st.write(f"🎫 Your Ticket Number: **{ticket_number}**")
                
                # Freeze form fields after successful submission
                st.session_state.form_frozen = True

            else:
                st.error("❌ Error submitting ticket. Please try again.")
                st.write(response)

        except Exception as e:
            st.error(f"❌ Failed to submit ticket: {str(e)}")

        st.session_state.confirm_submission = False

    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False
