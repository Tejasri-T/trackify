from flask import Flask
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail, Message

import threading
import time
import os

app = Flask(__name__)

# Database and Security Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///track.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_very_secure_secret_key')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)



# Email Config
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "trackifynote@gmail.com"
app.config['MAIL_PASSWORD'] = "wqwk tbyb cfhi dduq"
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)
from track import routes
# with app.app_context():
#         try:
#             msg = Message(
#                 subject="✅ Trackify Email Test",
#                 recipients=["tsree0421@gmail.com"],
#                 body="Hello! This is a test email from your Flask app."
#             )
#             mail.send(msg)
#             print("✅ Test email sent from __init__.py!")
#         except Exception as e:
#             print("❌ Failed to send test email:", str(e))


from track.email_utils import send_reminder_email, get_due_subscriptions
from track.models import User, Subscription

def email_scheduler():
    """Runs indefinitely, checking for due subscriptions every hour."""
    with app.app_context():
        while True:
            print("Checking for due subscriptions...")
            subscriptions = get_due_subscriptions()

            for sub in subscriptions:
                if not sub.last_notified or sub.last_notified < datetime.now(timezone.utc).date() - timedelta(days=1):
                    user = User.query.get(sub.user_id)
                    if user and user.notification_enabled:
                        send_reminder_email(user.email, sub.name, sub.due_date, sub)
                       
            time.sleep(3600)  # Sleep for 1 hour before checking again

# #Start the background task in a separate thread
threading.Thread(target=email_scheduler, daemon=True).start()
