"""Merge reviewed industrial defect-type papers and preserve claim-level provenance."""
import csv, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence/industrial_defect_classification'
EV.mkdir(parents=True,exist_ok=True)
def read(name): return json.loads((ROOT/'data'/name).read_text(encoding='utf-8-sig'))
def text(v): return '; '.join(map(str,v)) if isinstance(v,list) else json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else str(v) if v is not None else '未確認'
def csvout(path,rows,cols=None):
 cols=cols or list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore'); w.writeheader()
  w.writerows({k:text(r.get(k,'')) for k in cols} for r in rows)

keys=['records','sources','claims','claim_evidence','search_log','exclusions']
d={k:[] for k in keys}
for name in ['industrial_vit.json','industrial_vlm.json','industrial_mllm.json','industrial_root.json']:
 bundle=read(name)
 for k in keys: d[k].extend(bundle.get(k,[]))
annotations=read('industrial_annotations.json') if (ROOT/'data/industrial_annotations.json').exists() else {}
fields=read('industrial_schema.json')['record_fields']
for r in d['records']:
 r.update(annotations.get(r['id'],{}))
 for f in fields: r.setdefault(f,'未確認')
 for f in fields:
  if f!='source_ids' and not isinstance(r[f],(int,float,bool)): r[f]=text(r[f])
 if isinstance(r['source_ids'],str): r['source_ids']=[x for x in re.split(r'[;；／/,|\s]+',r['source_ids']) if x]
 family=r['model_family']
 r['family_group']='MLLM' if 'MLLM' in family else 'LLM（テキスト中心）' if 'LLM' in family and 'VLM' not in family else 'VLM／VLM由来特徴' if 'VLM' in family or 'CLIP' in family or r['id'].startswith('IV') else '視覚Transformer'
 r['adoption_group']='保留' if '保留' in r['status'] or '未確定' in r['status'] else '関連' if '関連' in r['status'] else '対象外' if '除外' in r['status'] or '対象外' in r['status'] else '採用'
 r['claim_ids']='; '.join(c['claim_id'] for c in d['claims'] if c['entity_id']==r['id'])

# Canonical source URLs deduplicate repeated references, while retaining an alias ledger.
source_map={}; seen={}; unique=[]; aliases=[]
for s in d['sources']:
 if isinstance(s.get('primary'),bool): s['primary']='一次情報' if s['primary'] else '二次情報'
 key=str(s.get('url','')).strip().rstrip('/')
 if key and key in seen:
  source_map[s['source_id']]=seen[key]
  aliases.append({'alias_source_id':s['source_id'],'canonical_source_id':seen[key],'url':key})
 else:
  source_map[s['source_id']]=s['source_id']; seen[key]=s['source_id']; unique.append(s)
d['sources']=unique
for r in d['records']:
 r['source_ids']=list(dict.fromkeys(source_map[s] for s in r['source_ids']))
for link in d['claim_evidence']: link['source_id']=source_map[link['source_id']]
for e in d['exclusions']:
 if isinstance(e.get('source_ids'),str): e['source_ids']=[x for x in re.split(r'[;；／/,|\s]+',e['source_ids']) if x]
 if isinstance(e.get('source_ids'),list): e['source_ids']=list(dict.fromkeys(source_map.get(s,s) for s in e['source_ids']))

for key,idfield in [('records','id'),('sources','source_id'),('claims','claim_id')]:
 ids=[r[idfield] for r in d[key]]
 assert len(ids)==len(set(ids)),f'Duplicate {key} IDs'
source_ids={s['source_id'] for s in d['sources']}; claim_ids={c['claim_id'] for c in d['claims']}
assert all(l['source_id'] in source_ids and l['claim_id'] in claim_ids for l in d['claim_evidence'])
assert {l['claim_id'] for l in d['claim_evidence']}==claim_ids,'Claim without evidence'
assert all(s in source_ids for r in d['records'] for s in r['source_ids'])
paper_keys={}
for r in d['records']:
 doi=r['doi'].lower().removeprefix('https://doi.org/').strip()
 title=re.sub(r'[^a-z0-9]','',r['title'].lower())
 for k in [title]+([doi] if doi.startswith('10.') else []):
  assert k not in paper_keys or paper_keys[k]==r['id'],f'Duplicate paper {paper_keys.get(k)} / {r["id"]}'
  paper_keys[k]=r['id']

main=[r for r in d['records'] if r['adoption_group']=='採用']
related=[r for r in d['records'] if r['adoption_group']=='関連']
held=[r for r in d['records'] if r['adoption_group']=='保留']
summary=[]
for family in ['視覚Transformer','VLM／VLM由来特徴','MLLM','LLM（テキスト中心）']:
 rows=[r for r in d['records'] if r['family_group']==family]
 summary.append({'model_family':family,'accepted_count':sum(r['adoption_group']=='採用' for r in rows),'related_count':sum(r['adoption_group']=='関連' for r in rows),'held_count':sum(r['adoption_group']=='保留' for r in rows),'paper_ids':'; '.join(r['id'] for r in rows)})
d['as_of']='2026-11-11'; d['family_summary']=summary
d['stats']={'accepted':len(main),'related':len(related),'held':len(held),'detailed_records':len(d['records']),'sources':len(d['sources']),'claims':len(d['claims']),'claim_links':len(d['claim_evidence']),'search_rows':len(d['search_log']),'exclusion_rows':len(d['exclusions']),'source_aliases':len(aliases)}
(ROOT/'data/industrial_integrated.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
for key in ['sources','claims','claim_evidence','search_log','exclusions']: csvout(EV/(key+'.csv'),d[key])
csvout(EV/'source_aliases.csv',aliases,['alias_source_id','canonical_source_id','url'])
csvout(EV/'unverified_items.csv',[{'id':r['id'],'status':r['status'],'verification':r['verification'],'limitations':r['limitations'],'source_ids':r['source_ids']} for r in d['records']])
csvout(ROOT/'outputs/industrial_defect_classification_benchmark.csv',d['records'])
csvout(ROOT/'outputs/industrial_model_family_summary.csv',summary)
print(json.dumps(d['stats'],ensure_ascii=False))
