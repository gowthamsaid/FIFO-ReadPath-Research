# Measured routed read-path cell/net decomposition — seed 1
**Source:** Archived matched-core baseline and decoder post-route ODB + SDC + SPEF; 8×32 and 64×32. Reanalysis with pinned ORFS and OpenSTA. No new P&R.

| FIFO | Architecture | Launch-to-output read delay (ns) | Cell arcs (ns) | Net arcs (ns) | Net fraction |
|---|---|---:|---:|---:|---:|
| 8×32 | Indexed baseline | 0.7326 | 0.7171 | 0.0154 | 2.1% |
| 8×32 | Shared decoder | 0.5383 | 0.5343 | 0.0039 | 0.7% |
| 64×32 | Indexed baseline | 0.8703 | 0.8279 | 0.0424 | 4.9% |
| 64×32 | Shared decoder | 0.7606 | 0.7379 | 0.0227 | 3.0% |

**Method:** Extracted SPEF timing report with input-pin and net rows. Cell arc delay includes launch FF clock-to-Q and combinational cell timing. Net arc delay comprises receiving-pin incremental delays. Numbers rounded individually. Reported first-path endpoints, arrival times, setup slacks, and total read delays were checked against archived `comparison.json` with 2 ps tolerance.

**Finding:** Cell delay dominates the measured critical read path in these cases, and the indexed baseline has greater absolute net delay. This does not support assuming the shared decoder's own long select nets are presently the dominant read-path issue.

**Caveats:** Only seed 1 and two width-extreme configurations at depth 32. The two architectures have different path endpoints and mapped logic. Path-specific net delay is not global routing delay. Cannot infer decoder-select-net causality or prove replication is beneficial. Next distinguish mapped pointer buffers and decoder-select sinks; inspect multiple seeds and path migration.

**Provenance:** [Original width/depth physical implementations](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170); [archived checkpoint detailed STA](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/workflows/readpath-detailed-audit.yml).
