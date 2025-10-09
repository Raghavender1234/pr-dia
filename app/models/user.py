from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.student_progress import StudentTestAttempt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    user_type = db.Column(db.String(20), nullable=False) # 'super_admin', 'main_co_admin', 'co_admin', 'student'
    status = db.Column(db.String(20), nullable=False, default='active') # 'active', 'inactive', 'pending_approval'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    availability_status = db.Column(db.String(20), nullable=False, default='available') # 'available' or 'busy'
    last_login = db.Column(db.DateTime)
    timezone = db.Column(db.String(50), default='UTC')


    memberships = db.relationship('OrganizationMembership', back_populates='user', lazy=True, cascade="all, delete-orphan")
    created_exams = db.relationship('Exam', back_populates='creator', lazy=True)
    created_subjects = db.relationship('Subject', back_populates='creator', lazy=True)
    created_topics = db.relationship('Topic', back_populates='creator', lazy=True)
    created_questions = db.relationship('Question', back_populates='creator', lazy=True)
    created_mock_tests = db.relationship('MockTest', back_populates='creator', lazy=True)
    exam_enrollments = db.relationship('StudentExam', back_populates='student', lazy='dynamic', cascade="all, delete-orphan")
    ai_subscriptions = db.relationship('StudentAISubscription', back_populates='student', lazy=True)
    reviewed_questions = db.relationship('StudentReviewedQuestion', back_populates='user', cascade="all, delete-orphan")
    test_attempts = db.relationship('StudentTestAttempt', foreign_keys=[StudentTestAttempt.student_user_id], back_populates='student'
    )



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.user_type})>"