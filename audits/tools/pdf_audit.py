#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess,sys,os,hashlib
from pathlib import Path

def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True)
 return p.returncode,p.stdout,p.stderr

def main(root_s):
 root=Path(root_s).resolve(); paper=root/'paper'; pdf=paper/'main.pdf'
 if not pdf.exists():
  cand=list(paper.glob('*.pdf'))
  if not cand: raise SystemExit('no paper PDF')
  pdf=cand[0]
 out=root/'artifact'/'audits'/'paper'; out.mkdir(parents=True,exist_ok=True)
 rc,info,err=run(['pdfinfo',str(pdf)])
 pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1)) if re.search(r'^Pages:\s+(\d+)',info,re.M) else None
 rc2,fonts,err2=run(['pdffonts',str(pdf)])
 font_rows=[x for x in fonts.splitlines()[2:] if x.strip()]
 unembedded=[]
 for x in font_rows:
  parts=x.split()
  if len(parts)>=7 and parts[-5].lower()=='no': unembedded.append(x)
 txt=out/'paper.txt'; run(['pdftotext','-layout',str(pdf),str(txt)])
 text=txt.read_text(encoding='utf-8',errors='replace') if txt.exists() else ''
 page_text=text.split('\f')
 lengths=[len(re.sub(r'\s+','',x)) for x in page_text[:pages]] if pages else []
 ref_page=None
 for i,x in enumerate(page_text[:pages],1):
  if re.search(r'^\s*(REFERENCES|References)\s*$',x,re.M): ref_page=i; break
 suspicious=[]
 pats=[r'/mnt/data',r'/home/oai',r'file_0{4,}',r'@[A-Za-z0-9.-]+\.(edu|com|org|net)',r'Anonymous Author\(s\).*Anonymous Author']
 for pat in pats:
  if re.search(pat,text,re.I): suspicious.append(pat)
 # Render every page and collect image geometry.
 render=out/'render'; render.mkdir(exist_ok=True)
 run(['pdftoppm','-png','-r','120',str(pdf),str(render/'page')])
 pngs=sorted(render.glob('page-*.png'))
 try:
  from PIL import Image,ImageChops
  image_stats=[]
  for p in pngs:
   im=Image.open(p).convert('L'); bbox=ImageChops.invert(im).getbbox()
   image_stats.append({'file':p.name,'width':im.width,'height':im.height,'content_bbox':bbox})
 except Exception as e: image_stats=[{'error':str(e)}]
 logs='\n'.join(p.read_text(errors='replace') for p in paper.glob('*.log'))
 warnings={
  'undefined_references':len(re.findall(r'undefined references?',logs,re.I)),
  'undefined_citations':len(re.findall(r'citation [`\'].*?undefined',logs,re.I)),
  'overfull_boxes':len(re.findall(r'Overfull \\[hv]box',logs)),
  'underfull_boxes':len(re.findall(r'Underfull \\[hv]box',logs)),
 }
 report={'pdf':str(pdf.relative_to(root)),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':pages,'reference_start_page':ref_page,
         'page_nonspace_characters':lengths,'near_blank_pages':[i+1 for i,n in enumerate(lengths) if n<120],
         'fonts':font_rows,'unembedded_font_rows':unembedded,'suspicious_identity_or_path_patterns':suspicious,'latex_warnings':warnings,'image_stats':image_stats}
 report['accepted']=bool(pages and pages>=10 and ref_page and not report['near_blank_pages'] and not unembedded and not suspicious and warnings['undefined_references']==0 and warnings['undefined_citations']==0 and warnings['overfull_boxes']==0)
 (out/'pdf-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({k:report[k] for k in ('pages','reference_start_page','near_blank_pages','unembedded_font_rows','suspicious_identity_or_path_patterns','latex_warnings','accepted')},ensure_ascii=False))
if __name__=='__main__': main(sys.argv[1])
