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


# ---- Added 20 Oct: per-instrument checking rates, punishment, scenarios, input checks ----

from spar_sim.checks import check_all, check_rows  # noqa: E402
from spar_sim.model import fine_multiple_needed  # noqa: E402
from spar_sim.params import read_rows  # noqa: E402


def test_fine_needed_matches_simulated_switch():
    # Binary instrument checked yearly with d = 0.5: needs a fine of 2x the gain.
    p = POLICY["permit_price"]
    assert np.isclose(fine_multiple_needed(1.0, 0.5), 2.0)
    for mult, expect_hidden in ((1.9, True), (2.1, False)):
        draws = dict(_draws(0.5), penalty_slope=np.full(200, mult * p))
        out = simulate(draws, "compute", 50, 1.0, POLICY, np.inf, np.random.default_rng(4))
        assert np.allclose(out["evaded_share"], POLICY["max_underreport_share"] if expect_hidden else 0.0)


def test_sanction_probability_scales_threshold():
    # Halving the chance of punishment doubles the audit rate needed.
    d = dict(_draws(0.8), sanction_probability=np.full(200, 0.5))
    out = simulate(d, "compute", 50, 0.5, POLICY, np.inf, np.random.default_rng(5))
    assert np.allclose(out["rho_needed_no_cap"], 0.5)


def test_per_world_audit_rate():
    rho = np.where(np.arange(200) < 100, 0.2, 0.3)  # below and above the 0.25 threshold
    out = simulate(_draws(0.8), "compute", 50, rho, POLICY, np.inf, np.random.default_rng(6))
    assert np.allclose(out["evaded_share"][:100], POLICY["max_underreport_share"])
    assert np.allclose(out["evaded_share"][100:], 0.0)


def test_every_instrument_has_a_checking_rate():
    for inst in load_instruments():
        assert "natural_audit_rate" in inst.ranges, inst.instrument_id


def test_new_draws_do_not_change_old_ones():
    # natural_audit_rate is drawn last, so earlier inputs match runs 1 and 2 for the same seed.
    inst = load_instruments()[1]
    a = inst.draw(np.random.default_rng(7), 50)
    del inst.ranges["natural_audit_rate"]
    b = inst.draw(np.random.default_rng(7), 50)
    for k in ("detection_max", "noise_sd", "false_alarm"):
        assert np.array_equal(a[k], b[k])


def test_scenario_overrides_only_listed_rows():
    main = {i.instrument_id: i for i in load_instruments()}
    worst = {i.instrument_id: i for i in load_instruments(scenario="worst_case")}
    assert worst["CI-05"].ranges["concealment_multiplier"].central < main["CI-05"].ranges["concealment_multiplier"].central
    assert worst["CI-05"].ranges["detection_unconcealed"] == main["CI-05"].ranges["detection_unconcealed"]


def test_input_files_pass_checks():
    assert check_all() == []


def test_checks_catch_bad_rows():
    rows = read_rows(ROOT / "data" / "placeholder_ranges.csv")
    bad = [dict(rows[1], low="0.9", central="0.5", high="0.6"),           # out of order
           dict(rows[2], parameter="x", status="made up"),               # unknown status
           dict(rows[1], parameter="detection_y", source="", status="evidence"),  # no source
           dict(rows[1], parameter="detection_z", high="1.4")]           # above 1
    errors = check_rows(bad, "test")
    assert len(errors) == 4
