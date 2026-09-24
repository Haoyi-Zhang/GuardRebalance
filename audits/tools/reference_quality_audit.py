#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,re,sys,collections
spec=importlib.util.spec_from_file_location('ra',Path(sys.argv[0]).with_name('reference_audit.py'))
# Fall back to sibling tool when copied.
if not spec or not spec.loader:
 raise SystemExit('cannot load reference parser')
ra=importlib.util.module_from_spec(spec); spec.loader.exec_module(ra)
root=Path(sys.argv[1]); entries=[]
for p in root.rglob('*.bib'):
 for e in ra.parse_bib(p): e['file']=str(p.relative_to(root)); entries.append(e)
by={e['key']:e for e in entries}; uses=[]
for p in (root/'paper').rglob('*.tex'):
 for u in ra.citations(p.read_text(encoding='utf-8',errors='replace')): u['file']=str(p.relative_to(root)); uses.append(u)

def quality(e):
 t=e['type'].lower(); f=e['fields']; blob=' '.join(f.values()).lower()
 if t in ('article','inproceedings','conference','incollection','book','phdthesis'): return 'scholarly-publication'
 if t in ('techreport','report') and any(x in blob for x in ('rfc','nist','standard','specification','technical report')): return 'authoritative-report-or-standard'
 if 'arxiv' in blob or f.get('eprint'): return 'preprint'
 if t in ('misc','online','webpage'): return 'web-or-software-record'
 return 'other'
rows=[]; counts=collections.Counter()
for e in entries:
 q=quality(e); counts[q]+=1; rows.append({'key':e['key'],'type':e['type'],'quality_class':q,'title':e['fields'].get('title',''),'venue':e['fields'].get('journal') or e['fields'].get('booktitle') or e['fields'].get('publisher','')})
# Group citations by exact context and detect strong empirical/theorem claims supported only by preprint/web records.
contexts=collections.defaultdict(list)
for u in uses: contexts[(u['file'],u['context'])].append(u['key'])
weak_only=[]
for (file,ctx),keys in contexts.items():
 qs=[quality(by[k]) for k in keys if k in by]
 if qs and all(q in ('preprint','web-or-software-record','other') for q in qs) and re.search(r'(?i)\b(prove|show|demonstrat|establish|guarantee|outperform|reduce|improve|optimal|complete|sound)\b',ctx):
  weak_only.append({'file':file,'keys':keys,'quality_classes':qs,'context':ctx})
report={'entry_count':len(entries),'quality_counts':dict(counts),'rows':rows,'strong_claims_supported_only_by_weak_records':weak_only}
report['accepted']=not weak_only and counts['scholarly-publication']>=20
out=root/'artifact/audits/reference'; out.mkdir(parents=True,exist_ok=True)
(out/'reference-quality-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'entry_count':len(entries),'quality_counts':dict(counts),'weak_only_claims':len(weak_only),'accepted':report['accepted']},ensure_ascii=False))
if not report['accepted']: raise SystemExit(1)
