import time
from supabase import create_client, Client
import resend
import os

# === CONFIG ===
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-api-key"
RESEND_API_KEY = "your-resend-api-key"
TABLE_NAME = "tickets"
CHECK_INTERVAL = 10  # seconds

# === SETUP ===
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
resend.api_key = RESEND_API_KEY

# Keep track of previous statuses
last_statuses = {}

def send_status_email(email: str, status: str, ticket_id: int):
    try:
        response = resend.Emails.send({
            "from": "Helpdesk <your@domain.com>",
            "to": [email],
            "subject": f"Ticket #{ticket_id} Status Updated",
            "html": f"<p>Hello,</p><p>The status of your ticket #{ticket_id} has been updated to: <strong>{status}</strong>.</p>"
        })
        print(f"✅ Email sent to {email} for ticket #{ticket_id}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def check_for_updates():
    global last_statuses

    response = supabase.table(TABLE_NAME).select("id, status, lark_email").execute()
    if not response.data:
        print("No records found.")
        return

    for record in response.data:
        ticket_id = record["id"]
        status = record["status"]
        email = record["lark_email"]

        if ticket_id not in last_statuses:
            last_statuses[ticket_id] = status
        elif last_statuses[ticket_id] != status:
            send_status_email(email, status, ticket_id)
            last_statuses[ticket_id] = status

if __name__ == "__main__":
    print("📡 Watching for status changes in Supabase...")
    while True:
        try:
            check_for_updates()
        except Exception as err:
            print(f"⚠️ Error during check: {err}")
        time.sleep(CHECK_INTERVAL)
