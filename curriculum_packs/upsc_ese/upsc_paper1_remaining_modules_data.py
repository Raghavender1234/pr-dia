# -*- coding: utf-8 -*-
"""
Rich HTML Study Compendiums & Structured MCQ Bank for UPSC ESE 2027 LMS
Covers all Paper-I topics & Mechanical Engineering integration.
"""

COMMON_LMS_STYLE = """
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
    padding: 24px 24px;
    border-radius: 12px;
    margin-bottom: 22px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.15);
  }
  .upsc-ese-article .cover-header h1 {
    margin: 0 0 8px 0 !important;
    font-size: 24px !important;
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
    font-size: 20px !important;
    font-weight: 700 !important;
    margin-top: 28px !important;
    margin-bottom: 12px !important;
  }
  .upsc-ese-article h3 {
    color: #0f4c81 !important;
    -webkit-text-fill-color: #0f4c81 !important;
    background: none !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    margin-top: 20px !important;
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
  .upsc-ese-article .box-update {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 5px solid #16a34a;
    padding: 14px 16px;
    margin: 16px 0;
    border-radius: 0 8px 8px 0;
  }
  .upsc-ese-article .box-update-title {
    font-weight: 700;
    color: #15803d;
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
  .upsc-ese-article .layer-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #1e3a8a;
    padding: 10px 14px;
    margin-bottom: 10px;
    border-radius: 0 6px 6px 0;
  }
</style>
"""


