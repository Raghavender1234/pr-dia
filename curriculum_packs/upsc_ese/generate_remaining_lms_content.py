# -*- coding: utf-8 -*-
"""
Generate comprehensive, publication-grade UPSC ESE study content for:
- Subject 9: Manufacturing & Production Engineering (Topics 46–51)
- Subject 11: Mechatronics & Robotics (Topics 57–61)
- Topic 65: General Principles of Design, Drawing & Safety (Detailed Modules)
- Topic 67: Basics of Energy and Environment (Detailed Modules)
- Topic 63: Engineering Aptitude (Detailed Modules)
- Topic 62: Current Issues (Detailed Modules)
- Topic 64: Engineering Mathematics (Modules 5 & 6)
"""
import sys, os
sys.path.insert(0, r"C:\Users\brred\Desktop\AI_Assistant\App\backend")
from app import create_app
from app.extensions import db
from app.models.topic import Topic, TopicContent

STYLE = """
<style>
  .upsc-ese-article {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 15.5px;
    line-height: 1.68;
    color: #1e293b;
    max-width: 100%;
    margin: 0 auto;
    background-color: #ffffff;
    padding: 8px 4px;
    box-sizing: border-box;
  }
  .upsc-ese-article * { box-sizing: border-box; }
  .upsc-ese-article .cover-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
    color: #ffffff !important;
    padding: 22px 24px;
    border-radius: 12px;
    margin-bottom: 22px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15);
  }
  .upsc-ese-article .cover-header h1 {
    margin: 0 0 8px 0 !important;
    font-size: 23px !important;
    line-height: 1.3 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    background: none !important;
    font-weight: 800 !important;
  }
  .upsc-ese-article .cover-header p {
    margin: 0 !important;
    font-size: 14.5px !important;
    color: #e2e8f0 !important;
    -webkit-text-fill-color: #e2e8f0 !important;
  }
  .upsc-ese-article .module-tag {
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
  }
  .upsc-ese-article h2 {
    color: #1e3a8a !important;
    -webkit-text-fill-color: #1e3a8a !important;
    background: none !important;
    border-bottom: 2.5px solid #2563eb;
    padding-bottom: 6px;
    font-size: 19.5px !important;
    font-weight: 700 !important;
    margin-top: 26px !important;
    margin-bottom: 12px !important;
  }
  .upsc-ese-article h3 {
    color: #0f4c81 !important;
    -webkit-text-fill-color: #0f4c81 !important;
    background: none !important;
    font-size: 16.5px !important;
    font-weight: 700 !important;
    margin-top: 18px !important;
    margin-bottom: 8px !important;
  }
  .upsc-ese-article .table-responsive {
    width: 100%;
    overflow-x: auto;
    margin: 14px 0 20px 0;
    border-radius: 8px;
  }
  .upsc-ese-article table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background: #fff;
  }
  .upsc-ese-article th, .upsc-ese-article td {
    border: 1px solid #cbd5e1;
    padding: 9px 12px;
    text-align: left;
    vertical-align: top;
  }
  .upsc-ese-article th {
    background-color: #eef2ff;
    color: #1e3a8a;
    font-weight: 700;
  }
  .upsc-ese-article tr:nth-child(even) td { background-color: #f8fafc; }
  .upsc-ese-article .box-upsc {
    background-color: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 5px solid #f59e0b;
    padding: 14px 16px;
    margin: 16px 0;
    border-radius: 0 8px 8px 0;
  }
  .upsc-ese-article .box-upsc-title {
    font-weight: 700;
    color: #b45309;
    font-size: 13.5px;
    margin-bottom: 5px;
    text-transform: uppercase;
  }
  .upsc-ese-article .box-tech {
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-left: 5px solid #0284c7;
    padding: 14px 16px;
    margin: 16px 0;
    border-radius: 0 8px 8px 0;
  }
  .upsc-ese-article .box-tech-title {
    font-weight: 700;
    color: #0369a1;
    font-size: 13.5px;
    margin-bottom: 5px;
    text-transform: uppercase;
  }
  .upsc-ese-article .grid-2 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px;
    margin: 14px 0;
  }
  .upsc-ese-article code {
    background: #f1f5f9;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 13.5px;
    color: #0f172a;
  }
</style>
"""

def wrap_art(tag, title, desc, body):
    return f"""{STYLE}
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">{tag}</span>
    <h1>{title}</h1>
    <p>{desc}</p>
  </div>
  {body}
</div>
"""

MODULES_DATA = {}

