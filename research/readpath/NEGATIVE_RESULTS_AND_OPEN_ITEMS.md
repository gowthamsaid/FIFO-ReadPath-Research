# Negative results, failed gates, and open items — FIFO read-path research

**Research status (8 November 2026):** The indexed-read versus fully shared one-hot study completed synthesis and routed comparisons. **The proposed physical explanation and selective-decoder follow-up did not pass their feasibility gate.** A failed mechanism hypothesis does not erase an observed measured timing improvement.

This is a **status ledger**, not a replacement for the [research chronology](RESULTS_AND_DECISIONS.md), [mechanism protocol](MECHANISM_AUDIT.md), [routed path audit](MECHANISM_DETAILED_SEED1.md), or [run evidence index](EVIDENCE_INDEX.md).

## Scientific tests and decisions

| Question / proposed experiment | Status | Supported interpretation and evidence |
|---|---|---|
| Is the shared one-hot decoder always better than indexed read? | **NOT ESTABLISHED** | Completed 30 five-seed repeatability pairs plus 20 width/depth pairs found size-dependent targeted read-path gains, with routing, area and whole-design critical-path tradeoffs. No universal speedup or Fmax claim. [Results](RESULTS_AND_DECISIONS.md), [repeatability](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41941967871), [width/depth](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170). |
| Does the shared-select *wire distribution* burden dominate the routed read path? | **MECHANISM GATE NOT PASSED / NO-GO** | Seed-1 SPEF audits of 8×32 and 64×32 found approximately 95–99% **cell-arc** delay along selected paths. In these selected paths, indexed—not shared—had higher absolute net delay. The sample does not prove an alternative causal mechanism either. [Measured breakdown](MECHANISM_DETAILED_SEED1.md). |
| Should two-group and four-group selective decoders be built and compared? | **NOT IMPLEMENTED / STOPPED AT PRE-IMPLEMENTATION GATE** | Proposed to address a hypothetical select-net bottleneck. Because that prerequisite was not demonstrated, no two-/four-group RTL or routed comparison was completed. Do not count them as implemented architectures. [Gate](MECHANISM_AUDIT.md), [decision](RESULTS_AND_DECISIONS.md). |
| Are all FIFO width/depth cases favorable in the same way? | **NO** | Benefits varied across sizes; the mechanism protocol flags 8×64 and 64×8 for negative/variable behavior. Width-trend observations are not a controlled scaling law: storage, dimensions and placement also change. [Protocol](MECHANISM_AUDIT.md). |
| Did the original cloud-to-local WSL routed-wire tolerance test reproduce? | **UNRESOLVED / NOT A PASSED REPRODUCTION GATE** | The original cross-environment tolerance discrepancy remains in the record. Successful controlled data are from the pinned cloud flow, not a proven cross-environment match. [Methods](README.md), [limitations](MECHANISM_AUDIT.md). |

## Failed workflows versus failed science

The GitHub Actions history includes unsuccessful **engineering** runs—for example [early post-route pilot 41936469639](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41936469639) and [early detailed audit 41979650584](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41979650584). Their failed CI status is not evidence that one decoder scientifically performed worse. Later [paired physical comparisons 41954769170](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41954769170) and [detailed audit 41980386347](https://github.com/gowthamsaid/FIFO-ReadPath-Research/actions/runs/41980386347) succeeded. Consult original job logs to determine an individual infrastructure failure's cause rather than guessing from its status.

## Final research conclusion

**Supported:** Decoder organization influenced mapped area and selected routed read-pointer-to-output path timing within the tested Nangate45 flip-flop FIFOs. Evidence includes repeated paired physical runs and a bounded path-level audit.

**Not supported or not done:** Shared-select routing as the demonstrated bottleneck; two-/four-group selective architectures; a general optimization rule; full signoff, formal FIFO equivalence, power analysis, or universal timing/area improvement.

**Next research:** The distinct [ORRAM study](https://github.com/gowthamsaid/ORRAM-Context-Aware-Memory-Research) asks how external address logic changes ranking between *existing* memory alternatives. ORRAM does not validate the stopped FIFO selective-decoder hypothesis.

**Artifact limitation:** Large ODB/SDC/SPEF and timing evidence are linked to time-limited Actions artifacts; the tracked path summaries and reports remain available here.