PROJECT_MANAGEMENT_HTML = COMMON_LMS_STYLE + """
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">UPSC ESE 2027 Paper-I &bull; Basics of Project Management</span>
    <h1>Master Compendium: Basics of Project Management (Prasanna Chandra + Gray &amp; Larson Synthesis)</h1>
    <p>Complete 2017&ndash;2026 Verbatim Textbook Synthesis: Project Life Cycle, Feasibilities, Capital Budgeting (NPV, IRR, BC Ratio), WBS, PERT/CPM, Crashing, Earned Value Management (EVM) &amp; Tendering/Contracts.</p>
  </div>

  <h2>1. Project Definition, Characteristics &amp; Project Life Cycle (PLC)</h2>
  <p>According to <strong>Clifford F. Gray &amp; Erik W. Larson</strong> (<em>Project Management: The Managerial Process</em>) and <strong>Prasanna Chandra</strong> (<em>Projects: Planning, Analysis, Selection, Financing, Implementation, and Review</em>), a project is a <strong>temporary, non-routine, complex, one-time effort</strong> limited by time, budget, resources, and performance specifications designed to meet customer needs.</p>

  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Phase of Project Life Cycle</th>
          <th>Resource / Effort Intensity</th>
          <th>Key Activities &amp; Deliverables (Asked in ESE 2017&ndash;2026)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Defining / Conception Stage</strong></td>
          <td>Low (Starts near zero, rises slowly)</td>
          <td>Project Charter, Idea Generation, SWOT Analysis, Preliminary Screening, Stakeholder Identification, Establishing Objectives &amp; Scope.</td>
        </tr>
        <tr>
          <td><strong>2. Planning / Formulation Stage</strong></td>
          <td>Moderate &amp; Rising</td>
          <td>Detailed Feasibility Studies (Market, Technical, Financial, Economic, Ecological), <strong>Work Breakdown Structure (WBS)</strong>, Responsibility Matrix, Network Scheduling (PERT/CPM), Cost &amp; Resource Baseline.</td>
        </tr>
        <tr>
          <td><strong>3. Executing / Implementation Stage</strong></td>
          <td><strong>Peak Resource &amp; Cost Intensity (75&ndash;85% of total budget)</strong></td>
          <td>Physical construction/coding/manufacturing, Procurement, Tendering &amp; Contracting, Quality Assurance, Team Management, Earned Value Monitoring (EVM) &amp; Crashing.</td>
        </tr>
        <tr>
          <td><strong>4. Closing / Termination / Clean-up Stage</strong></td>
          <td>Rapid Decline to Zero</td>
          <td>Final Acceptance Testing, Handover/Commissioning to customer, Release of resources, Post-Completion Audit (Lessons Learned), Archiving project records.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="box-upsc">
    <div class="box-upsc-title">⚡ UPSC Setter's Golden Curve Rule (ESE 2019, 2022, 2025, 2026)</div>
    <ul>
      <li><strong>Ability to Influence Final Project Cost &amp; Characteristics:</strong> Highest at the <strong>very beginning (Conception/Defining phase)</strong> and decreases continuously as the project progresses.</li>
      <li><strong>Cost of Making Changes / Correcting Errors:</strong> Lowest in the Conception phase and <strong>increases exponentially</strong> toward the Execution and Closing phases.</li>
    </ul>
  </div>

  <h2>2. Project Classification &amp; Feasibility Dimensions (Prasanna Chandra Ch. 1&ndash;5)</h2>
  <div class="grid-2">
    <div class="box-tech">
      <div class="box-tech-title">5 Core Feasibility Studies</div>
      <ul>
        <li><strong>Market &amp; Demand Analysis:</strong> Aggregate demand, market share, Delphi method, trend projection, end-use method (Consumption coefficient).</li>
        <li><strong>Technical Feasibility:</strong> Plant location, plant capacity, material inputs, choice of technology, civil works, product mix.</li>
        <li><strong>Financial Feasibility:</strong> Cost of project, means of finance, Debt-Equity ratio, WACC, Cash flows, NPV, IRR, Payback, Break-even.</li>
        <li><strong>Economic / Social Cost-Benefit Analysis (SCBA):</strong> Shadow prices (UNIDO &amp; Little-Mirrlees approaches), social rate of discount, externalities, employment impact.</li>
        <li><strong>Ecological / Environmental Feasibility:</strong> EIA, effluent treatment, environmental damage &amp; restoration costs.</li>
      </ul>
    </div>
    <div class="box-upsc">
      <div class="box-upsc-title">Capital Budgeting &amp; Investment Appraisal Formulas</div>
      <ul>
        <li><strong>Net Present Value (NPV):</strong> <code>NPV = &Sigma; [CF<sub>t</sub> / (1 + r)<sup>t</sup>] &minus; I<sub>0</sub></code>. Accept if <code>NPV &gt; 0</code>. (Assumes reinvestment at discount rate <em>r</em> = WACC).</li>
        <li><strong>Internal Rate of Return (IRR):</strong> Discount rate <em>r</em> at which <code>NPV = 0</code>. (Assumes reinvestment at <em>IRR</em> itself; can give multiple IRRs for non-conventional cash flows).</li>
        <li><strong>Benefit-Cost Ratio (BCR / Profitability Index PI):</strong> <code>PI = PV of Cash Inflows / Initial Outlay I<sub>0</sub> = 1 + (NPV / I<sub>0</sub>)</code>. Accept if <code>PI &gt; 1</code>.</li>
        <li><strong>Debt Service Coverage Ratio (DSCR):</strong> <code>DSCR = (PAT + Depreciation + Interest on Long-Term Debt) / (Interest on Long-Term Debt + Principal Repayment)</code>. Ideal benchmark: <strong>1.5 to 2.0</strong>.</li>
      </ul>
    </div>
  </div>

  <h2>3. Work Breakdown Structure (WBS), OBS &amp; Project Organization</h2>
  <ul>
    <li><strong>Work Breakdown Structure (WBS):</strong> A hierarchical, deliverable-oriented decomposition of the total scope of work to be carried out by the project team.
      <ul>
        <li><strong>Work Package:</strong> The lowest level of the WBS. It defines a short-duration task (typically 8 to 80 hours rule) with a single accountable owner, definite start/end events, and measurable budget.</li>
        <li><strong>Cost Account (Control Account):</strong> The intersection point of the <strong>WBS (Work Breakdown Structure)</strong> and the <strong>OBS (Organization Breakdown Structure)</strong> where cost and schedule performance are measured.</li>
        <li><strong>Responsibility Matrix (RACI Chart):</strong> Maps WBS tasks against project team members: <strong>R</strong>esponsible, <strong>A</strong>ccountable, <strong>C</strong>onsulted, <strong>I</strong>nformed (used for small projects or sub-modules).</li>
      </ul>
    </li>
    <li><strong>Project Organization Structures (Gray &amp; Larson Ch. 3):</strong>
      <ul>
        <li><strong>Functional Organization:</strong> Low project manager authority; high technical depth; slow cross-functional coordination.</li>
        <li><strong>Dedicated Project Team (Projectized):</strong> Project Manager has maximum (almost total) authority; fast execution; high duplication of resources; "Projectitis" (we-they divide &amp; post-project anxiety).</li>
        <li><strong>Matrix Organization (Weak, Balanced, Strong):</strong> Dual reporting (violates Fayol's Unity of Command); shares functional specialists across multiple projects.</li>
      </ul>
    </li>
  </ul>

  <h2>4. Network Scheduling: PERT vs. CPM, Floats &amp; Crashing</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Feature / Formula</th>
          <th>PERT (Program Evaluation &amp; Review Technique)</th>
          <th>CPM (Critical Path Method)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Nature of Model</strong></td>
          <td><strong>Probabilistic (Stochastic)</strong> &mdash; 3 time estimates (<em>t<sub>o</sub>, t<sub>m</sub>, t<sub>p</sub></em>) following a <strong>Beta Distribution</strong>.</td>
          <td><strong>Deterministic</strong> &mdash; Single time estimate; focuses on <strong>Time-Cost Trade-off (Crashing)</strong>.</td>
        </tr>
        <tr>
          <td><strong>Orientation</strong></td>
          <td><strong>Event-oriented</strong> (milestones). Suitable for R&amp;D and first-time projects.</td>
          <td><strong>Activity-oriented</strong>. Suitable for construction, maintenance, and repetitive industrial projects.</td>
        </tr>
        <tr>
          <td><strong>Expected Time &amp; Variance</strong></td>
          <td><code>t<sub>e</sub> = (t<sub>o</sub> + 4t<sub>m</sub> + t<sub>p</sub>) / 6</code><br><code>&sigma;<sup>2</sup> = [(t<sub>p</sub> &minus; t<sub>o</sub>) / 6]<sup>2</sup></code></td>
          <td>Path Standard Deviation: <code>&sigma;<sub>cp</sub> = &radic;(&Sigma; &sigma;<sub>i</sub><sup>2</sup>)</code> (Follows Central Limit Theorem &rarr; Normal Distribution).</td>
        </tr>
        <tr>
          <td><strong>Activity Floats (CPM)</strong></td>
          <td colspan="2">
            &bull; <strong>Total Float (TF):</strong> <code>TF = LFT &minus; EFT = LST &minus; EST = (LFT &minus; EST) &minus; t<sub>ij</sub></code> (Max delay without delaying project completion).<br>
            &bull; <strong>Free Float (FF):</strong> <code>FF = (EST of successor &minus; EFT of activity) = TF &minus; Head Event Slack (S<sub>j</sub>)</code> (Max delay without delaying any successor's EST).<br>
            &bull; <strong>Independent Float (IF):</strong> <code>IF = max(0, EST of successor &minus; LFT of predecessor &minus; t<sub>ij</sub>) = FF &minus; Tail Event Slack (S<sub>i</sub>)</code>.<br>
            &bull; <strong>Inequality Always Holds:</strong> <code>Total Float (TF) &ge; Free Float (FF) &ge; Independent Float (IF)</code>. On the <strong>Critical Path</strong>, <code>TF = FF = IF = 0</code>.
          </td>
        </tr>
        <tr>
          <td><strong>Project Crashing &amp; Cost Slope</strong></td>
          <td colspan="2">
            &bull; <strong>Cost Slope:</strong> <code>(&Delta;C / &Delta;T) = (Crash Cost &minus; Normal Cost) / (Normal Time &minus; Crash Time)</code>.<br>
            &bull; <strong>Crashing Rule:</strong> Always crash the activity on the <strong>Critical Path</strong> that has the <strong>MINIMUM Cost Slope</strong>. As you crash, Direct Cost increases linearly while Indirect (Overhead) Cost decreases; the <strong>Optimum Project Duration</strong> minimizes Total Project Cost.
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>5. Earned Value Management (EVM) &mdash; Complete Formula Matrix (Asked in 2018, 2020, 2023, 2025, 2026)</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>EVM Metric</th>
          <th>Exact Formula</th>
          <th>Interpretation for Exam Numericals</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Planned Value (PV / BCWS)</strong></td>
          <td><code>Scheduled % Complete &times; BAC</code></td>
          <td>Budgeted Cost of Work Scheduled up to status date.</td>
        </tr>
        <tr>
          <td><strong>Earned Value (EV / BCWP)</strong></td>
          <td><code>Actual % Work Completed &times; BAC</code></td>
          <td>Budgeted Cost of Work Actually Performed.</td>
        </tr>
        <tr>
          <td><strong>Actual Cost (AC / ACWP)</strong></td>
          <td>Actual money spent to date</td>
          <td>Actual Cost of Work Performed.</td>
        </tr>
        <tr>
          <td><strong>Cost Variance (CV)</strong></td>
          <td><code>CV = EV &minus; AC</code></td>
          <td><strong>CV &gt; 0: Under Budget (Favorable)</strong>; CV &lt; 0: Cost Overrun.</td>
        </tr>
        <tr>
          <td><strong>Schedule Variance (SV)</strong></td>
          <td><code>SV = EV &minus; PV</code></td>
          <td><strong>SV &gt; 0: Ahead of Schedule</strong>; SV &lt; 0: Behind Schedule.</td>
        </tr>
        <tr>
          <td><strong>Cost Performance Index (CPI)</strong></td>
          <td><code>CPI = EV / AC</code></td>
          <td><strong>CPI &gt; 1.0: Under Budget</strong> (Getting more than ₹1 value per ₹1 spent).</td>
        </tr>
        <tr>
          <td><strong>Schedule Performance Index (SPI)</strong></td>
          <td><code>SPI = EV / PV</code></td>
          <td><strong>SPI &gt; 1.0: Ahead of Schedule</strong>.</td>
        </tr>
        <tr>
          <td><strong>Estimate at Completion (EAC)</strong></td>
          <td><code>EAC = BAC / CPI</code> (if current variance continues)<br><code>EAC = AC + (BAC &minus; EV)</code> (if future work at planned rate)</td>
          <td>Projected total cost at completion. Variance at Completion <code>VAC = BAC &minus; EAC</code>.</td>
        </tr>
        <tr>
          <td><strong>To-Complete Performance Index (TCPI)</strong></td>
          <td><code>TCPI = (BAC &minus; EV) / (BAC &minus; AC)</code></td>
          <td>Required cost efficiency on remaining work to finish within original budget BAC.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>6. Tendering, Bidding &amp; Engineering Contracts</h2>
  <ul>
    <li><strong>Earnest Money Deposit (EMD / Bid Security):</strong> Deposited by all bidders along with the tender (typically <strong>1% to 2%</strong> of estimated contract value) to ensure a bidder does not withdraw their bid after opening or refuse to sign the contract. Refunded to unsuccessful bidders.</li>
    <li><strong>Security Deposit (Performance Security):</strong> Collected from the winning contractor (typically <strong>5% to 10%</strong> of contract value, inclusive of EMD) to guarantee faithful performance and quality during execution and the Defect Liability Period.</li>
    <li><strong>Types of Contracts:</strong>
      <ul>
        <li><strong>Lump-Sum Fixed Price Contract:</strong> Maximum risk on Contractor; used when scope and drawings are 100% frozen before bidding.</li>
        <li><strong>Item-Rate (Unit-Price / Schedule of Rates) Contract:</strong> Contractor quotes rates per unit item; paid based on actual measured quantities in Measurement Book (MB). Most widely used in CPWD/PWD civil works.</li>
        <li><strong>Cost-Plus Percentage Fee Contract:</strong> Maximum risk on Owner; contractor has perverse incentive to inflate project costs.</li>
        <li><strong>Turnkey / EPC (Engineering, Procurement, Construction):</strong> Single-point responsibility for design, procurement, construction, and commissioning.</li>
        <li><strong>BOT (Build-Operate-Transfer) &amp; BOOT (Build-Own-Operate-Transfer):</strong> Public-Private Partnership (PPP) models for highways, airports, and power plants.</li>
      </ul>
    </li>
  </ul>
</div>
"""


