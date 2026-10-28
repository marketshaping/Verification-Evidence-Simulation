# Sixth run: CI-02 split into two verifiers (21 October 2026)

**Status: still mostly guesses. Don't cite these as findings.** Following Joel's suggestion of 21 Oct, CI-02 is now two instruments:

| | Coder | What it checks | Margin in the model |
|---|---|---|---|
| **CI-02a** Third-party verifiers: framework compliance | Sidar | Whether a developer follows its own safety framework (New York bill verifier) | Claiming a lower risk class |
| **CI-02b** Third-party verifiers: compute reconciliation | Joon | Declared compute against provider and metering records | Hiding compute. This is also the verifier in the combined regime |

## What changed
- CI-02a keeps the old CI-02 inputs. Its catch-rate range is now marked a **guess**, not a stand-in. Tax audits reconcile amounts against records, which fits CI-02b better than a check of a safety framework.
- CI-02b starts with the same inputs (tax-audit stand-in for the catch rate; lenient verifiers as before; checked yearly, as in EU ETS verification). It's treated as pass/fail for now. If Joon's row gives a record error, it should become a measuring check like the meter.
- The combined regime's verifier is now CI-02b.

## Reproducibility
Everything from the fifth run is reproduced exactly: CI-02a matches the old CI-02 row for row, and CI-03+04, CI-05, the combined regime and the run-size results are unchanged. CI-02b was added last, so it doesn't shift anyone else's random draws.

## Results for CI-02b
Because CI-02a and CI-02b share inputs until their rows are coded, the fine needed is the same for both: about **2.6×** the gain with an honest verifier and about **10×** with a lenient one. Their lines coincide in Figure 1.

They differ only in what they protect:
- CI-02a stops developers claiming a lower risk class.
- CI-02b stops them hiding compute.

The share of compute hidden isn't comparable between them, because the two margins measure different things.

The sensitivity ranking for CI-02b matches CI-02a: fine compared with gain first (0.55), then the share of lenient verifiers (0.40).

## What would separate them
1. A catch rate for each. Even a range from Sidar's and Joon's rows would split the lines.
2. For CI-02b, the error in provider and metering records. That would make it a measuring check, with the small-cheating floor of Figure 2.
3. Whether the two verifiers are the same firm. If they are, being lenient on one probably means being lenient on both.
