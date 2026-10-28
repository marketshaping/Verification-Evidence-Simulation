# Midterm report (Overleaf)

`main.tex` is the version for Overleaf. Figures 2 and 3 are built from `results/sixth_run`; the evidence table, the pipeline and the route diagram are drawn in LaTeX inside `main.tex`.

```bash
cd paper
python make_paper_figs.py         # figures/regime.pdf, figures/size.pdf
python poster/make_poster_fig.py  # poster figure
```

All figures use `style.py`: Latin Modern (the paper font), black and grey with one navy and one dark-red accent, error bars with caps. Edit the text in Overleaf, but rebuild figures here so they stay tied to a results folder.
