from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.class_management import Notification
from app.models.organization import OrganizationMembership
from app.extensions import db
from datetime import datetime
from sqlalchemy import or_, and_, func, select
from .decorators import org_member_required, admin_role_required, student_required
from app.models.user import User

notification_bp = Blueprint('notification_api', __name__, url_prefix='/api/notifications')

def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    user = _current_user()
    if not user:
        return jsonify({"message": "User not found"}), 404

    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = 15 if not unread_only else 10

    # Base query: Get all top-level threads the user is part of.
    base_query = Notification.query.filter(
        Notification.parent_notification_id.is_(None),
        or_(
            Notification.user_id == user.id,
            Notification.sender_user_id == user.id
        )
    )

    # If the user is an admin and is busy, filter out notifications from students
    if user.user_type in ['main_co_admin', 'co_admin'] and user.availability_status == 'busy':
        base_query = base_query.join(User, Notification.sender_user_id == User.id).filter(User.user_type != 'student')

    # If the bell dropdown is asking for unread items, only show notifications
    # where the user is the RECIPIENT and hasn't read them
    if unread_only:
        subquery = db.session.query(Notification.id).filter(
            Notification.user_id == user.id,  # User is recipient
            Notification.read_at.is_(None)
        ).scalar_subquery()

        base_query = base_query.filter(
            or_(
                # Main notification is unread for this user (as recipient)
                and_(
                    Notification.id.in_(subquery),
                    Notification.user_id == user.id  # Ensure they're the recipient
                ),
                # OR has replies that are unread for this user (as recipient)
                Notification.replies.any(
                    and_(
                        Notification.id.in_(subquery),
                        Notification.user_id == user.id  # Ensure they're the recipient
                    )
                )
            )
        )

    # Subquery to find the last activity (latest reply) in each thread.
    last_reply_sq = db.session.query(
        Notification.parent_notification_id,
        func.max(Notification.created_at).label("last_activity")
    ).filter(Notification.parent_notification_id.isnot(None)).group_by(Notification.parent_notification_id).subquery()

    # Join the base query (which gets parent threads) with this subquery.
    base_query = base_query.outerjoin(last_reply_sq, Notification.id == last_reply_sq.c.parent_notification_id)

    # Order by the latest activity
    paginated_notifications = base_query.order_by(
        func.coalesce(last_reply_sq.c.last_activity, Notification.created_at).desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    notifications = paginated_notifications.items
    
    # IMPORTANT: Only count notifications where user is the RECIPIENT
    unread_count = Notification.query.filter(
        Notification.user_id == user.id,  # User is recipient
        Notification.read_at.is_(None)
    ).count()

    def serialize_reply(reply):
        return {
            'id': reply.id,
            'message': reply.message,
            'timestamp': reply.created_at.isoformat(),
            'sender_user_id': reply.sender_user_id,
            'sender_name': f"{reply.sender.first_name} {reply.sender.last_name}" if reply.sender else "Unknown"
        }

    # Serialize notifications
    notifications_data = []
    for n in notifications:
        # Mark as "read" only if the user is the recipient and it's been read
        is_read_for_user = (n.user_id == user.id and n.read_at is not None) or (n.user_id != user.id)
        
        notifications_data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': is_read_for_user,  # Fixed: Only show as unread if user is recipient
            'timestamp': n.created_at.isoformat(),
            'sender_user_id': n.sender_user_id,
            'sender_name': f"{n.sender.first_name} {n.sender.last_name}" if n.sender else "System",
            'replies': sorted([serialize_reply(r) for r in n.replies], key=lambda r: r['timestamp'])
        })

    return jsonify({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'has_next': paginated_notifications.has_next,
        'has_prev': paginated_notifications.has_prev,
        'page': paginated_notifications.page,
        'total_pages': paginated_notifications.pages
    })

