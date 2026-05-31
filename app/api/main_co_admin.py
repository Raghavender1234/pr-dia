from flask import Blueprint, request, jsonify, current_app, send_file, url_for
from app import db
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User
from app.models.exam import Exam, StudyPlan, StudyPlanItem
from app.models.subject import Subject
from app.models.topic import Topic, TopicContent
from app.models.student_progress import StudentExam, StudentAISubscription, StudentTestAttempt, StudentQuestionResponse, StudentWeeklyProgress
from app.models.question import Question, MCQOption, ComprehensionPassage, ReportedContent
from app.models.reports import MockTestReport, TopicPerformanceSummary
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.mock_test import MockTest, MockTestQuestion
from .decorators import admin_role_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case, or_, and_
from sqlalchemy.orm import joinedload
from flask_jwt_extended import jwt_required, get_jwt_identity
from razorpay import Client as RazorpayClient
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import base64
from app.extensions import scheduler
from app.models.class_management import Notification
import os
import uuid
import mimetypes
from urllib.parse import quote
import io
import csv
import json
from datetime import datetime, timezone, timedelta
import boto3
from botocore.exceptions import NoCredentialsError, ParamValidationError
import openpyxl
from app.utils.embed_urls import to_embed_url, ensure_scheme
import requests
from docx import Document
from bs4 import BeautifulSoup
from docx.shared import Inches, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import zipfile
from app.api.ai import client
import bleach
from PIL import Image
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch


DEFAULT_CONTACT_TEMPLATE = {
    "address": "2-3-703/a/2\nAmberpet, Hyderabad, Telangana\n500013, India",
    "general_email": "brreddy16@gmail.com",
    "support_email": "info@pr-dia.com",
    "phone": "(+91) 8712896693, (+44) 07554849910"
}


DEFAULT_FAQ_TEMPLATE = [
    {
        "question": "What is the DIA Exam Prep App?",
        "answer": "The DIA Exam Prep App is a comprehensive online platform designed to help students prepare for their exams. We offer a wide range of study materials, practice quizzes, AI-powered feedback, and official mock tests to ensure you are fully prepared for your exam day.",
        "category": "General"
    },
    {
        "question": "How can I get started with the DIA Exam Prep App?",
        "answer": "Getting started is easy! Simply click the 'Sign Up' button on our homepage to create an account. Once registered, you can explore our features, enroll in courses, and start your personalized study plan.",
        "category": "General"
    },
    {
        "question": "Is the DIA Exam Prep App available on mobile?",
        "answer": "Yes, our platform is fully responsive and works seamlessly on all modern web browsers, including on desktops, tablets, and smartphones. A dedicated mobile app is also in development to provide an even better mobile experience.",
        "category": "General"
    },
    {
        "question": "What features does the AI Assistant offer?",
        "answer": "Our integrated AI Assistant provides personalized feedback on your practice tests, helps you understand complex topics, and offers tailored suggestions to improve your study strategy. It's like having a personal tutor available 24/7.",
        "category": "Features"
    },
    {
        "question": "How do 'Official Mock Tests' differ from 'Practice Tests'?",
        "answer": "<strong>Official Mock Tests</strong> are designed by expert educators to mimic the actual exam experience, including timing, format, and difficulty. <strong>Practice Tests</strong> are customizable quizzes that you can generate to focus on specific subjects or topics, allowing you to practice at your own pace.",
        "category": "Features"
    },
    {
        "question": "Can I track my performance and progress?",
        "answer": "Absolutely. Your personal dashboard includes a 'Study Plan' section with detailed analytics on your performance. You can monitor your scores, identify strengths and weaknesses, and track your improvement over time.",
        "category": "Students"
    },
    {
        "question": "How do I enroll in an exam course?",
        "answer": "After logging in, you can browse the available exam courses on your dashboard. Click on any course to see its details, including curriculum and pricing, and follow the on-screen instructions to enroll.",
        "category": "Students"
    },
    {
        "question": "What should I do if I forget my password?",
        "answer": "If you forget your password, click the 'Forgot Password' link on the login page. You will receive an email with instructions on how to reset your password and regain access to your account.",
        "category": "Account"
    },
    {
        "question": "How is my personal data protected?",
        "answer": "We take data privacy seriously. All personal information is encrypted and stored securely. For more details, please review our Privacy Policy. We are committed to protecting your data and providing a secure learning environment.",
        "category": "Account"
    },
    {
        "question": "Who should I contact for support?",
        "answer": "For technical assistance or any questions about the platform, please contact our support team through the contact information provided on the 'Contact Us' page. We are here to help you succeed.",
        "category": "Support"
    }
]
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS)
ALLOWED_TAGS.update([
    'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5',
    'table', 'thead', 'tbody', 'tr', 'td', 'th', 'img', 'a', 'ul', 'ol', 'li',
    'strong', 'em', 'blockquote'
])

DEFAULT_ATTRS = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES = DEFAULT_ATTRS
ALLOWED_ATTRIBUTES.update({
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'a': ['href', 'title', 'target']
})


main_co_admin_bp = Blueprint('main_co_admin_api', __name__, url_prefix='/api/main-co-admin')

razorpay_client = RazorpayClient(auth=(
    os.getenv("RAZORPAY_KEY"),
    os.getenv("RAZORPAY_SECRET")
))

@main_co_admin_bp.route('/register_org', methods=['POST'])
def register_organization():
    data = request.get_json()
    org_name = data.get('organization_name')
    org_code = data.get('organization_code')
    admin_email = data.get('email')
    password = data.get('password')
    plan = data.get('plan')

    if not all([org_name, org_code, admin_email, password, plan]):
        return jsonify({"error": "Missing required fields for organization registration"}), 400

    if Organization.query.filter_by(code=org_code).first():
        return jsonify({"error": "Organization code already exists"}), 400

    if User.query.filter_by(email=admin_email).first():
        return jsonify({"error": "User with this email already registered"}), 400

    try:
        new_org = Organization(name=org_name, code=org_code, active=False, plan=plan)
        db.session.add(new_org)
        db.session.flush()

        new_admin_user = User(
            email=admin_email,
            first_name=org_name + " Admin",
            last_name="Account",
            user_type='main_co_admin',
            status='pending_approval'
        )
        new_admin_user.set_password(password)
        db.session.add(new_admin_user)
        db.session.flush()

        membership = OrganizationMembership(
            user_id=new_admin_user.id,
            organization_id=new_org.id,
            is_active=False
        )
        db.session.add(membership)
        db.session.commit()

        plan_prices = {"basic": 50000, "pro": 100000, "premium": 200000}
        amount = plan_prices.get(plan, 50000)
        razorpay_order = razorpay_client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": f"{new_org.code}_signup_{new_org.id}",
            "payment_capture": 1,
            "notes": {
                "organization_id": new_org.id,
                "user_id": new_admin_user.id,
                "user_type": "main_co_admin"
            }
        })

        return jsonify({
            "message": "Organization registration initiated. Please complete payment.",
            "razorpay_order": razorpay_order,
            "organization_id": new_org.id,
            "main_co_admin_user_id": new_admin_user.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error. Check unique constraints."} ), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error registering organization: {str(e)}"}), 500

def serialize_organization(org):
    return {
        "id": org.id,
        "name": org.name,
        "code": org.code,
        "plan": org.plan,
        "active": org.active,
        "created_at": org.created_at.isoformat() if hasattr(org, 'created_at') else None,
        "updated_at": org.updated_at.isoformat() if hasattr(org, 'updated_at') else None
    }

def serialize_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_type": user.user_type,
        "status": user.status,
        "last_login": user.last_login.isoformat() if getattr(user, 'last_login', None) else None
    }

def serialize_membership(membership):
    return {
        "user_id": membership.user_id,
        "organization_id": membership.organization_id,
        "is_active": membership.is_active,
        "joined_at": membership.joined_at.isoformat() if getattr(membership, 'joined_at', None) else None
    }

def serialize_exam(exam):
    return {
        "id": exam.id,
        "organization_id": exam.organization_id,
        "name": exam.name,
        "description": exam.description,
        "price": str(exam.price),
        "is_free": exam.is_free,
        "created_by_user_id": exam.created_by_user_id,
        "created_at": exam.created_at.isoformat() if hasattr(exam, 'created_at') else None,
        "updated_at": exam.updated_at.isoformat() if hasattr(exam, 'updated_at') else None
    }

def serialize_subject(subject):
    return {
        "id": subject.id,
        "exam_id": subject.exam_id,
        "name": subject.name,
        "description": subject.description,
        "created_by_user_id": subject.created_by_user_id,
        "topics_count": len(subject.topics) if hasattr(subject, 'topics') else 0,
        "created_at": subject.created_at.isoformat() if hasattr(subject, 'created_at') else None,
        "updated_at": subject.updated_at.isoformat() if hasattr(subject, 'updated_at') else None
    }

def serialize_topic(topic, include_content=False):
    data = {
        "id": topic.id,
        "subject_id": topic.subject_id,
        "name": topic.name,
        "description": topic.description,
        "questions_count": Question.query.filter_by(topic_id=topic.id, parent_question_id=None).count(),
        "contents_count": len(topic.contents) if hasattr(topic, 'contents') else 0,
        "created_by_user_id": topic.created_by_user_id,
        "created_at": topic.created_at.isoformat() if hasattr(topic, 'created_at') else None,
        "updated_at": topic.updated_at.isoformat() if hasattr(topic, 'updated_at') else None
    }
    if include_content and hasattr(topic, 'contents'):
        data["contents"] = [
            serialize_topic_content(c) for c in topic.contents
        ]
    return data

def serialize_topic_content(content):
    # Normalize URL-ish values for outbound payload
    raw_value = content.content_value or ""
    ctype = (content.content_type or "").strip().lower()
    if ctype in ("pdf", "video", "video_loop", "link", "image", "gif"):
        raw_value = ensure_scheme(raw_value)

    resolved = None
    if ctype in ("pdf", "video", "video_loop", "link", "image", "gif"):
        resolved = to_embed_url(ctype, raw_value)

    return {
        "id": content.id,
        "topic_id": content.topic_id,
        "title": content.title,
        "content_type": ctype,                  # normalized
        "content_value": raw_value,             # normalized (scheme added)
        "resolved_url": resolved,               # iframe/open-friendly URL
        "item_order": content.item_order,
        "created_at": content.created_at.isoformat() if getattr(content, 'created_at', None) else None,
        "updated_at": content.updated_at.isoformat() if getattr(content, 'updated_at', None) else None,
        "deleted_at": content.deleted_at.isoformat() if getattr(content, 'deleted_at', None) else None,
    }

def serialize_mcq_option(option):
    """Serializes a single MCQ option, including the answer."""
    return {
        "id": option.id,
        "option_text": option.option_text,
        "is_correct": option.is_correct
    }

def serialize_comprehension_passage(passage):
    """Serializes a comprehension passage."""
    if not passage:
        return None
    return {
        "id": passage.id,
        "passage_text": passage.passage_text
    }

def serialize_question(question, include_sub_questions=False):
    """
    The definitive serializer for all question types.
    This is used by both admin and student-facing APIs.
    """
    if not question:
        return None
     
    # --- 1. Base data for ALL question types ---
    q_data = {
        "id": question.id,
        "topic_id": question.topic_id,
        "question_type": question.question_type,
        "question_text": question.question_text,
        "explanation_text": question.explanation_text,
        "difficulty_level": question.difficulty_level,
        "parent_question_id": question.parent_question_id,
        "created_at": question.created_at.isoformat() if hasattr(question, 'created_at') and question.created_at else None,
        "updated_at": question.updated_at.isoformat() if hasattr(question, 'updated_at') and question.updated_at else None
    }
    
    # --- 2. Add specific fields based on the question type ---
    if question.question_type == "MCQ":
        # Filter out any deleted options if applicable
        active_options = [opt for opt in question.mcq_options if not hasattr(opt, 'deleted_at') or not opt.deleted_at]
        q_data["mcq_options"] = [serialize_mcq_option(opt) for opt in active_options]
     
    elif question.question_type == "Comprehension":
        # Use safe passage text extraction
        q_data["passage_text"] = question.comprehension_passage.passage_text if question.comprehension_passage else ""
                 
        # Recursively serialize the sub-questions if requested
        if include_sub_questions:
            # Filter out deleted sub-questions
            active_subs = [sub for sub in question.sub_questions if not hasattr(sub, 'deleted_at') or not sub.deleted_at]
            q_data["sub_questions"] = [serialize_question(sub, include_sub_questions=True) for sub in sorted(active_subs, key=lambda x: x.id)]
     
    elif question.question_type == "OpenEnded":
        q_data["sample_answer"] = question.sample_answer
     
    return q_data

def serialize_question_for_bank(question):
    return {
        "id": question.id,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "difficulty_level": question.difficulty_level,
        "sub_questions_count": len(question.sub_questions) if question.question_type == "Comprehension" else 0
    }

def serialize_mock_test(test):
    """
    Serializes a MockTest object with proper UTC timezone handling.
    """
    def format_utc_datetime(dt):
        """Helper to format datetime as UTC ISO string"""
        if dt is None:
            return None
        
        dt_aware = ensure_utc_aware(dt)
        return dt_aware.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    return {
        "id": test.id,
        "exam_id": test.exam_id,
        "exam_name": test.exam.name if test.exam else 'N/A',
        "title": test.title,
        "description": test.description,
        "duration_minutes": test.duration_minutes,
        "total_marks": str(test.total_marks),
        "passing_marks": str(test.passing_marks),
        "status": test.status,
        "report_status": test.report_status,
        "is_live_test": bool(test.is_live_test),
        "live_start_time": format_utc_datetime(test.live_start_time),
        "live_end_time": format_utc_datetime(test.live_end_time),
        "question_count": len(test.mock_test_questions) if hasattr(test, 'mock_test_questions') else 0,
        "created_at": format_utc_datetime(test.created_at)
    }

def _recalculate_mock_test_total_marks(test_id):
    """
    A helper function to calculate and update the total_marks for a mock test
    based on the sum of the marks of its associated questions.
    """
    test = MockTest.query.get(test_id)
    if not test:
        return
    new_total_marks = db.session.query(
        func.sum(MockTestQuestion.marks)
    ).filter(
        MockTestQuestion.mock_test_id == test_id
    ).scalar() or 0

    test.total_marks = new_total_marks
    db.session.commit()

def serialize_mock_test_question(mtq):
    if not mtq or not mtq.question:
        return None
    return {
        "mock_test_question_id": mtq.id,
        "question_id": mtq.question.id,
        "question_text": mtq.question.question_text,
        "question_order": mtq.question_order,
        "marks": str(mtq.marks)
    }

def serialize_student_test_attempt(attempt):
    return {
        "id": attempt.id,
        "student_user_id": attempt.student_user_id,
        "mock_test_id": attempt.mock_test_id,
        "score": str(attempt.score),
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
    }

def serialize_student_question_response(resp):
    return {
        "id": resp.id,
        "attempt_id": resp.attempt_id,
        "question_id": resp.question_id,
        "chosen_option_id": resp.chosen_option_id,
        "is_correct": resp.is_correct
    }

