# In backend/app/models/topic.py

from .. import db
from datetime import datetime

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # --- Relationships ---
    subject = db.relationship('Subject', back_populates='topics')
    # ✅ Rely on the foreign key to link to the creator
    creator = db.relationship('User', back_populates='created_topics', foreign_keys=[created_by_user_id])
    questions = db.relationship('Question', back_populates='topic', lazy='dynamic', cascade="all, delete-orphan")
    
    # ✅ This is the single, correct relationship to TopicContent
    contents = db.relationship(
        'TopicContent', 
        back_populates='topic', 
        lazy='select', # 'select' is good for loading all content items as a list
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Topic {self.name}>"


class TopicContent(db.Model):
    __tablename__ = 'topic_contents'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    
    title = db.Column(db.String(255)) 
    content_type = db.Column(db.String(50), nullable=False)  # 'text', 'video_link', 'pdf_link'
    content_value = db.Column(db.Text, nullable=False)      # The actual text or URL
    item_order = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)


    # ✅ This relationship correctly points back to the 'contents' attribute on the Topic model
    topic = db.relationship('Topic', back_populates='contents')

    def __repr__(self):
        return f'<TopicContent {self.id} Title: {self.title}>'