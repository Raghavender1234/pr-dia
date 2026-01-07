# backend/app/api/student.py
from flask import Blueprint, request, jsonify, current_app, g, url_for
from app import db
from app.models.user import User
import razorpay
from app.models.organization import OrganizationMembership, Organization, OrganizationReport
from app.models.exam import Exam, StudyPlan, StudyPlanItem, StudentStudyPlanProgress
from random import sample
from app.models.subject import Subject
from app.models.topic import Topic, TopicContent
from app.models.question import Question, MCQOption, ComprehensionPassage
from app.models.student_progress import StudentReviewedQuestion
from app.models.mock_test import MockTest, MockTestQuestion # Will be used for mock test logic
from app.models.student_progress import StudentExam, StudentTestAttempt, StudentQuestionResponse, StudentReviewedQuestion, StudentAISubscription, StudentTopicPractice
from collections import defaultdict
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime, timedelta, date, timezone 
from sqlalchemy import func, and_
from .decorators import student_required
from sqlalchemy.orm import joinedload, selectinload, subqueryload
import traceback
from app.utils.ai_evaluator import evaluate_open_ended_question
import random
from app.models.question import ReportedContent
from app.utils.localization import get_country_code, format_price
from collections import defaultdict
import statistics
from app.api.decorators import premium_feature_required
from app.api.ai_progress import ensure_weekly_snapshot as _ensure_weekly_snapshot
from app.api.ai_progress import recent_week_summaries as _recent_week_summaries



student_api_bp = Blueprint('student_api', __name__, url_prefix='/api/student')

# Helper functions for serialization (might need to be refined for student view)
def serialize_exam_for_student(exam):
    """ Correctly counts only active (not soft-deleted) subjects. """
    return {
        'id': exam.id,
        'name': exam.name,
        'description': exam.description,
        # FIX: Use a database query to count only non-deleted subjects.
        'subjects_count': exam.subjects.filter_by(deleted_at=None).count()
    }

def serialize_subject_for_student(subject):
    """ Correctly counts only active (not soft-deleted) topics. """
    return {
        'id': subject.id,
        'exam_id': subject.exam_id,
        'name': subject.name,
        'description': subject.description,
        # FIX: Use a database query to count only non-deleted topics.   
        'topics_count': Topic.query.filter_by(subject_id=subject.id, deleted_at=None).count()
    }

def serialize_recent_attempt(attempt):
    """Serializer for a student's recent test attempt."""
    return {
        "attempt_id": attempt.id,
        "test_title": attempt.mock_test.title if attempt.mock_test else "N/A",
        "exam_name": attempt.mock_test.exam.name if attempt.mock_test and attempt.mock_test.exam else "N/A",
        "completed_at": attempt.completed_at.strftime('%d %b %Y') if attempt.completed_at else "In Progress",
        "score": str(attempt.score) if attempt.score is not None else "N/A",
        "total_marks": str(attempt.total_possible_score) if attempt.total_possible_score is not None else "N/A",
        "result_url": url_for('frontend.student_mock_test_result', attempt_id=attempt.id)
    }

def serialize_student_membership(membership):
    """Serializer for a student's organization membership."""
    if not membership.organization:
        return None
    return {
        "org_name": membership.organization.name,
        "org_logo_url": membership.organization.logo_url or url_for('static', filename='images/default-org-logo.png'),
        "org_dashboard_url": url_for('frontend.student_dashboard', org=membership.organization.subdomain)
    }


@student_api_bp.route('/exams/<int:exam_id>/subjects', methods=['GET'])
@student_required()
def get_subjects_for_exam(current_user, exam_id, **kwargs):
    """
    Fetches subjects for an exam, but only if the student has both an active
    enrollment for the exam AND an active membership in the organization.
    """
    exam = Exam.query.get_or_404(exam_id)

    enrollment_record = StudentExam.query.filter(
        StudentExam.student_user_id == current_user.id,
        StudentExam.exam_id == exam_id,
        StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted'])
    ).first()

    if not enrollment_record:
        return jsonify({"message": "You are not enrolled in this exam."}), 403

    # --- ✅ CHECK 2 (THE FIX): Is the student's membership in the org active? ---
    membership_record = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=exam.organization_id,
        is_active=True  # This is the crucial check
    ).first()

    if not membership_record:
        return jsonify({"message": "Your access to this organization's content has been disabled by an administrator."}), 403

    # --- If both checks pass, proceed ---
    subjects = Subject.query.filter_by(exam_id=exam_id, deleted_at=None).all()
    return jsonify([serialize_subject_for_student(subject) for subject in subjects]), 200

def serialize_topic_for_student(topic, student_id):
    """
    Serialize a topic for a student, including:
    - Total number of questions (only parent questions)
    - Only counts public questions or questions created by this student
    - Number of correctly answered questions by the student
    """
    # Count only parent questions that are either public or created by this student
    total_questions = Question.query.filter(
        Question.topic_id == topic.id,
        Question.parent_question_id == None,
        Question.deleted_at == None,
        ((Question.visibility == 'public') | (Question.created_by_user_id == student_id))
    ).count()

    # Count how many questions the student answered correctly
    correctly_answered_count = db.session.query(func.count(StudentQuestionResponse.id)) \
        .join(StudentTestAttempt, StudentQuestionResponse.attempt_id == StudentTestAttempt.id) \
        .join(Question, StudentQuestionResponse.question_id == Question.id) \
        .filter(
            StudentTestAttempt.student_user_id == student_id,
            Question.topic_id == topic.id,
            StudentQuestionResponse.is_correct == True
        ).scalar()

    return {
        'id': topic.id,
        'subject_id': topic.subject_id,
        'name': topic.name,
        'description': topic.description,
        'questions_count': total_questions,
        'questions_correct_count': correctly_answered_count or 0
    }

def serialize_mcq_option_for_student(option):
    # IMPORTANT: We DO NOT send the 'is_correct' field to the student before they answer.
    return {
        'id': option.id,
        'option_text': option.option_text,
    }

def serialize_comprehension_passage_for_student(passage):
    if not passage:
        return None
    return {
        'id': passage.id,
        'passage_text': passage.passage_text
    }

def serialize_question_for_student(question, reviewed_ids=None):
    if reviewed_ids is None:
        reviewed_ids = set()

    question_data = {
        'id': question.id,
        'topic_id': question.topic_id,
        'question_type': question.question_type,
        'question_text': question.question_text,
        'is_marked_for_review': question.id in reviewed_ids
    }

    # --- MCQ ---
    if question.question_type == 'MCQ':
        question_data['mcq_options'] = [
            {
                'id': opt.id,
                'option_text': opt.option_text
            }
            for opt in question.mcq_options
        ]

    # --- Comprehension ---
    elif question.question_type == 'Comprehension':
        passage = question.comprehension_passage
        question_data['comprehension_passage'] = {
            'passage_text': passage.passage_text if passage else ''
        }
        question_data['sub_questions'] = [
            serialize_question_for_student(subq, reviewed_ids) for subq in question.sub_questions
        ]

    # --- Open-Ended ---
    elif question.question_type == 'OpenEnded':
        question_data['sample_answer'] = question.sample_answer or ""
        question_data['response_type'] = 'text'  # Could be 'essay', 'code', etc.

    return question_data

@student_api_bp.route('/questions/<int:question_id>/toggle-review', methods=['POST'])
@student_required()
def toggle_review_status(current_user, question_id, **kwargs):
    # Check if the entry already exists
    review_entry = StudentReviewedQuestion.query.filter_by(
        # ✅ CORRECTED: Use the correct column name 'student_user_id'
        student_user_id=current_user.id,
        question_id=question_id
    ).first()

    try:
        if review_entry:
            # It exists, so we unmark it by deleting the record
            db.session.delete(review_entry)
            db.session.commit()
            return jsonify({"message": "Question unmarked for review.", "marked": False}), 200
        else:
            # It does not exist, so we mark it by creating a new entry
            new_review_entry = StudentReviewedQuestion(
                student_user_id=current_user.id,
                question_id=question_id
            )
            db.session.add(new_review_entry)
            db.session.commit()
            return jsonify({"message": "Question marked for review.", "marked": True}), 200
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling review status: {e}")
        return jsonify({"message": "An error occurred."}), 500

def serialize_reviewed_question(question):
    return {
        'id': question.id,
        'topic_id': question.topic_id,
        'question_text': question.question_text,
        'question_type': question.question_type,
        'topic_name': question.topic.name if question.topic else 'N/A',
        'subject_name': question.topic.subject.name if question.topic and question.topic.subject else 'N/A'
    }

def serialize_question_with_answer_details(question):
    """
    Serializes a question and includes all details necessary for showing
    feedback to a student AFTER they have answered (including the correct answers).
    """
    question_data = {
        'id': question.id,
        'question_type': question.question_type,
        'question_text': question.question_text,
        'explanation_text': question.explanation_text,
        'sample_answer': question.sample_answer,
        'difficulty_level': question.difficulty_level,
    }

    if question.question_type == 'MCQ':
        options_data = []
        for opt in question.mcq_options:
            options_data.append({
                'id': opt.id,
                'option_text': opt.option_text,
                'is_correct': opt.is_correct, # Include correct answer for evaluation
            })
        question_data['mcq_options'] = options_data
    
    # --- THIS IS THE CORRECTED LOGIC ---
    # This block was mistakenly removed and is now restored.
    elif question.question_type == 'Comprehension':
        question_data['comprehension_passage'] = serialize_comprehension_passage_for_student(question.comprehension_passage)
        # We also need to serialize the sub-questions with their answers for feedback
        if hasattr(question, 'sub_questions'):
            question_data['sub_questions'] = [serialize_question_with_answer_details(sq) for sq in question.sub_questions]
    # --- END OF FIX ---

    return question_data

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

def serialize_mock_test_for_student(mock_test):
    """
    Serialize a MockTest object with proper timezone handling.
    """
    data = {
        'id': mock_test.id,
        'title': mock_test.title,
        'description': mock_test.description,
        'duration_minutes': mock_test.duration_minutes,
        'passing_marks': mock_test.passing_marks,
        'total_marks': mock_test.total_marks,
        'question_count': len(mock_test.mock_test_questions) if mock_test.mock_test_questions else 0,
        'status': mock_test.status,
        'is_live_test': getattr(mock_test, 'is_live_test', False),
    }
    
    # Handle live test times with proper UTC conversion
    if hasattr(mock_test, 'live_start_time') and mock_test.live_start_time:
        start_utc = ensure_utc_aware(mock_test.live_start_time)
        data['live_start_time'] = start_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    if hasattr(mock_test, 'live_end_time') and mock_test.live_end_time:
        end_utc = ensure_utc_aware(mock_test.live_end_time)
        data['live_end_time'] = end_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    return data

@student_api_bp.route('/profile', methods=['GET'])
@student_required()
def get_student_profile(current_user_id, organization_id): # organization_id is passed by decorator but not used directly here
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }), 200

@student_api_bp.route('/profile', methods=['PUT'])
@jwt_required()
@student_required()
def update_student_profile(current_user_id, organization_id):
    data = request.get_json()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Allow updating first_name and last_name
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    
    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating profile: {str(e)}"}), 500

def _serialize_recent_attempt(attempt):
    """
    ✅ HARDENED: Safely formats a recent test attempt, checking for missing data.
    """
    # Default values
    test_title = "N/A"
    exam_name = "N/A"
    result_url = "#"
    total_questions = 0
    correct_answers = 0

    if attempt.mock_test:
        test_title = attempt.mock_test.title
        if attempt.mock_test.exam:
            exam_name = attempt.mock_test.exam.name
    
    if attempt.id:
        result_url = url_for('frontend.student_mock_test_result', attempt_id=attempt.id, _external=True)

    # Calculate correct answers for this specific attempt
    responses = attempt.responses # Uses the relationship
    if responses:
        total_questions = len(responses)
        correct_answers = sum(1 for r in responses if r.is_correct)

    return {
        "attempt_id": attempt.id,
        "test_title": test_title,
        "exam_name": exam_name,
        "completed_at": attempt.completed_at.strftime('%d %b %Y, %I:%M %p') if attempt.completed_at else "In Progress",
        "score": str(attempt.score) if attempt.score is not None else "N/A",
        "total_marks": str(attempt.total_possible_score) if attempt.total_possible_score is not None else "N/A",
        "result_url": result_url,
        "total_questions": total_questions,
        "correct_answers": correct_answers
    }

def _serialize_student_membership(membership):
    """
    ✅ HARDENED: Safely formats an organization membership.
    """
    if not membership or not membership.organization:
        return None
    
    return {
        "organization_name": membership.organization.name,
        "role": "Member", # You can enhance this later if needed
        "org_dashboard_url": url_for('frontend.student_dashboard', org=membership.organization.subdomain, _external=True)
    }

@student_api_bp.route('/dashboard-summary', methods=['GET'])
@student_required()
def get_dashboard_summary(current_user, **kwargs):
    """
    Provides all necessary data for the student's main, global dashboard,
    ensuring the my_exams list is correctly populated.
    """
    try:
        user_id = current_user.id

        # ✅ Get all active enrollments for the student
        active_enrollments = StudentExam.query.filter(
            StudentExam.student_user_id == user_id,
            StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted'])
        ).options(
            joinedload(StudentExam.exam) # Eager load the exam to prevent extra queries
        ).all()
        
        # ✅ Create the my_exams list from these enrollments
        my_exams_data = [
            {"id": se.exam.id, "name": se.exam.name}
            for se in active_enrollments if se.exam
        ]

        # --- Other stats remain the same ---
        all_responses = db.session.query(StudentQuestionResponse).join(StudentTestAttempt).filter(StudentTestAttempt.student_user_id == user_id).all()
        total_answered = len(all_responses)
        correct_count = sum(1 for r in all_responses if r.is_correct)
        incorrect_count = total_answered - correct_count
        overall_accuracy = round((correct_count / total_answered) * 100) if total_answered > 0 else 0
        
        tests_completed_count = StudentTestAttempt.query.filter_by(student_user_id=user_id, status='completed').count()
        reviewed_questions_count = StudentReviewedQuestion.query.filter_by(student_user_id=user_id).count()
        
        recent_attempts = StudentTestAttempt.query.filter_by(student_user_id=user_id, status='completed')\
            .order_by(StudentTestAttempt.completed_at.desc()).limit(5).all()

        memberships = OrganizationMembership.query.filter_by(user_id=user_id, is_active=True).all()
        
        dashboard_data = {
            "student_name": current_user.first_name,
            "exams_enrolled_count": len(my_exams_data), # Count from our query
            "tests_completed_count": tests_completed_count,
            "overall_accuracy": overall_accuracy,
            "review_count": reviewed_questions_count,
            "membership_count": len(memberships),
            "my_exams": my_exams_data, # ✅ Pass the list to the frontend
            "correct_questions_count": correct_count,
            "incorrect_questions_count": incorrect_count,
            "recent_activity": [_serialize_recent_attempt(att) for att in recent_attempts], # Assumes you have this helper
            "memberships": [_serialize_student_membership(mem) for mem in memberships] # Assumes you have this helper
        }
        
        return jsonify(dashboard_data), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching global student dashboard: {e}", exc_info=True)
        return jsonify({"message": "Could not load dashboard data."}), 500

@student_api_bp.route('/subjects/<int:subject_id>/topics', methods=['GET'])
@student_required()
def get_topics_for_student(current_user, subject_id, **kwargs):
    subject = Subject.query.get_or_404(subject_id)
    
    # ✅ THE FIX: Check for active membership in this subject's specific organization
    membership = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=subject.exam.organization_id,
        is_active=True
    ).first()

    if not membership:
        return jsonify({"message": "Your access to this organization's content is disabled."}), 403

    # If the check passes, get the topics
    topics = Topic.query.filter_by(subject_id=subject_id, deleted_at=None).order_by(Topic.name).all()
    return jsonify([serialize_topic_for_student(topic, current_user.id) for topic in topics]), 200

@student_api_bp.route('/topics/<int:topic_id>/questions', methods=['GET'])
@student_required()
def get_questions_for_topic_practice(current_user, topic_id, **kwargs):
    """
    Intelligently fetches practice questions for a topic.
    - Excludes questions the student has already answered correctly.
    - Respects question visibility (public vs private).
    - Shuffles the remaining questions.
    - If all questions are mastered, it resets and serves them all again.
    """
    try:
        import random

        topic = Topic.query.get_or_404(topic_id)
        org_membership = OrganizationMembership.query.filter_by(
            user_id=current_user.id,
            is_active=True,
            organization_id=topic.subject.exam.organization_id
        ).first()

        if not org_membership:
            return jsonify({"message": "You do not have access to this topic."}), 403

        all_question_ids_query = db.session.query(Question.id).filter_by(
            topic_id=topic_id, deleted_at=None, parent_question_id=None
        )
        all_question_ids = {q[0] for q in all_question_ids_query.all()}

        if not all_question_ids:
            return jsonify([]), 200

        progress = StudentTopicPractice.query.filter_by(
            student_user_id=current_user.id,
            topic_id=topic_id
        ).first()

        correctly_answered_ids = set(progress.correctly_answered_ids) if progress else set()
        unseen_question_ids = list(all_question_ids - correctly_answered_ids)

        if not unseen_question_ids:
            unseen_question_ids = list(all_question_ids)

        random.shuffle(unseen_question_ids)

        questions_to_serve = Question.query.filter(
            Question.id.in_(unseen_question_ids),
            (Question.visibility == 'public') |
            ((Question.visibility == 'private') & (Question.created_by_user_id == current_user.id))
        ).all()

        # Maintain shuffled order
        questions_map = {q.id: q for q in questions_to_serve}
        sorted_questions = [questions_map[id] for id in unseen_question_ids if id in questions_map]

        return jsonify([serialize_question_for_student(q) for q in sorted_questions]), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching practice questions: {e}", exc_info=True)
        return jsonify({"message": "Could not load questions."}), 500

