from flask import Flask
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_manager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_migrate import Migrate

migrate = Migrate()

db = SQLAlchemy()

load_dotenv()
SECRET_KEY = os.environ.get("KEY")
DB_NAME = os.environ.get("DB_NAME")

def create_database():
        db.create_all()
        print("OK!")

def create_app():
    app = Flask(__name__)
    app.secret_key = "my_secret_key_12345!@#%^&*"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Hyong:TheHieuDoan@Hyong.mysql.pythonanywhere-services.com/Hyong$fsmdb"
    db.init_app(app)
    migrate.init_app(app, db) 
    from management.user import user
    from management.views import views
    from .models import User

    with app.app_context():
        create_database()

    app.register_blueprint(user)
    app.register_blueprint(views)

    login_manager = LoginManager()
    login_manager.login_view = "user.login"
    login_manager.init_app(app)
    app.permanent_session_lifetime = timedelta(minutes= 1)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
