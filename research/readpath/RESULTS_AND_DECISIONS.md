# Research evolution and decisions — FIFO read-path project

**Status:** The full indexed-versus-shared architecture comparison and bounded timing mechanism audit are complete. The selective-decoder follow-up was **not implemented**.

## 1. Observation in the public FIFO project

Original 8×16 and 32×32 RTL-to-GDSII runs met their 2 ns clock constraint. Their reported setup paths included read-pointer → registered-output read selection. The goal was to study physical read-path delay, **not** to fix a timing violation. Original design and timing reports reside only in the [public FIFO repository](https://github.com/gowthamsaid/FIFO-RTL-to-GDS).

## 2. Indexed vs fully shared one-hot decoding

Implemented `research/readpath/rtl/fifo_sync_onehot.v` as an alternative to the original public `rtl/fifo_sync.v`. Differential simulation against an independent FIFO queue model checked accepted reads/writes, full/empty, wraparound and simultaneous transfers. Generic synthesis and Nangate45 technology mapping checked that the alternatives produced different structures. Mapped-cell library area fell 2.7% to 9.1% across four reported sizes, but those synthesis results alone could not establish routed benefit.

## 3. Post-route matched architecture comparisons

Experiments compared the same FIFO size, timing constraints, library and physical conditions with explicitly controlled seeds/matched-core settings. **30 paired** repeatability trials plus **20 paired** width/depth trials completed. Targeted routed read-path timing often improved with full sharing, although area/routing tradeoffs and critical-path migration complicated universal conclusions.

Fixed depth 32: mean targeted read-path improvements were 23.311% (8×32), 18.310% (16×32), 14.097% (32×32), 11.131% (64×32).

Fixed width 32: mean targeted improvements were 10.446% (32×8), 7.630% (32×16), 14.097% (32×32), 15.979% (32×64).

These are different families; do not infer a single-variable physical law from all configurations. Routed timing and the whole-design critical path must be considered separately.

## 4. Selective (partial) decoder idea — NOT IMPLEMENTED

A proposed physical follow-up was to divide read selection into **two or four sharing groups**. The motivation was the possibility that distributing shared select signals over many bit lanes increased fanout, capacitance, buffering or routed net delay. Both were *prospective RTL structures*, not completed designs or measured physical results.

A mechanism-first go/no-go protocol was established **before** creating the RTL variants: establish distinct mapped read networks; demonstrate repeatable select-distribution bottleneck in extracted-SPEF paths; establish that selective grouping could address it; then run limited two-/four-group tests only if justified.

See [the archived decision protocol](MECHANISM_AUDIT.md).

## 5. Routed physical mechanism audit changed the direction

The detailed audit reopened archived routed OpenDB+SDC+SPEF and decomposed a selected read-pointer → registered-output path into cell and net increments. Selected seed-1 paths:

| FIFO | Architecture | Read delay (ns) | Cell arcs (ns) | Net arcs (ns) |
|---|---|---:|---:|---:|
| 8×32 | Indexed | 0.7326 | 0.7171 | 0.0154 |
| 8×32 | Shared | 0.5383 | 0.5343 | 0.0039 |
| 64×32 | Indexed | 0.8703 | 0.8279 | 0.0424 |
| 64×32 | Shared | 0.7606 | 0.7379 | 0.0227 |

Cell arcs accounted for roughly 95–99% in these selected paths. In this sample, the indexed baseline had greater net delay. The audit **did not validate** the original premise that distribution of fully shared select signals was the dominant physical read-path bottleneck. Differences in cell mapping, buffering and path selection were plausible confounders.

**Decision:** Do not implement selective two-/four-group architectures on the present evidence. This does **not** invalidate observed full-decoder area/read-path improvements; it limits the proposed mechanism and optimization direction. Wider path-specific connectivity and multi-seed causal analysis would be needed to revisit the hypothesis.

## 6. Next research question, pursued in a separate repo

The subsequent question became whether **surrounding registered address-generation timing** changes which *existing* standard-cell RAM decoder architecture wins after routing. This led to the [ORRAM context-aware memory study](https://github.com/gowthamsaid/ORRAM-Context-Aware-Memory-Research), with an independently defined hypothesis, implementation and evidence. FIFO results are not presented as ORRAM validation.

## Research limitations and feedback invited

The physical audit covers selected paths, limited seeds/configurations and the Nangate45 typical-corner flow. The work does not establish new architecture novelty, full design signoff, universal scaling, or a completed partial decoder. Faculty feedback is especially requested on whether a stronger causal experiment can separate mapped cell/logic effects from decoder select-net distribution, or whether a different timing-driven research question is more worthwhile.
