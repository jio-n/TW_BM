"""Persistent literature-review ledgers. Standard library only; no network crawler."""
import argparse
import copy
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

KIT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((KIT/'schema.json').read_text(encoding='utf-8'))
TABLES=SCHEMA['tables']
KEYS={t:cols[0] for t,cols in TABLES.items()}
DEFAULTS={
 'queries':dict(required='true',planned_limit='100',priority='3',state='planned'),
 'runs':dict(status='success',semantics='uncertain',total_kind='unknown'),
 'papers':dict(identity_status='unresolved',screening='unreviewed',access_status='unknown',download_status='not_attempted',reading_status='not_started',extraction_status='not_started',backward_status='not_started',forward_status='not_started',user_priority='3'),
 'tasks':dict(status='pending',priority='1'),
 'evidence':dict(verification='unknown'),
 'citation_checks':dict(total_kind='unknown',state='not_started'),
 'known_items':dict(database_indexed='unknown',test_type='posthoc')}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def number(value):
    return None if value in ('',None) else float(value)


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')


def normalize(table,row):
    unknown=set(row)-set(TABLES[table])
    if unknown: raise ValueError(f'{table}: unknown fields {sorted(unknown)}')
    values={**DEFAULTS.get(table,{}),**row}
    return {k:('' if values.get(k) is None else str(values.get(k,'')).lower() if isinstance(values.get(k),bool) else str(values.get(k,''))) for k in TABLES[table]}


def write_table(path,table,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.csv.tmp')
    with tmp.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=TABLES[table]);w.writeheader();w.writerows(rows)
    tmp.replace(path)


def load(project):
    cfg=json.loads((project/'project.json').read_text(encoding='utf-8-sig'))
    data={}
    for table in TABLES:
        with (project/'tables'/f'{table}.csv').open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=TABLES[table]:raise ValueError(f'{table}: schema headers do not match')
            data[table]=list(reader)
    return cfg,data


