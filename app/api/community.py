from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.community import ForumPost, ForumReply
from app.models.user import User

community_bp = Blueprint('community_api', __name__, url_prefix='/api/community')

# --- Helper Serializers ---

def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def serialize_reply(reply):
    return {
        'id': reply.id,
        'content': reply.content,
        'author_name': f"{reply.author.first_name} {reply.author.last_name}",
        'author_user_type': reply.author.user_type,
        'created_at': reply.created_at.isoformat()
    }

def serialize_post(post, include_replies=False):
    data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author_name': f"{post.author.first_name} {post.author.last_name}",
        'author_user_type': post.author.user_type,
        'organization_name': post.organization.name if post.organization else "Global",
        'created_at': post.created_at.isoformat(),
        'reply_count': post.replies.count()
    }
    if include_replies:
        data['replies'] = [serialize_reply(r) for r in post.replies.order_by(ForumReply.created_at.asc()).all()]
    return data

# --- API Routes ---

@community_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_forum_posts():
    """
    Context-aware route to fetch forum posts.
    - On a subdomain, shows that org's private posts + global posts.
    - On the main site, shows only global posts.
    """
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
    data = request.get_json()

    new_post = ForumPost(
        title=data.get('title'),
        content=data.get('content'),
        author_user_id=user_id,
        # If on a subdomain, associate it with the org. Otherwise, it's global (NULL).
        organization_id=g.current_organization.id if g.current_organization else None
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(serialize_post(new_post)), 201

@community_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_single_post(post_id):
    """Fetches a single post with all of its replies."""
    post = ForumPost.query.get_or_404(post_id)
    return jsonify(serialize_post(post, include_replies=True))

@community_bp.route('/posts/<int:post_id>/replies', methods=['POST'])
@jwt_required()
def add_reply_to_post(post_id):
    """Adds a new reply to a specific post."""
    user_id = get_jwt_identity()
    data = request.get_json()

    new_reply = ForumReply(
        post_id=post_id,
        content=data.get('content'),
        author_user_id=user_id
    )
    db.session.add(new_reply)
    db.session.commit()
    return jsonify(serialize_reply(new_reply)), 201

@community_bp.route('/posts/<int:post_id>/replies', methods=['GET'])
@jwt_required()
def get_post_replies(post_id):
    """Fetches all replies for a specific post."""
    try:
        replies = ForumReply.query.filter_by(post_id=post_id).order_by(ForumReply.created_at.asc()).all()
        return jsonify([serialize_reply(r) for r in replies])
    except Exception as e:
        return jsonify({"message": f"Could not load replies: {str(e)}"}), 500
