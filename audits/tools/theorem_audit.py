#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]); texs=sorted((root/'paper').rglob('*.tex'))
records=[]; labels={}; refs=[]
for p in texs:
 s=p.read_text(encoding='utf-8',errors='replace')
 for m in re.finditer(r'\\begin\{(theorem|lemma|proposition|corollary)\}(?:\[[^\]]*\])?(.*?)\\end\{\1\}',s,re.S|re.I):
  kind=m.group(1).lower(); body=m.group(2); labm=re.search(r'\\label\{([^}]+)\}',body)
  label=labm.group(1) if labm else ''
  after=s[m.end():m.end()+2500]
  proof=bool(re.match(r'\s*\\begin\{proof\}',after)) or bool(re.search(r'proof\s+(?:is|appears|follows).*?(?:Appendix|Section|Lemma|Theorem)',after[:800],re.I))
  line=s[:m.start()].count('\n')+1
  stmt=re.sub(r'\\(?:label|cite\w*|ref|cref|Cref)\{[^}]*\}','',body)
  stmt=re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?',' ',stmt); stmt=re.sub(r'[{}$]',' ',stmt); stmt=re.sub(r'\s+',' ',stmt).strip()
  rec={'file':str(p.relative_to(root)),'line':line,'kind':kind,'label':label,'proof_traceable':proof,'statement':stmt[:700]}; records.append(rec)
  if label: labels.setdefault(label,[]).append(rec)
 for rm in re.finditer(r'\\(?:ref|eqref|cref|Cref|autoref)\{([^}]+)\}',s): refs += [x.strip() for x in rm.group(1).split(',')]
all_labels={}
for p in texs:
 s=p.read_text(encoding='utf-8',errors='replace')
 for m in re.finditer(r'\\label\{([^}]+)\}',s): all_labels.setdefault(m.group(1),[]).append(str(p.relative_to(root)))
report={'statement_count':len(records),'statements':records,'missing_proof_trace':[r['label'] or f"{r['file']}:{r['line']}" for r in records if not r['proof_traceable']],
        'duplicate_labels':{k:v for k,v in all_labels.items() if len(v)>1},'undefined_refs':sorted(set(refs)-set(all_labels))}
report['accepted']=not report['missing_proof_trace'] and not report['duplicate_labels'] and not report['undefined_refs'] and len(records)>=3
out=root/'artifact/audits/paper'; out.mkdir(parents=True,exist_ok=True)
(out/'theorem-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:report[k] for k in ('statement_count','missing_proof_trace','duplicate_labels','undefined_refs','accepted')},ensure_ascii=False))
if not report['accepted']: raise SystemExit(1)
