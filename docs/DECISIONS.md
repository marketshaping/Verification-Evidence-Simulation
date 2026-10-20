# Modelling decisions

This page lists every choice in the simulation that someone could reasonably question, with the date, the reason, and what would make us change it. Use it when writing the paper's methods section, or when a teammate asks why a number is what it is. Newest first within each section.

Status of each input (`evidence`, `analogue`, `scenario`) is in the `status` column of the files in `data/`. This page covers the choices *around* the inputs.

## What the model asks

| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| Q1 | 20 Oct | **Headline = fine needed, as a multiple of the gain from hiding, at each instrument's normal checking rate** (not "audit rate needed"). | Most instruments already check about once a year (every verifier report; a satellite pass over a country in about a month; continuous telemetry), so asking what audit rate is needed answers a question nobody faces. | Evidence that an instrument checks much less often in practice, e.g. inspectors sample chips. |
| Q2 | 18 Oct | **Domestic instruments are judged on fines. Instruments used between countries will be judged on timeliness** (caught before a dangerous run finishes). | Between states the sanction isn't a fine and the gain isn't a permit saving. | Planned for December. Until then, CI-05 and CI-03 results carry this caveat. |
| Q3 | 13 Oct | **Extend Christoph (SSRN 6361077)**: a developer compares the gain from hiding with checking rate × catch rate × fine. Two margins: hiding compute, and claiming a lower risk class. | Agreed with Joel and Jonas; matches Kaplow & Shavell (1994). | — |

## How instruments are modelled

| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| I9 | 20 Oct | **Run size**: imagery detection of a site follows a logistic curve in log power, half at 3–10 MW. The cheater chooses how many sites (1–64) to split across, and each extra site adds 1–8% of the gain to its cost. | Clymer's misses were all under 4 MW. A frontier run needs 10 or more small sites to dodge imagery, so splitting cost is what stops it. | A measured detection-by-site-size curve, or real costs of training across sites. |
| I10 | 20 Oct | **Run size is shown alongside time to reach 10²⁶ FLOP** (H100, 40% utilisation). | Thresholds are in total compute, so a small site run for longer reaches the same threshold. | — |
| I1 | 20 Oct | **Combined regime: the cheater picks one of three routes** (monitored chips; defeat attestation; hidden site) and faces only the checks that see that route. | Checks fail together. Multiplying catch rates assumes every check sees every cheater, and overstates the regime by 2–3 times. | A route we haven't listed, e.g. splitting compute across routes or cloud rental under false names (CI-01). |
| I2 | 20 Oct | **Within a route, checks are independent.** | Simplest assumption that still captures route choice. | Evidence that the same inspection both checks meters and looks for tampering, which would make them fail together. |
| I3 | 20 Oct | **Route costs are a share of the gain from hiding** (attestation 0–20%, hidden site 10–60%, plus 1–8% for each extra site). | Keeps costs in the same units as the fine. | Cost figures for a covert site (AN-01) or for key extraction at scale. |
| I4 | 20 Oct | **The "multiplied" comparison uses exactly the same catch rates as route choice.** | So the gap between them comes only from route choice, not from different inputs. | — |
| I5 | 13 Oct | **CI-03 attestation and CI-04 metering are one instrument** in the single-instrument runs. Its catch rate = chance attestation holds × chance the meter catches it. | Attestation doesn't measure compute; it decides whether metering can be trusted. The combined regime (I1) separates them. | — |
| I6 | 13 Oct | **CI-02 third-party verification works on the risk-class margin** in the single-instrument runs, and on compute in the combined regime. | The CI-02 row describes checking a developer's own framework and statements. In the combined regime a verifier also checks the reported compute. | The CI-02 second-coder row. |
| I7 | 13 Oct | **Pass/fail vs measuring checks.** Satellites and verifiers find the violation or don't. Meters read compute with error, and the alarm threshold is set so an honest developer is flagged at the false-alarm rate. | Matches how each instrument works. It produces the small "shaving" that fines can't remove (Figure 2). | — |
| I8 | 13 Oct | **Lenient verifiers**: a share of developers have a verifier whose catch rate is multiplied by a factor below 1. | The verifier is paid by the lab it checks (AN-02). | A measured rate of verifier capture. |

## Where numbers come from

| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| N7 | 20 Oct | **Proposed: four new column O labels**: fine vs gain, punishment follow-through, evasion cost, worst-case catch rate. The 5 Oct labels stay. Full mapping in `docs/ADDING_EVIDENCE.md`. | The inputs that matter most in the sensitivity analysis and the combined regime have no label, so coders aren't tagging evidence for them. | Sidar and the coders agreeing, or preferring separate columns. |
| N1 | 20 Oct | **Worst case = the weakest route the evidence knows about**: GPU detector against white-box LoRA (42.6%); hiding cuts satellite detection to 2–30%; 10–50% of verifiers lenient; tamper detection 5–50%. | A strategic cheater uses the best evasion available, not the average one tested. | Coder pairs to agree these values. **Open: not yet agreed with the team.** |
| N2 | 20 Oct | **Chance a caught developer is punished = 1 in the main runs**, 0.3–1 in the sensitivity analysis. **Fine = 5× the gain in the main runs**, 1–20× in the sensitivity analysis. | No coded figure for either. Iran's IAEA findings led to referrals, not penalties. | The two sanction fields proposed for the codebook. |
| N3 | 18 Oct | **CI-02 catch rate from tax audits** (thorough audits find about a third), **not** from Dyck, Morse & Zingales. | Dyck et al. (auditors make 10.5% of fraud detections) measures who finds frauds, not a catch rate per check. It is used as evidence for lenient verifiers instead. | A measured verifier catch rate. |
| N4 | 18 Oct | **Meter error from nuclear material accountancy** (AN-04, 0.3–2.8%). | Only quantified measurement-error target found. The transfer is uncertain: compute is used up, and the gap between declared and metered compute is mostly about accounting conventions. | A direct compute-meter error figure. |
| N5 | 13 Oct | **Only a number from a coded row is `evidence`.** A number from another regime is `analogue`; anything else is `scenario`. The input check enforces a source for evidence and analogue rows. | So results can say which parts rest on guesses. | — |
| N6 | 13 Oct | **Flat fine cap = 5% of the industry's yearly permit bill**; 4 vs 200 developers with total compute fixed. | Stands in for flat statutory caps (SB 53 $1m; RAISE $1m then $3m) without claiming a real gain-to-cap ratio. | A real figure for gain against cap. |

## Method

| # | Date | Decision | Why | What would change it |
|---|---|---|---|---|
| M1 | 20 Oct | **Sensitivity = Spearman rank correlation**, with every uncertain input drawn at once. | Cheap, transparent and robust to the model's step changes. Its weakness: rankings depend on how wide each range is. | A variance-based method (e.g. Sobol) for the final paper, if time allows. |
| M2 | 20 Oct | **New inputs are drawn after old ones**, so earlier results reproduce exactly for the same seed. Checked: runs 3 and 4 reproduce run 2's shared-rate sweep. | So a new feature never silently changes old numbers. | — |
| M3 | 13 Oct | **Triangular draws over low / central / high, 2,000 draws per cell, seed 20261014.** The same draws are used across audit rates, developer counts and caps. | Simple to explain. Using the same draws makes comparisons across settings fair. | — |
| M4 | 13 Oct | **Developer sizes are lognormal** (spread 0.6), rescaled to a fixed total. | From the baseline agent model. | — |

## Project setup

| # | Date | Decision | Why |
|---|---|---|---|
| P1 | 14 Oct | The repo is private. Nat pushes; Claude can't push to the `marketshaping` account. | Nat's choice. |
| P2 | 20 Oct | Every run writes `manifest.json` and a copy of its inputs. Test runs go to `results/scratch/`, which git ignores. | Any number can be traced back, and kept results can't be overwritten by accident. |

## Open decisions

- **Worst-case values (N1)** need agreeing with each coder pair.
- **Sanction fields (N2) and new column O labels (N7):** to be agreed with Sidar and the coders.
- **Detection by site size:** the CI-05 row cites Koopmanschap & Barten, Table 5. The model's 3–10 MW midpoint should be replaced with those numbers once the paper is in hand.
- **Run size (I9):** the 3–10 MW midpoint and the 1–8% per-site cost are guesses anchored on Clymer's misses. They need a coder's view.
- **Timeliness model (Q2):** not started.
