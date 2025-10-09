from datetime import datetime
from app.extensions import db 

class Class(db.Model):
    """Represents a scheduled class for an organization."""
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    class_type = db.Column(db.String(20), nullable=False, default='live')
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    timezone = db.Column(db.String(50), default='UTC')
    
    meeting_link = db.Column(db.String(500)) 
    
    max_participants = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False, default='scheduled') 
    
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=True)
    subject_ids = db.Column(db.JSON) # e.g., [1, 5, 12]
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = db.relationship('Organization', backref=db.backref('classes', lazy=True))
    instructor = db.relationship('User', foreign_keys=[instructor_id], backref=db.backref('taught_classes', lazy=True))
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_classes', lazy=True))
    exam = db.relationship('Exam', backref=db.backref('associated_classes', lazy=True))


class ClassParticipant(db.Model):
    """Links a student to a class they are enrolled in."""
    __tablename__ = 'class_participants'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('organization_memberships.id'), nullable=False)
    
    registration_status = db.Column(db.String(20), default='registered') # 'registered', 'attended', 'absent'
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    class_session = db.relationship('Class', backref=db.backref('participants', lazy='dynamic', cascade="all, delete-orphan"))
    student = db.relationship('User', backref=db.backref('class_participations', lazy=True))
    membership = db.relationship('OrganizationMembership', backref=db.backref('class_participations', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('class_id', 'user_id', name='_class_user_uc'),)


class Notification(db.Model):
    """Represents a notification sent to a user within the platform."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    parent_notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    sender_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=True)
    
    notification_type = db.Column(db.String(50), nullable=False) 
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500)) 
    
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    recipient = db.relationship('User', foreign_keys=[user_id], backref=db.backref('received_notifications', lazy='dynamic'))
    sender = db.relationship('User', foreign_keys=[sender_user_id], backref=db.backref('sent_notifications', lazy='dynamic'))
    class_session = db.relationship('Class', backref=db.backref('notifications', lazy=True))
    replies = db.relationship(
        'Notification', 
        backref=db.backref('parent', remote_side=[id]),
        lazy='joined', # Use 'joined' to load replies efficiently with the parent
        cascade="all, delete-orphan"
    )

