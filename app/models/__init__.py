# backend/app/models/__init__.py

# Import all your model definitions here.
# This ensures SQLAlchemy's metadata object registers all models
# when the 'models' package is imported.

from .user import User 
from .organization import Plan, Organization, OrganizationMembership
from .exam import Exam
from .subject import Subject
from .topic import Topic
from .question import Question, MCQOption, ComprehensionPassage # ADD THIS LINE
from .mock_test import MockTest, MockTestQuestion # ADD THIS LINE
from .student_progress import StudentExam, StudentAISubscription, StudentTestAttempt, StudentQuestionResponse, StudentAIUsage
# You can potentially add other models here as you create them:
# from .question import Question, MCQOption, ComprehensionPassage
# from .mock_test import MockTest, MockTestQuestion
# from .student_progress import StudentExam, StudentAISubscription, StudentTestAttempt, StudentQuestionResponse