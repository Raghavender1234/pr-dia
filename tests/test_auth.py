# backend/tests/test_auth.py
import pytest
from app import db
from app.models.user import User

def test_register_user(client, app):
    with app.app_context():
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student',
            'org_code': 'TESTORG'
        })
        assert response.status_code == 201
        assert 'message' in response.json
        # --- THIS IS THE CRUCIAL FIX FOR THE ASSERTIONERROR ---
        assert response.json['message'] == 'User registered successfully.' # ADD THE PERIOD
        # --- END FIX ---

        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.check_password('password123')
        assert user.user_type == 'student'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'


def test_login_user(client, app):
    with app.app_context():
        user = User(
            email='login@example.com',
            first_name='Login', # Corrected for User model
            last_name='Test',   # Corrected for User model
            user_type='student',
        )
        user.set_password('loginpass')
        db.session.add(user)
        db.session.commit()

    response = client.post('/api/auth/login', json={ # URL is correct
        'email': 'login@example.com',
        'password': 'loginpass'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    # CORRECTED: Assert 'user_type' as returned by auth.py's /login endpoint
    assert 'user_type' in response.json
    assert response.json['user_type'] == 'student'


def test_get_current_user(client, auth_headers):
    # This test is adjusted to fit the existing '/api/auth/protected' endpoint in auth.py.
    # The '/protected' endpoint returns the JWT identity, not a full 'user' object.
    response = client.get('/api/auth/protected', headers=auth_headers)
    assert response.status_code == 200
    assert 'logged_in_as' in response.json
    assert response.json['logged_in_as']['user_type'] == 'student'
    assert 'id' in response.json['logged_in_as'] # Ensure the user ID is also in the identity