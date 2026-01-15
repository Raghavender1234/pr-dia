# backend/tests/conftest.py

import pytest
from app import create_app, db
import json
from app.models.organization import Organization, OrganizationMembership 
from app.models.user import User 
from app.models.exam import Exam 
from app.models.mock_test import MockTest, MockTestQuestion 
from app.models.student_progress import StudentTestAttempt, StudentQuestionResponse 

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite for tests       
        "JWT_SECRET_KEY": "test-jwt-secret", # A test secret key for JWT
        "RAZORPAY_KEY_ID": "test_key_id", # Mock Razorpay keys for tests
        "RAZORPAY_KEY_SECRET": "test_key_secret",
        "OPENAI_API_KEY": "test_openai_key" # Mock OpenAI key
    })

    with app.app_context():
        db.create_all() # Create tables for the in-memory database

        # Create a default test organization once per session
        test_org = Organization.query.filter_by(name='TestOrganization').first()
        if not test_org:
            test_org = Organization(name='TestOrganization', org_code='TESTORG') 
            db.session.add(test_org)
            db.session.commit()
            
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def auth(client):
    """A helper fixture for authentication."""
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def register(self, email, password, full_name, user_type='student', organization_id=None, org_code=None):
            data = {
                'email': email,
                'password': password,
                'full_name': full_name, # This `full_name` is for the API, not direct model creation
                'user_type': user_type
            }
            if organization_id:
                data['organization_id'] = organization_id
            if org_code:
                data['org_code'] = org_code
            return self._client.post('/auth/register', json=data)

        def login(self, email, password):
            return self._client.post(
                '/auth/login', json={'email': email, 'password': password}
            )

        def logout(self):
            return self._client.post('/auth/logout')

    return AuthActions(client)

@pytest.fixture(scope='function')
def test_organization(app):
    """Provides the default test organization."""
    with app.app_context():
        return Organization.query.filter_by(name='TestOrganization').first()

@pytest.fixture(scope='function')
def admin_user(app, test_organization):
    """Creates an admin user for tests."""
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        if not admin:
            admin = User(
                email='admin@test.com',
                first_name='Test',
                last_name='Admin',
                user_type='super_admin',
                organization_id=test_organization.id
            )
            # --- THIS IS THE CRUCIAL FIX FOR THE TYPEERROR ---
            admin.set_password('adminpass') # Call set_password on the instance
            # --- END FIX ---
            db.session.add(admin)
            db.session.commit()
            if admin.user_type in ['main_co_admin', 'co_admin']:
                membership = OrganizationMembership(user_id=admin.id, organization_id=test_organization.id)
                db.session.add(membership)
                db.session.commit()
        return admin

@pytest.fixture(scope='function')
def student_user(app, test_organization):
    """Creates a student user for tests."""
    with app.app_context():
        student = User.query.filter_by(email='student@test.com').first()
        if not student:
            student = User(
                email='student@test.com',
                first_name='Test',
                last_name='Student',
                user_type='student',
                organization_id=test_organization.id
            )
            # --- THIS IS THE CRUCIAL FIX FOR THE TYPEERROR ---
            student.set_password('studentpass') # Call set_password on the instance
            # --- END FIX ---
            db.session.add(student)
            db.session.commit()
            membership = OrganizationMembership(user_id=student.id, organization_id=test_organization.id)
            db.session.add(membership)
            db.session.commit()
        return student
    
@pytest.fixture(scope='function')
def auth_headers(client, student_user):
    """
    Logs in the student_user and returns authentication headers with JWT token.
    """
    login_data = {
        'email': student_user.email,
        'password': 'studentpass'
    }
    # IMPORTANT: Update this URL to '/api/auth/login' as well
    response = client.post('/api/auth/login', json=login_data) # <-- Corrected URL
    
    assert response.status_code == 200, f"Auth headers fixture login failed: {response.json}"
    assert 'access_token' in response.json

    access_token = response.json['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    return headers


# You might need to add more fixtures for exams, mock tests, questions, etc., as your tests grow.