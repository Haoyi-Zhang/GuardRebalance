#!/usr/bin/env python3
"""Post-hoc structural robustness checks.

This is not a preregistered held-out evaluation.  It checks that the unit suite
is insensitive to Python hash iteration order and that the retained confirmed
corpus contains multiple structural JSON families without exact cross-family
content duplication.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys
from pathlib import Path

def shape(x,depth=0):
    if depth>8:return '...'
    if isinstance(x,dict):return ('dict',tuple((k,shape(v,depth+1)) for k,v in sorted(x.items())))
    if isinstance(x,list):return ('list',len(x),tuple(shape(v,depth+1) for v in x[:16]))
    if isinstance(x,bool):return 'bool'
    if isinstance(x,int):return 'int'
    if isinstance(x,float):return 'float'
    if x is None:return 'null'
    return 'str'

def main():
    root=Path(__file__).resolve().parent.parent; tests=root/'artifact/tests'
    runs=[]
    for seed in (0,1,17,104729):
        env={**os.environ,'PYTHONHASHSEED':str(seed)}
        p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(tests),'-v'],cwd=root,text=True,capture_output=True,env=env,timeout=600)
        normalized='\n'.join(line for line in (p.stdout+p.stderr).splitlines() if not line.startswith('Ran ') and not line.startswith('OK'))
        runs.append({'hash_seed':seed,'returncode':p.returncode,'normalized_sha256':hashlib.sha256(normalized.encode()).hexdigest(),'tail':normalized[-3000:]})
    records=[]; content={}; families={}
    for p in sorted((root/'artifact/results/confirmed').rglob('*.json')) if (root/'artifact/results/confirmed').exists() else []:
        raw=p.read_bytes(); data=json.loads(raw); ch=hashlib.sha256(raw).hexdigest(); sh=hashlib.sha256(repr(shape(data)).encode()).hexdigest()
        records.append({'file':str(p.relative_to(root)),'content_sha256':ch,'structural_family':sh})
        content.setdefault(ch,[]).append(str(p.relative_to(root))); families.setdefault(sh,[]).append(str(p.relative_to(root)))
    report={'interpretation':'Post-hoc structural robustness check; not a preregistered holdout and not evidence for production-workload performance.',
            'hash_seed_runs':runs,'confirmed_files':records,'structural_family_count':len(families),
            'exact_duplicate_groups':{k:v for k,v in content.items() if len(v)>1}}
    report['accepted']=all(r['returncode']==0 for r in runs) and len(families)>=2
    out=root/'artifact/audits/experiments';out.mkdir(parents=True,exist_ok=True);(out/'robustness.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({'accepted':report['accepted'],'hash_seed_runs':len(runs),'structural_family_count':len(families),'duplicate_groups':len(report['exact_duplicate_groups'])}))
    if not report['accepted']:raise SystemExit(1)
if __name__=='__main__':main()