@notification_bp.route('/mark-read', methods=['POST'])
@jwt_required()
def mark_notifications_read():
    """Marks notification threads as read (including all replies) where user is the recipient."""
    user = _current_user()
    data = request.get_json()
    notification_ids = data.get('ids', [])

    if not notification_ids:
        return jsonify({'error': 'No notification IDs provided'}), 400

    # Mark the parent notifications as read (only where user is recipient)
    Notification.query.filter(
        Notification.id.in_(notification_ids),
        Notification.user_id == user.id  # User must be recipient
    ).update({'read_at': datetime.utcnow()}, synchronize_session=False)
    
    # Also mark all replies in these threads as read (only where user is recipient)
    Notification.query.filter(
        Notification.parent_notification_id.in_(notification_ids),
        Notification.user_id == user.id,  # User must be recipient
        Notification.read_at.is_(None)
    ).update({'read_at': datetime.utcnow()}, synchronize_session=False)
    
    db.session.commit()
    return jsonify({'message': 'Notifications marked as read.'})

@notification_bp.route('/users-for-tagging', methods=['GET'])
@org_member_required() # Any active member of an org can see other members
def get_users_for_tagging(current_user, organization, **kwargs):
    """Fetches a list of all users in the current organization for the tagging feature."""
    query = request.args.get('query', '').strip().lower()

    base_query = OrganizationMembership.query.filter(
        OrganizationMembership.organization_id == organization.id,
        OrganizationMembership.is_active == True,
        OrganizationMembership.user_id != current_user.id
    )

    if query:
        base_query = base_query.join(User).filter(
            or_(
                User.first_name.ilike(f"%{query}%"),
                User.last_name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        )

    memberships = base_query.limit(10).all()

    user_list = [{
        'id': m.user.id,
        'name': f"{m.user.first_name} {m.user.last_name}",
        'role': m.user.user_type
    } for m in memberships]

    return jsonify(user_list)

# 2. The "Admin Broadcast" Tool
@notification_bp.route('/broadcast', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def send_broadcast_notification(current_user, organization, **kwargs):
    """Sends a notification from an admin to all active students in their org."""
    data = request.get_json()
    title = data.get('title')
    message = data.get('message')

    if not title or not message:
        return jsonify({"message": "Title and message are required."}), 400

    student_members = OrganizationMembership.query.join(User).filter(
        OrganizationMembership.organization_id == organization.id,
        OrganizationMembership.is_active == True,
        User.user_type == 'student'
    ).all()

    for member in student_members:
        notification = Notification(
            organization_id=organization.id,
            user_id=member.user_id, # The recipient
            sender_user_id=current_user.id, # The sender
            notification_type='announcement',
            title=title,
            message=message
        )
        db.session.add(notification)
        
    db.session.commit()
    return jsonify({"message": f"Announcement sent to {len(student_members)} students."}), 200

@notification_bp.route('/send-direct', methods=['POST'])
@student_required()
def send_direct_notification(current_user, **kwargs):
    """Sends a notification from a student to one or more tagged users."""
    data = request.get_json()
    recipient_ids = data.get('recipient_ids', [])
    title = data.get('title')
    message = data.get('message')

    if not all([recipient_ids, title, message]):
        return jsonify({"message": "Recipients, title, and message are required."}), 400

    # For security, verify that all recipients are in the same organization as the sender.
    sender_org_id = current_user.memberships[0].organization_id if current_user.memberships else None
    if not sender_org_id:
        return jsonify({"message": "You must belong to an organization to send messages."}), 403

    # This ensures a student can't message users outside their own organization
    valid_recipients = User.query.join(OrganizationMembership).filter(
        User.id.in_(recipient_ids),
        OrganizationMembership.organization_id == sender_org_id
    ).all()

    if len(valid_recipients) != len(recipient_ids):
        return jsonify({"message": "One or more recipients are not valid."}), 400

    for user in valid_recipients:
        notification = Notification(
            organization_id=sender_org_id,
            user_id=user.id, # The recipient
            sender_user_id=current_user.id, # The sender
            notification_type='direct_message',
            title=title,
            message=f"From {current_user.first_name}: {message}"
        )
        db.session.add(notification)
        
    db.session.commit()
    return jsonify({"message": f"Message sent to {len(valid_recipients)} user(s)."}), 200

@notification_bp.route('/admin/send-direct', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def send_admin_direct_notification(current_user, organization, **kwargs):
    """Sends a direct notification from an admin to specific users in their org."""
    data = request.get_json()
    recipient_ids = data.get('recipient_ids', [])
    title = data.get('title')
    message = data.get('message')

    if not all([recipient_ids, title, message]):
        return jsonify({"message": "Recipients, title, and message are required."}), 400

    # Security: Verify all recipients belong to the admin's organization
    valid_recipients = User.query.join(OrganizationMembership).filter(
        User.id.in_(recipient_ids),
        OrganizationMembership.organization_id == organization.id
    ).all()

    if len(valid_recipients) != len(recipient_ids):
        return jsonify({"message": "One or more recipients are not valid members."}), 400

    for user in valid_recipients:
        notification = Notification(
            organization_id=organization.id,
            user_id=user.id,
            sender_user_id=current_user.id,
            notification_type='direct_message',
            title=title,
            message=message
        )
        db.session.add(notification)
        
    db.session.commit()
    return jsonify({"message": f"Direct message sent to {len(valid_recipients)} user(s)."}), 200

@notification_bp.route('/<int:notification_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_notification(notification_id):
    """Sends a reply to the other participant in a notification thread."""
    user = _current_user()
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"message": "Reply message is required."}), 400

    # Find the original notification to identify the participants
    original_notification = Notification.query.get_or_404(notification_id)
    
    # Security check: User must be either the sender or receiver to reply
    if user.id not in [original_notification.user_id, original_notification.sender_user_id]:
        return jsonify({"message": "Unauthorized"}), 403

    # --- THIS IS THE FIX ---
    # Determine the correct recipient for the reply.
    # If the current user (the one replying) was the original recipient,
    # then the new recipient is the original sender.
    if user.id == original_notification.user_id:
        recipient_id = original_notification.sender_user_id
    # Otherwise, the current user must be the original sender,
    # so the new recipient is the original recipient.
    else:
        recipient_id = original_notification.user_id
    
    if not recipient_id:
        return jsonify({"message": "This notification cannot be replied to (recipient not found)."}), 400
        
    # Find the top-level parent notification for proper threading
    parent_id = original_notification.parent_notification_id or original_notification.id

    # Create the new reply notification
    reply = Notification(
        organization_id=original_notification.organization_id,
        user_id=recipient_id,
        sender_user_id=user.id,
        notification_type='direct_message_reply', # A more specific type
        title=f"Re: {original_notification.parent.title if original_notification.parent else original_notification.title}",
        message=message,
        parent_notification_id=parent_id 
    )
    db.session.add(reply)
    db.session.commit()

    return jsonify({"message": "Reply sent successfully!"}), 201

@notification_bp.route('/<int:notification_id>/mark-thread-read', methods=['POST'])
@jwt_required()
def mark_thread_read(notification_id):
    """Marks all notifications in a thread as read for the current user."""
    user = _current_user()
    
    # Find the notification
    notification = Notification.query.get_or_404(notification_id)
    
    # Get the parent thread ID
    parent_id = notification.parent_notification_id or notification.id
    
    # Mark all notifications in this thread that belong to this user as read
    Notification.query.filter(
        or_(
            Notification.id == parent_id,
            Notification.parent_notification_id == parent_id
        ),
        Notification.user_id == user.id,
        Notification.read_at.is_(None)
    ).update({'read_at': datetime.utcnow()}, synchronize_session=False)
    
    db.session.commit()
    return jsonify({'message': 'Thread marked as read.'})