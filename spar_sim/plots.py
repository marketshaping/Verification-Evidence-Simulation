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


def _fmt_multiple(ax):
    ax.set_xscale("log")
    ticks = [1, 2, 5, 10, 20, 50]
    ax.set_xticks(ticks, [f"{t}×" for t in ticks])
    ax.minorticks_off()


def plot_regime(rows, path, current_multiple=5.0, worlds=2000):
    """Figure 5. Fine needed for the combined regime: multiplied vs route choice."""
    titles = {"main": "Main ranges", "worst_case": "Worst case"}
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    fig, axes = plt.subplots(1, len(scenarios), figsize=(4.6 * len(scenarios), 2.9), sharex=True, squeeze=False)
    items = [("multiplied", "honest", "Checks multiplied\n(every check sees every cheater)", MUTED),
             ("route", "honest", "Cheater picks one route,\nhonest verifier", "#2a78d6"),
             ("route", "lenient", "Cheater picks one route,\nlenient verifier", "#eb6834")]
    for ax, scen in zip(axes[0], scenarios):
        for y, (kind, ver, label, col) in enumerate(items[::-1]):
            r = next(x for x in rows if x["scenario"] == scen and x["verifier"] == ver)
            lo, mid, hi = (r[f"fine_needed_{kind}_p{q}"] for q in (10, 50, 90))
            ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round")
            ax.plot([mid], [y], "o", ms=8, color=col, mec="white", mew=2, zorder=3)
            ax.text(mid, y + 0.28, f"{mid:.1f}×", ha="center", va="bottom", fontsize=7.5, color=INK_2)
        ax.axvline(current_multiple, color=INK_2, ls=":", lw=1)
        ax.set_yticks(range(len(items)), [i[2] for i in items[::-1]], fontsize=7.5)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="y", visible=False)
        _fmt_multiple(ax)
        ax.set_xlim(1, 30)
        ax.set_ylim(-0.5, len(items) - 0.2)
        ax.set_title(titles.get(scen, scen), loc="left")
        ax.set_xlabel("Fine needed, as a multiple of the gain from hiding")
    for ax in axes[0][1:]:
        ax.set_yticklabels([])
    fig.suptitle("Figure 5. Multiplying catch rates understates the fine a combined regime needs", fontsize=10.5, x=0.01, ha="left")
    _footer(fig, f"Verifier + attested metering + satellite imagery. Dot: median over {worlds:,} draws; line: 10th–90th percentile. "
                 "Dotted line: the main assumption, fine = 5× gain.")
    fig.tight_layout(rect=(0, 0.06, 1, 0.92))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_weakest_link(head_rows, inst_rows, route_labels, path, verifier="honest", worlds=2000):
    """Figure 6. Which route cheaters use, and what perfecting or removing each instrument does."""
    titles = {"main": "Main ranges", "worst_case": "Worst case"}
    scenarios = list(dict.fromkeys(r["scenario"] for r in head_rows))
    fig, axes = plt.subplots(len(scenarios), 2, figsize=(9.4, 2.4 * len(scenarios) + 0.9),
                             gridspec_kw={"width_ratios": [1, 1.25]}, squeeze=False)
    for k, scen in enumerate(scenarios):
        h = next(r for r in head_rows if r["scenario"] == scen and r["verifier"] == verifier)
        ax = axes[k, 0]
        routes = list(route_labels)
        shares = [100 * h[f"share_route_{r}"] for r in routes]
        y = np.arange(len(routes))[::-1]
        ax.set_axisbelow(True)
        ax.barh(y, shares, color="#2a78d6", height=0.55)
        for yi, s in zip(y, shares):
            ax.text(s + 1.5, yi, f"{s:.0f}%", va="center", fontsize=7.5, color=INK_2)
        ax.set_yticks(y, [route_labels[r] for r in routes], fontsize=7.5)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="y", visible=False)
        ax.set_xlim(0, 110)
        ax.set_title(f"{titles.get(scen, scen)}: route that sets the fine (% of draws)", loc="left", fontsize=9)

        ax = axes[k, 1]
        sel = [r for r in inst_rows if r["scenario"] == scen and r["verifier"] == verifier]
        y = np.arange(len(sel))[::-1]
        for yi, r in zip(y, sel):
            now, perf, rem = r["fine_needed_now_p50"], r["fine_needed_if_perfect_p50"], r["fine_needed_if_removed_p50"]
            ax.plot([perf, rem], [yi, yi], color=GRID, lw=3, solid_capstyle="round", zorder=1)
            ax.plot([perf], [yi], "o", ms=7, color="#1baf7a", mec="white", mew=1.5, zorder=3, label="if perfect" if yi == y[0] else None)
            ax.plot([rem], [yi], "o", ms=7, color="#eb6834", mec="white", mew=1.5, zorder=3, label="if removed" if yi == y[0] else None)
            ax.plot([now], [yi], "|", ms=12, mew=2, color=INK, zorder=4, label="now" if yi == y[0] else None)
            ax.text(min(rem * 1.12, 55), yi, f"{rem:.1f}×", va="center", fontsize=7, color=INK_2)
        ax.set_yticks(y, [r["label"] for r in sel], fontsize=7.5)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="y", visible=False)
        _fmt_multiple(ax)
        ax.set_xlim(1, 80)
        ax.set_title("Fine needed (median) if one instrument changed", loc="left", fontsize=9)
        if k == 0:
            handles, labels = ax.get_legend_handles_labels()
    fig.suptitle("Figure 6. The weakest link sets the fine: improve the instrument on the cheapest route",
                 fontsize=10.5, x=0.01, ha="left")
    fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.99, 0.955), ncol=3, fontsize=7.5,
               handletextpad=0.3, columnspacing=1.0)
    _footer(fig, f"Combined regime, {verifier} verifier, {worlds:,} draws. 'Perfect' = that instrument always catches what it can see; "
                 "it still checks at its normal rate and still can't see routes outside its reach.")
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_size(rows, days_fn, path, current_multiple=5.0, worlds=2000):
    """Figure 7. Fine needed against the size of the hidden run."""
    titles = {"main": "Main ranges", "worst_case": "Worst case"}
    cols = {"main": "#2a78d6", "worst_case": "#eb6834"}
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for scen in dict.fromkeys(r["scenario"] for r in rows):
        sel = [r for r in rows if r["scenario"] == scen and r["verifier"] == "honest"]
        g = np.array([r["gpus"] for r in sel])
        ax.fill_between(g, [r["fine_needed_p10"] for r in sel], [r["fine_needed_p90"] for r in sel],
                        color=cols[scen], alpha=0.13, lw=0)
        ax.plot(g, [r["fine_needed_p50"] for r in sel], color=cols[scen], lw=2, label=titles.get(scen, scen))
    ax.axhline(current_multiple, color=INK_2, ls=":", lw=1)
    ax.text(1.05e3, current_multiple * 1.07, f"fine = {current_multiple:g}× gain (main assumption)", fontsize=7, color=INK_2)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1e3, 1e6); ax.set_ylim(1, 30)
    ax.set_yticks([1, 2, 5, 10, 20], ["1×", "2×", "5×", "10×", "20×"]); ax.minorticks_off()
    ticks = [1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6]
    ax.set_xticks(ticks, ["1k", "3k", "10k", "30k", "100k", "300k", "1M"])
    ax.set_xlabel("Size of the hidden run (H100-class GPUs)")
    ax.set_ylabel("Fine needed, as a multiple of the gain from hiding")
    top = ax.secondary_xaxis("top")
    top.set_xticks(ticks, [_days_label(days_fn(t)) for t in ticks], fontsize=7, color=INK_2)
    top.set_xlabel("Time that size needs to reach 10²⁶ FLOP", fontsize=8, color=INK_2)
    top.tick_params(length=0, which="both")
    top.minorticks_off()
    ax.legend(fontsize=8, loc="upper right")
    fig.suptitle("Figure 7. Small, slow runs are the hard ones to deter", fontsize=10.5, x=0.01, ha="left")
    _footer(fig, f"Combined regime, honest verifier, {worlds:,} draws; line: median, band: 10th–90th percentile. The cheater splits the run "
                 "across as many hidden sites as suits it; imagery finds half of sites at 3–10 MW; each extra site costs 1–8% of the gain. "
                 "Time axis assumes 40% utilisation.")
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def _days_label(days):
    if days >= 365:
        return f"{days / 365:.1f} yr"
    if days >= 60:
        return f"{days / 30.4:.0f} mo"
    return f"{days:.0f} d"
