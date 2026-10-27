import os
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership, Plan
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.student_progress import StudentExam, StudentAISubscription

UPSC_ESE_SYLLABUS = {
    "1. Fluid Mechanics & Turbo Machinery": [
        "Fluid Properties, Pressure Measurement & Hydrostatics",
        "Fluid Kinematics & Dynamics (Bernoulli, Euler, Navier-Stokes)",
        "Boundary Layer Theory, Pipe Flow (Laminar & Turbulent) & Dimensional Analysis",
        "Hydraulic Turbines (Pelton, Francis, Kaplan) & Specific Speed",
        "Centrifugal & Reciprocating Pumps, Cavitation & NPSH",
        "Compressible Flow, Steam & Gas Turbines, Impulse vs Reaction Stages"
    ],
    "2. Thermodynamics & Heat Transfer": [
        "Basic Concepts, Zeroth & First Law of Thermodynamics (Open & Closed Systems)",
        "Second Law, Entropy, Availability (Exergy) & Irreversibility",
        "Properties of Pure Substances & Thermodynamic Relations (Maxwell, Clausius-Clapeyron)",
        "Conduction (Steady, Unsteady, Fins, Lumped Heat Capacity)",
        "Convection (Forced & Free, Nusselt, Reynolds, Prandtl) & Heat Exchangers (LMTD, NTU)",
        "Thermal Radiation (Blackbody, Shape Factor, Radiation Shields)"
    ],
    "3. IC Engines, Refrigeration & Air Conditioning": [
        "Air Standard Cycles (Otto, Diesel, Dual, Brayton) & Performance",
        "Combustion in SI & CI Engines, Knocking, Detonation, Supercharging & Emissions",
        "Vapour Compression Refrigeration Cycle (VCR), COP, Subcooling & Superheating",
        "Vapour Absorption Systems, Heat Pumps, Refrigerants & Gas Cycle Refrigeration",
        "Psychrometry, Psychrometric Processes, Cooling Load & Comfort Air Conditioning"
    ],
    "4. Power Plant Engineering & Renewable Energy": [
        "Rankine Cycle, Reheat, Regenerative & Binary Vapour Cycles",
        "High Pressure Boilers, Mountings, Accessories & Draught Systems",
        "Steam Condensers, Cooling Towers & Gas Turbine Power Plants",
        "Nuclear Power Plants & Hydel Power Engineering",
        "Solar Thermal, Photovoltaic, Wind, Biomass, Fuel Cells & Tidal Energy"
    ],
    "5. Theory of Machines & Mechanical Vibrations": [
        "Mechanisms, Mobility (Grubler/Kutzbach), Inversions & Velocity/Acceleration Analysis",
        "Dynamic Force Analysis, Flywheels & Turning Moment Diagrams",
        "Gears (Law of Gearing, Interference, Undercutting) & Gear Trains (Epicyclic)",
        "Governors (Watt, Porter, Proell, Hartnell) & Gyroscopic Couple",
        "Cams & Followers, Balancing of Rotating & Reciprocating Masses",
        "Free, Damped & Forced Vibrations, Transmissibility, Whirling of Shafts"
    ],
    "6. Strength of Materials (Mechanics of Solids)": [
        "Stress, Strain, Elastic Constants, Thermal Stresses & Principal Stresses (Mohr Circle)",
        "Theories of Elastic Failure (Maximum Principal Stress, Tresca, Von Mises, Haigh)",
        "Shear Force & Bending Moment Diagrams (SFD & BMD)",
        "Bending & Shear Stresses in Beams, Deflection of Beams",
        "Torsion of Circular Shafts, Combined Bending & Torsion",
        "Thin & Thick Cylinders (Lame's Theory), Columns & Struts (Euler & Rankine), Springs"
    ],
    "7. Machine Design": [
        "Static & Dynamic Loading, Fatigue Strength (Soderberg, Goodman, Gerber)",
        "Design of Riveted, Welded & Bolted Joints (Eccentric Loading)",
        "Design of Shafts, Keys & Couplings",
        "Clutches (Uniform Pressure vs Uniform Wear) & Brakes (Block, Band, Internal Expanding)",
        "Sliding Contact (Hydrodynamic Journal Bearings, Sommerfeld Number) & Rolling Contact Bearings",
        "Design of Spur & Helical Gears (Lewis Equation), Belt, Rope & Chain Drives"
    ],
    "8. Engineering Materials": [
        "Crystal Structure, Unit Cells, Miller Indices & Imperfections in Solids",
        "Phase Diagrams, Iron-Iron Carbide (Fe-Fe3C) Equilibrium Diagram & TTT Diagrams",
        "Heat Treatment Processes (Annealing, Normalizing, Hardening, Tempering, Case Hardening)",
        "Ferrous & Non-Ferrous Alloys, Steels, Cast Irons",
        "Polymers, Ceramics, Composites & Nano-materials"
    ],
    "9. Manufacturing & Production Engineering": [
        "Metal Casting (Pattern Allowances, Gating Design, Solidification Time, Casting Defects)",
        "Metal Forming (Rolling, Forging, Extrusion, Wire Drawing, Sheet Metal Operations)",
        "Metal Joining / Welding (Arc, TIG, MIG, Resistance, Weldability & Defects)",
        "Metal Cutting & Machining (Merchant Circle, Tool Life - Taylor's Equation, Tool Signature)",
        "Machine Tools (Lathe, Milling, Drilling, Grinding), NC/CNC & Non-Traditional Machining (EDM, ECM, USM, LBM)",
        "Metrology & Inspection (Limits, Fits, Tolerances, Taylor's Principle, Comparators, Surface Roughness)"
    ],
    "10. Industrial Engineering & Maintenance": [
        "Production Planning & Control (Forecasting, Scheduling, Line Balancing, MRP, JIT)",
        "Inventory Control (EOQ Models, Safety Stock, ABC Analysis)",
        "Operations Research (Linear Programming, Simplex, Transportation, Assignment, PERT/CPM, Queuing Theory)",
        "Work Study (Method Study, Time Study, Work Sampling) & Statistical Quality Control (Control Charts)",
        "Failure Analysis, Preventive/Predictive/Condition-Based Maintenance & Reliability"
    ],
    "11. Mechatronics & Robotics": [
        "Microprocessors & Microcontrollers: Architecture, 8085/8086 Basics & Interfacing",
        "Sensors, Transducers & Actuators (Piezoelectric, LVDT, Encoders, Stepper & Servo Motors)",
        "Control Systems, PLC Programming, Logic Gates & Signal Conditioning",
        "Robotics: Robot Anatomy, Laws of Robotics, DOF, Homogeneous Transformations (DH Parameters)",
        "Forward & Inverse Kinematics, Trajectory Planning & Industrial Robot Applications"
    ],
    "12. Paper-I: General Studies & Engineering Aptitude": [
        "Current Issues of National & International Importance (Social, Economic & Industrial)",
        "Engineering Aptitude (Logical Reasoning & Analytical Ability)",
        "Engineering Mathematics & Numerical Analysis",
        "General Principles of Design, Drawing & Importance of Safety",
        "Standards and Quality Practices in Production, Construction, Maintenance and Services",
        "Basics of Energy and Environment: Conservation, Pollution & Climate Change",
        "Basics of Project Management (Lifecycle, Tendering, Contract Management)",
        "Basics of Material Science and Engineering",
        "Information and Communication Technologies (ICT) Based Tools and Networking",
        "Ethics and Values in Engineering Profession"
    ]
}


