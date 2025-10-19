# In app/tasks.py
from app import create_app, db
from .models.class_management import Class, Notification
from .models.organization import OrganizationMembership, Plan
from .models.user import User
from .models.mock_test import MockTest, MockTestQuestion
from .models.reports import MockTestReport, TopicPerformanceSummary
from .models.student_progress import StudentTestAttempt, StudentQuestionResponse
from .models.question import Question
from .models.topic import Topic
from sqlalchemy import func
from datetime import datetime

# --- NEW: Define the limit for free reports ---
FREE_TIER_REPORT_LIMIT = 2

def send_class_reminders(class_id):
    """
    This is the background task that finds a class, gets the students,
    and sends a notification to each one.
    """
    app = create_app()
    with app.app_context():
        live_class = Class.query.get(class_id)
        if not live_class or live_class.status != 'scheduled':
            print(f"Skipping notifications for class {class_id}, not found or not scheduled.")
            return

        organization_id = live_class.organization_id
        
        # Find all active students in the organization
        students_in_org = User.query.join(OrganizationMembership).filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.is_active == True,
            User.user_type == 'student'
        ).all()

        print(f"Sending reminders for class '{live_class.title}' to {len(students_in_org)} students.")

        for student in students_in_org:
            # You can make this link point to your live class page
            class_url = f"/class/{live_class.id}/live" 

            notification = Notification(
                organization_id=organization_id,
                user_id=student.id,
                sender_user_id=live_class.instructor_id,
                class_id=live_class.id,
                notification_type='class_reminder',
                title=f"Class Starting Soon: {live_class.title}",
                message=f"Your class is scheduled to begin in about 15 minutes. Get ready to join!",
                link=class_url
            )
            db.session.add(notification)
        
        db.session.commit()
        print("Notifications sent successfully.")


def analyze_mock_test_performance(mock_test_id):
    """
    Analyzes mock test performance, generates a report, and saves it.
    This is now smarter and respects the organization's subscription plan.
    """
    app = create_app()
    with app.app_context():
        mock_test = MockTest.query.get(mock_test_id)
        if not mock_test:
            print(f"Mock Test {mock_test_id} not found. Aborting analysis.")
            return

        try:
            organization = mock_test.exam.organization
            plan = organization.plan

            # --- THIS IS THE NEW FREEMIUM LOGIC ---
            is_premium_ai_plan = plan and "AI Assistant" in plan.features # Check if the org has the AI plan

            if not is_premium_ai_plan:
                # For free users, check their monthly report usage
                current_month = datetime.utcnow().strftime('%Y-%m')
                reports_this_month = MockTestReport.query.filter(
                    MockTestReport.organization_id == organization.id,
                    db.func.date_trunc('month', MockTestReport.generated_at) == datetime.strptime(current_month + '-01', '%Y-%m-%d')
                ).count()

                if reports_this_month >= FREE_TIER_REPORT_LIMIT:
                    print(f"Org {organization.id} has reached its free report limit for the month. Skipping analysis.")
                    # Optionally, we could still create a notification telling them to upgrade
                    return
            # --- END OF NEW LOGIC ---

            print(f"Starting performance analysis for Mock Test ID: {mock_test_id}...")

            # 1. Get all completed attempts for this test
            attempts = StudentTestAttempt.query.filter_by(
                mock_test_id=mock_test_id,
                status='completed'
            ).all()

            if not attempts:
                print(f"No completed attempts found for Mock Test {mock_test_id}. Nothing to analyze.")
                mock_test.report_status = 'no_data'
                db.session.commit()
                return

            total_attempts = len(attempts)
            attempt_ids = [a.id for a in attempts]
            
            # 2. Calculate high-level stats (Average Score, Pass Rate)
            total_score = db.session.query(func.sum(StudentTestAttempt.score)).filter(StudentTestAttempt.id.in_(attempt_ids)).scalar() or 0
            average_score = (total_score / total_attempts) if total_attempts > 0 else 0
            
            passed_count = sum(1 for a in attempts if a.score >= mock_test.passing_marks)
            pass_rate = (passed_count / total_attempts) * 100 if total_attempts > 0 else 0

            # 3. Create or update the main report record
            report = MockTestReport.query.filter_by(mock_test_id=mock_test_id).first()
            if not report:
                report = MockTestReport(mock_test_id=mock_test_id, organization_id=mock_test.exam.organization_id)
                db.session.add(report)

            report.total_attempts = total_attempts
            report.average_score = round(average_score, 2)
            report.pass_rate = round(pass_rate, 2)
            report.generated_at = func.now()

            # Clear old summaries
            TopicPerformanceSummary.query.filter_by(report_id=report.id).delete()
            db.session.flush()

            # 4. Analyze Performance by Topic
            topic_performance = db.session.query(
                Question.topic_id,
                Topic.name,
                func.count(StudentQuestionResponse.id).label('total_responses'),
                func.sum(db.case([(StudentQuestionResponse.is_correct == True, 1)], else_=0)).label('correct_responses')
            ).join(Question, StudentQuestionResponse.question_id == Question.id) \
            .join(Topic, Question.topic_id == Topic.id) \
            .filter(StudentQuestionResponse.attempt_id.in_(attempt_ids)) \
            .group_by(Question.topic_id, Topic.name).all()

            for topic_id, topic_name, total, correct in topic_performance:
                accuracy = (correct / total) * 100 if total > 0 else 0
                
                question_count_for_topic = db.session.query(func.count(MockTestQuestion.id)) \
                    .join(Question, MockTestQuestion.question_id == Question.id) \
                    .filter(MockTestQuestion.mock_test_id == mock_test_id) \
                    .filter(Question.topic_id == topic_id) \
                    .scalar()

                summary = TopicPerformanceSummary(
                    report_id=report.id,
                    topic_id=topic_id,
                    topic_name=topic_name,
                    average_accuracy=round(accuracy, 2),
                    question_count=question_count_for_topic,
                    student_count=total_attempts
                )
                db.session.add(summary)
            
            # --- NEW: Generate AI insights ONLY for premium users ---
            if is_premium_ai_plan:
                _generate_ai_report_insights(report, topic_performance, mock_test)
            else:
                # Fallback for non-premium users
                report.remedial_plan_details = {"message": "Upgrade to a premium plan to unlock AI-powered remedial plans."}
                report.at_risk_students = {"summary": "Upgrade to a premium plan to view at-risk student analysis.", "students": []}

            mock_test.report_status = 'completed'
            db.session.commit()
            print(f"Performance analysis for Mock Test ID: {mock_test_id} completed and saved.")

        except Exception as e:
            db.session.rollback()
            print(f"Error during performance analysis for Mock Test ID: {mock_test_id}. Error: {e}")
            if mock_test:
                mock_test.report_status = 'failed'
                db.session.commit()