@student_api_bp.route('/mock-tests', methods=['GET'])
@student_required()
def get_available_mock_tests(current_user, **kwargs):
    """
    Fetch active mock tests for exams the student is actively ENROLLED in,
    filtered by organization if an org_id is provided.
    Adds per-test attempt/lock/grading details.
    """
    try:
        org_id = request.args.get('org_id', type=int)

        # Exams this student can access
        enrolled_exam_ids = {
            se.exam_id
            for se in StudentExam.query.filter(
                StudentExam.student_user_id == current_user.id,
                StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted']),
            ).all()
        }

        if not enrolled_exam_ids:
            return jsonify([]), 200

        # Base query for available mock tests
        query = MockTest.query.filter(
            MockTest.status == 'active',
            MockTest.deleted_at.is_(None),
            MockTest.exam_id.in_(enrolled_exam_ids),
        )

        if org_id:
            query = query.join(Exam).filter(Exam.organization_id == org_id)

        mock_tests = query.all()

        output = []
        for mt in mock_tests:
            # Your existing serializer for core test data
            test_data = serialize_mock_test_for_student(mt)
            has_open_ended = any(
                getattr(q, "question_type", None) == "OpenEnded" for q in getattr(mt, "questions", [])
            )

            # Most recent attempt by this student for this test
            attempt = (
                StudentTestAttempt.query.filter_by(
                    student_user_id=current_user.id,
                    mock_test_id=mt.id,
                )
                .order_by(StudentTestAttempt.start_time.desc())
                .first()
            )

            has_attempt = attempt is not None
            last_attempt_id = attempt.id if attempt else None

            # Default derived fields
            student_attempt_status = 'not_started'
            is_locked = False
            grading_status = 'completed'  # default if no open-ended or nothing pending

            if attempt:
                # Preserve your "live test time-up" logic
                if (
                    getattr(mt, "is_live_test", False)
                    and getattr(mt, "live_end_time", None)
                    and datetime.utcnow() > mt.live_end_time
                    and attempt.status == 'in_progress'
                ):
                    student_attempt_status = 'time_up'
                else:
                    student_attempt_status = attempt.status

                # Lock/unlock status (works with your new is_unlocked flag)
                # If you already have attempt.is_locked, keep honoring it.
                is_locked = bool(getattr(attempt, "is_locked", False) and not getattr(attempt, "is_unlocked", False))

                # Grading status: only relevant after completion & when open-ended exists
                if attempt.status == 'completed' and has_open_ended:
                    pending_count = (
                        StudentQuestionResponse.query.join(Question, Question.id == StudentQuestionResponse.question_id)
                        .filter(
                            StudentQuestionResponse.attempt_id == attempt.id,
                            Question.question_type == 'OpenEnded',
                            # 'pending' is the value we populated in the migration default
                            StudentQuestionResponse.grading_status == 'pending',
                        )
                        .count()
                    )
                    grading_status = 'pending' if pending_count > 0 else 'completed'

            # Enrich the payload
            test_data.update(
                {
                    'exam_name': mt.exam.name if getattr(mt, "exam", None) else 'N/A',
                    'has_open_ended_questions': has_open_ended,
                    'has_attempt': has_attempt,
                    'last_attempt_id': last_attempt_id,
                    'student_attempt_status': student_attempt_status,
                    'is_locked': is_locked,
                    'grading_status': grading_status,
                }
            )

            output.append(test_data)

        return jsonify(output), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching available mock tests: {e}", exc_info=True)
        return jsonify({"message": "Could not load mock tests."}), 500

