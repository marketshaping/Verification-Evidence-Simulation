# Changelog

## Fifth run, 20 October 2026

**Model**
- Run size: the cheater can split a hidden run across up to 64 sites. Imagery detection rises with site power (half at 3–10 MW), and each extra site costs 1–8% of the gain. Four new rows in `data/regime.csv`.
- Run size is shown alongside the time needed to reach 10²⁶ FLOP.

**Outputs:** `size.csv` and Figure 7. Everything from the fourth run is reproduced exactly.

**Docs:** new `docs/DECISIONS.md`, a log of every modelling choice with its reason and what would change it. The playground has a new step for the combined regime.

**Tests:** 22, up from 18.

## Fourth run, 20 October 2026

**Model**
- New: the combined regime (`spar_sim/regime.py`, `data/regime.csv`). The verifier, attested metering and satellite imagery work together, and a cheater picks one of three routes past them: under-report on monitored chips, defeat attestation and then under-report, or use a hidden site. The fine has to deter the cheapest route.
- Compared with multiplying catch rates, and with each instrument perfected or removed.
- Two worst-case rows added (meter catch rate, tamper detection). Scenario files now ignore rows for instruments that aren't in the file they modify.

**Outputs**
- `regime.csv`, `regime_instruments.csv`, `regime_sensitivity.csv`, Figure 5 (multiplied vs route choice) and Figure 6 (weakest link).
- Everything from the third run is reproduced exactly.

**Tests:** 18, up from 14. They include a check that route choice never needs a smaller fine than multiplication, and a check of the route formula against direct simulation.

## Third run, 20 October 2026

**Model**
- Each instrument has its own normal checking rate (`natural_audit_rate`): verifiers yearly, satellites about yearly, metering yearly if telemetry streams (lower if inspectors sample).
- New input: chance a caught developer is actually punished (`sanction_probability`, 1 in the main runs).
- Audit rate, fine and chance of punishment can now differ across parameter draws, which the sensitivity analysis needs.
- Scenario files (`data/scenarios/`) override listed rows only. First one: `worst_case.csv`.

**Outputs**
- `headline.csv` and Figure 1: fine needed per instrument at its normal checking rate.
- Figure 2: hidden compute against meter error. Figure 3: few vs many developers under a flat cap. Figure 4: which unknowns matter most.

**Good practice**
- Input-file checks run before every run and in the tests.
- Every run writes `manifest.json` and copies its inputs.
- `run.py` writes to `results/scratch/` (ignored by git) unless `--out` is given, so test runs can't overwrite kept results.
- Version ranges in `requirements.txt`, exact versions in `requirements-lock.txt`, `Makefile`, tests on GitHub on every push. 14 tests (was 6).
- Docs: `docs/MODEL.md`, `docs/ADDING_EVIDENCE.md`.

**Reproducibility check.** With the same seed, `summary.csv` and `sweep.csv` in `third_run` match `second_run` exactly. The new inputs are drawn after the old ones, so they don't shift earlier draws.

## Second run, 18 October 2026
First inputs from coded rows: CI-02 catch rate (tax analogue), CI-03+04 meter error and false alarms (AN-04). See `results/second_run/RESULTS.md`.

## First run, 13 October 2026
Placeholder ranges; few vs many developers; flat cap. See `results/first_run/RESULTS.md`.
