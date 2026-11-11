"""Audit record consistency and expose incomplete searches, without claiming global recall."""
import argparse, csv, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def audit(data,plan,benchmarks):
    errors=[]; warnings=[]
    ids={}
    for key,field in [('search_log','search_id'),('candidates','candidate_id'),('citation_edges','edge_id'),('retrieval_attempts','attempt_id')]:
        values=[r.get(field,'') for r in data[key]]; ids[key]=set(values)
        if '' in values or len(values)!=len(set(values)): errors.append(f'{key}: ID欠落または重複')
    for edge in data['citation_edges']:
        if edge['candidate_id'] not in ids['candidates']: errors.append(f'{edge["edge_id"]}: 未登録候補')
        if edge['direction'] not in ['backward','forward','related','関連','version']: warnings.append(f'{edge["edge_id"]}: 非標準方向 {edge["direction"]}')
    for q in data['search_log']:
        for field in ['executed_at','query','provider','result_scope']:
            if not q.get(field): errors.append(f'{q["search_id"]}: {field}欠落')
        if 'returned_count' not in q: errors.append(f'{q["search_id"]}: 返却件数の記録欠落')
    for attempt in data['retrieval_attempts']:
        if not all(attempt.get(k) for k in ['route','executed_at','result']): errors.append(f'{attempt["attempt_id"]}: 取得試行の必須項目欠落')
        if not attempt.get('url') and not any(x in attempt['result'] for x in ['未発見','得られず']): errors.append(f'{attempt["attempt_id"]}: 取得URLまたはURL未発見の説明欠落')
    seed_rows=[]
    for scope,seeds in plan['expected_seed_ids'].items():
        for seed in seeds:
            for direction in plan['directions']:
                checks=[r for r in data['seed_checks'] if r['seed_id']==seed and r['direction']==direction]
                complete=[]
                for c in checks:
                    a,b=c.get('available_total'),c.get('screened_count')
                    if isinstance(a,int) and isinstance(b,int) and a==b and not any(x in c['scope_status'] for x in ['一部','部分','未完','未取得','上位']): complete.append(c)
                state='申告した取得集合を全件一次選別' if complete else '部分確認／総数未確認' if checks else '未実施'
                seed_rows.append({'scope':scope,'seed_id':seed,'direction':direction,'status':state,'record_count':len(checks),'details':' | '.join(f"{c.get('screened_count')}/{c.get('available_total')}: {c['scope_status']}" for c in checks)})
                if state=='未実施': warnings.append(f'{seed}/{direction}: 計画した方向の記録なし')
    for scope,b in benchmarks.items():
        sources={s['source_id'] for s in b['sources']}; claims={c['claim_id'] for c in b['claims']}
        linked=set()
        for l in b['claim_evidence']:
            if l['source_id'] not in sources or l['claim_id'] not in claims: errors.append(f'{scope}: 壊れたClaim/Sourceリンク {l}')
            linked.add(l['claim_id'])
        if claims-linked: errors.append(f'{scope}: 根拠対応のないClaim {sorted(claims-linked)}')
        for r in b['records']:
            if not all(r.get(k) for k in ['labels','performance','split','verification','locator']): errors.append(f'{r["id"]}: 比較表必須項目欠落')
            if '保留' in r['status'] and not any(a.get('record_id')==r['id'] for a in data['retrieval_attempts']): warnings.append(f'{r["id"]}: 本周回の本文取得試行が未記録')
    unresolved=[c for c in data['candidates'] if any(x in c['decision'] for x in ['保留','未確認','要確認'])]
    return {'structural_status':'PASS' if not errors else 'FAIL','errors':errors,'warnings':warnings,'search_rows':len(data['search_log']),'candidate_discovery_rows':len(data['candidates']),'candidate_keys':len({c.get('canonical_candidate_id',c['candidate_id']) for c in data['candidates']}),'unresolved_discovery_rows':len(unresolved),'unresolved_candidate_keys':len({c.get('canonical_candidate_id',c['candidate_id']) for c in unresolved}),'citation_edges':len(data['citation_edges']),'retrieval_attempts':len(data['retrieval_attempts']),'planned_seed_directions':len(seed_rows),'seed_states':dict(Counter(r['status'] for r in seed_rows)),'seed_checks':seed_rows,'coverage_conclusion':'選定seedの追跡状況は監査可能。新規候補が継続発見され、再帰追跡・独立検索式回収試験・除外再査読が未完了。完全網羅・探索飽和を主張しない。'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');args=p.parse_args()
    d=json.loads((ROOT/'data/round2_integrated.json').read_text(encoding='utf-8'))
    plan=json.loads((ROOT/'data/round2_search_plan.json').read_text(encoding='utf-8'))
    books={s:json.loads((ROOT/'data'/f).read_text(encoding='utf-8')) for s,f in [('工具','focused_integrated.json'),('工業','industrial_integrated.json')]}
    result=audit(d,plan,books)
    if args.self_test:
        import copy
        broken=copy.deepcopy(d);broken['citation_edges'][0]['candidate_id']='MISSING';del broken['search_log'][0]['query']
        a=audit(broken,plan,books)
        assert a['structural_status']=='FAIL' and any('未登録候補' in e for e in a['errors']) and any('query欠落' in e for e in a['errors'])
        absent=copy.deepcopy(d);absent['seed_checks']=[]
        assert audit(absent,plan,books)['seed_states']=={'未実施':32}
        print('Fault-injection self-test PASS');return
    (ROOT/'evidence/round2/audit_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    with (ROOT/'evidence/round2/seed_coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(result['seed_checks'][0]));w.writeheader();w.writerows(result['seed_checks'])
    print(json.dumps({k:v for k,v in result.items() if k!='seed_checks'},ensure_ascii=False))
    if result['errors']:raise SystemExit(1)
if __name__=='__main__':main()
