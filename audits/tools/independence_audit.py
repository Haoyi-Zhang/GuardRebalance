#!/usr/bin/env python3
from pathlib import Path
import ast,json,re,sys
root=Path(sys.argv[1]); art=root/'artifact'
js=[]
for p in art.rglob('*.js'):
 s=p.read_text(encoding='utf-8',errors='replace')
 if re.search(r'(?i)(pfc1|direct|verif|interpret)',p.name+' '+s):
  js.append({'file':str(p.relative_to(root)),'uses_child_process':bool(re.search(r"require\(['\"]child_process|from ['\"]child_process",s)),'invokes_python':bool(re.search(r'(?i)\bpython(?:3)?\b',s)),'bytes':len(s)})
py=[]
for p in art.rglob('*.py'):
 if 'audits' in p.parts:continue
 s=p.read_text(encoding='utf-8',errors='replace')
 if re.search(r'(?i)(explicit|exhaustive).{0,30}tree.{0,30}(oracle|enumerat)|(oracle|enumerat).{0,30}tree',p.name+' '+s,re.S):
  imports=[]
  try:
   t=ast.parse(s)
   for n in ast.walk(t):
    if isinstance(n,ast.Import):imports += [a.name for a in n.names]
    elif isinstance(n,ast.ImportFrom):imports.append(n.module or '')
  except Exception:pass
  py.append({'file':str(p.relative_to(root)),'imports':imports,'imports_optimizer':any(re.search(r'optimi|dynamic|search',x,re.I) for x in imports),'bytes':len(s)})
# Locate machine-readable campaigns and evidence counts.
campaigns=[]
for p in (art/'results').rglob('*.json') if (art/'results').exists() else []:
 try:d=json.loads(p.read_text())
 except Exception:continue
 blob=json.dumps(d).lower()
 if any(x in blob or x in p.name.lower() for x in ('node','cross-language','independent','mutation','direct verifier','direct_verifier')):
  campaigns.append({'file':str(p.relative_to(root)),'bytes':p.stat().st_size})
# Restricted extractor evidence.
extractors=[]
for p in list(art.rglob('*.py'))+list(art.rglob('*.md')):
 if 'audits' in p.parts:continue
 s=p.read_text(encoding='utf-8',errors='replace')
 if re.search(r'(?i)\b(GSIR|guarded.{0,20}(region|IR)|extract(?:ion|or)?.{0,30}(model|table))\b',p.name+' '+s,re.S):extractors.append(str(p.relative_to(root)))
test_blob='\n'.join(p.read_text(errors='replace').lower() for p in (art/'tests').rglob('*.py')) if (art/'tests').exists() else ''
report={'javascript_direct_interpreters':js,'explicit_tree_oracle_candidates':py,'campaign_result_files':campaigns,'cross_language_tests_present':bool(re.search(r'(node|javascript).{0,80}(direct|verif|interpret)|(direct|verif|interpret).{0,80}(node|javascript)',test_blob,re.S)),'restricted_extractor_files':sorted(set(extractors))}
report['accepted']=bool(js) and all(not x['uses_child_process'] and not x['invokes_python'] for x in js) and any(not x['imports_optimizer'] for x in py) and (bool(campaigns) or report['cross_language_tests_present']) and bool(extractors)
out=art/'audits'/'blind-review';out.mkdir(parents=True,exist_ok=True);(out/'independence-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
print(json.dumps(report,ensure_ascii=False))
if not report['accepted']:raise SystemExit(1)
