"""
OpenLMS - Universal Database Seeder
===================================
Initializes default organizations, plans, users, and curricula
for open-source evaluation, development, and self-hosted deployments.

Usage:
    python seed_database.py
"""

import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import (
    User, Plan, Organization, OrganizationMembership,
    Exam, Subject, Topic, Question, MCQOption, MockTest, MockTestQuestion
)

app = create_app()

def seed_open_source_environment():
    with app.app_context():
        print("=" * 70)
        print("[*] Seeding OpenLMS Database...")
        print("=" * 70)

        # 1. Create tables if not present
        db.create_all()

        # 2. Seed Default Subscription Plans
        plans_spec = [
            {
                'name': 'Community Free',
                'monthly_price': 0.0,
                'max_coadmins': 1,
                'max_invited_students': 50,
                'is_publicly_available': True,
                'description': 'Ideal for individual educators, study groups, and self-hosters.'
            },
            {
                'name': 'Academy Pro',
                'monthly_price': 1999.0,
                'max_coadmins': 10,
                'max_invited_students': 500,
                'is_publicly_available': True,
                'description': 'Built for coaching centers, departments, and training institutes.'
            },
            {
                'name': 'Enterprise Campus',
                'monthly_price': 7999.0,
                'max_coadmins': 50,
                'max_invited_students': 5000,
                'is_publicly_available': True,
                'description': 'Full-scale university, multi-campus, and enterprise L&D deployment.'
            }
        ]

        for p_data in plans_spec:
            existing_plan = Plan.query.filter_by(name=p_data['name']).first()
            if not existing_plan:
                db.session.add(Plan(**p_data))
        db.session.commit()
        print("  [OK] Subscription plans verified")

        # 3. Seed Default Organization
        default_org = Organization.query.filter_by(name="Open Academy").first()
        if not default_org:
            community_plan = Plan.query.filter_by(name='Academy Pro').first()
            default_org = Organization(
                name="Open Academy",
                code="OPENACADEMY",
                subdomain="openacademy",
                status="active",
                plan_id=community_plan.id if community_plan else None
            )
            db.session.add(default_org)
            db.session.commit()
            print(f"  [OK] Default Organization created: '{default_org.name}' (ID: {default_org.id})")
        else:
            print(f"  [OK] Default Organization found: '{default_org.name}'")

        # 4. Seed Standard Users
        demo_users = [
            {
                'email': 'admin@openlms.dev',
                'password': 'Admin@123',
                'first_name': 'System',
                'last_name': 'Administrator',
                'user_type': 'super_admin'
            },
            {
                'email': 'instructor@openlms.dev',
                'password': 'Instructor@123',
                'first_name': 'Lead',
                'last_name': 'Faculty',
                'user_type': 'co_admin'
            },
            {
                'email': 'student@openlms.dev',
                'password': 'Student@123',
                'first_name': 'Alex',
                'last_name': 'Learner',
                'user_type': 'student'
            }
        ]

        created_users = {}
        for u_data in demo_users:
            user = User.query.filter_by(email=u_data['email']).first()
            if not user:
                user = User(
                    email=u_data['email'],
                    password_hash=generate_password_hash(u_data['password'], method='pbkdf2:sha256'),
                    first_name=u_data['first_name'],
                    last_name=u_data['last_name'],
                    user_type=u_data['user_type'],
                    status='active'
                )
                db.session.add(user)
                db.session.commit()
                print(f"  [OK] Created user: {u_data['email']} ({u_data['user_type']})")
            else:
                print(f"  [OK] User exists: {u_data['email']}")
            created_users[u_data['user_type']] = user

        # 5. Link Co-Admin & Student to Default Organization
        for role, user in created_users.items():
            if role in ('co_admin', 'student'):
                membership = OrganizationMembership.query.filter_by(
                    user_id=user.id,
                    organization_id=default_org.id
                ).first()
                if not membership:
                    db.session.add(OrganizationMembership(
                        user_id=user.id,
                        organization_id=default_org.id,
                        access_type=role,
                        is_active=True
                    ))
        db.session.commit()
        print("  [OK] Organization memberships configured")

        # 6. Seed Sample Multi-Domain Curriculum if no Exams exist
        admin_user = created_users.get('super_admin') or User.query.filter_by(user_type='super_admin').first()
        admin_id = admin_user.id if admin_user else 1

        if Exam.query.count() == 0:
            print("  -> Populating initial starter curriculum...")
            cs_exam = Exam(
                name="Computer Science & Engineering (Core)",
                description="Comprehensive undergraduate & competitive curriculum for Computer Science.",
                organization_id=default_org.id,
                created_by_user_id=admin_id,
                is_free=True
            )
            db.session.add(cs_exam)
            db.session.commit()

            subj1 = Subject(exam_id=cs_exam.id, name="Data Structures & Algorithms", created_by_user_id=admin_id)
            subj2 = Subject(exam_id=cs_exam.id, name="Operating Systems & Architecture", created_by_user_id=admin_id)
            subj3 = Subject(exam_id=cs_exam.id, name="Computer Networks & Cybersecurity", created_by_user_id=admin_id)
            db.session.add_all([subj1, subj2, subj3])
            db.session.commit()

            # Add topics
            t1 = Topic(subject_id=subj1.id, name="Binary Trees & AVL Balancing", description="Tree traversals, balance factors, rotations.", created_by_user_id=admin_id)
            t2 = Topic(subject_id=subj2.id, name="Process Synchronization & Semaphores", description="Deadlocks, mutex locks, critical section problem.", created_by_user_id=admin_id)
            t3 = Topic(subject_id=subj3.id, name="TCP/IP Model, Subnetting & Routing Protocols", description="OSI layers, CIDR subnetting, BGP, OSPF.", created_by_user_id=admin_id)
            db.session.add_all([t1, t2, t3])
            db.session.commit()

            # Add sample question
            q1 = Question(
                topic_id=t1.id,
                exam_id=cs_exam.id,
                question_text="In an AVL tree, what is the maximum permissible difference between the heights of the left and right subtrees for any node?",
                question_type="MCQ",
                difficulty_level="Easy",
                explanation_text="An AVL tree maintains a balance factor of -1, 0, or +1 for every node. Any difference exceeding 1 triggers tree rotation.",
                created_by_user_id=admin_id
            )
            db.session.add(q1)
            db.session.commit()

            options = [
                MCQOption(question_id=q1.id, option_text="0", is_correct=False),
                MCQOption(question_id=q1.id, option_text="1", is_correct=True),
                MCQOption(question_id=q1.id, option_text="2", is_correct=False),
                MCQOption(question_id=q1.id, option_text="log(n)", is_correct=False),
            ]
            db.session.add_all(options)
            db.session.commit()
            print("  [OK] Starter curriculum & questions populated successfully")
        else:
            print(f"  [OK] Curriculum active: {Exam.query.count()} exam(s), {Subject.query.count()} subjects, {Question.query.count()} questions")

        print("=" * 70)
        print("[SUCCESS] Database setup complete! You can now log in:")
        print("-" * 70)
        print("  Role            Email                   Password")
        print("-" * 70)
        print("  Super Admin:    admin@openlms.dev       Admin@123")
        print("  Instructor:     instructor@openlms.dev  Instructor@123")
        print("  Student:        student@openlms.dev     Student@123")
        print("-" * 70)
        print("  Launch app:     python run.py")
        print("=" * 70)

if __name__ == '__main__':
    seed_open_source_environment()
