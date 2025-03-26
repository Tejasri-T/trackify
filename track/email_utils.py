from flask_mail import Message
from datetime import datetime, timedelta
from track import mail,db
from track.models import Subscription,User



def get_due_subscriptions():
    """Fetch subscriptions due within the next 7 days for users with notifications enabled."""
    upcoming_date = datetime.utcnow().date() + timedelta(days=7)

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
    subject = f"Reminder: {sub_name} Payment Due Soon!"
    body = (f"Hello,\n\nYour subscription '{sub_name}' is due on {due_date}. "
            "Make sure to complete your payment to avoid service interruptions.\n\n"
            "Regards,\nTrackify Team")

    msg = Message(subject=subject, recipients=[user_email], body=body)
    
    try:
        mail.send(msg)
        subscription.last_notified = datetime.utcnow().date()  # Update notification time
        db.session.commit()
        print(f"Reminder sent to {user_email} for {sub_name}.")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {str(e)}")

