# app/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, g, render_template, session, current_app, redirect, url_for, abort
from flask_cors import CORS
from .config import Config
from .extensions import db, mail, jwt, migrate, scheduler
from datetime import datetime
from flask_session import Session

# add these imports (if not already present)
from .models import Organization
from .models.user import User
from .models.student_progress import StudentAISubscription
from app.api.ai_progress import ai_progress_bp
from app.api.community import community_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    scheduler.start()
    CORS(app)
    Session(app)

    # --- Configure Logging ---
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/dia_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('DIA App startup')

    with app.app_context():
        from . import models 
        from .api.auth import auth_bp
        from .api.super_admin import super_admin_bp
        from .api.main_co_admin import main_co_admin_bp
        from .api.co_admin import co_admin_bp
        from .api.student import student_api_bp
        from .api.payment import payment_bp
        from .api.ai import ai_bp
        from .api.public import public_api_bp
        from .frontend.routes import frontend_bp
        from .api.class_routes import class_bp
        from .api.notification_routes import notification_bp
            

        app.register_blueprint(auth_bp)
        app.register_blueprint(super_admin_bp)
        app.register_blueprint(main_co_admin_bp)
        app.register_blueprint(co_admin_bp)
        app.register_blueprint(student_api_bp)
        app.register_blueprint(payment_bp)
        app.register_blueprint(ai_bp)
        app.register_blueprint(public_api_bp)
        app.register_blueprint(frontend_bp)
        app.register_blueprint(ai_progress_bp)
        app.register_blueprint(community_bp)
        app.register_blueprint(class_bp)
        app.register_blueprint(notification_bp, strict_slashes=False)

        # --- Request Hooks ---
        @app.before_request
        def before_request_handler():
            """
            Handles subdomain detection and sets up the global user context (g).
            This runs before every single request.
            """
            from .frontend.routes import get_user_context  # Import locally to avoid circular dependency
            
            g.user_context = get_user_context()
            g.current_organization = None

            # Extract host from the request (without port)
            host = request.host.split(':')[0]
            server_name_config = current_app.config.get("SERVER_NAME")

            # If SERVER_NAME is set (e.g., .pr-dia.com), use it, otherwise fall back to request.host
            if server_name_config:
                server_name = server_name_config.split(":")[0]
            else:
                server_name = host

            # Subdomain detection: check if host ends with the server_name
            if host != server_name and host.endswith(server_name):
                subdomain = host[:-len(server_name)].strip('.')
                if subdomain:
                    g.current_organization = Organization.query.filter_by(
                        subdomain=subdomain, status='active'
                    ).first()
                    if not g.current_organization:
                        abort(404)

        @app.context_processor
        def inject_template_globals():
            dashboard_map = {
                "student": "frontend.student_dashboard",
                "main_co_admin": "frontend.main_co_admin_dashboard",
                "co_admin": "frontend.co_admin_dashboard",
                "super_admin": "frontend.super_admin_dashboard",
            }
            user_type = g.get('user_context', {}).get("user_type")
            current_org = g.get("current_organization")
            return {
                "user_context": g.get('user_context', {}),
                "current_organization": current_org,
                "dashboard_url_endpoint": dashboard_map.get(user_type, 'frontend.index'),
                "current_year": datetime.utcnow().year,
                "org_param": {"org": current_org.subdomain} if current_org else {},
            }

        # --- Error handlers ---
        @app.errorhandler(404)
        def not_found_error(error):
            if request.path.startswith('/api/'):
                return jsonify({"message": "Resource not found."}), 404
            return render_template('errors/404.html'), 404

        @app.errorhandler(500)
        def internal_server_error(error):
            db.session.rollback()
            app.logger.exception(f"Internal Server Error (500): {request.url}")
            if request.path.startswith('/api/'):
                return jsonify({"message": "An internal server error occurred."}), 500
            return render_template('errors/500.html'), 500

    from . import commands
    commands.register_commands(app)
    return app
