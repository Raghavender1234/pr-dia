# backend/app/frontend/routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, g, jsonify, abort
from flask_login import login_required, current_user
from flask_jwt_extended import decode_token, get_jwt_identity, jwt_required
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime
from app.forms import UserRegistrationForm, OrgRegistrationForm, LoginForm, ExamForm, SubjectForm, TopicContentForm # Import the forms you need
from app.models.organization import Organization, OrganizationMembership # Ensure Organization is imported if used in forms.py validators
from flask_wtf import FlaskForm
from app.models.subject import Subject  # <<< ADD THIS LINE to import the Subject model
from app.models.topic import Topic    # <<< ADD THIS LINE if you also fetch Topics here (likely for this page)
from app.models.exam import Exam    # <<< ADD
from app.models.mock_test import MockTest
from app.models.user import User
from app.api.student import generate_advanced_study_plan
from app.models.student_progress import StudentTestAttempt, StudentAISubscription
from app.api.main_co_admin import DEFAULT_FAQ_TEMPLATE, DEFAULT_CONTACT_TEMPLATE
from app.models.student_progress import StudentAISubscription, StudentExam
from app.api.decorators import premium_feature_required, super_admin_required, student_required, admin_role_required
import json
from app.models.community import ForumPost, ForumReply
from app.models.class_management import Class, ClassParticipant

frontend_bp = Blueprint('frontend', __name__)

# --- Helper function for user context in templates ---
def get_user_context():
    user_context = {
        'is_logged_in': False, 'user_type': None, 'user_name': None,
        'access_token': None, 'organization_name': None, 'organization_id': None,
        'dashboard_url': url_for('frontend.index'),
        'is_premium': False, 'org_status': None
    }

    access_token = session.get('access_token')
    session_user_id = session.get('user_id')

    if access_token and session_user_id:
        try:
            decode_token(access_token)

            user_context['access_token'] = access_token
            user_context['is_logged_in'] = True
            user_context['user_type'] = session.get('user_type')
            user_context['user_id'] = session_user_id
            user_context['user_name'] = session.get('user_name')
            user_context['user_email'] = session.get('user_email')

            now = datetime.utcnow()
            is_premium = False
            user_type = user_context['user_type']

            if user_type == 'student':
                sub = StudentAISubscription.query.filter_by(
                    student_user_id=session_user_id, status='active'
                ).first()
                is_premium = bool(sub and (sub.end_date is None or sub.end_date >= now))
            
            elif user_type in ['main_co_admin', 'co_admin']:
                # For admins, check their organization's premium status
                membership = OrganizationMembership.query.filter_by(user_id=session_user_id).first()
                if membership and membership.organization:
                    is_premium = membership.organization.is_ai_premium
            
            elif user_type == 'super_admin':
                is_premium = True # Super admin always has premium access

            user_context['is_premium'] = is_premium
            session['is_premium'] = is_premium # Keep the session in sync

            # organization context (unchanged) ...
            org_id = session.get('organization_id')
            if org_id:
                organization = Organization.query.get(org_id)
                if organization:
                    user_context['organization_id'] = organization.id
                    user_context['organization_name'] = organization.name
                    user_context['org_status'] = organization.status

            user_type = user_context['user_type']
            if user_type:
                user_context['dashboard_url'] = f'frontend.{user_type}_dashboard'

        except (ExpiredSignatureError, InvalidTokenError):
            session.clear()
            return user_context

    return user_context

@frontend_bp.before_request
def load_user_context_to_g():
    g.user_context = get_user_context()

# --- Public Routes ---
@frontend_bp.route('/')
def index():
    """
    Renders the main index page.
    This is now "subdomain-aware" and will pass the organization
    object to the template if the user is on a subdomain.
    """
    # g.current_organization is set by the 'before_request' handler we created
    return render_template('index.html', organization=g.current_organization)

@frontend_bp.route('/login')
def login():
    # If the user is already logged in, redirect them away.
    if g.user_context.get('is_logged_in'):
        # This uses the subdomain-aware URL we fixed before.
        return redirect(url_for(g.user_context['dashboard_url'], org=g.current_organization.subdomain if g.current_organization else None))
    
    # --- THIS IS THE FIX ---
    # This now passes the detected organization to the login template.
    return render_template('auth/login.html', organization=g.current_organization)

@frontend_bp.route('/register')
def register():
    if g.user_context['is_logged_in']: return redirect(g.user_context['dashboard_url'] or url_for('frontend.index'))
    return render_template('public/register.html')

@frontend_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info') 
    return redirect(url_for('frontend.login'))

