# -*- coding: utf-8 -*-
import sys
from decimal import Decimal

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"C:\Users\brred\Desktop\AI_Assistant\App\backend")

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.exam import Exam
from app.models.topic import Topic
from app.models.question import Question, MCQOption
from app.models.mock_test import MockTest, MockTestQuestion

from populate_upsc_ese_lms_master import (
    add_topic_content_item,
    create_question_in_db,
    create_or_update_mock_test,
)
from upsc_paper1_remaining_modules_data import (
    PROJECT_MANAGEMENT_HTML,
    QUALITY_AND_MAINTENANCE_HTML,
)

EXTRA_ICT_AND_PAPER1_QUESTIONS = [
    # 13 Additional High-Yield ICT Questions (bringing ICT to 25 Questions!)
    (
        70,
        "[UPSC ESE 2023 Q.24 — Uncompressed Video Frame Storage Numerical] A multimedia camera captures full-color RGB (24 bits/pixel) uncompressed video frames at a resolution of 300 × 275 pixels (or 352 × 240 CIF). What is the storage size required for a single uncompressed RGB frame of 300 × 275 pixels (using 1 KB = 1000 bytes)?",
        [
            "82.5 KB",
            "165.0 KB",
            "247.5 KB",
            "330.0 KB"
        ],
        2,
        "Medium",
        "Source: Multimedia Communications / ESE 2023 Q.24. Total pixels per frame = 300 × 275 = 82,500 pixels. At 24 bits/pixel = 3 bytes/pixel (8 bits R + 8 bits G + 8 bits B), storage per frame = 82,500 × 3 = 247,500 bytes = 247.5 KB."
    ),
    (
        70,
        "[UPSC ESE 2026 Q.38 — One-Time Pad (Vernam Cipher) XOR Numerical] In a One-Time Pad (OTP) symmetric cipher, if the 8-bit binary plaintext message is P = 10110101 and the random secret key stream is K = 11011001, what is the resulting 8-bit ciphertext C = P ⊕ K?",
        [
            "01101100",
            "10010001",
            "11111101",
            "00101100"
        ],
        0,
        "Easy",
        "Source: William Stallings (Ch. 2 Stream Ciphers & Vernam OTP — ESE 2026 Q.38). Bitwise XOR (1 ⊕ 1 = 0, 0 ⊕ 0 = 0, 1 ⊕ 0 = 1): 10110101 ⊕ 11011001 = 01101100. Decryption is identical: C ⊕ K = 01101100 ⊕ 11011001 = 10110101 = P."
    ),
    (
        70,
        "[UPSC ESE 2026 Q.34 — Russell & Norvig AI Inference] Which inference algorithm in Artificial Intelligence knowledge-based systems is 'goal-driven' (starts with the query/goal theorem to be proved and works backward through Horn clauses to find known facts that support it), and is the core engine of Prolog and MYCIN?",
        [
            "Forward Chaining (Data-driven reasoning)",
            "Backward Chaining (Goal-driven reasoning)",
            "Simulated Annealing",
            "Minimax Alpha-Beta Pruning"
        ],
        1,
        "Easy",
        "Source: Stuart Russell & Peter Norvig, Artificial Intelligence: A Modern Approach (Ch. 7 & Ch. 9 — tested in ESE 2026 Q.34). Forward chaining is data-driven (starts from known facts), whereas Backward chaining is goal-driven (starts from the goal query and chains backward)."
    ),
    (
        70,
        "[UPSC ESE 2025 Q.81–86 — Digital Forensics & Cyber Operations] In digital crime scene investigation and incident analysis, a forensic investigation that reconstructs the timeline of events, evaluates victim profile and behavioral evidence, and objectively tests competing hypotheses when initial evidence is ambiguous is known as:",
        [
            "Equivocal Forensic Analysis",
            "Steganographic Carrier Analysis",
            "Diffie-Hellman Ephemeral Exchange",
            "Smurf Broadcast Amplification"
        ],
        0,
        "Hard",
        "Source: Digital Forensics (tested in ESE 2025). Equivocal forensic analysis evaluates ambiguous physical/digital evidence objectively without jumping to premature conclusions."
    ),
    (
        70,
        "[UPSC ESE 2020 Q.89 & 2022 Q.32 — UNESCO 4 Stages of ICT in Education] According to the UNESCO framework for ICT integration in teacher education and curriculum development, what is the correct progressive sequence of the four stages of ICT adoption?",
        [
            "Applying → Emerging → Transforming → Infusing",
            "Emerging → Applying → Infusing → Transforming",
            "Infusing → Emerging → Applying → Transforming",
            "Emerging → Infusing → Applying → Transforming"
        ],
        1,
        "Medium",
        "Source: UNESCO ICT Competency Framework for Teachers (tested in ESE 2020 and 2022). The 4 progressive stages are: (1) Emerging (discovering ICT tools), (2) Applying (learning how to use ICT in subject teaching), (3) Infusing (understanding how and when to embed ICT across the curriculum), and (4) Transforming (learner-centric innovation)."
    ),
    (
        70,
        "[UPSC ESE 2019 Q.73 & Q.76 — MPEG-4 & Digital Audio Pre-Echo] In perceptual transform audio coding (such as MP3 and AAC), 'Pre-Echo' distortion occurs when a sharp percussive attack (such as castanets) follows silence within a long transform block. How do modern audio codecs mitigate Pre-Echo?",
        [
            "By switching dynamically from a long transform window to short transform windows during transient attacks (Window Switching)",
            "By reducing the sampling rate below the Nyquist rate",
            "By converting stereo channels into mono PCM",
            "By disabling Huffman lossless entropy coding"
        ],
        0,
        "Hard",
        "Source: Multimedia Signal Coding (tested in ESE 2019 Q.76). Quantization noise spreads across the entire MDCT block; switching to a shorter time window (~2.6 ms instead of ~23 ms) confines the quantization noise tightly to the transient."
    ),
    (
        70,
        "[UPSC ESE PYQ — OSI Model Layers & Network Devices] Match the networking device with the highest OSI layer at which it primarily inspects headers and makes forwarding/filtering decisions:\n1. Repeater / Passive Hub\n2. Layer-2 Ethernet Switch / Bridge\n3. Router\n4. Application Proxy Firewall / Gateway",
        [
            "1: Physical (Layer 1) | 2: Data Link (Layer 2) | 3: Network (Layer 3) | 4: Application (Layer 7)",
            "1: Data Link (Layer 2) | 2: Network (Layer 3) | 3: Transport (Layer 4) | 4: Session (Layer 5)",
            "1: Physical (Layer 1) | 2: Network (Layer 3) | 3: Data Link (Layer 2) | 4: Transport (Layer 4)",
            "1: Network (Layer 3) | 2: Data Link (Layer 2) | 3: Physical (Layer 1) | 4: Application (Layer 7)"
        ],
        0,
        "Easy",
        "Source: Forouzan / Tanenbaum Ch. 1. Repeaters/Hubs operate at Layer 1 (Physical bits); Bridges/Switches operate at Layer 2 (MAC addresses, breaking collision domains); Routers operate at Layer 3 (IP addresses, breaking broadcast domains); Gateways/Application Firewalls operate up to Layer 7."
    ),
    (
        70,
        "[UPSC ESE PYQ — IoT Application Layer Protocols: MQTT vs CoAP] Consider the following statements comparing MQTT and CoAP in Internet of Things (IoT) networks:\n1. MQTT is a publish-subscribe messaging protocol running over TCP, whereas CoAP is a request-response RESTful protocol running over UDP.\n2. CoAP natively uses GET, POST, PUT, and DELETE methods modeled after HTTP for constrained nodes.\nWhich of the statements given above is/are correct?",
        [
            "1 only",
            "2 only",
            "Both 1 and 2",
            "Neither 1 nor 2"
        ],
        2,
        "Medium",
        "Source: IoT Protocols (Module 3). MQTT (Message Queuing Telemetry Transport) uses a broker-based Publish/Subscribe architecture over TCP (port 1883/8883). CoAP (Constrained Application Protocol, RFC 7252) uses a lightweight RESTful Request/Response architecture over UDP (port 5683)."
    ),
    (
        70,
        "[UPSC ESE PYQ — Space Technology NavIC / IRNSS Constellation] India's indigenous regional satellite navigation system NavIC (Navigation with Indian Constellation) achieves regional coverage over India and a 1,500 km boundary using a constellation of 7 operational satellites located in which orbits?",
        [
            "All 7 satellites in Low Earth Orbit (LEO) at 600 km altitude",
            "3 satellites in Geostationary Orbit (GEO) and 4 satellites in inclined Geosynchronous Orbit (GSO) at ~35,786 km altitude",
            "All 7 satellites in Medium Earth Orbit (MEO) at 20,200 km altitude",
            "4 satellites in Sun-Synchronous Polar Orbit (SSPO) and 3 in Molniya Orbit"
        ],
        1,
        "Medium",
        "Source: ISRO NavIC Architecture (Module 8). Unlike GPS (24+ satellites in MEO at 20,200 km), NavIC uses 3 GEO satellites (fixed over the equator at 32.5°E, 83°E, 131.5°E) and 4 inclined GSO satellites (inclination 29° to the equatorial plane) so all 7 remain continuously visible over the Indian region."
    ),
    (
        70,
        "[UPSC ESE PYQ — Optical Fiber Numerical Aperture] A step-index optical fiber has a core refractive index of n1 = 1.50 and a cladding refractive index of n2 = 1.47. What is the approximate Numerical Aperture (NA) of the optical fiber?",
        [
            "0.15",
            "0.30",
            "0.45",
            "0.60"
        ],
        1,
        "Medium",
        "Source: Optical Fiber Communications (Module 4). NA = sqrt(n1^2 - n2^2) = sqrt((1.50 - 1.47)(1.50 + 1.47)) = sqrt(0.03 × 2.97) = sqrt(0.0891) ≈ 0.2985 ≈ 0.30."
    ),
    (
        70,
        "[UPSC ESE PYQ — HTTP Status Codes] When browsing the World Wide Web, an HTTP status code of 500 returned by a web server indicates:",
        [
            "404 Not Found (Requested resource does not exist on the server)",
            "500 Internal Server Error (Generic server-side execution failure, such as a crashed CGI script or database error)",
            "301 Moved Permanently (URL redirection)",
            "403 Forbidden (Client lacks authorization)"
        ],
        1,
        "Easy",
        "Source: RFC 9110 / Web Technologies (tested in ESE 2024). 2xx = Success (200 OK); 3xx = Redirection (301/302); 4xx = Client Error (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found); 5xx = Server Error (500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable)."
    ),
    (
        70,
        "[UPSC ESE PYQ — Cloud Computing Service Models: IaaS, PaaS, SaaS] In which Cloud Computing service model does the cloud consumer manage their own Operating Systems, Middleware, Runtime, Data, and Applications, while the Cloud Provider manages only the underlying Virtualization, Servers, Storage, and Networking?",
        [
            "Software as a Service (SaaS)",
            "Platform as a Service (PaaS)",
            "Infrastructure as a Service (IaaS)",
            "Function as a Service (FaaS)"
        ],
        2,
        "Easy",
        "Source: NIST Cloud Computing Reference Architecture (SP 800-145). In IaaS (e.g., AWS EC2, Azure VMs), the provider manages hardware + virtualization, while the user manages OS, middleware, runtime, data, and applications. In PaaS, the provider also manages OS, middleware, and runtime. In SaaS, the provider manages everything."
    ),
    (
        70,
        "[UPSC ESE PYQ — CPU Cache Average Memory Access Time (AMAT) Numerical] A processor has an L1 cache with an access time of T_cache = 2 ns and a cache hit ratio of H = 0.95 (95%). If a cache miss incurs a main memory miss penalty of 60 ns, what is the Average Memory Access Time (AMAT)?",
        [
            "3.0 ns",
            "5.0 ns",
            "8.0 ns",
            "12.0 ns"
        ],
        1,
        "Medium",
        "Source: Computer Architecture (Module 1). AMAT = T_cache + (1 - H) × Miss Penalty = 2 ns + (1 - 0.95) × 60 ns = 2 ns + (0.05 × 60 ns) = 2 + 3 = 5.0 ns."
    ),
]


