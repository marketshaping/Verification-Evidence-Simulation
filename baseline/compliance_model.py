"""Baseline compliance calculations for the SPAR Fall 2026 project.

The model follows the two-margin deterrence logic in Joel Christoph's
risk-weighted compute permit model. It is intentionally small and auditable.
"""

from dataclasses import dataclass, asdict
import json


@dataclass
class VerificationParams:
    permit_price: float = 10.0
    compute_audit_probability: float = 0.25
    compute_detection_probability: float = 1.0
    compute_penalty_slope: float = 50.0
    evaluation_audit_probability: float = 0.25
    evaluation_detection_probability: float = 1.0
    evaluation_penalty_slope: float = 50.0
    compute_audit_cost: float = 1.0
    evaluation_audit_cost: float = 1.0
    enforcement_budget: float = 1.0


def expected_penalty_slope(audit_probability: float, detection_probability: float, penalty_slope: float) -> float:
    return audit_probability * detection_probability * penalty_slope


def margin_result(price: float, audit_probability: float, detection_probability: float, penalty_slope: float) -> dict:
    expected_slope = expected_penalty_slope(audit_probability, detection_probability, penalty_slope)
    return {
        "permit_price": price,
        "expected_penalty_slope": expected_slope,
        "deterrence_margin": expected_slope - price,
        "truthful_reporting_deterred": expected_slope >= price,
    }


def minimum_audit_probability(price: float, detection_probability: float, penalty_slope: float) -> float:
    denom = detection_probability * penalty_slope
    if denom <= 0:
        return float("inf")
    return price / denom


def minimum_budget(params: VerificationParams) -> float:
    rho_c = minimum_audit_probability(
        params.permit_price,
        params.compute_detection_probability,
        params.compute_penalty_slope,
    )
    rho_e = minimum_audit_probability(
        params.permit_price,
        params.evaluation_detection_probability,
        params.evaluation_penalty_slope,
    )
    return params.compute_audit_cost * rho_c + params.evaluation_audit_cost * rho_e


def evaluate(params: VerificationParams) -> dict:
    compute = margin_result(
        params.permit_price,
        params.compute_audit_probability,
        params.compute_detection_probability,
        params.compute_penalty_slope,
    )
    evaluation = margin_result(
        params.permit_price,
        params.evaluation_audit_probability,
        params.evaluation_detection_probability,
        params.evaluation_penalty_slope,
    )
    budget_used = (
        params.compute_audit_cost * params.compute_audit_probability
        + params.evaluation_audit_cost * params.evaluation_audit_probability
    )
    return {
        "parameters": asdict(params),
        "compute_margin": compute,
        "evaluation_margin": evaluation,
        "both_margins_deterred": compute["truthful_reporting_deterred"] and evaluation["truthful_reporting_deterred"],
        "budget_used": budget_used,
        "budget_feasible": budget_used <= params.enforcement_budget,
        "minimum_budget_for_full_deterrence": minimum_budget(params),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(VerificationParams()), indent=2))
