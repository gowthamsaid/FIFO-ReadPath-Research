#!/usr/bin/env python3
"""Audit separate one-factor width/depth sweeps using matched-core experiments.

No missing pair is treated as a zero or an unsuccessful architecture.
Expected input: downloaded per-job archives, each containing comparison.json
and baseline/decoder placement hashes.
"""
import csv
import json
import pathlib
import statistics
import sys

SIZES=("32x8","32x64","8x32","64x32")
SEEDS=(1,2,3,4,5)
FIELDS=("fifo","width","depth","storage_bits","seed","status",
        "baseline_read_ns","decoder_read_ns","read_reduction_pct",
        "baseline_final_area_um2","decoder_final_area_um2","area_change_pct",
        "baseline_wire_um","decoder_wire_um","wire_change_pct",
        "baseline_vias","decoder_vias","vias_change_pct",
        "baseline_setup_slack_ns","decoder_setup_slack_ns",
        "baseline_hold_slack_ns","decoder_hold_slack_ns",
        "baseline_place_hash","decoder_place_hash","source")
def number(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool)
def change(a,b):
    return round(100*(b-a)/a,4) if number(a) and number(b) and a else None
def metric(c,arch,key):
    v=c[arch][key]
    if not number(v): raise ValueError(f"Missing metric {arch}.{key}")
    return v
