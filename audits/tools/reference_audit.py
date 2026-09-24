#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, time, unicodedata, urllib.parse, urllib.request, hashlib
from pathlib import Path
from difflib import SequenceMatcher

UA='PCCFR-reference-audit/1.0 (mailto:artifact-audit@example.invalid)'

def norm(s):
    s=unicodedata.normalize('NFKD',s or '')
    s=''.join(c for c in s if not unicodedata.combining(c))
    s=re.sub(r'\\[a-zA-Z]+\s*\{([^{}]*)\}',r'\1',s)
    s=re.sub(r'[{}\\]','',s)
    s=s.replace('&',' and ')
    return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()

def split_entries(text):
    out=[]; i=0
    while True:
        m=re.search(r'@([A-Za-z]+)\s*([({])',text[i:])
        if not m: break
        start=i+m.start(); typ=m.group(1).lower(); op=m.group(2); cl='}' if op=='{' else ')'
        j=i+m.end(); depth=1; quote=False; esc=False
        while j<len(text) and depth:
            c=text[j]
            if esc: esc=False
            elif c=='\\': esc=True
            elif c=='"': quote=not quote
            elif not quote:
                if c==op: depth+=1
                elif c==cl: depth-=1
            j+=1
        out.append((typ,text[start:j])); i=j
    return out

def parse_entry(typ, raw):
    head=re.match(r'@[A-Za-z]+\s*[({]\s*([^,\s]+)\s*,',raw,re.S)
    if not head: return None
    key=head.group(1).strip(); body=raw[head.end():]
    if body and body[-1] in '})': body=body[:-1]
    fields={}; i=0
    while i<len(body):
        while i<len(body) and (body[i].isspace() or body[i]==','): i+=1
        m=re.match(r'([A-Za-z][A-Za-z0-9_-]*)\s*=\s*',body[i:])
        if not m: break
        name=m.group(1).lower(); i+=m.end()
        if i>=len(body): break
        if body[i]=='{':
            depth=1; j=i+1
            while j<len(body) and depth:
                if body[j]=='\\': j+=2; continue
                if body[j]=='{': depth+=1
                elif body[j]=='}': depth-=1
                j+=1
            value=body[i+1:j-1]; i=j
        elif body[i]=='"':
            j=i+1; esc=False
            while j<len(body):
                if esc: esc=False
                elif body[j]=='\\': esc=True
                elif body[j]=='"': break
                j+=1
            value=body[i+1:j]; i=j+1
        else:
            j=i
            while j<len(body) and body[j] not in ',\n': j+=1
            value=body[i:j].strip(); i=j
        fields[name]=value.strip()
    return {'key':key,'type':typ,'fields':fields,'raw':raw}

def parse_bib(path):
    text=path.read_text(encoding='utf-8',errors='replace')
    return [x for x in (parse_entry(t,r) for t,r in split_entries(text)) if x]

def citations(tex):
    # Strip comments conservatively.
    lines=[]
    for line in tex.splitlines():
        cut=None; esc=False
        for i,c in enumerate(line):
            if c=='%' and (i==0 or line[i-1]!='\\'): cut=i; break
        lines.append(line if cut is None else line[:cut])
    clean='\n'.join(lines)
    uses=[]
    pat=re.compile(r'\\cite\w*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}')
    for m in pat.finditer(clean):
        a=max(0,clean.rfind('\n\n',0,m.start())); b=clean.find('\n\n',m.end())
        if b<0: b=min(len(clean),m.end()+500)
        ctx=re.sub(r'\s+',' ',clean[a:b]).strip()
        for k in m.group(1).split(','):
            if k.strip(): uses.append({'key':k.strip(),'context':ctx[:1200]})
    return uses

def http_json(url, timeout=25):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.load(r)

def year_from_crossref(m):
    for k in ('published-print','published-online','issued','created'):
        dp=(m.get(k) or {}).get('date-parts')
        if dp and dp[0]: return str(dp[0][0])
    return ''

