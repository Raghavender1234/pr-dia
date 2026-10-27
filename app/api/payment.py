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
from app.utils.localization import get_country_code

payment_bp = Blueprint('payment_api', __name__, url_prefix='/api/payment')

razorpay_client = None
# ---------- helpers ----------
def get_razorpay_client():
    """Create/reuse a singleton Razorpay client using app config/env."""
    from razorpay import Client as RazorpayClient
    global razorpay_client

    key_id = current_app.config.get('RAZORPAY_KEY_ID') or os.getenv('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET') or os.getenv('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        return None

    if razorpay_client is None:
        razorpay_client = RazorpayClient(auth=(key_id, key_secret))
    return razorpay_client

def _get_rzp():
    key_id = current_app.config.get('RAZORPAY_KEY_ID') or os.getenv("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET') or os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        return None
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
        if not client:
            return jsonify({
                "message": "Payment gateway is not configured for this self-hosted instance. In community mode, all AI features are complimentary.",
                "community_mode": True
            }), 200
        plan_id = current_app.config.get('AI_ASSISTANT_PLAN_ID')

        if not plan_id:
            current_app.logger.error("AI Assistant subscription plan is not configured. Please define AI_ASSISTANT_PLAN_ID in your config.")
            return jsonify({"message": "AI Assistant subscription service is not configured. Please contact support."}), 500
        
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
        if not client:
            return jsonify({
                "message": "Payment gateway is not configured for this self-hosted instance. In community mode, all AI features are complimentary.",
                "community_mode": True
            }), 200
        
        data = request.get_json() or {}

        # ALWAYS use the INR Plan ID from your config
        plan_id = current_app.config.get('AI_TUTOR_PLAN_ID')

        if not plan_id:
            current_app.logger.error("AI Tutor Plan ID missing in config.")
            return jsonify({"message": "Subscription service misconfigured."}), 500

        # FORCE Razorpay to treat this as an INR transaction 
        # even if the user is in the UK/USA. Their bank handles the swap.
        subscription_data = {
            'plan_id': plan_id,
            'total_count': 12,
            'quantity': 1,
            'customer_notify': 1,
            'notes': {
                'type': 'ai_tutor_student',
                'user_id': user_id,
                'original_currency_preference': data.get('currency', 'INR') # Log preference but don't charge in it
            }
        }

        subscription = client.subscription.create(subscription_data)

        # Update or create the local subscription record
        sub = StudentAISubscription.query.filter_by(student_user_id=user.id).first()
        if not sub:
            sub = StudentAISubscription(student_user_id=user.id)
            db.session.add(sub)
        
        sub.razorpay_subscription_id = subscription['id']
        sub.status = 'pending'
        db.session.commit()

        return jsonify({
            "subscription_id": subscription['id'],
            "razorpay_key_id": current_app.config.get('RAZORPAY_KEY_ID'),
            "amount_inr": subscription.get('amount'), # Useful for frontend display
            "currency": "INR" # Tell frontend to invoke Razorpay Checkout in INR
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Razorpay Sub Error: {str(e)}")
        return jsonify({"message": "Could not initiate payment."}), 500

# ---------- Exam purchase endpoints (unchanged) ----------

@payment_bp.route('/create-exam-order', methods=['POST'])
@jwt_required()
def create_exam_payment_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    exam_id = data.get('exam_id')

    exam = Exam.query.get_or_404(exam_id)
    
    # Check if student already bought it
    existing = StudentExam.query.filter_by(student_user_id=user_id, exam_id=exam_id).first()
    if existing and existing.payment_status == 'completed':
        return jsonify({"message": "You already have access to this exam."}), 400

    try:
        client = get_razorpay_client()
        if not client:
            return jsonify({
                "message": "Payment gateway is not configured for this self-hosted instance. In community mode, all AI features are complimentary.",
                "community_mode": True
            }), 200
        
        # LOGIC: Even if frontend shows USD, we charge in INR.
        # Razorpay amounts are in PAISA (1 INR = 100 Paisa)
        amount_in_paisa = int(exam.price * 100) 

        order_data = {
            'amount': amount_in_paisa,
            'currency': 'INR', # Force INR to match your Razorpay account type
            'receipt': f"receipt_exam_{exam_id}_{user_id}",
            'notes': {
                'exam_id': exam_id,
                'user_id': user_id,
                'type': 'exam_purchase'
            }
        }

        razorpay_order = client.order.create(data=order_data)

        # We don't save to DB yet; we wait for verification
        return jsonify({
            "order_id": razorpay_order['id'],
            "amount": amount_in_paisa,
            "currency": "INR",
            "razorpay_key_id": current_app.config.get('RAZORPAY_KEY_ID')
        }), 200

    except Exception as e:
        current_app.logger.error(f"Exam Order Error: {str(e)}")
        return jsonify({"message": "Failed to initiate exam payment."}), 500
@payment_bp.route('/verify-exam-payment', methods=['POST'])
@jwt_required()
def verify_exam_payment():
    user_id = get_jwt_identity()
    data = request.get_json()

    # These are sent by the Razorpay Checkout Modal after success
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    exam_id = data.get('exam_id')

    try:
        client = get_razorpay_client()
        if not client:
            return jsonify({
                "message": "Payment gateway is not configured for this self-hosted instance. In community mode, all AI features are complimentary.",
                "community_mode": True
            }), 200
        
        # 1. VERIFY SIGNATURE (Security Check)
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_payment_signature(params_dict)

        # 2. UPDATE DATABASE
        # Check if record exists, else create
        student_exam = StudentExam.query.filter_by(student_user_id=user_id, exam_id=exam_id).first()
        if not student_exam:
            # We must resolve the membership_id
            exam = Exam.query.get_or_404(exam_id)
            membership = OrganizationMembership.query.filter_by(
                user_id=user_id,
                organization_id=exam.organization_id,
                is_active=True
            ).first()
            if not membership:
                membership = OrganizationMembership(
                    user_id=user_id,
                    organization_id=exam.organization_id,
                    is_active=True,
                    access_type='public'
                )
                db.session.add(membership)
                db.session.flush()

            student_exam = StudentExam(
                student_user_id=user_id,
                exam_id=exam_id,
                membership_id=membership.id
            )
            db.session.add(student_exam)

        student_exam.access_status = 'purchased'
        student_exam.razorpay_payment_id = razorpay_payment_id
        student_exam.purchased_at = datetime.utcnow()
        
        db.session.commit()

        return jsonify({"status": "success", "message": "Payment verified. Exam unlocked."}), 200

    except razorpay.errors.SignatureVerificationError:
        current_app.logger.warning(f"Payment verification failed for User {user_id}")
        return jsonify({"status": "failure", "message": "Invalid payment signature."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Verification Error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal verification error."}), 500

@payment_bp.route('/verify-ai-subscription', methods=['POST'])
@jwt_required()
def verify_ai_subscription():
    user_id = get_jwt_identity()
    data = request.get_json()

    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_subscription_id = data.get('razorpay_subscription_id')
    razorpay_signature = data.get('razorpay_signature')

    try:
        client = get_razorpay_client()
        if not client:
            return jsonify({
                "message": "Payment gateway is not configured for this self-hosted instance. In community mode, all AI features are complimentary.",
                "community_mode": True
            }), 200
        
        # 1. VERIFY SIGNATURE specifically for subscriptions
        params_dict = {
            'razorpay_subscription_id': razorpay_subscription_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_subscription_payment_signature(params_dict)

        # 2. UPDATE DATABASE
        # Check Student AI Subscription
        student_sub = StudentAISubscription.query.filter_by(
            razorpay_subscription_id=razorpay_subscription_id, 
            student_user_id=user_id
        ).first()
        
        if student_sub:
            student_sub.status = 'active'
            db.session.commit()
            return jsonify({"status": "success", "message": "Student AI Subscription verified and activated."}), 200

        # Check Organization AI Subscription
        org_sub = OrganizationAISubscription.query.filter_by(razorpay_subscription_id=razorpay_subscription_id).first()
        if org_sub:
            org_sub.status = 'active'
            if org_sub.organization:
                org_sub.organization.is_ai_premium = True
            db.session.commit()
            return jsonify({"status": "success", "message": "Organization AI Assistant verified and activated."}), 200

        return jsonify({"status": "error", "message": "Subscription record not found."}), 404

    except razorpay.errors.SignatureVerificationError:
        current_app.logger.warning(f"Subscription verification failed for User {user_id}")
        return jsonify({"status": "failure", "message": "Invalid payment signature."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Subscription Verification Error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal verification error."}), 500


@payment_bp.route('/verify-org-subscription', methods=['POST'])
def verify_org_subscription():
    """Verifies the main organization subscription (Basic, Pro, Premium). No JWT required as user just registered."""
    data = request.get_json()

    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_subscription_id = data.get('razorpay_subscription_id')
    razorpay_signature = data.get('razorpay_signature')

    try:
        client = get_razorpay_client()
        if not client:
            return jsonify({
                "message": "Payment gateway is not configured for this self-hosted instance. In community mode, all AI features are complimentary.",
                "community_mode": True
            }), 200
        params_dict = {
            'razorpay_subscription_id': razorpay_subscription_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_subscription_payment_signature(params_dict)

        org = Organization.query.filter_by(razorpay_subscription_id=razorpay_subscription_id).first()
        if org:
            org.status = 'active'
            if org.memberships:
                main_admin_membership = next((m for m in org.memberships if m.user.user_type == 'main_co_admin'), None)
                if main_admin_membership:
                    main_admin_membership.is_active = True
                    if main_admin_membership.user:
                        main_admin_membership.user.status = 'active'
            db.session.commit()
            return jsonify({"status": "success", "message": "Organization subscription verified and activated."}), 200

        return jsonify({"status": "error", "message": "Organization not found."}), 404

    except razorpay.errors.SignatureVerificationError:
        current_app.logger.warning(f"Org Subscription verification failed.")
        return jsonify({"status": "failure", "message": "Invalid payment signature."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Org Subscription Verification Error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal verification error."}), 500