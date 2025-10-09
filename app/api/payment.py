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
from app.models.organization import Organization, OrganizationMembership
from app.models.exam import Exam
from app.models.student_progress import StudentExam, StudentAISubscription
from app.api.decorators import admin_role_required

payment_bp = Blueprint('payment_api', __name__, url_prefix='/api/payment')


# ---------- helpers ----------
AI_PREMIUM_PRICE_PAISE = 49900  # ₹499.00
ORG_AI_PREMIUM_PRICE_PAISE = 99900 # This is now ₹999.00
razorpay_client = None  # placeholder

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
        # Optional (correct signature): 
        # razorpay_client.set_app_details({"title": "DIA", "version": "1.0"})
    return razorpay_client

def _get_rzp():
    key_id = current_app.config.get('RAZORPAY_KEY_ID') or os.getenv("RAZORPAY_KEY_ID")
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET') or os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise RuntimeError("Razorpay keys are not configured.")
    client = razorpay.Client(auth=(key_id, key_secret))
    # Optional: only for analytics/insights — pass a single dict
    try:
        client.set_app_details({"title": "ExamPrepApp", "version": "1.0"})
    except Exception:
        # Older/newer SDKs may not support this; safe to ignore
        pass
    return client


def _current_user():
    ident = get_jwt_identity()
    user_id = ident.get('id') if isinstance(ident, dict) else ident
    return User.query.get(user_id)


