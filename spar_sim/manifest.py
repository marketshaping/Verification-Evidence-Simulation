"""Record what produced a results folder, so any number can be traced and rerun.

Each run writes results/<name>/manifest.json (command, seed, code version,
package versions, a fingerprint of every input file) and copies the input
files to results/<name>/inputs/.
"""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from .params import DATA_DIR

ROOT = DATA_DIR.parent
PACKAGES = ("numpy", "scipy", "matplotlib")


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(out: Path, args: dict, extra: dict | None = None) -> dict:
    inputs = sorted(p for p in DATA_DIR.rglob("*.csv"))
    dest = out / "inputs"
    if dest.exists():
        shutil.rmtree(dest)
    for p in inputs:
        target = dest / p.relative_to(DATA_DIR)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    status = _git("status", "--porcelain")
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": "python -m spar_sim.run " + " ".join(sys.argv[1:]),
        "args": {k: str(v) for k, v in args.items()},
        "git_commit": _git("rev-parse", "HEAD"),
        "uncommitted_changes": bool(status) if status is not None else None,
        "python": platform.python_version(),
        "packages": {p: metadata.version(p) for p in PACKAGES},
        "inputs_sha256": {str(p.relative_to(DATA_DIR)): _sha256(p) for p in inputs},
        **(extra or {}),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
