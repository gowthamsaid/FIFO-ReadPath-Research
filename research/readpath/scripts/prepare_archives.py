#!/usr/bin/env python3
"""Stage final ODB/SDC/SPEF files from two existing GitHub Actions artifacts."""
import pathlib,json,shutil,sys
def main(root,out):
    root=pathlib.Path(root);out=pathlib.Path(out);provenance=[]
    for cfg in ('8x32','64x32'):
        s=root/cfg;d=out/cfg;d.mkdir(parents=True,exist_ok=True)
        info=json.loads((s/'comparison.json').read_text())
        if info.get('configuration')!=cfg or info.get('geometry')!='matched':raise ValueError('Unexpected archived design')
        shutil.copy2(s/'comparison.json',d/'comparison.json')
        for arch in ('baseline','decoder'):
            target=d/arch;target.mkdir(exist_ok=True)
            for ext in ('odb','sdc','spef'):
                f=s/f'{arch}_6_final.{ext}'
                if not f.is_file() or f.stat().st_size==0:raise ValueError('Missing '+str(f))
                shutil.copy2(f,target/f'6_final.{ext}')
            provenance.append({'fifo':cfg,'arch':arch,'seed':1,
                 'run_id':41954769170,'original_delay_ns':info[arch]['read_path']['clock_to_data_ns']})
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: prepare_archives.py raw prepared')
    main(*sys.argv[1:])
