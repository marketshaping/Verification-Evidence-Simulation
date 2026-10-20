"""Figures. All static PNGs for the report; light background, colour-blind-checked palette.

Instrument colours are fixed by instrument, never by rank, so the same
instrument has the same colour in every figure.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# Reference categorical palette, first three slots (validated all-pairs, light mode).
INSTRUMENT_COLORS = {"CI-02": "#2a78d6", "CI-03+04": "#eb6834", "CI-05": "#1baf7a"}
N_COLORS = {4: "#2a78d6", 200: "#eb6834"}
INK, INK_2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK_2, "xtick.color": INK_2,
    "ytick.color": INK_2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK,
})


def _footer(fig, text):
    fig.text(0.01, 0.01, text, ha="left", va="bottom", fontsize=7, color=MUTED, wrap=True)


def plot_sweep(rows, instruments, rho_ref, path, run_label=""):
    """Share hidden against one shared audit rate (the first- and second-run figure)."""
    fig, axes = plt.subplots(2, len(instruments), figsize=(4.2 * len(instruments), 7), sharex=True)
    for c, inst in enumerate(instruments):
        for r, cap in enumerate(("none", "flat")):
            ax = axes[r, c]
            for n in (4, 200):
                sel = sorted((x for x in rows if x["instrument_id"] == inst.instrument_id and x["N"] == n and x["cap"] == cap),
                             key=lambda x: x["rho"])
                rho = [x["rho"] for x in sel]
                ax.plot(rho, [x["evaded_mean"] for x in sel], color=N_COLORS[n], lw=2, label=f"{n} developers")
                ax.fill_between(rho, [x["evaded_p10"] for x in sel], [x["evaded_p90"] for x in sel], color=N_COLORS[n], alpha=0.12, lw=0)
            ax.axvline(rho_ref, color=MUTED, ls=":", lw=1)
            ax.set_ylim(-0.02, 1.02 if inst.margin == "evaluation" else 0.42)
            if r == 0:
                ax.set_title(f"{inst.instrument_id} {inst.name}\n({inst.margin} margin)")
            if r == 1:
                ax.set_xlabel("Audit rate per developer per year")
            if c == 0:
                ax.set_ylabel(("No fine cap" if cap == "none" else "Flat fine cap") + "\nshare hidden (mean, 10th–90th)")
    axes[0, 1].legend(fontsize=8, loc="upper right")
    fig.suptitle(f"{run_label}: share of compute (or excess risk-weighted compute) hidden".strip(": "), fontsize=11)
    _footer(fig, "Most ranges are scenarios, not evidence. See inputs/placeholder_ranges.csv. Dotted line: reference audit rate.")
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_fine_needed(curves, natural, path, current_multiple=5.0):
    """Figure 1. curves[scenario][instrument_id] = dict(rho, p10, p50, p90, name, captured=optional)."""
    scenarios = list(curves)
    titles = {"main": "Main ranges", "worst_case": "Worst case: cheater picks the weakest route"}
    fig, axes = plt.subplots(1, len(scenarios), figsize=(5.2 * len(scenarios), 4.3), sharey=True, squeeze=False)
    for ax, scen in zip(axes[0], scenarios):
        for iid, c in curves[scen].items():
            col = INSTRUMENT_COLORS[iid]
            ax.fill_between(c["rho"], c["p10"], c["p90"], color=col, alpha=0.13, lw=0)
            ax.plot(c["rho"], c["p50"], color=col, lw=2, label=f"{iid} {c['name']}")
            if "captured" in c:
                ax.plot(c["rho"], c["captured"]["p50"], color=col, lw=2, ls="--", label=f"{iid} with a lenient verifier")
            r0 = natural[scen][iid]
            y0 = np.interp(r0, c["rho"], c["p50"])
            ax.plot([r0], [y0], "o", ms=8, color=col, mec="white", mew=2, zorder=5)
        ax.axhline(current_multiple, color=INK_2, ls=":", lw=1)
        ax.text(0.05, current_multiple * 1.08, f"fine = {current_multiple:g}× gain (main assumption)", fontsize=7, color=INK_2)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(0.05, 1.08); ax.set_ylim(1, 1000)
        ax.set_xticks([0.05, 0.1, 0.25, 0.5, 1]); ax.set_xticklabels(["0.05", "0.1", "0.25", "0.5", "1"])
        ax.set_yticks([1, 2, 5, 10, 20, 50, 100, 1000]); ax.set_yticklabels(["1×", "2×", "5×", "10×", "20×", "50×", "100×", "1000×"])
        ax.set_xlabel("Chance a developer is checked in a year")
        ax.set_title(titles.get(scen, scen))
    axes[0, 0].set_ylabel("Fine needed, as a multiple of the gain from hiding")
    axes[0, 0].legend(fontsize=7, loc="upper right")
    fig.suptitle("Figure 1. How big the fine must be for honest reporting to pay", fontsize=11, x=0.01, ha="left")
    _footer(fig, "Line: median over parameter draws; band: 10th–90th percentile. Dot: the instrument's normal checking rate. "
                 "Fine needed = 1 / (checking rate × catch rate), assuming every caught developer is punished.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_noise(sigmas, curves, evidence_band, path):
    """Figure 2. curves = {label: hidden share array}."""
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    ax.axvspan(*[100 * x for x in evidence_band], color=GRID, alpha=0.7, lw=0)
    ax.text(100 * np.mean(evidence_band), 0.2, "nuclear accountancy\nrange (AN-04)", ha="center", fontsize=7, color=INK_2)
    for (label, y), col in zip(curves.items(), ("#2a78d6", "#eb6834")):
        ax.plot(100 * sigmas, 100 * y, color=col, lw=2, label=label)
        ax.text(100 * sigmas[-1], 100 * y[-1], "  " + label, va="center", fontsize=7, color=INK_2)
    ax.plot(100 * sigmas, 100 * sigmas, color=MUTED, lw=1, ls=":")
    ax.text(100 * sigmas[-1] * 0.62, 100 * sigmas[-1] * 0.72, "hidden = meter error", ha="right", fontsize=7, color=MUTED)
    ax.set_xlabel("Meter error (% of true compute, 1 standard deviation)")
    ax.set_ylabel("Compute hidden, % of total")
    ax.set_xlim(0, 100 * sigmas[-1]); ax.set_ylim(0, None)
    ax.set_title("Figure 2. Small cheating that checks every year cannot remove", loc="left")
    _footer(fig, "CI-03+04 attested metering, 200 developers, checked yearly, fine 5× gain, catch rate 0.70 "
                 "(central). Developers under-report up to the alarm threshold.")
    fig.tight_layout(rect=(0, 0.06, 0.88, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_few_vs_many(rows, instrument_id, name, path):
    """Figure 3. Few large vs many small developers, with and without a flat fine cap."""
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6), sharey=True)
    for ax, cap, title in zip(axes, ("none", "flat"), ("No cap on fines", "Flat cap on fines")):
        for n in (4, 200):
            sel = sorted((x for x in rows if x["instrument_id"] == instrument_id and x["N"] == n and x["cap"] == cap),
                         key=lambda x: x["rho"])
            rho = np.array([x["rho"] for x in sel])
            ax.plot(rho, [100 * x["evaded_mean"] for x in sel], color=N_COLORS[n], lw=2,
                    ls=("--" if n == 4 else "-"), zorder=(3 if n == 4 else 2),
                    label=("4 large developers" if n == 4 else "200 small developers"))
        ax.set_title(title, loc="left")
        ax.set_xlabel("Chance a developer is checked in a year")
        ax.set_xlim(0, 1)
    axes[0].set_ylabel("Compute hidden, % of total")
    axes[1].legend(fontsize=8, loc="center right")
    fig.suptitle(f"Figure 3. A flat fine cap fails when a few large developers dominate ({instrument_id} {name})",
                 fontsize=10, x=0.01, ha="left")
    _footer(fig, "Same total compute in both markets. Flat cap = 5% of the industry's yearly permit bill; "
                 "a cap that scales with size (EU AI Act style) behaves like no cap. Mean over 2,000 parameter draws; without a cap the two lines coincide.")
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_sensitivity(rows, instruments, path):
    """Figure 4. Which unknown matters most, per instrument."""
    tag = {"evidence": " (measured)", "analogue": " (stand-in)", "scenario": " (guess)"}
    fig, axes = plt.subplots(len(instruments), 1, figsize=(6.4, 2.0 * len(instruments) + 0.8), squeeze=False)
    for ax, inst in zip(axes[:, 0], instruments):
        sel = [r for r in rows if r["instrument_id"] == inst.instrument_id][:6][::-1]
        y = np.arange(len(sel))
        ax.barh(y, [r["abs_spearman"] for r in sel], color=INSTRUMENT_COLORS[inst.instrument_id], height=0.6)
        for yi, r in zip(y, sel):
            ax.text(r["abs_spearman"] + 0.015, yi, f"{r['abs_spearman']:.2f}", va="center", fontsize=7, color=INK_2)
        ax.set_yticks(y, [r["label"] + tag.get(r["status"], "") for r in sel], fontsize=7.5)
        ax.tick_params(axis="y", length=0)
        ax.set_xlim(0, 1)
        ax.grid(axis="y", visible=False)
        ax.set_title(f"{inst.instrument_id} {inst.name}", loc="left")
    axes[-1, 0].set_xlabel("Strength of link with compute hidden and not caught (|rank correlation|)")
    fig.suptitle("Figure 4. Which unknown inputs move the result most", fontsize=11, x=0.01, ha="left")
    _footer(fig, "All uncertain inputs drawn together: instrument ranges, checking rate, fine 1–20× gain, chance of\n"
                 "punishment 0.3–1. 200 developers. The ranking depends on how wide each range is.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(path, dpi=200)
    plt.close(fig)