def digest(cfg,data):
    return hashlib.sha256(json.dumps([cfg,data],sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def events(project):
    path=project/'history/events.jsonl'
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line] if path.exists() else []


def log_event(project,action,reason,before,after,changes):
    path=project/'history/events.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
    event=dict(event_id=f'EV{len(events(project))+1:06}',at=now(),action=action,reason=reason,before_hash=before,after_hash=after,changes=changes)
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')


def audit(cfg,data,project=None):
    errors=[];warnings=[]
    indexes={t:{r[KEYS[t]]:r for r in rows} for t,rows in data.items()}
    def err(message):errors.append(message)
    numeric_fields={'queries':['planned_limit','priority'],'runs':['total_hits','start_rank','requested_count','returned_count'],'hits':['rank'],'papers':['year','relevance','citation_count','user_priority'],'tasks':['priority'],'citation_checks':['total_hits','checked_count']}
    for t,fields in numeric_fields.items():
        for r in data[t]:
            for field in fields:
                if r[field] and (not r[field].isdigit()):err(f'{r[KEYS[t]]}: {field} must be a nonnegative integer or blank')
    if errors:return dict(status='FAIL',errors=errors,warnings=warnings)
    for t,rows in data.items():
        if len(indexes[t])!=len(rows):err(f'{t}: duplicate IDs')
        for r in rows:
            ident=r[KEYS[t]]
            if not ident:err(f'{t}: empty ID')
            for field,allowed in SCHEMA['enums'].items():
                target,key=field.split('.')
                if t==target and r[key] not in allowed:err(f'{ident}: invalid {key}={r[key]}')
    for q in data['queries']:
        if q['required'] not in ['true','false']:err(f'{q["query_id"]}: required must be true/false')
        if q['priority'] not in ['','1','2','3','4','5']:err(f'{q["query_id"]}: priority must be 1–5 or blank (default 3)')
        if not q['planned_limit'] or int(q['planned_limit'])<1:err(f'{q["query_id"]}: planned limit must be positive')
    for run in data['runs']:
        rid=run['run_id']
        if run['query_id'] not in indexes['queries']:err(f'{rid}: unknown query')
        if not run['executed_at'] or not run['search_set_id']:err(f'{rid}: missing time/search set')
        hits=[h for h in data['hits'] if h['run_id']==rid]
        if run['status']=='failed':
            if run['total_hits'] or run['returned_count'] or hits:err(f'{rid}: failed search encoded as numeric results')
        elif run['returned_count']=='' or int(run['returned_count'])!=len(hits):err(f'{rid}: returned count differs from recorded hits')
        if run['total_kind']=='unknown' and run['total_hits']:err(f'{rid}: unknown total given a number')
        if run['total_kind'] in ['exact','approximate'] and run['total_hits']=='':err(f'{rid}: reported total is missing')
        if run['total_kind']=='exact' and run['total_hits'] and hits and all(h['rank'] for h in hits) and max(int(h['rank']) for h in hits)>int(run['total_hits']):err(f'{rid}: rank exceeds exact result total')
        if run['status']=='success' and run['semantics']!='checked':warnings.append(f'{rid}: 検索式の意味確認が未完了')
    for h in data['hits']:
        if h['run_id'] not in indexes['runs'] or h['paper_id'] not in indexes['papers']:err(f'{h["hit_id"]}: orphan run/paper')
        if not h['rank'] or int(h['rank'])<1:err(f'{h["hit_id"]}: invalid rank')
    pairs=[(h['run_id'],h['rank']) for h in data['hits']]
    if len(pairs)!=len(set(pairs)):err('duplicate rank in one run')
    positions=defaultdict(set)
    for h in data['hits']:
        r=indexes['runs'].get(h['run_id'],{})
        if r.get('status')=='success':positions[(r['query_id'],r['search_set_id'],h['rank'])].add(h['paper_id'])
    if any(len(ids)>1 for ids in positions.values()):warnings.append('同一検索集合・順位に異なる論文。検索結果が変動した可能性があり、集合の取得完了を確定しない')
    for e in data['evidence']:
        if e['paper_id'] not in indexes['papers']:err(f'{e["evidence_id"]}: orphan paper')
        if e['verification']=='confirmed' and (not e['url'] or not e['locator'] or not e['value']):err(f'{e["evidence_id"]}: confirmed evidence missing source/location/value')
    for p in data['papers']:
        pid=p['paper_id']
        if not p['title'] or not p['url']:err(f'{pid}: missing title/URL')
        if p['user_priority'] not in ['','1','2','3','4','5']:err(f'{pid}: priority must be 1–5 or blank (default 3)')
        if p['year'] and int(p['year'])>int(cfg['as_of'][:4]):warnings.append(f'{pid}: 発表年が基準年より後。先行公開日・巻号年を確認する')
        if p['screening']!='unreviewed' and not p['screening_reason']:err(f'{pid}: decision without reason')
        if p['relevance'] and (number(p['relevance']) not in [0,1,2,3] or not p['relevance_reason']):err(f'{pid}: relevance must be 0–3 with reason')
        if p['citation_count'] and (number(p['citation_count'])<0 or not p['citation_source'] or not p['citation_checked_at']):err(f'{pid}: citation count needs source/date')
        if p['download_status']=='saved':
            if not p['local_path']:err(f'{pid}: saved file has no path')
            elif project and not (project/p['local_path']).exists():warnings.append(f'{pid}: 保存ファイルがこの環境にない（可搬性・移動を確認）')
        if p['extraction_status']=='complete':
            checked={e['field'] for e in data['evidence'] if e['paper_id']==pid and e['verification']=='confirmed'}
            missing=set(cfg['required_extraction_fields'])-checked
            if missing:err(f'{pid}: complete extraction missing confirmed {sorted(missing)}')
            if p['reading_status'] not in ['sections','full']:err(f'{pid}: extraction complete without relevant-section reading')
        for direction in ['backward','forward']:
            if p[direction+'_status']=='complete' and not any(c['paper_id']==pid and c['direction']==direction and c['state']=='complete' for c in data['citation_checks']):err(f'{pid}: {direction} complete without citation check')
    dois=defaultdict(list)
    for p in data['papers']:
        doi=p['doi'].lower().strip().removeprefix('https://doi.org/').removeprefix('doi:').strip()
        if doi:dois[doi].append(p['paper_id'])
    for doi,ids in dois.items():
        if len(ids)>1:warnings.append(f'DOI重複候補 {doi}: {", ".join(ids)}。同一workを確認して統合する')
    for c in data['citation_checks']:
        if c['paper_id'] not in indexes['papers']:err(f'{c["check_id"]}: orphan seed')
        if c['state']=='complete' and (c['total_kind']!='exact' or c['total_hits']=='' or c['checked_count']=='' or int(c['checked_count'])!=int(c['total_hits']) or not c['evidence_url']):err(f'{c["check_id"]}: citation completion lacks exact checked set')
    for task in data['tasks']:
        tid=task['task_id'];kind=task['target_type']
        target_table={'paper':'papers','query':'queries'}.get(kind)
        if target_table and task['target_id'] not in indexes[target_table]:err(f'{tid}: unknown target')
        if task['priority'] not in ['1','2','3','4','5']:err(f'{tid}: priority must be 1–5')
        if task['status']=='done' and (not task['completed_at'] or not task['evidence_ref']):err(f'{tid}: done without completion time/evidence')
        if task['status']=='done' and task['evidence_ref']:
            refs=[x.strip() for x in task['evidence_ref'].split(';')]
            if not any(ref in indexes['evidence'] or ref in indexes['runs'] or ref in indexes['citation_checks'] or ref.startswith(('https://','http://')) for ref in refs):err(f'{tid}: completion evidence is not a registered ID or source URL')
            paper=indexes['papers'].get(task['target_id'],{})
            if task['action']=='read_fulltext' and paper.get('reading_status') not in ['sections','full']:err(f'{tid}: read task done but paper still unread')
            if task['action']=='extract' and paper.get('extraction_status')!='complete':err(f'{tid}: extraction task done but paper incomplete')
    for item in data['known_items']:
        if item['paper_id'] not in indexes['papers'] or item['query_id'] not in indexes['queries']:err(f'{item["test_id"]}: unknown test target')
        if item['found_run_id']:
            run=indexes['runs'].get(item['found_run_id'])
            if not run or run['query_id']!=item['query_id'] or not any(h['run_id']==item['found_run_id'] and h['paper_id']==item['paper_id'] for h in data['hits']):err(f'{item["test_id"]}: known item not found in claimed run')
            elif item['test_type']=='predeclared':
                try:
                    registered=datetime.fromisoformat(item['registered_at']).replace(tzinfo=timezone.utc)
                    searched=datetime.fromisoformat(run['executed_at']).replace(tzinfo=timezone.utc)
                    if registered>searched:err(f'{item["test_id"]}: predeclared test registered after search')
                except ValueError:err(f'{item["test_id"]}: known-item test needs an ISO registration time')
    weights=cfg['priority']['weights']
    if abs(sum(weights.values())-1)>1e-8 or min(weights.values())<0:err('priority weights must be nonnegative and sum to 1')
    if cfg['priority']['exploration_fraction']+cfg['priority']['recent_fraction']>1:err('queue allocation exceeds 100%')
    if min(cfg['priority']['exploration_fraction'],cfg['priority']['recent_fraction'])<0:err('queue allocations must be nonnegative')
    if any(not isinstance(n,int) or n<1 for n in cfg['limits'].values()):err('batch/target/depth limits must be positive integers')
    if cfg['priority']['recency_years']<=0 or cfg['priority']['citation_rate_cap']<=0:err('priority denominators must be positive')
    if cfg['stop_rules']['claim_exhaustive']:err('this kit cannot certify exhaustive coverage')
    if not cfg['scope']['include']:warnings.append('採用条件が未設定')
    if not cfg['scope']['exclude']:warnings.append('除外条件が未設定')
    if project:
        history=events(project)
        if not history or history[-1]['after_hash']!=digest(cfg,data):warnings.append('履歴に対応しない初期データ／直接編集あり。理由付きcheckpointで記録する')
        if any(a['after_hash']!=b['before_hash'] for a,b in zip(history,history[1:])):warnings.append('イベント間に未追跡の変更あり。過去の差分記録は不完全')
    return dict(status='FAIL' if errors else 'WARN' if warnings else 'PASS',errors=errors,warnings=warnings)


def priority(p,cfg):
    year=number(p['year']);asof=int(cfg['as_of'][:4])
    age=asof-year if year is not None and year<=asof else None
    components={'relevance':number(p['relevance'])/3 if p['relevance'] else None,
                'recency':max(0,1-age/cfg['priority']['recency_years']) if age is not None else None,
                'citations':min(1,number(p['citation_count'])/max(1,age+1)/cfg['priority']['citation_rate_cap']) if p['citation_count'] and p['citation_source'] and p['citation_checked_at'] and age is not None else None}
    weights=cfg['priority']['weights']
    score=sum(weights[k]*v for k,v in components.items() if v is not None)*100
    known=sum(weights[k] for k,v in components.items() if v is not None)
    return dict(score=round(score,2),score_known_weight=round(known,3),score_upper=round(score+(1-known)*100,2))


def summarize(cfg,data):
    pindex={p['paper_id']:p for p in data['papers']};qindex={q['query_id']:q for q in data['queries']}
    byrun=defaultdict(list)
    for h in data['hits']:byrun[h['run_id']].append(h)
    groups=defaultdict(list)
    for r in sorted(data['runs'],key=lambda r:r['executed_at']):groups[(r['query_id'],r['search_set_id'])].append(r)
    rows=[]
    for (qid,ssid),runs in groups.items():
        q=qindex[qid];valid=[r for r in runs if r['status']=='success' and r['semantics']!='invalid']
        hits=[h for r in valid for h in byrun[r['run_id']]]
        ranks={int(h['rank']) for h in hits};paper_ids={h['paper_id'] for h in hits}
        totals={int(r['total_hits']) for r in valid if r['total_hits']}
        kinds={r['total_kind'] for r in valid}
        positions=defaultdict(set)
        for h in hits:positions[h['rank']].add(h['paper_id'])
        stable=not any(len(ids)>1 for ids in positions.values())
        consistent=len(totals)==1 and len(kinds)==1 and stable
        total=next(iter(totals)) if consistent else None
        kind=next(iter(kinds)) if consistent else 'unknown'
        first=1
        while first in ranks:first+=1
        target=int(q['planned_limit'] or cfg['limits']['per_query_target'])
        if kind=='exact' and total is not None:target=min(target,total)
        decisions=Counter(pindex[pid]['screening'] for pid in paper_ids)
        decided=sum(decisions[k] for k in ['include','potential','exclude']);positive=decisions['include']+decisions['potential']
        rate=positive/decided if decided else None
        prospect='不明（判定不足）' if decided<cfg['stop_rules']['min_decided_for_yield'] else '高め（取得済み範囲）' if rate>=.3 else '中程度（取得済み範囲）' if rate>=.1 else '低め（取得済み範囲）'
        semantics_ok=bool(valid) and all(r['semantics']=='checked' for r in valid)
        if not semantics_ok:prospect='不明（検索式の意味要確認）'
        notes=[]
        if not consistent:notes.append('総数なし／スナップショット内の総数差')
        if not stable:notes.append('同順位の論文が変動。別検索集合への分離・再取得が必要')
        if not semantics_ok:notes.append('検索式の意味は未検証。探索完了に数えない')
        if kind=='approximate':notes.append('総数は概数。残件数を確定しない')
        rows.append(dict(query_id=qid,search_set_id=ssid,source=q['source'],query_text=q['query_text'],total_hits=total,total_kind=kind,retrieved_slots=len(ranks),unique_papers=len(paper_ids),first_missing_rank=first,remaining_slots=max(0,total-len(ranks)) if kind=='exact' and total is not None else None,remaining_to_target=sum(i not in ranks for i in range(1,target+1)),decided=decided,positive=positive,yield_pct=round(rate*100,1) if rate is not None else None,prospect=prospect,notes='／'.join(notes),semantics_checked=semantics_ok and stable,scope_closed=semantics_ok and stable and kind=='exact' and total is not None and all(i in ranks for i in range(1,total+1))))
    for q in data['queries']:
        if not any(r['query_id']==q['query_id'] for r in data['runs']):
            rows.append(dict(query_id=q['query_id'],search_set_id='未実行',source=q['source'],query_text=q['query_text'],total_hits=None,total_kind='unknown',retrieved_slots=0,unique_papers=0,first_missing_rank=1,remaining_slots=None,remaining_to_target=int(q['planned_limit'] or cfg['limits']['per_query_target']),decided=0,positive=0,yield_pct=None,prospect='未調査',notes=q['notes'],semantics_checked=False,scope_closed=False))
    latest={r['query_id']:r for r in rows}
    good_queries={qid for qid,s in latest.items() if s['semantics_checked']}
    ps=data['papers'];active=[p for p in ps if p['screening']!='exclude']
    counts=dict(paper_total=len(ps),screen_unreviewed=sum(p['screening']=='unreviewed' for p in ps),screen_potential=sum(p['screening']=='potential' for p in ps),screen_include=sum(p['screening']=='include' for p in ps),screen_hold=sum(p['screening']=='hold' for p in ps),screen_exclude=sum(p['screening']=='exclude' for p in ps),download_saved=sum(p['download_status']=='saved' for p in ps),read_sections_or_full=sum(p['reading_status'] in ['sections','full'] for p in ps),extraction_complete=sum(p['extraction_status']=='complete' for p in ps),user_pending=sum(t['status'] in ['pending','in_progress','blocked'] for t in data['tasks']),required_queries_unsearched=sum(q['required']=='true' and q['query_id'] not in good_queries for q in data['queries']),fulltext_unread=sum(p['reading_status'] not in ['sections','full'] for p in active),extraction_incomplete=sum(p['extraction_status']!='complete' for p in active),saved_unread=sum(p['download_status']=='saved' and p['reading_status'] not in ['sections','full'] for p in active))
    indexed=[i for i in data['known_items'] if i['database_indexed']=='yes' and i['test_type']=='predeclared']
    required=[q for q in data['queries'] if q['required']=='true']
    in_target=set()
    for q in required:
        ss=latest[q['query_id']]['search_set_id']
        for r in groups.get((q['query_id'],ss),[]):
            if r['status']=='success' and r['semantics']=='checked':
                in_target.update(h['paper_id'] for h in byrun[r['run_id']] if int(h['rank'])<=int(q['planned_limit']))
    seeds=sorted([p for p in ps if p['screening']=='include'],key=lambda p:-priority(p,cfg)['score'])[:cfg['limits']['citation_seed_target']]
    def gate(label,observed,limit,unit):return dict(label=label,observed=observed,limit=limit,unit=unit,passed=observed<=limit)
    checks=[gate('必須式の未実施・意味未確認',counts['required_queries_unsearched'],cfg['stop_rules']['max_required_unsearched'],'式'),
            gate('予定範囲未取得',sum(latest[q['query_id']]['remaining_to_target'] for q in required),0,'順位枠（論文数ではない）'),
            gate('予定範囲未選別',sum(pindex[pid]['screening']=='unreviewed' for pid in in_target),cfg['stop_rules']['max_unreviewed_in_target'],'論文'),
            gate('採用論文の抽出未完',sum(p['screening']=='include' and p['extraction_status']!='complete' for p in ps),0,'論文'),
            gate('必須seed未追跡',sum(p[d+'_status'] not in ['complete','not_applicable'] for p in seeds for d in ['backward','forward']),0,'方向'),
            gate('利用者指示未完',counts['user_pending'],cfg['stop_rules']['max_pending_user_tasks'],'指示')]
    if not required:checks.insert(0,gate('必須検索式の計画未設定',1,0,'件'))
    return dict(generated_at=now(),counts=counts,search_sets=rows,plan_checks=checks,known_item_test=dict(eligible=len(indexed),found=sum(bool(i['found_run_id']) for i in indexed)),limitations=['未発見論文の総数・世界全体の網羅率は推定していない。','取得済み上位結果の候補率は現在の判定状態から算出。未知の残ページへ外挿しない。','検索集合間の残順位を足して独立論文数としない。','優先点は読む順番の説明用。品質・正解確率ではなく、欠測重みは未評価。',cfg.get('migration_scope','')])


def next_actions(cfg,data,status):
    actions=[];used=set()
    def add(action,kind,ident,reason,priority_value=3,amount='',lane='優先点',extra=None,aid=None):
        key=(action,kind,ident)
        if key in used:return
        used.add(key)
        actions.append(dict(action_id=aid or f'A-{action}-{ident}',action=action,target_type=kind,target_id=ident,priority=priority_value,amount=amount,reason=reason,lane=lane,**(extra or {})))
    for t in sorted(data['tasks'],key=lambda r:(int(r['priority']),r['created_at'])):
        if t['status'] in ['pending','in_progress']:add(t['action'],t['target_type'],t['target_id'],t['reason'],int(t['priority']),t['amount'],'ユーザー指示',aid=t['task_id'])
    latest={}
    for s in status['search_sets']:latest[s['query_id']]=s
    for q in sorted(data['queries'],key=lambda r:int(r['priority'] or 3)):
        s=latest[q['query_id']]
        if q['state'] in ['paused','closed']:continue
        if s['remaining_to_target'] or not s['semantics_checked']:
            reason=f'次の未取得順位 {s["first_missing_rank"]}、今回目標まで {s["remaining_to_target"]}枠。'+('検索式の意味確認を先行。' if not s['semantics_checked'] else '')
            add('search_more','query',q['query_id'],reason,int(q['priority'] or 3),min(cfg['limits']['screen_batch'],s['remaining_to_target'] or cfg['limits']['screen_batch']),'検索の残範囲')
    candidates=[]
    diagnostic_only={h['paper_id'] for h in data['hits']} - {h['paper_id'] for h in data['hits'] if any(r['run_id']==h['run_id'] and r['status']=='success' for r in data['runs'])}
    for p in data['papers']:
        if p['screening']=='exclude' or (p['paper_id'] in diagnostic_only and not p['relevance']):continue
        action=('screen' if p['screening']=='unreviewed' else 'obtain_fulltext' if p['access_status'] not in ['online_fulltext'] and p['download_status']!='saved' and p['reading_status'] not in ['sections','full'] else 'read_fulltext' if p['reading_status'] not in ['sections','full'] else 'extract' if p['extraction_status']!='complete' else 'verify_identity' if p['identity_status']!='verified_identifier' else None)
        if action:candidates.append((p,action,priority(p,cfg)))
    ranked=sorted(candidates,key=lambda t:(int(t[0]['user_priority'] or 3),-t[2]['score'],t[0]['paper_id']))
    cap=cfg['limits']['screen_batch'];nrecent=int(cap*cfg['priority']['recent_fraction']);nexplore=int(cap*cfg['priority']['exploration_fraction']);nmain=cap-nrecent-nexplore
    selected=[];picked=set()
    for items,n,lane in [(ranked,nmain,'優先点'),(sorted(candidates,key=lambda t:-(number(t[0]['year']) or 0)),nrecent,'新しさ'),(sorted(candidates,key=lambda t:hashlib.sha256((cfg['priority']['seed']+t[0]['paper_id']).encode()).hexdigest()),nexplore,'探索枠')]:
        group=[x for x in items if x[0]['paper_id'] not in picked][:n]
        selected.extend((x,lane) for x in group);picked.update(x[0]['paper_id'] for x in group)
    reads=0
    for (p,action,points),lane in selected:
        if action in ['read_fulltext','extract']:
            if reads>=cfg['limits']['read_batch']:continue
            reads+=1
        add(action,'paper',p['paper_id'],p['title']+'／'+(p['screening_reason'] or 'まだ選別していない'),int(p['user_priority'] or 3),1,lane,points)
    seeds=sorted([p for p in data['papers'] if p['screening']=='include'],key=lambda p:-priority(p,cfg)['score'])[:cfg['limits']['citation_seed_target']]
    for p in seeds:
        for direction in ['backward','forward']:
            if p[direction+'_status'] in ['not_started','partial']:add('trace_'+direction,'paper',p['paper_id'],'採用論文の引用追跡。取得集合と選別数を記録する。',4,cfg['limits']['citation_depth'],'引用の拡張')
    return actions


def save_changes(project,oldcfg,olddata,cfg,data,action,reason):
    result=audit(cfg,data)
    if result['errors']:raise ValueError('\n'.join(result['errors']))
    changes={}
    for t in TABLES:
        before={r[KEYS[t]]:r for r in olddata[t]}
        changed=[{'id':r[KEYS[t]],'before':before.get(r[KEYS[t]]),'after':r} for r in data[t] if before.get(r[KEYS[t]])!=r]
        if changed:changes[t]=changed
    if cfg!=oldcfg:changes['project']={'before':oldcfg,'after':cfg}
    if not changes:return False
    for t in TABLES:
        if t in changes:write_table(project/'tables'/f'{t}.csv',t,data[t])
    if cfg!=oldcfg:dump(project/'project.json',cfg)
    log_event(project,action,reason,digest(oldcfg,olddata),digest(cfg,data),changes)
    return True


def export_rows(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r)) or ['action_id']
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def build(project):
    cfg,data=load(project);check=audit(cfg,data,project)
    if check['errors']:raise ValueError('\n'.join(check['errors']))
    status=summarize(cfg,data);actions=next_actions(cfg,data,status)
    status['data_hash']=digest(cfg,data)
    output=project/'outputs';output.mkdir(exist_ok=True)
    dump(output/'status.json',status);dump(output/'audit.json',check);dump(output/'next.json',actions)
    export_rows(output/'next_actions.csv',actions);export_rows(output/'search_coverage.csv',status['search_sets'])
    from dashboard import render
    (output/'dashboard.html').write_text(render(cfg,data,status,actions,check),encoding='utf-8')
    return status,check


