from collections import defaultdict
from track import app
from flask import render_template , flash , redirect , url_for, abort,request
from track.models import Subscription , User 
from track.forms import RegisterForm, LoginForm , SubscriptionForm ,EditSubscriptionForm,EditUsernameForm,ChangePasswordForm,BudgetForm
from track import db
from flask_login import login_user,current_user,logout_user,login_required
from sqlalchemy.sql import func
from datetime import datetime,date,timezone ,timedelta
import pandas as pd
from flask import send_file
import os
import time

@app.route('/') 
@app.route('/index')
def index():
    return render_template('index.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user_to_create)
        db.session.commit() 
        login_user(user_to_create)
        return redirect(url_for('dashboard') )
    if form.errors!= {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html',form = form)





@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are Logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check email and password ', category='danger')
    return render_template('login.html' , form = form)


@app.route('/help-support')
def help_support():
    return render_template('help_support.html')


@app.route('/Logout')
@login_required
def logout():
    logout_user()
    flash("You have been Logged out!", category='info')
    return redirect(url_for('index'))



@app.route('/dashboard')
@login_required
def dashboard():
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    total = db.session.query(Subscription).filter(Subscription.due_date > datetime.now(timezone.utc)).count()
    subscription_costs = [sub.cost for sub in subscriptions]  
    total_cost = sum(subscription_costs)
    monthly_costs = defaultdict(int)
    for sub in subscriptions:
        month_year = sub.due_date.strftime('%b %Y')  # Format as 'Jan 2025'
        monthly_costs[month_year] += sub.cost

    # Sort by date
    sorted_costs = dict(sorted(monthly_costs.items(), key=lambda x: datetime.strptime(x[0], "%b %Y")))
    if current_user.monthly_budget == 0 or current_user.monthly_budget is None:
        current_user.monthly_budget = 1500
        db.session.commit() 

    budget = current_user.monthly_budget
    current_time = datetime.now(timezone.utc)  # Use timezone-aware datetime
    budget_used_percentage = (total_cost / budget) * 100

    subscriptions = Subscription.query.filter(
        Subscription.user_id == current_user.id,
        Subscription.due_date.between(current_time, current_time + timedelta(days=7))
    ).all()

    return render_template('dashboard.html',subscriptions=subscriptions,total=total,total_cost=total_cost, subscription_costs= sorted_costs,budget = budget, budget_used_percentage=budget_used_percentage)


@app.route('/addsubscription', methods=['GET', 'POST'])
@login_required
def addsubscription():
    form = SubscriptionForm()
    
    min_date = date.today().strftime('%Y-%m-%d')
    if form.validate_on_submit():
        new_subscription = Subscription(
            name=form.name.data,
            cost=float(form.cost.data),
            subscription_type=form.subscription_type.data,
            due_date=form.due_date.data,
            category=form.category.data,
            user_id=current_user.id
        )

        new_subscription.set_cost()
        
        db.session.add(new_subscription)
        db.session.commit()
        if new_subscription.cost == 0:  # Ensure it's correctly handled
            flash(f"Free trial for {new_subscription.name} added successfully!", "success")
        else:
            flash(f'{new_subscription.name} Subscription added successfully!', 'success')
        return redirect(url_for('subscriptions'))

    return render_template('addsubscription.html', form=form,min_date=min_date)


@app.route('/subscriptions')
@login_required
def subscriptions():
    month = request.args.get('month', type=int)
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()

    # Convert due_date (db.Date) to Unix timestamp at midnight (start of the due date)

    subscriptions_data = [
        {
            "id": sub.id,
            "name": sub.name,
            "cost": sub.cost,
            "subscription_type": sub.subscription_type,
            "due_date": sub.due_date,  # Keep original date for display
            "end_date": int(datetime.combine(sub.due_date, datetime.min.time()).timestamp()),  # Convert to timestamp
            "category": sub.category
        }
        for sub in subscriptions if not month or sub.due_date.month == month
    ]

    return render_template('subscriptions.html', subscriptions=subscriptions_data)


@app.route('/edit_subscription/<int:subscription_id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    form = SubscriptionForm(obj=subscription)

    if form.validate_on_submit():
        subscription.name = form.name.data
        subscription.cost = float(form.cost.data) 
        subscription.subscription_type = form.subscription_type.data
        subscription.due_date = form.due_date.data
        subscription.category = form.category.data
        
        if subscription.subscription_type == "free_trial":
            subscription.cost = 0 

        db.session.commit()

        flash('Subscription updated successfully!', 'success')
        return redirect(url_for('subscriptions'))
    else:
        print("Form errors:", form.errors)   
          

    return render_template('edit_subscription.html', form=form, subscription=subscription)


@app.route('/delete_subscription/<int:subscription_id>', methods=['GET','POST'])
@login_required
def delete_subscription(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    print(f"Current User ID: {current_user.id}, Subscription Owner ID: {subscription.user_id}")

    if subscription.user_id != current_user.id:  
        abort(403)  
    
    db.session.delete(subscription)
    db.session.commit()
    
    flash('Subscription deleted successfully!', 'success')
    return redirect(url_for('subscriptions'))  


@app.route('/budgetmanager')
@login_required
def budgetmanager():
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    total = db.session.query(Subscription).count()
    subscription_costs = [sub.cost for sub in subscriptions]  
    total_cost = sum(subscription_costs)
    categories = ['entertainment', 'utilities', 'health', 'others']
    category_costs = {cat: 0 for cat in categories}  # Initialize all as 0
    form = BudgetForm()
    # Sum up costs for each category
    for sub in subscriptions:
        category = sub.category if sub.category in categories else 'others'
        category_costs[category] += sub.cost

    # if current_user.monthly_budget == 0 or current_user.monthly_budget is None:
    #     current_user.monthly_budget = 1500
    #     db.session.commit() 

    budget = current_user.monthly_budget 


    return render_template('budgetmanager.html',subscriptions=subscriptions,total=total,total_cost=total_cost, category_costs=list(category_costs.values()),budget=budget,form=form)

@app.route('/settings_modal')
@login_required
def settings_modal():
    return render_template('includes/settings_modal.html')


@app.route('/edit_username', methods=['GET', 'POST'])
@login_required
def edit_username():
    form = EditUsernameForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Username updated successfully!', 'success')

        next_page = request.referrer
        return redirect(next_page) if next_page else redirect(url_for("dashboard"))
    

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password_correction(form.current_password.data) and form.current_password.data != form.new_password.data and form.new_password.data == form.confirm_password.data:
            current_user.password = form.new_password.data
            db.session.commit()
            flash('Password updated successfully!', 'success')
        else:
            if not current_user.check_password_correction(form.current_password.data):
                flash('Old password is incorrect. Please try again.', 'danger')
            elif form.current_password.data == form.new_password.data:
                flash('New password must be different from old password.', 'danger')
            elif form.new_password.data != form.confirm_password.data:
                flash('New password and Confirm password must match.', 'danger')
   
    next_page = request.referrer
    return redirect(next_page) if next_page else redirect(url_for("dashboard"))
    
@app.route('/deactivate', methods=['GET','POST'])
@login_required
def deactivate():
    user = User.query.get_or_404(current_user.id)
    
    if not current_user.id:  
        abort(403)  
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Account deactivated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        budget = form.budget.data
        current_user.monthly_budget = budget
        db.session.commit()
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('budgetmanager'))
    else:
        flash('Invalid budget value(Budget should atleast be Rs.0.01). Please try again.', 'danger')
        return redirect(url_for('budgetmanager'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')


def calculate_reports():
    monthly_spending = {}
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    for sub in subscriptions:
        month = sub.due_date.strftime("%Y-%m") 
        monthly_spending[month] = monthly_spending.get(month, 0) + sub.cost

    report_data = []
    for month, spending in monthly_spending.items():
        budget_status = "Over Budget" if spending > current_user.monthly_budget else "Under Budget"
        report_data.append([month, spending, current_user.monthly_budget, budget_status])

    return report_data

@app.route('/export_financial_report_excel')
def export_financial_report_excel():
    report_data = calculate_reports()
    
    # Create DataFrame
    df = pd.DataFrame(report_data, columns=["Month", "Total Spending", "Budget", "Over/Under Budget"])
    
    # Save as Excel file
    file_path = os.path.join(os.getcwd(), "financial_report.xlsx")
    df.to_excel(file_path, index=False)
    
    return send_file(file_path, as_attachment=True)
    
@app.route('/export_subscriptions_excel')
def export_subscriptions_excel():
    # import os
    # print("Current working directory:", os.getcwd())
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    data = [
    {
        "Subscription Name": sub.name,
        "Cost (₹)": sub.cost,
        "Subscription Type": sub.subscription_type,
        "Due Date": sub.due_date.strftime("%Y-%m-%d"),  # Format date properly
        "Category": sub.category
    }
    for sub in subscriptions
]
    df_subscriptions = pd.DataFrame(data)  # Create DataFrame for subscriptions

    
    file_path = os.path.join(os.getcwd(), "subscriptions.xlsx")
    df_subscriptions.to_excel(file_path, index=False)  # Save to Excel

    return send_file(file_path, as_attachment=True)
    


@app.context_processor
def inject_forms():
    return {"edit_username_form": EditUsernameForm(),
        "change_password_form": ChangePasswordForm(),}



if __name__ == '__main__':
    app.run(debug=True)
