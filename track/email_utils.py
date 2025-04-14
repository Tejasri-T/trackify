from flask_mail import Message
from datetime import datetime, timedelta,timezone
from track import mail,db
from track.models import Subscription,User



def get_due_subscriptions():
    """Fetch subscriptions due within the next 7 days for users with notifications enabled."""
    upcoming_date = datetime.now(timezone.utc) + timedelta(days=7)

    due_subscriptions = (
        Subscription.query
        .join(User)
        .filter(
            Subscription.due_date <= upcoming_date,
            User.notification_preferences == True  # Only users who want notifications
        )
        .all()
    )
    
    return due_subscriptions




def send_reminder_email(user_email, sub_name, due_date, subscription):
    """Sends an email reminder for a subscription."""
    if due_date < datetime.now(timezone.utc).date() and (subscription.last_notified is None or subscription.last_notified < subscription.due_date):
        subject = f"⚠️ Urgent: {sub_name} Subscription expired!"
        body = (
            f"Hello,\n\n"
            f"We noticed that your subscription '{sub_name}' has expired on {due_date}.\n"
            f"To continue enjoying the service without interruption, please renew your subscription as soon as possible.\n\n"
            f"If you've already taken action, feel free to ignore this message.\n\n"
            f"Best regards,\n"
            f"Trackify Team"
        )
    else:
        subject = f"Reminder: {sub_name} Payment Due Soon!"
        body = (f"Hello,\n\nYour subscription '{sub_name}' is due on {due_date}. "
            "Make sure to complete your payment to avoid service interruptions.\n\n"
            "Regards,\nTrackify Team")

    
   
    msg = Message(subject=subject, recipients=[user_email], body=body)
    
    try:
        mail.send(msg)
        subscription.last_notified = datetime.now(timezone.utc)  # Update notification time
        db.session.commit()
        print(f"Reminder sent to {user_email} for {sub_name}.")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {str(e)}")

