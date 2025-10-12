from functools import wraps
from flask import jsonify, g
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db

from app.models import User, OrganizationMembership, StudentAISubscription, StudentAIUsage

DEFAULT_GENERATE_LIMIT = 50
DEFAULT_VALIDATE_LIMIT = 50
DEFAULT_EXPLAIN_LIMIT = 50

def super_admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user and user.user_type == 'super_admin':
                kwargs['current_user'] = user
                return fn(*args, **kwargs)
            return jsonify({"message": "Super Admin access required."}), 403
        return decorator
    return wrapper

def admin_role_required(allowed_roles):
    """
    A flexible decorator to check for specific admin roles.
    It also validates that the user has an active membership in an active organization.
    
    :param allowed_roles: A list of user_type strings to allow (e.g., ['main_co_admin', 'co_admin'])
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # 1. Check if user exists and has an allowed role
            if not user or user.user_type not in allowed_roles:
                return jsonify({"message": "Permission denied for this role."}), 403

            # 2. Check for an active membership in an active organization
            membership = OrganizationMembership.query.filter_by(user_id=user.id, is_active=True).first()
            
            if not membership or not membership.organization or membership.organization.status != 'active':
                return jsonify({
                    "message": "Access denied. User is not linked to an active organization membership."
                }), 403

            # 3. If all checks pass, add user and organization to the view function's arguments
            kwargs['current_user'] = user
            kwargs['organization'] = membership.organization
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def student_required():
    """Checks for a logged-in Student."""
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user and user.user_type == 'student':
                kwargs['current_user'] = user
                return fn(*args, **kwargs)
            return jsonify({"message": "Student access required."}), 403
        return decorator
    return wrapper

def org_member_required():
    def decorator(fn):
        @wraps(fn)
        @jwt_required() 
        def wrapper(*args, **kwargs):
            # Assumes g.current_organization is loaded from subdomain
            if not g.current_organization:
                return jsonify({"message": "Organization context is required."}), 400
            
            user_id = get_jwt_identity()
            membership = OrganizationMembership.query.filter_by(
                user_id=user_id,
                organization_id=g.current_organization.id,
                is_active=True
            ).first()

            if not membership:
                return jsonify({"message": "You are not an active member of this organization."}), 403
            
            # Pass the current user and organization to the route
            kwargs['current_user'] = User.query.get(user_id)
            kwargs['organization'] = g.current_organization
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def _current_user_from_identity():
    """Support either int user_id or {'id': ..} identities."""
    ident = get_jwt_identity()
    user_id = ident.get('id') if isinstance(ident, dict) else ident
    return User.query.get(user_id)


def _has_active_premium(user_id: int) -> bool:
    now = datetime.utcnow()
    # ✅ respect user.is_premium as an instant override (optional but handy)
    user = User.query.get(user_id)
    if user and getattr(user, "is_premium", False):
        return True

    sub = StudentAISubscription.query.filter(
        StudentAISubscription.student_user_id == user_id,
        StudentAISubscription.status == 'active'
    ).first()
    if not sub:
        return False
    return sub.end_date is None or sub.end_date >= now


def premium_feature_required():
    """
    Allows Super Admin always; everyone else must have active premium.
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user = _current_user_from_identity()
            if not user:
                return jsonify({"message": "User not found."}), 404

            if user.user_type == 'super_admin' or _has_active_premium(user.id):
                kwargs['current_user'] = user
                return fn(*args, **kwargs)

            return jsonify({"message": "A premium AI subscription is required for this feature."}), 403
        return decorator
    return wrapper

def ai_premium_org_required():
    """
    Decorator to protect routes that require an organization-level AI subscription.
    Checks the 'is_ai_premium' flag on the organization.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Assumes your @admin_role_required decorator provides the organization object
            organization = kwargs.get('organization')
            if not organization:
                return jsonify({"message": "Organization context is required."}), 401

            if not organization.is_ai_premium:
                return jsonify({"message": "This is a premium feature for your organization. Please upgrade to access."}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def ai_usage_limited(feature_type: str):
    """
    Protects routes with usage limits.
    - Premium users: unlimited (we still record usage).
    - Free users: DEFAULT_* limits enforced per month.
    """
    assert feature_type in ('generate', 'validate', 'explain'), "feature_type must be 'generate', 'validate', or 'explain'"

    def decorator(fn):
        @wraps(fn)
        @jwt_required()  # ✅ ensure JWT context exists
        def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user') or _current_user_from_identity()
            if not current_user:
                return jsonify({"message": "Authentication required."}), 401

            now_month = datetime.utcnow().strftime("%Y-%m")
            usage = StudentAIUsage.query.filter_by(
                student_user_id=current_user.id,
                usage_month=now_month
            ).first()

            if not usage:
                usage = StudentAIUsage(
                    student_user_id=current_user.id,
                    usage_month=now_month,
                    generate_calls=0,
                    validate_calls=0,
                    explain_calls=0
                )
                db.session.add(usage)

            is_premium = _has_active_premium(current_user.id)

            if not is_premium:
                if feature_type == 'generate' and usage.generate_calls >= DEFAULT_GENERATE_LIMIT:
                    return jsonify({"message": f"You have reached your monthly limit of {DEFAULT_GENERATE_LIMIT} question generations."}), 403
                if feature_type == 'validate' and usage.validate_calls >= DEFAULT_VALIDATE_LIMIT:
                    return jsonify({"message": f"You have reached your monthly limit of {DEFAULT_VALIDATE_LIMIT} answer validations."}), 403
                if feature_type == 'explain' and usage.explain_calls >= DEFAULT_EXPLAIN_LIMIT:
                    return jsonify({"message": f"You have reached your monthly limit of {DEFAULT_EXPLAIN_LIMIT} explanations."}), 403

            # Record usage
            if feature_type == 'generate':
                usage.generate_calls = (usage.generate_calls or 0) + 1
            elif feature_type == 'validate':
                usage.validate_calls = (usage.validate_calls or 0) + 1
            elif feature_type == 'explain':
                usage.explain_calls = (usage.explain_calls or 0) + 1

            db.session.commit()
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def org_member_flexible():
    """New - works on both subdomain and global domain"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required() 
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id)
            
            if not current_user:
                return jsonify({"message": "User not found."}), 404
            
            organization = g.current_organization
            
            # If no subdomain org, get user's default/first organization
            if not organization:
                membership = OrganizationMembership.query.filter_by(
                    user_id=user_id,
                    is_active=True
                ).first()
                
                if not membership:
                    return jsonify({"message": "You are not a member of any organization."}), 403
                
                organization = membership.organization
            else:
                # Verify membership in subdomain org
                membership = OrganizationMembership.query.filter_by(
                    user_id=user_id,
                    organization_id=organization.id,
                    is_active=True
                ).first()
                
                if not membership:
                    return jsonify({"message": "You are not an active member of this organization."}), 403
            
            kwargs['current_user'] = current_user
            kwargs['organization'] = organization
            return fn(*args, **kwargs)
        return wrapper
    return decorator