def main():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(user_type='super_admin').first() or User.query.filter_by(user_type='co_admin').first() or User.query.first()
        exam = Exam.query.first()

        # Also link Project Management & Quality/Maintenance notes into Paper-II Subject 10 (Topics 52–56)
        for tid in [52, 53, 54]:
            t = db.session.get(Topic, tid)
            if t:
                add_topic_content_item(t.id, "📘 Master Compendium: Project Management, PERT/CPM, Crashing & Operations Research", "text", PROJECT_MANAGEMENT_HTML, 1)
        for tid in [55, 56]:
            t = db.session.get(Topic, tid)
            if t:
                add_topic_content_item(t.id, "📘 Master Compendium: SQC Control Charts, Process Capability, Reliability & Maintenance (BS EN 13306)", "text", QUALITY_AND_MAINTENANCE_HTML, 1)

        # Add extra ICT questions
        for tid, q_text, opts, c_idx, diff, exp in EXTRA_ICT_AND_PAPER1_QUESTIONS:
            create_question_in_db(exam.id, admin.id, tid, q_text, opts, c_idx, diff, exp)

        db.session.commit()

        # Refresh ICT Mock Test & Full Grand Mock Test so they include all 25 ICT questions!
        ict_qs = Question.query.filter_by(topic_id=70, deleted_at=None).all()
        create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: ICT Master Test (PYQs + 2027 Setter Predictions)",
            "Complete 25-Question ICT Master Test covering Computer Architecture, e-Governance (2nd ARC), IoT, 5G/Optical/Satellites, Tanenbaum & Peterson/Davie Network Numericals, Stallings Cryptography, AI Search & Cyber Laws.",
            45,
            ict_qs
        )

        all_qs = Question.query.filter_by(deleted_at=None).all()
        create_or_update_mock_test(
            exam.id, admin.id,
            "UPSC ESE 2027 Paper-I: Full-Syllabus High-Yield Grand Mock Test",
            "Comprehensive Paper-I Grand Test combining all 10 UPSC ESE General Studies & Engineering Aptitude subjects with negative marking (-1/3) and verbatim textbook explanations.",
            120,
            all_qs
        )

        db.session.commit()
        print(f"Updated LMS! Total TopicContents: {db.session.query(Topic).join(Topic.contents).count()} topics with content | Total Questions: {Question.query.count()} | ICT Questions: {len(ict_qs)} | Active Mock Tests: {MockTest.query.count()}")


if __name__ == "__main__":
    main()