QUALITY_AND_MAINTENANCE_HTML = COMMON_LMS_STYLE + """
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">UPSC ESE 2027 Paper-I &bull; Standards &amp; Quality Practices</span>
    <h1>Master Compendium: Standards, Quality Practices, Reliability &amp; Maintenance Engineering</h1>
    <p>Complete Synthesis of Amitava Mitra, Dale H. Besterfield, M. Jeya Chandra &amp; BS EN 13306 Maintenance Terminology (2017&ndash;2026).</p>
  </div>

  <h2>1. Dimensions of Quality &amp; Quality Philosophy Gurus</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Quality Guru / Framework</th>
          <th>Core Contributions &amp; Verbatim UPSC Exam Keywords</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>David A. Garvin's 8 Dimensions of Quality</strong></td>
          <td><strong>1. Performance</strong> (primary operating traits), <strong>2. Features</strong> ("bells &amp; whistles"), <strong>3. Reliability</strong> (probability of surviving time <em>t</em>), <strong>4. Conformance</strong> (meeting specifications), <strong>5. Durability</strong> (economic/physical service life), <strong>6. Serviceability</strong> (speed/ease of repair), <strong>7. Aesthetics</strong> (sensory appeal), <strong>8. Perceived Quality</strong> (reputation/brand).</td>
        </tr>
        <tr>
          <td><strong>W. Edwards Deming</strong></td>
          <td><strong>PDCA / PDSA Cycle</strong> (Plan-Do-Check/Study-Act), <strong>Deming's 14 Points</strong> for Management, System of Profound Knowledge, Seven Deadly Diseases of Management.</td>
        </tr>
        <tr>
          <td><strong>Joseph M. Juran</strong></td>
          <td>Defined quality as <strong>"Fitness for Use"</strong>. Formulated the <strong>Juran Quality Trilogy</strong>: (1) Quality Planning, (2) Quality Control, and (3) Quality Improvement. Applied Pareto Principle (80/20 rule) to quality.</td>
        </tr>
        <tr>
          <td><strong>Philip B. Crosby</strong></td>
          <td>Defined quality as <strong>"Conformance to Requirements"</strong>. Coined <strong>"Zero Defects"</strong>, <strong>"Quality is Free"</strong>, and the vaccine of Prevention (Do It Right the First Time &mdash; DIRFT).</td>
        </tr>
        <tr>
          <td><strong>Kaoru Ishikawa</strong></td>
          <td>Father of <strong>Quality Circles</strong> and creator of the <strong>Cause-and-Effect (Fishbone / Ishikawa) Diagram</strong>; popularized the <strong>7 Basic QC Tools</strong> (Flowchart, Check Sheet, Histogram, Pareto Chart, Cause-and-Effect Diagram, Scatter Diagram, Control Chart).</td>
        </tr>
        <tr>
          <td><strong>Genichi Taguchi</strong></td>
          <td><strong>Taguchi Quadratic Quality Loss Function:</strong> <code>L(x) = k (x &minus; m)<sup>2</sup></code> (Societal loss increases quadratically as soon as a product deviates from the target nominal value <em>m</em>, even inside specification limits!). Pioneered Robust Design &amp; Orthogonal Arrays (Signal-to-Noise S/N Ratio).</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>2. Costs of Quality (PAF Model)</h2>
  <ul>
    <li><strong>1. Prevention Costs (Cost of Good Quality):</strong> Quality planning, supplier capability surveys, design reviews, employee training, preventive maintenance.</li>
    <li><strong>2. Appraisal Costs (Cost of Good Quality):</strong> Incoming material inspection, in-process testing, gauge calibration, destructive testing, lab audits.</li>
    <li><strong>3. Internal Failure Costs (Cost of Poor Quality &mdash; detected BEFORE shipment):</strong> Scrap, rework, re-inspection, machine downtime due to defects, downgrading.</li>
    <li><strong>4. External Failure Costs (Cost of Poor Quality &mdash; detected AFTER delivery to customer):</strong> Warranty claims, product recalls, field servicing, liability lawsuits, loss of customer goodwill.</li>
  </ul>

  <h2>3. Statistical Quality Control (SQC): Control Charts &amp; Process Capability</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Control Chart Type</th>
          <th>Data Type &amp; Distribution</th>
          <th>Application &amp; Control Limits</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>X&#772; and R Chart (or X&#772; and s Chart)</strong></td>
          <td><strong>Variables (Continuous Measurement)</strong> &mdash; Normal Distribution</td>
          <td>Monitors process mean (centering) via <code>X&#772;</code> chart and process dispersion (spread) via <code>R</code> chart: <code>UCL = X&#772;&#772; + A<sub>2</sub>R&#772;</code>, <code>LCL = X&#772;&#772; &minus; A<sub>2</sub>R&#772;</code>.</td>
        </tr>
        <tr>
          <td><strong>p-Chart &amp; np-Chart</strong></td>
          <td><strong>Attributes (Defective / Non-conforming Units)</strong> &mdash; <strong>Binomial Distribution</strong></td>
          <td><code>p-Chart</code> plots fraction defective (sample size can vary): <code>&sigma;<sub>p</sub> = &radic;[p&#772;(1 &minus; p&#772;) / n]</code>.<br><code>np-Chart</code> plots number of defectives (requires constant sample size <em>n</em>).</td>
        </tr>
        <tr>
          <td><strong>c-Chart &amp; u-Chart</strong></td>
          <td><strong>Attributes (Number of Defects / Non-conformities per unit)</strong> &mdash; <strong>Poisson Distribution</strong></td>
          <td><code>c-Chart</code> plots count of defects per inspection unit of constant size: <code>UCL = c&#772; + 3&radic;c&#772;</code>.<br><code>u-Chart</code> plots defects per unit when sample area/size varies: <code>UCL = u&#772; + 3&radic;(u&#772;/n)</code>.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="box-upsc">
    <div class="box-upsc-title">⚡ Process Capability Indices (C<sub>p</sub> vs. C<sub>pk</sub>) &amp; Six Sigma</div>
    <ul>
      <li><strong>Potential Process Capability (C<sub>p</sub>):</strong> <code>C<sub>p</sub> = (USL &minus; LSL) / (6&sigma;)</code>. Measures spread relative to tolerance width, assuming the process is centered.</li>
      <li><strong>Actual Process Capability (C<sub>pk</sub>):</strong> <code>C<sub>pk</sub> = min[ (USL &minus; &mu;) / (3&sigma;), (&mu; &minus; LSL) / (3&sigma;) ]</code>. Accounts for off-centering! Always <code>C<sub>pk</sub> &le; C<sub>p</sub></code> (Equal only when process mean <code>&mu; = (USL + LSL)/2</code>).</li>
      <li><strong>Six Sigma (6&sigma;) Quality:</strong> Corresponds to <code>C<sub>p</sub> = 2.0</code> and (with Motorola's 1.5&sigma; mean shift) <code>C<sub>pk</sub> = 1.5</code>, yielding <strong>3.4 Defects Per Million Opportunities (DPMO)</strong> (99.99966% defect-free).</li>
      <li><strong>DMAIC vs. DMADV:</strong> <strong>DMAIC</strong> (Define-Measure-Analyze-Improve-Control) improves <em>existing</em> processes; <strong>DMADV / DFSS</strong> (Define-Measure-Analyze-Design-Verify) designs <em>new</em> products/processes.</li>
    </ul>
  </div>

  <h2>4. Reliability Engineering, Bath-Tub Curve &amp; System Reliability Numericals</h2>
  <ul>
    <li><strong>Bath-Tub Hazard Rate Curve &lambda;(t):</strong>
      <ol>
        <li><strong>Infant Mortality (Burn-in / Debugging Phase):</strong> Decreasing failure rate (&lambda; decreases with time; Weibull shape parameter <code>&beta; &lt; 1</code>). Caused by manufacturing defects; eliminated by burn-in testing.</li>
        <li><strong>Useful Life (Normal Operating Phase):</strong> Constant random failure rate (&lambda; = constant; <code>&beta; = 1</code>, Exponential distribution). Reliability is <code>R(t) = e<sup>&minus;&lambda;t</sup></code> and <code>MTBF = 1 / &lambda;</code>.</li>
        <li><strong>Wear-out Phase:</strong> Rapidly increasing failure rate (&lambda; increases; <code>&beta; &gt; 1</code>) due to fatigue, corrosion, creep, and insulation breakdown. Mitigated by Preventive Replacement.</li>
      </ol>
    </li>
    <li><strong>Series vs. Parallel Reliability:</strong>
      <ul>
        <li><strong>Series System:</strong> <code>R<sub>s</sub> = R<sub>1</sub> &times; R<sub>2</sub> &times; &hellip; &times; R<sub>n</sub></code>; failure rates add up: <code>&lambda;<sub>s</sub> = &Sigma;&lambda;<sub>i</sub></code>. (System reliability is strictly less than the weakest component!).</li>
        <li><strong>Parallel (Redundant) System:</strong> <code>R<sub>p</sub> = 1 &minus; [(1 &minus; R<sub>1</sub>)(1 &minus; R<sub>2</sub>)&hellip;(1 &minus; R<sub>n</sub>)]</code>.</li>
      </ul>
    </li>
    <li><strong>Inherent Availability:</strong> <code>A = MTBF / (MTBF + MTTR) = &mu; / (&lambda; + &mu;)</code>, where <code>&mu; = 1 / MTTR</code> is the repair rate.</li>
  </ul>

  <h2>5. Maintenance Strategies, BS EN 13306 (ESE 2026 Verbatim!) &amp; ISO Standards</h2>
  <div class="grid-2">
    <div class="box-tech">
      <div class="box-tech-title">BS EN 13306 Maintenance Classification (Asked in ESE 2026!)</div>
      <ul>
        <li><strong>Preventive Maintenance:</strong> Carried out at predetermined intervals or according to prescribed criteria to reduce the probability of failure:
          <ul>
            <li><em>Predetermined (Time-Based) Maintenance:</em> Scheduled without prior condition investigation.</li>
            <li><em>Condition-Based Maintenance (CBM) / Predictive Maintenance:</em> Based on continuous or periodic condition monitoring (vibration analysis, thermography, ferrography/oil analysis, acoustic emission).</li>
          </ul>
        </li>
        <li><strong>Corrective Maintenance:</strong> Carried out after fault recognition:
          <ul>
            <li><em>Immediate (Emergency) Corrective Maintenance:</em> Performed immediately after an unacceptable fault occurs.</li>
            <li><em>Deferred Corrective Maintenance:</em> Delayed in accordance with given maintenance rules.</li>
          </ul>
        </li>
        <li><strong>Total Productive Maintenance (TPM &mdash; Seiichi Nakajima):</strong> 8 Pillars; measures <strong>Overall Equipment Effectiveness (OEE)</strong> = <code>Availability &times; Performance Efficiency &times; Quality Rate</code> (World-class OEE benchmark = <strong>85%</strong>).</li>
      </ul>
    </div>
    <div class="box-update">
      <div class="box-update-title">ISO Standards Quick-Lookup Table</div>
      <ul>
        <li><strong>ISO 9000 / 9001:</strong> Quality Management Systems (QMS) fundamentals &amp; requirements.</li>
        <li><strong>ISO 14001:</strong> Environmental Management Systems (EMS) &amp; Life Cycle Assessment (ISO 14040).</li>
        <li><strong>ISO 19011:</strong> Guidelines for auditing management systems.</li>
        <li><strong>ISO/IEC 27001:</strong> Information Security Management Systems (ISMS).</li>
        <li><strong>ISO 31000:</strong> Risk Management guidelines.</li>
        <li><strong>ISO 45001:</strong> Occupational Health and Safety (OH&amp;S) Management Systems (replaced OHSAS 18001).</li>
        <li><strong>ISO 50001:</strong> Energy Management Systems.</li>
      </ul>
    </div>
  </div>
</div>
"""