# --- Dashboard Routes ---
@frontend_bp.route('/student/dashboard')
def student_dashboard():
    # Basic check to ensure a student is logged in
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        return redirect(url_for('frontend.login'))

    # Γ£à THE FIX: Check if we are on a subdomain.
    if g.current_organization:
        # If g.current_organization exists, it means we are on a subdomain.
        # Render the specific, branded dashboard for that organization.
        return render_template(
            'student/organization_dashboard.html', 
            organization=g.current_organization
        )
    else:
        # If g.current_organization is None, we are on the main global site.
        # Render the default, global dashboard.
        return render_template('dashboards/student_dashboard.html')

@frontend_bp.route('/main-co-admin/dashboard')
def main_co_admin_dashboard():
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'main_co_admin':
        return redirect(url_for('frontend.login'))
    return render_template('dashboards/main_co_admin_dashboard.html')

@frontend_bp.route('/co-admin/dashboard')
def co_admin_dashboard():
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'co_admin':
        return redirect(url_for('frontend.login'))
    return render_template('dashboards/co_admin_dashboard.html')

@frontend_bp.route('/super-admin/dashboard')
def super_admin_dashboard():
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'super_admin':
        return redirect(url_for('frontend.login'))
    return render_template('dashboards/super_admin_dashboard.html')

# --- Student Content Routes ---

@frontend_bp.route('/student/exams/<int:exam_id>/subjects')
def student_subject_browse(exam_id):
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        return redirect(url_for('frontend.login'))
    exam = Exam.query.get_or_404(exam_id)
    return render_template('student/subject_browse.html', exam=exam)

@frontend_bp.route('/student/topics/<int:subject_id>')
def student_topic_browse(subject_id):
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        return redirect(url_for('frontend.login'))
    subject = Subject.query.get_or_404(subject_id)
    return render_template('student/topic_browse.html', subject=subject)

@frontend_bp.route('/student/topics/<int:topic_id>/content')
def student_topic_content(topic_id):
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        return redirect(url_for('frontend.login'))
    topic = Topic.query.get_or_404(topic_id)
    return render_template('student/view_topic_content.html', topic=topic)

# --- AI Feature Routes ---
@frontend_bp.route('/learn-with-ai', endpoint='student_learn_with_ai')
def learn_with_ai():
    if not g.user_context.get('is_logged_in'):
        flash("Please log in to access this feature.", "warning")
        return redirect(url_for('frontend.login'))

    user_type = g.user_context.get('user_type')
    is_premium = g.user_context.get('is_premium')

    if user_type == 'student':
        # Template itself shows premium vs upsell view
        return render_template('student/learn_with_ai.html')

    if user_type in ['main_co_admin', 'co_admin', 'super_admin']:
        if is_premium:
            return render_template('admin/ai_assistant.html')
        return render_template('admin/ai_assistant_upsell.html')

    return redirect(g.user_context.get('dashboard_url') or url_for('frontend.index'))

