# backend/app/api/payment.py
import os
import hmac
import hashlib
from functools import wraps
from datetime import datetime, timedelta

import razorpay
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership, OrganizationAISubscription
from app.models.exam import Exam
from app.models.student_progress import StudentExam, StudentAISubscription
from app.api.decorators import admin_role_required

payment_bp = Blueprint('payment_api', __name__, url_prefix='/api/payment')

razorpay_client = None
# ---------- helpers ----------
def get_razorpay_client():
    """Create/reuse a singleton Razorpay client using app config/env."""
    from razorpay import Client as RazorpayClient
    global razorpay_client

    if razorpay_client is None:
        key_id = current_app.config.get('RAZORPAY_KEY_ID') or os.getenv('RAZORPAY_KEY_ID')
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET') or os.getenv('RAZORPAY_KEY_SECRET')
        if not key_id or not key_secret:
            raise RuntimeError("Razorpay keys are not configured (RAZORPAY_KEY_ID/SECRET).")

        razorpay_client = RazorpayClient(auth=(key_id, key_secret))
    return razorpay_client

def _get_rzp():
    key_id = current_app.config.get('RAZORPAY_KEY_ID') or os.getenv("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET') or os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise RuntimeError("Razorpay keys are not configured.")
    client = razorpay.Client(auth=(key_id, key_secret))
    return client


# ---------- Webhook Handlers ----------
def handle_subscription_charged(payload):
    subscription_payload = payload.get('subscription', {}).get('entity', {})
    subscription_id = subscription_payload.get('id')
    notes = subscription_payload.get('notes', {})
    sub_type = notes.get('type')

    if not subscription_id:
        current_app.logger.error("'subscription.charged' webhook missing subscription ID.")
        return

    # Handle Org AI Assistant Subscription
    if sub_type == 'org_ai_assistant':
        org_sub = OrganizationAISubscription.query.filter_by(razorpay_subscription_id=subscription_id).first()
        if org_sub:
            org_sub.status = 'active'
            org_sub.ends_at = datetime.fromtimestamp(subscription_payload['current_end'])
            if org_sub.organization:
                org_sub.organization.is_ai_premium = True
            current_app.logger.info(f"Organization {org_sub.organization_id} AI Assistant subscription renewed. New end date: {org_sub.ends_at}")
        else:
            current_app.logger.warning(f"Received 'subscription.charged' for unknown Org AI sub ID: {subscription_id}")
        return

    # Handle Student AI Tutor Subscription
    if sub_type == 'ai_tutor_student':
        student_sub = StudentAISubscription.query.filter_by(razorpay_subscription_id=subscription_id).first()
        if student_sub:
            student_sub.status = 'active'
            student_sub.end_date = datetime.fromtimestamp(subscription_payload['current_end'])
            student_sub.next_payment_date = datetime.fromtimestamp(subscription_payload['charge_at']) if subscription_payload.get('charge_at') else None
            current_app.logger.info(f"Student {student_sub.student_user_id} AI subscription renewed. New end date: {student_sub.end_date}")
        else:
            current_app.logger.warning(f"Received 'subscription.charged' for unknown Student AI sub ID: {subscription_id}")
        return

    # Handle Main Organization Subscription
    org = Organization.query.filter_by(razorpay_subscription_id=subscription_id).first()
    if org:
        org.status = 'active'
        org.subscription_ends_at = datetime.fromtimestamp(subscription_payload['current_end'])
        # Also activate the user and membership if they are pending
        if org.memberships:
            main_admin_membership = next((m for m in org.memberships if m.user.user_type == 'main_co_admin'), None)
            if main_admin_membership and not main_admin_membership.is_active:
                main_admin_membership.is_active = True
                if main_admin_membership.user:
                    main_admin_membership.user.status = 'active'
                current_app.logger.info(f"Activated main co-admin and membership for Org {org.id} via webhook.")
        current_app.logger.info(f"Organization {org.id} subscription renewed. New end date: {org.subscription_ends_at}")
        return

    current_app.logger.warning(f"Received 'subscription.charged' webhook for unknown subscription ID: {subscription_id}")

def handle_subscription_halted(payload):
    subscription_payload = payload.get('subscription', {}).get('entity', {})
    subscription_id = subscription_payload.get('id')
    notes = subscription_payload.get('notes', {})
    sub_type = notes.get('type')

    if not subscription_id:
        current_app.logger.error("'subscription.halted' webhook missing subscription ID.")
        return

    # Handle Org AI Assistant Subscription
    if sub_type == 'org_ai_assistant':
        org_sub = OrganizationAISubscription.query.filter_by(razorpay_subscription_id=subscription_id).first()
        if org_sub:
            org_sub.status = 'halted'
            if org_sub.organization:
                org_sub.organization.is_ai_premium = False
            current_app.logger.info(f"Organization {org_sub.organization_id} AI Assistant subscription halted.")
        return

    # Handle Student AI Tutor Subscription
    if sub_type == 'ai_tutor_student':
        student_sub = StudentAISubscription.query.filter_by(razorpay_subscription_id=subscription_id).first()
        if student_sub:
            student_sub.status = 'inactive'
            current_app.logger.info(f"Student {student_sub.student_user_id} AI subscription halted.")
        return

    # Handle Main Organization Subscription
    org = Organization.query.filter_by(razorpay_subscription_id=subscription_id).first()
    if org:
        org.status = 'halted'
        current_app.logger.info(f"Organization {org.id} subscription has been halted due to payment failure.")
        return

    current_app.logger.warning(f"Received 'subscription.halted' webhook for unknown subscription ID: {subscription_id}")

@payment_bp.route('/razorpay/webhook', methods=['POST'])
def razorpay_webhook():
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    if not webhook_secret:
        current_app.logger.error("RAZORPAY_WEBHOOK_SECRET not set.")
        return jsonify({"error": "Webhook secret not configured"}), 500

    signature = request.headers.get('X-Razorpay-Signature', '')
    payload = request.get_data()
    try:
        client = _get_rzp()
        client.utility.verify_webhook_signature(payload, signature, webhook_secret)
    except razorpay.errors.SignatureVerificationError as e:
        current_app.logger.warning(f"Invalid Razorpay webhook signature: {e}")
        return jsonify({"error": "Invalid signature"}), 400

    event = request.get_json()
    event_type = event.get('event')
    payload_data = event.get('payload', {})

    current_app.logger.info(f"Received Razorpay webhook: {event_type}")

    try:
        if event_type == 'subscription.charged':
            handle_subscription_charged(payload_data)
        elif event_type == 'subscription.halted':
            handle_subscription_halted(payload_data)
        else:
            current_app.logger.info(f"Unhandled webhook event type: {event_type}")

        db.session.commit()
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing webhook {event_type}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal server error"}), 200


# ---------- AI Assistant Subscription (for Orgs) ----------
@payment_bp.route('/organization/create-ai-subscription', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def create_org_ai_subscription(current_user, organization, **kwargs):
    """
    Creates a Razorpay subscription for an organization to purchase the AI Assistant.
    """
    existing_sub = OrganizationAISubscription.query.filter(
        OrganizationAISubscription.organization_id == organization.id,
        OrganizationAISubscription.status.in_(['active', 'pending'])
    ).first()
    if existing_sub:
        return jsonify({"message": f"This organization already has an {existing_sub.status} AI Assistant subscription."}), 400

    try:
        client = get_razorpay_client()
        plan_id = current_app.config.get('AI_ASSISTANT_PLAN_ID')
        current_app.logger.info(f"Attempting to create subscription with plan_id: {plan_id}")

        subscription = client.subscription.create({
            'plan_id': plan_id,
            'total_count': 12,
            'quantity': 1,
            'notes': {
                'type': 'org_ai_assistant',
                'organization_id': organization.id,
                'created_by_user_id': current_user.id
            }
        })

        sub = OrganizationAISubscription.query.filter_by(organization_id=organization.id).first()
        if not sub:
            sub = OrganizationAISubscription(organization_id=organization.id)
            db.session.add(sub)

        sub.razorpay_subscription_id = subscription['id']
        sub.status = 'pending'
        db.session.commit()

        return jsonify({
            "message": "Organization AI Assistant subscription created. Proceed to payment.",
            "subscription_id": subscription['id'],
            "razorpay_key_id": os.getenv('RAZORPAY_KEY_ID')
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating org AI subscription: {e}", exc_info=True)
        return jsonify({"message": "Could not initiate AI subscription payment."}), 500


# ---------- AI Tutor Subscription (for Students) ----------
@payment_bp.route('/create-ai-subscription-order', methods=['POST'])
@jwt_required()
def create_ai_subscription_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        client = get_razorpay_client()
        plan_id = current_app.config.get('AI_TUTOR_PLAN_ID')
        current_app.logger.info(f"Attempting to create subscription with plan_id: {plan_id}")

        subscription = client.subscription.create({
            'plan_id': plan_id,
            'total_count': 12,
            'quantity': 1,
            'notes': {
                'type': 'ai_tutor_student',
                'user_id': user_id
            }
        })

        sub = StudentAISubscription.query.filter_by(student_user_id=user.id).first()
        if not sub:
            sub = StudentAISubscription(student_user_id=user.id)
            db.session.add(sub)
        
        sub.razorpay_subscription_id = subscription['id']
        sub.status = 'pending'
        db.session.commit()

        return jsonify({
            "message": "AI Tutor subscription created. Proceed to payment.",
            "subscription_id": subscription['id'],
            "razorpay_key_id": os.getenv('RAZORPAY_KEY_ID')
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating AI subscription: {e}", exc_info=True)
        return jsonify({"message": "Could not initiate subscription payment."}), 500


# ---------- Exam purchase endpoints (unchanged) ----------

@payment_bp.route('/create-exam-order', methods=['POST'])
@jwt_required()
def create_exam_payment_order():
    # ... (this function remains unchanged)
    pass

@payment_bp.route('/verify-exam-payment', methods=['POST'])
@jwt_required()
def verify_exam_payment():
    # ... (this function remains unchanged)
    pass