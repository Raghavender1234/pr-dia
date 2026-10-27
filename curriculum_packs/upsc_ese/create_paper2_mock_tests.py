# -*- coding: utf-8 -*-
"""
Create comprehensive Mock Tests in LMS for Paper-II Mechanical Engineering
and updated Paper-I General Studies.
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.mock_test import MockTest, MockTestQuestion
from app.models.question import Question

def main():
    app = create_app()
    with app.app_context():
        # Test 1: Thermal & Fluids (Topics 1-22)
        q_thermal = Question.query.filter(Question.topic_id.between(1, 22), Question.deleted_at == None).order_by(Question.id).all()
        mt1 = MockTest.query.filter_by(exam_id=1, title="UPSC ESE Prelims Paper-II: Thermal & Fluid Engineering Sectional Mock Test").first()
        if not mt1:
            mt1 = MockTest(
                exam_id=1,
                title="UPSC ESE Prelims Paper-II: Thermal & Fluid Engineering Sectional Mock Test",
                description="Comprehensive sectional test covering Fluid Mechanics, Turbo Machinery, Thermodynamics, Heat Transfer, IC Engines, RAC, Power Plant & Renewable Energy (Topics 1 to 22).",
                duration_minutes=120,
                total_marks=len(q_thermal) * 2.0,
                passing_marks=len(q_thermal) * 0.8,
                status='active',
                default_marks_per_question=2.00,
                negative_marking_enabled=True,
                negative_marking_ratio=0.33,
                created_by_user_id=1
            )
            db.session.add(mt1)
            db.session.flush()
            for idx, q in enumerate(q_thermal, 1):
                db.session.add(MockTestQuestion(mock_test_id=mt1.id, question_id=q.id, question_order=idx, marks=2.0))

        # Test 2: Design & Materials (Topics 23-45)
        q_design = Question.query.filter(Question.topic_id.between(23, 45), Question.deleted_at == None).order_by(Question.id).all()
        mt2 = MockTest.query.filter_by(exam_id=1, title="UPSC ESE Prelims Paper-II: Design, TOM, SOM & Materials Sectional Mock Test").first()
        if not mt2:
            mt2 = MockTest(
                exam_id=1,
                title="UPSC ESE Prelims Paper-II: Design, TOM, SOM & Materials Sectional Mock Test",
                description="Sectional test covering Theory of Machines, Vibrations, Strength of Materials, Machine Design, and Engineering Materials (Topics 23 to 45).",
                duration_minutes=120,
                total_marks=len(q_design) * 2.0,
                passing_marks=len(q_design) * 0.8,
                status='active',
                default_marks_per_question=2.00,
                negative_marking_enabled=True,
                negative_marking_ratio=0.33,
                created_by_user_id=1
            )
            db.session.add(mt2)
            db.session.flush()
            for idx, q in enumerate(q_design, 1):
                db.session.add(MockTestQuestion(mock_test_id=mt2.id, question_id=q.id, question_order=idx, marks=2.0))

        # Test 3: Manufacturing, Industrial & Mechatronics (Topics 46-61)
        q_mfg = Question.query.filter(Question.topic_id.between(46, 61), Question.deleted_at == None).order_by(Question.id).all()
        mt3 = MockTest.query.filter_by(exam_id=1, title="UPSC ESE Prelims Paper-II: Manufacturing, Industrial & Mechatronics Mock Test").first()
        if not mt3:
            mt3 = MockTest(
                exam_id=1,
                title="UPSC ESE Prelims Paper-II: Manufacturing, Industrial & Mechatronics Mock Test",
                description="Sectional test covering Casting, Forming, Welding, Machining, Metrology, PPC, Inventory, OR, Reliability, Microprocessors, Sensors & Robotics (Topics 46 to 61).",
                duration_minutes=90,
                total_marks=len(q_mfg) * 2.0,
                passing_marks=len(q_mfg) * 0.8,
                status='active',
                default_marks_per_question=2.00,
                negative_marking_enabled=True,
                negative_marking_ratio=0.33,
                created_by_user_id=1
            )
            db.session.add(mt3)
            db.session.flush()
            for idx, q in enumerate(q_mfg, 1):
                db.session.add(MockTestQuestion(mock_test_id=mt3.id, question_id=q.id, question_order=idx, marks=2.0))

        # Test 4: Paper-II Full Grand Mock Test (Topics 1-61)
        q_paper2_all = Question.query.filter(Question.topic_id.between(1, 61), Question.deleted_at == None).order_by(Question.id).all()
        mt4 = MockTest.query.filter_by(exam_id=1, title="UPSC ESE Prelims Paper-II: Mechanical Engineering Full-Syllabus Grand Mock Test").first()
        if not mt4:
            mt4 = MockTest(
                exam_id=1,
                title="UPSC ESE Prelims Paper-II: Mechanical Engineering Full-Syllabus Grand Mock Test",
                description="Comprehensive full-syllabus mock exam covering all 11 Mechanical Engineering disciplines (183 questions). Standard UPSC 1/3rd negative marking.",
                duration_minutes=180,
                total_marks=len(q_paper2_all) * 2.0,
                passing_marks=len(q_paper2_all) * 0.8,
                status='active',
                default_marks_per_question=2.00,
                negative_marking_enabled=True,
                negative_marking_ratio=0.33,
                created_by_user_id=1
            )
            db.session.add(mt4)
            db.session.flush()
            for idx, q in enumerate(q_paper2_all, 1):
                db.session.add(MockTestQuestion(mock_test_id=mt4.id, question_id=q.id, question_order=idx, marks=2.0))

        # Test 5: Paper-I All 10 Subjects Grand Mock Test (Topics 62-71)
        q_paper1_all = Question.query.filter(Question.topic_id.between(62, 71), Question.deleted_at == None).order_by(Question.id).all()
        mt5 = MockTest.query.filter_by(exam_id=1, title="UPSC ESE Prelims Paper-I: General Studies & Engineering Aptitude Complete 10-Subject Grand Mock").first()
        if not mt5:
            mt5 = MockTest(
                exam_id=1,
                title="UPSC ESE Prelims Paper-I: General Studies & Engineering Aptitude Complete 10-Subject Grand Mock",
                description="Comprehensive 140-question mock exam covering all 10 Paper-I GS subjects (Current Issues, Aptitude, Maths, Design/Drawing, Quality, Environment, Project Management, Material Science, ICT, Ethics).",
                duration_minutes=120,
                total_marks=len(q_paper1_all) * 2.0,
                passing_marks=len(q_paper1_all) * 0.66,
                status='active',
                default_marks_per_question=2.00,
                negative_marking_enabled=True,
                negative_marking_ratio=0.33,
                created_by_user_id=1
            )
            db.session.add(mt5)
            db.session.flush()
            for idx, q in enumerate(q_paper1_all, 1):
                db.session.add(MockTestQuestion(mock_test_id=mt5.id, question_id=q.id, question_order=idx, marks=2.0))

        db.session.commit()
        print("Successfully created all Sectional and Grand Mock Tests in LMS database!")

if __name__ == '__main__':
    main()
