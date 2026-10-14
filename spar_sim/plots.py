"""Figure for the first run: share of compute hidden vs audit rate."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLORS = {4: "#C2410C", 200: "#1D4ED8"}


def plot_sweep(rows, instruments, rho_ref, path):
    fig, axes = plt.subplots(2, len(instruments), figsize=(4.2 * len(instruments), 7), sharex=True, sharey=False)
    for c, inst in enumerate(instruments):
        for r, cap in enumerate(("none", "flat")):
            ax = axes[r, c]
            for n in (4, 200):
                sel = sorted((x for x in rows if x["instrument_id"] == inst.instrument_id and x["N"] == n and x["cap"] == cap),
                             key=lambda x: x["rho"])
                rho = [x["rho"] for x in sel]
                ax.plot(rho, [x["evaded_mean"] for x in sel], color=COLORS[n], lw=2, label=f"N = {n} developers")
                ax.fill_between(rho, [x["evaded_p10"] for x in sel], [x["evaded_p90"] for x in sel], color=COLORS[n], alpha=0.12, lw=0)
            ax.axvline(rho_ref, color="#6B7280", ls=":", lw=1)
            ax.set_ylim(-0.02, 1.02 if inst.margin == "evaluation" else 0.42)
            ax.grid(alpha=0.25)
            if r == 0:
                ax.set_title(f"{inst.instrument_id} {inst.name}\n({inst.margin} margin)", fontsize=10)
            if r == 1:
                ax.set_xlabel("Audit rate per developer per year (rho)")
            if c == 0:
                ax.set_ylabel(("No penalty cap" if cap == "none" else "Flat penalty cap") + "\nshare hidden (mean, p10-p90)")
    axes[0, 1].legend(fontsize=8, frameon=False, loc="upper right")
    fig.suptitle("First run, placeholder ranges: share of compute (or excess risk-weighted compute) hidden", fontsize=11)
    fig.text(0.5, 0.005, "Most ranges are scenarios, not evidence. See data/placeholder_ranges.csv. Dotted line: reference audit rate.",
             ha="center", fontsize=8, color="#6B7280")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(path, dpi=150)
    plt.close(fig)