def initialize(args):
    project=args.project
    if project.exists() and any(project.iterdir()):raise ValueError('project directory is not empty; refusing overwrite')
    cfg=json.loads((KIT/'templates/project.json').read_text(encoding='utf-8'))
    cfg.update(project_id=project.name,title=args.title,topic=args.topic,as_of=args.as_of,mode=args.mode)
    quick=dict(per_query_target=20,screen_batch=10,read_batch=3,citation_seed_target=3,citation_depth=1)
    deep=dict(per_query_target=300,screen_batch=50,read_batch=10,citation_seed_target=20,citation_depth=2)
    if args.mode=='quick':cfg['limits']=quick
    if args.mode=='deep':cfg['limits']=deep
    data={t:[] for t in TABLES};dump(project/'project.json',cfg)
    for t in TABLES:write_table(project/'tables'/f'{t}.csv',t,[])
    log_event(project,'init','New topic; scope and sources must be configured','',digest(cfg,data),{})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ['init','ingest','update','configure','request','import-requests','next','build','audit','checkpoint']:
        p=sub.add_parser(name);p.add_argument('--project',type=Path,required=True)
        if name=='init':
            p.add_argument('--title',required=True);p.add_argument('--topic',required=True);p.add_argument('--as-of',required=True);p.add_argument('--mode',choices=['quick','standard','deep'],default='standard')
        if name in ['ingest','import-requests']:p.add_argument('--file',type=Path,required=True)
        if name in ['update','configure']:
            p.add_argument('--set',action='append',required=True);p.add_argument('--reason',required=True)
        if name=='update':p.add_argument('--table',choices=list(TABLES),required=True);p.add_argument('--id',required=True)
        if name=='checkpoint':p.add_argument('--reason',required=True)
        if name=='request':
            p.add_argument('--action',choices=SCHEMA['enums']['tasks.action'],required=True);p.add_argument('--target-type',choices=['paper','query','project'],required=True);p.add_argument('--target-id',required=True);p.add_argument('--priority',type=int,choices=range(1,6),default=1);p.add_argument('--amount',default='');p.add_argument('--reason',required=True)
    args=parser.parse_args();project=args.project.resolve()
    if args.command=='init':initialize(args)
    cfg,data=load(project)
    oldcfg,olddata=copy.deepcopy(cfg),copy.deepcopy(data)
    if args.command=='ingest':
        packet=json.loads(args.file.read_text(encoding='utf-8-sig'))
        if set(packet)-set(TABLES):raise ValueError('ingest requires table arrays at top level')
        for t,rows in packet.items():
            if not isinstance(rows,list):raise ValueError('table packet must be a list')
            indexes={r[KEYS[t]]:i for i,r in enumerate(data[t])}
            for raw in rows:
                ident=raw.get(KEYS[t]);before=data[t][indexes[ident]] if ident in indexes else {}
                row=normalize(t,{**before,**raw})
                if ident in indexes:data[t][indexes[ident]]=row
                else:indexes[ident]=len(data[t]);data[t].append(row)
        save_changes(project,oldcfg,olddata,cfg,data,'ingest',str(args.file.name))
    elif args.command=='update':
        row=next((r for r in data[args.table] if r[KEYS[args.table]]==args.id),None)
        if row is None:raise ValueError('unknown record ID')
        for pair in args.set:
            key,value=pair.split('=',1)
            if key not in TABLES[args.table] or key==KEYS[args.table]:raise ValueError('invalid field or immutable ID')
            row[key]=value
        save_changes(project,oldcfg,olddata,cfg,data,'update',args.reason)
    elif args.command=='configure':
        for pair in args.set:
            path,value=pair.split('=',1);keys=path.split('.');target=cfg
            for key in keys[:-1]:target=target[key]
            if keys[-1] not in target:raise ValueError('unknown configuration key')
            try:value=json.loads(value)
            except json.JSONDecodeError:pass
            target[keys[-1]]=value
        save_changes(project,oldcfg,olddata,cfg,data,'configure',args.reason)
    elif args.command in ['request','import-requests']:
        requests=([dict(action=args.action,target_type=args.target_type,target_id=args.target_id,priority=args.priority,amount=args.amount,reason=args.reason)] if args.command=='request' else json.loads(args.file.read_text(encoding='utf-8-sig'))['requests'])
        existing={r['task_id']:r for r in data['tasks']}
        for request in requests:
            identity=json.dumps(request,sort_keys=True,ensure_ascii=False)
            if args.command=='request':identity=now()+identity
            rid=request.get('request_id') or 'REQ-'+hashlib.sha256(identity.encode()).hexdigest()[:16]
            row=normalize('tasks',dict(task_id=rid,action=request['action'],target_type=request['target_type'],target_id=request['target_id'],priority=request.get('priority',1),amount=request.get('amount',''),reason=request['reason'],created_at=now(),requested_by='user'))
            if rid in existing:
                fields=['action','target_type','target_id','priority','amount','reason']
                if any(existing[rid][f]!=row[f] for f in fields):raise ValueError('request ID reused with changed contents')
                continue
            data['tasks'].append(row);existing[rid]=row
        save_changes(project,oldcfg,olddata,cfg,data,'request','User instructions queued; no research executed')
    elif args.command=='checkpoint':
        check=audit(cfg,data)
        if check['errors']:raise ValueError('\n'.join(check['errors']))
        previous=events(project)
        log_event(project,'checkpoint',args.reason,previous[-1]['after_hash'] if previous else '',digest(cfg,data),{'note':'Snapshot of imported/directly edited state; does not reconstruct unrecorded earlier edits.'})
        dump(project/'history/checkpoints'/f'{len(events(project)):06}.json',dict(config=cfg,data=data,status=summarize(cfg,data)))
    if args.command=='audit':
        result=audit(cfg,data,project);print(json.dumps(result,ensure_ascii=False,indent=2))
        if result['errors']:raise SystemExit(1)
    elif args.command=='next':print(json.dumps(next_actions(cfg,data,summarize(cfg,data)),ensure_ascii=False,indent=2))
    else:
        status,check=build(project)
        print(json.dumps(dict(project=str(project),audit=check['status'],counts=status['counts'],dashboard=str(project/'outputs/dashboard.html')),ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,FileNotFoundError) as error:raise SystemExit(str(error))