# ----------------- Subject 9: Manufacturing (Topics 46 to 51) -----------------
MODULES_DATA[46] = ("📘 Metal Casting Technology — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Manufacturing (Topic 46)",
    "Metal Casting: Pattern Allowances, Gating Design, Solidification Time &amp; Defects",
    "Complete textbook synthesis of P.N. Rao and Kalpakjian covering Chvorinov's Rule, Gating Ratios, Riser Design &amp; Casting Inspection.",
    """
    <h2>1. Pattern Allowances &amp; Sand Properties</h2>
    <p>A pattern is a replica of the object to be cast with necessary dimensional allowances:</p>
    <ul>
      <li><strong>Shrinkage Allowance:</strong> Liquid and solidification shrinkages are compensated by the <strong>riser</strong>; solid contraction from room temperature is compensated by pattern shrinkage allowance. Order of solid contraction: Invar (0) &lt; Cast Iron &lt; Steel &lt; Brass &lt; Copper &lt; Aluminum &lt; Zinc &lt; Lead. Liquid shrinkage is maximum for aluminum; solid shrinkage is maximum for zinc. (Note: Gray cast iron expands during solidification due to graphite precipitation!).</li>
      <li><strong>Draft (Taper) Allowance:</strong> Provided on vertical surfaces (typically 1° to 3°) to facilitate easy pattern withdrawal without damaging the sand mold cavity.</li>
      <li><strong>Machining / Finish Allowance:</strong> 1.5 to 3.0 mm extra material provided for subsequent machining operations.</li>
      <li><strong>Shake / Rapping Allowance:</strong> A negative allowance; pattern is made slightly smaller because rapping enlarges the mold cavity.</li>
      <li><strong>Distortion (Camber) Allowance:</strong> Provided for U, V, and L-shaped thin-section castings to prevent warpage during uneven cooling.</li>
    </ul>

    <h2>2. Gating System Design &amp; Gating Ratios</h2>
    <div class="table-responsive">
      <table>
        <tr><th>Gating Parameter</th><th>Pressurized Gating System</th><th>Unpressurized Gating System</th></tr>
        <tr><td><strong>Gating Ratio (A_sprue : A_runner : A_ingate)</strong></td><td>Decreasing area: e.g., <strong>4 : 2 : 1 or 2 : 2 : 1</strong> (Choke area is at the <strong>Ingate</strong>).</td><td>Increasing area: e.g., <strong>1 : 2 : 2 or 1 : 4 : 4</strong> (Choke area is at the <strong>Sprue Base</strong>).</td></tr>
        <tr><td><strong>Fluid Velocity &amp; Pressure</strong></td><td>High velocity at gate; causes turbulence and mold erosion. Runner remains full at all times.</td><td>Low velocity at gate; smooth laminar entry into cavity. Air aspiration can occur if sprue is not tapered!</td></tr>
        <tr><td><strong>Ideal Applications</strong></td><td>Ferrous metals (Cast Iron, Steels) where dross formation is low.</td><td>Non-ferrous alloys (Aluminum, Magnesium) prone to rapid oxidation and dross formation.</td></tr>
      </table>
    </div>

    <h2>3. Chvorinov's Rule &amp; Riser Design</h2>
    <div class="box-tech">
      <div class="box-tech-title">Chvorinov's Solidification Time Rule</div>
      <p>Solidification time $t_s$ of a casting depends on its geometric modulus (Volume $V$ to Surface Area $A$ ratio):</p>
      <p style="text-align:center; font-weight:bold; font-size:16px;">$$t_s = C \left(\frac{V}{A}\right)^n \quad (n \approx 2)$$</p>
      <p><strong>Caine's Riser Design:</strong> A riser must solidify <em>after</em> the casting. Therefore: $(V/A)_{\\text{riser}} &gt; (V/A)_{\\text{casting}}$. For an optimum cylindrical side riser: $h = d$; for an optimum top riser: $h = d/2$.</p>
    </div>

    <h2>4. Casting Defects &amp; Non-Destructive Testing</h2>
    <ul>
      <li><strong>Blowholes &amp; Pinholes:</strong> Smooth-walled spherical cavities caused by excessive moisture, low permeability, or poor venting.</li>
      <li><strong>Misrun &amp; Cold Shut:</strong> Incomplete filling of mold cavity or imperfect fusion of two converging metal streams due to <strong>low pouring temperature or low fluidity</strong>.</li>
      <li><strong>Hot Tears (Hot Cracking):</strong> Ragged, irregular tears caused by non-uniform cooling and high resistance to contraction (poor mold collapsibility).</li>
      <li><strong>Scab &amp; Rat Tail:</strong> Expansion defects on casting surface caused by excessive mold radiant heat causing thin sand layers to buckle.</li>
    </ul>
    """
))

MODULES_DATA[47] = ("📘 Metal Forming Processes — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Manufacturing (Topic 47)",
    "Metal Forming: Rolling, Forging, Extrusion, Wire Drawing &amp; Sheet Metal Operations",
    "Complete synthesis of Kalpakjian and P.N. Rao covering Rolling mechanics, neutral angle, draft, extrusion ratios, deep drawing &amp; clearance formulas.",
    """
    <h2>1. Mechanics of Rolling</h2>
    <ul>
      <li><strong>Angle of Bite &amp; Maximum Draft:</strong> Maximum reduction in thickness $\Delta h_{\max} = h_0 - h_f = \mu^2 R$, where $\mu$ is coefficient of friction and $R$ is roll radius. For self-entry without pushing: $\tan \alpha \le \mu$ (where $\alpha$ is bite angle).</li>
      <li><strong>Neutral (No-Slip) Point:</strong> The point in the roll gap where metal velocity equals roll peripheral surface velocity ($v = v_r$). Entry side: metal moves slower than rolls ($v &lt; v_r$; friction pulls metal in); Exit side: metal moves faster than rolls ($v &gt; v_r$; friction opposes motion).</li>
      <li><strong>Roll Camber:</strong> Rolls are ground with a crown (convexity at center) to counteract elastic deflection under heavy roll separating forces, producing uniform sheet thickness.</li>
    </ul>

    <h2>2. Forging, Extrusion &amp; Wire Drawing</h2>
    <div class="grid-2">
      <div class="box-tech">
        <div class="box-tech-title">Extrusion &amp; Drawing Formulations</div>
        <ul>
          <li><strong>Direct (Forward) vs Indirect (Backward) Extrusion:</strong> In direct extrusion, billet moves relative to container wall, incurring massive container wall friction. In indirect extrusion, billet is stationary; zero wall friction reduces extrusion force by 25–30%.</li>
          <li><strong>Extrusion Ratio ($R$):</strong> $R = A_0 / A_f$. True strain $\varepsilon = \ln(R)$.</li>
          <li><strong>Maximum Theoretical Reduction in Wire Drawing:</strong> For an ideal plastic material with zero friction and redundant work, maximum reduction per pass is $r_{\max} = 1 - e^{-1} \approx 63.2\%$ (corresponding to $\sigma_d = \sigma_y$).</li>
        </ul>
      </div>
      <div class="box-upsc">
        <div class="box-upsc-title">Sheet Metal Clearance &amp; Punching/Blanking Rules</div>
        <ul>
          <li><strong>Punching (Piercing) Operation (Hole is useful part):</strong> Punch diameter = Hole size; Die diameter = Punch size $+ 2c$.</li>
          <li><strong>Blanking Operation (Slug is useful part):</strong> Die diameter = Blank size; Punch diameter = Die size $- 2c$.</li>
          <li><strong>Radial Clearance ($c$):</strong> $c = 0.0032 \cdot t \cdot \sqrt{\tau}$ (typically $5\%\text{--}8\%$ of sheet thickness $t$).</li>
          <li><strong>Limiting Drawing Ratio (LDR):</strong> In deep drawing of cups, $LDR = D_{\max} / d \approx 2.0$ to $2.2$. If blank diameter exceeds $2d$, drawing must be performed in multiple stages with intermediate annealing.</li>
        </ul>
      </div>
    </div>
    """
))

