"""Headline results, the meter-noise curve and the sensitivity analysis.

Headline question: at each instrument's normal checking rate, how big must the
fine be, relative to what a developer gains by hiding compute, for honest
reporting to pay?

For a pass/fail instrument the answer is exact: a/p >= 1 / (rho * d * q).
For a measuring instrument the same bound deters large evasion, but small
under-reports inside the noise band stay profitable at any fine, so we also
report that floor.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from .model import fine_multiple_needed, simulate
from .params import Instrument

FINE_GRID = np.round(np.geomspace(1, 100, 31), 3)  # fine-to-gain ratios tried
HIDDEN_TARGET = 0.05  # "deterred" means on average less than 5% hidden


def pct(x: np.ndarray, q: float) -> float:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(np.percentile(x, q)) if len(x) else float("nan")


def headline(inst: Instrument, draws: dict, policy: dict, n_firms: int, seed, scenario: str) -> dict:
    """One row of the headline table for one instrument under one scenario."""
    p = policy["permit_price"]
    rho = draws["natural_audit_rate"]
    d = draws["detection_max"]
    honest = fine_multiple_needed(rho, d)
    captured = fine_multiple_needed(rho, d * draws["collusion_multiplier"])
    has_capture = bool(np.any(draws["collusion_share"] > 0))

    m = simulate(draws, inst.margin, n_firms, rho, policy, np.inf, np.random.default_rng([*seed, 0]))

    # Smallest fine ratio at which, on average across worlds, under 5% is hidden.
    reached = "above 100"
    for j, mult in enumerate(FINE_GRID):
        trial = dict(draws, penalty_slope=np.full(len(d), mult * p))
        mm = simulate(trial, inst.margin, n_firms, rho, policy, np.inf, np.random.default_rng([*seed, 1, j]))
        if np.nanmean(mm["evaded_share"]) < HIDDEN_TARGET:
            reached = float(mult)
            break

    return {
        "scenario": scenario,
        "instrument_id": inst.instrument_id,
        "instrument": inst.name,
        "natural_audit_rate_p50": pct(rho, 50),
        "detection_p10": pct(d, 10), "detection_p50": pct(d, 50), "detection_p90": pct(d, 90),
        "fine_needed_honest_p10": pct(honest, 10),
        "fine_needed_honest_p50": pct(honest, 50),
        "fine_needed_honest_p90": pct(honest, 90),
        "fine_needed_captured_p50": pct(captured, 50) if has_capture else "",
        "fine_needed_captured_p90": pct(captured, 90) if has_capture else "",
        "share_worlds_deterred_at_5x": float(np.mean(honest <= policy["penalty_slope"] / p)),
        "hidden_at_5x_mean": float(np.nanmean(m["evaded_share"])),
        "undetected_at_5x_mean": float(np.nanmean(m["undetected_share"])),
        "undetected_at_5x_p90": pct(m["undetected_share"], 90),
        "fine_for_under_5pct_hidden": reached,
        "N": n_firms,
    }


def fine_curve(draws: dict, rhos: np.ndarray, multiplier: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """Fine ratio needed against audit rate: 10th, 50th and 90th percentile over worlds."""
    d = draws["detection_max"] * (1.0 if multiplier is None else multiplier)
    inv = 1.0 / d
    return {
        "p10": np.percentile(inv, 10) / rhos,
        "p50": np.percentile(inv, 50) / rhos,
        "p90": np.percentile(inv, 90) / rhos,
    }


def noise_curve(inst: Instrument, policy: dict, sigmas: np.ndarray, false_alarm: float, rho: float = 1.0,
                worlds: int = 50, seed: int = 0) -> np.ndarray:
    """Share of compute hidden against meter error, other inputs at their central values."""
    central = {k: float(r.central) for k, r in inst.ranges.items() if isinstance(r.central, (int, float))}
    out = []
    for i, s in enumerate(sigmas):
        draws = {
            "detection_max": np.full(worlds, central["detection_max"]),
            "noise_sd": np.full(worlds, s),
            "false_alarm": np.full(worlds, false_alarm),
            "collusion_share": np.zeros(worlds),
            "collusion_multiplier": np.ones(worlds),
        }
        m = simulate(draws, "compute", 200, rho, policy, np.inf, np.random.default_rng([seed, i]), grid_points=801)
        out.append(float(np.nanmean(m["evaded_share"])))
    return np.array(out)


LABELS = {
    "detection_max": "Catch rate per check",
    "detection_unconcealed": "Catch rate, unhidden site",
    "concealment_multiplier": "Effect of hiding the site",
    "noise_sd": "Meter error",
    "false_alarm": "False-alarm rate",
    "collusion_share": "Share of lenient verifiers",
    "collusion_multiplier": "How lenient they are",
    "natural_audit_rate": "How often checked",
    "fine_multiple": "Fine / gain",
    "sanction_probability": "Chance caught lab is punished",
}


def sensitivity(inst: Instrument, policy: dict, policy_ranges: dict, worlds: int, n_firms: int, seed) -> list[dict]:
    """Rank correlation of each uncertain input with the share of compute hidden and not caught.

    Every input with a range is drawn at once (instrument inputs, checking
    rate, fine-to-gain ratio, chance of punishment), then each input's
    Spearman correlation with the outcome is reported. A larger absolute value
    means pinning that input down would change the answer more.
    """
    rng = np.random.default_rng(seed)
    raw: dict[str, np.ndarray] = {}
    draws = inst.draw(rng, worlds, record=raw)
    fine = policy_ranges["fine_multiple"].draw(rng, worlds)
    q = policy_ranges["sanction_probability"].draw(rng, worlds)
    raw["fine_multiple"], raw["sanction_probability"] = fine, q
    draws = dict(draws, penalty_slope=fine * policy["permit_price"], sanction_probability=q)
    m = simulate(draws, inst.margin, n_firms, draws["natural_audit_rate"], policy, np.inf, rng)
    y = m["undetected_share"]
    rows = []
    for key, x in raw.items():
        if np.ptp(x) == 0:
            continue
        ok = np.isfinite(y)
        r = spearmanr(x[ok], y[ok]).statistic
        rows.append({"instrument_id": inst.instrument_id, "input": key, "label": LABELS.get(key, key),
                     "status": (policy_ranges.get(key) or inst.ranges.get(key)).status,
                     "spearman": float(r), "abs_spearman": abs(float(r)), "worlds": worlds})
    return sorted(rows, key=lambda r: -r["abs_spearman"])
