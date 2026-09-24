#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys
root=Path(sys.argv[1]); contractp=root/'artifact/audits/paper/venue-contract.json'; contract=json.loads(contractp.read_text())
pdfj=json.loads((root/'artifact/audits/paper/pdf-audit.json').read_text())
texs=[p for p in (root/'paper').rglob('*.tex') if '\\documentclass' in p.read_text(errors='replace')]; main=max(texs,key=lambda p:p.stat().st_size); s=main.read_text(encoding='utf-8',errors='replace')
expected=contract.get('expected_reference_start_page'); class_files=list(root.rglob('acmart.cls')); local_cls=class_files[0] if class_files else None
local_hash=hashlib.sha256(local_cls.read_bytes()).hexdigest() if local_cls else None; template_hashes=contract.get('template_acmart_hashes',[])
forbidden=[]
checks={r'\\usepackage(?:\[[^\]]*\])?\{geometry\}':'geometry package',r'\\setlength\s*\{\\(?:textwidth|textheight|oddsidemargin|evensidemargin|topmargin)\}':'manual page geometry',r'\\fontsize\s*\{[0-8](?:\.|\})':'sub-template global font',r'\\vspace\s*\{\s*-':'negative vertical space'}
for pat,name in checks.items():
 if re.search(pat,s):forbidden.append(name)
report={'contract':contract,'expected_reference_start_page':expected,'actual_reference_start_page':pdfj.get('reference_start_page'),'documentclass_lines':[l.strip() for l in s.splitlines() if '\\documentclass' in l],
'local_acmart_class':str(local_cls.relative_to(root)) if local_cls else None,'local_class_sha256':local_hash,'class_matches_supplied_template':bool(local_hash and any(x['sha256']==local_hash for x in template_hashes)),'forbidden_layout_overrides':forbidden}
page_ok=expected is None or pdfj.get('reference_start_page')==expected
report['accepted']=page_ok and not forbidden and ('acmart' in s) and (not template_hashes or report['class_matches_supplied_template'])
out=root/'artifact/audits/paper'; (out/'venue-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(report,ensure_ascii=False))
if not report['accepted']:raise SystemExit(1)