MODULES_DATA[48] = ("📘 Metal Joining & Welding — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Manufacturing (Topic 48)",
    "Metal Joining: Arc, TIG, MIG, Resistance, Submerged Arc, Electron Beam &amp; Laser Welding",
    "Complete synthesis of P.N. Rao and Ghosh &amp; Mallik covering heat input, V-I arc characteristics, resistance spot welding &amp; HAZ defects.",
    """
    <h2>1. Welding Arc Characteristics &amp; Power Source Matching</h2>
    <p>The electric arc behaves like a non-linear variable resistor. The power source characteristic is typically a linear droop: $V = V_{oc} - \left(\frac{V_{oc}}{I_{sc}}\right) I$, and the arc characteristic is: $V = a + bL$.</p>
    <div class="box-tech">
      <div class="box-tech-title">Maximum Power Condition</div>
      <p>To maximize arc power ($P = V \cdot I$):</p>
      <p style="text-align:center; font-weight:bold; font-size:16px;">$$V_{\\text{opt}} = \\frac{V_{oc}}{2}, \\qquad I_{\\text{opt}} = \\frac{I_{sc}}{2} \\implies P_{\\max} = \\frac{V_{oc} \\cdot I_{sc}}{4}$$</p>
    </div>

    <h2>2. Advanced Welding Processes Comparison</h2>
    <div class="table-responsive">
      <table>
        <tr><th>Process</th><th>Electrode &amp; Shielding</th><th>Distinguishing Mechanism &amp; Key Applications</th></tr>
        <tr><td><strong>TIG (GTAW)</strong></td><td>Non-consumable Tungsten; Argon/Helium gas.</td><td>High-precision, cleanest welds without flux; pulsed DC for thin aluminum/magnesium and stainless steel aerospace tubes. High-frequency unit for arc ignition.</td></tr>
        <tr><td><strong>MIG / GMAW</strong></td><td>Consumable wire fed automatically; Argon/CO2.</td><td>High deposition rate; spray/globular/short-circuit transfer modes. CO2 (MAG) used for structural carbon steels.</td></tr>
        <tr><td><strong>Submerged Arc (SAW)</strong></td><td>Consumable bare wire under granular flux blanket.</td><td>Extremely high currents (up to 2000 A); deep penetration, 100% spatter-free; restricted strictly to flat/horizontal positions on thick plates.</td></tr>
        <tr><td><strong>Resistance Spot Welding</strong></td><td>Non-consumable Copper-alloy water-cooled tips.</td><td>Heat generated by contact resistance ($H = I^2 R t$). Nugget forms at interface. High currents (10,000 A) at low voltage (2–10 V) in milliseconds. Automobile car bodies.</td></tr>
        <tr><td><strong>Laser &amp; Electron Beam (EBW)</strong></td><td>Focused coherent photons / accelerated electrons in high vacuum.</td><td>Extremely high power density ($10^6\text{--}10^8\text{ W/cm}^2$); narrow deep keyhole welds; depth-to-width ratio up to <strong>20 : 1</strong>; minimum Heat Affected Zone (HAZ).</td></tr>
      </table>
    </div>
    """
))

