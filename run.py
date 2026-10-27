import os
import sys
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

from app import create_app, db

app = create_app()

def initialize_database():
    """Ensure database schema is created on startup if missing."""
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[!] Database initialization notice: {e}")

if __name__ == '__main__':
    initialize_database()

    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() in ('1', 'true', 'yes')

    print("=" * 70)
    print("   🚀 OpenLMS - AI-Powered Learning & Assessment Platform")
    print("=" * 70)
    print(f" * Server running on: http://{host}:{port}/")
    print(f" * Student Portal:    http://{host}:{port}/student/dashboard")
    print(f" * Admin Portal:      http://{host}:{port}/admin/dashboard")
    print(f" * Quick Seeding:     Run 'python seed_database.py' for full demo data")
    print("=" * 70)

    app.run(host=host, port=port, debug=debug)
