"""Core model: noisy detection, each developer's best response, audit outcomes.

Setting (extends the two-margin model in Christoph, SSRN 6361077):

* A developer with true compute s declares (1 - delta) * s. Hiding a share
  delta saves p * delta * s in permits.
* With probability rho it is audited. An audit catches the under-report with
  probability d(delta). If caught it pays min(a * delta * s, cap).
* Measurement instruments (e.g. metering) read true compute with relative
  error sigma. The alarm threshold k * sigma is set so a compliant developer
  is flagged with probability f, so k = Phi^-1(1 - f). Then
      d(delta) = d_max * Phi((delta - k * sigma) / sigma).
  Small under-reports hide inside the noise band, which is why a little
  "shaving" stays profitable at any audit rate.
* Binary instruments (satellite imagery, third-party verification) either
  find the violation or not: d(delta) = d_max for any delta > 0.
* Evaluation margin: a high-risk developer may report the low-risk class,
  saving (alpha - 1) * p * s. Penalty per unit of evaded risk-weighted
  compute is a, so the same algebra applies with base (alpha - 1) * s.
* Collusion: a colluding verifier multiplies detection by a factor < 1.

Each developer picks the delta that maximises its expected payoff. Ties go
to the smaller delta (honesty when indifferent).
"""

from __future__ import annotations

import numpy as np
from scipy.special import ndtr, ndtri


def detection_shape(delta_grid: np.ndarray, noise_sd: np.ndarray, false_alarm: np.ndarray) -> np.ndarray:
    """Detection probability per unit of d_max, shape (worlds, grid).

    noise_sd is NaN for binary instruments.
    """
    delta = delta_grid[None, :]
    sd = noise_sd[:, None]
    binary = np.isnan(sd)
    sd_safe = np.where(binary, 1.0, sd)
    k = ndtri(1.0 - np.where(binary, 0.5, false_alarm[:, None]))
    curve = ndtr((delta - k * sd_safe) / sd_safe)
    step = (delta > 0).astype(float)
    return np.where(binary, step, curve)


def firm_sizes(rng: np.random.Generator, worlds: int, n_firms: int, total: float, size_sd: float) -> np.ndarray:
    """Lognormal developer sizes, rescaled so each world's total is fixed."""
    raw = rng.lognormal(0.0, size_sd, size=(worlds, n_firms))
    return raw / raw.sum(axis=1, keepdims=True) * total


def simulate(
    draws: dict[str, np.ndarray],
    margin: str,
    n_firms: int,
    rho: float,
    policy: dict[str, float],
    cap: float,
    rng: np.random.Generator,
    grid_points: int = 81,
    block: int = 250,
) -> dict[str, np.ndarray]:
    """Run one block of worlds. Returns per-world metrics (arrays of length W)."""
    p = policy["permit_price"]
    a = policy["penalty_slope"]
    worlds = len(draws["detection_max"])

    sizes = firm_sizes(rng, worlds, n_firms, policy["total_industry_compute"], policy["firm_size_sd"])
    if margin == "evaluation":
        high_risk = rng.random((worlds, n_firms)) < policy["high_risk_share"]
        base = np.where(high_risk, (policy["risk_multiplier"] - 1.0) * sizes, 0.0)
        grid = np.array([0.0, 1.0])
    else:
        base = sizes
        grid = np.linspace(0.0, policy["max_underreport_share"], grid_points)

    colluding = rng.random((worlds, n_firms)) < draws["collusion_share"][:, None]
    d_firm = draws["detection_max"][:, None] * np.where(colluding, draws["collusion_multiplier"][:, None], 1.0)
    shape = detection_shape(grid, draws["noise_sd"], draws["false_alarm"])  # (W, G)

    chosen = np.empty((worlds, n_firms))
    d_chosen = np.empty((worlds, n_firms))
    for start in range(0, worlds, block):  # keep memory small for N = 200
        sl = slice(start, start + block)
        b = base[sl][:, :, None]
        g = grid[None, None, :]
        det = d_firm[sl][:, :, None] * shape[sl][:, None, :]
        payoff = p * g * b - rho * det * np.minimum(a * g * b, cap)
        idx = payoff.argmax(axis=2)
        chosen[sl] = grid[idx]
        d_chosen[sl] = np.take_along_axis(det, idx[:, :, None], axis=2)[:, :, 0]

    audited = rng.random((worlds, n_firms)) < rho
    caught = audited & (rng.random((worlds, n_firms)) < d_chosen) & (chosen > 0)

    hidden = chosen * base
    total_base = base.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        evaded_share = np.where(total_base > 0, hidden.sum(axis=1) / total_base, np.nan)
        undetected_share = np.where(total_base > 0, (hidden * ~caught).sum(axis=1) / total_base, np.nan)
    big_evader = chosen >= (0.1 if margin == "compute" else 1.0)
    evading_compute_share = (sizes * big_evader).sum(axis=1) / sizes.sum(axis=1)
    rho_needed = p / (draws["detection_max"] * a)

    return {
        "evaded_share": evaded_share,
        "undetected_share": undetected_share,
        "evading_compute_share": evading_compute_share,
        "rho_needed_no_cap": rho_needed,
        "median_firm_underreport": np.median(chosen, axis=1),
    }
