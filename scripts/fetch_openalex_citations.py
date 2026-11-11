"""Fetch a bounded citation neighborhood; never turn a partial page into zero findings."""
import argparse,csv,json,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone,timedelta

p=argparse.ArgumentParser();p.add_argument('seed_id');p.add_argument('work_id');p.add_argument('--as-of',default='2026-11-11');p.add_argument('--max-pages',type=int,default=10);a=p.parse_args()
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'evidence/raw/round2_root'/a.seed_id;out.mkdir(parents=True,exist_ok=True)
log=[]
def get(url,name):
 started=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'LiteratureBenchmark/1.0'})
  with urllib.request.urlopen(req,timeout=30) as response:body=json.load(response)
  (out/(name+'.json')).write_text(json.dumps(body,ensure_ascii=False),encoding='utf-8')
  log.append({'at':started,'url':url,'status':'success','returned':len(body.get('results',[])),'count':body.get('meta',{}).get('count')})
  return body
 except Exception as e:
  log.append({'at':started,'url':url,'status':'failed','error':str(e)});return None
work=get('https://api.openalex.org/works/'+a.work_id,'seed')
if work is None:
 (out/'retrieval_log.json').write_text(json.dumps({'seed_id':a.seed_id,'as_of':a.as_of,'directions':{},'requests':log},ensure_ascii=False,indent=2),encoding='utf-8')
 raise SystemExit('Seed request failed; attempt recorded. No zero-result inference.')
results=[];direction_status={}
refs=work.get('referenced_works',[])
for start in range(0,len(refs),50):
 url='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':'openalex:'+'|'.join(x.rsplit('/',1)[-1] for x in refs[start:start+50]),'per_page':200})
 body=get(url,'backward_'+str(start))
 if body:results.extend(('backward',x) for x in body['results'])
direction_status['backward']={'listed_ids':len(refs),'retrieved':sum(k=='backward' for k,x in results)}
cursor='*';total=None;complete=False
for page in range(a.max_pages):
 url='https://api.openalex.org/works?'+urllib.parse.urlencode({'filter':f'cites:{a.work_id},to_publication_date:{a.as_of}','per_page':200,'cursor':cursor})
 body=get(url,'forward_'+str(page))
 if not body:break
 total=body['meta']['count'];results.extend(('forward',x) for x in body['results']);cursor=body['meta'].get('next_cursor')
 if not cursor or not body['results'] or sum(k=='forward' for k,x in results)>=total:complete=True;break
direction_status['forward']={'query_total':total,'retrieved':sum(k=='forward' for k,x in results),'pagination_complete':complete,'next_cursor':cursor if not complete else None}
def abstract(inv):
 if not inv:return ''
 seq={pos:word for word,positions in inv.items() for pos in positions};return ' '.join(seq[k] for k in sorted(seq))
rows=[]
for direction,w in results:
 rows.append({'seed_id':a.seed_id,'direction':direction,'openalex_id':w['id'],'doi':w.get('doi') or '', 'title':w.get('title'), 'year':w.get('publication_year'),'publication_date':w.get('publication_date'),'abstract':abstract(w.get('abstract_inverted_index')),'landing_url':(w.get('primary_location') or {}).get('landing_page_url') or '', 'decision':'未判定','reason':''})
with (out/'screening.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['seed_id']);writer.writeheader();writer.writerows(rows)
(out/'retrieval_log.json').write_text(json.dumps({'seed_id':a.seed_id,'as_of':a.as_of,'directions':direction_status,'requests':log},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'seed_id':a.seed_id,'directions':direction_status,'rows':len(rows)},ensure_ascii=False))
