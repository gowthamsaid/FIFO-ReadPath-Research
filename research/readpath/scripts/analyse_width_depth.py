#!/usr/bin/env python3
"""Combine two GitHub Actions runs into controlled one-factor scaling tables.

Inputs are raw per-configuration artifact folders: repeat-... for the initial
study and width-depth-... for the additional sizes. Never impute missing runs.
"""
import csv
import json
import pathlib
import statistics
import sys

DEPTH_SWEEP=((32,8),(32,16),(32,32),(32,64))
WIDTH_SWEEP=((8,32),(16,32),(32,32),(64,32))
SEEDS=range(1,6)
FIELDS=("sweep","width","depth","storage_bits","seed","source","status",
"baseline_delay_ns","decoder_delay_ns","read_gain_pct",
"baseline_area_um2","decoder_area_um2","area_change_pct",
"baseline_wire_um","decoder_wire_um","wire_change_pct",
"baseline_vias","decoder_vias","via_change_pct",
"baseline_setup_slack_ns","decoder_setup_slack_ns",
"setup_slack_delta_ns","baseline_hold_slack_ns","decoder_hold_slack_ns",
"baseline_placement_hash","decoder_placement_hash")
def pct(base,alt):
    if not isinstance(base,(int,float)) or base==0 or not isinstance(alt,(int,float)):
        raise ValueError("invalid denominator/metric")
    return (alt-base)/base*100
def unique_folder(root,size,seed):
    pattern=(f"repeat-{size}-s{seed}-*" if size in ("32x16","32x32","16x32")
             else f"width-depth-{size}-s{seed}-*")
    dirs=[p for p in root.iterdir() if p.is_dir() and p.match(pattern)]
    if len(dirs)!=1: raise ValueError(f"expected one artifact matching {pattern}; got {len(dirs)}")
    return dirs[0]
def load(root,w,d,seed,sweep):
    size=f"{w}x{d}"
    row={"sweep":sweep,"width":w,"depth":d,"storage_bits":w*d,
         "seed":seed,"status":"incomplete"}
    p=unique_folder(root,size,seed)
    c=json.loads((p/"comparison.json").read_text())
    if c.get("configuration")!=size or c.get("geometry")!="matched":
        raise ValueError("unexpected config/geometry")
    b=c["baseline"]; z=c["decoder"]
    if b["routing_drc_final"]!=0 or z["routing_drc_final"]!=0:
        raise ValueError("routing violations")
    hashes={}
    for arch in ("baseline","decoder"):
        value=(p/f"{arch}_placement-sha256.txt").read_text().strip()
        if len(value)!=64 or any(t not in "0123456789abcdef" for t in value):
            raise ValueError("invalid placement hash")
        hashes[arch]=value
    bd=b["read_path"]["clock_to_data_ns"]; zd=z["read_path"]["clock_to_data_ns"]
    ba=b["final_cell_area_rounded_um2"]; za=z["final_cell_area_rounded_um2"]
    bw=b["routing_wire_length_um"]; zw=z["routing_wire_length_um"]
    bv=b["routing_vias"]; zv=z["routing_vias"]
    bs=b["worst_overall_setup_slack_ns"]; zs=z["worst_overall_setup_slack_ns"]
    row.update(source=p.name,status="complete",
      baseline_delay_ns=bd,decoder_delay_ns=zd,read_gain_pct=round(-pct(bd,zd),5),
      baseline_area_um2=ba,decoder_area_um2=za,area_change_pct=round(pct(ba,za),5),
      baseline_wire_um=bw,decoder_wire_um=zw,wire_change_pct=round(pct(bw,zw),5),
      baseline_vias=bv,decoder_vias=zv,via_change_pct=round(pct(bv,zv),5),
      baseline_setup_slack_ns=bs,decoder_setup_slack_ns=zs,
      setup_slack_delta_ns=round(zs-bs,6),
      baseline_hold_slack_ns=b["worst_hold_slack_ns"],
      decoder_hold_slack_ns=z["worst_hold_slack_ns"],
      baseline_placement_hash=hashes["baseline"],
      decoder_placement_hash=hashes["decoder"])
    return row
def summary(rows):
    ret={}
    metrics=("baseline_delay_ns","decoder_delay_ns","read_gain_pct",
             "baseline_area_um2","decoder_area_um2","area_change_pct",
             "baseline_wire_um","decoder_wire_um","wire_change_pct",
             "baseline_vias","decoder_vias","via_change_pct","setup_slack_delta_ns")
    for typ,coords in (("depth",DEPTH_SWEEP),("width",WIDTH_SWEEP)):
        groups=[]
        for w,d in coords:
            completed=[r for r in rows if r["sweep"]==typ and r["width"]==w
                       and r["depth"]==d and r["status"]=="complete"]
            m={"width":w,"depth":d,"n":len(completed),"expected_seeds":len(SEEDS)}
            for metric in metrics:
                if completed:
                    values=[r[metric] for r in completed]
                    m[metric+"_mean"]=round(statistics.mean(values),6)
                    m[metric+"_sd"]=round(statistics.stdev(values),6) if len(values)>1 else None
                else:
                    m[metric+"_mean"]=None
                    m[metric+"_sd"]=None
            m["decoder_wins"]=sum(r["read_gain_pct"]>0 for r in completed)
            m["unique_baseline_placements"]=len({r["baseline_placement_hash"] for r in completed})
            m["unique_decoder_placements"]=len({r["decoder_placement_hash"] for r in completed})
            groups.append(m)
        ret[typ]=groups
    return ret
