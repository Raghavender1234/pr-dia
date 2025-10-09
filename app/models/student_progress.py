# backend/app/models/student_progress.py

from app.extensions import db 
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class StudentExam(db.Model):
    __tablename__ = 'student_exams'
    # Tracks which students have access to which exams (either paid or free)

    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    
    access_status = db.Column(db.String(20), nullable=False, default='pending') # 'pending', 'purchased', 'free_access', 'expired', 'revoked'
    membership_id = db.Column(db.Integer, db.ForeignKey('organization_memberships.id'), nullable=False, index=True)

    purchased_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime) # For time-limited access
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ Add this line
    
    # Reference to Razorpay payment if applicable
    razorpay_order_id = db.Column(db.String(40), nullable=True, index=True)
    razorpay_payment_id = db.Column(db.String(40), nullable=True)

    __table_args__ = (db.UniqueConstraint('student_user_id', 'exam_id', name='_student_exam_access_uc'),)

    # Relationships
    student = db.relationship('User', back_populates='exam_enrollments')
    exam = db.relationship('Exam', back_populates='student_accesses') # Assuming 'Exam' model has 'student_accesses' back_populates
    membership = db.relationship('OrganizationMembership', back_populates='exam_enrollments')

    def __repr__(self):
        return f"<StudentExam User:{self.student_user_id} Exam:{self.exam_id} ({self.access_status})>"


class StudentAISubscription(db.Model):
    __tablename__ = 'student_ai_subscriptions'
    # Tracks student subscriptions for the AI-powered practice feature

    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True) # Assuming one active AI sub per student
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True) # Optional, if AI sub is tied to an org affiliation

    status = db.Column(db.String(20), nullable=False, default='inactive') # 'active', 'inactive', 'trial', 'cancelled'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime) # Null for indefinite, or specific end for trial/fixed period

    # Razorpay subscription details
    razorpay_subscription_id = db.Column(db.String(100))
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime) # For recurring payments

    # Relationship
    student = db.relationship('User', back_populates='ai_subscriptions')
    organization = db.relationship('Organization', lazy=True) # No backref needed for this one, already has 'id' foreign key

    def __repr__(self):
        return f"<StudentAISubscription User:{self.student_user_id} Status:{self.status}>"


