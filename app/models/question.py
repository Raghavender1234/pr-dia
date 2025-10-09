# backend/app/models/question.py
from .. import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    question_type = db.Column(db.String(50), nullable=False) # 'MCQ', 'Comprehension', 'OpenEnded'
    question_text = db.Column(db.Text, nullable=False)
    explanation_text = db.Column(db.Text, nullable=True) # Explicitly nullable=True if optional
    sample_answer = db.Column(db.Text, nullable=True)    # Explicitly nullable=True if optional
    difficulty_level = db.Column(db.String(50))
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    review_entries = db.relationship('StudentReviewedQuestion', back_populates='question', cascade="all, delete-orphan")
    student_responses = db.relationship('StudentQuestionResponse', back_populates='question', cascade="all, delete-orphan")
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    exam = db.relationship('Exam', back_populates='questions')
    image_url = db.Column(db.String(512), nullable=True)
    visibility = db.Column(db.String(20), nullable=False, default='public', server_default='public',index=True)

    parent_question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    sub_question_order = db.Column(db.Integer, nullable=True) 

    # Relationships
    topic = db.relationship('Topic', back_populates='questions')
    creator = db.relationship('User', back_populates='created_questions')

    mcq_options = db.relationship('MCQOption', back_populates='question', lazy='select', cascade="all, delete-orphan")
    
    comprehension_passage = db.relationship(
        'ComprehensionPassage', 
        uselist=False, 
        back_populates='question', 
        lazy='select',  # CHANGED from 'dynamic' to 'select'
        cascade="all, delete-orphan"
    )
    
    sub_questions = db.relationship(
        'Question',
        backref=db.backref('parent_question', remote_side=[id]),
        lazy='select', # 'select' or 'joined' are fine; 'dynamic' also works for one-to-many
        cascade="all, delete-orphan",
        foreign_keys=[parent_question_id]
    )
    
    mock_test_questions = db.relationship('MockTestQuestion', back_populates='question', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question {self.id} ({self.question_type})>"

class MCQOption(db.Model):
    __tablename__ = 'mcq_options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    question = db.relationship('Question', back_populates='mcq_options')

    def __repr__(self):
        return f"<MCQOption {self.id} (Q: {self.question_id}, Correct: {self.is_correct})>"


class ComprehensionPassage(db.Model):
    __tablename__ = 'comprehension_passages'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, unique=True)
    passage_text = db.Column(db.Text, nullable=False)

    question = db.relationship('Question', back_populates='comprehension_passage')

    def __repr__(self):
        return f"<ComprehensionPassage {self.id} (Q: {self.question_id})>"
    
class ReportedContent(db.Model):
    __tablename__ = 'reported_content'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # e.g., 'incorrect_answer', 'typo', 'inappropriate', 'other'
    reason = db.Column(db.String(50), nullable=False) 
    comments = db.Column(db.Text) # Optional extra details from the student
    
    # 'pending', 'resolved', 'dismissed'
    status = db.Column(db.String(20), default='pending', nullable=False, index=True) 
    
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question')
    reporter = db.relationship('User')
