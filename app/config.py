import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env')) # Looks for .env in the backend folder

class Config:
    """Base configuration settings."""

    # --- Core Flask Settings ---
    # A strong, random secret key is critical for security (sessions, signing, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # --- Database (SQLAlchemy) ---
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT (Flask-JWT-Extended) ---
    # It's good practice to use a separate secret for JWTs
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '24')))

    SERVER_NAME = os.getenv("SERVER_NAME", None)

    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'https'

    # --- Session Cookie Settings ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
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
    # Used for creating links in emails (e.g., password reset)
    FRONTEND_URL = os.getenv('FRONTEND_URL')

    # --- AWS S3 Configuration ---
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION')
    S3_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    S3_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')

    # --- File Upload Limits ---
    # Max size for image/pdf uploads (e.g., 20MB)
    MAX_IMAGE_PDF_UPLOAD_SIZE = 20 * 1024 * 1024
    # Max size for video uploads (e.g., 500MB)
    MAX_VIDEO_UPLOAD_SIZE = 500 * 1024 * 1024

    # --- Razorpay Plan Mapping ---
    # Maps frontend plan identifiers to actual Razorpay Plan IDs
    RAZORPAY_PLANS = {
        '13': 'plan_RRQUYFdyhs7kEW', # Basic 1999 Plan
        '14': 'plan_RRQaOQ8HM4krXH', # Pro 4999 Plan
        '15': 'plan_RRQgEpIkuHHijr', # Premium 9999 Plan
        # Add other plans here as you create them
    }

    # --- AI Subscription Plan IDs ---
    AI_ASSISTANT_PLAN_ID = os.getenv('AI_ASSISTANT_PLAN_ID', 'plan_RRe2VVk0INlo0p')
    AI_TUTOR_PLAN_ID = os.getenv('AI_TUTOR_PLAN_ID', 'plan_RRe1LwkOmKn6Y7')
