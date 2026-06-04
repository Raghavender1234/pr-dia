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

# One OpenAI client for this module
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CA_KEYWORDS_SUBJ = ['current affairs', 'general awareness', 'gk', 'general knowledge']
CA_KEYWORDS_TOPIC = ['current affairs', 'current events', 'news', 'national affairs', 'international affairs']

def _upload_image_to_s3(image_url):
    try:
        s3_bucket = os.environ.get('S3_BUCKET_NAME')
        if not s3_bucket:
            current_app.logger.error("S3_BUCKET_NAME environment variable not set.")
            return None

        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        s3_client = boto3.client('s3')
        image_key = f"generated_questions/{uuid.uuid4()}.png"

        s3_client.upload_fileobj(response.raw, s3_bucket, image_key)

        # Construct the URL manually
        region = os.environ.get('AWS_REGION', 'us-east-1') # Default to us-east-1 if not set
        s3_url = f"https://{s3_bucket}.s3.{region}.amazonaws.com/{image_key}"
        
        return s3_url
    except Exception as e:
        current_app.logger.error(f"S3 upload failed: {e}")
        return None



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

**CRITICAL FORMATTING RULES (STRICTLY ENFORCED):**
1. Do NOT wrap your entire response in an HTML or markdown code block (do not use ```). Use HTML tags (<b>, <h3>, <ul>, <li>) instead of markdown symbols (**, #) for formatting.
2. Write the passage text first. 
3. Each sub-question MUST start exactly with a number, a period, and a space (e.g., "1. ", "2. "). Do NOT make the numbers bold.
4. Each sub-question MUST have exactly 4 options. They MUST start with "A) ", "B) ", "C) ", "D) ".
5. Append exactly "(Correct)" to the end of the correct option's text.

**EXAMPLE EXACT FORMAT:**
Here is the new passage text...

1. What is the main idea of the passage?
A) Option one
B) Option two (Correct)
C) Option three
D) Option four

**Original Passage:**
{passage_text}
'''
    else:
        prompt = f'''
You are an expert Question Generator for Indian competitive exams, specializing in creating insightful and thought-provoking questions.
A student is preparing for the "{exam_name}" exam, studying the "{subject_name}" subject, and focusing on the "{topic_name}" topic.

Based on the following original question (difficulty: "{difficulty}"), generate 3 new, distinct, and more interesting Multiple-Choice Questions.

**Analysis of the Original Question:**
First, analyze the original question provided at the end. Does it contain any of the following?
- A mathematical equation (e.g., quadratic formula, integral)
- A chemical reaction (e.g., acid-base neutralization)
- A diagram or circuit (described in text or as ASCII art)

**Instructions for Generating High-Quality Questions:**

1.  **Mirror Complexity (When Applicable):**
    *   If the original question **does** contain a diagram, equation, or reaction, you **must generate at least one** new question that features a similar type of complex element. For example, if the original has a circuit diagram, one of your new questions should also be based on a circuit diagram.

2.  **Emphasize Real-World Scenarios:**
    *   For all questions, aim to create scenarios that mirror real-world problems.
    *   If relevant to the `{topic_name}`, consider introducing diagrams, chemical equations, or mathematical formulas even if the original question didn't have them.

3.  **Use Advanced Formatting (Where Appropriate):**
    *   **Use HTML for all text formatting** (e.g., `<h3>` for subheadings, `<ul>/<li>` for lists, `<b>` for bold). Do NOT use Markdown symbols like asterisks (`**`) or hashtags (`#`).
    *   **Mathematical/Chemical Equations:** ALWAYS enclose LaTeX expressions in double dollar signs (`$...$`). For example: `$2H_2 + O_2 \rightarrow 2H_2O$` or `$x = \frac{{-b \pm \sqrt{{b^2-4ac}}}}{{2a}}$`.
    *   **Diagrams/Circuits:** For complex visuals that cannot be drawn with ASCII art, you MUST use the following format: `[GENERATE_IMAGE: A detailed, specific description of the image to be generated]`. The description should be sufficient for a text-to-image model to create an accurate and relevant image for the question. For simple diagrams, you can use ASCII art inside a `<pre>` block.

4.  **Vary the Question Style:**
    *   Go beyond simple "what is" questions. Ask "why," "how," or present a scenario for analysis.
    *   Try creating questions based on application, exceptions to a rule, or comparing concepts.

5.  **Maintain Quality:**
    *   The new questions should match the original's "{difficulty}" level.
    *   All questions must be strictly relevant to the "{topic_name}".
    *   Incorrect options (distractors) should be challenging and based on common misconceptions.

**CRITICAL FORMATTING RULES (STRICTLY ENFORCED):**
1. Do NOT wrap your entire response in an HTML or markdown code block (do not use ```).
2. Each question MUST begin exactly with a number, a period, and a space (e.g., "1. ", "2. "). Do NOT make the numbers bold.
3. Each question MUST provide exactly four options starting with "A) ", "B) ", "C) ", "D) ".
4. You MUST mark the correct option by appending exactly "(Correct)" at the very end of the option text.

**EXAMPLE EXACT FORMAT:**
1. What is the value of $x$ in $2x = 4$?
A) 1
B) 2 (Correct)
C) 3
D) 4

**Original Question to Base Off Of:**
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

        # Find image generation requests
        image_requests = re.findall(r'\[GENERATE_IMAGE: (.*?)\]', generated_text)

        for image_prompt in image_requests:
            try:
                # Generate image with DALL-E
                image_resp = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024",
                    response_format="url"
                )
                dalle_image_url = image_resp.data[0].url

                # Upload to S3
                s3_url = _upload_image_to_s3(dalle_image_url)

                if s3_url:
                    # Replace placeholder with HTML image
                    html_image = f'<img src="{s3_url}" alt="{image_prompt}" />'
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", html_image, 1)
                else:
                    # If upload fails, replace with a note
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "[Image generation failed]", 1)

            except Exception as img_e:
                current_app.logger.error(f"DALL-E or S3 error: {img_e}")
                generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "[Image generation failed]", 1)


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
            f"focusing on '{subject_name}'. Explain concepts clearly using daily-life analogies. "
            "Format your responses using HTML tags (like <h3> for sub headings, <ul>/<li> for bullet points, and <b> for bold text). Do NOT use markdown symbols like hashtags (#) or asterisks (*)."
        )
    else: # For admins
        system_prompt = (
            f"You are a professional content creation assistant helping an administrator named {user.first_name}. "
            f"Your goal is to help them generate ideas for questions and content. "
            "Format your responses using HTML tags (like <h3> for sub headings, <ul>/<li> for bullet points, and <b> for bold text). Do NOT use markdown symbols like hashtags (#) or asterisks (*)."
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
    You are an {persona}. Based on the following conversation about '{subject_name}', create exactly {question_count} multiple-choice questions (MCQs).

    **Instructions for Generating High-Quality Questions:**

    1.  **Analyze the Conversation:** Review the chat history to identify key concepts, formulas, or topics discussed.

    2.  **Create Scenario-Based Questions:**
        *   Generate questions that apply the discussed concepts to real-world scenarios.
        *   If the conversation involved topics from science (Physics, Chemistry) or Math, **you are encouraged to include relevant equations, formulas, or simple diagrams** to make the questions more practical and comprehensive.

    3.  **Formatting Guidelines:**
        *   **Use HTML for all text formatting** (e.g., `<h3>` for subheadings, `<ul>/<li>` for lists, `<b>` for bold text). Do NOT use Markdown symbols like asterisks (`**`) or hashtags (`#`).
        *   **Equations:** Enclose all LaTeX code in double dollar signs (`$...$`). For example: `$E = mc^2$`.
        *   **Diagrams:** For complex visuals, you MUST use the format `[GENERATE_IMAGE: A detailed description]`. For simple diagrams, use HTML `<pre>` tags for ASCII art.

    **CRITICAL FORMATTING RULES:**
    1.  Each question must start with a number followed by a period (e.g., "1.").
    2.  Provide exactly four options, each starting with A), B), C), and D).
    3.  **You MUST mark the correct answer by appending `(Correct)` to the end of the correct option's text.**

    **EXAMPLE OF PERFECT FORMATTING:**
    1.  What is the formula for calculating the area of a circle?
        A) `$A = \pi r$`
        B) `$A = 2\pi r$`
        C) `$A = \pi r^2$ (Correct)`
        D) `$A = d^2$`

    **Conversation History:**
    "{' '.join([msg['content'] for msg in history])}"
    '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        generated_text = response.choices[0].message.content
        
        # Find image generation requests
        image_requests = re.findall(r'\[GENERATE_IMAGE: (.*?)\]', generated_text)

        for image_prompt in image_requests:
            try:
                # Generate image with DALL-E
                image_resp = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024",
                    response_format="url"
                )
                dalle_image_url = image_resp.data[0].url

                # Upload to S3
                s3_url = _upload_image_to_s3(dalle_image_url)

                if s3_url:
                    # Replace placeholder with HTML image
                    html_image = f'<img src="{s3_url}" alt="{image_prompt}" />'
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", html_image, 1)
                else:
                    # If upload fails, replace with a note
                    generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "[Image generation failed]", 1)

            except Exception as img_e:
                current_app.logger.error(f"DALL-E or S3 error: {img_e}")
                generated_text = generated_text.replace(f"[GENERATE_IMAGE: {image_prompt}]", "[Image generation failed]", 1)

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
            StudentExam.exam_id == exam.id,
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
You are an exam coach. Generate exactly 10 multiple-choice questions (MCQs) for the '{exam.name}' exam,
focused on '{subject_name} / Current Affairs', relevant to events from the last 30 days (as of {today_str}).

