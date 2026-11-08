# FIFO read-path research — methods, studies, and archive

This document explains the **experimental approach** in the private FIFO read-path research repository. Begin with the [research overview](../../README.md), [results and decisions](RESULTS_AND_DECISIONS.md), or [evidence index](EVIDENCE_INDEX.md) for the current scientific conclusions.

## Motivation and original baseline

The [completed public FIFO designs](https://github.com/gowthamsaid/FIFO-RTL-to-GDS) include 8×16 and 32×32 synchronous FIFOs, each meeting the recorded 2 ns setup constraint. The original timing reports showed paths through read-pointer-driven selection logic, providing a performance question without an existing timing violation:

- [8×16 archived timing report](https://github.com/gowthamsaid/FIFO-RTL-to-GDS/blob/main/reports/fifo_8x16/final_timing.rpt)
- [32×32 archived timing report](https://github.com/gowthamsaid/FIFO-RTL-to-GDS/blob/main/reports/fifo_32x32/final_timing.rpt)

This repository does not replicate the original RTL, reports, GDSII layouts or portfolio documentation.

## Falsifiable architecture hypothesis

**H1:** A fully shared one-hot read decoder may reduce targeted routed read-path delay and mapped area relative to an indexed read for some width/depth combinations.

**Competing explanation:** Technology mapping, buffered fanout, physical congestion or path migration can outweigh or explain the observed differences. Targeted read-path timing and whole-design critical timing must be reported independently.

**Tested:** The unchanged baseline FIFO is restored at a pinned upstream commit with `bash research/readpath/scripts/fetch_public_baseline.sh`. The research decoder is [`rtl/fifo_sync_onehot.v`](rtl/fifo_sync_onehot.v). Both are checked against the [independent queue-model testbench](tb/fifo_readpath_equiv_tb.v) using directed simulation, not formal FIFO equivalence.

## Experiments and measured evidence

1. **Initial simulation and generic synthesis:** Six width/depth configurations. Validate FIFO function before comparing gate counts.
2. **Mapped Nangate45 synthesis:** Same Liberty corner and mapping commands, with technology-mapped cell-area comparisons for 8×16, 32×32, 8×64 and 32×16.
3. **Matched physical implementations:** Same timing intent, library, dimensions/geometry within pairs, and repeatable flow. Examine extracted-SPEF read paths in addition to overall setup timing.
4. **Repeatability:** [30 routed pairs in five-seed study](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41941967871).
5. **Width/depth effects:** [20 additional routed pairs](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170) and [cross-run comparison](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41964695467).
6. **Physical mechanism:** [Preliminary stage/output-pin study](MECHANISM_SEED1_PRELIMINARY.md), followed by [input-pin-inclusive SPEF cell/net decomposition](MECHANISM_DETAILED_SEED1.md).

The complete outcome, including percentage improvements and the unimplemented partial-sharing proposal, is in [RESULTS_AND_DECISIONS.md](RESULTS_AND_DECISIONS.md).

## Selective (partial) decoding: proposal only

Based on variable benefits across widths, we considered two-group and four-group selective sharing. Before implementing them, the [mechanism-first protocol](MECHANISM_AUDIT.md) required evidence that shared decoder select distribution was a dominant, physically actionable bottleneck. Selected detailed STA paths were **mostly cell arc delay**, not select-net wire delay. The proposed mechanism did not clear the gate, and **neither two- nor four-group decoder designs were implemented or evaluated**.

The resulting revised research question, tested independently in a [separate ORRAM repo](https://github.com/gowthamsaid/ORRAM-Context-Aware-Memory-Research), concerns how *external address-generation timing* affects physical preference between existing RAM decoders.

## How to rerun the research

The current workflows and research scripts restore the original public FIFO baseline from its pinned commit and verify its Git blob hash. `rtl/fifo_sync.v` is generated/ignored, not tracked in this repo.

```bash
bash research/readpath/scripts/fetch_public_baseline.sh
bash research/readpath/scripts/run_mapped_synthesis.sh 8 16
```

The first command requires Git/network access; mapped synthesis also needs Yosys and curl.

For local ORFS experiments, see [the stage-by-stage guide](ROUTED_EXPERIMENT_GUIDE.md), which requires a working version-compatible OpenROAD-flow-scripts installation. For controlled cloud physical experiments, inspect [`readpath-repeatability.yml`](../../.github/workflows/readpath-repeatability.yml) and [`readpath-width-depth.yml`](../../.github/workflows/readpath-width-depth.yml). The [evidence index](EVIDENCE_INDEX.md) is the easiest way to inspect successful runs rather than rerun them.

## Scope, history, and limitations

- Mapped area is not post-route cell/core area; targeted read-path gains do not necessarily imply overall Fmax gains.
- Historical early pilot runs were made with natural and matched floorplan choices. Do not directly compare original October portfolio results with new paired research variants.
- Early cloud-versus-local WSL wire-length tolerance mismatch was not resolved; do not present the old comparison as a passed reproduction gate.
- No universal performance or signoff claim is made. The physical timing mechanism audit covers selected paths under the available Nangate45 conditions.
- Previous interpretations and incomplete hypotheses are retained in the archived mechanism reports and Git history, rather than rewritten as successful results.
