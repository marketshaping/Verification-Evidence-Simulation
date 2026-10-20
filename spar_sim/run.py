"""Run everything and write one results folder.

    python -m spar_sim.run --out results/third_run       # full run, about 3 minutes
    python -m spar_sim.run --quick                       # smoke test, writes results/scratch/

The default output folder, results/scratch/, is ignored by git, so a test run
never overwrites a committed result. Name a folder with --out to keep a run.

Outputs
  headline.csv           fine needed per instrument at its normal checking rate (main + scenarios)
  fig1_fine_needed.png   fine needed against checking rate
  fig2_meter_noise.png   small cheating left by meter error
  fig3_few_vs_many.png   few large vs many small developers under a flat fine cap
  sensitivity.csv, fig4_sensitivity.png   which unknown matters most
  summary.csv, sweep.csv, fig_evasion_vs_audit_rate.png   one shared audit rate (as in runs 1 and 2)
  manifest.json, inputs/ what produced this folder
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

from . import analysis, plots
from .checks import check_all
from .manifest import write_manifest
from .model import simulate
from .params import load_instruments, load_policy, load_policy_ranges

ROOT = Path(__file__).resolve().parent.parent
N_VALUES = (4, 200)
RHO_GRID = np.round(np.concatenate([np.arange(0.02, 0.3, 0.02), np.arange(0.3, 1.01, 0.05)]), 3)


def q(x: np.ndarray, pct: float) -> float:
    x = x[~np.isnan(x)]
    return float(np.percentile(x, pct)) if len(x) else float("nan")


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


def shared_rate_sweep(instruments, policy, worlds, seed):
    """One audit rate for all instruments, swept 0.02 to 1. Same seeds as runs 1 and 2."""
    caps = {"none": np.inf, "flat": policy["penalty_cap_flat"]}
    rho_ref = policy["reference_audit_probability"]
    report_rhos = sorted({rho_ref, 0.5, 1.0})
    summary_rows, sweep_rows = [], []
    for i, inst in enumerate(instruments):
        # Same parameter draws for every N, cap and audit rate (common random numbers).
        draws = inst.draw(np.random.default_rng([seed, i]), worlds)
        for n in N_VALUES:
            for cap_name, cap in caps.items():
                for j, rho in enumerate(sorted(set(RHO_GRID) | set(report_rhos))):
                    m = simulate(draws, inst.margin, n, rho, policy, cap, np.random.default_rng([seed, i, n, j]))
                    sweep_rows.append({
                        "instrument_id": inst.instrument_id, "N": n, "cap": cap_name, "rho": rho,
                        "evaded_p10": q(m["evaded_share"], 10), "evaded_p50": q(m["evaded_share"], 50),
                        "evaded_p90": q(m["evaded_share"], 90), "evaded_mean": float(np.nanmean(m["evaded_share"])),
                    })
                    if any(np.isclose(rho, r) for r in report_rhos):
                        ud = m["undetected_share"]
                        summary_rows.append({
                            "instrument_id": inst.instrument_id, "instrument": inst.name, "margin": inst.margin,
                            "N": n, "cap": cap_name, "rho": rho, "audits_per_year": rho * n,
                            "rho_needed_p10": q(m["rho_needed_no_cap"], 10),
                            "rho_needed_p50": q(m["rho_needed_no_cap"], 50),
                            "rho_needed_p90": q(m["rho_needed_no_cap"], 90),
                            "evaded_mean": float(np.nanmean(m["evaded_share"])),
                            "evaded_p50": q(m["evaded_share"], 50),
                            "evaded_p90": q(m["evaded_share"], 90),
                            "undetected_mean": float(np.nanmean(ud)),
                            "undetected_p90": q(ud, 90),
                            "p_undetected_over_10pct": float(np.nanmean(ud[~np.isnan(ud)] > 0.10)),
                            "evading_compute_share_mean": float(np.mean(m["evading_compute_share"])),
                            "median_firm_underreport_p50": q(m["median_firm_underreport"], 50),
                            "worlds": worlds,
                        })
    # Smallest audit rate at which, on average, less than 5% is hidden.
    for r in summary_rows:
        sel = sorted((x for x in sweep_rows if x["instrument_id"] == r["instrument_id"] and x["N"] == r["N"] and x["cap"] == r["cap"]),
                     key=lambda x: x["rho"])
        ok = [x["rho"] for x in sel if x["evaded_mean"] < 0.05]
        r["rho_for_under_5pct_hidden"] = min(ok) if ok else "above 1"
    return summary_rows, sweep_rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "scratch")
    ap.add_argument("--worlds", type=int, default=2000, help="parameter draws per cell")
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--scenarios", default="main,worst_case", help="comma-separated; 'main' = no scenario file")
    ap.add_argument("--quick", action="store_true", help="few draws, for a smoke test")
    args = ap.parse_args(argv)
    if args.quick:
        args.worlds = 100
    t0 = time.time()

    errors = check_all()
    if errors:
        print("\n".join("ERROR " + e for e in errors))
        sys.exit("Fix the input files first (python -m spar_sim.checks).")
    args.out.mkdir(parents=True, exist_ok=True)

    policy = load_policy()
    policy_ranges = load_policy_ranges()
    instruments = load_instruments()
    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]

    # 1. Shared audit-rate sweep (comparable with runs 1 and 2).
    summary_rows, sweep_rows = shared_rate_sweep(instruments, policy, args.worlds, args.seed)
    write_csv(args.out / "summary.csv", summary_rows)
    write_csv(args.out / "sweep.csv", sweep_rows)
    plots.plot_sweep(sweep_rows, instruments, policy["reference_audit_probability"],
                     args.out / "fig_evasion_vs_audit_rate.png", run_label=args.out.name.replace("_", " ").capitalize())

    # 2. Headline: fine needed at each instrument's normal checking rate.
    head_rows, curves, natural = [], {}, {}
    rhos = np.geomspace(0.05, 1, 60)
    for k, scen in enumerate(scenarios):
        insts = load_instruments(scenario=None if scen == "main" else scen)
        curves[scen], natural[scen] = {}, {}
        for i, inst in enumerate(insts):
            draws = inst.draw(np.random.default_rng([args.seed, 100 + k, i]), args.worlds)
            head_rows.append(analysis.headline(inst, draws, policy, 200, [args.seed, 200 + k, i], scen))
            c = analysis.fine_curve(draws, rhos)
            c.update(rho=rhos, name=inst.name)
            if np.any(draws["collusion_share"] > 0):
                c["captured"] = analysis.fine_curve(draws, rhos, draws["collusion_multiplier"])
            curves[scen][inst.instrument_id] = c
            natural[scen][inst.instrument_id] = float(np.median(draws["natural_audit_rate"]))
    write_csv(args.out / "headline.csv", head_rows)
    plots.plot_fine_needed(curves, natural, args.out / "fig1_fine_needed.png",
                           policy["penalty_slope"] / policy["permit_price"])

    # 3. Meter error.
    metering = next(i for i in instruments if not i.is_binary)
    sigmas = np.linspace(0.001, 0.05, 50)
    noise = {f"false alarms {fa:.0%}": analysis.noise_curve(metering, policy, sigmas, fa, seed=args.seed)
             for fa in (0.01, 0.03)}
    write_csv(args.out / "meter_noise.csv",
              [{"meter_error": s, **{k: v[j] for k, v in noise.items()}} for j, s in enumerate(sigmas)])
    band = (metering.ranges["noise_sd"].low, metering.ranges["noise_sd"].high)
    plots.plot_noise(sigmas, noise, band, args.out / "fig2_meter_noise.png")

    # 4. Few vs many under a flat cap (binary instrument, so the effect is clean).
    sat = next(i for i in instruments if i.instrument_id == "CI-05")
    plots.plot_few_vs_many(sweep_rows, sat.instrument_id, sat.name, args.out / "fig3_few_vs_many.png")

    # 5. Sensitivity.
    sens_rows = []
    for i, inst in enumerate(instruments):
        sens_rows += analysis.sensitivity(inst, policy, policy_ranges, max(2 * args.worlds, 400), 200, [args.seed, 300, i])
    write_csv(args.out / "sensitivity.csv", sens_rows)
    plots.plot_sensitivity(sens_rows, instruments, args.out / "fig4_sensitivity.png")

    write_manifest(args.out, vars(args), {"runtime_seconds": round(time.time() - t0, 1)})
    print(f"Wrote results to {args.out} in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
