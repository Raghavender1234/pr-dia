# -*- coding: utf-8 -*-
"""
Seed authentic UPSC ESE Prelims MCQs for Paper-II Mechanical Engineering:
Wing B: Design, Mechanics & Materials (Topics 23 to 45)
Subject 5: Theory of Machines & Vibrations (Topics 23-28)
Subject 6: Strength of Materials (Topics 29-34)
Subject 7: Machine Design (Topics 35-40)
Subject 8: Engineering Materials (Topics 41-45)
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.question import Question, MCQOption

QUESTIONS = [
    # ==================== SUBJECT 5: THEORY OF MACHINES & VIBRATIONS ====================
    # Topic 23: Mechanisms & Velocity/Acceleration
    {
        "topic_id": 23,
        "question_text": "[UPSC ESE Prelims — Grubler's Mobility Criterion]\nFor a planar kinematic mechanism with n links, j simple binary revolute joints (single degree of freedom), and h higher pairs (two degrees of freedom), Grubler's criterion for degrees of freedom (F) is given by:",
        "difficulty": "Easy",
        "options": [
            ("F = 3(n - 1) - 2j - h", True),
            ("F = 3n - 2j - h", False),
            ("F = 2(n - 1) - 3j - h", False),
            ("F = 3(n - 1) - j - 2h", False)
        ],
        "explanation": "Kutzbach-Grubler criterion for planar mechanisms: F = 3(n - 1) - 2j_1 - j_2 = 3(n - 1) - 2j - h."
    },
    {
        "topic_id": 23,
        "question_text": "[UPSC ESE Prelims — Coriolis Acceleration]\nA slider moves with a relative velocity v along a link rotating with uniform angular velocity omega. The Coriolis component of acceleration has a magnitude and direction given by:",
        "difficulty": "Medium",
        "options": [
            ("Magnitude 2 * omega * v, directed by rotating the relative velocity vector v through 90 degrees in the sense of omega", True),
            ("Magnitude omega * v, directed parallel to the sliding link", False),
            ("Magnitude 2 * omega^2 * r, directed towards the center of rotation", False),
            ("Magnitude omega * v^2 / r, directed perpendicular to the link", False)
        ],
        "explanation": "Coriolis acceleration a_c = 2 * omega * v. Its direction is obtained by rotating the relative velocity vector v by 90 degrees in the direction of the link's angular velocity vector omega."
    },
    {
        "topic_id": 23,
        "question_text": "[UPSC ESE Prelims — Inversions of Kinematic Chains]\nWhich of the following mechanisms is obtained as an inversion of the Double Slider-Crank chain?",
        "difficulty": "Easy",
        "options": [
            ("Elliptical Trammel and Scotch Yoke mechanism", True),
            ("Whitworth Quick Return and Crank & Slotted Lever mechanism", False),
            ("Gnome engine and Pendulum pump", False),
            ("Ackermann steering mechanism", False)
        ],
        "explanation": "Double Slider-Crank inversions: 1. Elliptical trammel (slotted plate fixed), 2. Scotch yoke mechanism (slider 1 fixed), 3. Oldham's coupling (intermediate link fixed). (Whitworth and Crank & Slotted Lever are inversions of Single Slider-Crank chain)."
    },

    # Topic 24: Dynamic Force Analysis & Flywheels
    {
        "topic_id": 24,
        "question_text": "[UPSC ESE Prelims — Flywheel Energy Equation]\nIn a machine with turning moment diagram, the maximum fluctuation of energy is Delta E = 1200 J. If the mean angular speed is omega = 50 rad/s and coefficient of fluctuation of speed is C_s = 0.02, what is the required mass moment of inertia (I) of the flywheel?",
        "difficulty": "Medium",
        "options": [
            ("24 kg*m^2", True),
            ("12 kg*m^2", False),
            ("48 kg*m^2", False),
            ("6 kg*m^2", False)
        ],
        "explanation": "Delta E = I * omega^2 * C_s.\n1200 = I * (50)^2 * 0.02 = I * 2500 * 0.02 = I * 50.\nI = 1200 / 50 = 24 kg*m^2."
    },
    {
        "topic_id": 24,
        "question_text": "[UPSC ESE Prelims — Flywheel vs Governor]\nWhich of the following statements correctly distinguishes the operational function of a Flywheel from a Governor?",
        "difficulty": "Medium",
        "options": [
            ("A flywheel controls cyclic speed variations within each single engine cycle, while a governor regulates mean speed variations across multiple cycles caused by varying external loads", True),
            ("A governor controls cyclic energy fluctuations by varying fuel supply within a stroke", False),
            ("A flywheel acts as an active sensor; a governor stores kinetic energy passively", False),
            ("A flywheel maintains constant mean speed when the external load changes permanently", False)
        ],
        "explanation": "A flywheel is a passive energy reservoir that smooths out cyclic fluctuations of torque within one thermodynamic cycle without altering fuel supply. A governor is an active control device that adjusts fuel supply when external load changes to maintain constant mean speed over time."
    },
    {
        "topic_id": 24,
        "question_text": "[UPSC ESE Prelims — Equivalent Dynamic System]\nIn dynamic equivalence of a rigid link of mass m, moment of inertia I_G about its CG, replaced by two dynamically equivalent point masses m_1 and m_2 at distances L_1 and L_2 from CG, the required conditions are:",
        "difficulty": "Medium",
        "options": [
            ("m_1 + m_2 = m;  m_1 * L_1 = m_2 * L_2;  and  L_1 * L_2 = k_G^2", True),
            ("m_1 = m_2 = m/2;  L_1 = L_2 = k_G", False),
            ("m_1 + m_2 = m;  L_1 + L_2 = k_G", False),
            ("m_1 * L_1^2 + m_2 * L_2^2 = m * k_G", False)
        ],
        "explanation": "Conditions for dynamic equivalence: 1. Total mass: m_1 + m_2 = m; 2. Center of gravity unchanged: m_1 * L_1 = m_2 * L_2; 3. Mass moment of inertia unchanged: m_1 * L_1^2 + m_2 * L_2^2 = I_G = m * k_G^2. Combining (1) and (2) with (3) yields the golden rule: L_1 * L_2 = k_G^2."
    },

    # Topic 25: Gears & Gear Trains
    {
        "topic_id": 25,
        "question_text": "[UPSC ESE Prelims — Involute Gear Interference]\nTo avoid interference between two standard 20-degree full-depth involute spur gear teeth, the minimum number of teeth on the pinion (T_min) meshing with an equal gear is:",
        "difficulty": "Easy",
        "options": [
            ("14", False),
            ("18", True),
            ("12", False),
            ("24", False)
        ],
        "explanation": "T_min = 2 * A_w / (sin^2 phi). For standard full-depth teeth (addendum coefficient A_w = 1) and pressure angle phi = 20 deg: T_min = 2 / sin^2(20 deg) = 2 / (0.342)^2 = 2 / 0.117 approx 17.1 ==> minimum 18 teeth. (For 14.5 deg: T_min = 32)."
    },
    {
        "topic_id": 25,
        "question_text": "[UPSC ESE Prelims — Law of Gearing]\nThe fundamental Law of Gearing for constant angular velocity ratio requires that:",
        "difficulty": "Easy",
        "options": [
            ("The common normal to the tooth profiles at the point of contact must always pass through a fixed point called the pitch point", True),
            ("The contact path must be a straight line only", False),
            ("The root circle diameter must equal base circle diameter", False),
            ("The pitch circle diameters of mating gears must be identical", False)
        ],
        "explanation": "The Law of Gearing states that for a constant angular velocity ratio between two mating gears, the common normal to the contacting tooth profiles at all points of contact must pass through the fixed pitch point."
    },
    {
        "topic_id": 25,
        "question_text": "[UPSC ESE Prelims — Epicyclic Gear Trains]\nIn an epicyclic gear train, arm A rotates at 100 rpm clockwise. Sun gear S (20 teeth) is fixed. The number of teeth on the annular ring gear R is 80 teeth. What is the speed of ring gear R?",
        "difficulty": "Hard",
        "options": [
            ("125 rpm clockwise", True),
            ("100 rpm counter-clockwise", False),
            ("75 rpm clockwise", False),
            ("80 rpm counter-clockwise", False)
        ],
        "explanation": "Tabular method: Give +y to all members (arm speed = y = +100 rpm).\nFix arm, give +x to Sun gear S: N_S = y + x = 0 (since Sun is fixed ==> x = -y = -100 rpm).\nRing gear R speed relative to arm: (N_R - y) / (N_S - y) = -T_S / T_R (external/internal meshing: sun to planet is external -, planet to annular is internal + ==> overall ratio is -T_S / T_R = -20/80 = -1/4).\n(N_R - 100) / (-100) = -1/4 ==> N_R - 100 = 25 ==> N_R = 125 rpm clockwise."
    },

    # Topic 26: Governors & Gyroscope
    {
        "topic_id": 26,
        "question_text": "[UPSC ESE Prelims — Hartnell Governor]\nA Hartnell governor is classified as which type of governor?",
        "difficulty": "Easy",
        "options": [
            ("Spring-controlled centrifugal governor", True),
            ("Gravity-controlled dead weight governor", False),
            ("Pure inertia governor", False),
            ("Pendulum type governor", False)
        ],
        "explanation": "Hartnell governor is a spring-loaded centrifugal governor with bell-crank levers, where controlling force is supplied by a helical compression spring. (Watt, Porter, and Proell are gravity-controlled governors)."
    },
    {
        "topic_id": 26,
        "question_text": "[UPSC ESE Prelims — Gyroscopic Couple]\nA naval ship has its turbine rotor spinning clockwise when viewed from the stern (aft). If the ship makes a left (port) turn, the gyroscopic couple will cause the ship to:",
        "difficulty": "Medium",
        "options": [
            ("Dip the bow (nose) and raise the stern", True),
            ("Raise the bow and dip the stern", False),
            ("Roll towards the port side", False),
            ("Roll towards the starboard side", False)
        ],
        "explanation": "Spin vector points forward (from stern to bow). In a port (left) turn, precession vector points vertically upwards. By right-hand screw rule, the reactive gyroscopic couple tilts the nose (bow) DOWNWARDS and raises the stern."
    },
    {
        "topic_id": 26,
        "question_text": "[UPSC ESE Prelims — Governor Sensitiveness & Hunting]\nA centrifugal governor that is excessively sensitive and continuously fluctuates above and below the mean equilibrium speed with small load variations is said to be:",
        "difficulty": "Easy",
        "options": [
            ("Hunting", True),
            ("Isochronous", False),
            ("Stable", False),
            ("Insensitive", False)
        ],
        "explanation": "Hunting is the phenomenon where a governor fluctuates continuously above and below the mean speed. It is caused by an over-sensitive governor with inadequate damping friction."
    },

    # Topic 27: Balancing & Cams
    {
        "topic_id": 27,
        "question_text": "[UPSC ESE Prelims — Primary vs Secondary Unbalance]\nIn a single-cylinder reciprocating engine, what is the magnitude of the maximum primary unbalanced force and maximum secondary unbalanced force (reciprocating mass m, crank radius r, connecting rod length l = n*r, crank speed omega)?",
        "difficulty": "Medium",
        "options": [
            ("Primary = m * r * omega^2;  Secondary = m * r * omega^2 / n", True),
            ("Primary = m * r * omega^2 / n;  Secondary = m * r * omega^2", False),
            ("Primary = m * r * omega^2;  Secondary = m * r * omega^2 * n", False),
            ("Both are equal to m * r * omega^2", False)
        ],
        "explanation": "Inertia force of reciprocating parts: F_unbalanced = m * r * omega^2 * [cos(theta) + cos(2*theta) / n]. Primary maximum occurs at cos(theta) = 1 (magnitude m * r * omega^2). Secondary maximum occurs at cos(2*theta) = 1 (magnitude m * r * omega^2 / n, occurring at twice engine speed)."
    },
    {
        "topic_id": 27,
        "question_text": "[UPSC ESE Prelims — Cam Follower Motion]\nWhich follower motion curve produces ZERO acceleration at both the beginning and end of stroke, completely avoiding infinite jerk (shock/impact) and making it ideal for high-speed cams?",
        "difficulty": "Medium",
        "options": [
            ("Cycloidal motion", True),
            ("Simple Harmonic Motion (SHM)", False),
            ("Uniform Velocity motion", False),
            ("Uniform Acceleration and Retardation (Parabolic motion)", False)
        ],
        "explanation": "Cycloidal motion has smooth zero acceleration at the start and end of stroke, yielding continuous finite jerk without sudden spikes. SHM has maximum acceleration at ends, causing jerk discontinuities; parabolic motion has abrupt acceleration steps."
    },
    {
        "topic_id": 27,
        "question_text": "[UPSC ESE Prelims — Complete Dynamic Balance of Rotating Masses]\nFor complete dynamic balancing of several masses rotating in different planes on a shaft, which conditions must be satisfied simultaneously?",
        "difficulty": "Easy",
        "options": [
            ("Resultant dynamic force must be zero (sum m*r = 0) AND resultant dynamic couple must be zero (sum m*r*l = 0)", True),
            ("Only the resultant centrifugal force must be zero", False),
            ("All masses must lie in the same transverse plane", False),
            ("The shaft must rotate at its critical whirling speed", False)
        ],
        "explanation": "Static balance requires sum F = 0 (polygon of centrifugal forces closes). Complete dynamic balance requires BOTH sum F = 0 (no net force) AND sum M = 0 (couple polygon closes)."
    },

    # Topic 28: Mechanical Vibrations
    {
        "topic_id": 28,
        "question_text": "[UPSC ESE Prelims — Vibration Transmissibility]\nIn vibration isolation of a machine mounting, the force transmissibility (epsilon) is less than 1 (meaning isolation is effective) ONLY when the frequency ratio (omega / omega_n) satisfies:",
        "difficulty": "Easy",
        "options": [
            ("omega / omega_n > sqrt(2)", True),
            ("omega / omega_n < 1", False),
            ("omega / omega_n = 1", False),
            ("1 < omega / omega_n < sqrt(2)", False)
        ],
        "explanation": "Transmissibility formula epsilon = sqrt(1 + (2*zeta*r)^2) / sqrt((1 - r^2)^2 + (2*zeta*r)^2). When r = omega/omega_n = sqrt(2), epsilon = 1 for all damping ratios. When r > sqrt(2), epsilon < 1, providing true vibration isolation."
    },
    {
        "topic_id": 28,
        "question_text": "[UPSC ESE Prelims — Critical Whirling Speed of Shafts]\nThe critical or whirling speed of a shaft carrying a rotor coincides mathematically with:",
        "difficulty": "Easy",
        "options": [
            ("The natural frequency of transverse vibration of the shaft-rotor system", True),
            ("The natural frequency of torsional vibration", False),
            ("Twice the longitudinal vibration frequency", False),
            ("Half the torsional critical speed", False)
        ],
        "explanation": "Whirling speed is the rotational speed at which the shaft deflects radially and vibrates violently. It equals the natural frequency of transverse (lateral) vibration: omega_cr = sqrt(g / delta_static)."
    },
    {
        "topic_id": 28,
        "question_text": "[UPSC ESE Prelims — Logarithmic Decrement]\nIn a viscously damped free vibration system, the ratio of any two successive displacement amplitudes is x_1 / x_2 = 2.718 (e). What is the logarithmic decrement (delta) of the system?",
        "difficulty": "Easy",
        "options": [
            ("1.0", True),
            ("0.5", False),
            ("2.0", False),
            ("0.1", False)
        ],
        "explanation": "Logarithmic decrement delta = ln(x_1 / x_2) = ln(e) = 1.0. (Also delta = 2 * pi * zeta / sqrt(1 - zeta^2))."
    },

    # ==================== SUBJECT 6: STRENGTH OF MATERIALS ====================
    # Topic 29: Stress, Strain & Elastic Constants
    {
        "topic_id": 29,
        "question_text": "[UPSC ESE Prelims — Elastic Constants Relation]\nFor an isotropic, homogeneous linear elastic material, what is the exact mathematical relationship between Young's Modulus (E), Shear Modulus (G), and Bulk Modulus (K)?",
        "difficulty": "Easy",
        "options": [
            ("E = 9KG / (3K + G)", True),
            ("E = 3KG / (9K + G)", False),
            ("E = 9KG / (K + 3G)", False),
            ("E = 6KG / (3K + G)", False)
        ],
        "explanation": "Standard elastic relations: E = 2G(1 + mu) and E = 3K(1 - 2mu). Eliminating Poisson's ratio mu gives: E = 9KG / (3K + G)."
    },
    {
        "topic_id": 29,
        "question_text": "[UPSC ESE Prelims — Mohr's Circle of Stress]\nAt a point in a strained material, the state of stress is pure shear of magnitude tau (sigma_x = 0, sigma_y = 0, tau_xy = tau). The radius of Mohr's circle and the principal stresses are respectively:",
        "difficulty": "Easy",
        "options": [
            ("Radius = tau; Principal stresses are +tau and -tau", True),
            ("Radius = 2*tau; Principal stresses are +tau and 0", False),
            ("Radius = 0; Principal stresses are zero", False),
            ("Radius = tau / 2; Principal stresses are +tau/2 and -tau/2", False)
        ],
        "explanation": "Center = ((sigma_x + sigma_y)/2, 0) = (0, 0). Radius R = sqrt(((sigma_x - sigma_y)/2)^2 + tau_xy^2) = sqrt(0 + tau^2) = tau. Principal stresses sigma_1,2 = Center +/- R = +/- tau."
    },
    {
        "topic_id": 29,
        "question_text": "[UPSC ESE Prelims — Thermal Stress in Constrained Rod]\nA steel bar of length L, cross-sectional area A, Young's modulus E, and coefficient of thermal expansion alpha is rigidly fixed between two unyielding walls. If its temperature is raised by Delta T, the thermal stress induced in the bar is:",
        "difficulty": "Easy",
        "options": [
            ("alpha * E * Delta T (Compressive)", True),
            ("alpha * E * Delta T (Tensile)", False),
            ("alpha * Delta T / E (Compressive)", False),
            ("Zero, because displacement is prevented", False)
        ],
        "explanation": "Free expansion delta = L * alpha * Delta T. Since fixed walls prevent expansion, compressive strain epsilon = delta / L = alpha * Delta T. Compressive stress sigma = E * epsilon = alpha * E * Delta T."
    },

    # Topic 30: Theories of Elastic Failure
    {
        "topic_id": 30,
        "question_text": "[UPSC ESE Prelims — Theories of Failure Tresca vs Von Mises]\nFor ductile materials subjected to pure shear stress tau, the maximum shear stress theory (Tresca) and the distortion energy theory (Von Mises) predict the yield strength in shear (S_ys) as:",
        "difficulty": "Medium",
        "options": [
            ("Tresca: S_ys = 0.50 S_yt;  Von Mises: S_ys = 0.577 S_yt (S_yt / sqrt(3))", True),
            ("Tresca: S_ys = 0.577 S_yt;  Von Mises: S_ys = 0.50 S_yt", False),
            ("Tresca: S_ys = S_yt;  Von Mises: S_ys = 0.5 S_yt", False),
            ("Both theories predict S_ys = 0.50 S_yt", False)
        ],
        "explanation": "Under pure shear (sigma_1 = tau, sigma_2 = -tau, sigma_3 = 0):\nTresca: tau_max = (sigma_1 - sigma_2)/2 = tau = S_yt / 2 ==> S_ys = 0.50 S_yt.\nVon Mises: sigma_vm = sqrt(3) * tau = S_yt ==> S_ys = S_yt / sqrt(3) approx 0.577 S_yt."
    },
    {
        "topic_id": 30,
        "question_text": "[UPSC ESE Prelims — Maximum Principal Stress Theory (Rankine)]\nRankine's Maximum Principal Stress Theory is most suitable and accurately predicts failure for:",
        "difficulty": "Easy",
        "options": [
            ("Brittle materials (like cast iron and concrete) under tensile loads", True),
            ("Ductile materials under pure shear", False),
            ("Ductile materials under hydrostatic pressure", False),
            ("Rubber and highly elastic polymers", False)
        ],
        "explanation": "Rankine's theory (failure occurs when maximum tensile principal stress reaches yield/ultimate strength) provides excellent agreement for brittle materials like cast iron, rock, and glass."
    },
    {
        "topic_id": 30,
        "question_text": "[UPSC ESE Prelims — Hydrostatic Stress & Distortion Energy]\nWhen a material is subjected to equal hydrostatic triaxial tensile stress (sigma_1 = sigma_2 = sigma_3 = sigma), the Von Mises equivalent stress is:",
        "difficulty": "Easy",
        "options": [
            ("Zero", True),
            ("sigma", False),
            ("3 * sigma", False),
            ("sqrt(3) * sigma", False)
        ],
        "explanation": "sigma_vm = sqrt(1/2 * [(sigma_1 - sigma_2)^2 + (sigma_2 - sigma_3)^2 + (sigma_3 - sigma_1)^2]). When sigma_1 = sigma_2 = sigma_3, all difference terms are zero ==> sigma_vm = 0. Pure hydrostatic stress causes volumetric change but ZERO distortion, hence ductile materials cannot yield under pure hydrostatic stress."
    },

    # Topic 31: SFD & BMD
    {
        "topic_id": 31,
        "question_text": "[UPSC ESE Prelims — Point of Contraflexure]\nIn a beam subjected to bending loads, a 'point of contraflexure' (or inflection point) is a point where:",
        "difficulty": "Easy",
        "options": [
            ("The bending moment is zero and changes its sign", True),
            ("The shear force is zero", False),
            ("The bending moment is at its absolute maximum", False),
            ("The deflection of the beam is zero", False)
        ],
        "explanation": "A point of contraflexure occurs where the bending moment curve passes through zero (M = 0) and changes sign (from sagging to hogging or vice-versa), causing the curvature of the beam to reverse."
    },
    {
        "topic_id": 31,
        "question_text": "[UPSC ESE Prelims — SFD BMD Calculus Relationships]\nThe mathematical relationship between load intensity w(x), shear force V(x), and bending moment M(x) along a beam is:",
        "difficulty": "Easy",
        "options": [
            ("dV / dx = -w(x)  and  dM / dx = V(x)", True),
            ("dV / dx = M(x)  and  dM / dx = -w(x)", False),
            ("d^2 M / dx^2 = +w(x)  and  d^2 V / dx^2 = M(x)", False),
            ("dM / dx = -V(x)  and  dV / dx = w(x)^2", False)
        ],
        "explanation": "Slope of shear force diagram = -load intensity (dV/dx = -w); slope of bending moment diagram = shear force (dM/dx = V). Maximum bending moment occurs where shear force changes sign (V = 0)."
    },
    {
        "topic_id": 31,
        "question_text": "[UPSC ESE Prelims — BMD of Cantilever Beam]\nA cantilever beam of span L carries a uniformly distributed load of w per unit length over its entire span. The maximum bending moment occurs at the fixed support with magnitude:",
        "difficulty": "Easy",
        "options": [
            ("w * L^2 / 2", True),
            ("w * L^2 / 8", False),
            ("w * L^2 / 12", False),
            ("w * L", False)
        ],
        "explanation": "For a cantilever with UDL: Maximum bending moment occurs at the fixed root support = w * L * (L/2) = w * L^2 / 2 (hogging moment)."
    },

    # Topic 32: Bending & Deflection of Beams
    {
        "topic_id": 32,
        "question_text": "[UPSC ESE Prelims — Pure Bending Equation]\nIn the engineering theory of pure bending (Euler-Bernoulli beam theory: M / I = sigma / y = E / R), which of the following is NOT an underlying assumption?",
        "difficulty": "Medium",
        "options": [
            ("Plane sections before bending remain plane after bending", False),
            ("Young's modulus E is identical in tension and compression", False),
            ("The beam cross-section must be symmetrical about both principal axes", True),
            ("The radius of curvature is very large compared to cross-sectional dimensions", False)
        ],
        "explanation": "The cross-section needs to be symmetrical only about the plane of bending (so no twisting occurs). It does NOT need to be doubly symmetrical (e.g., T-sections and unsymmetrical I-beams are routinely analyzed under pure bending)."
    },
    {
        "topic_id": 32,
        "question_text": "[UPSC ESE Prelims — Deflection of Cantilever Beam]\nA cantilever beam of length L and flexural rigidity EI carries a concentrated point load W at its free end. The maximum deflection at the free end is:",
        "difficulty": "Easy",
        "options": [
            ("W * L^3 / (3 EI)", True),
            ("W * L^3 / (48 EI)", False),
            ("W * L^3 / (8 EI)", False),
            ("5 W * L^4 / (384 EI)", False)
        ],
        "explanation": "Cantilever with end point load: Deflection delta_max = W * L^3 / (3 EI), Slope theta_max = W * L^2 / (2 EI)."
    },
    {
        "topic_id": 32,
        "question_text": "[UPSC ESE Prelims — Shear Stress Distribution in Beams]\nFor a beam of rectangular cross-section (width b, depth d) subjected to a transverse shear force V, the maximum shear stress (tau_max) occurs at the neutral axis and equals:",
        "difficulty": "Easy",
        "options": [
            ("1.5 * tau_avg", True),
            ("1.33 * tau_avg", False),
            ("2.0 * tau_avg", False),
            ("1.12 * tau_avg", False)
        ],
        "explanation": "For rectangular section: tau(y) = 3V/(2bd) * [1 - (2y/d)^2]. At neutral axis (y = 0): tau_max = 1.5 * (V / bd) = 1.5 * tau_avg. (For solid circular section: tau_max = 4/3 * tau_avg = 1.33 * tau_avg)."
    },

    # Topic 33: Torsion of Shafts
    {
        "topic_id": 33,
        "question_text": "[UPSC ESE Prelims — Torsion Equation]\nFor a solid circular shaft of diameter d subjected to twisting torque T, the maximum shear stress induced at the outer surface is:",
        "difficulty": "Easy",
        "options": [
            ("16 T / (pi * d^3)", True),
            ("32 T / (pi * d^3)", False),
            ("8 T / (pi * d^3)", False),
            ("64 T / (pi * d^4)", False)
        ],
        "explanation": "Torsion formula: T / J = tau / r. Polar moment of inertia J = pi * d^4 / 32, r_max = d/2. tau_max = T * (d/2) / (pi * d^4 / 32) = 16 T / (pi * d^3)."
    },
    {
        "topic_id": 33,
        "question_text": "[UPSC ESE Prelims — Solid vs Hollow Shaft Strength]\nA hollow circular shaft has an outer diameter D and inner diameter d = D/2. Comparing it with a solid circular shaft of the same material, length, and weight, the hollow shaft is:",
        "difficulty": "Medium",
        "options": [
            ("Stronger in torsion and stiffer because material is located farther from the neutral axis", True),
            ("Weaker in torsion due to the central hole", False),
            ("Identical in torsional strength since mass is the same", False),
            ("Twice as flexible in angular twist", False)
        ],
        "explanation": "For equal weight, the hollow shaft has a larger outer diameter. Since torsional resistance depends on polar section modulus Z_p (proportional to r^3), concentrating mass far from the neutral axis maximizes polar moment of inertia, giving superior torque capacity and torsional stiffness."
    },
    {
        "topic_id": 33,
        "question_text": "[UPSC ESE Prelims — Combined Bending and Torsion]\nA shaft of diameter d is subjected to simultaneous bending moment M and twisting moment T. The equivalent twisting moment T_e and equivalent bending moment M_e are:",
        "difficulty": "Medium",
        "options": [
            ("T_e = sqrt(M^2 + T^2)  and  M_e = 0.5 * [M + sqrt(M^2 + T^2)]", True),
            ("T_e = M + T  and  M_e = sqrt(M^2 + T^2)", False),
            ("T_e = sqrt(M^2 + T^2)  and  M_e = M + T", False),
            ("T_e = 0.5 * [M + T]  and  M_e = sqrt(M * T)", False)
        ],
        "explanation": "Based on maximum shear stress theory (Tresca): T_e = sqrt(M^2 + T^2).\nBased on maximum principal stress theory (Rankine): M_e = 0.5 * [M + sqrt(M^2 + T^2)]."
    },

    # Topic 34: Cylinders, Columns & Springs
    {
        "topic_id": 34,
        "question_text": "[UPSC ESE Prelims — Thin Cylinders Hoop vs Longitudinal Stress]\nIn a thin-walled cylindrical pressure vessel of internal diameter d, wall thickness t (t < d/20), and internal gauge pressure p, the ratio of hoop (circumferential) stress to longitudinal stress is:",
        "difficulty": "Easy",
        "options": [
            ("2.0", True),
            ("0.5", False),
            ("1.0", False),
            ("4.0", False)
        ],
        "explanation": "Hoop stress sigma_h = p * d / (2 * t).\nLongitudinal stress sigma_l = p * d / (4 * t).\nRatio sigma_h / sigma_l = (p*d/2t) / (p*d/4t) = 2.0."
    },
    {
        "topic_id": 34,
        "question_text": "[UPSC ESE Prelims — Euler's Crippling Load for Columns]\nMatch the column end conditions with the effective length L_e for Euler's buckling load formula P_cr = pi^2 * E * I / L_e^2:\n1. Both ends hinged\n2. One end fixed, other end free\n3. Both ends fixed\n4. One end fixed, other end hinged\nEffective length L_e values:\nA. L / 2\nB. L / sqrt(2)\nC. L\nD. 2L\nSelect the correct code:",
        "difficulty": "Easy",
        "options": [
            ("1-C, 2-D, 3-A, 4-B", True),
            ("1-D, 2-C, 3-A, 4-B", False),
            ("1-C, 2-A, 3-D, 4-B", False),
            ("1-A, 2-D, 3-C, 4-B", False)
        ],
        "explanation": "Both hinged: L_e = L. Fixed-Free: L_e = 2L. Both fixed: L_e = L/2. Fixed-Hinged: L_e = L/sqrt(2) approx 0.707 L."
    },
    {
        "topic_id": 34,
        "question_text": "[UPSC ESE Prelims — Helical Springs Wahl Factor]\nIn the design of a close-coiled helical compression spring, the Wahl stress concentration factor K_w accounts for:",
        "difficulty": "Medium",
        "options": [
            ("Both direct transverse shear stress and the curvature effect of the spring coil wire", True),
            ("Only direct shear stress", False),
            ("Only torsional shear stress", False),
            ("Centrifugal expansion of the spring coils", False)
        ],
        "explanation": "Wahl factor K_w = (4C - 1)/(4C - 4) + 0.615/C (where C = D/d is spring index). The first term accounts for the wire curvature effect (stress concentration on inner fiber) and the second term (0.615/C) accounts for direct transverse shear."
    },

    # ==================== SUBJECT 7: MACHINE DESIGN ====================
    # Topic 35: Fatigue & Failure Criteria
    {
        "topic_id": 35,
        "question_text": "[UPSC ESE Prelims — Soderberg, Goodman & Gerber Fatigue Lines]\nUnder fluctuating fatigue loading with mean stress sigma_m and stress amplitude sigma_a, which design failure criterion is the MOST CONSERVATIVE?",
        "difficulty": "Medium",
        "options": [
            ("Soderberg Line (sigma_a / S_e + sigma_m / S_yt = 1)", True),
            ("Goodman Line (sigma_a / S_e + sigma_m / S_ut = 1)", False),
            ("Gerber Parabola (sigma_a / S_e + (sigma_m / S_ut)^2 = 1)", False),
            ("ASME Elliptic Line", False)
        ],
        "explanation": "Soderberg criterion uses yield strength S_yt on the mean stress axis (S_yt < S_ut). Therefore, the Soderberg line lies completely inside the Goodman and Gerber curves, making it the most conservative criterion against both fatigue and static yielding."
    },
    {
        "topic_id": 35,
        "question_text": "[UPSC ESE Prelims — Endurance Limit Modifying Factors]\nAccording to Marin's equation, the endurance limit S_e of a real mechanical component is related to the laboratory rotating-beam specimen endurance limit S_e' by modifying factors. Which factor DECREASES as the surface finish gets rougher?",
        "difficulty": "Easy",
        "options": [
            ("Surface finish factor k_a", True),
            ("Size factor k_b", False),
            ("Reliability factor k_c", False),
            ("Temperature factor k_d", False)
        ],
        "explanation": "S_e = k_a * k_b * k_c * k_d * S_e'. The surface condition factor k_a is 1.0 for mirror-polished specimens and decreases significantly (e.g. 0.4 - 0.7) for ground, machined, or as-forged surfaces due to micro-notches acting as stress raisers."
    },
    {
        "topic_id": 35,
        "question_text": "[UPSC ESE Prelims — Stress Concentration Factor]\nThe notch sensitivity factor q relating the fatigue notch factor K_f to the theoretical stress concentration factor K_t is defined by:",
        "difficulty": "Medium",
        "options": [
            ("q = (K_f - 1) / (K_t - 1)", True),
            ("q = (K_t - 1) / (K_f - 1)", False),
            ("q = K_f / K_t", False),
            ("q = (K_f + 1) / (K_t + 1)", False)
        ],
        "explanation": "Notch sensitivity q = (K_f - 1) / (K_t - 1). When q = 0 (completely insensitive), K_f = 1. When q = 1 (fully notch sensitive), K_f = K_t."
    },

    # Topic 36: Joints (Riveted, Welded, Bolted)
    {
        "topic_id": 36,
        "question_text": "[UPSC ESE Prelims — Throat of Fillet Weld]\nIn the strength calculation of a transverse or parallel fillet weld of leg size s (angle 45 degrees), the design throat thickness t is taken as:",
        "difficulty": "Easy",
        "options": [
            ("s * cos(45 deg) = 0.707 s", True),
            ("s", False),
            ("1.414 s", False),
            ("0.5 s", False)
        ],
        "explanation": "The throat is the minimum cross-section through the root of the fillet weld: t = s * sin(45 deg) = s / sqrt(2) approx 0.707 s. Welds are always designed assuming failure occurs in shear across this throat area."
    },
    {
        "topic_id": 36,
        "question_text": "[UPSC ESE Prelims — Preloaded Bolted Joints]\nA preloaded bolt with stiffness k_b clamps plates of combined stiffness k_c. If an external tensile working load P is applied, what fraction of P is actually carried by the bolt?",
        "difficulty": "Medium",
        "options": [
            ("P * [k_b / (k_b + k_c)]", True),
            ("P * [k_c / (k_b + k_c)]", False),
            ("P", False),
            ("P * (k_b / k_c)", False)
        ],
        "explanation": "Bolt stiffness constant C = k_b / (k_b + k_c). The additional tensile force felt by the bolt is Delta P_b = C * P = P * [k_b / (k_b + k_c)]. Since plate stiffness k_c is typically 3-5 times bolt stiffness k_b, the bolt carries only ~15-25% of the external load, providing excellent fatigue resistance."
    },
    {
        "topic_id": 36,
        "question_text": "[UPSC ESE Prelims — Riveted Joint Failure Modes]\nWhich of the following is NOT a standard failure mode of a riveted lap joint?",
        "difficulty": "Easy",
        "options": [
            ("Buckling of the rivet shank as a slender column", True),
            ("Shearing of the rivet shank", False),
            ("Tearing of the plate between rivet holes", False),
            ("Crushing (bearing failure) of the plate or rivet", False)
        ],
        "explanation": "Standard riveted joint failure modes: 1. Shearing of rivets, 2. Tearing of plate along rivet row, 3. Crushing of plate or rivet, 4. Shearing of plate margin. Buckling does not occur because rivets are short and fully confined."
    },

    # Topic 37: Shafts, Keys & Couplings
    {
        "topic_id": 37,
        "question_text": "[UPSC ESE Prelims — ASME Design Code for Shafts]\nUnder the ASME design code for transmission shafting subjected to combined shock and fatigue, the allowable shear stress tau_max is calculated using:",
        "difficulty": "Medium",
        "options": [
            ("tau_max = (16 / (pi * d^3)) * sqrt((K_b * M)^2 + (K_t * T)^2)", True),
            ("tau_max = (32 / (pi * d^3)) * (K_b * M + K_t * T)", False),
            ("tau_max = (16 / (pi * d^3)) * (M + T)", False),
            ("tau_max = sqrt((K_b * M)^2 + (K_t * T)^2) / d", False)
        ],
        "explanation": "ASME code applies numerical shock and fatigue factors: K_b to bending moment M and K_t to twisting moment T. Equivalent torque T_e = sqrt((K_b * M)^2 + (K_t * T)^2), giving tau_max = 16 T_e / (pi * d^3)."
    },
    {
        "topic_id": 37,
        "question_text": "[UPSC ESE Prelims — Sunk Key Design]\nFor a standard square sunk key of width w = h and length L transmitting torque from a shaft of diameter d, equal strength in shear and crushing requires that:",
        "difficulty": "Medium",
        "options": [
            ("Permissible crushing stress must be twice the permissible shear stress (sigma_c = 2 * tau)", True),
            ("Permissible crushing stress must equal permissible shear stress", False),
            ("Length L must equal shaft diameter d", False),
            ("Width w must equal d / 2", False)
        ],
        "explanation": "Shear force capacity: F = L * w * tau. Crushing force capacity: F = L * (h/2) * sigma_c. Equating the two with w = h: L * w * tau = L * (w/2) * sigma_c ==> sigma_c = 2 * tau."
    },
    {
        "topic_id": 37,
        "question_text": "[UPSC ESE Prelims — Flexible Couplings Oldham & Bush-Pin]\nWhich flexible coupling is specifically designed to connect two shafts whose axes are parallel but have a lateral offset (radial misalignment)?",
        "difficulty": "Easy",
        "options": [
            ("Oldham's Coupling", True),
            ("Hooke's Universal Joint", False),
            ("Bush-Pin flexible flange coupling", False),
            ("Muff coupling", False)
        ],
        "explanation": "Oldham's coupling (an inversion of the double slider-crank chain) is designed specifically for connecting two shafts having parallel lateral misalignment. (Hooke's joint is for intersecting angular misalignment)."
    },

    # Topic 38: Clutches & Brakes
    {
        "topic_id": 38,
        "question_text": "[UPSC ESE Prelims — Friction Clutches Uniform Pressure vs Wear]\nIn a multi-plate friction clutch with friction radii r_1 (outer) and r_2 (inner), the torque capacity calculated under Uniform Wear Theory compared to Uniform Pressure Theory is:",
        "difficulty": "Medium",
        "options": [
            ("Slightly lower, making Uniform Wear Theory more conservative and suitable for worn/used clutches", True),
            ("Significantly higher", False),
            ("Identical for all diameter ratios", False),
            ("Only valid for brand-new freshly machined clutches", False)
        ],
        "explanation": "R_wear = (r_1 + r_2)/2, while R_pressure = 2/3 * (r_1^3 - r_2^3)/(r_1^2 - r_2^2). Mathematically R_wear <= R_pressure. Therefore, torque capacity under uniform wear is lower, providing a conservative and realistic design criterion for run-in clutches."
    },
    {
        "topic_id": 38,
        "question_text": "[UPSC ESE Prelims — Self-Locking Brakes]\nA differential band brake or internal shoe brake becomes 'self-locking' when:",
        "difficulty": "Medium",
        "options": [
            ("The friction moment helps the actuating force to such an extent that the brake remains engaged with zero or negative applied operating force", True),
            ("The braking torque is zero", False),
            ("The coefficient of friction drops to zero", False),
            ("The brake drum rotates only in the reverse direction", False)
        ],
        "explanation": "A brake is self-energizing when friction torque aids the actuating force. If the actuating force required to hold the load becomes zero or negative (P <= 0), the brake is SELF-LOCKING (it locks automatically upon contact without requiring external effort)."
    },
    {
        "topic_id": 38,
        "question_text": "[UPSC ESE Prelims — Number of Contact Surfaces in Clutches]\nA multi-plate clutch has 4 plates on the driving shaft and 3 plates on the driven shaft. How many pairs of contacting friction surfaces (n) are active?",
        "difficulty": "Easy",
        "options": [
            ("6", True),
            ("7", False),
            ("5", False),
            ("12", False)
        ],
        "explanation": "Number of active friction surfaces n = n_1 + n_2 - 1 = 4 + 3 - 1 = 6."
    },

    # Topic 39: Sliding & Rolling Contact Bearings
    {
        "topic_id": 39,
        "question_text": "[UPSC ESE Prelims — Hydrodynamic Journal Bearings Sommerfeld Number]\nThe dimensionless Sommerfeld number (S) characterizing hydrodynamic lubrication in a journal bearing is defined as:",
        "difficulty": "Medium",
        "options": [
            ("S = (r / c)^2 * (mu * N_s / P)", True),
            ("S = (c / r)^2 * (P / (mu * N_s))", False),
            ("S = (r / c) * (mu * N_s / P)", False),
            ("S = mu * N_s / (P * c)", False)
        ],
        "explanation": "Sommerfeld Number: S = (r / c)^2 * (mu * N_s / P), where r is journal radius, c is radial clearance, mu is dynamic viscosity, N_s is rev/sec, and P is projected pressure (W / 2rL)."
    },
    {
        "topic_id": 39,
        "question_text": "[UPSC ESE Prelims — Rolling Contact Bearing Life]\nIf the radial load on a deep-groove ball bearing is doubled (2P), the rated fatigue life (L_10) of the bearing will decrease to:",
        "difficulty": "Easy",
        "options": [
            ("1 / 8 of its original life (12.5%)", True),
            ("1 / 4 of its original life (25%)", False),
            ("1 / 2 of its original life (50%)", False),
            ("1 / 10 of its original life", False)
        ],
        "explanation": "Bearing life equation: L_10 = (C / P)^p million revolutions. For ball bearings, p = 3 (for roller bearings, p = 10/3 = 3.33). If P becomes 2P: L_10' = (C / 2P)^3 = (1/8) * (C/P)^3 = 1/8 of original life."
    },
    {
        "topic_id": 39,
        "question_text": "[UPSC ESE Prelims — Petroff's Equation]\nPetroff's equation for lightly loaded journal bearings operating under hydrodynamic regime is used to determine:",
        "difficulty": "Easy",
        "options": [
            ("The coefficient of friction and viscous frictional power loss", True),
            ("The fatigue life of the bearing bush", False),
            ("The critical whirling speed of the journal", False),
            ("The minimum oil film thickness under extreme shock", False)
        ],
        "explanation": "Petroff's equation assumes journal is concentric (eccentricity epsilon approx 0) and computes friction torque T_f = 2 * pi^2 * mu * N_s * L * r^3 / c, from which coefficient of friction f = 2 * pi^2 * (mu * N_s / P) * (r / c)."
    },

    # Topic 40: Gears & Drives Design
    {
        "topic_id": 40,
        "question_text": "[UPSC ESE Prelims — Lewis Beam Strength Equation for Gears]\nIn the Lewis equation for the beam strength of spur gear teeth (F_b = sigma_b * b * m * Y), the Lewis form factor Y depends ONLY on:",
        "difficulty": "Easy",
        "options": [
            ("The number of teeth and the pressure angle / tooth profile system", True),
            ("The face width and module of the gear", False),
            ("The material yield strength and pitch line velocity", False),
            ("The power transmitted and speed ratio", False)
        ],
        "explanation": "Lewis modeled a gear tooth as a cantilever beam. The dimensionless form factor Y = pi * y depends strictly on the tooth geometry: number of teeth T and pressure angle phi (e.g. Y = 0.154 - 0.912/T for 20 deg full depth)."
    },
    {
        "topic_id": 40,
        "question_text": "[UPSC ESE Prelims — Belt Drive Maximum Power Condition]\nIn a flat belt drive of mass m per unit length running at velocity v under maximum allowable belt tension T_max, maximum power is transmitted when the centrifugal tension T_c equals:",
        "difficulty": "Easy",
        "options": [
            ("T_max / 3", True),
            ("T_max / 2", False),
            ("T_max / 4", False),
            ("2 * T_max / 3", False)
        ],
        "explanation": "Power P = (T_1 - T_2) * v = (T_max - T_c) * (1 - e^(-mu*theta)) * v. Since T_c = m * v^2: dP/dv = 0 yields v = sqrt(T_max / (3m)), which means T_c = T_max / 3. Maximum power occurs when centrifugal tension is 1/3 of maximum permissible tension."
    },
    {
        "topic_id": 40,
        "question_text": "[UPSC ESE Prelims — Pitting Failure in Gears]\nPitting of gear tooth surfaces is a surface fatigue failure caused by:",
        "difficulty": "Medium",
        "options": [
            ("Repeated high cyclic contact stresses (Hertz contact stress) exceeding the surface endurance strength", True),
            ("Inadequate tooth root bending strength", False),
            ("Complete breakdown of lubricant oil causing metal seizure (scuffing)", False),
            ("Excessive tooth backlash", False)
        ],
        "explanation": "Pitting is a surface fatigue phenomenon: cyclic compressive Hertzian contact stresses generate subsurface shear cracks, eventually leading to the detachment of small flakes of metal from the pitch line region."
    },

    # ==================== SUBJECT 8: ENGINEERING MATERIALS ====================
    # Topic 41: Crystal Structure & Imperfections
    {
        "topic_id": 41,
        "question_text": "[UPSC ESE Prelims — Atomic Packing Factor (APF)]\nWhat are the Atomic Packing Factors (APF) for Simple Cubic (SC), Body-Centered Cubic (BCC), and Face-Centered Cubic (FCC) crystal structures respectively?",
        "difficulty": "Easy",
        "options": [
            ("SC = 0.52, BCC = 0.68, FCC = 0.74", True),
            ("SC = 0.68, BCC = 0.52, FCC = 0.74", False),
            ("SC = 0.52, BCC = 0.74, FCC = 0.68", False),
            ("SC = 0.74, BCC = 0.68, FCC = 0.52", False)
        ],
        "explanation": "APF = Volume of atoms in unit cell / Volume of unit cell.\nSC: APF = pi/6 approx 0.52 (coord number 6).\nBCC: APF = sqrt(3)*pi / 8 approx 0.68 (coord number 8).\nFCC & HCP: APF = pi / (3*sqrt(2)) approx 0.74 (coord number 12, close-packed)."
    },
    {
        "topic_id": 41,
        "question_text": "[UPSC ESE Prelims — Crystal Imperfections & Burgers Vector]\nWhich type of dislocation has its Burgers vector oriented strictly PARALLEL to the dislocation line?",
        "difficulty": "Easy",
        "options": [
            ("Screw Dislocation", True),
            ("Edge Dislocation", False),
            ("Mixed Dislocation", False),
            ("Frank-Read source", False)
        ],
        "explanation": "Edge dislocation: Burgers vector is PERPENDICULAR to dislocation line.\nScrew dislocation: Burgers vector is PARALLEL to dislocation line.\nMixed dislocation: Burgers vector is at an arbitrary angle."
    },
    {
        "topic_id": 41,
        "question_text": "[UPSC ESE Prelims — Miller Indices]\nIn a cubic unit cell, a crystal plane intercepts the crystallographic axes at x = 1, y = 2, and is parallel to the z-axis (z = infinity). The Miller indices of this plane are:",
        "difficulty": "Easy",
        "options": [
            ("(2 1 0)", True),
            ("(1 2 0)", False),
            ("(1 1 0)", False),
            ("(2 1 1)", False)
        ],
        "explanation": "Intercepts: (1, 2, inf). Reciprocals: (1/1, 1/2, 1/inf) = (1, 1/2, 0). Clear fractions by multiplying by 2 ==> (2 1 0)."
    },

    # Topic 42: Phase Diagrams & Fe-Fe3C System
    {
        "topic_id": 42,
        "question_text": "[UPSC ESE Prelims — Fe-Fe3C Invariant Reactions]\nMatch List-I (Invariant Reaction in Fe-Fe3C) with List-II (Reaction Equation & Temperature):\nList-I:\nA. Eutectic Reaction\nB. Eutectoid Reaction\nC. Peritectic Reaction\nList-II:\n1. Liquid (0.53% C) + Delta-ferrite (0.09% C) -> Austenite (0.17% C) at 1495 deg C\n2. Liquid (4.3% C) -> Austenite (2.11% C) + Fe3C (6.67% C) [Ledeburite] at 1147 deg C\n3. Austenite (0.76% C) -> Alpha-ferrite (0.022% C) + Fe3C (6.67% C) [Pearlite] at 727 deg C\nSelect the correct code:",
        "difficulty": "Medium",
        "options": [
            ("A-2, B-3, C-1", True),
            ("A-3, B-2, C-1", False),
            ("A-1, B-2, C-3", False),
            ("A-2, B-1, C-3", False)
        ],
        "explanation": "Eutectic at 1147 deg C: Liquid (4.3% C) -> gamma + Fe3C (Ledeburite).\nEutectoid at 727 deg C: gamma (0.76% C) -> alpha + Fe3C (Pearlite).\nPeritectic at 1495 deg C: Liquid (0.53% C) + delta (0.09% C) -> gamma (0.17% C)."
    },
    {
        "topic_id": 42,
        "question_text": "[UPSC ESE Prelims — Lever Rule Calculation]\nIn a binary alloy system with two components A and B, an alloy of 40% B is at temperature T where it separates into alpha phase (10% B) and beta phase (60% B). The mass fraction of beta phase (W_beta) is:",
        "difficulty": "Easy",
        "options": [
            ("60%", True),
            ("40%", False),
            ("50%", False),
            ("30%", False)
        ],
        "explanation": "Lever Rule: W_beta = (C_0 - C_alpha) / (C_beta - C_alpha) = (40 - 10) / (60 - 10) = 30 / 50 = 0.60 = 60%."
    },
    {
        "topic_id": 42,
        "question_text": "[UPSC ESE Prelims — Gibbs Phase Rule]\nUnder constant atmospheric pressure (condensed phase rule P + F = C + 1), the number of degrees of freedom (F) at an invariant eutectic point of a binary system (C = 2) is:",
        "difficulty": "Easy",
        "options": [
            ("0", True),
            ("1", False),
            ("2", False),
            ("3", False)
        ],
        "explanation": "At eutectic point, 3 phases coexist in equilibrium (Liquid, Alpha, Beta ==> P = 3). For binary system C = 2. Under condensed rule: F = C - P + 1 = 2 - 3 + 1 = 0 (invariant point; both temperature and composition are uniquely fixed)."
    },

    # Topic 43: Heat Treatment Processes
    {
        "topic_id": 43,
        "question_text": "[UPSC ESE Prelims — Martensitic Transformation]\nDuring rapid water quenching of austenitized medium-carbon steel, the formation of Martensite is characterized by:",
        "difficulty": "Medium",
        "options": [
            ("A diffusionless, athermal shear transformation that distorts the FCC lattice into Body-Centered Tetragonal (BCT)", True),
            ("Diffusion-controlled nucleation and growth of lamellar cementite", False),
            ("A phase transformation that occurs only at constant elevated temperature", False),
            ("Precipitation of globular graphite nodules", False)
        ],
        "explanation": "Martensite forms by a rapid, diffusionless (athermal) shear displacement of iron atoms trapping carbon supersaturated in interstitial sites, converting parent FCC austenite into hard, brittle Body-Centered Tetragonal (BCT) structure."
    },
    {
        "topic_id": 43,
        "question_text": "[UPSC ESE Prelims — Austempering vs Martempering]\nAustempering of steel is an isothermal heat treatment process designed specifically to produce which microstructure?",
        "difficulty": "Easy",
        "options": [
            ("Bainite", True),
            ("Tempered Martensite", False),
            ("Coarse Pearlite", False),
            ("Spheroidite", False)
        ],
        "explanation": "Austempering: Quench steel in molten salt bath held above M_s temperature (approx 250-400 deg C), maintain isothermally until complete transformation to BAINITE, then air cool. Provides high ductility and impact toughness without distortion."
    },
    {
        "topic_id": 43,
        "question_text": "[UPSC ESE Prelims — Case Hardening Nitriding]\nWhich of the following is a key advantage of Gas Nitriding over Carburizing for surface hardening of precision alloy gears?",
        "difficulty": "Medium",
        "options": [
            ("It is carried out at lower temperature (approx 500-550 deg C) with no subsequent quenching required, minimizing thermal distortion", True),
            ("It produces a much deeper case depth of up to 5 mm in just 1 hour", False),
            ("It can be applied effectively to plain low carbon steels without alloying elements", False),
            ("It requires water quenching from 900 deg C", False)
        ],
        "explanation": "Nitriding occurs in ammonia gas at sub-critical temperatures (500-550 deg C). Nitrogen diffuses to form ultra-hard alloy nitrides (with Al, Cr, Mo). Because no phase transformation (austenite to martensite) and NO QUENCHING is involved, distortion is almost zero."
    },

    # Topic 44: Ferrous & Non-Ferrous Alloys
    {
        "topic_id": 44,
        "question_text": "[UPSC ESE Prelims — Spheroidal Graphite (SG) Cast Iron]\nIn ductile (nodular / SG) cast iron, spherical nodules of graphite are produced by adding small amounts of which element to molten grey cast iron just prior to casting?",
        "difficulty": "Easy",
        "options": [
            ("Magnesium (Mg) or Cerium (Ce)", True),
            ("Chromium (Cr)", False),
            ("Nickel (Ni)", False),
            ("Molybdenum (Mo)", False)
        ],
        "explanation": "Adding magnesium (0.03-0.05%) or cerium into low-sulfur molten iron alters surface tension and causes graphite to precipitate as spheroids (nodules) instead of sharp flakes, giving ductile cast iron high tensile strength and ductility."
    },
    {
        "topic_id": 44,
        "question_text": "[UPSC ESE Prelims — Stainless Steels 18/8]\nStandard austenitic stainless steel (AISI 304 / 18-8 stainless steel) contains approximately:",
        "difficulty": "Easy",
        "options": [
            ("18% Chromium and 8% Nickel (FCC structure, non-magnetic)", True),
            ("18% Nickel and 8% Chromium (BCC structure, highly magnetic)", False),
            ("18% Tungsten and 8% Cobalt", False),
            ("18% Carbon and 8% Silicon", False)
        ],
        "explanation": "18/8 stainless steel has ~18% Cr and ~8% Ni. Nickel stabilizes the face-centered cubic (FCC) austenite phase down to room temperature, making it exceptionally ductile, corrosion-resistant, and NON-MAGNETIC."
    },
    {
        "topic_id": 44,
        "question_text": "[UPSC ESE Prelims — High Speed Steel (HSS 18:4:1)]\nTraditional 18-4-1 High Speed Steel (HSS) contains which alloying elements in the ratio 18:4:1?",
        "difficulty": "Easy",
        "options": [
            ("18% Tungsten (W), 4% Chromium (Cr), and 1% Vanadium (V)", True),
            ("18% Chromium, 4% Nickel, and 1% Carbon", False),
            ("18% Vanadium, 4% Tungsten, and 1% Cobalt", False),
            ("18% Molybdenum, 4% Titanium, and 1% Silicon", False)
        ],
        "explanation": "T1 High Speed Steel: 18% Tungsten (provides red hardness), 4% Chromium (increases hardenability and corrosion resistance), 1% Vanadium (forms hard wear-resistant VC carbides), and ~0.7% Carbon."
    },

    # Topic 45: Polymers, Ceramics & Composites
    {
        "topic_id": 45,
        "question_text": "[UPSC ESE Prelims — Thermoplastic vs Thermosetting Polymers]\nWhich of the following statements correctly distinguishes Thermosetting polymers from Thermoplastics?",
        "difficulty": "Easy",
        "options": [
            ("Thermosets have cross-linked 3D network structures that permanently set upon heating and degrade rather than melt upon reheating", True),
            ("Thermosets can be repeatedly softened by heating and reshaped upon cooling", False),
            ("Thermoplastics are joined by permanent covalent cross-links between polymer chains", False),
            ("Polyethylene and PVC are typical thermosetting polymers", False)
        ],
        "explanation": "Thermoplastics (PE, PP, PVC, Nylon) consist of linear/branched chains bonded by weak secondary van der Waals forces (melt and reshape repeatedly). Thermosets (Bakelite, Epoxy, Phenol formaldehyde) form highly cross-linked covalent 3D networks; they do not melt upon reheating and decompose."
    },
    {
        "topic_id": 45,
        "question_text": "[UPSC ESE Prelims — Rule of Mixtures for Composites]\nIn a continuous unidirectional fiber-reinforced composite, the Young's modulus in the longitudinal direction (isostrain condition) is given by the Rule of Mixtures as:",
        "difficulty": "Easy",
        "options": [
            ("E_cl = E_f * V_f + E_m * V_m", True),
            ("1 / E_cl = V_f / E_f + V_m / E_m", False),
            ("E_cl = (E_f * E_m) / (V_f * E_f + V_m * E_m)", False),
            ("E_cl = sqrt(E_f * E_m)", False)
        ],
        "explanation": "Under longitudinal loading parallel to fibers, both fibers and matrix experience equal strain (isostrain: epsilon_c = epsilon_f = epsilon_m). Force equilibrium yields: E_cl = E_f * V_f + E_m * V_m."
    },
    {
        "topic_id": 45,
        "question_text": "[UPSC ESE Prelims — Engineering Ceramics]\nEngineering ceramics such as Alumina (Al2O3) and Silicon Carbide (SiC) exhibit exceptionally high compressive strength and melting points but low fracture toughness primarily due to:",
        "difficulty": "Medium",
        "options": [
            ("Strong directional ionic and covalent bonding with very few independent slip systems to accommodate dislocation motion", True),
            ("High density of mobile edge dislocations", False),
            ("Free metallic electrons that cause lattice softening", False),
            ("Amorphous glass structures with zero crystalline order", False)
        ],
        "explanation": "Ceramics have strong ionic/covalent bonds with high Peierls-Nabarro stress. The lack of active slip systems inhibits dislocation motion, making ceramics inherently brittle and sensitive to micro-cracks under tensile stress."
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
        print(f"Successfully added {added} authentic UPSC ESE Prelims questions for Wing B: Design & Materials (Topics 23-45)!")

if __name__ == '__main__':
    main()
