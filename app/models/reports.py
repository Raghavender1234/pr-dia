# In app/models/reports.py

from app.extensions import db
from datetime import datetime

class MockTestReport(db.Model):
    __tablename__ = 'mock_test_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id'), nullable=False, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)
    
    # High-level summary stats
    total_attempts = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    pass_rate = db.Column(db.Float, default=0.0)
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- Suggested Additions for AI Features ---
    # 1. For the "AI-Generated Remedial Action Plan"
    remedial_plan_details = db.Column(db.JSON) # Stores structured plan: text, links to quizzes/notes
    
    # 2. For the "Student Performance Archetype" Analysis
    archetype_analysis = db.Column(db.JSON) # Stores {'Gamblers': [...], 'Cautious Planners': [...]}
    
    # 3. For the "Question Quality & Effectiveness" Audit
    question_audit = db.Column(db.JSON) # Stores {'flawed_questions': [...], 'ineffective_questions': [...]}
    
    # 4. For identifying "At-Risk Students"
    at_risk_students = db.Column(db.JSON) # Stores a list of student IDs and reasons

    # --- Relationships ---
    topic_summaries = db.relationship('TopicPerformanceSummary', back_populates='report', lazy='dynamic', cascade="all, delete-orphan")
    mock_test = db.relationship('MockTest')

class TopicPerformanceSummary(db.Model):
    __tablename__ = 'topic_performance_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('mock_test_reports.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    topic_name = db.Column(db.String, nullable=False) # Denormalized for performance
    
    # Core metric
    average_accuracy = db.Column(db.Float, default=0.0) 
    
    # --- Suggested Additions for Deeper Analysis ---
    # Average time spent on questions in this topic (in seconds)
    average_time_spent = db.Column(db.Float, default=0.0)
    
    # Number of unique students who answered questions from this topic
    student_count = db.Column(db.Integer, default=0)
    
    # Total questions from this topic in the mock test
    question_count = db.Column(db.Integer, default=0)

    # --- Relationships ---
    report = db.relationship('MockTestReport', back_populates='topic_summaries')
    topic = db.relationship('Topic')
