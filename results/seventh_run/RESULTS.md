# Seventh run: first coded inputs from the analogue rows (25 November 2026)

**Status: still mostly guesses.** This run adds the first values taken from coded analogue rows. Both come from analogues that differ from compute in important ways, explained below. Most other inputs are unchanged guesses. To rerun: `python -m spar_sim.run --out results/seventh_run`.

## What changed

| Input | Was | Now | From |
|---|---|---|---|
| How often a public body rechecks a verified report | not in the model | **1.3% a year**, fixed | AN-02, Joon's row (EU ETS: 141 inspection visits across 10,569 installations in 2019) |
| How quickly satellite detection rises with site size | 1.5 / 2.0 / 3.0 (guess) | **1.0 / 1.5 / 2.0** | AN-05, Vir's row (Global Fishing Watch) |
| Cost of each extra hidden site | 1–8% of the gain | **3–15%** (placeholder, range still to agree with Vir) | 18 Nov call: "a higher cost of splitting a run" |
| Satellite false alarms (recorded only) | 1% | 1–2% | AN-05 |

**New output:** `split_cost.csv` and Figure 8 show the fine needed at every splitting cost from 0% to 30% per site. Any range agreed with Vir can be read straight off it.

Nothing else changed. The 1.3% recheck is a fixed value and uses no random draws, so every input keeps its random values from the sixth run. That makes each change below traceable to one input. The honest-verifier results for each instrument, and the combined regime without run size, are identical to the sixth run.

## Result 1: a 1.3% public recheck barely helps against a lenient verifier

AN-02 shows that in EU emissions trading the hired verifier checks every report. The authority's own recheck reaches only about 1.3% of installations a year. In the model, that recheck is the only thing that can catch what a lenient verifier lets through. It is assumed to catch as well as an honest verifier, which is generous.

| Fine needed (median), lenient verifier | Sixth run | Seventh run |
|---|---|---|
| CI-02b verifier on its own | 9.9× | **9.4×** |
| CI-02a verifier on its own | 9.8× | 9.3× |
| Combined regime, main ranges | 2.54× | 2.53× |
| Combined regime, worst case | 6.17× | 6.12× |

**What it means:** a public recheck at the EU rate does almost nothing to back up a captured verifier. If verifiers are paid by the labs they check, the recheck rate would need to be many times higher. Otherwise, what limits capture has to be something else: rotation, liability, or regulators choosing the verifier. Sidar's AN-02 row notes that regulators, not operators, chose the verifier in 35% of country-years.

## Result 2: the fishing-vessel curve makes small hidden runs easier to deter, and splitting stops paying

In Global Fishing Watch, over 90% of ships longer than 50 m were found, about 70% at 25 m, and most under 15 m were missed. Fitting the model's detection curve to those points gives:

- a steepness of about **2 if detection depends on ship length**;
- about **1 if it depends on ship area**, because area grows with the square of length.

A data centre's footprint grows roughly with its power, so the new range is 1 to 2. It is less steep than the old guess (1.5 to 3).

A shallower curve means small sites are found more often and large ones a little less. The bigger effect is on splitting. With a steepness near 1, splitting a run across many small sites barely lowers the chance that *some* site is found. The cheater now mostly runs one hidden site (median 1 site, against 5 at 3,000 GPUs in the sixth run).

Fine needed (median), honest verifier (Figure 7, `size.csv`):

| Hidden run | Time to 10²⁶ FLOP | Main ranges, sixth → seventh | Worst case, sixth → seventh |
|---|---|---|---|
| 1,000 GPUs | 8 years | 11.3× → **7.9×** | 12.9× → 11.5× |
| 3,000 GPUs | 2.7 years | 6.7× → **3.7×** | 9.8× → **7.8×** |
| 10,000 GPUs | 10 months | 2.5× → 2.2× | 5.3× → 5.2× |
| 30,000 GPUs or more | 3 months or less | 2.0× → 2.0× | 4.4× → 4.5× |

Rows are the nearest points on the size grid ("3,000" is 3,162 GPUs), as in the fifth run.

- **A 5× fine now stops hidden runs from about 2,100 GPUs** (main ranges, about 4 years to 10²⁶ FLOP). The sixth run said 4,600 GPUs. In the worst case, the cut-off stays at about 12,000 GPUs (8 months).
- **Most of the change comes from the curve's shape, not the higher splitting cost.** With the shape changed and the old 1–8% splitting cost, 3,000 GPUs needs 4.0×. Raising the cost to 3–15% takes it to 3.7×.
- **Large runs are slightly harder to deter** (4.3× → 4.5× worst case at 30,000 GPUs), because a shallower curve finds big sites a little less reliably.
- **The headline stands: small, slow runs are still the hardest to deter.** In the worst case they still need 8–12×. Checks that don't rely on seeing a site (CI-01 cloud reporting, CI-08 chip tracking) are still what covers them.

## Result 3: the exact splitting cost matters only below about 5% per site

Figure 8 (`split_cost.csv`), fine needed at exactly 3,000 GPUs (median):

| Cost of each extra site | 0% | 1% | 3% | 5% | 8% | 15% or more |
|---|---|---|---|---|---|---|
| Main ranges | 8.3× | 5.3× | 4.3× | 4.0× | 3.9× | 3.8× |
| Worst case | 11.5× | 8.9× | 8.2× | 8.0× | 8.0× | 8.0× |

Above about 5% per site, cheaters stop splitting, so a higher cost changes nothing. **For Vir:** the question to settle is whether splitting a run costs more or less than a few percent of what hiding saves. A precise number isn't needed. If low-communication training methods make splitting nearly free, small runs go back to needing about 8× (main) to 11× (worst case).

## Limits

- **AN-05: the ships weren't hiding.** Transfer confidence is low (Vir's row). Its curve fixes only the *shape*. Where detection reaches 50% (3–10 MW) is still a guess anchored on Clymer's misses. Translating ship length into site power is an assumption: detection may depend on footprint, heat, or something else. A curve from data centres, such as Koopmanschap & Barten's Table 5 if it has one, would replace this.
- **AN-02: one year of data (2019), from emissions trading.** The 1.3% counts inspection visits, not full rechecks of a report. The model treats the recheck as being as good as an honest verifier, which flatters it.
- The splitting cost is a placeholder until Vir agrees a range. Figure 8 covers the whole plausible range.
- Results 2 and 3 depend on sites being independent draws for imagery. If finding one hidden site leads investigators to the others, splitting helps even less.

## What this means for the team

1. **Report:** Result 1 is a clean point for the verifier section. Small public rechecks don't fix verifier capture. That is also relevant to AIFP's pacing proposal, which relies on auditors.
2. **Vir:** settle whether splitting costs above or below about 5% per site. Figure 8 shows the rest doesn't matter.
3. **CI-05:** a measured detection-by-size curve for data centres, even a rough one, would replace AN-05's ships. Whether detection grows with power or more steeply now decides how much splitting helps.
4. **Next run (after 1 Dec):** add CI-01 cloud reporting and CI-08 chip tracking as checks on the hidden-site route.