@frontend_bp.route('/student/ai-chat', endpoint='student_ai_chat')
def ai_chat():
    # Must be logged in
    if not g.user_context.get('is_logged_in'):
        flash("Please log in to access this feature.", "warning")
        return redirect(url_for('frontend.login'))

    # Must be premium
    if not g.user_context.get('is_premium'):
        flash("A premium subscription is required to use the AI Tutor.", "warning")
        return redirect(url_for('frontend.student_learn_with_ai'))

    exam_id = request.args.get('exam_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    topic_id = request.args.get('topic_id', type=int)

    if not exam_id or not subject_id:
        flash("You must select an exam and a subject.", "warning")
        return redirect(url_for('frontend.student_learn_with_ai'))

    # Load models (adjust imports to your layout)

    exam = Exam.query.get_or_404(exam_id)

    # Ensure the subject belongs to this exam
    subject = Subject.query.filter_by(id=subject_id, exam_id=exam_id).first_or_404()

    # (Optional, but recommended) If user is a student, ensure they are enrolled in this exam
    if g.user_context.get('user_type') == 'student':
        student_id = g.user_context.get('user_id')  # adjust if your g.user_context uses a different key
        if student_id:
            enrolled = StudentExam.query.filter_by(student_user_id=student_id, exam_id=exam_id).first()
            if not enrolled:
                flash("You donΓÇÖt have access to this exam.", "warning")
                return redirect(url_for('frontend.student_learn_with_ai'))

    return render_template('student/ai_chat.html', exam=exam, subject=subject, topic_id=topic_id)

# --- Helper Route for Frontend JS ---
@frontend_bp.route('/get-jwt-for-client')
def get_jwt_for_client():
    token = session.get('access_token')
    if token:
        try:
            decode_token(token)
            return jsonify(access_token=token), 200
        except (ExpiredSignatureError, InvalidTokenError):
            session.clear()
    return jsonify({"message": "No active session token"}), 401


# NEW: AJAX Endpoint to trigger backend JWT logout (to handle POST and JWT_REQUIRED)
@frontend_bp.route('/perform_logout_api', methods=['POST'])
@jwt_required() 
def perform_logout_api():
    session.clear()
    return jsonify({"message": "Successfully logged out via AJAX proxy"}), 200

# --- Organization Registration Route (for Main Co-Admin creating NEW Org) ---
@frontend_bp.route('/organization/register', methods=['GET', 'POST'])
def org_register():
    if g.user_context['is_logged_in']:
        return redirect(g.user_context['dashboard_url'] or url_for('frontend.index'))
    
    form = OrgRegistrationForm() # Use the new form
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # This path is for direct HTML POST, not our AJAX.
            flash('Organization registration initiated. Please complete payment.', 'success')
            return redirect(url_for('frontend.login')) # Or to a payment confirmation page
        else:
            flash('Please correct the errors in the form.', 'danger')

    razorpay_key_id = current_app.config.get('RAZORPAY_KEY_ID', 'YOUR_RAZORPAY_KEY_ID_NOT_SET') # For Razorpay JS
    return render_template('auth/org_register.html', form=form, razorpay_key_id=razorpay_key_id, **g.user_context)

@frontend_bp.route('/super-admin/organization/<int:org_id>/details')
@jwt_required(optional=True) # Ensures g.user_context is always populated
def org_details_management(org_id):
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'super_admin':
        flash('Access denied. Super Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))
    
    # Γ£à FIX 1: Fetch the full Organization object from the database using the ID
    org = Organization.query.get_or_404(org_id)
    
    # Γ£à FIX 2: Pass the complete 'org' object to the template
    return render_template('super_admin/org_details_management.html', org=org, **g.user_context)

@frontend_bp.route('/password/request')
def password_request():
    """Renders the page where a user can request a password reset link."""
    # This route just shows the HTML form.
    return render_template('auth/password_request.html')


@frontend_bp.route('/password/reset/<token>')
def password_reset_confirm(token):
    """Renders the page where a user enters their new password."""
    return render_template('auth/password_reset_confirm.html', token=token)

# --- Student Profile & Navigation Routes ---
@frontend_bp.route('/student/profile')
def student_profile(): # Removed jwt_required here as get_user_context already handles token check
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'student':
        flash('Access denied. Please log in as a student to view your profile.', 'danger')
        return redirect(url_for('frontend.login'))
    return render_template('student/profile.html', **g.user_context) 

@frontend_bp.route('/student/organizations')
def student_organizations():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'student':
        flash('Access denied. Please log in as a student.', 'danger')
        return redirect(url_for('frontend.login'))
    return render_template('student/organizations.html', **g.user_context) # NEW TEMPLATE PATH


@frontend_bp.route('/student/transactions')
def student_transactions():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'student':
        flash('Access denied. Please log in as a student.', 'danger')
        return redirect(url_for('frontend.login'))
    return render_template('student/transactions.html', **g.user_context) # NEW TEMPLATE PATH

@frontend_bp.route('/student/questions/<int:topic_id>')
@jwt_required(optional=True)
def student_question_practice(topic_id):
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash('Please log in as a student to practice questions.', 'warning')
        return redirect(url_for('frontend.login'))
    
    topic = Topic.query.get_or_404(topic_id)
    
    # Render the page shell. JavaScript will fetch the questions.
    return render_template('student/practice_question.html', topic=topic, **g.user_context)

@frontend_bp.route('/student/mock-tests')
def student_mock_test_browse():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'student':
        flash('Access denied. Please log in as a student.', 'danger')
        return redirect(url_for('frontend.login'))
    return render_template('student/mock_test_browse.html', **g.user_context)

@frontend_bp.route('/student/mock-test/take/<int:attempt_id>')
@jwt_required(optional=True)
def student_take_mock_test(attempt_id):
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash('Please log in to take a mock test.', 'warning')
        return redirect(url_for('frontend.login'))
    
    # We pass the attempt_id to the template so the JavaScript knows which test to load
    return render_template('student/take_mock_test.html', attempt_id=attempt_id, **g.user_context)

# --- Admin Management Routes (Shared by Main Co-Admin & Co-Admin) ---
@frontend_bp.route('/admin/exams/<int:exam_id>/subjects')
def subject_management(exam_id):
    # Step 1: Check if the user is an admin type and is logged in.
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))

    # Step 2: Get the exam from the database.
    exam = Exam.query.get_or_404(exam_id)

    # Step 3: This authorization check now works because the login fix provides the correct organization_id.
    # It ensures the admin is not trying to access an exam from another organization.
    if g.user_context.get('user_type') != 'super_admin':
        if exam.organization_id != g.user_context.get('organization_id'):
            flash('Unauthorized to manage this exam.', 'danger')
            return redirect(url_for('frontend.exam_management'))

    # Step 4: If all checks pass, render the page.
    form = SubjectForm()
    return render_template(
        'admin/subject_management.html',
        exam=exam,  # Pass the full exam object to the template
        form=form,
        **g.user_context
    )