def crossref_doi(doi):
    return http_json('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))['message']

def crossref_search(title):
    q=urllib.parse.urlencode({'query.bibliographic':title,'rows':5,'select':'DOI,title,author,published-print,published-online,issued,container-title,URL,type'})
    return http_json('https://api.crossref.org/works?'+q)['message']['items']

def dblp_search(title):
    q=urllib.parse.urlencode({'q':title,'format':'json','h':5})
    return http_json('https://dblp.org/search/publ/api?'+q)['result']['hits'].get('hit',[])

def first_bib_author(author):
    if not author:return ''
    a=re.split(r'\s+and\s+',author,flags=re.I)[0].strip()
    if ',' in a: return norm(a.split(',')[0])
    parts=norm(a).split(); return parts[-1] if parts else ''

def first_cr_author(m):
    a=(m.get('author') or [{}])[0]
    return norm(a.get('family',''))

def title_of(m):
    t=m.get('title') or []
    return t[0] if isinstance(t,list) and t else (t if isinstance(t,str) else '')

def verify_entry(e, cache, online):
    f=e['fields']; title=f.get('title',''); year=re.sub(r'\D','',f.get('year',''))[:4]
    doi=normdoi(f.get('doi',''))
    result={'key':e['key'],'bib_title':title,'bib_year':year,'bib_first_author':first_bib_author(f.get('author','')),
            'doi':doi,'url':f.get('url',''),'status':'unverified','evidence_kind':'none','notes':[]}
    ck='doi:'+doi if doi else 'title:'+hashlib.sha256(norm(title).encode()).hexdigest()
    data=cache.get(ck)
    if data is None and online:
        try:
            if doi: data={'source':'crossref-doi','record':crossref_doi(doi)}
            else:
                items=crossref_search(title)
                best=max(items,key=lambda m:SequenceMatcher(None,norm(title),norm(title_of(m))).ratio()) if items else None
                if best and SequenceMatcher(None,norm(title),norm(title_of(best))).ratio()>=0.90:
                    data={'source':'crossref-search','record':best}
                else:
                    hits=dblp_search(title)
                    data={'source':'dblp-search','record':hits[0]['info']} if hits else {'source':'none'}
            cache[ck]=data; time.sleep(0.08)
        except Exception as ex:
            data={'source':'error','error':type(ex).__name__+': '+str(ex)}; cache[ck]=data
    if not data:
        result['notes'].append('no cached registry evidence'); return result
    result['evidence_kind']=data.get('source','none')
    if data.get('source','').startswith('crossref'):
        m=data['record']; rt=title_of(m); ry=year_from_crossref(m); ra=first_cr_author(m)
        sim=SequenceMatcher(None,norm(title),norm(rt)).ratio(); am=bool(result['bib_first_author'] and ra and (result['bib_first_author']==ra or result['bib_first_author'] in ra or ra in result['bib_first_author']))
        ym=not year or not ry or year==ry
        result.update(registry_title=rt,registry_year=ry,registry_first_author=ra,title_similarity=round(sim,4),author_match=am,year_match=ym,evidence_url=m.get('URL',''))
        if sim>=0.94 and am and ym: result['status']='verified-strict'
        elif sim>=0.94 and am and year and ry and abs(int(year)-int(ry))<=1:
            result['status']='verified-publication-year-variant'; result['notes'].append('online/print year differs by at most one')
        elif sim>=0.90 and ym: result['status']='verified-metadata-review'
        else: result['status']='mismatch'
    elif data.get('source')=='dblp-search':
        m=data['record']; rt=m.get('title',''); ry=str(m.get('year','')); auth=m.get('authors',{}).get('author',[])
        if isinstance(auth,dict): auth=[auth]
        if isinstance(auth,str): auth=[auth]
        ra=norm((auth[0].get('text','') if auth and isinstance(auth[0],dict) else (auth[0] if auth else '')).split()[-1] if auth else '')
        sim=SequenceMatcher(None,norm(title),norm(rt)).ratio(); am=not result['bib_first_author'] or not ra or result['bib_first_author']==ra
        ym=not year or not ry or year==ry
        result.update(registry_title=rt,registry_year=ry,registry_first_author=ra,title_similarity=round(sim,4),author_match=am,year_match=ym,evidence_url=m.get('url',''))
        result['status']='verified-strict' if sim>=0.94 and am and ym else ('verified-publication-year-variant' if sim>=0.94 and am and year and ry and abs(int(year)-int(ry))<=1 else ('verified-metadata-review' if sim>=0.90 and ym else 'mismatch'))
    else:
        result['notes'].append(data.get('error','registry lookup failed'))
    if result['status'] in ('unverified','mismatch') and result.get('url'):
        u=result['url']; uck='url:'+u
        cached_url=cache.get(uck)
        if cached_url and cached_url.get('verified'):
            result['status']='verified-authoritative-url'
            result['evidence_kind']='authoritative-url-cache'
            result['evidence_url']=cached_url.get('final_url',u)
            result['notes'].append('authoritative endpoint evidence replayed from cache')
        elif online:
            try:
                host=urllib.parse.urlparse(u).hostname or ''
                trusted=('acm.org','ieee.org','computer.org','springer.com','springerlink.com','arxiv.org','usenix.org','llvm.org','rfc-editor.org','nist.gov','dblp.org','doi.org','cambridge.org','oup.com','sciencedirect.com','elsevier.com','hal.science','inria.fr')
                if any(host==d or host.endswith('.'+d) for d in trusted):
                    req=urllib.request.Request(u,headers={'User-Agent':UA})
                    with urllib.request.urlopen(req,timeout=25) as rr:
                        if 200 <= getattr(rr,'status',200) < 400:
                            cache[uck]={'verified':True,'final_url':rr.geturl(),'status':getattr(rr,'status',200)}
                            result['status']='verified-authoritative-url'
                            result['evidence_kind']='authoritative-url'
                            result['evidence_url']=rr.geturl()
                            result['notes'].append('identity supported by cited authoritative endpoint; bibliographic fields still checked for closure')
            except Exception as ex:
                cache[uck]={'verified':False,'error':type(ex).__name__+': '+str(ex)}
                result['notes'].append('URL verification failed: '+type(ex).__name__)
    return result

def normdoi(s):
    s=(s or '').strip().lower()
    s=re.sub(r'^https?://(dx\.)?doi\.org/','',s)
    return s.strip('{} ')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--online',action='store_true'); ap.add_argument('--cache'); ap.add_argument('--out',required=True)
    a=ap.parse_args(); root=Path(a.root); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    bibs=list(root.rglob('*.bib')); texs=[p for p in root.rglob('*.tex') if not any(x in p.parts for x in ('build','_minted'))]
    entries=[]
    for p in bibs:
        for e in parse_bib(p): e['file']=str(p.relative_to(root)); entries.append(e)
    uses=[]
    for p in texs:
        for u in citations(p.read_text(encoding='utf-8',errors='replace')): u['file']=str(p.relative_to(root)); uses.append(u)
    bykey={e['key']:e for e in entries}; used={u['key'] for u in uses}; keys=set(bykey)
    dois={}; titles={}
    for e in entries:
        d=normdoi(e['fields'].get('doi','')); t=norm(e['fields'].get('title',''))
        if d: dois.setdefault(d,[]).append(e['key'])
        if t: titles.setdefault(t,[]).append(e['key'])
    cachep=Path(a.cache) if a.cache else out/'registry-cache.json'; cache=json.loads(cachep.read_text()) if cachep.exists() else {}
    rows=[]
    for e in entries: rows.append(verify_entry(e,cache,a.online))
    cachep.parent.mkdir(parents=True,exist_ok=True); cachep.write_text(json.dumps(cache,indent=2,ensure_ascii=False,sort_keys=True),encoding='utf-8')
    contexts={k:[] for k in keys}
    for u in uses:
        if u['key'] in contexts and u['context'] not in contexts[u['key']]: contexts[u['key']].append(u['context'])
    for r in rows: r['citation_contexts']=contexts.get(r['key'],[])
    statuses={}
    for r in rows: statuses[r['status']]=statuses.get(r['status'],0)+1
    report={
      'entry_count':len(entries),'citation_use_count':len(uses),'cited_key_count':len(used),
      'undefined_citation_keys':sorted(used-keys),'uncited_bib_keys':sorted(keys-used),
      'duplicate_dois':{k:v for k,v in dois.items() if len(v)>1},
      'duplicate_titles':{k:v for k,v in titles.items() if len(v)>1},
      'status_counts':statuses,
      'problem_keys':[r['key'] for r in rows if not r['status'].startswith('verified')],
      'metadata_review_keys':[r['key'] for r in rows if r['status']=='verified-metadata-review'],
      'rows':rows,
    }
    report['accepted']=not report['undefined_citation_keys'] and not report['uncited_bib_keys'] and not report['duplicate_dois'] and not report['duplicate_titles'] and not report['problem_keys']
    (out/'reference-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True),encoding='utf-8')
    md=['# Reference audit','',f"- Entries: **{len(entries)}**",f"- Distinct cited keys: **{len(used)}**",f"- Registry status: `{statuses}`",f"- Accepted: **{report['accepted']}**",'', '## Closure problems','',f"- Undefined: `{report['undefined_citation_keys']}`",f"- Uncited: `{report['uncited_bib_keys']}`",f"- Duplicate DOI: `{report['duplicate_dois']}`",f"- Duplicate title: `{report['duplicate_titles']}`",f"- Mismatch/unverified: `{report['problem_keys']}`",f"- Metadata review: `{report['metadata_review_keys']}`",'', '## Per-entry evidence','']
    for r in rows:
        md += [f"### `{r['key']}` — {r['status']}",f"- Bibliography: {r['bib_title']} ({r['bib_year']}); first author `{r['bib_first_author']}`",f"- Registry: {r.get('registry_title','')} ({r.get('registry_year','')}); first author `{r.get('registry_first_author','')}`",f"- Evidence: {r['evidence_kind']} {r.get('evidence_url','')}",f"- Contexts: {len(r.get('citation_contexts',[]))}"]
        for c in r.get('citation_contexts',[])[:3]: md.append('  - '+c)
        md.append('')
    (out/'reference-audit.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('entry_count','cited_key_count','status_counts','problem_keys','accepted')},ensure_ascii=False))
if __name__=='__main__': main()
