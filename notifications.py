# notifications.py (new file)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from storage import get_budget, get_transactions
from datetime import datetime

def send_email_notification(subject, body, to_email):
    # Implementation for sending email notifications
    pass

def check_budget_alerts():
    current_budget = get_budget()
    if not current_budget:
        return
    
    transactions = get_transactions()
    df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
    
    if not df.empty:
        current_month = datetime.now().strftime('%Y-%m')
        monthly_expenses = df[(df['date'].str.startswith(current_month)) & 
                             (df['type'] == 'expense')]['amount'].sum()
        
        utilization = monthly_expenses / current_budget
        
        if utilization > 0.9:
            send_email_notification(
                "Budget Alert: You've exceeded 90% of your budget",
                f"You've spent ${monthly_expenses:.2f} of your ${current_budget:.2f} budget.",
                "user@example.com"
            )
        elif utilization > 0.75:
            send_email_notification(
                "Budget Warning: You've exceeded 75% of your budget",
                f"You've spent ${monthly_expenses:.2f} of your ${current_budget:.2f} budget.",
                "user@example.com"
            )