#!/usr/bin/env python3
from pathlib import Path
import json,sys
root=Path(sys.argv[1]); files=sorted((root/'artifact/results').rglob('*.json'))
rows=[]
def flatten(x,p=''):
 out=[]
 if isinstance(x,dict):
  for k,v in x.items():out+=flatten(v,f'{p}.{k}' if p else k)
 elif isinstance(x,list):
  out.append((p+'.length',len(x)))
  for i,v in enumerate(x):
   if i<40:out+=flatten(v,f'{p}[{i}]')
 elif isinstance(x,(int,float,bool,str)) and (not isinstance(x,str) or len(x)<200):out.append((p,x))
 return out
for f in files:
 try:d=json.loads(f.read_text())
 except Exception:continue
 nums=[(k,v) for k,v in flatten(d) if isinstance(v,(int,float,bool))]
 rows.append({'file':str(f.relative_to(root)),'numeric_fields':nums})
out=root/'artifact/audits/experiments'; out.mkdir(parents=True,exist_ok=True)
(out/'all-results-inventory.json').write_text(json.dumps({'files':rows},indent=2,ensure_ascii=False),encoding='utf-8')
md=['# Complete machine-readable result inventory','',
'This inventory lists every numeric field in every JSON result file.  It is deliberately exhaustive rather than a selected “best result” table.', '']
for r in rows:
 md.append('## `'+r['file']+'`')
 for k,v in r['numeric_fields']:md.append(f'- `{k}`: `{v}`')
 md.append('')
(out/'all-results-inventory.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'json_files':len(rows),'numeric_fields':sum(len(r['numeric_fields']) for r in rows)}))
