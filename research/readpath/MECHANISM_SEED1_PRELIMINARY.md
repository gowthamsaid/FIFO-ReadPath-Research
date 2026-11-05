# Preliminary Physical-Mechanism Audit: Read-Path Data (Seed 1)
**Status: preliminary evidence; no causal mechanism established.** Date: November 5, 2026.

## Scope and provenance
Three matched-core FIFO sizes at fixed depth 32 (8×32, 32×32, 64×32), seed 1 only. Both architectures use identical SDC and die/core dimensions *within* each FIFO size, Nangate45, pinned ORFS revision `d056a2b304182bf76ff10653531165b1dd9848d4`, and pinned image digest recorded in the experiment. Differences *between* sizes include memory bit count, output width and floorplan. Source reports and final checkpoints are in the private [width/depth Actions run](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170) for 8×32 and 64×32, and [repeatability run](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41941967871) for 32×32.

The first reported constrained `read_ptr -> data_out` setup path was extracted for each architecture. Its endpoints may differ between architectures. The path clock-to-data values were cross-checked against the archived `comparison.json` (the sum of report incremental delays agrees within 0.0003 ns).

## Measured path evidence
All time values are **ns**. Buffer and logic *segment increments* below are sums of the incremental values shown at those output-pin rows in the **existing, output-only STA report**. They include upstream wire effects where the report does not separately display input pins. **They are not isolated standard-cell delays.** The clock-to-Q column is the incremental delay recorded on the launch FF /Q row.

| FIFO | Arch. | Read-path time | Launch FF /Q increment | Buffered stages on path | Buffer-segment increments | Logic-segment increments | Max displayed path fanout |
|---|---|---:|---:|---:|---:|---:|---:|
| 8×32 | Indexed mux | 0.7326 | 0.1740 | 2 | 0.2633 | 0.2952 | 38 |
| 8×32 | Shared decoder | 0.5383 | 0.1018 | 1 | 0.0832 | 0.3531 | 8 |
| 32×32 | Indexed mux | 0.7979 | 0.1934 | 3 | 0.3631 | 0.2413 | 32 |
| 32×32 | Shared decoder | 0.6747 | 0.1006 | 2 | 0.2291 | 0.3450 | 18 |
| 64×32 | Indexed mux | 0.8703 | 0.1545 | 4 | 0.4939 | 0.2217 | 48 |
| 64×32 | Shared decoder | 0.7606 | 0.1012 | 4 | 0.3075 | 0.3520 | 21 |

The read-path improvement for seed 1 is **26.52%, 15.44%, and 12.60%** respectively. The **five-seed mean** improvements were 23.31%, 14.10%, and 11.13%; do not conflate single-seed path-level evidence with five-seed averages.

## Mechanism clues — interpretation deliberately limited
1. The baseline has high incremental delay associated with launch FF and buffer-chain points. This grows to four buffer stages and 0.4939 ns of buffer-associated increments for 64×32 seed 1. The decoder has lower delay at those stages, though four buffer stages appear for 64×32.
2. The decoder has **greater combined logic-segment delay** in each example (~0.35 ns versus ~0.22–0.30 ns), even though its total read path is shorter. This means the architecture's apparent advantage is *not* simply fewer or faster logic gates.
3. In these selected read paths, the maximum reported output fanout is 38/32/48 for baseline and 8/18/21 for decoder. This is **path-local**, not the maximum design-wide fanout nor proof of a decoder-select fanout bottleneck.
4. The critical read paths start from different read pointer bits and may end at different output data bits. Comparing their individual gate sequences does not provide matched-node causal attribution.

## What we cannot yet conclude
- Net delay versus cell delay: the archived output-only report combines effects. We must **rerun STA on the archived final ODB+SDC+SPEF** with `-fields {input_pin net fanout capacitance slew}` to expose interconnect increments. No new placement or routing should be required.
- Whether the expensive nets are *decoder-select nets*, read-pointer fanout, or unrelated controls. This requires mapping timing pins to the actual netlist and design topology.
- Whether local decoder replication would help or be merged away by synthesis; no partial-sharing architecture is implemented yet.
- Statistical causal significance. Only one seed was decomposed here. Next audit must include more seeds and losing cases.

## Near-term research decision
The evidence provisionally points to **read-pointer/buffer distribution in the indexed baseline**, while the shared decoder exhibits nontrivial **logic-network cost**. This is different from assuming that the shared decoder's own select-net distribution is the key limitation. Therefore, **do not commit to decoder replication until detailed cell/net and connectivity analysis supports that mechanism.**

A valid outcome is that our original selective-sharing hypothesis is wrong. We should report that, revise the hypothesis on evidence, and preserve the width/depth scaling dataset as a useful independent artifact.

## Next action
1. Extract input-pin-inclusive timing reports from the **existing** final ODB and SPEF for 8×32 and 64×32.
2. Verify the new report reproduces the same targeted clock-to-data and path endpoints as the archived comparison. If not, stop and diagnose.
3. Calculate actual per-stage cell/net contributions and inspect high-load nets by name.
4. Expand to additional seeds **only after the parser and methodology have been validated**.
