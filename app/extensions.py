from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate() # Instantiate Migrate here
mail = Mail()
jwt = JWTManager()
scheduler = APScheduler()