DESIGN_DRAWING_SAFETY_HTML = COMMON_LMS_STYLE + """
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">UPSC ESE 2027 Paper-I &bull; Design, Drawing &amp; Importance of Safety</span>
    <h1>Master Compendium: Engineering Drawing (N.D. Bhatt), Design Principles (Dieter/Spotts) &amp; Industrial Safety</h1>
    <p>Complete Verbatim Synthesis of N.D. Bhatt Engineering Drawing, Engineering Design Methodology &amp; Industrial Safety Calculations (2017&ndash;2026).</p>
  </div>

  <h2>1. Engineering Drawing Standards, Sheet Sizes, Lines &amp; Scales (N.D. Bhatt Ch. 1&ndash;4)</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Standard Topic</th>
          <th>Exact Specification / Formula (Repeatedly Tested in ESE)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Drawing Sheet Sizes (ISO-A Series, Aspect Ratio 1 : &radic;2)</strong></td>
          <td><strong>A0:</strong> <code>841 mm &times; 1189 mm</code> (Area = 1 m<sup>2</sup>) &bull; <strong>A1:</strong> <code>594 &times; 841 mm</code> &bull; <strong>A2:</strong> <code>420 &times; 594 mm</code> &bull; <strong>A3:</strong> <code>297 &times; 420 mm</code> &bull; <strong>A4:</strong> <code>210 &times; 297 mm</code>.</td>
        </tr>
        <tr>
          <td><strong>BIS Standard Line Types (SP 46 / IS 10714)</strong></td>
          <td>
            &bull; <strong>Type A (Continuous Thick):</strong> Visible outlines and visible edges.<br>
            &bull; <strong>Type B (Continuous Thin):</strong> Dimension lines, leader lines, extension lines, hatching/section lines, revolved sections.<br>
            &bull; <strong>Type C (Continuous Thin Freehand) / Type D (Zigzag):</strong> Limits of partial or interrupted views.<br>
            &bull; <strong>Type E / F (Dashed Thick/Thin):</strong> Hidden outlines and hidden edges.<br>
            &bull; <strong>Type G (Chain Thin &mdash; Long-Short-Long):</strong> Center lines, lines of symmetry, pitch circles.<br>
            &bull; <strong>Type H (Chain Thin, Thick at Ends):</strong> Cutting-plane lines.<br>
            &bull; <strong>Type K (Chain Thin Double-Dashed):</strong> Outlines of adjacent parts, extreme positions of movable parts, centroidal lines.
          </td>
        </tr>
        <tr>
          <td><strong>Representative Fraction (RF) &amp; Scales</strong></td>
          <td>
            <code>RF = (Length of drawing) / (Actual length of object)</code> (Note: For a 3D volume/area given: <code>RF = &radic;(Drawing Area / Actual Area) = &root;3(Drawing Volume / Actual Volume)</code>).<br>
            <code>Length of Scale (LOS) = RF &times; Maximum Length to be Measured</code>.<br>
            &bull; <strong>Plain Scale:</strong> Measures 2 consecutive units (e.g., meters and decimeters).<br>
            &bull; <strong>Diagonal Scale:</strong> Measures <strong>3 consecutive units</strong> (e.g., meters, decimeters, centimeters) based on similar triangles.<br>
            &bull; <strong>Vernier Scale:</strong> Direct Vernier: <code>n VSD = (n &minus; 1) MSD &rArr; LC = 1 MSD &minus; 1 VSD = MSD / n</code>; Retrograde Vernier: <code>n VSD = (n + 1) MSD</code>.<br>
            &bull; <strong>Scale of Chords:</strong> Used to measure or set off angles when a protractor is unavailable (based on chord lengths on a quadrant of a circle).
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>2. Conic Sections, Engineering Curves &amp; Orthographic Projections (N.D. Bhatt Ch. 6&ndash;14)</h2>
  <ul>
    <li><strong>Conic Sections &amp; Eccentricity (e = Distance from Focus / Distance from Directrix):</strong>
      <ul>
        <li><strong>Circle:</strong> Cutting plane perpendicular to cone axis (<code>e = 0</code>).</li>
        <li><strong>Ellipse:</strong> Cutting plane inclined to axis at angle <code>&theta; &gt; &alpha;</code> (semi-apex angle), cutting all generators (<code>0 &lt; e &lt; 1</code>). Sum of focal distances = Major axis <code>2a</code>.</li>
        <li><strong>Parabola:</strong> Cutting plane parallel to a generator (<code>&theta; = &alpha;</code>, <code>e = 1</code>).</li>
        <li><strong>Hyperbola:</strong> Cutting plane inclined at <code>&theta; &lt; &alpha;</code>, cutting both nappes of double cone (<code>e &gt; 1</code>). Rectangular hyperbola (asymptotes at 90&deg;, Boyle's Law curve <code>PV = C</code>) has <code>e = &radic;2</code>.</li>
      </ul>
    </li>
    <li><strong>Cycloidal Curves &amp; Involutes:</strong>
      <ul>
        <li><strong>Cycloid:</strong> Locus of a point on the circumference of a circle rolling without slipping along a straight line.</li>
        <li><strong>Epicycloid:</strong> Circle rolling on the <em>outside</em> of another directing circle.</li>
        <li><strong>Hypocycloid:</strong> Circle rolling on the <em>inside</em> of another directing circle. (Crucial Trap: If rolling circle diameter = half of directing circle diameter, <code>r = R/2</code>, the hypocycloid is a <strong>straight line</strong> equal to the diameter of the directing circle!).</li>
        <li><strong>Involute:</strong> Locus of the free end of an inelastic taut string unwound from a circle or polygon. The normal to an involute at any point is always tangent to the base circle.</li>
      </ul>
    </li>
    <li><strong>First-Angle vs. Third-Angle Projection &amp; Points/Lines Rules:</strong>
      <ul>
        <li><strong>First-Angle Projection (BIS Standard):</strong> Object lies in 1st Quadrant (<strong>Above HP, In front of VP</strong>) &rArr; Observer &rarr; Object &rarr; Plane. Top View (Plan) is drawn <strong>below</strong> the XY reference line; Front View (Elevation) is drawn <strong>above</strong> XY; Left-Hand Side View is drawn on the <strong>right</strong> of Front View. Symbol: Frustum circle on the right of trapezoid (or cone taper pointing toward the circle).</li>
        <li><strong>Third-Angle Projection (ANSI/US Standard):</strong> Object lies in 3rd Quadrant (Below HP, Behind VP) &rArr; Observer &rarr; Transparent Plane &rarr; Object. Top View is <strong>above</strong> XY; Front View is <strong>below</strong> XY.</li>
        <li><strong>Projections of Straight Lines (N.D. Bhatt Golden Table):</strong>
          <ul>
            <li>Line parallel to both HP and VP &rArr; Both Front View and Top View show <strong>True Length (TL)</strong> and are parallel to XY.</li>
            <li>Line inclined at <code>&theta;</code> to HP and <code>&phi;</code> to VP &rArr; Apparent inclinations in projections (<code>&alpha;</code> in FV, <code>&beta;</code> in TV) are <strong>always greater than true inclinations</strong> (<code>&alpha; &gt; &theta;</code> and <code>&beta; &gt; &phi;</code>). If <code>&theta; + &phi; = 90&deg;</code>, both views lie on a single vertical projector with <code>&alpha; = &beta; = 90&deg;</code>!</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><strong>Isometric Projection vs. Isometric View (Drawing):</strong>
      <ul>
        <li>In Isometric Projection, the three principal axes are mutually inclined at <strong>120&deg;</strong>, and all isometric lines are foreshortened by the <strong>Isometric Scale Factor</strong>: <code>Isometric Length / True Length = cos 45&deg; / cos 30&deg; = (1/&radic;2) / (&radic;3/2) = &radic;(2/3) = 0.8165 (&asymp; 81.65% or 9/11)</code>.</li>
        <li>An <strong>Isometric View (Isometric Drawing)</strong> is drawn using True Lengths directly (100% scale) without foreshortening, so its linear dimensions are <code>1 / 0.8165 = 1.225</code> times larger than an Isometric Projection. A sphere in isometric projection appears as a circle of <strong>True Radius</strong> while its center is located using the isometric scale.</li>
      </ul>
    </li>
  </ul>

  <h2>3. General Principles of Engineering Design (George Dieter &amp; M.F. Spotts)</h2>
  <div class="grid-2">
    <div class="box-tech">
      <div class="box-tech-title">Shigley / Dieter 6-Phase Engineering Design Process</div>
      <ol>
        <li><strong>Recognition of Need</strong> (identifying the problem/market deficiency).</li>
        <li><strong>Definition of Problem</strong> (specifications, constraints, functional requirements).</li>
        <li><strong>Synthesis (Ideation / Brainstorming / Morphological Chart)</strong>.</li>
        <li><strong>Analysis and Optimization</strong> (stress, thermal, kinematic modeling, FEA).</li>
        <li><strong>Evaluation</strong> (prototyping, testing against specifications).</li>
        <li><strong>Presentation / Communication</strong> (manufacturing drawings, BOM).</li>
      </ol>
      <p><strong>Design for X (DFX):</strong> Design for Manufacturability (DFM), Design for Assembly (DFA &mdash; Boothroyd-Dewhurst method reducing part count), Design for Reliability (DFR), Design for Environment (DFE / Eco-design).</p>
    </div>
    <div class="box-upsc">
      <div class="box-upsc-title"> industrial Safety Engineering &amp; Accident Ratios</div>
      <ul>
        <li><strong>Heinrich's Domino Theory (1931):</strong> 5 sequential dominoes: (1) Ancestry &amp; Social Environment &rarr; (2) Fault of Person &rarr; (3) <strong>Unsafe Act / Mechanical or Physical Hazard (Middle Domino &mdash; remove this to prevent accidents!)</strong> &rarr; (4) Accident &rarr; (5) Injury.</li>
        <li><strong>Heinrich's 88 : 10 : 2 Ratio:</strong> 88% of industrial accidents are caused by <strong>Unsafe Acts of persons</strong>, 10% by <strong>Unsafe Mechanical/Physical Conditions</strong>, and 2% by unpreventable acts (Acts of God).</li>
        <li><strong>Heinrich's Safety Pyramid (1 : 29 : 300):</strong> For every <strong>1 Major/Fatal Injury</strong>, there are <strong>29 Minor Injuries</strong> and <strong>300 No-Injury Near-Miss Accidents</strong>. (Frank Bird's 1969 Triangle: <strong>1 : 10 : 30 : 600</strong>).</li>
        <li><strong>Safety Metrics:</strong>
          <ul>
            <li><strong>Frequency Rate (FR):</strong> <code>(Number of disabling injuries &times; 10<sup>6</sup>) / Total man-hours worked</code>.</li>
            <li><strong>Severity Rate (SR):</strong> <code>(Total man-days lost &times; 10<sup>6</sup>) / Total man-hours worked</code>.</li>
            <li><strong>OSHA Incidence Rate:</strong> <code>(Number of injuries/illnesses &times; 200,000) / Total hours worked</code>.</li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</div>
"""


