from app.extensions import db
from datetime import datetime

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # This is the key: if NULL, it's a global post. If set, it's private.
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True, index=True)
    
    author_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User')
    organization = db.relationship('Organization')
    replies = db.relationship('ForumReply', back_populates='post', lazy='dynamic', cascade="all, delete-orphan")

class ForumReply(db.Model):
    __tablename__ = 'forum_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    author_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('ForumPost', back_populates='replies')
    author = db.relationship('User')
