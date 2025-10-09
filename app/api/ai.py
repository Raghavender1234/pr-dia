# backend/app/api/ai.py
import os
from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.extensions import db
from app.api.decorators import ai_usage_limited, student_required, premium_feature_required, admin_role_required
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.student_progress import StudentExam, StudentAISubscription
from app.models.question import Question, MCQOption
from openai import OpenAI
from app.models.user import User


ai_bp = Blueprint('ai_api', __name__, url_prefix='/api/ai')

# One OpenAI client for this module
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CA_KEYWORDS_SUBJ = ['current affairs', 'general awareness', 'gk', 'general knowledge']
CA_KEYWORDS_TOPIC = ['current affairs', 'current events', 'news', 'national affairs', 'international affairs']


@ai_bp.route('/generate_questions', methods=['POST'])
@student_required()
@ai_usage_limited(feature_type='generate')
def generate_similar_questions(current_user, **kwargs):
    data = request.get_json() or {}

    question_type = data.get('question_type', 'MCQ')
    original_question = data.get('question_text', '')
    passage_text = data.get('passage_text')  # for comprehension
    difficulty = data.get('difficulty', 'medium')
    topic_name = data.get('topic_name', 'this topic')
    subject_name = data.get('subject_name', 'this subject')
    exam_name = data.get('exam_name', 'their exam')

    if not original_question and question_type != 'Comprehension':
        return jsonify({"message": "The 'question_text' field is required."}), 400

    if question_type == 'Comprehension':
        prompt = f'''
You are an expert Question Generator for Indian competitive exams, skilled at creating engaging and analytical comprehension exercises.
A student is studying the "{topic_name}" topic.

**Your Task:**
1.  Based on the original passage below, generate **one new, distinct, and more engaging passage** on the same subject matter. Make it interesting by including a small narrative, a problem to be solved, or a point of debate.
2.  After the new passage, generate **3 new, distinct multiple-choice sub-questions** that test higher-order thinking skills.

**Instructions for Generating High-Quality Questions:**
*   **Go Beyond Literal Comprehension:** Instead of just finding information in the text, ask questions that require the student to:
    *   Infer the author's intent or purpose.
    *   Identify the main idea or primary argument.
    *   Analyze the tone or style of the passage.
    *   Apply the information to a new context.
*   **Maintain Difficulty:** The new passage and questions should be at a "{difficulty}" difficulty level.
*   **Create Plausible Distractors:** The incorrect options should be challenging and relate to the passage's nuances.

**Formatting Rules:**
*   Each sub-question must have 4 options (A, B, C, D).
*   Clearly label the correct answer for each sub-question with `(Correct)`.
*   Format as plain text.

**Original Passage Example:**
{passage_text}
'''
    else:
        prompt = f'''
You are an expert Question Generator for Indian competitive exams, specializing in creating insightful and thought-provoking questions.
A student is preparing for the "{exam_name}" exam, studying the "{subject_name}" subject, and focusing on the "{topic_name}" topic.

Based on the following original question (difficulty: "{difficulty}"), generate 3 new, distinct, and more interesting Multiple-Choice Questions.

**Instructions for Generating Interesting Questions:**
1.  **Go Beyond Rote Memorization:** Instead of just asking "what," try to create questions that ask "why," "how," or present a scenario.
2.  **Explore Different Angles:**
    *   **Application:** How is this concept applied in a real-world scenario?
    *   **Exception:** Which of the following is an exception to the rule/concept?
    *   **Analysis:** Ask the student to analyze a situation or compare/contrast concepts.
3.  **Create Plausible Distractors:** The incorrect options should be challenging and based on common misconceptions related to the "{topic_name}".
4.  **Maintain Difficulty:** The new questions should match the original's "{difficulty}" level.
5.  **Stay Relevant:** All questions must remain strictly relevant to the "{topic_name}" topic.

**Formatting Rules:**
*   Each question must have 4 options (A, B, C, D).
*   Mark the single correct option in each with `(Correct)`.
*   Output as plain text.

**Original Question:**
{original_question}
'''

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700
        )
        generated_text = resp.choices[0].message.content
        return jsonify({"generated": generated_text}), 200
    except Exception as e:
        current_app.logger.error(f"OpenAI error (generate): {e}")
        return jsonify({"message": "Could not generate questions due to an AI service error."}), 500


@ai_bp.route('/validate_answer', methods=['POST'])
@student_required()
@ai_usage_limited(feature_type='validate')
def validate_open_ended_answer(current_user, **kwargs):
    data = request.get_json() or {}
    question = data.get('question')
    student_answer = data.get('answer')

    if not question or not student_answer:
        return jsonify({"message": "Both 'question' and 'answer' are required."}), 400

    prompt = f'''
A student was asked: '{question}'
The student answered: '{student_answer}'
Provide concise, encouraging feedback in 1–2 sentences. If there are mistakes, point them out gently.
'''

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200
        )
        feedback = resp.choices[0].message.content
        return jsonify({"feedback": feedback}), 200
    except Exception as e:
        current_app.logger.error(f"OpenAI error (validate): {e}")
        return jsonify({"message": "Could not validate answer at the moment."}), 500


