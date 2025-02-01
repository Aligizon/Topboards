from flask import Flask, redirect, url_for, request
from flask_migrate import Migrate
from os import path
from flask_login import LoginManager
from .model import db
from .model.models import User
from .view import homeView as main_blueprint
from .view import adminView as admin_blueprint
from .controller import auth as auth_blueprint
from .controller import adminAuth as admin_auth_blueprint
    
from datetime import timedelta

DB_NAME = "database"

def create_app():
    app = Flask(__name__)
    app.secret_key = 'HFIAV3JA8MDCMAW2HKjdakw091JKDA6m'
    app.permanent_session_lifetime = timedelta(days=7)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True

    app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
    app.config["UPLOAD_PATH"] = 'website/static/img/product_images'

    app.config['SECRET_KEY'] = 'f70hjsnjvs83n742n48c94w35jith5slp4qac'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@localhost:5432/{DB_NAME}'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@192.168.56.1:5432/{DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://topboards:my_topboards_16@postgres:5432/{DB_NAME}'
   
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
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Database created')