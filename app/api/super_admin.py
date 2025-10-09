# backend/app/api/super_admin.py (Verify these imports are present at the top)
from flask import Blueprint, request, jsonify, current_app
from app import db
import json
from werkzeug.security import generate_password_hash
from app.models.organization import Plan, Organization, OrganizationMembership, OrganizationReport
from app.models.user import User
from app.models.subject import Subject
from app.models.question import Question
from app.models.exam import Exam
from app.models.topic import Topic
from app.models.student_progress import StudentTestAttempt # Added for activity feed
from app.models.mock_test import MockTest # Added for activity feed
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func
from .decorators import super_admin_required

super_admin_bp = Blueprint('super_admin_api', __name__, url_prefix='/api/super-admin')

def serialize_organization(org):
    """Converts an Organization SQLAlchemy object into a JSON-friendly dictionary."""
    if not org:
        return None
    
    return {
        "id": org.id,
        "name": org.name,
        "code": org.code,
        "plan": org.plan.name if org.plan else "N/A", # Safely get plan name
        "status": org.status,
        "is_verified": org.is_verified,
        "subdomain": org.subdomain,
        "logo_url": org.logo_url,
        "created_at": org.created_at.isoformat() if org.created_at else None
    }

@super_admin_bp.route('/dashboard/summary', methods=['GET'])
@super_admin_required()
def get_super_admin_summary(current_user, **kwargs):
    first_name = current_user.first_name
    total_organizations = Organization.query.count()
    total_users = User.query.filter(User.user_type != 'super_admin').count()
    active_plans = Plan.query.filter_by(status='active').count()
    total_questions = Question.query.filter(Question.parent_question_id.is_(None)).count()
    return jsonify({
        "first_name": first_name, "total_organizations": total_organizations, "total_users": total_users,
        "active_plans": active_plans, "total_questions": total_questions
    }), 200

@super_admin_bp.route('/user_roles', methods=['GET'])
@super_admin_required()
def get_user_roles_distribution(current_user, **kwargs):
    user_role_counts = db.session.query(User.user_type, func.count(User.id)).filter(User.user_type != 'super_admin').group_by(User.user_type).all()
    labels = [role.replace('_', ' ').title() for role, _ in user_role_counts]
    counts = [count for _, count in user_role_counts]
    return jsonify({"labels": labels, "counts": counts}), 200

@super_admin_bp.route('/activity', methods=['GET'])
@super_admin_required()
def get_recent_activity(current_user, **kwargs):
    limit = request.args.get('limit', 8, type=int)
    recent_users = User.query.order_by(User.created_at.desc()).limit(limit).all()
    activity_list = [{"message": f"New user: {user.first_name} registered.", "timestamp": user.created_at.isoformat()} for user in recent_users]
    return jsonify(activity_list), 200


# --- THIS IS THE SINGLE, CORRECTED FUNCTION for Organizations ---
@super_admin_bp.route('/organizations', methods=['GET'])
@super_admin_required()
def get_all_organizations(current_user, **kwargs):
    """
    Provides a list of ALL organizations with full details for the management table.
    This new version actively counts the members instead of relying on stored numbers.
    """
    try:
        orgs = Organization.query.order_by(Organization.created_at.desc()).all()
        output = []
        for org in orgs:
            # --- THIS IS THE FIX ---
            # We calculate the counts live by checking the memberships for each organization.
            student_count = 0
            co_admin_count = 0
            for member in org.memberships:
                if member.is_active:
                    if member.user.user_type == 'student':
                        student_count += 1
                    elif member.user.user_type == 'co_admin':
                        co_admin_count += 1
            # --- END OF FIX ---

            output.append({
                'id': org.id,
                'name': org.name,
                'org_code': org.code,
                'plan_name': org.plan.name if org.plan else 'N/A',
                'status': org.status,
                'current_student_count': student_count, # Use the live count
                'current_coadmin_count': co_admin_count, # Use the live count
                'is_verified': org.is_verified, 
                'created_at': org.created_at.isoformat()
            })
        return jsonify(output), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_all_organizations: {e}", exc_info=True)
        return jsonify({"message": "Could not load organizations list."}), 500

