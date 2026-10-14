"""First run: placeholder ranges, few vs many developers, with and without a flat penalty cap.

    python -m spar_sim.run                 # writes results/first_run/
    python -m spar_sim.run --worlds 500    # quicker

Outputs
  summary.csv   one row per instrument x N x cap, at the reference audit rate
  sweep.csv     the same metrics across audit rates (feeds the figure)
  fig_evasion_vs_audit_rate.png
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from .model import simulate
from .params import load_instruments, load_policy

ROOT = Path(__file__).resolve().parent.parent
N_VALUES = (4, 200)
RHO_GRID = np.round(np.concatenate([np.arange(0.02, 0.3, 0.02), np.arange(0.3, 1.01, 0.05)]), 3)


def q(x: np.ndarray, pct: float) -> float:
    x = x[~np.isnan(x)]
    return float(np.percentile(x, pct)) if len(x) else float("nan")


def run_cell(inst, draws, n, rho, policy, cap, seed):
    rng = np.random.default_rng(seed)
    return simulate(draws, inst.margin, n, rho, policy, cap, rng)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "first_run")
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)

    policy = load_policy()
    instruments = load_instruments()
    caps = {"none": np.inf, "flat": policy["penalty_cap_flat"]}
    rho_ref = policy["reference_audit_probability"]
    report_rhos = sorted({rho_ref, 0.5, 1.0})

    summary_rows, sweep_rows = [], []
    for i, inst in enumerate(instruments):
        # Same parameter draws for every N, cap and audit rate (common random numbers).
        draws = inst.draw(np.random.default_rng([args.seed, i]), args.worlds)
        for n in N_VALUES:
            for cap_name, cap in caps.items():
                for j, rho in enumerate(sorted(set(RHO_GRID) | set(report_rhos))):
                    m = run_cell(inst, draws, n, rho, policy, cap, [args.seed, i, n, j])
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
                            "worlds": args.worlds,
                        })

    # Smallest audit rate at which, on average, less than 5% is hidden.
    for r in summary_rows:
        sel = sorted((x for x in sweep_rows if x["instrument_id"] == r["instrument_id"] and x["N"] == r["N"] and x["cap"] == r["cap"]),
                     key=lambda x: x["rho"])
        ok = [x["rho"] for x in sel if x["evaded_mean"] < 0.05]
        r["rho_for_under_5pct_hidden"] = min(ok) if ok else "above 1"

    for name, rows in (("summary.csv", summary_rows), ("sweep.csv", sweep_rows)):
        with open(args.out / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    from .plots import plot_sweep
    plot_sweep(sweep_rows, instruments, rho_ref, args.out / "fig_evasion_vs_audit_rate.png")
    print(f"Wrote {len(summary_rows)} summary rows and {len(sweep_rows)} sweep rows to {args.out}")


if __name__ == "__main__":
    main()
