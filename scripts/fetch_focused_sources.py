"""Fetch a short, explicit list of public primary documents for the focused review."""
import json, pathlib, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pypdf import PdfReader

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEST=ROOT/'evidence/raw/focused_root'
DEST.mkdir(parents=True,exist_ok=True)
ITEMS={
 'mamledesai2020.pdf':'https://mdpi-res.com/d_attachment/applsci/applsci-10-07298/article_deploy/applsci-10-07298.pdf',
 'masklennet2026.pdf':'https://mdpi-res.com/d_attachment/jmmp/jmmp-10-00286/article_deploy/jmmp-10-00286.pdf',
 'yang2025.pdf':'https://journal.ump.edu.my/ijame/article/download/11406/3777/53932',
}
def fetch(item):
 name,url=item
 record={'url':url,'file':name,'accessed':datetime.now(timezone.utc).isoformat()}
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(request,timeout=40) as r: data=r.read()
  p=DEST/name;p.write_bytes(data)
  reader=PdfReader(p)
  p.with_suffix('.txt').write_text('\n'.join(f'=== PDF p.{i+1} ===\n'+(pg.extract_text() or '') for i,pg in enumerate(reader.pages)),encoding='utf-8')
  record['status']='saved';record['pages']=len(reader.pages)
 except Exception as e:record['status']=str(e)
 return record
with ThreadPoolExecutor(max_workers=3) as ex: records=list(ex.map(fetch,ITEMS.items()))
(DEST/'download_log.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
