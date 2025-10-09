from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for, g, flash
from app import db
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership, Plan
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import os
from razorpay import Client as RazorpayClient
from authlib.integrations.flask_client import OAuth
from sqlalchemy import func
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from app import mail
from app.utils.email_utils import send_email 
from .decorators import admin_role_required
import razorpay
# --- Blueprint Setup ---
auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

oauth = OAuth(current_app)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    # FIX: Using the correct server metadata URL for Google
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


# --- Razorpay Client Initialization ---
razorpay_client = RazorpayClient(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

DASHBOARD_ROUTES = {
    'student': 'templates.student_dashboard',
    'main_co_admin': 'templates.main_co_admin_dashboard',
    'co_admin': 'templates.co_admin_dshboard',  # Co-admins land directly on content
    'super_admin': 'frontend.super_admin_dashboard'
}


# --- REGISTRATION ENDPOINTS ---

@auth_bp.route('/register-student', methods=['POST'])
def register_student():
    """
    Handles registration for new student accounts.
    Creates the user with a 'pending_verification' status, sends a verification email,
    and optionally joins them to an organization if a valid code is provided.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    org_code = data.get('organization_code')

    if not all([email, password, first_name, last_name]):
        return jsonify({"message": "All fields are required: email, password, first name, and last name."}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "An account with this email already exists."}), 409

    try:
        # Create the user but mark them as unverified
        new_student = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type='student',
            status='pending_verification' 
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.flush() # Flush to get the new_student.id before creating membership

        org_message = ""
        if org_code:
            organization = Organization.query.filter_by(code=org_code, status='active').first()
            if organization:
                # This logic correctly creates a 'public' membership
                # that does NOT count against the organization's invited student limit.
                membership = OrganizationMembership(
                    user_id=new_student.id,
                    organization_id=organization.id,
                    is_active=True,
                    access_type='public'
                )
                db.session.add(membership)
                org_message = f" You have also been successfully joined to {organization.name}."
            else:
                org_message = " The organization code you entered was not found."

        db.session.commit()

        # Send the verification email after the user is successfully saved
        send_verification_email(new_student.email)
        
        # This new message is clearer about the next step
        final_message = f"Student account created successfully! Please check your email to verify your account.{org_message}"

        return jsonify({"message": final_message}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during student registration: {e}", exc_info=True)
        return jsonify({"message": "An unexpected server error occurred during registration."}), 500

@auth_bp.route('/register-organization', methods=['POST'])
def register_organization():
    data = request.get_json()
    print("✅ RECEIVED REGISTRATION PAYLOAD:", data)

    org_name = data.get('organization_name')
    org_code = data.get('code')
    admin_email = data.get('email')
    password = data.get('password')
    razorpay_plan_id = data.get('plan_id')  # This should now be Razorpay's plan_id

    print(f"  - Org Name: {org_name}")
    print(f"  - Org Code: {org_code}")
    print(f"  - Email: {admin_email}")
    print(f"  - Razorpay Plan ID: {razorpay_plan_id}")

    # Basic validation
    if not all([org_name, org_code, admin_email, password, razorpay_plan_id]):
        print("❌ FAILED at: Missing required fields check.")
        return jsonify({"message": "Missing required fields."}), 400

    if Organization.query.filter_by(code=org_code).first():
        return jsonify({"message": "Organization code is already taken."}), 409

    if User.query.filter_by(email=admin_email).first():
        return jsonify({"message": "An account with this email already exists."}), 409

    try:
        # Create new organization
        new_org = Organization(
            name=org_name,
            code=org_code,
            status='pending_payment'
        )
        db.session.add(new_org)
        db.session.flush()

        # Create admin user
        new_admin = User(
            email=admin_email,
            first_name=org_name,
            last_name="Admin",
            user_type='main_co_admin',
            status='pending_payment'
        )
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.flush()

        # Create organization membership
        membership = OrganizationMembership(
            user_id=new_admin.id,
            organization_id=new_org.id,
            is_active=False,
            access_type='internal'
        )
        db.session.add(membership)

        # ✅ Razorpay Subscription logic
        razorpay_client = razorpay.Client(auth=(
            current_app.config['RAZORPAY_KEY_ID'],
            current_app.config['RAZORPAY_KEY_SECRET']
        ))

        subscription = razorpay_client.subscription.create({
            "plan_id": razorpay_plan_id,
            "total_count": 12,  # Total billing cycles (e.g., 12 months)
            "quantity": 1,
            "notes": {
                "organization_id": new_org.id,
                "user_id": new_admin.id
            }
        })

        # Save subscription ID to org
        new_org.razorpay_subscription_id = subscription['id']
        db.session.commit()

        return jsonify({
            "message": "Organization registered. Proceed to payment.",
            "razorpay_key_id": current_app.config['RAZORPAY_KEY_ID'],
            "subscription_id": subscription['id'],
            "org_name": new_org.name,
            "admin_email": new_admin.email
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during organization registration: {e}", exc_info=True)
        return jsonify({"message": "An unexpected server error occurred."}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    org_subdomain = data.get('org_subdomain')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    user = User.query.filter(func.lower(User.email) == email).first()

    if user and user.check_password(password):
        if user.status != 'active':
            return jsonify({"message": "Your account is not active. Please check your email to verify your account."}), 403
        access_token = create_access_token(identity=str(user.id))
        session.clear()

        session['access_token'] = access_token
        session['user_id'] = str(user.id)
        session['user_type'] = user.user_type
        session['user_name'] = user.first_name
        session['user_email'] = user.email
        user.last_login = datetime.utcnow()

        # ✅ START OF THE FIX: This logic now correctly handles all user types
        organization_id = None
        organization_name = None
        target_org = None

        if org_subdomain:
            target_org = Organization.query.filter_by(subdomain=org_subdomain, status='active').first()

        if user.user_type in ['main_co_admin', 'co_admin']:
            # For admins, find their primary organization
            membership = OrganizationMembership.query.filter_by(user_id=user.id, is_active=True).first()
            if membership and membership.organization:
                organization_id = membership.organization_id
                organization_name = membership.organization.name
        
        elif user.user_type == 'student' and target_org:
            # For students, find their membership specifically for the target organization
            membership = OrganizationMembership.query.filter_by(
                user_id=user.id, 
                organization_id=target_org.id, 
                is_active=True
            ).first()
            if membership:
                organization_id = membership.organization_id
                organization_name = membership.organization.name
        
        session['organization_id'] = organization_id
        session['organization_name'] = organization_name
        # ✅ END OF THE FIX
        
        db.session.commit()

        url_params = {'org': org_subdomain} if org_subdomain and organization_id else {}
        dashboard_endpoint = f"frontend.{user.user_type}_dashboard"
        redirect_url = url_for(dashboard_endpoint, **url_params)
        
        return jsonify({"redirect_url": redirect_url}), 200
    
    return jsonify({"message": "Invalid email or password."}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    session.clear()
    response = jsonify({"message": "Successfully logged out"})
    # FIX: Unset JWT cookies if they are being used
    unset_jwt_cookies(response)
    return response, 200

# Example of a protected route (requires JWT token)
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # You can get identity (user_id) directly
    current_user_id = get_jwt_identity()
    # To get additional claims like user_type:
    claims = get_jwt() # Returns dictionary of all claims
    user_type = claims.get('user_type')
    return jsonify(logged_in_as=current_user_id, user_type=user_type), 200

@auth_bp.route('/password/request-reset', methods=['POST'])
def request_password_reset():
    email = request.get_json().get('email')
    user = User.query.filter_by(email=email).first()

    if user:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='password-reset-salt')
        reset_url = url_for('frontend.password_reset_confirm', token=token, _external=True)

        html_content = f"<h3>Password Reset Request</h3><p>Please click the link to reset your password: <a href='{reset_url}'>Reset Password</a></p>"

        send_email(
            to_email=email,
            subject="Password Reset Request",
            html_content=html_content
        )

    return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200

@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Check token validity (expires in 3600 seconds = 1 hour)
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({"message": "The password reset link has expired."}), 400
    except Exception:
        return jsonify({"message": "Invalid password reset link."}), 400

    user = User.query.filter_by(email=email).first_or_404()
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({"message": "Your password has been updated successfully!"}), 200

@auth_bp.route('/join-organization', methods=['POST'])
@jwt_required()
def join_organization():
    # Get user_id directly from JWT identity
    user_id = get_jwt_identity() # ✅ FIXED: get_jwt_identity() returns the identity itself
    
    data = request.get_json()
    org_code = data.get('organization_code')

    if not org_code:
        return jsonify({"message": "Organization code is required"}), 400

    org = Organization.query.filter_by(code=org_code).first() # Assuming 'code' for Organization model
    if not org:
        return jsonify({"message": "Invalid organization code"}), 404

    # Ensure user isn't already an active member of this organization
    existing_membership = OrganizationMembership.query.filter_by(user_id=user_id, organization_id=org.id, is_active=True).first()
    if existing_membership:
        return jsonify({"message": "Already an active member of this organization"}), 409

    # If they were previously inactive, reactivate. Otherwise, create new.
    membership = OrganizationMembership.query.filter_by(user_id=user_id, organization_id=org.id).first()
    if membership:
        membership.is_active = True
        message = "Successfully reactivated membership for organization"
    else:
        membership = OrganizationMembership(user_id=user_id, organization_id=org.id, is_active=True)
        db.session.add(membership)
        message = "Successfully joined organization"

    # Increment student count if the joining user is a student
    user = User.query.get(user_id)
    if user and user.user_type == 'student':
        org.current_student_count += 1

    db.session.commit()
    return jsonify({"message": f"{message}: {org.name}"}), 200

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if request.method == 'GET':
        return jsonify({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }), 200

    if request.method == 'PUT':
        data = request.get_json()
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        db.session.commit()
        # Update the name in the session as well
        session['user_name'] = user.first_name
        return jsonify({"message": "Profile updated successfully"}), 200

# CHANGE USER'S OWN PASSWORD
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"message": "Current and new passwords are required"}), 400

    if not user.check_password(current_password):
        return jsonify({"message": "Current password is incorrect"}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password changed successfully"}), 200

@auth_bp.route('/login/google')
def google_login():
    """Redirects the user to Google's authentication page."""
    
    # ✅ THE FIX: Build the redirect URI using the main domain from your config
    # This ensures Google always sends the user back to the same, approved address.
    main_domain_callback = f"https://{current_app.config['SERVER_NAME']}/api/auth/google/callback"
    
    # ✅ Store the user's current subdomain in the session so we can return them later.
    if g.current_organization:
        session['oauth_subdomain'] = g.current_organization.subdomain
    else:
        session.pop('oauth_subdomain', None) # Clear it if they are on the main site

    return oauth.google.authorize_redirect(main_domain_callback)


@auth_bp.route('/google/callback')
def google_callback():
    """Handles the callback from Google, logs in or creates the user."""
    try:
        # Get user information from Google
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token)

        # Find or create the user in your database
        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            # If the user doesn't exist, create a new student account
            user = User(
                email=user_info['email'],
                first_name=user_info.get('given_name', 'New'),
                last_name=user_info.get('family_name', 'User'),
                user_type='student', # Default new users to students
                status='active'
                # No password is set, as they use Google to log in
            )
            db.session.add(user)
            db.session.commit()

        # Log the user in by creating a session
        access_token = create_access_token(identity=str(user.id))
        session.clear()
        session['access_token'] = access_token
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        session['user_name'] = user.first_name
        
        # Redirect to the appropriate dashboard
        subdomain = session.pop('oauth_subdomain', None) # Get and remove from session
        org_param = {'org': subdomain} if subdomain else {}
        
        dashboard_url = url_for(f'frontend.{user.user_type}_dashboard', **org_param)
        
        return redirect(dashboard_url)
    except Exception as e:
        current_app.logger.error(f"Google OAuth Error: {e}")
        flash("An error occurred during Google authentication. Please try again.", "danger")
        return redirect(url_for('frontend.login'))
    
