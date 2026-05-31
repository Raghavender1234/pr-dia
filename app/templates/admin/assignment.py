from app.extensions import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    max_marks = db.Column(db.Numeric(5, 2), nullable=True)
    
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy=True, cascade="all, delete-orphan")

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submission_text = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(20), default='submitted') # 'submitted', 'graded', 'late'
    marks_awarded = db.Column(db.Numeric(5, 2), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime, nullable=True)
    graded_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    __table_args__ = (db.UniqueConstraint('assignment_id', 'student_user_id', name='_student_assignment_uc'),)