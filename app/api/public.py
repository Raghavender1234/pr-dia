from flask import Blueprint, jsonify, request, current_app
from app import db                                  # ← your SQLAlchemy db
from app.models import Exam, Organization, Plan          # ← your Exam & Organization models
from sqlalchemy import or_                          # ← for the OR filter
from flask import g  # For accessing global context



public_api_bp = Blueprint(
    'public_api',
    __name__,
    url_prefix='/api/public'
)

@public_api_bp.route('/search-exams', methods=['GET'])
def search_exams():
    """Public search for exams with robust duplicate handling."""
    name_query = request.args.get('name', '', type=str)
    org_code_query = request.args.get('org_code', '', type=str)
    is_free_query = request.args.get('is_free', 'false', type=str).lower() == 'true'

    # Base query joining Exam and Organization (exclude internal-only exams from public search)
    query = db.session.query(Exam).join(Organization).filter(
        Exam.deleted_at.is_(None),
        Organization.status == 'active',
        Exam.is_internal_only == False
    )

    # Filter by subdomain if applicable
    if g.get('current_organization'):
        query = query.filter(Exam.organization_id == g.current_organization.id)

    # Filter by search term in exam name OR organization name
    if name_query:
        search_term = f"%{name_query}%"
        query = query.filter(or_(
            Exam.name.ilike(search_term),
            Organization.name.ilike(search_term)
        ))

    # Filter by organization code
    if org_code_query:
        query = query.filter(Organization.code.ilike(f"%{org_code_query}%"))

    # Filter by free exams
    if is_free_query:
        query = query.filter(Exam.is_free == True)

    # ** THIS IS THE FIX **
    # Instead of relying solely on database `distinct`, we will ensure
    # uniqueness in Python, which is foolproof.
    
    # First, get all potential results from the database.
    all_exams_from_db = query.limit(100).all() # Fetch a bit more to allow for duplicates.

    # Now, create a final list with only unique exams.
    unique_exams = []
    seen_exam_ids = set()
    for exam in all_exams_from_db:
        if exam.id not in seen_exam_ids:
            unique_exams.append(exam)
            seen_exam_ids.add(exam.id)

    # Format the unique results for the frontend
    results = [{
        "id": exam.id,
        "name": exam.name,
        "description": exam.description,
        "organization_name": exam.organization.name,
        "is_free": exam.is_free,
        "price": exam.price if exam.price else "Free",
        "is_verified": exam.organization.is_verified
    } for exam in unique_exams]

    # Return only up to 50 unique results to the frontend.
    return jsonify(results[:50]), 200

@public_api_bp.route('/plans', methods=['GET'])
def get_public_plans():
    """Fetches the top 3 publicly visible and active subscription plans."""
    try:
        # ✅ This query now matches your Plan model's column names
        plans = Plan.query.filter_by(
            status='active',
            is_publicly_available=True
        ).order_by(Plan.monthly_price).limit(3).all()

        serialized_plans = [{
            "id": plan.id,
            "name": plan.name,
            "price": plan.monthly_price
        } for plan in plans]
        return jsonify(serialized_plans)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching public plans: {e}")
        return jsonify({"message": "Could not load subscription plans."}) , 500

from app.utils.email_utils import send_email

@public_api_bp.route('/contact', methods=['POST'])
def contact_form():
    """
    Handles contact form submissions.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')

    if not all([name, email, subject, message]):
        return jsonify({"message": "All fields are required."}), 400

    # Send email to admin
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if not admin_email:
        current_app.logger.error("ADMIN_EMAIL not set.")
        return jsonify({"message": "Could not send message."}), 500

    html_content = f"""
    <h3>New Contact Form Submission</h3>
    <p><b>Name:</b> {name}</p>
    <p><b>Email:</b> {email}</p>
    <p><b>Subject:</b> {subject}</p>
    <p><b>Message:</b></p>
    <p>{message}</p>
    """

    send_email(
        to_email=admin_email,
        subject=f"New Contact Form Submission: {subject}",
        html_content=html_content
    )

    return jsonify({"message": "Your message has been sent successfully!"}), 200
