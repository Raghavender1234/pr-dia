# -*- coding: utf-8 -*-
"""
Seed UPSC ESE Prelims Questions for Paper-I Topics 62 to 68.
Topics:
62: Current Issues of National & International Importance
63: Engineering Aptitude (Logical Reasoning & Analytical Ability)
64: Engineering Mathematics & Numerical Analysis
65: General Principles of Design, Drawing & Importance of Safety
66: Standards and Quality Practices
67: Basics of Energy and Environment
68: Basics of Project Management
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.question import Question, MCQOption

QUESTIONS_DATA = [
    # ==================== TOPIC 62: Current Issues ====================
    {
        "topic_id": 62,
        "question_text": "[UPSC ESE Prelims Paper-I — National Engineering Missions]\nUnder the National Green Hydrogen Mission approved by the Government of India, what is the targeted production capacity of Green Hydrogen per annum by the year 2030?",
        "difficulty": "Medium",
        "options": [
            ("At least 1 Million Metric Tonnes (MMT)", False),
            ("At least 5 Million Metric Tonnes (MMT)", True),
            ("At least 10 Million Metric Tonnes (MMT)", False),
            ("At least 20 Million Metric Tonnes (MMT)", False),
        ],
        "explanation": "Target of the National Green Hydrogen Mission (approved Jan 2023): Develop green hydrogen production capacity of at least 5 MMT (Million Metric Tonnes) per annum by 2030, with an associated renewable energy capacity addition of about 125 GW."
    },
    {
        "topic_id": 62,
        "question_text": "[UPSC ESE Prelims Paper-I — Semiconductor Mission]\nWhich of the following incentives is offered under the Modified Scheme for setting up Semiconductor Fabs in India under the India Semiconductor Mission (ISM)?",
        "difficulty": "Medium",
        "options": [
            ("Fiscal support of 25% of the project cost on pari-passu basis", False),
            ("Fiscal support of 50% of the project cost on pari-passu basis across all technology nodes", True),
            ("100% tax holiday for 15 years with zero capital subsidy", False),
            ("Fiscal support only for legacy nodes (>65 nm) capped at Rs 5,000 Crore", False),
        ],
        "explanation": "Under the modified India Semiconductor Mission (ISM) scheme, uniform fiscal support of 50% of the project cost is provided on a pari-passu basis for all technology nodes (leading as well as mature nodes)."
    },
    {
        "topic_id": 62,
        "question_text": "[UPSC ESE Prelims Paper-I — Space Engineering]\nConsider the following statements regarding the Aditya-L1 Mission of ISRO:\n1. It is positioned at the Sun-Earth Lagrangian Point L1, approximately 1.5 million km from Earth.\n2. At the L1 point, an uninterrupted continuous view of the Sun is possible without any occultation or eclipse.\n3. The primary payload VELC (Visible Emission Line Coronagraph) studies the solar corona and coronal mass ejections.\nWhich of the above statements are correct?",
        "difficulty": "Hard",
        "options": [
            ("1 and 2 only", False),
            ("2 and 3 only", False),
            ("1 and 3 only", False),
            ("1, 2 and 3", True),
        ],
        "explanation": "All three statements are correct. Aditya-L1 is placed in a halo orbit around the Sun-Earth Lagrangian point L1 (~1.5 million km from Earth). A satellite in halo orbit around L1 has the major advantage of continuously viewing the Sun without any occultation/eclipses. VELC is the primary coronagraph payload."
    },
    {
        "topic_id": 62,
        "question_text": "[UPSC ESE Prelims Paper-I — Infrastructure Missions]\nStatement (I): PM GatiShakti National Master Plan integrates multi-modal connectivity infrastructure across railways, roadways, ports, and airways via a unified GIS platform.\nStatement (II): PM GatiShakti relies on the National Logistics Policy (NLP) to reduce India's logistics cost to single digits of GDP by 2030.\nWhich of the following is correct?",
        "difficulty": "Medium",
        "options": [
            ("Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)", False),
            ("Both Statement (I) and Statement (II) are individually true but Statement (II) is NOT the correct explanation of Statement (I)", True),
            ("Statement (I) is true but Statement (II) is false", False),
            ("Statement (I) is false but Statement (II) is true", False),
        ],
        "explanation": "Both statements are correct facts of India's infrastructure policy: GatiShakti integrates 16 ministries on a BISAG-N GIS platform, and the NLP complements it with a target of reducing logistics costs to ~8-9% of GDP. However, Statement II is a target of NLP, not the causal engineering explanation of GIS integration."
    },
    {
        "topic_id": 62,
        "question_text": "[UPSC ESE Prelims Paper-I — Ocean Engineering]\nUnder the Deep Ocean Mission of the Ministry of Earth Sciences, the indigenous manned submersible being developed to carry 3 humans to a depth of 6,000 metres is named:",
        "difficulty": "Medium",
        "options": [
            ("Varunastra 6000", False),
            ("Matsya 6000", True),
            ("Sagardhwani", False),
            ("Samudrayaan-1", False),
        ],
        "explanation": "Under the Samudrayaan project of the Deep Ocean Mission, the manned submersible vehicle designed by NIOT Chennai is named 'Matsya 6000', with a titanium alloy sphere capable of withstanding 600 bar hydrostatic pressure at 6,000 m depth."
    },

    # ==================== TOPIC 63: Engineering Aptitude ====================
    {
        "topic_id": 63,
        "question_text": "[UPSC ESE Prelims Paper-I — Aufmann Apportionment Theory]\nIn apportionment theory, the Alabama Paradox occurs when:",
        "difficulty": "Hard",
        "options": [
            ("A state loses a seat even though its population has increased more rapidly than other states.", False),
            ("An increase in the total number of seats to be apportioned causes a state to lose a seat, with no change in population.", True),
            ("The addition of a new state changes the seat allocation of existing states.", False),
            ("A smaller state receives proportionally more seats than a larger state.", False),
        ],
        "explanation": "The Alabama Paradox (observed in 1880 with Hamilton's method of largest remainders) occurs when an increase in the total house size (total number of seats available) results in a state losing a seat, even though all population counts remain constant."
    },
    {
        "topic_id": 63,
        "question_text": "[UPSC ESE Prelims Paper-I — Voting Theory & Social Choice]\nArrow's Impossibility Theorem mathematically demonstrates that for three or more distinct alternatives, no ranked voting electoral system can convert the ranked preferences of individuals into a community-wide ranking while simultaneously satisfying which set of criteria?",
        "difficulty": "Hard",
        "options": [
            ("Transitivity, Unrestricted Domain, Pareto Efficiency, and Independence of Irrelevant Alternatives (without a dictator)", True),
            ("Borda count proportionality, single transferable vote criteria, and condorcet winner criteria", False),
            ("Majority criterion, monotonicity criterion, and plurality representation", False),
            ("Proportional taxation, Pareto optimality, and Nash equilibrium", False),
        ],
        "explanation": "Kenneth Arrow's Impossibility Theorem (Nobel Prize 1972) proves that when voters have three or more alternatives, no deterministic voting rule can satisfy: 1) Non-dictatorship, 2) Unrestricted domain, 3) Weak Pareto efficiency, and 4) Independence of Irrelevant Alternatives (IIA), assuming transitivity of preferences."
    },
    {
        "topic_id": 63,
        "question_text": "[UPSC ESE Prelims Paper-I — Work & Time Aptitude]\nPumps A, B, and C can fill an industrial storage tank in 12 hours, 15 hours, and 20 hours respectively. If Pump A is kept open all the time and Pumps B and C are opened alternately for 1 hour each, in how many hours will the tank be completely filled?",
        "difficulty": "Medium",
        "options": [
            ("6 hours", False),
            ("7 hours", True),
            ("7.5 hours", False),
            ("8 hours", False),
        ],
        "explanation": "Let tank capacity = LCM(12, 15, 20) = 60 units.\nEfficiency: A = 5 units/hr, B = 4 units/hr, C = 3 units/hr.\nHour 1 (A + B): 5 + 4 = 9 units.\nHour 2 (A + C): 5 + 3 = 8 units.\nIn a 2-hour cycle: 9 + 8 = 17 units.\nIn 3 cycles (6 hours): 17 * 3 = 51 units filled. Remaining = 60 - 51 = 9 units.\nHour 7 (A + B turns): fills exactly 9 units.\nTotal time = 6 + 1 = 7 hours."
    },
    {
        "topic_id": 63,
        "question_text": "[UPSC ESE Prelims Paper-I — Permutations & Probability]\nIn an engineering quality test, 6 different components are arranged in a row. What is the probability that 2 specific critical components are always placed together?",
        "difficulty": "Medium",
        "options": [
            ("1/6", False),
            ("1/3", True),
            ("1/2", False),
            ("2/5", False),
        ],
        "explanation": "Total arrangements of 6 components = 6! = 720.\nTreat the 2 specific components as 1 block: we have 5 blocks arranged in 5! ways. Inside the block, the 2 components can be arranged in 2! ways.\nFavorable arrangements = 5! * 2! = 120 * 2 = 240.\nProbability = 240 / 720 = 1/3."
    },

    # ==================== TOPIC 64: Engineering Mathematics ====================
    {
        "topic_id": 64,
        "question_text": "[UPSC ESE Prelims Paper-I — Linear Algebra & Eigenvalues]\nFor a 3x3 matrix A, the eigenvalues are lambda_1 = 1, lambda_2 = 2, lambda_3 = 3. What is the trace and determinant of the inverse matrix A^(-1)?",
        "difficulty": "Medium",
        "options": [
            ("Trace = 6, Det = 6", False),
            ("Trace = 11/6, Det = 1/6", True),
            ("Trace = 1, Det = 0", False),
            ("Trace = 6, Det = 1/6", False),
        ],
        "explanation": "If eigenvalues of A are lambda_i, then eigenvalues of A^(-1) are 1/lambda_i.\nEigenvalues of A^(-1) = 1/1, 1/2, 1/3.\nTrace(A^(-1)) = sum of eigenvalues = 1 + 1/2 + 1/3 = 11/6.\nDet(A^(-1)) = product of eigenvalues = 1 * (1/2) * (1/3) = 1/6."
    },
    {
        "topic_id": 64,
        "question_text": "[UPSC ESE Prelims Paper-I — Vector Calculus]\nThe value of the line integral of F = (2xy + z^3) i + x^2 j + 3xz^2 k around any closed curve C is:",
        "difficulty": "Medium",
        "options": [
            ("Zero", True),
            ("2*pi", False),
            ("Area enclosed by C", False),
            ("Dependent on path shape", False),
        ],
        "explanation": "Check if F is irrotational: curl(F) = det([i, j, k; d/dx, d/dy, d/dz; 2xy+z^3, x^2, 3xz^2]) = i(0 - 0) - j(3z^2 - 3z^2) + k(2x - 2x) = 0.\nSince curl(F) = 0 everywhere, F is a conservative field (F = grad(phi)). By Stokes' theorem, the line integral of a conservative vector field around any closed path is strictly ZERO."
    },
    {
        "topic_id": 64,
        "question_text": "[UPSC ESE Prelims Paper-I — Numerical Analysis]\nIn solving an algebraic equation f(x) = 0 using Newton-Raphson method, the order of convergence is quadratic (p = 2) provided:",
        "difficulty": "Medium",
        "options": [
            ("The initial guess is equidistant between two roots", False),
            ("The root is a simple root such that f'(x_0) != 0 and f''(x_0) is finite", True),
            ("f(x) is a quadratic polynomial only", False),
            ("The error decreases linearly with each iteration", False),
        ],
        "explanation": "Newton-Raphson has quadratic convergence (p = 2, e_{n+1} approx C * e_n^2) specifically for simple roots where f'(alpha) != 0. If f'(alpha) = 0 (multiple root of multiplicity m > 1), convergence reduces to linear (p = 1)."
    },
    {
        "topic_id": 64,
        "question_text": "[UPSC ESE Prelims Paper-I — Complex Analysis]\nIf f(z) = u(x, y) + i v(x, y) is an analytic function in a domain D, which of the following is the Cauchy-Riemann equations in polar coordinates (r, theta)?",
        "difficulty": "Hard",
        "options": [
            ("du/dr = (1/r) dv/dtheta  and  dv/dr = -(1/r) du/dtheta", True),
            ("du/dr = dv/dtheta  and  dv/dr = -du/dtheta", False),
            ("r du/dr = dv/dtheta  and  r dv/dr = du/dtheta", False),
            ("du/dtheta = r dv/dr  and  dv/dtheta = -r du/dr", False),
        ],
        "explanation": "In polar coordinates, Cauchy-Riemann conditions are: (du/dr) = (1/r)(dv/dtheta) and (dv/dr) = -(1/r)(du/dtheta)."
    },

    # ==================== TOPIC 65: Design, Drawing & Safety ====================
    {
        "topic_id": 65,
        "question_text": "[UPSC ESE Prelims Paper-I — Engineering Drawing N.D. Bhatt]\nIn orthographic projection, which of the following comparisons between First Angle Projection and Third Angle Projection is correct?",
        "difficulty": "Medium",
        "options": [
            ("In First Angle, the object lies between the observer and the plane of projection; in Third Angle, the projection plane lies between the observer and the object.", True),
            ("In First Angle, the top view is drawn above the front view; in Third Angle, the top view is drawn below the front view.", False),
            ("First Angle projection is standard in USA and Canada; Third Angle is standard in India (BIS) and Europe (ISO).", False),
            ("Both projections produce identical left and right side view locations relative to the front view.", False),
        ],
        "explanation": "In First Angle: Observer -> Object -> Plane. Top view is below front view; left side view is on the right of front view. (BIS / ISO standard).\nIn Third Angle: Observer -> Plane -> Object. Top view is above front view; left side view is on the left of front view. (ANSI/ASME standard)."
    },
    {
        "topic_id": 65,
        "question_text": "[UPSC ESE Prelims Paper-I — Conic Sections & Drawing]\nA point moves such that the ratio of its distance from a fixed point (focus) to its distance from a fixed straight line (directrix) is constant (eccentricity e). If e = 1, e < 1, and e > 1, the curves generated are respectively:",
        "difficulty": "Easy",
        "options": [
            ("Parabola, Ellipse, Hyperbola", True),
            ("Ellipse, Parabola, Hyperbola", False),
            ("Hyperbola, Ellipse, Parabola", False),
            ("Circle, Ellipse, Parabola", False),
        ],
        "explanation": "By definition of conics: e = 1 -> Parabola; e < 1 -> Ellipse; e > 1 -> Hyperbola; e = 0 -> Circle."
    },
    {
        "topic_id": 65,
        "question_text": "[UPSC ESE Prelims Paper-I — Industrial Safety Engineering]\nWhich of the following qualitative risk assessment techniques systematically uses guide words such as 'NO', 'MORE', 'LESS', 'REVERSE', 'AS WELL AS', 'PART OF' to identify potential operational deviations in chemical and process plants?",
        "difficulty": "Medium",
        "options": [
            ("Fault Tree Analysis (FTA)", False),
            ("Failure Mode and Effects Analysis (FMEA)", False),
            ("Hazard and Operability Study (HAZOP)", True),
            ("Event Tree Analysis (ETA)", False),
        ],
        "explanation": "HAZOP (Hazard and Operability Study) uses standardized guide words (No, More, Less, As well as, Part of, Reverse, Other than) combined with process parameters (Flow, Pressure, Temp, Level) to detect hazards."
    },
    {
        "topic_id": 65,
        "question_text": "[UPSC ESE Prelims Paper-I — Safety Engineering & Reliability]\nIn quantitative safety analysis, Fault Tree Analysis (FTA) is a:\n1. Top-down, deductive failure analysis method.\n2. Bottom-up, inductive failure analysis method.\n3. Technique where Boolean logic gates (AND gate, OR gate) combine lower-level basic events to produce an undesired top event.\nWhich of the above statements are correct?",
        "difficulty": "Medium",
        "options": [
            ("1 and 2 only", False),
            ("1 and 3 only", True),
            ("2 and 3 only", False),
            ("1, 2 and 3", False),
        ],
        "explanation": "FTA is a top-down, deductive methodology starting from an undesired top event (accident) down to basic component failures using Boolean logic (AND/OR). In contrast, FMEA/ETA are bottom-up, inductive methods."
    },

    # ==================== TOPIC 66: Standards & Quality Practices ====================
    {
        "topic_id": 66,
        "question_text": "[UPSC ESE Prelims Paper-I — Six Sigma Methodology]\nIn Six Sigma quality management, what is the defect rate corresponding to a true 6-sigma process capability when accounting for the standard 1.5-sigma long-term mean shift?",
        "difficulty": "Easy",
        "options": [
            ("66,807 Defects Per Million Opportunities (DPMO)", False),
            ("233 Defects Per Million Opportunities (DPMO)", False),
            ("3.4 Defects Per Million Opportunities (DPMO)", True),
            ("0.001 Defects Per Million Opportunities (DPMO)", False),
        ],
        "explanation": "With the standard Motorola 1.5 sigma shift, a 6-sigma process yields 99.99966% defect-free parts, which equals exactly 3.4 DPMO (Defects Per Million Opportunities)."
    },
    {
        "topic_id": 66,
        "question_text": "[UPSC ESE Prelims Paper-I — Taguchi Loss Function]\nAccording to Genichi Taguchi's Quality Philosophy, the societal quality loss function for a 'Nominal-is-Best' characteristic with target m and tolerance +/- Delta is given by:\nL(y) = k * (y - m)^2\nIf the cost to scrap/rework at the tolerance specification limit (y = m +/- 0.05 mm) is Rs 200, what is the quality loss when the produced dimension deviates by 0.02 mm from the target?",
        "difficulty": "Medium",
        "options": [
            ("Rs 16", False),
            ("Rs 32", True),
            ("Rs 64", False),
            ("Rs 80", False),
        ],
        "explanation": "At tolerance limit: L = 200 = k * (0.05)^2 = k * 0.0025 ==> k = 200 / 0.0025 = 80,000 Rs/mm^2.\nWhen deviation (y - m) = 0.02 mm:\nL = 80,000 * (0.02)^2 = 80,000 * 0.0004 = Rs 32."
    },
    {
        "topic_id": 66,
        "question_text": "[UPSC ESE Prelims Paper-I — ISO Management Standards]\nMatch List-I (ISO Standard) with List-II (Core Domain):\nList-I:\nA. ISO 9001\nB. ISO 14001\nC. ISO 45001\nD. ISO 50001\nList-II:\n1. Occupational Health & Safety\n2. Quality Management Systems\n3. Energy Management\n4. Environmental Management\nSelect the correct code:",
        "difficulty": "Easy",
        "options": [
            ("A-2, B-4, C-1, D-3", True),
            ("A-4, B-2, C-1, D-3", False),
            ("A-2, B-1, C-4, D-3", False),
            ("A-3, B-4, C-1, D-2", False),
        ],
        "explanation": "ISO 9001 = Quality Management; ISO 14001 = Environmental Management; ISO 45001 = Occupational Health and Safety; ISO 50001 = Energy Management Systems."
    },
    {
        "topic_id": 66,
        "question_text": "[UPSC ESE Prelims Paper-I — Statistical Process Control]\nWhich statistical control chart is used for monitoring the NUMBER OF DEFECTS (count of non-conformities) per unit when the inspection subgroup sample size is CONSTANT?",
        "difficulty": "Medium",
        "options": [
            ("p-chart", False),
            ("np-chart", False),
            ("c-chart", True),
            ("u-chart", False),
        ],
        "explanation": "c-chart: Count of defects with constant sample size (Poisson distribution).\nu-chart: Defect rate per unit with variable sample size.\np-chart: Fraction non-conforming (defective) with variable sample size (Binomial).\nnp-chart: Number of defectives with constant sample size (Binomial)."
    },

    # ==================== TOPIC 67: Energy & Environment ====================
    {
        "topic_id": 67,
        "question_text": "[UPSC ESE Prelims Paper-I — Environmental Pollution Gilbert Masters]\nWhen an environmental lapse rate (ELR) is greater than the dry adiabatic lapse rate (DALR = 9.8 deg C/km), the atmosphere is said to be superadiabatic (unstable). What type of smoke plume dispersion behavior is observed under this condition?",
        "difficulty": "Medium",
        "options": [
            ("Fanning plume", False),
            ("Looping plume", True),
            ("Coning plume", False),
            ("Lofting plume", False),
        ],
        "explanation": "When ELR > DALR (superadiabatic / unstable atmosphere with strong solar heating and convective turbulence), the plume exhibits high vertical rolling eddies termed LOOPING. While it disperses quickly, high ground-level concentrations can occur close to the stack."
    },
    {
        "topic_id": 67,
        "question_text": "[UPSC ESE Prelims Paper-I — Renewable Energy & Wind Betz Limit]\nAccording to Betz's law, the theoretical maximum aerodynamic efficiency (power coefficient C_p) that an ideal wind turbine rotor can extract from the kinetic energy of the incoming wind is:",
        "difficulty": "Easy",
        "options": [
            ("50.0%", False),
            ("59.3% (16/27)", True),
            ("66.7% (2/3)", False),
            ("75.0%", False),
        ],
        "explanation": "Derived by Albert Betz (1919) using 1D momentum theory: Maximum C_p = 16/27 approx 59.26% (occurring when downstream wake velocity v_2 = (1/3) v_1)."
    },
    {
        "topic_id": 67,
        "question_text": "[UPSC ESE Prelims Paper-I — International Environmental Treaties]\nUnder the Kigali Amendment to the Montreal Protocol, countries agreed to phase down the production and consumption of which class of greenhouse gases?",
        "difficulty": "Medium",
        "options": [
            ("Chlorofluorocarbons (CFCs)", False),
            ("Hydrochlorofluorocarbons (HCFCs)", False),
            ("Hydrofluorocarbons (HFCs)", True),
            ("Perfluorocarbons (PFCs)", False),
        ],
        "explanation": "The Kigali Amendment (2016) to the Montreal Protocol legally mandates the phase-down of Hydrofluorocarbons (HFCs), which do not deplete the ozone layer but are potent greenhouse gases with global warming potentials thousands of times higher than CO2."
    },
    {
        "topic_id": 67,
        "question_text": "[UPSC ESE Prelims Paper-I — Water Pollution & BOD Kinetics]\nA wastewater sample has an ultimate first-stage biochemical oxygen demand (L_0) of 300 mg/L. If the deoxygenation rate constant (base e) is k = 0.23 day^(-1), what is the 5-day BOD (BOD_5) of the sample? (Take e^(-1.15) approx 0.316)",
        "difficulty": "Medium",
        "options": [
            ("95 mg/L", False),
            ("150 mg/L", False),
            ("205 mg/L", True),
            ("285 mg/L", False),
        ],
        "explanation": "BOD_t = L_0 * (1 - e^(-k*t)).\nHere t = 5 days, k*t = 0.23 * 5 = 1.15.\nBOD_5 = 300 * (1 - e^(-1.15)) = 300 * (1 - 0.316) = 300 * 0.684 = 205.2 mg/L."
    },

    # ==================== TOPIC 68: Project Management ====================
    {
        "topic_id": 68,
        "question_text": "[UPSC ESE Prelims Paper-I — Project Management Prasanna Chandra]\nIn a PERT network, an activity has the following time estimates:\nOptimistic time (a) = 4 days\nMost likely time (m) = 7 days\nPessimistic time (b) = 16 days\nThe expected activity duration (t_e) and standard deviation (sigma) are respectively:",
        "difficulty": "Medium",
        "options": [
            ("7 days and 2 days", False),
            ("8 days and 2 days", True),
            ("8 days and 4 days", False),
            ("9 days and 2 days", False),
        ],
        "explanation": "Expected duration t_e = (a + 4m + b) / 6 = (4 + 4*7 + 16) / 6 = (4 + 28 + 16) / 6 = 48 / 6 = 8 days.\nStandard deviation sigma = (b - a) / 6 = (16 - 4) / 6 = 12 / 6 = 2 days."
    },
    {
        "topic_id": 68,
        "question_text": "[UPSC ESE Prelims Paper-I — Earned Value Management (EVM)]\nIn project performance monitoring, if Cost Variance (CV) is negative and Schedule Performance Index (SPI) is greater than 1.0, what does this indicate about the project status?",
        "difficulty": "Medium",
        "options": [
            ("Project is under budget and ahead of schedule", False),
            ("Project is over budget and ahead of schedule", True),
            ("Project is over budget and behind schedule", False),
            ("Project is under budget and behind schedule", False),
        ],
        "explanation": "Cost Variance CV = EV - AC. CV < 0 implies Actual Cost (AC) > Earned Value (EV), meaning OVER BUDGET.\nSchedule Performance Index SPI = EV / PV. SPI > 1.0 implies Earned Value (EV) > Planned Value (PV), meaning AHEAD OF SCHEDULE."
    },
    {
        "topic_id": 68,
        "question_text": "[UPSC ESE Prelims Paper-I — CPM Network Floats]\nIn Critical Path Method (CPM), which type of float represents the portion of total float within which an activity can be delayed without affecting the start of subsequent (succeeding) activities?",
        "difficulty": "Medium",
        "options": [
            ("Total Float", False),
            ("Free Float", True),
            ("Independent Float", False),
            ("Interfering Float", False),
        ],
        "explanation": "Free Float = Early Start of successor - Early Finish of activity = (E_j - E_i) - t_{ij}.\nFree float delays the activity without delaying the early start of ANY succeeding activity. (Total float can affect successor early start up to latest start)."
    },
    {
        "topic_id": 68,
        "question_text": "[UPSC ESE Prelims Paper-I — Project Crashing]\nWhen crashing a project network to compress schedule duration, the priority order for crashing activities is determined by:",
        "difficulty": "Medium",
        "options": [
            ("Crashing non-critical activities with the highest cost slope first", False),
            ("Crashing critical activities with the lowest cost slope first", True),
            ("Crashing activities with the longest duration regardless of critical path", False),
            ("Crashing critical activities with the highest normal cost first", False),
        ],
        "explanation": "Crashing rules:\n1. Only critical activities affect project completion time.\n2. To minimize cost penalty, always crash the critical activity having the LEAST cost slope (Cost Slope = (Crash Cost - Normal Cost) / (Normal Time - Crash Time))."
    }
]

def main():
    app = create_app()
    with app.app_context():
        added = 0
        for qd in QUESTIONS_DATA:
            # Check if identical question text exists in this topic
            ex = Question.query.filter_by(topic_id=qd["topic_id"], question_text=qd["question_text"]).first()
            if not ex:
                q = Question(
                    exam_id=1,
                    topic_id=qd["topic_id"],
                    question_type='MCQ',
                    question_text=qd["question_text"],
                    explanation_text=qd["explanation"],
                    difficulty_level=qd["difficulty"],
                    created_by_user_id=1,
                    visibility='public'
                )
                db.session.add(q)
                db.session.flush()

                for opt_txt, is_corr in qd["options"]:
                    db.session.add(MCQOption(question_id=q.id, option_text=opt_txt, is_correct=is_corr))
                added += 1

        db.session.commit()
        print(f"Successfully added {added} authentic UPSC ESE Prelims questions for Paper-I Topics 62-68!")

if __name__ == '__main__':
    main()
