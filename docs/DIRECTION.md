# Simulation: what it shows so far and what would help most

*Nat, 20 October 2026. For the team. Based on the third run; most inputs are still guesses.*

## The short version

1. **At the rate each instrument already checks (about once a year), a fine of 2–3× the gain from hiding is enough**, if the checker is honest and the cheater doesn't know how to beat it.
2. **The worst cases are what matter.** A lenient verifier needs a fine about 10× the gain. A cheater who beats the metering detector needs about 5×. A deliberately hidden site needs about 9×. None of these has a measured rate.
3. **The fine and whether it's actually imposed matter as much as detection.** Nobody on the team is coding either. This affects the midterm's line that "detection is the parameter that matters most": the model now says detection is one of three things that matter, alongside the fine-to-gain ratio and the chance of punishment.

## What the evidence team could look for

Ranked by how much each would change the answer (Figure 4 in `results/third_run/`):

| # | What | Instruments | Where it might be found |
|---|---|---|---|
| 1 | **Fine relative to gain** in an analogue regime | All | EU ETS excess-emissions penalty against the carbon price; IRS penalties against evaded tax |
| 2 | **How often detection leads to punishment** | All | ETS penalties actually imposed; IAEA findings → Board referrals; IRS assessments collected |
| 3 | **How often verifiers go easy** | CI-02 | Accreditation withdrawals (AN-02 already has 4); audit findings later overturned |
| 4 | **Imagery against deliberate concealment** | CI-05 | Nuclear cases (AN-01); any red-team or camouflage study |
| 5 | **Real compute-meter error** | CI-04 | Cloud billing disputes; GPU counter accuracy studies |
| 6 | **Whether attestation holds against a motivated lab** | CI-03 | Red-team rates, not just proofs of concept like TEE.fail |

**Suggested codebook change:** add two fields to each analogue row: *typical fine relative to the gain from cheating*, and *share of detected violations that led to a penalty*. Even a rough range helps, because the model currently assumes 5× and 100%.

## Proposed next steps for the simulation (to 14 December)

- **By 9 November:** load the second-coder rows and rerun. Agree the worst-case values with the coders, because they drive the results.
- **By 24 November:** combine instruments into one regime, where breaking attestation also blinds metering, and let CI-05 detection depend on site size.
- **By 14 December:** report the between-country instruments (CI-05, CI-03 against a state) on **timeliness**, meaning whether cheating is caught before a run finishes, rather than on fines. Final figures and a single summary table: instrument, evidence status, fine needed.

## Questions for the team

1. Can coders add the two sanction fields to analogue rows before 9 Nov?
2. Who agrees the worst-case values? I'd suggest each instrument's coder pair.
3. Should the midterm say "detection is one of three inputs that matter most" instead of "the parameter that matters most"?