@student_api_bp.route('/mock-tests/<int:mock_test_id>/start-attempt', methods=['POST'])
@student_required()
def start_or_resume_attempt(current_user, mock_test_id, **kwargs):
    """
    Creates a new test attempt for a student or resumes an existing one.
    This is the central logic for starting a test.
    """
    mock_test = MockTest.query.get_or_404(mock_test_id)

    # Security check: Ensure the student is an active member of the org that owns this test
    membership = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=mock_test.exam.organization_id,
        is_active=True
    ).first()

    if not membership:
        return jsonify({"message": "You do not have access to this mock test."}), 403

    # Check for an existing attempt for this specific test
    existing_attempt = StudentTestAttempt.query.filter_by(
        student_user_id=current_user.id,
        mock_test_id=mock_test_id
    ).first()

    if existing_attempt:
        # Case 1: The test is in progress and can be resumed
        if existing_attempt.status == 'in_progress':
            # Sub-case: The test has been locked by the proctoring system
            if existing_attempt.is_locked and not getattr(existing_attempt, 'is_unlocked', False):
                return jsonify({"message": "Your test is locked. Please contact your administrator."}), 403
            
            # If not locked, allow the student to resume
            return jsonify({"attempt_id": existing_attempt.id, "status": "resumed"}), 200

        # Case 2: The test is already completed or was locked and never unlocked
        else:
            return jsonify({"message": "You have already completed this test and cannot start it again."}), 409

    # Case 3: No existing attempt found, so create a new one
    try:
        # For live tests, check the start and end times
        if mock_test.is_live_test:
            now = datetime.utcnow()
            if mock_test.live_start_time and now < mock_test.live_start_time:
                return jsonify({"message": "This live test has not started yet."}), 400
            if mock_test.live_end_time and now > mock_test.live_end_time:
                return jsonify({"message": "This live test has already ended."}), 400

        # Create the new attempt record
        new_attempt = StudentTestAttempt(
            student_user_id=current_user.id,
            mock_test_id=mock_test_id,
            membership_id=membership.id, # This is the crucial link
            status='in_progress',
            time_limit_minutes=mock_test.duration_minutes
        )
        db.session.add(new_attempt)
        db.session.commit()
        
        return jsonify({"attempt_id": new_attempt.id, "status": "created"}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error starting test attempt: {e}")
        return jsonify({"message": "An error occurred while trying to start the test."}), 500
    
@student_api_bp.route('/mock-test/attempts/<int:attempt_id>/questions', methods=['GET'])
@student_required()
def get_mock_test_questions_for_attempt(current_user, attempt_id, **kwargs):
    # Find the specific attempt for the current student
    attempt = StudentTestAttempt.query.filter_by(id=attempt_id, student_user_id=current_user.id).first_or_404()

    # ✅ Check if the attempt is already locked (proctoring lock)
    if attempt.is_locked:
        return jsonify({
            "message": "This test attempt has been locked due to excessive tab switching.",
            "status": "locked"
        }), 403

    # Only allow fetching questions for a test that is 'in_progress'
    if attempt.status != 'in_progress':
        return jsonify({"message": "This test is not in progress.", "status": attempt.status}), 403

    # Check if the time limit has expired on the server side
    time_limit_seconds = (attempt.time_limit_minutes or 0) * 60
    elapsed_seconds = (datetime.utcnow() - attempt.start_time).total_seconds()
    if time_limit_seconds > 0 and elapsed_seconds > time_limit_seconds:
        attempt.status = 'time_up'
        db.session.commit()
        return jsonify({"message": "Time has expired for this test.", "status": "time_up"}), 403

    # Fetch all question associations for this mock test, in order
    mock_test_questions_assoc = MockTestQuestion.query.filter_by(
        mock_test_id=attempt.mock_test_id
    ).order_by(MockTestQuestion.question_order).all()

    # Get previously saved responses for this attempt
    saved_responses_query = StudentQuestionResponse.query.filter_by(attempt_id=attempt_id).all()
    saved_responses = {res.question_id: res for res in saved_responses_query}

    questions_data = []
    for mtq_assoc in mock_test_questions_assoc:
        # Apply visibility filter: only public questions or the current student's own questions
        question = Question.query.filter(
            Question.id == mtq_assoc.question_id,
            ((Question.visibility == 'public') | (Question.created_by_user_id == current_user.id))
        ).first()

        if not question:
            # Skip questions that the student is not allowed to see
            continue

        # Use the student-safe serializer (no correct answers leaked)
        q_data = serialize_question_for_student(question, set())  # empty set for reviewed_ids for now
        q_data['subject_name'] = question.topic.subject.name if question.topic and question.topic.subject else 'General'

        # Add previously saved answer (if any)
        saved_res = saved_responses.get(question.id)
        if saved_res:
            q_data['student_selected_option_id'] = saved_res.selected_mcq_option_id
            q_data['is_marked_for_review'] = saved_res.marked_for_review

        questions_data.append(q_data)

    return jsonify({
        "attempt_id": attempt.id,
        "mock_test_title": attempt.mock_test.title,
        "exam_name": attempt.mock_test.exam.name,
        "time_limit_minutes": attempt.time_limit_minutes,
        "remaining_seconds": max(0, int(time_limit_seconds - elapsed_seconds)),
        "questions": questions_data,
        "status": attempt.status,
        "mock_test_status": attempt.mock_test.status,

        # ✅ Added proctoring-related info for frontend
        "is_live_test": attempt.mock_test.is_live_test,
        "initial_switch_count": attempt.tab_switch_count,
        "is_locked": attempt.is_locked
    }), 200

@student_api_bp.route('/mock-test/attempts/<int:attempt_id>/lock', methods=['POST'])
@student_required()
def lock_test_attempt(current_user, attempt_id, **kwargs):
    attempt = StudentTestAttempt.query.filter_by(id=attempt_id, student_user_id=current_user.id).first_or_404()

    # Only lock a test that is currently in progress
    if attempt.status == 'in_progress':
        attempt.status = 'locked'
        db.session.commit()
        return jsonify({"message": "Test has been locked."}), 200
    
    return jsonify({"message": "Test is not in a lockable state."}), 400

@student_api_bp.route('/mock-test/attempts/<int:attempt_id>/save-response', methods=['POST'])
@student_required()
def save_mock_test_response(current_user, attempt_id, **kwargs):
    attempt = StudentTestAttempt.query.filter_by(
        id=attempt_id,
        student_user_id=current_user.id,
        status='in_progress'
    ).first_or_404()

    if attempt.is_locked:
        return jsonify({"message": "This test attempt is locked and cannot be updated."}), 403

    data = request.get_json()
    question_id = data.get('question_id')
    response_data = data.get('response_data')
    is_marked_for_review = data.get('is_marked_for_review', False)

    if not question_id:
        return jsonify({"message": "Missing question_id."}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"message": "Question not found."}), 404

    response = StudentQuestionResponse.query.filter_by(
        attempt_id=attempt.id,
        question_id=question_id
    ).first()

    if not response:
        response = StudentQuestionResponse(
            attempt_id=attempt.id,
            question_id=question_id,
        )
        db.session.add(response)

    if question.question_type == 'MCQ':
        response.selected_mcq_option_id = response_data
        response.response_text = None
    elif question.question_type == 'OpenEnded':
        response.response_text = response_data
        response.selected_mcq_option_id = None

    response.marked_for_review = is_marked_for_review
    response.answered_at = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({"message": "Progress saved."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving mock test response: {e}", exc_info=True)
        return jsonify({"message": "Could not save your progress."}), 500

@student_api_bp.route('/mock-test/attempts/<int:attempt_id>/proctor-event', methods=['POST'])
@student_required()
def record_proctor_event(current_user, attempt_id, **kwargs):
    """
    Records a tab switch event, increments the count, and correctly locks 
    the test if the limit is reached for a live test.
    """
    attempt = StudentTestAttempt.query.filter_by(
        id=attempt_id,
        student_user_id=current_user.id
    ).first_or_404()

    # Only process events for tests that are still in progress
    if attempt.status != 'in_progress':
        return jsonify({"is_locked": attempt.is_locked, "new_switch_count": attempt.tab_switch_count}), 200

    attempt.tab_switch_count = (attempt.tab_switch_count or 0) + 1
    
    # Check if the attempt should be locked
    if attempt.mock_test.is_live_test and attempt.tab_switch_count > 3:
        attempt.is_locked = True
        
        attempt.status = "locked"
        attempt.completed_at = datetime.utcnow() 

    db.session.commit()

    return jsonify({
        "message": "Event recorded.",
        "new_switch_count": attempt.tab_switch_count,
        "is_locked": attempt.is_locked
    }), 200

@student_api_bp.route('/mock-test/attempts/<int:attempt_id>/submit', methods=['POST'])
@student_required()
def submit_mock_test(current_user, attempt_id, **kwargs):
    """
    Handles mock test submission with nuanced grading logic:
    - Live Tests: Open-ended questions are sent for manual/AI-assisted review.
    - Non-Live & Practice Tests: Open-ended questions are graded automatically by AI.
    """
    attempt = StudentTestAttempt.query.filter_by(
        id=attempt_id,
        student_user_id=current_user.id
    ).first_or_404("Test attempt not found.")

    if attempt.is_locked:
        return jsonify({"message": "This test attempt is locked and cannot be submitted."}), 403

    if attempt.status not in ['in_progress', 'practice_in_progress']:
        return jsonify({"message": "This test has already been submitted."}), 400

    # --- Start of grading logic ---
    mock_test_questions = MockTestQuestion.query.filter_by(mock_test_id=attempt.mock_test_id).all()
    student_responses = StudentQuestionResponse.query.filter_by(attempt_id=attempt.id).all()
    responses_by_q_id = {res.question_id: res for res in student_responses}

    final_score = 0.0
    
    # NEW: Determine the grading strategy based on the test type.
    # The 'is_live_test' flag is set by the admin in the form you provided.
    is_live_official_test = attempt.mock_test.is_live_test

    for mt_question in mock_test_questions:
        question = mt_question.question
        student_response = responses_by_q_id.get(question.id)

        if not student_response:
            continue

        # --- THIS IS THE CORRECTED LOGIC ---
        if question.question_type == 'OpenEnded':
            # 1. LIVE OFFICIAL TEST: Send to the manual grading queue for the teacher.
            if is_live_official_test:
                student_response.status = 'pending_review'
                student_response.score = 0.0  # Admin will update this score later.
            
            # 2. NON-LIVE OFFICIAL TEST or SELF-PRACTICE TEST: Use AI for instant evaluation.
            else:
                evaluation = evaluate_open_ended_question(
                    question_text=question.question_text,
                    sample_answer=question.sample_answer, # Ensure your Question model has this field
                    student_response=student_response.response_text or ""
                )
                student_response.is_correct = evaluation.get('is_correct', False)
                student_response.score = float(mt_question.marks) if student_response.is_correct else 0.0
                student_response.ai_feedback_text = evaluation.get('feedback')
                student_response.status = 'graded'
        
        # This part for MCQ grading is already correct and works for all test types.
        elif student_response.selected_mcq_option_id is not None:
            correct_option = next((opt for opt in question.mcq_options if opt.is_correct), None)
            if correct_option and student_response.selected_mcq_option_id is not None and int(student_response.selected_mcq_option_id) == correct_option.id:
                student_response.is_correct = True
                student_response.score = float(mt_question.marks)
            else:
                student_response.is_correct = False
                student_response.score = 0.0
        
        # Add the graded score to the final total
        if student_response.score:
            final_score += float(student_response.score)

    # --- Finalize attempt ---
    attempt.score = final_score
    
    # Check if any questions are still pending review (only possible for live tests)
    has_pending_reviews = any(
        res.status == 'pending_review' for res in responses_by_q_id.values()
    )
    attempt.status = 'pending_review' if has_pending_reviews else 'completed'
    
    attempt.completed_at = datetime.utcnow()
    attempt.total_possible_score = sum(float(q.marks) for q in mock_test_questions if q.marks is not None)

    try:
        db.session.commit()
        return jsonify({
            "message": "Test submitted successfully!",
            "attempt_id": attempt.id
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error finalizing test submission: {e}", exc_info=True)
        return jsonify({"message": "An error occurred while saving your results."}), 500

@student_api_bp.route('/questions/<int:question_id>/submit-answer', methods=['POST'])
@student_required()
def submit_practice_answer(current_user, question_id, **kwargs):
    """
    Handles a student's answer for a single practice question and correctly logs it.
    - If attempt_id is provided: treat as a formal test question submission (tracks StudentQuestionResponse).
    - If attempt_id is not provided: treat as practice mode (no attempt), but still track progress on correct answers.
    """
    data = request.get_json(silent=True) or {}
    student_answer_id = data.get('answer')  # For MCQ, this is the selected option ID
    attempt_id = data.get('attempt_id')     # Optional; present only for formal tests

    # Basic validations
    if student_answer_id is None:
        return jsonify({"message": "An answer is required."}), 400

    # Load the question
    question = Question.query.get_or_404(question_id)

    # Normalize/validate the answer id for MCQ
    selected_option_id = None
    try:
        # Only attempt to cast if non-empty; tolerate string input from frontend
        if student_answer_id != '':
            selected_option_id = int(student_answer_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid answer format."}), 400

    # If attempt_id present, validate it belongs to this student
    attempt = None
    if attempt_id is not None:
        try:
            attempt_id_int = int(attempt_id)
        except (TypeError, ValueError):
            return jsonify({"message": "Invalid attempt_id."}), 400

        attempt = StudentTestAttempt.query.filter_by(
            id=attempt_id_int,
            student_user_id=current_user.id
        ).first_or_404()

    # --- Answer correctness check (MCQ) ---
    is_correct = False
    if question.question_type == 'MCQ':
        correct_option = next((opt for opt in question.mcq_options if getattr(opt, 'is_correct', False)), None)
        if correct_option and selected_option_id is not None and correct_option.id == selected_option_id:
            is_correct = True
    # If you add more question types later, extend correctness logic here
    # else: keep default is_correct = False for unknown types

    # DB operations
    try:
        # Use a sub-transaction to ensure atomicity
        with db.session.begin_nested():

            # --- FIX: For formal tests, correctly save/update the response ---
            if attempt is not None:
                response = StudentQuestionResponse.query.filter_by(
                    attempt_id=attempt.id,
                    question_id=question.id
                ).first()

                if not response:
                    response = StudentQuestionResponse(
                        attempt_id=attempt.id,
                        question_id=question.id
                    )
                    db.session.add(response)

                if question.question_type == 'MCQ':
                    response.selected_mcq_option_id = selected_option_id
                    response.is_correct = is_correct
                else:
                    # If you support other types later, set fields accordingly here
                    response.is_correct = is_correct

            # --- NEW: Track Progress on Correct Answer in practice or test ---
            # We purposely track topic mastery regardless of attempt mode
            if is_correct and question.topic_id is not None:
                progress = StudentTopicPractice.query.filter_by(
                    student_user_id=current_user.id,
                    topic_id=question.topic_id
                ).first()

                if not progress:
                    progress = StudentTopicPractice(
                        student_user_id=current_user.id,
                        topic_id=question.topic_id,
                        correctly_answered_ids=[],
                    )
                    db.session.add(progress)

                # Ensure unique addition and reassign the list so SQLAlchemy detects changes
                if question.id not in (progress.correctly_answered_ids or []):
                    updated_ids = (progress.correctly_answered_ids or []) + [question.id]
                    progress.correctly_answered_ids = updated_ids

        # Commit outer transaction
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving answer for question_id={question_id}, attempt_id={attempt_id}: {e}")
        return jsonify({"message": "Could not save your answer."}), 500

    # Prepare feedback payload
    full_question_data = serialize_question_with_answer_details(question)

    return jsonify({
        "message": "Answer processed.",
        "is_correct": is_correct,
        "question_details": full_question_data
    }), 200

@student_api_bp.route('/topics/<int:topic_id>/start-practice', methods=['POST'])
@student_required()
def start_practice_session(current_user, topic_id, **kwargs):
    """Creates a lightweight 'attempt' record for tracking practice question responses."""
    try:
        topic = Topic.query.get_or_404(topic_id)
        exam_id = topic.subject.exam_id
        
        # --- ADD MEMBERSHIP LOGIC ---
        # Find or create membership for the exam's organization
        organization_id = topic.subject.exam.organization_id
        membership = OrganizationMembership.query.filter_by(
            user_id=current_user.id,
            organization_id=organization_id
        ).first()
        
        if not membership:
            membership = OrganizationMembership(
                user_id=current_user.id, 
                organization_id=organization_id, 
                is_active=True, 
                access_type='public'
            )
            db.session.add(membership)
        elif not membership.is_active:
            membership.is_active = True
        
        # Commit membership to ensure it has an ID
        db.session.commit()
        # --- END MEMBERSHIP LOGIC ---
        
        # Check if a generic 'practice' test already exists for this exam
        practice_test = MockTest.query.filter_by(exam_id=exam_id, status='practice').first()
        
        if not practice_test:
            # If not, create one
            practice_test = MockTest(
                exam_id=exam_id,
                title=f"Practice Test for {topic.subject.exam.name}",
                status='practice',  # A special status to hide it from normal lists
                duration_minutes=0,
                passing_marks=0,
                total_marks=0,  # Must be set to avoid NOT NULL violation
                created_by_user_id=current_user.id
            )
            db.session.add(practice_test)
            db.session.flush()  # Get the ID for the new practice_test

        # Now, create the attempt and link it to the practice test
        new_attempt = StudentTestAttempt(
            student_user_id=current_user.id,
            mock_test_id=practice_test.id,
            membership_id=membership.id,  # Link to membership
            status='practice_in_progress'  # A clear status for this type of attempt
        )
        db.session.add(new_attempt)
        db.session.commit()
        
        return jsonify({
            "message": "Practice session started.", 
            "attempt_id": new_attempt.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error starting practice session: {e}", exc_info=True)
        return jsonify({"message": "Could not start practice session."}), 500
    
@student_api_bp.route('/comprehensions/<int:parent_id>/submit-answers', methods=['POST'])
@student_required()
def submit_comprehension_answers(current_user, parent_id, **kwargs):
    """Submits and grades all answers for a comprehension question at once."""
    data = request.get_json()
    answers = data.get('answers', [])
    attempt_id = data.get('attempt_id')

    if not attempt_id:
        return jsonify({"message": "Attempt ID is missing."}), 400

    feedback_results = []
    for sub in answers:
        sub_question = Question.query.get(sub.get('question_id'))
        if not sub_question or sub_question.parent_question_id != parent_id:
            continue

        correct_option = next((opt for opt in sub_question.mcq_options if opt.is_correct), None)
        is_correct = correct_option and correct_option.id == int(sub.get('answer'))
        
        feedback_results.append({
            "question_id": sub_question.id,
            "is_correct": is_correct,
            "correct_answer_text": correct_option.option_text if correct_option else "N/A"
        })
    
    parent_question = Question.query.get(parent_id)
    return jsonify({
        "message": "Comprehension answers processed.",
        "results": feedback_results,
        "overall_explanation": parent_question.explanation_text or "No overall explanation provided."
    }), 200


@student_api_bp.route('/mock-test/attempts/<int:attempt_id>/result', methods=['GET'])
@student_required()
def get_mock_test_result(current_user, attempt_id, **kwargs):
    """
    Returns a student's mock test result.
    """
    attempt = StudentTestAttempt.query.filter_by(
        id=attempt_id,
        student_user_id=current_user.id
    ).first_or_404("Test attempt not found.")

    mock_test = attempt.mock_test

    if attempt.status == 'locked':
        if mock_test.is_live_test and mock_test.live_end_time and datetime.utcnow() > mock_test.live_end_time:
            attempt.status = 'completed'
            db.session.commit()
        else:
            # The test is still live, so the student remains locked out.
            return jsonify({
                "status": "locked",
                "message": "Your test is locked. Please contact your administrator."
            }), 200 # Return 200 OK to let the frontend handle the message

    has_pending_grading = StudentQuestionResponse.query.join(Question).filter(
        StudentQuestionResponse.attempt_id == attempt.id,
        Question.question_type == 'OpenEnded',
        StudentQuestionResponse.grading_status == 'pending'
    ).first() is not None

    if has_pending_grading and attempt.status == 'completed':
        return jsonify({
            "status": "awaiting_grading",
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "mock_test_title": attempt.mock_test.title if attempt.mock_test else None,
            "mock_test_id": attempt.mock_test_id
        }), 200

    # Otherwise, build the full results
    questions_in_test = (
        MockTestQuestion.query
        .filter_by(mock_test_id=attempt.mock_test_id)
        .order_by(MockTestQuestion.question_order)
        .all()
    )

    responses = StudentQuestionResponse.query.filter_by(attempt_id=attempt.id).all()
    responses_by_q_id = {res.question_id: res for res in responses}

    questions_results = []
    for mt_question in questions_in_test:
        question = mt_question.question
        response = responses_by_q_id.get(question.id)

        student_response_data = {}
        if response:
            if question.question_type == 'MCQ':
                student_response_data = {
                    "selected_option_id": response.selected_mcq_option_id,
                    "is_correct": response.is_correct,
                    "score_obtained": str(response.score) if response.score is not None else "0.00"
                }
            elif question.question_type == 'OpenEnded':
                student_response_data = {
                    "open_ended_answer": response.response_text,
                    "grader_comments": response.ai_feedback_text,
                    "points_awarded": str(response.score) if response.score is not None else "0.00",
                    "is_correct": response.is_correct
                }

        q_result = {
            "question": serialize_question_with_answer_details(question),
            "student_response": student_response_data
        }
        questions_results.append(q_result)

    result_data = {
        "status": "ready",
        "attempt_id": attempt.id,
        "mock_test_title": attempt.mock_test.title if attempt.mock_test else None,
        "mock_test_id": attempt.mock_test_id,  # keep the fix you added
        "score": str(attempt.score) if attempt.score is not None else "0.00",
        "total_possible_score": str(attempt.total_possible_score) if attempt.total_possible_score is not None else None,
        "passing_marks": str(attempt.mock_test.passing_marks) if attempt.mock_test and attempt.mock_test.passing_marks is not None else None,
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "was_pending_grading": bool(getattr(attempt, "was_pending_grading", False)),
        "results": questions_results,
    }

    return jsonify(result_data), 200

def serialize_topic_content(content):
    return {
        "id": content.id,
        "title": content.title,
        "type": content.content_type,     # keep if student UI expects 'type'
        "value": content.content_value,   # keep if student UI expects 'value'
        "item_order": content.item_order
    }

@student_api_bp.route('/topics/<int:topic_id>/content', methods=['GET'])
@student_required()
def get_topic_content(current_user, topic_id, **kwargs):
    topic = Topic.query.get_or_404(topic_id)
    exam = topic.subject.exam

    # Ensure user is an active member of the org
    membership_record = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=exam.organization_id,
        is_active=True
    ).first()
    if not membership_record:
        return jsonify({"message": "Your access to this organization's content is disabled."}), 403

    # Ensure user has access to the exam
    access_record = StudentExam.query.filter(
        StudentExam.student_user_id == current_user.id,
        StudentExam.exam_id == exam.id,
        StudentExam.access_status.in_(["purchased", "free_access", "admin_granted"])
    ).first()
    if not access_record:
        return jsonify({"message": "You are not enrolled in the exam for this topic."}), 403

    # ✅ Only active (non-archived) contents
    contents = (TopicContent.query
                .filter(
                    TopicContent.topic_id == topic.id,
                    TopicContent.deleted_at.is_(None)
                )
                .order_by(TopicContent.item_order.asc())
                .all())

    resp = jsonify({
        "topic_name": topic.name,
        "contents": [serialize_topic_content(c) for c in contents]
    })
    # Optional: avoid stale caches on student side
    resp.headers["Cache-Control"] = "no-store"
    return resp, 200

def serialize_organization_membership(membership):
    if not membership or not membership.organization:
        return None
    return {
        "organization_id": membership.organization_id,
        "organization_name": membership.organization.name,
        "organization_code": membership.organization.code,
        "is_active": membership.is_active,
        "access_type": membership.access_type # 'internal' or 'public'
    }

@student_api_bp.route('/organization-memberships', methods=['GET'])
@student_required()
def get_student_organization_memberships(current_user, **kwargs):
    memberships = OrganizationMembership.query.options(
        joinedload(OrganizationMembership.organization)
    ).filter_by(user_id=current_user.id).all()
    
    serialized_memberships = []
    for m in memberships:
        if m.organization: # Safety check
            serialized_memberships.append({
                "organization_id": m.organization.id,
                "organization_name": m.organization.name,
                "organization_code": m.organization.code,
                "subdomain": m.organization.subdomain,
                "is_active": m.is_active
            })
    
    return jsonify(serialized_memberships), 200

@student_api_bp.route('/enroll-exam', methods=['POST'])
@student_required()
def enroll_in_exam(current_user, **kwargs):
    data = request.get_json()
    exam_id = data.get('exam_id')
    if not exam_id:
        return jsonify({"message": "Exam ID is required."}), 400

    exam = Exam.query.get_or_404(exam_id)
    organization_id = exam.organization_id
    country_code = get_country_code()

    enrollment = StudentExam.query.filter_by(
        student_user_id=current_user.id,
        exam_id=exam.id
    ).first()

    if enrollment and enrollment.access_status in ['purchased', 'free_access', 'admin_granted']:
        return jsonify({"message": "You are already actively enrolled in this exam."}), 409

    # --- Find or Create Membership ---
    membership = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=organization_id
    ).first()
    
    if not membership:
        membership = OrganizationMembership(  # <-- FIX: Assign to the 'membership' variable
            user_id=current_user.id, 
            organization_id=organization_id, 
            is_active=True, 
            access_type='public'
        )
        db.session.add(membership)
    elif not membership.is_active:
        membership.is_active = True
    
    # We commit the membership here to ensure it has an ID before we use it.
    db.session.commit()

    # --- Enrollment Logic: UPDATE or CREATE ---
    try:
        # Case 1: Free Exam
        if exam.is_free:
            if enrollment:
                enrollment.access_status = 'free_access'
                enrollment.purchased_at = datetime.utcnow()
                enrollment.expires_at = None
                enrollment.membership_id = membership.id # <-- FIX: Add ID on update too
            else:
                enrollment = StudentExam(
                    student_user_id=current_user.id,
                    exam_id=exam.id,
                    access_status='free_access',
                    purchased_at=datetime.utcnow(),
                    membership_id=membership.id  # <-- FIX: Pass the ID here
                )
                db.session.add(enrollment)
            
            db.session.commit()
            return jsonify({"message": f"Successfully enrolled in {exam.name}!", "payment_required": False}), 200

        # Case 2: Paid Exam
        else:
            if enrollment:
                db.session.delete(enrollment)
                db.session.commit()

            client = razorpay.Client(auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET']))
            
            price = exam.price
            currency = 'INR'
            if country_code != 'IN':
                price = price / 83.0
                currency = 'USD'

            order = client.order.create({
                "amount": int(price * 100),
                "currency": currency,
                "notes": {"exam_id": exam.id, "user_id": current_user.id}
            })

            new_pending_enrollment = StudentExam(
                student_user_id=current_user.id,
                exam_id=exam.id,
                access_status='pending_payment',
                razorpay_order_id=order['id'],
                membership_id=membership.id  
            )
            db.session.add(new_pending_enrollment)
            db.session.commit()

            return jsonify({
                "payment_required": True,
                "razorpay_key_id": current_app.config['RAZORPAY_KEY_ID'],
                "order_id": order['id'],
                "amount": order['amount'],
                "exam_name": exam.name,
                "currency": currency
            }), 202

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Enrollment Error: {e}", exc_info=True)
        return jsonify({"message": "An error occurred during the enrollment process."}), 500
    
@student_api_bp.route('/my-exams', methods=['GET'])
@student_required()
def get_my_enrolled_exams(current_user, **kwargs):
    """
    Fetches enrolled exams with the corrected database query to ensure
    organization filtering works correctly.
    """
    org_id_from_url = request.args.get('org_id', type=int)
    enrolled_statuses = ['purchased', 'free_access', 'admin_granted']

    # ** THIS IS THE CORRECTED QUERY **
    # It now correctly joins the Exam table first, so all filters work as expected.
    query = db.session.query(StudentExam).join(Exam).filter(
        StudentExam.student_user_id == current_user.id,
        StudentExam.access_status.in_(enrolled_statuses),
        Exam.deleted_at.is_(None)
    ).options(
        joinedload(StudentExam.exam).joinedload(Exam.organization)
    )

    # This filtering logic is correct and will now be applied properly.
    if g.get('current_organization'):
        query = query.filter(Exam.organization_id == g.current_organization.id)
    elif org_id_from_url:
        query = query.filter(Exam.organization_id == org_id_from_url)

    student_exams = query.order_by(Exam.name).all()
    
    exams_data = []
    for se in student_exams:
        if se.exam:
            exams_data.append({
                "exam_id": se.exam.id,
                "exam_name": se.exam.name,
                "organization_name": se.exam.organization.name if se.exam.organization else "N/A",
                "access_status": se.access_status,
                "purchased_at": se.purchased_at.isoformat() if se.purchased_at else None
            })

    return jsonify({"data": exams_data}), 200

@student_api_bp.route('/available-exams', methods=['GET'])
@student_required()
def get_available_exams(current_user, **kwargs):
    """
    Fetches exams available for enrollment with corrected multi-tenancy logic.
    - Subdomain/Specific Org: Shows exams only from that organization.
    - Global View: Shows exams ONLY from organizations the user is a member of.
    """
    try:
        country_code = get_country_code()
        # 1. Get IDs of exams the user is already actively enrolled in.
        # This part is correct and remains the same.
        enrolled_exam_ids = {
            se.exam_id for se in StudentExam.query.filter(
                StudentExam.student_user_id == current_user.id,
                StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted'])
            ).all()
        }

        # 2. ✅ DETERMINE THE CONTEXT: The core fix for Bug #2.
        base_query = Exam.query.join(Organization).filter(
            Organization.status == 'active',
            Exam.deleted_at.is_(None)
        )

        org_id_from_url = request.args.get('org_id', type=int)

        # Case A: Subdomain context.
        if g.get('current_organization'):
            query = base_query.filter(Exam.organization_id == g.current_organization.id)
        
        # Case B: Specific organization context from a URL parameter.
        elif org_id_from_url:
            query = base_query.filter(Exam.organization_id == org_id_from_url)

        # Case C: GLOBAL context.
        else:
            # First, find all organizations the student is a member of.
            memberships = OrganizationMembership.query.filter_by(user_id=current_user.id, is_active=True).all()
            member_of_org_ids = [m.organization_id for m in memberships]

            # If the user is not a member of any organization, show nothing.
            if not member_of_org_ids:
                return jsonify([]), 200
            
            # Filter the query to only include exams from those organizations.
            query = base_query.filter(Exam.organization_id.in_(member_of_org_ids))
            
        # 3. Filter out exams the user is already enrolled in.
        # This part is correct and remains the same.
        if enrolled_exam_ids:
            query = query.filter(db.not_(Exam.id.in_(enrolled_exam_ids)))

        available_exams = query.all()
        
        results = [{
            "id": e.id,
            "name": e.name,
            "organization_name": e.organization.name,
            "is_free": e.is_free,
            "price": format_price(e.price, country_code) if e.price else "Free"
        } for e in available_exams]
        
        return jsonify(results), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching available exams: {e}", exc_info=True)
        return jsonify({"message": "Could not load available exams."}), 500


@student_api_bp.route('/generate-practice-test', methods=['POST'])
@student_required()
def generate_practice_test(current_user, **kwargs):
    data = request.get_json()
    scope_type = data.get('scope_type')
    scope_id = data.get('scope_id')
    num_questions = data.get('num_questions')
    time_limit = data.get('time_limit')

    if not all([scope_type, scope_id, num_questions, time_limit]):
        return jsonify({"message": "Missing required test parameters."}), 400
    
    try:
        num_questions = int(num_questions)
        time_limit = int(time_limit)
        if num_questions <= 0 or time_limit <= 0: 
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"message": "Number of questions and time limit must be positive numbers."}), 400

    # Build a query that only selects parent questions
    base_query = Question.query.filter(Question.parent_question_id.is_(None), Question.deleted_at.is_(None))
    
    if scope_type == 'subject':
        subject = Subject.query.get_or_404(scope_id)
        scope_name = f"{subject.exam.name} - {subject.name}"
        exam_id = subject.exam_id
        # Filter questions belonging to topics within this subject
        available_questions = base_query.join(Topic).filter(Topic.subject_id == scope_id).all()
    elif scope_type == 'exam':
        exam = Exam.query.get_or_404(scope_id)
        scope_name = exam.name
        exam_id = exam.id
        # Filter questions belonging to topics within subjects within this exam
        available_questions = base_query.join(Topic).join(Subject).filter(Subject.exam_id == scope_id).all()
    else:
        return jsonify({"message": "Invalid scope type."}), 400

    # --- ADD MEMBERSHIP LOGIC ---
    # Find or create membership for the exam's organization
    organization_id = Exam.query.get(exam_id).organization_id
    membership = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=organization_id
    ).first()
    
    if not membership:
        membership = OrganizationMembership(
            user_id=current_user.id, 
            organization_id=organization_id, 
            is_active=True, 
            access_type='public'
        )
        db.session.add(membership)
    elif not membership.is_active:
        membership.is_active = True
    
    # Commit membership to ensure it has an ID
    db.session.commit()
    # --- END MEMBERSHIP LOGIC ---

    if len(available_questions) < num_questions:
        return jsonify({"message": f"Not enough questions available to generate a test. Only {len(available_questions)} found."}), 400
    
    selected_questions = sample(available_questions, num_questions)

    try:
        # Make the title unique by adding a timestamp
        unique_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        practice_test_title = f"Practice: {scope_name} ({unique_timestamp})"

        practice_test = MockTest(
            exam_id=exam_id,
            title=practice_test_title,
            description=f"A dynamically generated practice test for {current_user.email}",
            duration_minutes=time_limit,
            total_marks=num_questions,
            passing_marks=num_questions * 0.5,
            status='practice',  # Special status for student-generated tests
            created_by_user_id=current_user.id
        )
        db.session.add(practice_test)
        db.session.flush()

        for i, question in enumerate(selected_questions):
            mtq = MockTestQuestion(
                mock_test_id=practice_test.id,
                question_id=question.id,
                question_order=i + 1,
                marks=1
            )
            db.session.add(mtq)
        
        new_attempt = StudentTestAttempt(
            student_user_id=current_user.id,
            mock_test_id=practice_test.id,
            membership_id=membership.id,  # Link to membership
            status='in_progress',
            time_limit_minutes=time_limit
        )
        db.session.add(new_attempt)
        db.session.commit()

        return jsonify({
            "message": "Practice test generated successfully!", 
            "attempt_id": new_attempt.id
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating practice test: {e}", exc_info=True)
        return jsonify({"message": "An error occurred while generating the test."}), 500
    
@student_api_bp.route('/exams', methods=['GET'])
@student_required()
def get_my_exams(current_user):
    enrolled_exams = (
        db.session.query(Exam)
        .join(StudentExam, StudentExam.exam_id == Exam.id)
        .filter(StudentExam.student_user_id == current_user.id)
        .filter(Exam.deleted_at == None)
        .all()
    )

    result = [{
        "id": exam.id,
        "name": exam.name,
        # Optional: add more fields or nested subjects
    } for exam in enrolled_exams]

    return jsonify(result), 200

@student_api_bp.route('/reviewed-questions', methods=['GET'])
@student_required()
def get_reviewed_questions(current_user, **kwargs):
    """
    Fetches all questions that the current student has marked for review.
    If an org_id is provided, it filters for questions within that organization.
    """
    try:
        # ✅ THE FIX: Read the org_id from the URL and build the query
        org_id = request.args.get('org_id', type=int)

        # Base query to get reviewed questions for the current user
        query = StudentReviewedQuestion.query.filter_by(
            student_user_id=current_user.id
        )

        # If an org_id is provided, join through to Exam and filter
        if org_id:
            query = query.join(Question, StudentReviewedQuestion.question_id == Question.id)\
                         .join(Topic, Question.topic_id == Topic.id)\
                         .join(Subject, Topic.subject_id == Subject.id)\
                         .join(Exam, Subject.exam_id == Exam.id)\
                         .filter(Exam.organization_id == org_id)

        reviewed_entries = query.order_by(StudentReviewedQuestion.marked_at.desc()).all()

        questions = [entry.question for entry in reviewed_entries if entry.question]
        
        # Using the serializer to include topic and subject context
        serialized_questions = [serialize_reviewed_question(q) for q in questions]

        return jsonify(serialized_questions), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching reviewed questions: {e}", exc_info=True)
        return jsonify({"message": "Could not load your reviewed questions due to a server error."}), 500

@student_api_bp.route('/my-transactions', methods=['GET'])
@student_required()
def get_my_transactions(current_user, **kwargs):
    """ Gathers all financial transactions for the student from organizations
    where their membership is currently active. """
    transactions = []
    
    active_memberships = OrganizationMembership.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).all()
    active_org_ids = [m.organization_id for m in active_memberships]

    if not active_org_ids:
        return jsonify([]), 200

    # 1. Get transactions from Exam Purchases
    exam_purchases = StudentExam.query.join(Exam).filter(
        StudentExam.student_user_id == current_user.id,
        StudentExam.razorpay_payment_id.isnot(None),
        Exam.organization_id.in_(active_org_ids)
    ).all()
    
    for purchase in exam_purchases:
        transactions.append({
            "date": purchase.purchased_at.isoformat() if purchase.purchased_at else None,
            "description": f"Exam Enrollment: {purchase.exam.name}",
            # ✅ Safe access to price to prevent errors
            "amount": f"{purchase.exam.price:.2f}" if purchase.exam and purchase.exam.price is not None else "0.00",
            "status": "Completed",
            "transaction_id": purchase.razorpay_payment_id
        })

    # 2. Get transactions from AI Subscriptions (this logic can also be enhanced)
    # For now, we assume AI subscriptions are global and not tied to an org.
    ai_subs = StudentAISubscription.query.filter(
        StudentAISubscription.student_user_id == current_user.id,
        StudentAISubscription.razorpay_subscription_id.isnot(None)
    ).all()

    for sub in ai_subs:
        transactions.append({
            "date": sub.last_payment_date.isoformat() if sub.last_payment_date else sub.start_date.isoformat(),
            "description": "AI Feature Subscription",
            "amount": "N/A",
            "status": "Active" if sub.status == 'active' else "Inactive",
            "transaction_id": sub.razorpay_subscription_id
        })

    # Sort all transactions by date, descending
    sorted_transactions = sorted(
        transactions, 
        key=lambda t: t.get('date') or datetime.min.isoformat(), 
        reverse=True
    )    
    return jsonify(sorted_transactions), 200

@student_api_bp.route('/ai-tutor/context-options', methods=['GET'])
@jwt_required()
def get_ai_tutor_context_options():
    """
    For Students: return only enrolled exams.
    For Super Admins: return all non-deleted exams across orgs.
    Response shape matches the JS in learn_with_ai.html.
    """
    ident = get_jwt_identity()
    user_id = ident.get('id') if isinstance(ident, dict) else ident
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    try:
        if user.user_type == 'super_admin':
            exams = Exam.query.filter(Exam.deleted_at.is_(None)).all()
        elif user.user_type == 'student':
            access_rows = StudentExam.query.filter_by(student_user_id=user.id).all()
            # only exams that exist & not deleted
            exams = [r.exam for r in access_rows if r.exam and r.exam.deleted_at is None]
        else:
            # co_admin/main_co_admin don’t use this student picker
            return jsonify([]), 200

        results = []
        for exam in exams:
            subjects = (
                Subject.query
                .filter(
                    Subject.exam_id == exam.id,
                    Subject.deleted_at.is_(None)
                )
                .all()
            )

            # Pick a sensible default topic id (first non-deleted topic if present)
            def default_topic_id_for_subject(s):
                if not getattr(s, 'topics', None):
                    return None
                # filter out deleted topics if you have deleted_at on Topic
                try:
                    t = next((t for t in s.topics if getattr(t, 'deleted_at', None) is None), None)
                    return t.id if t else None
                except Exception:
                    return None

            exam_name = f"{exam.name} ({exam.organization.name})" if user.user_type == 'super_admin' else exam.name
            results.append({
                "exam_id": exam.id,
                "exam_name": exam_name,
                "subjects": [
                    {
                        "subject_id": s.id,
                        "subject_name": s.name,
                        "default_topic_id": default_topic_id_for_subject(s)
                    }
                    for s in subjects
                ]
            })

        results.sort(key=lambda x: x['exam_name'])
        return jsonify(results), 200

    except Exception as e:
        current_app.logger.error("Error fetching AI tutor context options", exc_info=True)
        return jsonify({"message": "Could not load data for AI Tutor."}), 500

@student_api_bp.route('/my-exams/<int:exam_id>', methods=['DELETE'])
@student_required()
def unenroll_from_exam(current_user, exam_id, **kwargs):
    """
    Allows a student to unenroll from an exam. If it's the last active exam
    in an organization, the membership for that org is marked as inactive.
    """
    enrollment = StudentExam.query.filter_by(
        student_user_id=current_user.id,
        exam_id=exam_id
    ).first_or_404("Enrollment record not found.")

    organization_id = enrollment.exam.organization_id

    try:
        # Step 1: Mark the specific exam enrollment as 'unenrolled'.
        enrollment.access_status = 'unenrolled'
        db.session.commit()

        # Step 2: ✅ Check for any OTHER active enrollments in the same organization.
        other_active_enrollments = StudentExam.query.join(Exam).filter(
            StudentExam.student_user_id == current_user.id,
            Exam.organization_id == organization_id,
            StudentExam.id != enrollment.id,  # Exclude the one we just unenrolled
            StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted'])
        ).count()

        # Step 3: If there are no other active enrollments, deactivate the membership.
        if other_active_enrollments == 0:
            membership = OrganizationMembership.query.filter_by(
                user_id=current_user.id,
                organization_id=organization_id
            ).first()
            if membership:
                membership.is_active = False
                db.session.commit()

        return jsonify({"message": "You have been successfully unenrolled."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unenrollment Error: {e}", exc_info=True)
        return jsonify({"message": "An error occurred during unenrollment."}), 500
    
# Helper to serialize a recent test attempt
def _serialize_org_dashboard_activity(attempt):
    if not attempt or not attempt.mock_test: return None
    return {
        "icon": "📝",
        "title": f"Completed: <strong>{attempt.mock_test.title}</strong>",
        "time": f"{attempt.completed_at.strftime('%d %b %Y, %I:%M %p')}",
        "url": url_for('frontend.student_mock_test_result', attempt_id=attempt.id, **g.get('org_param', {}))
    }

@student_api_bp.route('/dashboard/organization-summary/<int:org_id>', methods=['GET'])
@student_required()
def get_org_dashboard_summary(current_user, org_id, **kwargs):
    """
    Returns dashboard data for the student within the context of a specific organization.
    """
    try:
        user_id = current_user.id

        # --- ADD MEMBERSHIP VALIDATION ---
        membership = OrganizationMembership.query.filter_by(
            user_id=user_id,
            organization_id=org_id,
            is_active=True
        ).first()
        
        if not membership:
            return jsonify({"message": "You don't have access to this organization."}), 403
        # --- END MEMBERSHIP VALIDATION ---

        # --- Base: Completed Attempts (UPDATED to filter by membership) ---
        base_attempts_query = StudentTestAttempt.query.join(MockTest).join(Exam).filter(
            Exam.organization_id == org_id,
            StudentTestAttempt.student_user_id == user_id,
            StudentTestAttempt.membership_id == membership.id  # ADDED: Filter by membership
        )
        completed_attempts = base_attempts_query.filter(
            StudentTestAttempt.status == 'completed'
        ).all()

        # --- 1. Quick Stats ---
        attempts_subquery = base_attempts_query.subquery()

        # Use the same variable in the join condition
        all_responses_query = db.session.query(StudentQuestionResponse).join(
            attempts_subquery,
            StudentQuestionResponse.attempt_id == attempts_subquery.c.id
        )

        questions_answered = all_responses_query.count()
        correct_answers = all_responses_query.filter(StudentQuestionResponse.is_correct.is_(True)).count()
        accuracy = round((correct_answers / questions_answered) * 100) if questions_answered > 0 else 0

        # --- 2. Streak (based on test dates) ---
        streak_days = 0
        if completed_attempts:
            dates = sorted(
                list(set(att.completed_at.date() for att in completed_attempts)),
                reverse=True
            )
            streak = 1
            if len(dates) > 1:
                for i in range(len(dates) - 1):
                    if (dates[i] - dates[i + 1]).days == 1:
                        streak += 1
                    else:
                        break
            streak_days = streak

        # --- 3. Performance Chart Data ---
        latest_attempts = sorted(completed_attempts, key=lambda x: x.completed_at, reverse=True)[:10]
        performance_data = {
            "labels": [att.mock_test.title[:15] for att in reversed(latest_attempts)],
            "scores": [float(att.score) for att in reversed(latest_attempts)],
            "accuracy": [
                round((att.score / att.total_possible_score) * 100) if att.total_possible_score > 0 else 0
                for att in reversed(latest_attempts)
            ]
        }

        # --- 4. Subject-wise Stats (UPDATED to filter by membership) ---
        subject_stats_raw = defaultdict(lambda: {'correct': 0, 'total': 0})
        subject_query = db.session.query(
            Subject.name,
            StudentQuestionResponse.is_correct
        ).select_from(StudentQuestionResponse)\
            .join(StudentTestAttempt, StudentTestAttempt.id == StudentQuestionResponse.attempt_id)\
            .join(MockTest, MockTest.id == StudentTestAttempt.mock_test_id)\
            .join(Exam, Exam.id == MockTest.exam_id)\
            .join(Question, Question.id == StudentQuestionResponse.question_id)\
            .join(Topic, Topic.id == Question.topic_id)\
            .join(Subject, Subject.id == Topic.subject_id)\
            .filter(
                StudentTestAttempt.student_user_id == user_id,
                StudentTestAttempt.membership_id == membership.id,  # ADDED: Filter by membership
                Exam.organization_id == org_id,
                StudentTestAttempt.status == 'completed'
            ).all()

        for name, is_correct in subject_query:
            subject_stats_raw[name]['total'] += 1
            if is_correct:
                subject_stats_raw[name]['correct'] += 1

        subject_performance = []
        for name, stats in subject_stats_raw.items():
            acc = round((stats['correct'] / stats['total']) * 100) if stats['total'] > 0 else 0
            subject_performance.append({
                "name": name,
                "questionsAnswered": stats['total'],
                "accuracy": acc,
                "strength": "Strong" if acc >= 75 else "Moderate" if acc >= 50 else "Weak"
            })

        # --- 5. Recent Activity ---
        recent_activity = [_serialize_org_dashboard_activity(att) for att in latest_attempts[:5]]

        # --- 6. Enrolled & Available Exams (Corrected) ---
        enrolled_exams_query = Exam.query.join(StudentExam).filter(
            Exam.organization_id == org_id,
            StudentExam.student_user_id == user_id,
            StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted']),
            StudentExam.membership_id == membership.id,  # ADDED: Filter by membership
            Exam.deleted_at.is_(None)
        ).all()

        enrolled_exam_ids = {e.id for e in enrolled_exams_query}

        all_org_exams = Exam.query.filter_by(organization_id=org_id, deleted_at=None).all()
        available_exams = [e for e in all_org_exams if e.id not in enrolled_exam_ids]

        # --- 7. Final JSON ---
        dashboard_data = {
            "stats": {
                "totalTests": len(completed_attempts),
                "accuracy": accuracy,
                "questionsAnswered": questions_answered,
                "streakDays": streak_days
            },
            "performanceData": performance_data,
            "subjectStats": sorted(subject_performance, key=lambda x: x['accuracy'], reverse=True),
            "recentActivity": recent_activity,
            "enrolledExams": [{"id": e.id, "name": e.name} for e in enrolled_exams_query],
            "availableExams": [{"id": e.id, "name": e.name, "is_free": e.is_free} for e in available_exams],
            "achievements": [
                {"icon": "🏆", "title": "First Test Completed"},
                {"icon": "⭐", "title": "High Scorer"}
            ]
        }

        return jsonify(dashboard_data), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching org dashboard for org_id {org_id}: {e}", exc_info=True)
        return jsonify({"message": "Could not load organization dashboard data."}), 500


@student_api_bp.route('/mock-test/<int:mock_test_id>/leaderboard', methods=['GET'])
@student_required()
def get_mock_test_leaderboard(current_user, mock_test_id, **kwargs):
    try:
        mock_test = MockTest.query.get_or_404(mock_test_id)
        exam = mock_test.exam

        # Check if student has active membership in the exam's organization
        membership_record = OrganizationMembership.query.filter_by(
            user_id=current_user.id,
            organization_id=exam.organization_id,
            is_active=True
        ).first()
        if not membership_record:
            return jsonify({"message": "Access denied: no active membership in this organization."}), 403

        # Check if student is enrolled in this exam
        enrollment = StudentExam.query.filter(
            StudentExam.student_user_id == current_user.id,
            StudentExam.exam_id == exam.id,
            StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted']),
            StudentExam.membership_id == membership_record.id  # ADDED: Filter by membership
        ).first()
        if not enrollment:
            return jsonify({"message": "Access denied: you are not enrolled in this exam."}), 403

        # UPDATED: Fetch completed attempts filtered by membership
        attempts = StudentTestAttempt.query.join(MockTest).join(Exam).filter(
            StudentTestAttempt.mock_test_id == mock_test_id,
            StudentTestAttempt.status == 'completed',
            StudentTestAttempt.membership_id == membership_record.id,  # ADDED: Filter by membership
            Exam.organization_id == exam.organization_id
        ).order_by(
            StudentTestAttempt.score.desc().nullslast(),
            StudentTestAttempt.completed_at.asc()
        ).all()

        if not attempts:
            return jsonify({"leaderboard": [], "currentUserRank": None, "mock_test_title": mock_test.title}), 200

        leaderboard_data = []
        current_user_rank = None
        rank = 0
        last_score = -1

        for i, attempt in enumerate(attempts):
            current_score = float(attempt.score or 0)
            if current_score != last_score:
                rank = i + 1
            last_score = current_score

            is_current = (attempt.student_user_id == current_user.id)

            student_data = {
                "rank": rank,
                "student_name": f"{attempt.student.first_name} {attempt.student.last_name}",
                "score": current_score,
                "total_marks": float(attempt.total_possible_score or 0),
                "completed_at": attempt.completed_at.strftime('%d %b %Y'),
                "is_current_user": is_current
            }
            leaderboard_data.append(student_data)

            if is_current:
                current_user_rank = student_data

        if current_user_rank:
            leaderboard_data = [item for item in leaderboard_data if not item['is_current_user']]
            leaderboard_data.insert(0, current_user_rank)

        return jsonify({
            "leaderboard": leaderboard_data,
            "currentUserRank": current_user_rank,
            "mock_test_id": mock_test.id,  # FIXED: Use mock_test.id instead of attempt.mock_test_id
            "mock_test_title": mock_test.title
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching leaderboard for mock test {mock_test_id}: {e}", exc_info=True)
        return jsonify({"message": "Could not load leaderboard data."}), 500
    
# Add this new route to the student API file

def monday_of(date_obj: date) -> date:
    return date_obj - timedelta(days=date_obj.weekday())

def build_weekly_metrics(performance_rows, week_start: date, week_end: date):
    """
    performance_rows: list of ORM rows with fields:
      - is_correct (bool), time_taken (seconds), difficulty_level, completed_at (datetime), subject_name, topic_name
    """
    week_items = [r for r in performance_rows if week_start <= r.completed_at.date() <= week_end]
    total = len(week_items)
    correct = sum(1 for r in week_items if r.is_correct)
    accuracy = round((correct / total) * 100, 2) if total else 0.0

    # per-topic counts
    topic_counts = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in week_items:
        t = r.topic_name or 'General'
        topic_counts[t]['total'] += 1
        if r.is_correct:
            topic_counts[t]['correct'] += 1
    topic_summary = [
        {'topic': t, 'accuracy': round((v['correct']/v['total'])*100, 1) if v['total'] else 0, 'attempts': v['total']}
        for t, v in topic_counts.items()
    ]
    topic_summary.sort(key=lambda x: x['accuracy'])

    times = [r.time_taken for r in week_items if r.time_taken]
    avg_time = round(statistics.mean(times), 2) if times else 0

    # difficulty distribution
    diff_dist = defaultdict(int)
    for r in week_items:
        diff_dist[r.difficulty_level or 'medium'] += 1

    # recent activity score (simple)
    recent_score = min(100, total * 5)  # 20 attempts → 100

    return {
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'attempts': total,
        'accuracy': accuracy,
        'avg_time_sec': avg_time,
        'difficulty_distribution': dict(diff_dist),
        'topics': topic_summary[:8],              # keep it small
        'recent_activity_score': recent_score,
    }

@student_api_bp.route('/study-plan/generate-advanced/<int:exam_id>', methods=['POST'])
@student_required()
@premium_feature_required()  # ✅ premium-only
def generate_advanced_study_plan(current_user, exam_id, **kwargs):
    try:
        # 0) Must be on an org subdomain
        if not getattr(g, 'current_organization', None):
            return jsonify({"success": False, "message": "This feature is only available within an organization subdomain."}), 403

        org = g.current_organization

        # 1) Student must be an active member of this org
        membership = OrganizationMembership.query.filter_by(
            user_id=current_user.id,
            organization_id=org.id,
            is_active=True
        ).first()
        if not membership:
            return jsonify({"success": False, "message": "You don't have access to this organization."}), 403

        # 2) Exam must belong to this org
        exam = Exam.query.get_or_404(exam_id)
        if exam.organization_id != org.id:
            return jsonify({"success": False, "message": "Exam does not belong to this organization."}), 403

        # 3) Student must have access to this exam (purchased/free/admin_granted)
        student_exam = StudentExam.query.filter_by(
            student_user_id=current_user.id,
            exam_id=exam_id
        ).filter(StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted'])).first()
        if not student_exam:
            return jsonify({"success": False, "message": "No access to this exam."}), 403

        # 4) (Optional) Double-check premium active (decorator already enforced)
        #    Kept for clarity if you ever call this internally.
        now = datetime.utcnow()
        sub = StudentAISubscription.query.filter_by(
            student_user_id=current_user.id, status='active'
        ).first()
        if not sub or not (sub.end_date is None or sub.end_date >= now):
            return jsonify({"success": False, "message": "Premium required."}), 403

        # ------ your existing logic continues below ------

        # Get request params
        data = request.get_json() or {}
        study_hours_per_day   = data.get('study_hours_per_day', 2)
        difficulty_preference = data.get('difficulty_preference', 'balanced')
        focus_areas           = data.get('focus_areas', [])
        use_organization_plan = data.get('use_organization_plan', False)

        if use_organization_plan:
            # keep your existing org plan path (already scoped by org above)
            return _get_organization_study_plan(exam_id, current_user.id, exam)

        # --- Build performance_data exactly like you do now (exam-scoped) ---
        performance_data = db.session.query(
            Subject.name.label('subject_name'),
            Topic.name.label('topic_name'),
            Question.difficulty_level,
            StudentQuestionResponse.is_correct,
            StudentQuestionResponse.time_taken,
            StudentTestAttempt.completed_at,
            StudentTestAttempt.score,
            Question.id.label('question_id'),
            MockTest.title.label('test_name')
        ).select_from(StudentQuestionResponse)\
         .join(StudentTestAttempt, StudentTestAttempt.id == StudentQuestionResponse.attempt_id)\
         .join(MockTest, MockTest.id == StudentTestAttempt.mock_test_id)\
         .join(Question, Question.id == StudentQuestionResponse.question_id)\
         .join(Topic, Topic.id == Question.topic_id)\
         .join(Subject, Subject.id == Topic.subject_id)\
         .filter(
            StudentTestAttempt.student_user_id == current_user.id,
            MockTest.exam_id == exam_id,
            StudentTestAttempt.status == 'completed',
            StudentTestAttempt.completed_at >= (datetime.utcnow() - timedelta(days=365))
         ).order_by(StudentTestAttempt.completed_at.asc()).all()

        # --- Auto-refresh weekly snapshot & pull recent weeks (no clicks) ---
        try:
            _ensure_weekly_snapshot(current_user.id, exam_id, performance_data)  # from section 3
            recent_weeks = _recent_week_summaries(current_user.id, exam_id, limit=8)
        except Exception as e:
            current_app.logger.warning(f"Weekly snapshot/summaries failed: {e}")
            recent_weeks = []

        if not performance_data:
            # beginner plan still allowed (premium route)
            return _generate_beginner_plan(exam_id, exam)

        analytics = _analyze_exam_performance(performance_data, exam_id)
        learning_patterns = _identify_learning_patterns(performance_data, current_user.id)
        difficulty_recommendations = _calculate_optimal_difficulty(analytics, difficulty_preference)

        ai_analytics = _generate_ai_powered_insights(
            performance_data, analytics, current_user.id, exam_id, exam,
            weekly_summaries=recent_weeks  # small addition to your helper
        )

        # Generate tasks (hybrid AI + your base tasks)
        daily_tasks = _generate_hybrid_tasks(
            analytics, learning_patterns, difficulty_recommendations,
            study_hours_per_day, focus_areas, exam_id, exam, ai_analytics
        )

        # Build response (same shape you already return)
        progress_insights = _generate_progress_insights(analytics, current_user.id, exam)
        all_tasks = daily_tasks
        response_data = {
            "success": True,
            "study_plan": {
                "exam_info": {
                    "exam_name": exam.name,
                    "exam_id": exam_id,
                    "organization": exam.organization.name if exam.organization else "N/A"
                },
                "reminder_message": _generate_motivational_message(analytics, progress_insights, exam),
                "todays_focus": all_tasks[:5],
                "all_tasks": all_tasks,
                "analytics": {
                    "overall_performance": analytics['overall_performance'],
                    "strengths": analytics['top_strengths'][:3],
                    "improvement_areas": analytics['weak_areas'][:3],
                    "learning_velocity": learning_patterns['learning_velocity'],
                    "recommended_study_time": f"{study_hours_per_day} hours",
                    "difficulty_level": difficulty_recommendations['current_level'],
                    "exam_specific_score": analytics.get('latest_exam_score', 0),
                    "total_questions_attempted": analytics['total_questions_attempted']
                },
                "progress_insights": progress_insights,
                "next_milestones": _generate_milestones(analytics, exam),
                "study_streak": _calculate_study_streak(current_user.id, exam_id),
                "personalization": {
                    "optimal_study_time": learning_patterns['optimal_time_slots'],
                    "question_pace": learning_patterns['average_time_per_question'],
                    "retention_rate": learning_patterns['retention_rate']
                },
                "plan_type": "ai_powered",
                "ai_insights": ai_analytics
            }
        }
        return jsonify(response_data), 200

    except Exception as e:
        current_app.logger.error(f"Error generating advanced study plan for exam {exam_id}: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Could not generate your study plan."}), 500

# Additional ML-Driven Analytics Features for Your Study Plan System

def _advanced_learning_curve_analysis(performance_data, user_id):
    """
    Advanced learning curve analysis with trend prediction
    """
    import numpy as np
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Group performance by week
    weekly_performance = defaultdict(list)
    for item in performance_data:
        week = item.completed_at.isocalendar()[1]
        year = item.completed_at.year
        week_key = f"{year}-W{week:02d}"
        weekly_performance[week_key].append(item.is_correct)
    
    # Calculate weekly accuracy trends
    weekly_trends = []
    for week, results in sorted(weekly_performance.items()):
        accuracy = sum(r or 0 for r in results) / len(results) * 100 if results else 0
        weekly_trends.append({
            'week': week,
            'accuracy': accuracy,
            'questions_attempted': len(results),
            'improvement_rate': 0  # Will be calculated
        })
    
    # Calculate improvement rates
    for i in range(1, len(weekly_trends)):
        prev_accuracy = weekly_trends[i-1]['accuracy']
        curr_accuracy = weekly_trends[i]['accuracy']
        weekly_trends[i]['improvement_rate'] = curr_accuracy - prev_accuracy
    
    # Predict next week's performance using simple linear regression
    if len(weekly_trends) >= 3:
        accuracies = [w['accuracy'] for w in weekly_trends[-4:]]  # Last 4 weeks
        x = np.arange(len(accuracies))
        z = np.polyfit(x, accuracies, 1)
        predicted_next_week = z[0] * len(accuracies) + z[1]
        
        return {
            'weekly_trends': weekly_trends,
            'predicted_performance': max(0, min(100, predicted_next_week)),
            'learning_velocity': np.mean([w['improvement_rate'] for w in weekly_trends[-3:]]),
            'consistency_score': 100 - np.std([w['accuracy'] for w in weekly_trends[-4:]]) if len(weekly_trends) >= 4 else 0
        }
    
    return {
        'weekly_trends': weekly_trends,
        'predicted_performance': 0,
        'learning_velocity': 0,
        'consistency_score': 0
    }


def _cognitive_load_analysis(performance_data, user_id):
    """
    Analyze cognitive load patterns based on question difficulty and time taken
    """
    difficulty_mapping = {'easy': 1, 'medium': 2, 'hard': 3}
    
    cognitive_data = []
    for item in performance_data:
        if item.time_taken and item.difficulty_level:
            cognitive_load = difficulty_mapping.get(item.difficulty_level, 2) * (item.time_taken / 60)  # Load factor
            cognitive_data.append({
                'load': cognitive_load,
                'correct': item.is_correct,
                'time_of_day': item.completed_at.hour,
                'difficulty': item.difficulty_level
            })
    
    if not cognitive_data:
        return {'optimal_load': 0, 'fatigue_threshold': 0, 'recommendations': []}
    
    # Find optimal cognitive load range
    load_performance = defaultdict(list)
    for data in cognitive_data:
        load_bucket = int(data['load'])
        load_performance[load_bucket].append(data['correct'])
    
    optimal_loads = []
    for load, results in load_performance.items():
        if len(results) >= 3:  # Minimum sample size
            accuracy = sum(results) / len(results) * 100
            if accuracy > 70:  # Good performance threshold
                optimal_loads.append(load)
    
    # Detect fatigue patterns
    time_performance = defaultdict(list)
    for data in cognitive_data:
        time_performance[data['time_of_day']].append(data['correct'])
    
    fatigue_hours = []
    for hour, results in time_performance.items():
        if len(results) >= 3:
            accuracy = sum(r or 0 for r in results) / len(results) * 100 if results else 0
            if accuracy < 60:  # Below average performance
                fatigue_hours.append(hour)
    
    recommendations = []
    if optimal_loads:
        recommendations.append(f"Your optimal study intensity is at level {min(optimal_loads)}-{max(optimal_loads)}")
    if fatigue_hours:
        recommendations.append(f"Consider avoiding study sessions at {', '.join(map(str, fatigue_hours))}:00")
    
    return {
        'optimal_load': sum(optimal_loads) / len(optimal_loads) if optimal_loads else 2,
        'fatigue_threshold': len(fatigue_hours),
        'recommendations': recommendations,
        'peak_hours': [h for h in range(24) if h not in fatigue_hours][:3]
    }


def _knowledge_gap_mapping(performance_data, exam_id):
    """
    Create a knowledge gap map showing interconnected weak areas
    """
    from collections import defaultdict, Counter
    
    # Topic relationship analysis
    topic_relationships = defaultdict(lambda: defaultdict(int))
    topic_performance = defaultdict(list)
    
    for item in performance_data:
        topic_performance[item.topic_name].append(item.is_correct)
    
    # Calculate topic mastery levels
    mastery_levels = {}
    for topic, results in topic_performance.items():
        accuracy = sum(r or 0 for r in results) / len(results) * 100 if results else 0
        if accuracy >= 80:
            mastery_levels[topic] = 'mastered'
        elif accuracy >= 60:
            mastery_levels[topic] = 'developing'
        else:
            mastery_levels[topic] = 'needs_work'
    
    # Identify critical gaps (topics that are prerequisites for others)
    critical_gaps = []
    developing_topics = []
    
    for topic, level in mastery_levels.items():
        if level == 'needs_work':
            critical_gaps.append(topic)
        elif level == 'developing':
            developing_topics.append(topic)
    
    # Priority ranking based on impact
    gap_priorities = []
    for gap in critical_gaps:
        impact_score = len([t for t in developing_topics if gap.lower() in t.lower()])
        gap_priorities.append({
            'topic': gap,
            'mastery_level': mastery_levels[gap],
            'impact_score': impact_score,
            'priority': 'high' if impact_score > 0 else 'medium'
        })
    
    gap_priorities.sort(key=lambda x: x['impact_score'], reverse=True)
    
    return {
        'critical_gaps': gap_priorities[:3],
        'mastery_distribution': dict(Counter(mastery_levels.values())),
        'recommended_sequence': [gap['topic'] for gap in gap_priorities[:5]]
    }


def _adaptive_difficulty_engine(analytics, user_id, exam_id):
    """
    ML-based adaptive difficulty system that adjusts in real-time
    """
    recent_performance = analytics.get('overall_performance', 0)
    learning_velocity = analytics.get('learning_velocity', 0)
    
    # Base difficulty adjustment
    if recent_performance >= 85 and learning_velocity > 2:
        suggested_difficulty = 'hard'
        confidence = 0.9
    elif recent_performance >= 70 and learning_velocity > 0:
        suggested_difficulty = 'medium'
        confidence = 0.8
    elif recent_performance < 50:
        suggested_difficulty = 'easy'
        confidence = 0.7
    else:
        suggested_difficulty = 'medium'
        confidence = 0.6
    
    # Adjust based on topic-specific performance
    weak_areas = analytics.get('weak_areas', [])
    if len(weak_areas) > 3:
        suggested_difficulty = 'easy'  # Focus on fundamentals
        confidence = 0.8
    
    return {
        'suggested_difficulty': suggested_difficulty,
        'confidence_score': confidence,
        'reasoning': f"Based on {recent_performance}% performance and {learning_velocity}% improvement rate",
        'next_adjustment_in': 5,  # questions
        'adaptive_parameters': {
            'performance_threshold': 75,
            'velocity_threshold': 1.5,
            'stability_required': 3  # sessions
        }
    }


def _motivation_and_engagement_analysis(user_id, exam_id, performance_data):
    """
    Analyze motivation patterns and engagement levels
    """
    from datetime import datetime, timedelta
    
    # Study session analysis
    session_gaps = []
    session_lengths = []
    
    if performance_data:
        sorted_data = sorted(performance_data, key=lambda x: x.completed_at)
        
        for i in range(1, len(sorted_data)):
            time_gap = (sorted_data[i].completed_at - sorted_data[i-1].completed_at).total_seconds() / 3600
            if time_gap < 24:  # Same day sessions
                session_gaps.append(time_gap)
        
        # Calculate session patterns
        avg_session_gap = sum(session_gaps) / len(session_gaps) if session_gaps else 0
        
        # Engagement metrics
        recent_week = datetime.utcnow() - timedelta(days=7)
        recent_questions = len([x for x in performance_data if x.completed_at > recent_week])
        
        # Motivation score based on consistency and recent activity
        consistency_score = min(100, (1 / (avg_session_gap + 1)) * 50) if avg_session_gap > 0 else 0
        activity_score = min(100, recent_questions * 2)
        motivation_score = (consistency_score + activity_score) / 2
        
        # Generate motivational insights
        insights = []
        if motivation_score > 70:
            insights.append("🔥 High motivation detected! You're on fire!")
        elif motivation_score > 40:
            insights.append("📈 Good study rhythm. Keep it up!")
        else:
            insights.append("💪 Let's rebuild that study momentum!")
        
        if recent_questions < 10:
            insights.append("📚 Try to answer at least 10 questions this week")
        
        return {
            'motivation_score': round(motivation_score, 1),
            'engagement_level': 'high' if motivation_score > 70 else 'medium' if motivation_score > 40 else 'low',
            'insights': insights,
            'recommended_actions': _generate_motivation_actions(motivation_score),
            'study_consistency': consistency_score
        }
    
    return {
        'motivation_score': 0,
        'engagement_level': 'new',
        'insights': ["Welcome! Let's start your learning journey!"],
        'recommended_actions': ["Take your first practice test"],
        'study_consistency': 0
    }


def _generate_motivation_actions(motivation_score):
    """Generate specific actions to boost motivation"""
    if motivation_score > 70:
        return [
            "Set a challenging weekly goal",
            "Try advanced difficulty questions",
            "Compete with friends or study groups"
        ]
    elif motivation_score > 40:
        return [
            "Maintain daily study streak",
            "Focus on weak areas",
            "Take a full mock test"
        ]
    else:
        return [
            "Start with 15-minute daily sessions",
            "Focus on easy questions to build confidence",
            "Set small, achievable daily goals"
        ]


def _personalized_review_scheduler(analytics, user_id, exam_id):
    """
    AI-powered spaced repetition scheduler
    """
    from datetime import datetime, timedelta
    
    # Ebbinghaus forgetting curve implementation
    def calculate_review_interval(mastery_level, previous_interval, success_rate):
        base_intervals = {
            'new': 1,      # 1 day
            'learning': 3,  # 3 days  
            'review': 7,   # 1 week
            'mastered': 30 # 1 month
        }
        
        interval = base_intervals.get(mastery_level, 1)
        
        # Adjust based on success rate
        if success_rate > 0.8:
            interval *= 1.5
        elif success_rate < 0.6:
            interval *= 0.7
        
        return max(1, int(interval))
    
    # Get topics that need review
    topic_performance = analytics.get('topic_performance', {})
    review_schedule = []
    
    for topic, perf_data in topic_performance.items():
        if perf_data['total'] > 0:
            success_rate = perf_data['correct'] / perf_data['total']
            
            # Determine mastery level
            if success_rate >= 0.9:
                mastery = 'mastered'
            elif success_rate >= 0.7:
                mastery = 'review'
            elif success_rate >= 0.5:
                mastery = 'learning'
            else:
                mastery = 'new'
            
            # Calculate next review date
            interval = calculate_review_interval(mastery, 1, success_rate)
            next_review = datetime.utcnow() + timedelta(days=interval)
            
            review_schedule.append({
                'topic': topic,
                'mastery_level': mastery,
                'success_rate': round(success_rate * 100, 1),
                'next_review_date': next_review.strftime('%Y-%m-%d'),
                'priority': 'high' if mastery == 'new' else 'medium' if mastery == 'learning' else 'low',
                'estimated_time': 20 if mastery == 'new' else 15 if mastery == 'learning' else 10
            })
    
    # Sort by priority and next review date
    review_schedule.sort(key=lambda x: (x['priority'] == 'low', x['next_review_date']))
    
    return {
        'scheduled_reviews': review_schedule[:10],  # Next 10 reviews
        'due_today': [r for r in review_schedule if r['next_review_date'] <= datetime.utcnow().strftime('%Y-%m-%d')],
        'overdue_count': len([r for r in review_schedule if r['next_review_date'] < datetime.utcnow().strftime('%Y-%m-%d')])
    }


def _exam_readiness_predictor(analytics, user_id, exam_id, exam_date=None):
    """
    Predict exam readiness using ML techniques
    """
    from datetime import datetime, timedelta
    
    # Collect readiness factors
    factors = {
        'overall_performance': analytics.get('overall_performance', 0),
        'consistency': analytics.get('study_consistency', 0),
        'weak_areas_count': len(analytics.get('weak_areas', [])),
        'total_questions': analytics.get('total_questions_attempted', 0),
        'learning_velocity': analytics.get('learning_velocity', 0),
        'recent_activity': analytics.get('recent_activity_score', 0)
    }
    
    # Weighted readiness calculation
    weights = {
        'overall_performance': 0.3,
        'consistency': 0.2,
        'weak_areas_count': -0.15,  # Negative weight
        'total_questions': 0.1,
        'learning_velocity': 0.2,
        'recent_activity': 0.15
    }
    
    # Normalize factors
    normalized_factors = {
        'overall_performance': min(100, factors['overall_performance']),
        'consistency': min(100, factors['consistency']),
        'weak_areas_count': max(0, 100 - factors['weak_areas_count'] * 10),
        'total_questions': min(100, factors['total_questions'] / 5),  # 500 questions = 100%
        'learning_velocity': max(0, min(100, factors['learning_velocity'] * 10 + 50)),
        'recent_activity': min(100, factors['recent_activity'])
    }
    
    # Calculate readiness score
    readiness_score = sum(normalized_factors[factor] * weight 
                         for factor, weight in weights.items())
    
    # Determine readiness level
    if readiness_score >= 85:
        readiness_level = 'exam_ready'
        message = "🎯 You're ready for the exam! Focus on final review."
    elif readiness_score >= 70:
        readiness_level = 'almost_ready'
        message = "📚 Almost there! Focus on weak areas and practice tests."
    elif readiness_score >= 50:
        readiness_level = 'developing'
        message = "📈 Good progress! Continue with structured study plan."
    else:
        readiness_level = 'needs_work'
        message = "💪 Keep studying! Focus on fundamentals and consistency."
    
    # Generate specific recommendations
    recommendations = []
    if normalized_factors['overall_performance'] < 70:
        recommendations.append("Improve overall accuracy with targeted practice")
    if normalized_factors['consistency'] < 60:
        recommendations.append("Build daily study habits")
    if factors['weak_areas_count'] > 5:
        recommendations.append("Focus on reducing weak areas")
    if factors['total_questions'] < 200:
        recommendations.append("Increase practice question volume")
    
    return {
        'readiness_score': round(readiness_score, 1),
        'readiness_level': readiness_level,
        'message': message,
        'recommendations': recommendations,
        'factor_breakdown': normalized_factors,
        'confidence_interval': 0.85 if readiness_score > 70 else 0.75
    }


# Enhanced version of your existing function with ML integration
def _generate_ai_powered_study_plan(analytics, learning_patterns, exam_id, exam, user_id):
    """
    Generate ML-powered study plan with advanced analytics
    """
    # Get advanced analytics
    learning_curve = _advanced_learning_curve_analysis(analytics.get('performance_data', []), user_id)
    cognitive_load = _cognitive_load_analysis(analytics.get('performance_data', []), user_id)
    knowledge_gaps = _knowledge_gap_mapping(analytics.get('performance_data', []), exam_id)
    adaptive_difficulty = _adaptive_difficulty_engine(analytics, user_id, exam_id)
    motivation_analysis = _motivation_and_engagement_analysis(user_id, exam_id, analytics.get('performance_data', []))
    review_schedule = _personalized_review_scheduler(analytics, user_id, exam_id)
    exam_readiness = _exam_readiness_predictor(analytics, user_id, exam_id)
    
    # Generate AI-powered tasks
    ai_tasks = []
    task_id = 1
    
    # Critical gap tasks (highest priority)
    for gap in knowledge_gaps['critical_gaps'][:2]:
        ai_tasks.append({
            "id": task_id,
            "task": f"🎯 **Critical Gap**: Master {gap['topic']} - Your weakest area with high impact",
            "type": "critical_gap",
            "estimated_time": 45,
            "priority": "critical",
            "topic": gap['topic'],
            "difficulty": "adaptive",
            "ai_reasoning": f"This topic has {gap['impact_score']} dependencies",
            "is_complete": False
        })
        task_id += 1
    
    # Adaptive difficulty task
    ai_tasks.append({
        "id": task_id,
        "task": f"🧠 **Adaptive Challenge**: {adaptive_difficulty['suggested_difficulty'].title()} level questions",
        "type": "adaptive_practice",
        "estimated_time": 30,
        "priority": "high",
        "difficulty": adaptive_difficulty['suggested_difficulty'],
        "ai_reasoning": adaptive_difficulty['reasoning'],
        "confidence": adaptive_difficulty['confidence_score'],
        "is_complete": False
    })
    task_id += 1
    
    # Spaced repetition tasks
    for review in review_schedule['due_today'][:2]:
        ai_tasks.append({
            "id": task_id,
            "task": f"🔄 **Spaced Review**: {review['topic']} (Success rate: {review['success_rate']}%)",
            "type": "spaced_repetition",
            "estimated_time": review['estimated_time'],
            "priority": review['priority'],
            "topic": review['topic'],
            "mastery_level": review['mastery_level'],
            "is_complete": False
        })
        task_id += 1
    
    # Cognitive load optimized task
    if cognitive_load['peak_hours']:
        ai_tasks.append({
            "id": task_id,
            "task": f"⚡ **Peak Performance**: Study during your optimal hours ({cognitive_load['peak_hours'][0]}:00-{cognitive_load['peak_hours'][0]+2}:00)",
            "type": "cognitive_optimization",
            "estimated_time": 60,
            "priority": "medium",
            "ai_reasoning": "Optimized for your cognitive load patterns",
            "is_complete": False
        })
        task_id += 1
    
    return {
        "ai_tasks": ai_tasks,
        "advanced_analytics": {
            "learning_curve": learning_curve,
            "cognitive_load": cognitive_load,
            "knowledge_gaps": knowledge_gaps,
            "adaptive_difficulty": adaptive_difficulty,
            "motivation_analysis": motivation_analysis,
            "review_schedule": review_schedule,
            "exam_readiness": exam_readiness
        }
    }


# New endpoint to get AI insights
def get_ai_study_insights(user_id, exam_id):
    """
    Get comprehensive AI-powered study insights
    """
    # This would integrate with your existing analytics
    analytics = {}  # Get from your existing function
    
    ai_insights = _generate_ai_powered_study_plan(analytics, {}, exam_id, {}, user_id)
    
    return {
        "success": True,
        "insights": ai_insights,
        "generated_at": datetime.utcnow().isoformat(),
        "confidence_score": 0.85
    }


def _generate_ai_powered_insights(performance_data, analytics, user_id, exam_id, exam, weekly_summaries=None):
    """
    Generate AI insights while preserving your existing analytics
    """
    # Get advanced analytics (from the previous artifact)
    learning_curve = _advanced_learning_curve_analysis(performance_data, user_id)
    cognitive_load = _cognitive_load_analysis(performance_data, user_id)
    knowledge_gaps = _knowledge_gap_mapping(performance_data, exam_id)
    adaptive_difficulty = _adaptive_difficulty_engine(analytics, user_id, exam_id)
    motivation_analysis = _motivation_and_engagement_analysis(user_id, exam_id, performance_data)
    review_schedule = _personalized_review_scheduler(analytics, user_id, exam_id)
    exam_readiness = _exam_readiness_predictor(analytics, user_id, exam_id)
    
    return {
        "learning_curve": learning_curve,
        "cognitive_load": cognitive_load,
        "knowledge_gaps": knowledge_gaps,
        "adaptive_difficulty": adaptive_difficulty,
        "motivation_analysis": motivation_analysis,
        "review_schedule": review_schedule,
        "exam_readiness": exam_readiness,
        "ai_confidence": 0.85
    }

def _generate_hybrid_tasks(analytics, learning_patterns, difficulty_recommendations,
                           study_hours, focus_areas, exam_id, exam, ai_analytics):
    """
    Hybrid task generation combining existing exam-specific tasks with AI insights,
    augmented with calendar-friendly fields for the UI (day/start_date/scheduled_date/order).
    """

    # 1) Start with your existing generator (which may or may not already add day/dates)
    existing_tasks = _generate_exam_specific_tasks(
        analytics, learning_patterns, difficulty_recommendations,
        study_hours, focus_areas, exam_id, exam
    ) or []

    base_date = datetime.utcnow().date()

    # Normalize existing tasks so the calendar always has required fields
    normalized = []
    max_day = 0
    max_id = 0
    for idx, t in enumerate(existing_tasks, start=1):
        task = dict(t)  # shallow copy

        # id
        if "id" not in task or task["id"] is None:
            task["id"] = idx
        try:
            max_id = max(max_id, int(task["id"]))
        except Exception:
            # if non-numeric, just leave max_id as-is; we'll base new ids on len()
            pass

        # day
        day_val = task.get("day")
        if not isinstance(day_val, int) or day_val < 1:
            day_val = idx
            task["day"] = day_val

        # scheduled date
        sd = task.get("scheduled_date") or task.get("start_date")
        if not sd:
            scheduled = base_date + timedelta(days=day_val - 1)
            sd = scheduled.isoformat()
            task["start_date"] = sd
            task["scheduled_date"] = sd
        else:
            # ensure both keys exist if one is present
            task.setdefault("start_date", sd)
            task.setdefault("scheduled_date", sd)

        # order
        task.setdefault("order", idx)

        # flags
        task.setdefault("exam_specific", True)
        task.setdefault("is_organization_task", False)

        normalized.append(task)
        max_day = max(max_day, day_val if isinstance(day_val, int) else 0)

    # 2) Build AI-powered tasks (robust to missing keys)
    ai_tasks = []
    next_id = (max_id + 1) if max_id else (len(normalized) + 1)
    next_day = (max_day + 1) if max_day else (len(normalized) + 1)

    ai = ai_analytics or {}
    knowledge_gaps = (ai.get("knowledge_gaps") or {})
    critical_gaps = (knowledge_gaps.get("critical_gaps") or [])

    # Critical gap task
    if critical_gaps:
        topic = critical_gaps[0].get("topic", "a critical topic")
        impact = critical_gaps[0].get("impact_score", "multiple")
        ai_tasks.append({
            "id": next_id,
            "task": f"🎯 **AI Recommendation**: Focus on {topic} (High Impact Area)",
            "type": "ai_critical_gap",
            "estimated_time": 30,
            "priority": "critical",
            "topic": topic,
            "difficulty": "adaptive",
            "ai_reasoning": f"This topic affects {impact} other areas",
            "is_complete": False,
            "exam_specific": True
        })
        next_id += 1

    # Cognitive load optimization task
    cog = (ai.get("cognitive_load") or {})
    peak_hours = (cog.get("peak_hours") or [])
    if peak_hours:
        try:
            h = int(peak_hours[0])
            start_str = f"{h:02d}:00"
            end_str = f"{(h + 2) % 24:02d}:00"
            hours_label = f"{start_str}-{end_str}"
        except Exception:
            # fallback to raw
            hours_label = f"{peak_hours[0]}:00-{peak_hours[0]}+2:00" if isinstance(peak_hours[0], (int, float)) else str(peak_hours[0])

        ai_tasks.append({
            "id": next_id,
            "task": f"⚡ **AI Timing**: Study during your peak hours ({hours_label})",
            "type": "ai_cognitive_optimization",
            "estimated_time": 60,
            "priority": "medium",
            "ai_reasoning": "Optimized for your cognitive performance patterns",
            "is_complete": False,
            "exam_specific": True
        })
        next_id += 1

    # Spaced repetition task(s)
    review_sched = (ai.get("review_schedule") or {})
    due_reviews = (review_sched.get("due_today") or [])
    for review in due_reviews[:1]:  # add at most one
        ai_tasks.append({
            "id": next_id,
            "task": f"🔄 **AI Review**: Spaced repetition for {review.get('topic', 'selected topic')} "
                    f"(Success: {review.get('success_rate', 0)}%)",
            "type": "ai_spaced_repetition",
            "estimated_time": review.get("estimated_time", 20),
            "priority": review.get("priority", "medium"),
            "topic": review.get("topic"),
            "mastery_level": review.get("mastery_level"),
            "is_complete": False,
            "exam_specific": True
        })
        next_id += 1

    # 3) Calendar-friendly augmentation for AI tasks (continue after existing days)
    for i, task in enumerate(ai_tasks, start=0):
        day_num = next_day + i
        task["day"] = day_num
        scheduled = base_date + timedelta(days=day_num - 1)
        sd = scheduled.isoformat()
        task["start_date"] = sd
        task["scheduled_date"] = sd
        task["order"] = len(normalized) + i + 1
        task["is_organization_task"] = False  # distinguish from org plan items

    # 4) Return merged list
    return normalized + ai_tasks

@student_api_bp.route('/study-plan/ai-insights/<int:exam_id>', methods=['GET'])
@student_required()
def get_ai_study_insights(current_user, exam_id, **kwargs):
    """
    Get detailed AI insights for the study plan
    """
    try:
        user_id = current_user.id
        
        # Get performance data (reuse your existing logic)
        performance_data = db.session.query(
            Subject.name.label('subject_name'),
            Topic.name.label('topic_name'),
            Question.difficulty_level,
            StudentQuestionResponse.is_correct,
            StudentQuestionResponse.time_taken,
            StudentTestAttempt.completed_at,
            StudentTestAttempt.score,
            Question.id.label('question_id'),
            MockTest.title.label('test_name')
        ).select_from(StudentQuestionResponse)\
         .join(StudentTestAttempt, StudentTestAttempt.id == StudentQuestionResponse.attempt_id)\
         .join(MockTest, MockTest.id == StudentTestAttempt.mock_test_id)\
         .join(Question, Question.id == StudentQuestionResponse.question_id)\
         .join(Topic, Topic.id == Question.topic_id)\
         .join(Subject, Subject.id == Topic.subject_id)\
         .filter(
            StudentTestAttempt.student_user_id == user_id,
            MockTest.exam_id == exam_id,
            StudentTestAttempt.status == 'completed',
            StudentTestAttempt.completed_at >= (datetime.utcnow() - timedelta(days=365))
         ).order_by(StudentTestAttempt.completed_at.asc()).all()
        
        if not performance_data:
            return jsonify({"success": False, "message": "No performance data available"}), 404
        
        # Get your existing analytics
        analytics = _analyze_exam_performance(performance_data, exam_id)
        exam = Exam.query.get(exam_id)
        
        # Generate AI insights
        ai_insights = _generate_ai_powered_insights(performance_data, analytics, user_id, exam_id, exam)
        
        return jsonify({
            "success": True,
            "ai_insights": ai_insights,
            "generated_at": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting AI insights: {e}")
        return jsonify({"success": False, "message": "Could not generate AI insights"}), 500


# 5. OPTIONAL: Add feature flag to enable/disable AI features
def _check_ai_features_enabled(user_id, exam_id):
    """
    Check if AI features are enabled for this user/exam
    """
    # You can add this as a user preference or organization setting
    # For now, return True to enable for everyone
    return True

def _get_organization_study_plan(exam_id, user_id, exam):
    """
    Get the organization's predefined study plan for this exam,
    augmented with a calculated start date for each task so the calendar can plot them.

    Returns:
        (Response, int): Flask JSON response and HTTP status.
    """
    try:
        # Eagerly load relationships: StudyPlan → StudyPlanItem → Topic, MockTest
        study_plan = (
            StudyPlan.query.options(
                joinedload(StudyPlan.items).joinedload(StudyPlanItem.topic),
                joinedload(StudyPlan.items).joinedload(StudyPlanItem.mock_test),
            )
            .filter_by(exam_id=exam_id)
            .first()
        )

        if not study_plan:
            return jsonify({"success": False, "message": "No organization study plan available."}), 404

        # Collect item IDs for this plan (to scope completion correctly)
        plan_item_ids = {it.id for it in study_plan.items}

        # Get student's completed progress on THIS study plan only
        completed_item_ids = set()
        if plan_item_ids:
            completed_rows = (
                db.session.query(StudentStudyPlanProgress.study_plan_item_id)
                .filter(
                    StudentStudyPlanProgress.student_user_id == user_id,
                    StudentStudyPlanProgress.is_completed.is_(True),
                    StudentStudyPlanProgress.study_plan_item_id.in_(plan_item_ids),
                )
                .all()
            )
            completed_item_ids = {row[0] for row in completed_rows}

        # Build tasks with full details + calendar date
        tasks = []
        today = datetime.utcnow().date()  # base start date for Day 1

        # Sort by (day_number asc, order asc/nulls last)
        sorted_items = sorted(study_plan.items, key=lambda x: (x.day_number or 0, x.order or 0))

        for item in sorted_items:
            day_num = item.day_number or 1

            # Compute scheduled date for the calendar: today + (day - 1)
            scheduled_date = today + timedelta(days=day_num - 1)

            topic_name = item.topic.name if getattr(item, "topic", None) else "General"
            mock_test_title = item.mock_test.title if getattr(item, "mock_test", None) else None

            # Human-friendly task text, preserving your previous format
            base_desc = (item.description or "Study task").strip()
            if mock_test_title:
                task_description = f"{base_desc} (Mock Test: {mock_test_title})"
            elif topic_name and topic_name != "General":
                task_description = f"{base_desc} (Topic: {topic_name})"
            else:
                task_description = base_desc

            is_complete = item.id in completed_item_ids

            tasks.append({
                "id": item.id,
                "study_plan_item_id": item.id,
                "day": day_num,
                # Calendar fields (both for compatibility with different front-ends)
                "start_date": scheduled_date.isoformat(),       # e.g., "2025-09-16"
                "scheduled_date": scheduled_date.isoformat(),   # same value; many UIs read this key
                # Display fields
                "task": f"📋 {task_description}",
                "type": item.item_type,
                "estimated_time": item.estimated_time_minutes or 30,
                "priority": "high" if day_num == 1 else "medium",
                "topic": topic_name,
                "mock_test": mock_test_title,
                "difficulty": item.difficulty_level or "medium",
                "order": item.order or 0,
                "is_complete": is_complete,
                "is_organization_task": True,  # so the client can toggle completion correctly
                "exam_specific": True,
            })

        # Progress stats
        total_items = len(tasks)
        completed_count = sum(1 for t in tasks if t["is_complete"])
        completion_percentage = (completed_count / total_items * 100.0) if total_items else 0.0

        # Study streak (safe)
        try:
            study_streak = _calculate_study_streak(user_id, exam_id)
        except Exception as e:
            current_app.logger.warning(f"Study streak calculation failed: {e}")
            study_streak = {"current_streak": 0, "message": "No streak data"}

        # Safe exam/org names
        exam_name = getattr(exam, "name", None) or "Unnamed Exam"
        org_name = getattr(getattr(exam, "organization", None), "name", None) or "N/A"

        # Today's focus = tasks scheduled for Day 1 (limit 5 like before)
        todays_focus = [t for t in tasks if t["day"] == 1][:5]

        # Response structure preserved from your previous helper (so UI keeps working)
        payload = {
            "success": True,
            "study_plan": {
                "exam_info": {
                    "exam_name": exam_name,
                    "exam_id": exam_id,
                    "organization": org_name,
                },
                "reminder_message": f"🏫 **{study_plan.name}** - Follow your organization's structured study plan for {exam_name}",
                "todays_focus": todays_focus,
                "all_tasks": tasks,  # calendar will use start_date/scheduled_date
                "analytics": {
                    "overall_performance": 0,
                    "strengths": [],
                    "improvement_areas": [],
                    "learning_velocity": 0,
                    "recommended_study_time": "2 hours",
                    "difficulty_level": "medium",
                    "completion_percentage": round(completion_percentage, 1),
                    "completed_tasks": completed_count,
                    "total_tasks": total_items,
                },
                "progress_insights": [
                    {
                        "type": "organization_plan",
                        "message": f"📊 You've completed {completed_count} out of {total_items} tasks ({completion_percentage:.1f}%)",
                        "action": "Continue following your organization's structured plan.",
                    }
                ],
                "next_milestones": [
                    {
                        "title": "Plan Completion",
                        "description": f"Complete all {total_items} tasks in the organization plan",
                        "progress": round(completion_percentage, 1),
                        "target": 100,
                        "reward": "Ready for exam!",
                    }
                ],
                "study_streak": study_streak,
                "personalization": {
                    "optimal_study_time": [],
                    "question_pace": 0,
                    "retention_rate": 0,
                },
                "plan_type": "organization",
            },
        }

        return jsonify(payload), 200

    except Exception as e:
        current_app.logger.error(f"Error getting organization study plan: {e}\n{traceback.format_exc()}")
        return jsonify({"success": False, "message": "Could not fetch organization plan."}), 500

def _analyze_exam_performance(performance_data, exam_id):
    """Analyze performance specifically for this exam"""
    
    # Group by subject and topic for this exam
    subject_performance = defaultdict(lambda: {'correct': 0, 'total': 0, 'time_spent': 0, 'recent_performance': []})
    topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0, 'difficulty_distribution': defaultdict(int), 'last_seen': datetime.min, 'trend': []})
    
    # Track test scores for this exam
    test_scores = []
    
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    
    for item in performance_data:
        # Subject analysis
        subject_performance[item.subject_name]['total'] += 1
        subject_performance[item.subject_name]['time_spent'] += item.time_taken or 0
        if item.is_correct:
            subject_performance[item.subject_name]['correct'] += 1
        
        if item.completed_at > recent_cutoff:
            subject_performance[item.subject_name]['recent_performance'].append(item.is_correct)
        
        # Topic analysis
        topic_performance[item.topic_name]['total'] += 1
        topic_performance[item.topic_name]['difficulty_distribution'][item.difficulty_level or 'medium'] += 1
        if item.is_correct:
            topic_performance[item.topic_name]['correct'] += 1
        
        if item.completed_at > topic_performance[item.topic_name]['last_seen']:
            topic_performance[item.topic_name]['last_seen'] = item.completed_at
            
        # Track performance trend over time
        topic_performance[item.topic_name]['trend'].append({
            'date': item.completed_at,
            'correct': item.is_correct,
            'difficulty': item.difficulty_level
        })
        
        # Collect test scores
        if hasattr(item, 'score') and item.score:
            test_scores.append(item.score)
    
    # Calculate metrics
    overall_correct = sum(s['correct'] for s in subject_performance.values())
    overall_total = sum(s['total'] for s in subject_performance.values())
    overall_performance = (overall_correct / overall_total * 100) if overall_total > 0 else 0
    
    # Get latest test score
    latest_exam_score = max(test_scores) if test_scores else 0
    
    # Identify strengths and weaknesses
    subject_accuracies = [(subj, (data['correct'] / data['total'] * 100)) 
                         for subj, data in subject_performance.items() if data['total'] > 0]
    subject_accuracies.sort(key=lambda x: x[1], reverse=True)
    
    topic_accuracies = [(topic, (data['correct'] / data['total'] * 100)) 
                       for topic, data in topic_performance.items() if data['total'] > 0]
    topic_accuracies.sort(key=lambda x: x[1])
    
    return {
        'overall_performance': round(overall_performance, 2),
        'subject_performance': dict(subject_performance),
        'topic_performance': dict(topic_performance),
        'top_strengths': [subj for subj, acc in subject_accuracies[:5]],
        'weak_areas': [topic for topic, acc in topic_accuracies[:5]],
        'subject_accuracies': subject_accuracies,
        'topic_accuracies': topic_accuracies,
        'total_questions_attempted': overall_total,
        'latest_exam_score': latest_exam_score,
        'exam_id': exam_id
    }


def _generate_exam_specific_tasks(analytics, learning_patterns, difficulty_recommendations, 
                                  study_hours, focus_areas, exam_id, exam):
    """Generate tasks specific to this exam with calendar-friendly dates and ordering."""

    tasks = []
    task_id = 1

    # Time allocation based on study hours
    time_blocks = {
        1: {'review': 20, 'practice': 30, 'challenge': 10},
        2: {'review': 30, 'practice': 60, 'challenge': 30},
        3: {'review': 45, 'practice': 90, 'challenge': 45},
        4: {'review': 60, 'practice': 120, 'challenge': 60}
    }
    try:
        sh = int(study_hours) if study_hours is not None else 2
    except Exception:
        sh = 2
    time_allocation = time_blocks.get(sh, time_blocks[2])

    # Safe reads
    analytics = analytics or {}
    difficulty_recommendations = difficulty_recommendations or {}
    weak_areas = (analytics.get('weak_areas') or [])[:3]
    strong_areas = (analytics.get('top_strengths') or [])[:2]
    current_level = difficulty_recommendations.get('current_level', 'medium')
    exam_name = getattr(exam, 'name', None) or 'Your Exam'

    # Task 1: Exam-specific weakness improvement
    if weak_areas:
        tasks.append({
            "id": task_id,
            "task": f"🎯 **{exam_name} Focus**: Deep dive into {weak_areas[0]}. Study core concepts and complete 15 practice questions.",
            "type": "weakness_focus",
            "estimated_time": time_allocation['practice'],
            "priority": "high",
            "topic": weak_areas[0],
            "difficulty": "medium",
            "is_complete": False,
            "exam_specific": True
        })
        task_id += 1

    # Task 2: Exam pattern practice
    tasks.append({
        "id": task_id,
        "task": f"📝 **{exam_name} Pattern Practice**: Take a mock test following the exact pattern and timing of {exam_name}.",
        "type": "exam_pattern",
        "estimated_time": 45,
        "priority": "high",
        "topic": "full exam simulation",
        "difficulty": current_level,
        "is_complete": False,
        "exam_specific": True
    })
    task_id += 1

    # Task 3: Strength maintenance
    if strong_areas:
        tasks.append({
            "id": task_id,
            "task": f"🔄 **Strength Maintenance**: Quick review of {strong_areas[0]} to maintain your edge in {exam_name}.",
            "type": "strength_maintenance",
            "estimated_time": time_allocation['review'],
            "priority": "medium",
            "topic": strong_areas[0],
            "difficulty": "easy",
            "is_complete": False,
            "exam_specific": True
        })
        task_id += 1

    # Task 4: Custom focus for this exam
    if focus_areas:
        tasks.append({
            "id": task_id,
            "task": f"📚 **{exam_name} Custom Focus**: Dedicated study session on {focus_areas[0]}. Complete 20 questions from {exam_name} syllabus.",
            "type": "custom_focus",
            "estimated_time": 30,
            "priority": "high",
            "topic": focus_areas[0],
            "difficulty": current_level,
            "is_complete": False,
            "exam_specific": True
        })
        task_id += 1

    # ---- Calendar-friendly augmentation ----
    base_date = datetime.utcnow().date()  # Day 1 = today (UTC)
    for idx, t in enumerate(tasks, start=1):
        # Consecutive days: 1, 2, 3, ...
        t["day"] = idx
        scheduled = base_date + timedelta(days=idx - 1)
        # Provide both keys for front-end compatibility
        t["start_date"] = scheduled.isoformat()      # e.g. "2025-09-16"
        t["scheduled_date"] = t["start_date"]
        t["order"] = idx
        t["is_organization_task"] = False  # distinguish from org plan items

    return tasks


def _calculate_study_streak(user_id, exam_id):
    """Calculate study streak for specific exam"""
    
    # Get recent study sessions for this exam
    recent_sessions = db.session.query(
        func.date(StudentTestAttempt.completed_at).label('study_date')
    ).join(MockTest, MockTest.id == StudentTestAttempt.mock_test_id)\
     .filter(
        StudentTestAttempt.student_user_id == user_id,
        MockTest.exam_id == exam_id,
        StudentTestAttempt.status == 'completed'
    ).distinct().order_by(func.date(StudentTestAttempt.completed_at).desc()).limit(30).all()
    
    if not recent_sessions:
        return {"current_streak": 0, "longest_streak": 0, "message": "Start your streak today!"}
    
    # Calculate current streak
    current_streak = 0
    today = datetime.utcnow().date()
    
    for session in recent_sessions:
        expected_date = today - timedelta(days=current_streak)
        if session.study_date == expected_date:
            current_streak += 1
        else:
            break
    
    return {
        "current_streak": current_streak,
        "longest_streak": len(recent_sessions),
        "message": f"🔥 {current_streak} day streak for this exam!" if current_streak > 0 else "Start your exam streak today!"
    }


def _generate_beginner_plan(exam_id, exam):
    """Generate beginner plan for specific exam with calendar-friendly fields."""

    # Safe names
    exam_name = getattr(exam, "name", None) or "Your Exam"
    org_name = getattr(getattr(exam, "organization", None), "name", None) or "N/A"

    # Base "today" in UTC (Day 1)
    today = datetime.utcnow().date()

    # Original 3 onboarding tasks (kept as "today's focus")
    todays_focus = [
        {
            "id": 1,
            "task": f"📋 Complete your first {exam_name} diagnostic test",
            "type": "diagnostic",
            "estimated_time": 30,
            "priority": "high",
            "is_complete": False,
            "exam_specific": True
        },
        {
            "id": 2,
            "task": f"📚 Explore {exam_name} study materials and syllabus",
            "type": "exploration",
            "estimated_time": 15,
            "priority": "medium",
            "is_complete": False,
            "exam_specific": True
        },
        {
            "id": 3,
            "task": f"🎯 Set your {exam_name} study goals and timeline",
            "type": "goal_setting",
            "estimated_time": 10,
            "priority": "medium",
            "is_complete": False,
            "exam_specific": True
        }
    ]
    def enrich_for_calendar(task, day, order):
        scheduled = today + timedelta(days=day - 1)
        t = dict(task)  # shallow copy to avoid mutating originals
        t.update({
            "day": day,
            "start_date": scheduled.isoformat(),
            "scheduled_date": scheduled.isoformat(),
            "order": order,
            "is_organization_task": False
        })
        return t

    # For a beginner plan, all three items are intended for "today".
    # (If you prefer to spread them over 3 days, change day to 1,2,3 respectively.)
    enriched_todays_focus = [
        enrich_for_calendar(t, day=1, order=i+1) for i, t in enumerate(todays_focus)
    ]

    # Provide all_tasks so the calendar has an event source
    all_tasks = list(enriched_todays_focus)

    return jsonify({
        "success": True,
        "study_plan": {
            "exam_info": {
                "exam_name": exam_name,
                "exam_id": exam_id,
                "organization": org_name
            },
            "reminder_message": f"🚀 Welcome to your {exam_name} study journey! Let's start with some diagnostic tests to understand your current level.",
            "todays_focus": enriched_todays_focus,   # now includes day/start_date/scheduled_date/order
            "all_tasks": all_tasks,                  # calendar will read from here
            "analytics": {
                "overall_performance": 0,
                "message": f"Complete your first {exam_name} test to see your analytics!"
            },
            "progress_insights": [
                {
                    "type": "welcome",
                    "message": f"🎉 Welcome to your personalized {exam_name} study experience!",
                    "action": "Take your first diagnostic test to get started."
                }
            ],
            # Optional extras your UI may show; harmless defaults if unused:
            "study_streak": {"current_streak": 0, "message": "No streak yet — start today!"},
            "personalization": {"optimal_study_time": [], "question_pace": 0, "retention_rate": 0},
            "plan_type": "beginner"
        }
    }), 200

# Add these helper functions to your backend code

def _identify_learning_patterns(performance_data, user_id):
    """Identify learning patterns from performance data"""
    if not performance_data:
        return {
            'learning_velocity': 0,
            'optimal_time_slots': [],
            'average_time_per_question': 0,
            'retention_rate': 0
        }
    
    # Calculate learning velocity (improvement over time)
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    old_cutoff = datetime.utcnow() - timedelta(days=14)
    
    recent_performance = [item for item in performance_data if item.completed_at > recent_cutoff]
    old_performance = [item for item in performance_data if old_cutoff < item.completed_at <= recent_cutoff]
    
    recent_accuracy = sum(1 for item in recent_performance if item.is_correct) / len(recent_performance) * 100 if recent_performance else 0
    old_accuracy = sum(1 for item in old_performance if item.is_correct) / len(old_performance) * 100 if old_performance else 0
    
    learning_velocity = recent_accuracy - old_accuracy
    
    # Calculate optimal time slots (analyze performance by hour)
    time_performance = defaultdict(list)
    for item in performance_data:
        hour = item.completed_at.hour
        time_performance[hour].append(item.is_correct)
    
    optimal_hours = []
    for hour, results in time_performance.items():
        if len(results) >= 5:  # Minimum attempts for statistical significance
            accuracy = sum(1 for r in results if r is True) / len(results) * 100 if results else 0
            if accuracy > 70:  # Good performance threshold
                optimal_hours.append(f"{hour:02d}:00")
    
    # Calculate average time per question
    time_data = [item.time_taken for item in performance_data if item.time_taken]
    average_time = sum(time_data) / len(time_data) if time_data else 0
    
    # Calculate retention rate (simplified)
    total_attempts = len(performance_data)
    correct_attempts = sum(1 for item in performance_data if item.is_correct)
    retention_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        'learning_velocity': round(learning_velocity, 2),
        'optimal_time_slots': optimal_hours[:3],  # Top 3 time slots
        'average_time_per_question': round(average_time, 2),
        'retention_rate': round(retention_rate, 2)
    }


def _calculate_optimal_difficulty(analytics, difficulty_preference):
    """Calculate optimal difficulty based on performance and preference"""
    overall_performance = analytics.get('overall_performance', 0)
    
    if difficulty_preference == 'easy':
        base_level = 'easy'
    elif difficulty_preference == 'hard':
        base_level = 'hard'
    else:  # balanced
        if overall_performance >= 80:
            base_level = 'hard'
        elif overall_performance >= 60:
            base_level = 'medium'
        else:
            base_level = 'easy'
    
    return {
        'current_level': base_level,
        'next_level': 'hard' if base_level == 'medium' else 'medium',
        'recommendation': f"Based on your {overall_performance}% performance, {base_level} level is optimal"
    }


def _generate_progress_insights(analytics, user_id, exam):
    """Generate progress insights for the student"""
    insights = []
    
    overall_performance = analytics.get('overall_performance', 0)
    
    # Performance-based insights
    if overall_performance >= 80:
        insights.append({
            'type': 'success',
            'message': f'🎉 Excellent performance! You\'re scoring {overall_performance}% on average.',
            'action': 'Keep up the great work and focus on challenging questions.'
        })
    elif overall_performance >= 60:
        insights.append({
            'type': 'progress',
            'message': f'📈 Good progress! You\'re at {overall_performance}% accuracy.',
            'action': 'Focus on weak areas to push your score higher.'
        })
    else:
        insights.append({
            'type': 'encouragement',
            'message': f'🎯 Building foundation with {overall_performance}% accuracy.',
            'action': 'Focus on understanding core concepts before attempting difficult questions.'
        })
    
    # Weak areas insights
    weak_areas = analytics.get('weak_areas', [])
    if weak_areas:
        insights.append({
            'type': 'warning',
            'message': f'⚠️ Focus needed in: {", ".join(weak_areas[:2])}',
            'action': 'Spend extra time on these topics today.'
        })
    
    # Strengths insights
    strengths = analytics.get('top_strengths', [])
    if strengths:
        insights.append({
            'type': 'positive',
            'message': f'💪 Strong performance in: {", ".join(strengths[:2])}',
            'action': 'Use these strengths to boost confidence.'
        })
    
    return insights


def _generate_spaced_repetition_tasks(analytics, user_id, exam_id):
    """Generate spaced repetition tasks based on previous performance"""
    tasks = []
    
    # Get topics that need review (answered incorrectly in the past)
    weak_topics = analytics.get('weak_areas', [])
    
    for i, topic in enumerate(weak_topics[:2]):  # Limit to 2 spaced repetition tasks
        tasks.append({
            'id': f'sr_{i+1}',
            'task': f'🔄 **Spaced Repetition**: Review {topic} concepts you struggled with before',
            'type': 'spaced_repetition',
            'estimated_time': 20,
            'priority': 'medium',
            'topic': topic,
            'difficulty': 'review',
            'is_complete': False,
            'exam_specific': True
        })
    
    return tasks


def _generate_milestones(analytics, exam):
    """Generate milestones based on current performance"""
    milestones = []
    
    overall_performance = analytics.get('overall_performance', 0)
    total_questions = analytics.get('total_questions_attempted', 0)
    
    # Performance milestone
    if overall_performance < 70:
        milestones.append({
            'title': 'Reach 70% Accuracy',
            'description': 'Improve your overall accuracy to 70%',
            'progress': overall_performance,
            'target': 70,
            'reward': 'Unlock advanced practice questions'
        })
    elif overall_performance < 85:
        milestones.append({
            'title': 'Achieve Excellence',
            'description': 'Reach 85% accuracy across all topics',
            'progress': overall_performance,
            'target': 85,
            'reward': 'Ready for the actual exam!'
        })
    
    # Question milestone
    if total_questions < 100:
        milestones.append({
            'title': 'Practice Champion',
            'description': 'Complete 100 practice questions',
            'progress': total_questions,
            'target': 100,
            'reward': 'Detailed analytics unlock'
        })
    elif total_questions < 500:
        milestones.append({
            'title': 'Question Master',
            'description': 'Complete 500 practice questions',
            'progress': total_questions,
            'target': 500,
            'reward': 'Advanced study techniques'
        })
    
    return milestones


def _generate_motivational_message(analytics, progress_insights, exam):
    """Generate a motivational message based on current state"""
    overall_performance = analytics.get('overall_performance', 0)
    exam_name = exam.name
    
    if overall_performance >= 80:
        return f"🌟 **Outstanding Progress!** You're excelling in {exam_name} with {overall_performance}% accuracy. Keep pushing for perfection!"
    elif overall_performance >= 60:
        return f"🚀 **Great Momentum!** Your {exam_name} preparation is on track at {overall_performance}%. Focus on weak areas to reach the next level!"
    elif overall_performance > 0:
        return f"💪 **Building Strong Foundation!** You're making progress in {exam_name} with {overall_performance}% accuracy. Every question brings you closer to success!"
    else:
        return f"🎯 **Ready to Begin!** Your {exam_name} journey starts now. Take your first practice test to see where you stand!"

@student_api_bp.route('/study-plan/mark-complete/<int:exam_id>/<int:task_id>', methods=['POST'])
@student_required()
def mark_exam_task_complete(current_user, exam_id, task_id, **kwargs):
    """Mark an exam-specific study plan task as complete"""
    try:
        data = request.get_json() or {}
        is_organization_task = data.get('is_organization_task', False)
        
        if is_organization_task:
            # Update organization study plan progress
            progress = StudentStudyPlanProgress.query.filter_by(
                student_user_id=current_user.id,
                study_plan_item_id=task_id
            ).first()
            
            if not progress:
                progress = StudentStudyPlanProgress(
                    student_user_id=current_user.id,
                    study_plan_item_id=task_id,
                    is_completed=True,
                    completed_at=datetime.utcnow()
                )
                db.session.add(progress)
            else:
                progress.is_completed = True
                progress.completed_at = datetime.utcnow()
            
            db.session.commit()
        
        # In a real implementation, you'd also store personal task completions
        
        return jsonify({
            "success": True,
            "message": "Task marked as complete!",
            "points_earned": 10,
            "streak_updated": True,
            "exam_id": exam_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error marking exam task complete: {e}")
        return jsonify({"success": False, "message": "Could not update task."}), 500


@student_api_bp.route('/study-plan/student-exams', methods=['GET'])
@student_required()
def get_student_exams(current_user, **kwargs):
    try:
        # Get the current organization from the subdomain context
        current_organization = g.current_organization
        
        if not current_organization:
            return jsonify({
                "success": False, 
                "message": "No organization found for this subdomain."
            }), 400
        
        # Check if student has active membership in this organization
        membership = OrganizationMembership.query.filter_by(
            user_id=current_user.id,
            organization_id=current_organization.id,
            is_active=True
        ).first()
        
        if not membership:
            return jsonify({
                "success": False,
                "message": "You don't have access to this organization."
            }), 403
        
        # Query only exams from the current organization where the student is enrolled
        student_exams = db.session.query(Exam).join(
            StudentExam, StudentExam.exam_id == Exam.id
        ).filter(
            StudentExam.student_user_id == current_user.id,
            StudentExam.access_status.in_(['purchased', 'free_access', 'admin_granted']),
            Exam.organization_id == current_organization.id,  # ✅ Only current org's exams
            current_organization.status == 'active'
        ).all()
        
        exams_data = []
        for exam in student_exams:
            exams_data.append({
                "id": exam.id,
                "name": exam.name,
                "organization": exam.organization.name if exam.organization else "N/A",
                "description": exam.description or "",
                "has_organization_plan": StudyPlan.query.filter_by(exam_id=exam.id).first() is not None
            })
        
        return jsonify({
            "success": True,
            "exams": exams_data
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting student exams: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Could not fetch exams."}), 500
    
@student_api_bp.route('/study-plan/all-plans-for-exam/<int:exam_id>', methods=['GET'])
@student_required()
def get_all_study_plans_for_exam(current_user, exam_id, **kwargs):
    """
    Fetches both the AI-generated personal plan and the official organization
    plan for a given exam.
    """
    all_plans = []
    
    # 1. Generate the Personal AI Plan (reusing your existing logic)
    try:
        # This is a simplified version of your advanced generator for this context
        analytics = _analyze_exam_performance(performance_data, exam_id) # You'd need to get performance_data
        # For simplicity, we'll create a placeholder personal plan. 
        # You can integrate your full _generate_... logic here.
        personal_plan = {
            "name": "My Personal AI Plan",
            "type": "personal",
            "reminder_message": "Your AI-powered plan is ready.",
            "todays_focus": [{"task": "Focus on your weakest areas.", "completed": False}]
        }
        all_plans.append(personal_plan)
    except Exception as e:
        current_app.logger.error(f"Could not generate personal plan: {e}")

    # 2. Fetch the Official Organization Plan
    org_plan_record = StudyPlan.query.filter_by(exam_id=exam_id).first()
    if org_plan_record:
        official_plan = {
            "name": org_plan_record.name or "Organization Plan",
            "type": "official",
            "description": org_plan_record.description,
            "items": [{"day": item.day_number, "description": item.description} for item in org_plan_record.items]
        }
        all_plans.append(official_plan)

    return jsonify(all_plans), 200

@student_api_bp.route('/questions/<int:question_id>/report', methods=['POST'])
@student_required()
def report_question(current_user, question_id, **kwargs):
    data = request.get_json()
    reason = data.get('reason')
    if not reason:
        return jsonify({"message": "A reason for the report is required."}), 400

    # Prevent duplicate reports from the same user for the same question
    existing_report = ReportedContent.query.filter_by(
        question_id=question_id, 
        reported_by_user_id=current_user.id
    ).first()
    if existing_report:
        return jsonify({"message": "You have already reported this question."}), 409

    report = ReportedContent(
        question_id=question_id,
        reported_by_user_id=current_user.id,
        reason=reason,
        comments=data.get('comments')
    )
    db.session.add(report)
    db.session.commit()
    
    return jsonify({"message": "Thank you! The question has been reported for review."}), 200

@student_api_bp.route('/organizations/<int:org_id>/report', methods=['POST'])
@student_required()
def report_organization(current_user, org_id, **kwargs):
    data = request.get_json()
    reason = data.get('reason')
    if not reason:
        return jsonify({"message": "A reason is required to report an organization."}), 400

    report = OrganizationReport(
        organization_id=org_id,
        reported_by_user_id=current_user.id,
        reason=reason,
        comments=data.get('comments')
    )
    db.session.add(report)
    db.session.commit()
    
    return jsonify({"message": "Thank you. Your report has been submitted to our moderation team."}), 200
