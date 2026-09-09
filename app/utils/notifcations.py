import time
from datetime import datetime

def send_email(to: str, subject: str, body: str):
    """Simulate sending an email (slow operation)."""
    print(f"[EMAIL] Sending to {to}...")
    time.sleep(2)  # Simulate network delay
    print(f"[EMAIL] Sent: '{subject}' to {to}")

    with open("email_log.txt", "a") as f:
        f.write(f"{datetime.now()} | To: {to} | Subject: {subject}\\n")

def generate_report(user_id: int, report_type: str):
    """Simulate generating a report (slow operation)."""
    print(f"[REPORT] Generating {report_type} for user {user_id}...")
    time.sleep(3)  # Simulate heavy computation
    print(f"[REPORT] Complete: {report_type} for user {user_id}")

    with open("report_log.txt", "a") as f:
        f.write(f"{datetime.now()} | User: {user_id} | Type: {report_type}\\n")

def log_activity(user_id: int, action: str):
    """Simulate logging to activity_log.txt file with a timestamp"""
    print(f"[ACTION] Updating Activity Log with action {action} for user {user_id}")
    time.sleep(3)
    print(f"[ACTION] Complete: {action} logged for user {user_id}")

    with open("activity_log.txt", "a") as f:
        f.write(f"{datetime.now()} | User: {user_id}  | Activity logged: {action}\\n")

def send_notification(email: str, message: str):
    """Simulate sending a notification with a 2 second delay"""
    print(f"[NOTIFICATION] Sending to {email}.")
    time.sleep(2)
    print(f"[NOTIFICATION] Sent: '{message}' to {email}")

    with open("notification_log.txt", "a") as f:
        f.write(f"{datetime.now()} | To: {email} | Message: {message}\\n")