ENERGY_AND_ENVIRONMENT_HTML = COMMON_LMS_STYLE + """
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">UPSC ESE 2027 Paper-I &bull; Basics of Energy &amp; Environment</span>
    <h1>Master Compendium: Energy Resources, Ecology, Pollution Control, EIA &amp; Climate Treaties</h1>
    <p>Complete Synthesis of Gilbert M. Masters, C.S. Rao, G.D. Rai, Odum / Bharucha &amp; Larry Canter (2017&ndash;2026).</p>
  </div>

  <h2>1. Ecology, Ecosystems &amp; Biodiversity</h2>
  <ul>
    <li><strong>Ecological Terms:</strong>
      <ul>
        <li><strong>Ecotone &amp; Edge Effect:</strong> An <em>ecotone</em> is a transition zone between two diverse ecosystems (e.g., mangrove forests, estuary, grassland-forest boundary). The tendency for species diversity and population density to be greater in the ecotone than in either adjoining community is the <strong>Edge Effect</strong> (species primarily abundant here are <em>Edge Species</em>).</li>
        <li><strong>Ecological Niche:</strong> Not just the physical address (<em>Habitat</em>), but the functional role, trophic position, and resource utilization of a species within the ecosystem (coined by Joseph Grinnell / Hutchinson). No two species can occupy the exact same ecological niche indefinitely (<strong>Gause's Competitive Exclusion Principle</strong>).</li>
        <li><strong>Lindeman's 10% Law &amp; Ecological Pyramids:</strong>
          <ul>
            <li><strong>Pyramid of Energy:</strong> <strong>ALWAYS Upright</strong> (never inverted) because ~90% of energy is lost as metabolic heat at each trophic transfer (Second Law of Thermodynamics).</li>
            <li><strong>Pyramid of Numbers:</strong> Upright in grassland/pond; <strong>Inverted</strong> in a parasitic food chain on a single large tree (1 Tree &rarr; Many herbivorous birds &rarr; Thousands of ectoparasites).</li>
            <li><strong>Pyramid of Biomass:</strong> Upright in terrestrial ecosystems; <strong>Inverted in Aquatic/Marine Ecosystems</strong> (small standing crop of phytoplankton supports a larger standing biomass of fishes/zooplankton due to rapid phytoplankton turnover).</li>
          </ul>
        </li>
        <li><strong>Ecological Succession:</strong> <em>Pioneer Community</em> (e.g., Lichens/Mosses in Xerarch primary succession on bare rock) &rarr; <em>Seral Stages (Sere)</em> &rarr; stable <em>Climax Community</em> (mesophytic forest).</li>
      </ul>
    </li>
    <li><strong>Biogeochemical Cycles:</strong>
      <ul>
        <li><strong>Nitrogen Cycle:</strong> (1) <em>Nitrogen Fixation</em> (N<sub>2</sub> &rarr; NH<sub>3</sub> by symbiotic <em>Rhizobium</em>, free-living <em>Azotobacter</em>, <em>Clostridium</em>, cyanobacteria <em>Anabaena/Nostoc</em>), (2) <em>Nitrification</em> (NH<sub>3</sub> &rarr; NO<sub>2</sub><sup>&minus;</sup> by <strong><em>Nitrosomonas</em></strong>; NO<sub>2</sub><sup>&minus;</sup> &rarr; NO<sub>3</sub><sup>&minus;</sup> by <strong><em>Nitrobacter</em></strong>), (3) <em>Assimilation</em>, (4) <em>Ammonification</em>, (5) <em>Denitrification</em> (NO<sub>3</sub><sup>&minus;</sup> &rarr; N<sub>2</sub> by anaerobic <strong><em>Pseudomonas</em></strong> and <em>Thiobacillus</em>).</li>
        <li><strong>Sedimentary Cycles:</strong> <strong>Phosphorus Cycle</strong> and <strong>Sulphur Cycle</strong> (main reservoir is Earth's crust/rocks rather than the atmosphere).</li>
      </ul>
    </li>
  </ul>

  <h2>2. Atmospheric Stability, Lapse Rates, Plume Behavior &amp; Air Pollution Control (Gilbert M. Masters &amp; C.S. Rao)</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Plume Type</th>
          <th>Lapse Rate Condition (ELR vs. DALR &Gamma;<sub>d</sub> = 9.8&deg;C/km)</th>
          <th>Atmospheric Stability &amp; Dispersion Characteristics (High-Yield ESE!)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Looping Plume</strong></td>
          <td><strong>Super-adiabatic (ELR &gt; DALR)</strong></td>
          <td><strong>Highly Unstable atmosphere</strong> (strong daytime solar heating). Large thermal eddies cause wavy, sinuous plume; high turbulence brings puffs briefly to ground near stack.</td>
        </tr>
        <tr>
          <td><strong>2. Coning Plume</strong></td>
          <td><strong>Sub-adiabatic / Near-Neutral (SALR &lt; ELR &lt; DALR)</strong></td>
          <td><strong>Neutral / Slightly Stable atmosphere</strong> (cloudy, windy days). Plume spreads symmetrically in a cone; basis for the <strong>Gaussian Plume Dispersion Equation</strong>.</td>
        </tr>
        <tr>
          <td><strong>3. Fanning Plume</strong></td>
          <td><strong>Temperature Inversion (ELR &lt; 0, temperature increases with height)</strong></td>
          <td><strong>Extremely Stable atmosphere</strong> (clear night with radiative cooling). Vertical motion is completely suppressed; plume spreads horizontally like a thin flat fan.</td>
        </tr>
        <tr>
          <td><strong>4. Lofting Plume</strong></td>
          <td><strong>Inversion below stack top; Super-adiabatic/Unstable above stack top</strong></td>
          <td><strong>MOST FAVORABLE / IDEAL Condition for Pollution Dispersion!</strong> Downward mixing to the ground is blocked by the lower inversion layer, while upward dispersion into the upper atmosphere is unrestricted!</td>
        </tr>
        <tr>
          <td><strong>5. Fumigation Plume</strong></td>
          <td><strong>Inversion layer just above stack top; Super-adiabatic/Unstable below stack top</strong></td>
          <td><strong>MOST DANGEROUS / WORST Ground-Level Condition!</strong> Occurs in the morning when rising sun breaks up a nocturnal surface inversion from the ground upward, rapidly mixing the trapped pollutants straight down to ground level.</td>
        </tr>
        <tr>
          <td><strong>6. Trapping Plume</strong></td>
          <td><strong>Inversion layers both above and below the stack height</strong></td>
          <td>Plume is trapped between two stable inversion layers and can only diffuse within a limited vertical mixing depth.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>3. Water Pollution, BOD Numericals &amp; Environmental Impact Assessment (EIA)</h2>
  <div class="grid-2">
    <div class="box-tech">
      <div class="box-tech-title">BOD<sub>5</sub> Formula &amp; Water Quality (Gilbert M. Masters)</div>
      <ul>
        <li><strong>First-Order BOD Kinetics:</strong> <code>BOD<sub>t</sub> = L<sub>0</sub> (1 &minus; e<sup>&minus;kt</sup>) = L<sub>0</sub> (1 &minus; 10<sup>&minus;K<sub>10</sub> t</sup>)</code>, where <code>L<sub>0</sub></code> is Ultimate Carbonaceous BOD and <code>k = 2.303 K<sub>10</sub></code>.</li>
        <li><strong>Temperature Dependence of Rate Constant:</strong> <code>k<sub>T</sub> = k<sub>20</sub> (1.047)<sup>T &minus; 20</sup></code>. (Standard BOD test is <strong>5 days at 20&deg;C</strong> in the dark; typically <code>BOD<sub>5</sub> at 20&deg;C &asymp; BOD<sub>3</sub> at 27&deg;C &asymp; 68% of Ultimate BOD L<sub>0</sub></code>).</li>
        <li><strong>Dilution BOD Formula:</strong> <code>BOD<sub>5</sub> = [(DO<sub>i</sub> &minus; DO<sub>f</sub>) &minus; (B<sub>i</sub> &minus; B<sub>f</sub>)(1 &minus; P)] / P</code>, where <code>P = V<sub>sample</sub> / V<sub>bottle</sub></code> is the dilution fraction (300 mL bottle).</li>
        <li><strong>Drinking Water Triggers:</strong> Excess <strong>Nitrate (&gt; 45 mg/L)</strong> &rarr; <em>Methemoglobinemia (Blue Baby Syndrome)</em>; <strong>Fluoride (&gt; 1.5 mg/L)</strong> &rarr; <em>Dental/Skeletal Fluorosis</em>; <strong>Mercury (Hg)</strong> &rarr; <em>Minamata Disease</em>; <strong>Cadmium (Cd)</strong> &rarr; <em>Itai-Itai (Ouch-Ouch) Disease</em>; <strong>Arsenic (As)</strong> &rarr; <em>Blackfoot Disease</em>.</li>
      </ul>
    </div>
    <div class="box-upsc">
      <div class="box-upsc-title">EIA Sequential Steps &amp; International Climate Treaties</div>
      <ul>
        <li><strong>8 Sequential Steps of EIA (Larry Canter):</strong>
          <br><code>1. Screening &rarr; 2. Scoping (produces Terms of Reference ToR) &rarr; 3. Baseline Data Collection &rarr; 4. Impact Prediction &amp; Assessment &rarr; 5. Mitigation &amp; EMP (Environmental Management Plan) &rarr; 6. Public Hearing / Consultation &rarr; 7. Decision-Making (Appraisal) &rarr; 8. Post-Project Monitoring</code>.</li>
        <li><strong>Major Treaties:</strong>
          <ul>
            <li><strong>Ramsar Convention (1971):</strong> Conservation of Wetlands (Montreux Record).</li>
            <li><strong>Montreal Protocol (1987):</strong> Phase-out of Ozone-Depleting Substances (CFCs/Halons).</li>
            <li><strong>Kigali Amendment (2016):</strong> Phase-down of Hydrofluorocarbons (HFCs &mdash; high GWP greenhouse gases, though zero ODP) under the Montreal Protocol.</li>
            <li><strong>Basel (1989) / Rotterdam (1998) / Stockholm (2001):</strong> Transboundary Hazardous Wastes / Prior Informed Consent (PIC) for Hazardous Chemicals / Persistent Organic Pollutants (POPs).</li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</div>
"""