MODULES_DATA[49] = ("📘 Metal Cutting & Machine Tools — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Manufacturing (Topic 49)",
    "Metal Cutting: Merchant's Circle Analysis, Taylor's Tool Life Equation &amp; Machinability",
    "Complete synthesis of Amitabha Ghosh &amp; Asok Kumar Mallik covering Merchant's shear angle, tool signatures, cutting forces &amp; economics.",
    """
    <h2>1. Tool Geometry &amp; Tool Signatures</h2>
    <ul>
      <li><strong>ASA Tool Signature (7 Elements):</strong> Back Rake Angle &ndash; Side Rake Angle &ndash; End Relief Angle &ndash; Side Relief Angle &ndash; End Cutting Edge Angle &ndash; Side Cutting Edge Angle &ndash; Nose Radius ($r$ in mm or inches). E.g., <code>0-7-7-7-15-15-0.8 mm</code>.</li>
      <li><strong>Orthogonal Rake System (ORS / ISO Signature):</strong> Inclination Angle ($i$) &ndash; Normal Rake Angle ($\alpha_n$) &ndash; Side Relief Angle &ndash; End Relief Angle &ndash; Principal Cutting Edge Angle ($\lambda$) &ndash; Auxiliary Cutting Edge Angle &ndash; Nose Radius. (Pure orthogonal cutting when $i = 0$).</li>
    </ul>

    <h2>2. Merchant's Circle Force Analysis</h2>
    <p>In orthogonal cutting, chip thickness ratio $r = t_1 / t_2 = \frac{\sin \phi}{\cos(\phi - \alpha)}$. Merchant's minimum energy criterion gives the optimum shear angle $\phi$:</p>
    <div class="box-tech">
      <div class="box-tech-title">Merchant's Optimum Shear Angle Relation</div>
      <p style="text-align:center; font-weight:bold; font-size:16px;">$$\phi = \\frac{\\pi}{4} - \\frac{\\beta}{2} + \\frac{\\alpha}{2} = 45^\\circ - \\frac{\\beta - \\alpha}{2}$$</p>
      <p>Where $\alpha$ is orthogonal rake angle and $\beta = \\tan^{-1}(\\mu)$ is friction angle at tool-chip interface.</p>
    </div>

    <h2>3. Taylor's Tool Life Equation &amp; Machining Economics</h2>
    <p>Taylor's equation relates cutting speed $V$ (m/min) and tool life $T$ (minutes): $V T^n = C$. Typical exponent $n$: High-Speed Steel (HSS) $n \approx 0.1\text{--}0.2$; Tungsten Carbide $n \approx 0.2\text{--}0.4$; Ceramics $n \approx 0.4\text{--}0.6$; CBN/PCD $n \approx 0.6\text{--}0.8$.</p>
    <div class="box-upsc">
      <div class="box-upsc-title">Optimum Cutting Speed for Minimum Cost &amp; Max Production Rate</div>
      <ul>
        <li><strong>Cutting Speed for Maximum Production Rate ($V_{\\max}$):</strong> $T_{\\text{opt}} = \\left(\\frac{1 - n}{n}\\right) T_c$, where $T_c$ is tool change time.</li>
        <li><strong>Cutting Speed for Minimum Cost of Operation ($V_{\\min}$):</strong> $T_{\\text{opt}} = \\left(\\frac{1 - n}{n}\\right) \\left(T_c + \\frac{C_t}{C_m}\\right)$, where $C_t$ is tool cost per edge and $C_m$ is machine labor rate.</li>
      </ul>
    </div>
    """
))

MODULES_DATA[50] = ("📘 Machine Tools, CNC & Non-Traditional Machining — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Manufacturing (Topic 50)",
    "Machine Tools (Lathe, Milling, Grinding), CNC G-Codes &amp; Advanced Machining (EDM, ECM, USM, LBM)",
    "Complete synthesis of P.N. Rao and Kalpakjian covering grinding mechanics, CNC coordinate systems &amp; non-traditional metal removal mechanisms.",
    """
    <h2>1. Machine Tools: Lathe, Milling &amp; Grinding</h2>
    <ul>
      <li><strong>Up-Milling (Conventional) vs Down-Milling (Climb):</strong> In Up-milling, chip thickness starts at zero and increases to maximum; cutter forces tend to lift the workpiece; higher tool wear due to rubbing. In Down-milling, chip thickness starts at maximum and decreases to zero; cutter pushes workpiece down; requires backlash eliminator on feed screw!</li>
      <li><strong>Grinding Wheel Specification (IS Standard):</strong> E.g., <code>W &ndash; A &ndash; 46 &ndash; K &ndash; 5 &ndash; V &ndash; 17</code>:
        <ul>
          <li><code>A</code>: Abrasive type (A = Aluminum Oxide for ferrous; C = Silicon Carbide for non-ferrous/cast iron; D = Diamond; B = CBN).</li>
          <li><code>46</code>: Grain size (Coarse 10–24, Medium 30–60, Fine 70–180, Very Fine 220–600).</li>
          <li><code>K</code>: Grade / Hardness of bond (A to H soft; I to P medium; Q to Z hard).</li>
          <li><code>5</code>: Structure (0 to 8 dense; 9 to 16 open).</li>
          <li><code>V</code>: Bond type (V = Vitrified, most common; B = Resinoid; R = Rubber; S = Silicate; E = Shellac).</li>
        </ul>
      </li>
    </ul>

    <h2>2. Non-Traditional Machining (NTM) Mechanism Matrix</h2>
    <div class="table-responsive">
      <table>
        <tr><th>Process</th><th>Mechanism of Metal Removal</th><th>Electrolyte / Medium</th><th>Key UPSC Facts &amp; MRR Dependency</th></tr>
        <tr><td><strong>EDM (Electric Discharge Machining)</strong></td><td>Melting and vaporization by controlled spark erosion between tool and workpiece.</td><td>Dielectric fluid (Kerosene / Deionized water).</td><td>Tool must be electrically conductive (Copper/Graphite). Zero mechanical force; can machine any hardness if conductive. Relaxation circuit: $f = 1 / [R C \ln(V_0 / (V_0 - V_d))]$.</td></tr>
        <tr><td><strong>ECM (Electrochemical Machining)</strong></td><td>Anodic dissolution by electrolysis following Faraday's Laws ($MRR = \frac{A \cdot I}{\rho \cdot z \cdot F}$).</td><td>Conductive aqueous electrolyte (NaCl / NaNO3).</td><td>Tool wear is zero; no thermal damage or residual stress. High current density (50–500 A/cm²); dangerous hydrogen gas generation.</td></tr>
        <tr><td><strong>USM (Ultrasonic Machining)</strong></td><td>Mechanical micro-chipping/abrasion by high-frequency abrasive slurry impact.</td><td>Abrasive slurry (B4C / SiC in water) at 20–40 kHz.</td><td>Ideal for hard, brittle non-conductive materials (Glass, Ceramics, Quartz, Gemstones). Magnetostrictive transducer.</td></tr>
        <tr><td><strong>AJM / WJM / AWJM</strong></td><td>Erosion by high-velocity abrasive gas jet / water jet.</td><td>Abrasive particles in pressurized gas/water.</td><td>Deflashing, cleaning, micro-machining brittle glass/resins.</td></tr>
      </table>
    </div>
    """
))