@super_admin_bp.route('/plans', methods=['POST'])
@super_admin_required()
def create_plan(current_user, **kwargs):
    data = request.get_json()
    name = data.get('name')
    monthly_price = data.get('monthly_price')
    max_coadmins = data.get('max_coadmins')
    max_students = data.get('max_students')
    description = data.get('description')

    if not all([name, monthly_price, max_coadmins, max_students]):
        return jsonify({"message": "Missing required plan fields"}), 400
    
    try:
        new_plan = Plan(
            name=name,
            monthly_price=monthly_price,
            max_coadmins=max_coadmins,
            max_students=max_students,
            description=description
        )
        db.session.add(new_plan)
        db.session.commit()
        return jsonify({"message": "Plan created successfully", "plan_id": new_plan.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating plan: {str(e)}"}), 500

@super_admin_bp.route('/plans', methods=['GET'])
@super_admin_required()
def get_all_plans(current_user, **kwargs):
    plans = Plan.query.all()
    output = []
    for plan in plans:
        output.append({
            'id': plan.id,
            'name': plan.name,
            'monthly_price': str(plan.monthly_price),
            'max_coadmins': plan.max_coadmins,
            "max_free_exams": plan.max_free_exams,
            'max_invited_students': plan.max_invited_students,
            'description': plan.description,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat()
        })
    return jsonify(output), 200

@super_admin_bp.route('/plans/<int:plan_id>', methods=['GET'])
@super_admin_required()
def get_plan(plan_id, current_user, **kwargs):
    plan = Plan.query.get_or_404(plan_id)
    return jsonify({
        'id': plan.id,
        'name': plan.name,
        'monthly_price': str(plan.monthly_price),
        'max_coadmins': plan.max_coadmins,
        # THIS IS THE FIX
        'max_invited_students': plan.max_invited_students, # Use the new correct name
        'description': plan.description,
        'created_at': plan.created_at.isoformat(),
        'updated_at': plan.updated_at.isoformat()
    }), 200

@super_admin_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@super_admin_required()
def update_plan(plan_id, current_user, **kwargs):
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json()
    
    plan.name = data.get('name', plan.name)
    plan.monthly_price = data.get('monthly_price', plan.monthly_price)
    plan.max_coadmins = data.get('max_coadmins', plan.max_coadmins)
    # THIS IS THE FIX
    plan.max_invited_students = data.get('max_invited_students', plan.max_invited_students) # Use the new correct name
    plan.description = data.get('description', plan.description)

    try:
        db.session.commit()
        return jsonify({"message": "Plan updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating plan: {str(e)}"}), 500

@super_admin_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@super_admin_required()
def delete_plan(plan_id, current_user, **kwargs):
    plan = Plan.query.get(plan_id)
    if not plan:
        return jsonify({"message": "Plan not found"}), 404
    
    # Check for dependent organizations
    if plan.organizations:
        return jsonify({"message": "Cannot delete plan with associated organizations. Please reassign organizations first."}), 400

    try:
        db.session.delete(plan)
        db.session.commit()
        return jsonify({"message": "Plan deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting plan: {str(e)}"}), 500
    
@super_admin_bp.route('/organizations/<int:org_id>/toggle-verification', methods=['POST'])
@super_admin_required()
def toggle_organization_verification(org_id, current_user, **kwargs):
    """Toggles the verification status of an organization."""
    org = Organization.query.get_or_404(org_id)
    try:
        # Flip the boolean status
        org.is_verified = not org.is_verified
        db.session.commit()
        new_status = "Verified" if org.is_verified else "Not Verified"
        return jsonify({"message": f"Organization '{org.name}' status set to {new_status}."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating verification status."}), 500

# --- Organization Management Endpoints ---

@super_admin_bp.route('/organizations', methods=['POST'])
@super_admin_required()
def create_organization(current_user, **kwargs):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request body."}), 400

    required_fields = ['name', 'code', 'plan_id', 'main_co_admin_email', 'main_co_admin_password']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields."}), 400

    try:
        # Check if an active organization already exists with the same code
        existing_org = Organization.query.filter_by(code=data['code'], status='active').first()
        if existing_org:
            return jsonify({"message": "This organization code is already in use by an active organization."}), 409

        # Create the new organization
        new_organization = Organization(
            name=data['name'],
            code=data['code'],
            plan_id=data['plan_id'],
            status='active'
        )
        db.session.add(new_organization)
        db.session.flush()  # Get new_organization.id

        # Check for existing user with the same email
        existing_user = User.query.filter_by(email=data['main_co_admin_email']).first()

        if existing_user:
            if existing_user.status != 'active':
                # Reactivate and update the user
                existing_user.first_name = data.get('main_co_admin_first_name')
                existing_user.last_name = data.get('main_co_admin_last_name')
                existing_user.password_hash = generate_password_hash(data['main_co_admin_password'])
                existing_user.user_type = 'main_co_admin'
                existing_user.status = 'active'
                db.session.flush()
                user_id = existing_user.id
            else:
                return jsonify({"message": "An active account with this email already exists."}), 409
        else:
            # Create a new main co-admin user
            main_co_admin = User(
                first_name=data.get('main_co_admin_first_name'),
                last_name=data.get('main_co_admin_last_name'),
                email=data['main_co_admin_email'],
                password_hash=generate_password_hash(data['main_co_admin_password']),
                user_type='main_co_admin',
                status='active'
            )
            db.session.add(main_co_admin)
            db.session.flush()
            user_id = main_co_admin.id

        # Create the membership link between user and org
        membership = OrganizationMembership(
            user_id=user_id,
            organization_id=new_organization.id,
            is_active=True,
            access_type='admin_created'
        )
        db.session.add(membership)

        # Commit all changes
        db.session.commit()

        return jsonify({"message": "Organization and Main Co-Admin created successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating organization: {e}", exc_info=True)
        return jsonify({"message": "An internal server error occurred."}), 500

@super_admin_bp.route('/organizations/<int:org_id>', methods=['GET'])
@super_admin_required()
def get_organization(org_id, current_user, **kwargs):
    org = Organization.query.get_or_404(org_id)
    
    members = []
    for membership in org.memberships:
        members.append({
            'user_id': membership.user.id,
            'email': membership.user.email,
            'full_name': f"{membership.user.first_name} {membership.user.last_name}",
            'user_type': membership.user.user_type,
            'status': membership.user.status,
            'is_active_in_org': membership.is_active,
            'joined_at': membership.joined_at.isoformat(),
        })

    return jsonify({
        'id': org.id,
        'name': org.name,
        'org_code': org.code, # <<< THIS IS THE FIX: The key is now 'org_code' for consistency
        'plan_id': org.plan_id,
        'plan_name': org.plan.name if org.plan else 'N/A',
        'status': org.status,
        'current_invited_student_count': org.current_invited_student_count,
        'current_coadmin_count': org.current_coadmin_count,
        'created_at': org.created_at.isoformat(),
        'updated_at': org.updated_at.isoformat(),
        'subdomain': org.subdomain, 
        'members': members
    }), 200

@super_admin_bp.route('/organizations/<int:org_id>', methods=['PUT'])
@super_admin_required()
def update_organization(org_id, current_user, **kwargs):
    org = Organization.query.get_or_404(org_id)
    data = request.get_json()

    # --- THIS IS THE BULLETPROOF FIX ---
    # It checks if the data was accidentally corrupted into a string.
    if isinstance(data, str):
        try:
            # If it's a string, we try to parse it back into a dictionary.
            data = json.loads(data)
        except json.JSONDecodeError:
            # If it's a string but not valid JSON, then it's a real error.
            return jsonify({"message": "Invalid data format received."}), 400

    # The rest of the function can now proceed safely.
    subdomain = data.get('subdomain', '').strip().lower()
    if subdomain:
        existing_org = Organization.query.filter(
            Organization.id != org_id, 
            Organization.subdomain == subdomain
        ).first()
        if existing_org:
            return jsonify({"message": f"Subdomain '{subdomain}' is already taken."}), 409
        org.subdomain = subdomain
    else:
        org.subdomain = None

    if 'name' in data: org.name = data['name']
    if 'code' in data: org.code = data['code']
    if 'plan_id' in data: org.plan_id = data['plan_id']
    if 'status' in data: org.status = data['status']

    try:
        db.session.commit()
        return jsonify({"message": "Organization updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating organization {org_id}: {e}")
        return jsonify({"message": "An error occurred while updating."}), 500

@super_admin_bp.route('/organizations/<int:org_id>', methods=['DELETE'])
@super_admin_required()
def delete_organization(org_id, current_user, **kwargs):
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"message": "Organization not found"}), 404
    
    # Due to cascade="all, delete-orphan" on relationships in Organization model,
    # deleting the organization should automatically delete associated memberships, exams, mock tests, etc.
    # However, it's good practice to be explicit or at least aware of cascading deletes.
    # We might want to prevent deletion if there's active student data, etc., in a real app.
    
    try:
        db.session.delete(org)
        db.session.commit()
        return jsonify({"message": "Organization and related data deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting organization: {str(e)}"}), 500


# --- User Management (Super Admin's view) ---
@super_admin_bp.route('/users', methods=['GET'])
@super_admin_required()
def get_all_users(current_user, **kwargs):
    organization_id = request.args.get('organization_id', type=int)

    query = User.query

    if organization_id:
        query = query.join(OrganizationMembership).filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.is_active == True
        )

    users = query.all()
    output = []

    for user in users:
        # ✅ FIXED: Get the first active membership safely from list
        org_membership = next((m for m in user.memberships if m.is_active), None)
        org_name = org_membership.organization.name if org_membership and org_membership.organization else None

        output.append({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
            'status': user.status,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'organization_name': org_name
        })

    return jsonify(output), 200

@super_admin_bp.route('/users/<int:user_id>', methods=['GET'])
@super_admin_required()
def get_user_by_id(user_id, current_user, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_type': user.user_type,
        'status': user.status,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }), 200

@super_admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@super_admin_required()
def update_user_status(user_id, current_user, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status or new_status not in ['active', 'inactive', 'pending_approval']:
        return jsonify({"message": "Invalid status provided"}), 400
    
    user.status = new_status
    try:
        db.session.commit()
        return jsonify({"message": f"User {user_id} status updated to {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating user status: {str(e)}"}), 500

@super_admin_bp.route('/users/<int:user_id>/type', methods=['PUT'])
@super_admin_required()
def update_user_type(user_id, current_user, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.get_json()
    new_user_type = data.get('user_type')
    
    if not new_user_type or new_user_type not in ['admin', 'main_co_admin', 'co_admin', 'student']:
        return jsonify({"message": "Invalid user type provided"}), 400
    
    # Prevent changing a user's type to 'admin' without specific authorization/process.
    # For now, we'll allow it as it's for the super_admin API.
    # In a real app, this might have more complex logic.
    user.user_type = new_user_type
    try:
        db.session.commit()
        return jsonify({"message": f"User {user_id} type updated to {new_user_type}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating user type: {str(e)}"}), 500

@super_admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@super_admin_required()
def delete_user(user_id, current_user, **kwargs):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Prevent deleting the last Super Admin user if this is the only one.
    if user.user_type == 'super_admin' and User.query.filter_by(user_type='super_admin').count() == 1:
        return jsonify({"message": "Cannot delete the last Super Admin user"}), 400

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User and associated memberships/data deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting user: {str(e)}"}), 500
    
@super_admin_bp.route('/question_stats', methods=['GET'])
@super_admin_required()
def get_question_statistics(current_user, **kwargs):
    question_type_counts = db.session.query(Question.question_type, func.count(Question.id)).group_by(Question.question_type).all()

    labels = [q_type for q_type, count in question_type_counts]
    counts = [count for q_type, count in question_type_counts]

    return jsonify({
        "labels": labels,
        "counts": counts
    }), 200

@super_admin_bp.route('/archived-content', methods=['GET'])
@super_admin_required()
def get_archived_content(current_user, **kwargs):
    """Fetches all soft-deleted items for the recycle bin."""
    try:
        archived_exams = Exam.query.filter(Exam.deleted_at.isnot(None)).all()
        archived_subjects = Subject.query.filter(Subject.deleted_at.isnot(None)).all()
        archived_topics = Topic.query.filter(Topic.deleted_at.isnot(None)).all()
        archived_questions = Question.query.filter(Question.deleted_at.isnot(None)).all()
        archived_mock_tests = MockTest.query.filter(MockTest.deleted_at.isnot(None)).all()

        return jsonify({
            "exams": [{"id": e.id, "name": e.name, "deleted_at": e.deleted_at.isoformat()} for e in archived_exams],
            "subjects": [{"id": s.id, "name": s.name, "deleted_at": s.deleted_at.isoformat()} for s in archived_subjects],
            "topics": [{"id": t.id, "name": t.name, "deleted_at": t.deleted_at.isoformat()} for t in archived_topics],
            "questions": [{"id": q.id, "name": q.question_text[:80] + '...', "deleted_at": q.deleted_at.isoformat()} for q in archived_questions],
            "mock_tests": [{"id": m.id, "name": m.name, "deleted_at": m.deleted_at.isoformat()} for m in archived_mock_tests],
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching archived content: {e}")
        return jsonify({"message": "Could not load archived content."}), 500

@super_admin_bp.route('/archived-content/restore', methods=['POST'])
@super_admin_required()
def restore_archived_content(current_user, **kwargs):
    """
    Restores a soft-deleted item and its entire parent hierarchy.
    """
    data = request.get_json()
    item_type = data.get('item_type')
    model_map = {"exam": Exam, "subject": Subject, "topic": Topic, "question": Question, "mock_test": MockTest}
    Model = model_map.get(item_type)
    
    if not Model:
        return jsonify({"message": "Invalid item type specified."}), 400

    item = Model.query.get_or_404(item_id)
    
    try:
        # Restore the item itself
        item.deleted_at = None
        
        # --- NEW: Cascading Restore Logic ---
        # Traverse up the hierarchy and restore parents if they are archived.
        current_item = item
        while True:
            parent = None
            if hasattr(current_item, 'topic') and current_item.topic:
                parent = current_item.topic
            elif hasattr(current_item, 'subject') and current_item.subject:
                parent = current_item.subject
            elif hasattr(current_item, 'exam') and current_item.exam:
                parent = current_item.exam
            
            if parent and parent.deleted_at is not None:
                parent.deleted_at = None
                current_item = parent # Move up the chain
            else:
                break # Stop when there's no parent or the parent is already active
        
        db.session.commit()
        return jsonify({"message": f"{item_type.capitalize()} and its parent containers have been restored."}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error restoring item: {e}")
        return jsonify({"message": "An error occurred during restoration."}), 500

@super_admin_bp.route('/archived-content/permanent-delete', methods=['POST'])
@super_admin_required()
def permanently_delete_content(current_user, **kwargs):
    """Permanently deletes an archived item. This is irreversible."""
    data = request.get_json()
    item_type = data.get('item_type')
    model_map = {"exam": Exam, "subject": Subject, "topic": Topic, "question": Question, "mock_test": MockTest}
    Model = model_map.get(item_type)

    if not Model:
        return jsonify({"message": "Invalid item type specified."}), 400

    item = Model.query.get_or_404(item_id)
    
    # You could add extra safety checks here if needed
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({"message": f"{item_type.capitalize()} has been permanently deleted."}), 200

@super_admin_bp.route('/archived-content/bulk-permanent-delete', methods=['POST'])
@super_admin_required()
def bulk_permanently_delete_content(current_user, **kwargs):
    """
    Permanently deletes a list of archived items of various types.
    Expects a list of objects, e.g., [{"item_type": "question", "item_id": 1}, ...]
    """
    data = request.get_json()
    items_to_delete = request.get_json(force=True)

    if not items_to_delete or not isinstance(items_to_delete, list):
        return jsonify({"message": "A list of items to delete is required."}), 400

    model_map = {"exam": Exam, "subject": Subject, "topic": Topic, "question": Question, "mock_test": MockTest}
    
    try:
        for item_data in items_to_delete:
            item_type = item_data.get('item_type')
            item_id = item_data.get('item_id')
            Model = model_map.get(item_type)

            if Model and item_id:
                item_to_delete = Model.query.get(item_id)
                if item_to_delete:
                    # Additional check: ensure it was actually soft-deleted before permanent deletion
                    if hasattr(item_to_delete, 'deleted_at') and item_to_delete.deleted_at:
                        db.session.delete(item_to_delete)
        
        db.session.commit()
        return jsonify({"message": f"Successfully deleted {len(items_to_delete)} items permanently."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during bulk permanent deletion: {e}", exc_info=True)
        return jsonify({"message": "An error occurred during permanent deletion."}), 500

@super_admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@super_admin_required()
def update_user_details(user_id, current_user, **kwargs):
    """Updates a user's details."""
    user = User.query.get_or_404(user_id)
    if user.user_type == 'super_admin':
        return jsonify({"message": "Cannot modify a Super Admin account."}), 403

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request."}), 400

    # Check if the new email is already taken by another user
    new_email = data.get('email')
    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({"message": f"Email '{new_email}' is already in use."}), 409
        user.email = new_email

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)

    try:
        db.session.commit()
        return jsonify({"message": "User details updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user details: {e}", exc_info=True)
        return jsonify({"message": "An error occurred while saving."}), 500


@super_admin_bp.route('/organizations/pending', methods=['GET'])
@super_admin_required()
def get_pending_organizations(current_user, **kwargs):
    """Fetches all organizations with a 'pending_approval' status."""
    try:
        pending_orgs = Organization.query.filter_by(status='pending_approval').all()
        # You'll need a serializer function for your Organization model
        return jsonify([serialize_organization(org) for org in pending_orgs])
    except Exception as e:
        current_app.logger.error(f"Error fetching pending organizations: {e}")
        return jsonify({"message": "Could not retrieve pending organizations."}), 500


@super_admin_bp.route('/organizations/<int:org_id>/approve', methods=['POST'])
@super_admin_required()
def approve_organization(current_user, org_id, **kwargs):
    """Approves an organization and activates its main admin."""
    try:
        organization = Organization.query.get_or_404(org_id)
        if organization.status != 'pending_approval':
            return jsonify({"message": "Organization is not pending approval."}), 400

        organization.status = 'active'
        
        # Find and activate the main co-admin for this organization
        admin_membership = OrganizationMembership.query.join(User).filter(
            OrganizationMembership.organization_id == org_id,
            User.user_type == 'main_co_admin'
        ).first()

        if admin_membership and admin_membership.user:
            admin_membership.user.status = 'active'
            admin_membership.is_active = True
            # You can add logic here to send a "Welcome! Your account is active" email
            # send_email(admin_membership.user.email, "Your Organization is Approved!", "...")

        db.session.commit()
        return jsonify({"message": f"Organization '{organization.name}' has been approved and is now active."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving organization {org_id}: {e}")
        return jsonify({"message": "An error occurred during approval."}), 500

@super_admin_bp.route('/organizations/<int:org_id>/reject', methods=['POST'])
@super_admin_required()
def reject_organization(current_user, org_id, **kwargs):
    """Rejects a pending organization and deactivates its admin."""
    try:
        organization = Organization.query.get_or_404(org_id)
        if organization.status != 'pending_approval':
            return jsonify({"message": "Organization is not pending approval."}), 400

        # Set status to 'rejected'. This keeps a record without deleting the data.
        organization.status = 'rejected'
        
        # Find and deactivate the main co-admin and their membership
        admin_membership = OrganizationMembership.query.join(User).filter(
            OrganizationMembership.organization_id == org_id,
            User.user_type == 'main_co_admin'
        ).first()

        if admin_membership:
            if admin_membership.user:
                admin_membership.user.status = 'rejected'
            admin_membership.is_active = False

        db.session.commit()
        # You could also send an email here informing them of the rejection
        
        return jsonify({"message": f"Organization '{organization.name}' has been rejected."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting organization {org_id}: {e}")
        return jsonify({"message": "An error occurred during rejection."}), 500

@super_admin_bp.route('/organization-reports', methods=['GET'])
@super_admin_required()
def get_organization_reports(current_user, **kwargs):
    """Fetches all pending organization reports."""
    try:
        reports = OrganizationReport.query.filter_by(status='pending').order_by(OrganizationReport.reported_at.asc()).all()
        
        report_data = [{
            "report_id": report.id,
            "organization_id": report.organization_id,
            "organization_name": report.organization.name,
            "reason": report.reason.replace('_', ' ').title(),
            "comments": report.comments,
            "reporter_email": report.reporter.email,
            "reported_at": report.reported_at.isoformat()
        } for report in reports]
        
        return jsonify(report_data)
    except Exception as e:
        current_app.logger.error(f"Error fetching organization reports: {e}")
        return jsonify({"message": "Could not retrieve reports."}), 500

@super_admin_bp.route('/organization-reports/<int:report_id>/resolve', methods=['POST'])
@super_admin_required()
def resolve_organization_report(current_user, report_id, **kwargs):
    """Resolves a report by marking its status as resolved (e.g., after a warning was sent)."""
    try:
        report = OrganizationReport.query.get_or_404(report_id)
        report.status = 'resolved_warning_sent'
        db.session.commit()
        # You could add logic here to send a warning email to the organization's admin
        return jsonify({"message": "Report has been marked as resolved."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while resolving the report."}), 500

@super_admin_bp.route('/organization-reports/<int:report_id>/suspend', methods=['POST'])
@super_admin_required()
def suspend_organization_from_report(current_user, report_id, **kwargs):
    """Suspends an organization based on a report."""
    try:
        report = OrganizationReport.query.get_or_404(report_id)
        organization = report.organization
        
        organization.status = 'suspended' # Change the organization's main status
        report.status = 'resolved_account_suspended'
        
        # Deactivate all memberships for that organization
        OrganizationMembership.query.filter_by(organization_id=organization.id).update({"is_active": False})
        
        db.session.commit()
        return jsonify({"message": f"Organization '{organization.name}' has been suspended."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while suspending the organization."}), 500
