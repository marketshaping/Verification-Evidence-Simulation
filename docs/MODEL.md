# How the model works

This page is for anyone on the team who wants to know what the simulation assumes, without reading the code.

## The question

A developer can hide some of its compute, or claim its run is lower-risk than it is. Hiding saves it money (fewer permits, less compliance work). A regulator checks some developers each year. A check catches the hiding with some probability. If caught, the developer may be fined.

**Honest reporting pays when the expected fine is bigger than the gain:**

> chance of being checked × chance a check catches it × chance a caught developer is punished × fine ≥ gain

Rearranged, the **fine needed** as a multiple of the gain is

> fine / gain ≥ 1 / (checking rate × catch rate × chance of punishment)

This is the headline number in each run (`headline.csv`, Figure 1). It extends Christoph, *Risk-Weighted Compute Permit Markets under Imperfect Monitoring* (SSRN 6361077), and follows Kaplow & Shavell (1994).

## Two kinds of instrument

| Kind | Examples | What a check does | Consequence |
|---|---|---|---|
| **Pass/fail** | CI-02 third-party verifiers, CI-05 satellite imagery | Finds the violation or doesn't | The formula above is exact. Below the bar, a developer hides as much as it can; above it, nothing |
| **Measuring** | CI-03+04 attested compute metering | Reads compute with some error and raises an alarm above a threshold | The formula deters large hiding. Small under-reports inside the error band stay hidden at **any** fine (Figure 2) |

For a measuring instrument the alarm threshold is set so an honest developer is wrongly flagged at the false-alarm rate. More meter error means a wider band to hide in. A higher false-alarm rate means a tighter threshold and less room.

## What else is in the model

- **Lenient verifiers (CI-02).** Some verifiers go easy on the lab that pays them. For those, the catch rate is multiplied by a factor below 1.
- **Few vs many developers.** Total compute is fixed. With 4 developers each is large; with 200 each is small. This only matters when fines have a **flat cap** (as in CA SB 53 and NY RAISE): a large developer's gain can exceed the cap, so no checking rate deters it (Figure 3). A cap that scales with size (EU AI Act) behaves like no cap.
- **Uncertainty.** Every input is a range (low, central, high). Each run draws 2,000 sets of inputs and reports the spread.

## The combined regime (added 20 Oct)

Real regimes run several instruments at once. A cheater doesn't face them one at a time: it picks **one way of hiding** and faces only the checks that can see it.

| Route | Who can catch it | Extra cost to the cheater |
|---|---|---|
| 1. Under-report on monitored chips | Verifier; meter (attestation intact) | None |
| 2. Defeat attestation, then under-report | Inspection that finds the tampering; verifier, partly fooled by fake meter data | Small (key extraction for under $1,000 of kit) |
| 3. Use a hidden site with diverted chips | Satellite; verifier only through gaps such as chip purchases that don't add up | Large (building and hiding a site) |

The cheater uses whichever route pays best, so **the fine has to deter the cheapest route**. Route 2 is the "attestation failure blinds metering" case.

The usual shortcut is to multiply catch rates, as if every check saw every cheater. That always asks for a smaller fine than route choice does (Figure 5). The model also asks, for each instrument, what the fine would be if it were perfect or removed (Figure 6). Improving an instrument helps only if it covers the route cheaters actually use.

Inputs are in `data/regime.csv`. Apart from the meter's catch rate (Rahman & Tajdari, a lab test), all of them are guesses. Within a route, checks are treated as independent.

## Run size (added 20 Oct)

A hidden run needs power: about 1–1.4 kW per GPU, so 10,000 GPUs draw about 12 MW. The cheater can split the run across several hidden sites. Smaller sites are harder for imagery to find: detection rises with site power and is half at 3–10 MW. Every miss in Clymer's test was under 4 MW. But each extra site costs 1–8% of the gain, because training across sites is slower and needs links between them. The cheater picks the number of sites that's hardest to deter (Figure 7).

The same compute can come from a big cluster for a short time or a small one for a long time. A 10²⁶ FLOP run takes about a month on 100,000 H100s, or about 2.7 years on 3,000. The top axis of Figure 7 shows this, assuming 40% utilisation.

## What the model leaves out

These are known gaps, listed so nobody reads more into the results than is there.

1. **A cheater picks the weakest route.** Lab tests give average catch rates over the tricks they tried. The `worst_case` scenario stands in for this, but it's a guess.
2. **The combined regime has only three routes and three instruments.** CI-01 and CI-06/07 aren't in it yet, and route costs are guesses. Small under-reports inside the meter error band are a separate effect (Figure 2), not part of the combined regime.
3. **Run size only changes the hidden-site route.** A verifier's chance of noticing off-book chips doesn't yet grow with the number of chips bought. Slow runs also face a cost that isn't modelled: a model trained over years may be out of date when it's done.
4. **A satellite flag isn't a catch.** Someone has to inspect the site and be let in. Inspection capacity isn't modelled.
5. **Between countries, fines are the wrong lens.** For CI-05 and CI-03 against a state, the question is whether cheating is caught before a dangerous run finishes. The fine model fits checks on labs within one country.
6. **Hiding 1% of a declared run isn't the safety risk.** Hiding a whole run is. The metering floor (Figure 2) is about accuracy and permit revenue, not catastrophe.

## Where each number comes from

Every input lives in `data/`, with a `status` and a `source`:

| Status | Meaning | How to talk about results that depend on it |
|---|---|---|
| `evidence` | Measured for this instrument, from a coded row | Can be cited, with the row |
| `analogue` | Measured in another regime (tax, nuclear, emissions), from a coded analogue row | "Based on X, assuming it transfers" |
| `scenario` | Our guess | "If..." only. Never as a finding |

Figure 4 shows which guesses move the result most. Those are the most valuable things for the evidence team to find.
