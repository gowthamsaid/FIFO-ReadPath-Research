#!/usr/bin/env python3
"""Audit cell and net incremental delay from existing routed SPEF timing paths."""
import csv,json,pathlib,re,sys
edge=re.compile(r'\s([\^v])\s+(\S.*)$')
def parse(txt,old,cfg,arch):
    sections=txt.split('Startpoint:')
    if len(sections)<2: raise ValueError('No timing path')
    t='Startpoint:'+sections[1]
    def get(pattern,label):
        x=re.search(pattern,t,re.M)
        if x is None: raise ValueError('Missing '+label)
        return x.group(1).strip()
    start=get(r'^Startpoint:\s*(.+)$','startpoint')
    end=get(r'^Endpoint:\s*(.+)$','endpoint')
    arrival=float(get(r'^\s*([+-]?\d+\.\d+)\s+data arrival time\s*$','arrival'))
    slack=float(get(r'^\s*([+-]?\d+\.\d+)\s+slack\s+\((?:MET|VIOLATED)\)','slack'))
    if start != old['startpoint'] or end != old['endpoint']: raise ValueError('Path endpoints mismatch')
    if abs(arrival-old['arrival_including_clock_ns'])>.002: raise ValueError('Arrival mismatch')
    if abs(slack-old['setup_slack_ns'])>.002: raise ValueError('Slack mismatch')
    lines=t.split('data arrival time')[0].splitlines()
    ck=next((i for i,x in enumerate(lines) if 'read_ptr[' in x and '/CK ' in x),None)
    if ck is None: raise ValueError('No launch CK')
    rows=[]
    inputs={'A','A1','A2','A3','A4','B','B1','B2','B3','B4','C','C1','C2','CI','D','D1','D2','S','S0','S1','S2','CK','CLK','EN','SE','SI','RN','SN'}
    for line in lines[ck:]:
        m=edge.search(line)
        if not m: continue
        words=line[:m.start()].split()
        if len(words)<2: raise ValueError('Unexpected row: '+line)
        delta,time=float(words[-2]),float(words[-1])
        desc=m.group(2).strip();pin=desc.split(' ')[0]
        if 'read_ptr[' in pin and '/CK' in pin: typ='clock'
        elif pin.endswith('/Q') and 'DFF' in desc:typ='launch_ff'
        elif 'data_out[' in pin and pin.endswith('/D'):typ='end_net'
        elif '/' in pin and pin.rsplit('/',1)[1] in inputs:typ='net'
        elif '/' in pin:typ='cell'
        else:raise ValueError('Unclassified pin: '+desc)
        rows.append(dict(fifo=cfg,architecture=arch,type=typ,pin=pin,description=desc,increment_ns=delta,arrival_ns=time))
    if rows[0]['type']!='clock' or rows[-1]['type']!='end_net':raise ValueError('Malformed data path')
    clock=rows[0]['arrival_ns']
    expected=old['clock_to_data_ns']
    if abs(clock-old['launch_clock_insertion_ns'])>.002:raise ValueError('Clock insertion mismatch')
    if abs(rows[-1]['arrival_ns']-clock-expected)>.002:raise ValueError('Detailed path mismatch')
    if abs(sum(x['increment_ns'] for x in rows[1:])-expected)>.002:raise ValueError('Missing pin increments')
    if not any(x['type']=='net' and x['increment_ns']>0 for x in rows):raise ValueError('No separate net delay; cannot decompose')
    groups={k:sum(x['increment_ns'] for x in rows if x['type']==k) for k in ('launch_ff','cell','net','end_net')}
    if abs(sum(groups.values())-expected)>.002:raise ValueError('Cell/net split does not sum to path')
    return rows,dict(fifo=cfg,architecture=arch,startpoint=start,endpoint=end,
        read_delay_ns=expected,cell_delay_ns=round(groups['launch_ff']+groups['cell'],6),
        net_delay_ns=round(groups['net']+groups['end_net'],6),
        launch_ff_delay_ns=round(groups['launch_ff'],6),comb_cell_delay_ns=round(groups['cell'],6),
        net_fraction_pct=round(100*(groups['net']+groups['end_net'])/expected,3),
        cell_stages=sum(x['type']=='cell' for x in rows),
        net_stages=sum(x['type']=='net' for x in rows),setup_slack_ns=slack)
def main(src,out):
    src=pathlib.Path(src);out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    points=[];summary=[]
    for cfg in ('8x32','64x32'):
        c=json.loads((src/cfg/'comparison.json').read_text())
        if c['configuration']!=cfg or c['geometry']!='matched':raise ValueError('Wrong source config')
        for arch in ('baseline','decoder'):
            old=c[arch]['read_path']
            rows,stat=parse((src/cfg/arch/'readpath-detailed.rpt').read_text(),old,cfg,arch)
            points.extend(rows);summary.append(stat)
    for name,data in (('path-pins.csv',points),('path-decomposition.csv',summary)):
        with (out/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=data[0].keys());writer.writeheader();writer.writerows(data)
    (out/'path-decomposition.json').write_text(json.dumps(summary,indent=2)+'\n')
    md=['# Read-path cell/net delay: archived routed checkpoints','',
        'Only existing post-route ODB, SPEF, SDC were used. No P&R.',
        'Exact first-path startpoints/endpoints, arrival times and slack validated against original run.',
        'The cell and net increments must reproduce the targeted path delay.',
        '','|FIFO|Architecture|Read delay (ns)|Cell delay (ns)|Net delay (ns)|Net share|',
        '|---|---|---:|---:|---:|---:|']
    for s in summary:
        md.append(f"|{s['fifo']}|{s['architecture']}|{s['read_delay_ns']:.4f}|{s['cell_delay_ns']:.4f}|{s['net_delay_ns']:.4f}|{s['net_fraction_pct']:.1f}%|")
    md+=['','This is the first path of each architecture, not a common internal-net path.',
       'Cell/net split is physical evidence, but cannot alone attribute delay to decoder select nets.',
       'Next: identify mapped select nets and sinks; compare multiple seeds and critical-path migration.']
    (out/'README.md').write_text('\n'.join(md)+'\n')
    print('\n'.join(md))
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: parse_detailed_sta.py archive-input report-output')
    main(*sys.argv[1:])
