# backend/app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, TextAreaField, URLField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError, NumberRange

from app.models.user import User
from app.models.organization import Organization # For organization code/name uniqueness checks

# --- Base Form for Authentication ---
class BaseAuthForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Submit') # Generic submit

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one or log in.')

# --- Login Form ---
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me') # Add back if needed
    submit = SubmitField('Log In')

# --- User Registration Form (Student/Co-Admin Joining an Org) ---
class UserRegistrationForm(BaseAuthForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=64)])
    
    user_type = SelectField(
        'User Type',
        choices=[('student', 'Student'), ('main-co-admin', 'Main-Co-Admin'), ('co-admin', 'Co-Admin')],
        validators=[DataRequired()]
    )

    # organization_code is REQUIRED for UserRegistrationForm
    organization_code = StringField('Organization Code', validators=[DataRequired(), Length(min=1, max=20)])

    submit = SubmitField('Register')

    # Custom validation for organization_code (must exist)
    def validate_organization_code(self, organization_code):
        org = Organization.query.filter_by(org_code=organization_code.data).first()
        if not org:
            raise ValidationError('Invalid Organization Code. Please enter a valid code.')

# --- Organization Registration Form (Main Co-Admin Creating a NEW Org) ---
class OrgRegistrationForm(BaseAuthForm):
    # Main Co-Admin details (inherits email, password, confirm_password from BaseAuthForm)
    first_name = StringField('Admin First Name', validators=[DataRequired(), Length(min=2, max=64)])
    last_name = StringField('Admin Last Name', validators=[DataRequired(), Length(min=2, max=64)])

    # Organization details
    organization_name = StringField('Organization Name', validators=[DataRequired(), Length(min=3, max=100)])
    organization_code = StringField('Unique Organization Code', validators=[DataRequired(), Length(min=3, max=20)])
    
    # Placeholder for plan. In a real app, this would be dynamic from DB.
    plan = SelectField('Subscription Plan', 
                       choices=[('basic', 'Basic (₹5,000 / month)'),
                                ('pro', 'Pro (₹10,000 / month)'),
                                ('premium', 'Premium (₹20,000 / month)')],
                       validators=[DataRequired()])

    submit = SubmitField('Register Organization')

    # Custom validation for organization code/name uniqueness for new orgs
    def validate_organization_code(self, organization_code):
        org = Organization.query.filter_by(org_code=organization_code.data).first()
        if org:
            raise ValidationError('This Organization Code is already taken. Please choose another.')
    
    def validate_organization_name(self, organization_name):
        org = Organization.query.filter_by(name=organization_name.data).first()
        if org:
            raise ValidationError('An Organization with this Name already exists. Please choose another.')
        
class ExamForm(FlaskForm):
    # No actual fields needed here, just for CSRF
    pass

class OrgUserManagementForm(FlaskForm):
    # No actual fields needed here, just for CSRF
    pass

class SubjectForm(FlaskForm):
    # No actual fields needed here, just for CSRF
    pass

class TopicContentForm(FlaskForm):
    title = StringField('Content Title') # Optional based on your old HTML (no 'required')
    content_type = SelectField('Content Type', 
                                choices=[
                                    ('text', 'Text Content'),
                                    ('video_link', 'Video Link'),
                                    ('pdf_link', 'PDF Link')
                                    # Add other types if needed, e.g., 'image_upload', 'pdf_upload'
                                ], 
                                validators=[DataRequired()])
    
    # We'll use JavaScript to show/hide these based on content_type,
    # but declare them here. Validation will also be handled by JS/backend.
    content_value_text = TextAreaField('Text Content (Markdown supported)') # For 'text' type
    content_value_url = URLField('URL (for Video/PDF Links)') # For link types
    
    item_order = IntegerField('Display Order', default=0, validators=[Optional(), NumberRange(min=0)])
    
    submit = SubmitField('Save Content') # This might not be directly used if we handle submit via JS buttons

    # You can add custom validators later if needed, e.g., ensure URL is present if type is link.
    # For now, the JavaScript and API backend will handle conditional requirements.
