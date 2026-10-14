"""Load instrument ranges and policy scenarios, and draw parameter worlds.

Every range in data/placeholder_ranges.csv is drawn from a triangular
distribution (low, central, high). A range marked "evidence" comes from a
coded row; a range marked "scenario" is an assumption and must be reported as
one. The status column is kept so results can say which is which.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


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

    def draw(self, rng: np.random.Generator, n: int) -> dict[str, np.ndarray]:
        """Draw n parameter worlds for this instrument."""
        out: dict[str, np.ndarray] = {}
        if "detection_max" in self.ranges:
            out["detection_max"] = self.ranges["detection_max"].draw(rng, n)
        else:  # satellite imagery: unconcealed rate x concealment factor
            out["detection_max"] = (
                self.ranges["detection_unconcealed"].draw(rng, n)
                * self.ranges["concealment_multiplier"].draw(rng, n)
            )
        if self.is_binary:
            out["noise_sd"] = np.full(n, np.nan)
            out["false_alarm"] = np.full(n, np.nan)
        else:
            out["noise_sd"] = self.ranges["noise_sd"].draw(rng, n)
            out["false_alarm"] = self.ranges["false_alarm"].draw(rng, n)
        for key in ("collusion_share", "collusion_multiplier"):
            out[key] = self.ranges[key].draw(rng, n) if key in self.ranges else np.full(n, 0.0 if key == "collusion_share" else 1.0)
        return out


def load_instruments(path: Path | None = None) -> list[Instrument]:
    path = path or DATA_DIR / "placeholder_ranges.csv"
    by_id: dict[str, Instrument] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            iid = row["instrument_id"].strip()
            inst = by_id.setdefault(iid, Instrument(iid, row["instrument"].strip(), margin="compute"))
            if row["parameter"] == "margin":
                inst.margin = row["central"].strip()
                continue
            if row["status"].strip() in ("not used", "unreported") and not (row["low"] or row["central"]):
                continue
            inst.ranges[row["parameter"].strip()] = Range(
                _num(row["low"]), _num(row["central"]), _num(row["high"]),
                row["status"].strip(), row["source"].strip(),
            )
    return list(by_id.values())


def load_policy(path: Path | None = None) -> dict[str, float]:
    path = path or DATA_DIR / "policy_scenarios.csv"
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["parameter"]: float(r["value"]) for r in csv.DictReader(fh)}