class StudentTestAttempt(db.Model):
    __tablename__ = 'student_test_attempts'
    # Records each time a student attempts a mock test

    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('organization_memberships.id'), nullable=False, index=True)
    is_unlocked = db.Column(db.Boolean, default=False, nullable=False)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    unlocked_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    was_pending_grading = db.Column(db.Boolean, default=False, nullable=False)

    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    # Changed from end_time to completed_at for clarity, matches frontend
    completed_at = db.Column(db.DateTime) 
    
    score = db.Column(db.Numeric(5, 2)) # Final score for the attempt
    # max_score is more consistently named as total_possible_score in frontend/backend
    total_possible_score = db.Column(db.Numeric(5, 2)) 
    
    status = db.Column(db.String(20), nullable=False, default='in_progress') # 'in_progress', 'completed', 'submitted'
    
    time_limit_minutes = db.Column(db.Integer) # From mock_test
    negative_marking = db.Column(db.Boolean, default=False) # From mock_test

    # Relationships
    student = db.relationship('User', foreign_keys=[student_user_id], back_populates='test_attempts')
    mock_test = db.relationship('MockTest', back_populates='student_attempts')
    tab_switch_count = db.Column(db.Integer, default=0, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    membership = db.relationship('OrganizationMembership', back_populates='test_attempts')

    # Individual responses for this attempt - IMPORTANT: Define back_populates here
    responses = db.relationship('StudentQuestionResponse', back_populates='attempt', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestAttempt User:{self.student_user_id} Test:{self.mock_test_id} Status:{self.status}>"


class StudentQuestionResponse(db.Model):
    __tablename__ = 'student_question_responses'
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('student_test_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    # Use your defined column names: response_text and selected_mcq_option_id
    response_text = db.Column(db.Text) # For OpenEnded, Comprehension
    selected_mcq_option_id = db.Column(db.Integer, db.ForeignKey('mcq_options.id')) # For MCQ
    grading_status = db.Column(db.String(20), default='graded', nullable=False) # Default to 'graded' for old MCQs
    points_awarded = db.Column(db.Numeric(5, 2), nullable=True)
    grader_comments = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)
    graded_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_correct = db.Column(db.Boolean) # True/False for MCQ, None for AI-evaluated questions initially
    score = db.Column(db.Float) # Individual question score, populated by AI or MCQ logic
    ai_feedback_text = db.Column(db.Text) # Your existing AI feedback text field
    ai_score = db.Column(db.Numeric(5, 2)) # NEW: For AI score (0-100 or relative)
    time_taken = db.Column(db.Float, nullable=True)  # in seconds
    marked_for_review = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(50), default='graded', nullable=False)

    # Define relationship to StudentTestAttempt - IMPORTANT: Use back_populates
    attempt = db.relationship('StudentTestAttempt', back_populates='responses') 
    
    # Ensure relationships to Question and MCQOption are correctly defined if not back_populating
    question = db.relationship('Question', back_populates='student_responses')
    selected_mcq_option = db.relationship('MCQOption', backref='selected_by_responses', lazy=True)

    # UNIQUE CONSTRAINT - IMPORTANT: Must be in __table_args__
    __table_args__ = (db.UniqueConstraint('attempt_id', 'question_id', name='_attempt_question_uc'),)

class StudentReviewedQuestion(db.Model):
    __tablename__ = 'student_reviewed_questions'
    id = db.Column(db.Integer, primary_key=True)
    # Ensure this is named 'student_user_id'
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    # The constraint correctly uses 'student_user_id'

    user = db.relationship('User', back_populates='reviewed_questions')
    question = db.relationship('Question', back_populates='review_entries')

    __table_args__ = (db.UniqueConstraint('student_user_id', 'question_id', name='_student_question_review_uc'),)


class StudentTopicPractice(db.Model):
    """
    Tracks a student's practice progress on a per-topic basis,
    specifically which questions they have answered correctly.
    """
    __tablename__ = 'student_topic_practice'
    
    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, index=True)
    
    correctly_answered_ids = db.Column(JSONB, nullable=False, default=[])
    
    last_practiced_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_user_id', 'topic_id', name='_student_topic_uc'),)


class StudentAIUsage(db.Model):
    """
    Tracks the number of AI API calls a student makes per month
    to enforce usage limits for premium features.
    """
    __tablename__ = 'student_ai_usage'

    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Stores the year and month as a string, e.g., "2025-09"
    usage_month = db.Column(db.String(7), nullable=False, index=True)
    
    generate_calls = db.Column(db.Integer, default=0, nullable=False)
    validate_calls = db.Column(db.Integer, default=0, nullable=False)
    explain_calls = db.Column(db.Integer, default=0, nullable=False)

    # Ensures a student has only one usage record per month
    __table_args__ = (db.UniqueConstraint('student_user_id', 'usage_month', name='_student_month_usage_uc'),)


class StudentWeeklyProgress(db.Model):
    __tablename__ = 'student_weekly_progress'

    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False, index=True)
    membership_id = db.Column(db.Integer, db.ForeignKey('organization_memberships.id'), nullable=False, index=True)

    # ISO week period
    week_start = db.Column(db.Date, nullable=False, index=True)  # Monday of that ISO week
    week_end   = db.Column(db.Date, nullable=False)

    # Compact metrics blob you control
    metrics = db.Column(JSONB, nullable=False, default={})

    membership = db.relationship('OrganizationMembership', back_populates='weekly_progress')

    # For provenance
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_user_id', 'exam_id', 'week_start', name='_student_exam_week_uc'),
    )
