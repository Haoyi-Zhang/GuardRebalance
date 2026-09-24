#!/usr/bin/env python3
from pathlib import Path
import json,os,subprocess,sys,time
root=Path(sys.argv[1]).resolve(); logs=Path(os.environ.get('PCCFR_GATE_LOG_DIR', str(root/'artifact/audits/final-run-logs'))); logs.mkdir(parents=True,exist_ok=True); py=sys.executable

def run(name,cmd,timeout=2400,env=None):
 t=time.time()
 try:p=subprocess.run(cmd,cwd=root,text=True,capture_output=True,timeout=timeout,env={**os.environ,**(env or {})})
 except subprocess.TimeoutExpired as e:
  rec={'name':name,'cmd':cmd,'returncode':124,'seconds':round(time.time()-t,3),'stdout':(e.stdout or '')[-20000:] if isinstance(e.stdout,str) else '','stderr':'timeout'}
 else:rec={'name':name,'cmd':cmd,'returncode':p.returncode,'seconds':round(time.time()-t,3),'stdout':p.stdout[-20000:],'stderr':p.stderr[-20000:]}
 (logs/(name+'.json')).write_text(json.dumps(rec,indent=2,ensure_ascii=False)+"\n")
 return rec
T=root/'artifact/audits/tools'
cmds=[]
cmds.append(run('reproduce-clean',['bash',str(root/'artifact/reproduce-clean.sh')],3600))
# Rebuild publication PDF from source after reproduction.
build=root/'paper/build.sh'
cmds.append(run('paper-build',['bash',str(build)] if build.exists() else ['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','main.tex'],1200))
cmds.append(run('reference-audit',[py,str(T/'reference_audit.py'),str(root),'--cache',str(root/'artifact/audits/reference/registry-cache.json'),'--out',str(root/'artifact/audits/reference')],600))
cmds.append(run('reference-quality',[py,str(T/'reference_quality_audit.py'),str(root)],300))
cmds.append(run('project-audit',[py,str(T/'project_audit.py'),str(root),'--skip-reproduce'],1200))
cmds.append(run('independence-audit',[py,str(T/'independence_audit.py'),str(root)],300))
cmds.append(run('experiment-audit',[py,str(T/'experiment_audit.py'),str(root)],300))
cmds.append(run('robustness',[py,str(root/'artifact/robustness.py')],1200))
cmds.append(run('results-inventory',[py,str(T/'results_inventory.py'),str(root)],300))
cmds.append(run('pdf-audit',[py,str(T/'pdf_audit.py'),str(root)],600))
cmds.append(run('theorem-audit',[py,str(T/'theorem_audit.py'),str(root)],300))
cmds.append(run('claim-provenance',[py,str(T/'claim_provenance_audit.py'),str(root)],300))
cmds.append(run('style-audit',[py,str(T/'style_audit.py'),str(root)],300))
cmds.append(run('venue-audit',[py,str(T/'venue_audit.py'),str(root)],300))
cmds.append(run('supply-chain',[py,str(T/'supply_chain_audit.py'),str(root)],300))
# Mutation testing is diagnostic; run and record, but equivalent mutants prevent using it as a logical correctness gate.
cmds.append(run('mutation-guard',[py,str(T/'mutation_guard.py'),str(root)],3600))
reports={
'reference':root/'artifact/audits/reference/reference-audit.json',
'reference_quality':root/'artifact/audits/reference/reference-quality-audit.json',
'project':root/'artifact/audits/blind-review/project-audit.json',
'independence':root/'artifact/audits/blind-review/independence-audit.json',
'experiments':root/'artifact/audits/experiments/experiment-audit.json',
'robustness':root/'artifact/audits/experiments/robustness.json',
'pdf':root/'artifact/audits/paper/pdf-audit.json',
'theorems':root/'artifact/audits/paper/theorem-audit.json',
'claim_provenance':root/'artifact/audits/paper/claim-provenance-audit.json',
'style':root/'artifact/audits/paper/style-audit.json',
'venue':root/'artifact/audits/paper/venue-audit.json',
'supply_chain':root/'artifact/audits/supply-chain/supply-chain-audit.json',
'mutation_guard':root/'artifact/audits/tests/mutation-guard.json',
}
data={};missing=[]
for k,p in reports.items():
 if not p.exists():missing.append(k);continue
 try:data[k]=json.loads(p.read_text())
 except Exception as e:data[k]={'accepted':False,'parse_error':str(e)}
hard_reports=set(reports)-{'mutation_guard'}
hard_commands={c['name'] for c in cmds if c['name']!='mutation-guard'}
command_failures=[c for c in cmds if c['name'] in hard_commands and c['returncode']!=0]
report_failures=[k for k in hard_reports if data.get(k,{}).get('accepted') is not True]
# Additional non-negotiable thresholds, independent of each script's own acceptance flag.
threshold_failures=[]
r=data.get('reference',{})
if r.get('entry_count',0)<30:threshold_failures.append('fewer than 30 retained technical references')
if r.get('entry_count')!=r.get('cited_key_count'):threshold_failures.append('bibliography/citation key count mismatch')
p=data.get('project',{})
if p.get('test_function_count',0)<20:threshold_failures.append('fewer than 20 discovered tests')
if not all((p.get('features') or {}).values()):threshold_failures.append('one or more independent evidence-chain features absent')
e=data.get('experiments',{})
if e.get('confirmed_json_count',0)<1 or e.get('structural_signature_count',0)<2:threshold_failures.append('confirmed result corpus lacks structural diversity')
pdf=data.get('pdf',{})
if pdf.get('reference_start_page')!=21:threshold_failures.append('references do not start on page 21 under the project contract')
accepted=not missing and not command_failures and not report_failures and not threshold_failures
summary={'accepted':accepted,'missing_reports':missing,'command_failures':[{k:c[k] for k in ('name','returncode','seconds')} for c in command_failures],
'report_failures':report_failures,'threshold_failures':threshold_failures,
'commands':[{k:c[k] for k in ('name','returncode','seconds')} for c in cmds],
'components':{k:{'accepted':v.get('accepted'),'headline':{x:v.get(x) for x in ('entry_count','cited_key_count','status_counts','problem_keys','quality_counts','test_function_count','features','command_failures','json_file_count','confirmed_json_count','structural_signature_count','pages','reference_start_page','statement_count','missing_proof_trace','undefined_refs','unsupported_experimental_numbers','long_sentences','repeated_words','loaded_claim_words','class_matches_supplied_template','forbidden_layout_overrides','secret_hits','local_path_hits','project_email_hits','network_commands_in_build_or_reproduce','mutants','killed','survived','score') if x in v}} for k,v in data.items()},
'interpretation':'Internal fail-closed gate. It establishes reproducibility and consistency within the declared scope; it is not external peer review or an acceptance prediction.'}
out=root/'artifact/audits/final-gate.json';out.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
(root/'artifact/audits/final-gate.md').write_text('# Final internal gate\n\nAccepted: **'+str(accepted)+'**\n\n```json\n'+json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n```\n')
print(json.dumps(summary,ensure_ascii=False))
raise SystemExit(0 if accepted else 1)
