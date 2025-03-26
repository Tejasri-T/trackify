from track import db , login_manager
from track import bcrypt
from flask_login import UserMixin
from datetime import datetime,timezone

@login_manager.user_loader
def load_user(user_id ):
    return User.query.get(int(user_id ))


class User(db.Model,UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password_hash = db.Column(db.String(255), nullable=False)  
    profile_picture = db.Column(db.String(255), nullable=True)  
    monthly_budget = db.Column(db.Float, nullable=True)  
    notification_preferences = db.Column(db.Boolean, default=True)  
    last_login = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) 
    total_subscriptions = db.Column(db.Integer, default=0)
    total_monthly_cost = db.Column(db.Float, default=0.0)  
    is_verified = db.Column(db.Boolean, default=False) 
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade="all, delete-orphan")


    @property
    def password(self): 
        return self.password 
    
    @password.setter
    def password(self,plainpass):
        self.password_hash = bcrypt.generate_password_hash(plainpass).decode('utf-8')

    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password) 


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    cost = db.Column(db.Integer, nullable=False, default=0)
    subscription_type = db.Column(db.String(15), nullable=False, default="normal")  
    due_date = db.Column(db.Date, nullable=False) 
    category = db.Column(db.String(30), nullable=False)
    last_notified = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    def __repr__(self):
        return (f"Subscription(name='{self.name}', cost={self.cost}, "
                f"subscription_type='{self.subscription_type}', due_date={self.due_date}, "
                f"category='{self.category}', user_id={self.user_id})")

    def set_cost(self):
        """Automatically sets cost to 0 if the subscription is a free trial."""
        if self.subscription_type == "free_trial":
            self.cost = 0
