# Verification-Evidence-Simulation

Simulation for SPAR Fall 2026, *Verification Evidence for Compute Governance*. It takes evidence from the codebook and works out how much compute developers would hide under a given audit rate, fine and verification instrument. It extends Christoph, *Risk-Weighted Compute Permit Markets under Imperfect Monitoring* (SSRN 6361077).

**Current inputs are mostly placeholders. Don't cite the outputs.**

## Run

```bash
pip install -r requirements.txt
python -m pytest -q        # checks
python -m spar_sim.run     # ~1.5 min, writes results/first_run/
```

Playground: open `docs/index.html` in a browser. Sliders show the same model live.

## Change the inputs

| File | What to edit |
|---|---|
| `data/placeholder_ranges.csv` | Instrument inputs (detection, noise, false alarms, collusion). One row per instrument × parameter: `low,central,high`, `status` (`evidence` or `scenario`), `source` (codebook row, e.g. `AN-03 (CI-03)`) |
| `data/policy_scenarios.csv` | Permit price, fine, audit rate, penalty cap, total compute |

Rules: a number from a coded row is `evidence` with its source. Anything else is `scenario`. Leave `noise_sd` blank for pass-or-fail checks.

## Files

| Path | |
|---|---|
| `spar_sim/model.py` | The model |
| `spar_sim/run.py` | The run: instruments × 4 or 200 developers × cap or no cap × audit rates |
| `results/first_run/` | `RESULTS.md` (summary), `summary.csv`, `sweep.csv`, figure |
| `docs/index.html` | Interactive playground |
| `baseline/` | The original model files, kept for reference |

## Save changes to GitHub

```bash
git add .
git commit -m "what changed"
git push
```
