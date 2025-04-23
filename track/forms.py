from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField,EmailField,PasswordField,SubmitField,FloatField, DateField, SelectField
from wtforms.validators import DataRequired, Email , EqualTo, Optional,Length,ValidationError,NumberRange
from track.models import User
from wtforms.validators import ValidationError
from datetime import date

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("This username is taken.  Try another. ")

    def validate_email(self, email_check):
        user = User.query.filter_by(email=email_check.data).first()
        if user:
            raise ValidationError("Email is already registered. Did you mean to log in?")

    username = StringField("Full Name", validators=[DataRequired(), Length(min=3 , max = 50) ], render_kw={"placeholder": "Enter your name"})
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField("Password", validators=[DataRequired(),Length(min=4)], render_kw={"placeholder": "Enter your password"})
    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[DataRequired(), EqualTo("password", message="Oops! Your passwords don’t match—try again!")],
        render_kw={"placeholder": "Confirm your password"}
    )
    submit = SubmitField("Register", render_kw={"class": "register-btn"})



class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


    def validate_due_date(form, field):
        if form.subscription_type.data == 'free_trial' and not field.data:
            raise ValidationError('Due date is required for free trials.')

class SubscriptionForm(FlaskForm):
    
    name = StringField('Subscription Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    subscription_type = SelectField('Subscription Type', choices=[
        ('normal', 'Normal Subscription'),
        ('free_trial', 'Free Trial')
    ], validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('health', 'Health'),
        ('others', 'Others')
    ])
    submit = SubmitField('Add Subscription')
    def validate_due_date(self, field):
        if field.data < date.today():
            raise ValidationError('Due date cannot be in the past!')
    
    


class EditSubscriptionForm(FlaskForm):
    name = StringField('Subscription Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    subscription_type = SelectField('Subscription Type', choices=[
        ('normal', 'Normal Subscription'),
        ('free_trial', 'Free Trial')
    ], validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('health', 'Health'),
        ('others', 'Others')
    ])
    submit = SubmitField('Update Subscription')

class EditUsernameForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Update username')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')]
    )
    submit = SubmitField('Change Password')

class BudgetForm(FlaskForm):
    budget = FloatField('Enter Budget', validators=[DataRequired(), NumberRange(min=0.01, message='Budget must be at least Rs. 0.01')])
    submit = SubmitField('Set Budget')


class NotificationPreferenceForm(FlaskForm):
    notifications_enabled = BooleanField("Enable Notifications")
    notify_before = SelectField(
        "Notify me before due date",
        choices=[('1', '1 day'), ('3', '3 days'), ('7', '1 week')],
        validators=[Optional()]
    )
    submit = SubmitField("Save Preferences")