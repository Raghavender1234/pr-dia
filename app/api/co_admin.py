from flask import Blueprint, jsonify, current_app
from app import db
from app.models.question import Question
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.mock_test import MockTest
from sqlalchemy import func
from .decorators import admin_role_required

co_admin_bp = Blueprint('co_admin_api', __name__, url_prefix='/api/co-admin')

@co_admin_bp.route('/dashboard/summary', methods=['GET'])
@admin_role_required(allowed_roles=['co_admin'])
def get_co_admin_summary(current_user, organization, **kwargs):
    """Provides summary statistics for the Co-Admin dashboard."""
    try:
        total_questions_in_org = db.session.query(Question).join(Topic).join(Subject).join(Exam).filter(
            Exam.organization_id == organization.id,
            Question.parent_question_id == None,
            Question.deleted_at == None  # Only active questions
        ).count()

        active_mock_tests = db.session.query(MockTest).join(Exam).filter(
            Exam.organization_id == organization.id,
            MockTest.status == 'active'
        ).count()

        return jsonify({
            "total_questions_in_org": total_questions_in_org,
            "active_mock_tests": active_mock_tests
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching co-admin summary: {e}", exc_info=True)
        return jsonify({"message": "Could not load dashboard statistics."}), 500

@co_admin_bp.route('/question-type-distribution', methods=['GET'])
@admin_role_required(allowed_roles=['co_admin'])
def get_question_type_distribution(current_user, organization, **kwargs):
    """Provides the breakdown of question types for the co-admin's organization."""
    try:
        question_counts = db.session.query(Question.question_type, func.count(Question.id))\
            .join(Topic).join(Subject).join(Exam)\
            .filter(
                Exam.organization_id == organization.id,
                Question.parent_question_id == None,
                Question.deleted_at == None
            )\
            .group_by(Question.question_type).all()
        
        labels = [q_type for q_type, count in question_counts]
        counts = [count for q_type, count in question_counts]

        return jsonify({"labels": labels, "counts": counts}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching question distribution: {e}", exc_info=True)
        return jsonify({"message": "Could not load chart data."}), 500
