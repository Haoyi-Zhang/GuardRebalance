#!/usr/bin/env python3
from pathlib import Path
import ast,json,re,sys,hashlib
root=Path(sys.argv[1]).resolve(); files=[p for p in root.rglob('*') if p.is_file()]
symlinks=[str(p.relative_to(root)) for p in root.rglob('*') if p.is_symlink()]
secret_patterns={
 'private_key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 'github_token':re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
 'aws_key':re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
 'generic_secret':re.compile(r'''(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*["'][^"']{12,}["']'''),
}
# Build local-path needles without embedding a literal path that would self-trigger.
local_needles=['/'+'mnt'+'/data','/'+'home'+'/oai']
secret_hits=[]; path_hits=[]; email_hits=[]; network=[]
for p in files:
 rel=str(p.relative_to(root)).replace('\\','/')
 if rel=='artifact/audits/tools/supply_chain_audit.py' or (rel.startswith('artifact/audits/') and not rel.startswith('artifact/audits/tools/')):continue
 if p.suffix.lower() in ('.pdf','.png','.jpg','.jpeg','.zip','.pyc','.bin'):continue
 try:s=p.read_text(encoding='utf-8',errors='replace')
 except Exception:continue
 for name,pat in secret_patterns.items():
  for m in pat.finditer(s):secret_hits.append({'file':rel,'kind':name,'context':s[max(0,m.start()-40):m.end()+40]})
 for needle in local_needles:
  if needle in s:path_hits.append({'file':rel,'pattern':needle})
 for pat in (r'user-[A-Za-z0-9]+',r'file_0{4,}[A-Za-z0-9]*'):
  if re.search(pat,s):path_hits.append({'file':rel,'pattern':pat})
 if p.suffix!='.bib' and 'registry-cache' not in rel:
  for e in re.findall(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',s):
   el=e.lower()
   if not (el.endswith('@example.invalid') or 'anonymous' in el or '@example.' in el):email_hits.append({'file':rel,'email':e})
 if p.suffix=='.sh' and ('reproduce' in p.name or 'build' in p.name):
  for i,l in enumerate(s.splitlines(),1):
   if re.search(r'\b(curl|wget|pip\s+install|npm\s+install|git\s+clone)\b',l) and not l.lstrip().startswith('#'):network.append({'file':rel,'line':i,'text':l})
imports=set()
for p in root.rglob('*.py'):
 if '__pycache__' in p.parts:continue
 try:t=ast.parse(p.read_text(encoding='utf-8'))
 except Exception:continue
 for n in ast.walk(t):
  if isinstance(n,ast.Import):imports.update(a.name.split('.')[0] for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module:imports.add(n.module.split('.')[0])
licenses=[str(p.relative_to(root)) for p in files if p.name.lower() in ('license','license.txt','license.md','copying','notice') or 'license' in p.name.lower()]
report={'file_count':len(files),'symlinks':symlinks,'secret_hits':secret_hits,'local_path_hits':path_hits,'project_email_hits':email_hits,'network_commands_in_build_or_reproduce':network,
'top_level_python_imports':sorted(imports),'license_files':licenses,'file_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.stat().st_size<20_000_000}}
report['accepted']=not symlinks and not secret_hits and not path_hits and not email_hits and not network and bool(licenses)
out=root/'artifact/audits/supply-chain';out.mkdir(parents=True,exist_ok=True);(out/'supply-chain-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
print(json.dumps({k:report[k] for k in ('file_count','symlinks','secret_hits','local_path_hits','project_email_hits','network_commands_in_build_or_reproduce','license_files','accepted')},ensure_ascii=False))
if not report['accepted']:raise SystemExit(1)
