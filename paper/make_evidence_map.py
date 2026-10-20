"""Evidence map for the midterm: what kind of number backs each model input, per instrument (20 Oct 2026)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
STYLE = {  # ordinal blue ramp, validated; label in every cell so colour is never alone
    "M": ("#184f95", "white", "Measured"),
    "S": ("#2a78d6", "white", "Stand-in"),
    "G": ("#86b6ef", INK, "Guess"),
    "N": ("white", INK2, "Nothing yet"),
    "-": ("#f2f1ee", MUTED, ""),
}
cols = ["CI-02\nThird-party\nverifiers", "CI-03\nOn-chip\nattestation", "CI-04\nCompute\nmetering", "CI-05\nSatellite\nimagery"]
rows = [
    ("Catch rate, normal use",        ["S", "N", "M", "M"]),
    ("Catch rate, best evasion",      ["N", "N", "M", "N"]),
    ("Catch rate by site size",       ["-", "-", "-", "M"]),
    ("False alarms",                  ["-", "-", "M", "M"]),
    ("Meter error",                   ["-", "-", "S", "-"]),
    ("How often checked",             ["S", "S", "G", "G"]),
    ("Lenient checkers",              ["G", "-", "-", "-"]),
    ("Cost of evading",               ["-", "G", "-", "G"]),
    ("Fine compared with gain",       ["N", "N", "N", "N"]),
    ("Caught → actually punished",    ["N", "N", "N", "N"]),
]
notes = {(0, 0): "tax audits", (0, 2): "lab, 98%", (0, 3): "unhidden, 98.6%", (1, 2): "lab, 43%",
         (2, 3): "not yet used", (4, 2): "nuclear", (5, 0): "yearly", (5, 1): "every 3 months"}

fig, ax = plt.subplots(figsize=(6.4, 4.5))
cw, ch = 1.0, 0.62
for i, (label, cells) in enumerate(rows):
    y = -i * ch
    ax.text(-0.08, y + ch / 2, label, ha="right", va="center", fontsize=8.5, color=INK)
    for j, s in enumerate(cells):
        face, txt, name = STYLE[s]
        ax.add_patch(Rectangle((j * cw + 0.03, y + 0.04), cw - 0.06, ch - 0.08, facecolor=face,
                               edgecolor=(MUTED if s == "N" else face), lw=0.8, ls=(":" if s == "N" else "-")))
        sub = notes.get((i, j))
        if name:
            ax.text(j * cw + cw / 2, y + ch / 2 + (0.07 if sub else 0), name, ha="center", va="center", fontsize=7.8,
                    color=txt, fontweight="bold" if s in "MS" else "normal")
        if sub:
            ax.text(j * cw + cw / 2, y + ch / 2 - 0.12, sub, ha="center", va="center", fontsize=6.3, color=txt)
for j, c in enumerate(cols):
    ax.text(j * cw + cw / 2, ch + 0.08, c, ha="center", va="bottom", fontsize=8, color=INK, linespacing=1.15)
# bracket the two rows the sensitivity analysis ranks highest
yb = -(len(rows) - 1) * ch
ax.add_patch(Rectangle((-2.3, yb + 0.01), 2.3 + 4 * cw, 2 * ch - 0.02, fill=False, edgecolor="#eb6834", lw=1.4))
ax.text(4 * cw + 0.06, yb + ch, "No column O label\nyet. Fine vs gain\nranks first or second\nfor every instrument",
        ha="left", va="center", fontsize=7, color=INK2)
ax.set_xlim(-2.35, 5.3); ax.set_ylim(yb - 0.15, ch + 0.75)
ax.axis("off")
fig.text(0.01, 0.01, "Measured: a test of this instrument. Stand-in: measured in another regime (tax, nuclear, emissions trading). "
         "Guess: a stated scenario. Grey: not relevant to this instrument. First coded rows, 20 Oct 2026.",
         fontsize=6.6, color=MUTED, ha="left", va="bottom", wrap=True)
fig.tight_layout(rect=(0, 0.04, 1, 1))
OUT = Path(__file__).resolve().parent / "figures"
fig.savefig(OUT / "evidence_map.pdf")
