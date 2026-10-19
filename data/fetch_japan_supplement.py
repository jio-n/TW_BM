import pathlib,json,urllib.request,concurrent.futures,re
from html import unescape
ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/'evidence/raw/japan_supplement'; RAW.mkdir(parents=True,exist_ok=True)
DOIS=['10.20965/ijat.2016.p0767','10.20965/ijat.2019.p0125','10.1299/transjsme.17-00433','10.1299/jsmelem.2025.11.os05-3']
def fetch(item):
 i,doi=item
 try:
  with urllib.request.urlopen('https://api.crossref.org/works/'+doi,timeout=45) as response: data=json.load(response)
  (RAW/f'R{i:04d}_crossref.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
  m=data['message']
  return dict(id=f'R{i:04d}',doi=doi,title=m.get('title'),authors=[a.get('given','')+' '+a.get('family','') for a in m.get('author',[])],affiliations=[x['name'] for a in m.get('author',[]) for x in a.get('affiliation',[])],published=m.get('published'),online=m.get('published-online'),print=m.get('published-print'),journal=m.get('container-title'),abstract=unescape(re.sub('<[^>]+>',' ',m.get('abstract',''))))
 except Exception as e:return dict(id=f'R{i:04d}',doi=doi,error=str(e))
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:out=list(p.map(fetch,enumerate(DOIS,30)))
 (RAW/'metadata.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(out,ensure_ascii=True,indent=2))
