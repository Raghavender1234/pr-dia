# backend/app/api/ai.py
import os
import uuid
import requests
import boto3
import re
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

# Lazy loader for OpenAI client
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client

CA_KEYWORDS_SUBJ = ['current affairs', 'general awareness', 'gk', 'general knowledge', 'general studies', 'engineering aptitude']
CA_KEYWORDS_TOPIC = ['current affairs', 'current events', 'news', 'national affairs', 'international affairs', 'general studies']

def _upload_image_to_s3(image_url):
    """
    Saves generated AI diagrams locally to app/static/uploads/generated_questions/
    when S3 is not configured (0 cloud storage cost for local personal use).
    """
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()

        s3_bucket = os.environ.get('S3_BUCKET_NAME')
        if s3_bucket and os.environ.get('AWS_ACCESS_KEY_ID'):
            s3_client = boto3.client('s3')
            image_key = f"generated_questions/{uuid.uuid4()}.png"
            s3_client.upload_fileobj(response.raw, s3_bucket, image_key)
            region = os.environ.get('AWS_REGION', 'us-east-1')
            return f"https://{s3_bucket}.s3.{region}.amazonaws.com/{image_key}"

        # Local fallback: save directly on PC inside app/static/uploads/generated_questions
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'generated_questions')
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"/static/uploads/generated_questions/{filename}"
    except Exception as e:
        current_app.logger.error(f"Image save failed: {e}")
        return None


