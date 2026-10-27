import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env')) # Looks for .env in the backend folder

class Config:
    """Base configuration settings."""

    # --- Core Flask Settings ---
    SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') or 'openlms-development-secret-key-change-in-production'
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # --- Database (SQLAlchemy) ---
    default_db_path = os.path.join(basedir, '..', 'app.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or f"sqlite:///{default_db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT (Flask-JWT-Extended) ---
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '24')))

    SERVER_NAME = os.getenv("SERVER_NAME", None)

    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'https' if os.getenv('FLASK_ENV') == 'production' else 'http'

    # --- Session Cookie Settings ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = False
    
    # Set secure cookies in production
    if os.getenv('FLASK_ENV') == 'production':
        SESSION_COOKIE_SECURE = True
        if SERVER_NAME:
            SESSION_COOKIE_DOMAIN = f".{SERVER_NAME}"

    # --- Razorpay API Keys ---
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
    
    # --- OpenAI API Key ---
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    # --- Frontend URL ---
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5000')

    # --- AWS S3 Configuration ---
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION')
    S3_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    S3_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')

    # --- File Upload Limits ---
    MAX_IMAGE_PDF_UPLOAD_SIZE = 20 * 1024 * 1024
    MAX_VIDEO_UPLOAD_SIZE = 500 * 1024 * 1024

    # --- Razorpay Plan Mapping ---
    RAZORPAY_PLANS = {
        '1': os.environ.get('RAZORPAY_PLAN_ID_1'),
        '2': os.environ.get('RAZORPAY_PLAN_ID_2'),
        '3': os.environ.get('RAZORPAY_PLAN_ID_3')
    }

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@openlms.dev')

    # --- AI Subscription Plan IDs ---
    AI_ASSISTANT_PLAN_ID = os.getenv('AI_ASSISTANT_PLAN_ID')
    AI_TUTOR_PLAN_ID = os.getenv('AI_TUTOR_PLAN_ID')
