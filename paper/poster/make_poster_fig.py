"""Poster figure for the Technical AI Governance Forum (14-15 Nov 2026).

One message: multiplying catch rates makes a verification regime look stronger
than it is. Drawn from results/sixth_run/regime.csv (honest verifier).
Sized for a poster column about 30 cm wide; change WIDTH_CM / HEIGHT_CM once the
poster format is known.
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import matplotlib.pyplot as plt  # noqa: E402
import style  # noqa: E402

WIDTH_CM, HEIGHT_CM = 30, 13
RUN = HERE.parent.parent / "results" / "sixth_run"
style.apply(22)

rows = {r["scenario"]: r for r in csv.DictReader(open(RUN / "regime.csv")) if r["verifier"] == "honest"}
fig, ax = plt.subplots(figsize=(WIDTH_CM / 2.54, HEIGHT_CM / 2.54))
ticks, labels, y = [], [], 0
for scen, name in (("main", "Middle-range inputs"), ("worst_case", "Worst case")):
    r = rows[scen]
    ax.text(0.0, y + 0.75, name, transform=ax.get_yaxis_transform(), fontsize=22, style="italic", va="center")
    for kind, label, col, mk, filled in (("route", "Cheater takes the\neasiest way past", style.ACCENT, "o", True),
                                         ("multiplied", "Catch rates\nmultiplied", style.GREY, "D", False)):
        lo, mid, hi = (float(r[f"fine_needed_{kind}_p{q}"]) for q in (10, 50, 90))
        ax.errorbar([mid], [y], xerr=[[mid - lo], [hi - mid]], fmt=mk, color=col, ms=13,
                    mfc=col if filled else "white", mew=2, capsize=7, elinewidth=2, capthick=2)
        ax.text(hi * 1.1, y, f"{mid:.1f}$\\times$", va="center", fontsize=24)
        ticks.append(y); labels.append(label)
        y -= 1
    y -= 0.8
ax.axvline(5, color=style.GREY, ls=(0, (3, 3)), lw=1.5)
ax.text(5.3, ticks[-1] - 0.7, "fine = 5$\\times$ gain", fontsize=18, color=style.GREY, va="center")
ax.set_xscale("log"); ax.set_xlim(0.9, 25); ax.minorticks_off()
ax.set_xticks([1, 2, 5, 10, 20], ["1$\\times$", "2$\\times$", "5$\\times$", "10$\\times$", "20$\\times$"])
ax.set_yticks(ticks, labels); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.set_ylim(ticks[-1] - 1.1, 1.2)
ax.set_xlabel("Fine needed for honest reporting to pay ($\\times$ gain)")
for a in ("xtick.major.width", "axes.linewidth"):
    pass
ax.tick_params(axis="x", width=1.2, length=6)
ax.spines["bottom"].set_linewidth(1.2)
fig.savefig(HERE / "poster_regime.pdf")
fig.savefig(HERE / "poster_regime.png", dpi=300)
print("ok")