@ai_bp.route('/generate_questions', methods=['POST'])
@student_required()
@ai_usage_limited(feature_type='generate')
def generate_similar_questions(current_user, **kwargs):
    if not get_openai_client():
        return jsonify({
            "message": "OpenAI API key is not configured in .env. Please set OPENAI_API_KEY to generate live AI questions."
        }), 400

    data = request.get_json() or {}

    question_type = data.get('question_type', 'MCQ')
    original_question = data.get('question_text', '')
    passage_text = data.get('passage_text')  # for comprehension
    difficulty = data.get('difficulty', 'medium')
    topic_name = data.get('topic_name', 'Core Topic')
    subject_name = data.get('subject_name', 'Core Subject')
    exam_name = data.get('exam_name') or 'Academic & Competitive Examination'

    if not original_question and question_type != 'Comprehension':
        return jsonify({"message": "The 'question_text' field is required."}), 400

    if question_type == 'Comprehension':
        prompt = fr'''
You are an elite academic Question Setter and Subject Matter Expert specializing in "{subject_name}" for "{exam_name}".
A candidate is studying the "{topic_name}" topic under "{subject_name}".

**Your Task:**
1. Based on the original passage/case study below, generate **one new, rigorous academic case study or analytical comprehension passage** on the same subject matter suitable for "{exam_name}" standards.
2. After the new passage, generate **3 new, distinct multiple-choice sub-questions** that test analytical reasoning, governing principles, or practical applications.

**Instructions for Generating High-Quality Questions:**
*   Test conceptual clarity, edge cases, underlying assumptions, and practical application.
*   Maintain "{difficulty}" difficulty level matching standard curriculum benchmarks.
*   Create plausible distractors based on common misconceptions and calculation errors.

**CRITICAL FORMATTING RULES (STRICTLY ENFORCED):**
1. Do NOT wrap your entire response in an HTML or markdown code block (do not use ```). Use HTML tags (<b>, <h3>, <ul>, <li>) instead of markdown symbols (**, #) for formatting.
2. Write the passage text first.
3. Each sub-question MUST start exactly with a number, a period, and a space (e.g., "1. ", "2. "). Do NOT make the numbers bold.
4. Each sub-question MUST have exactly 4 options. They MUST start with "A) ", "B) ", "C) ", "D) ".
5. Append exactly "(Correct)" to the end of the correct option's text.

**EXAMPLE EXACT FORMAT:**
Here is the new passage text...

1. What is the primary governing principle in the above system?
A) Option one
B) Option two (Correct)
C) Option three
D) Option four

**Original Passage:**
{passage_text}
'''
    else:
        prompt = fr'''
You are an elite academic Question Author and Subject Matter Expert specializing in "{subject_name}" for "{exam_name}".
The candidate is preparing for "{exam_name}", studying the subject "{subject_name}", and focusing on the topic "{topic_name}".

Based on the following original question (difficulty: "{difficulty}"), generate **3 new, distinct, high-yield examination Multiple-Choice Questions (MCQs)**.

**Question Design Guidelines:**
1. **Diverse Question Archetypes:**
   * Mix standard rigorous question archetypes across the 3 generated questions:
     - **Type 1 (Conceptual / Multi-Statement):** e.g., *"Consider the following statements regarding {topic_name}: (1) ... (2) ... (3) ... Which of the above statements is/are correct?"*
     - **Type 2 (Assertion-Reason / Statement-I & Statement-II):** e.g., *"Statement (I): ... Statement (II): ... Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)"*.
     - **Type 3 (Analytical / Numerical / Practical Application):** Problems with clean numbers or direct application, testing core principles of "{subject_name}".
2. **Mirror Complexity & Equations:**
   * **Use HTML for all text formatting** (`<h3>`, `<ul>/<li>`, `<b>`). Do NOT use Markdown symbols (`**`, `#`).
   * **Mathematical & Scientific Equations:** ALWAYS enclose LaTeX expressions in single dollar signs (`$...$`).
   * **Diagrams/Charts:** If strictly required, use ASCII art inside `<pre>` tags or `[GENERATE_IMAGE: detailed technical description]`.
3. **High-Precision Distractors:**
   * Incorrect options must reflect common student misconceptions, sign errors, or classic edge cases.

**CRITICAL FORMATTING RULES (STRICTLY ENFORCED):**
1. Do NOT wrap your entire response in an HTML or markdown code block (do not use ```).
2. Each question MUST begin exactly with a number, a period, and a space (e.g., "1. ", "2. ", "3. ").
3. For Type 1 (Multi-Statement) questions:
   - Always state: "Consider the following statements regarding [Topic]:"
   - Number the internal statements as "(1) ", "(2) ", "(3) " (using parentheses, never bare numbers without parentheses).
   - Follow with: "Which of the above statements is/are correct?"
   - Options must be: A) 1 and 2 only, B) 2 and 3 only, C) 1 and 3 only, D) 1, 2 and 3.
4. For Type 2 (Assertion-Reason / Statement-I & Statement-II) questions:
   - You MUST write both statements explicitly:
     Statement (I): [Technical assertion / property]
     Statement (II): [Governing physical explanation / mechanism]
   - NEVER use angle brackets like `<I>` or `<II>`. Always use parentheses `Statement (I)` and `Statement (II)`.
   - The four standard options MUST be:
     A) Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)
     B) Both Statement (I) and Statement (II) are individually true, but Statement (II) is not the correct explanation of Statement (I)
     C) Statement (I) is true, but Statement (II) is false
     D) Statement (I) is false, but Statement (II) is true
5. Each question MUST provide exactly four options starting with "A) ", "B) ", "C) ", "D) ".
6. You MUST mark the correct option by appending exactly "(Correct)" at the very end of the option text.

**EXAMPLE EXACT FORMAT:**
1. Consider the following statements regarding Virtual Private Networks (VPNs):
(1) VPNs establish an encrypted tunnel across public networks to preserve confidentiality.
(2) IPsec operate at the network layer to authenticate and encrypt IP packets.
(3) VPNs eliminate the physical propagation delay of undersea fiber optic cables.
Which of the above statements is/are correct?
A) (1) and (2) only (Correct)
B) (2) and (3) only
C) (1) and (3) only
D) (1), (2) and (3)

2. Statement (I): In a counter-flow heat exchanger, the exit temperature of the cold fluid can exceed the exit temperature of the hot fluid.
Statement (II): In counter-flow arrangement, the temperature difference between the two fluids along the length of the exchanger remains more uniform than in parallel flow.
A) Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I) (Correct)
B) Both Statement (I) and Statement (II) are individually true, but Statement (II) is not the correct explanation of Statement (I)
C) Statement (I) is true, but Statement (II) is false
D) Statement (I) is false, but Statement (II) is true

**Original Question to Base Off Of:**
{original_question}
'''

    client = get_openai_client()
    if not client:
        return jsonify({
            "message": "OpenAI API key is not configured in .env. Please configure OPENAI_API_KEY to generate live AI questions."
        }), 400

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=900
        )
        generated_text = resp.choices[0].message.content

        # Find image generation requests
        image_requests = re.findall(r'\[GENERATE_IMAGE: (.*?)\]', generated_text)

        for image_prompt in image_requests:
            try:
                image_resp = get_openai_client().images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024",
                    response_format="url"
                )
                dalle_image_url = image_resp.data[0].url
                saved_url = _upload_image_to_s3(dalle_image_url)

                if saved_url:
                    html_image = f'<img src="{saved_url}" alt="{image_prompt}" style="max-width:100%; border-radius:8px; margin:8px 0;" />'
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", html_image, 1)
                else:
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "", 1)

            except Exception as img_e:
                current_app.logger.error(f"DALL-E or image save error: {img_e}")
                generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "", 1)

        return jsonify({"generated": generated_text}), 200
    except Exception as e:
        current_app.logger.error(f"OpenAI error (generate): {e}")
        return jsonify({"message": "Could not generate questions due to an AI service error."}), 500


