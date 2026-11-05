# Mechanism-first research protocol — 2026-11-05

## Purpose
Test whether physically expensive read-select distribution—not just RTL syntax or
placement noise—explains differences between a synthesis-inferred indexed read
and a full shared one-hot decoder in flip-flop-based synchronous FIFOs. This
is a **feasibility gate** for pursuing physically informed selective decoder
sharing, not an assertion of novelty, optimality, or publication readiness.

## Existing evidence (not training and test data yet)
- Repeatability: [run 41941967871](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41941967871),
  30 paired post-route trials, 5 placement seeds per FIFO, with verified
  different placements. All paired jobs succeeded.
- Controlled one-factor sweep: [run 41954769170](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170),
  20 additional paired trials; all jobs succeeded.
- Cross-run scaling report: [run 41964695467](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41964695467).
  Archived original stage reports, SPEF, SDC, ODB, mapped netlists and design
  checkpoints are evidence sources; use them before scheduling new full routes.

At fixed depth=32, average read-path delay improvement from the full decoder:
8x32 23.311%, 16x32 18.310%, 32x32 14.097%, 64x32 11.131%.
This is a trend *in these measurements*; it is not a physical law. Across
these configurations, output width, register count, die dimensions and total
storage all change. No claims about power, IR drop or standalone cause.

At fixed width=32, mean read-path delay improvement is non-monotonic:
32x8 10.446%, 32x16 7.630%, 32x32 14.097%, 32x64 15.979%.

## Falsifiable mechanism hypotheses
- M1: In some larger-width configurations, shared decoder select signals incur
  additional high-fanout wire capacitance, buffer stages or net delay.
- Alternative M0: Loss of improvement arises primarily from differences in
  mapped gate structure, *other* paths, placement, or synthesis optimization,
  rather than decoder-select distribution.
- Mechanism must be observed in actual extracted-SPEF paths; total global
  wire-length increase alone does not demonstrate M1.

## First audit (no new full P&R)
Compare *matched-core, same-seed* baseline/decoder pairs for:
- 8x32, 32x32 and 64x32: fixed depth, width trend.
- 32x8 and 32x64: fixed width, depth contrast.
- 8x64 and 64x8: negative/variable benefits.

For each pair, archive an auditable **path-level** table:
1. Design, architecture, placement seed, RTL hash, OpenROAD commit and
   pinned image, matched die/core dimensions, path startpoint/endpoint.
2. Target read-path delay excluding clock insertion, setup slack, and complete
   FIFO worst setup slack. Do not equate targeted read-path improvement with Fmax.
3. Launch/capture clock tree components separately; enumerate cell arcs and
   interconnect arcs where the existing report supports decomposition.
4. Map read-select and read-pointer driver nets to actual mapped cells; measure
   fanout, extracted capacitance, net delay, buffer count and logical depth.
   Explicitly distinguish path-specific measures from whole-design totals.
5. Include at least one losing seed for a variable configuration, and both
   winning and losing outcomes when possible.
6. Mark unsupported or ambiguous cells/nets as unknown; never infer a physical
   cause solely from a path name or gate count.

## Go/no-go, before new architecture implementation
GO only if:
- Mapped read networks are genuinely distinct and can be attributed to the RTL.
- A repeatable physical bottleneck is identified in detailed paths/netlists.
- The bottleneck plausibly responds to localized decoder sharing and is not
  already eliminated by standard synthesis/placement buffering.
- Candidate architecture structure can be preserved during technology mapping
  without illegitimate optimization constraints.

NO-GO if select-net delay does not drive the difference, if the variants map
to essentially identical networks, or if other paths negate read-path gains.
A NO-GO is a legitimate result: document why and use that to choose the next
specific question rather than indiscriminately increasing the sweep.

## If GO: limited causal intervention
Build a parameterized partial-sharing RTL prototype with two and four decoder
groups, verify against an independent queue model, inspect technology-mapped
netlists to confirm distinct structures, and run a *small* matched comparison
against both existing architectures. No 100-run matrix until this gate passes.
Define an area constraint before interpreting improvements. If favorable,
develop a physical-feedback selection rule; freeze it, then evaluate on **held-out
FIFO dimensions and an independent design**, with appropriate comparisons
against prior standard-cell memory generators and OpenROAD optimization methods.

## Scientific and application boundaries
- We have a reproducible analysis *within the pinned cloud flow*; an earlier
  cloud-to-local WSL routed-wire tolerance failure remains unresolved.
- One-hot decoding, shared select logic, hierarchical decoding, cell replication
  and timing-driven architecture search have prior art. The novelty hurdle is a
  **specific validated optimization method**, not merely an RTL alternative.
- The past width/depth runs remain a useful secondary, independent engineering
  scaling report even if selective sharing fails.
- A useful PhD research sample requires the student to be able to explain the
  hypothesis, path-level evidence, competing explanations, limits and negative
  outcomes in their own words.
