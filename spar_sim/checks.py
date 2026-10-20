"""Check the input files before a run, so a bad row fails loudly instead of quietly.

    python -m spar_sim.checks          # check the main file and every scenario

Rules (see docs/ADDING_EVIDENCE.md):
* low <= central <= high, and all three present for a drawn parameter;
* probabilities and shares lie in [0, 1];
* status is one of the allowed labels;
* an "evidence" or "analogue" row names its source.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .params import DATA_DIR, _num, read_rows

STATUSES = {"evidence", "analogue", "scenario", "design", "not used", "unreported"}
UNIT_INTERVAL = {
    "detection_max", "detection_unconcealed", "concealment_multiplier", "false_alarm",
    "collusion_share", "collusion_multiplier", "natural_audit_rate", "sanction_probability",
    "meter_catch_intact", "tamper_detection", "tamper_cost", "hidden_site_cost",
    "verifier_tamper_factor", "verifier_hidden_factor",
}
NUMERIC_SKIP = {"margin", "shared_failure"}
REQUIRED = ["instrument_id", "instrument", "parameter", "low", "central", "high", "unit", "status", "source", "note"]


def check_rows(rows: list[dict[str, str]], label: str) -> list[str]:
    errors = []
    if rows and list(rows[0].keys()) != REQUIRED:
        errors.append(f"{label}: columns should be {','.join(REQUIRED)}")
        return errors
    seen = set()
    for n, r in enumerate(rows, start=2):  # line 1 is the header
        where = f"{label} line {n} ({r['instrument_id']} {r['parameter']})"
        key = (r["instrument_id"], r["parameter"])
        if key in seen:
            errors.append(f"{where}: duplicate row")
        seen.add(key)
        if r["status"] not in STATUSES:
            errors.append(f"{where}: status '{r['status']}' is not one of {sorted(STATUSES)}")
        if r["status"] in ("evidence", "analogue") and not r["source"]:
            errors.append(f"{where}: {r['status']} row needs a source")
        if r["parameter"] in NUMERIC_SKIP:
            continue
        vals = [_num(r[k]) for k in ("low", "central", "high")]
        if all(v is None for v in vals):
            if r["status"] not in ("not used", "unreported"):
                errors.append(f"{where}: no values; mark it 'not used' or 'unreported'")
            continue
        if any(v is None or isinstance(v, str) for v in vals):
            errors.append(f"{where}: low, central and high must all be numbers")
            continue
        lo, mid, hi = vals
        if not lo <= mid <= hi:
            errors.append(f"{where}: need low <= central <= high, got {lo}, {mid}, {hi}")
        if r["parameter"] in UNIT_INTERVAL and not (0 <= lo and hi <= 1):
            errors.append(f"{where}: must lie between 0 and 1")
    return errors


def check_all(data_dir: Path = DATA_DIR) -> list[str]:
    errors = check_rows(read_rows(data_dir / "placeholder_ranges.csv"), "placeholder_ranges.csv")
    errors += check_rows(read_rows(data_dir / "regime.csv"), "regime.csv")
    for path in sorted((data_dir / "scenarios").glob("*.csv")):
        errors += check_rows(read_rows(path), f"scenarios/{path.name}")
    return errors


def main() -> int:
    errors = check_all()
    for e in errors:
        print("ERROR", e)
    print("Inputs OK" if not errors else f"{len(errors)} problem(s) in the input files")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