MODULES_DATA[51] = ("📘 Metrology & Inspection — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Manufacturing (Topic 51)",
    "Metrology: Limits, Fits, Tolerances, Taylor's Principle, Gauge Design &amp; Surface Roughness",
    "Complete synthesis of R.K. Jain and P.N. Rao covering IS:919 limits and fits, hole-basis vs shaft-basis, GO/NO-GO gauge tolerances &amp; Ra/Rz.",
    """
    <h2>1. Systems of Limits and Fits (IS:919 / ISO)</h2>
    <ul>
      <li><strong>Hole Basis System:</strong> Basic size = Lower limit of hole (Fundamental deviation for Hole $H = 0$). Widely preferred in engineering practice because holes are produced by fixed-size tools (drills, reamers, broaches) while shafts are easily turned to varying sizes.</li>
      <li><strong>Shaft Basis System:</strong> Basic size = Upper limit of shaft (Fundamental deviation for Shaft $h = 0$). Used when multiple fits are required on a single long transmission shaft.</li>
      <li><strong>Standard Tolerance Unit ($i$):</strong> For diameters up to 500 mm: $i = 0.45 \sqrt[3]{D} + 0.001 D$ ($\mu$m), where $D = \sqrt{D_1 D_2}$ is the geometric mean of diameter step. Standard tolerance grades: IT01, IT0, IT1 to IT16 (IT6 = $10i$; IT7 = $16i$; IT8 = $25i$; IT9 = $40i$; IT10 = $64i$, etc.).</li>
    </ul>

    <h2>2. Taylor's Principle of Limit Gauge Design</h2>
    <div class="box-upsc">
      <div class="box-upsc-title">Taylor's Golden Rule for GO and NO-GO Gauges</div>
      <ul>
        <li><strong>GO Gauge:</strong> Must check the <strong>Maximum Metal Condition (MMC)</strong> (i.e., minimum hole size or maximum shaft size) and should check as many dimensions simultaneously as possible (full form). E.g., Plug gauge full cylindrical length.</li>
        <li><strong>NO-GO Gauge:</strong> Must check the <strong>Least Metal Condition (LMC)</strong> (i.e., maximum hole size or minimum shaft size) and should check only <strong>one dimension at a time</strong> (point contact / pin contact).</li>
      </ul>
    </div>

    <h2>3. Surface Roughness Parameters</h2>
    <ul>
      <li><strong>Center Line Average ($R_a$):</strong> $R_a = \frac{1}{L} \int_0^L |y|\,dx \approx \frac{\sum |y_i|}{N}$. Measures average vertical deviations from the mean line.</li>
      <li><strong>Theoretical Peak-to-Valley Roughness ($h_{\max}$):</strong>
        <ul>
          <li>Turning with sharp single-point tool: $h_{\max} = \frac{f}{\tan C_s + \cot C_e}$.</li>
          <li>Turning with nose-radius tool ($r$): $h_{\max} \approx \frac{f^2}{8r}$ and $R_a \approx \frac{h_{\max}}{4} = \frac{f^2}{32r}$ (where $f$ is feed in mm and $r$ is nose radius in mm).</li>
        </ul>
      </li>
    </ul>
    """
))

# ----------------- Subject 11: Mechatronics & Robotics (Topics 57 to 61) -----------------
MODULES_DATA[57] = ("📘 Microprocessors & Microcontrollers — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechatronics (Topic 57)",
    "Microprocessors &amp; Microcontrollers: 8085/8086 Architecture, Registers, Bus Timing &amp; Interfacing",
    "Complete synthesis of Ramesh Gaonkar and W. Bolton covering 8085 pinouts, ALU flags, memory mapping, interrupt priorities &amp; 8255 PPI.",
    """
    <h2>1. Intel 8085 Microprocessor Architecture</h2>
    <ul>
      <li><strong>Registers:</strong> 8-bit Accumulator (A), Flag register (Sign S, Zero Z, Auxiliary Carry AC, Parity P, Carry CY), General Purpose 8-bit registers (B, C, D, E, H, L) pairing as 16-bit register pairs (BC, DE, HL for memory pointer), 16-bit Program Counter (PC), and 16-bit Stack Pointer (SP).</li>
      <li><strong>Buses:</strong> 16-bit Address bus ($A_{15}\text{--}A_0$ capable of addressing $2^{16} = 64\text{ KB}$ of memory) with multiplexed lower address/data bus ($AD_7\text{--}AD_0$ demultiplexed using the <strong>Address Latch Enable (ALE)</strong> pin via 74LS373 latch).</li>
      <li><strong>Interrupts Hierarchy:</strong>
        <div class="table-responsive">
          <table>
            <tr><th>Interrupt</th><th>Priority</th><th>Maskable?</th><th>Trigger Type</th><th>Vector Address</th></tr>
            <tr><td><strong>TRAP (RST 4.5)</strong></td><td><strong>1 (Highest)</strong></td><td>Non-Maskable (NMI)</td><td>Edge &amp; Level sensitive</td><td><code>0024H</code></td></tr>
            <tr><td><strong>RST 7.5</strong></td><td>2</td><td>Maskable</td><td>Rising Edge sensitive</td><td><code>003CH</code></td></tr>
            <tr><td><strong>RST 6.5</strong></td><td>3</td><td>Maskable</td><td>High Level sensitive</td><td><code>0034H</code></td></tr>
            <tr><td><strong>RST 5.5</strong></td><td>4</td><td>Maskable</td><td>High Level sensitive</td><td><code>002CH</code></td></tr>
            <tr><td><strong>INTR</strong></td><td>5 (Lowest)</td><td>Maskable</td><td>Level sensitive</td><td>Supplied externally by 8259</td></tr>
          </table>
        </div>
      </li>
    </ul>
    """
))