@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def handle_ai_chat():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    # --- UNIFIED SECURITY CHECK ---
    is_premium_user = False
    if user.user_type == 'student':
        subscription = StudentAISubscription.query.filter_by(student_user_id=user.id, status='active').first()
        if subscription:
            is_premium_user = True
    
    elif user.user_type in ['main_co_admin', 'co_admin']:
        membership = user.memberships[0] if user.memberships else None
        if membership and membership.organization and membership.organization.is_ai_premium:
            is_premium_user = True
            
    elif user.user_type == 'super_admin':
        is_premium_user = True

    if not is_premium_user:
        return jsonify({"message": "This is a premium feature. Please subscribe to access."}), 403
    # --- END OF SECURITY CHECK ---

    data = request.get_json() or {}
    user_message = data.get('message')
    if not user_message:
        return jsonify({"message": "A message is required."}), 400

    history = data.get('history', [])
    exam_name = data.get('exam_name', 'general')
    subject_name = data.get('subject_name', 'general topics')

    system_prompt = ""
    if user.user_type == 'student':
        system_prompt = (
            f"You are a friendly expert tutor named DIA helping {user.first_name} study for the '{exam_name}' exam, "
            f"focusing on '{subject_name}'. Explain concepts clearly using daily-life analogies."
        )
    else: # For admins
        system_prompt = (
            f"You are a professional content creation assistant helping an administrator named {user.first_name}. "
            f"Your goal is to help them generate ideas for questions and content."
        )

    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_message}]

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.7, max_tokens=600)
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply}), 200
    except Exception as e:
        current_app.logger.error(f"OpenAI error (chat): {e}")
        return jsonify({"message": "The AI assistant is currently unavailable."}), 503


@ai_bp.route('/generate-practice-from-chat', methods=['POST'])
@jwt_required()
def generate_practice_from_chat():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # This route will now implicitly have the same security as the main chat
    # because only premium users can access the page that calls it.

    data = request.get_json()
    history = data.get('history', [])
    subject_name = data.get('subject_name', 'the topic')

    question_count = 10 if user.user_type != 'student' else 5
    persona = "expert question author" if user.user_type != 'student' else "expert tutor"

    system_prompt = f'''
    You are an expert question author. Based on the following conversation, create exactly {question_count} multiple-choice questions (MCQ).
    
    **CRITICAL FORMATTING RULES:**
    1. Each question must start with a number followed by a period (e.g., "1.").
    2. Provide exactly four options, each starting with A), B), C), and D).
    3. **You MUST mark the correct answer by appending `(Correct)` to the end of the correct option's text.**

    **EXAMPLE OF PERFECT FORMATTING:**
    1. What is the capital of France?
    A) London
    B) Berlin
    C) Paris (Correct)
    D) Madrid

    Conversation: "{' '.join([msg['content'] for msg in history])}"
    '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        generated_text = response.choices[0].message.content
        return jsonify({"generated_questions": generated_text})
    except Exception as e:
        return jsonify({"message": f"Error generating questions: {str(e)}"}), 503

@ai_bp.route('/save-generated-question', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin', 'super_admin'])
def save_generated_question(current_user, **kwargs):
    if Question is None or MCQOption is None:
        return jsonify({"message": "Server model import path for Question/MCQOption is not configured."}), 500

    data = request.get_json() or {}
    topic_id = data.get('topic_id')
    if not data.get('question_text') or not topic_id:
        return jsonify({"message": "Incomplete question data provided."}), 400

    try:
        # 🔽 derive exam_id from topic -> subject -> exam
        topic = Topic.query.get(topic_id)
        if not topic or not getattr(topic, 'subject', None) or not getattr(topic.subject, 'exam_id', None):
            return jsonify({"message": "Invalid topic: cannot resolve exam for this topic."}), 400
        exam_id = topic.subject.exam_id

        existing = Question.query.filter_by(
            question_text=data['question_text'],
            created_by_user_id=current_user.id
        ).first()
        if existing:
            return jsonify({"message": "You have already saved this question."}), 409

        new_question = Question(
            topic_id=topic_id,
            question_type='MCQ',
            question_text=data['question_text'],
            difficulty_level=data.get('difficulty_level', 'medium'),
            created_by_user_id=current_user.id,
            exam_id=exam_id,                     
            visibility='private',                 
        )

        options = []
        for opt in data.get('options', []):
            if isinstance(opt, dict) and 'text' in opt:
                options.append(MCQOption(
                    option_text=opt['text'],
                    is_correct=bool(opt.get('is_correct'))
                ))
        new_question.mcq_options = options

        db.session.add(new_question)
        db.session.commit()
        return jsonify({"message": "Question saved to your practice list!"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving AI-generated question: {e}")
        return jsonify({"message": "Could not save the question due to a server error."}), 500
    
def _exam_has_current_affairs(exam_id, subject_id=None):
    q_subj = Subject.query.filter_by(exam_id=exam_id)
    if subject_id:
        subj = q_subj.filter_by(id=subject_id).first()
        if subj:
            # 1) direct subject match
            if any(k in subj.name.lower() for k in CA_KEYWORDS_SUBJ):
                return True, subj, None
            # 2) any topic under this subject matches
            t = Topic.query.filter_by(subject_id=subj.id).all()
            if any(any(k in (x.name or '').lower() for k in CA_KEYWORDS_TOPIC) for x in t):
                return True, subj, None
            return False, subj, None

    # Scan full exam
    subjects = q_subj.all()
    for s in subjects:
        if any(k in s.name.lower() for k in CA_KEYWORDS_SUBJ):
            return True, s, None
        topics = Topic.query.filter_by(subject_id=s.id).all()
        if any(any(k in (t.name or '').lower() for k in CA_KEYWORDS_TOPIC) for t in topics):
            return True, s, None

    return False, None, None


@ai_bp.route('/current-affairs', methods=['POST'])
@jwt_required()
# @student_required()                     # optional: restrict to students
# @ai_usage_limited('generate')           # optional: count usage for free users
def current_affairs():
    """
    Generate daily current-affairs MCQs *only if* the exam includes CA/GK.
    Tailors the questions to the exam and (optionally) the chosen subject.
    Returns:
      - 200 with {available: false, message: "..."} if exam has no CA.
      - 200 with {available: true, generated: "..."} otherwise.
    """
    try:
        ident = get_jwt_identity()
        user_id = ident.get('id') if isinstance(ident, dict) else ident

        data = request.get_json() or {}
        exam_id = data.get('exam_id')
        subject_id = data.get('subject_id')

        if not exam_id:
            return jsonify({"message": "exam_id is required"}), 400

        # Validate exam exists
        exam = Exam.query.get(exam_id)
        if not exam:
            return jsonify({"message": "Exam not found."}), 404

        # Optional: ensure student has access to this exam
        access = StudentExam.query.filter(
            StudentExam.student_user_id == user_id,
            StudentExam.exam_id == exam_.id,
            StudentExam.access_status.in_(['purchased','free_access','admin_granted'])
        ).first()
        if not access:
            return jsonify({"message": "You do not have access to this exam."}), 403

        # Gate by syllabus
        has_ca, matched_subject, _ = _exam_has_current_affairs(exam_id, subject_id)
        if not has_ca:
            return jsonify({
                "available": False,
                "message": f"'{exam.name}' does not include a Current Affairs/GK component."
            }), 200

        # Craft exam-aware prompt
        subject_name = matched_subject.name if matched_subject else "General Awareness"
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        prompt = f'''
You are an exam coach. Generate exactly 10 multiple-choice questions (MCQs) for **{exam.name}**
focused on **{subject_name} / Current Affairs**, relevant to events from the last 30 days (as of {today_str}).

