import smtplib
 import ssl
 import time
 from supabase import create_client, Client
 from email.mime.multipart import MIMEMultipart
 from email.mime.text import MIMEText
 
 # Supabase configuration
 SUPABASE_URL = "https://twyoryuxgvskitkvauyx.supabase.co"
 SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eW9yeXV4Z3Zza2l0a3ZhdXl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Njc1MDgsImV4cCI6MjA1ODU0MzUwOH0.P9M25ysxrIOpucNaUKQ-UzExO_MbF2ucTGovVU-uILk"
 supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
 
 # Email configuration
 SENDER_EMAIL = "your_email@example.com"
 SENDER_PASSWORD = "your_email_password"  # Or use app-specific passwords if you're using Gmail
 SMTP_SERVER = "smtp.gmail.com"
 SMTP_PORT = 465  # For SSL
 
 # Function to fetch ticket data
 def fetch_tickets():
     tickets_response = supabase.table("tickets").select("ticket_number, lark_email, status, updated_at").execute()
     return tickets_response.data
 
 # Function to send an email
 def send_email(receiver_email, subject, body):
     # Create the email content
     message = MIMEMultipart()
     message["From"] = SENDER_EMAIL
     message["To"] = receiver_email
     message["Subject"] = subject
     message.attach(MIMEText(body, "plain"))
 
     # Set up the secure SSL context
     context = ssl.create_default_context()
 
     try:
         # Connect to the Gmail SMTP server and send the email
         with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
             server.login(SENDER_EMAIL, SENDER_PASSWORD)
             server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
             print(f"Email sent to {receiver_email}")
     except Exception as e:
         print(f"Error: {e}")
 
 # Monitor for status changes and send emails
 def monitor_and_notify():
     previous_statuses = {}
 
     while True:
         tickets = fetch_tickets()
 
         for ticket in tickets:
             ticket_number = ticket["ticket_number"]
             lark_email = ticket["lark_email"]
             current_status = ticket["status"]
             updated_at = ticket["updated_at"]
 
             # Check if the status has changed since the last check
             if ticket_number not in previous_statuses or previous_statuses[ticket_number] != current_status:
                 # Prepare the email subject and body
                 subject = f"Ticket #{ticket_number} Status Updated"
                 body = f"Ticket #{ticket_number} has been updated.\n\nCurrent Status: {current_status}\nUpdated At: {updated_at}"
 
                 # Send an email to the user
                 send_email(lark_email, subject, body)
 
                 # Update the previous status to the current status
                 previous_statuses[ticket_number] = current_status
 
         # Wait for a while before checking again
         time.sleep(60)  # Check every minute
 
 if __name__ == "__main__":
     monitor_and_notify()