**CRITICAL FORMATTING RULES (STRICTLY ENFORCED):**
1.  Do NOT wrap your response in a markdown code block.
2.  Use HTML for all text formatting (e.g., `<b>` for bold). Do NOT use Markdown symbols.
3.  Each question must start with a number followed by a period (e.g., "1. ").
4.  Provide exactly four options, each starting with A), B), C), and D).
5.  **You MUST mark the correct answer by appending `(Correct)` to the end of the correct option's text.**
6.  Mix topics like National/International, Economy, Science/Tech, Sports, and Government Schemes.

**EXAMPLE OF PERFECT FORMATTING:**
1.  What recent initiative was launched by the Indian government to promote digital literacy in rural areas?
    A) Digital India Mission
    B) Pradhan Mantri Gramin Digital Saksharta Abhiyan (PMGDISHA) (Correct)
    C) Skill India
    D) Make in India
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
    Please explain the core concept behind this answer in a witty and funny way, but ensure it remains highly sensible, educational, and easy to understand for a student. 
    Use a clever real-world analogy if it helps make the concept stick. Do not just rephrase the original explanation.
    Format your response using HTML tags (like <h3> for sub headings, <ul>/<li> for bullet points, <b> for bold text). Do NOT use markdown symbols like asterisks (**) or hashtags (#).'''

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