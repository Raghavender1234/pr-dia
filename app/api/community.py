from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.community import ForumPost, ForumReply
from app.models.class_management import Notification
from app.models.organization import OrganizationMembership
from app.models.user import User
from app.api.main_co_admin import _upload_file_to_s3
from app.utils.membership import can_access_internal_org_features

community_bp = Blueprint('community_api', __name__, url_prefix='/api/community')

# --- Helper Serializers ---

def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def _membership_for_org(user_id, organization_id):
    if not organization_id:
        return None
    return OrganizationMembership.query.filter_by(
        user_id=user_id,
        organization_id=organization_id,
        is_active=True
    ).first()


def _can_use_community(user, organization_id):
    if user and user.user_type in ['main_co_admin', 'co_admin', 'super_admin']:
        return True
    return can_access_internal_org_features(user, _membership_for_org(user.id, organization_id))


def serialize_reply(reply):
    return {
        'id': reply.id,
        'content': reply.content,
        'attachment_url': getattr(reply, 'attachment_url', None),
        'attachment_name': getattr(reply, 'attachment_name', None),
        'author_name': f"{reply.author.first_name} {reply.author.last_name}",
        'author_user_type': reply.author.user_type,
        'created_at': reply.created_at.isoformat()
    }

def serialize_post(post, include_replies=False):
    data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'attachment_url': getattr(post, 'attachment_url', None),
        'attachment_name': getattr(post, 'attachment_name', None),
        'author_name': f"{post.author.first_name} {post.author.last_name}",
        'author_user_type': post.author.user_type,
        'organization_name': post.organization.name if post.organization else "Global",
        'created_at': post.created_at.isoformat(),
        'reply_count': post.replies.count()
    }
    if include_replies:
        data['replies'] = [serialize_reply(r) for r in post.replies.order_by(ForumReply.created_at.asc()).all()]
    return data

def notify_org_members_about_post(post, author_id):
    if not post.organization_id:
        return

    members = OrganizationMembership.query.filter(
        OrganizationMembership.organization_id == post.organization_id,
        OrganizationMembership.is_active == True,
        OrganizationMembership.access_type == 'internal',
        OrganizationMembership.user_id != author_id
    ).all()

    for member in members:
        db.session.add(Notification(
            organization_id=post.organization_id,
            user_id=member.user_id,
            sender_user_id=author_id,
            notification_type='community_post',
            title=f"New community post: {post.title}",
            message=(post.content or '')[:240],
            link=f"/forum/post/{post.id}"
        ))

def notify_post_author_about_reply(post, reply):
    if not post.organization_id or post.author_user_id == reply.author_user_id:
        return

    db.session.add(Notification(
        organization_id=post.organization_id,
        user_id=post.author_user_id,
        sender_user_id=reply.author_user_id,
        notification_type='community_reply',
        title=f"New reply to: {post.title}",
        message=(reply.content or '')[:240],
        link=f"/forum/post/{post.id}"
    ))

# --- API Routes ---

@community_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_forum_posts():
    """
    Context-aware route to fetch forum posts.
    - On a subdomain, shows that org's private posts + global posts.
    - On the main site, shows only global posts.
    """
    user = _current_user()
    if user.user_type == 'student' and not _can_use_community(user, g.current_organization.id if g.current_organization else None):
        return jsonify({"message": "Community access is available only to internally invited students."}), 403

    if g.current_organization:
        # On a subdomain, show this org's private posts AND global posts
        posts = ForumPost.query.filter(
            (ForumPost.organization_id == g.current_organization.id) |
            (ForumPost.organization_id.is_(None))
        ).order_by(ForumPost.created_at.desc()).all()
    else:
        # On the main site, show ONLY global posts
        posts = ForumPost.query.filter(
            ForumPost.organization_id.is_(None)
        ).order_by(ForumPost.created_at.desc()).all()
        
    return jsonify([serialize_post(p) for p in posts])

@community_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_forum_post():
    """Creates a new forum post, making it private if on a subdomain."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    organization_id = g.current_organization.id if g.current_organization else None
    if user.user_type == 'student' and not _can_use_community(user, organization_id):
        return jsonify({"message": "Community access is available only to internally invited students."}), 403

    data = request.get_json()

    new_post = ForumPost(
        title=data.get('title'),
        content=data.get('content'),
        author_user_id=user_id,
        # If on a subdomain, associate it with the org. Otherwise, it's global (NULL).
        organization_id=organization_id
    )
    db.session.add(new_post)
    db.session.flush()
    notify_org_members_about_post(new_post, user_id)
    db.session.commit()
    return jsonify(serialize_post(new_post)), 201

@community_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_single_post(post_id):
    """Fetches a single post with all of its replies."""
    post = ForumPost.query.get_or_404(post_id)
    user = _current_user()
    if user.user_type == 'student' and not _can_use_community(user, post.organization_id):
        return jsonify({"message": "Community access is available only to internally invited students."}), 403
    return jsonify(serialize_post(post, include_replies=True))

@community_bp.route('/posts/<int:post_id>/replies', methods=['POST'])
@jwt_required()
def add_reply_to_post(post_id):
    """Adds a new reply to a specific post."""
    user_id = get_jwt_identity()
    data = request.get_json()
    post = ForumPost.query.get_or_404(post_id)
    user = User.query.get(user_id)
    if user.user_type == 'student' and not _can_use_community(user, post.organization_id):
        return jsonify({"message": "Community access is available only to internally invited students."}), 403

    new_reply = ForumReply(
        post_id=post_id,
        content=data.get('content'),
        author_user_id=user_id
    )
    db.session.add(new_reply)
    db.session.flush()
    notify_post_author_about_reply(post, new_reply)
    db.session.commit()
    return jsonify(serialize_reply(new_reply)), 201

@community_bp.route('/posts/<int:post_id>/replies', methods=['GET'])
@jwt_required()
def get_post_replies(post_id):
    """Fetches all replies for a specific post."""
    try:
        post = ForumPost.query.get_or_404(post_id)
        user = _current_user()
        if user.user_type == 'student' and not _can_use_community(user, post.organization_id):
            return jsonify({"message": "Community access is available only to internally invited students."}), 403

        replies = ForumReply.query.filter_by(post_id=post_id).order_by(ForumReply.created_at.asc()).all()
        return jsonify([serialize_reply(r) for r in replies])
    except Exception as e:
        return jsonify({"message": f"Could not load replies: {str(e)}"}), 500
