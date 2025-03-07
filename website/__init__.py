from flask import Flask, redirect, url_for, request
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from os import path
from flask_login import LoginManager
from .model import db
from .model.models import User
from .view import homeView as main_blueprint
from .view import adminView as admin_blueprint
from .controller import auth as auth_blueprint
from .controller import adminAuth as admin_auth_blueprint
    
from datetime import timedelta


def create_app():
    app = Flask(__name__)

    load_dotenv()
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
    app.config["UPLOAD_PATH"] = 'website/static/img/product_images'
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@postgres:5432/{os.getenv("POSTGRES_DB")}'
   

    app.config['SECURITY_ADMIN_LOGIN_URL'] = '/admin/login'
    app.config['SECURITY_CLIENT_LOGIN_URL'] = '/login'
    migrate = Migrate(app, db)
    db.init_app(app)

    app.register_blueprint(main_blueprint, url_prefix='/')
    app.register_blueprint(auth_blueprint, url_prefix='/')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(admin_auth_blueprint, url_prefix='/admin')

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'homeView.home'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if request.path.startswith('/admin'):
            return redirect(url_for('adminAuth.adminLogin'))
        else:
            return redirect(url_for('homeView.home'))

    return app


def create_database(app):
    if not path.exists('website/' + os.getenv("POSTGRES_DB")):
        with app.app_context():
            db.create_all()
        print('Database created')