# Research evidence and GitHub Actions index

This index links to the **original recorded run evidence**. Workflow artifacts are not permanent and may expire; their run IDs and the compact, tracked mechanism results preserve the audit trail. Runs were created on the historical research revision. The tracked scripts and the pinned upstream retrieval helper are the recommended starting point for new reproductions.

| Research question | Workflow run | Recorded outcome / use |
|---|---|---|
| Did the physical effect repeat with changed placements? | [Repeatability: 41941967871](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41941967871) | 30 paired routed comparisons over five seeds; saved placement fingerprints and full per-case artifacts |
| How did results change with FIFO width/depth? | [Width-depth: 41954769170](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170) | 20 paired matched-core routed comparisons; summary and per-case ODB/SDC/SPEF/STA |
| Are the trends consistent across those two runs? | [Cross-run analysis: 41964695467](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41964695467) | Aggregated width/depth scaling outcomes |
| What was the read-path physical mechanism? | [Detailed archived STA](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/workflows/readpath-detailed-audit.yml) | Extracted, endpoint-checked cell/net delay analysis from previously routed checkpoints |

## Compact checked-in evidence

- [Preliminary mechanism observations](MECHANISM_SEED1_PRELIMINARY.md) — path start/end points, buffered stages and associated increments; preliminary output-only reports combine wire and cell effects.
- [Detailed per-arc breakdown](MECHANISM_DETAILED_SEED1.md) — extracted-SPEF actual cell/net increments for selected paths.
- [Structured decomposition CSV](data/mechanism_detailed_seed1.csv).
- [Preliminary path summary CSV](data/mechanism_seed1_path_summary.csv).
- [Mechanism-first decision protocol](MECHANISM_AUDIT.md).
- [Results and decisions](RESULTS_AND_DECISIONS.md).

## What a reviewer should inspect

1. **Architecture:** [research shared decoder](rtl/fifo_sync_onehot.v), [baseline source pinned in public repository](https://github.com/gowthamsaid/FIFO-RTL-to-GDS/blob/b909ff13dcda0a323e598220b9b24ef47a9a4029/rtl/fifo_sync.v), [queue-model testbench](tb/fifo_readpath_equiv_tb.v).
2. **Controls:** [research SDC](orfs/constraint.sdc), [matched comparison runner](scripts/run_openroad_comparison.sh), [repeatability workflow](../../.github/workflows/readpath-repeatability.yml), [width-depth workflow](../../.github/workflows/readpath-width-depth.yml).
3. **Timing interpretation:** [mechanism audit](MECHANISM_AUDIT.md) and [detailed cell/net breakdown](MECHANISM_DETAILED_SEED1.md).
4. **Incomplete branch of investigation:** [selective decoder gating and stop decision](RESULTS_AND_DECISIONS.md#4-selective-partial-decoder-idea--not-implemented).

## Provenance caveats

- Mapped synthesis cells/area are not placed area; targeted read delay is not the whole-design timing period.
- Selected timing path startpoints/endpoints may differ between variants.
- Direct cloud-to-local WSL physical-wire reproduction under the earlier tolerance check remains unresolved.
- Artifacts are retained by GitHub Actions only for their configured retention period. An archive's disappearance later does not mean the workflow failed.
- No selective-sharing (two-/four-group) routed artifacts exist because the mechanism gate was not passed.
