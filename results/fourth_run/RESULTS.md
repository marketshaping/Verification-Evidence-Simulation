# Fourth run: the combined regime (20 October 2026)

**Status: still mostly guesses. Don't cite these as findings.** Same inputs as the third run, plus `data/regime.csv` (route costs, tamper detection, the meter's catch rate) and two new worst-case rows. Everything the third run produced is reproduced here exactly (`headline.csv`, `summary.csv`, `sweep.csv`, `sensitivity.csv`, `meter_noise.csv`), so this file covers only what's new. Rerun with `python -m spar_sim.run --out results/fourth_run`.

## What's new

Until now each instrument was judged on its own. Real regimes run several at once, and a cheater picks **one way of hiding** that gets past all of them:

1. **Under-report on monitored chips.** The verifier and the meter can catch it.
2. **Defeat attestation, then under-report.** The meter is blind. An inspection may find the tampering, and the verifier is partly fooled by the fake meter data.
3. **Use a hidden site.** Only the satellite, plus a verifier that notices gaps, can see it. Setting it up is costly.

The fine has to deter the cheapest route. See `docs/MODEL.md`.

## Result 1: multiplying catch rates understates the fine needed (Figure 5, `regime.csv`)

Fine needed, as a multiple of the gain from hiding (median, 10th–90th percentile):

| | Checks multiplied | Cheater picks a route | Ratio | Deterred at 5×, route choice |
|---|---|---|---|---|
| Main, honest verifier | 1.1× (1.0–1.2) | **2.0×** (1.5–3.0) | 1.8 | 99.8% of draws |
| Main, lenient verifier | 1.1× (1.1–1.4) | **2.5×** (1.7–4.2) | 2.2 | 95% |
| Worst case, honest verifier | 1.4× (1.3–1.7) | **4.4×** (2.9–7.4) | 3.0 | 63% |
| Worst case, lenient verifier | 1.8× (1.5–2.3) | **6.2×** (4.0–10.6) | 3.4 | 27% |

Both columns use the same catch rates. Multiplying treats the regime as if every check saw every cheater, which makes it look 2–3 times stronger than it is. With multiplication, a 5× fine deters in every draw, even in the worst case. With route choice it deters in only 27–63% of worst-case draws.

## Result 2: the weakest link sets the fine (Figure 6, `regime_instruments.csv`)

Which route sets the fine (honest verifier):

| | Monitored chips | Defeat attestation | Hidden site |
|---|---|---|---|
| Main | 4% | **59%** | 38% |
| Worst case | 0% | 11% | **89%** |

Cheaters almost never under-report on monitored chips, because the verifier and the meter together catch that route well. So:

- **A better meter barely helps.** A perfect meter lowers the median fine needed in only 4% of main draws, and in no worst-case draws.
- **Tamper detection matters in the main ranges.** Perfecting it cuts the median from 2.0× to 1.6×. Removing it raises the median to 4.0×.
- **Satellites are load-bearing.** Without them a hidden site is nearly free, and the fine needed jumps to about 14×; with a lenient verifier, about 52×. In the worst case, perfect imagery cuts the median from 4.4× to 2.5×.
- **The verifier is the only instrument on every route**, so improving it always helps a little (main: 2.0× → 1.5×).

## Result 3: the only measured input matters least (`regime_sensitivity.csv`)

Rank correlation of each input with the fine needed (honest verifier):

| | Main | Worst case |
|---|---|---|
| Satellite catch rate when sites are hidden (guess) | 0.45 | **0.75** |
| Chance tampering is found (guess) | **0.43** | 0.07 |
| How often the meter is checked (guess) | 0.35 | 0.03 |
| Cost of a hidden site (guess) | 0.18 | 0.37 |
| Verifier sees a hidden site (guess) | 0.05 | 0.33 |
| Verifier catch rate (stand-in) | 0.20 | 0.18 |
| **Meter catch rate, attestation intact (measured)** | **0.03** | 0.04 |

The meter's catch rate is the one combined-regime input with a measured value (Rahman & Tajdari's 98%), and it has almost no effect. A cheater who can defeat attestation or use a hidden site doesn't go near the meter. **Evidence on how well metering works is worth less than evidence on how easily it can be bypassed.**

## Limits
- Route costs, tamper detection and the verifier factors are all guesses (see `data/regime.csv`).
- Within a route, checks are treated as independent. If inspectors who look for tampering are also the ones checking the meter, they may fail together.
- One cheater, one route. A cheater could also split compute across routes.
- Hidden-site cost doesn't grow with run size yet. A frontier run would need 10 or more small sites (CI-05 notes), so this probably understates the cost for large runs. The planned site-size step will fix this.
- Pass/fail only. Small under-reports inside the meter's error band (Figure 2 in the third run) come on top.

## What this means for evidence collection
1. **CI-05:** satellite detection against deliberate concealment. This matters most in the worst case.
2. **CI-03:** how often tampering is found in practice, not just whether attestation can be broken.
3. **CI-05 / AN-01:** the cost of building and hiding a site, and how it grows with size.
4. **CI-02:** whether verifiers notice off-book capacity (chip purchases, power contracts).
5. **CI-04:** a better meter catch rate is low priority.
