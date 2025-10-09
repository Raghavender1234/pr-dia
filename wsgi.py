from app import create_app, db
from flask_migrate import Migrate
import os
import click
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Make sure to import all the models you need for seeding
from app.models import Plan, Organization, User, OrganizationMembership

app = create_app()
migrate = Migrate(app, db)

# Your shell context can remain the same
@app.shell_context_processor
def make_shell_context():
    # ... your existing context code ...
    return {
        'db': db,
        'User': User,
        'Organization': Organization,
        'Plan': Plan,
        'OrganizationMembership': OrganizationMembership
    }

# --- UPDATED AND EXPANDED SEED COMMAND ---
@app.cli.command("seed")
def seed():
    """Seeds the database with plans, a super admin, and a test organization."""
    print("--- Starting database seeding ---")

    # Clear old data
    db.session.query(OrganizationMembership).delete()
    db.session.query(Organization).delete()
    db.session.query(User).delete()
    db.session.query(Plan).delete()

    # 1. Seed Plans
    print("Seeding plans...")
    # ... (plan creation logic remains the same) ...
    plans_data = [
        {'name': 'Basic', 'monthly_price': 1999.00, 'max_coadmins': 2, 'max_invited_students': 20, 'is_publicly_available': True, 'description': "For small teams."},
        {'name': 'Standard', 'monthly_price': 4999.00, 'max_coadmins': 5, 'max_invited_students': 50, 'is_publicly_available': True, 'description': "For growing institutions."},
        {'name': 'Premium', 'monthly_price': 9999.00, 'max_coadmins': 10, 'max_invited_students': 100, 'is_publicly_available': True, 'description': "For large-scale use."}
    ]
    for plan_data in plans_data:
        plan = Plan(**plan_data)
        db.session.add(plan)
    db.session.commit()

    # 2. Seed Super Admin
    print("Seeding Super Admin...")
    super_admin_password = os.getenv('SUPER_ADMIN_PASSWORD')
    if not super_admin_password:
        raise ValueError("SUPER_ADMIN_PASSWORD environment variable not set.")
    super_admin = User(
        email='superadmin@dia.com',
        password_hash=generate_password_hash(super_admin_password, method='pbkdf2:sha256'),
        first_name='Super',
        last_name='Admin',
        user_type='super_admin',
        status='active'
    )
    db.session.add(super_admin)
    db.session.commit()

    # 3. Seed Test Organization and Users
    print("Seeding Test Organization: Test University Alpha...")
    # ... (organization creation logic remains the same) ...
    test_org = Organization(
        name='Test University Alpha',
        code='TESTORG001',
        plan_id=Plan.query.filter_by(name='Standard').first().id,
        status='active',
        is_verified=True
    )
    db.session.add(test_org)
    db.session.commit()


    print("Seeding users for Test University Alpha...")
    users_to_create = [
        {'email': 'main_co_admin@testorg.com', 'password_env': 'MAIN_CO_ADMIN_PASSWORD', 'type': 'main_co_admin', 'first': 'Principal', 'last': 'Admin'},
        {'email': 'co_admin@testorg.com', 'password_env': 'CO_ADMIN_PASSWORD', 'type': 'co_admin', 'first': 'Teacher', 'last': 'Admin'},
        {'email': 'student1@testorg.com', 'password_env': 'STUDENT1_PASSWORD', 'type': 'student', 'first': 'Test', 'last': 'StudentOne'},
        {'email': 'student2@testorg.com', 'password_env': 'STUDENT2_PASSWORD', 'type': 'student', 'first': 'Test', 'last': 'StudentTwo'}
    ]

    for user_data in users_to_create:
        password = os.getenv(user_data['password_env'])
        if not password:
            raise ValueError(f"{user_data['password_env']} environment variable not set.")
        new_user = User(
            email=user_data['email'],
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            first_name=user_data['first'],
            last_name=user_data['last'],
            user_type=user_data['type'],
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()

        membership = OrganizationMembership(
            user_id=new_user.id,
            organization_id=test_org.id,
            access_type=user_data['type']
        )
        db.session.add(membership)

    db.session.commit()
    print("--- Seeding complete! ---")


# --- PRODUCTION INITIALIZATION COMMAND ---
@app.cli.command("init-prod")
def init_prod():
    """Initializes the production database with essential data (plans and super admin) without deleting existing data."""
    print("--- Starting production initialization ---")

    # 1. Seed Plans (Idempotent)
    print("Checking and seeding plans...")
    plans_data = [
        {'name': 'Basic', 'monthly_price': 1999.00, 'max_coadmins': 2, 'max_invited_students': 20, 'is_publicly_available': True, 'description': "For small teams."},
        {'name': 'Standard', 'monthly_price': 4999.00, 'max_coadmins': 5, 'max_invited_students': 50, 'is_publicly_available': True, 'description': "For growing institutions."},
        {'name': 'Premium', 'monthly_price': 9999.00, 'max_coadmins': 10, 'max_invited_students': 100, 'is_publicly_available': True, 'description': "For large-scale use."}
    ]

    for plan_data in plans_data:
        existing_plan = Plan.query.filter_by(name=plan_data['name']).first()
        if not existing_plan:
            print(f"Creating plan: {plan_data['name']}")
            plan = Plan(**plan_data)
            db.session.add(plan)
        else:
            print(f"Plan already exists: {plan_data['name']}")

    # 2. Seed Super Admin (Idempotent)
    print("Checking and seeding super admin...")
    super_admin_email = 'brreddy16@gmail.com'
    existing_super_admin = User.query.filter_by(email=super_admin_email).first()

    if not existing_super_admin:
        print(f"Creating super admin: {super_admin_email}")
        super_admin_password = os.getenv('SUPER_ADMIN_PASSWORD')
        if not super_admin_password:
            raise ValueError("SUPER_ADMIN_PASSWORD environment variable not set. Cannot create super admin.")
        
        super_admin = User(
            email=super_admin_email,
            password_hash=generate_password_hash(super_admin_password, method='pbkdf2:sha256'),
            first_name='Super',
            last_name='Admin',
            user_type='super_admin',
            status='active'
        )
        db.session.add(super_admin)
    else:
        print(f"Super admin already exists: {super_admin_email}")

    db.session.commit()
    print("--- Production initialization complete! ---")


if __name__ == '__main__':
    # For local development, use 'flask run' after setting FLASK_APP and FLASK_DEBUG.
    # Example:
    # export FLASK_APP=wsgi.py
    # export FLASK_DEBUG=1
    # flask run
    # The app is run by Gunicorn in production (see Dockerfile).
    app.run()