@frontend_bp.route('/admin/mock-tests')
def mock_test_management():
    user_type = g.user_context.get('user_type')
    if user_type not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))

    # If user is a Main Co-Admin or Super Admin, show the full-featured page
    if user_type in ['main_co_admin', 'super_admin', 'co_admin']:
        return render_template('admin/mock_test_management.html', **g.user_context)

# --- Main Co-Admin Specific Routes ---
@frontend_bp.route('/main-co-admin/users')
def org_users_management():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'main_co_admin':
        flash('Access denied. Main Co-Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))
    return render_template('admin/org_users_management.html', **g.user_context)

# --- Super Admin Specific Routes ---

@frontend_bp.route('/super-admin/organizations-users') # Route for the combined page
def org_user_global_management():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'super_admin':
        flash('Access denied. Super Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))
    
    # We need to pass a form for adding new organizations/users if done from this page
    # For now, we'll do AJAX for everything, so forms are just rendered from templates.
    
    return render_template('super_admin/org_user_global_management.html', **g.user_context) # Render this template

@frontend_bp.route('/super-admin/plans')
def plan_management():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] != 'super_admin':
        flash('Access denied. Super Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))
    return render_template('super_admin/plan_management.html', **g.user_context)

@frontend_bp.route('/admin/exams')
def exam_management():
    user_type = g.user_context.get('user_type')
    if user_type == 'main_co_admin':
        return render_template('admin/exam_management.html', **g.user_context) # The full-featured page
    elif user_type == 'co_admin':
        return render_template('admin/exam_management_read.html', **g.user_context) # The new read-only page
    else:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('frontend.index'))

# --- Co-Admin Content Management Routes ---
@frontend_bp.route('/admin/content/select-exam') # NEW ROUTE for selecting exam before managing content
def select_exam_for_content():
    if not g.user_context['is_logged_in'] or g.user_context['user_type'] not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))
    # No form needed, as this page just lists and links
    return render_template('admin/select_exam_for_content.html', **g.user_context)

# NEW: Endpoint to securely retrieve JWT from session for client-side JS
@frontend_bp.route('/get-jwt-token', methods=['GET'])
def get_jwt_token_for_js():
    access_token = session.get('access_token')
    if access_token:
        try:
            # Optionally decode to verify it's still valid (though jwt_required handles this later)
            decoded = decode_token(access_token) 
            return jsonify({"access_token": access_token}), 200
        except (ExpiredSignatureError, InvalidTokenError) as e:
            current_app.logger.warning(f"Expired or invalid token when requested by JS: {e}")
            session.clear() # Clear session if token is bad
            return jsonify({"message": "Token expired or invalid"}), 401
    return jsonify({"message": "No active session token"}), 401

@frontend_bp.route('/admin/subjects/<int:subject_id>/topics')
#@jwt_required() # Or your specific admin role decorator
def topic_management(subject_id):
    if not g.user_context.get('is_logged_in') or \
       g.user_context.get('user_type') not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))

    subject = Subject.query.get_or_404(subject_id)
    # Ensure admin has access to this subject's organization
    if g.user_context.get('user_type') != 'super_admin' and \
       subject.exam.organization_id != g.user_context.get('organization_id'):
        flash('Unauthorized to manage topics for this subject.', 'danger')
        return redirect(url_for('frontend.exam_management')) # Or appropriate redirect

    # Pass an empty form for CSRF token, if your base.html or this form uses it
    from app.forms import ExamForm # Or a generic CSRF form if you have one
    csrf_form = ExamForm() 

    return render_template(
        'admin/topic_management.html', 
        subject_id=subject_id, 
        subject=subject, # Pass the whole subject object for breadcrumbs etc.
        form=csrf_form, # For CSRF token
        **g.user_context
    )