def main(src,dst):
    src,dst=pathlib.Path(src),pathlib.Path(dst)
    dst.mkdir(parents=True,exist_ok=True)
    rows=[]
    errors=[]
    for size in SIZES:
        w,d=map(int,size.split("x"))
        for seed in SEEDS:
            stem=f"width-depth-{size}-s{seed}-"
            folders=sorted(p for p in src.glob(stem+"*") if p.is_dir())
            row={"fifo":size,"width":w,"depth":d,"storage_bits":w*d,
                 "seed":seed,"status":"incomplete"}
            if len(folders)!=1:
                errors.append(f"{size} seed {seed}: expected one archive, found {len(folders)}")
                rows.append(row)
                continue
            p=folders[0]
            try:
                c=json.loads((p/"comparison.json").read_text())
                if c["configuration"]!=size or c["geometry"]!="matched":
                    raise ValueError("wrong configuration or geometry")
                if any(c[x]["routing_drc_final"]!=0 for x in ("baseline","decoder")):
                    raise ValueError("routing DRC violations")
                bd=c["baseline"]["read_path"]["clock_to_data_ns"]
                dd=c["decoder"]["read_path"]["clock_to_data_ns"]
                if not number(bd) or not number(dd) or bd<=0:raise ValueError("invalid read delay")
                ba=metric(c,"baseline","final_cell_area_rounded_um2")
                da=metric(c,"decoder","final_cell_area_rounded_um2")
                bw=metric(c,"baseline","routing_wire_length_um")
                dw=metric(c,"decoder","routing_wire_length_um")
                bv=metric(c,"baseline","routing_vias")
                dv=metric(c,"decoder","routing_vias")
                bh=(p/"baseline_placement-sha256.txt").read_text().strip()
                dh=(p/"decoder_placement-sha256.txt").read_text().strip()
                if not all(len(x)==64 and all(c in "0123456789abcdef" for c in x) for x in (bh,dh)):
                    raise ValueError("missing or malformed placement fingerprint")
                row.update(status="complete",baseline_read_ns=bd,decoder_read_ns=dd,
                    read_reduction_pct=round(100*(bd-dd)/bd,4),
                    baseline_final_area_um2=ba,decoder_final_area_um2=da,area_change_pct=change(ba,da),
                    baseline_wire_um=bw,decoder_wire_um=dw,wire_change_pct=change(bw,dw),
                    baseline_vias=bv,decoder_vias=dv,vias_change_pct=change(bv,dv),
                    baseline_setup_slack_ns=metric(c,"baseline","worst_overall_setup_slack_ns"),
                    decoder_setup_slack_ns=metric(c,"decoder","worst_overall_setup_slack_ns"),
                    baseline_hold_slack_ns=metric(c,"baseline","worst_hold_slack_ns"),
                    decoder_hold_slack_ns=metric(c,"decoder","worst_hold_slack_ns"),
                    baseline_place_hash=bh,decoder_place_hash=dh,source=p.name)
            except (OSError,KeyError,ValueError,TypeError,ZeroDivisionError) as e:
                errors.append(f"{size} seed {seed}: {e}")
            rows.append(row)
    with (dst/"paired-runs.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary=[]
    for size in SIZES:
        group=[r for r in rows if r["fifo"]==size and r["status"]=="complete"]
        if not group:
            summary.append({"fifo":size,"n":0,"status":"missing"})
            continue
        vals=[r["read_reduction_pct"] for r in group]
        unique_b=len({r["baseline_place_hash"] for r in group})
        unique_d=len({r["decoder_place_hash"] for r in group})
        if unique_b!=len(group) or unique_d!=len(group):
            errors.append(f"{size}: repeated physical placement despite different seed(s)")
        summary.append({"fifo":size,"n":len(group),
            "status":"complete" if len(group)==len(SEEDS) else "partial",
            "unique_baseline_placements":unique_b,"unique_decoder_placements":unique_d,
            "mean_read_reduction_pct":round(statistics.mean(vals),4),
            "sd_read_reduction_pct":round(statistics.stdev(vals),4) if len(vals)>1 else None,
            "min_read_reduction_pct":round(min(vals),4),"max_read_reduction_pct":round(max(vals),4),
            "wins":sum(v>0 for v in vals),
            "mean_area_change_pct":round(statistics.mean(r["area_change_pct"] for r in group),4),
            "mean_wire_change_pct":round(statistics.mean(r["wire_change_pct"] for r in group),4),
            "mean_vias_change_pct":round(statistics.mean(r["vias_change_pct"] for r in group),4)})
    (dst/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (dst/"errors.json").write_text(json.dumps(errors,indent=2)+"\n")
    md=["# FIFO width/depth sweep, new sizes (matched-core)", "",
        "Four new configurations; five matched-core placement seeds per size.",
        "Use raw paired-runs.csv and archived timing reports for validation.",
        "A changed seed is not a distinct sample unless placement hashes differ.",
        "Prior 512-bit and repeatability data are combined in the separate cross-run analysis.",
        "Previous cloud-to-WSL wire-length tolerance failure remains unresolved.",
        "",
        "| FIFO | Complete pairs | Unique placements (baseline/decoder) | Mean read improvement | Sample SD | Range | Wins | Mean cell-area change | Mean wire change |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in summary:
        if not r["n"]:
            md.append(f"| {r['fifo']} | 0/5 | — | — | — | — | — | — | — |")
            continue
        fmt=lambda v: "n/a" if v is None else f"{v:+.3f}%"
        md.append(f"| {r['fifo']} | {r['n']}/5 | {r['unique_baseline_placements']}/{r['unique_decoder_placements']} | "
            f"{fmt(r['mean_read_reduction_pct'])} | {fmt(r['sd_read_reduction_pct'])} | "
            f"{r['min_read_reduction_pct']:.3f} to {r['max_read_reduction_pct']:.3f}% | "
            f"{r['wins']}/{r['n']} | {fmt(r['mean_area_change_pct'])} | {fmt(r['mean_wire_change_pct'])} |")
    md+=["","## Warnings",*(["- "+x for x in errors] or ["None."]),
          "","Mean and sample SD describe five placement seeds, not process variations.",
          "Cell area is not floorplan area, and routed wire length alone does not prove congestion or power."]
    (dst/"summary.md").write_text("\n".join(md)+"\n")
    print("\n".join(md))
    return 1 if errors else 0
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Usage: aggregate_width_depth.py collected output")
    raise SystemExit(main(*sys.argv[1:]))
