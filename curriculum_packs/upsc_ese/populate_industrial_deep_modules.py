# -*- coding: utf-8 -*-
"""
Populate specialized full-depth interactive modules for:
Topic 52: Production Planning & Control (PPC, Forecasting, Scheduling, Line Balancing, MRP, JIT)
Topic 53: Inventory Control (Deterministic & Probabilistic EOQ, Safety Stock, Selective Control ABC/VED)
Topic 54: Operations Research (Simplex, Duality, Transportation, Hungarian Assignment, Queuing M/M/1)
Topic 55: Work Study & Ergonomics (Method Study, Time Study, Work Sampling, Therbligs)
Topic 56: Maintenance Engineering, Reliability & Failure Analysis (Bathtub curve, MTBF, TPM, OEE)
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.topic import TopicContent

def wrap_art(badge, title, subtitle, body_html):
    return f"""
    <div class="art-container" style="padding: 18px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.65; max-width: 100%;">
      <div class="cover-header" style="background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%); color: #ffffff !important; padding: 28px 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 14px rgba(0,0,0,0.12);">
        <span style="display:inline-block; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; background: rgba(255,255,255,0.22); color: #ffffff !important; padding: 4px 12px; border-radius: 20px; font-weight: 700; margin-bottom: 12px;">{badge}</span>
        <h1 style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; background: none !important; margin: 0 0 10px 0; font-size: 24px; font-weight: 800; line-height: 1.3;">{title}</h1>
        <p style="color: #e0f2fe !important; margin: 0; font-size: 14px; line-height: 1.5;">{subtitle}</p>
      </div>
      <div class="art-body" style="font-size: 15px;">
        {body_html}
      </div>
    </div>
    """

MODULES = {}

# ----------------- Topic 52: PPC -----------------
MODULES[52] = ("📘 Module 52: Production Planning & Control (PPC), Forecasting & Line Balancing", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechanical Engineering (Topic 52)",
    "Production Planning, Demand Forecasting, Sequencing & Assembly Line Balancing",
    "Complete synthesis based on Buffa & Sarin, Mahajan and O.P. Khanna covering quantitative forecasting models, Johnson's Rule & assembly line efficiency.",
    """
    <h2>1. Demand Forecasting Quantitative Models</h2>
    <div class="table-responsive">
      <table style="width:100%; border-collapse:collapse; margin-bottom:18px;">
        <tr style="background:#f1f5f9; text-align:left;"><th style="padding:10px; border:1px solid #cbd5e1;">Model</th><th style="padding:10px; border:1px solid #cbd5e1;">Mathematical Formulation</th><th style="padding:10px; border:1px solid #cbd5e1;">Key Exam Insights &amp; Properties</th></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Simple Moving Average</strong></td><td style="padding:10px; border:1px solid #cbd5e1;">$F_t = \frac{D_{t-1} + D_{t-2} + \dots + D_{t-n}}{n}$</td><td style="padding:10px; border:1px solid #cbd5e1;">Equal weights $\frac{1}{n}$. Larger $n$ smooths random fluctuations but lags trends.</td></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Weighted Moving Average</strong></td><td style="padding:10px; border:1px solid #cbd5e1;">$F_t = \sum_{i=1}^n w_i D_{t-i}, \quad \sum w_i = 1$</td><td style="padding:10px; border:1px solid #cbd5e1;">Heavier weight given to recent periods ($w_1 > w_2 > \dots > w_n$).</td></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Exponential Smoothing</strong></td><td style="padding:10px; border:1px solid #cbd5e1;">$F_t = F_{t-1} + \alpha (D_{t-1} - F_{t-1})$</td><td style="padding:10px; border:1px solid #cbd5e1;">Special case of weighted moving average where weights decline exponentially. Smoothing constant $\alpha = \frac{2}{N+1}$. Low $\alpha$ (0.1) = stable demand; High $\alpha$ (0.7) = volatile demand.</td></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Tracking Signal (TS)</strong></td><td style="padding:10px; border:1px solid #cbd5e1;">$\text{TS} = \frac{\sum (D_t - F_t)}{\text{MAD}} = \frac{\text{Cumulative Forecast Error}}{\text{MAD}}$</td><td style="padding:10px; border:1px solid #cbd5e1;">Acceptable limits: $-4 \le \text{TS} \le +4$. Persistent positive TS indicates under-forecasting; persistent negative TS indicates over-forecasting.</td></tr>
      </table>
    </div>

    <h2>2. Sequencing &amp; Scheduling (Johnson's Algorithm)</h2>
    <ul>
      <li><strong>$n$ Jobs on 2 Machines ($M_1 \to M_2$):</strong> Find the minimum processing time among all remaining jobs on both machines. If the minimum time occurs on $M_1$, schedule that job <em>first</em>. If it occurs on $M_2$, schedule that job <em>last</em>. Remove the job and repeat.</li>
      <li><strong>Makespan:</strong> Total elapsed time from start of first job on $M_1$ to completion of last job on $M_2$. Minimizing makespan minimizes idle time.</li>
      <li><strong>$n$ Jobs on 3 Machines ($M_1 \to M_2 \to M_3$):</strong> Valid if $\min(t_{i1}) \ge \max(t_{i2})$ OR $\min(t_{i3}) \ge \max(t_{i2})$. Convert to 2 virtual machines: $G_i = t_{i1} + t_{i2}$, $H_i = t_{i2} + t_{i3}$.</li>
    </ul>

    <h2>3. Assembly Line Balancing (ALB)</h2>
    <ul>
      <li><strong>Cycle Time ($T_c$):</strong> $T_c = \frac{\text{Available Production Time per Day}}{\text{Daily Demand Rate}}$. (Also: $T_c \ge \max(t_i)$ where $t_i$ is task time).</li>
      <li><strong>Theoretical Minimum Number of Workstations ($N_{\min}$):</strong> $N_{\min} = \left\lceil \frac{\sum t_i}{T_c} \right\rceil$.</li>
      <li><strong>Line Efficiency ($\eta_L$):</strong> $\eta_L = \frac{\sum t_i}{N_{\text{actual}} \times T_c} \times 100\%$.</li>
      <li><strong>Balance Delay ($d$ / Smoothness Index):</strong> $d = 100\% - \eta_L = \frac{N_{\text{actual}} T_c - \sum t_i}{N_{\text{actual}} T_c} \times 100\%$.</li>
    </ul>
    """
))

# ----------------- Topic 53: Inventory Control -----------------
MODULES[53] = ("📘 Module 53: Inventory Control Models, Safety Stock & Selective Classification", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechanical Engineering (Topic 53)",
    "Deterministic & Probabilistic EOQ, Reorder Point, Quantity Discounts & ABC/VED Analysis",
    "Complete synthesis based on Hamdy A. Taha and N.D. Vohra covering Wilson's EOQ, Finite Production Rate (EPQ), Backorder models, and Service Levels.",
    """
    <h2>1. Classical Deterministic Inventory Models</h2>
    <div class="table-responsive">
      <table style="width:100%; border-collapse:collapse; margin-bottom:18px;">
        <tr style="background:#f1f5f9; text-align:left;"><th style="padding:10px; border:1px solid #cbd5e1;">Model</th><th style="padding:10px; border:1px solid #cbd5e1;">Economic Order Quantity ($Q^*$)</th><th style="padding:10px; border:1px solid #cbd5e1;">Total Variable Cost ($\text{TIC}^*$)</th></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Basic Wilson EOQ</strong> (Instantaneous supply, no shortages)</td><td style="padding:10px; border:1px solid #cbd5e1;">$Q^* = \sqrt{\frac{2 D C_o}{C_h}}$</td><td style="padding:10px; border:1px solid #cbd5e1;">$\text{TIC}^* = \sqrt{2 D C_o C_h}$. At EOQ: $\text{Annual Ordering Cost} = \text{Annual Holding Cost}$.</td></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Production / EPQ Model</strong> (Finite replenishment rate $p > d$)</td><td style="padding:10px; border:1px solid #cbd5e1;">$Q^* = \sqrt{\frac{2 D C_o}{C_h \left(1 - \frac{d}{p}\right)}}$</td><td style="padding:10px; border:1px solid #cbd5e1;">$\text{TIC}^* = \sqrt{2 D C_o C_h \left(1 - \frac{d}{p}\right)}$. Maximum inventory level $= Q^* \left(1 - \frac{d}{p}\right) < Q^*$.</td></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Planned Shortages / Backorder Model</strong> ($C_b$ = shortage cost)</td><td style="padding:10px; border:1px solid #cbd5e1;">$Q^* = \sqrt{\frac{2 D C_o}{C_h}} \times \sqrt{\frac{C_h + C_b}{C_b}}$</td><td style="padding:10px; border:1px solid #cbd5e1;">$\text{TIC}^* = \sqrt{2 D C_o C_h} \times \sqrt{\frac{C_b}{C_h + C_b}}$. Max backorder level $S^* = Q^* \frac{C_h}{C_h + C_b}$.</td></tr>
      </table>
    </div>

    <h2>2. Safety Stock &amp; Probabilistic Reorder Point (ROP)</h2>
    <ul>
      <li><strong>Constant Lead Time ($L$), Variable Demand ($D \sim N(\mu_d, \sigma_d^2)$):</strong>
        <p style="text-align:center; font-weight:bold;">$\text{ROP} = \bar{d} \cdot L + z \cdot \sigma_L = \bar{d} \cdot L + z \cdot (\sigma_d \sqrt{L})$</p>
        where $\text{Safety Stock (SS)} = z \cdot \sigma_d \sqrt{L}$, and $z$ is standard normal deviate for desired service level ($z = 1.645$ for 95%, $z = 2.33$ for 99%).
      </li>
      <li><strong>Variable Lead Time ($L \sim N(\mu_L, \sigma_L^2)$), Constant Demand ($d$):</strong>
        <p style="text-align:center; font-weight:bold;">$\text{SS} = z \cdot d \cdot \sigma_L$</p>
      </li>
    </ul>

    <h2>3. Selective Inventory Control Classifications</h2>
    <ul>
      <li><strong>ABC Analysis:</strong> Based on <em>Annual Usage Value</em> (Pareto 80/20 principle). A-items: ~10% items, ~70% value (tight control, low safety stock). B-items: ~20% items, ~20% value. C-items: ~70% items, ~10% value (simple control, bulk orders).</li>
      <li><strong>VED Analysis:</strong> Based on <em>Criticality to production</em> (Vital, Essential, Desirable). Vital items halt plant if missing.</li>
      <li><strong>FSN Analysis:</strong> Based on <em>Consumption rate</em> (Fast moving, Slow moving, Non-moving). Non-moving items must be dead-stocked.</li>
      <li><strong>SDE Analysis:</strong> Based on <em>Procurement availability</em> (Scarce, Difficult, Easy to acquire).</li>
      <li><strong>HML Analysis:</strong> Based on <em>Unit price of material</em> (High, Medium, Low cost per unit).</li>
    </ul>
    """
))

# ----------------- Topic 54: Operations Research -----------------
MODULES[54] = ("📘 Module 54: Operations Research (Linear Programming, Transportation, Assignment & Queuing)", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechanical Engineering (Topic 54)",
    "Simplex Method, Duality Theorems, VAM/MODI Transportation, Hungarian Method & M/M/1 Queuing",
    "Complete synthesis based on Hamdy A. Taha and Kantiswarup covering Degeneracy, Duality, Unbalanced matrices, and birth-death queuing metrics.",
    """
    <h2>1. Linear Programming &amp; Simplex Method</h2>
    <ul>
      <li><strong>Standard Form:</strong> All constraints converted to equalities using Slack variables ($+\ s_i$ for $\le$) and Surplus variables ($-\ s_i$ for $\ge$). Artificial variables ($+ A_i$) added for $\ge$ and $=$ constraints.</li>
      <li><strong>Big-M Method:</strong> Penalize artificial variables in objective with $-M A_i$ (for Max) or $+M A_i$ (for Min). If an artificial variable remains in optimal basis with positive value $\implies$ <strong>Infeasible Solution</strong>.</li>
      <li><strong>Special Conditions in Simplex:</strong>
        <ul>
          <li><strong>Unbounded Solution:</strong> All constraint coefficients in pivot column are non-positive ($\le 0$) during minimum ratio test.</li>
          <li><strong>Multiple / Alternate Optima:</strong> Net evaluation row ($C_j - Z_j = 0$) for a <em>non-basic variable</em> at optimal tableau.</li>
          <li><strong>Degeneracy:</strong> Tie in minimum ratio test $\implies$ basic variable becomes zero in next iteration; may cause cycling.</li>
        </ul>
      </li>
      <li><strong>Duality Relationships:</strong> Primal Max $Z = CX$ subject to $AX \le B, X \ge 0 \iff$ Dual Min $W = B^T Y$ subject to $A^T Y \ge C^T, Y \ge 0$.
        <ul>
          <li>Number of dual variables = Number of primal constraints. Number of dual constraints = Number of primal variables.</li>
          <li>If primal has finite optimal solution, dual also has finite optimal solution and $\max Z = \min W$ (Strong Duality).</li>
          <li>If primal is unbounded $\implies$ dual is <strong>infeasible</strong>.</li>
        </ul>
      </li>
    </ul>

    <h2>2. Transportation &amp; Assignment Models</h2>
    <ul>
      <li><strong>Initial Basic Feasible Solution (IBFS):</strong>
        <ul>
          <li><strong>Vogel's Approximation Method (VAM):</strong> Computes penalties (difference between two lowest costs in each row and column). Selects row/col with largest penalty and allocates as much as possible to cell with lowest cost. Gives solution closest to optimal.</li>
          <li>Total allocations required for non-degeneracy $= m + n - 1$.</li>
        </ul>
      </li>
      <li><strong>Optimality Test (MODI / $u-v$ Method):</strong> Compute $u_i + v_j = c_{ij}$ for allocated cells. For unallocated cells: opportunity cost $\Delta_{ij} = c_{ij} - (u_i + v_j)$. Optimal if all $\Delta_{ij} \ge 0$ (for minimization).</li>
      <li><strong>Hungarian Assignment Method:</strong> Subtract row minimum from each row, then column minimum from each column. Draw minimum number of lines to cover all zeros. If lines $= n$, optimal assignment found. If not, subtract smallest uncovered element and add it to intersection elements.</li>
    </ul>

    <h2>3. Queuing Theory ($M/M/1 : \infty / \text{FIFO}$)</h2>
    <ul>
      <li>Arrival rate $\lambda$ (Poisson process), Service rate $\mu$ (Exponential service times). System stable only if traffic intensity $\rho = \frac{\lambda}{\mu} < 1$.</li>
      <li><strong>Probability of $n$ customers in system:</strong> $P_n = (1 - \rho) \rho^n$. Probability system is empty $P_0 = 1 - \rho$.</li>
      <li><strong>Average Number in System ($L_s$):</strong> $L_s = \frac{\rho}{1 - \rho} = \frac{\lambda}{\mu - \lambda}$.</li>
      <li><strong>Average Number in Queue ($L_q$):</strong> $L_q = L_s - \rho = \frac{\lambda^2}{\mu(\mu - \lambda)}$.</li>
      <li><strong>Little's Law:</strong> $L_s = \lambda W_s$ and $L_q = \lambda W_q$.</li>
      <li><strong>Average Waiting Time in System ($W_s$):</strong> $W_s = \frac{1}{\mu - \lambda}$.</li>
      <li><strong>Average Waiting Time in Queue ($W_q$):</strong> $W_q = \frac{\lambda}{\mu(\mu - \lambda)} = W_s - \frac{1}{\mu}$.</li>
    </ul>
    """
))

# ----------------- Topic 55: Work Study -----------------
MODULES[55] = ("📘 Module 55: Work Study, Method Study, Time Study & Ergonomics", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechanical Engineering (Topic 55)",
    "Motion Study, Therbligs, Standard Time Derivation, Work Sampling & Ergonomic Workplace Design",
    "Complete synthesis based on ILO Introduction to Work Study and Ralph M. Barnes covering recording techniques, performance rating, and relaxation allowances.",
    """
    <h2>1. Method Study &amp; Motion Economy</h2>
    <ul>
      <li><strong>Process Charts &amp; Standard Symbols:</strong>
        <ul>
          <li>$\bigcirc$ (Circle) = Operation (e.g., machining, assembly, chemical treatment).</li>
          <li>$\square$ (Square) = Inspection (checking dimensions, quality, count).</li>
          <li>$\Rightarrow$ (Arrow) = Transportation (movement of workers, materials, or equipment).</li>
          <li>$D$ (Semi-circle / D) = Delay (temporary stoppage, waiting for next operation).</li>
          <li>$\nabla$ (Inverted Triangle) = Storage (controlled storage requiring authorization to release).</li>
          <li>$\bigcirc$ inside $\square$ = Combined Operation and Inspection.</li>
        </ul>
      </li>
      <li><strong>Micro-Motion Study &amp; Therbligs:</strong> Frank and Lillian Gilbreth divided all human movements into 17 basic elemental motions termed <em>Therbligs</em> (e.g., Search, Select, Grasp, Transport Loaded, Hold, Release Load, Plan, Unavoidable Delay). Recorded via <strong>SIMO Chart</strong> (Simultaneous Motion Cycle Chart) using a wink counter ($1 \text{ wink} = 1/2000 \text{ min}$).</li>
    </ul>

    <h2>2. Work Measurement &amp; Time Study (Stopwatch Method)</h2>
    <ul>
      <li><strong>Observed Time ($OT$):</strong> Mean time recorded by stopwatch over several cycles.</li>
      <li><strong>Normal Time ($NT$):</strong> $NT = OT \times \left(\frac{\text{Performance Rating}}{100}\right) = OT \times RF$.
        <p>Performance rating adjusts for fast, normal (100%), or slow operator tempo (Westinghouse rating system considers Skill, Effort, Conditions, and Consistency).</p>
      </li>
      <li><strong>Standard Time ($ST$):</strong> $ST = NT + \text{Allowances}$.
        <p style="text-align:center; font-weight:bold;">$ST = NT \times (1 + \text{Allowance Fraction}) = \frac{NT}{1 - \text{Allowance on Standard Time}}$</p>
        Allowances cover Relaxation (Personal needs, fatigue), Interference, Contingency, and Policy.
      </li>
    </ul>

    <h2>3. Work Sampling (Tippett's Ratio Delay Method)</h2>
    <ul>
      <li>Statistical technique based on binomial distribution to estimate the proportion of time spent by workers or machines in various states (working vs idle).</li>
      <li><strong>Required Sample Size ($N$):</strong> For 95% confidence level ($2\sigma$) and relative accuracy $s$:
        <p style="text-align:center; font-weight:bold;">$N = \frac{4 (1 - p)}{s^2 \cdot p}$</p>
        where $p$ is the estimated proportion of time of the activity. For absolute accuracy $A$: $N = \frac{4 p (1 - p)}{A^2}$.
      </li>
    </ul>
    """
))

# ----------------- Topic 56: Maintenance & Reliability -----------------
MODULES[56] = ("📘 Module 56: Maintenance Engineering, Reliability & Failure Analysis", wrap_art(
    "UPSC ESE Prelims &bull; Paper-II Mechanical Engineering (Topic 56)",
    "Reliability Calculations, Bathtub Curve, MTBF/MTTF, Condition Monitoring & TPM / OEE",
    "Complete synthesis based on BS EN 13306, E.E. Lewis and Nakajima covering series/parallel reliability, vibration analysis, and Overall Equipment Effectiveness.",
    """
    <h2>1. Reliability Theory &amp; The Bathtub Curve</h2>
    <ul>
      <li><strong>Bathtub Curve Lifecycle Phases:</strong>
        <ol>
          <li><strong>Infant Mortality / Early Failure Phase:</strong> Decreasing failure rate ($d\lambda/dt < 0$). Caused by manufacturing defects, poor assembly, material flaws. Mitigated by <em>burn-in testing</em> and quality screening.</li>
          <li><strong>Useful Life / Random Failure Phase:</strong> Constant failure rate ($\lambda = \text{const}$, exponential distribution). Failures caused by random environmental shocks, overloads. Governed by $R(t) = e^{-\lambda t}$.</li>
          <li><strong>Wear-Out Phase:</strong> Increasing failure rate ($d\lambda/dt > 0$, Weibull / Normal distribution). Caused by fatigue, corrosion, erosion, mechanical wear. Mitigated by preventive component replacement.</li>
        </ol>
      </li>
      <li><strong>Key Metrics (Constant Failure Rate $\lambda$):</strong>
        <ul>
          <li><strong>Mean Time To Failure (MTTF):</strong> For non-repairable systems: $\text{MTTF} = \int_0^\infty R(t)\,dt = \frac{1}{\lambda}$.</li>
          <li><strong>Mean Time Between Failures (MTBF):</strong> For repairable systems: $\text{MTBF} = \text{MTTF} + \text{MTTR} \approx \frac{1}{\lambda}$.</li>
          <li><strong>Inherent Availability ($A_i$):</strong> $A_i = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$.</li>
        </ul>
      </li>
    </ul>

    <h2>2. System Reliability Configurations</h2>
    <div class="table-responsive">
      <table style="width:100%; border-collapse:collapse; margin-bottom:18px;">
        <tr style="background:#f1f5f9; text-align:left;"><th style="padding:10px; border:1px solid #cbd5e1;">Configuration</th><th style="padding:10px; border:1px solid #cbd5e1;">System Reliability ($R_s$)</th><th style="padding:10px; border:1px solid #cbd5e1;">Key Behavior</th></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Series System</strong> (All components must function)</td><td style="padding:10px; border:1px solid #cbd5e1;">$R_s = \prod_{i=1}^n R_i = R_1 \cdot R_2 \dots R_n$</td><td style="padding:10px; border:1px solid #cbd5e1;">$R_s < \min(R_i)$. Overall failure rate $\lambda_s = \sum \lambda_i$. Adding components degrades system reliability.</td></tr>
        <tr><td style="padding:10px; border:1px solid #cbd5e1;"><strong>Parallel System</strong> (System functions if at least 1 works)</td><td style="padding:10px; border:1px solid #cbd5e1;">$R_s = 1 - \prod_{i=1}^n (1 - R_i)$</td><td style="padding:10px; border:1px solid #cbd5e1;">$R_s > \max(R_i)$. Redundancy significantly increases system reliability.</td></tr>
      </table>
    </div>

    <h2>3. Total Productive Maintenance (TPM) &amp; OEE</h2>
    <ul>
      <li>TPM was introduced by Seiichi Nakajima in Japan. It relies on <strong>8 Pillars</strong>, with <em>Jishu Hozen</em> (Autonomous Maintenance by machine operators) at its core.</li>
      <li><strong>Overall Equipment Effectiveness (OEE):</strong>
        <p style="text-align:center; font-weight:bold; font-size:16px;">$\text{OEE} = \text{Availability} (A) \times \text{Performance Rate} (P) \times \text{Quality Rate} (Q)$</p>
        <ul>
          <li><strong>Availability:</strong> $\frac{\text{Operating Time}}{\text{Planned Production Time}} = \frac{\text{Planned Time} - \text{Downtime Losses}}{\text{Planned Time}}$ (Losses: Equipment breakdowns, setup/adjustments).</li>
          <li><strong>Performance Rate:</strong> $\frac{\text{Ideal Cycle Time} \times \text{Total Count Produced}}{\text{Operating Time}}$ (Losses: Idling, minor stoppages, reduced speed).</li>
          <li><strong>Quality Rate:</strong> $\frac{\text{Good Units Produced}}{\text{Total Units Started}}$ (Losses: Process defects, rework, startup scrap).</li>
          <li><strong>World-Class Benchmark:</strong> $A \ge 90\%$, $P \ge 95\%$, $Q \ge 99.9\% \implies \mathbf{\text{OEE} \ge 85\%}$.</li>
        </ul>
      </li>
    </ul>
    """
))

def main():
    app = create_app()
    with app.app_context():
        for tid in [52, 53, 54, 55, 56]:
            if tid in MODULES:
                title, html = MODULES[tid]
                ex = TopicContent.query.filter_by(topic_id=tid, title=title).first()
                if ex:
                    ex.content_value = html
                    ex.content_type = 'text'
                    ex.item_order = 1
                    ex.deleted_at = None
                else:
                    db.session.add(TopicContent(topic_id=tid, title=title, content_type='text', content_value=html, item_order=1))
        db.session.commit()
        print("Successfully loaded dedicated high-yield modules for Industrial Engineering (Topics 52-56) into app.db!")

if __name__ == '__main__':
    main()