def _generate_ai_report_insights(report, topic_performance_data, mock_test):
    """
    Uses OpenAI to generate a summary, remedial plan, and identify at-risk students.
    """
    try:
        from openai import OpenAI
        import json
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 1. Format the data for the prompt
        topic_summary = "\n".join([
            f"- Topic: '{item.topic_name}', Average Accuracy: {item.average_accuracy}%"
            for item in topic_performance_data
        ])

        at_risk_students_data = db.session.query(
                StudentTestAttempt.student_user_id,
                User.first_name,
                User.last_name,
                StudentTestAttempt.score
            ).join(User, StudentTestAttempt.student_user_id == User.id)\
            .filter(StudentTestAttempt.mock_test_id == mock_test.id)\
            .filter(StudentTestAttempt.score < mock_test.passing_marks)\
            .order_by(StudentTestAttempt.score.asc())\
            .limit(5).all()

        at_risk_summary = "\n".join([
            f"- Student ID: {s.student_user_id}, Name: {s.first_name} {s.last_name}, Score: {s.score}"
            for s in at_risk_students_data
        ])

        prompt = f"""
        You are an expert educational analyst reviewing a mock test report for the test '{mock_test.title}'.

        **Performance Data:**
        - Total Attempts: {report.total_attempts}
        - Average Score: {report.average_score:.2f}
        - Pass Rate: {report.pass_rate:.2f}%
        - Passing Marks: {mock_test.passing_marks}

        **Performance by Topic:**
        {topic_summary}

        **Students who scored below passing marks (at-risk):**
        {at_risk_summary if at_risk_summary else "None"}

        **Your Task:**
        Based on the data, provide a concise analysis in JSON format. The JSON object must have the following keys:
        1. "executive_summary": A 2-3 sentence professional summary of the overall performance.
        2. "remedial_plan": A bulleted list (as a single string with '\n- ') identifying the top 2-3 weakest topics (lowest accuracy) and suggesting a brief, actionable remedial plan for each.
        3. "at_risk_students_summary": A 1-2 sentence summary identifying the number of at-risk students and the general trend (e.g., "struggling with specific topics").

        **Example JSON Output:**
        {{
          "executive_summary": "Overall performance was moderate, with a pass rate of 65%. While students performed well in Algebra, there is a significant weakness in Geometry and Trigonometry that needs to be addressed.",
          "remedial_plan": "- Geometry (45% Accuracy): Recommend a review session on foundational theorems and provide 10 additional practice problems.\n- Trigonometry (52% Accuracy): Suggest students watch the video lecture on trigonometric identities and complete the associated quiz.",
          "at_risk_students_summary": "5 students are at risk, primarily due to low scores in the identified weak topics. They may require one-on-one attention."
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=600
        )

        insights = json.loads(response.choices[0].message.content)

        # Update the report with the generated insights
        report.remedial_plan_details = {
            "summary": insights.get("executive_summary", "AI summary could not be generated."),
            "plan": insights.get("remedial_plan", "Remedial plan could not be generated.")
        }
        report.at_risk_students = {
            "summary": insights.get("at_risk_students_summary", "Could not generate at-risk summary."),
            "students": [s.student_user_id for s in at_risk_students_data]
        }
        print("Successfully generated AI insights for the report.")

    except Exception as e:
        print(f"Could not generate AI insights for report {report.id}. Error: {e}")
        # Fallback to placeholder
        report.remedial_plan_details = {"message": "AI analysis failed to run."}
        report.at_risk_students = {"summary": "AI analysis failed to run.", "students": []}