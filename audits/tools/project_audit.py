#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path
from collections import Counter, defaultdict

def run(cmd,cwd,timeout=300):
    t=time.time()
    try:
        p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=timeout,env={**os.environ,'PYTHONHASHSEED':'0'})
        return {'cmd':cmd,'returncode':p.returncode,'seconds':round(time.time()-t,3),'stdout':p.stdout[-20000:],'stderr':p.stderr[-20000:]}
    except subprocess.TimeoutExpired as e:
        return {'cmd':cmd,'returncode':124,'seconds':round(time.time()-t,3),'stdout':(e.stdout or '')[-20000:] if isinstance(e.stdout,str) else '', 'stderr':'timeout'}

def loc(path):
    lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
    return len(lines),sum(1 for x in lines if x.strip() and not x.lstrip().startswith('#'))

def py_info(path,root):
    src=path.read_text(encoding='utf-8',errors='replace'); rec={'file':str(path.relative_to(root))}
    rec['loc'],rec['sloc']=loc(path)
    try: t=ast.parse(src); rec['syntax_ok']=True
    except SyntaxError as e: rec.update(syntax_ok=False,syntax_error=str(e)); return rec
    rec['functions']=[n.name for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
    rec['classes']=[n.name for n in ast.walk(t) if isinstance(n,ast.ClassDef)]
    rec['test_functions']=[x for x in rec['functions'] if x.startswith('test_')]
    imports=[]; broad=[]; bare=[]; passes=[]; asserts=0
    for n in ast.walk(t):
        if isinstance(n,ast.Import): imports += [a.name for a in n.names]
        elif isinstance(n,ast.ImportFrom): imports.append(n.module or '')
        elif isinstance(n,ast.ExceptHandler):
            if n.type is None: bare.append(getattr(n,'lineno',0))
            elif isinstance(n.type,ast.Name) and n.type.id in ('Exception','BaseException'): broad.append(getattr(n,'lineno',0))
            if len(n.body)==1 and isinstance(n.body[0],ast.Pass): passes.append(getattr(n,'lineno',0))
        elif isinstance(n,ast.Assert): asserts+=1
    rec.update(imports=sorted(set(imports)),broad_except_lines=broad,bare_except_lines=bare,pass_except_lines=passes,assert_count=asserts)
    rec['todo_lines']=[i+1 for i,l in enumerate(src.splitlines()) if re.search(r'\b(TODO|FIXME|XXX|HACK)\b',l,re.I)]
    rec['unseeded_random_lines']=[i+1 for i,l in enumerate(src.splitlines()) if re.search(r'\brandom\.(random|randint|choice|shuffle|sample|uniform)\s*\(',l) and 'seed' not in l]
    return rec

def sh_info(path,root):
    s=path.read_text(encoding='utf-8',errors='replace')
    return {'file':str(path.relative_to(root)),'loc':len(s.splitlines()),'has_set_e':bool(re.search(r'set\s+-[^\n]*e',s)),
            'network_lines':[i+1 for i,l in enumerate(s.splitlines()) if re.search(r'\b(curl|wget|pip\s+install|npm\s+install|git\s+clone)\b',l) and not l.lstrip().startswith('#')]}

def main(root_s):
    root=Path(root_s).resolve(); art=root/'artifact'; out=art/'audits'/'blind-review'; out.mkdir(parents=True,exist_ok=True)
    pys=[p for p in root.rglob('*.py') if '.git' not in p.parts and 'audits' not in p.parts]
    js=[p for p in root.rglob('*.js') if '.git' not in p.parts and 'audits' not in p.parts]
    sh=[p for p in root.rglob('*.sh') if '.git' not in p.parts and 'audits' not in p.parts]
    pi=[py_info(p,root) for p in pys]; si=[sh_info(p,root) for p in sh]
    tests=sum(len(x.get('test_functions',[])) for x in pi)
    names='\n'.join(str(p.relative_to(root)).lower()+'\n'+p.read_text(errors='replace').lower()[:20000] for p in pys+js)
    features={
      'explicit_tree_shape_oracle': bool(re.search(r'(explicit|exhaustive).{0,30}tree.{0,30}(oracle|enumerat)|(oracle|enumerat).{0,30}tree.{0,30}(shape|topolog)',names,re.S)),
      'independent_node_verifier': bool(js) and bool(re.search(r'(direct|independent).{0,30}(verif|interpret)|(verif|interpret).{0,30}(pfc1|object)',names,re.S)),
      'restricted_ir_extractor': bool(re.search(r'(gsir|guarded.{0,20}(ir|region)|extract.{0,30}(model|table))',names,re.S)),
      'search_refusal': bool(re.search(r'searchrefusal|search_refusal|optimality_proven|not.proven.optimal',names,re.S)),
      'strict_json': bool(re.search(r'parse_constant|object_pairs_hook|duplicate.{0,10}(key|field)|nan|infinity',names,re.S)),
      'heldout_or_robustness': bool(re.search(r'held.?out|robustness|out.?of.?family|metamorphic|adversarial',names,re.S)),
    }
    commands=[]
    commands.append(run([sys.executable,'-m','compileall','-q',str(art)],root,180))
    commands.append(run([sys.executable,'-m','unittest','discover','-s',str(art/'tests'),'-v'],root,600))
    if shutil_which('node'):
        for p in js: commands.append(run(['node','--check',str(p)],root,60))
    if '--skip-reproduce' not in sys.argv and (root/'artifact/reproduce-clean.sh').exists(): commands.append(run(['bash',str(root/'artifact/reproduce-clean.sh')],root,1800))
    broad=[(x['file'],x['broad_except_lines']) for x in pi if x.get('broad_except_lines')]
    bare=[(x['file'],x['bare_except_lines']) for x in pi if x.get('bare_except_lines')]
    passx=[(x['file'],x['pass_except_lines']) for x in pi if x.get('pass_except_lines')]
    todos=[(x['file'],x['todo_lines']) for x in pi if x.get('todo_lines')]
    network=[(x['file'],x['network_lines']) for x in si if x['network_lines']]
    report={
      'root':str(root),'python_files':len(pys),'javascript_files':len(js),'shell_files':len(sh),
      'python_loc':sum(x.get('loc',0) for x in pi),'python_sloc':sum(x.get('sloc',0) for x in pi),'test_function_count':tests,
      'features':features,'broad_exception_handlers':broad,'bare_exception_handlers':bare,'silent_exception_handlers':passx,'todos':todos,
      'network_in_shell_scripts':network,'python_files_detail':pi,'shell_files_detail':si,'commands':commands,
    }
    report['command_failures']=[{'cmd':c['cmd'],'returncode':c['returncode']} for c in commands if c['returncode']!=0]
    report['accepted']=not report['command_failures'] and all(features.values()) and tests>=20
    (out/'project-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True),encoding='utf-8')
    md=['# Blind code and artifact audit','',f"- Python: {len(pys)} files, {report['python_sloc']} non-comment lines",f"- JavaScript: {len(js)} files",f"- Tests discovered: {tests}",f"- Accepted: **{report['accepted']}**",'', '## Evidence chains','']
    for k,v in features.items(): md.append(f"- {k}: **{v}**")
    md += ['', '## Command results','']
    for c in commands: md.append(f"- `{c['cmd']}` → rc={c['returncode']}, {c['seconds']} s")
    md += ['', '## Static risks','',f"- Broad exception handlers: `{broad}`",f"- Bare exception handlers: `{bare}`",f"- Silent exception handlers: `{passx}`",f"- TODO/FIXME: `{todos}`",f"- Network in reproduction shell scripts: `{network}`"]
    (out/'project-audit.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps({'accepted':report['accepted'],'tests':tests,'features':features,'failures':report['command_failures']},ensure_ascii=False))

def shutil_which(x):
    import shutil; return shutil.which(x)
if __name__=='__main__': main(sys.argv[1])
