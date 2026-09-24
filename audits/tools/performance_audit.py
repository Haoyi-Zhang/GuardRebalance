#!/usr/bin/env python3
from pathlib import Path
import cProfile,pstats,io,json,re,subprocess,sys,time,os
root=Path(sys.argv[1]); art=root/'artifact'; metrics=[]
def walk(x,path,file):
 if isinstance(x,dict):
  for k,v in x.items():walk(v,path+'.'+k if path else k,file)
 elif isinstance(x,list):
  for i,v in enumerate(x[:5000]):walk(v,f'{path}[{i}]',file)
 elif isinstance(x,(int,float)) and re.search(r'(?i)(time|second|millis|runtime|memory|rss|byte|size|action|input|state|node|instance)',path):metrics.append({'file':file,'path':path,'value':x})
for p in (art/'results').rglob('*.json') if (art/'results').exists() else []:
 try:walk(json.loads(p.read_text()),'',str(p.relative_to(root)))
 except Exception:pass
# Profile the unit suite as an implementation hot-spot diagnostic, not a production benchmark.
prof=art/'audits'/'experiments'/'unittest.prof'; prof.parent.mkdir(parents=True,exist_ok=True)
t=time.time(); cp=subprocess.run([sys.executable,'-m','cProfile','-o',str(prof),'-m','unittest','discover','-s',str(art/'tests')],cwd=root,text=True,capture_output=True,timeout=1200,env={**os.environ,'PYTHONHASHSEED':'0'}); elapsed=time.time()-t
buf=io.StringIO()
try:pstats.Stats(str(prof),stream=buf).strip_dirs().sort_stats('cumulative').print_stats(40)
except Exception as e:buf.write(str(e))
report={'interpretation':'Operational profiling and retained size/timing inventory. It is not a production compiler or hardware performance evaluation.',
'unit_profile_returncode':cp.returncode,'unit_profile_wall_seconds':elapsed,'unit_profile_top':buf.getvalue(),'retained_size_timing_metrics':metrics,
'has_retained_metrics':bool(metrics)}
report['accepted']=cp.returncode==0
out=art/'audits'/'experiments';(out/'performance-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({'returncode':cp.returncode,'wall_seconds':elapsed,'retained_metrics':len(metrics),'accepted':report['accepted']}))
if not report['accepted']:raise SystemExit(1)