def main(root,out):
    root=pathlib.Path(root);out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[]
    for typ,coords in (("depth",DEPTH_SWEEP),("width",WIDTH_SWEEP)):
        for w,d in coords:
            for seed in SEEDS:
                try: rows.append(load(root,w,d,seed,typ))
                except (OSError,ValueError,KeyError,TypeError,ZeroDivisionError) as e:
                    errors.append(f"{typ} {w}x{d} seed {seed}: {e}")
                    rows.append({"sweep":typ,"width":w,"depth":d,
                                 "storage_bits":w*d,"seed":seed,"status":"incomplete"})
    report=summary(rows)
    for typ,groups in report.items():
        for g in groups:
            if g["n"] and (g["unique_baseline_placements"]!=g["n"] or
                           g["unique_decoder_placements"]!=g["n"]):
                errors.append(f"{typ} {g['width']}x{g['depth']}: duplicate physical placements")
    with (out/"width-depth-seed-data.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,FIELDS);writer.writeheader();writer.writerows(rows)
    with (out/"width-depth-mean-data.csv").open("w",newline="") as f:
        fields=["sweep"]+list(report["depth"][0].keys())
        writer=csv.DictWriter(f,fields);writer.writeheader()
        for typ,groups in report.items():
            for x in groups: writer.writerow({"sweep":typ,**x})
    (out/"width-depth-summary.json").write_text(json.dumps(report,indent=2)+"\n")
    (out/"warnings.json").write_text(json.dumps(errors,indent=2)+"\n")
    lines=["# Width/depth matched-core seed study","","Five seeds per architecture and size; same pinned PDK and SDC.",
       "Comparisons within each FIFO size use identical die/core bounds.",
       "Across sizes, floorplan size and storage capacity grow; trends are not",
       "proof that only width/depth directly causes timing change.",
       "Overall critical path can differ from targeted read-pointer path.",
       "Previous cloud-to-WSL routed-wire reproducibility tolerance remains unresolved.",
       "",
       "| Sweep | FIFO | Pairs | Read delay improvement (mean) | SD (pp) | Area delta | Routed wire delta | Setup slack delta | Wins |",
       "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for typ,groups in report.items():
        for g in groups:
            fmt=lambda v: "n/a" if v is None else f"{v:+.3f}"
            lines.append(f"|{typ}|{g['width']}x{g['depth']}|{g['n']}/5|"
              f"{fmt(g['read_gain_pct_mean'])}%|{fmt(g['read_gain_pct_sd'])}|"
              f"{fmt(g['area_change_pct_mean'])}%|{fmt(g['wire_change_pct_mean'])}%|"
              f"{fmt(g['setup_slack_delta_ns_mean'])} ns|{g['decoder_wins']}/{g['n']}|")
    lines+=["","## Adjacent doubling trends",
            "For each step, percentage below is percent change in mean *absolute* metric",
            "(not percent improvement), compared with the previous size.",
            "Interpret changes in absolute timing and routing alongside architecture deltas.",""]
    for typ,groups in report.items():
        lines.append(f"### {typ.capitalize()} increases (other dimension fixed)")
        for a,b in zip(groups,groups[1:]):
            if not a["n"] or not b["n"]:
                lines.append(f"- {a['width']}x{a['depth']} → {b['width']}x{b['depth']}: incomplete")
                continue
            def change(key):
                old=a[key+"_mean"]; new=b[key+"_mean"]
                return "n/a" if not old else f"{(new-old)/old*100:+.2f}%"
            lines.append(f"- {a['width']}x{a['depth']} → {b['width']}x{b['depth']}: "
             f"baseline read delay {change('baseline_delay_ns')}, decoder read delay {change('decoder_delay_ns')}, "
             f"baseline wire {change('baseline_wire_um')}, decoder wire {change('decoder_wire_um')}.")
        lines.append("")
    lines+=["## Incomplete and audit warnings",*(["- "+e for e in errors] if errors else ["None."]),
            "","Mean and sample standard deviation cover placement seeds, not PVT variability.",
            "Routing wire length is a proxy for connectivity, not a direct congestion or power measurement."]
    (out/"width-depth-report.md").write_text("\n".join(lines)+"\n")
    print("\n".join(lines))
    return 0 if not errors else 1
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Usage: analyse_width_depth.py collected summary-dir")
    raise SystemExit(main(*sys.argv[1:]))
