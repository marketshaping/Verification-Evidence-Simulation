"""Paper versions of Figures 3 and 4 (6.3 in wide), drawn from results/fifth_run of the simulation repo."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUN = Path(__file__).resolve().parent.parent / "results" / "fifth_run"
OUT = Path(__file__).resolve().parent / "figures"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
                     "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.titlecolor": INK})
rows = lambda f: list(csv.DictReader(open(RUN / f)))

def mult_axis(ax, ticks, lo, hi):
    ax.set_xscale("log"); ax.set_xlim(lo, hi); ax.minorticks_off()
    ax.set_xticks(ticks, [f"{t:g}×" for t in ticks])

# Figure 3: combined regime
reg = rows("regime.csv")
fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.3), sharey=True)
items = [("route", "lenient", "Cheater picks a route,\nlenient verifier", ORANGE),
         ("route", "honest", "Cheater picks a route,\nhonest verifier", BLUE),
         ("multiplied", "honest", "Catch rates multiplied", MUTED)]
for ax, scen, title in zip(axes, ("main", "worst_case"), ("Middle-range inputs", "Worst case")):
    for y, (kind, ver, label, col) in enumerate(items):
        r = next(x for x in reg if x["scenario"] == scen and x["verifier"] == ver)
        lo, mid, hi = (float(r[f"fine_needed_{kind}_p{q}"]) for q in (10, 50, 90))
        ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle="round")
        ax.plot([mid], [y], "o", ms=6.5, color=col, mec="white", mew=1.5, zorder=3)
        ax.text(mid, y + 0.3, f"{mid:.1f}×", ha="center", va="bottom", fontsize=7.5, color=INK2)
    ax.axvline(5, color=INK2, ls=":", lw=1)
    mult_axis(ax, [1, 2, 5, 10, 20], 0.85, 25)
    ax.set_ylim(-0.5, 2.85); ax.grid(axis="y", visible=False); ax.tick_params(axis="y", length=0)
    ax.set_yticks(range(3), [i[2] for i in items], fontsize=7.5)
    ax.set_title(title, loc="left")
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.supxlabel("Fine needed, as a multiple of the gain from hiding", fontsize=8, color=INK2, y=0.03)
fig.savefig(OUT / "regime.pdf")

# Figure 4: run size
size = rows("size.csv")
DAYS = lambda g: 1e26 / (g * 989e12 * 0.4) / 86400
fig, ax = plt.subplots(figsize=(6.3, 3.1))
for scen, col, name in (("main", BLUE, "Middle-range inputs"), ("worst_case", ORANGE, "Worst case")):
    s = [r for r in size if r["scenario"] == scen]
    g = np.array([float(r["gpus"]) for r in s])
    ax.fill_between(g, [float(r["fine_needed_p10"]) for r in s], [float(r["fine_needed_p90"]) for r in s], color=col, alpha=0.13, lw=0)
    ax.plot(g, [float(r["fine_needed_p50"]) for r in s], color=col, lw=2, label=name)
ax.axhline(5, color=INK2, ls=":", lw=1)
ax.text(9.5e5, 5.25, "fine = 5× gain (main assumption)", ha="right", va="bottom", fontsize=7, color=INK2)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e3, 1e6); ax.set_ylim(1, 30); ax.minorticks_off()
ticks = [1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6]
ax.set_xticks(ticks, ["1k", "3k", "10k", "30k", "100k", "300k", "1M"])
ax.set_yticks([1, 2, 5, 10, 20], ["1×", "2×", "5×", "10×", "20×"])
ax.set_xlabel("Size of the hidden run (H100-class GPUs)")
ax.set_ylabel("Fine needed (× gain)")
lab = lambda d: f"{d/365:.1f} yr" if d >= 365 else (f"{d/30.4:.0f} mo" if d >= 60 else f"{d:.0f} d")
top = ax.secondary_xaxis("top"); top.set_xticks(ticks, [lab(DAYS(t)) for t in ticks], fontsize=7, color=INK2)
top.minorticks_off(); top.tick_params(length=0, which="both")
top.set_xlabel("Time that size needs to reach 10²⁶ FLOP", fontsize=7.5, color=INK2)
ax.legend(fontsize=7.5, loc="upper right", bbox_to_anchor=(1, 0.93))
fig.tight_layout()
fig.savefig(OUT / "size.pdf")
print("ok")
