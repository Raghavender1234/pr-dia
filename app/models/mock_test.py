# backend/app/models/mock_test.py
from app.extensions import db
from datetime import datetime

class MockTest(db.Model):
    __tablename__ = 'mock_tests'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    passing_marks = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft') # 'draft', 'active', 'archived'
    report_status = db.Column(db.String(20), nullable=True, server_default=None) # 'pending', 'completed', 'failed'
    default_marks_per_question = db.Column(db.Numeric(5, 2), nullable=False, default=1.00, server_default='1.00')

    
    negative_marking_enabled = db.Column(db.Boolean, default=False, nullable=False)
    negative_marking_ratio = db.Column(db.Numeric(3, 2), default=0.25, nullable=False)

    is_live_test = db.Column(db.Boolean, default=False, nullable=False)
    live_start_time = db.Column(db.DateTime)
    live_end_time = db.Column(db.DateTime)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    exam = db.relationship('Exam', back_populates='mock_tests')
    creator = db.relationship('User', back_populates='created_mock_tests', foreign_keys=[created_by_user_id])
    student_attempts = db.relationship('StudentTestAttempt', back_populates='mock_test', lazy=True, cascade="all, delete-orphan")
    
    # This relationship is 'mock_test_questions', and its backref is 'mock_test' on MockTestQuestion
    mock_test_questions = db.relationship('MockTestQuestion', back_populates='mock_test', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint('exam_id', 'title', name='_exam_title_uc'),)

    def __repr__(self):
        return f"<MockTest {self.title} (Exam: {self.exam_id})>"

class MockTestQuestion(db.Model):
    __tablename__ = 'mock_test_questions'
    id = db.Column(db.Integer, primary_key=True)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question_order = db.Column(db.Integer, nullable=False) # Order of question in test
    marks = db.Column(db.Numeric(5, 2), nullable=False)
    mock_test = db.relationship('MockTest', back_populates='mock_test_questions')
    question = db.relationship('Question', back_populates='mock_test_questions')

    __table_args__ = (db.UniqueConstraint('mock_test_id', 'question_id', name='_mock_test_question_uc'),)

    def __repr__(self):
        return f"<MockTestQuestion Test:{self.mock_test_id} Question:{self.question_id}>"