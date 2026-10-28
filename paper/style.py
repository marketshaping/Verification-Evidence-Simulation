"""Shared figure style for the paper and poster: classic academic look.

Serif type that matches the LaTeX text (Latin Modern, falling back to Times or
DejaVu Serif), black text and axes, one dark accent and greys, thin lines,
error bars with caps, ticks outward, no background bands.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLACK = "#000000"
GREY = "#6e6e6e"
LIGHT = "#d9d9d9"
ACCENT = "#1f3a5f"   # dark navy: the result the figure is about
ACCENT2 = "#9b2226"  # dark red: the second series, always also dashed


def apply(base_size=9):
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Latin Modern Roman", "CMU Serif", "Times New Roman", "Times", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": base_size,
        "axes.labelsize": base_size,
        "axes.titlesize": base_size,
        "axes.titleweight": "normal",
        "xtick.labelsize": base_size * 0.9,
        "ytick.labelsize": base_size * 0.9,
        "legend.fontsize": base_size * 0.9,
        "text.color": BLACK, "axes.labelcolor": BLACK, "axes.edgecolor": BLACK,
        "xtick.color": BLACK, "ytick.color": BLACK,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 3, "ytick.major.size": 3, "xtick.direction": "out", "ytick.direction": "out",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False,
        "legend.frameon": False,
        "lines.linewidth": 1.2,
        "pdf.fonttype": 3, "ps.fonttype": 3,  # Type 3 embeds the OpenType Latin Modern cleanly
        "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
    })