def send_verification_email(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(email, salt='email-verification-salt')
    verify_url = url_for('auth_api.verify_email', token=token, _external=True)

    html_content = f"<p>Welcome! Please click the link below to verify your email address and activate your account:</p><p><a href='{verify_url}'>Verify Your Email</a></p><p>This link will expire in 24 hours.</p>"

    send_email(
        to_email=email,
        subject="Confirm Your Email for DIA App",
        html_content=html_content
    )


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Check token validity (expires in 1 day)
        email = s.loads(token, salt='email-verification-salt', max_age=86400)
    except (SignatureExpired, BadTimeSignature):
        # You can create a simple HTML page for this
        return "<h1>The verification link is invalid or has expired.</h1>"

    user = User.query.filter_by(email=email).first_or_404()
    
    if user.status == 'active':
        flash('Your account is already active. Please log in.', 'info')
    else:
        user.status = 'active'
        db.session.commit()
        flash('Your account has been successfully verified! You can now log in.', 'success')

    return redirect(url_for('frontend.login'))

@auth_bp.route('/toggle-availability', methods=['POST'])
@jwt_required()
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def toggle_availability(current_user, **kwargs):
    """Toggles the admin's availability status between 'available' and 'busy'."""
    if current_user.availability_status == 'available':
        current_user.availability_status = 'busy'
    else:
        current_user.availability_status = 'available'
    db.session.commit()
    return jsonify({'message': f'Your status has been updated to {current_user.availability_status}', 'new_status': current_user.availability_status}), 200