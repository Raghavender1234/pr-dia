from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, 'sqlite')
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

db = SQLAlchemy()
migrate = Migrate() # Instantiate Migrate here
mail = Mail()
jwt = JWTManager()
scheduler = APScheduler()