@frontend_bp.route('/admin/topics/<int:topic_id>/content-editor')
# @jwt_required() # Recommended to remove if using g.user_context for frontend pages
def topic_content_editor(topic_id):
    # Access control based on user role
    if not g.user_context.get('is_logged_in') or \
       g.user_context.get('user_type') not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))

    topic = Topic.query.get_or_404(topic_id)
    
    # Authorization: Ensure admin belongs to the organization of the topic's exam
    if g.user_context.get('user_type') != 'super_admin':
        if not topic.subject or not topic.subject.exam or \
           topic.subject.exam.organization_id != g.user_context.get('organization_id'):
            flash('You are not authorized to manage content for this topic.', 'danger')
            # Redirect to a sensible page, e.g., the topic management for the parent subject
            return redirect(url_for('frontend.topic_management', subject_id=topic.subject_id if topic.subject else 0))

    form = TopicContentForm() # Instantiate the form to pass to the template (e.g., for CSRF if needed by JS, or select choices)

    return render_template(
        'admin/topic_content_editor.html',
        topic=topic, # Pass the full topic object
        subject_name=topic.subject.name if topic.subject else 'Unknown Subject',
        parent_subject_id=topic.subject_id,
        form=form, # Pass the form instance
        **g.user_context
    )

@frontend_bp.route('/admin/topics/<int:topic_id>/questions')
# @jwt_required() # Prefer g.user_context checks for frontend routes
def question_management(topic_id):
    if not g.user_context.get('is_logged_in') or \
       g.user_context.get('user_type') not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))

    topic = Topic.query.get_or_404(topic_id)
    
    # Authorization: Ensure admin has access to this topic's organization
    if g.user_context.get('user_type') != 'super_admin':
        if not topic.subject or not topic.subject.exam or \
           topic.subject.exam.organization_id != g.user_context.get('organization_id'):
            flash('You are not authorized to manage questions for this topic.', 'danger')
            return redirect(url_for('frontend.topic_management', subject_id=topic.subject_id if topic.subject else 0))

    from app.forms import ExamForm # Or a generic CSRF form
    csrf_form = ExamForm() 

    return render_template(
        'admin/question_management.html', 
        topic=topic,
        form=csrf_form, # For CSRF token if needed by JS for create/update/delete
        **g.user_context
    )

@frontend_bp.route('/student/my-review-list')
@jwt_required(optional=True) # Use optional=True so g.user_context is populated
def student_review_list():
    # This check ensures only logged-in students can access this page
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash('Please log in to view your reviewed questions.', 'warning')
        return redirect(url_for('frontend.login'))
    
    # This route just renders the HTML page shell.
    # The JavaScript on the page will fetch the actual list of reviewed questions.
    return render_template('student/review_list.html', **g.user_context)

@frontend_bp.route('/student/my-organizations')
def student_my_organizations():
    # Your existing user check is correct
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash('Please log in to view your organizations.', 'warning')
        return redirect(url_for('frontend.login'))
    
    # Γ£à THE FIX: Pass the server name into the template context
    return render_template(
        'student/my_organizations.html', 
        server_name=current_app.config['SERVER_NAME']
    )

@frontend_bp.route('/student/my-exams')
def student_my_exams():
    """
    This is the SINGLE route for the "My Exams" page.
    It handles all multi-tenancy cases and renders one template.
    """
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        return redirect(url_for('frontend.login'))

    # This will hold the specific organization's data, if any.
    org_context = {
        "organization_id": None,
        "organization_name": None
    }
    
    # Case 1: The user is visiting a subdomain (e.g., org.yourapp.com/student/my-exams)
    # The 'org_id' is passed as an argument from the URL rule.
    org_id_from_url = request.view_args.get('organization_id')

    if org_id_from_url:
        org = Organization.query.get_or_404(org_id_from_url)
        org_context["organization_id"] = org.id
        org_context["organization_name"] = org.name

    # Case 2: The user is on a subdomain. `g.current_organization` is already loaded.
    elif g.get('current_organization'):
        org = g.current_organization
        org_context["organization_id"] = org.id
        org_context["organization_name"] = org.name
    
    # Case 3: A specific organization is requested via a query parameter.
    # This is useful for links from other pages, e.g., /student/my-exams?org_id=5
    elif 'org_id' in request.args:
        org = Organization.query.get_or_404(request.args.get('org_id'))
        org_context["organization_id"] = org.id
        org_context["organization_name"] = org.name
        
    # Now, we render our single, powerful template and pass the context to it.
    # The template will use these variables to decide what to show.
    return render_template('student/exam_browse.html', **org_context)