MODULES_DATA[58] = ("📘 Sensors, Transducers & Actuators — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechatronics (Topic 58)",
    "Sensors, Transducers &amp; Actuators: LVDT, Piezoelectric, Encoders, Stepper &amp; Servo Motors",
    "Complete synthesis of W. Bolton and Doebelin covering displacement, velocity, optical encoders, brushless DC &amp; stepper motor pulse rates.",
    """
    <h2>1. Displacement, Force &amp; Motion Transducers</h2>
    <ul>
      <li><strong>LVDT (Linear Variable Differential Transformer):</strong> Inductive passive displacement sensor with one primary coil excited by AC ($1\text{--}10\text{ kHz}$) and two identical secondary coils connected in <strong>series opposition</strong> ($V_{\text{out}} = V_{s1} - V_{s2}$). At the null position, $V_{\text{out}} = 0$; moving the magnetic core produces an AC output whose amplitude is linear with displacement and whose phase indicates direction. Infinite resolution, frictionless.</li>
      <li><strong>Piezoelectric Transducers:</strong> Asymmetric quartz, Rochelle salt, or PZT ceramics generate an electric charge when subjected to mechanical stress ($Q = d \cdot F$). <strong>Cannot measure static loads</strong> because charge leaks through input impedance; ideal for dynamic vibration, impact force, and acceleration.</li>
      <li><strong>Optical Encoders:</strong> <em>Incremental Encoders</em> use two offset optical tracks (A and B in quadrature at 90° phase shift) to measure speed and detect direction of rotation + Z marker pulse. <em>Absolute Encoders</em> use binary or Gray code tracks to provide unique angular position even after power loss.</li>
    </ul>

    <h2>2. Stepper Motors &amp; Servo Actuators</h2>
    <div class="box-tech">
      <div class="box-tech-title">Stepper Motor Step Angle &amp; Frequency Formulas</div>
      <p>Step angle $\beta$ in terms of stator phases $m$ and rotor teeth $N_r$ (or stator teeth $N_s$ and rotor teeth $N_r$):</p>
      <p style="text-align:center; font-weight:bold; font-size:16px;">$$\beta = \frac{360^\circ}{m \cdot N_r} = \frac{|N_s - N_r|}{N_s \cdot N_r} \times 360^\circ$$</p>
      <p>Motor speed in rpm: $N = \frac{\beta \cdot f}{360^\circ} \times 60 = \frac{\text{PPS}}{N_{\text{steps/rev}}} \times 60$, where $f$ is input pulse frequency in pulses per second (PPS).</p>
    </div>
    """
))

MODULES_DATA[59] = ("📘 Control Systems, PLC & Signal Conditioning — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechatronics (Topic 59)",
    "Control Systems, PLC Programming, Logic Gates, Operational Amplifiers &amp; Signal Conditioning",
    "Complete synthesis of W. Bolton Mechatronics and Katsuhiko Ogata covering PID controllers, ladder logic &amp; op-amp circuits.",
    """
    <h2>1. PID Controllers &amp; Tuning</h2>
    <ul>
      <li><strong>Proportional (P) Controller:</strong> $u(t) = K_p e(t)$. Reduces rise time; increases system gain; but <strong>cannot eliminate steady-state error (offset)</strong>!</li>
      <li><strong>Integral (I) Controller:</strong> $u(t) = K_i \int e(t)\,dt$. Increases system type number; <strong>completely eliminates steady-state error</strong>; however, degrades stability and increases overshoot/settling time.</li>
      <li><strong>Derivative (D) Controller:</strong> $u(t) = K_d \frac{de(t)}{dt}$. Anticipatory control; adds damping; reduces peak overshoot and improves transient stability; highly sensitive to high-frequency noise.</li>
    </ul>

    <h2>2. Programmable Logic Controllers (PLC) &amp; Ladder Logic</h2>
    <p>PLCs operate in a cyclic 3-step scan: <strong>1. Read Inputs &rarr; 2. Execute Ladder Logic Program &rarr; 3. Update Outputs</strong>.</p>
    <div class="table-responsive">
      <table>
        <tr><th>Ladder Logic Element</th><th>Symbol</th><th>Description</th></tr>
        <tr><td><strong>Normally Open Contact (NO)</strong></td><td><code>--[ ]--</code></td><td>Examines if an input is ON (logic 1); closes when bit is set.</td></tr>
        <tr><td><strong>Normally Closed Contact (NC)</strong></td><td><code>--[/]--</code></td><td>Examines if an input is OFF (logic 0); opens when bit is set.</td></tr>
        <tr><td><strong>Output Coil</strong></td><td><code>--( )--</code></td><td>Sets output energized when ladder rung has true logic continuity.</td></tr>
      </table>
    </div>
    """
))

