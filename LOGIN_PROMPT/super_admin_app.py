import streamlit as st
import plotly.express as px
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="Super Admin Panel", layout="wide")

# Supabase config
SUPABASE_URL = "https://wuugzjctcrysqddghhtk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1dWd6amN0Y3J5c3FkZGdoaHRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3NjY2NTcsImV4cCI6MjA2MDM0MjY1N30.JjraFNEpG-CUDqT77pk9KDlMkdsM_sH3alD50gEm1EE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run():
    st.title("Super Admin Panel")

    tab1, tab2, tab3 = st.tabs(["Ticket Management", "User & Role Management", "Audit Logs"])

    # --------- TAB 1: TICKET MANAGEMENT ---------
    with tab1:
        st.subheader("Ticket Overview")
        tickets_response = supabase.table("tickets").select("*").execute()
        df = pd.DataFrame(tickets_response.data)
    
        if df.empty:
            st.warning("No tickets available.")
        else:
            status_counts = df["status"].value_counts()
            st.dataframe(status_counts.rename_axis("Status").reset_index(name="Count"), use_container_width=True)
    
            # Enhanced pie chart with hole and total ticket count in the center
            st.subheader("Ticket Status Distribution")
            total_tickets = df.shape[0]
            fig = px.pie(
                names=status_counts.index,
                values=status_counts.values,
                title="Tickets by Status",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            # Make it a donut chart by setting the 'hole' parameter
            fig.update_traces(hole=0.4)  # Adjust hole size as needed
    
            # Add total tickets count in the center
            fig.update_layout(
                annotations=[
                    dict(
                        text=f"{total_tickets}",
                        x=0.5, y=0.5,
                        font_size=30,  # Font size for the count
                        showarrow=False,
                        font=dict(size=30, color="black", family="Arial")
                    )
                ],
                title="Tickets by Status"
            )
    
            st.plotly_chart(fig, use_container_width=True)
    
            # Delete closed tickets
            st.subheader("Delete Closed Tickets")
            closed_count = df[df["status"] == "Closed"].shape[0]
            if closed_count == 0:
                st.info("There are no closed tickets to delete.")
            else:
                st.warning(f"You are about to delete **{closed_count}** closed tickets.")
                confirm = st.checkbox("I confirm I want to delete all closed tickets.")
                if st.button("Delete Closed Tickets") and confirm:
                    try:
                        response = supabase.table("tickets").delete().eq("status", "Closed").execute()
                        if response.data:
                            st.success(f"✅ Deleted {len(response.data)} closed tickets.")
                            st.rerun()
                        else:
                            st.warning("No tickets deleted.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    

    # --------- TAB 2: USER & ROLE MANAGEMENT ---------
    with tab2:
        st.subheader("Create or Update User")
    
        # Input fields
        email = st.text_input("User Email")
        password_disabled = email.strip().lower() == "admin"
        password = st.text_input("Password", type="password", disabled=password_disabled)
        role = st.selectbox("Role", ["agent", "analyst", "super_admin"], disabled=password_disabled)
    
        if password_disabled:
            st.warning("Modifying the default admin user is not allowed.")
    
        if st.button("Create/Update User", disabled=password_disabled):
            existing_user = supabase.table("users").select("*").eq("email", email).execute().data
            if existing_user:
                supabase.table("users").update({"password": password, "role": role}).eq("email", email).execute()
                st.success(f"🔄 Updated user `{email}`")
            else:
                supabase.table("users").insert({"email": email, "password": password, "role": role}).execute()
                st.success(f"✅ Created user `{email}`")
    
        st.divider()
    
        st.subheader("Current Users & Roles")
        users_response = supabase.table("users").select("id, email, role").neq("email", "admin").execute()
        user_df = pd.DataFrame(users_response.data)
    
        if not user_df.empty:
            st.dataframe(user_df, use_container_width=True)
        else:
            st.info("No users found.")


        # --------- TAB 3: AUDIT LOGS ---------
    with tab3:
        st.subheader("Recent Ticket Updates")
        ticket_logs = supabase.table("tickets").select("*").order("updated_at", desc=True).limit(100).execute().data
        log_df = pd.DataFrame(ticket_logs)

        if not log_df.empty:
            # Optional: show only relevant columns
            display_cols = ["id", "title", "status", "updated_at", "assigned_to"]
            filtered_df = log_df[display_cols] if all(col in log_df.columns for col in display_cols) else log_df
            st.dataframe(filtered_df.sort_values(by="updated_at", ascending=False), use_container_width=True)
        else:
            st.info("No recent ticket updates found.")
