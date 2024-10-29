from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.login.data) | (User.email == form.login.data)).first()
        if user:
            # First, try to verify with bcrypt
            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            # If bcrypt fails, check if the password matches the stored hash directly
            # This is to handle cases where the password was not re-hashed during restore
            elif user.password_hash == form.password.data:
                # If it matches, re-hash the password with bcrypt
                user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                db.session.commit()
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
        flash('Login unsuccessful. Please check email/username and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

# ... (keep other routes unchanged)
