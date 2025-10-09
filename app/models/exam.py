# backend/app/models/exam.py
from app.extensions import db
from datetime import datetime

class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), default=0.00, nullable=False) # Price for students to access this exam
    is_free = db.Column(db.Boolean, default=False, nullable=False) # NEW: is_free field
    
    # Creator of the exam (Main Co-Admin)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    questions = db.relationship('Question', back_populates='exam', cascade="all, delete-orphan")

    # Relationships
    organization = db.relationship('Organization', back_populates='exams')
    creator = db.relationship('User', back_populates='created_exams', foreign_keys=[created_by_user_id])
    subjects = db.relationship('Subject', back_populates='exam', lazy=True, cascade="all, delete-orphan")
    mock_tests = db.relationship('MockTest', back_populates='exam', lazy=True, cascade="all, delete-orphan")
    student_accesses = db.relationship('StudentExam', back_populates='exam', lazy=True, cascade="all, delete-orphan") # For tracking which students have access
    deleted_at = db.Column(db.DateTime, nullable=True)


    def __repr__(self):
        return f"<Exam {self.name} (Org: {self.organization_id})>"

    # Add UniqueConstraint here if not already present from previous updates
    __table_args__ = (db.UniqueConstraint('organization_id', 'name', name='_exam_org_name_uc'),)


class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to items
    items = db.relationship('StudyPlanItem', back_populates='study_plan', cascade="all, delete-orphan")
    exam = db.relationship('Exam', backref='study_plans')

class StudyPlanItem(db.Model):
    __tablename__ = 'study_plan_items'
    id = db.Column(db.Integer, primary_key=True)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False) # NEW: Stores a real date like 2025-10-25
    item_type = db.Column(db.String(50), nullable=False) # 'read', 'practice_quiz', 'mock_test'
    description = db.Column(db.Text, nullable=False)
    estimated_time_minutes = db.Column(db.Integer, nullable=True)
    difficulty_level = db.Column(db.String(50), nullable=True)
    day_number = db.Column(db.Integer)  # new
    order = db.Column(db.Integer, nullable=True)
    
    # Link to specific content
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id'), nullable=True)

    # Relationships
    study_plan = db.relationship('StudyPlan', back_populates='items')
    topic = db.relationship('Topic')
    mock_test = db.relationship('MockTest')


class StudentStudyPlanProgress(db.Model):
    __tablename__ = 'student_study_plan_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    study_plan_item_id = db.Column(db.Integer, db.ForeignKey('study_plan_items.id'), nullable=False)
    
    # You can track status or just completion time
    status = db.Column(db.String(50), default='completed', nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=True, nullable=False)

    # Add a unique constraint to prevent a user from completing the same item twice
    __table_args__ = (db.UniqueConstraint('student_user_id', 'study_plan_item_id', name='_student_plan_item_uc'),)