MODULES_DATA[60] = ("📘 Robotics Anatomy & DH Transformations — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechatronics (Topic 60)",
    "Robotics: Anatomy, Coordinate Configurations, Work Envelopes &amp; Denavit-Hartenberg (D-H) Parameters",
    "Complete synthesis of John J. Craig and Saeed Niku covering robot topologies, degrees of freedom &amp; 4 D-H parameters.",
    """
    <h2>1. Robot Anatomy &amp; Coordinate Configurations</h2>
    <div class="table-responsive">
      <table>
        <tr><th>Configuration</th><th>Joint Sequence</th><th>Work Envelope Geometry</th><th>Industrial Applications</th></tr>
        <tr><td><strong>Cartesian / Gantry</strong></td><td>PPP (3 Prismatic)</td><td>Rectangular box / Cuboid</td><td>Large-span material transfer, overhead palletizing, 3D printing, pick-and-place.</td></tr>
        <tr><td><strong>Cylindrical</strong></td><td>RPP (1 Revolute, 2 Prismatic)</td><td>Cylindrical volume</td><td>Loading/unloading machine tools, assembly around a central pillar.</td></tr>
        <tr><td><strong>Spherical / Polar</strong></td><td>RRP (2 Revolute, 1 Prismatic)</td><td>Part of a sphere</td><td>Die casting, furnace charging, injection molding extraction.</td></tr>
        <tr><td><strong>SCARA</strong></td><td>RRP (Horizontal revolute joints)</td><td>Cylindrical slice (Selective compliance)</td><td>High-speed vertical electronic PCB component insertion; stiff vertically, compliant horizontally.</td></tr>
        <tr><td><strong>Articulated / Revolute</strong></td><td>RRR (3 Revolute, like human arm)</td><td>Complex swept sphere</td><td>Automotive spot welding, spray painting, seam welding, robotic surgery.</td></tr>
      </table>
    </div>

    <h2>2. Denavit-Hartenberg (D-H) 4-Parameter Convention</h2>
    <p>Any spatial transformation between joint link $i-1$ and link $i$ is completely defined by <strong>4 kinematic parameters</strong>:</p>
    <div class="box-tech">
      <div class="box-tech-title">The 4 D-H Parameters (Tested in ESE 2024 &amp; 2026!)</div>
      <ol>
        <li><strong>Link Length ($a_i$):</strong> Distance along axis $X_i$ from $Z_{i-1}$ to $Z_i$ (length of common normal).</li>
        <li><strong>Link Twist ($\alpha_i$):</strong> Angle from $Z_{i-1}$ to $Z_i$ measured about the $X_i$ axis.</li>
        <li><strong>Link Offset ($d_i$):</strong> Distance along axis $Z_{i-1}$ from $X_{i-1}$ to $X_i$ (variable in prismatic joints).</li>
        <li><strong>Joint Angle ($\theta_i$):</strong> Angle from $X_{i-1}$ to $X_i$ measured about the $Z_{i-1}$ axis (variable in revolute joints).</li>
      </ol>
    </div>
    """
))

MODULES_DATA[61] = ("📘 Robot Kinematics, Dynamics & Trajectory — Complete Study Module", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechatronics (Topic 61)",
    "Forward &amp; Inverse Kinematics, Jacobian, Singularities &amp; Industrial Applications",
    "Complete synthesis of John J. Craig and M.P. Groover covering manipulator kinematics, Jacobian matrix &amp; velocity mapping.",
    """
    <h2>1. Forward vs. Inverse Kinematics</h2>
    <ul>
      <li><strong>Forward Kinematics:</strong> Given the joint angles/displacements $\mathbf{q} = [\theta_1, \theta_2, \dots, \theta_n]^T$, compute the end-effector position and orientation $[x, y, z, \text{roll}, \text{pitch}, \text{yaw}]^T$ in the base frame. (Always yields a unique, straightforward closed-form solution via chained homogeneous matrices: $T_0^n = A_1 A_2 \dots A_n$).</li>
      <li><strong>Inverse Kinematics:</strong> Given the desired end-effector cartesian pose, calculate the required joint variables $\mathbf{q}$. Non-linear, complex, may have multiple solutions or no solution (if pose lies outside the work envelope). Pieper's criterion guarantees closed-form inverse kinematics if three consecutive revolute joint axes intersect at a common point (spherical wrist).</li>
    </ul>

    <h2>2. Manipulator Jacobian &amp; Singularities</h2>
    <p>The Jacobian matrix $\mathbf{J}(\mathbf{q})$ maps joint velocities to cartesian end-effector linear and angular velocities: $\dot{\mathbf{x}} = \mathbf{J}(\mathbf{q}) \dot{\mathbf{q}}$.</p>
    <div class="box-upsc">
      <div class="box-upsc-title">Kinematic Singularities</div>
      <p>Configurations where $\det(\mathbf{J}(\mathbf{q})) = 0$ are <strong>Kinematic Singularities</strong>:</p>
      <ul>
        <li>The manipulator loses one or more degrees of freedom (cannot move in certain cartesian directions).</li>
        <li>Inverse kinematics requires infinite joint velocities ($\dot{\mathbf{q}} = \mathbf{J}^{-1} \dot{\mathbf{x}}$).</li>
        <li>Small cartesian forces can produce infinite joint torques (mechanical lock).</li>
      </ul>
    </div>
    """
))

