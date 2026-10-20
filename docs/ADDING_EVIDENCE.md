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
