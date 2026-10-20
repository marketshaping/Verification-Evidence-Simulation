# Changelog

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