@ai_bp.route('/validate_answer', methods=['POST'])
@student_required()
@ai_usage_limited(feature_type='validate')
def validate_open_ended_answer(current_user, **kwargs):
    if not get_openai_client():
        return jsonify({
            "feedback": "AI evaluation is in offline mode. Configure OPENAI_API_KEY in your .env file to enable live evaluation."
        }), 200

    data = request.get_json() or {}
    question = data.get('question')
    student_answer = data.get('answer')

    if not question or not student_answer:
        return jsonify({"message": "Both 'question' and 'answer' are required."}), 400

    prompt = f'''
You are a knowledgeable and encouraging academic evaluator.
A student was asked: '{question}'
The student answered: '{student_answer}'
Evaluate the technical accuracy, key principles, formulas, and completeness in 2–3 concise sentences.
'''

    client = get_openai_client()
    if not client:
        return jsonify({
            "feedback": "AI evaluation is in offline mode. Configure OPENAI_API_KEY in your .env file to enable live evaluation."
        }), 200

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=250
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

    data = request.get_json() or {}
    user_message = data.get('message')
    if not user_message:
        return jsonify({"message": "A message is required."}), 400

    history = data.get('history', [])
    exam_name = data.get('exam_name') or 'Academic & Competitive Examination'
    subject_name = data.get('subject_name') or 'Core Subject Concepts'

    if user.user_type == 'student':
        system_prompt = (
            f"You are OpenLMS AI, an intelligent academic mentor helping {user.first_name} "
            f"master '{exam_name}', specifically focusing on '{subject_name}'. "
            "Focus on deep conceptual clarity, derivations, governing principles, practical intuition, common exam traps, "
            "and step-by-step problem solving. "
            "Format your responses using clean HTML tags (<h3> for subheadings, <ul>/<li> for bullet points, <b> for bold text) and enclose equations in $...$. "
            "Do NOT use markdown symbols like hashtags (#) or asterisks (**)."
        )
    else:  # For admins / question generation
        system_prompt = (
            f"You are an expert academic Question Setter and Technical Content Architect "
            f"assisting {user.first_name}. Your goal is to generate authentic examination-level MCQs (Multi-statement, Statement-I/Statement-II Assertion-Reason, "
            f"and analytical numericals), concise revision notes, formula sheets, and high-yield explanations across '{subject_name}' for '{exam_name}'. "
            "Format your responses using HTML tags (<h3>, <ul>/<li>, <b>) and LaTeX math inside $...$. Do NOT use markdown hashtags (#) or asterisks (**)."
        )

    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_message}]

    client = get_openai_client()
    if not client:
        return jsonify({
            "reply": "<h3>AI Study Assistant (Offline Mode)</h3><p>To enable live AI conversations, please configure your <code>OPENAI_API_KEY</code> in the <code>.env</code> file.</p>"
        }), 200

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=900
        )
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

    data = request.get_json() or {}
    history = data.get('history', [])
    subject_name = data.get('subject_name', 'Core Course Concepts')

    question_count = 10 if user.user_type != 'student' else 5

    system_prompt = f'''
You are an elite academic Question Setter and Curriculum Architect.
Based on the following discussion about '{subject_name}', create exactly {question_count} high-yield examination multiple-choice questions (MCQs).

**Instructions for Generating Authentic Questions:**
1. **Analyze the Discussion:** Identify the key principles, theories, equations, problem-solving methods, or analytical concepts discussed.
2. **Use Rigorous Question Styles:**
   * Include a mix of:
     - Conceptual multi-statement questions (*"Consider the following statements regarding [Topic]: (1)... (2)... Which of the above is/are correct?"*)
     - Statement (I) and Statement (II) (Assertion-Reason) questions
     - Practical application and numerical problems testing exact formulas.
3. **Formatting Guidelines:**
   * **Use HTML for all text formatting** (`<h3>`, `<ul>/<li>`, `<b>`). Do NOT use Markdown symbols (`**`, `#`).
   * **Equations:** Enclose all LaTeX code in dollar signs (`$...$`).
   * **Diagrams:** Only if strictly necessary, use HTML `<pre>` tags for ASCII art.

**CRITICAL FORMATTING RULES:**
1. Each question must start with a number followed by a period and space (e.g., "1. ", "2. ").
2. For Multi-Statement questions:
   - State: "Consider the following statements regarding [Topic]:"
   - Number the internal statements as "(1) ", "(2) ", "(3) " (using parentheses).
   - Follow with: "Which of the above statements is/are correct?"
   - Options must be: A) 1 and 2 only, B) 2 and 3 only, C) 1 and 3 only, D) 1, 2 and 3.
3. For Statement (I) and Statement (II) questions:
   - Provide both statements explicitly:
     Statement (I): [Technical assertion / property]
     Statement (II): [Governing physical explanation / mechanism]
   - NEVER use angle brackets like `<I>` or `<II>`. Always use parentheses `Statement (I)` and `Statement (II)`.
   - The four standard options MUST be:
     A) Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)
     B) Both Statement (I) and Statement (II) are individually true, but Statement (II) is not the correct explanation of Statement (I)
     C) Statement (I) is true, but Statement (II) is false
     D) Statement (I) is false, but Statement (II) is true
4. Provide exactly four options on separate lines, each starting with A) , B) , C) , and D) .
5. **You MUST mark the correct answer by appending `(Correct)` to the end of the correct option's text.**

**EXAMPLE OF PERFECT FORMATTING:**
1. Consider the following statements regarding Virtual Private Networks (VPNs):
(1) VPNs establish an encrypted tunnel across public networks to preserve confidentiality.
(2) IPsec operates at the network layer to authenticate and encrypt IP packets.
(3) VPNs eliminate the physical propagation delay of undersea fiber optic cables.
Which of the above statements is/are correct?
A) (1) and (2) only (Correct)
B) (2) and (3) only
C) (1) and (3) only
D) (1), (2) and (3)

**Conversation History:**
"{' '.join([msg.get('content', '') for msg in history])}"
'''

    try:
        response = get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7,
            max_tokens=1800
        )
        generated_text = response.choices[0].message.content

        image_requests = re.findall(r'\[GENERATE_IMAGE: (.*?)\]', generated_text)
        for image_prompt in image_requests:
            try:
                image_resp = get_openai_client().images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024",
                    response_format="url"
                )
                dalle_image_url = image_resp.data[0].url
                saved_url = _upload_image_to_s3(dalle_image_url)
                if saved_url:
                    html_image = f'<img src="{saved_url}" alt="{image_prompt}" style="max-width:100%; border-radius:8px; margin:8px 0;" />'
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", html_image, 1)
                else:
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "", 1)
            except Exception as img_e:
                current_app.logger.error(f"DALL-E or image save error: {img_e}")
                generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "", 1)

        return jsonify({"generated_questions": generated_text})
    except Exception as e:
        return jsonify({"message": f"Error generating questions: {str(e)}"}), 503


