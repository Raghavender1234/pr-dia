# -*- coding: utf-8 -*-
"""
Seed authentic UPSC ESE Prelims MCQs for Paper-II Mechanical Engineering:
Wing A: Thermal & Fluids Engineering (Topics 1 to 22)
Subject 1: Fluid Mechanics & Turbo Machinery (Topics 1-6)
Subject 2: Thermodynamics & Heat Transfer (Topics 7-12)
Subject 3: IC Engines, Refrigeration & Air Conditioning (Topics 13-17)
Subject 4: Power Plant Engineering & Renewable Energy (Topics 18-22)
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.question import Question, MCQOption

QUESTIONS = [
    # ==================== SUBJECT 1: FLUID MECHANICS & TURBO MACHINERY ====================
    # Topic 1: Fluid Properties, Pressure Measurement & Hydrostatics
    {
        "topic_id": 1,
        "question_text": "[UPSC ESE Prelims — Fluid Properties]\nIf the shear stress tau between two fluid layers is proportional to (du/dy)^n, which of the following pairs correctly matches the fluid behavior with the flow behavior index n and yield stress tau_0?",
        "difficulty": "Medium",
        "options": [
            ("Pseudoplastic (Shear-thinning): n < 1 and tau_0 = 0", True),
            ("Dilatant (Shear-thickening): n < 1 and tau_0 = 0", False),
            ("Bingham Plastic: n = 1 and tau_0 = 0", False),
            ("Thixotropic: n > 1 and time-independent", False)
        ],
        "explanation": "Ostwald-de Waele model: tau = tau_0 + k (du/dy)^n.\nFor Pseudoplastic (shear-thinning like blood, milk, paper pulp): tau_0 = 0 and n < 1 (apparent viscosity decreases with strain rate).\nFor Dilatant (shear-thickening like starch, quicksand): tau_0 = 0 and n > 1.\nFor Bingham plastic (toothpaste): tau_0 > 0 and n = 1."
    },
    {
        "topic_id": 1,
        "question_text": "[UPSC ESE Prelims — Hydrostatics & Center of Pressure]\nA vertical rectangular gate of width b and height h is submerged in water such that its top edge coincides with the free liquid surface. The depth of the center of pressure from the free surface is:",
        "difficulty": "Easy",
        "options": [
            ("h / 2", False),
            ("2h / 3", True),
            ("3h / 4", False),
            ("h / 3", False)
        ],
        "explanation": "h_cp = h_cg + I_G / (A * h_cg). For rectangle: h_cg = h/2, I_G = b*h^3 / 12, A = b*h.\nh_cp = h/2 + (b*h^3 / 12) / (b*h * h/2) = h/2 + h/6 = 2h/3."
    },
    {
        "topic_id": 1,
        "question_text": "[UPSC ESE Prelims — Buoyancy & Metacentric Height]\nFor a floating body to be in stable equilibrium, the metacentric height (GM) must be positive. This requires that:",
        "difficulty": "Medium",
        "options": [
            ("Metacenter M must lie above the center of gravity G", True),
            ("Center of gravity G must lie above the center of buoyancy B", False),
            ("Metacenter M must coincide with the center of buoyancy B", False),
            ("Center of buoyancy B must lie above the metacenter M", False)
        ],
        "explanation": "For floating bodies: Stable equilibrium requires M above G (GM > 0). Neutral equilibrium when M coincides with G (GM = 0). Unstable equilibrium when M is below G (GM < 0)."
    },

    # Topic 2: Fluid Kinematics & Dynamics
    {
        "topic_id": 2,
        "question_text": "[UPSC ESE Prelims — Fluid Kinematics]\nIn a 2D incompressible fluid flow, the velocity potential function is given by phi = x^2 - y^2. What is the corresponding stream function psi (assuming psi = 0 at origin)?",
        "difficulty": "Medium",
        "options": [
            ("psi = 2xy", True),
            ("psi = x^2 + y^2", False),
            ("psi = -2xy", False),
            ("psi = x^2 - y^2", False)
        ],
        "explanation": "u = -dphi/dx = -2x, and u = -dpsi/dy ==> dpsi/dy = 2x ==> psi = 2xy + f(x).\nv = -dphi/dy = 2y, and v = dpsi/dx ==> dpsi/dx = 2y ==> f'(x) = 0 ==> psi = 2xy."
    },
    {
        "topic_id": 2,
        "question_text": "[UPSC ESE Prelims — Bernoulli's Equation]\nWhich of the following assumptions is NOT required in the standard derivation of Bernoulli's equation along a streamline from Euler's equation of motion?",
        "difficulty": "Medium",
        "options": [
            ("Flow is steady", False),
            ("Fluid is frictionless (inviscid)", False),
            ("Flow must be irrotational across all streamlines", True),
            ("Fluid is incompressible", False)
        ],
        "explanation": "Bernoulli's equation along a single streamline requires only: steady, inviscid, incompressible flow, and flow along a streamline. Irrotationality is NOT required along a single streamline (it is only required if Bernoulli constant is to be identical across DIFFERENT streamlines)."
    },
    {
        "topic_id": 2,
        "question_text": "[UPSC ESE Prelims — Momentum Equation]\nA horizontal jet of water with cross-sectional area A and velocity V strikes a vertical flat plate normally. If the plate is moving in the direction of the jet with a constant velocity u (u < V), the force exerted by the jet on the plate is:",
        "difficulty": "Medium",
        "options": [
            ("rho * A * (V - u)^2", True),
            ("rho * A * (V^2 - u^2)", False),
            ("rho * A * V * (V - u)", False),
            ("rho * A * (V - u)", False)
        ],
        "explanation": "Mass flow rate striking moving plate = rho * A * (V - u). Change in velocity in x-direction = (V - u) - 0 = (V - u).\nForce F_x = mass rate * delta V = rho * A * (V - u)^2."
    },

    # Topic 3: Boundary Layer Theory & Pipe Flow
    {
        "topic_id": 3,
        "question_text": "[UPSC ESE Prelims — Boundary Layer Theory]\nFor laminar boundary layer flow over a flat plate of length L, the boundary layer thickness delta and local skin friction coefficient C_fx vary with distance x from leading edge as:",
        "difficulty": "Easy",
        "options": [
            ("delta proportional to x^(1/2) and C_fx proportional to x^(-1/2)", True),
            ("delta proportional to x^(-1/2) and C_fx proportional to x^(1/2)", False),
            ("delta proportional to x^(4/5) and C_fx proportional to x^(-1/5)", False),
            ("delta proportional to x and C_fx is constant", False)
        ],
        "explanation": "Blasius exact solution for laminar boundary layer: delta / x = 5.0 / sqrt(Re_x) ==> delta proportional to x^(1/2).\nLocal shear stress tau_w = 0.332 rho U^2 / sqrt(Re_x) ==> C_fx proportional to x^(-1/2)."
    },
    {
        "topic_id": 3,
        "question_text": "[UPSC ESE Prelims — Laminar Flow Through Pipes]\nIn fully developed laminar flow through a circular pipe of radius R (Hagen-Poiseuille flow), the ratio of maximum velocity to average velocity is:",
        "difficulty": "Easy",
        "options": [
            ("1.5", False),
            ("2.0", True),
            ("1.33", False),
            ("2.5", False)
        ],
        "explanation": "In Hagen-Poiseuille pipe flow: u(r) = u_max (1 - r^2 / R^2). The average velocity V_avg = u_max / 2. Therefore, u_max / V_avg = 2.0. (For parallel plates, u_max / V_avg = 1.5)."
    },
    {
        "topic_id": 3,
        "question_text": "[UPSC ESE Prelims — Dimensional Analysis]\nMatch List-I (Dimensionless Number) with List-II (Ratio of Forces):\nList-I:\nA. Froude Number\nB. Weber Number\nC. Mach Number\nD. Reynolds Number\nList-II:\n1. Inertia force to Surface Tension force\n2. Inertia force to Gravity force\n3. Inertia force to Viscous force\n4. Inertia force to Elastic force\nSelect the correct code:",
        "difficulty": "Easy",
        "options": [
            ("A-2, B-1, C-4, D-3", True),
            ("A-1, B-2, C-3, D-4", False),
            ("A-2, B-4, C-1, D-3", False),
            ("A-3, B-1, C-4, D-2", False)
        ],
        "explanation": "Froude = sqrt(Inertia / Gravity); Weber = sqrt(Inertia / Surface Tension); Mach = sqrt(Inertia / Elastic); Reynolds = Inertia / Viscous."
    },

    # Topic 4: Hydraulic Turbines
    {
        "topic_id": 4,
        "question_text": "[UPSC ESE Prelims — Hydraulic Turbines]\nThe specific speed N_s of a hydraulic turbine developing power P under head H at speed N is defined by which formula?",
        "difficulty": "Medium",
        "options": [
            ("N_s = N * sqrt(P) / H^(5/4)", True),
            ("N_s = N * sqrt(Q) / H^(3/4)", False),
            ("N_s = N * P^(3/4) / H^(5/4)", False),
            ("N_s = N * sqrt(P) / H^(3/4)", False)
        ],
        "explanation": "For a turbine: N_s = N * sqrt(P) / H^(5/4). (For a pump: N_s = N * sqrt(Q) / H^(3/4))."
    },
    {
        "topic_id": 4,
        "question_text": "[UPSC ESE Prelims — Turbine Classification]\nWhich of the following hydraulic turbines is an axial-flow reaction turbine with adjustable runner blades?",
        "difficulty": "Easy",
        "options": [
            ("Pelton Wheel", False),
            ("Francis Turbine", False),
            ("Propeller Turbine", False),
            ("Kaplan Turbine", True)
        ],
        "explanation": "Kaplan turbine is an axial flow reaction turbine with adjustable runner blades and adjustable guide vanes, ideal for low heads and large discharges. (Propeller turbine has fixed runner blades)."
    },
    {
        "topic_id": 4,
        "question_text": "[UPSC ESE Prelims — Draft Tube in Turbines]\nWhat is the primary thermodynamic and hydrodynamic function of a draft tube in a reaction hydraulic turbine?",
        "difficulty": "Medium",
        "options": [
            ("To increase the velocity of water entering the tail race", False),
            ("To recover kinetic energy leaving the runner by converting it into pressure energy and establish suction head", True),
            ("To prevent water hammer in the penstock", False),
            ("To prevent surging in the runner blades", False)
        ],
        "explanation": "A draft tube is a gradually expanding conduit that connects runner exit to tail race. It converts exit kinetic energy (V^2 / 2g) into useful pressure head and allows the turbine to be set above tail race without losing net effective head."
    },

    # Topic 5: Pumps & Cavitation
    {
        "topic_id": 5,
        "question_text": "[UPSC ESE Prelims — Centrifugal Pumps & Cavitation]\nCavitation in a centrifugal pump is most likely to initiate at which of the following locations?",
        "difficulty": "Easy",
        "options": [
            ("Volute casing outlet", False),
            ("Suction eye and inlet tips of the impeller blades", True),
            ("Diffuser exit passage", False),
            ("Delivery pipe discharge nozzle", False)
        ],
        "explanation": "Cavitation occurs where static pressure drops to or below the vapor pressure (P_v) of the liquid. In a pump, minimum static pressure occurs at the suction eye and the suction tips of the impeller blades."
    },
    {
        "topic_id": 5,
        "question_text": "[UPSC ESE Prelims — NPSH in Pumps]\nTo avoid cavitation in a hydraulic pump installation, which condition between Net Positive Suction Head Available (NPSHA) and Required (NPSHR) must be satisfied?",
        "difficulty": "Easy",
        "options": [
            ("NPSHA > NPSHR", True),
            ("NPSHA < NPSHR", False),
            ("NPSHA = 0", False),
            ("NPSHR must be greater than atmospheric head", False)
        ],
        "explanation": "For cavitation-free operation: NPSHA must exceed NPSHR (NPSHA > NPSHR), typically with a safety margin of at least 0.5 to 1.0 m."
    },
    {
        "topic_id": 5,
        "question_text": "[UPSC ESE Prelims — Reciprocating Pumps & Air Vessels]\nIn a single-acting reciprocating pump, the installation of an air vessel on the delivery pipe as close to the cylinder as possible results in:",
        "difficulty": "Medium",
        "options": [
            ("A continuous uniform discharge in the delivery pipe and savings of approximately 84.8% in friction work", True),
            ("Complete elimination of suction head", False),
            ("A reduction in pump volumetric efficiency", False),
            ("Friction work savings of only 39.2%", False)
        ],
        "explanation": "An air vessel acts as a surge damper, converting fluctuating reciprocating flow into uniform flow beyond the vessel. Work saved against pipe friction = 84.8% for single-acting and 39.2% for double-acting reciprocating pumps."
    },

    # Topic 6: Compressible Flow & Turbines
    {
        "topic_id": 6,
        "question_text": "[UPSC ESE Prelims — Compressible Flow Nozzles]\nFor isentropic compressible flow of an ideal gas through a converging-diverging (de Laval) nozzle, sonic conditions (Mach number M = 1) can occur ONLY at the:",
        "difficulty": "Easy",
        "options": [
            ("Inlet of the converging section", False),
            ("Minimum cross-sectional area (Throat)", True),
            ("Exit of the diverging section", False),
            ("Any point where back pressure equals ambient pressure", False)
        ],
        "explanation": "From dA / A = (M^2 - 1) * (dV / V): When M = 1, dA / A = 0, which corresponds to the minimum area location, i.e., the THROAT."
    },
    {
        "topic_id": 6,
        "question_text": "[UPSC ESE Prelims — Steam Turbine Blading]\nIn an axial impulse steam turbine stage (De Laval stage), the theoretical maximum blade efficiency (eta_b,max) for blades with symmetrical angles is given by:",
        "difficulty": "Medium",
        "options": [
            ("cos^2(alpha_1)", True),
            ("cos(alpha_1)", False),
            ("2 cos^2(alpha_1) / (1 + cos^2(alpha_1))", False),
            ("(1 + cos(alpha_1)) / 2", False)
        ],
        "explanation": "For pure impulse stage with nozzle angle alpha_1: optimum blade-speed ratio rho = u / V_1 = (cos alpha_1) / 2. At this ratio, maximum blade efficiency eta_b,max = cos^2(alpha_1). (For 50% reaction Parsons stage: eta_b,max = 2 cos^2(alpha_1) / (1 + cos^2(alpha_1)))."
    },
    {
        "topic_id": 6,
        "question_text": "[UPSC ESE Prelims — Compounding of Steam Turbines]\nCurtis staging in impulse steam turbines utilizes which method of compounding?",
        "difficulty": "Medium",
        "options": [
            ("Pressure Compounding (Rateau Staging)", False),
            ("Velocity Compounding", True),
            ("Pressure-Velocity Compounding", False),
            ("Reaction Compounding (Parsons Staging)", False)
        ],
        "explanation": "Curtis stage = Velocity compounding (steam expands in one set of nozzles, followed by multiple rows of moving blades separated by fixed guide blades).\nRateau stage = Pressure compounding (multiple impulse stages in series, each having nozzles and a moving blade wheel)."
    },

    # ==================== SUBJECT 2: THERMODYNAMICS & HEAT TRANSFER ====================
    # Topic 7: First Law & Basic Concepts
    {
        "topic_id": 7,
        "question_text": "[UPSC ESE Prelims — Thermodynamics First Law]\nDuring a throttling process (flow through a porous plug or partially opened valve), which property remains constant for an ideal gas?",
        "difficulty": "Easy",
        "options": [
            ("Enthalpy and Temperature", True),
            ("Entropy and Pressure", False),
            ("Internal energy and Pressure", False),
            ("Volume and Enthalpy", False)
        ],
        "explanation": "Throttling is an isenthalpic process (h_1 = h_2). For an ideal gas, h = C_p * T, hence constant enthalpy also implies constant temperature (T_1 = T_2, Joule-Thomson coefficient mu_JT = 0)."
    },
    {
        "topic_id": 7,
        "question_text": "[UPSC ESE Prelims — Open System First Law]\nIn a steady flow system, 1 kg/s of fluid enters at 100 m/s with enthalpy 3000 kJ/kg and leaves at 50 m/s with enthalpy 2000 kJ/kg. If heat loss from the turbine casing is 50 kW, what is the power output developed by the turbine?",
        "difficulty": "Medium",
        "options": [
            ("946.25 kW", False),
            ("953.75 kW", True),
            ("1000 kW", False),
            ("1053.75 kW", False)
        ],
        "explanation": "SFEE: m_dot * [h_1 + V_1^2 / 2000] + Q_dot = m_dot * [h_2 + V_2^2 / 2000] + W_dot.\n1 * [3000 + 100^2 / 2000] + (-50) = 1 * [2000 + 50^2 / 2000] + W_dot\n[3000 + 5] - 50 = [2000 + 1.25] + W_dot\n2955 = 2001.25 + W_dot ==> W_dot = 2955 - 2001.25 = 953.75 kW."
    },
    {
        "topic_id": 7,
        "question_text": "[UPSC ESE Prelims — Thermodynamic Processes]\nWhich of the following thermodynamic processes on a p-V diagram has a polytropic index n = infinity?",
        "difficulty": "Easy",
        "options": [
            ("Isobaric process (constant pressure)", False),
            ("Isochoric process (constant volume)", True),
            ("Isothermal process (constant temperature)", False),
            ("Isentropic process (reversible adiabatic)", False)
        ],
        "explanation": "p V^n = C ==> p^(1/n) V = C'. As n -> infinity: p^0 V = V = constant (Isochoric / isometric process). When n = 0, p = constant (Isobaric)."
    },

    # Topic 8: Second Law, Entropy & Exergy
    {
        "topic_id": 8,
        "question_text": "[UPSC ESE Prelims — Clausius Inequality]\nAccording to the Clausius inequality, for any thermodynamic cycle, the cyclic integral of (delta Q / T) satisfies:",
        "difficulty": "Easy",
        "options": [
            ("Cyclic integral <= 0 (strictly zero for reversible, < 0 for irreversible)", True),
            ("Cyclic integral >= 0", False),
            ("Cyclic integral = 0 for all cycles", False),
            ("Cyclic integral > 0 for irreversible cycles", False)
        ],
        "explanation": "Clausius Inequality: cyclic integral of delta Q / T <= 0. If = 0, cycle is reversible. If < 0, cycle is irreversible. If > 0, cycle is impossible."
    },
    {
        "topic_id": 8,
        "question_text": "[UPSC ESE Prelims — Exergy / Availability]\nThe maximum theoretical useful work that can be extracted from a closed system containing an ideal gas in contact with an ambient thermal reservoir at T_0 as it comes to equilibrium with the environment is called:",
        "difficulty": "Medium",
        "options": [
            ("Helmholtz function", False),
            ("Gibbs free energy", False),
            ("Exergy (Availability)", True),
            ("Irreversibility", False)
        ],
        "explanation": "Availability (Exergy) represents the maximum theoretical useful work obtainable from a system as it reaches complete thermal, mechanical, and chemical equilibrium with the dead state environment (T_0, P_0)."
    },
    {
        "topic_id": 8,
        "question_text": "[UPSC ESE Prelims — Entropy Generation & Gouy-Stodola]\nThe Gouy-Stodola theorem states that the rate of loss of available work (irreversibility rate I_dot) in any engineering process is directly proportional to:",
        "difficulty": "Medium",
        "options": [
            ("The ambient temperature T_0 multiplied by the entropy generation rate S_dot_gen", True),
            ("The source temperature multiplied by total heat supplied", False),
            ("The difference between heat added and work produced", False),
            ("The change in Gibbs free energy across the system boundaries", False)
        ],
        "explanation": "Gouy-Stodola theorem: Irreversibility rate I_dot = T_0 * S_dot_gen, where T_0 is the absolute temperature of the surrounding environment."
    },

    # Topic 9: Pure Substances & Thermodynamic Relations
    {
        "topic_id": 9,
        "question_text": "[UPSC ESE Prelims — Maxwell Relations]\nWhich of the following is one of Maxwell's four thermodynamic relations for a simple compressible substance?",
        "difficulty": "Medium",
        "options": [
            ("(dT / dV)_s = -(dP / dS)_v", True),
            ("(dT / dP)_s = -(dV / dS)_p", False),
            ("(dP / dT)_v = -(dS / dV)_t", False),
            ("(dV / dT)_p = (dP / dS)_t", False)
        ],
        "explanation": "From du = T ds - P dv: (dT / dv)_s = -(dP / ds)_v.\nFrom dh = T ds + v dP: (dT / dP)_s = (dv / ds)_P.\nFrom da = -s dT - P dv: (ds / dv)_T = (dP / dT)_v.\nFrom dg = -s dT + v dP: -(ds / dP)_T = (dv / dT)_P."
    },
    {
        "topic_id": 9,
        "question_text": "[UPSC ESE Prelims — Clausius-Clapeyron Equation]\nThe Clausius-Clapeyron equation relating the slope of the saturation vapor pressure curve (dP/dT)_sat to latent heat of vaporization h_fg is:",
        "difficulty": "Medium",
        "options": [
            ("(dP / dT)_sat = h_fg / [T * (v_g - v_f)]", True),
            ("(dP / dT)_sat = [T * (v_g - v_f)] / h_fg", False),
            ("(dP / dT)_sat = h_fg / [v_g - v_f]", False),
            ("(dP / dT)_sat = T * h_fg / (v_g - v_f)", False)
        ],
        "explanation": "Clausius-Clapeyron equation: (dP / dT)_sat = s_fg / v_fg = h_fg / [T_sat * (v_g - v_f)]."
    },
    {
        "topic_id": 9,
        "question_text": "[UPSC ESE Prelims — Pure Substance Phase Change]\nAt the critical point of water, which of the following statements is correct?",
        "difficulty": "Easy",
        "options": [
            ("The latent heat of vaporization becomes zero", True),
            ("Liquid water and steam exist at two clearly distinct densities", False),
            ("The specific volume of saturated vapor is much higher than saturated liquid", False),
            ("Sublimation occurs directly into dry vapor", False)
        ],
        "explanation": "At the critical point (for water: P_c = 22.09 MPa, T_c = 374.14 deg C): v_f = v_g, and the latent heat of phase change h_fg = 0."
    },

    # Topic 10: Conduction Heat Transfer
    {
        "topic_id": 10,
        "question_text": "[UPSC ESE Prelims — Critical Radius of Insulation]\nFor a hollow circular pipe of outer radius r_0 carrying hot steam and exposed to ambient air with convective coefficient h, the critical radius of insulation r_c is given by (k = thermal conductivity of insulation):",
        "difficulty": "Easy",
        "options": [
            ("r_c = k / h", True),
            ("r_c = 2k / h", False),
            ("r_c = h / k", False),
            ("r_c = sqrt(k / h)", False)
        ],
        "explanation": "For a cylinder: r_c = k / h. (For a sphere: r_c = 2k / h). Adding insulation when r_outer < r_c increases heat loss until r_c is reached."
    },
    {
        "topic_id": 10,
        "question_text": "[UPSC ESE Prelims — Lumped Heat Capacity System]\nThe lumped capacitance method for transient conduction analysis is valid when the Biot number (Bi) satisfies which condition?",
        "difficulty": "Easy",
        "options": [
            ("Bi < 0.1", True),
            ("Bi > 1.0", False),
            ("Bi = 1.0", False),
            ("Fourier number Fo < 0.2", False)
        ],
        "explanation": "Biot number Bi = h * L_c / k_solid. When Bi < 0.1, internal conductive thermal resistance is negligible compared to external convective resistance, and the solid temperature can be treated as spatially uniform."
    },
    {
        "topic_id": 10,
        "question_text": "[UPSC ESE Prelims — Extended Surfaces / Fins]\nFor an infinitely long fin of cross-sectional area A_c, perimeter P, and thermal conductivity k exposed to a fluid with heat transfer coefficient h, the heat transfer rate from the fin base at temperature T_0 is:",
        "difficulty": "Medium",
        "options": [
            ("sqrt(h * P * k * A_c) * (T_0 - T_infinity)", True),
            ("(h * P * k * A_c) * (T_0 - T_infinity)", False),
            ("sqrt(h * k / P * A_c) * (T_0 - T_infinity)", False),
            ("sqrt(h * P / k * A_c) * (T_0 - T_infinity)", False)
        ],
        "explanation": "For an infinitely long fin: q_fin = M = sqrt(h * P * k * A_c) * theta_0, where theta_0 = (T_0 - T_infinity)."
    },

    # Topic 11: Convection & Heat Exchangers
    {
        "topic_id": 11,
        "question_text": "[UPSC ESE Prelims — Dimensionless Numbers in Convection]\nThe Prandtl number (Pr) represents the physical ratio of:",
        "difficulty": "Easy",
        "options": [
            ("Kinematic viscosity (momentum diffusivity) to thermal diffusivity", True),
            ("Inertia force to viscous force", False),
            ("Buoyancy force to viscous force", False),
            ("Convective heat transfer to conductive heat transfer", False)
        ],
        "explanation": "Pr = nu / alpha = (mu / rho) / (k / rho * C_p) = mu * C_p / k. It reflects the relative thickness of velocity boundary layer to thermal boundary layer."
    },
    {
        "topic_id": 11,
        "question_text": "[UPSC ESE Prelims — Heat Exchanger NTU Method]\nIn a heat exchanger where one fluid undergoes phase change (e.g., steam condenser or boiler evaporator where C_max -> infinity and heat capacity ratio C_r = C_min / C_max = 0), the effectiveness epsilon for both parallel and counter-flow is given by:",
        "difficulty": "Medium",
        "options": [
            ("epsilon = 1 - e^(-NTU)", True),
            ("epsilon = NTU / (1 + NTU)", False),
            ("epsilon = 1 - e^(-2 NTU)", False),
            ("epsilon = 0.5 * (1 - e^(-NTU))", False)
        ],
        "explanation": "When C_r = 0 (condenser or evaporator), the effectiveness formulas for all heat exchangers (parallel, counter-flow, cross-flow) collapse identically to: epsilon = 1 - e^(-NTU)."
    },
    {
        "topic_id": 11,
        "question_text": "[UPSC ESE Prelims — LMTD Correction Factor]\nFor identical inlet and outlet temperatures, which of the following comparisons between Counter-Flow and Parallel-Flow heat exchangers is correct?",
        "difficulty": "Easy",
        "options": [
            ("LMTD of counter-flow is strictly greater than parallel-flow, requiring smaller heat transfer area", True),
            ("LMTD of parallel-flow is greater than counter-flow", False),
            ("In parallel flow, cold fluid exit temperature can exceed hot fluid exit temperature", False),
            ("Both exchangers require identical heat transfer area for the same heat duty", False)
        ],
        "explanation": "For identical temperatures: LMTD_counter > LMTD_parallel. Therefore, since Q = U * A * LMTD, the counter-flow heat exchanger requires less surface area (A_counter < A_parallel). Furthermore, counter-flow allows T_cold,out > T_hot,out, which is impossible in parallel flow."
    },

    # Topic 12: Thermal Radiation
    {
        "topic_id": 12,
        "question_text": "[UPSC ESE Prelims — Radiation Stefan-Boltzmann Law]\nA blackbody at absolute temperature T emits total radiant power E_b. If the absolute temperature is doubled (2T), by what factor does the total emissive power increase?",
        "difficulty": "Easy",
        "options": [
            ("4", False),
            ("8", False),
            ("16", True),
            ("32", False)
        ],
        "explanation": "Stefan-Boltzmann Law: E_b = sigma * T^4. If T becomes 2T: E_b' = sigma * (2T)^4 = 16 * (sigma * T^4) = 16 times."
    },
    {
        "topic_id": 12,
        "question_text": "[UPSC ESE Prelims — Radiation Shape Factors]\nA hemispherical cavity of radius R has its flat circular base closed. What is the view factor F_{11} of the hemispherical surface 1 to itself?",
        "difficulty": "Medium",
        "options": [
            ("0.25", False),
            ("0.50", True),
            ("0.75", False),
            ("1.0", False)
        ],
        "explanation": "Let 1 = hemispherical surface, 2 = flat base.\nFlat surface cannot see itself: F_{22} = 0 ==> F_{21} = 1.\nBy reciprocity theorem: A_1 * F_{12} = A_2 * F_{21}.\nHere A_1 = 2 * pi * R^2, A_2 = pi * R^2.\n(2 * pi * R^2) * F_{12} = (pi * R^2) * 1 ==> F_{12} = 1/2 = 0.5.\nBy summation rule for surface 1: F_{11} + F_{12} = 1 ==> F_{11} = 1 - 0.5 = 0.5."
    },
    {
        "topic_id": 12,
        "question_text": "[UPSC ESE Prelims — Radiation Shields]\nBetween two large parallel black plates exchanging heat by radiation, n identical radiation shields with emissivity equal to the plates are inserted. The net radiative heat transfer rate is reduced by a factor of:",
        "difficulty": "Medium",
        "options": [
            ("1 / (n + 1)", True),
            ("1 / n", False),
            ("1 / (2n + 1)", False),
            ("1 / 2^n", False)
        ],
        "explanation": "With n shields of identical emissivity inserted between two parallel surfaces: Q_with_shields = [1 / (n + 1)] * Q_without_shields."
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
        print(f"Successfully added {added} authentic UPSC ESE Prelims questions for Wing A: Thermal & Fluids (Topics 1-12)!")

if __name__ == '__main__':
    main()
