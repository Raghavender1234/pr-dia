# backend/app/models/subject.py
from .. import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Creator of the subject (Main Co-Admin or Co-Admin)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)


    # Relationships
    exam = db.relationship('Exam', back_populates='subjects')
    creator = db.relationship('User', back_populates='created_subjects', foreign_keys=[created_by_user_id])
    topics = db.relationship('Topic', back_populates='subject', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject {self.name} (Exam: {self.exam_id})>"