@frontend_bp.route('/student/organization/<int:organization_id>/exams')
def student_org_exam_browse_redirect(organization_id):
    """
    This route captures the old URL structure and uses our new, centralized logic.
    """
    return student_my_exams()


@frontend_bp.route('/browse-exams')
@jwt_required(optional=True) 
def browse_all_exams():
    # Renders the main exam marketplace/search page
    return render_template('public/exam_search.html', **g.user_context)


@frontend_bp.route('/student/start-practice-test')
@jwt_required(optional=True)
def student_start_practice_test():
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        return redirect(url_for('frontend.login'))
    return render_template('student/start_practice_test.html', **g.user_context)

@frontend_bp.route('/student/mock-test/result/<int:attempt_id>')
def student_mock_test_result(attempt_id):
    """Renders the test results page for a specific attempt."""
    
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for('frontend.login'))
    
    # Get the attempt to find the mock_test_id
    attempt = StudentTestAttempt.query.filter_by(
        id=attempt_id,
        student_user_id=g.user_context['user_id']
    ).first()
    
    if not attempt:
        flash("Test result not found.", "danger")
        return redirect(url_for('frontend.student_dashboard'))
    
    return render_template(
        'student/test_result.html',
        attempt_id=attempt_id,
        mock_test_id=attempt.mock_test_id  # Pass the mock_test_id
    )

@frontend_bp.route('/profile')
@jwt_required(optional=True) # Ensures g.user_context is populated
def profile():
    """Renders the universal user profile page for any logged-in user."""
    if not g.user_context.get('is_logged_in'):
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('frontend.login'))
    
    # The route just renders the shell. JavaScript will fetch data and handle updates.
    return render_template('account/profile.html', **g.user_context)

@frontend_bp.route('/<page_slug>')
def public_page(page_slug):
    """
    Serves both global and organization-specific public pages.
    """
    organization = g.current_organization
    
    page_map = {
        'about': {'db_field': 'about_html', 'template': 'public/about.html'},
        'contact': {'db_field': 'contact_data', 'template': 'public/contact.html'}, # Use contact_data
        'privacy': {'db_field': 'privacy_policy_html', 'template': 'public/privacy.html'},
        'terms': {'db_field': 'tos_html', 'template': 'public/terms.html'},
        'faq': {'db_field': 'faq_data', 'template': 'public/faq.html'}
    }

    if page_slug not in page_map:
        abort(404)

    page_config = page_map[page_slug]
    page_title = page_slug.replace('_', ' ').title()

    if organization:
        # User is on a subdomain. Check for custom content.
        custom_content = getattr(organization, page_config['db_field'], None)
        
        if custom_content:
            # If custom content exists, display it.
            if page_slug == 'faq':
                return render_template(page_config['template'], title=f"{page_title} - {organization.name}", faq_data=custom_content, organization=organization)
            elif page_slug == 'contact':
                 return render_template(page_config['template'], title=f"{page_title} - {organization.name}", contact_data=custom_content, organization=organization)
            else:
                return render_template(
                    'public/public_page_template.html', 
                    title=f"{page_title} - {organization.name}",
                    content=custom_content,
                    organization=organization
                )

    # --- THIS IS THE CORRECTED FALLBACK LOGIC ---
    # If on the main site OR the org has no custom content, render the default page.
    if page_slug == 'faq':
        return render_template(page_config['template'], title=page_title, faq_data=DEFAULT_FAQ_TEMPLATE)
    elif page_slug == 'contact':
        # Pass the default contact data to the contact template
        return render_template(page_config['template'], title=page_title, contact_data=DEFAULT_CONTACT_TEMPLATE)
    else:
        # For all other pages, just render the static template
        return render_template(page_config['template'], title=page_title)

@frontend_bp.route('/global-content-import')
def global_content_import_page():
    """
    Renders the page for admins to upload a single file
    to add content to multiple topics at once.
    """
    # This corrected check now allows both main_co_admin and co_admin
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    # If the check passes, render the page.
    return render_template('admin/global_content_import.html', **g.user_context)

@frontend_bp.route('/super-admin/archive')
def archived_content():
    # This check uses the g.user_context from the session, which is the correct
    # way to protect a frontend page.
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'super_admin':
        flash('Access denied. Super Admin privileges required.', 'danger')
        return redirect(url_for('frontend.login'))
    
    # If the check passes, render the page.
    return render_template('super_admin/archived_content.html', **g.user_context)
