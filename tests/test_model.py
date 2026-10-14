"""Checks that the new model agrees with the baseline and behaves sensibly."""

import importlib.util
from pathlib import Path

import numpy as np

from spar_sim.model import detection_shape, simulate
from spar_sim.params import load_instruments, load_policy

ROOT = Path(__file__).resolve().parent.parent
POLICY = load_policy()


def _baseline():
    spec = importlib.util.spec_from_file_location("baseline", ROOT / "baseline" / "compliance_model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _draws(d, n=200, sd=np.nan, f=np.nan, coll=0.0):
    return {"detection_max": np.full(n, d), "noise_sd": np.full(n, sd), "false_alarm": np.full(n, f),
            "collusion_share": np.full(n, coll), "collusion_multiplier": np.full(n, 0.25)}


def test_threshold_matches_baseline():
    # Baseline: minimum audit rate = p / (d * a) = 10 / (0.8 * 50) = 0.25
    base = _baseline()
    assert np.isclose(base.minimum_audit_probability(10, 0.8, 50), 0.25)
    out = simulate(_draws(0.8), "compute", 50, 0.25, POLICY, np.inf, np.random.default_rng(0))
    assert np.allclose(out["rho_needed_no_cap"], 0.25)


def test_binary_instrument_switches_at_threshold():
    rng = np.random.default_rng(1)
    below = simulate(_draws(0.8), "compute", 50, 0.20, POLICY, np.inf, rng)
    above = simulate(_draws(0.8), "compute", 50, 0.30, POLICY, np.inf, rng)
    assert np.allclose(below["evaded_share"], POLICY["max_underreport_share"])
    assert np.allclose(above["evaded_share"], 0.0)


def test_noisy_instrument_leaves_shaving_inside_noise_band():
    # Even with certain audits, small under-reports below the alarm threshold pay.
    out = simulate(_draws(0.9, sd=0.03, f=0.02), "compute", 50, 1.0, POLICY, np.inf, np.random.default_rng(2))
    shave = out["median_firm_underreport"]
    assert np.all(shave > 0) and np.all(shave < 0.15)


def test_detection_shape_false_alarm_at_zero():
    shape = detection_shape(np.array([0.0]), np.array([0.05]), np.array([0.02]))
    assert np.isclose(shape[0, 0], 0.02)


def test_flat_cap_hurts_large_developers_only():
    rng = np.random.default_rng(3)
    cap = POLICY["penalty_cap_flat"]
    few = simulate(_draws(0.8), "compute", 4, 0.5, POLICY, cap, rng)
    many = simulate(_draws(0.8), "compute", 200, 0.5, POLICY, cap, rng)
    assert few["evaded_share"].mean() > 0.3
    assert many["evaded_share"].mean() < 0.05


def test_ranges_load():
    ids = [i.instrument_id for i in load_instruments()]
    assert ids == ["CI-02", "CI-03+04", "CI-05"]