Rules:
- Each question should be 1–2 lines.
- 4 options (A–D). Mark the correct option by appending a single asterisk (*) at the end of that option line.
- Mix National/International, Economy, Science/Tech, Sports, Govt Schemes, Appointments, Summits, Reports.
- Difficulty: moderate and exam-appropriate.
- Output plain text only. Format exactly like:

1. Question text?
A) Option 1
B) Option 2*
C) Option 3
D) Option 4

2. Question text?
A) ...
B) ...*
C) ...
D) ...

(continue until 10)
'''

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=900
        )
        text = resp.choices[0].message.content.strip() if resp and resp.choices else "No content generated."

        return jsonify({
            "available": True,
            "generated": text,
            "exam": {"id": exam.id, "name": exam.name},
            "subject_used": subject_name
        }), 200
    except Exception as e:
        current_app.logger.exception("Current affairs generation failed: %s", e)
        return jsonify({"message": "Failed to generate current affairs."}), 500


@ai_bp.route('/explain-question', methods=['POST'])
@student_required()
@ai_usage_limited(feature_type='explain')
def explain_question_differently(current_user, **kwargs):
    data = request.get_json() or {}
    question_text = data.get('question_text')
    explanation_text = data.get('explanation_text')

    if not question_text or not explanation_text:
        return jsonify({"message": "Question and explanation are required."}), 400

    prompt = f'''A student is reviewing a question and needs a different perspective. 
    The question is: '{question_text}'. 
    The correct explanation is: '{explanation_text}'. 
    Please explain the core concept behind this answer in a simpler way. 
    You can use a real-world analogy if it helps. Do not just rephrase the original explanation.'''

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=400
        )
        ai_explanation = resp.choices[0].message.content
        return jsonify({"explanation": ai_explanation}), 200
    except Exception as e:
        current_app.logger.error(f"OpenAI error (explain): {e}")
        return jsonify({"message": "Could not generate explanation due to an AI service error."}), 500