# Route for Students (leads to the setup page)

@frontend_bp.route('/admin/ai-assistant')
def admin_ai_assistant():
    """
    Renders the AI Assistant page for authorized administrators.
    This function now uses the correct method for protecting a web page.
    """
    # 1. First, check if the user is logged in at all.
    if not g.user_context.get('is_logged_in'):
        flash("Please log in to access this feature.", "warning")
        return redirect(url_for('frontend.login'))

    # 2. Check if the user is an admin type.
    user_type = g.user_context.get('user_type')
    if user_type not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash("This feature is for administrators.", "danger")
        return redirect(g.user_context.get('dashboard_url'))

    # 3. Check for premium access (Super Admins are always premium).
    if not g.user_context.get('is_premium'):
         flash("A premium subscription is required to use the AI Assistant.", "warning")
         # We can create an admin-specific subscription page later if needed.
         # For now, we'll redirect them to their dashboard.
         return redirect(g.user_context.get('dashboard_url'))
    
    # 4. If all checks pass, render the page.
    return render_template('admin/ai_assistant.html', **g.user_context)

@frontend_bp.route('/complete-subscription')
def complete_subscription():
    # This is the correct pattern for protecting a user-facing page.
    # It checks the session context that is loaded before every request.
    if not g.user_context.get('is_logged_in'):
        flash('Please log in to complete your subscription.', 'warning')
        return redirect(url_for('frontend.login'))

    # You can add a more specific role check if you want, for example:
    if g.user_context.get('user_type') not in ['main_co_admin', 'super_admin']:
         flash('You do not have permission to access this page.', 'danger')
         return redirect(g.user_context.get('dashboard_url') or url_for('frontend.index'))

    # If all checks pass, render the page. The user is properly logged in.
    # The 'access_token' is already in g.user_context for any JavaScript on this page to use.
    return render_template('admin/complete_subscription.html', **g.user_context)

@frontend_bp.route('/payment/verify-org-subscription')
@jwt_required()
def verify_org_subscription_payment():
    # This page handles the verification after returning from Razorpay
    # (The logic for this route is in the payment.py file)
    return render_template('public/payment_verify.html', 
        payment_id=request.args.get('payment_id'),
        order_id=request.args.get('order_id'),
        signature=request.args.get('signature')
    )

@frontend_bp.route('/account-status')
def account_status():
    # This is the correct pattern for protecting a page.
    # It checks the context that was loaded from the valid session cookie.
    if not g.user_context.get('is_logged_in'):
        flash('You must be logged in to view your account status.', 'warning')
        return redirect(url_for('frontend.login'))
    
    # If the user is logged in, the page can be safely rendered.
    return render_template('admin/account_status.html', **g.user_context)

@frontend_bp.route('/organization/settings')
def organization_settings_page():
    # --- This is the correct way to protect a web page ---
    # It checks the session context, it does NOT use an API decorator.
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'main_co_admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
    
    # If the check passes, render the page.
    return render_template('admin/organization_settings.html', **g.user_context)

@frontend_bp.route('/student/mock-test/<int:mock_test_id>/leaderboard')
def leaderboard_page(mock_test_id):
    """Renders the leaderboard page for a specific mock test."""

    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for('frontend.login'))

    # Γ£à Check organization ownership
    mock_test = MockTest.query.join(Exam, MockTest.exam_id == Exam.id).filter(
        MockTest.id == mock_test_id,
        Exam.organization_id == g.user_context['organization_id']
    ).first()

    if not mock_test:
        flash("You are not allowed to view this leaderboard.", "danger")
        return redirect(url_for('frontend.student_dashboard'))

    return render_template(
        'student/leaderboard.html',
        mock_test_id=mock_test_id,
    )

@frontend_bp.route('/student/study-plan')
def study_plan_page():
    """Renders the student's personalized study plan page."""
    
    # Γ£à THE FIX: Use g.user_context for page protection, not an API decorator.
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'student':
        flash("You must be logged in to view your study plan.", "warning")
        return redirect(url_for('frontend.login'))
        
    return render_template(
        'student/study_plan.html', 
        organization=g.current_organization
    )


@frontend_bp.route('/admin/exam/<int:exam_id>/study-plan')
def study_plan_editor(exam_id):
    """Renders the editor page for an exam's study plan."""
    
    # Γ£à THE FIX: This is the correct way to protect a frontend page.
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    exam = Exam.query.filter_by(id=exam_id, organization_id=g.current_organization.id).first_or_404()
    
    return render_template(
        'admin/study_plan_editor.html', 
        exam=exam
    )