def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        # 0. Ensure Default Plan
        plan = Plan.query.first()
        if not plan:
            plan = Plan(
                name='UPSC ESE Unlimited Local',
                monthly_price=0,
                max_main_coadmins=10,
                max_coadmins=50,
                max_invited_students=1000,
                max_free_exams=100,
                description='Unlimited Local Personal Plan',
                is_publicly_available=True,
                status='active'
            )
            db.session.add(plan)
            db.session.flush()

        # 1. Ensure active Organization
        org = Organization.query.filter_by(code='UPSCESE').first() or Organization.query.first()
        if not org:
            org = Organization(
                name='UPSC ESE Mechanical Hub',
                code='UPSCESE',
                plan_id=plan.id,
                subdomain='upsc-ese',
                status='active',
                is_verified=True,
                is_ai_premium=True
            )
            db.session.add(org)
            db.session.flush()
        else:
            org.status = 'active'
            org.is_verified = True
            org.is_ai_premium = True
            if not org.plan_id:
                org.plan_id = plan.id

        # 2. Ensure Admin User
        admin = User.query.filter_by(user_type='super_admin').first() or User.query.filter_by(email='admin@openlms.dev').first()
        if not admin:
            admin = User(
                email='admin@openlms.dev',
                first_name='Admin',
                last_name='User',
                user_type='main_co_admin',
                status='active'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.flush()
        else:
            admin.set_password('saibaba123')
            admin.status = 'active'
            if admin.user_type not in ['main_co_admin', 'super_admin']:
                admin.user_type = 'main_co_admin'

        # Link Admin to Organization
        admin_mem = OrganizationMembership.query.filter_by(user_id=admin.id, organization_id=org.id).first()
        if not admin_mem:
            admin_mem = OrganizationMembership(
                user_id=admin.id,
                organization_id=org.id,
                access_type='invited',
                is_active=True
            )
            db.session.add(admin_mem)
            db.session.flush()
        else:
            admin_mem.is_active = True

        # 3. Ensure Student User (student@upsc.local / saibaba123) for practicing/mock tests
        student = User.query.filter_by(email='student@upsc.local').first()
        if not student:
            student = User(
                email='student@upsc.local',
                first_name='Aspirant',
                last_name='ESE',
                user_type='student',
                status='active'
            )
            student.set_password('saibaba123')
            db.session.add(student)
            db.session.flush()
        else:
            student.set_password('saibaba123')
            student.status = 'active'

        student_mem = OrganizationMembership.query.filter_by(user_id=student.id, organization_id=org.id).first()
        if not student_mem:
            student_mem = OrganizationMembership(
                user_id=student.id,
                organization_id=org.id,
                access_type='invited',
                is_active=True
            )
            db.session.add(student_mem)
            db.session.flush()

        # Ensure Student AI Subscription
        sub = StudentAISubscription.query.filter_by(student_user_id=student.id).first()
        if not sub:
            sub = StudentAISubscription(
                student_user_id=student.id,
                organization_id=org.id,
                status='active'
            )
            db.session.add(sub)
        else:
            sub.status = 'active'

        # 4. Ensure UPSC ESE (Mechanical Engineering) Exam
        exam_name = "UPSC ESE (Mechanical Engineering)"
        exam = Exam.query.filter_by(name=exam_name).first()
        if not exam:
            exam = Exam(
                name=exam_name,
                description="UPSC Engineering Services Examination (IES) — Mechanical Engineering (Paper-I GS & Engineering Aptitude + Paper-II Mechanical Engineering)",
                organization_id=org.id,
                created_by_user_id=admin.id,
                is_free=True,
                price=0.0
            )
            db.session.add(exam)
            db.session.flush()
        else:
            exam.organization_id = org.id
            exam.is_free = True
            exam.deleted_at = None

        # Enroll Student in UPSC ESE Exam
        enrollment = StudentExam.query.filter_by(student_user_id=student.id, exam_id=exam.id).first()
        if not enrollment:
            enrollment = StudentExam(
                student_user_id=student.id,
                exam_id=exam.id,
                membership_id=student_mem.id,
                access_status='free_access'
            )
            db.session.add(enrollment)
        else:
            enrollment.access_status = 'free_access'

        # 5. Seed Official UPSC ESE Mechanical Engineering Subjects & Topics
        for subj_name, topics_list in UPSC_ESE_SYLLABUS.items():
            subj = Subject.query.filter_by(exam_id=exam.id, name=subj_name).first()
            if not subj:
                subj = Subject(
                    name=subj_name,
                    description=f"UPSC ESE syllabus module: {subj_name}",
                    exam_id=exam.id,
                    created_by_user_id=admin.id
                )
                db.session.add(subj)
                db.session.flush()

            for topic_name in topics_list:
                topic = Topic.query.filter_by(subject_id=subj.id, name=topic_name).first()
                if not topic:
                    topic = Topic(
                        name=topic_name,
                        description=f"UPSC ESE (Mechanical Engineering) topic: {topic_name}",
                        subject_id=subj.id,
                        created_by_user_id=admin.id
                    )
                    db.session.add(topic)

        db.session.commit()
        print(f"Successfully seeded '{exam.name}' (ID: {exam.id}) with {len(UPSC_ESE_SYLLABUS)} subjects!")

if __name__ == '__main__':
    seed_database()
