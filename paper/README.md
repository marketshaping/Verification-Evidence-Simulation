# Midterm report (Overleaf)

`main.tex` is the version uploaded to Overleaf on 20 Oct 2026. The figures in `figures/` are built from `results/fifth_run`:

```bash
cd paper
python make_evidence_map.py   # Figure 2: what backs each model input
python make_paper_figs.py     # Figures 3 and 4: combined regime, run size
```

Figure 1 (the pipeline) is drawn in TikZ inside `main.tex`. Edit the text in Overleaf, but rebuild the figures here, so they stay tied to a results folder.
