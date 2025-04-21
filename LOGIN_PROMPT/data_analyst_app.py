import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Data Analyst Dashboard", layout="wide")

# --- SUPABASE CONFIG ---
url = st.secrets["https://wuugzjctcrysqddghhtk.supabase.co"]
key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"]
supabase = create_client(url, key)

def run():
    st.title("📊 Data Analyst Helpdesk Dashboard")

    # --- Fetch Data ---
    ticket_data = supabase.table("tickets").select("*").execute().data
    df = pd.DataFrame(ticket_data)
    df['submission_time'] = pd.to_datetime(df['submission_time'])
    df = df.sort_values("submission_time", ascending=False)

    # --- Metrics ---
    status_counts = df['status'].value_counts()
    open_count = status_counts.get("Open", 0)
    progress_count = status_counts.get("In Progress", 0)
    resolved_count = status_counts.get("Resolved", 0)
    closed_count = status_counts.get("Closed", 0)

    # --- Metrics UI ---
    with st.container():
        st.subheader("🎯 Ticket Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟥 Open", open_count)
        col2.metric("🟧 In Progress", progress_count)
        col3.metric("🟩 Resolved", resolved_count)
        col4.metric("⬜ Closed", closed_count)

    st.markdown("---")

    # --- Sidebar Filters ---
    with st.sidebar:
        st.title("🔎 Filter Tickets")
        with st.expander("📂 Filter Options", expanded=True):
            impact_filter = st.selectbox("Impact", ["ALL"] + df["impact"].dropna().unique().tolist())
            request_filter = st.selectbox("Request Type", ["ALL"] + df["request"].dropna().unique().tolist())
            status_filter = st.selectbox("Status", ["ALL"] + df["status"].dropna().unique().tolist())
            priority_filter = st.selectbox("Priority", ["ALL"] + df["priority"].dropna().unique().tolist())
            search_query = st.text_input("🔎 Ticket Number")

    # --- Apply Filters ---
    filtered_df = df.copy()
    if impact_filter != "ALL":
        filtered_df = filtered_df[filtered_df["impact"] == impact_filter]
    if request_filter != "ALL":
        filtered_df = filtered_df[filtered_df["request"] == request_filter]
    if status_filter != "ALL":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]
    if priority_filter != "ALL":
        filtered_df = filtered_df[filtered_df["priority"] == priority_filter]
    if search_query:
        filtered_df = filtered_df[filtered_df["ticket_number"].astype(str).str.contains(search_query)]

    st.subheader(f"📋 Tickets ({len(filtered_df)})")

    # --- Display Tickets as Cards ---
    for _, row in filtered_df.iterrows():
        ticket_id = row["id"]
        ticket_number = row["ticket_number"]
        impact = row["impact"]
        request_type = row["request"]
        priority = row["priority"]
        status = row["status"]
        description = row["description"]
        submission_time = row["submission_time"].strftime("%Y-%m-%d %H:%M:%S")

        with st.container():
            st.markdown(f"""
                <div style='
                    padding: 1rem;
                    margin-bottom: 1.5rem;
                    border-radius: 12px;
                    background-color: #f9f9f9;
                    border: 1px solid #e0e0e0;
                '>
                    <h4>{ticket_number} - {request_type}</h4>
                    <p><strong>Status:</strong> {status} | <strong>Priority:</strong> {priority} | <strong>Impact:</strong> {impact}</p>
                    <p><strong>Submitted:</strong> {submission_time}</p>
                    <p><strong>Description:</strong> {description}</p>
            """, unsafe_allow_html=True)

            # --- Status Update Form ---
            with st.form(key=f"form_{ticket_id}"):
                new_status = st.selectbox("Update Status", ["Open", "In Progress", "Resolved", "Closed"], index=["Open", "In Progress", "Resolved", "Closed"].index(status))
                submitted = st.form_submit_button("✅ Update")
                if submitted and new_status != status:
                    supabase.table("tickets").update({"status": new_status}).eq("id", ticket_id).execute()
                    supabase.table("status_notifications").insert({"ticket_id": ticket_id, "new_status": new_status}).execute()
                    st.toast(f"✅ Ticket {ticket_number} updated to '{new_status}'")
                    st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

