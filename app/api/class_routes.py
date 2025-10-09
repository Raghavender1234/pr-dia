from flask import Blueprint, jsonify, request, url_for
from app import db
from app.models.class_management import Class, Notification
from app.models.organization import OrganizationMembership
from app.models.user import User
from datetime import datetime, timedelta, timezone
from .decorators import admin_role_required, org_member_required
from flask_jwt_extended import jwt_required, get_jwt_identity

class_bp = Blueprint('class_api', __name__, url_prefix='/api/classes')

def _current_user():
    """Helper function to get the user object from the JWT token."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def ensure_utc_aware(dt):
    """
    Ensure a datetime is UTC-aware.
    If naive, assume it's already in UTC and add timezone info.
    If aware, convert to UTC.
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    else:
        return dt.astimezone(timezone.utc)

@class_bp.route('/', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def create_class(current_user, organization, **kwargs):
    data = request.get_json()
    
    required_fields = ['title', 'scheduled_at', 'duration_minutes']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Parse the ISO datetime string
        scheduled_at_str = data['scheduled_at']
        if scheduled_at_str.endswith('Z'):
            scheduled_at_str = scheduled_at_str[:-1] + '+00:00'
        
        start_time_utc = datetime.fromisoformat(scheduled_at_str)
        
        # Ensure it's UTC aware
        if start_time_utc.tzinfo is None:
            start_time_utc = start_time_utc.replace(tzinfo=timezone.utc)
        else:
            start_time_utc = start_time_utc.astimezone(timezone.utc)
        
        # Store as naive UTC in database
        start_time_naive_utc = start_time_utc.replace(tzinfo=None)
        
        new_class = Class(
            organization_id=organization.id,
            title=data['title'],
            description=data.get('description', ''),
            instructor_id=current_user.id,
            scheduled_at=start_time_naive_utc,
            duration_minutes=int(data['duration_minutes']),
            meeting_link=data.get('meeting_link'),
            created_by=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()

        # Try to schedule notification - wrapped in try-except
        try:
            from app.extensions import scheduler
            from app.tasks import send_class_reminders
            
            reminder_time = start_time_utc - timedelta(minutes=15)
            now_in_utc = datetime.now(timezone.utc)

            if reminder_time <= now_in_utc:
                run_at = now_in_utc + timedelta(seconds=5)
            else:
                run_at = reminder_time

            scheduler.add_job(
                id=f'class_reminder_{new_class.id}',
                func=send_class_reminders,
                args=[new_class.id],
                trigger='date',
                run_date=run_at,
                replace_existing=True
            )
        except Exception as scheduler_error:
            print(f"Warning: Could not schedule reminder: {scheduler_error}")
            # Continue without failing - class was created successfully

        return jsonify({
            'message': 'Class created successfully!',
            'id': new_class.id
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@class_bp.route('/organization/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_classes_for_organization(organization_id):
    user = _current_user()
    membership = OrganizationMembership.query.filter_by(
        user_id=user.id,
        organization_id=organization_id,
        is_active=True
    ).first()
    
    if not membership:
        return jsonify({'error': 'Access denied'}), 403

    classes = Class.query.filter_by(organization_id=organization_id).all()

    calendar_events = []
    for cls in classes:
        if not cls.scheduled_at or not cls.duration_minutes:
            continue

        # Assume database stores naive UTC, add timezone info
        start_time_utc = ensure_utc_aware(cls.scheduled_at)
        end_time_utc = start_time_utc + timedelta(minutes=cls.duration_minutes)
        
        # Format as ISO 8601 with Z suffix (UTC indicator)
        start_iso = start_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_iso = end_time_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        join_url = url_for('frontend.live_class_view', class_id=cls.id, _external=True)

        calendar_events.append({
            'id': cls.id,
            'title': cls.title,
            'start': start_iso,
            'end': end_iso,
            'extendedProps': {
                'description': cls.description or '',
                'meeting_link': cls.meeting_link or '',
                'class_url': join_url
            }
        })
    
    return jsonify(calendar_events)