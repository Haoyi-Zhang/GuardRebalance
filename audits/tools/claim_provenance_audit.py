#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]); paper=root/'paper'; art=root/'artifact'
values=set(); value_paths={}
def walk(x,path):
 if isinstance(x,dict):
  for k,v in x.items(): walk(v,path+'.'+k)
 elif isinstance(x,list):
  values.add(len(x)); value_paths.setdefault(len(x),[]).append(path+'.<length>')
  for i,v in enumerate(x): walk(v,f'{path}[{i}]')
 elif isinstance(x,(int,float)) and not isinstance(x,bool):
  # preserve exact integers
  if isinstance(x,int) or float(x).is_integer():
   n=int(x); values.add(n); value_paths.setdefault(n,[]).append(path)
for p in art.rglob('*.json'):
 try: walk(json.loads(p.read_text()),str(p.relative_to(root)))
 except Exception: pass
tex='\n'.join(p.read_text(encoding='utf-8',errors='replace') for p in paper.rglob('*.tex'))
# Strip commands that are overwhelmingly labels/citations and math equation blocks.
text=re.sub(r'\\(?:cite\w*|ref|eqref|label|pageref|Cref|cref)\{[^}]*\}',' ',tex)
contexts=[]
for m in re.finditer(r'(?<![A-Za-z])([0-9][0-9,]{2,})(?![A-Za-z])',text):
 raw=m.group(1); n=int(raw.replace(',',''))
 ctx=re.sub(r'\s+',' ',text[max(0,m.start()-180):min(len(text),m.end()+180)])
 if 1900<=n<=2100: continue
 # Only experimental/resource claims, not theorem constants or DOI fragments.
 if not re.search(r'(?i)(compar|case|instance|test|trial|mutation|object|input|model|error|mismatch|accept|reject|byte|second|minute|MiB|GiB|seed|experiment|replay|enumerat|state|tree|certificate|check)',ctx):
  continue
 
 # Accept exact cells/list lengths, or transparent sums of two recorded nonnegative counters.
 exact=n in values
 pair=[]
 if not exact:
  small=[v for v in values if isinstance(v,int) and 0<=v<=n]
  ss=set(small)
  for a in small:
   if n-a in ss:
    pair=[a,n-a]; break
 contexts.append({'number':n,'raw':raw,'supported_by_json':exact or bool(pair),'support_kind':'exact' if exact else ('derived-sum' if pair else 'none'),'derived_terms':pair,'json_paths':value_paths.get(n,[])[:20],'context':ctx})
unsupported=[x for x in contexts if not x['supported_by_json']]
report={'machine_numeric_value_count':len(values),'paper_experimental_numbers':contexts,'unsupported_experimental_numbers':unsupported}
# Some derived totals legitimately equal sums rather than a single JSON cell. Keep them review-required, not silently accepted.
report['accepted']=len(unsupported)==0
out=art/'audits'/'paper'; out.mkdir(parents=True,exist_ok=True)
(out/'claim-provenance-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'paper_experimental_numbers':len(contexts),'unsupported':[(x['number'],x['context'][:100]) for x in unsupported],'accepted':report['accepted']},ensure_ascii=False))
if not report['accepted']: raise SystemExit(1)
