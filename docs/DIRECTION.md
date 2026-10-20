# Simulation: what it shows so far and what would help most

*Nat, 20 October 2026. For the team. Based on the third to fifth runs; most inputs are still guesses.*

## The short version

1. **At the rate each instrument already checks (about once a year), a fine of 2–3× the gain from hiding is enough**, if the checker is honest and the cheater doesn't know how to beat it.
2. **The worst cases are what matter.** A lenient verifier needs a fine about 10× the gain. A cheater who beats the metering detector needs about 5×. A deliberately hidden site needs about 9×. None of these has a measured rate.
3. **The fine and whether it's actually imposed matter as much as detection.** Nobody on the team is coding either. This affects the midterm's line that "detection is the parameter that matters most": the model now says detection is one of three things that matter, alongside the fine-to-gain ratio and the chance of punishment.

## Instruments together, not one at a time (fourth run)

A cheater picks **one way of hiding** past all the checks: under-report on monitored chips, defeat attestation and then under-report, or use a hidden site. The fine has to deter the cheapest of these.

- **Multiplying catch rates makes a regime look 2–3 times stronger than it is.** With route choice, the fine needed is 2.0× (main ranges) to 4.4× (worst case), against 1.1× and 1.4× when the catch rates are multiplied.
- **Cheaters almost never go past the meter.** They defeat attestation (main ranges) or use a hidden site (worst case). A perfect meter barely changes anything.
- **Satellites are load-bearing.** Without them, the fine needed jumps to about 14×.
- **The only measured input, the meter's 98% catch rate, has the least effect on the result.** Evidence on how instruments are bypassed is worth more than evidence on how well they work when nobody tries to get around them.

## Small, slow runs are the hard ones to deter (fifth run)

A 10²⁶ FLOP run takes about a month on 100,000 GPUs, or about 2.7 years on 3,000 GPUs in a few small sites that imagery mostly misses.

- **Fast, frontier-scale runs can't hide by splitting.** Above about 15,000 GPUs, splitting into enough small sites costs more than it saves. A fine of about 2× the gain is enough with middle-range inputs, and 4.3× in the worst case.
- **Slow runs can hide.** At 3,000 GPUs they need a fine of about 7× (middle-range inputs) to 10× (worst case).
- **So satellites cover fast runs, and slow runs need other checks:** verifiers, tracking where chips go, and cloud reporting (CI-01). CI-01 has no coders yet and chip tracking isn't in the register, so both are worth adding.

## What the evidence team could look for

Ranked by how much each would change the answer (Figure 4 in `results/third_run/`):

| # | What | Instruments | Where it might be found |
|---|---|---|---|
| 1 | **Fine relative to gain** in an analogue regime | All | EU ETS excess-emissions penalty against the carbon price; IRS penalties against evaded tax |
| 2 | **How often detection leads to punishment** | All | ETS penalties actually imposed; IAEA findings → Board referrals; IRS assessments collected |
| 3 | **How often verifiers go easy** | CI-02 | Accreditation withdrawals (AN-02 already has 4); audit findings later overturned |
| 4 | **Imagery against deliberate concealment, detection by site size**, and what a hidden site costs | CI-05 | Nuclear cases (AN-01); any red-team or camouflage study. This matters most in the worst case |
| 5 | **Real compute-meter error** (a better meter *catch rate* is low priority) | CI-04 | Cloud billing disputes; GPU counter accuracy studies |
| 6 | **How often tampering with attestation is found** | CI-03 | Red-team rates and inspection findings, not just proofs of concept like TEE.fail. This matters most in the main ranges |

**Suggested codebook change: four new labels for column O.** The 5 Oct labels (detection, false alarms, metering noise, audit frequency, shared failure, timeliness, audit cost) are working, but the inputs that matter most now have no label:

1. **Fine vs gain:** how big penalties are compared with what cheating saves.
2. **Punishment follow-through:** the share of detected violations that ended in a penalty.
3. **Evasion cost:** what it cost to beat the check (equipment, a separate site, lost efficiency).
4. **Worst-case catch rate:** the catch rate against the best evasion tested, not the average.

Even a rough range helps, because the model currently assumes a fine of 5× the gain and that every caught developer is punished. The full mapping of codebook fields to model inputs is in `docs/ADDING_EVIDENCE.md`.

**Already coded and useful:** Joon's CI-05 row cites a table of detection by facility size (Koopmanschap & Barten, Table 5), which can replace the model's guessed site-size curve. Vir's CI-04 note (a meter with 1% error lets a lab hide about 3% of declared compute) matches the model's result for meter error from a different direction.

## Proposed next steps for the simulation (to 14 December)

- **By 9 November:** load the second-coder rows and rerun. Agree the worst-case values with the coders, because they drive the results.
- **Done 20 October:** combined regime, where breaking attestation also blinds metering.
- **Done 20 October:** CI-05 detection and hidden-site cost depend on run size.
- **By 24 November:** add cloud reporting (CI-01) and chip tracking to the combined regime once they are coded, since they are the checks that cover slow runs.
- **By 14 December:** report the between-country instruments (CI-05, CI-03 against a state) on **timeliness**, meaning whether cheating is caught before a run finishes, rather than on fines. Final figures and a single summary table: instrument, evidence status, fine needed.

## Questions for the team

1. Can we add the four column O labels, and can coders tag evidence for them before 9 Nov?
2. Who agrees the worst-case values? I'd suggest each instrument's coder pair.
3. Should the midterm say "detection is one of three inputs that matter most" instead of "the parameter that matters most"?
