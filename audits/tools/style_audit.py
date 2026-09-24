#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]); texs=sorted((root/'paper').rglob('*.tex'))
text='\n'.join(p.read_text(encoding='utf-8',errors='replace') for p in texs)
# Remove comments and common commands for rough prose checks.
clean=re.sub(r'(?m)(?<!\\)%.*$',' ',text)
clean=re.sub(r'\\(?:cite\w*|ref|eqref|label|url|href|footnote)\s*(?:\[[^\]]*\])?\{[^{}]*\}(?:\{[^{}]*\})?',' ',clean)
clean=re.sub(r'\\[A-Za-z@]+\*?(?:\[[^\]]*\])?',' ',clean)
clean=re.sub(r'[{}$~_^]',' ',clean); clean=re.sub(r'\s+',' ',clean)
sents=[s.strip() for s in re.split(r'(?<=[.!?])\s+',clean) if len(s.strip())>20]
long=[]
for s in sents:
 words=re.findall(r"[A-Za-z][A-Za-z'-]*",s)
 if len(words)>55: long.append({'words':len(words),'text':s[:500]})
repeated=[]
for p in texs:
 for i,l in enumerate(p.read_text(errors='replace').splitlines(),1):
  for m in re.finditer(r'\b([A-Za-z]{3,})\s+\1\b',l,re.I): repeated.append({'file':str(p.relative_to(root)),'line':i,'word':m.group(1)})
loaded=[]
for w in ('obviously','clearly','trivially','undeniably','unprecedented','revolutionary','guaranteed'):
 for m in re.finditer(r'\b'+w+r'\b',clean,re.I): loaded.append({'word':w,'context':clean[max(0,m.start()-100):m.end()+100]})
# Very rough acronym audit: definitions like full phrase (ABC), then uses.
defs=set(re.findall(r'\(([A-Z][A-Z0-9-]{1,10})\)',clean)); uses=set(re.findall(r'\b([A-Z][A-Z0-9-]{2,10})\b',clean))
allow={'ACM','CPU','CFG','NP','DP','IR','JSON','PDF','DOI','URL','UTF','API','PFC','PFC1','GSIR','AND','OR'}
undefined=sorted(uses-defs-allow)
report={'sentence_count':len(sents),'long_sentences':long,'repeated_words':repeated,'loaded_claim_words':loaded,'acronym_definitions':sorted(defs),'possibly_undefined_acronyms':undefined}
# Long sentences/acronyms are review warnings; repeated words and loaded claim words are hard issues.
report['accepted']=not repeated and not loaded
out=root/'artifact/audits/paper'; out.mkdir(parents=True,exist_ok=True)
(out/'style-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'long_sentences':len(long),'repeated_words':repeated,'loaded_claim_words':loaded,'possibly_undefined_acronyms':undefined,'accepted':report['accepted']},ensure_ascii=False))
if not report['accepted']: raise SystemExit(1)