# ----------------- Topic 64: Maths Modules 5 & 6 -----------------
MODULES_DATA[6405] = ("📘 Module 5: Probability, Statistics & Distributions", wrap_art(
    "UPSC ESE Prelims &bull; Paper-I Engineering Mathematics (Topic 64)",
    "Probability Distributions (Binomial, Poisson, Normal, Exponential) &amp; Bayes' Theorem",
    "Complete synthesis of B.S. Grewal and S.C. Gupta covering conditional probability, expectation, variance &amp; regression.",
    """
    <h2>1. Probability Distributions Summary Table</h2>
    <div class="table-responsive">
      <table>
        <tr><th>Distribution</th><th>Probability Mass / Density Function</th><th>Mean ($\mu$)</th><th>Variance ($\sigma^2$) &amp; Key Properties</th></tr>
        <tr><td><strong>Binomial ($n, p$)</strong></td><td>$P(X = k) = \binom{n}{k} p^k (1 - p)^{n-k}$</td><td>$n p$</td><td>$n p (1 - p)$ (Always Mean &gt; Variance). Used for $n$ independent Bernoulli trials.</td></tr>
        <tr><td><strong>Poisson ($\lambda$)</strong></td><td>$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$</td><td>$\lambda$</td><td>$\lambda$ (<strong>Mean = Variance = $\lambda$</strong>). Limiting form of Binomial when $n \to \infty, p \to 0$ with $n p = \lambda$.</td></tr>
        <tr><td><strong>Exponential ($\lambda$)</strong></td><td>$f(x) = \lambda e^{-\lambda x} \quad (x \ge 0)$</td><td>$1 / \lambda$</td><td>$1 / \lambda^2$. Memoryless continuous distribution ($P(X &gt; s + t \mid X &gt; s) = P(X &gt; t)$).</td></tr>
        <tr><td><strong>Normal ($\mu, \sigma^2$)</strong></td><td>$f(x) = \frac{1}{\sigma \sqrt{2\pi}} e^{-(x - \mu)^2 / (2\sigma^2)}$</td><td>$\mu$</td><td>$\sigma^2$. Symmetrical bell curve; inflection points at $x = \mu \pm \sigma$. Area within $\pm 1\sigma = 68.27\%$, $\pm 2\sigma = 95.45\%$, $\pm 3\sigma = 99.73\%$.</td></tr>
      </table>
    </div>
    """
))

MODULES_DATA[6406] = ("📘 Module 6: Numerical Methods & Analysis", wrap_art(
    "UPSC ESE Prelims &bull; Paper-I Engineering Mathematics (Topic 64)",
    "Numerical Analysis: Root Finding, Linear Solvers, Numerical Integration &amp; ODEs",
    "Complete synthesis of M.K. Jain, S.R.K. Iyengar and R.K. Jain covering Bisection, Secant, Newton-Raphson, Simpson's Rules &amp; RK4.",
    """
    <h2>1. Convergence &amp; Order of Root-Finding Algorithms</h2>
    <div class="table-responsive">
      <table>
        <tr><th>Method</th><th>Iteration Formula</th><th>Order of Convergence</th><th>Key Exam Features</th></tr>
        <tr><td><strong>Bisection</strong></td><td>$x_{n+1} = (a + b) / 2$</td><td>$p = 1$ (Linear)</td><td>Guaranteed convergence if $f(a)f(b) &lt; 0$. Error halves each step.</td></tr>
        <tr><td><strong>Regula Falsi</strong></td><td>$x_{n+1} = \frac{a f(b) - b f(a)}{f(b) - f(a)}$</td><td>$p = 1$</td><td>Always retains bracketing of root; slower than Secant.</td></tr>
        <tr><td><strong>Secant Method</strong></td><td>$x_{n+1} = x_n - f(x_n) \frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$</td><td>$p = \frac{1 + \sqrt{5}}{2} \approx 1.618$ (Superlinear)</td><td>Does not require computing derivatives; does not guarantee bracketing.</td></tr>
        <tr><td><strong>Newton-Raphson</strong></td><td>$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$</td><td><strong>$p = 2$ (Quadratic)</strong></td><td>Fastest convergence for simple roots; fails if $f'(x_n) \approx 0$; reduces to $p = 1$ for multiple roots!</td></tr>
      </table>
    </div>

    <h2>2. Numerical Integration &amp; Error Terms</h2>
    <ul>
      <li><strong>Trapezoidal Rule:</strong> Exact for linear polynomials ($n = 1$). Global error $= -\\frac{b - a}{12} h^2 f''(\\xi) \\propto O(h^2)$. Valid for any number of subintervals.</li>
      <li><strong>Simpson's 1/3 Rule:</strong> Approximates curve by quadratic parabolas ($n = 2$). Exact for polynomials up to <strong>degree 3 (cubics!)</strong>. Global error $= -\\frac{b - a}{180} h^4 f^{(iv)}(\\xi) \\propto O(h^4)$. Requires <strong>EVEN number of subintervals</strong>.</li>
      <li><strong>Simpson's 3/8 Rule:</strong> Approximates curve by cubics ($n = 3$). Global error $= -\\frac{b - a}{80} h^4 f^{(iv)}(\\xi) \\propto O(h^4)$. Requires subintervals to be a <strong>MULTIPLE OF 3</strong>.</li>
    </ul>
    """
))

def main():
    app = create_app()
    with app.app_context():
        def put_tc(tid, title, val, order=1):
            ex = TopicContent.query.filter_by(topic_id=tid, title=title).first()
            if ex:
                ex.content_value = val
                ex.content_type = 'text'
                ex.item_order = order
                ex.deleted_at = None
            else:
                db.session.add(TopicContent(topic_id=tid, title=title, content_type='text', content_value=val, item_order=order))

        for tid in [46, 47, 48, 49, 50, 51, 57, 58, 59, 60, 61]:
            if tid in MODULES_DATA:
                title, html = MODULES_DATA[tid]
                put_tc(tid, title, html, 1)

        if 6405 in MODULES_DATA:
            t, h = MODULES_DATA[6405]
            put_tc(64, t, h, 5)
        if 6406 in MODULES_DATA:
            t, h = MODULES_DATA[6406]
            put_tc(64, t, h, 6)

        db.session.commit()
        print("Successfully loaded Subject 9, Subject 11, and Maths advanced modules into app.db!")

if __name__ == '__main__':
    main()