ENGINEERING_MATHS_AND_APTITUDE_HTML = COMMON_LMS_STYLE + """
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">UPSC ESE 2027 Paper-I &bull; Engineering Mathematics &amp; Engineering Aptitude</span>
    <h1>Master Compendium: Engineering Mathematics (Grewal / Jain-Iyengar) &amp; Engineering Aptitude (Aufmann / Nelsen)</h1>
    <p>Complete Formula &amp; Setter Source Compendium covering Linear Algebra, Calculus, Differential Equations, Probability, Numerical Methods, Apportionment, Voting Power Indices &amp; Graph Theory.</p>
  </div>

  <h2>1. Numerical Methods Master Table (Jain, Iyengar &amp; Jain &mdash; Asked Every Year!)</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Numerical Method</th>
          <th>Iteration / Integration Formula</th>
          <th>Order of Convergence / Error Term &amp; Restrictions</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Bisection (Bolzano) Method</strong></td>
          <td><code>x<sub>n+1</sub> = (a<sub>n</sub> + b<sub>n</sub>) / 2</code></td>
          <td><strong>Linear Convergence (Order p = 1)</strong>; guaranteed convergence if <code>f(a)f(b) &lt; 0</code>; error halves each step: <code>|e<sub>n</sub>| &le; (b &minus; a) / 2<sup>n</sup></code>.</td>
        </tr>
        <tr>
          <td><strong>Regula-Falsi (False Position)</strong></td>
          <td><code>x<sub>n+1</sub> = [a f(b) &minus; b f(a)] / [f(b) &minus; f(a)]</code></td>
          <td>Order of convergence <strong>p = 1 (Superlinear ~1.618 for Secant)</strong>; always brackets the root.</td>
        </tr>
        <tr>
          <td><strong>Secant Method</strong></td>
          <td><code>x<sub>n+1</sub> = x<sub>n</sub> &minus; f(x<sub>n</sub>)(x<sub>n</sub> &minus; x<sub>n&minus;1</sub>) / [f(x<sub>n</sub>) &minus; f(x<sub>n&minus;1</sub>)]</code></td>
          <td>Order of convergence <strong>p = (1 + &radic;5)/2 &asymp; 1.618 (Golden Ratio)</strong>; does not require derivatives.</td>
        </tr>
        <tr>
          <td><strong>Newton-Raphson Method</strong></td>
          <td><code>x<sub>n+1</sub> = x<sub>n</sub> &minus; f(x<sub>n</sub>) / f'(x<sub>n</sub>)</code></td>
          <td><strong>Quadratic Convergence (Order p = 2)</strong> for simple roots (reduces to <strong>p = 1</strong> for multiple roots!). Fails if <code>f'(x<sub>n</sub>) &asymp; 0</code>.</td>
        </tr>
        <tr>
          <td><strong>Trapezoidal Rule (Degree 1)</strong></td>
          <td><code>(h / 2) [ (y<sub>0</sub> + y<sub>n</sub>) + 2(y<sub>1</sub> + y<sub>2</sub> + &hellip; + y<sub>n&minus;1</sub>) ]</code></td>
          <td>Valid for <strong>ANY number of subintervals n</strong>; Global Error = <code>&minus;[(b &minus; a) / 12] h<sup>2</sup> f''(&xi;) &propto; O(h<sup>2</sup>)</code>. Exact for polynomials up to <strong>degree 1</strong>.</td>
        </tr>
        <tr>
          <td><strong>Simpson's 1/3 Rule (Degree 2 Parabola)</strong></td>
          <td><code>(h / 3) [ (y<sub>0</sub> + y<sub>n</sub>) + 4(y<sub>1</sub> + y<sub>3</sub> + &hellip;) + 2(y<sub>2</sub> + y<sub>4</sub> + &hellip;) ]</code></td>
          <td>Requires <strong>n to be EVEN</strong>; Global Error = <code>&minus;[(b &minus; a) / 180] h<sup>4</sup> f<sup>(iv)</sup>(&xi;) &propto; O(h<sup>4</sup>)</code>. Exact for polynomials up to <strong>degree 3 (cubics!)</strong>.</td>
        </tr>
        <tr>
          <td><strong>Simpson's 3/8 Rule (Degree 3 Cubic)</strong></td>
          <td><code>(3h / 8) [ (y<sub>0</sub> + y<sub>n</sub>) + 3(y<sub>1</sub> + y<sub>2</sub> + y<sub>4</sub> + &hellip;) + 2(y<sub>3</sub> + y<sub>6</sub> + &hellip;) ]</code></td>
          <td>Requires <strong>n to be a MULTIPLE OF 3</strong>; Global Error = <code>&minus;[(b &minus; a) / 80] h<sup>4</sup> f<sup>(iv)</sup>(&xi;) &propto; O(h<sup>4</sup>)</code>.</td>
        </tr>
        <tr>
          <td><strong>Runge-Kutta 4th Order (RK4) for dy/dx = f(x, y)</strong></td>
          <td><code>y<sub>n+1</sub> = y<sub>n</sub> + (1/6)(k<sub>1</sub> + 2k<sub>2</sub> + 2k<sub>3</sub> + k<sub>4</sub>)</code></td>
          <td>Single-step explicit method; Local truncation error <code>O(h<sup>5</sup>)</code>, Global error <code>O(h<sup>4</sup>)</code>; requires 4 function evaluations per step.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>2. Aufmann's "Mathematical Excursions" — Apportionment &amp; Voting Theory (ESE 2024 Verbatim Source!)</h2>
  <p>In ESE 2024, UPSC lifted <strong>11 consecutive questions</strong> verbatim from <em>Mathematical Excursions</em> by Richard N. Aufmann, Joanne Lockwood, Richard D. Nation, and Daniel K. Clegg (Chapters 4 &amp; 5):</p>
  <div class="grid-2">
    <div class="box-upsc">
      <div class="box-upsc-title">Apportionment Methods &amp; Quota Rule</div>
      <ul>
        <li><strong>Standard Divisor (SD):</strong> <code>SD = Total Population / Total Seats to Apportion</code>.</li>
        <li><strong>Standard Quota (SQ):</strong> <code>SQ = State Population / SD</code>. Lower Quota <code>LQ = &lfloor;SQ&rfloor;</code>; Upper Quota <code>UQ = &lceil;SQ&rceil;</code>.</li>
        <li><strong>Hamilton's Method:</strong> Give each state its Lower Quota <code>LQ</code>; assign remaining surplus seats one by one to states with the <strong>largest fractional decimal remainders</strong>.</li>
        <li><strong>Jefferson's Method:</strong> Uses a smaller <em>Modified Divisor d &lt; SD</em> and rounds <strong>DOWN (Floor &lfloor;MQ&rfloor;)</strong>. Favors large states; can violate Upper Quota.</li>
        <li><strong>Adams's Method:</strong> Uses a larger <em>Modified Divisor d &gt; SD</em> and rounds <strong>UP (Ceiling &lceil;MQ&rceil;)</strong>. Favors small states; can violate Lower Quota.</li>
        <li><strong>Webster's Method:</strong> Uses a Modified Divisor and rounds to the <strong>nearest integer</strong> (arithmetic mean cutoff <code>0.5</code>).</li>
        <li><strong>Huntington-Hill Method (Current U.S. House Method):</strong> Uses the <strong>Geometric Mean cutoff</strong> <code>&radic;[n(n + 1)]</code> between Lower Quota <em>n</em> and Upper Quota <em>n + 1</em>.</li>
        <li><strong>Three Apportionment Paradoxes (Balinski-Young Theorem):</strong>
          <ul>
            <li><em>Alabama Paradox:</em> Increasing the total number of seats causes a state to lose a seat.</li>
            <li><em>Population Paradox:</em> State A grows faster than State B, yet loses a seat to State B.</li>
            <li><em>New-States Paradox:</em> Adding a new state with its fair share of seats alters the apportionment among existing states.</li>
          </ul>
        </li>
      </ul>
    </div>
    <div class="box-tech">
      <div class="box-tech-title">Weighted Voting Systems &amp; Voting Methods</div>
      <ul>
        <li><strong>Weighted Voting Notation:</strong> <code>[q : w<sub>1</sub>, w<sub>2</sub>, &hellip;, w<sub>n</sub>]</code>, where <code>q</code> is the quota (must satisfy <code>W/2 &lt; q &le; W</code>) and <code>w<sub>i</sub></code> are voter weights.</li>
        <li><strong>Special Voters:</strong>
          <ul>
            <li><strong>Dictator:</strong> A voter whose weight alone is <code>w<sub>i</sub> &ge; q</code> (has 100% of power; all other voters are dummies).</li>
            <li><strong>Dummy Voter:</strong> A voter who is never a critical voter in any winning coalition (Banzhaf power = 0).</li>
            <li><strong>Veto Power:</strong> A voter without whom no coalition can reach the quota: <code>(W &minus; w<sub>i</sub>) &lt; q</code>.</li>
          </ul>
        </li>
        <li><strong>Banzhaf Power Index:</strong> Count how many times each voter is a <strong>Critical Voter</strong> (whose departure turns a winning coalition into a losing one) divided by total critical voter instances across all winning coalitions.</li>
        <li><strong>Four Fairness Criteria (Arrow's Impossibility Theorem):</strong>
          <ol>
            <li><em>Majority Criterion:</em> Candidate with &gt;50% first-place votes must win. (Violated by Borda Count!).</li>
            <li><em>Condorcet (Head-to-Head) Criterion:</em> Candidate who beats every other candidate in 1-on-1 pairwise comparisons must win.</li>
            <li><em>Monotonicity Criterion:</em> Ranking a winner higher on re-vote must never hurt them. (Violated by Plurality-with-Elimination!).</li>
            <li><em>Independence of Irrelevant Alternatives (IIA):</em> Removing a losing candidate must not change the winner.</li>
          </ol>
        </li>
      </ul>
    </div>
  </div>
</div>
"""


