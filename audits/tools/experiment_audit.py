#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib,json,re,sys,collections
root=Path(sys.argv[1]); art=root/'artifact'; result_root=art/'results'
files=sorted(result_root.rglob('*.json')) if result_root.exists() else []
rows=[]; bad=[]; hashes=collections.defaultdict(list); seeds=[]; counters=collections.Counter(); signatures=collections.Counter()

def shape(x,depth=0):
 if depth>6:return '...'
 if isinstance(x,dict):return ('dict',tuple((k,shape(v,depth+1)) for k,v in sorted(x.items())))
 if isinstance(x,list):return ('list',len(x),tuple(shape(v,depth+1) for v in x[:8]))
 if isinstance(x,bool):return 'bool'
 if isinstance(x,int):return 'int'
 if isinstance(x,float):return 'float'
 if x is None:return 'null'
 return 'str'

def walk(x,path=''):
 if isinstance(x,dict):
  for k,v in x.items():
   kp=f'{path}.{k}' if path else k
   kl=k.lower()
   if kl in ('seed','random_seed','rng_seed') and isinstance(v,(int,str)): seeds.append((kp,str(v)))
   if any(t in kl for t in ('error','mismatch','failure','reject','accept','trial','case','comparison','instance','mutation')) and isinstance(v,(int,float,bool)):
    counters[kp]+=int(v) if not isinstance(v,bool) else int(v)
   walk(v,kp)
 elif isinstance(x,list):
  for i,v in enumerate(x[:10000]): walk(v,f'{path}[{i}]')
for p in files:
 try:
  raw=p.read_bytes(); data=json.loads(raw); h=hashlib.sha256(raw).hexdigest(); hashes[h].append(str(p.relative_to(root)))
  sig=hashlib.sha256(repr(shape(data)).encode()).hexdigest()[:16]; signatures[sig]+=1; walk(data)
  rows.append({'file':str(p.relative_to(root)),'bytes':len(raw),'sha256':h,'structural_signature':sig})
 except Exception as e: bad.append({'file':str(p.relative_to(root)),'error':type(e).__name__+': '+str(e)})
duplicates={h:v for h,v in hashes.items() if len(v)>1}
# Inputs/results separation indicators.
input_files=[r for r in rows if re.search(r'(input|corpus|case|table)',r['file'],re.I)]
confirmed=[r for r in rows if '/confirmed/' in ('/'+r['file']).lower()]
exploratory=[r for r in rows if re.search(r'explor|pilot|scratch',r['file'],re.I)]
# Source scan for explicit fixed seeds and post-hoc robustness language.
source='\n'.join(p.read_text(errors='replace') for p in art.rglob('*.py'))
seed_literals=sorted(set(re.findall(r'(?i)(?:seed\s*=\s*|Random\s*\()([0-9]{1,12})',source)))
robustness_terms=sorted(set(re.findall(r'(?i)\b(held.?out|out.?of.?family|robustness|metamorphic|negative control|adversarial)\b',source)))
report={'json_file_count':len(rows),'invalid_json':bad,'duplicate_exact_files':duplicates,'confirmed_json_count':len(confirmed),'exploratory_json_count':len(exploratory),
        'input_like_json_count':len(input_files),'structural_signature_count':len(signatures),'structural_signature_histogram':dict(signatures),
        'recorded_seed_occurrences':seeds[:1000],'source_seed_literals':seed_literals,'counter_inventory':dict(counters),'robustness_terms_in_code':robustness_terms,'files':rows}
# Exact duplicates are allowed only when one is a deliberate summary copy; flag but do not automatically fail.
report['accepted']=len(rows)>=3 and not bad and len(signatures)>=2 and len(confirmed)>=1
out=art/'audits'/'experiments'; out.mkdir(parents=True,exist_ok=True)
(out/'experiment-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True),encoding='utf-8')
md=['# Experiment and corpus audit','',f"- Machine-readable JSON files: **{len(rows)}**",f"- Confirmed-result JSON files: **{len(confirmed)}**",f"- Structural signatures: **{len(signatures)}**",f"- Invalid JSON: **{len(bad)}**",f"- Accepted: **{report['accepted']}**",'', '## Interpretation','',
'This audit checks provenance, parseability, structural diversity, exact duplicates, recorded seeds, and the separation of confirmed from exploratory outputs.  It does not turn a post-hoc split into a preregistered holdout and does not substitute for semantic oracles.', '', '## Counter inventory','']
for k,v in sorted(counters.items()): md.append(f'- `{k}`: {v}')
(out/'experiment-audit.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('json_file_count','confirmed_json_count','structural_signature_count','invalid_json','accepted')},ensure_ascii=False))
if not report['accepted']: raise SystemExit(1)
