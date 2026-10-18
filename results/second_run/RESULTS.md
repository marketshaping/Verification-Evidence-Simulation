# Second run: first evidence-based ranges (18 October 2026)

**Status: still mostly scenarios. Do not cite these as findings.** Compared with the first run, three inputs now come from coded rows or outside analogues instead of guesses. Everything else is unchanged (p = 10, a = 50, 2,000 draws per cell, same seed).

## What changed in `data/placeholder_ranges.csv`

| Instrument | Parameter | First run | Now | Basis |
|---|---|---|---|---|
| CI-02 Third-party verifiers | detection | 0.10 / 0.40 / 0.70 (scenario) | 0.20 / 0.35 / 0.60 (analogue) | Thorough tax audits find about a third of evaded income (see below) |
| CI-03+04 Attested metering | metering noise | 1% / 3% / 10% (placeholder) | 0.3% / 1% / 2.8% (analogue) | AN-04: IAEA plutonium measurement-uncertainty targets 0.28–2.8% |
| CI-03+04 Attested metering | false alarm | 1% / 2% / 5% (placeholder) | 1% / 1% / 3.1% (analogue) | AN-04: about 1% for accountancy alarms; CI-04: 3.06% per 30 s window for a GPU telemetry classifier in the lab |

Not changed: attestation detection (CI-03) and satellite concealment (CI-05). No measured rate exists for either. The notes in the ranges file now record what was searched.

## Results, no cap, N = 200

| Instrument | Audit rate needed (median, 10th–90th) | Hidden if audited yearly | Audit rate for under 5% hidden |
|---|---|---|---|
| CI-02 Third-party verifiers | 0.53 (0.40–0.73), was 0.50 | 13% of risk-weighted compute, was 17% | above 1, unchanged |
| CI-03+04 Attested metering | 0.30 (0.24–0.43), unchanged | **1.3%, was 3.9%** | **0.45, was 0.70** |
| CI-05 Satellite imagery | 0.41 (0.28–0.72), unchanged | 1.3%, unchanged | 0.70, unchanged |

**1. The under-reporting floor from metering noise falls from about 4% to about 1%.** This happens because the noise range is now tied to nuclear accountancy (central 1%) instead of a made-up 3%. The floor is still roughly the size of the metering noise. So it remains a statement about the noise assumption, and the transfer from plutonium to compute is uncertain: compute is used up, so it can't be re-measured the way a stock of material can.

**2. CI-02 barely moves.** The analogue range is narrower than the old guess but has a similar centre. Third-party verification still needs an audit rate of about 0.5 to deter large misreporting, and it leaves about an eighth hidden even with yearly checks, mainly because of verifier collusion.

**3. The deterrence threshold is unchanged where detection is unchanged.** Detection is still the input that matters most, and CI-03 and CI-05 under concealment remain pure scenarios.

## Detection-rate evidence found, by instrument

