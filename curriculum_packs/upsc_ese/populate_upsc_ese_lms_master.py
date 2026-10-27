# -*- coding: utf-8 -*-
import os
import re
import sys
import shutil
from decimal import Decimal

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"C:\Users\brred\Desktop\AI_Assistant\App\backend")

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic, TopicContent
from app.models.question import Question, MCQOption
from app.models.mock_test import MockTest, MockTestQuestion

from upsc_paper1_remaining_modules_data import (
    COMMON_LMS_STYLE,
    PROJECT_MANAGEMENT_HTML,
    QUALITY_AND_MAINTENANCE_HTML,
    DESIGN_DRAWING_SAFETY_HTML,
    ENERGY_AND_ENVIRONMENT_HTML,
    ENGINEERING_MATHS_AND_APTITUDE_HTML,
    CURRENT_ISSUES_AND_STRATEGY_HTML,
)
from upsc_ese_question_bank_data import CURATED_UPSC_QUESTIONS

BACKEND_DIR = r"C:\Users\brred\Desktop\AI_Assistant\App\backend"
STATIC_PDF_DIR = os.path.join(BACKEND_DIR, "app", "static", "uploads", "upsc_pdfs")
os.makedirs(STATIC_PDF_DIR, exist_ok=True)

PREP_2027_DIR = r"C:\Users\brred\Desktop\preparation 2027"
BLOGGER_POSTS_DIR = os.path.join(PREP_2027_DIR, "Blogger_Posts")


def copy_pdf_to_static(src_path, dest_filename=None):
    if not os.path.exists(src_path):
        print(f"  [WARN] Missing PDF: {src_path}")
        return None
    if not dest_filename:
        dest_filename = os.path.basename(src_path)
    # sanitize spaces in filename for clean URLs
    clean_name = dest_filename.replace(" ", "_")
    dst_path = os.path.join(STATIC_PDF_DIR, clean_name)
    shutil.copy2(src_path, dst_path)
    return f"/static/uploads/upsc_pdfs/{clean_name}"


def load_blogger_html_for_lms(html_path):
    """Loads our Blogger-ready HTML and ensures headings inside .upsc-ese-article override view_topic_content.html gradient text clip."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    # Strip top HTML comment and <meta> tags
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"<meta[^>]*>", "", html, flags=re.IGNORECASE)
    # Inject -webkit-text-fill-color overrides so LMS's .content-text h1/h2/h3 gradient clip doesn't hide white banner text
    override_css = """
  .upsc-ese-article .cover-header h1 {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    background: none !important;
  }
  .upsc-ese-article .cover-header p,
  .upsc-ese-article .cover-header .module-tag {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
  }
  .upsc-ese-article h2 {
    -webkit-text-fill-color: #1e3c72 !important;
    background: none !important;
  }
  .upsc-ese-article h3 {
    -webkit-text-fill-color: #0d47a1 !important;
    background: none !important;
  }
