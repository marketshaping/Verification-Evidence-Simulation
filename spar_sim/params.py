"""Load instrument ranges and policy scenarios, and draw parameter worlds.

Every range in data/placeholder_ranges.csv is drawn from a triangular
distribution (low, central, high). A range marked "evidence" comes from a
coded row; a range marked "scenario" is an assumption and must be reported as
one. The status column is kept so results can say which is which.

A scenario file in data/scenarios/ has the same columns. Its rows replace the
matching (instrument_id, parameter) rows of the main file, so a scenario only
lists what it changes.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCENARIO_DIR = DATA_DIR / "scenarios"


def _num(x: str):
    x = (x or "").strip()
    if x == "":
        return None
    try:
        return float(x)
    except ValueError:
        return x


@dataclass
class Range:
    low: float | None
    central: float | str | None
    high: float | None
    status: str
    source: str

    def draw(self, rng: np.random.Generator, n: int) -> np.ndarray:
        lo, mid, hi = self.low, self.central, self.high
        if lo is None and hi is None:
            return np.full(n, float(mid))
        if lo == hi:
            return np.full(n, float(lo))
        return rng.triangular(lo, mid, hi, size=n)


@dataclass
class Instrument:
    instrument_id: str
    name: str
    margin: str  # "compute" or "evaluation"
    ranges: dict[str, Range] = field(default_factory=dict)

    @property
    def is_binary(self) -> bool:
        r = self.ranges.get("noise_sd")
        return r is None or (r.low is None and r.central is None and r.high is None)

    def draw(self, rng: np.random.Generator, n: int, record: dict | None = None) -> dict[str, np.ndarray]:
        """Draw n parameter worlds for this instrument.

        The order of draws is fixed: changing it changes every result for a
        given seed. If record is a dict, each raw input drawn is stored in it
        under its parameter name (used by the sensitivity analysis).
        """
        def take(key: str) -> np.ndarray:
            x = self.ranges[key].draw(rng, n)
            if record is not None:
                record[key] = x
            return x

        out: dict[str, np.ndarray] = {}
        if "detection_max" in self.ranges:
            out["detection_max"] = take("detection_max")
        else:  # satellite imagery: unconcealed rate x concealment factor
            out["detection_max"] = take("detection_unconcealed") * take("concealment_multiplier")
        if self.is_binary:
            out["noise_sd"] = np.full(n, np.nan)
            out["false_alarm"] = np.full(n, np.nan)
        else:
            out["noise_sd"] = take("noise_sd")
            out["false_alarm"] = take("false_alarm")
        for key in ("collusion_share", "collusion_multiplier"):
            out[key] = take(key) if key in self.ranges else np.full(n, 0.0 if key == "collusion_share" else 1.0)
        # Drawn last so earlier draws, and so earlier runs, are unchanged.
        out["natural_audit_rate"] = take("natural_audit_rate") if "natural_audit_rate" in self.ranges else np.full(n, np.nan)
        return out


def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(fh)]


def scenario_path(name: str) -> Path:
    return SCENARIO_DIR / f"{name}.csv"


def load_instruments(path: Path | None = None, scenario: str | None = None) -> list[Instrument]:
    """Load instruments, applying a named scenario file on top if given."""
    path = path or DATA_DIR / "placeholder_ranges.csv"
    rows = read_rows(path)
    if scenario:
        index = {(r["instrument_id"], r["parameter"]): i for i, r in enumerate(rows)}
        for r in read_rows(scenario_path(scenario)):
            key = (r["instrument_id"], r["parameter"])
            if key in index:
                rows[index[key]] = r
            else:
                rows.append(r)
    by_id: dict[str, Instrument] = {}
    for row in rows:
        iid = row["instrument_id"]
        inst = by_id.setdefault(iid, Instrument(iid, row["instrument"], margin="compute"))
        if row["parameter"] == "margin":
            inst.margin = row["central"]
            continue
        if row["status"] in ("not used", "unreported") and not (row["low"] or row["central"]):
            continue
        inst.ranges[row["parameter"]] = Range(
            _num(row["low"]), _num(row["central"]), _num(row["high"]), row["status"], row["source"],
        )
    return list(by_id.values())


def load_policy(path: Path | None = None) -> dict[str, float]:
    path = path or DATA_DIR / "policy_scenarios.csv"
    return {r["parameter"]: float(r["value"]) for r in read_rows(path)}


def load_policy_ranges(path: Path | None = None) -> dict[str, Range]:
    """Uncertain policy inputs, used only by the sensitivity analysis."""
    path = path or DATA_DIR / "policy_ranges.csv"
    return {
        r["parameter"]: Range(_num(r["low"]), _num(r["central"]), _num(r["high"]), r["status"], r["source"])
        for r in read_rows(path)
    }
