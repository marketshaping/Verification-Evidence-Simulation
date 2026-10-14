# First run: placeholder ranges (13 October 2026)

**Status: placeholder ranges. These are not results to cite.** Most inputs are scenarios (see `data/placeholder_ranges.csv`, column `status`). The point of this run is to show the pipeline from coded rows to model output works end to end. It also shows which parameters the answer is most sensitive to, so coders know where evidence matters most.

Settings: permit price p = 10, penalty slope a = 50 (baseline defaults), 2,000 parameter draws per cell, total industry compute held fixed. N = 4 means four large developers. N = 200 means many small ones.

Instruments run: the three with coded rows by 12 October.

| Instrument | Margin | What drives detection here | Evidence or scenario |
|---|---|---|---|
| CI-02 Third-party verifiers | Evaluation (risk class) | Detection 0.10–0.70, verifier collusion 0–30% | Scenario. AN-02 gives no detection rate |
| CI-03+04 Attested compute metering | Compute | Attestation holds 0.30–0.95; metering noise 1–10%; false alarms 1–5% | Scenario. CI-04 rows not in yet |
| CI-05 Satellite imagery | Compute (undeclared site) | 98.6% unconcealed × concealment factor 0.1–0.9 | Unconcealed rate is evidence (Clymer 2025). Concealment is a scenario |

## Four things the run shows

**1. The baseline audit rate of 0.25 deters large evasion for none of the three instruments.** The audit rate needed is p / (d × a), so it depends only on detection (median, with the 10th–90th percentile across draws):

| Instrument | Audit rate needed |
|---|---|
| CI-03+04 attested metering | 0.30 (0.24–0.43) |
| CI-05 satellite imagery | 0.41 (0.28–0.72) |
| CI-02 third-party verifiers | 0.50 (0.36–0.87) |

The baseline's 0.25 assumed detection of 0.8. None of the placeholder ranges centre that high once tampering or concealment is allowed for. This is why detection is the parameter where evidence matters most.

**2. Noisy measurement leaves a floor of under-reporting that audits cannot remove.** With metering noise, small under-reports stay inside the alarm threshold. Even if every developer is audited every year, the typical developer still hides about 3.5% of its compute, and about 4% of industry compute goes unreported. Binary instruments (imagery, third-party verification) have no such floor. This is the "shaving" result again, now per instrument. The size of the floor is set by metering noise and the false-alarm setting, so those two CI-04 fields matter.

**3. Third-party verification is weak even with an audit every year.** CI-02 is checked annually, as EU ETS verification is (AN-02). Even then, about 17% of the risk-weighted compute that high-risk developers could hide stays misreported on average. The cause is low detection draws and collusion with verifiers the developer hires. The range is very wide (10th–90th percentile: 0–100% in some cells) because detection is entirely a scenario.

**4. Few or many developers only matters if the penalty cap is flat.**
- **No cap:** the curves for N = 4 and N = 200 lie on top of each other, because each developer's choice doesn't depend on its size. What differs is cost: auditing everyone yearly takes 4 audits with 4 developers and 200 with 200.
- **Flat statutory cap** (set at 5% of the industry's yearly permit bill): with four large developers, the cap is small relative to what each could save. They hide the maximum (40%) **at every audit rate** for metering and imagery, and misreport risk class every time under CI-02. With 200 small developers the cap rarely binds and results barely change.
- A cap that scales with turnover behaves like no cap. So whether fines scale with developer size is the policy detail that decides whether a few-lab world is enforceable. This makes the "fragile with four labs" point from the parameter table concrete.
- **Existing AI rules do both, which makes this a live issue, not a hypothetical.** The two US state frontier-AI laws use flat caps: California SB 53 caps penalties at $1 million per violation, and New York's RAISE Act (N.Y. Gen. Bus. Law § 1427, as amended) caps them at $1 million for a first violation and $3 million after that. The amendment cut these from $10 million and $30 million, and enforcement is delayed to January 2027. The EU AI Act's cap for general-purpose AI providers scales with size: 3% of worldwide turnover or €15 million, whichever is higher (Art. 101). The US caps are tiny next to a frontier lab's compute spend, so they sit far below the flat cap used in this run. If anything the run understates the problem under US state law.

Figure: `fig_evasion_vs_audit_rate.png`. Top row: no cap. Bottom row: flat cap. In the top row the two N lines overlap.

## Not yet in the model
- Timeliness, audit cost and shared failure are recorded in the ranges file but not used.
- Detection doesn't vary with facility size for CI-05. In reality sites under about 10 MW are mostly missed, which invites splitting into small sites.
- Instruments run one at a time. Combining them, including correlated failure when CI-03 is defeated, is the next step.
- Developers don't react to each other (no racing), and a regulator can't target audits.
- Penalty on false alarms for compliant developers.

## What would most change these numbers
1. Any measured detection rate under adversarial conditions, for any instrument. Detection drives point 1.
2. CI-04 metering noise and false-alarm setting. These set the floor in point 2.
3. Penalty caps, now answered for three laws (see point 4). Next step: put the US caps in model units by comparing them with frontier training-run costs, so the cap scenario uses real figures.