CURRENT_ISSUES_AND_STRATEGY_HTML = COMMON_LMS_STYLE + """
<div class="upsc-ese-article">
  <div class="cover-header">
    <span class="module-tag">UPSC ESE 2027 Paper-I &bull; Current Issues &amp; 10-Subject Exam Strategy</span>
    <h1>Master Compendium: National &amp; International Engineering Initiatives &amp; 10-Year Paper-I Setter Blueprint</h1>
    <p>Flagship Missions (National Green Hydrogen, IndiaAI, National Quantum Mission, Semiconductor Mission, PM GatiShakti) &amp; Complete 10-Subject Weightage Matrix (2017&ndash;2026).</p>
  </div>

  <h2>1. High-Yield National Engineering, Infrastructure &amp; Tech Missions for ESE 2027</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>Flagship Mission / Policy</th>
          <th>Nodal Ministry / Outlay</th>
          <th>Key Technical Targets &amp; Exam Facts</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>National Green Hydrogen Mission (NGHM)</strong></td>
          <td>Ministry of New &amp; Renewable Energy (MNRE) &bull; ₹19,744 Crore</td>
          <td>Target: <strong>5 MMT (Million Metric Tonnes) per annum</strong> of Green Hydrogen production capacity by <strong>2030</strong>, accompanied by ~125 GW of associated renewable energy capacity and SIGHT (Strategic Interventions for Green Hydrogen Transition) incentives for electrolyzer manufacturing.</td>
        </tr>
        <tr>
          <td><strong>National Quantum Mission (NQM)</strong></td>
          <td>Department of Science &amp; Technology (DST) &bull; ₹6,003.65 Crore (2023&ndash;2031)</td>
          <td>Develop intermediate-scale quantum computers with <strong>50&ndash;1000 physical qubits in 8 years</strong> across <strong>4 Thematic Hubs (T-Hubs)</strong>: (1) Quantum Computing (IISc Bengaluru), (2) Quantum Communication (IIT Madras), (3) Quantum Sensing &amp; Metrology (IIT Bombay), and (4) Quantum Materials &amp; Devices (IIT Delhi).</td>
        </tr>
        <tr>
          <td><strong>IndiaAI Mission</strong></td>
          <td>Ministry of Electronics &amp; IT (MeitY) &bull; ₹10,371.92 Crore</td>
          <td>7 Pillars: IndiaAI Compute Capacity (10,000+ GPUs via PPP), IndiaAI Innovation Centre (indigenous foundational LMMs/LLMs), IndiaAI Datasets Platform (AIKosh), Application Development, FutureSkills, Startup Financing, and Safe &amp; Trusted AI.</td>
        </tr>
        <tr>
          <td><strong>India Semiconductor Mission (ISM)</strong></td>
          <td>MeitY &bull; ₹76,000 Crore Semicon India Programme</td>
          <td>Up to 50% pari-passu fiscal support for Silicon CMOS fabs, Compound Semiconductors/ATMP/OSAT units, and Design-Linked Incentive (DLI) scheme.</td>
        </tr>
        <tr>
          <td><strong>PM GatiShakti &amp; National Logistics Policy (NLP)</strong></td>
          <td>DPIIT (Ministry of Commerce &amp; Industry)</td>
          <td>GIS-based digital master planning integrating <strong>7 Engines</strong> (Roads, Railways, Airports, Ports, Mass Transport, Waterways, Logistics Infrastructure) developed by <strong>BISAG-N</strong>, plus <strong>ULIP (Unified Logistics Interface Platform)</strong>.</td>
        </tr>
        <tr>
          <td><strong>Panchamrit &amp; Net-Zero Climate Pledges</strong></td>
          <td>MoEFCC / UNFCCC COP</td>
          <td>(1) 500 GW non-fossil energy capacity by 2030, (2) 50% cumulative electric power installed capacity from non-fossil sources by 2030, (3) Reduce carbon intensity of GDP by <strong>45% by 2030</strong> (over 2005 levels), (4) Reduce 1 Billion tonnes projected emissions by 2030, (5) Achieve <strong>Net-Zero Emissions by 2070</strong>.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>2. Complete 10-Year (2017&ndash;2026) UPSC ESE Paper-I Setter's Weightage &amp; Bookshelf Blueprint</h2>
  <div class="table-responsive">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Official Paper-I Subject</th>
          <th>10-Yr Avg Qs</th>
          <th>2025 Qs</th>
          <th>2026 Qs</th>
          <th>Primary Verbatim Textbooks Used by UPSC Setters</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td><strong>Current Issues (Economy/Social/Industrial)</strong></td>
          <td>9.8</td>
          <td>14</td>
          <td>10</td>
          <td>PIB Year-End Reviews, Economic Survey, Union Budget, India Year Book, NITI Aayog Reports.</td>
        </tr>
        <tr>
          <td>2</td>
          <td><strong>Engineering Aptitude (Reasoning)</strong></td>
          <td>13.9</td>
          <td>15</td>
          <td>15</td>
          <td><em>R.S. Aggarwal</em>, <em>Richard N. Aufmann (Mathematical Excursions Ch. 4&ndash;5)</em>, <em>Roger Nelsen (Proofs Without Words)</em>.</td>
        </tr>
        <tr>
          <td>3</td>
          <td><strong>Engineering Mathematics &amp; Numerical Analysis</strong></td>
          <td>12.8</td>
          <td>10</td>
          <td>10</td>
          <td><em>B.S. Grewal (Higher Engineering Mathematics)</em>, <em>M.K. Jain, S.R.K. Iyengar &amp; R.K. Jain (Numerical Methods)</em>.</td>
        </tr>
        <tr>
          <td>4</td>
          <td><strong>Design, Drawing &amp; Importance of Safety</strong></td>
          <td>8.7</td>
          <td>9</td>
          <td>7</td>
          <td><em>N.D. Bhatt (Engineering Drawing)</em>, <em>George E. Dieter (Engineering Design)</em>, <em>M.F. Spotts</em>.</td>
        </tr>
        <tr>
          <td>5</td>
          <td><strong>Standards &amp; Quality Practices</strong></td>
          <td>9.2</td>
          <td>8</td>
          <td>10</td>
          <td><em>Amitava Mitra</em>, <em>Dale H. Besterfield (TQM)</em>, <em>M. Jeya Chandra</em>, <em>BS EN 13306 Maintenance Standard</em>.</td>
        </tr>
        <tr>
          <td>6</td>
          <td><strong>Basics of Energy &amp; Environment</strong></td>
          <td>10.2</td>
          <td>11</td>
          <td>10</td>
          <td><em>Gilbert M. Masters</em>, <em>C.S. Rao (Air Pollution)</em>, <em>G.D. Rai</em>, <em>Odum / Bharucha</em>, <em>Larry Canter (EIA)</em>.</td>
        </tr>
        <tr>
          <td>7</td>
          <td><strong>Basics of Project Management</strong></td>
          <td>8.7</td>
          <td>9</td>
          <td>8</td>
          <td><em>Prasanna Chandra (Projects)</em>, <em>Clifford F. Gray &amp; Erik W. Larson (Project Management)</em>.</td>
        </tr>
        <tr>
          <td>8</td>
          <td><strong>Basics of Material Science &amp; Engineering</strong></td>
          <td>9.1</td>
          <td>9</td>
          <td>6</td>
          <td><em>William D. Callister Jr. (Materials Science and Engineering + Worked Examples)</em>, <em>V. Raghavan</em>.</td>
        </tr>
        <tr>
          <td>9</td>
          <td><strong>Information &amp; Communication Technologies (ICT)</strong></td>
          <td>8.6</td>
          <td>9</td>
          <td>12</td>
          <td><em>Andrew S. Tanenbaum</em>, <em>Peterson &amp; Davie</em>, <em>William Stallings</em>, <em>George W. Reynolds</em>, <em>Russell &amp; Norvig</em>, <em>2nd ARC 11th Report</em>.</td>
        </tr>
        <tr>
          <td>10</td>
          <td><strong>Ethics &amp; Values in Engineering Profession</strong></td>
          <td>9.0</td>
          <td>6</td>
          <td>12</td>
          <td><em>Mike W. Martin &amp; Roland Schinzinger</em>, <em>R.R. Gaur, R. Sangal &amp; G.P. Bagaria (AICTE UHV)</em>, <em>Michael Davis</em>, <em>R.S. Naagarazan</em>.</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
"""