"""
    html = html.replace("</style>", override_css + "\n</style>", 1)
    return html.strip()


def add_topic_content_item(topic_id, title, content_type, content_value, item_order):
    existing = TopicContent.query.filter_by(topic_id=topic_id, title=title).first()
    if existing:
        existing.content_type = content_type
        existing.content_value = content_value
        existing.item_order = item_order
        existing.deleted_at = None
        return existing
    item = TopicContent(
        topic_id=topic_id,
        title=title,
        content_type=content_type,
        content_value=content_value,
        item_order=item_order
    )
    db.session.add(item)
    return item


def parse_layer_card_questions(html_path, subject_tag):
    """Extracts the 25 predicted MCQs from Module 8 HTML files (.layer-card blocks)."""
    if not os.path.exists(html_path):
        return []
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Only look after "<h2>3." where the 25 predicted questions live
    sec3_idx = content.find("<h2>3.")
    if sec3_idx != -1:
        content = content[sec3_idx:]

    cards = re.findall(r'<div\s+class=["\']layer-card["\']\s*>(.*?)</div>', content, flags=re.DOTALL | re.IGNORECASE)
    parsed = []
    for card in cards:
        clean_card = card.strip()
        # Extract answer letter (a), (b), (c), or (d)
        ans_match = re.search(r"Answer:\s*\(([a-d])\)", clean_card, flags=re.IGNORECASE)
        if not ans_match:
            continue
        ans_letter = ans_match.group(1).lower()
        correct_idx = {"a": 0, "b": 1, "c": 2, "d": 3}[ans_letter]

        # Split lines
        lines = [re.sub(r"<[^>]+>", "", ln).strip() for ln in re.split(r"<br\s*/?>", clean_card) if ln.strip()]
        if len(lines) < 3:
            continue

        # Find option line(s) containing (a), (b), (c), (d)
        full_text = "\n".join(lines)
        opt_pattern = re.search(
            r"\(a\)\s*(.*?)\s*\(b\)\s*(.*?)\s*\(c\)\s*(.*?)\s*\(d\)\s*(.*?)(?:\n|&rarr;|→|Answer:|$)",
            full_text,
            flags=re.DOTALL | re.IGNORECASE
        )
        if not opt_pattern:
            continue

        opts = [
            re.sub(r"\s+", " ", opt_pattern.group(1)).strip(),
            re.sub(r"\s+", " ", opt_pattern.group(2)).strip(),
            re.sub(r"\s+", " ", opt_pattern.group(3)).strip(),
            re.sub(r"\s+", " ", opt_pattern.group(4)).strip(),
        ]

        # Question stem is everything before (a)
        q_stem = full_text[:opt_pattern.start()].strip()
        q_stem = re.sub(r"&mdash;", "—", q_stem)
        q_stem = re.sub(r"&ndash;", "–", q_stem)
        q_stem = re.sub(r"&ldquo;|&rdquo;", '"', q_stem)
        q_stem = re.sub(r"&amp;", "&", q_stem)
        q_stem = re.sub(r"&ne;", "≠", q_stem)
        q_stem = re.sub(r"&le;", "≤", q_stem)
        q_stem = re.sub(r"&ge;", "≥", q_stem)
        q_stem = re.sub(r"&times;", "×", q_stem)
        q_stem = re.sub(r"&minus;", "−", q_stem)
        q_stem = re.sub(r"&deg;", "°", q_stem)
        q_stem = re.sub(r"&radic;", "√", q_stem)
        q_stem = re.sub(r"&alpha;", "α", q_stem)
        q_stem = re.sub(r"&beta;", "β", q_stem)
        q_stem = re.sub(r"&gamma;", "γ", q_stem)
        q_stem = re.sub(r"&sigma;", "σ", q_stem)
        q_stem = re.sub(r"&tau;", "τ", q_stem)
        q_stem = re.sub(r"&varepsilon;", "ε", q_stem)
        q_stem = re.sub(r"&phi;", "φ", q_stem)
        q_stem = re.sub(r"&lambda;", "λ", q_stem)
        q_stem = re.sub(r"&rho;", "ρ", q_stem)

        def decode_entities(s):
            reps = {
                "&mdash;": "—", "&ndash;": "–", "&ldquo;": '"', "&rdquo;": '"',
                "&amp;": "&", "&ne;": "≠", "&le;": "≤", "&ge;": "≥", "&lt;": "<", "&gt;": ">",
                "&times;": "×", "&minus;": "−", "&deg;": "°", "&radic;": "√",
                "&alpha;": "α", "&beta;": "β", "&gamma;": "γ", "&sigma;": "σ",
                "&tau;": "τ", "&varepsilon;": "ε", "&phi;": "φ", "&lambda;": "λ",
                "&rho;": "ρ", "&mu;": "μ", "&pi;": "π", "&Delta;": "Δ", "&rArr;": "⇒",
                "&rarr;": "→", "&harr;": "↔", "&parallel;": "∥"
            }
            for k, v in reps.items():
                s = s.replace(k, v)
            return s

        q_stem = decode_entities(q_stem)
        opts = [decode_entities(o) for o in opts]
        exp_line = decode_entities(lines[-1])

        parsed.append((subject_tag, q_stem, opts, correct_idx, "Medium", exp_line))

    return parsed


def create_question_in_db(exam_id, admin_id, topic_id, q_text, options_list, correct_idx, difficulty, explanation):
    existing = Question.query.filter_by(topic_id=topic_id, question_text=q_text).first()
    if existing:
        return existing

    q = Question(
        exam_id=exam_id,
        topic_id=topic_id,
        question_type="MCQ",
        question_text=q_text,
        explanation_text=explanation,
        difficulty_level=difficulty,
        created_by_user_id=admin_id,
        visibility="public"
    )
    db.session.add(q)
    db.session.flush()

    for idx, opt_str in enumerate(options_list):
        opt = MCQOption(
            question_id=q.id,
            option_text=opt_str,
            is_correct=(idx == correct_idx)
        )
        db.session.add(opt)

    return q


def create_or_update_mock_test(exam_id, admin_id, title, description, duration_mins, question_objs):
    mt = MockTest.query.filter_by(exam_id=exam_id, title=title).first()
    marks_per_q = Decimal("2.00")
    total_marks = marks_per_q * len(question_objs)
    passing_marks = (total_marks * Decimal("0.50")).quantize(Decimal("0.01"))

    if not mt:
        mt = MockTest(
            exam_id=exam_id,
            title=title,
            description=description,
            duration_minutes=duration_mins,
            total_marks=total_marks,
            passing_marks=passing_marks,
            status="active",
            default_marks_per_question=marks_per_q,
            negative_marking_enabled=True,
            negative_marking_ratio=Decimal("0.33"),
            is_live_test=False,
            created_by_user_id=admin_id
        )
        db.session.add(mt)
        db.session.flush()
    else:
        mt.description = description
        mt.duration_minutes = duration_mins
        mt.total_marks = total_marks
        mt.passing_marks = passing_marks
        mt.status = "active"
        mt.default_marks_per_question = marks_per_q
        mt.negative_marking_enabled = True
        mt.negative_marking_ratio = Decimal("0.33")
        mt.deleted_at = None
        MockTestQuestion.query.filter_by(mock_test_id=mt.id).delete()
        db.session.flush()

    for order_idx, q_obj in enumerate(question_objs, start=1):
        mtq = MockTestQuestion(
            mock_test_id=mt.id,
            question_id=q_obj.id,
            question_order=order_idx,
            marks=marks_per_q
        )
        db.session.add(mtq)

    return mt


def main():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(user_type='super_admin').first() or User.query.filter_by(user_type='co_admin').first() or User.query.first()
        exam = Exam.query.first()
        if not admin or not exam:
            raise RuntimeError("Run seed_upsc_ese.py first so Admin and Exam exist!")

        print(f"Populating LMS for Exam '{exam.name}' (ID: {exam.id}) as Admin '{admin.email}'...")

        # Map key topics by ID / Name
        topics_all = Topic.query.all()
        topic_by_name = {t.name: t for t in topics_all}

        t_current = Topic.query.get(62)
        t_aptitude = Topic.query.get(63)
        t_maths = Topic.query.get(64)
        t_design = Topic.query.get(65)
        t_quality = Topic.query.get(66)
        t_energy = Topic.query.get(67)
        t_proj_mgmt = Topic.query.get(68)
        t_matsci = Topic.query.get(69)
        t_ict = Topic.query.get(70)
        t_ethics = Topic.query.get(71)

        # Paper-II Engineering Materials topics (41..45)
        t_mat_crystal = Topic.query.get(41)
        t_mat_phase = Topic.query.get(42)
        t_mat_heat = Topic.query.get(43)
        t_mat_alloys = Topic.query.get(44)
        t_mat_poly = Topic.query.get(45)

        # ====================================================================
        # 1. COPY ALL MASTER & MODULE PDFS TO app/static/uploads/upsc_pdfs/
        # ====================================================================
        print("\n--- Step 1: Copying Master & Module PDFs into LMS static storage ---")
        ict_master_pdf_url = copy_pdf_to_static(os.path.join(PREP_2027_DIR, "UPSC_ESE_ICT_2027_Master_Complete_Compendium.pdf"))
        ethics_master_pdf_url = copy_pdf_to_static(os.path.join(PREP_2027_DIR, "UPSC_ESE_Ethics_2027_Master_Complete_Compendium.pdf"))
        matsci_master_pdf_url = copy_pdf_to_static(os.path.join(PREP_2027_DIR, "UPSC_ESE_Material_Science_2027_Master_Complete_Compendium.pdf"))
        drawing_pdf_url = copy_pdf_to_static(os.path.join(PREP_2027_DIR, "engineering drawing.pdf"), "UPSC_ESE_Engineering_Drawing_Notes.pdf")
        pyq_2025_gs_url = copy_pdf_to_static(os.path.join(PREP_2027_DIR, "QP-ESEP-25-GENERAL-STUDIES-AND-ENGINEERING-APTITUDE-P-I-090625.pdf"), "UPSC_ESE_2025_Paper_1_Official_Question_Paper.pdf")
        pyq_2026_gs_url = copy_pdf_to_static(os.path.join(PREP_2027_DIR, "2012purl_gs-ese-2026-exam-solution-updated.pdf"), "UPSC_ESE_2026_Paper_1_Detailed_Solutions.pdf")

        # ====================================================================
        # 2. POPULATE TOPIC 70: ICT (8 Interactive HTML Modules + Master & Module PDFs)
        # ====================================================================
        print("\n--- Step 2: Populating Topic 70 (ICT) with 8 Interactive Modules + PDFs ---")
        ict_modules_meta = [
            ("📘 Module 1 (Interactive Notes): Computer Hardware, I/O Printers, Memory Hierarchy & OS Architecture", "ICT_Module_01_Blogger_Ready.html", "module_01_hardware_printers_storage.pdf"),
            ("📘 Module 2 (Interactive Notes): Digital India, e-Governance, 2nd ARC Report, NeGP & Education ICT", "ICT_Module_02_Blogger_Ready.html", "module_02_digital_india_egovernance.pdf"),
            ("📘 Module 3 (Interactive Notes): Internet of Things (IoT), Smart Sensors, RFID, ZigBee, LoRaWAN & Cloud", "ICT_Module_03_Blogger_Ready.html", "module_03_iot_sensors_wireless.pdf"),
            ("📘 Module 4 (Interactive Notes): Telecommunications, 1G–5G/6G Cellular Evolution, Optical Fiber & Satellites", "ICT_Module_04_Blogger_Ready.html", "module_04_telecom_cellular_satellite.pdf"),
            ("📘 Module 5 (Interactive Notes): Computer Networking, OSI vs TCP/IP, IPv4/IPv6, Routing & ALOHA Numericals", "ICT_Module_05_Blogger_Ready.html", "module_05_computer_networking_osi_devices.pdf"),
            ("📘 Module 6 (Interactive Notes): Cybersecurity, Cryptography (RSA/AES/DES/DSA), Digital Forensics & IT Act", "ICT_Module_06_Blogger_Ready.html", "module_06_cybersecurity_threats_dpdp.pdf"),
            ("📘 Module 7 (Interactive Notes): Artificial Intelligence (AI Search & Logic), Quantum, Supercomputers & Blockchain", "ICT_Module_07_Blogger_Ready.html", "module_07_emerging_tech_ai_supercomputing_quantum_blockchain.pdf"),
            ("📘 Module 8 (Interactive Notes): Space Technology, LEO/MEO/GEO Orbits, PSLV/GSLV/LVM3, NavIC & ISRO Missions", "ICT_Module_08_Blogger_Ready.html", "module_08_space_technology_orbits_missions.pdf"),
        ]
        order = 1
        add_topic_content_item(t_ict.id, "📕 FULL BOOK PDF (96 Pages): UPSC ESE 2027 ICT Master Complete Compendium", "pdf_link", ict_master_pdf_url, order)
        for mod_title, blogger_file, mod_pdf_name in ict_modules_meta:
            order += 1
            html_path = os.path.join(BLOGGER_POSTS_DIR, "01_ICT_Modules", blogger_file)
            html_val = load_blogger_html_for_lms(html_path)
            add_topic_content_item(t_ict.id, mod_title, "text", html_val, order)
            # Also copy individual module PDF
            mod_pdf_src = os.path.join(r"C:\Users\brred\.gemini\antigravity\scratch\upsc_ict_book\modules", mod_pdf_name)
            mod_pdf_url = copy_pdf_to_static(mod_pdf_src, f"ICT_{mod_pdf_name}")
            if mod_pdf_url:
                order += 1
                add_topic_content_item(t_ict.id, mod_title.replace("📘", "📄").replace("(Interactive Notes)", "(Printable PDF)"), "pdf_link", mod_pdf_url, order)

        # ====================================================================
        # 3. POPULATE TOPIC 71: ETHICS (8 Interactive HTML Modules + Master & Module PDFs)
        # ====================================================================
        print("\n--- Step 3: Populating Topic 71 (Ethics & Values) with 8 Interactive Modules + PDFs ---")
        ethics_modules_meta = [
            ("📘 Module 1 (Interactive Notes): Foundations of Engineering Ethics, 3 Inquiries, Kohlberg vs Gilligan & Values", "Ethics_Module_01_Blogger_Ready.html", "module_01_foundations_moral_inquiry_philosophers.pdf"),
            ("📘 Module 2 (Interactive Notes): Ethical Theories — Act vs Rule Utilitarianism, Kant, Ross, Rights & Virtue Ethics", "Ethics_Module_02_Blogger_Ready.html", "module_02_ethical_theories_utilitarianism_deontology_virtue.pdf"),
            ("📘 Module 3 (Interactive Notes): AICTE Universal Human Values (UHV) — Self-Exploration, Sukh, 9 Feelings & 4 Orders", "Ethics_Module_03_Blogger_Ready.html", "module_03_aicte_universal_human_values_uhv.pdf"),
            ("📘 Module 4 (Interactive Notes): Professionalism, 3 Identity Stages, NSPE Canons, Hammurabi & Davis's 8 Moral Tests", "Ethics_Module_04_Blogger_Ready.html", "module_04_professionalism_codes_moral_tests.pdf"),
            ("📘 Module 5 (Interactive Notes): Engineering as Social Experimentation, Safety/Risk Analysis, Liability & Disasters", "Ethics_Module_05_Blogger_Ready.html", "module_05_engineering_experimentation_safety_risk_liability.pdf"),
            ("📘 Module 6 (Interactive Notes): Workplace Responsibilities, Conflict of Interest, Loyalty, Whistleblowing & IPR", "Ethics_Module_06_Blogger_Ready.html", "module_06_workplace_responsibilities_rights_whistleblowing_ipr.pdf"),
            ("📘 Module 7 (Interactive Notes): Global Issues, MNCs, Carroll's CSR Pyramid, Environmental Ethics (CERES/EWB) & Bioethics", "Ethics_Module_07_Blogger_Ready.html", "module_07_global_issues_csr_environmental_computer_ethics.pdf"),
            ("📘 Module 8 (Interactive Notes): Complete 10-Year Ethics PYQ Decoder (2017–2026) & 25 Predicted Questions for 2027", "Ethics_Module_08_Blogger_Ready.html", "module_08_10year_pyq_bank_and_2027_predicted_questions.pdf"),
        ]
        order = 1
        add_topic_content_item(t_ethics.id, "📕 FULL BOOK PDF (74 Pages): UPSC ESE 2027 Ethics & Human Values Master Compendium", "pdf_link", ethics_master_pdf_url, order)
        for mod_title, blogger_file, mod_pdf_name in ethics_modules_meta:
            order += 1
            html_path = os.path.join(BLOGGER_POSTS_DIR, "02_Ethics_Modules", blogger_file)
            html_val = load_blogger_html_for_lms(html_path)
            add_topic_content_item(t_ethics.id, mod_title, "text", html_val, order)
            mod_pdf_src = os.path.join(r"C:\Users\brred\.gemini\antigravity\scratch\upsc_ethics_book\modules", mod_pdf_name)
            mod_pdf_url = copy_pdf_to_static(mod_pdf_src, f"Ethics_{mod_pdf_name}")
            if mod_pdf_url:
                order += 1
                add_topic_content_item(t_ethics.id, mod_title.replace("📘", "📄").replace("(Interactive Notes)", "(Printable PDF)"), "pdf_link", mod_pdf_url, order)

        # ====================================================================
        # 4. POPULATE TOPIC 69 & SUBJECT 8 (TOPICS 41–45): MATERIAL SCIENCE
        # ====================================================================
        print("\n--- Step 4: Populating Topic 69 & Paper-II Subject 8 (Material Science) ---")
        matsci_modules_meta = [
            ("📘 Module 1 (Interactive Notes): Atomic Structure, Interatomic Bonding, Lennard-Jones & Pauling Radius Ratios", "MatSci_Module_01_Blogger_Ready.html", "module_01_atomic_structure_chemical_bonding_coordination.pdf", [t_mat_crystal]),
            ("📘 Module 2 (Interactive Notes): Crystallography, 7 Crystal Systems, SC/BCC/FCC/HCP, Density Numericals & Miller Indices", "MatSci_Module_02_Blogger_Ready.html", "module_02_crystallography_crystal_systems_density_miller.pdf", [t_mat_crystal]),
            ("📘 Module 3 (Interactive Notes): Crystal Imperfections, Schottky vs Frenkel, Hume-Rothery Rules, Dislocations & Diffusion", "MatSci_Module_03_Blogger_Ready.html", "module_03_crystal_imperfections_dislocations_diffusion.pdf", [t_mat_crystal]),
            ("📘 Module 4 (Interactive Notes): Mechanical Properties, Stress-Strain, Hardness, Strengthening, Griffith Fracture & Creep", "MatSci_Module_04_Blogger_Ready.html", "module_04_mechanical_properties_slip_strengthening_fracture.pdf", [t_mat_heat]),
            ("📘 Module 5 (Interactive Notes): Phase Diagrams, Lever Rule, Fe-Fe3C System, TTT Curves, Heat Treatment & Alloys", "MatSci_Module_05_Blogger_Ready.html", "module_05_phase_diagrams_iron_carbon_heat_treatment_alloys.pdf", [t_mat_phase, t_mat_heat, t_mat_alloys]),
            ("📘 Module 6 (Interactive Notes): Polymers (Vulcanization Numericals, Tacticity, Tg), Ceramics, Refractories & Composites", "MatSci_Module_06_Blogger_Ready.html", "module_06_polymers_ceramics_composites.pdf", [t_mat_poly]),
            ("📘 Module 7 (Interactive Notes): Electrical, Semiconductors, Hall Effect, Dielectrics, Magnets, Superconductors & Qubits", "MatSci_Module_07_Blogger_Ready.html", "module_07_electrical_semiconductor_magnetic_quantum_materials.pdf", [t_mat_poly]),
            ("📘 Module 8 (Interactive Notes): 10-Year Material Science PYQ Decoder (2017–2026), Callister Worked Numericals & 25 MCQs", "MatSci_Module_08_Blogger_Ready.html", "module_08_10year_pyq_bank_and_2027_predicted_questions.pdf", [t_mat_alloys]),
        ]
        order = 1
        add_topic_content_item(t_matsci.id, "📕 FULL BOOK PDF (99 Pages): UPSC ESE 2027 Material Science Master Compendium", "pdf_link", matsci_master_pdf_url, order)
        for mod_title, blogger_file, mod_pdf_name, extra_topics in matsci_modules_meta:
            order += 1
            html_path = os.path.join(BLOGGER_POSTS_DIR, "03_Material_Science_Modules", blogger_file)
            html_val = load_blogger_html_for_lms(html_path)
            add_topic_content_item(t_matsci.id, mod_title, "text", html_val, order)
            mod_pdf_src = os.path.join(r"C:\Users\brred\.gemini\antigravity\scratch\upsc_matsci_book\modules", mod_pdf_name)
            mod_pdf_url = copy_pdf_to_static(mod_pdf_src, f"MatSci_{mod_pdf_name}")
            if mod_pdf_url:
                order += 1
                add_topic_content_item(t_matsci.id, mod_title.replace("📘", "📄").replace("(Interactive Notes)", "(Printable PDF)"), "pdf_link", mod_pdf_url, order)

            # Also link to Paper-II Subject 8 topics!
            for et in extra_topics:
                if et:
                    add_topic_content_item(et.id, mod_title, "text", html_val, 1)
                    if mod_pdf_url:
                        add_topic_content_item(et.id, mod_title.replace("📘", "📄").replace("(Interactive Notes)", "(Printable PDF)"), "pdf_link", mod_pdf_url, 2)
                    add_topic_content_item(et.id, "📕 FULL BOOK PDF (99 Pages): Material Science Master Compendium", "pdf_link", matsci_master_pdf_url, 3)

        # ====================================================================
        # 5. POPULATE REMAINING PAPER-I TOPICS (TOPICS 62, 63, 64, 65, 66, 67, 68)
        # ====================================================================
        print("\n--- Step 5: Populating Topics 62–68 with Master Compendium Notes & PDFs ---")
        # Topic 68: Project Management
        add_topic_content_item(t_proj_mgmt.id, "📘 Master Compendium: Basics of Project Management (Prasanna Chandra + Gray & Larson Synthesis)", "text", PROJECT_MANAGEMENT_HTML, 1)

        # Topic 66: Standards & Quality Practices
        add_topic_content_item(t_quality.id, "📘 Master Compendium: Standards, Quality Practices, SQC, Reliability & BS EN 13306 Maintenance", "text", QUALITY_AND_MAINTENANCE_HTML, 1)

        # Topic 65: Design, Drawing & Safety
        add_topic_content_item(t_design.id, "📘 Master Compendium: Engineering Drawing (N.D. Bhatt), Design Principles & Industrial Safety", "text", DESIGN_DRAWING_SAFETY_HTML, 1)
        if drawing_pdf_url:
            add_topic_content_item(t_design.id, "📕 Complete Engineering Drawing Notes PDF", "pdf_link", drawing_pdf_url, 2)

        # Topic 67: Energy & Environment
        add_topic_content_item(t_energy.id, "📘 Master Compendium: Energy Resources, Ecology, Plume Behavior, BOD/EIA & Climate Treaties", "text", ENERGY_AND_ENVIRONMENT_HTML, 1)

        # Topic 64: Engineering Mathematics
        add_topic_content_item(t_maths.id, "📘 Master Compendium: Engineering Mathematics & Numerical Analysis (Grewal + Jain, Iyengar & Jain)", "text", ENGINEERING_MATHS_AND_APTITUDE_HTML, 1)

        # Topic 63: Engineering Aptitude
        add_topic_content_item(t_aptitude.id, "📘 Master Compendium: Engineering Aptitude, Aufmann Apportionment/Voting Theory & Analytical Reasoning", "text", ENGINEERING_MATHS_AND_APTITUDE_HTML, 1)

        # Topic 62: Current Issues & Master Strategy
        add_topic_content_item(t_current.id, "📘 Master Compendium: National Engineering Missions (Green Hydrogen, Quantum, IndiaAI, Semicon) & 10-Subject Blueprint", "text", CURRENT_ISSUES_AND_STRATEGY_HTML, 1)
        if pyq_2026_gs_url:
            add_topic_content_item(t_current.id, "📕 Official UPSC ESE 2026 Paper-I Solved Question Paper PDF", "pdf_link", pyq_2026_gs_url, 2)
        if pyq_2025_gs_url:
            add_topic_content_item(t_current.id, "📕 Official UPSC ESE 2025 Paper-I Question Paper PDF", "pdf_link", pyq_2025_gs_url, 3)

        db.session.commit()

        # ====================================================================
        # 6. POPULATE QUESTIONS (CURATED + MODULE 8 PREDICTED BANKS)
        # ====================================================================
        print("\n--- Step 6: Populating Authentic UPSC ESE Questions into Question Bank ---")
        ethics_mod8_path = r"C:\Users\brred\.gemini\antigravity\scratch\upsc_ethics_book\modules\module_08_10year_pyq_bank_and_2027_predicted_questions.html"
        matsci_mod8_path = r"C:\Users\brred\.gemini\antigravity\scratch\upsc_matsci_book\modules\module_08_10year_pyq_bank_and_2027_predicted_questions.html"

        ethics_parsed_qs = parse_layer_card_questions(ethics_mod8_path, "ETHICS")
        matsci_parsed_qs = parse_layer_card_questions(matsci_mod8_path, "MATSCI")
        print(f"  Parsed {len(ethics_parsed_qs)} predicted MCQs from Ethics Module 8 and {len(matsci_parsed_qs)} predicted MCQs from Material Science Module 8.")

        all_question_records = CURATED_UPSC_QUESTIONS + ethics_parsed_qs + matsci_parsed_qs

        topic_map_by_tag = {
            "ICT": t_ict.id,
            "ETHICS": t_ethics.id,
            "MATSCI": t_matsci.id,
            "PROJ_MGMT": t_proj_mgmt.id,
            "QUALITY": t_quality.id,
            "DESIGN_DRAWING": t_design.id,
            "ENERGY_ENV": t_energy.id,
            "MATHS": t_maths.id,
            "APTITUDE": t_aptitude.id,
            "CURRENT": t_current.id,
        }

        questions_by_tag = {k: [] for k in topic_map_by_tag}

        for tag, q_text, opts, c_idx, diff, exp in all_question_records:
            tid = topic_map_by_tag.get(tag, t_current.id)
            q_obj = create_question_in_db(exam.id, admin.id, tid, q_text, opts, c_idx, diff, exp)
            questions_by_tag[tag].append(q_obj)

        db.session.commit()

        # ====================================================================
        # 7. CREATE ACTIVE MOCK TESTS FOR IMMEDIATE PRACTICE
        # ====================================================================
        print("\n--- Step 7: Building Active UPSC ESE 2027 Mock Tests ---")
        mt1 = create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: ICT Master Test (PYQs + 2027 Setter Predictions)",
            "Covers Tanenbaum Network Topologies & ALOHA Numericals, Peterson/Davie BDP/RTT, Stallings RSA/AES/DSA Cryptography, Russell & Norvig AI Search, Silberschatz OS Device-Status Table, Reynolds Cyber Laws & 2nd ARC e-Governance.",
            25,
            questions_by_tag["ICT"]
        )
        mt2 = create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: Ethics & Universal Human Values (UHV) Master Test",
            "Covers AICTE Universal Human Values (R.R. Gaur, Sangal & Bagaria — 9 Feelings, Self vs Body, Sukh vs Samriddhi), Martin & Schinzinger Ethical Theories, Kohlberg vs Gilligan, Michael Davis's 8 Moral Tests, Safety/Risk & CSR.",
            45,
            questions_by_tag["ETHICS"]
        )
        mt3 = create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: Material Science & Callister Numericals Master Test",
            "Covers William D. Callister Jr. & V. Raghavan: 7 Crystal Systems, Theoretical Density, Schottky/Frenkel, Dislocations, ASTM Grain Size, Diffusion, Stress-Strain, Griffith Crack Length, Lever Rule, Fe-Fe3C, Polymers & Electronic/Magnetic Materials.",
            45,
            questions_by_tag["MATSCI"]
        )
        mt4 = create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: Project Management, Quality, Design & Environment Test",
            "Covers Earned Value Management (CPI/SPI/EAC), PERT/CPM, Process Capability (Cp/Cpk), Taguchi Loss, BS EN 13306 Maintenance, N.D. Bhatt Engineering Drawing, Heinrich Safety Pyramid, Plume Behavior, BOD5 & Numerical/Aptitude.",
            40,
            questions_by_tag["PROJ_MGMT"] + questions_by_tag["QUALITY"] + questions_by_tag["DESIGN_DRAWING"] + questions_by_tag["ENERGY_ENV"] + questions_by_tag["MATHS"] + questions_by_tag["APTITUDE"] + questions_by_tag["CURRENT"]
        )

        # Full Grand Mock Test combining all questions
        all_qs_flat = []
        for k in ["CURRENT", "APTITUDE", "MATHS", "DESIGN_DRAWING", "QUALITY", "ENERGY_ENV", "PROJ_MGMT", "MATSCI", "ICT", "ETHICS"]:
            all_qs_flat.extend(questions_by_tag[k])

        mt5 = create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: Full-Syllabus High-Yield Grand Mock Test",
            "Comprehensive Paper-I Grand Test combining all 10 UPSC ESE General Studies & Engineering Aptitude subjects with negative marking (-1/3) and verbatim textbook explanations.",
            120,
            all_qs_flat
        )

        db.session.commit()

        print("\n==================================================================")
        print("LMS POPULATION COMPLETE!")
        print(f"  Total TopicContent items in DB : {TopicContent.query.count()}")
        print(f"  Total Questions in DB          : {Question.query.count()}")
        print(f"  Total MCQOptions in DB         : {MCQOption.query.count()}")
        print(f"  Total Active MockTests in DB   : {MockTest.query.count()}")
        print("==================================================================")


if __name__ == "__main__":
    main()
