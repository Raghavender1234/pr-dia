# -*- coding: utf-8 -*-
"""
Seed authentic UPSC ESE Prelims MCQs for Paper-II Mechanical Engineering:
Subject 3: IC Engines, Refrigeration & Air Conditioning (Topics 13-17)
Subject 4: Power Plant Engineering & Renewable Energy (Topics 18-22)
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.question import Question, MCQOption

QUESTIONS = [
    # ==================== SUBJECT 3: IC ENGINES, RAC ====================
    # Topic 13: Air Standard Cycles
    {
        "topic_id": 13,
        "question_text": "[UPSC ESE Prelims — Air Standard Cycles]\nFor the same compression ratio r and same heat input, what is the correct relationship between the thermal efficiencies of Otto, Dual, and Diesel cycles?",
        "difficulty": "Easy",
        "options": [
            ("eta_Otto > eta_Dual > eta_Diesel", True),
            ("eta_Diesel > eta_Dual > eta_Otto", False),
            ("eta_Otto = eta_Dual = eta_Diesel", False),
            ("eta_Diesel > eta_Otto > eta_Dual", False)
        ],
        "explanation": "For same compression ratio and heat input, heat rejection is minimum in Otto cycle and maximum in Diesel cycle. Since eta = 1 - Q_R / Q_S: eta_Otto > eta_Dual > eta_Diesel. (Note: For same peak pressure and temperature: eta_Diesel > eta_Dual > eta_Otto)."
    },
    {
        "topic_id": 13,
        "question_text": "[UPSC ESE Prelims — Brayton Cycle Pressure Ratio]\nIn an ideal air-standard Brayton cycle operating between maximum temperature T_max and minimum temperature T_min, the pressure ratio r_p that yields maximum net work output is:",
        "difficulty": "Medium",
        "options": [
            ("r_p = (T_max / T_min)^[gamma / (2*(gamma - 1))]", True),
            ("r_p = (T_max / T_min)^[(gamma - 1) / gamma]", False),
            ("r_p = sqrt(T_max / T_min)", False),
            ("r_p = (T_max / T_min)^[2*gamma / (gamma - 1)]", False)
        ],
        "explanation": "Maximum work condition for Brayton cycle: T_2 = T_4 = sqrt(T_1 * T_3) = sqrt(T_min * T_max). This gives optimum pressure ratio r_p,opt = (T_max / T_min)^[gamma / (2*(gamma - 1))]."
    },
    {
        "topic_id": 13,
        "question_text": "[UPSC ESE Prelims — Mean Effective Pressure]\nThe Mean Effective Pressure (mep) of an internal combustion engine is physically defined as:",
        "difficulty": "Easy",
        "options": [
            ("Net work done per cycle divided by piston displacement volume (V_s)", True),
            ("Maximum cylinder pressure divided by clearance volume (V_c)", False),
            ("Brake power divided by engine speed in rpm", False),
            ("Total heat input divided by cylinder total volume", False)
        ],
        "explanation": "mep = W_net / (V_1 - V_2) = W_net / V_s, where V_s is the swept volume."
    },

    # Topic 14: Combustion in SI & CI Engines
    {
        "topic_id": 14,
        "question_text": "[UPSC ESE Prelims — Knocking in SI vs CI Engines]\nWhich of the following operational factors reduces the tendency of knocking in a Spark Ignition (SI) engine but INCREASES the knocking tendency in a Compression Ignition (CI) engine?",
        "difficulty": "Medium",
        "options": [
            ("Increasing compression ratio", False),
            ("Increasing engine speed (rpm)", True),
            ("Increasing intake air temperature", False),
            ("Advancing injection/spark timing", False)
        ],
        "explanation": "In SI engines, higher engine speed increases turbulence and flame speed, reducing the time available for end gas to auto-ignite -> REDUCES knocking. In CI engines, higher rpm decreases physical time for fuel vaporization and mixing during ignition delay period, leading to accumulation of unburned fuel -> INCREASES knocking tendency."
    },
    {
        "topic_id": 14,
        "question_text": "[UPSC ESE Prelims — Fuel Rating Octane & Cetane]\nMatch List-I (Reference Fuel) with List-II (Assigned Value):\nList-I:\nA. Iso-octane\nB. n-Heptane\nC. Cetane (Hexadecane)\nD. alpha-Methyl naphthalene\nList-II:\n1. Cetane number = 0\n2. Octane number = 100\n3. Octane number = 0\n4. Cetane number = 100\nSelect the correct code:",
        "difficulty": "Easy",
        "options": [
            ("A-2, B-3, C-4, D-1", True),
            ("A-3, B-2, C-1, D-4", False),
            ("A-2, B-1, C-4, D-3", False),
            ("A-4, B-3, C-2, D-1", False)
        ],
        "explanation": "Iso-octane = Octane 100; n-Heptane = Octane 0; Cetane = Cetane 100; alpha-Methyl naphthalene = Cetane 0 (or Heptamethylnonane HMN = 15)."
    },
    {
        "topic_id": 14,
        "question_text": "[UPSC ESE Prelims — Engine Emissions & Catalytic Converters]\nIn a Three-Way Catalytic Converter (TWC) of a modern petrol automobile, the reduction catalyst and oxidation catalyst typically consist of noble metals:",
        "difficulty": "Medium",
        "options": [
            ("Platinum (Pt) and Rhodium (Rh)", True),
            ("Copper and Nickel", False),
            ("Aluminum and Cobalt", False),
            ("Silver and Titanium", False)
        ],
        "explanation": "Three-way catalytic converters use Rhodium (Rh) as the primary reduction catalyst to reduce NOx to N2 and O2, and Platinum (Pt) / Palladium (Pd) as oxidation catalysts to oxidize CO and unburnt hydrocarbons (HC) to CO2 and H2O."
    },

    # Topic 15: Vapour Compression Refrigeration Cycle (VCR)
    {
        "topic_id": 15,
        "question_text": "[UPSC ESE Prelims — VCR Cycle Performance]\nIn a standard vapour compression refrigeration (VCR) cycle, subcooling of the liquid refrigerant before the expansion valve without changing evaporator temperature results in:",
        "difficulty": "Medium",
        "options": [
            ("Increase in refrigerating effect and increase in COP", True),
            ("Decrease in refrigerating effect and decrease in COP", False),
            ("Increase in compressor work with no change in COP", False),
            ("Decrease in volumetric efficiency of the compressor", False)
        ],
        "explanation": "Subcooling moves the throttling entry point leftward on p-h diagram, increasing the refrigerating effect (h_1 - h_4) without altering compressor work (h_2 - h_1). Therefore, COP = (h_1 - h_4) / (h_2 - h_1) INCREASES."
    },
    {
        "topic_id": 15,
        "question_text": "[UPSC ESE Prelims — COP of VCR System]\nA refrigeration plant operates on simple VCR cycle using R-134a. The enthalpies are: Evaporator exit = 250 kJ/kg; Compressor exit = 280 kJ/kg; Condenser exit = 100 kJ/kg. What is the COP of the plant?",
        "difficulty": "Easy",
        "options": [
            ("5.0", True),
            ("4.0", False),
            ("6.0", False),
            ("3.5", False)
        ],
        "explanation": "Refrigerating effect q_e = h_1 - h_4 = 250 - 100 = 150 kJ/kg (since throttling is isenthalpic: h_4 = h_3 = 100 kJ/kg).\nCompressor work w_c = h_2 - h_1 = 280 - 250 = 30 kJ/kg.\nCOP = q_e / w_c = 150 / 30 = 5.0."
    },
    {
        "topic_id": 15,
        "question_text": "[UPSC ESE Prelims — Ton of Refrigeration]\nOne Ton of Refrigeration (1 TR) is mathematically equivalent to the extraction of heat at the rate of:",
        "difficulty": "Easy",
        "options": [
            ("3.517 kW (210 kJ/min)", True),
            ("2.50 kW (150 kJ/min)", False),
            ("4.184 kW (250 kJ/min)", False),
            ("1.0 kW (60 kJ/min)", False)
        ],
        "explanation": "1 TR is defined as the latent heat absorbed to freeze 1 short ton (2000 lb approx 907.18 kg) of pure water at 0 deg C into ice at 0 deg C in 24 hours. Latent heat of ice = 333.55 kJ/kg. 1 TR = (907.18 * 333.55) / (24 * 3600) = 3.5167 kW approx 3.517 kW = 211 kJ/min approx 210 kJ/min."
    },

    # Topic 16: Vapour Absorption & Refrigerants
    {
        "topic_id": 16,
        "question_text": "[UPSC ESE Prelims — Vapour Absorption Refrigeration (VAR)]\nIn an Aqua-Ammonia (NH3-H2O) vapour absorption refrigeration system, which substance acts as the refrigerant and which acts as the absorbent?",
        "difficulty": "Easy",
        "options": [
            ("Ammonia is refrigerant and Water is absorbent", True),
            ("Water is refrigerant and Ammonia is absorbent", False),
            ("Lithium Bromide is refrigerant and Water is absorbent", False),
            ("Water is refrigerant and Lithium Bromide is absorbent", False)
        ],
        "explanation": "In Aqua-Ammonia VAR: Ammonia (NH3) is the volatile REFRIGERANT (boiling point -33.3 deg C) and Water (H2O) is the ABSORBENT. In LiBr-Water VAR: Water is the REFRIGERANT and LiBr salt solution is the ABSORBENT."
    },
    {
        "topic_id": 16,
        "question_text": "[UPSC ESE Prelims — Maximum COP of VAR System]\nIn a vapour absorption refrigeration system, heat Q_g is supplied at generator temperature T_g, heat Q_e is absorbed at evaporator temperature T_e, and heat is rejected to ambient atmosphere at temperature T_0. The maximum theoretical COP is given by:",
        "difficulty": "Medium",
        "options": [
            ("COP_max = [1 - (T_0 / T_g)] * [T_e / (T_0 - T_e)]", True),
            ("COP_max = [T_g / (T_g - T_0)] * [T_e / T_0]", False),
            ("COP_max = [T_e / (T_g - T_e)]", False),
            ("COP_max = [T_g / T_0] * [(T_0 - T_e) / T_e]", False)
        ],
        "explanation": "A VAR system can be modeled as a Carnot engine (operating between T_g and T_0) driving a Carnot refrigerator (operating between T_e and T_0). COP_max = eta_Carnot * COP_refrig = [(T_g - T_0)/T_g] * [T_e / (T_0 - T_e)] = [1 - T_0/T_g] * [T_e / (T_0 - T_e)]."
    },
    {
        "topic_id": 16,
        "question_text": "[UPSC ESE Prelims — Refrigerant Nomenclature]\nAccording to the ASHRAE refrigerant designation R-(c-1)(h+1)f, what is the chemical formula of refrigerant R-134a?",
        "difficulty": "Medium",
        "options": [
            ("CF3-CH2F (Tetrafluoroethane)", True),
            ("CCl2F2 (Dichlorodifluoromethane)", False),
            ("CHClF2 (Chlorodifluoromethane)", False),
            ("CH2F2 (Difluoromethane)", False)
        ],
        "explanation": "For R-134a: c - 1 = 1 ==> c = 2 carbon atoms; h + 1 = 3 ==> h = 2 hydrogen atoms; f = 4 fluorine atoms. Chemical formula: C2H2F4 (1,1,1,2-Tetrafluoroethane, CF3-CH2F)."
    },

    # Topic 17: Psychrometry & Air Conditioning
    {
        "topic_id": 17,
        "question_text": "[UPSC ESE Prelims — Psychrometric Processes]\nDuring a sensible heating process of moist atmospheric air, which of the following psychrometric properties remains CONSTANT?",
        "difficulty": "Easy",
        "options": [
            ("Specific humidity (humidity ratio omega) and Dew Point Temperature (DPT)", True),
            ("Relative Humidity (RH) and Dry Bulb Temperature (DBT)", False),
            ("Wet Bulb Temperature (WBT) and Enthalpy", False),
            ("Relative Humidity and Specific Volume", False)
        ],
        "explanation": "Sensible heating is represented by a horizontal line to the right on a psychrometric chart. Moisture content (omega) does not change, hence Dew Point Temperature (DPT) and partial pressure of water vapor remain strictly CONSTANT. (DBT increases, RH decreases)."
    },
    {
        "topic_id": 17,
        "question_text": "[UPSC ESE Prelims — Saturated Moist Air]\nFor completely saturated moist air (Relative Humidity phi = 100%), which of the following relationships holds true?",
        "difficulty": "Easy",
        "options": [
            ("DBT = WBT = DPT", True),
            ("DBT > WBT > DPT", False),
            ("DPT > WBT > DBT", False),
            ("DBT = WBT but DPT is zero", False)
        ],
        "explanation": "At 100% relative humidity, no further evaporation can occur: Dry Bulb Temperature (DBT), Wet Bulb Temperature (WBT), and Dew Point Temperature (DPT) are all identically equal (DBT = WBT = DPT)."
    },
    {
        "topic_id": 17,
        "question_text": "[UPSC ESE Prelims — By-pass Factor of Cooling Coil]\nAir enters a cooling coil at 30 deg C DBT and leaves at 18 deg C DBT. If the apparatus dew point (ADP) of the coil surface is 10 deg C, the by-pass factor (BPF) of the coil is:",
        "difficulty": "Medium",
        "options": [
            ("0.40", True),
            ("0.60", False),
            ("0.25", False),
            ("0.50", False)
        ],
        "explanation": "BPF = (T_exit - ADP) / (T_inlet - ADP) = (18 - 10) / (30 - 10) = 8 / 20 = 0.40. (Coil contact factor = 1 - BPF = 0.60)."
    },

    # ==================== SUBJECT 4: POWER PLANT & RENEWABLE ENERGY ====================
    # Topic 18: Rankine Cycle & Modifications
    {
        "topic_id": 18,
        "question_text": "[UPSC ESE Prelims — Rankine Cycle Reheating]\nWhat is the primary thermodynamic advantage of incorporating steam reheating in a modern thermal power plant Rankine cycle?",
        "difficulty": "Medium",
        "options": [
            ("To increase steam dryness fraction at turbine exhaust and protect low-pressure blades from droplet erosion", True),
            ("To drastically increase cycle thermal efficiency by over 20%", False),
            ("To reduce the size of the high pressure boiler drum", False),
            ("To eliminate the need for a steam condenser", False)
        ],
        "explanation": "While reheating provides a modest gain in cycle efficiency (about 3-5%), its primary engineering benefit is increasing the steam dryness fraction at LP turbine exhaust (keeping moisture < 10-12%) to prevent severe blade erosion."
    },
    {
        "topic_id": 18,
        "question_text": "[UPSC ESE Prelims — Regenerative Feed Heating]\nRegenerative feed water heating in a steam power plant increases thermal efficiency primarily because:",
        "difficulty": "Medium",
        "options": [
            ("It increases the mean temperature of heat addition (T_m1) in the boiler", True),
            ("It decreases the temperature of heat rejection in the condenser", False),
            ("It increases total work output per kg of boiler steam", False),
            ("It reduces pump work to zero", False)
        ],
        "explanation": "eta_Rankine = 1 - T_2 / T_m1. Regenerative heating uses extracted steam to pre-heat boiler feedwater, eliminating low-temperature heat addition in the economizer and thereby increasing the Mean Temperature of Heat Addition (T_m1)."
    },
    {
        "topic_id": 18,
        "question_text": "[UPSC ESE Prelims — Binary Vapour Cycle]\nIn a Mercury-Steam binary vapour power cycle, mercury is selected as the topping fluid primarily because of its:",
        "difficulty": "Medium",
        "options": [
            ("High critical temperature (approx 1490 deg C) and low saturation pressure at high temperatures", True),
            ("High freezing point and non-toxic properties", False),
            ("High latent heat of vaporization compared to water", False),
            ("Extremely low molecular weight", False)
        ],
        "explanation": "Mercury has a high critical temperature (1490 deg C) and reasonable saturation pressure (approx 12-14 bar at 550 deg C), allowing high-temperature heat addition without immense supercritical pressures."
    },

    # Topic 19: High Pressure Boilers & Draught
    {
        "topic_id": 19,
        "question_text": "[UPSC ESE Prelims — Boiler Mountings vs Accessories]\nWhich of the following components of a steam boiler is classified as a BOILER MOUNTING (essential for safe operation) rather than a boiler accessory?",
        "difficulty": "Easy",
        "options": [
            ("Fusible Plug", True),
            ("Economizer", False),
            ("Superheater", False),
            ("Air Preheater", False)
        ],
        "explanation": "Boiler Mountings (safety & operation): Safety valves, Water level indicator, Pressure gauge, Fusible plug, Blow-off cock, Feed check valve.\nBoiler Accessories (efficiency enhancement): Economizer, Superheater, Air Preheater, Feed pump, Steam trap."
    },
    {
        "topic_id": 19,
        "question_text": "[UPSC ESE Prelims — Once-Through Supercritical Boilers]\nBenson boiler is a high-pressure once-through boiler that operates above the critical pressure of water (P > 22.09 MPa). A key distinctive feature of the Benson boiler is:",
        "difficulty": "Medium",
        "options": [
            ("It operates without any steam boiler drum", True),
            ("It requires an external forced circulation pump of 20 bar head", False),
            ("It has natural circulation driven by large density differences", False),
            ("It uses fire-tubes submerged in water", False)
        ],
        "explanation": "At supercritical pressures, water transforms directly into steam without boiling/bubbles (latent heat = 0). Hence, no phase separation is required, completely eliminating the steam drum (drumless once-through boiler)."
    },
    {
        "topic_id": 19,
        "question_text": "[UPSC ESE Prelims — Balanced Draught System]\nIn a modern utility thermal boiler, a 'Balanced Draught' system employs:",
        "difficulty": "Easy",
        "options": [
            ("Both a Forced Draught (FD) fan to deliver combustion air and an Induced Draught (ID) fan to maintain slight negative pressure in furnace", True),
            ("Only a single high-capacity natural draught chimney", False),
            ("Two forced draught fans operating in parallel without an ID fan", False),
            ("A steam jet draught system in the flue duct", False)
        ],
        "explanation": "Balanced draught uses an FD fan to force combustion air through air preheaters/burners and an ID fan to draw flue gases through economizers/ESP out through the chimney, maintaining slight negative pressure (-2 to -5 mm of water) in the furnace to prevent hot gas blowout."
    },

    # Topic 20: Condensers, Cooling Towers & Gas Turbines
    {
        "topic_id": 20,
        "question_text": "[UPSC ESE Prelims — Steam Condenser Vacuum Efficiency]\nIn a surface condenser, the vacuum efficiency is defined as the ratio of:",
        "difficulty": "Medium",
        "options": [
            ("Actual vacuum recorded by vacuum gauge to the ideal vacuum (Barometric pressure - Saturation pressure at condenser steam temperature)", True),
            ("Condenser pressure to atmospheric pressure", False),
            ("Mass of cooling water to mass of condensed steam", False),
            ("Temperature of condensate to inlet cooling water temperature", False)
        ],
        "explanation": "Vacuum Efficiency = (Actual Vacuum) / (Ideal Vacuum) = (P_barometric - P_condenser) / (P_barometric - P_sat(T_steam)). Air leakage increases P_condenser and reduces vacuum efficiency."
    },
    {
        "topic_id": 20,
        "question_text": "[UPSC ESE Prelims — Cooling Towers Approach & Range]\nIn industrial evaporative cooling tower terminology, the 'Approach' is defined as the difference between:",
        "difficulty": "Medium",
        "options": [
            ("Cold water temperature leaving the tower and Ambient air Wet Bulb Temperature (WBT)", True),
            ("Hot water temperature entering the tower and cold water temperature leaving the tower", False),
            ("Cold water temperature leaving the tower and Dry Bulb Temperature (DBT)", False),
            ("Hot water entering temperature and Ambient air Wet Bulb Temperature", False)
        ],
        "explanation": "Cooling Range = T_hot_in - T_cold_out.\nCooling Approach = T_cold_out - WBT_ambient. Approach indicates how closely the leaving water approaches the lowest theoretical limit (ambient WBT)."
    },
    {
        "topic_id": 20,
        "question_text": "[UPSC ESE Prelims — Gas Turbine Blade Cooling]\nIn modern high-temperature gas turbine power plants, film cooling of nozzle guide vanes and rotor blades works by:",
        "difficulty": "Medium",
        "options": [
            ("Discharging bleed compressor air through tiny shaped holes on the blade surface to form an insulating protective boundary layer", True),
            ("Circulating cold liquid sodium through internal closed channels", False),
            ("Spraying high-pressure water droplets directly into the combustion chamber", False),
            ("Applying high-emissivity ceramic paints on the trailing edge only", False)
        ],
        "explanation": "Film cooling injects high-pressure cool air bled from compressor discharge through small laser-drilled angled holes over the turbine blade aerofoil surface, creating a continuous protective thermal boundary layer that isolates blade metal from 1400-1600 deg C hot combustion gases."
    },

    # Topic 21: Nuclear Power Plants & Hydel Power
    {
        "topic_id": 21,
        "question_text": "[UPSC ESE Prelims — Nuclear Reactor Moderator]\nIn a thermal nuclear reactor, the primary physical function of a moderator (such as Heavy Water D2O or High-Purity Graphite) is to:",
        "difficulty": "Easy",
        "options": [
            ("Slow down fast fission neutrons (approx 2 MeV) to thermal energy levels (approx 0.025 eV) without absorbing them", True),
            ("Absorb excess thermal neutrons to shut down the chain reaction", False),
            ("Extract fission heat from fuel bundles to the steam generator", False),
            ("Shield personnel from gamma and beta radiation", False)
        ],
        "explanation": "Neutrons born from U-235 fission are fast (~2 MeV) with low fission capture cross-section. The moderator slows them down via elastic collisions to thermal energy (~0.025 eV), where fission cross-section is hundreds of times higher. (Control rods like Boron/Cadmium absorb neutrons)."
    },
    {
        "topic_id": 21,
        "question_text": "[UPSC ESE Prelims — Indian Nuclear Power Program]\nIndia's indigenous Pressurized Heavy Water Reactors (PHWRs) utilize which combination of nuclear fuel and coolant/moderator?",
        "difficulty": "Easy",
        "options": [
            ("Natural Uranium dioxide (UO2) fuel with Heavy Water (D2O) as both moderator and coolant", True),
            ("Enriched Uranium (3% U-235) with Light Water (H2O) as moderator", False),
            ("Plutonium-239 with Liquid Sodium as coolant", False),
            ("Thorium-232 with Molten Salt as coolant", False)
        ],
        "explanation": "Indian Stage-1 PHWRs (e.g. Kakrapar, Narora, Kaiga) use Natural Uranium (~0.7% U-235) as fuel, which requires Heavy Water (D2O) as moderator and primary coolant because D2O has an exceptionally low neutron absorption cross-section."
    },
    {
        "topic_id": 21,
        "question_text": "[UPSC ESE Prelims — Hydel Power Surge Tanks]\nA surge tank is installed on the penstock conduit of a high-head hydroelectric power installation primarily to:",
        "difficulty": "Easy",
        "options": [
            ("Relieve high pressure transients (water hammer) during sudden load rejection and supply water during sudden load demand", True),
            ("Filter silt and floating debris before entering the runner", False),
            ("Increase the gross head available at the turbine nozzle", False),
            ("Prevent cavitation in the tail race canal", False)
        ],
        "explanation": "A surge tank acts as an open water storage buffer between long headrace tunnel and penstocks. It absorbs water hammer pressure surges when governor rapidly closes turbine gates, and provides emergency flow during sudden governor opening."
    },

    # Topic 22: Solar, Wind, Biomass & Renewable Energy
    {
        "topic_id": 22,
        "question_text": "[UPSC ESE Prelims — Solar Photovoltaic Cell Fill Factor]\nIn the characterization of a solar photovoltaic (PV) cell, the Fill Factor (FF) is defined by which formula?",
        "difficulty": "Medium",
        "options": [
            ("FF = (V_mp * I_mp) / (V_oc * I_sc)", True),
            ("FF = (V_oc * I_sc) / (V_mp * I_mp)", False),
            ("FF = V_mp / V_oc", False),
            ("FF = I_mp / I_sc", False)
        ],
        "explanation": "Fill Factor (FF) = Maximum Power Output / (Open-Circuit Voltage * Short-Circuit Current) = (V_mp * I_mp) / (V_oc * I_sc). It measures the squareness of the I-V curve; typical high-quality silicon cells have FF between 0.75 and 0.85."
    },
    {
        "topic_id": 22,
        "question_text": "[UPSC ESE Prelims — Fuel Cell Thermodynamics]\nIn a Proton Exchange Membrane Fuel Cell (PEMFC) operating on pure hydrogen and oxygen, the theoretical maximum electrical efficiency is given by the ratio of:",
        "difficulty": "Medium",
        "options": [
            ("Change in Gibbs Free Energy (Delta G) to Change in Enthalpy (Delta H)", True),
            ("Change in Enthalpy (Delta H) to Change in Entropy (T Delta S)", False),
            ("Carnot efficiency based on cell operating temperature", False),
            ("Faraday constant to molar mass of hydrogen", False)
        ],
        "explanation": "Unlike heat engines governed by Carnot limits, fuel cells convert chemical energy directly to electricity electrochemically. The maximum theoretical reversible efficiency eta_max = Delta G / Delta H (approx 83% at standard conditions for liquid water product)."
    },
    {
        "topic_id": 22,
        "question_text": "[UPSC ESE Prelims — Biomass Gasification Syngas]\nIn a downdraft biomass gasifier, the combustible components of the produced producer gas (syngas) are primarily:",
        "difficulty": "Medium",
        "options": [
            ("Carbon monoxide (CO), Hydrogen (H2), and Methane (CH4)", True),
            ("Carbon dioxide (CO2) and Nitrogen (N2) only", False),
            ("Sulfur dioxide (SO2) and Ammonia (NH3)", False),
            ("Pure Oxygen (O2) and Ethane (C2H6)", False)
        ],
        "explanation": "Producer gas produced by partial oxidation of biomass in air consists of combustible gases: CO (~20%), H2 (~15%), CH4 (~2-3%), along with inert gases N2 (~50%) and CO2 (~10-12%). Calorific value is approx 4.5 - 5.5 MJ/Nm^3."
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
        print(f"Successfully added {added} authentic UPSC ESE Prelims questions for Topics 13 to 22 (IC Engines, RAC, Power Plant & Renewables)!")

if __name__ == '__main__':
    main()
