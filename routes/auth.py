from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('user_role') != role and session.get('user_role') != 'admin':
                flash('Unauthorized access for your role.', 'danger')
                return redirect(url_for('auth.redirect_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect_by_role(user.role)
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@auth_bp.route('/demo_login/<role>')
def demo_login(role):
    role_email_map = {
        'student': 'student@canteenflow.com',
        'vendor': 'vendor@canteenflow.com',
        'admin': 'admin@canteenflow.com'
    }
    email = role_email_map.get(role, 'student@canteenflow.com')
    user = User.query.filter_by(email=email).first()
    if user:
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role
        flash(f'Logged in as Demo {role.capitalize()}: {user.name}', 'success')
        return redirect_by_role(user.role)
    flash('Demo user account not found. Please run seed.py first.', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def redirect_dashboard():
    return redirect_by_role(session.get('user_role', 'student'))

def redirect_by_role(role):
    if role == 'vendor':
        return redirect(url_for('vendor.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))