@ai_bp.route('/save-generated-question', methods=['POST'])
@admin_role_required(allowed_roles=['main_co_admin', 'co_admin', 'super_admin'])
def save_generated_question(current_user, organization=None, **kwargs):
    if Question is None or MCQOption is None:
        return jsonify({"message": "Server model import path for Question/MCQOption is not configured."}), 500

    data = request.get_json() or {}
    topic_id = data.get('topic_id')
    if not data.get('question_text') or not topic_id:
        return jsonify({"message": "Incomplete question data provided."}), 400

    try:
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
        return jsonify({"message": "Question saved to your question bank!"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving AI-generated question: {e}")
        return jsonify({"message": "Could not save the question due to a server error."}), 500


@ai_bp.route('/current-affairs', methods=['POST'])
@jwt_required()
def current_affairs():
    """
    Generates UPSC ESE Paper-I (General Studies & Engineering Aptitude) Current Affairs & GS MCQs.
    """
    try:
        data = request.get_json() or {}
        exam_id = data.get('exam_id')
        exam = Exam.query.get(exam_id) if exam_id else Exam.query.first()
        exam_name = exam.name if exam else "UPSC ESE (Engineering Services Examination)"
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        prompt = f'''
You are a UPSC ESE (Engineering Services Examination) Paper-I (General Studies and Engineering Aptitude) Coach.
Generate exactly 10 high-yield multiple-choice questions (MCQs) for '{exam_name}' Paper-I:
Current issues of national and international importance relating to social, economic and industrial development,
Engineering Aptitude, Energy & Environment, Project Management, Material Science, ICT, and Ethics in Engineering (as of {today_str}).

**CRITICAL FORMATTING RULES (STRICTLY ENFORCED):**
1. Do NOT wrap your response in a markdown code block.
2. Use HTML for all text formatting (e.g., `<b>` for bold). Do NOT use Markdown symbols.
3. Each question must start with a number followed by a period (e.g., "1. ").
4. Provide exactly four options, each starting with A), B), C), and D).
5. **You MUST mark the correct answer by appending `(Correct)` to the end of the correct option's text.**

**EXAMPLE OF PERFECT FORMATTING:**
1. Which national mission launched by the Government of India focuses on accelerating green hydrogen production and electrolyzer manufacturing?
A) National Bio-Energy Mission
B) National Green Hydrogen Mission (Correct)
C) Perform Achieve and Trade (PAT) Scheme
D) FAME-II Mission
'''

        resp = get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1100
        )
        text = resp.choices[0].message.content.strip() if resp and resp.choices else "No content generated."

        return jsonify({
            "available": True,
            "generated": text,
            "exam": {"id": exam.id if exam else 1, "name": exam_name},
            "subject_used": "UPSC ESE Paper-I: General Studies & Engineering Aptitude"
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

    prompt = f'''A UPSC ESE (Mechanical Engineering) candidate is reviewing a question and needs a crystal-clear, intuitive engineering explanation.
    The question is: '{question_text}'.
    The reference explanation is: '{explanation_text}'.
    Please explain the core Mechanical Engineering concept behind this answer using physical intuition, governing equations (in $...$ LaTeX), a practical engineering analogy, and highlight any common UPSC ESE exam traps or shortcuts to solve it quickly without a calculator.
    Format your response using HTML tags (<h3> for sub headings, <ul>/<li> for bullet points, <b> for bold text). Do NOT use markdown symbols like asterisks (**) or hashtags (#).'''

    client = get_openai_client()
    if not client:
        return jsonify({
            "explanation": "<h3>AI Socratic Tutor (Offline Mode)</h3><p>To enable live conceptual explanations, set <code>OPENAI_API_KEY</code> in your <code>.env</code> file.</p>"
        }), 200

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        ai_explanation = resp.choices[0].message.content
        return jsonify({"explanation": ai_explanation}), 200
    except Exception as e:
        current_app.logger.error(f"OpenAI error (explain): {e}")
        return jsonify({"message": "Could not generate explanation due to an AI service error."}), 500

