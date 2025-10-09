# app/api/ai_progress.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta, date
from sqlalchemy import and_
from app.models.organization import OrganizationMembership
from flask import g
from collections import defaultdict

from app.extensions import db
from app.api.decorators import premium_feature_required, student_required
from app.models.student_progress import StudentWeeklyProgress, StudentExam
from app.models.mock_test import MockTest
from app.models.question import Question
from app.models.student_progress import StudentTestAttempt, StudentQuestionResponse
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.exam import Exam

ai_progress_bp = Blueprint('ai_progress', __name__, url_prefix='/api/ai')

def get_perf_rows_for_exam(user_id, exam_id):
    return db.session.query(
        Subject.name.label('subject_name'),
        Topic.name.label('topic_name'),
        Question.difficulty_level,
        StudentQuestionResponse.is_correct,
        StudentQuestionResponse.time_taken,
        StudentTestAttempt.completed_at,
        StudentTestAttempt.score,
        Question.id.label('question_id'),
        MockTest.title.label('test_name')
    ).select_from(StudentQuestionResponse)\
     .join(StudentTestAttempt, StudentTestAttempt.id == StudentQuestionResponse.attempt_id)\
     .join(MockTest, MockTest.id == StudentTestAttempt.mock_test_id)\
     .join(Question, Question.id == StudentQuestionResponse.question_id)\
     .join(Topic, Topic.id == Question.topic_id)\
     .join(Subject, Subject.id == Topic.subject_id)\
     .filter(
        StudentTestAttempt.student_user_id == user_id,
        MockTest.exam_id == exam_id,
        StudentTestAttempt.status == 'completed'
     ).all()

def current_week_bounds():
    today = datetime.utcnow().date()
    start = today - timedelta(days=today.weekday())   # Monday
    end   = start + timedelta(days=6)                 # Sunday
    return start, end

@ai_progress_bp.route('/weekly-progress/<int:exam_id>/snapshot', methods=['POST'])
@student_required()
@premium_feature_required()
def snapshot_week(current_user, exam_id, **kwargs):
    # 1) gather data for this exam
    rows = get_perf_rows_for_exam(current_user.id, exam_id)
    week_start, week_end = current_week_bounds()
    metrics = build_weekly_metrics(rows, week_start, week_end)

    # 2) upsert into StudentWeeklyProgress
    rec = StudentWeeklyProgress.query.filter_by(
        student_user_id=current_user.id, exam_id=exam_id, week_start=week_start
    ).first()
    if not rec:
        rec = StudentWeeklyProgress(
            student_user_id=current_user.id,
            exam_id=exam_id,
            week_start=week_start,
            week_end=week_end,
            metrics=metrics
        )
        db.session.add(rec)
    else:
        rec.week_end = week_end
        rec.metrics = metrics
        rec.generated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True, "record": {
        "week_start": rec.week_start.isoformat(),
        "metrics": rec.metrics
    }}), 200

@ai_progress_bp.route('/weekly-progress/<int:exam_id>', methods=['GET'])
@student_required()
@premium_feature_required()
def get_weeks(current_user, exam_id, **kwargs):
    limit = min(int(request.args.get('limit', 8)), 26)  # up to half a year
    rows = (StudentWeeklyProgress.query
            .filter_by(student_user_id=current_user.id, exam_id=exam_id)
            .order_by(StudentWeeklyProgress.week_start.desc())
            .limit(limit).all())
    data = [{
        "week_start": r.week_start.isoformat(),
        "week_end": r.week_end.isoformat(),
        "metrics": r.metrics,
        "generated_at": r.generated_at.isoformat()
    } for r in rows]
    return jsonify({"success": True, "weeks": list(reversed(data))}), 200

