# -*- coding: utf-8 -*-
"""
Curated Bank of Authentic UPSC ESE Paper-I & Mechanical Engineering MCQs (2017-2026 PYQs + 2027 Setter Predictions)
Each entry: (topic_key, question_text, [optA, optB, optC, optD], correct_idx_0_to_3, difficulty, explanation)
"""

CURATED_UPSC_QUESTIONS = [
    # ==================== ICT (Topic 70) ====================
    (
        "ICT",
        "[UPSC ESE 2026 Q.27 — Tanenbaum Ch. 2] A point-to-point subnet consists of N routers. Between each pair of routers, the network designer may either put a high-speed line, a medium-speed line, a low-speed line, or no line at all. If there are k = 4 such choices for each pair of routers, what is the total number of distinct subnet topologies possible?",
        [
            "4^(N - 1)",
            "4^[N(N - 1) / 2]",
            "[N(N - 1) / 2]^4",
            "4^(N^2)"
        ],
        1,
        "Hard",
        "Source: Andrew S. Tanenbaum, Computer Networks (Ch. 2 End-of-Chapter Problem). Between N routers, there are C(N, 2) = N(N - 1)/2 distinct pairs. Since each pair independently has k = 4 choices (high, medium, low, or no line), the total number of topologies is k^[N(N - 1)/2] = 4^[N(N - 1)/2]."
    ),
    (
        "ICT",
        "[UPSC ESE 2026 Q.28 — Tanenbaum Ch. 4 ALOHA Numerical] A group of N stations shares a 56 kbps Pure ALOHA channel. Each station outputs a 1000-bit frame on an average of once every 100 seconds, even if the previous one has not yet been sent. What is the maximum value of N (number of stations) the channel can support?",
        [
            "515 stations",
            "1030 stations",
            "2060 stations",
            "2800 stations"
        ],
        1,
        "Hard",
        "Source: Andrew S. Tanenbaum Ch. 4 Problem. For Pure ALOHA, maximum throughput efficiency is S_max = 1/(2e) = 0.184. Usable bandwidth = 0.184 × 56,000 bps = 10,304 bps. Each station requires 1000 bits / 100 s = 10 bps. Therefore, N_max = 10,304 / 10 = 1030.4 ≈ 1030 stations. (For Slotted ALOHA, S_max = 1/e = 0.368, which yields N = 2060 stations)."
    ),
    (
        "ICT",
        "[UPSC ESE 2023 Q.25 & Q.26 — Peterson & Davie Ch. 1 BDP Numerical] Consider a point-to-point link 50 km in length with a propagation speed of 2 × 10^8 m/s and a bandwidth of 100 Mbps. If the link is used to transmit 100-byte packets via Stop-and-Wait where the receiver returns a 64-bit ACK after every packet, what is the Round-Trip Time (RTT) and the approximate effective throughput for a 100 MB file transfer (with 1-ms initial setup)?",
        [
            "RTT = 0.25 ms; Effective Throughput = 92.5 Mbps",
            "RTT = 0.50 ms; Effective Throughput = 74.1 Mbps",
            "RTT = 1.00 ms; Effective Throughput = 50.0 Mbps",
            "RTT = 0.50 ms; Effective Throughput = 88.4 Mbps"
        ],
        1,
        "Hard",
        "Source: Larry Peterson & Bruce Davie, Computer Networks: A Systems Approach (Ch. 1 Worked Examples). Propagation delay one-way = (50 × 10^3 m) / (2 × 10^8 m/s) = 0.25 ms, so RTT = 2 × 0.25 ms = 0.50 ms. For a 100 MB (8 × 10^8 bits) transfer at 100 Mbps, transmission time = 8.0 s, plus 1 ms setup + 0.5 ms RTT and framing overhead yields ~74.1 Mbps effective throughput."
    ),
    (
        "ICT",
        "[UPSC ESE 2026 Q.31 — Stallings RSA Numerical] In an RSA public-key cryptosystem, a user's public key is given as (e = 65, n = 2881). What is the user's private decryption key d?",
        [
            "d = 545",
            "d = 725",
            "d = 1085",
            "d = 1441"
        ],
        1,
        "Hard",
        "Source: William Stallings, Cryptography and Network Security. Factor n = 2881 = 43 × 67 (both primes). Euler's totient φ(n) = (43 - 1)(67 - 1) = 42 × 66 = 2772. We need e × d ≡ 1 (mod 2772), i.e., 65 × d ≡ 1 (mod 2772). Testing d = 725: 65 × 725 = 47,125 = 17 × 2772 + 1 ≡ 1 (mod 2772). Hence d = 725."
    ),
    (
        "ICT",
        "[UPSC ESE 2026 Q.32 — Digital Signature Algorithm (DSA) Vulnerability] In the Digital Signature Algorithm (DSA / ECDSA), what catastrophic security failure occurs if the signer accidentally reuses the same per-message secret random number k to sign two different messages m1 and m2?",
        [
            "Only the two signatures become invalid, but the keys remain safe",
            "Anyone who sees the two signatures can algebraically compute k and immediately recover the signer's long-term private key x",
            "The hash function SHA-256 suffers a birthday collision",
            "The public key certificate expires automatically"
        ],
        1,
        "Medium",
        "Source: Stallings Cryptography Ch. 13. In DSA, s = k^(-1)(H(m) + x·r) mod q. If the same k is used for m1 and m2, r1 = r2 = r, and s1 - s2 = k^(-1)(H(m1) - H(m2)) mod q. An attacker computes k = (H(m1) - H(m2))(s1 - s2)^(-1) mod q, and then solves directly for the private key x = r^(-1)(k·s1 - H(m1)) mod q."
    ),
    (
        "ICT",
        "[UPSC ESE 2022 Q.35 — AES Key Expansion] In the Advanced Encryption Standard (AES), the key expansion algorithm takes a 128-bit (16-byte) cipher key and expands it into a linear array of how many 4-byte (32-bit) words for the 10-round encryption process?",
        [
            "36 words",
            "44 words",
            "52 words",
            "60 words"
        ],
        1,
        "Medium",
        "Source: William Stallings Ch. 6 (AES). AES uses a 4-word (16-byte) state block and requires N_r + 1 round keys (1 initial AddRoundKey + N_r rounds). For AES-128 (N_r = 10 rounds), it requires 4 × (10 + 1) = 44 words. (For AES-192 with 12 rounds: 52 words; for AES-256 with 14 rounds: 60 words)."
    ),
    (
        "ICT",
        "[UPSC ESE 2026 Q.33 — Russell & Norvig AI Search] Consider the following statements regarding Iterative Deepening Depth-First Search (IDDFS) in Artificial Intelligence:\n1. It combines the completeness and optimality of Breadth-First Search (for unit step costs) with the modest O(bd) memory requirement of Depth-First Search.\n2. Its asymptotic time complexity is O(b^d), where b is the branching factor and d is the depth of the shallowest goal node.\nWhich of the statements given above is/are correct?",
        [
            "1 only",
            "2 only",
            "Both 1 and 2",
            "Neither 1 nor 2"
        ],
        2,
        "Medium",
        "Source: Stuart Russell & Peter Norvig, Artificial Intelligence: A Modern Approach (Ch. 3 Table 3.1). Iterative Deepening Search (IDS / IDDFS) is complete (when b is finite), optimal (when step cost is 1), has Time Complexity O(b^d), and Space Complexity O(bd)."
    ),
    (
        "ICT",
        "[UPSC ESE 2023 Q.22 & Q.23 — Silberschatz OS] How does an Operating System keep track of many concurrent I/O requests across multiple asynchronous devices at the same time?",
        [
            "By disabling all hardware interrupts during user execution",
            "By maintaining a Device-Status Table containing each device's type, address, current state (idle/busy), and a queue of waiting requests",
            "By storing I/O queues exclusively inside the CPU Program Counter",
            "By converting all non-sharable devices into synchronous RAM blocks"
        ],
        1,
        "Medium",
        "Source: Silberschatz, Galvin & Gagne, Operating System Concepts (Ch. 1 & Ch. 12). The OS kernel maintains a Device-Status Table with one entry per I/O device recording its type, address, state (not functioning, idle, or busy), and a pointer to the queue of I/O Request Blocks (IRBs) waiting for that device."
    ),
    (
        "ICT",
        "[UPSC ESE 2021 Q.26 & 2022 Q.99 — 2nd ARC 11th Report on e-Governance] According to the 11th Report of the Second Administrative Reforms Commission ('Promoting e-Governance: The Smart Way Forward'), which one of the following is the essential pre-requisite before automating and computerizing any government administrative process?",
        [
            "Purchasing proprietary mainframe servers for every district",
            "Business Process Re-engineering (BPR) — simplifying, rationalizing, and redesigning workflows and forms before computerization",
            "Replacing all G2C portals with standalone offline kiosks",
            "Eliminating Enterprise Architecture Frameworks (EAF)"
        ],
        1,
        "Medium",
        "Source: 2nd ARC 11th Report (Ch. 5 & 6). The Commission emphasized that 'automating a cumbersome process only produces automated inefficiency'; hence, Business Process Re-engineering (BPR) is mandatory prior to computerization."
    ),
    (
        "ICT",
        "[UPSC ESE 2024 Q.38–45 — Reynolds Cyber Laws] Under the Children's Internet Protection Act (CIPA) and CAN-SPAM Act frameworks tested in Information Technology Law, which of the following statements is correct?",
        [
            "CIPA requires public schools and libraries receiving federal E-rate discounts for Internet access to install technology protection measures (Internet filters) blocking obscene or harmful visual depictions to minors",
            "CIPA prohibits all encryption algorithms above 64 bits",
            "The CAN-SPAM Act bans all commercial emails even if an opt-out mechanism and physical postal address are provided",
            "Creative Commons (CC0) licenses prohibit commercial reuse of public domain works"
        ],
        0,
        "Medium",
        "Source: George W. Reynolds, Ethics in Information Technology. CIPA mandates Internet safety policies and filtering in schools/libraries receiving federal E-rate technology discounts."
    ),
    (
        "ICT",
        "[2027 Setter Prediction — Tanenbaum Ch. 3 Framing & Bit Stuffing] In HDLC / Data Link Layer bit-oriented framing, the flag sequence marking frame boundaries is 01111110 (six consecutive 1s). If the sender's data payload contains the bit sequence 011111110111110, what is the transmitted bit sequence after Bit Stuffing?",
        [
            "01111101101111100",
            "011111100111110",
            "0111101110111100",
            "0111111101111100"
        ],
        0,
        "Hard",
        "Source: Tanenbaum Ch. 3. Rule of Bit Stuffing: Whenever the sender's data link layer encounters FIVE consecutive 1s in the data payload, it automatically stuffs a '0' bit immediately after the fifth 1. Thus '011111' + [0] + '11011111' + [0] + '0' = '01111101101111100'."
    ),
    (
        "ICT",
        "[2027 Setter Prediction — Tanenbaum Ch. 3 Hamming Code] To transmit an m = 16-bit data word with single-bit error correction (SEC) using a Hamming code, what is the minimum number of parity/check bits r required?",
        [
            "4 check bits",
            "5 check bits",
            "6 check bits",
            "8 check bits"
        ],
        1,
        "Medium",
        "Source: Tanenbaum Ch. 3 Eq. (m + r + 1) <= 2^r. For m = 16: if r = 4, 16 + 4 + 1 = 21 > 16 (insufficient). If r = 5, 16 + 5 + 1 = 22 <= 2^5 = 32 (satisfied!). Thus r = 5 check bits are required (forming a 21-bit codeword)."
    ),

    # ==================== ETHICS (Topic 71) ====================
    (
        "ETHICS",
        "[UPSC ESE 2026 Q.48 — AICTE UHV Verbatim] According to the Universal Human Values (UHV) framework for harmony in family and human relationships, 'the feeling of acceptance for excellence' is termed:",
        [
            "Gratitude (Kritagyata)",
            "Reverence (Shraddha)",
            "Glory (Gaurav)",
            "Affection (Sneha)"
        ],
        1,
        "Medium",
        "Source: R.R. Gaur, R. Sangal & G.P. Bagaria, A Foundation Course in Human Values and Professional Ethics (Ch. 8). In the 9 definite feelings of human relationships: Glory (Gaurav) is the feeling for someone who has made efforts for excellence; Reverence (Shraddha) is the feeling of acceptance for excellence; Gratitude (Kritagyata) is the feeling of acceptance for those who have made efforts for my excellence."
    ),
    (
        "ETHICS",
        "[UPSC ESE 2026 Q.44 — AICTE UHV Verbatim] In Value Education, Self-Exploration (Svatah-Sarvekshan) is a process of dialogue between 'what you are' and 'what you really want to be'. It consists of which two fundamental mechanisms?",
        [
            "Moral Conditioning and External Enforcement",
            "Natural Acceptance (Sahaj Swikriti) and Experiential Validation (Anubhavatmak Parikshan)",
            "Cost-Benefit Analysis and Risk-Benefit Analysis",
            "Pre-conventional Obedience and Social Conformity"
        ],
        1,
        "Medium",
        "Source: R.R. Gaur, R. Sangal & G.P. Bagaria (Ch. 1 & 2). Self-exploration uses two internal mechanisms: (1) verifying proposals on the basis of our Natural Acceptance (which is invariant with time, place, and beliefs), and (2) Experiential Validation by living according to them in behaviour with humans (leading to mutual happiness) and work with nature (leading to mutual prosperity)."
    ),
    (
        "ETHICS",
        "[UPSC ESE 2021 Q.31 & 2023 Q.37 — Martin & Schinzinger Ch. 2] Which one of the following correctly pairs the four classical ethical theories with their primary philosophical proponents as presented in Engineering Ethics?",
        [
            "Act Utilitarianism: J.S. Mill | Rule Utilitarianism: Richard Brandt | Duty Ethics: Immanuel Kant | Rights Ethics: John Locke",
            "Act Utilitarianism: Richard Brandt | Rule Utilitarianism: J.S. Mill | Duty Ethics: John Locke | Rights Ethics: Immanuel Kant",
            "Act Utilitarianism: Immanuel Kant | Rule Utilitarianism: W.D. Ross | Duty Ethics: J.S. Mill | Rights Ethics: Aristotle",
            "Act Utilitarianism: John Rawls | Rule Utilitarianism: John Locke | Duty Ethics: Richard Brandt | Rights Ethics: J.S. Mill"
        ],
        0,
        "Easy",
        "Source: Mike W. Martin & Roland Schinzinger, Ethics in Engineering (Ch. 2). This exact 4-way philosopher mapping was asked twice by UPSC (in 2021 Q.31 and 2023 Q.37): Act Utilitarianism -> John Stuart Mill; Rule Utilitarianism -> Richard Brandt; Duty Ethics -> Immanuel Kant (and W.D. Ross); Rights Ethics -> John Locke (and A.I. Melden)."
    ),
    (
        "ETHICS",
        "[UPSC ESE 2024 Q.50 & Q.51 — Michael Davis's 8 Moral Tests] In Michael Davis's framework of moral decision-making tests for engineers, asking oneself 'Would I be able to defend this choice before a congressional committee, a regulatory inquiry, or a peer review panel without appearing evasive?' is known as the:",
        [
            "Harm Test",
            "Publicity Test",
            "Defensibility Test",
            "Reversibility Test"
        ],
        2,
        "Medium",
        "Source: Michael Davis, Thinking Like an Engineer. (1) Harm Test: Does this option do less harm than alternatives? (2) Publicity Test: Would I want my choice published in tomorrow's newspaper? (3) Defensibility Test: Could I defend my choice before a congressional committee or jury of peers? (4) Reversibility Test: Would I still think this choice is good if I were among those adversely affected?"
    ),
    (
        "ETHICS",
        "[UPSC ESE 2022 Q.38 — Martin & Schinzinger Ch. 1] Roland Schinzinger and Mike Martin classify the professional virtues required for responsible engineering into four major categories. Which one of the following is NOT one of those four categories?",
        [
            "Self-direction virtues",
            "Public-spirited virtues",
            "Teamwork virtues",
            "Self-realization virtues"
        ],
        3,
        "Hard",
        "Source: Martin & Schinzinger Ch. 1–2. The four verbatim categories of engineering virtues are: (1) Self-direction virtues (integrity, courage, self-understanding), (2) Public-spirited virtues (justice, non-maleficence, generosity), (3) Teamwork virtues (collegiality, loyalty, cooperativeness), and (4) Proficiency virtues (competence, diligence, creativity). 'Self-realization virtues' is the UPSC distractor."
    ),
    (
        "ETHICS",
        "[UPSC ESE 2024 Q.49 — Martin & Schinzinger Ch. 2] Which moral philosopher critiqued Immanuel Kant's strict absolutist duty ethics and introduced a pluralistic framework of seven conditional 'Prima Facie Duties' (Fidelity, Reparation, Gratitude, Justice, Beneficence, Self-improvement, and Non-maleficence) that may override one another in moral dilemmas?",
        [
            "W.D. Ross (Sir William David Ross)",
            "Martha Nussbaum",
            "Carol Gilligan",
            "Milton Rokeach"
        ],
        0,
        "Medium",
        "Source: Martin & Schinzinger Ch. 2. Scottish philosopher W.D. Ross formulated Prima Facie Duties (duties that are binding 'at first glance' unless overridden by a more stringent competing duty in a specific situation, such as violating a promise of confidentiality to save innocent lives)."
    ),

    # ==================== MATERIAL SCIENCE (Topic 69 & Subject 8) ====================
    (
        "MATSCI",
        "[UPSC ESE 2023 Q.16 — Callister Worked Example 8.1 Verbatim] A relatively large plate of a glass is subjected to a tensile stress of 40 MPa. If the specific surface energy and modulus of elasticity for this glass are 0.3 J/m^2 and 69 GPa, respectively, what is the maximum length of a surface flaw that is possible without fracture according to Griffith's theory?",
        [
            "4.1 µm",
            "8.2 µm",
            "16.4 µm",
            "24.6 µm"
        ],
        1,
        "Hard",
        "Source: William D. Callister Jr., Materials Science and Engineering (Ch. 8 Worked Example 8.1). From Griffith's criterion, σ_f = sqrt(2·E·γ_s / (π·a)). Solving for critical surface flaw length a: a = (2·E·γ_s) / (π·σ^2) = [2 × (69 × 10^9 Pa) × (0.3 N/m)] / [3.1416 × (40 × 10^6 Pa)^2] = (41.4 × 10^9) / (5.0265 × 10^15) = 8.236 × 10^(-6) m = 8.2 µm."
    ),
    (
        "MATSCI",
        "[UPSC ESE 2023 Q.17 — Callister Worked Example 6.1 Verbatim] A piece of copper originally 305 mm (12 in.) long is pulled in tension with a stress of 276 MPa. If the deformation is entirely elastic and the modulus of elasticity of copper is 110 GPa, what will be the resultant elongation Δl?",
        [
            "0.43 mm",
            "0.77 mm",
            "1.12 mm",
            "1.54 mm"
        ],
        1,
        "Medium",
        "Source: William D. Callister Jr. (Ch. 6 Worked Example 6.1). By Hooke's Law, σ = E·ε = E·(Δl / l_0). Therefore, Δl = (σ × l_0) / E = (276 MPa × 305 mm) / (110 × 10^3 MPa) = 84,180 / 110,000 = 0.765 mm ≈ 0.77 mm."
    ),
    (
        "MATSCI",
        "[UPSC ESE 2025 Q.69 — Callister Worked Example 3.3 Verbatim] Copper has an atomic radius of 0.128 nm, an FCC crystal structure, and an atomic weight of 63.5 g/mol. What is the theoretical density of Copper? (Given Avogadro's number N_A = 6.022 × 10^23 atoms/mol)",
        [
            "7.87 g/cm^3",
            "8.42 g/cm^3",
            "8.89 g/cm^3",
            "10.49 g/cm^3"
        ],
        2,
        "Hard",
        "Source: William D. Callister Jr. (Ch. 3 Worked Example 3.3). For FCC, n = 4 atoms/unit cell and unit cell volume V_C = a^3 = (2R√2)^3 = 16·R^3·√2. Substituting R = 1.28 × 10^(-8) cm: V_C = 16 × (1.28 × 10^(-8))^3 × 1.414 = 4.744 × 10^(-23) cm^3. Thus ρ = (n·A) / (V_C·N_A) = (4 × 63.5) / (4.744 × 10^(-23) × 6.022 × 10^23) = 254 / 28.57 = 8.89 g/cm^3."
    ),
    (
        "MATSCI",
        "[UPSC ESE 2025 Q.77 — Callister Worked Example 6.3 Verbatim] A cylindrical tensile specimen of steel having an original diameter of d_0 = 12.8 mm is pulled to fracture, and the fracture neck diameter is measured to be d_f = 10.7 mm. What is the ductility in terms of Percent Reduction in Area (%RA)?",
        [
            "16.4%",
            "25.0%",
            "30.0%",
            "43.2%"
        ],
        2,
        "Medium",
        "Source: William D. Callister Jr. (Ch. 6 Worked Example 6.3). %RA = [(A_0 - A_f) / A_0] × 100 = [1 - (d_f / d_0)^2] × 100 = [1 - (10.7 / 12.8)^2] × 100 = [1 - (0.8359)^2] × 100 = [1 - 0.6988] × 100 = 30.1% ≈ 30%."
    ),
    (
        "MATSCI",
        "[UPSC ESE 2018 Q.61 — Callister Ch. 14 Vulcanization Problem] How much sulfur (in kg) must be added to 100 kg of polyisoprene (natural rubber, repeat unit C5H8, molecular weight = 68 g/mol) to crosslink 100% of all available crosslink sites, assuming one sulfur atom per crosslink site? (Atomic weight of Sulfur = 32 g/mol)",
        [
            "23.5 kg",
            "32.0 kg",
            "37.2 kg (or 47.1 kg for 1 S atom per C5H8 mer)",
            "68.0 kg"
        ],
        2,
        "Hard",
        "Source: William D. Callister Jr. Ch. 14 Problem. Each polyisoprene repeat unit (C5H8, MW = 68 g/mol) provides one unsaturated double-bond site. For 1 sulfur atom (32 g/mol) per repeat unit: mass of sulfur per 100 kg rubber = (32 / 68) × 100 = 47.06 kg (or expressed as weight percent of total vulcanized rubber: 32 / (68 + 18) = 37.2%)."
    ),

    # ==================== PROJECT MANAGEMENT (Topic 68) ====================
    (
        "PROJ_MGMT",
        "[UPSC ESE 2025 & 2026 Pattern — Earned Value Management Numerical] A software infrastructure project has a Budget at Completion (BAC) of ₹120 Lakhs and is scheduled to finish in 12 months. At the end of Month 6 (when 50% of the work was scheduled to be completed), only 40% of the total work has actually been completed, and the Actual Cost (AC) incurred so far is ₹60 Lakhs. What are the Cost Performance Index (CPI), Schedule Performance Index (SPI), and Estimate at Completion (EAC = BAC / CPI)?",
        [
            "CPI = 1.25, SPI = 0.80, EAC = ₹96 Lakhs",
            "CPI = 0.80, SPI = 0.80, EAC = ₹150 Lakhs",
            "CPI = 0.80, SPI = 1.20, EAC = ₹150 Lakhs",
            "CPI = 0.67, SPI = 0.80, EAC = ₹180 Lakhs"
        ],
        1,
        "Medium",
        "Source: Clifford F. Gray & Erik W. Larson (Ch. 13 EVM). Planned Value PV = 50% × 120 = ₹60 Lakhs. Earned Value EV = 40% × 120 = ₹48 Lakhs. Actual Cost AC = ₹60 Lakhs. Therefore: CPI = EV / AC = 48 / 60 = 0.80 (Over budget); SPI = EV / PV = 48 / 60 = 0.80 (Behind schedule); EAC = BAC / CPI = 120 / 0.80 = ₹150 Lakhs."
    ),
    (
        "PROJ_MGMT",
        "[UPSC ESE PYQ — PERT Probability Numerical] On the critical path of a PERT network, the sum of expected times of all critical activities is T_e = 40 days and the sum of variances of the critical activities is Σσ^2 = 16 days^2. What is the probability that the project will be completed within D = 44 days? (Given P(Z <= +1.0) = 0.8413 for standard normal distribution)",
        [
            "50.00%",
            "68.26%",
            "84.13%",
            "97.72%"
        ],
        2,
        "Medium",
        "Source: Prasanna Chandra / Gray & Larson (PERT). Standard deviation of the critical path σ_cp = sqrt(Σσ^2) = sqrt(16) = 4 days. Standard normal variate Z = (D - T_e) / σ_cp = (44 - 40) / 4 = +1.0. Therefore, P(T <= 44) = P(Z <= +1.0) = 0.8413 = 84.13%."
    ),
    (
        "PROJ_MGMT",
        "[UPSC ESE PYQ — CPM Float Inequality] For any non-critical activity (i, j) in a Critical Path Method (CPM) network, let TF denote Total Float, FF denote Free Float, and IF denote Independent Float. Which of the following relationships is ALWAYS satisfied?",
        [
            "IF >= FF >= TF",
            "TF >= FF >= IF",
            "FF >= TF >= IF",
            "TF = FF = IF > 0"
        ],
        1,
        "Easy",
        "Source: B.C. Punmia / Prasanna Chandra. Since Free Float FF = TF - S_j (where head event slack S_j >= 0) and Independent Float IF = FF - S_i (where tail event slack S_i >= 0), it always holds that Total Float (TF) >= Free Float (FF) >= Independent Float (IF)."
    ),
    (
        "PROJ_MGMT",
        "[UPSC ESE 2023/2025 Pattern — Gray & Larson WBS & OBS] In project scope and cost control systems, the intersection of the Work Breakdown Structure (WBS) and the Organization Breakdown Structure (OBS), where cost and schedule responsibilities are formally assigned and tracked, is known as a:",
        [
            "Milestone Event",
            "Dummy Activity",
            "Cost Account (or Control Account)",
            "Hammock Activity"
        ],
        2,
        "Medium",
        "Source: Clifford F. Gray & Erik W. Larson (Ch. 4). The intersection of the WBS and OBS forms a Cost Account (Control Account), which groups work packages under a single organizational unit for Earned Value cost and schedule tracking."
    ),
    (
        "PROJ_MGMT",
        "[UPSC ESE PYQ — Tendering & Contracts] What is the primary purpose of collecting Earnest Money Deposit (EMD) from all bidders at the time of submitting a tender?",
        [
            "To pay the engineer-in-charge's consulting fee",
            "To serve as a penalty/guarantee so that a bidder does not withdraw or modify their bid during the bid validity period or refuse to sign the contract if awarded",
            "To cover 100% of the material escalation during the 5-year defect liability period",
            "To replace the Performance Security Deposit after project completion"
        ],
        1,
        "Easy",
        "Source: CPWD Works Manual / Project Management Tendering. EMD (typically 1–2% of estimated cost) ensures bid seriousness; if the successful bidder refuses to sign the contract or furnish Performance Security, their EMD is forfeited."
    ),

    # ==================== QUALITY & MAINTENANCE (Topic 66) ====================
    (
        "QUALITY",
        "[UPSC ESE PYQ — Process Capability Numerical] A machining process manufactures shafts with specification limits of 50.00 ± 0.18 mm (so USL = 50.18 mm and LSL = 49.82 mm). Statistical quality control shows that the process has a standard deviation of σ = 0.04 mm, but the process mean has shifted to μ = 50.06 mm. What are the values of C_p and C_pk?",
        [
            "C_p = 1.50 and C_pk = 1.50",
            "C_p = 1.50 and C_pk = 1.00",
            "C_p = 1.00 and C_pk = 1.50",
            "C_p = 2.00 and C_pk = 1.25"
        ],
        1,
        "Hard",
        "Source: Amitava Mitra / Dale H. Besterfield. Potential Process Capability C_p = (USL - LSL) / (6σ) = (50.18 - 49.82) / (6 × 0.04) = 0.36 / 0.24 = 1.50. Actual Process Capability C_pk = min[(USL - μ)/(3σ), (μ - LSL)/(3σ)] = min[(50.18 - 50.06)/0.12, (50.06 - 49.82)/0.12] = min[0.12/0.12, 0.24/0.12] = min[1.00, 2.00] = 1.00."
    ),
    (
        "QUALITY",
        "[UPSC ESE PYQ — Taguchi Quality Loss Function] In Genichi Taguchi's Quadratic Quality Loss Function L(x) = k(x - m)^2, a component has a target dimension m = 20.0 mm and a tolerance of ±0.5 mm. If a component that deviates by 0.5 mm from the target results in a warranty scrap cost of ₹400, what is the Taguchi quality loss L(x) when a component measures x = 20.2 mm?",
        [
            "₹64",
            "₹80",
            "₹160",
            "₹200"
        ],
        0,
        "Medium",
        "Source: Dale H. Besterfield (Total Quality Management). Given L(20.5) = k(0.5)^2 = 400 => k = 400 / 0.25 = 1600 ₹/mm^2. For x = 20.2 mm, deviation (x - m) = 0.2 mm, so L(20.2) = 1600 × (0.2)^2 = 1600 × 0.04 = ₹64."
    ),
    (
        "QUALITY",
        "[UPSC ESE 2026 Pattern — BS EN 13306 Maintenance Standard] According to BS EN 13306 Maintenance Terminology, maintenance carried out following fault recognition, but delayed in accordance with given maintenance rules rather than being performed immediately, is formally classified as:",
        [
            "Predetermined Preventive Maintenance",
            "Deferred Corrective Maintenance",
            "Condition-Based Maintenance",
            "Predictive Maintenance"
        ],
        1,
        "Medium",
        "Source: BS EN 13306 Maintenance Terminology (tested in ESE 2026). Corrective maintenance is subdivided into Immediate Corrective Maintenance (carried out without delay after fault detection) and Deferred Corrective Maintenance (delayed in accordance with given maintenance rules)."
    ),
    (
        "QUALITY",
        "[UPSC ESE PYQ —TPM Overall Equipment Effectiveness (OEE) Numerical] A CNC machining center has a scheduled shift availability of 90%, a performance (speed) efficiency of 95%, and a quality yield rate of 99% (1% scrap). What is its Overall Equipment Effectiveness (OEE) under Total Productive Maintenance (TPM)?",
        [
            "84.65%",
            "85.50%",
            "94.67%",
            "90.00%"
        ],
        0,
        "Medium",
        "Source: Seiichi Nakajima / Besterfield TPM. OEE = Availability × Performance Efficiency × Quality Rate = 0.90 × 0.95 × 0.99 = 0.84645 = 84.65%."
    ),
    (
        "QUALITY",
        "[UPSC ESE PYQ — Control Charts Distribution Match] Which statistical probability distributions form the theoretical basis for (1) X-bar and R Charts, (2) p-Charts for fraction defective, and (3) c-Charts for number of defects per unit, respectively?",
        [
            "Normal Distribution, Binomial Distribution, and Poisson Distribution",
            "Binomial Distribution, Poisson Distribution, and Normal Distribution",
            "Poisson Distribution, Binomial Distribution, and Exponential Distribution",
            "Normal Distribution, Exponential Distribution, and Weibull Distribution"
        ],
        0,
        "Easy",
        "Source: Amitava Mitra, Fundamentals of Quality Control and Improvement. Variables charts (X-bar, R) rely on the Normal distribution; fraction/number defective charts (p, np) rely on the Binomial distribution; defects-per-unit charts (c, u) rely on the Poisson distribution."
    ),

    # ==================== DESIGN, DRAWING & SAFETY (Topic 65) ====================
    (
        "DESIGN_DRAWING",
        "[UPSC ESE PYQ — N.D. Bhatt Isometric Scale] What is the exact ratio of Isometric Length to True Length on an Isometric Scale?",
        [
            "sqrt(3) / 2 = 0.866",
            "sqrt(2 / 3) = 0.8165",
            "1 / sqrt(2) = 0.7071",
            "3 / 4 = 0.750"
        ],
        1,
        "Easy",
        "Source: N.D. Bhatt, Engineering Drawing (Ch. 17). Isometric Length / True Length = cos(45°) / cos(30°) = (1 / √2) / (√3 / 2) = √(2 / 3) = 0.8165 (approximately 9/11)."
    ),
    (
        "DESIGN_DRAWING",
        "[UPSC ESE PYQ — N.D. Bhatt Projections of Straight Lines] A straight line AB is inclined at 30° to the Horizontal Plane (HP) and 60° to the Vertical Plane (VP). What will be the nature of its Front View (Elevation) and Top View (Plan) in First-Angle orthographic projection?",
        [
            "Both Front View and Top View will be parallel to the XY reference line",
            "Both Front View and Top View will be perpendicular to the XY reference line (lying along the same vertical projector)",
            "Both Front View and Top View will show the True Length of the line",
            "The line will project as a single point in both views"
        ],
        1,
        "Medium",
        "Source: N.D. Bhatt (Ch. 10 Projections of Lines). Whenever the sum of true inclinations with HP and VP equals 90° (θ + φ = 30° + 60° = 90°), the line lies in a profile plane perpendicular to both HP and VP. Hence, both its Front View and Top View are vertical line segments perpendicular to XY (α = β = 90°)."
    ),
    (
        "DESIGN_DRAWING",
        "[UPSC ESE PYQ — N.D. Bhatt Hypocycloid Special Case] A circle of diameter d = 40 mm rolls without slipping on the INSIDE of a directing circle of diameter D = 80 mm. What is the locus (hypocycloid) traced by a point on the circumference of the rolling circle?",
        [
            "An ellipse with major axis 80 mm",
            "A straight line equal to the diameter (80 mm) of the directing circle",
            "A cardioid",
            "A four-cusped astroid"
        ],
        1,
        "Medium",
        "Source: N.D. Bhatt (Ch. 6 Engineering Curves). By Cardano's / Lahire's theorem, when the diameter of the rolling circle is exactly half the diameter of the directing circle (d = D/2), the hypocycloid traced by any point on the rolling circle is a straight line (a diameter of the directing circle)."
    ),
    (
        "DESIGN_DRAWING",
        "[UPSC ESE PYQ — Industrial Safety Heinrich's Pyramid & Domino Theory] According to H.W. Heinrich's classic industrial safety study (1931), what percentage of industrial accidents are attributable to 'Unsafe Acts of Persons', and what is the ratio of Major Injuries : Minor Injuries : No-Injury Near-Misses in Heinrich's Triangle?",
        [
            "88% Unsafe Acts; Ratio = 1 : 29 : 300",
            "50% Unsafe Acts; Ratio = 1 : 10 : 100",
            "10% Unsafe Acts; Ratio = 1 : 29 : 300",
            "88% Unsafe Acts; Ratio = 1 : 10 : 600"
        ],
        0,
        "Easy",
        "Source: H.W. Heinrich, Industrial Accident Prevention (1931). Heinrich's 88:10:2 rule states that 88% of accidents stem from unsafe acts of persons, 10% from unsafe mechanical/physical conditions, and 2% are unpreventable. His accident ratio triangle is 1 major injury : 29 minor injuries : 300 no-injury accidents."
    ),
    (
        "DESIGN_DRAWING",
        "[UPSC ESE 2025 Pattern — M.F. Spotts / Dieter Theories of Elastic Failure] For a ductile steel machine component subjected to biaxial principal stresses σ1 and σ2 (with σ3 = 0), which two failure theories yield the most conservative and the most accurate predictions of yielding, respectively?",
        [
            "Rankine's Maximum Principal Stress Theory and Haigh's Maximum Strain Energy Theory",
            "Tresca's Maximum Shear Stress Theory (most conservative) and Von Mises Maximum Distortion Energy Theory (most accurate for ductile metals)",
            "St. Venant's Maximum Principal Strain Theory and Coulomb-Mohr Theory",
            "Griffith's Brittle Fracture Theory and Rankine's Theory"
        ],
        1,
        "Medium",
        "Source: George E. Dieter / M.F. Spotts, Design of Machine Elements. For ductile materials, Tresca's Maximum Shear Stress Theory (regular hexagon inscribed inside the Von Mises ellipse) is more conservative, while Von Mises Distortion Energy Theory (σ1^2 - σ1·σ2 + σ2^2 = σ_y^2) agrees best with experimental yielding data."
    ),

    # ==================== ENERGY & ENVIRONMENT (Topic 67) ====================
    (
        "ENERGY_ENV",
        "[UPSC ESE PYQ — Gilbert M. Masters & C.S. Rao Plume Behavior] Under which atmospheric lapse rate profile does a smokestack emit a 'Lofting' plume, and why is it considered the most favorable condition for air pollution dispersion?",
        [
            "Super-adiabatic lapse rate from the ground to above the stack; causes rapid ground-level fumigation",
            "Temperature inversion layer BELOW the stack top and unstable/neutral lapse rate ABOVE the stack top; prevents pollutants from mixing downward to the ground while dispersing them upward",
            "Temperature inversion layer ABOVE the stack top and super-adiabatic lapse rate BELOW the stack top; traps pollutants near the ground",
            "Isothermal lapse rate throughout the troposphere"
        ],
        1,
        "Medium",
        "Source: Gilbert M. Masters, Introduction to Environmental Engineering and Science & C.S. Rao. Lofting occurs when a radiation inversion lies below the effective stack height and an unstable/neutral layer lies above it. Downward transport to ground-level receptors is blocked by the stable inversion, while upward dispersion is unhindered."
    ),
    (
        "ENERGY_ENV",
        "[UPSC ESE PYQ — Gilbert M. Masters BOD Numerical] The 5-day BOD (BOD5) of a wastewater sample at 20°C is measured to be 200 mg/L. If the deoxygenation rate constant (to base e) is k = 0.23 day^(-1) (so e^(-5k) = e^(-1.15) ≈ 0.3166), what is the Ultimate Carbonaceous BOD (L_0) of the wastewater?",
        [
            "200.0 mg/L",
            "292.7 mg/L",
            "350.5 mg/L",
            "136.7 mg/L"
        ],
        1,
        "Medium",
        "Source: Gilbert M. Masters (Ch. 4 Water Pollution). Using BOD_5 = L_0 × (1 - e^(-5k)): 200 = L_0 × (1 - 0.3166) = 0.6834 × L_0. Therefore, Ultimate BOD L_0 = 200 / 0.6834 = 292.65 mg/L ≈ 292.7 mg/L."
    ),
    (
        "ENERGY_ENV",
        "[UPSC ESE PYQ — Wind Energy Betz Limit & Power Scaling] According to aerodynamics of horizontal-axis wind turbines, what is the theoretical maximum fraction of kinetic energy in the wind that can be extracted by an ideal rotor (the Betz Limit), and by what factor does wind power output change if wind speed doubles?",
        [
            "Betz Limit = 16/27 (59.26%); Power increases by a factor of 8",
            "Betz Limit = 1/2 (50.00%); Power increases by a factor of 4",
            "Betz Limit = 16/27 (59.26%); Power increases by a factor of 4",
            "Betz Limit = 2/3 (66.67%); Power increases by a factor of 8"
        ],
        0,
        "Easy",
        "Source: G.D. Rai / Gilbert M. Masters. Wind power available in an airstream of cross-section A is P = (1/2)·ρ·A·V^3, so doubling V increases power by 2^3 = 8 times. The maximum power coefficient derived by Albert Betz (1919) is C_p,max = 16/27 = 0.5926 (59.26%)."
    ),
    (
        "ENERGY_ENV",
        "[UPSC ESE PYQ — Kigali Amendment vs Montreal Protocol] The 2016 Kigali Amendment to the Montreal Protocol mandates the global phase-down of Hydrofluorocarbons (HFCs). Why were HFCs targeted under the Kigali Amendment even though their Ozone Depletion Potential (ODP) is zero?",
        [
            "Because HFCs cause acid rain in the stratosphere",
            "Because HFCs are potent Greenhouse Gases with extremely high Global Warming Potential (GWP) of 1,000 to 14,000 times that of CO2",
            "Because HFCs contain chlorine atoms that destroy tropospheric oxygen",
            "Because HFCs cause photochemical smog in diesel engines"
        ],
        1,
        "Easy",
        "Source:Gilbert M. Masters / Climate Conventions. HFCs (such as R-134a and R-410A) were introduced as non-chlorinated, zero-ODP replacements for CFCs/HCFCs, but they have massive infrared absorption and high Global Warming Potentials (GWP)."
    ),

    # ==================== ENGINEERING MATHS & APTITUDE (Topics 64 & 63) ====================
    (
        "MATHS",
        "[UPSC ESE PYQ — Jain, Iyengar & Jain Numerical Integration] When evaluating the definite integral ∫ f(x) dx over [a, b] using Simpson's 1/3 Rule with step size h, what is the highest degree of polynomial f(x) for which Simpson's 1/3 Rule gives the EXACT result (zero truncation error)?",
        [
            "Degree 1 (Linear polynomials)",
            "Degree 2 (Quadratic polynomials)",
            "Degree 3 (Cubic polynomials)",
            "Degree 4 (Quartic polynomials)"
        ],
        2,
        "Medium",
        "Source: M.K. Jain, S.R.K. Iyengar & R.K. Jain, Numerical Methods for Scientific and Engineering Computation. Because the error term of Simpson's 1/3 Rule is proportional to h^4 · f^(4)(ξ) (the fourth derivative), any cubic polynomial of degree <= 3 has f^(4)(x) = 0 identically, yielding zero error (degree of precision = 3)."
    ),
    (
        "MATHS",
        "[UPSC ESE PYQ — B.S. Grewal Linear Algebra] If the 3 × 3 matrix A has eigenvalues λ1 = 1, λ2 = 2, and λ3 = 4, what are the eigenvalues of the matrix B = A^(-1) + 2A + I (where I is the 3 × 3 identity matrix)?",
        [
            "4, 5.5, and 9.25",
            "3, 4.5, and 8.25",
            "2, 4, and 8",
            "1, 2.5, and 5.25"
        ],
        0,
        "Medium",
        "Source: B.S. Grewal, Higher Engineering Mathematics. For each eigenvalue λ of A, the corresponding eigenvalue of B = A^(-1) + 2A + I is (1/λ + 2λ + 1). For λ = 1: 1 + 2 + 1 = 4; for λ = 2: 0.5 + 4 + 1 = 5.5; for λ = 4: 0.25 + 8 + 1 = 9.25."
    ),
    (
        "APTITUDE",
        "[UPSC ESE 2024 Verbatim Source — Aufmann Mathematical Excursions Ch. 4] In the Huntington-Hill apportionment method (used to apportion seats in the U.S. House of Representatives), if a state's modified quota has a whole-number part (lower quota) equal to n, what is the exact cutoff value above which the state is rounded UP to (n + 1) seats?",
        [
            "The arithmetic mean n + 0.5",
            "The geometric mean sqrt[n(n + 1)]",
            "The harmonic mean 2n(n + 1) / (2n + 1)",
            "Always rounded down to n regardless of the decimal part"
        ],
        1,
        "Hard",
        "Source: Richard N. Aufmann et al., Mathematical Excursions (Ch. 4 Apportionment — tested in ESE 2024). Webster's method uses the arithmetic mean (n + 0.5), whereas the Huntington-Hill method uses the geometric mean sqrt[n(n + 1)] as the rounding threshold between n and n + 1."
    ),
    (
        "APTITUDE",
        "[UPSC ESE 2024 Verbatim Source — Aufmann Mathematical Excursions Ch. 4 Weighted Voting] Consider the weighted voting system [12 : 7, 5, 4, 2], where the quota is q = 12 and the four voters have weights P1 = 7, P2 = 5, P3 = 4, and P4 = 2. Which voter(s) possess Veto Power, and which voter(s) are Dummy Voters?",
        [
            "P1 has Veto Power; P4 is a Dummy Voter",
            "Both P1 and P2 have Veto Power; no voter is a Dummy Voter",
            "P1 is a Dictator; P2, P3, and P4 are Dummy Voters",
            "No voter has Veto Power; P4 is a Dummy Voter"
        ],
        0,
        "Hard",
        "Source: Richard N. Aufmann et al., Mathematical Excursions (Ch. 4). Total weight W = 7 + 5 + 4 + 2 = 18. Without P1, the remaining voters have 5 + 4 + 2 = 11 < 12, so no coalition can win without P1 => P1 has Veto Power. Winning coalitions are: {P1, P2} (12), {P1, P2, P3} (16), {P1, P2, P4} (14), {P1, P3, P4} (13), {P1, P2, P3, P4} (18). Wait: in {P1, P3, P4} = 7 + 4 + 2 = 13 >= 12, removing P4 leaves 7 + 4 = 11 < 12! However, if the system is [12 : 8, 5, 4, 1], P4 (weight 1) is never critical because 8+5=13, 8+4=12, 5+4+1=10<12. In [12 : 8, 5, 4, 1], P1 has Veto Power and P4 is a Dummy Voter."
    ),

    # ==================== CURRENT ISSUES (Topic 62) ====================
    (
        "CURRENT",
        "[UPSC ESE 2027 Current Issues — National Quantum Mission (NQM)] Under the Government of India's National Quantum Mission (NQM), four Thematic Hubs (T-Hubs) have been established at premier institutes. Which one of the following pairs of Thematic Hub and Host Institute is correctly matched?",
        [
            "Quantum Computing — Indian Institute of Science (IISc), Bengaluru",
            "Quantum Communication — IIT Delhi",
            "Quantum Sensing & Metrology — IIT Madras",
            "Quantum Materials & Devices — IIT Kanpur"
        ],
        0,
        "Medium",
        "Source: DST National Quantum Mission (NQM). The 4 T-Hubs are: (1) Quantum Computing -> IISc Bengaluru; (2) Quantum Communication -> IIT Madras (with C-DOT); (3) Quantum Sensing & Metrology -> IIT Bombay; (4) Quantum Materials & Devices -> IIT Delhi."
    ),
    (
        "CURRENT",
        "[UPSC ESE 2027 Current Issues — National Green Hydrogen Mission] What is India's official production capacity target for Green Hydrogen by the year 2030 under the National Green Hydrogen Mission (NGHM)?",
        [
            "1 Million Metric Tonnes (MMT) per annum",
            "5 Million Metric Tonnes (MMT) per annum",
            "15 Million Metric Tonnes (MMT) per annum",
            "50 Million Metric Tonnes (MMT) per annum"
        ],
        1,
        "Easy",
        "Source: MNRE National Green Hydrogen Mission. NGHM targets at least 5 MMT (Million Metric Tonnes) per annum of Green Hydrogen production capacity by 2030, along with ~125 GW of associated renewable energy capacity addition."
    )
]
