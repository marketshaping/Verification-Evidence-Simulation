# Verification-Evidence-Simulation

Simulation code for SPAR Fall 2026, *Verification Evidence for Compute Governance*. It turns the coded evidence (codebook tables 01 and 02) into parameter ranges per instrument. It then reports the audit rates and penalties at which truthful reporting pays. This replaces the old baseline repository; the baseline files are kept in `baseline/` for reference and are checked against in the tests.

The model extends the two-margin compliance model in Christoph, *Risk-Weighted Compute Permit Markets under Imperfect Monitoring* (SSRN 6361077). The details are at the top of `spar_sim/model.py`.

## Playground

`docs/index.html` is a one-page interactive version of the model. Open it in a browser, or turn on GitHub Pages (Settings → Pages → branch `main`, folder `/docs`) to get a link you can share. It calculates the same model as the Python code, using central values instead of random draws, so its numbers match the run at those values. The defaults are placeholders.

## Run it

```bash
pip install -r requirements.txt
python -m pytest -q          # 6 checks, including agreement with the baseline
python -m spar_sim.run       # about 1.5 minutes on a laptop; writes results/first_run/
```

## Layout

| Path | What it is |
|---|---|
| `data/placeholder_ranges.csv` | One row per instrument × parameter: low, central, high, unit, **status** (evidence or scenario) and the codebook row it came from |
| `data/policy_scenarios.csv` | Policy levers and setting: permit price, penalty slope, audit rate, penalty cap, number of developers |
| `spar_sim/model.py` | Detection curve, each developer's best response, audit outcomes |
| `spar_sim/params.py` | Loads the CSVs and draws parameter worlds (triangular over low, central, high) |
| `spar_sim/run.py` | First run: each instrument × N = 4 or 200 × cap or no cap × audit rate |
| `results/first_run/` | `summary.csv`, `sweep.csv`, the figure, and `RESULTS.md` (read this first) |
| `baseline/` | The original `compliance_model.py`, `agent_based_model.py` and `parameter_schema.csv` |

## From a codebook row to a range

Column O of table 02 ("Model parameter informed") uses the nine agreed labels. Each label maps to a column of the ranges file:

| Column O label | Ranges file parameter | Used in the model yet? |
|---|---|---|
| Detection rate | `detection_max` (or `detection_unconcealed` × `concealment_multiplier`) | Yes |
| False-alarm rate | `false_alarm` | Yes (sets the alarm threshold) |
| Measurement uncertainty | `noise_sd` | Yes |
| Evaluation detection | `detection_max` on an evaluation-margin instrument | Yes |
| Metering noise | `noise_sd` for metering instruments | Yes |
| Audit frequency | `audit_frequency` | Recorded; audit rate is swept as a policy lever |
| Audit cost | `audit_cost` | Not yet |
| Timeliness | `timeliness_days` | Not yet |
| Shared failure | `shared_failure` | Not yet |

Rules, following the codebook's coding rules:
- When a row reports a number, enter it with its source cell in `source` and set `status` to `evidence`.
- When nothing measured exists, enter a range, set `status` to `scenario`, and say why in `note`. Never relabel a scenario as evidence.
- A new instrument needs a `margin` row (compute or evaluation). Leave `noise_sd` empty if the check is pass or fail.

## Next steps
1. Replace CI-03+04 scenario values when Vir and Max's CI-04 rows arrive.
2. Make detection depend on facility size for CI-05 (sites under about 10 MW are mostly missed).
3. Combine instruments, with correlated failure when attestation (CI-03) is defeated.
4. Use audit cost to find the cheapest audit mix that keeps hidden compute under a target.
5. Convert the real flat caps (CA SB 53, NY RAISE) into model units using frontier training-run costs, and replace the placeholder cap. See finding 4 in `results/first_run/RESULTS.md`.