@ai_progress_bp.route('/weekly-insights/<int:exam_id>', methods=['POST'])
@student_required()
@premium_feature_required()
def weekly_insights(current_user, exam_id, **kwargs):
    # fetch last N weeks (default 8)
    limit = min(int(request.args.get('limit', 8)), 26)
    rows = (StudentWeeklyProgress.query
            .filter_by(student_user_id=current_user.id, exam_id=exam_id)
            .order_by(StudentWeeklyProgress.week_start.desc())
            .limit(limit).all())
    if not rows:
        return jsonify({"success": False, "message": "No weekly progress yet."}), 404

    # compact payload for the model
    weeks = [{
        "week": r.week_start.isoformat(),
        "accuracy": r.metrics.get('accuracy', 0),
        "attempts": r.metrics.get('attempts', 0),
        "avg_time_sec": r.metrics.get('avg_time_sec', 0),
        "topics": r.metrics.get('topics', []),
        "difficulty": r.metrics.get('difficulty_distribution', {})
    } for r in reversed(rows)]

    # prompt the model for insights
    prompt = f"""
You are an exam coach. Given weekly practice metrics below for a student, produce:
- a 4–6 bullet "What changed this week" summary,
- top 2 weak topics to focus next week,
- a realistic target for next week (accuracy & attempts),
- 3 concrete actions.

Respond as pure JSON with keys: summary_bullets, weak_topics, next_week_target, actions.

Weeks JSON:
{weeks}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3,
        max_tokens=400
    )
    text = resp.choices[0].message.content

    # do a safe parse attempt; if not JSON, just return text
    import json
    try:
        parsed = json.loads(text)
        return jsonify({"success": True, "insights": parsed, "weeks": weeks}), 200
    except Exception:
        return jsonify({"success": True, "insights_text": text, "weeks": weeks}), 200

def build_weekly_metrics(rows, week_start, week_end):
    # Keep only rows inside the target week
    week_rows = [r for r in rows if week_start <= r.completed_at.date() <= week_end]

    total = len(week_rows)
    correct = sum(1 for r in week_rows if r.is_correct)
    accuracy = round((correct / total) * 100, 2) if total else 0.0

    # avg time
    times = [r.time_taken for r in week_rows if r.time_taken]
    avg_time_sec = round(sum(times) / len(times), 2) if times else 0.0

    # difficulty distribution
    diff = defaultdict(int)
    for r in week_rows:
        diff[r.difficulty_level or 'medium'] += 1

    # topic stats (lowest accuracy first; cap list to keep payload small)
    topic_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    for r in week_rows:
        t = r.topic_name or 'General'
        topic_stats[t]['total'] += 1
        if r.is_correct:
            topic_stats[t]['correct'] += 1

    topics = []
    for t, v in topic_stats.items():
        acc = round((v['correct'] / v['total']) * 100, 1) if v['total'] else 0.0
        topics.append({'topic': t, 'accuracy': acc, 'attempts': v['total']})
    topics.sort(key=lambda x: x['accuracy'])  # weakest first
    topics = topics[:8]

    return {
        'attempts': total,
        'accuracy': accuracy,
        'avg_time_sec': avg_time_sec,
        'difficulty_distribution': dict(diff),
        'topics': topics
    }

def _enforce_org_and_exam(current_user, exam_id):
    # Must be on an org subdomain
    if not getattr(g, 'current_organization', None):
        return False, (jsonify({"success": False, "message": "Open from your organization's portal."}), 403)

    org = g.current_organization

    # Must be an active member of this org
    membership = OrganizationMembership.query.filter_by(
        user_id=current_user.id, organization_id=org.id, is_active=True
    ).first()
    if not membership:
        return False, (jsonify({"success": False, "message": "You don't have access to this organization."}), 403)

    # Exam must belong to this org
    exam = Exam.query.get_or_404(exam_id)
    if exam.organization_id != org.id:
        return False, (jsonify({"success": False, "message": "Exam does not belong to this organization."}), 403)

    # Student must have exam access
    access = StudentExam.query.filter(
        StudentExam.student_user_id == current_user.id,
        StudentExam.exam_id == exam_id,
        StudentExam.access_status.in_(['purchased','free_access','admin_granted'])
    ).first()
    if not access:
        return False, (jsonify({"success": False, "message": "You don't have access to this exam."}), 403)

    return True, None


def ensure_weekly_snapshot(user_id, exam_id, performance_rows=None):
    """Compute & upsert the current week’s metrics for (user, exam)."""
    exam = Exam.query.get(exam_id)
    if not exam:
        return None

    membership = OrganizationMembership.query.filter_by(
        user_id=user_id,
        organization_id=exam.organization_id
    ).first()

    if not membership:
        return None

    if performance_rows is None:
        performance_rows = get_perf_rows_for_exam(user_id, exam_id)

    week_start, week_end = current_week_bounds()
    metrics = build_weekly_metrics(performance_rows, week_start, week_end)

    rec = StudentWeeklyProgress.query.filter_by(
        student_user_id=user_id, exam_id=exam_id, week_start=week_start
    ).first()
    if not rec:
        rec = StudentWeeklyProgress(
            student_user_id=user_id,
            exam_id=exam_id,
            membership_id=membership.id,
            week_start=week_start,
            week_end=week_end,
            metrics=metrics
        )
        db.session.add(rec)
    else:
        rec.membership_id = membership.id
        rec.week_end = week_end
        rec.metrics = metrics
        rec.generated_at = datetime.utcnow()
    db.session.commit()
    return rec


def recent_week_summaries(user_id, exam_id, limit=8):
    """Return a compact list of the last N week snapshots (ascending by week)."""
    limit = min(int(limit or 8), 26)
    rows = (StudentWeeklyProgress.query
            .filter_by(student_user_id=user_id, exam_id=exam_id)
            .order_by(StudentWeeklyProgress.week_start.desc())
            .limit(limit).all())

    data = [{
        "week_start": r.week_start.isoformat(),
        "week_end": r.week_end.isoformat(),
        "metrics": r.metrics,
        "generated_at": r.generated_at.isoformat()
    } for r in rows]
    return list(reversed(data))
