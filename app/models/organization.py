from .. import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Plan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    monthly_price = db.Column(db.Numeric(10, 2), nullable=False)
    max_main_coadmins = db.Column(db.Integer, default=1)
    max_coadmins = db.Column(db.Integer, nullable=False)
    max_invited_students = db.Column(db.Integer, nullable=False)
    max_free_exams = db.Column(db.Integer, default=1, nullable=False)
    description = db.Column(db.Text)
    is_publicly_available = db.Column(db.Boolean, default=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # ✅ newly added
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organizations = db.relationship('Organization', back_populates='plan', lazy=True)

    def __repr__(self):
        return f"<Plan {self.name}>"


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending_payment')
    razorpay_order_id = db.Column(db.String(100))
    current_invited_student_count = db.Column(db.Integer, default=0)
    current_coadmin_count = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_ai_premium = db.Column(db.Boolean, default=False, nullable=False) 
    subdomain = db.Column(db.String(64), unique=True, nullable=True) 
    logo_url = db.Column(db.String(255), nullable=True)
    login_image_url = db.Column(db.String(255), nullable=True)
    register_image_url = db.Column(db.String(255), nullable=True)
    social_links = db.Column(JSON, nullable=True) 
    contact_email = db.Column(db.String(120), nullable=True)
    favicon_url = db.Column(db.String(255), nullable=True)
    footer_text = db.Column(db.Text, nullable=True)
    allow_class_creation = db.Column(db.Boolean, default=True)
    default_class_duration = db.Column(db.Integer, default=60)


    # ✅ New org-specific content fields
    tos_html = db.Column(db.Text, nullable=True)          # Terms of Service
    privacy_policy_html = db.Column(db.Text, nullable=True)
    about_html = db.Column(db.Text, nullable=True)
    contact_data = db.Column(db.JSON, nullable=True)
    faq_data = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # --- Relationships ---
    plan = db.relationship('Plan', back_populates='organizations')
    memberships = db.relationship(
        'OrganizationMembership',
        back_populates='organization',
        lazy=True,
        cascade="all, delete-orphan"
    )
    exams = db.relationship(
        'Exam',
        back_populates='organization',
        lazy=True,
        cascade="all, delete-orphan"
    )

    # --- String Representation ---
    def __repr__(self):
        return f"<Organization {self.name} ({self.code})>"

    # --- Constraints ---
    __table_args__ = (
        db.UniqueConstraint('name', name='_organization_name_uc'),
        db.UniqueConstraint('code', name='_organization_org_code_uc'),  # ✅ updated constraint key
    )

class OrganizationMembership(db.Model):
    __tablename__ = 'organization_memberships'
    # Composite primary key for uniqueness, or a simple ID and unique constraint
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    access_type = db.Column(db.String(50), nullable=False, default='public', server_default='public')
    exam_enrollments = db.relationship('StudentExam', back_populates='membership', cascade="all, delete-orphan")
    test_attempts = db.relationship('StudentTestAttempt', back_populates='membership', cascade="all, delete-orphan")
    weekly_progress = db.relationship('StudentWeeklyProgress', back_populates='membership', cascade="all, delete-orphan")

    
    is_active = db.Column(db.Boolean, default=True, nullable=False) # Allows deactivating a user within an org
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'organization_id', name='_user_organization_uc'),) # Ensures a user can only have one membership per organization

    # Relationships
    user = db.relationship('User', back_populates='memberships')
    organization = db.relationship('Organization', back_populates='memberships')

    def __repr__(self):
        return f"<Membership User: {self.user_id}, Org: {self.organization_id}>"
    
class OrganizationReport(db.Model):
    __tablename__ = 'organization_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # e.g., 'spam', 'inappropriate_content', 'copyright_violation', 'other'
    reason = db.Column(db.String(50), nullable=False) 
    comments = db.Column(db.Text)
    
    # 'pending', 'resolved_warning', 'resolved_suspension'
    status = db.Column(db.String(20), default='pending', nullable=False) 
    
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('Organization')
    reporter = db.relationship('User')
