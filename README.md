# Verification-Evidence-Simulation

Simulation track for SPAR Fall 2026, *Verification Evidence for Compute Governance*. It takes the evidence coded in the codebook and works out how big a fine must be, at each instrument's normal checking rate, for honest compute reporting to pay. It extends Christoph, *Risk-Weighted Compute Permit Markets under Imperfect Monitoring* (SSRN 6361077).

**Most inputs are still guesses. Don't cite the outputs as findings.** Each input is labelled `evidence`, `analogue` or `scenario`; see `docs/MODEL.md`.

## Run

```bash
make setup                   # once: creates .venv and installs packages
source .venv/bin/activate
make test                    # checks the input files, then runs the tests
make run RUN=fourth_run      # full run into results/fourth_run/ (about 3 minutes)
make quick                   # smoke test into results/scratch/ (ignored by git)
```

Without `make`: `python -m spar_sim.checks`, `python -m pytest -q`, `python -m spar_sim.run --out results/fourth_run`.

Every results folder holds a `manifest.json` (command, seed, code commit, package versions, input fingerprints) and a copy of the inputs, so any number can be traced back and rerun. Tests also run on GitHub on every push.

## Latest results

`results/third_run/RESULTS.md` (20 Oct): fine needed by instrument, worst case, meter error, few vs many developers, and which unknowns matter most.

## Layout

| Path | |
|---|---|
| `data/placeholder_ranges.csv` | Instrument inputs. One row per instrument × parameter: `low,central,high`, `status`, `source` |
| `data/scenarios/` | Files that override some rows, e.g. `worst_case.csv` |
| `data/policy_scenarios.csv` | Permit price, fine, flat cap, total compute |
| `data/policy_ranges.csv` | Ranges for the fine and chance of punishment, used in the sensitivity analysis |
| `spar_sim/model.py` | The model |
| `spar_sim/analysis.py` | Headline table, meter-error curve, sensitivity analysis |
| `spar_sim/run.py` | Runs everything into one results folder |
| `spar_sim/checks.py` | Input-file checks |
| `spar_sim/plots.py` | Figures |
| `tests/` | Tests (14) |
| `results/` | One folder per run. `first_run` and `second_run` are kept for comparison |
| `docs/MODEL.md` | How the model works and what it leaves out |
| `docs/ADDING_EVIDENCE.md` | How to turn a coded row into inputs |
| `docs/index.html` | Interactive playground |
| `baseline/` | The original model, kept for reference |
| `CHANGELOG.md` | What changed, run by run |

## Save changes to GitHub

Run these from this folder, never from your home folder:

```bash
git add .
git commit -m "what changed"
git push
```
