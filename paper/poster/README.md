# Poster figure (Technical AI Governance Forum, 14–15 Nov 2026)

`poster_regime.pdf` (vector, use this) and `poster_regime.png` (300 dpi). It is drawn 30 × 13 cm in Latin Modern (the paper font) at 18–24 pt, using the shared style in `paper/style.py`. Change `WIDTH_CM` and `HEIGHT_CM` in `make_poster_fig.py` once the poster format is known, then run `python make_poster_fig.py`.

**Suggested headline:** Multiplying catch rates makes a verification regime look stronger than it is.

**Suggested caption (about 60 words):**
A developer facing a verifier, chip metering and satellite imagery doesn't meet each check in turn: it picks the easiest way past them, such as breaking the chip checks or using a hidden site. Dots show the fine needed for honest reporting to pay (markers: median over 2,000 draws; bars: 10th–90th percentiles). Most inputs are placeholders until the evidence rows are complete.

Source: `results/sixth_run/regime.csv`, honest verifier.