def payment_initiator_required():
    """
    Students (and admins for testing) can create/verify orders.
    Injects 'current_user' into the view.
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user = _current_user()
            if not user:
                return jsonify({"message": "Authentication required"}), 401
            if user.user_type not in ('student', 'co_admin', 'main_co_admin', 'super_admin'):
                return jsonify({"message": "Unauthorized: Only students/admins can initiate payments"}), 403
            kwargs['current_user'] = user
            return fn(*args, **kwargs)
        return decorator
    return wrapper


# ---------- Org subscription webhook (leave disabled if you don't need it yet) ----------

@payment_bp.route('/razorpay/webhook', methods=['POST'])
def razorpay_webhook():
    """
    Keep only if you actually use Razorpay webhooks for org billing.
    Make sure RAZORPAY_WEBHOOK_SECRET is set in env.
    """
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
    if not webhook_secret:
        return jsonify({"error": "Webhook secret not configured"}), 400

    signature = request.headers.get('X-Razorpay-Signature', '')
    payload = request.get_data() or b''

    generated = hmac.new(webhook_secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, generated):
        return jsonify({"error": "Invalid signature"}), 400

    # Handle events as needed…
    return jsonify({"status": "ok"}), 200


# ---------- Org subscription (unchanged behavior) ----------

@payment_bp.route('/organization/create-ai-order', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def create_org_ai_subscription_order(current_user, organization, **kwargs):
    """
    Creates a Razorpay order for an organization to purchase the AI Assistant.
    - Only accessible to org admins (main_co_admin, co_admin).
    - Prevents creating an order if the organization already has the AI premium flag set.
    """
    try:
        # Prevent duplicate purchases / accidental re-ordering
        if getattr(organization, 'is_ai_premium', False):
            return jsonify({"message": "Organization already has AI premium enabled."}), 400

        # Price in paise: prefer explicit numeric config, then env var, then fallback value (₹999.00)
        price_cfg = current_app.config.get('ORG_AI_PREMIUM_PRICE_PAISE') or os.getenv('ORG_AI_PREMIUM_PRICE_PAISE')
        try:
            order_amount = int(price_cfg) if price_cfg is not None else 99900  # default ₹999.00
        except (ValueError, TypeError):
            order_amount = 99900

        # Build order payload
        order_payload = {
            'amount': order_amount,
            'currency': 'INR',
            'receipt': f"org_ai_{organization.id}_{datetime.utcnow().timestamp()}",
            'notes': {
                'organization_id': organization.id,
                'created_by_user_id': current_user.id
            }
        }

        # Create Razorpay order
        rzp = _get_rzp()
        order = rzp.order.create(order_payload)

        # Persist order id on organization model.
        organization.razorpay_order_id = order.get('id')

        db.session.commit()

        return jsonify({
            "message": "Organization AI subscription order created.",
            "order_id": order.get('id'),
            "amount": order.get('amount') or order_amount,
            "razorpay_key_id": current_app.config.get('RAZORPAY_KEY_ID') or os.getenv("RAZORPAY_KEY_ID"),
            "org_name": organization.name,
            "price_paise": order_amount
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating org AI subscription order: {e}", exc_info=True)
        return jsonify({"message": "Could not initiate AI subscription payment."}), 500

# ---------- AI personal subscription (NEW verify; improved create) ----------

@payment_bp.route('/create-ai-subscription-order', methods=['POST'])
@jwt_required()
def create_ai_subscription_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    AI_SUBSCRIPTION_PRICE_PAISE = 49900

    order_payload = {
        'amount': AI_SUBSCRIPTION_PRICE_PAISE,
        'currency': 'INR',
        'receipt': f"ai_sub_rcpt_{user.id}_{datetime.utcnow().timestamp()}",
        'payment_capture': '1'
    }

    try:
        client = get_razorpay_client()
        order = client.order.create(order_payload)
        return jsonify({
            "message": "AI Subscription order created.",
            "order_id": order['id'],
            "amount": order['amount'],
            "razorpay_key_id": (current_app.config.get("RAZORPAY_KEY_ID") or os.getenv("RAZORPAY_KEY_ID"))
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error creating AI subscription order: {e}", exc_info=True)
        return jsonify({"message": "Could not initiate subscription payment."}), 500


@payment_bp.route('/verify-ai-subscription', methods=['POST'])
@jwt_required()
def verify_ai_subscription():
    # ✅ 1) robust identity extraction
    ident = get_jwt_identity()
    user_id = ident.get('id') if isinstance(ident, dict) else ident
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json() or {}
    for k in ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'):
        if not data.get(k):
            return jsonify({"message": "Missing payment verification details."}), 400

    try:
        client = get_razorpay_client()
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"message": "Payment verification failed: Invalid signature"}), 400
    except Exception as e:
        current_app.logger.error(f"[AI SUB VERIFY] Unexpected error: {e}", exc_info=True)
        return jsonify({"message": "Could not verify payment due to a server error."}), 500

    try:
        now = datetime.utcnow()
        end = now + timedelta(days=30)

        sub = StudentAISubscription.query.filter_by(student_user_id=user.id).first()
        if not sub:
            sub = StudentAISubscription(
                student_user_id=user.id,
                status='active',
                start_date=now,
                end_date=end
            )
            db.session.add(sub)
        else:
            sub.status = 'active'
            sub.start_date = sub.start_date or now
            sub.end_date = end

        # optional: if your User has this column
        if hasattr(user, 'is_premium'):
            user.is_premium = True

        db.session.commit()

        # ✅ 2) mark session so next render shows premium immediately
        from flask import session
        session['is_premium'] = True

        return jsonify({"message": "Subscription activated successfully.", "is_premium": True}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[AI SUB VERIFY] DB error: {e}", exc_info=True)
        return jsonify({"message": "Payment verified but could not activate subscription."}), 500

# ---------- Exam purchase endpoints (kept; small refactor to helpers) ----------

@payment_bp.route('/create-exam-order', methods=['POST'])
@jwt_required()
@payment_initiator_required()
def create_exam_payment_order(current_user):
    """
    Creates a Razorpay order for a student enrolling in an exam.
    Honors internal/public membership, platform fee, and transfers.
    """
    exam_id = (request.get_json() or {}).get('exam_id')
    if not exam_id:
        return jsonify({"message": "Exam ID is required."}), 400

    exam = Exam.query.get_or_404(exam_id)
    organization = exam.organization

    membership = OrganizationMembership.query.filter_by(
        user_id=current_user.id,
        organization_id=organization.id
    ).first()

    if not membership:
        return jsonify({"message": "You are not a member of this organization."}), 403

    rzp = _get_rzp()

    # Invited/internal: grant for free
    if membership.access_type == 'internal':
        enrollment = StudentExam.query.filter_by(
            student_user_id=current_user.id,
            exam_id=exam.id
        ).first()
        if not enrollment:
            enrollment = StudentExam(student_user_id=current_user.id, exam_id=exam.id)
            db.session.add(enrollment)

        enrollment.access_status = 'free_access'
        enrollment.purchased_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": f"Free access granted to {exam.name}.", "access_granted": True}), 200

    # Public + free exam → platform fee
    if membership.access_type == 'public' and getattr(exam, 'is_free', False):
        platform_fee_paise = 1000  # ₹10
        order = rzp.order.create({
            "amount": platform_fee_paise,
            "currency": "INR",
            "notes": {"exam_id": exam.id, "user_id": current_user.id, "type": "platform_fee"}
        })
        return jsonify({
            "razorpay_key_id": current_app.config.get('RAZORPAY_KEY_ID') or os.getenv("RAZORPAY_KEY_ID"),
            "order_id": order['id'],
            "amount": order['amount']
        }), 200

    # Public + paid exam → transfer org share
    if membership.access_type == 'public' and not getattr(exam, 'is_free', False):
        org_acct = organization.razorpay_linked_account_id
        if not org_acct:
            return jsonify({"message": "This organization is not set up to receive payments."}), 400

        total_amount_paise = int(exam.price * 100)
        commission_paise = int(total_amount_paise * 0.10)
        org_share_paise = total_amount_paise - commission_paise

        order = rzp.order.create({
            "amount": total_amount_paise,
            "currency": "INR",
            "notes": {"exam_id": exam.id, "user_id": current_user.id, "type": "exam_purchase"},
            "transfers": [{
                "account": org_acct,
                "amount": org_share_paise,
                "currency": "INR",
            }]
        })
        return jsonify({
            "razorpay_key_id": current_app.config.get('RAZORPAY_KEY_ID') or os.getenv("RAZORPAY_KEY_ID"),
            "order_id": order['id'],
            "amount": order['amount']
        }), 200

    return jsonify({"message": "Unexpected membership state."}), 500


@payment_bp.route('/verify-exam-payment', methods=['POST'])
@jwt_required()
@payment_initiator_required()
def verify_exam_payment(current_user):
    """Verifies the Razorpay payment for an exam and grants access."""
    data = request.get_json() or {}

    try:
        rzp = _get_rzp()
        rzp.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
    except Exception as e:
        current_app.logger.error(f"Payment signature verification failed: {e}")
        return jsonify({"message": "Payment verification failed."}), 400

    enrollment = StudentExam.query.filter_by(
        student_user_id=current_user.id,
        razorpay_order_id=data.get('razorpay_order_id'),
        access_status='pending_payment'
    ).first()

    if not enrollment:
        return jsonify({"message": "Pending enrollment for this order not found."}), 404

    try:
        enrollment.access_status = 'purchased'
        enrollment.purchased_at = datetime.utcnow()
        enrollment.razorpay_payment_id = data.get('razorpay_payment_id')

        membership = OrganizationMembership.query.filter_by(
            user_id=current_user.id,
            organization_id=enrollment.exam.organization_id
        ).first()
        if membership:
            membership.is_active = True

        db.session.commit()
        return jsonify({"message": f"Payment successful! You are now enrolled in {enrollment.exam.name}."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error finalizing enrollment after payment: {e}")
        return jsonify({"message": "Payment was successful, but granting access failed. Please contact support."}), 500

@payment_bp.route('/organization/verify-ai-payment', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin'])
def verify_org_ai_payment(current_user, organization, **kwargs):
    """Verifies the payment and activates the AI premium feature for the organization."""
    data = request.get_json()
    
    try:
        client = get_razorpay_client()
        client.utility.verify_payment_signature({
           'razorpay_order_id': data['razorpay_order_id'],
           'razorpay_payment_id': data['razorpay_payment_id'],
           'razorpay_signature': data['razorpay_signature']
        })
    except Exception:
        return jsonify({"message": "Payment verification failed."}), 400

    org_to_activate = Organization.query.filter_by(razorpay_order_id=data['razorpay_order_id']).first_or_404()
    if org_to_activate.id != organization.id:
        return jsonify({"message": "Authorization error."}), 403

    try:
        org_to_activate.is_ai_premium = True
        
        from flask import session
        session['is_premium'] = True

        db.session.commit()
        return jsonify({"message": "Payment successful! The AI Assistant is now active."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Payment successful, but there was an error activating the feature."}), 500