@main_co_admin_bp.route('/organization/summary', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin'])
def get_organization_summary(current_user, organization, **kwargs):
    total_students = OrganizationMembership.query.join(User).filter(OrganizationMembership.organization_id == organization.id, User.user_type == 'student').count()
    total_co_admins = OrganizationMembership.query.join(User).filter(OrganizationMembership.organization_id == organization.id, User.user_type == 'co_admin').count()
    exams_managed = Exam.query.filter_by(organization_id=organization.id, deleted_at=None).count()
    active_mock_tests = MockTest.query.join(Exam).filter(Exam.organization_id == organization.id, MockTest.status == 'active', MockTest.deleted_at == None).count()
    return jsonify({"total_students": total_students, "total_co_admins": total_co_admins, "exams_managed": exams_managed, "active_mock_tests": active_mock_tests}), 200


@main_co_admin_bp.route('/user_roles_org', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin'])
def get_org_user_roles_distribution(current_user, organization, **kwargs):
    """
    Fetches the distribution of user roles for the main co-admin's organization.
    """
    try:
        # This query groups users by their role within the specific organization and counts them.
        user_role_counts = db.session.query(
            User.user_type, 
            func.count(User.id) # Now 'func' is defined
        ).join(
            OrganizationMembership, User.id == OrganizationMembership.user_id
        ).filter(
            OrganizationMembership.organization_id == organization.id,
            OrganizationMembership.is_active == True,
            User.user_type.in_(['main_co_admin', 'co_admin', 'student'])
        ).group_by(
            User.user_type
        ).all()

        # The keys here now match what the code produces (e.g., 'Main Co Admin' with a space).
        role_map = {
            'Main Co Admin': 0, 
            'Co Admin': 0, 
            'Student': 0
        }

        for role, count in user_role_counts:
            # This line will now work correctly.
            processed_role_name = role.replace('_', ' ').title()
            if processed_role_name in role_map:
                role_map[processed_role_name] = count

        # To maintain a consistent order for the chart labels
        final_labels = ['Student', 'Co Admin', 'Main Co Admin']
        final_counts = [role_map['Student'], role_map['Co Admin'], role_map['Main Co Admin']]

        return jsonify({"labels": final_labels, "counts": final_counts}), 200

    except Exception as e:
        # It's good practice to log the actual error on the server for debugging.
        current_app.logger.error(f"Error in get_org_user_roles_distribution: {e}", exc_info=True)
        return jsonify({"message": "Could not load user roles chart due to a server error."} ), 500

@main_co_admin_bp.route('/exam_performance_trends', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin'])
def get_exam_performance_trends(current_user, organization, **kwargs):
    """
    Calculates and returns the average score and pass rate for each
    exam within the admin's organization.
    """
    try:
        # This query calculates the statistics directly in the database.
        trends = db.session.query(
            Exam.name,
            func.avg(StudentTestAttempt.score).label('avg_score'),
            # Calculate pass rate: (passing_attempts / total_attempts) * 100
            (func.sum(case((StudentTestAttempt.score >= MockTest.passing_marks, 1), else_=0)).cast(db.Float) / 
             func.count(StudentTestAttempt.id) * 100).label('pass_rate')
        ).join(MockTest, StudentTestAttempt.mock_test_id == MockTest.id)\
        .join(Exam, MockTest.exam_id == Exam.id)\
        .filter(
            Exam.organization_id == organization.id,
            StudentTestAttempt.status == 'completed' # Only consider completed tests
        )\
        .group_by(Exam.id, Exam.name)\
        .order_by(Exam.name)\
        .all()

        # Process the query results into the format the chart expects.
        labels = [row.name for row in trends]
        avg_scores = [round(float(row.avg_score or 0), 2) for row in trends]
        pass_rates = [round(float(row.pass_rate or 0), 2) for row in trends]

        return jsonify({
            "labels": labels, 
            "avg_scores": avg_scores, 
            "pass_rates": pass_rates
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching exam performance trends: {e}", exc_info=True)
        return jsonify({"message": "Could not calculate performance data."} ), 500


def _pct(numerator, denominator):
    if not denominator:
        return 0
    return round((float(numerator or 0) / float(denominator)) * 100, 2)


def _readiness_label(score):
    if score >= 75:
        return "Ready"
    if score >= 55:
        return "Watch"
    return "Needs Attention"


@main_co_admin_bp.route('/learning-intelligence', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_learning_intelligence(current_user, organization, **kwargs):
    """Aggregates learning health signals for internal college students."""
    try:
        cutoff_14_days = datetime.utcnow() - timedelta(days=14)

        internal_memberships = OrganizationMembership.query.join(User).filter(
            OrganizationMembership.organization_id == organization.id,
            OrganizationMembership.is_active == True,
            OrganizationMembership.access_type == 'internal',
            User.user_type == 'student'
        ).all()
        internal_membership_ids = [m.id for m in internal_memberships]
        internal_student_ids = [m.user_id for m in internal_memberships]

        if not internal_membership_ids:
            return jsonify({
                "summary": {
                    "internal_students": 0,
                    "active_learners_14d": 0,
                    "completed_attempts": 0,
                    "average_accuracy": 0,
                    "at_risk_students": 0
                },
                "exam_readiness": [],
                "weakest_topics": [],
                "at_risk_students": [],
                "recent_reports": [],
                "remedial_actions": [],
                "question_quality_flags": []
            }), 200

        completed_attempts = StudentTestAttempt.query.join(MockTest).join(Exam).filter(
            StudentTestAttempt.membership_id.in_(internal_membership_ids),
            StudentTestAttempt.status == 'completed',
            Exam.organization_id == organization.id
        ).all()

        active_learners_14d = len({
            attempt.student_user_id
            for attempt in completed_attempts
            if attempt.completed_at and attempt.completed_at >= cutoff_14_days
        })

        total_score = sum(float(attempt.score or 0) for attempt in completed_attempts)
        total_possible = sum(float(attempt.total_possible_score or attempt.mock_test.total_marks or 0) for attempt in completed_attempts)
        average_accuracy = _pct(total_score, total_possible)

        exam_rows = db.session.query(
            Exam.id,
            Exam.name,
            func.count(StudentTestAttempt.id).label('attempt_count'),
            func.count(func.distinct(StudentTestAttempt.student_user_id)).label('learner_count'),
            func.sum(StudentTestAttempt.score).label('score_sum'),
            func.sum(func.coalesce(StudentTestAttempt.total_possible_score, MockTest.total_marks, 0)).label('possible_sum'),
            func.sum(case((StudentTestAttempt.score >= MockTest.passing_marks, 1), else_=0)).label('passed_count')
        ).join(MockTest, MockTest.exam_id == Exam.id)\
         .join(StudentTestAttempt, StudentTestAttempt.mock_test_id == MockTest.id)\
         .filter(
            Exam.organization_id == organization.id,
            Exam.deleted_at.is_(None),
            StudentTestAttempt.membership_id.in_(internal_membership_ids),
            StudentTestAttempt.status == 'completed'
         ).group_by(Exam.id, Exam.name).order_by(Exam.name).all()

        weakest_topic_rows = db.session.query(
            Exam.id.label('exam_id'),
            Exam.name.label('exam_name'),
            Subject.name.label('subject_name'),
            Topic.id.label('topic_id'),
            Topic.name.label('topic_name'),
            func.count(StudentQuestionResponse.id).label('total_answers'),
            func.sum(case((StudentQuestionResponse.is_correct == True, 1), else_=0)).label('correct_answers'),
            func.avg(StudentQuestionResponse.time_taken).label('avg_time_seconds'),
            func.count(func.distinct(StudentTestAttempt.student_user_id)).label('student_count')
        ).select_from(StudentQuestionResponse)\
         .join(StudentTestAttempt, StudentTestAttempt.id == StudentQuestionResponse.attempt_id)\
         .join(Question, Question.id == StudentQuestionResponse.question_id)\
         .join(Topic, Topic.id == Question.topic_id)\
         .join(Subject, Subject.id == Topic.subject_id)\
         .join(Exam, Exam.id == Subject.exam_id)\
         .filter(
            Exam.organization_id == organization.id,
            StudentTestAttempt.membership_id.in_(internal_membership_ids),
            StudentTestAttempt.status == 'completed',
            StudentQuestionResponse.is_correct.isnot(None),
            Topic.deleted_at.is_(None),
            Subject.deleted_at.is_(None),
            Exam.deleted_at.is_(None)
         ).group_by(Exam.id, Exam.name, Subject.name, Topic.id, Topic.name).all()

        topic_accuracy_by_exam = {}
        weakest_topics = []
        for row in weakest_topic_rows:
            accuracy = _pct(row.correct_answers, row.total_answers)
            topic_accuracy_by_exam.setdefault(row.exam_id, []).append(accuracy)
            if row.total_answers >= 3:
                weakest_topics.append({
                    "exam_name": row.exam_name,
                    "subject_name": row.subject_name,
                    "topic_name": row.topic_name,
                    "accuracy": accuracy,
                    "answers": int(row.total_answers or 0),
                    "student_count": int(row.student_count or 0),
                    "avg_time_seconds": round(float(row.avg_time_seconds or 0), 1)
                })
        weakest_topics = sorted(weakest_topics, key=lambda item: (item["accuracy"], -item["answers"]))[:10]

        exam_readiness = []
        for row in exam_rows:
            accuracy = _pct(row.score_sum, row.possible_sum)
            pass_rate = _pct(row.passed_count, row.attempt_count)
            weak_topic_count = len([acc for acc in topic_accuracy_by_exam.get(row.id, []) if acc < 50])
            readiness_score = round((accuracy * 0.55) + (pass_rate * 0.35) + (max(0, 100 - weak_topic_count * 10) * 0.10), 2)
            exam_readiness.append({
                "exam_id": row.id,
                "exam_name": row.name,
                "attempts": int(row.attempt_count or 0),
                "active_learners": int(row.learner_count or 0),
                "average_accuracy": accuracy,
                "pass_rate": pass_rate,
                "weak_topic_count": weak_topic_count,
                "readiness_score": readiness_score,
                "status": _readiness_label(readiness_score)
            })

        student_rows = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            func.count(StudentTestAttempt.id).label('attempt_count'),
            func.sum(StudentTestAttempt.score).label('score_sum'),
            func.sum(func.coalesce(StudentTestAttempt.total_possible_score, MockTest.total_marks, 0)).label('possible_sum'),
            func.sum(case((StudentTestAttempt.score < MockTest.passing_marks, 1), else_=0)).label('failed_count'),
            func.max(StudentTestAttempt.completed_at).label('last_activity')
        ).select_from(User)\
         .join(StudentTestAttempt, StudentTestAttempt.student_user_id == User.id)\
         .join(MockTest, MockTest.id == StudentTestAttempt.mock_test_id)\
         .join(Exam, Exam.id == MockTest.exam_id)\
         .filter(
            User.id.in_(internal_student_ids),
            StudentTestAttempt.membership_id.in_(internal_membership_ids),
            StudentTestAttempt.status == 'completed',
            Exam.organization_id == organization.id
         ).group_by(User.id, User.first_name, User.last_name, User.email).all()

        students_with_attempts = {row.id for row in student_rows}
        at_risk_students = []
        for row in student_rows:
            accuracy = _pct(row.score_sum, row.possible_sum)
            days_inactive = (datetime.utcnow() - row.last_activity).days if row.last_activity else None
            reasons = []
            if accuracy < 50:
                reasons.append("low accuracy")
            if (row.failed_count or 0) >= 2:
                reasons.append("multiple failed tests")
            if days_inactive is not None and days_inactive >= 14:
                reasons.append("inactive for 14+ days")
            if reasons:
                at_risk_students.append({
                    "student_id": row.id,
                    "name": f"{row.first_name} {row.last_name}",
                    "email": row.email,
                    "attempts": int(row.attempt_count or 0),
                    "average_accuracy": accuracy,
                    "failed_tests": int(row.failed_count or 0),
                    "last_activity": row.last_activity.isoformat() if row.last_activity else None,
                    "reason": ", ".join(reasons)
                })

        for membership in internal_memberships:
            if membership.user_id not in students_with_attempts:
                at_risk_students.append({
                    "student_id": membership.user_id,
                    "name": f"{membership.user.first_name} {membership.user.last_name}",
                    "email": membership.user.email,
                    "attempts": 0,
                    "average_accuracy": 0,
                    "failed_tests": 0,
                    "last_activity": None,
                    "reason": "no completed mock tests"
                })

        at_risk_students = sorted(
            at_risk_students,
            key=lambda item: (item["attempts"] > 0, item["average_accuracy"], -item["failed_tests"])
        )[:10]

        recent_reports = MockTestReport.query.join(MockTest).join(Exam).filter(
            MockTestReport.organization_id == organization.id,
            Exam.organization_id == organization.id
        ).order_by(MockTestReport.generated_at.desc()).limit(5).all()

        report_data = [{
            "mock_test_title": report.mock_test.title,
            "exam_name": report.mock_test.exam.name,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "total_attempts": report.total_attempts,
            "average_score": round(float(report.average_score or 0), 2),
            "pass_rate": round(float(report.pass_rate or 0), 2)
        } for report in recent_reports]

        remedial_actions = [{
            "priority": "High" if topic["accuracy"] < 40 else "Medium",
            "exam_name": topic["exam_name"],
            "subject_name": topic["subject_name"],
            "topic_name": topic["topic_name"],
            "suggested_action": "Schedule a remedial class and assign a focused practice quiz.",
            "affected_students": topic["student_count"],
            "accuracy": topic["accuracy"]
        } for topic in weakest_topics[:5]]

        question_quality_rows = db.session.query(
            Question.id,
            Topic.name.label('topic_name'),
            func.count(StudentQuestionResponse.id).label('answers'),
            func.sum(case((StudentQuestionResponse.is_correct == False, 1), else_=0)).label('wrong_answers'),
            func.avg(StudentQuestionResponse.time_taken).label('avg_time_seconds')
        ).select_from(StudentQuestionResponse)\
         .join(StudentTestAttempt, StudentTestAttempt.id == StudentQuestionResponse.attempt_id)\
         .join(Question, Question.id == StudentQuestionResponse.question_id)\
         .join(Topic, Topic.id == Question.topic_id)\
         .join(Subject, Subject.id == Topic.subject_id)\
         .join(Exam, Exam.id == Subject.exam_id)\
         .filter(
            Exam.organization_id == organization.id,
            StudentTestAttempt.membership_id.in_(internal_membership_ids),
            StudentTestAttempt.status == 'completed',
            StudentQuestionResponse.is_correct.isnot(None)
         ).group_by(Question.id, Topic.name).having(func.count(StudentQuestionResponse.id) >= 5).limit(10).all()

        question_quality_flags = []
        for row in question_quality_rows:
            miss_rate = _pct(row.wrong_answers, row.answers)
            if miss_rate >= 80:
                question_quality_flags.append({
                    "question_id": row.id,
                    "topic_name": row.topic_name,
                    "answers": int(row.answers or 0),
                    "miss_rate": miss_rate,
                    "avg_time_seconds": round(float(row.avg_time_seconds or 0), 1),
                    "signal": "High miss rate"
                })

        return jsonify({
            "summary": {
                "internal_students": len(internal_student_ids),
                "active_learners_14d": active_learners_14d,
                "completed_attempts": len(completed_attempts),
                "average_accuracy": average_accuracy,
                "at_risk_students": len(at_risk_students)
            },
            "exam_readiness": exam_readiness,
            "weakest_topics": weakest_topics,
            "at_risk_students": at_risk_students,
            "recent_reports": report_data,
            "remedial_actions": remedial_actions,
            "question_quality_flags": question_quality_flags
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error building learning intelligence: {e}", exc_info=True)
        return jsonify({"message": "Could not calculate learning intelligence."}), 500

@main_co_admin_bp.route('/exams', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_exams(current_user, organization, **kwargs):
    if request.method == 'GET':
        exams = Exam.query.filter_by(organization_id=organization.id, deleted_at=None).order_by(Exam.name).all()
        return jsonify([serialize_exam(e) for e in exams]), 200

    if request.method == 'POST':
        if current_user.user_type != 'main_co_admin':
            return jsonify({"message": "Permission denied to create exams."} ), 403
        
        data = request.get_json()
        is_free = data.get('is_free', False)

        # --- THIS IS THE NEW LOGIC ---
        if is_free:
            plan = organization.plan
            if not plan:
                 return jsonify({"message": "Organization does not have an active plan."} ), 400

            # Count how many free exams this organization already has
            current_free_exam_count = Exam.query.filter_by(
                organization_id=organization.id,
                is_free=True,
                deleted_at=None
            ).count()
            
            if current_free_exam_count >= plan.max_free_exams:
                return jsonify({
                    "message": f"You have reached the limit of {plan.max_free_exams} free exams for your current plan. Please upgrade to create more."
                }), 403
        # --- END OF NEW LOGIC ---

        new_exam = Exam(
            name=data['name'], 
            description=data.get('description'), 
            price=data.get('price', 0), 
            is_free=is_free, 
            organization_id=organization.id, 
            created_by_user_id=current_user.id
        )
        db.session.add(new_exam)
        db.session.commit()
        return jsonify({"message": "Exam created successfully"}), 201

@main_co_admin_bp.route('/exams/<int:exam_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_single_exam(current_user, organization, exam_id, **kwargs):
    exam = Exam.query.filter_by(id=exam_id, organization_id=organization.id, deleted_at=None).first_or_404()
    
    if request.method == 'GET':
        return jsonify({ "id": exam.id, "name": exam.name, "description": exam.description, "price": str(exam.price), "is_free": exam.is_free }), 200

    if request.method == 'PUT':
        data = request.get_json()
        is_being_made_free = data.get('is_free', False)

        # --- THIS IS THE NEW LOGIC ---
        # Check the limit only if the admin is trying to make a currently paid exam free.
        if is_being_made_free and not exam.is_free:
            plan = organization.plan
            if not plan:
                 return jsonify({"message": "Organization does not have an active plan."} ), 400
            
            current_free_exam_count = Exam.query.filter_by(
                organization_id=organization.id,
                is_free=True,
                deleted_at=None
            ).count()
            
            if current_free_exam_count >= plan.max_free_exams:
                return jsonify({
                    "message": f"You have reached the limit of {plan.max_free_exams} free exams for your current plan. Please upgrade to create more."
                }), 403
        # --- END OF NEW LOGIC ---

        exam.name = data.get('name', exam.name)
        exam.description = data.get('description', exam.description)
        exam.is_free = is_being_made_free
        exam.price = 0.00 if exam.is_free else data.get('price', exam.price)
        db.session.commit()
        return jsonify({"message": "Exam updated successfully."} ), 200

    if request.method == 'DELETE':
        if Subject.query.filter_by(exam_id=exam.id, deleted_at=None).first():
            return jsonify({"message": "Cannot archive exam with active subjects."} ), 400
        exam.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Exam archived successfully."} ), 200
# --- Subject Management ---

@main_co_admin_bp.route('/exams/<int:exam_id>/subjects', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_subjects(current_user, organization, exam_id, **kwargs):
    exam = Exam.query.filter_by(id=exam_id, organization_id=organization.id, deleted_at=None).first_or_404()

    if request.method == 'GET':
        subjects = Subject.query.filter_by(exam_id=exam_id, deleted_at=None).order_by(Subject.name).all()
        return jsonify([{ 
            'id': subject.id,
            'exam_id': subject.exam_id,
            'name': subject.name,
            'description': subject.description,
            'topics_count': len(subject.topics),
            'created_at': subject.created_at.isoformat(),
            'updated_at': subject.updated_at.isoformat()
        } for subject in subjects]), 200

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        if not name:
            return jsonify({"message": "Subject name is required"}), 400
        try:
            new_subject = Subject(
                exam_id=exam_id,
                name=name,
                description=description,
                created_by_user_id=current_user.id
            )
            db.session.add(new_subject)
            db.session.commit()
            return jsonify({"message": "Subject created successfully", "subject_id": new_subject.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "A subject with this name already exists under this exam."} ), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating subject: {str(e)}"}), 500


@main_co_admin_bp.route('/subjects/<int:subject_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_single_subject(current_user, organization, subject_id, **kwargs):
    subject = Subject.query.get_or_404(subject_id)
    if subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify({
            'id': subject.id,
            'exam_id': subject.exam_id,
            'name': subject.name,
            'description': subject.description,
            'topics_count': len(subject.topics),
            'created_at': subject.created_at.isoformat(),
            'updated_at': subject.updated_at.isoformat()
        }), 200

    if request.method == 'PUT':
        data = request.get_json()
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        try:
            db.session.commit()
            return jsonify({"message": "Subject updated successfully"}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "A subject with this name already exists under this exam."} ), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error updating subject: {str(e)}"}), 500

    if request.method == 'DELETE':
        active_topic = Topic.query.filter_by(subject_id=subject.id, deleted_at=None).first()
        if active_topic:
            return jsonify({"message": "Cannot delete this subject because it still contains active topics. Please archive them first."} ), 400
        try:
            subject.deleted_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Subject archived successfully."} ), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error archiving subject: {str(e)}"}), 500


# --- Topic Management ---

@main_co_admin_bp.route('/subjects/<int:subject_id>/topics', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_topics(current_user, organization, subject_id, **kwargs):
    subject = Subject.query.get_or_404(subject_id)
    if subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        topics = Topic.query.filter_by(subject_id=subject_id, deleted_at=None).order_by(Topic.name).all()
        return jsonify([{ 
            'id': topic.id,
            'subject_id': topic.subject_id,
            'name': topic.name,
            'description': topic.description,
            'questions_count': db.session.query(Question.id).join(User).filter(
                Question.topic_id == topic.id,
                Question.parent_question_id.is_(None),
                Question.deleted_at.is_(None),
                User.user_type != 'student'
            ).count(),
            'created_at': topic.created_at.isoformat(),
            'updated_at': topic.updated_at.isoformat()
        } for topic in topics]), 200

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        if not name:
            return jsonify({"message": "Topic name is required"}), 400
        try:
            new_topic = Topic(
                subject_id=subject_id,
                name=name,
                description=description,
                created_by_user_id=current_user.id
            )
            db.session.add(new_topic)
            db.session.commit()
            return jsonify({"message": "Topic created successfully", "topic_id": new_topic.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "A topic with this name already exists under this subject."} ), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating topic: {str(e)}"}), 500


@main_co_admin_bp.route('/topics/<int:topic_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_single_topic(current_user, organization, topic_id, **kwargs):
    topic = Topic.query.get_or_404(topic_id)
    if topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify({
            'id': topic.id,
            'subject_id': topic.subject_id,
            'name': topic.name,
            'description': topic.description,
            'questions_count': Question.query.filter_by(topic_id=topic.id, parent_question_id=None).count(),
            'created_at': topic.created_at.isoformat(),
            'updated_at': topic.updated_at.isoformat()
        }), 200

    if request.method == 'PUT':
        data = request.get_json()
        topic.name = data.get('name', topic.name)
        topic.description = data.get('description', topic.description)
        try:
            db.session.commit()
            return jsonify({"message": "Topic updated successfully"}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "A topic with this name already exists under this subject."} ), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error updating topic: {str(e)}"}), 500

    if request.method == 'DELETE':
        if topic.questions.filter_by(deleted_at=None).first():
            return jsonify({"message": "Cannot archive topic. Please archive all questions within it first."} ), 400
        # --- END OF FIX ---
        
        try:
            topic.deleted_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Topic archived successfully."} ), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error archiving topic: {str(e)}"}), 500
        
# --- Topic Content Management ---

@main_co_admin_bp.route('/topics/<int:topic_id>/contents', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def topic_contents(current_user, organization, topic_id, **kwargs):
    topic = Topic.query.get_or_404(topic_id)
    if topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        contents = (
            TopicContent.query
            .filter_by(topic_id=topic_id, deleted_at=None)
            .order_by(TopicContent.item_order)
            .all()
        )
        return jsonify([serialize_topic_content(c) for c in contents]), 200

    # POST
    data = request.get_json() or {}
    try:
        # Normalize content_type to lowercase and trim
        ctype = (data.get('content_type') or 'text').strip().lower()
        if ctype not in ('text', 'pdf', 'video', 'video_loop', 'link', 'image', 'gif'):
            # fallback to 'link' for unknown non-text if a URL is present, else 'text'
            ctype = 'link' if data.get('content_value') else 'text'

        value = data.get('content_value')
        if ctype in ('pdf', 'video', 'video_loop', 'link', "image", "gif"):
            value = ensure_scheme(value)

        new_item = TopicContent(
            topic_id=topic_id,
            title=(data.get('title') or '').strip(),
            content_type=ctype,
            content_value=value,
            item_order=data.get('item_order', 0)
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Content item added successfully.",
            "content": serialize_topic_content(new_item)
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding topic content: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Error adding content."} ), 500

@main_co_admin_bp.route('/topic_content/<int:content_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_single_topic_content(current_user, organization, content_id, **kwargs):
    content = TopicContent.query.get_or_404(content_id)

    if content.topic.subject.exam.organization_id != organization.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify({
            "success": True,
            "message": "Content item fetched.",
            "content": serialize_topic_content(content)
        }), 200

    if request.method == 'PUT':
        data = request.get_json() or {}

        if data.get('restore') is True:
            content.deleted_at = None

        if 'title' in data:
            content.title = (data['title'] or '').strip()

        # determine final content_type first (normalize to lowercase)
        final_type = (data.get('content_type', content.content_type) or 'text').strip().lower()
        if final_type not in ('text', 'pdf', 'video', 'video_loop', 'link', 'image', 'gif'):
            final_type = content.content_type or 'text'
            final_type = final_type.strip().lower()
            if final_type not in ('text', 'pdf', 'video', 'video_loop', 'link', 'image', 'gif'):
                final_type = 'text'
        content.content_type = final_type

        if 'content_value' in data:
            val = data['content_value']
            if final_type in ('pdf', 'video', 'video_loop', 'link', 'image', 'gif'):
                val = ensure_scheme(val)
            content.content_value = val

        if 'item_order' in data:
            content.item_order = data['item_order']

        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Content item updated successfully.",
                "content": serialize_topic_content(content)
            }), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating topic content {content_id}: {e}", exc_info=True)
            return jsonify({"success": False, "message": "Error updating content."} ), 500

    # DELETE -> soft delete (archive)
    try:
        content.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Content item archived successfully.",
            "content": serialize_topic_content(content)
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error archiving topic content {content_id}: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Error archiving content."} ), 500
        
@main_co_admin_bp.route('/topics/<int:topic_id>/comprehension-questions', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_comprehension_questions(current_user, organization, topic_id, **kwargs):
    topic = Topic.query.get_or_404(topic_id)
    if topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    questions = Question.query.filter_by(
        topic_id=topic_id,
        question_type='Comprehension',
        deleted_at=None
    ).all()

    return jsonify([{ 
        "id": q.id,
        "question_text": q.question_text
    } for q in questions]), 200

def _convert_base64_images_to_s3(html_content):
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')

    for img in images:
        src = img.get('src')
        if src and src.startswith('data:image'):
            try:
                # e.g., data:image/png;base64,iVBORw0KGgo...
                header, encoded = src.split(',', 1)
                # Get file extension
                ext = header.split(';')[0].split('/')[1]
                
                decoded_data = base64.b64decode(encoded)
                
                # Create a file-like object
                image_stream = io.BytesIO(decoded_data)
                
                # Create a mock file object for _upload_file_to_s3
                from werkzeug.datastructures import FileStorage
                mock_file = FileStorage(
                    stream=image_stream,
                    filename=f'pasted_image.{ext}',
                    content_type=f'image/{ext}'
                )

                # Upload to S3
                upload_result = _upload_file_to_s3(mock_file, subfolder="content_images")
                image_url = upload_result.get("url")

                if image_url:
                    img['src'] = image_url
                else:
                    # If upload fails, maybe remove the image or leave a placeholder
                    img.decompose() # Or some other handling

            except Exception as e:
                current_app.logger.error(f"Error converting base64 image to S3: {e}", exc_info=True)
                # Decide on error handling: remove image, add alt text, etc.
                img.decompose() # Removing the broken image tag

    return str(soup)


@main_co_admin_bp.route('/topics/<int:topic_id>/questions', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_questions(current_user, organization, topic_id, **kwargs):
    """
    GET: Fetches all questions for a topic.
    POST: Creates a new question (MCQ, Comprehension, or OpenEnded).
    """
    topic = Topic.query.get_or_404(topic_id)
    if topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        # Eager load relationships
        questions = Question.query.join(User, Question.created_by_user_id == User.id).options(
            db.joinedload(Question.sub_questions).joinedload(Question.mcq_options),
            db.joinedload(Question.comprehension_passage),
            db.joinedload(Question.mcq_options)  # Add this for direct MCQ questions
        ).filter(
            Question.topic_id == topic_id,
            Question.deleted_at.is_(None),
            Question.parent_question_id.is_(None),
            User.user_type != 'student'  
        ).order_by(Question.created_at).all()

        return jsonify([serialize_question(q, include_sub_questions=True) for q in questions]), 200

    if request.method == 'POST':
        data = request.get_json()
        question_type = data.get('question_type')
        if not question_type:
            return jsonify({"message": "Question type is required."} ), 400

        try:
            # ✅ Resolve exam_id from topic
            if not topic.subject or not topic.subject.exam_id:
                return jsonify({"message": "Cannot resolve exam_id for this topic"}), 400
            exam_id_val = topic.subject.exam_id

            # Create the main question
            new_question = Question(
                exam_id=exam_id_val,
                topic_id=topic_id,
                question_type=question_type,
                question_text=data.get('question_text'),
                difficulty_level=data.get('difficulty_level', 'medium'),
                explanation_text=data.get('explanation_text'),
                sample_answer=data.get('sample_answer'),
                created_by_user_id=current_user.id
            )

            db.session.add(new_question)
            db.session.flush()  # get new_question.id

            if question_type == 'MCQ':
                for opt_data in data.get('mcq_options', []):
                    mcq_option = MCQOption(
                        question_id=new_question.id,
                        option_text=opt_data.get('option_text'),
                        is_correct=opt_data.get('is_correct', False)
                    )
                    db.session.add(mcq_option)

            elif question_type == 'Comprehension':
                # Convert any pasted base64 images to S3 URLs before saving
                passage_html = data.get('passage_text', '')
                processed_passage_html = _convert_base64_images_to_s3(passage_html)
                # Create passage
                passage = ComprehensionPassage(
                    question_id=new_question.id,
                    passage_text=processed_passage_html
                )
                db.session.add(passage)

                # Create sub-questions
                for order, sub_data in enumerate(data.get('sub_questions', []), 1):
                    sub_q = Question(
                        exam_id=exam_id_val,  # ✅ sub-questions need exam_id too
                        topic_id=topic_id,
                        parent_question_id=new_question.id,
                        question_text=sub_data.get('question_text'),
                        question_type='MCQ',
                        difficulty_level=sub_data.get('difficulty_level', 'medium'),
                        explanation_text=sub_data.get('explanation_text'),
                        sub_question_order=order,
                        created_by_user_id=current_user.id
                    )
                    db.session.add(sub_q)
                    db.session.flush()

                    for opt_data in sub_data.get('mcq_options', []):
                        mcq_option = MCQOption(
                            question_id=sub_q.id,
                            option_text=opt_data.get('option_text'),
                            is_correct=opt_data.get('is_correct', False)
                        )
                        db.session.add(mcq_option)

            db.session.commit()
            return jsonify({
                "message": "Question created successfully!",
                "question": serialize_question(new_question, include_sub_questions=True)
            }), 201

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating question: {e}", exc_info=True)
            return jsonify({"message": "An error occurred while creating the question."} ), 500
 
@main_co_admin_bp.route('/questions/bulk-delete', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def bulk_delete_questions(current_user, organization, **kwargs):
    """Archives a list of questions in bulk."""
    data = request.get_json()
    question_ids = data.get('question_ids', [])

    if not question_ids or not isinstance(question_ids, list):
        return jsonify({"message": "A list of question_ids is required."} ), 400

    try:
        # First, archive all sub-questions of any comprehension questions in the list
        Question.query.filter(
            Question.parent_question_id.in_(question_ids)
        ).update({"deleted_at": datetime.utcnow()}, synchronize_session=False)

        # Then, archive the main questions themselves
        Question.query.filter(
            Question.id.in_(question_ids),
            # Security check: Ensure questions belong to the user's organization
            Question.topic.has(Subject.exam.has(organization_id=organization.id))
        ).update({"deleted_at": datetime.utcnow()}, synchronize_session=False)

        db.session.commit()
        return jsonify({"message": f"Successfully archived {len(question_ids)} questions."} ), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Bulk delete error: {e}", exc_info=True)
        return jsonify({"message": "An error occurred during the bulk delete operation."} ), 500

# ====================================
# FIXED SERIALIZER FUNCTIONS
# ====================================

def serialize_mcq_option(option):
    """Serializes a single MCQ option, including the answer."""
    return {
        "id": option.id,
        "option_text": option.option_text,
        "is_correct": option.is_correct
    }

def serialize_comprehension_passage(passage):
    """Serializes a comprehension passage."""
    if not passage:
        return None
    return {
        "id": passage.id,
        "passage_text": passage.passage_text
    }

def serialize_question(question, include_sub_questions=False):
    """
    The definitive serializer for all question types.
    This is used by both admin and student-facing APIs.
    """
    if not question:
        return None
     
    # --- 1. Base data for ALL question types ---
    q_data = {
        "id": question.id,
        "topic_id": question.topic_id,
        "question_type": question.question_type,
        "question_text": question.question_text,
        "explanation_text": question.explanation_text,
        "difficulty_level": question.difficulty_level,
        "parent_question_id": question.parent_question_id,
        "created_at": question.created_at.isoformat() if hasattr(question, 'created_at') and question.created_at else None,
        "updated_at": question.updated_at.isoformat() if hasattr(question, 'updated_at') and question.updated_at else None
    }
    
    # --- 2. Add specific fields based on the question type ---
    if question.question_type == "MCQ":
        # Filter out any deleted options if applicable
        active_options = [opt for opt in question.mcq_options if not hasattr(opt, 'deleted_at') or not opt.deleted_at]
        q_data["mcq_options"] = [serialize_mcq_option(opt) for opt in active_options]
     
    elif question.question_type == "Comprehension":
        # Use safe passage text extraction
        q_data["passage_text"] = question.comprehension_passage.passage_text if question.comprehension_passage else ""
                 
        # Recursively serialize the sub-questions if requested
        if include_sub_questions:
            # Filter out deleted sub-questions
            active_subs = [sub for sub in question.sub_questions if not hasattr(sub, 'deleted_at') or not sub.deleted_at]
            q_data["sub_questions"] = [serialize_question(sub, include_sub_questions=True) for sub in sorted(active_subs, key=lambda x: x.id)]
     
    elif question.question_type == "OpenEnded":
        q_data["sample_answer"] = question.sample_answer
     
    return q_data

@main_co_admin_bp.route('/questions/<int:question_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_single_question(current_user, organization, question_id, **kwargs):
    question = Question.query.options(
        db.joinedload(Question.sub_questions).joinedload(Question.mcq_options),
        db.joinedload(Question.comprehension_passage),
        db.joinedload(Question.mcq_options)
    ).get_or_404(question_id)

    # Authorization: question must belong to org
    if question.topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        return jsonify(serialize_question(question, include_sub_questions=True)), 200

    if request.method == 'PUT':
        data = request.get_json() or {}

        # Basic editable fields
        question.difficulty_level = data.get('difficulty_level', question.difficulty_level)
        question.explanation_text = data.get('explanation_text', question.explanation_text)

        # Optional: enforce that top-level questions have an exam_id
        if question.parent_question_id is None and question.exam_id is None:
            return jsonify({"message": "Parent question has no exam assigned; cannot update sub-questions without exam."}), 400

        try:
            if question.question_type == 'MCQ':
                question.question_text = data.get('question_text', question.question_text)

                # --- Parent comprehension assignment ---
                parent_id = data.get('parent_question_id')
                if parent_id:
                    # Validate parent belongs to same organization
                    parent = Question.query.get(parent_id)
                    if not parent or parent.topic.subject.exam.organization_id != organization.id:
                        return jsonify({"message": "Invalid parent question"}), 400

                    question.parent_question_id = parent_id

                    # <<< FIX: inherit exam_id from parent when present
                    if question.exam_id is None:
                        question.exam_id = parent.exam_id

                    max_order = db.session.query(
                        db.func.max(Question.sub_question_order)
                    ).filter_by(parent_question_id=parent_id).scalar() or 0
                    question.sub_question_order = max_order + 1
                else:
                    question.parent_question_id = None
                    question.sub_question_order = None

                # --- MCQ Options ---
                existing_options = MCQOption.query.filter_by(question_id=question.id).all()
                existing_ids = {opt.id for opt in existing_options}
                incoming = data.get('mcq_options', [])
                incoming_ids = {opt.get('id') for opt in incoming if opt.get('id')}

                # Delete removed options (if not used)
                to_delete_ids = existing_ids - incoming_ids
                for opt in existing_options:
                    if opt.id in to_delete_ids:
                        is_used = db.session.query(
                            db.exists().where(StudentQuestionResponse.selected_mcq_option_id == opt.id)
                        ).scalar()
                        if not is_used:
                            db.session.delete(opt)

                # Update/Create options
                for opt_data in incoming:
                    if opt_data.get('id') in existing_ids:
                        opt = next(o for o in existing_options if o.id == opt_data['id'])
                        opt.option_text = opt_data.get('option_text', opt.option_text)
                        opt.is_correct = opt_data.get('is_correct', opt.is_correct)
                    else:
                        db.session.add(MCQOption(
                            question_id=question.id,
                            option_text=opt_data.get('option_text'),
                            is_correct=opt_data.get('is_correct', False)
                        ))

            elif question.question_type == 'Comprehension':
                question.question_text = data.get('question_text', question.question_text)
                passage_text = data.get('passage_text')
                sub_questions_data = data.get('sub_questions', [])
                existing_ids = data.get('existing_mcq_ids', [])

                if not passage_text:
                    return jsonify({"message": "Passage text is required."}), 400
                if not sub_questions_data and not existing_ids:
                    return jsonify({"message": "At least one sub-question or existing MCQ is required."}), 400

                # --- Passage ---
                processed_passage_html = _convert_base64_images_to_s3(passage_text)
                if question.comprehension_passage:
                    question.comprehension_passage.passage_text = processed_passage_html
                else:
                    # comprehension passage uses the parent's question.id
                    question.comprehension_passage = ComprehensionPassage(
                        question_id=question.id,
                        passage_text=processed_passage_html
                    )
                    db.session.add(question.comprehension_passage)

                # --- Remove deleted sub-questions ---
                current_sub_ids = {sub.id for sub in question.sub_questions}
                to_delete = current_sub_ids - set(existing_ids)
                for sub_q in list(question.sub_questions):
                    if sub_q.id in to_delete:
                        existing_opts = MCQOption.query.filter_by(question_id=sub_q.id).all()
                        for opt in existing_opts:
                            is_used = db.session.query(
                                db.exists().where(StudentQuestionResponse.selected_mcq_option_id == opt.id)
                            ).scalar()
                            if not is_used:
                                db.session.delete(opt)
                        db.session.delete(sub_q)

                # --- Reset sub_question_order for all remaining sub-questions ---
                order = 1
                all_existing_subs = Question.query.filter_by(
                    parent_question_id=question.id
                ).filter(Question.id.in_(existing_ids)).order_by(Question.id).all()
                for sub in all_existing_subs:
                    sub.sub_question_order = order
                    order += 1

                # --- Assign existing MCQs as sub-questions ---
                for mcq_id in existing_ids:
                    if mcq_id not in current_sub_ids:  # Only if not already a sub-question
                        mcq = Question.query.get(mcq_id)
                        if mcq and mcq.question_type == 'MCQ':
                            # Validate MCQ belongs to same organization
                            if mcq.topic.subject.exam.organization_id != organization.id:
                                return jsonify({"message": "Invalid MCQ selection"}), 400

                            mcq.parent_question_id = question.id
                            mcq.topic_id = question.topic_id
                            # <<< FIX: ensure MCQ inherits parent's exam_id (avoid NOT NULL failure)
                            if mcq.exam_id is None:
                                mcq.exam_id = question.exam_id
                            mcq.sub_question_order = order
                            order += 1

                # --- Add new sub-questions ---
                for sub_data in sub_questions_data:
                    sub_q = Question(
                        topic_id=question.topic_id,
                        parent_question_id=question.id,
                        question_text=sub_data.get('question_text'),
                        question_type='MCQ',
                        difficulty_level=sub_data.get('difficulty_level', 'medium'),
                        explanation_text=sub_data.get('explanation_text'),
                        created_by_user_id=current_user.id,
                        # <<< FIX: inherit exam_id from parent question (required column)
                        exam_id=question.exam_id
                    )
                    sub_q.sub_question_order = order
                    order += 1
                    db.session.add(sub_q)
                    # safe to flush because exam_id is set
                    db.session.flush()

                    for opt_data in sub_data.get('mcq_options', []):
                        db.session.add(MCQOption(
                            question_id=sub_q.id,
                            option_text=opt_data.get('option_text'),
                            is_correct=opt_data.get('is_correct', False)
                        ))

            elif question.question_type == 'OpenEnded':
                question.question_text = data.get('question_text', question.question_text)
                question.sample_answer = data.get('sample_answer', question.sample_answer)

            # <<< FIX: final sanity check - ensure no sub-question will have a null exam_id
            null_exam_exists = db.session.query(
                db.exists().where(
                    (Question.parent_question_id == question.id) &
                    (Question.exam_id.is_(None))
                )
            ).scalar()
            if null_exam_exists:
                db.session.rollback()
                return jsonify({"message": "Internal error: one or more sub-questions lack exam_id. Parent must have an exam."}), 400

            db.session.commit()
            return jsonify({"message": "Question updated successfully."}), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating question {question_id}: {e}", exc_info=True)
            return jsonify({"message": "An error occurred while updating the question."}), 500

    if request.method == 'DELETE':
        question.deleted_at = datetime.utcnow()
        for sub_q in question.sub_questions:
            sub_q.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Question archived successfully."}), 200

def ensure_utc_aware(dt):
    """
    Ensure a datetime is UTC-aware.
    If naive, assume it's already in UTC and add timezone info.
    If aware, convert to UTC.
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    else:
        return dt.astimezone(timezone.utc)


@main_co_admin_bp.route('/mock-tests', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_mock_tests(current_user, organization, **kwargs):
    if current_user.user_type != 'main_co_admin':
        return jsonify({"message": "Permission denied"}), 403
            
    data = request.get_json()
            
    required_fields = ['title', 'exam_id', 'duration_minutes', 'passing_marks']
    if not all(data.get(field) is not None for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400
            
    try:
        live_start_time = None
        live_end_time = None
                    
        if data.get('live_start_time'):
            start_str = data.get('live_start_time')
            if start_str.endswith('Z'):
                start_str = start_str[:-1] + '+00:00'
            live_start_time = datetime.fromisoformat(start_str)
            
            if live_start_time.tzinfo is None:
                live_start_time = live_start_time.replace(tzinfo=timezone.utc)
            else:
                live_start_time = live_start_time.astimezone(timezone.utc)
            
            live_start_time = live_start_time.replace(tzinfo=None)
                    
        if data.get('live_end_time'):
            end_str = data.get('live_end_time')
            if end_str.endswith('Z'):
                end_str = end_str[:-1] + '+00:00'
            live_end_time = datetime.fromisoformat(end_str)
            
            if live_end_time.tzinfo is None:
                live_end_time = live_end_time.replace(tzinfo=timezone.utc)
            else:
                live_end_time = live_end_time.astimezone(timezone.utc)
            
            live_end_time = live_end_time.replace(tzinfo=None)
                    
        new_test = MockTest(
            exam_id=data.get('exam_id'),
            title=data.get('title'),
            description=data.get('description'),
            duration_minutes=int(data['duration_minutes']),
            passing_marks=float(data['passing_marks']),
            status=data.get('status', 'draft'),
            is_live_test=data.get('is_live_test', False),
            live_start_time=live_start_time,
            live_end_time=live_end_time,
            negative_marking_enabled=data.get('negative_marking_enabled', False),
            negative_marking_ratio=float(data.get('negative_marking_ratio', 0.25)),
            created_by_user_id=current_user.id
        )
                    
        db.session.add(new_test)
        db.session.commit()

        # --- THIS IS THE NEW SCHEDULING LOGIC ---
        if new_test.is_live_test and new_test.live_end_time:
            from app.tasks import analyze_mock_test_performance
            # Schedule the analysis to run 10 minutes after the test ends
            run_time = new_test.live_end_time + timedelta(minutes=10)
            
            # Use a unique ID for the job to prevent duplicates
            job_id = f'analyze_mock_test_{new_test.id}'
            
            scheduler.add_job(
                id=job_id,
                func=analyze_mock_test_performance,
                args=[new_test.id],
                trigger='date',
                run_date=run_time,
                replace_existing=True # Overwrite if this test is updated later
            )
            print(f"Scheduled performance analysis for test {new_test.id} to run at {run_time} UTC.")
        # --- END OF NEW LOGIC ---

        return jsonify({
            "message": "Mock Test created successfully!",
            "mock_test": serialize_mock_test(new_test)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating mock test: {e}", exc_info=True)
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
@main_co_admin_bp.route('/mock-tests/<int:test_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_single_mock_test(current_user, organization, test_id, **kwargs):
    test = (MockTest.query
        .join(Exam, MockTest.exam_id == Exam.id)
        .filter(MockTest.id == test_id, Exam.organization_id == organization.id)
        .first_or_404())

    if request.method == 'GET':
        return jsonify(serialize_mock_test(test)), 200

    if current_user.user_type != 'main_co_admin':
        return jsonify({"message": "You do not have permission to edit or delete mock test settings."} ), 403

    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid request data."} ), 400
            
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return jsonify({"message": "Invalid data format received."} ), 400

        # --- UPDATED LOGIC WITH PROPER NULL HANDLING ---

        # 1. Update basic fields
        basic_fields = ['title', 'description', 'duration_minutes', 'passing_marks', 'status']
        for field in basic_fields:
            if field in data:
                setattr(test, field, data[field])

        # 2. Handle exam_id separately if needed
        if 'exam_id' in data:
            test.exam_id = data['exam_id']

        if 'negative_marking_enabled' in data:
            if data['negative_marking_enabled'] is False:
                test.negative_marking_enabled = False
                test.negative_marking_ratio = 0.0  # Provide a default value when disabled
            else:
                test.negative_marking_enabled = True
                # Only read the ratio if it was enabled
                ratio = data.get('negative_marking_ratio')
                if ratio is not None:
                    test.negative_marking_ratio = ratio
                else:
                    # If ratio is not provided but marking is enabled, use default
                    test.negative_marking_ratio = 0.25

        # 4. Smartly handle Live Test status
        if 'is_live_test' in data:
            if data['is_live_test'] is False:
                test.is_live_test = False
                test.live_start_time = None
                test.live_end_time = None
            else:
                test.is_live_test = True
                # Only read the times if it's a live test
                start_str = data.get('live_start_time')
                end_str = data.get('live_end_time')
                if start_str:
                    try:
                        test.live_start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        return jsonify({"message": "Invalid live_start_time format."} ), 400
                if end_str:
                    try:
                        test.live_end_time = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        return jsonify({"message": "Invalid live_end_time format."} ), 400
        
        # 5. Ensure negative_marking_ratio is never null (safety check)
        if test.negative_marking_ratio is None:
            test.negative_marking_ratio = 0.0

        # --- END OF UPDATED LOGIC ---

        # --- THIS IS THE NEW SCHEDULING LOGIC ---
        if test.is_live_test and test.live_end_time:
            from app.tasks import analyze_mock_test_performance
            run_time = test.live_end_time + timedelta(minutes=10)
            job_id = f'analyze_mock_test_{test.id}'
            
            scheduler.add_job(
                id=job_id,
                func=analyze_mock_test_performance,
                args=[test.id],
                trigger='date',
                run_date=run_time,
                replace_existing=True # This is important for updates
            )
            print(f"Rescheduled performance analysis for test {test.id} to run at {run_time} UTC.")
        # --- END OF NEW LOGIC ---
        
        try:
            db.session.commit()
            return jsonify({"message": "Mock test updated successfully."} ), 200
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Database integrity error updating mock test {test_id}: {e}")
            return jsonify({"message": "Database error occurred. Please check the data."} ), 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating mock test {test_id}: {e}")
            return jsonify({"message": "An error occurred while updating the mock test."} ), 500

    # DELETE -> soft delete (archive)
    if request.method == 'DELETE':
        try:
            test.deleted_at = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Mock test has been successfully archived and hidden from view."} ), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error archiving mock test {test_id}: {e}")
            return jsonify({"message": "An error occurred while archiving the mock test."} ), 500


@main_co_admin_bp.route('/mock-tests/<int:test_id>/report', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_mock_test_report_data(current_user, organization, test_id, **kwargs):
    """
    Fetches the performance report data for a specific mock test.
    """
    test = (MockTest.query
        .join(Exam, MockTest.exam_id == Exam.id)
        .filter(MockTest.id == test_id, Exam.organization_id == organization.id)
        .first_or_404())

    report = MockTestReport.query.filter_by(mock_test_id=test.id).first()

    if not report:
        return jsonify({"message": "Report not found for this mock test."} ), 404

    plan = organization.plan
    is_premium = plan and "AI Assistant" in plan.features

    topic_summaries = TopicPerformanceSummary.query.filter_by(report_id=report.id).order_by(TopicPerformanceSummary.average_accuracy.asc()).all()

    serialized_summaries = [{
        "topic_name": s.topic_name,
        "average_accuracy": s.average_accuracy,
        "question_count": s.question_count,
        "student_count": s.student_count
    } for s in topic_summaries]

    report_data = {
        "id": report.id,
        "mock_test_title": test.title,
        "generated_at": report.generated_at.isoformat(),
        "total_attempts": report.total_attempts,
        "average_score": report.average_score,
        "pass_rate": report.pass_rate,
        "topic_performance": serialized_summaries,
        "remedial_plan": report.remedial_plan_details,
        "at_risk_students": report.at_risk_students
    }

    return jsonify({
        "report": report_data,
        "is_premium": is_premium
    }), 200


@main_co_admin_bp.route('/mock-tests/<int:test_id>/generate-report', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin'])
def generate_mock_test_report(current_user, organization, test_id, **kwargs):
    """
    Triggers a background task to generate a performance report for a mock test.
    """
    test = (MockTest.query
        .join(Exam, MockTest.exam_id == Exam.id)
        .filter(MockTest.id == test_id, Exam.organization_id == organization.id)
        .first_or_404())

    if test.report_status == 'pending':
        return jsonify({"message": "A report for this test is already being generated."} ), 409

    # Check for completed attempts
    completed_attempts = StudentTestAttempt.query.filter_by(mock_test_id=test_id, status='completed').count()
    if completed_attempts == 0:
        return jsonify({"message": "Cannot generate a report. There are no completed attempts for this mock test yet."} ), 400

    # Reset status to pending
    test.report_status = 'pending'
    db.session.commit()

    from app.tasks import analyze_mock_test_performance
    # Enqueue the background task
    job_id = f'analyze_mock_test_{test.id}'
    scheduler.add_job(
        id=job_id,
        func=analyze_mock_test_performance,
        args=[test.id],
        trigger='date',
        run_date=datetime.utcnow() + timedelta(seconds=1),
        replace_existing=True
    )

    return jsonify({"message": "Report generation has been started. It will be available shortly."} ), 202


# --- Mock Test Question Association ---

@main_co_admin_bp.route('/mock-tests/<int:test_id>/questions', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_mock_test_questions(current_user, organization, test_id, **kwargs):
    test = MockTest.query.get_or_404(test_id)
    
    # Ensure test belongs to current organization
    if test.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403
    
    if request.method == 'GET':
        # Fetch questions in order
        links = MockTestQuestion.query.filter_by(mock_test_id=test_id).order_by(MockTestQuestion.question_order).all()
        
        return jsonify([{ 
            'mock_test_question_id': link.id,
            'question_id': link.question_id,
            'question_order': link.question_order,
            'marks': str(link.marks),
            'question_text': link.question.question_text if link.question else None
        } for link in links]), 200
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Handle corrupted JSON strings
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return jsonify({"message": "Invalid data format received."} ), 400
        
        question_id = data.get('question_id')
        if not question_id:
            return jsonify({"message": "Question ID is required."} ), 400
        
        # ✅ Validate question exists, is not deleted, and belongs to same organization
        question = Question.query.get(question_id)
        if not question or question.deleted_at or question.parent_question_id:
            return jsonify({"message": "Cannot add this question."} ), 400
        
        if question.topic.subject.exam.organization_id != organization.id:
            return jsonify({"message": "Invalid question selection."} ), 400
        
        # ✅ NEW SECURITY CHECK - Ensure the question was not created by a student
        if question.creator and question.creator.user_type == 'student':
            return jsonify({"message": "Cannot add a student-generated practice question to an official mock test."} ), 403
        
        # Check if already added
        existing = MockTestQuestion.query.filter_by(
            mock_test_id=test_id,
            question_id=question_id
        ).first()
        if existing:
            return jsonify({"message": "This question is already added to the mock test."} ), 400
        
        # Determine question order
        last = MockTestQuestion.query.filter_by(mock_test_id=test_id).order_by(MockTestQuestion.question_order.desc()).first()
        order = (last.question_order + 1) if last else 1
        
        # Add the question
        link = MockTestQuestion(
            mock_test_id=test_id,
            question_id=question_id,
            question_order=order,
            marks=test.default_marks_per_question
        )
        
        try:
            db.session.add(link)
            db.session.commit()
            
            # Recalculate total marks
            _recalculate_mock_test_total_marks(test_id)
            
            return jsonify({
                "message": "Question added to mock test successfully.",
                "mock_test_question_id": link.id,
                "question_id": link.question_id,
                "question_order": link.question_order,
                "marks": str(link.marks)
            }), 201
        
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "This question is already in the mock test (duplicate key)."} ), 400
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding question to mock test {test_id}: {e}", exc_info=True)
            return jsonify({"message": "An error occurred while adding the question."} ), 500
        
@main_co_admin_bp.route('/mock-tests/<int:test_id>/questions/<int:mtq_id>', methods=['PUT', 'DELETE'])
@admin_role_required(allowed_roles=['main_co_admin'])
def manage_single_mock_test_question(current_user, organization, test_id, mtq_id, **kwargs):
    link = MockTestQuestion.query.get_or_404(mtq_id)
    # Security check to ensure the item belongs to the user's organization
    if link.mock_test.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'PUT':
        data = request.get_json()

        # --- THIS IS THE FIX ---
        # Add the robustness check to handle corrupted JSON strings from the frontend.
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return jsonify({"message": "Invalid data format received."} ), 400
        # --- END OF FIX ---

        link.marks = data.get('marks', link.marks)
        db.session.commit()
        _recalculate_mock_test_total_marks(test_id) 
        return jsonify({"message": "Marks updated for question."} ), 200

    if request.method == 'DELETE':
        db.session.delete(link)
        db.session.commit()
        _recalculate_mock_test_total_marks(test_id) 
        return jsonify({"message": "Question removed from mock test."} ), 200


@main_co_admin_bp.route('/mock-tests/<int:test_id>/questions/reorder', methods=['PUT'])
@admin_role_required(allowed_roles=['main_co_admin'])
def reorder_mock_test_questions(current_user, organization, test_id, **kwargs):
    data = request.get_json()
    ordered_ids = data.get('ordered_ids')

    if not isinstance(ordered_ids, list):
        return jsonify({"message": "Invalid data format."} ), 400

    for idx, mtq_id in enumerate(ordered_ids):
        mtq = MockTestQuestion.query.get(mtq_id)
        if mtq and mtq.mock_test_id == test_id and mtq.mock_test.exam.organization_id == organization.id:
            mtq.question_order = idx

    db.session.commit()
    return jsonify({"message": "Question order saved."} ), 200

@main_co_admin_bp.route('/topics/<int:topic_id>/questions/import', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def import_questions_from_file(current_user, organization, topic_id, **kwargs):
    topic = Topic.query.get_or_404(topic_id)
    if topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if 'question_file' not in request.files:
        return jsonify({"message": "No file part in the request."} ), 400

    file = request.files['question_file']
    filename = file.filename
    if not filename or not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        return jsonify({"message": "Please upload a valid .csv or .xlsx file."} ), 400

    rows = []
    try:
        if filename.endswith('.xlsx'):
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            headers = [cell.value for cell in sheet[1]]
            for row in sheet.iter_rows(min_row=2):
                row_data = {headers[i]: cell.value for i, cell in enumerate(row) if headers[i]}
                rows.append(row_data)
        else:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            rows = list(csv_reader)

        parent_map = {}
        newly_created_questions = []
        processed_count = 0
        skipped_duplicates = 0

        # === First Pass: Comprehension ===
        for row in rows:
            if row.get('question_type', '').strip() != 'Comprehension':
                continue

            question_text = str(row.get('question_text', '')).strip()
            passage_text = str(row.get('passage_text', '')).strip()
            if not question_text or not passage_text:
                continue

            # Duplicate check
            exists = Question.query.filter_by(
                topic_id=topic_id,
                question_type='Comprehension',
                question_text=question_text
            ).filter(Question.deleted_at.is_(None)).first()
            if exists:
                skipped_duplicates += 1
                continue

            new_q = Question(
                topic_id=topic_id,
                exam_id=topic.subject.exam_id,  # ✅ ADD THIS LINE
                question_type='Comprehension',
                question_text=question_text,
                explanation_text=str(row.get('explanation_text', '')).strip(),
                image_url=row.get('image_url', '').strip() or None,                
                difficulty_level=str(row.get('difficulty_level', 'medium')).strip(),
                created_by_user_id=current_user.id
            )
            db.session.add(new_q)
            db.session.flush()

            passage = ComprehensionPassage(
                question_id=new_q.id,
                passage_text=passage_text
            )
            db.session.add(passage)
            parent_map[question_text] = new_q
            newly_created_questions.append(new_q)
            processed_count += 1

        # === Second Pass: MCQs ===
        for row in rows:
            if row.get('question_type', '').strip() != 'MCQ':
                continue

            question_text = str(row.get('question_text', '')).strip()
            if not question_text:
                continue

            # Duplicate check
            exists = Question.query.filter_by(
                topic_id=topic_id,
                question_type='MCQ',
                question_text=question_text
            ).filter(Question.deleted_at.is_(None)).first()
            if exists:
                skipped_duplicates += 1
                continue

            parent_id = None
            parent_text = str(row.get('parent_question_text', '')).strip()
            if parent_text in parent_map:
                parent_id = parent_map[parent_text].id

            new_q = Question(
                topic_id=topic_id,
                question_type='MCQ',
                exam_id=topic.subject.exam_id,  # ✅ ADD THIS LINE
                question_text=question_text,
                explanation_text=str(row.get('explanation_text', '')).strip(),
                difficulty_level=str(row.get('difficulty_level', 'medium')).strip(),
                image_url=row.get('image_url', '').strip() or None,                
                created_by_user_id=current_user.id,
                parent_question_id=parent_id
            )

            if parent_id:
                max_order = db.session.query(
                    db.func.max(Question.sub_question_order)
                ).filter_by(parent_question_id=parent_id).scalar() or 0
                new_q.sub_question_order = max_order + 1

            db.session.add(new_q)
            db.session.flush()

            options_added = False
            for i in range(1, 10):
                opt_text = row.get(f'option{i}')
                if not opt_text:
                    continue

                is_correct_raw = str(row.get(f'is_correct{i}', '')).strip().lower()
                is_correct = is_correct_raw in ['1', 'true', 'yes', 'correct']

                db.session.add(MCQOption(
                    question_id=new_q.id,
                    option_text=str(opt_text).strip(),
                    is_correct=is_correct
                ))
                options_added = True

            if not options_added:
                db.session.rollback()
                continue

            if not parent_id:
                newly_created_questions.append(new_q)

            processed_count += 1

        # === Third Pass: OpenEnded ===
        for row in rows:
            if row.get('question_type', '').strip() != 'OpenEnded':
                continue

            question_text = str(row.get('question_text', '')).strip()
            if not question_text:
                continue

            # Duplicate check
            exists = Question.query.filter_by(
                topic_id=topic_id,
                question_type='OpenEnded',
                question_text=question_text
            ).filter(Question.deleted_at.is_(None)).first()
            if exists:
                skipped_duplicates += 1
                continue

            new_q = Question(
                exam_id=topic.subject.exam_id,
                topic_id=topic_id,
                question_type='OpenEnded',
                question_text=question_text,
                explanation_text=str(row.get('explanation_text', '')).strip(),
                difficulty_level=str(row.get('difficulty_level', 'medium')).strip(),
                image_url=row.get('image_url', '').strip() or None, 
                sample_answer=str(row.get('sample_answer', '')).strip(),
                created_by_user_id=current_user.id
            )
            db.session.add(new_q)
            newly_created_questions.append(new_q)
            processed_count += 1

        db.session.commit()

        return jsonify({
            "message": f"Import completed: {processed_count} questions imported. {skipped_duplicates} duplicates skipped.",
            "new_questions": [serialize_question(q, include_sub_questions=True) for q in newly_created_questions]
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Import Error: {e}", exc_info=True)
        return jsonify({"message": f"Import failed: {str(e)}"}), 500

@main_co_admin_bp.route('/mock-tests/<int:mock_test_id>/questions/import', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def import_questions_to_mock_test(current_user, organization, mock_test_id, **kwargs):
    mock_test = MockTest.query.get_or_404(mock_test_id)
    if mock_test.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    if 'question_file' not in request.files:
        return jsonify({"message": "No file part in the request."} ), 400

    file = request.files['question_file']
    filename = file.filename
    if not filename or not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        return jsonify({"message": "Please upload a valid .csv or .xlsx file."} ), 400

    rows = []
    try:
        if filename.endswith('.xlsx'):
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            headers = [cell.value for cell in sheet[1]]
            for row in sheet.iter_rows(min_row=2):
                row_data = {headers[i]: cell.value for i, cell in enumerate(row) if headers[i]}
                rows.append(row_data)
        else:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            rows = list(csv_reader)

        parent_map = {}
        newly_created_questions = []
        processed_count = 0
        skipped_duplicates = 0
        max_order = db.session.query(db.func.max(MockTestQuestion.question_order)) \
            .filter_by(mock_test_id=mock_test_id).scalar() or 0

        # === First Pass: Comprehension ===
        for row in rows:  # ← Fixed: moved left by 4 spaces
            if row.get('question_type', '').strip() != 'Comprehension':
                continue

            question_text = str(row.get('question_text', '')).strip()
            passage_text = str(row.get('passage_text', '')).strip()
            if not question_text or not passage_text:
                continue

            topic_id = row.get('topic_id')
            if not topic_id:
                continue

            topic = Topic.query.get(topic_id)
            if not topic or topic.subject.exam_id != mock_test.exam_id:
                continue

            existing_q = Question.query.filter_by(
                topic_id=topic_id,
                question_text=question_text,
                question_type='Comprehension'
            ).first()

            q_to_add = existing_q

            if not existing_q:
                new_q = Question(
                    topic_id=topic_id,
                    exam_id=mock_test.exam_id,
                    question_type='Comprehension',
                    question_text=question_text,
                    explanation_text=str(row.get('explanation_text', '')).strip(),
                    image_url=row.get('image_url', '').strip() or None,
                    difficulty_level=str(row.get('difficulty_level', 'medium')).strip(),
                    created_by_user_id=current_user.id
                )
                db.session.add(new_q)
                db.session.flush()

                db.session.add(ComprehensionPassage(
                    question_id=new_q.id,
                    passage_text=passage_text
                ))
                parent_map[question_text] = new_q
                newly_created_questions.append(new_q)
                q_to_add = new_q
            else:
                parent_map[question_text] = existing_q

            is_already_in_test = MockTestQuestion.query.filter_by(
                mock_test_id=mock_test_id,
                question_id=q_to_add.id
            ).first()

            if is_already_in_test:
                skipped_duplicates += 1
                continue

            db.session.add(MockTestQuestion(
                mock_test_id=mock_test_id,
                question_id=q_to_add.id,
                marks=1.0,
                question_order=max_order + processed_count + 1
            ))
            processed_count += 1

        # === Second Pass: MCQs ===
        for row in rows:  # ← Fixed: moved left by 4 spaces
            if row.get('question_type', '').strip() != 'MCQ':
                continue

            question_text = str(row.get('question_text', '')).strip()
            if not question_text:
                continue

            topic_id = row.get('topic_id')
            if not topic_id:
                continue

            topic = Topic.query.get(topic_id)
            if not topic or topic.subject.exam_id != mock_test.exam_id:
                continue

            existing_q = Question.query.filter_by(
                topic_id=topic_id,
                question_text=question_text,
                question_type='MCQ'
            ).first()

            q_to_add = existing_q

            if not existing_q:
                parent_text = str(row.get('parent_question_text', '')).strip()
                parent_id = parent_map[parent_text].id if parent_text in parent_map else None

                new_q = Question(
                    topic_id=topic_id,
                    exam_id=mock_test.exam_id,
                    question_type='MCQ',
                    question_text=question_text,
                    explanation_text=str(row.get('explanation_text', '')).strip(),
                    image_url=row.get('image_url', '').strip() or None,
                    difficulty_level=str(row.get('difficulty_level', 'medium')).strip(),
                    created_by_user_id=current_user.id,
                    parent_question_id=parent_id
                )

                if parent_id:
                    max_sub_order = db.session.query(db.func.max(Question.sub_question_order)) \
                        .filter_by(parent_question_id=parent_id).scalar() or 0
                    new_q.sub_question_order = max_sub_order + 1

                db.session.add(new_q)
                db.session.flush()

                options_added = False
                for i in range(1, 10):
                    opt_text = row.get(f'option{i}')
                    if not opt_text:
                        continue

                    is_correct_raw = str(row.get(f'is_correct{i}', '')).strip().lower()
                    is_correct = is_correct_raw in ['1', 'true', 'yes', 'correct']

                    db.session.add(MCQOption(
                        question_id=new_q.id,
                        option_text=str(opt_text).strip(),
                        is_correct=is_correct
                    ))
                    options_added = True

                if not options_added:
                    db.session.rollback()
                    continue
                
                newly_created_questions.append(new_q)
                q_to_add = new_q

            if not q_to_add:
                skipped_duplicates += 1
                continue

            is_already_in_test = MockTestQuestion.query.filter_by(
                mock_test_id=mock_test_id,
                question_id=q_to_add.id
            ).first()

            if is_already_in_test:
                skipped_duplicates += 1
                continue

            db.session.add(MockTestQuestion(
                mock_test_id=mock_test_id,
                question_id=q_to_add.id,
                marks=1.0,
                question_order=max_order + processed_count + 1
            ))
            processed_count += 1

        # === Third Pass: OpenEnded ===
        for row in rows:  # ← Fixed: moved left by 4 spaces
            if row.get('question_type', '').strip() != 'OpenEnded':
                continue

            question_text = str(row.get('question_text', '')).strip()
            if not question_text:
                continue

            topic_id = row.get('topic_id')
            if not topic_id:
                continue

            topic = Topic.query.get(topic_id)
            if not topic or topic.subject.exam_id != mock_test.exam_id:
                continue

            existing_q = Question.query.filter_by(
                topic_id=topic_id,
                question_text=question_text,
                question_type='OpenEnded'
            ).first()

            q_to_add = existing_q

            if not existing_q:
                new_q = Question(
                    topic_id=topic_id,
                    exam_id=mock_test.exam_id,
                    question_type='OpenEnded',
                    question_text=question_text,
                    explanation_text=str(row.get('explanation_text', '')).strip(),
                    difficulty_level=str(row.get('difficulty_level', 'medium')).strip(),
                    image_url=row.get('image_url', '').strip() or None,
                    sample_answer=str(row.get('sample_answer', '')).strip(),
                    created_by_user_id=current_user.id
                )
                db.session.add(new_q)
                db.session.flush()
                newly_created_questions.append(new_q)
                q_to_add = new_q

            if not q_to_add:
                skipped_duplicates += 1
                continue

            is_already_in_test = MockTestQuestion.query.filter_by(
                mock_test_id=mock_test_id,
                question_id=q_to_add.id
            ).first()

            if is_already_in_test:
                skipped_duplicates += 1
                continue

            db.session.add(MockTestQuestion(
                mock_test_id=mock_test_id,
                question_id=q_to_add.id,
                marks=1.0,
                question_order=max_order + processed_count + 1
            ))
            processed_count += 1

        db.session.commit()

        return jsonify({
            "message": f"Import completed: {processed_count} questions imported. {skipped_duplicates} duplicates skipped.",
            "new_questions": [serialize_question(q, include_sub_questions=True) for q in newly_created_questions]
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Import Error: {e}", exc_info=True)
        return jsonify({"message": f"Import failed: {str(e)}"}), 500
        
# --- Organization User Management ---
@main_co_admin_bp.route('/organization/users', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin'])
def get_organization_users(current_user, organization, **kwargs):
    """Fetches all users belonging to the admin's organization."""
    memberships = OrganizationMembership.query.filter_by(organization_id=organization.id).all()
    users_data = []
    for membership in memberships:
        user = membership.user
        if user: # Ensure user exists
            users_data.append({
                'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name,
                'email': user.email, 'user_type': user.user_type,
                'status': 'active' if membership.is_active else 'inactive',
                'joined_at_org': membership.joined_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
    return jsonify(users_data), 200

@main_co_admin_bp.route('/users/check-existence', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin'])
def check_user_existence(current_user, organization, **kwargs):
    data = request.get_json()

    # --- THIS IS THE FIX ---
    # Add the robustness check to handle corrupted JSON strings from the frontend.
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return jsonify({"message": "Invalid data format received."} ), 400
    # --- END OF FIX ---

    email = data.get('email')
    if not email:
        return jsonify({"exists": False, "message": "Email is required."} ), 400
        
    user_exists = User.query.filter_by(email=email).first() is not None
    return jsonify({"exists": user_exists}), 200

@main_co_admin_bp.route('/users/invite', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin'])
def invite_user_to_org(current_user, organization, **kwargs):
    """
    Invites a new or existing user to the organization.

    - Robust against corrupted JSON payloads from the frontend.
    - Enforces plan.max_invited_students (for student invites only).
    - Increments organization.current_invited_student_count when a student membership is created.
    - Uses access_type='internal' to mark invited memberships.
    """
    # --- Robust JSON parsing (handles stringified JSON) ---
    data = request.get_json(silent=True)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return jsonify({"message": "Invalid data format received."} ), 400
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid payload."} ), 400

    # --- Extract inputs ---
    email = (data.get('email') or '').strip().lower()
    user_type = (data.get('user_type') or '').strip().lower()

    if not email or not user_type:
        return jsonify({"message": "Email and User Role are required."} ), 400

    # --- Plan + limit metadata ---
    plan = getattr(organization, 'plan', None)
    max_invited = getattr(plan, 'max_invited_students', None)  # None -> unlimited

    # --- Locate existing user, if any ---
    user = User.query.filter_by(email=email).first()

    # Determine whether this invite counts against the student limit
    # For existing users, use their actual user_type
    is_student_invite = (user.user_type.lower() == 'student') if user else (user_type == 'student')

    # --- Enforce invited-student limit BEFORE creating anything ---
    if is_student_invite and max_invited is not None:
        current = getattr(organization, 'current_invited_student_count', 0) or 0
        if current >= max_invited:
            return jsonify({
                "message": f"You have reached the limit of {max_invited} invited students for your plan."
            }), 403

    if user:
        # User exists globally — add to this org if not already a member
        existing_membership = OrganizationMembership.query.filter_by(
            user_id=user.id,
            organization_id=organization.id
        ).first()
        if existing_membership:
            return jsonify({"message": f"User '{email}' is already a member of your organization."} ), 409

        membership = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            access_type='internal'  # Mark this user as an invited member
        )
        db.session.add(membership)

        # If this invite counts as a student invite, increment the counter
        if is_student_invite and max_invited is not None:
            organization.current_invited_student_count = (
                (getattr(organization, 'current_invited_student_count', 0) or 0) + 1
            )

        db.session.commit()
        return jsonify({"message": f"Existing user '{email}' successfully invited to your organization."} ), 200

    # --- Brand new user path ---
    first_name = (data.get('first_name') or '').strip()
    last_name  = (data.get('last_name') or '').strip()
    password   = data.get('password') or ''

    if not first_name or not last_name or not password:
        return jsonify({
            "message": "First Name, Last Name, and Initial Password are required for new users."
        }), 400

    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        user_type=user_type
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.flush()  # get new_user.id

    membership = OrganizationMembership(
        user_id=new_user.id,
        organization_id=organization.id,
        access_type='internal'  # invited member
    )
    db.session.add(membership)

    # Increment invited-student count if applicable
    if is_student_invite and max_invited is not None:
        organization.current_invited_student_count = (
            (getattr(organization, 'current_invited_student_count', 0) or 0) + 1
        )

    db.session.commit()
    return jsonify({"message": "New user account created and invited successfully."} ), 201

@main_co_admin_bp.route('/organization/users/<int:user_id>/status', methods=['PUT'])
@admin_role_required(allowed_roles=['main_co_admin'])
def update_org_user_status(current_user, organization, user_id, **kwargs):
    # This function is correct and remains unchanged.
    membership = OrganizationMembership.query.filter_by(user_id=user_id, organization_id=organization.id).first_or_404()
    if membership.user.user_type == 'main_co_admin':
        return jsonify({"message": "Cannot change status of the Main Co-Admin."} ), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['active', 'inactive']:
        return jsonify({"message": "Invalid status."} ), 400
    
    membership.is_active = (new_status == 'active')
    db.session.commit()
    return jsonify({"message": "User status within the organization has been updated."} ), 200

@main_co_admin_bp.route('/organization/users/<int:user_id>', methods=['DELETE'])
@admin_role_required(allowed_roles=['main_co_admin'])
def remove_user_from_org(current_user, organization, user_id, **kwargs):

    membership = OrganizationMembership.query.filter_by(
        user_id=user_id,
        organization_id=organization.id
    ).first_or_404()


    if membership.user.user_type == 'main_co_admin':
        return jsonify({"message": "Cannot remove the Main Co-Admin."} ), 403

    if membership.is_active:
        return jsonify({"message": "User must be inactive before they can be removed."} ), 400

    try:
        org_exam_ids = [int(e.id) for e in getattr(organization, 'exams', []) if getattr(e, 'id', None) is not None]

        if org_exam_ids:
            StudentExam.query.filter(
                StudentExam.student_user_id == user_id,
                StudentExam.exam_id.in_(org_exam_ids)
            ).delete(synchronize_session=False)

            mock_test_q = MockTest.query.filter(MockTest.exam_id.in_(org_exam_ids)).with_entities(MockTest.id)
            mock_test_ids = [mt.id for mt in mock_test_q]

            StudentWeeklyProgress.query.filter(
                StudentWeeklyProgress.student_user_id == user_id,
                StudentWeeklyProgress.exam_id.in_(org_exam_ids)
            ).delete(synchronize_session=False)

            if mock_test_ids:
                StudentTestAttempt.query.filter(
                    StudentTestAttempt.student_user_id == user_id,
                    StudentTestAttempt.mock_test_id.in_(mock_test_ids)
                ).delete(synchronize_session=False)

        db.session.delete(membership)
        db.session.commit()

        return jsonify({"message": "User and all their associated data have been permanently removed from the organization."} ), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error removing user %s from organization %s", user_id, organization.id)
        return jsonify({"message": "Failed to remove user. See server logs for details."} ), 500

@main_co_admin_bp.route('/organization/settings', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin'])
def get_organization_settings(current_user, organization, **kwargs):
    """Fetches all general and custom organization settings."""
    
    return jsonify({
        # General settings
        "logo_url": organization.logo_url or "",
        "social_links": organization.social_links or {},
        "contact_email": organization.contact_email or "",
        "footer_text": organization.footer_text or "",

        # Page content
        "about_html": organization.about_html or "",
        "privacy_policy_html": organization.privacy_policy_html or "",
        "tos_html": organization.tos_html or "",

        # FAQ (fallback to default)
        "faq_data": organization.faq_data if organization.faq_data else DEFAULT_FAQ_TEMPLATE,

        # Contact (fallback to default)
        "contact_data": organization.contact_data if organization.contact_data else DEFAULT_CONTACT_TEMPLATE
    }), 200

@main_co_admin_bp.route('/organization/settings', methods=['PUT'])
@admin_role_required(allowed_roles=['main_co_admin'])
def update_organization_settings(current_user, organization, **kwargs):
    """Updates general and custom organization settings with validation + sanitization."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON payload."} ), 400

    # Whitelist of allowed fields
    updatable_fields = {
        "social_links": dict,
        "contact_email": str,
        "footer_text": str,
        "about_html": str,
        "privacy_policy_html": str,
        "tos_html": str,
        "faq_data": list,
        "contact_data": dict
    }

    try:
        # Validate types & sanitize HTML fields
        for field, expected_type in updatable_fields.items():
            if field not in data:
                continue

            value = data[field]
            # type check
            if not isinstance(value, expected_type):
                return jsonify({"message": f"Invalid type for '{field}'. Expected {expected_type.__name__}."} ), 400

            # sanitize HTML content (for CKEditor fields)
            if field in ("about_html", "privacy_policy_html", "tos_html"):
                # sanitize to allowed tags / attributes
                safe_html = bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
                setattr(organization, field, safe_html)
            elif field == "social_links":
                # enforce dict of url strings; small sanity checks
                cleaned_links = {}
                for k, v in value.items():
                    if v is None or v == '':
                        continue
                    if not isinstance(v, str) or len(v) > 200:
                        return jsonify({"message": f"Invalid social link for {k}."} ), 400
                    cleaned_links[k] = v.strip()
                organization.social_links = cleaned_links
            elif field == "faq_data":
                # basic validation of FAQ shape: list of {question, answer, category}
                if len(value) > 200:
                    return jsonify({"message": "Too many FAQ items."} ), 400
                cleaned_faqs = []
                for idx, item in enumerate(value):
                    if not isinstance(item, dict):
                        return jsonify({"message": f"Invalid FAQ item at index {idx}."} ), 400
                    q = item.get('question', '')
                    a = item.get('answer', '')
                    cat = item.get('category', 'General')
                    if not (isinstance(q, str) and isinstance(a, str) and isinstance(cat, str)):
                        return jsonify({"message": f"Invalid FAQ fields at index {idx}."} ), 400
                    if len(q) > 1000 or len(a) > 10000:
                        return jsonify({"message": f"FAQ item too long at index {idx}."} ), 400
                    cleaned_faqs.append({
                        'question': q.strip(),
                        'answer': bleach.clean(a, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True),
                        'category': cat.strip()
                    })
                organization.faq_data = cleaned_faqs
            elif field == "contact_data":
                # Validate expected contact data keys & lengths
                cd = {}
                address = value.get('address', '')
                phone = value.get('phone', '')
                general_email = value.get('general_email', '')
                support_email = value.get('support_email', '')
                if address and not isinstance(address, str):
                    return jsonify({"message": "Invalid contact address."} ), 400
                cd['address'] = address.strip() if address else ''
                cd['phone'] = phone.strip() if phone else ''
                cd['general_email'] = general_email.strip() if general_email else ''
                cd['support_email'] = support_email.strip() if support_email else ''
                organization.contact_data = cd
            else:
                # Simple string fields
                if isinstance(value, str) and len(value) > 10000:
                    return jsonify({"message": f"Field {field} too long."} ), 400
                setattr(organization, field, value)

        db.session.commit()
        return jsonify({"message": "Settings updated successfully."} ), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error updating organization settings")
        return jsonify({"message": "An error occurred while saving settings."} ), 500


@main_co_admin_bp.route('/organization/asset-upload', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin'])
def upload_organization_asset(current_user, organization, **kwargs):
    """Handles secure uploading of organization assets with validation."""
    asset_type = request.form.get('asset_type', '').strip()
    if not asset_type or asset_type not in ALLOWED_ASSET_TYPES:
        return jsonify({"message": "An 'asset_type' is required and must be one of: " + ','.join(sorted(ALLOWED_ASSET_TYPES))}), 400

    if 'asset_file' not in request.files or request.files['asset_file'].filename == '':
        return jsonify({"message": "No file selected."} ), 400

    file = request.files['asset_file']
    filename = secure_filename(file.filename)
    if '.' not in filename:
        return jsonify({"message": "Invalid file."} ), 400

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return jsonify({"message": f"Unsupported file extension: .{ext}"} ), 400

    # Basic size check (request.content_length may be None)
    file.stream.seek(0, os.SEEK_END)
    file_size = file.stream.tell()
    file.stream.seek(0)
    max_size = MAX_UPLOAD_SIZE
    # Example: allow larger login/register images (customize as needed)
    if asset_type in ('login_image', 'register_image'):
        max_size = 5 * 1024 * 1024  # 5 MB for large hero images

    if file_size > max_size:
        return jsonify({"message": f"File too large. Max size is {max_size // (1024*1024)} MB."} ), 400

    # Verify image by reading header with PIL or imghdr
    try:
        # Use PIL to open & verify
        file.stream.seek(0)
        img = Image.open(file.stream)
        img.verify()  # will raise if not an image
        file.stream.seek(0)
    except Exception as e:
        current_app.logger.warning("Uploaded file failed image verification", exc_info=True)
        return jsonify({"message": "Uploaded file is not a valid image."} ), 400

    # Build a deterministic, collision-resistant filename (e.g., orgid-assettype-timestamp.ext)
    import time, uuid
    unique_token = uuid.uuid4().hex[:8]
    final_filename = f"org_{organization.id}_{asset_type}_{int(time.time())}_{unique_token}.{ext}"

    try:
        # delegate actual upload to your S3 helper; ensure helper accepts file.stream or FileStorage
        asset_url = _upload_file_to_s3(file, filename=final_filename, subfolder="org_assets")

        # Update DB field
        if asset_type == 'logo':
            organization.logo_url = asset_url
        elif asset_type == 'favicon':
            organization.favicon_url = asset_url
        elif asset_type == 'login_image':
            organization.login_image_url = asset_url
        elif asset_type == 'register_image':
            organization.register_image_url = asset_url

        db.session.commit()
        return jsonify({"message": f"{asset_type.capitalize()} uploaded successfully.", "url": asset_url}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Asset upload failed")
        return jsonify({"message": "Failed to upload asset."} ), 500

@main_co_admin_bp.route('/test-attempts/<int:attempt_id>/unlock', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin'])
def unlock_student_test_attempt(current_user, organization, attempt_id, **kwargs):
    """Unlock a student test attempt so the student can resume."""
    attempt = StudentTestAttempt.query.get_or_404(attempt_id)

    # ✅ Security check: ensure attempt belongs to the same organization
    if attempt.mock_test.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    # ✅ Unlock logic
    attempt.is_unlocked = True
    attempt.unlocked_at = datetime.utcnow()
    attempt.unlocked_by_admin_id = current_user.id

    # Reset to allow resumption
    attempt.is_locked = False  # keep compatibility if you still use this flag
    attempt.status = 'in_progress'
    attempt.tab_switch_count = 0   # optional reset
    attempt.completed_at = None    # optional reset

    db.session.commit()

    return jsonify({
        "message": "Test unlocked successfully. The student can now resume.",
        "attempt_id": attempt.id,
        "unlocked_at": attempt.unlocked_at.isoformat(),
        "unlocked_by_admin_id": attempt.unlocked_by_admin_id
    }), 200

@main_co_admin_bp.route('/locked-attempts', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin'])
def get_locked_attempts_api(current_user, organization, **kwargs):
    """Fetch all locked student test attempts for the organization."""
    
    locked_attempts = (
        db.session.query(StudentTestAttempt)
        .join(MockTest)
        .join(Exam)
        .filter(
            StudentTestAttempt.status.ilike('locked'),   # case-insensitive
            Exam.organization_id == organization.id      # keep org filter
        )
        .all()
    )

    data = []
    for attempt in locked_attempts:
        student_email = getattr(attempt.student, 'email', 'N/A')
        test_title = getattr(attempt.mock_test, 'title', 'N/A')
        tab_switches = getattr(attempt, 'tab_switch_count', 0)
        data.append({
            "attempt_id": attempt.id,
            "student_email": student_email,
            "test_title": test_title,
            "tab_switches": tab_switches
        })

    return jsonify({"data": data}), 200


def _upload_file_to_s3(
    file,
    subfolder,
    allowed_extensions=None,
    make_public=True,
    max_bytes=None,
    cache_control=None,
    use_sse=True
):
    """
    Uploads a file-like object to S3 with validation and sensible defaults.
    """
    # -------- Configuration --------
    bucket_name = current_app.config['S3_BUCKET']
    aws_region = current_app.config['S3_REGION']
    aws_access_key_id = current_app.config['S3_KEY']
    aws_secret_access_key = current_app.config['S3_SECRET']

    if not all([bucket_name, aws_region, aws_access_key_id, aws_secret_access_key]):
        raise Exception("S3 credentials or configuration are missing from your environment.")

    # -------- Filename & validation --------
    safe_filename = secure_filename(getattr(file, "filename", "upload.bin"))
    if allowed_extensions:
        ext = safe_filename.rsplit(".", 1)[-1].lower() if "." in safe_filename else ""
        if not ext or ext not in allowed_extensions:
            raise Exception(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")

    # -------- File size validation --------
    if max_bytes:
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        if file_length > max_bytes:
            raise Exception(f"File size exceeds the limit of {max_bytes // 1024 // 1024}MB.")
        file.seek(0)

    # -------- Content-Type detection --------
    content_type = getattr(file, "mimetype", None) or "application/octet-stream"

    # -------- Object key --------
    key = f"{subfolder.strip('/')}/{uuid.uuid4().hex}_{safe_filename}"

    # -------- S3 client --------
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )

    # -------- Extra args (ACL removed) --------
    extra_args = {"ContentType": content_type}
    if cache_control:
        extra_args["CacheControl"] = cache_control
    if use_sse:
        extra_args["ServerSideEncryption"] = "AES256"

    # -------- Upload --------
    try:
        s3_client.upload_fileobj(file, bucket_name, key, ExtraArgs=extra_args)
        
        # Standard AWS S3 URL
        url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{quote(key)}"
        
        return { "url": url, "key": key }

    except (NoCredentialsError, ClientError, ParamValidationError) as e:
        # Catch specific Boto3 errors and re-raise them clearly
        raise Exception(f"S3 upload failed: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during upload: {e}")

@main_co_admin_bp.route('/image-upload', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def handle_image_upload(current_user, organization, **kwargs):
    if 'image_file' not in request.files:
        return jsonify({"message": "No file part in the request."} ), 400

    file = request.files['image_file']
    if file.filename == '':
        return jsonify({"message": "No file selected."} ), 400

    try:
        # --- THIS IS THE FIX ---
        # The helper returns a dictionary, so we get the 'url' from it
        upload_result = _upload_file_to_s3(file, subfolder="question-images")
        image_url = upload_result.get("url") # Get the specific URL string
        
        if not image_url:
            raise Exception("S3 helper did not return a URL.")

        # Now, we send back a clean JSON with the correct string value
        return jsonify({"message": "File uploaded successfully!", "image_url": image_url}), 200
        # --- END OF FIX ---
        
    except Exception as e:
        return jsonify({"message": f"Upload failed: {str(e)}"} ), 500
    
@main_co_admin_bp.route('/upload/pdf', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def handle_pdf_upload(current_user, organization, **kwargs):
    """
    Handles uploading a PDF file for topic content to the S3 bucket.
    """
    if 'file' not in request.files: # The JS sends the file with the key 'file'
        return jsonify({"message": "No file part in the request."} ), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected."} ), 400

    try:
        # Use your powerful S3 helper, specifying that only PDFs are allowed
        upload_result = _upload_file_to_s3(
            file,
            subfolder="topic_pdfs",
            allowed_extensions=['pdf']
        )
        
        # Return the URL from the result object
        return jsonify({
            "message": "PDF uploaded successfully!", 
            "url": upload_result.get("url") # Send back the URL
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"PDF upload failed: {e}", exc_info=True)
        return jsonify({"message": f"Upload failed: {str(e)}"} ), 500

@main_co_admin_bp.route('/upload/video', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def handle_video_upload(current_user, organization, **kwargs):
    """
    Handles uploading a video file for topic content to the S3 bucket.
    """
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request."} ), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected."} ), 400

    try:
        upload_result = _upload_file_to_s3(
            file,
            subfolder="topic_videos",
            allowed_extensions=['mp4', 'mov', 'avi', 'wmv', 'webm', 'gif'],
            max_bytes=current_app.config['MAX_VIDEO_UPLOAD_SIZE']
        )
        
        return jsonify({
            "message": "Video uploaded successfully!", 
            "url": upload_result.get("url")
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Video upload failed: {e}", exc_info=True)
        return jsonify({"message": f"Upload failed: {str(e)}"} ), 500

@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def global_content_import(current_user, organization, **kwargs):
    """
    Accepts a CSV or XLSX containing rows with at least:
      - exam_name
      - subject_name
      - topic_name
      - title (optional)
      - content_type (defaults to 'text')
      - content_value
      - display_order (optional; integer)
    and creates TopicContent records under the matching Topic (scoped to organization).
    """
    if 'content_file' not in request.files:
        return jsonify({"message": "No file part in the request."} ), 400

    file = request.files['content_file']
    filename = file.filename or ""
    if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
        return jsonify({"message": "Please upload a valid .csv or .xlsx file."} ), 400

    try:
        # --- Parse to list[dict] with lowercase, trimmed keys ---
        def _normalize_row_keys(row_dict):
            # Lower-case keys and strip surrounding whitespace in both keys and string values
            norm = {}
            for k, v in row_dict.items():
                key = (k or "").strip().lower()
                # Keep None as None; only strip if it's a string
                if isinstance(v, str):
                    norm[key] = v.strip()
                else:
                    norm[key] = v
            return norm

        if filename.endswith('.xlsx'):
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            headers = [((cell.value or "").strip().lower()) for cell in sheet[1]]
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                rows.append(_normalize_row_keys(row_dict))
        else:
            # CSV
            # Important: rewind to ensure we read from start if Werkzeug consumed any bytes for mimetype sniffing
            try:
                file.stream.seek(0)
            except Exception:
                pass
            stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
            csv_reader = csv.DictReader(stream)
            rows = [_normalize_row_keys(r) for r in csv_reader]

        if not rows:
            return jsonify({"message": "No data rows found in the file."} ), 400

        created_count = 0
        skipped_count = 0
        errors = []

        for index, row in enumerate(rows, start=2):  # start=2 to match spreadsheet line numbers
            try:
                exam_name    = (row.get('exam_name') or "").strip()
                subject_name = (row.get('subject_name') or "").strip()
                topic_name   = (row.get('topic_name') or "").strip()

                if not (exam_name and subject_name and topic_name):
                    skipped_count += 1
                    errors.append(f"Row {index}: Missing exam_name/subject_name/topic_name. Skipped.")
                    continue

                content_value = (row.get('content_value') or "")
                if isinstance(content_value, str):
                    content_value = content_value.strip()
                if not content_value:
                    skipped_count += 1
                    errors.append(f"Row {index}: Empty content_value. Skipped.")
                    continue

                title = (row.get('title') or "").strip()
                content_type = (row.get('content_type') or "text").strip().lower()

                # display_order: accept int-like strings; default 0 on failure/blank
                display_order_raw = row.get('display_order')
                try:
                    item_order = int(display_order_raw) if display_order_raw not in (None, "") else 0
                except Exception:
                    item_order = 0

                # Find Topic scoped to this organization
                topic = (
                    db.session.query(Topic)
                    .join(Subject, Topic.subject_id == Subject.id)
                    .join(Exam, Subject.exam_id == Exam.id)
                    .filter(
                        Exam.organization_id == organization.id,
                        Exam.name == exam_name,
                        Subject.name == subject_name,
                        Topic.name == topic_name,
                    )
                    .first()
                )

                if not topic:
                    skipped_count += 1
                    errors.append(
                        f"Row {index}: Topic '{topic_name}' in Subject '{subject_name}' under Exam '{exam_name}' not found. Skipped."
                    )
                    continue

                new_content = TopicContent(
                    topic_id=topic.id,
                    title=title,
                    content_type=content_type,
                    content_value=content_value,
                    item_order=item_order,
                )
                db.session.add(new_content)
                created_count += 1

            except Exception as row_err:
                skipped_count += 1
                errors.append(f"Row {index}: {row_err}. Skipped.")
                # continue to next row

        # Commit all successful rows
        db.session.commit()

        message = f"Import complete. Added: {created_count}, Skipped: {skipped_count}."
        if errors:
            # Keep message concise; you can also return errors as a separate array if your client expects it
            message += " Details: " + " ".join(errors)

        return jsonify({"message": message}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Global content import failed: {e}", exc_info=True)
        return jsonify({"message": f"Import failed: {str(e)}"} ), 500


@main_co_admin_bp.route('/grade-submissions/queue', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_grading_queue(current_user, organization, **kwargs):
    pending_submissions = StudentQuestionResponse.query \
        .join(Question).join(Topic).join(Subject).join(Exam) \
        .filter(
            Exam.organization_id == organization.id,
            StudentQuestionResponse.status == 'pending_review'
        ).all()
    
    data = [{
        "response_id": r.id,
        "student_email": r.attempt.student.email,
        "question_text": r.question.question_text,
        "student_answer": r.response_text
    } for r in pending_submissions]
    
    return jsonify({"data": data})

@main_co_admin_bp.route('/grade-submission/<int:response_id>/ai-grade', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_ai_grade_suggestion(current_user, organization, response_id, **kwargs):
    response = StudentQuestionResponse.query.get_or_404(response_id)
    question = response.question

    prompt = f"""
    Evaluate the following student's answer for this question and sample answer:

    Question: {question.question_text}
    Sample Answer (if provided): {question.sample_answer}
    Student's Answer: {response.response_text}

    Provide concise feedback and a numerical score out of 100.
    Format JSON: {{ "feedback": "...", "score": <number> }}
    """

    try:
        ai_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        content = ai_resp.choices[0].message.content.strip()
        # Try parsing JSON if AI returns structured feedback
        import json
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {"feedback": content, "score": 0}

        return jsonify(data), 200

    except Exception as e:
        current_app.logger.error(f"AI grading failed: {e}")
        return jsonify({"message": "AI grading service failed."} ), 500


@main_co_admin_bp.route('/grade-submission/<int:response_id>/confirm', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def confirm_grade(current_user, organization, response_id, **kwargs):
    data = request.get_json()
    final_score = data.get('score')
    final_feedback = data.get('feedback')

    response = StudentQuestionResponse.query.get_or_404(response_id)
    # ... (security check) ...
    
    # Update the question response
    response.score = final_score
    response.ai_feedback_text = final_feedback
    response.status = 'graded'

    # Recalculate the total test score
    attempt = response.attempt
    all_responses = attempt.responses
    new_total_score = sum(r.score for r in all_responses if r.score is not None)
    attempt.score = new_total_score

    db.session.commit()
    return jsonify({"message": "Grade confirmed and total score updated."} ), 200

@main_co_admin_bp.route('/exams/<int:exam_id>/study-plan', methods=['PUT'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def update_study_plan(current_user, organization, exam_id, **kwargs):
    data = request.get_json()
    plan_name = data.get('name')
    visibility = data.get('visibility', 'internal_only')
    items_data = data.get('items', [])
    
    if not plan_name:
        return jsonify({"success": False, "message": "Study plan name is required."} ), 400
        
    exam = Exam.query.filter_by(id=exam_id, organization_id=organization.id).first_or_404()
    study_plan = StudyPlan.query.filter_by(exam_id=exam_id).first()
    
    if not study_plan:
        study_plan = StudyPlan(exam_id=exam_id, name=plan_name, created_by_user_id=current_user.id, visibility=visibility)
        db.session.add(study_plan)
        db.session.flush()
    else:
        study_plan.name = plan_name
        study_plan.description = data.get('description', study_plan.description)
        study_plan.visibility = visibility
    
    # Delete old items to replace with the new list
    StudyPlanItem.query.filter_by(study_plan_id=study_plan.id).delete()
    db.session.flush()
    
    # Insert the new list of items with the scheduled_date
    for item_data in items_data:
        new_item = StudyPlanItem(
            study_plan_id=study_plan.id,
            scheduled_date=date.fromisoformat(item_data['scheduled_date']), # Use the new date field
            item_type=item_data.get('item_type'),
            description=item_data.get('description'),
            topic_id=item_data.get('topic_id'),
            mock_test_id=item_data.get('mock_test_id')
        )
        db.session.add(new_item)
        
    db.session.commit()
    return jsonify({"success": True, "message": "Study plan saved successfully."} )

@main_co_admin_bp.route('/exams/<int:exam_id>/study-plan', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_study_plan(current_user, organization, exam_id, **kwargs):
    # Ensure the exam belongs to the current org
    exam = Exam.query.filter_by(id=exam_id, organization_id=organization.id).first_or_404()

    study_plan = StudyPlan.query.filter_by(exam_id=exam_id).first()
    if not study_plan:
        # Return empty structure if no plan exists yet
        return jsonify({"name": "", "description": "", "visibility": "internal_only", "items": []}), 200

    # Load items with topic/mock_test for display; order by date then explicit order
    items = (
        StudyPlanItem.query.options(
            joinedload(StudyPlanItem.topic),
            joinedload(StudyPlanItem.mock_test)
        )
        .filter_by(study_plan_id=study_plan.id)
        .order_by(StudyPlanItem.scheduled_date.asc(), StudyPlanItem.order.asc())
        .all()
    )

    serialized_items = []
    for item in items:
        serialized_items.append({
            "id": item.id,
            "scheduled_date": item.scheduled_date.isoformat() if item.scheduled_date else None,  # e.g. "2025-10-25"
            "description": item.description,
            "item_type": item.item_type,
            "topic_id": item.topic_id,
            "topic_name": item.topic.name if item.topic else None,
            "mock_test_id": item.mock_test_id,
            "mock_test_title": item.mock_test.title if item.mock_test else None,
            "estimated_time_minutes": getattr(item, "estimated_time_minutes", None),
            "difficulty_level": getattr(item, "difficulty_level", None),
            "order": getattr(item, "order", None),
            # (Optional: keep legacy day_number if still on the model; remove if dropped)
            # "day_number": getattr(item, "day_number", None),
        })

    return jsonify({
        "name": study_plan.name,
        "description": study_plan.description,
        "visibility": getattr(study_plan, 'visibility', 'internal_only'),
        "items": serialized_items
    }), 200

@main_co_admin_bp.route('/exams/<int:exam_id>/topics', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_topics_for_exam(current_user, organization, exam_id):
    """Fetches all topics belonging to a specific exam for dropdowns."""
    topics = Topic.query.join(Subject).filter(Subject.exam_id == exam_id, Topic.deleted_at.is_(None)).all()
    return jsonify([{"id": t.id, "name": t.name} for t in topics])


@main_co_admin_bp.route('/mock-tests', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_all_mock_tests(current_user, organization, **kwargs):
    """
    Fetches all OFFICIAL mock tests for the organization, excluding
    any practice tests created by students.
    """
    tests = MockTest.query.join(Exam).join(User, MockTest.created_by_user_id == User.id).filter(
        Exam.organization_id == organization.id,
        User.user_type.in_(['main_co_admin', 'co_admin']),
        MockTest.deleted_at == None
    ).order_by(MockTest.created_at.desc()).all()
    # --- END OF FIX ---
    
    return jsonify([serialize_mock_test(test) for test in tests])

@main_co_admin_bp.route('/ckeditor-image-upload', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def ckeditor_image_upload(current_user, organization, **kwargs):
    # CKEditor sends the file in a field named 'upload'
    if 'upload' not in request.files:
        return jsonify({"error": {"message": "No upload file part found."}}), 400

    file = request.files['upload']
    try:
        # Call our central helper function which returns a dict
        upload_result = _upload_file_to_s3(file, subfolder="content_images")
        image_url = upload_result.get("url")

        if not image_url:
            raise Exception("S3 helper did not return a URL.")
        
        # CKEditor expects a specific JSON format: {"url": "http://..."}
        return jsonify({"url": image_url}), 200
    except Exception as e:
        return jsonify({"error": {"message": f"Upload failed: {str(e)}" }}), 500

@main_co_admin_bp.route('/reported-questions', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_reported_questions(current_user, organization, **kwargs):
    """Fetches all pending reported questions for the admin's organization."""
    reports = ReportedContent.query.join(Question).join(Topic).join(Subject).join(Exam).filter(
        Exam.organization_id == organization.id,
        ReportedContent.status == 'pending'
    ).all()
    
    report_data = [{
        "report_id": report.id,
        "question_id": report.question_id,
        "question_text": report.question.question_text,
        "topic_id": report.question.topic_id, # <-- NEW: Added for the edit link
        "topic_name": report.question.topic.name, # <-- NEW: Added for context
        "reason": report.reason.replace('_', ' ').title(),
        "comments": report.comments,
        "reporter_email": report.reporter.email,
        "reported_at": report.reported_at.isoformat()
    } for report in reports]
    
    return jsonify(report_data)


@main_co_admin_bp.route('/reports/<int:report_id>/resolve', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def resolve_reported_question(current_user, organization, report_id, **kwargs):
    """
    Resolves a report by changing its status.
    It NO LONGER archives the question.
    """
    report = ReportedContent.query.get_or_404(report_id)
    if report.question.topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403
    
    report.status = 'resolved'
    # We no longer delete the question here. The admin fixes it manually.
    # report.question.deleted_at = datetime.utcnow() <-- This line is removed
    
    db.session.commit()
    return jsonify({"message": "Report has been marked as resolved."} )

@main_co_admin_bp.route('/reports/<int:report_id>/dismiss', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def dismiss_reported_question(current_user, organization, report_id, **kwargs):
    """Dismisses a report, leaving the question active."""
    try:
        report = ReportedContent.query.get_or_404(report_id)
        if report.question.topic.subject.exam.organization_id != organization.id:
            return jsonify({"message": "Unauthorized"}), 403

        report.status = 'dismissed'
        db.session.commit()
        return jsonify({"message": "Report has been dismissed."} )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred."} ), 500


def _prepare_document(title_text, org_name, exam_name=None, subject_name=None, margin_cm=2.54):
    doc = Document()
    # Set margins (applies to first section)
    section = doc.sections[0]
    section.top_margin = Cm(margin_cm)
    section.bottom_margin = Cm(margin_cm)
    section.left_margin = Cm(margin_cm)
    section.right_margin = Cm(margin_cm)

    # Nice header: org name centered and smaller subtitle
    header_para = doc.add_paragraph()
    header_run = header_para.add_run(org_name or "DIA")
    header_run.bold = True
    header_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    if exam_name or subject_name:
        sub_para = doc.add_paragraph()
        sub_text = " | ".join(filter(None, [exam_name, subject_name]))
        sub_run = sub_para.add_run(sub_text)
        sub_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Horizontal separator
    doc.add_paragraph("-" * 50)
    # Title
    doc.add_heading(title_text, level=1)
    return doc

# helper: safely extract plain text from HTML fragments and insert images when encountered
def _append_html_to_paragraph(document, container_paragraph, html_fragment):
    """
    container_paragraph: a python-docx paragraph object where we will append text.
    html_fragment: BeautifulSoup element or string
    """
    soup = BeautifulSoup(html_fragment, "html.parser")
    for element in soup.contents:
        if getattr(element, "name", None) == "img":
            src = element.get("src")
            if src:
                try:
                    resp = requests.get(src, stream=True, timeout=10)
                    resp.raise_for_status()
                    image_stream = io.BytesIO(resp.content)
                    # Add image as its own paragraph for layout control
                    img_p = document.add_paragraph()
                    img_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    img_run = img_p.add_run()
                    img_run.add_picture(image_stream, width=Inches(4.0))
                except Exception:
                    # fallback: textual note
                    container_paragraph.add_run(f"[Image could not be loaded: {src}]")
        else:
            # normal text nodes
            text = element.get_text() if hasattr(element, "get_text") else str(element)
            container_paragraph.add_run(text)

# helper: format MCQ options with letter labels
def _format_mcq_options(document, options):
    # options: iterable of option objects with .option_text (and possibly .is_correct)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for idx, opt in enumerate(options):
        label = letters[idx] if idx < len(letters) else f"({idx+1})"
        document.add_paragraph(f"{label}. {getattr(opt, 'option_text', '')}", style='List Bullet')

def _add_html_content_to_doc(doc, html_content, s3_client):
    """
    Parses HTML, adds text to the document,
    and downloads images from S3 to embed them.
    """
    if not html_content:
        return
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # We create a new paragraph for this block of content
    current_paragraph = doc.add_paragraph()

    for element in soup.contents:
        if getattr(element, 'name', None) == 'p':
            # Handle paragraphs
            current_paragraph = doc.add_paragraph()
            for child in element.contents:
                _process_html_element(doc, current_paragraph, child, s3_client)
        elif getattr(element, 'name', None) == 'img':
            # Handle images that are not in a <p> tag
            _process_html_element(doc, current_paragraph, element, s3_client)
        else:
            # Handle other tags like <b>, <i>, <span>, or raw text
            _process_html_element(doc, current_paragraph, element, s3_client)

def _process_html_element(doc, paragraph, element, s3_client):
    """
    Recursive helper to process text, formatting tags, and images.
    Handles images from S3 URLs and Base64 data URIs.
    """
    if isinstance(element, str):
        paragraph.add_run(element)
        return

    if element.name == 'img' and element.get('src'):
        image_url = element['src']
        try:
            image_stream = None
            # Case 1: Image is a Base64-encoded Data URI
            if image_url.startswith('data:image'):
                import base64
                # e.g., data:image/png;base64,iVBORw0KGgo...
                header, encoded = image_url.split(',', 1)
                decoded_data = base64.b64decode(encoded)
                image_stream = io.BytesIO(decoded_data)
            
            # Case 2: Image is a full S3 URL
            elif 's3.amazonaws.com' in image_url:
                bucket_name = current_app.config['S3_BUCKET']
                # Ensure bucket_name is valid before splitting
                if bucket_name and f"{bucket_name}.s3.amazonaws.com/" in image_url:
                    object_key = image_url.split(f"{bucket_name}.s3.amazonaws.com/")[1]
                    image_stream = io.BytesIO()
                    s3_client.download_fileobj(bucket_name, object_key, image_stream)
                    image_stream.seek(0)
                else:
                    raise ValueError("S3 bucket name not configured or URL format is unexpected.")

            # Case 3: Image is a general public URL (fallback)
            else:
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()
                image_stream = io.BytesIO(response.content)

            if image_stream:
                paragraph.add_run().add_picture(image_stream, width=Inches(4.0))

        except Exception as e:
            print(f"Error processing image {image_url}: {e}")
            paragraph.add_run(f" [Image not found: {image_url}] ").italic = True

    # Handle formatting tags (bold, italic, etc.)
    elif element.name in ['strong', 'b']:
        run = paragraph.add_run()
        run.bold = True
        for child in element.contents: _process_html_element(doc, run, child, s3_client)
    elif element.name in ['em', 'i']:
        run = paragraph.add_run()
        run.italic = True
        for child in element.contents: _process_html_element(doc, run, child, s3_client)
    
    # Handle other tags or just get their text
    elif element.contents:
        for child in element.contents:
            _process_html_element(doc, paragraph, child, s3_client)
    elif element.string:
        paragraph.add_run(element.string)

# ---------- Topic export route (ZIP) ----------
@main_co_admin_bp.route('/topics/<int:topic_id>/export-zip')
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def export_topic_questions_zip(current_user, organization, topic_id, **kwargs):
    topic = Topic.query.get_or_404(topic_id)
    # authorization
    if topic.subject.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    # --- NEW: Initialize S3 Client ---
    s3_client = boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET'],
        region_name=current_app.config.get('S3_REGION')
    )

    # collect questions (top-level only)
    questions = Question.query.filter_by(
        topic_id=topic_id,
        deleted_at=None,
        parent_question_id=None
    ).order_by(Question.id).all()

    org_name = getattr(organization, "name", None) or "DIA"
    exam_name = getattr(topic.subject, "exam").name if getattr(topic.subject, "exam", None) else None
    subject_name = getattr(topic.subject, "name", None)

    # Prepare two documents
    doc_questions = _prepare_document(f"Practice Test: {topic.name}", org_name, exam_name, subject_name)
    doc_answers = _prepare_document(f"Answers & Explanations: {topic.name}", org_name, exam_name, subject_name)

    q_counter = 1
    for q in questions:
        # QUESTIONS doc (no answers)
        if q.question_type == 'Comprehension':
            p = doc_questions.add_paragraph()
            p.add_run(f"Q{q_counter} (Comprehension): ").bold = True
            _add_html_content_to_doc(doc_questions, q.question_text or "", s3_client)

            if getattr(q, "comprehension_passage", None):
                passage_p = doc_questions.add_paragraph()
                passage_p.add_run("Read the passage below and answer the questions that follow:").italic = True
                _add_html_content_to_doc(doc_questions, q.comprehension_passage.passage_text or "", s3_client)

            if getattr(q, "sub_questions", None):
                for sub_idx, sub_q in enumerate(q.sub_questions):
                    sp = doc_questions.add_paragraph()
                    sp.add_run(f"  Sub-Q {sub_idx + 1}: ").bold = True
                    _add_html_content_to_doc(doc_questions, sub_q.question_text or "", s3_client)
                    if getattr(sub_q, "mcq_options", None):
                        _format_mcq_options(doc_questions, sub_q.mcq_options)

            # ANSWERS doc
            ap = doc_answers.add_paragraph()
            ap.add_run(f"Q{q_counter} (Comprehension): ").bold = True
            _add_html_content_to_doc(doc_answers, q.question_text or "", s3_client)
            if getattr(q, "comprehension_passage", None):
                passage_ap = doc_answers.add_paragraph()
                passage_ap.add_run("Read the passage below and answer the questions that follow:").italic = True
                _add_html_content_to_doc(doc_answers, q.comprehension_passage.passage_text or "", s3_client)

            if getattr(q, "sub_questions", None):
                for sub_idx, sub_q in enumerate(q.sub_questions):
                    subp = doc_answers.add_paragraph()
                    subp.add_run(f"  Sub-Q {sub_idx + 1}: ").bold = True
                    _add_html_content_to_doc(doc_answers, sub_q.question_text or "", s3_client)
                    if getattr(sub_q, "mcq_options", None):
                        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        for idx, opt in enumerate(sub_q.mcq_options):
                            label = letters[idx] if idx < len(letters) else f"({idx+1})"
                            text = getattr(opt, "option_text", "")
                            is_correct = getattr(opt, "is_correct", False) or getattr(opt, "correct", False)
                            opt_para = doc_answers.add_paragraph(f"{label}. {text}", style='List Bullet')
                            if is_correct:
                                opt_para.add_run("  ← Correct").bold = True
                    explanation = getattr(sub_q, "explanation_text", None)
                    if explanation:
                        ex_p = doc_answers.add_paragraph()
                        ex_p.add_run("Explanation: ").italic = True
                        _add_html_content_to_doc(doc_answers, explanation, s3_client)

        else:
            p = doc_questions.add_paragraph()
            p.add_run(f"Q{q_counter}: ").bold = True
            _add_html_content_to_doc(doc_questions, q.question_text or "", s3_client)

            if q.question_type == 'MCQ' and getattr(q, "mcq_options", None):
                _format_mcq_options(doc_questions, q.mcq_options)

            # Answers doc for non-comprehension
            ap = doc_answers.add_paragraph()
            ap.add_run(f"Q{q_counter}: ").bold = True
            _add_html_content_to_doc(doc_answers, q.question_text or "", s3_client)

            if q.question_type == 'MCQ' and getattr(q, "mcq_options", None):
                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                for idx, opt in enumerate(q.mcq_options):
                    label = letters[idx] if idx < len(letters) else f"({idx+1})"
                    text = getattr(opt, "option_text", "")
                    is_correct = getattr(opt, "is_correct", False) or getattr(opt, "correct", False)
                    opt_para = doc_answers.add_paragraph(f"{label}. {text}", style='List Bullet')
                    if is_correct:
                        opt_para.add_run("  ← Correct").bold = True
            
            if q.question_type == 'OpenEnded':
                sample_answer = getattr(q, "sample_answer", None)
                if sample_answer:
                    sa_p = doc_answers.add_paragraph()
                    sa_p.add_run("Sample Answer: ").italic = True
                    _add_html_content_to_doc(doc_answers, sample_answer, s3_client)

            # per-question explanation if present
            explanation = getattr(q, "explanation_text", None)
            if explanation:
                ex_p = doc_answers.add_paragraph()
                ex_p.add_run("Explanation: ").italic = True
                _add_html_content_to_doc(doc_answers, explanation, s3_client)

        # spacing between questions
        doc_questions.add_paragraph()
        doc_answers.add_paragraph()
        q_counter += 1

    # Save both docs to in-memory streams
    q_stream = io.BytesIO()
    a_stream = io.BytesIO()
    doc_questions.save(q_stream)
    doc_answers.save(a_stream)
    q_stream.seek(0)
    a_stream.seek(0)

    # Build zip in-memory
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        safe_topic_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic.name)
        zf.writestr(f"{safe_topic_name}_questions.docx", q_stream.read())
        zf.writestr(f"{safe_topic_name}_answers.docx", a_stream.read())

    zip_stream.seek(0)
    return send_file(
        zip_stream,
        as_attachment=True,
        download_name=f"{safe_topic_name}_Practice_Package.zip",
        mimetype="application/zip"
    )


# ---------- Mock test export route (ZIP) ----------
@main_co_admin_bp.route('/mock-tests/<int:test_id>/export-zip')
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def export_mock_test_zip(current_user, organization, test_id, **kwargs):
    mock_test = MockTest.query.get_or_404(test_id)
    if mock_test.exam.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    # --- NEW: Initialize S3 Client ---
    s3_client = boto3.client(
        's3',
        aws_access_key_id=current_app.config['S3_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET'],
        region_name=current_app.config.get('S3_REGION')
    )

    mock_test_questions = MockTestQuestion.query.filter_by(
        mock_test_id=test_id
    ).order_by(MockTestQuestion.question_order).all()

    org_name = getattr(mock_test.exam.organization, "name", None) or "DIA"
    exam_name = getattr(mock_test.exam, "name", None)
    # if mock_test has subject context use it, otherwise leave None
    subject_name = getattr(mock_test.exam, "name", None)

    doc_questions = _prepare_document(f"Mock Test: {mock_test.title}", org_name, exam_name, subject_name)
    doc_answers = _prepare_document(f"Answers & Explanations: {mock_test.title}", org_name, exam_name, subject_name)

    q_counter = 1
    for mtq in mock_test_questions:
        question = getattr(mtq, "question", None)
        if not question:
            continue

        if question.question_type == 'Comprehension':
            p = doc_questions.add_paragraph()
            p.add_run(f"Q{q_counter} (Comprehension): ").bold = True
            _add_html_content_to_doc(doc_questions, question.question_text or "", s3_client)

            if getattr(question, "comprehension_passage", None):
                passage_p = doc_questions.add_paragraph()
                passage_p.add_run("Read the passage below and answer the questions that follow:").italic = True
                _add_html_content_to_doc(doc_questions, question.comprehension_passage.passage_text or "", s3_client)

            if getattr(question, "sub_questions", None):
                for sub_idx, sub_q in enumerate(question.sub_questions):
                    sp = doc_questions.add_paragraph()
                    sp.add_run(f"  Sub-Q {sub_idx + 1}: ").bold = True
                    _add_html_content_to_doc(doc_questions, sub_q.question_text or "", s3_client)
                    if getattr(sub_q, "mcq_options", None):
                        _format_mcq_options(doc_questions, sub_q.mcq_options)

            # Answers
            ap = doc_answers.add_paragraph()
            ap.add_run(f"Q{q_counter} (Comprehension): ").bold = True
            _add_html_content_to_doc(doc_answers, question.question_text or "", s3_client)
            if getattr(question, "comprehension_passage", None):
                passage_ap = doc_answers.add_paragraph()
                passage_ap.add_run("Read the passage below and answer the questions that follow:").italic = True
                _add_html_content_to_doc(doc_answers, question.comprehension_passage.passage_text or "", s3_client)

            if getattr(question, "sub_questions", None):
                for sub_idx, sub_q in enumerate(question.sub_questions):
                    subp = doc_answers.add_paragraph()
                    subp.add_run(f"  Sub-Q {sub_idx + 1}: ").bold = True
                    _add_html_content_to_doc(doc_answers, sub_q.question_text or "", s3_client)
                    if getattr(sub_q, "mcq_options", None):
                        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        for idx, opt in enumerate(sub_q.mcq_options):
                            label = letters[idx] if idx < len(letters) else f"({idx+1})"
                            text = getattr(opt, "option_text", "")
                            is_correct = getattr(opt, "is_correct", False) or getattr(opt, "correct", False)
                            opt_para = doc_answers.add_paragraph(f"{label}. {text}", style='List Bullet')
                            if is_correct:
                                opt_para.add_run("  ← Correct").bold = True
                    explanation = getattr(sub_q, "explanation", None)
                    if explanation:
                        ex_p = doc_answers.add_paragraph()
                        ex_p.add_run("Explanation: ").italic = True
                        _add_html_content_to_doc(doc_answers, explanation, s3_client)

        else:
            p = doc_questions.add_paragraph()
            p.add_run(f"Q{q_counter}: ").bold = True
            _add_html_content_to_doc(doc_questions, question.question_text or "", s3_client)

            if question.question_type == 'MCQ' and getattr(question, "mcq_options", None):
                _format_mcq_options(doc_questions, question.mcq_options)

            # Answers doc
            ap = doc_answers.add_paragraph()
            ap.add_run(f"Q{q_counter}: ").bold = True
            _add_html_content_to_doc(doc_answers, question.question_text or "", s3_client)

            if question.question_type == 'MCQ' and getattr(question, "mcq_options", None):
                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                for idx, opt in enumerate(question.mcq_options):
                    label = letters[idx] if idx < len(letters) else f"({idx+1})"
                    text = getattr(opt, "option_text", "")
                    is_correct = getattr(opt, "is_correct", False) or getattr(opt, "correct", False)
                    opt_para = doc_answers.add_paragraph(f"{label}. {text}", style='List Bullet')
                    if is_correct:
                        opt_para.add_run("  ← Correct").bold = True
            
            if question.question_type == 'OpenEnded':
                sample_answer = getattr(question, "sample_answer", None)
                if sample_answer:
                    sa_p = doc_answers.add_paragraph()
                    sa_p.add_run("Sample Answer: ").italic = True
                    _add_html_content_to_doc(doc_answers, sample_answer, s3_client)

            explanation = getattr(question, "explanation_text", None)
            if explanation:
                ex_p = doc_answers.add_paragraph()
                ex_p.add_run("Explanation: ").italic = True
                _add_html_content_to_doc(doc_answers, explanation, s3_client)

        # spacing between questions
        doc_questions.add_paragraph()
        doc_answers.add_paragraph()
        q_counter += 1

    # Save docs to streams
    q_stream = io.BytesIO()
    a_stream = io.BytesIO()
    doc_questions.save(q_stream)
    doc_answers.save(a_stream)
    q_stream.seek(0)
    a_stream.seek(0)

    # Build zip
    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in mock_test.title)
        zf.writestr(f"{safe_title}_questions.docx", q_stream.read())
        zf.writestr(f"{safe_title}_answers.docx", a_stream.read())

    zip_stream.seek(0)
    return send_file(
        zip_stream,
        as_attachment=True,
        download_name=f"{safe_title}_Practice_Package.zip",
        mimetype="application/zip"
    )

@main_co_admin_bp.route('/all-topics', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_all_topics_for_org(current_user, organization, **kwargs):
    """Fetches a flat list of all topics in the organization for dropdowns."""
    try:
        # --- THIS IS THE CORRECTED QUERY ---
        # We now explicitly define the join path: Topic -> Subject -> Exam
        topics = (
            db.session.query(
                Topic.id,
                Topic.name,
                Subject.name,
                Exam.name
            )
            .join(Subject, Topic.subject_id == Subject.id)
            .join(Exam, Subject.exam_id == Exam.id)
            .filter(
                Exam.organization_id == organization.id,
                Topic.deleted_at.is_(None)
            )
            .order_by(Exam.name, Subject.name, Topic.name)
            .all()
        )
        # --- END OF CORRECTION ---

        topic_list = [
            {
                "id": t[0],
                "name": t[1],
                "subject_name": t[2],
                "exam_name": t[3]
            }
            for t in topics
        ]
        
        return jsonify(topic_list)

    except Exception as e:
        current_app.logger.error(f"Error fetching all topics for org: {e}")
        return jsonify({"message": "Could not retrieve topic list."}), 500

@main_co_admin_bp.route('/notifications/send', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin']) # Allow both admin types
def send_custom_notification(current_user, organization, **kwargs):
    """
    Sends a custom notification message from an admin to all active 
    students in their organization.
    """
    data = request.get_json()
    title = data.get('title')
    message = data.get('message')

    if not title or not message:
        return jsonify({"message": "A title and message are required."} ), 400

    try:
        # Find all active student members of the current admin's organization
        student_memberships = OrganizationMembership.query.join(User).filter(
            OrganizationMembership.organization_id == organization.id,
            OrganizationMembership.is_active == True,
            User.user_type == 'student'
        ).all()

        if not student_memberships:
            return jsonify({"message": "There are no active students in your organization to notify."} ), 400

        # Create a notification for each student
        for membership in student_memberships:
            notification = Notification(
                organization_id=organization.id,
                user_id=membership.user_id,
                notification_type='announcement', # A new type for custom messages
                title=title,
                message=message
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({"message": f"Announcement sent to {len(student_memberships)} students."} ), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending custom notification: {e}")
        return jsonify({"message": "An error occurred while sending the notification."} ), 500

def _generate_performance_graph(topic_performance_data):
    """Generates a bar chart of topic performance and returns it as an in-memory image."""
    if not topic_performance_data:
        return None

    topics = [item['topic_name'] for item in topic_performance_data]
    accuracies = [item['average_accuracy'] for item in topic_performance_data]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(topics, accuracies, color='skyblue')
    ax.set_xlabel('Average Accuracy (%)')
    ax.set_title('Performance by Topic')
    ax.set_xlim(0, 100)

    # Add labels to the bars
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width + 1
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2., f'{width:.1f}%', va='center')

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close(fig)
    return img_buffer

def _create_report_pdf(report_data, graph_image_buffer):
    """Creates a PDF report from the given data and graph."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"Mock Test Report: {report_data['mock_test_title']}", styles['h1']))
    story.append(Spacer(1, 0.2*inch))

    # Summary Stats
    story.append(Paragraph("Overall Performance Summary", styles['h2']))
    summary_text = (
        f"<b>Total Attempts:</b> {report_data['total_attempts']}<br/>"
        f"<b>Average Score:</b> {report_data['average_score']:.2f}%<br/>"
        f"<b>Pass Rate:</b> {report_data['pass_rate']:.2f}%"
    )
    story.append(Paragraph(summary_text, styles['body']))
    story.append(Spacer(1, 0.2*inch))

    # Graph
    if graph_image_buffer:
        story.append(Paragraph("Topic Performance Graph", styles['h2']))
        graph_img = ReportLabImage(graph_image_buffer, width=6*inch, height=4*inch)
        story.append(graph_img)
        story.append(Spacer(1, 0.2*inch))

    # Topic Performance Table
    story.append(Paragraph("Detailed Topic Performance", styles['h2']))
    table_data = [['Topic', 'Avg. Accuracy (%)', 'Questions', 'Students']]
    for item in report_data['topic_performance']:
        table_data.append([
            item['topic_name'],
            f"{item['average_accuracy']:.2f}",
            item['question_count'],
            item['student_count']
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer

@main_co_admin_bp.route('/mock-tests/<int:test_id>/export-pdf-report', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def export_mock_test_pdf_report(current_user, organization, test_id, **kwargs):
    """Generates and downloads a PDF performance report for a mock test."""
    test = (MockTest.query
        .join(Exam, MockTest.exam_id == Exam.id)
        .filter(MockTest.id == test_id, Exam.organization_id == organization.id)
        .first_or_404())

    report = MockTestReport.query.filter_by(mock_test_id=test.id).first()

    if not report:
        return jsonify({"message": "Report not found for this mock test. Please generate it first."} ), 404

    topic_summaries = TopicPerformanceSummary.query.filter_by(report_id=report.id).order_by(TopicPerformanceSummary.average_accuracy.asc()).all()

    serialized_summaries = [{
        "topic_name": s.topic_name,
        "average_accuracy": s.average_accuracy,
        "question_count": s.question_count,
        "student_count": s.student_count
    } for s in topic_summaries]

    report_data = {
        "mock_test_title": test.title,
        "total_attempts": report.total_attempts,
        "average_score": report.average_score,
        "pass_rate": report.pass_rate,
        "topic_performance": serialized_summaries,
    }

    try:
        # Generate graph
        graph_buffer = _generate_performance_graph(report_data['topic_performance'])

        # Generate PDF
        pdf_buffer = _create_report_pdf(report_data, graph_buffer)

        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in test.title)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{safe_title}_Performance_Report.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f"Failed to generate PDF report for mock test {test_id}: {e}", exc_info=True)
        return jsonify({"message": "An error occurred while generating the PDF report."} ), 500


# --- ASSIGNMENT MANAGEMENT ---

@main_co_admin_bp.route('/assignments', methods=['GET', 'POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def manage_assignments(current_user, organization, **kwargs):
    if request.method == 'GET':
        assignments = Assignment.query.filter_by(organization_id=organization.id).order_by(Assignment.due_date.desc()).all()
        result = []
        for a in assignments:
            submissions_count = AssignmentSubmission.query.filter_by(assignment_id=a.id).count()
            graded_count = AssignmentSubmission.query.filter_by(assignment_id=a.id, status='graded').count()
            result.append({
                'id': a.id,
                'title': a.title,
                'description': a.description,
                'due_date': a.due_date.isoformat() if a.due_date else None,
                'max_marks': str(a.max_marks),
                'attachment_url': a.attachment_url,
                'submissions_count': submissions_count,
                'graded_count': graded_count
            })
        return jsonify(result), 200

    if request.method == 'POST':
        # Handle both multipart form data (with file) and json
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            data = request.form
            file = request.files.get('file')
        else:
            data = request.get_json()
            file = None
            
        try:
            attachment_url = None
            if file and file.filename != '':
                upload_result = _upload_file_to_s3(file, subfolder="assignment_attachments")
                attachment_url = upload_result.get("url")

            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            new_assignment = Assignment(
                organization_id=organization.id,
                title=data['title'],
                description=data.get('description'),
                due_date=due_date.replace(tzinfo=None),
                max_marks=float(data.get('max_marks', 100)),
                attachment_url=attachment_url,
                created_by_user_id=current_user.id
            )
            db.session.add(new_assignment)
            db.session.commit()
            return jsonify({"message": "Assignment created successfully!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating assignment: {str(e)}"}), 500

@main_co_admin_bp.route('/assignments/<int:assignment_id>/submissions', methods=['GET'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def get_assignment_submissions(current_user, organization, assignment_id, **kwargs):
    assignment = Assignment.query.filter_by(id=assignment_id, organization_id=organization.id).first_or_404()
    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).all()
    
    data = [{
        "id": sub.id,
        "student_email": User.query.get(sub.student_user_id).email,
        "student_name": f"{User.query.get(sub.student_user_id).first_name} {User.query.get(sub.student_user_id).last_name}",
        "submission_text": sub.submission_text,
        "file_url": sub.file_url,
        "status": sub.status,
        "marks_awarded": str(sub.marks_awarded) if sub.marks_awarded is not None else None,
        "feedback": sub.feedback,
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
    } for sub in submissions]
    
    return jsonify({"assignment_title": assignment.title, "max_marks": str(assignment.max_marks), "data": data}), 200

@main_co_admin_bp.route('/assignments/submissions/<int:submission_id>/grade', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def grade_assignment_submission(current_user, organization, submission_id, **kwargs):
    data = request.get_json()
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    
    # Authorization check
    if submission.assignment.organization_id != organization.id:
        return jsonify({"message": "Unauthorized"}), 403

    try:
        submission.marks_awarded = float(data['marks'])
        submission.feedback = data.get('feedback', '')
        submission.status = 'graded'
        submission.graded_at = datetime.utcnow()
        submission.graded_by_admin_id = current_user.id
        
        db.session.commit()
        return jsonify({"message": "Grade submitted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to grade: {str(e)}"}), 500
