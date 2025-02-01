from flask import url_for, request, redirect, flash, current_app as app
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth
from ..model.models import User, Role, UserType, Role
from ..model import db



@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('_email')
        password = request.form.get('_password')

        user = User.query.filter(User.role==Role.Customer.value, User.type==UserType.Permanent.value).filter_by(email=email).first()

        if user:
            if user.is_enabled:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully', category='success')
                    login_user(user, remember=True)
                else:
                    # flash('Incorrect user name or password', category='loginError')
                    flash('Incorrect user name or password', category='error')
            else:
                flash('Your account was disabled. Please contact our support team.', category='error')
        else:
            flash('User with this email doesn\'t exist', category='error')

    return redirect(url_for('homeView.home'))

@auth.route('/signUp', methods = ['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        firstName = request.form.get('_firstName')
        lastName = request.form.get('_lastName')
        phoneNumber = request.form.get('_phoneNumber')
        email = request.form.get('_email')
        password = request.form.get('_password')
        passwordConfirm = request.form.get('_password_confirm')
        dataAgreement = request.form.get('_data-processing-agreement')

        user = User.query.filter_by(email=email).first()

        if len(firstName) < 2:
            flash('Name must be greater than 1 character', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
        elif len(phoneNumber) < 6:
            flash('Phone number must be greater than 5 characters', category='error')
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
        elif password != passwordConfirm:
            flash('Passwords don\'t match', category='error')
        elif not dataAgreement:
            flash('You have to accept the data processing agreement', category='error')
        elif user:
            flash('User with this email already exists', category='error')
        else:
            try: 
                new_user = User(first_name=firstName, last_name=lastName, phone_number=phoneNumber, email=email, role=Role.Customer.value, type=UserType.Permanent.value, password=generate_password_hash(password))
                db.session.add(new_user)
            except Exception as e:
                db.session.rollback()
                app.logger.error(e)
                flash('An error occurred', category='error')
                return redirect(url_for('homeView.home'))
            
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')

    return redirect(url_for('homeView.home'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homeView.home'))