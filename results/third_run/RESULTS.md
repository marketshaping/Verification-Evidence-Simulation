# Third run: fine needed at each instrument's normal checking rate (20 October 2026)

**Status: still mostly guesses. Don't cite these as findings.** The inputs are the same as the second run, plus each instrument's normal checking rate, a worst-case scenario and ranges for the fine and the chance of punishment. Every input's status is in `inputs/`. Rerun with `python -m spar_sim.run --out results/third_run` (seed 20261014, 2,000 draws).

## The question has changed

Runs 1 and 2 asked what audit rate deters cheating, using one rate for every instrument. But most instruments already check about once a year: every verifier report is checked, satellites can image a whole country in a month, and metering can stream continuously. So the useful question is: **at the rate each instrument already checks, how big must the fine be, relative to what a developer gains by hiding, for honest reporting to pay?**

## Headline (Figure 1, `headline.csv`)

Fine needed as a multiple of the gain, median (10th–90th percentile over draws), 200 developers:

| Instrument | Checked per year | Main ranges | Worst case: cheater picks the weakest route |
|---|---|---|---|
| CI-02 Third-party verifiers, honest verifier | 1 | **2.6×** (2.0–3.6) | 2.6× (unchanged) |
| CI-02, lenient verifier | 1 | **9.8×** (p90 16.7×) | 9.5× (p90 16.1×), but three times as many lenient verifiers |
| CI-03+04 Attested metering | 0.78 | **2.1×** (1.4–3.5) | **4.8×** (3.3–8.5) |
| CI-05 Satellite imagery | 0.86 | **2.5×** (1.6–4.7) | **9.4×** (5.3–18.6) |

At the main assumption of a fine 5× the gain:

| | Draws where an honest-checked developer is deterred | Compute hidden (mean) | Fine needed for under 5% hidden |
|---|---|---|---|
| CI-02, main | 100% | 12% (lenient verifiers) | 11.7× |
| CI-03+04, main | 98% | 2.2% (mostly inside the meter error) | 4.0× |
| CI-05, main | 92% | 3.2% | 4.6× |
| CI-02, worst case | 100% | 29% | 15.8× |
| CI-03+04, worst case | 53% | 19% | 8.6× |
| CI-05, worst case | 7% | 37% | 18.5× |

**What this says.** With honest checkers and the main ranges, a modest fine (2–3× the gain) is enough at normal checking rates. The problems are all in the worst cases. A lenient verifier needs a fine about 10× the gain. A cheater who beats the metering detector needs about 5×. A deliberately hidden site needs about 9×. So the result turns on **how often the worst cases happen**, and none of them has a measured rate.

## Small cheating from meter error (Figure 2)

With checks every year and a fine 5× the gain, developers still under-report by about the size of the meter error (about 1% hidden at 1% error, with a 1% false-alarm rate). A higher false-alarm rate means a tighter alarm threshold and less room: about 0.75% at 3%. Bigger fines don't remove this. It's a statement about accuracy and permit revenue, not about hiding a dangerous run.

## Few large vs many small developers (Figure 3)

Unchanged from earlier runs. With no cap, market structure makes no difference. With a flat cap, 4 large developers hide the maximum at every checking rate, because their gain is bigger than the cap. 200 small developers behave as if there were no cap. Real flat caps: CA SB 53, $1m per violation; NY RAISE, $1m then $3m. The EU AI Act's cap scales with turnover, so it behaves like no cap.

## Which unknowns matter most (Figure 4, `sensitivity.csv`)

All uncertain inputs drawn together. Fine ranges from 1–20× the gain and chance of punishment from 0.3–1. Outcome: share of compute hidden and not caught.

| Instrument | Top three (|rank correlation|) |
|---|---|
| CI-02 | fine / gain 0.54 (guess), share of lenient verifiers 0.34 (guess), catch rate 0.26 (stand-in) |
| CI-03+04 | meter error 0.69 (stand-in), fine / gain 0.41 (guess), how often checked 0.27 (guess) |
| CI-05 | fine / gain 0.44 (guess), effect of hiding the site 0.32 (guess), chance of punishment 0.21 (guess) |

**This qualifies the claim that detection matters most.** Once checking rates are realistic, the **size of the fine relative to the gain** and **whether caught developers are actually punished** matter as much as the catch rate or more. The evidence team isn't coding either of them. The one measured catch rate (Clymer's 98.6% for unhidden sites) barely matters, because what limits CI-05 is concealment, not the classifier.

The ranking depends on how wide each range is. Fine / gain ranks high partly because its range (1–20×) is wide. That's honest, since nobody has a figure for it, but a coded range could change the order.

## Reproducibility

`summary.csv` and `sweep.csv` (one shared audit rate, as in runs 1 and 2) match `second_run` exactly for the same seed. The new inputs are drawn after the old ones.

## Still missing, in order of what would change the answer most
1. **Fine relative to gain** in any analogue regime (EU ETS excess-emissions penalty against the carbon price; IRS penalties against evaded tax).
2. **How often detection leads to punishment** (ETS penalties actually imposed; IAEA findings → referrals; IRS assessments collected).
3. **How often verifiers are lenient** (CI-02: accreditation withdrawals, findings later overturned).
4. **Imagery against deliberate concealment** (CI-05).
5. **Real compute-meter error** (CI-04), to replace the plutonium stand-in.
6. **Whether attestation holds against a motivated lab** (CI-03: red-team rates, not just proofs of concept).