| Instrument | Best evidence | Rate | Type | Transfer |
|---|---|---|---|---|
| CI-05 Satellite imagery | Clymer 2025 | 98.6% at 1% false positives | Lab test, unconcealed US sites, about 230 images | High for unconcealed sites; none for concealed ones |
| CI-04 Metering (workload detection) | Rahman & Tajdari 2026 (ICML TAIGR workshop), NVML telemetry, 9 GPU models, 1,404 runs | 98.2% overall, 3.06% false positives; 92–95% on unseen evasion strategies; **43–87% against white-box evasion** (worst: white-box LoRA, 42.6%) | Lab, single node of at most 8 GPUs, telemetry assumed untampered | Medium: it detects whether training happens, not how much compute is under-reported |
| CI-04 Metering (power side channel) | Gargiulo (from Vir's row; arXiv 2609.00309, not yet checked) | 97% accuracy on 930 traces; diluted LoRA caught 48–88%, 98% or more with a rescue rule | Lab | Medium |
| CI-04 analogue | Nuclear material accountancy (AN-04) | No detection rate. Noise 0.28–2.8%, false alarm about 1% | Published targets | Medium |
| CI-02 collusion (not detection) | Dyck, Morse & Zingales 2010 and 2024 | External auditors make only 10.5% of fraud detections (216 cases, 1996–2004). About 1/3 of frauds are ever detected, by anyone, over their lifetime | Case data; natural experiment (Arthur Andersen collapse) | Not a per-audit rate. Evidence that checkers hired by the checked firm catch little, which bears on CI-02 collusion |
| CI-02 analogue | IRS random audits (NRP); HMRC tax gap | IRS scales detected evasion up about 3× (about 33% detected); HMRC multipliers imply 33–100%, central 52–79% | Detection-controlled estimation; data matching | Medium |
| CI-03 Attestation | None | No measured rate. Defeat evidence only: TEE.fail key extraction for under $1,000; 198/198 seals defeated, 15% undetectable even forensically (AN-03) | Lab attacks | n/a |
| CI-05 under concealment | None | Untested. Covert nuclear sites were found through intelligence tips, not imagery alone (AN-01) | Qualitative | n/a |

Lead not followed up: Listner, Rezniczek, Stein, Niemeyer & Canty (IAEA Symposium 2014), "Quantifying Detection Probabilities for Proliferation Activities in Undeclared Facilities". The abstract proposes methods (analogy, Bayes, frequentist, process) but reports no numbers.

## Correction to how detection evidence should be read (added 18 Oct)

**Each instrument has its own audit rate, and that changes the detection bar.** Deterrence needs ρ·d ≥ p/a. The runs above apply one swept ρ to every instrument, but the evidence fixes ρ for most of them:

| Instrument | Natural audit rate | Detection needed (p/a = 0.2) | What the evidence says |
|---|---|---|---|
| CI-02 Third-party verifiers | 1: every annual report is verified (AN-02) | 0.20 | Non-colluding checker: about 0.33 (tax analogue), so it passes. Colluding: 0.33 × 0.25 ≈ 0.08, so it fails. The weakness is capture, not detection |
| CI-05 Satellite imagery | About 1: all of China imaged in about a month (Clymer, back-of-envelope) | 0.20 | Unconcealed 0.986, so it passes. It fails only if concealment cuts detection by more than about 80%, or the site is under about 10 MW |
| CI-03+04 Attested metering | About 1 if telemetry streams continuously; below 1 for Shavit-style sampled inspection | 0.20 plus the noise band | Depends on whether attestation holds. Likely for domestic labs; doubtful against a state (TEE.fail, under $1,000) |

**So the evidence question gets easier.** It changes from "what is d?" to "is d above about 20%, and which evasions push it below?". That is a bound, which the coding rules allow ("no forced point estimate").

**The 20% has three placeholders hidden in it.** The full condition is ρ · d · P(sanction | detected) · a ≥ p.
- **a/p = 5 is a placeholder.** In a real permit market (Joel's setting) p is the permit price. Under the US state laws there is no permit price: the gain from misreporting is avoided compliance cost or delay. So comparing SB 53's or RAISE's caps with training-run costs (as an earlier draft did) doesn't measure a/p. Non-fine costs (reputation, executive liability, loss of contracts) also enter a. Whether fines alone deter is open.
- **P(sanction | detected) is taken as 1.** In practice detection leads to referral, dispute and maybe a fine. Iran's IAEA findings led to Board referrals, not penalties.
- **The CI-02 collusion multiplier (0.25) is a scenario.** So "CI-02 fails through capture" is driven by an assumption. The evidence (auditors make 10.5% of fraud detections) points the same way but doesn't give the number.

**Metering noise caveat.** A chip's cycle counter isn't a noisy physical assay the way plutonium measurement is. The gap between declared and metered compute comes mostly from accounting conventions (what counts as a training FLOP, precision, utilisation), so the AN-04 range is a stand-in and could be too high or too low.

## Limits of the detection-threshold framing (added 18 Oct)

1. **Lab rates are averages over the evasions tested. A strategic evader picks the weakest one,** so the relevant d is the worst feasible case, not the mean. For CI-04 that is the white-box LoRA case (42.6%), not 98.2%. For CI-05 it's whichever concealment is cheapest, and that is untested.
2. **Combining instruments is a choice of route, not independent draws.** The evader picks a route that beats the whole set: small sites to dodge imagery, then defeat attestation so metering is blind. Since CI-04 relies on CI-03, they fail together. Multiplying detection probabilities would overstate the combined rate.
3. **Satellite d is a pipeline, not a classifier score:** imaged × flagged × candidate inspected × inspection allowed × confirmed. At a 1% false-positive rate over thousands of industrial sites, flagged candidates run into the hundreds (Clymer plans for a few hundred inspections). So inspection capacity and access, not the 98.6%, set end-to-end detection.
4. **Expected fines are the wrong lens for international verification.** CI-05, and CI-03 against a state, matter between states, where the sanction is treaty breakdown or worse, not a fine, and the gain is strategic, not permit savings. There, the question is **timeliness**: detection before a dangerous run finishes, compared with how long a run takes. The fine-based model fits the domestic instruments (CI-02, CI-04 domestic). Report the international ones on timeliness.
5. **The metering floor is about permit revenue, not safety.** Shaving 1% off a declared run doesn't hide a run above a threshold. What matters for safety is whether a **whole** run can be hidden, which is the binary case (Rahman's numbers; CI-05).
6. **Frontier scale cuts against small-site evasion.** Sites under about 10 MW (about 7–10k H100s at about 1–1.4 kW each, all-in) are mostly missed. But a frontier run needs on the order of 100k GPUs, so it would have to be split across 10 or more hidden sites with long-distance training. That's possible but costly. Detection should depend on run size, not just facility size.

## Still most needed
1. Any measured rate for attestation being defeated in the field, or a red-team rate.
2. Imagery detection against deliberate concealment.
3. A direct compute-metering error figure, to replace the plutonium analogue for noise.
