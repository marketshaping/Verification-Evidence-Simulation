"""Paper Figures 3 and 4 (6.3 in wide), drawn from results/sixth_run."""
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import style

style.apply(9)
HERE = Path(__file__).resolve().parent
RUN = HERE.parent / "results" / "sixth_run"
OUT = HERE / "figures"
rows = lambda f: list(csv.DictReader(open(RUN / f)))


def fine_axis(ax, lo=0.85, hi=25):
    ax.set_xscale("log"); ax.set_xlim(lo, hi); ax.minorticks_off()
    ticks = [1, 2, 5, 10, 20]
    ax.set_xticks(ticks, [f"{t}$\\times$" for t in ticks])


# Figure 3: combined regime
reg = rows("regime.csv")
items = [("route", "lenient", "Route choice, lenient verifier", style.ACCENT2, "s"),
         ("route", "honest", "Route choice, honest verifier", style.ACCENT, "o"),
         ("multiplied", "honest", "Catch rates multiplied", style.GREY, "D")]
fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.0), sharey=True)
for ax, scen, title in zip(axes, ("main", "worst_case"), ("(a) Middle-range inputs", "(b) Worst case")):
    for y, (kind, ver, label, col, mk) in enumerate(items):
        r = next(x for x in reg if x["scenario"] == scen and x["verifier"] == ver)
        lo, mid, hi = (float(r[f"fine_needed_{kind}_p{q}"]) for q in (10, 50, 90))
        ax.errorbar([mid], [y], xerr=[[mid - lo], [hi - mid]], fmt=mk, color=col, ms=4.5,
                    mfc=col if kind == "route" else "white", capsize=2.5, elinewidth=0.9, capthick=0.9)
        ax.text(mid, y + 0.28, f"{mid:.1f}$\\times$", ha="center", va="bottom", fontsize=8)
    ax.axvline(5, color=style.GREY, ls=(0, (2, 2)), lw=0.7)
    fine_axis(ax)
    ax.set_ylim(-0.5, 2.75)
    ax.set_yticks(range(3), [i[2] for i in items]); ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_title(title, loc="left")
fig.tight_layout(rect=(0, 0.09, 1, 1))
fig.supxlabel("Fine needed for honest reporting to pay (multiple of the gain from hiding)", fontsize=9, y=0.02)
fig.savefig(OUT / "regime.pdf")

# Figure 4: run size
size = rows("size.csv")
DAYS = lambda g: 1e26 / (g * 989e12 * 0.4) / 86400
fig, ax = plt.subplots(figsize=(6.3, 3.0))
for scen, col, ls, name in (("main", style.ACCENT, "-", "Middle-range inputs"), ("worst_case", style.ACCENT2, "--", "Worst case")):
    s = [r for r in size if r["scenario"] == scen]
    g = np.array([float(r["gpus"]) for r in s])
    lo = [float(r["fine_needed_p10"]) for r in s]; hi = [float(r["fine_needed_p90"]) for r in s]
    ax.plot(g, [float(r["fine_needed_p50"]) for r in s], color=col, ls=ls, lw=1.4, label=f"{name} (median)")
    ax.plot(g, lo, color=col, ls=ls, lw=0.5, alpha=0.6); ax.plot(g, hi, color=col, ls=ls, lw=0.5, alpha=0.6)
ax.plot([], [], color=style.GREY, lw=0.5, label="10th and 90th percentiles")
ax.axhline(5, color=style.GREY, ls=(0, (2, 2)), lw=0.7)
ax.text(9.5e5, 5.25, "fine = 5$\\times$ gain", ha="right", va="bottom", fontsize=8, color=style.GREY)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e3, 1e6); ax.set_ylim(1, 30); ax.minorticks_off()
ticks = [1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6]
ax.set_xticks(ticks, ["1k", "3k", "10k", "30k", "100k", "300k", "1M"])
ax.set_yticks([1, 2, 5, 10, 20], ["1$\\times$", "2$\\times$", "5$\\times$", "10$\\times$", "20$\\times$"])
ax.set_xlabel("Size of the hidden run (H100-class GPUs)")
ax.set_ylabel("Fine needed (multiple of gain)")
lab = lambda d: f"{d/365:.1f} yr" if d >= 365 else (f"{d/30.4:.0f} mo" if d >= 60 else f"{d:.0f} d")
top = ax.secondary_xaxis("top"); top.set_xticks(ticks, [lab(DAYS(t)) for t in ticks]); top.minorticks_off()
top.set_xlabel("Time that size needs to reach $10^{26}$ FLOP")
ax.legend(loc="upper right", bbox_to_anchor=(1, 0.9))
fig.tight_layout()
fig.savefig(OUT / "size.pdf")
print("ok")