@frontend_bp.route('/admin/locked-attempts') 
def view_locked_attempts():
    """Renders the page for managing locked student test attempts."""
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
    return render_template('admin/locked_attempts.html')
        
@frontend_bp.route('/admin/grade-submissions')
def grade_submissions_page():
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    return render_template('admin/grade_submissions.html')

@frontend_bp.route('/admin/image-uploader')
def image_uploader_page():
    """Renders the dedicated page for uploading images."""
    
    # Γ£à THE FIX: This is the correct way to protect a frontend page.
    # It checks the user's session before rendering the HTML.
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin', 'super_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    return render_template('admin/image_uploader.html')


@frontend_bp.route('/super-admin/approvals')
def approval_queue_page():
    """
    Renders the page for the super admin to approve new organizations.
    This now uses the correct security pattern for a frontend page.
    """
    # This is the correct security check, consistent with your other pages
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'super_admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    # If the check passes, render the page.
    return render_template('super_admin/approval_queue.html', **g.user_context)

@frontend_bp.route('/admin/reported-content')
def reported_content_page():
    """Renders the page for admins to review reported questions."""
    
    # --- THIS IS THE FIX ---
    # We use the standard g.user_context check for frontend pages
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    # If the check passes, render the page.
    return render_template('admin/reported_content.html', **g.user_context)

@frontend_bp.route('/pricing')
def pricing_page():
    """Renders the public pricing page."""
    return render_template('public/pricing.html')

@frontend_bp.route('/super-admin/organization-reports')
def organization_reports_page():
    """Renders the page for the super admin to review reported organizations."""
    
    # This is the correct security check for a frontend page
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') != 'super_admin':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
        
    # If the check passes, render the page
    return render_template('super_admin/organization_reports.html', **g.user_context)

@frontend_bp.route('/forum')
def forum_home():
    """Renders the main forum page."""
    # --- THIS IS THE FIX ---
    # We now use the correct security check for a frontend page.
    if not g.user_context.get('is_logged_in'):
        flash("You must be logged in to access the forum.", "warning")
        return redirect(url_for('frontend.login'))
    
    return render_template('community/forum.html')


@frontend_bp.route('/forum/post/<int:post_id>')
def view_forum_post(post_id):
    """Renders the page for a single forum post."""
    
    post = ForumPost.query.get_or_404(post_id)
    
    return render_template('community/view_post.html', post=post)

@frontend_bp.route('/admin/calendar') 
def view_class_calendar():
    """
    Renders the main calendar page for class scheduling.
    This is the single, correct route for this page.
    """
    # 1. First, check if the user is a logged-in admin
    if not g.user_context.get('is_logged_in') or g.user_context.get('user_type') not in ['main_co_admin', 'co_admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('frontend.login'))
    
    # 2. Find the admin's organization to pass its ID to the calendar
    user_id = g.user_context.get('user_id')
    membership = OrganizationMembership.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()

    if not membership:
        flash("You are not an active member of any organization.", "warning")
        # Redirect to their specific dashboard
        return redirect(url_for(g.user_context.get('dashboard_url')))

    # 3. If all checks pass, render the calendar page
    return render_template(
        'admin/calendar.html', 
        organization_id=membership.organization_id
    )

@frontend_bp.route('/class/<int:class_id>/live')
def live_class_view(class_id):
    """Renders the live class viewing page."""
    if not g.user_context.get('is_logged_in'):
        flash("You must be logged in to view a live class.", "warning")
        return redirect(url_for('frontend.login'))
        
    live_class = Class.query.get_or_404(class_id)
    user_id = g.user_context.get('user_id')
    user_type = g.user_context.get('user_type')

    # THIS IS THE FIX: Use the correct context for security checks
    is_admin = user_type in ['main_co_admin', 'co_admin']
    participant = ClassParticipant.query.filter_by(
        class_id=class_id, user_id=user_id
    ).first()

    if not participant and not is_admin:
        flash("You are not enrolled in this class.", "danger")
        # Redirect to the user's specific dashboard
        return redirect(url_for(g.user_context.get('dashboard_url')))

    # Render the page, passing the class details to the template
    return render_template('student/live_class.html', live_class=live_class, current_user_id=user_id)


@frontend_bp.route('/my-notifications')
def all_notifications_page():
    """Renders the page to display all user notifications."""
    if not g.user_context.get('is_logged_in'):
        flash("Please log in to view your notifications.", "warning")
        return redirect(url_for('frontend.login'))
        
    return render_template('account/all_notifications.html')
