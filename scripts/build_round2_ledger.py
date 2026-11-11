"""Combine the four reviewed discovery bundles and export auditable search tables."""
import csv, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence/round2'; EV.mkdir(exist_ok=True)
schema=json.loads((ROOT/'data/round2_schema.json').read_text(encoding='utf-8'))
names=['round2_root.json','round2_wear.json','round2_vit.json','round2_vlm.json']
keys=['search_log','candidates','citation_edges','retrieval_attempts','seed_checks','record_updates','performance_rows']
d={k:[] for k in keys}
for name in names:
    bundle=json.loads((ROOT/'data'/name).read_text(encoding='utf-8-sig'))
    for k in keys:
        for row in bundle.get(k,[]): d[k].append({**row,'bundle':name})
def csvout(path,rows,columns=None):
    columns=columns or list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader()
        w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
for row in d['citation_edges']+d['seed_checks']:
    row['direction']={'後方':'backward','前方':'forward'}.get(row['direction'],row['direction'])
canonical={}; aliases=[]
for c in d['candidates']:
    doi=str(c.get('doi','')).lower().replace('https://doi.org/','').strip()
    title=''.join(ch for ch in c['title'].casefold() if ch.isalnum())
    key=doi if doi.startswith('10.') else title
    canonical.setdefault(key,c['candidate_id'])
    c['canonical_candidate_id']=canonical[key]
    aliases.append({'candidate_id':c['candidate_id'],'canonical_candidate_id':canonical[key],'match_key':key,'record_id':c.get('record_id','')})
# Discovery rows remain separate; the canonical ledger prevents adding their counts as papers.
d['candidate_aliases']=aliases
for key in keys+['candidate_aliases']:
    csvout(EV/(key+'.csv'),d[key])
csvout(EV/'unresolved_candidates.csv',[r for r in d['candidates'] if any(x in r['decision'] for x in ['保留','要確認','未確認'])])
plan={'as_of':'2026-11-11','round':'Round2','expected_seed_ids':{'工具':['FT001','FIA02','FIA04','FT002','MM001'],'工業ViT':['IT003','IT004','IT005','IT006','IT009'],'工業VLM_MLLM':['IV001','IV002','IV003','IM001','IM002','IM003']},'directions':['backward','forward'],'stop_condition':'選定主要16本の両方向を調査し、範囲と保留を記録。新発見論文の再帰的全件追跡は次周回。探索飽和は主張しない','known_item_recall_test':'独立テスト未実施','independent_exclusion_review':'独立二重選別・無作為除外監査は未実施'}
(ROOT/'data/round2_search_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/round2_integrated.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
for schema_key,name in [('search_log_fields','search_log'),('candidate_fields','candidates'),('citation_edge_fields','citation_edges'),('retrieval_fields','retrieval_attempts'),('seed_check_fields','seed_checks')]:
    csvout(ROOT/'methods/templates'/(name+'.csv'),[],schema[schema_key])
print(json.dumps({k:len(v) for k,v in d.items()},ensure_ascii=False))
