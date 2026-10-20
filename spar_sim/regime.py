"""Combined regime: verifiers, attested metering and satellite imagery working together.

A developer that wants to hide compute doesn't face each instrument one at a
time. It picks one way of hiding (a route) and faces whichever instruments
can see that route:

  1. Under-report on monitored chips. Seen by the verifier and the meter
     (attestation intact). The satellite sees nothing: the site is declared.
  2. Defeat attestation, then under-report. The meter is blind, which is the
     "attestation failure blinds metering" case. The tampering itself may be
     found at an inspection, and the verifier is partly fooled by fake meter data.
  3. Use a hidden site with diverted chips. Only the satellite, plus a verifier
     that notices gaps, can see it. Costly to set up.

Within a route the instruments are treated as independent, so the chance of
being caught on route r is

    P_r = 1 - prod_i (1 - rate_i * catch_{i,r})

and route r pays when (1 - cost_r) * gain > chance of punishment * P_r * fine.
Honest reporting pays only if every route is deterred, so the fine needed, as
a multiple of the gain, is

    fine needed = max_r (1 - cost_r) / (chance of punishment * P_r).

The "multiplied" comparison uses the same catch rates but assumes every check
applies to every cheater, which is what multiplying catch rates implicitly does:

    fine needed (multiplied) = 1 / (chance of punishment * (1 - prod_i (1 - rate_i * catch_i)))

with i running over the verifier, the meter, tamper detection and the
satellite. Each route faces a subset of these checks, at most as strong, and
route 1 costs nothing extra, so route choice never needs a smaller fine than
multiplication. The gap is how much multiplying overstates a combined regime.

Pass/fail logic only: small under-reports inside the meter's error band
(Figure 2) are a separate effect and not included here.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from .params import Instrument, Range

ROUTES = ("monitored", "tamper", "hidden_site")
ROUTE_LABELS = {
    "monitored": "Under-report on monitored chips",
    "tamper": "Defeat attestation, then under-report",
    "hidden_site": "Use a hidden site",
}
INSTRUMENTS = ("verifier", "meter", "attestation", "satellite")
INSTRUMENT_LABELS = {
    "verifier": "CI-02 verifier",
    "meter": "CI-04 meter (attestation intact)",
    "attestation": "CI-03 tamper detection",
    "satellite": "CI-05 satellite imagery",
}
REGIME_LABELS = {
    "meter_catch_intact": "Meter catch rate, attestation intact",
    "tamper_detection": "Chance tampering is found",
    "tamper_cost": "Cost of defeating attestation",
    "verifier_tamper_factor": "Verifier fooled by fake meter data",
    "hidden_site_cost": "Cost of a hidden site",
    "verifier_hidden_factor": "Verifier sees a hidden site",
    "verifier_catch": "Verifier catch rate",
    "verifier_rate": "How often verifier checks",
    "meter_rate": "How often meter is checked",
    "satellite_catch": "Satellite catch rate (with hiding)",
    "satellite_rate": "How often satellite screens",
}


def draw_inputs(instruments: dict[str, Instrument], regime: dict[str, Range], rng: np.random.Generator,
                n: int, lenient_verifier: bool = False) -> dict[str, np.ndarray]:
    """Draw n worlds of every input the combined regime needs."""
    v = instruments["CI-02"].draw(rng, n)
    m = instruments["CI-03+04"].draw(rng, n)
    s = instruments["CI-05"].draw(rng, n)
    x = {k: r.draw(rng, n) for k, r in regime.items()}
    verifier = v["detection_max"] * (v["collusion_multiplier"] if lenient_verifier else 1.0)
    return {
        **x,
        "verifier_catch": verifier, "verifier_rate": v["natural_audit_rate"],
        "meter_rate": m["natural_audit_rate"],
        "satellite_catch": s["detection_max"], "satellite_rate": s["natural_audit_rate"],
    }


def route_catch(x: dict[str, np.ndarray], perfect: str | None = None, drop: str | None = None) -> dict[str, np.ndarray]:
    """Chance of being caught on each route. perfect / drop set one instrument's catch rate to 1 / 0."""
    def catch(name, value):
        if name == perfect:
            return np.ones_like(value)
        if name == drop:
            return np.zeros_like(value)
        return value

    ver = catch("verifier", x["verifier_catch"]) * x["verifier_rate"]
    met = catch("meter", x["meter_catch_intact"]) * x["meter_rate"]
    tam = catch("attestation", x["tamper_detection"]) * x["meter_rate"]
    sat = catch("satellite", x["satellite_catch"]) * x["satellite_rate"]
    # A perfect or missing verifier changes its base catch rate; the route factors still apply.
    return {
        "monitored": 1 - (1 - ver) * (1 - met),
        "tamper": 1 - (1 - ver * x["verifier_tamper_factor"]) * (1 - tam),
        "hidden_site": 1 - (1 - ver * x["verifier_hidden_factor"]) * (1 - sat),
    }


