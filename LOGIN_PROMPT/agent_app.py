import streamlit as st
import datetime
from supabase import create_client, Client
import pytz

def run():
    # Set timezone to Philippines (UTC+8)
    ph_tz = pytz.timezone('Asia/Manila')

    # Supabase configuration
    SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"  # replace this with an environment variable for security
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Initialize session state
    if "confirm_submission" not in st.session_state:
        st.session_state.confirm_submission = False
    if "form_disabled" not in st.session_state:
        st.session_state.form_disabled = False
    if "submitted_ticket" not in st.session_state:
        st.session_state.submitted_ticket = None
    if "submitted_data" not in st.session_state:
        st.session_state.submitted_data = None

    st.title("Agent Helpdesk - Submit a Ticket")
    st.markdown("---")

    # Hide Streamlit toolbar
    st.markdown("""
        <style>
        div[data-testid='stToolbar'] {
            display:none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Step 1: Ticket Form
    with st.form("ticket_form"):
        st.subheader("Submit a Ticket")

        lark_email = st.text_input("Lark Email:", disabled=st.session_state.form_disabled)
        campaign = st.selectbox("Campaign:", ["", "AEON", "AIQON", "BANK OF MAKATI", "BANKARD", "BDO", "BDO 60DPD", "BDO AR", "BDO AUTO LOAN", 
         "BDO AUTO SKIP", "BDO HOME LOAN", "BDO HOMELOAN COLLECT", "BDO HOMELOAN SKIP", "BDO INSURANCE", 
         "BDO PRE LEGAL", "BDO PRU", "BPI AUTO", "BPI AUTO SKIP", "BPI BANKO", "BPI BANKO", 
         "BPI CARDS 30 DPD", "BPI CARDS XDAYS", "BPI PL XDAYS", "BPI RBANK CARDS 30DPD", "BUSINESS LOAN", 
         "CBC", "CBS AUTO LOAN", "CBS HOMELOAN", "CBS PERSONAL LOAN", "CEBU PL", "CEBUANA LHUILLIER", 
         "CHINA BANK SAVINGS", "COLLECTIUS", "CSB", "CSB REPO", "DAVPL", "EWB", "EWB AUTO", "ESQUIRE", 
         "FHL SALMON", "FUSE", "GARNET", "GENERAL", "HOME CREDIT", "HSBG", "HSBM", "HSBC UAE", "INVESTREE PH", 
         "LEGAL BNB MSME", "LEGAL BNB SL", "LEGAL BMI MCL", "LEGAL BPI", "LEGAL BPI BSL", "LEGAL BDO", 
         "LEGAL CSB DEPED", "LEGAL CSB MCL", "LEGAL HSBC", "LEGAL RCBC", "LEGAL SBC", "LEGAL SBF", 
         "MAD120DPD", "MAD150DPD", "MAD150DPD PL", "MAD180DPD", "MADCEBU 1 AND 2", "MADCEBU 180DPD", 
         "MADDAV 120DPD", "MADDAV 150DPD", "MADDAV1", "MADDAV2", "MADILO 1 AND 2", "MADILO 180DPD", "MADPL1", 
         "MALAYAN SAVINGS BANK", "MALAYAN SB PL", "MAYA", "MBA", "MBTC P2", "MBTC PA", "MCC", "MCC 30DPD", 
         "MCC AP13", "MCC P4", "MCC P90", "MCC PL", "MITSU MOTOR LOAN CURING", "MITSU MOTOR LOAN RECOV", 
         "MSME", "MSME NON WRITE", "NBD CARDS", "NCCF SALARY LOAN", "ONB", "ORICO AUTO LOAN", "PIF - MINDANAO", 
         "PIF - NCR", "PIF - NORTH LUZON", "PIF - SOUTH LUZON", "PIF - VISAYAS", "PIF LEGAL", "PL RECO 1", 
         "PL RECO 2", "PL RECO 3", "PNB HOMELOAN", "PRE LEGAL BPI CARDS", "PRE LEGAL CSB MCL", "PRELEGAL BNB MSME", 
         "PRELEGAL BNB SL", "PRELEGAL BMI MCL", "PRELEGAL BPI BSL", "PRELEGAL BNB SL", "PRELEGAL BPI BSL", 
         "PRELEGAL CSB DEPED", "PRELEGAL CSB MCL", "PRELEGAL HSBC", "PRELEGAL RCBC", "PRELEGAL SBF FINANCE", 
         "PRELEGAL SBC", "PSB", "PSB AUTO", "PSB AUTO CURING", "RCBC AUTO LOAN", "RCBC PRE WRITE", 
         "RECO 1 CARDS", "RECO 2 CARDS", "RECO 3 CARDS", "RECO SPECIAL PROJECT", "RIZAL MICROBANK", 
         "ROBINSONS", "ROB AUTO", "ROB BIKE", "SARISUKI", "SBC - CARDS", "SBC - CURING", "SBC - PL", 
         "SBC AUTO - CURING", "SBC AUTO LOAN", "SBC HOMELOAN", "SBF Motor Loan", "SBF Personal Loan", 
         "SUMISHO", "TALA EDC", "TENDOPAY", "TEST", "TOYOTA LEVEL 3", "TONIK", "UBP - CARDS", "UBP - COMBANK", 
         "UBP - SEEKCAP", "UBP - SME", "UBP - SME DPD", "UBP PRE WRITE CURING", "UD CASH LOAN", "UNIONDIGITAL", 
         "UNO"], disabled=st.session_state.form_disabled)
        impact = st.selectbox("Impact:", ["", "Data Analyst", "Campaign"], disabled=st.session_state.form_disabled)
        request = st.selectbox("Request Type:", ["", "Data Extraction", "Report Issue", "New Report Request", "Dashboard Update", "System Issue", "Other"], disabled=st.session_state.form_disabled)
        description = st.text_area("Description:", disabled=st.session_state.form_disabled)
        priority = st.selectbox("Priority:", ["", "Critical", "High", "Medium", "Low"], disabled=st.session_state.form_disabled)
        attachment = st.file_uploader("📎 Attachment (if any):", type=["png", "jpg", "pdf"], disabled=st.session_state.form_disabled)
        
        submit_button = st.form_submit_button("Submit Ticket")

    # Step 2: Validate required fields
    if submit_button:
        if not lark_email or not campaign or not request or not description:
            st.error("⚠️ Please fill in all required fields.")
        else:
            st.session_state.confirm_submission = True

    # Step 3: Confirmation message
    if st.session_state.confirm_submission and not st.session_state.submitted_ticket:
        st.warning("⚠️ Please confirm your submission before proceeding:")

        st.write(f"**Lark Email:** {lark_email}")
        st.write(f"**Campaign:** {campaign}")
        st.write(f"**Impact:** {impact}")
        st.write(f"**Request Type:** {request}")
        st.write(f"**Priority:** {priority}")
        st.write(f"**Description:** {description}")

        confirm = st.button("✅ Confirm Submission")
        cancel = st.button("❌ Cancel")

        if confirm:
            st.session_state.form_disabled = True
            st.rerun()
        elif cancel:
            st.warning("Submission cancelled. You can modify the details before submitting again.")
            st.session_state.confirm_submission = False

    # Step 4: Submit to Supabase
    if st.session_state.form_disabled and not st.session_state.submitted_ticket:
        ticket_number = f"DAH-{datetime.datetime.now().strftime('%H%M%S')}"
        submission_time = datetime.datetime.now(ph_tz).strftime('%Y-%m-%d %H:%M:%S')

        data = {
            "ticket_number": ticket_number,
            "lark_email": lark_email,
            "campaign": campaign,
            "impact": impact,
            "request": request,
            "description": description,
            "priority": priority,
            "status": "Open",
            "submission_time": submission_time,
        }

        try:
            response = supabase.table("tickets").insert(data).execute()
            if response and "error" not in response:
                st.session_state.submitted_ticket = ticket_number
                st.session_state.submitted_data = {
                    "ticket_number": ticket_number,
                    "lark_email": lark_email,
                    "campaign": campaign,
                    "impact": impact,
                    "request": request,
                    "priority": priority,
                    "description": description,
                    "submission_time": submission_time,
                }
                st.rerun()
            else:
                st.error("❌ Error submitting ticket. Please try again.")
        except Exception as e:
            st.error(f"❌ Failed to submit ticket: {str(e)}")

    # Step 5: Success Message and Buttons
    if st.session_state.submitted_ticket:
        st.success(f"✅ Ticket Submitted! 🎫 Your Ticket Number: **{st.session_state.submitted_ticket}**")

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("📄 View Submitted Response"):
                submitted = st.session_state.submitted_data
                if submitted:
                    st.info(f"""
                        **Ticket Number:** {submitted['ticket_number']}  
                        **Lark Email:** {submitted['lark_email']}  
                        **Campaign:** {submitted['campaign']}  
                        **Impact:** {submitted['impact']}  
                        **Request Type:** {submitted['request']}  
                        **Priority:** {submitted['priority']}  
                        **Description:** {submitted['description']}  
                        **Submitted At:** {submitted['submission_time']}
                    """)
                else:
                    st.error("❌ No submitted data available.")

        with col2:
            if st.button("📝 Submit Another Ticket"):
                st.session_state.confirm_submission = False
                st.session_state.form_disabled = False
                st.session_state.submitted_ticket = None
                st.session_state.submitted_data = None
                st.rerun()
