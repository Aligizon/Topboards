from flask import url_for, request, render_template, redirect, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import adminAuth
from ..model.models import User, Role

@adminAuth.route('/login', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        email = request.form.get('_email')
        password = request.form.get('_password')

        user = User.query.filter(User.is_enabled==True, User.role!=Role.Customer.value).filter_by(email=email).first()

        if user:
            if user.is_enabled:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('adminView.home'))
                else:
                    flash('Incorrect user name or password', category='error')
            else:
                flash('Your account was disabled. Please contact your employer.', category='error')
        else:
            flash('User with this email doesn\'t exist', category='error')

    return render_template('admin/admin_login.html')

@adminAuth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('adminView.home'))