def fine_needed(x: dict[str, np.ndarray], sanction_probability=1.0, **kw) -> tuple[np.ndarray, np.ndarray]:
    """Fine needed (multiple of gain) under route choice, and which route sets it."""
    p = route_catch(x, **kw)
    cost = {"monitored": 0.0, "tamper": x["tamper_cost"], "hidden_site": x["hidden_site_cost"]}
    with np.errstate(divide="ignore"):
        need = np.stack([(1 - cost[r]) / (sanction_probability * p[r]) for r in ROUTES])
    return need.max(axis=0), need.argmax(axis=0)


def fine_needed_multiplied(x: dict[str, np.ndarray], sanction_probability=1.0) -> np.ndarray:
    """Fine needed if every check applied to every cheater (same catch rates as the routes)."""
    miss = ((1 - x["verifier_catch"] * x["verifier_rate"])
            * (1 - x["meter_catch_intact"] * x["meter_rate"])
            * (1 - x["tamper_detection"] * x["meter_rate"])
            * (1 - x["satellite_catch"] * x["satellite_rate"]))
    return 1 / (sanction_probability * (1 - miss))


def pct(a: np.ndarray, q: float) -> float:
    a = np.asarray(a, float)
    a = np.where(np.isfinite(a), a, 1e9)  # an undeterrable world counts as a huge fine
    return float(np.percentile(a, q))


def summarise(x: dict[str, np.ndarray], scenario: str, verifier: str, current_multiple: float) -> tuple[list, list]:
    """Rows for regime.csv (headline) and regime_instruments.csv (perfect / drop each instrument)."""
    need, route = fine_needed(x)
    naive = fine_needed_multiplied(x)
    head = {
        "scenario": scenario, "verifier": verifier,
        "fine_needed_route_p10": pct(need, 10), "fine_needed_route_p50": pct(need, 50), "fine_needed_route_p90": pct(need, 90),
        "fine_needed_multiplied_p10": pct(naive, 10), "fine_needed_multiplied_p50": pct(naive, 50),
        "fine_needed_multiplied_p90": pct(naive, 90),
        "ratio_route_to_multiplied_p50": pct(need / naive, 50),
        "share_deterred_at_current_fine_route": float(np.mean(need <= current_multiple)),
        "share_deterred_at_current_fine_multiplied": float(np.mean(naive <= current_multiple)),
        **{f"share_route_{r}": float(np.mean(route == i)) for i, r in enumerate(ROUTES)},
    }
    inst = []
    for name in INSTRUMENTS:
        perfect, _ = fine_needed(x, perfect=name)
        dropped, _ = fine_needed(x, drop=name)
        inst.append({
            "scenario": scenario, "verifier": verifier, "instrument": name, "label": INSTRUMENT_LABELS[name],
            "fine_needed_now_p50": pct(need, 50),
            "fine_needed_if_perfect_p50": pct(perfect, 50),
            "fine_needed_if_removed_p50": pct(dropped, 50),
            "share_worlds_helped_by_perfecting": float(np.mean(perfect < need - 1e-12)),
        })
    return [head], inst


def sensitivity(x: dict[str, np.ndarray], scenario: str, statuses: dict[str, str] | None = None) -> list[dict]:
    """Rank correlation of each input with the fine needed under route choice."""
    need, _ = fine_needed(x)
    y = np.where(np.isfinite(need), need, 1e9)
    rows = []
    for key, label in REGIME_LABELS.items():
        a = x[key]
        if np.ptp(a) == 0:
            continue
        r = float(spearmanr(a, y).statistic)
        rows.append({"scenario": scenario, "input": key, "label": label, "status": (statuses or {}).get(key, ""),
                     "spearman": r, "abs_spearman": abs(r)})
    return sorted(rows, key=lambda r: -r["abs_spearman"])
