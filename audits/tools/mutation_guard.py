#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys,time,os
root=Path(sys.argv[1]).resolve(); pkg=root/'artifact'/'pccfr'; tests=root/'artifact'/'tests'; out=root/'artifact'/'audits'/'tests'; out.mkdir(parents=True,exist_ok=True)
patterns=[
 ('eq_to_ne',re.compile(r'(?<![!<>=]) == (?![=])'),' != '),
 ('ne_to_eq',re.compile(r' != (?![=])'),' == '),
 ('le_to_lt',re.compile(r' <= (?![=])'),' < '),
 ('ge_to_gt',re.compile(r' >= (?![=])'),' > '),
 ('and_to_or',re.compile(r'\band\b'),'or'),
 ('or_to_and',re.compile(r'\bor\b'),'and'),
 ('return_true',re.compile(r'\breturn True\b'),'return False'),
 ('return_false',re.compile(r'\breturn False\b'),'return True'),
]
mutants=[]
for p in sorted(pkg.rglob('*.py')):
 if p.name=='__init__.py': continue
 lines=p.read_text(encoding='utf-8').splitlines(True)
 for li,line in enumerate(lines):
  if line.lstrip().startswith(('#','"""',"'''")): continue
  for name,pat,rep in patterns:
   m=pat.search(line)
   if m:
    nl=line[:m.start()]+rep+line[m.end():]
    mutants.append({'file':p,'line':li,'kind':name,'old':line.rstrip(),'new':nl.rstrip()})
# Deterministic stratified cap: first two per file/kind, max 72.
sel=[]; seen={}
for m in mutants:
 k=(m['file'],m['kind']); n=seen.get(k,0)
 if n<2: sel.append(m); seen[k]=n+1
sel=sel[:72]
results=[]
for idx,m in enumerate(sel):
 p=m['file']; orig=p.read_text(encoding='utf-8'); lines=orig.splitlines(True); lines[m['line']]=m['new']+('\n' if lines[m['line']].endswith('\n') and not m['new'].endswith('\n') else '')
 p.write_text(''.join(lines),encoding='utf-8')
 t=time.time()
 try:
  cp=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(tests)],cwd=root,text=True,capture_output=True,timeout=90,env={**os.environ,'PYTHONHASHSEED':'0'})
  killed=cp.returncode!=0; detail=(cp.stdout+cp.stderr)[-1200:]
 except subprocess.TimeoutExpired:
  killed=True; detail='test timeout under mutation'
 finally:
  p.write_text(orig,encoding='utf-8')
 results.append({'id':idx,'file':str(p.relative_to(root)),'line':m['line']+1,'kind':m['kind'],'old':m['old'],'new':m['new'],'killed':killed,'seconds':round(time.time()-t,3),'detail':detail})
killed=sum(r['killed'] for r in results); score=killed/len(results) if results else 0.0
report={'mutants':len(results),'killed':killed,'survived':len(results)-killed,'score':score,'results':results,
        'interpretation':'Survivors require manual classification because some source-level mutants are semantically equivalent. The score is diagnostic, not a correctness proof.'}
report['accepted']=len(results)>=12 and score>=0.70
(out/'mutation-guard.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'mutants':len(results),'killed':killed,'survived':len(results)-killed,'score':score,'accepted':report['accepted']}))
if not report['accepted']: raise SystemExit(1)
