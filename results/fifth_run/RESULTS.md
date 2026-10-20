# Fifth run: run size (20 October 2026)

**Status: still mostly guesses. Don't cite these as findings.** This run uses the same inputs as the fourth, plus four new rows in `data/regime.csv`: how imagery detection depends on site power, power per GPU, and the cost of each extra hidden site. Everything the fourth run produced is reproduced here exactly, so this file covers only what's new. To rerun: `python -m spar_sim.run --out results/fifth_run`.

## What's new

In the fourth run, a hidden site cost the same and was equally easy to spot whatever the size of the run. Now:

- A run needs about 1.2 kW per GPU, so 10,000 GPUs draw about 12 MW.
- The cheater can split the run across several hidden sites. Imagery finds half of sites at 3–10 MW, and fewer below that. Every miss in Clymer's test was under 4 MW.
- Each extra site costs 1–8% of the gain, because training across sites is slower and needs links between them.
- The cheater picks the number of sites that is hardest to deter.

A compute threshold such as 10²⁶ FLOP can be reached quickly on a big cluster or slowly on a small one. Figure 7 shows both: run size along the bottom, and the time to reach 10²⁶ FLOP along the top (H100s at 40% utilisation).

## Result: small, slow runs are the hard ones to deter (Figure 7, `size.csv`)

Fine needed, as a multiple of the gain from hiding (median), with an honest verifier:

| Hidden run | Power | Time to 10²⁶ FLOP | Main ranges | Worst case |
|---|---|---|---|---|
| 1,000 GPUs | 1 MW | 8 years | 11× | 13× |
| 3,000 GPUs | 4 MW | 2.7 years | **7×** | **10×** |
| 10,000 GPUs | 12 MW | 10 months | 2.5× | 5.3× |
| 30,000 GPUs or more | 36 MW+ | 3 months or less | **2.0×** | **4.3×** |

- **A frontier-scale run can't hide by splitting.** Above about 15,000 GPUs the cheater uses one site, because splitting into enough sub-4 MW sites would cost more than it saves. The fine needed then settles at about the fourth run's values: 2.0× (main ranges) and 4.3–4.4× (worst case; the small difference comes from different random draws).
- **A small, slow run can.** At 3,000 GPUs the run fits in a few sites that imagery mostly misses. With middle-range inputs it needs a fine of about 7×; in the worst case, about 10×. A 5× fine stops it only above about 4,600 GPUs (main ranges, 1.8 years to 10²⁶ FLOP), or above about 12,000 GPUs (worst case, 8 months).
- **So satellites protect against fast runs and leave slow ones to other checks.** Slow runs have to be caught by checks that don't rely on seeing a site: verifiers, tracking where chips go (not yet in the case register), and cloud reporting (CI-01, no coders yet).

## Limits
- The 3–10 MW midpoint and the 1–8% cost per site are guesses anchored on Clymer's misses. Neither has a measured value.
- Only the hidden-site route depends on size. The chance a verifier notices off-book chip purchases doesn't yet grow with the number of chips.
- Slow runs face costs the model leaves out. A model trained over 3 years may be out of date when it's finished, so the real gain from hiding a slow run is probably smaller than assumed.
- The time axis assumes H100s at 40% utilisation. Newer chips shorten all the times.

## What this means for the team
1. **CI-05:** detection rates by site size, not one overall rate. Clymer's misses are the only data so far.
2. **Cost of training across sites:** any figures on cross-site training efficiency would pin down the per-site cost.
3. **The paper's framing:** a compute threshold says nothing about how fast the compute is used. If a rule is meant to cover slow runs, it needs checks that don't rely on seeing a site: verifiers, chip tracking, and cloud reporting (CI-01).
