import streamlit as st
import sqlite3
import datetime
import os

# Database connection
conn = sqlite3.connect("helpdesk.db", check_same_thread=False)
cursor = conn.cursor()

# Ensure the tickets table has the correct schema
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_number TEXT UNIQUE,
        lark_email TEXT,
        campaign TEXT,
        impact TEXT,
        request TEXT,
        description TEXT,
        priority TEXT,
        attachment TEXT,
        status TEXT DEFAULT 'Open',
        submission_time TEXT
    );
""")
conn.commit()

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
        attachment_path = None
        if attachment:
            attachment_dir = "attachments"
            os.makedirs(attachment_dir, exist_ok=True)

            # Avoid duplicate file names
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{attachment.name}"
            attachment_path = os.path.join(attachment_dir, filename)

            with open(attachment_path, "wb") as f:
                f.write(attachment.getbuffer())

            # Debugging message
            st.write(f"✅ File saved at: {attachment_path}")

        # Get submission time
        submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert ticket into the database
        cursor.execute("""
            INSERT INTO tickets (ticket_number, lark_email, campaign, impact, request, description, priority, attachment, status, submission_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_number, lark_email, campaign, impact, request, description, priority, attachment_path, "Open", submission_time))
        conn.commit()

        st.success("✅ Ticket Submitted!")
        st.write("📌 Please wait for a moment, a Data Analyst will come back to you soon.")
        st.write(f"🎫 Your Ticket Number: **{ticket_number}**")

        # Reset confirmation state
        st.session_state.confirm_submission = False

    elif cancel:
        st.warning("Submission cancelled. You can modify the details before submitting again.")
        st.session_state.confirm_submission = False

# Close database connection
conn.close()
