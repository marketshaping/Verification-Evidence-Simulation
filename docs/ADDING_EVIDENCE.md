# Turning a coded row into model inputs

For Nat, or anyone updating `data/placeholder_ranges.csv` after a codebook row is filled in.

## Steps

1. **Find the parameter.** Each codebook field maps to one model input:

   | Codebook field | Model input (`parameter` column) |
   |---|---|
   | Measured detection rate | `detection_max` (or `detection_unconcealed` for CI-05) |
   | False-alarm rate | `false_alarm` |
   | Measurement uncertainty / metering noise | `noise_sd` (as a share of true compute) |
   | Inspection frequency | `natural_audit_rate` (chance a developer is checked in a year, at most 1) |
   | Known evasion, collusion | `concealment_multiplier`, `collusion_share`, `collusion_multiplier` |
   | Chance tampering is found (CI-03) | `tamper_detection` in `data/regime.csv` |
   | Cost of evading (attestation, hidden site) | `tamper_cost`, `hidden_site_cost` in `data/regime.csv` |
   | Detection by site size (CI-05) | `site_p50_mw`, `site_steepness` in `data/regime.csv` |
   | Cost of training across several sites | `split_cost_per_site` in `data/regime.csv` |
   | Timeliness, inspection effort | Recorded but not yet used |

2. **Write a range, not a point.** `low`, `central`, `high`. If the source gives one number, use its confidence interval. If there's none, use the spread across sources, or say why the range is what it is in `note`.
3. **Set `status`** to `evidence`, `analogue` or `scenario` (see `docs/MODEL.md`). Only a number from a coded row is `evidence`.
4. **Fill `source`** with the codebook row (e.g. `AN-04 (CI-04)`) and the paper. Evidence and analogue rows without a source fail the check.
5. **Keep the old values in `note`** ("Was 0.10/0.40/0.70"), so the change is visible without git.
6. **Run the checks, then a new run** under a new folder name:

   ```bash
   make test                    # checks the input files, then the tests
   make run RUN=fourth_run      # writes results/fourth_run/
   ```

7. **Write `results/<run>/RESULTS.md`**: what changed in the inputs, what moved in `headline.csv`, and what didn't.

## Which codebook labels feed which model inputs

Column O of tab 02 ("Model parameter informed") and column I of tab 01 ("Model parameters") tag what each row informs. The labels were agreed with Sidar on 5 October. Since then the model has added inputs that no label covers; those rows are in bold below. Labels can be combined, and a row can say "none" with a reason.

| Model input | Column O label | Status (20 Oct) | What coders have found |
|---|---|---|---|
| Catch rate per check | Detection | In use | Mostly "no basis for a detection probability" (AN-01, AN-02, AN-03) |
| False alarms | False alarms | In use | AN-04 (about 1%), CI-04 (3.06% per 30 s, lab), CI-05 (1%) |
| Meter error | Metering noise | In use | AN-04 (0.28–2.8%) |
| How often each check runs | Audit frequency | In use | AN-02 yearly; AN-03 every 3 months or daily remote |
| Checks failing together | Shared failure | In use, qualitative | AN-03: losing the device or channel stops attestation and remote monitoring |
| Time to notice | Timeliness | Coded; not used until the December timeliness model | AN-01, AN-03, AN-04 |
| Cost of checking | Audit cost | Coded; not used yet | AN-02, AN-03, AN-04 |
| **Fine compared with the gain** | **None. Proposed: "fine vs gain"** | **Missing** | Nothing. Ranks first or second in every sensitivity test |
| **Chance a caught developer is punished** | **None. Proposed: "punishment follow-through"** | **Missing** | Nothing. AN-01 has a qualitative case (Iran: Board referrals, not penalties) |
| **Cost of evading** (breaking chip checks, a hidden site, splitting a run) | **None. Proposed: "evasion cost"** | **Missing** | CI-03 mentions TEE.fail (under $1,000 of kit) in prose |
| **Catch rate against the best evasion** | **None. Proposed: "worst-case catch rate"** | **Missing; sometimes in "Evasion and failure modes"** | CI-04: 43–87% against white-box evasion |
| Detection by site size | Detection (CI-05) | Coded in tab 01, not yet pulled into the model | CI-05 cites Koopmanschap & Barten, PDF pp. 10–12, Table 5 |

Proposed 20 Oct: add the four labels in bold. The existing ones stay. See `docs/DECISIONS.md` (N7).

## Worst-case and other scenarios

A file in `data/scenarios/` lists only the rows it changes. `worst_case.csv` assumes a cheater uses the weakest route the evidence knows about. To add a scenario, copy that file, edit it, and add its name to `--scenarios`:

```bash
python -m spar_sim.run --out results/fourth_run --scenarios main,worst_case,my_scenario
```

## Rules the input check enforces

- `low ≤ central ≤ high`, all three numbers.
- Probabilities and shares lie between 0 and 1.
- `status` is one of: `evidence`, `analogue`, `scenario`, `design`, `not used`, `unreported`.
- No duplicate (instrument, parameter) rows.
