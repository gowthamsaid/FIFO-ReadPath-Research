# FIFO Read-Path Research — Decoder Architecture and Physical Timing

**Independent research extension of [FIFO RTL-to-GDSII](https://github.com/gowthamsaid/FIFO-RTL-to-GDS), not a duplicate of the original implementation.**

**Question:** For flip-flop-based synchronous FIFOs, when does an explicit, fully shared one-hot read decoder improve post-route read-path timing or standard-cell area compared with a synthesis-inferred indexed read? What physical mechanism explains the difference, and is selective (partial) decoder sharing justified?

**Current status (November 2026):** Completed mapped-synthesis experiments, **50 paired routed comparisons** across repeatability and width/depth studies, and a detailed routed timing-mechanism audit. The full shared decoder improved *targeted* read-path timing in several measured configurations. The proposed **two-group and four-group selective decoders were not implemented**, because the suspected select-net routing bottleneck did not pass a mechanism-first feasibility gate. This result motivated a separate [ORRAM context-aware memory investigation](https://github.com/gowthamsaid/ORRAM-Context-Aware-Memory-Research). No publication novelty, universal speedup, or full signoff is claimed.

## What changed from the public FIFO project?

The [public repository](https://github.com/gowthamsaid/FIFO-RTL-to-GDS) owns the original parameterized `fifo_sync.v`, functional testbenches, 8×16 and 32×32 GDSII layouts, and the completed M.S. technical-paper implementation. **Those files are intentionally not duplicated here.**

This research repository contains the *additional* implementation, controls, scripts, and evidence for comparing **indexed read** (original public RTL) with **fully shared one-hot read decoding** (`research/readpath/rtl/fifo_sync_onehot.v`). A pinned fetch helper restores the exact public baseline when an experiment is run; it is not tracked in this repository.

## Results at a glance

| Study | Verified observation | Interpretation |
|---|---|---|
| Nangate45 mapped synthesis | Decoder mapped library area lower by **2.7% (8×16), 8.5% (32×16), 8.2% (8×64), 9.1% (32×32)** | Mapped-cell estimates, not post-route area |
| Matched repeatability | **30** paired routed trials (five physical seeds per configuration) | Checks placement repeatability, not independent production designs |
| Width/depth expansion | **20** additional paired routed trials | Benefits depend on width and depth; some routing costs and critical-path migration |
| Fixed depth 32 width study | Mean targeted read-path improvements: **23.311% (8×32), 18.310% (16×32), 14.097% (32×32), 11.131% (64×32)** | Trend for this tested family, not a universal scaling law |
| Fixed width 32 depth study | Mean targeted improvements: **10.446% (32×8), 7.630% (32×16), 14.097% (32×32), 15.979% (32×64)** | Non-monotonic |
| Detailed routed STA audit | For selected seed-1 8×32 and 64×32 paths, cell arcs account for about **95–99%** of measured read-path delay | Does **not** establish shared decoder select-net routing as the dominant bottleneck |
| Partial sharing proposal | Two-/four-group architectures discussed but **not implemented or validated** | Mechanism-first gate did not justify another RTL architecture |

**Important:** “Read-path improvement” refers to the specifically constrained read-pointer → registered-output path. It does **not** imply identical improvement in whole-design worst setup slack or Fmax. The paths compared across architectures may have different endpoints. The detailed delay split covers selected paths, not every decoder net.

## Start here — research evidence

1. **[Research evolution and decisions](research/readpath/RESULTS_AND_DECISIONS.md)** — chronological hypotheses, observations, incomplete selective sharing proposal, and next direction.
2. **[Research experiments and interpretation](research/readpath/README.md)** — setup, functional checks, synthesis, and experiment history.
3. **[Mechanism-first decision protocol](research/readpath/MECHANISM_AUDIT.md)** — explicit go/no-go criteria *before* building a partial decoder.
4. **[Measured detailed cell/net audit](research/readpath/MECHANISM_DETAILED_SEED1.md)** and [CSV](research/readpath/data/mechanism_detailed_seed1.csv) — actual routed ODB/SDC/SPEF path decomposition.
5. **[Evidence and Actions index](research/readpath/EVIDENCE_INDEX.md)** — original successful runs, artifact names, and provenance.
6. **[Shared decoder RTL](research/readpath/rtl/fifo_sync_onehot.v)** and [independent queue-model comparison testbench](research/readpath/tb/fifo_readpath_equiv_tb.v).

## Repository map

```text
README.md                         Research overview (this page)
research/readpath/
  rtl/fifo_sync_onehot.v          Research-only full shared-decoder RTL
  tb/fifo_readpath_equiv_tb.v     Both implementations vs independent FIFO queue model
  orfs/                           Research-specific paired OpenROAD configurations and SDC
  scripts/                        Pinned baseline retrieval, experiment runners and STA parsers
  data/                           Selected compact, path-level mechanism summaries
  README.md                       Original pilot protocol and historical experimental progression
  RESULTS_AND_DECISIONS.md        Current conclusions and selective-decoder decision
  EVIDENCE_INDEX.md               Successful workflow runs and output provenance
  MECHANISM_*.md                  Preliminary and detailed routed-path audits
  ROUTED_EXPERIMENT_GUIDE.md      Stage-by-stage WSL/ORFS operating notes
.github/workflows/readpath-*.yml  Research pilots, physical comparisons and analysis
```

## Reproduce a functional comparison

Requirements: Git, Bash, Icarus Verilog (`iverilog`/`vvp`), network access to the public baseline repository. From the root of this research repository:

```bash
bash research/readpath/scripts/fetch_public_baseline.sh
iverilog -g2012 -s fifo_readpath_equiv_tb \
  -P fifo_readpath_equiv_tb.DATA_WIDTH=8 \
  -P fifo_readpath_equiv_tb.DEPTH=16 \
  -o /tmp/readpath.vvp \
  rtl/fifo_sync.v \
  research/readpath/rtl/fifo_sync_onehot.v \
  research/readpath/tb/fifo_readpath_equiv_tb.v
vvp /tmp/readpath.vvp
```

The fetch helper pins the upstream **commit and blob hash**, and `rtl/fifo_sync.v` is intentionally gitignored. The two architectures must pass the reference-model tests; this is **directed functional verification, not formal equivalence proof**.

For mapped-synthesis experiments (Yosys required), run `bash research/readpath/scripts/run_mapped_synthesis.sh 8 16`. For physical comparison, use the matched, digest-pinned ORFS runner `research/readpath/scripts/run_openroad_comparison.sh` with `WIDTH DEPTH natural|matched`, `ORFS_ROOT` and `ORFS_IMAGE` configured as in the [workflow](.github/workflows/readpath-width-depth.yml). The stage-by-stage `run_orfs_stage.sh` is an alternative requiring a compatible local ORFS checkout. Old workflow designs are preserved as a historical record; not all old cloud-to-WSL reproducibility checks are resolved.

## Limitations and relation to subsequent research

- The baseline and decoder are functionally compared using an independent queue-model simulation, not exhaustive formal FIFO equivalence.
- Nangate45 timing and area are technology-, constraint-, and implementation-specific; no power, EM/IR, multi-corner signoff or fabrication was performed.
- The detailed cell/net decomposition concerns *selected* routed paths and does not establish decoder-select net causality.
- Partial/selective-sharing variants were **proposed only**; do not count them as implemented architectures.
- Archived experiment outputs are held by GitHub Actions with finite retention. Selected derived CSVs and research conclusions are in the tracked source tree. [Run-index](research/readpath/EVIDENCE_INDEX.md) records where the original raw artifacts reside.
- This is distinct from the [later ORRAM study](https://github.com/gowthamsaid/ORRAM-Context-Aware-Memory-Research), which investigates **existing** row-versus-word standard-cell RAM choices under different address-generation contexts.

**Author:** Gowtham Sai Damalacheruvu · M.S. Electrical & Computer Engineering, Rutgers University.
