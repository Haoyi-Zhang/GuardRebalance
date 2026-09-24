#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,re,sys,time,urllib.parse,urllib.request
from difflib import SequenceMatcher
root=Path(sys.argv[1]); tools=root/'artifact/audits/tools'
spec=importlib.util.spec_from_file_location('ra',tools/'reference_audit.py'); ra=importlib.util.module_from_spec(spec); spec.loader.exec_module(ra)
entries=[]
for p in root.rglob('*.bib'):entries+=ra.parse_bib(p)
known=[(e['key'],e['fields'].get('title','')) for e in entries]
queries=[
'exception preserving instruction scheduling predication',
'precise exceptions if conversion hyperblock compiler',
'fault preserving control flow restructuring compiler',
'proof carrying validation instruction scheduling optimization',
'translation validation speculative code motion exceptions',
'and or precedence guarded scheduling compiler',
'decision tree optimization exception semantics',
'guarded control flow faults exceptions equivalence',
'observer relative compiler transformation equivalence',
'predication rebalancing control flow compiler',
]
UA='PCCFR-novelty-diligence/1.0'
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
rows=[]; errors=[]
for q in queries:
 try:
  u='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':12,'select':'DOI,title,author,published-print,published-online,issued,container-title,URL,type'})
  items=get(u)['message']['items']
  for m in items:
   title=ra.title_of(m); sims=sorted(((SequenceMatcher(None,ra.norm(title),ra.norm(t)).ratio(),k,t) for k,t in known),reverse=True)
   rows.append({'query':q,'source':'Crossref','title':title,'year':ra.year_from_crossref(m),'doi':m.get('DOI',''),'url':m.get('URL',''),'closest_bibliography':{'similarity':round(sims[0][0],4),'key':sims[0][1],'title':sims[0][2]} if sims else None})
  time.sleep(.1)
 except Exception as e:errors.append({'query':q,'source':'Crossref','error':type(e).__name__+': '+str(e)})
 try:
  u='https://dblp.org/search/publ/api?'+urllib.parse.urlencode({'q':q,'format':'json','h':12})
  hits=get(u)['result']['hits'].get('hit',[])
  for h in hits:
   m=h['info']; title=re.sub(r'<[^>]+>','',m.get('title','')); sims=sorted(((SequenceMatcher(None,ra.norm(title),ra.norm(t)).ratio(),k,t) for k,t in known),reverse=True)
   rows.append({'query':q,'source':'DBLP','title':title,'year':str(m.get('year','')),'doi':m.get('doi',''),'url':m.get('url',''),'closest_bibliography':{'similarity':round(sims[0][0],4),'key':sims[0][1],'title':sims[0][2]} if sims else None})
  time.sleep(.1)
 except Exception as e:errors.append({'query':q,'source':'DBLP','error':type(e).__name__+': '+str(e)})
# Dedupe by normalized title and rank candidates not already near-identical to bibliography.
ded={}
for r in rows:ded.setdefault(ra.norm(r['title']),r)
rows=list(ded.values()); candidates=[r for r in rows if (r.get('closest_bibliography') or {}).get('similarity',0)<.90]
report={'retrieved_at':'2026-09-21','queries':queries,'bibliography_entry_count':len(entries),'result_count':len(rows),'errors':errors,'results':rows,'candidate_not_already_matched':candidates,
'interpretation':'This search log documents due diligence and exposes candidate prior art. Search coverage cannot prove novelty; priority claims remain qualified and model-scoped.'}
report['accepted']=len(rows)>=25 and len(errors)<=len(queries)
out=root/'artifact/literature'; out.mkdir(parents=True,exist_ok=True); (out/'novelty-search.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
md=['# Novelty-search log','',f"- Queries: {len(queries)}",f"- Unique registry results: {len(rows)}",f"- Candidates below 0.90 title similarity to current bibliography: {len(candidates)}",f"- Retrieval errors: {len(errors)}",'',
'This log is due diligence, not proof of priority.  A reviewer can rerun the queries and inspect every candidate.', '', '## Queries','']+[f'- {q}' for q in queries]+['','## Unmatched candidates','']
for r in candidates[:100]:md.append(f"- {r['title']} ({r['year']}), {r['source']}, DOI `{r['doi']}`; closest current key `{(r.get('closest_bibliography') or {}).get('key','')}`")
(out/'novelty-search.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'results':len(rows),'candidates':len(candidates),'errors':len(errors),'accepted':report['accepted']}))
if not report['accepted']:raise SystemExit(1)
