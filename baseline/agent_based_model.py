"""Stylized agent-based stress test for verification architectures.

This is a transparent test harness, not an empirical model. Agents may
under-report compute or misreport a high-risk evaluation when the private
saving from evasion exceeds the expected penalty. Noisy detection and
provider collusion reduce effective detection probabilities.
"""

from dataclasses import dataclass
import argparse
import json
import random
import statistics


@dataclass
class StressParams:
    n_agents: int = 200
    permit_price: float = 10.0
    risk_multiplier: float = 2.0
    high_risk_probability: float = 0.25
    compute_audit_probability: float = 0.25
    evaluation_audit_probability: float = 0.25
    compute_detection_probability: float = 0.8
    evaluation_detection_probability: float = 0.8
    compute_penalty_slope: float = 50.0
    evaluation_penalty_slope: float = 50.0
    meter_noise_sd: float = 0.05
    collusion_share: float = 0.0
    collusion_detection_multiplier: float = 0.25
    max_compute_underreport_share: float = 0.4


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def one_world(params: StressParams, rng: random.Random) -> dict:
    truthful_compute = 0
    truthful_eval = 0
    violations = 0
    detected = 0
    total_true_compute = 0.0
    total_reported_compute = 0.0

    for _ in range(params.n_agents):
        compute = max(0.1, rng.lognormvariate(0.0, 0.6))
        high_risk = rng.random() < params.high_risk_probability
        colluding = rng.random() < params.collusion_share
        detection_multiplier = params.collusion_detection_multiplier if colluding else 1.0

        meter_noise = rng.gauss(0.0, params.meter_noise_sd)
        compute_detection = clamp(params.compute_detection_probability * detection_multiplier * (1.0 - abs(meter_noise)))
        eval_detection = clamp(params.evaluation_detection_probability * detection_multiplier)

        expected_compute_penalty = (
            params.compute_audit_probability
            * compute_detection
            * params.compute_penalty_slope
        )
        compute_evasion_profitable = expected_compute_penalty < params.permit_price

        if compute_evasion_profitable:
            gap = clamp((params.permit_price - expected_compute_penalty) / max(params.permit_price, 1e-9))
            underreport_share = params.max_compute_underreport_share * gap
        else:
            underreport_share = 0.0

        reported_compute = compute * (1.0 - underreport_share)
        compute_truthful = underreport_share <= 1e-12

        if high_risk:
            expected_eval_penalty = (
                params.evaluation_audit_probability
                * eval_detection
                * params.evaluation_penalty_slope
            )
            eval_evasion_profitable = expected_eval_penalty < params.permit_price
        else:
            eval_evasion_profitable = False

        eval_truthful = not eval_evasion_profitable
        violated = (not compute_truthful) or (not eval_truthful)

        was_detected = False
        if not compute_truthful and rng.random() < params.compute_audit_probability:
            was_detected = rng.random() < compute_detection
        if not eval_truthful and rng.random() < params.evaluation_audit_probability:
            was_detected = was_detected or (rng.random() < eval_detection)

        truthful_compute += int(compute_truthful)
        truthful_eval += int(eval_truthful)
        violations += int(violated)
        detected += int(was_detected)
        total_true_compute += compute
        total_reported_compute += reported_compute

    return {
        "truthful_compute_share": truthful_compute / params.n_agents,
        "truthful_evaluation_share": truthful_eval / params.n_agents,
        "violation_share": violations / params.n_agents,
        "detected_violation_share_of_agents": detected / params.n_agents,
        "reported_to_true_compute_ratio": total_reported_compute / total_true_compute,
    }


def simulate(params: StressParams, runs: int, seed: int) -> dict:
    rng = random.Random(seed)
    worlds = [one_world(params, rng) for _ in range(runs)]
    keys = worlds[0].keys()
    summary = {}
    for key in keys:
        values = [w[key] for w in worlds]
        summary[key] = {
            "mean": statistics.fmean(values),
            "p10": sorted(values)[max(0, int(0.10 * (len(values) - 1)))],
            "p90": sorted(values)[max(0, int(0.90 * (len(values) - 1)))],
        }
    return {"parameters": params.__dict__, "runs": runs, "summary": summary}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--collusion-share", type=float, default=0.0)
    parser.add_argument("--meter-noise-sd", type=float, default=0.05)
    args = parser.parse_args()

    p = StressParams(collusion_share=args.collusion_share, meter_noise_sd=args.meter_noise_sd)
    print(json.dumps(simulate(p, runs=args.runs, seed=args.seed), indent=2))
