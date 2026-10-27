# -*- coding: utf-8 -*-
"""
Seed authentic UPSC ESE Prelims MCQs for Paper-II Mechanical Engineering:
Wing C: Manufacturing, Industrial & Mechatronics (Topics 46 to 61)
Subject 9: Manufacturing & Production Engineering (Topics 46-51)
Subject 10: Industrial Engineering & Maintenance (Topics 52-56)
Subject 11: Mechatronics & Robotics (Topics 57-61)
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.question import Question, MCQOption

QUESTIONS = [
    # ==================== SUBJECT 9: MANUFACTURING & PRODUCTION ====================
    # Topic 46: Metal Casting
    {
        "topic_id": 46,
        "question_text": "[UPSC ESE Prelims — Chvorinov's Rule in Casting]\nAccording to Chvorinov's rule (t_s = C * (V / A)^2), to ensure directional solidification such that a riser solidifies AFTER the casting it feeds, the modulus of the riser (M_r = V_r / A_r) compared to the casting modulus (M_c = V_c / A_c) should satisfy:",
        "difficulty": "Easy",
        "options": [
            ("M_r >= 1.2 M_c", True),
            ("M_r <= 0.8 M_c", False),
            ("M_r = M_c / 2", False),
            ("M_r is independent of M_c", False)
        ],
        "explanation": "To ensure the riser stays molten until the casting has completely solidified and fed: t_{s,riser} > t_{s,casting} ==> (V_r/A_r)^2 > (V_c/A_c)^2. Standard foundry practice (Caine's rule / Modulus method) requires M_r >= 1.2 M_c (riser modulus at least 20% larger than casting modulus)."
    },
    {
        "topic_id": 46,
        "question_text": "[UPSC ESE Prelims — Gating System in Casting]\nIn an unpressurized gating system with gating ratio 1 : 2 : 4 (Sprue : Runner : Gate), which of the following is a characteristic feature?",
        "difficulty": "Medium",
        "options": [
            ("The choke area is at the bottom of the sprue, minimizing liquid metal entry velocity into the mould cavity and preventing air aspiration", True),
            ("The choke area is at the ingate, causing high velocity jetting into the mould cavity", False),
            ("The gating ratio creates severe turbulent flow suitable only for grey cast iron", False),
            ("The sprue is always designed with a cylindrical parallel shape", False)
        ],
        "explanation": "In an unpressurized gating system (e.g. 1 : 2 : 4 or 1 : 4 : 4), minimum area (choke) is at the sprue base. Metal flows slowly through larger runners and gates with minimum turbulence, preventing oxidation and air aspiration — essential for light reactive alloys (Al, Mg)."
    },
    {
        "topic_id": 46,
        "question_text": "[UPSC ESE Prelims — Casting Defects]\nThe casting defect known as 'Hot Tear' is caused primarily by:",
        "difficulty": "Medium",
        "options": [
            ("Severe restraint to thermal contraction during solidification due to high dry strength of the mould/core", True),
            ("High moisture content in the green sand generating excessive steam", False),
            ("Low pouring temperature causing premature freezing of metal streams", False),
            ("Excessive venting in the drag", False)
        ],
        "explanation": "Hot tears are jagged, irregular internal or surface cracks formed when solidifying metal contracts thermally while restrained mechanically by rigid cores or hard moulds lacking adequate collapsibility."
    },

    # Topic 47: Metal Forming
    {
        "topic_id": 47,
        "question_text": "[UPSC ESE Prelims — Metal Rolling Maximum Draft]\nIn flat rolling of a metal strip between two rolls of radius R, the maximum draft (Delta h_max = h_0 - h_f) that can be achieved in a single pass without pushing the strip is:",
        "difficulty": "Easy",
        "options": [
            ("Delta h_max = mu^2 * R", True),
            ("Delta h_max = mu * R", False),
            ("Delta h_max = mu * R^2", False),
            ("Delta h_max = 2 * mu * R", False)
        ],
        "explanation": "For self-entry into the roll gap: tan(alpha) <= mu. Since cos(alpha) = 1 - Delta h / (2R) approx 1 - alpha^2/2: alpha^2 approx Delta h / R. At the limit alpha = mu: Delta h_max = mu^2 * R."
    },
    {
        "topic_id": 47,
        "question_text": "[UPSC ESE Prelims — Sheet Metal Operations]\nIn a sheet metal blanking operation to produce a disc of diameter D from a plate of thickness t with radial clearance c, the punch and die sizes are chosen as:",
        "difficulty": "Medium",
        "options": [
            ("Die diameter = D;  Punch diameter = D - 2c", True),
            ("Punch diameter = D;  Die diameter = D + 2c", False),
            ("Both punch and die diameters are equal to D", False),
            ("Die diameter = D - 2c;  Punch diameter = D + 2c", False)
        ],
        "explanation": "In BLANKING: the blank (cut piece) is the useful product. The die controls blank size: Die diameter = D. Clearance is subtracted from punch: Punch diameter = D - 2c. (In PIERCING/PUNCHING: hole is useful -> Punch diameter = D, Die = D + 2c)."
    },
    {
        "topic_id": 47,
        "question_text": "[UPSC ESE Prelims — Extrusion Defects]\nDuring hot direct extrusion of an alloy billet, the formation of an internal chevron or center-burst defect is caused by:",
        "difficulty": "Medium",
        "options": [
            ("Secondary hydrostatic tensile stresses developed along the centerline of the deformation zone", True),
            ("Excessive friction between container wall and billet surface", False),
            ("Rapid surface oxidation at the die exit", False),
            ("Inadequate extrusion pressure at the dummy block", False)
        ],
        "explanation": "Chevron cracking (center-burst) occurs along the central axis of an extruded rod due to secondary hydrostatic tensile stresses arising when die angle is too large for a given small reduction."
    },

    # Topic 48: Metal Joining / Welding
    {
        "topic_id": 48,
        "question_text": "[UPSC ESE Prelims — Arc Welding Power Source Characteristics]\nA linear drooping V-I characteristic power source has open-circuit voltage V_oc = 80 V and short-circuit current I_sc = 300 A. If the arc voltage follows V = 20 + 0.1 I, what is the optimum arc current for maximum arc power?",
        "difficulty": "Hard",
        "options": [
            ("150 A", True),
            ("100 A", False),
            ("200 A", False),
            ("300 A", False)
        ],
        "explanation": "Drooping power source line: V = V_oc - (V_oc / I_sc) * I = 80 - (80/300) * I.\nArc power P = V * I = 80 I - (80/300) I^2.\nTo maximize arc power dP/dI = 0 ==> 80 - (160/300) I = 0 ==> I = 80 * 300 / 160 = 150 A."
    },
    {
        "topic_id": 48,
        "question_text": "[UPSC ESE Prelims — TIG Welding & Polarity]\nIn Tungsten Inert Gas (TIG) welding of Aluminum, which welding power configuration is preferred to achieve effective oxide-film cathodic cleaning without melting the non-consumable tungsten electrode?",
        "difficulty": "Medium",
        "options": [
            ("Alternating Current (AC)", True),
            ("Direct Current Straight Polarity (DCSP / DCEN)", False),
            ("Direct Current Reverse Polarity (DCRP / DCEP) continuously", False),
            ("High frequency Pulsed DCEN only", False)
        ],
        "explanation": "Aluminum forms a tenacious Al2O3 oxide film. During positive half-cycle (DCEP), electrons leave the plate, breaking the oxide layer (cathodic cleaning). During negative half-cycle (DCEN), electrons strike the plate, providing deep penetration and keeping tungsten cool. Hence AC is standard."
    },
    {
        "topic_id": 48,
        "question_text": "[UPSC ESE Prelims — Resistance Spot Welding]\nIn resistance spot welding of two 1.5 mm thick steel sheets with current 10,000 A for 0.1 s, if the contact resistance is 100 micro-ohms (10^(-4) Omega), the heat generated at the interface is:",
        "difficulty": "Easy",
        "options": [
            ("1,000 Joules", True),
            ("500 Joules", False),
            ("10,000 Joules", False),
            ("100 Joules", False)
        ],
        "explanation": "Joule heating: H = I^2 * R * t = (10,000)^2 * (100 * 10^(-6)) * 0.1 = 10^8 * 10^(-4) * 0.1 = 10,000 * 0.1 = 1,000 J."
    },

    # Topic 49: Metal Cutting & Machining
    {
        "topic_id": 49,
        "question_text": "[UPSC ESE Prelims — Merchant's Shear Angle Relationship]\nAccording to Ernst and Merchant's original minimum energy analysis for orthogonal machining, the shear angle phi is related to rake angle alpha and friction angle beta by:",
        "difficulty": "Easy",
        "options": [
            ("phi = pi / 4 - beta / 2 + alpha / 2", True),
            ("phi = pi / 2 - beta + alpha", False),
            ("phi = pi / 4 + beta / 2 - alpha / 2", False),
            ("phi = beta - alpha", False)
        ],
        "explanation": "Merchant's equation: 2 phi + beta - alpha = pi / 2 ==> phi = pi / 4 - beta / 2 + alpha / 2. (Lee & Shaffer's slip-line model gives phi + beta - alpha = pi / 4)."
    },
    {
        "topic_id": 49,
        "question_text": "[UPSC ESE Prelims — Taylor's Tool Life Equation]\nIn a turning test, doubling the cutting speed (2V) reduces the tool life to 1/8 of its original value (T/8). What is the Taylor tool life exponent n in V * T^n = C?",
        "difficulty": "Medium",
        "options": [
            ("0.33 (1/3)", True),
            ("0.50 (1/2)", False),
            ("0.25 (1/4)", False),
            ("0.10", False)
        ],
        "explanation": "V_1 * T_1^n = V_2 * T_2^n ==> V_1 * T_1^n = (2 V_1) * (T_1 / 8)^n.\n1 = 2 * (1/8)^n ==> 8^n = 2 ==> (2^3)^n = 2^1 ==> 3n = 1 ==> n = 1/3 approx 0.333."
    },
    {
        "topic_id": 49,
        "question_text": "[UPSC ESE Prelims — ASA Tool Signature]\nIn the American Standards Association (ASA) tool signature system, the sequence of angles and nose radius is:",
        "difficulty": "Easy",
        "options": [
            ("Back rake, Side rake, End relief, Side relief, End cutting edge, Side cutting edge, Nose radius", True),
            ("Side rake, Back rake, Side relief, End relief, Side cutting edge, End cutting edge, Nose radius", False),
            ("Back rake, Side rake, Side relief, End relief, End cutting edge, Side cutting edge, Nose radius", False),
            ("Inclination angle, Normal rake, Side relief, End relief, Principal cutting edge, Auxiliary cutting edge, Nose radius", False)
        ],
        "explanation": "ASA Signature: alpha_b - alpha_s - theta_e - theta_s - C_e - C_s - R (Back rake, Side rake, End relief, Side relief, End cutting edge, Side cutting edge, Nose radius in inches)."
    },

    # Topic 50: Machine Tools & Non-Traditional Machining
    {
        "topic_id": 50,
        "question_text": "[UPSC ESE Prelims — Non-Traditional Machining Material Removal Mechanisms]\nMatch List-I (Non-Traditional Machining Process) with List-II (Dominant Material Removal Mechanism):\nList-I:\nA. Ultrasonic Machining (USM)\nB. Electric Discharge Machining (EDM)\nC. Electrochemical Machining (ECM)\nD. Laser Beam Machining (LBM)\nList-II:\n1. Melting and vaporization by spark erosion\n2. Mechanical micro-chipping / erosion by abrasive slurry\n3. Thermal vaporization by focused coherent photon beam\n4. Anodic dissolution based on Faraday's laws of electrolysis\nSelect the correct code:",
        "difficulty": "Easy",
        "options": [
            ("A-2, B-1, C-4, D-3", True),
            ("A-1, B-2, C-4, D-3", False),
            ("A-2, B-4, C-1, D-3", False),
            ("A-4, B-1, C-2, D-3", False)
        ],
        "explanation": "USM = Abrasive erosion; EDM = Spark erosion / melting; ECM = Anodic electrochemical dissolution (zero tool wear); LBM = Laser thermal vaporization."
    },
    {
        "topic_id": 50,
        "question_text": "[UPSC ESE Prelims — EDM Dielectric & Tool Material]\nIn Electric Discharge Machining (EDM), which of the following statements is INCORRECT?",
        "difficulty": "Medium",
        "options": [
            ("The workpiece must be an electrical insulator like ceramic or glass", True),
            ("The dielectric fluid is commonly kerosene or deionized water", False),
            ("The tool is typically made of copper, brass, or graphite", False),
            ("There are zero physical cutting forces between tool and workpiece", False)
        ],
        "explanation": "Statement A is incorrect because EDM relies on spark discharges between conductors; therefore, both tool and workpiece MUST be electrically conductive. (USM is used for machining non-conductive ceramics/glass)."
    },
    {
        "topic_id": 50,
        "question_text": "[UPSC ESE Prelims — CNC Machine Coordinate System & G-Codes]\nIn CNC part programming, the preparatory codes G00, G01, G02, and G03 represent respectively:",
        "difficulty": "Easy",
        "options": [
            ("Rapid positioning, Linear interpolation, Circular interpolation clockwise, Circular interpolation counter-clockwise", True),
            ("Linear interpolation, Rapid positioning, Circular CW, Circular CCW", False),
            ("Dwell, Linear interpolation, Thread cutting, Circular interpolation", False),
            ("Incremental programming, Absolute programming, Feed per rev, Feed per min", False)
        ],
        "explanation": "Standard ISO G-codes: G00 = Rapid traverse (point-to-point); G01 = Linear interpolation at programmed feed rate; G02 = Circular interpolation Clockwise; G03 = Circular interpolation Counter-Clockwise."
    },

    # Topic 51: Metrology & Inspection
    {
        "topic_id": 51,
        "question_text": "[UPSC ESE Prelims — Taylor's Principle of Limit Gauging]\nAccording to Taylor's Principle of Limit Gauging, the GO and NOT GO plug gauges for inspecting a cylindrical hole should be designed such that:",
        "difficulty": "Medium",
        "options": [
            ("The GO gauge checks the Maximum Material Limit (minimum hole diameter) and should check all dimensions simultaneously, while NOT GO checks the Least Material Limit and should check only one dimension at a time", True),
            ("The GO gauge checks the Least Material Limit and NOT GO checks the Maximum Material Limit", False),
            ("Both GO and NOT GO gauges must be full-form spherical gauges", False),
            ("The GO gauge must never enter the hole", False)
        ],
        "explanation": "Taylor's Principle: GO gauge checks Maximum Material Condition (MMC: minimum hole size / maximum shaft size) and must incorporate full form. NOT GO gauge checks Least Material Condition (LMC) and should check a single element (e.g. pin gauge)."
    },
    {
        "topic_id": 51,
        "question_text": "[UPSC ESE Prelims — Standard Tolerance Unit]\nFor diameter steps up to 500 mm in the ISO system of limits and fits, the standard tolerance unit i (in micrometres) is given by (where D is geometric mean diameter in mm):",
        "difficulty": "Easy",
        "options": [
            ("i = 0.45 * D^(1/3) + 0.001 * D", True),
            ("i = 0.55 * D^(1/2) + 0.002 * D", False),
            ("i = 0.45 * D + 0.001 * D^(1/3)", False),
            ("i = 0.045 * D^(1/3)", False)
        ],
        "explanation": "Standard tolerance unit i = 0.45 * cbrt(D) + 0.001 * D (in microns, with D = sqrt(D_1 * D_2) in mm). IT6 = 10i, IT7 = 16i, IT8 = 25i, etc."
    },
    {
        "topic_id": 51,
        "question_text": "[UPSC ESE Prelims — Surface Roughness Parameters]\nIn surface metrology, the Center Line Average (CLA) or roughness average R_a is defined as:",
        "difficulty": "Easy",
        "options": [
            ("The arithmetic average of the absolute values of profile heights y(x) from the mean line over the evaluation length L", True),
            ("The root-mean-square value of deviations from the center line", False),
            ("The distance between highest peak and lowest valley (R_z)", False),
            ("The spacing between consecutive profile peaks", False)
        ],
        "explanation": "Roughness average R_a = (1 / L) * integral_0^L |y(x)| dx. It is the arithmetic mean of absolute vertical deviations from the mean line. (R_q or RMS is root-mean-square)."
    },

    # ==================== SUBJECT 10: INDUSTRIAL ENGINEERING & MAINTENANCE ====================
    # Topic 52: PPC & Line Balancing
    {
        "topic_id": 52,
        "question_text": "[UPSC ESE Prelims — Exponential Smoothing Forecast]\nThe forecast for the month of May was 500 units, but actual demand turned out to be 540 units. Using exponential smoothing with smoothing constant alpha = 0.3, the forecast for June is:",
        "difficulty": "Easy",
        "options": [
            ("512 units", True),
            ("520 units", False),
            ("540 units", False),
            ("506 units", False)
        ],
        "explanation": "F_{t+1} = F_t + alpha * (D_t - F_t) = 500 + 0.3 * (540 - 500) = 500 + 0.3 * 40 = 500 + 12 = 512 units."
    },
    {
        "topic_id": 52,
        "question_text": "[UPSC ESE Prelims — Assembly Line Balance Delay]\nAn assembly line has a cycle time of 2.0 minutes and 5 workstations. If the sum of task times is 8.0 minutes, the balance delay of the line is:",
        "difficulty": "Easy",
        "options": [
            ("20%", True),
            ("80%", False),
            ("25%", False),
            ("10%", False)
        ],
        "explanation": "Line efficiency eta = (sum t_i) / (N * T_c) = 8.0 / (5 * 2.0) = 8.0 / 10.0 = 80%.\nBalance delay d = 100% - eta = 100% - 80% = 20%."
    },
    {
        "topic_id": 52,
        "question_text": "[UPSC ESE Prelims — Material Requirements Planning (MRP)]\nWhich of the following are the THREE fundamental inputs to a Material Requirements Planning (MRP) system?",
        "difficulty": "Easy",
        "options": [
            ("Master Production Schedule (MPS), Bill of Materials (BOM), and Inventory Status Records", True),
            ("Sales forecast, Capacity plan, and Maintenance schedule", False),
            ("Time study records, Purchase orders, and Route sheets", False),
            ("Quality control charts, Vendor rating, and Cash flow statement", False)
        ],
        "explanation": "MRP requires 3 master inputs: 1. Master Production Schedule (what finished goods to make and when), 2. Bill of Materials (product structure / tree), 3. Inventory Status File (on-hand inventory, lead times, scheduled receipts)."
    },

    # Topic 53: Inventory Control
    {
        "topic_id": 53,
        "question_text": "[UPSC ESE Prelims — Economic Order Quantity (EOQ)]\nIf annual demand for an item doubles and order cost is halved, while holding cost remains constant, the Economic Order Quantity (EOQ):",
        "difficulty": "Easy",
        "options": [
            ("Remains unchanged", True),
            ("Doubles", False),
            ("Halves", False),
            ("Increases by 41.4% (sqrt(2))", False)
        ],
        "explanation": "EOQ = sqrt(2 * D * C_o / C_h). If D' = 2D and C_o' = C_o / 2: EOQ' = sqrt(2 * (2D) * (C_o / 2) / C_h) = sqrt(2 * D * C_o / C_h) = EOQ. The EOQ remains completely UNCHANGED."
    },
    {
        "topic_id": 53,
        "question_text": "[UPSC ESE Prelims — Production Order Quantity (EPQ)]\nIn the finite production rate model (EPQ) where production rate is P and consumption rate is d (P > d), the maximum inventory level reached in the warehouse is:",
        "difficulty": "Medium",
        "options": [
            ("Q * (1 - d / P)", True),
            ("Q", False),
            ("Q * (1 + d / P)", False),
            ("Q * (d / P)", False)
        ],
        "explanation": "During the production run time t_p = Q / P, inventory accumulates at rate (P - d). Maximum inventory = (P - d) * t_p = (P - d) * (Q / P) = Q * (1 - d / P)."
    },
    {
        "topic_id": 53,
        "question_text": "[UPSC ESE Prelims — ABC Inventory Classification]\nIn ABC inventory control, 'A' class items are characterized by:",
        "difficulty": "Easy",
        "options": [
            ("High annual consumption value (approx 70-80% of total expenditure) but low quantity of items (approx 10-15% of total parts)", True),
            ("High quantity of items with negligible monetary value", False),
            ("Items that are vital to prevent immediate plant shutdown regardless of cost", False),
            ("Items that are fast-moving with high turnover frequency", False)
        ],
        "explanation": "ABC is based on Pareto's 80/20 law: A-items represent ~10-15% of inventory count but account for ~70-80% of annual usage value (requiring stringent control, frequent ordering, and low safety stock)."
    },

    # Topic 54: Operations Research
    {
        "topic_id": 54,
        "question_text": "[UPSC ESE Prelims — Simplex Method Degeneracy]\nIn solving a Linear Programming Problem (LPP) by the Simplex method, degeneracy occurs when:",
        "difficulty": "Medium",
        "options": [
            ("There is a tie in the minimum ratio test for selecting the leaving basic variable, causing one or more basic variables to become zero in the next tableau", True),
            ("The objective function value increases without bound", False),
            ("All constraint coefficients in the pivot column are negative", False),
            ("An artificial variable appears in the objective function with coefficient -M", False)
        ],
        "explanation": "Degeneracy in Simplex occurs when two or more basic variables tie for the minimum ratio (X_B / a_{ir}), leading to a basic feasible solution with one or more basic variables equal to zero. This may lead to cycling."
    },
    {
        "topic_id": 54,
        "question_text": "[UPSC ESE Prelims — Transportation Problem Non-Degeneracy]\nFor a balanced transportation problem with m origins and n destinations, a basic feasible solution is non-degenerate if the number of allocated basic cells is strictly equal to:",
        "difficulty": "Easy",
        "options": [
            ("m + n - 1", True),
            ("m * n", False),
            ("m + n", False),
            ("m + n + 1", False)
        ],
        "explanation": "Non-degeneracy in an m x n transportation problem requires exactly m + n - 1 independent positive allocations without forming any closed loop."
    },
    {
        "topic_id": 54,
        "question_text": "[UPSC ESE Prelims — Queuing Theory M/M/1]\nAt an industrial service station, machinery arrives following Poisson distribution at 4 per hour, and service time is exponentially distributed with a mean rate of 6 per hour. What is the average number of machines in the system (L_s)?",
        "difficulty": "Medium",
        "options": [
            ("2.0 machines", True),
            ("1.5 machines", False),
            ("3.0 machines", False),
            ("0.67 machines", False)
        ],
        "explanation": "Arrival rate lambda = 4 / hr, service rate mu = 6 / hr.\nTraffic intensity rho = lambda / mu = 4 / 6 = 2/3.\nAverage number in system L_s = rho / (1 - rho) = (2/3) / (1 - 2/3) = (2/3) / (1/3) = 2.0 machines."
    },

    # Topic 55: Work Study & Ergonomics
    {
        "topic_id": 55,
        "question_text": "[UPSC ESE Prelims — Standard Time Calculation]\nIn a time study of an assembly operation, the observed cycle time is 2.0 minutes, the worker's performance rating is 120%, and company allowances are 15% of normal time. The standard time for the operation is:",
        "difficulty": "Easy",
        "options": [
            ("2.76 minutes", True),
            ("2.40 minutes", False),
            ("2.50 minutes", False),
            ("3.00 minutes", False)
        ],
        "explanation": "Normal Time NT = Observed Time * (Rating / 100) = 2.0 * (120 / 100) = 2.40 minutes.\nStandard Time ST = Normal Time * (1 + Allowance) = 2.40 * (1 + 0.15) = 2.40 * 1.15 = 2.76 minutes."
    },
    {
        "topic_id": 55,
        "question_text": "[UPSC ESE Prelims — Therbligs in Micro-Motion Study]\nIn micro-motion study developed by Frank and Lillian Gilbreth, fundamental hand and eye motions are divided into 17 basic units termed 'Therbligs'. Which of the following is considered an UNAVOIDABLE DELAY Therblig?",
        "difficulty": "Medium",
        "options": [
            ("A delay outside the operator's control, such as waiting for a machine cycle or power interruption", True),
            ("A delay caused by operator daydreaming or fatigue", False),
            ("The time taken to visually inspect a component", False),
            ("The motion of transporting an empty hand to reach an object", False)
        ],
        "explanation": "Unavoidable delay (symbol UD) is an idle delay beyond the operator's control (e.g. waiting for machine cycle). Avoidable delay (symbol AD) is operator-induced idling. (Transport empty is TE; Inspect is I)."
    },
    {
        "topic_id": 55,
        "question_text": "[UPSC ESE Prelims — Work Sampling Sample Size]\nIn Tippett's work sampling technique, the number of random observations N required for a confidence level of 95% (2 sigma) with relative accuracy s and estimated activity occurrence fraction p is:",
        "difficulty": "Easy",
        "options": [
            ("N = 4 * (1 - p) / (s^2 * p)", True),
            ("N = 2 * (1 - p) / (s * p)", False),
            ("N = 4 * p * (1 - p) / s^2", False),
            ("N = (1 - p) / (s^2 * p^2)", False)
        ],
        "explanation": "Standard work sampling formula: relative error s = 2 * sqrt(p(1 - p) / N) / p = 2 * sqrt((1 - p) / (N * p)). Squaring both sides yields: N = 4 * (1 - p) / (s^2 * p)."
    },

    # Topic 56: Maintenance & Reliability
    {
        "topic_id": 56,
        "question_text": "[UPSC ESE Prelims — Series System Reliability]\nA system consists of 3 independent components connected in SERIES with reliabilities 0.90, 0.90, and 0.80. The overall system reliability is:",
        "difficulty": "Easy",
        "options": [
            ("0.648 (64.8%)", True),
            ("0.800 (80.0%)", False),
            ("0.867 (86.7%)", False),
            ("0.998 (99.8%)", False)
        ],
        "explanation": "For a series system, all components must function: R_s = R_1 * R_2 * R_3 = 0.90 * 0.90 * 0.80 = 0.81 * 0.80 = 0.648."
    },
    {
        "topic_id": 56,
        "question_text": "[UPSC ESE Prelims — Overall Equipment Effectiveness (OEE)]\nOverall Equipment Effectiveness (OEE) in Total Productive Maintenance (TPM) is calculated by multiplying which three factors?",
        "difficulty": "Easy",
        "options": [
            ("Availability, Performance Rate, and Quality Rate", True),
            ("MTBF, MTTR, and Inherent Availability", False),
            ("Efficiency, Capacity, and Utilization", False),
            ("Reliability, Maintainability, and Safety", False)
        ],
        "explanation": "OEE = Availability * Performance * Quality. World class benchmark: Availability >= 90%, Performance >= 95%, Quality >= 99.9% ==> OEE >= 85%."
    },
    {
        "topic_id": 56,
        "question_text": "[UPSC ESE Prelims — Bathtub Curve Failure Phases]\nIn reliability engineering, the 'useful life' phase (flat bottom of the bathtub curve) is characterized by:",
        "difficulty": "Easy",
        "options": [
            ("A CONSTANT failure rate (lambda = constant), governed by exponential distribution", True),
            ("A linearly decreasing failure rate governed by Weibull distribution with beta < 1", False),
            ("A rapidly increasing failure rate due to wear and corrosion", False),
            ("Zero random failures", False)
        ],
        "explanation": "Bathtub curve: 1. Infant mortality: decreasing failure rate (burn-in); 2. Useful life: CONSTANT failure rate lambda (governed by exponential distribution R(t) = e^(-lambda*t)); 3. Wear-out: increasing failure rate."
    },

    # ==================== SUBJECT 11: MECHATRONICS & ROBOTICS ====================
    # Topic 57: Microprocessors & Interfacing
    {
        "topic_id": 57,
        "question_text": "[UPSC ESE Prelims — 8085 Microprocessor Interrupts]\nAmong the hardware interrupts of the 8085 microprocessor, which interrupt has the HIGHEST priority and is strictly NON-MASKABLE?",
        "difficulty": "Easy",
        "options": [
            ("TRAP (RST 4.5)", True),
            ("RST 7.5", False),
            ("RST 6.5", False),
            ("INTR", False)
        ],
        "explanation": "In 8085: TRAP (RST 4.5) has highest priority and is NON-MASKABLE (used for catastrophic events like power failure). Priority order: TRAP > RST 7.5 > RST 6.5 > RST 5.5 > INTR."
    },
    {
        "topic_id": 57,
        "question_text": "[UPSC ESE Prelims — Microprocessor Bus Architecture]\nIn the 8085 microprocessor, how many address lines and data lines are present, and what is the maximum directly addressable memory capacity?",
        "difficulty": "Easy",
        "options": [
            ("16 address lines, 8 data lines, and 64 KB memory (2^16 bytes)", True),
            ("8 address lines, 8 data lines, and 256 bytes memory", False),
            ("20 address lines, 16 data lines, and 1 MB memory", False),
            ("16 address lines, 16 data lines, and 128 KB memory", False)
        ],
        "explanation": "8085 is an 8-bit microprocessor with an 8-bit data bus (multiplexed AD0-AD7) and a 16-bit address bus (A0-A15). Direct memory addressability = 2^16 bytes = 65,536 bytes = 64 KB."
    },
    {
        "topic_id": 57,
        "question_text": "[UPSC ESE Prelims — Microcontroller Harvard vs Von Neumann]\nWhat is the fundamental architectural difference between a Harvard architecture microcontroller (such as PIC or AVR) and a Von Neumann architecture processor?",
        "difficulty": "Medium",
        "options": [
            ("Harvard architecture possesses physically separate memory buses and address spaces for program instructions and data, allowing simultaneous instruction fetch and data read/write", True),
            ("Harvard architecture uses a single shared bus for both instruction and data memory", False),
            ("Von Neumann architecture cannot execute instructions sequentially", False),
            ("Harvard architecture lacks an internal Arithmetic Logic Unit (ALU)", False)
        ],
        "explanation": "Von Neumann has a shared single bus for both instructions and data (creating a Von Neumann bottleneck). Harvard architecture uses physically independent memories and buses for program code (ROM) and data (RAM), allowing concurrent execution."
    },

    # Topic 58: Sensors & Actuators
    {
        "topic_id": 58,
        "question_text": "[UPSC ESE Prelims — LVDT Transducer]\nIn a Linear Variable Differential Transformer (LVDT), when the ferromagnetic core is at the exact central null position, the differential output voltage is ideally zero because:",
        "difficulty": "Easy",
        "options": [
            ("Equal and opposite voltages are induced in the two identical secondary windings connected in series opposition", True),
            ("The magnetic flux linking the primary becomes zero", False),
            ("The secondary coils are short-circuited", False),
            ("The core blocks the high-frequency AC carrier excitation", False)
        ],
        "explanation": "An LVDT consists of one primary coil and two identical secondary coils connected in series opposition (V_out = V_s1 - V_s2). At null position, flux linkage to both secondaries is identical, so V_s1 = V_s2 ==> V_out = 0."
    },
    {
        "topic_id": 58,
        "question_text": "[UPSC ESE Prelims — Piezoelectric Transducers]\nPiezoelectric sensors (using quartz crystals or PZT ceramics) are suitable for measuring:",
        "difficulty": "Medium",
        "options": [
            ("Dynamic forces, vibrations, and high-frequency transient pressures, but CANNOT measure static loads", True),
            ("Static weights and steady hydrostatic pressure", False),
            ("Only steady direct current voltages", False),
            ("Low-frequency drift over hours without signal loss", False)
        ],
        "explanation": "Piezoelectric elements generate charge Q proportional to applied stress (Q = d * F). However, under static load, the electric charge rapidly leaks away through the input impedance of the measuring amplifier. Hence, piezoelectric transducers CANNOT measure static forces."
    },
    {
        "topic_id": 58,
        "question_text": "[UPSC ESE Prelims — Stepper Motor Step Angle]\nA variable reluctance stepper motor has 8 stator poles and 6 rotor teeth. What is the step angle (beta) of the motor?",
        "difficulty": "Medium",
        "options": [
            ("15 degrees", True),
            ("30 degrees", False),
            ("7.5 degrees", False),
            ("45 degrees", False)
        ],
        "explanation": "Step angle beta = |N_s - N_r| / (N_s * N_r) * 360 deg = |8 - 6| / (8 * 6) * 360 deg = 2 / 48 * 360 = 360 / 24 = 15 degrees."
    },

    # Topic 59: Control Systems & PLC
    {
        "topic_id": 59,
        "question_text": "[UPSC ESE Prelims — PID Controller Actions]\nIn a closed-loop feedback control system, what is the specific effect of incorporating an Integral (I) control action into a Proportional (P) controller?",
        "difficulty": "Medium",
        "options": [
            ("It increases the system type number and completely eliminates the steady-state error, but tends to reduce stability and increase overshoot", True),
            ("It improves transient damping and reduces settling time", False),
            ("It provides anticipatory control against future rate of change of error", False),
            ("It decreases the order of the closed-loop system", False)
        ],
        "explanation": "Proportional action alone always produces steady-state offset error. Integral control (u(t) proportional to integral e dt) adds a pole at the origin (increasing system type by 1), driving steady-state error to zero; however, it adds phase lag (-90 deg), degrading stability margin."
    },
    {
        "topic_id": 59,
        "question_text": "[UPSC ESE Prelims — PLC Ladder Logic]\nIn Programmable Logic Controller (PLC) ladder logic programming, a 'Normally Open' (NO) contact associated with input I:1/0 behaves as:",
        "difficulty": "Easy",
        "options": [
            ("Open when de-energized (0) and passes power (true) when the external physical switch is activated (1)", True),
            ("Closed when de-energized and opens when activated", False),
            ("A memory timer that delays output by 5 seconds", False),
            ("An analog voltage level converter", False)
        ],
        "explanation": "Examine If Closed (XIC / Normally Open contact symbol --[ ]--): Evaluates to TRUE (passes logic rung continuity) if the corresponding input bit is 1 (energized / closed)."
    },
    {
        "topic_id": 59,
        "question_text": "[UPSC ESE Prelims — Signal Conditioning Op-Amp]\nAn operational amplifier circuit has feedback resistor R_f = 100 k-ohms and input resistor R_1 = 10 k-ohms connected in an inverting configuration. The closed-loop voltage gain (A_v) is:",
        "difficulty": "Easy",
        "options": [
            ("-10", True),
            ("+10", False),
            ("+11", False),
            ("-100", False)
        ],
        "explanation": "For an inverting op-amp amplifier: A_v = -R_f / R_1 = -100 / 10 = -10."
    },

    # Topic 60: Robotics Anatomy & DH Parameters
    {
        "topic_id": 60,
        "question_text": "[UPSC ESE Prelims — Robot Degrees of Freedom (DOF)]\nHow many degrees of freedom (DOF) are required for a spatial robot manipulator to achieve arbitrary position (x, y, z) and arbitrary orientation (roll, pitch, yaw) of its end-effector in 3D workspace?",
        "difficulty": "Easy",
        "options": [
            ("6 DOF (3 for position + 3 for orientation)", True),
            ("3 DOF", False),
            ("4 DOF", False),
            ("12 DOF", False)
        ],
        "explanation": "A rigid body in 3D space possesses 6 degrees of freedom: 3 translational (x, y, z position) typically provided by regional base/arm joints, and 3 rotational (roll, pitch, yaw orientation) provided by a spherical wrist."
    },
    {
        "topic_id": 60,
        "question_text": "[UPSC ESE Prelims — Denavit-Hartenberg (DH) Parameters]\nIn robotics kinematic modeling, how many DH parameters are required to relate any two consecutive coordinate frames (Link i-1 and Link i), and what are they?",
        "difficulty": "Medium",
        "options": [
            ("4 parameters: Link length (a_i), Link twist (alpha_i), Link offset (d_i), and Joint angle (theta_i)", True),
            ("6 parameters: 3 translations and 3 Euler angles", False),
            ("3 parameters: x, y, and z coordinates", False),
            ("2 parameters: Link length and rotation matrix", False)
        ],
        "explanation": "Denavit-Hartenberg convention describes 3D joint-link relationships using exactly 4 parameters: two link parameters (length a_i along x_i, twist alpha_i about x_i) and two joint parameters (offset d_i along z_{i-1}, angle theta_i about z_{i-1})."
    },
    {
        "topic_id": 60,
        "question_text": "[UPSC ESE Prelims — SCARA Robot Configuration]\nA SCARA (Selective Compliance Assembly Robot Arm) manipulator has which kinematic joint configuration?",
        "difficulty": "Easy",
        "options": [
            ("R-R-P (Two revolute joints with vertical parallel axes for horizontal compliance, and one prismatic joint for vertical insertion)", True),
            ("P-P-P (Cartesian gantry configuration)", False),
            ("R-R-R (Articulated anthropomorphic arm)", False),
            ("R-P-P (Cylindrical robot arm)", False)
        ],
        "explanation": "SCARA robot has an RRP joint configuration. The two revolute joints move in horizontal plane (selective compliance for peg-in-hole assembly) while a third prismatic joint provides vertical motion with high vertical rigidity."
    },

    # Topic 61: Robot Kinematics & Applications
    {
        "topic_id": 61,
        "question_text": "[UPSC ESE Prelims — Forward vs Inverse Kinematics in Robotics]\nWhich of the following statements correctly compares Forward Kinematics with Inverse Kinematics of an industrial robot arm?",
        "difficulty": "Medium",
        "options": [
            ("Forward kinematics computes end-effector pose from known joint angles and always has a unique closed-form solution, while inverse kinematics computes joint angles from desired end-effector pose and may have multiple solutions or no solution (singularities)", True),
            ("Forward kinematics is computationally much more complex and non-linear than inverse kinematics", False),
            ("Inverse kinematics always guarantees a single unique mathematical solution", False),
            ("Neither kinematics problem depends on link lengths or joint angles", False)
        ],
        "explanation": "Forward kinematics: q -> [x, y, z, roll, pitch, yaw]^T (always unique via matrix multiplication). Inverse kinematics: pose -> q (highly non-linear, involves transcendental trigonometric equations, often yields multiple solutions [elbow up/down, wrist flipped] or no solution outside workspace, and exhibits singularities where Jacobian determinant is zero)."
    },
    {
        "topic_id": 61,
        "question_text": "[UPSC ESE Prelims — Robot Jacobian & Singularities]\nAt a kinematic SINGULARITY of a robot manipulator, which of the following phenomena occurs?",
        "difficulty": "Medium",
        "options": [
            ("The robot loses one or more degrees of freedom, the Jacobian matrix loses rank (det(J) = 0), and infinite joint rates may be required to maintain Cartesian trajectory", True),
            ("The robot gains extra degrees of freedom and moves with infinite speed", False),
            ("The end-effector payload capacity drops to zero", False),
            ("All joints lock permanently and cannot be powered", False)
        ],
        "explanation": "Singularities occur when det(J) = 0. The manipulator loses the ability to move or exert force in certain Cartesian directions. If trajectory planning attempts to command motion along the lost direction, inverse Jacobian yields infinite joint velocity."
    },
    {
        "topic_id": 61,
        "question_text": "[UPSC ESE Prelims — Robot Trajectory Planning]\nIn industrial robotic trajectory planning, why are Cubic and Quintic polynomial splines preferred over simple linear interpolation for joint trajectories?",
        "difficulty": "Medium",
        "options": [
            ("To guarantee continuous velocity and continuous acceleration (eliminating infinite jerk) at starting, via, and goal points", True),
            ("To maximize the maximum actuator speed", False),
            ("To ensure the robot arm strictly follows a circular path", False),
            ("To prevent joint sensors from overheating", False)
        ],
        "explanation": "Linear trajectory interpolation causes abrupt velocity steps and infinite acceleration (shocks/vibrations). Cubic (3rd degree) polynomials ensure smooth positions and velocities. Quintic (5th degree) splines ensure continuous acceleration (finite jerk) from rest to rest, preserving motor and gearbox life."
    }
]

def main():
    app = create_app()
    with app.app_context():
        added = 0
        for qd in QUESTIONS:
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
        print(f"Successfully added {added} authentic UPSC ESE Prelims questions for Wing C: Manufacturing, Industrial & Mechatronics (Topics 46-61)!")

if __name__ == '__main__':
    main()
