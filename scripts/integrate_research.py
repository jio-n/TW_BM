"""Normalize the four independently researched bundles; audit referential integrity."""
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
schema=json.loads((ROOT/'data/schema.json').read_text(encoding='utf-8'))
bundle_names=['commercial_japan.json','commercial_global.json','academic_image.json','academic_sensor.json']
if (ROOT/'data/academic_japan_supplement.json').exists():bundle_names.append('academic_japan_supplement.json')
bundles=[json.loads((ROOT/'data'/name).read_text(encoding='utf-8')) for name in bundle_names]
for folder in ['outputs','reports','evidence','details']:(ROOT/folder).mkdir(exist_ok=True)

def save_csv(path, rows, columns=None):
    rows=list(rows)
    columns=columns or list(dict.fromkeys(k for row in rows for k in row))
    with (ROOT/path).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k:('; '.join(map(str,v)) if isinstance(v,list) else json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v) for k,v in row.items()})

def split_ids(value):return [x.strip() for x in re.split(r'[;,；]',str(value)) if x.strip()]

sources=[]
aliases={}
url_ids={}
for bundle in bundles:
    for row in bundle.get('sources',[]):
        row=dict(row)
        row['saved_path']=row.get('saved_path') or '未保存（URL参照）'
        url=str(row.get('url','')).strip().rstrip('/').lower()
        if url and url in url_ids:
            aliases[row['source_id']]=url_ids[url]
        else:
            sources.append(row)
            aliases[row['source_id']]=row['source_id']
            if url:url_ids[url]=row['source_id']

products=[]
papers=[]
candidates=[]
for bundle in bundles:
    for row in bundle.get('products',[]):
        p={k:row.get(k,'未確認') for k in schema['products']}
        p['エビデンスID']='; '.join(dict.fromkeys(aliases.get(x,x) for x in split_ids(p['エビデンスID'])))
        products.append(p)
    for row in bundle.get('papers',[]):
        row=dict(row)
        row['研究概要']=row.get('研究概要',row.get('研究概要（100〜200字程度）','未確認'))
        row['確認状況']=row.get('確認状況',row.get('確認状況（全文／抄録のみ等）','未確認'))
        p={k:row.get(k,'未確認') for k in schema['papers']}
        p['エビデンスID']='; '.join(dict.fromkeys(aliases.get(x,x) for x in split_ids(p['エビデンスID'])))
        (candidates if '候補' in p['採用区分'] else papers).append(p)
products.sort(key=lambda p:p['製品ID'])
papers.sort(key=lambda p:p['論文ID'])
category_alias={'時系列':'LSTM・GRU・時系列','センサ解析':'センサ信号解析','融合':'マルチモーダル・センサ融合','自己教師':'自己教師あり学習','転移':'転移学習','Few/Zero-shot':'Few-shot／Zero-shot','物理AI':'物理モデル・AI統合','特徴量ML':'特徴量ベースML','VLM/Foundation Model':'Foundation Model（画像分割）'}
for p in papers+candidates:
    p['主カテゴリ']=category_alias.get(p['主カテゴリ'],p['主カテゴリ'])

claims=[dict(row) for b in bundles for row in b.get('claims',[])]
links=[dict(row) for b in bundles for row in b.get('claim_evidence',[])]
for row in links:row['source_id']=aliases.get(row['source_id'],row['source_id'])
quote_samples={'R0106':('判定精度・性能','test accuracy of 97.50%'),'R0109':('データ規模','977 microscopic images'),'R0110':('具体的なモデル・手法','U-Net as an automated prompt generator'),'R0117':('データ規模','24 microscopy images'),'R0120':('判定精度・性能','The relative error for flank wear measurements was 3.81%'),'R0125':('判定精度・性能','Dice = 0.85')}
for claim in claims:
    spec=quote_samples.get(claim['entity_id'])
    if spec and claim['field']==spec[0]:
        for link in links:
            if link['claim_id']==claim['claim_id']:link['quote']=spec[1]

# Retain one short literal excerpt per canonical source. All claims keep their locators.
quoted=set()
for row in links:
    quote=str(row.get('quote',''))
    if not quote:continue
    sid=row['source_id']
    if sid in quoted:row['quote']='';continue
    quoted.add(sid)
    row['quote']=' '.join(quote.split()[:18])[:80]

searches=[dict(row) for b in bundles for row in b.get('searches',[])]
# Actual root queries are recorded in execution order; search service gives no total hit count.
query_batches=[
 ('search_initial.json',['tool wear image recognition deep learning YOLO segmentation review 2024 2025','tool wear vision transformer SAM CLIP DINO foundation model 2025 2026','tool wear image classification convolutional neural network 2017 2018 2019','工具 摩耗 画像 深層学習 J-STAGE 論文']),
 ('search_001_003.json',['tool wear YOLO detection segmentation site:mdpi.com','tool wear vision transformer image site:mdpi.com','"tool wear" "CLIP" OR "DINO" OR "SAM" OR "Qwen" OR "LLaVA"']),
 ('search_004_007.json',['"tool wear" "SAM" segmentation','"tool wear" "CLIP" vision language','"tool wear" "DINOv2"','"tool wear" "YOLO" image detection 2024 2025 2026 paper']),
 ('search_008_010.json',['"Efficient Cutting Tool Wear Segmentation Based on Segment Anything Model"','"tool wear" "Mask R-CNN"','"tool wear" "U-Net" segmentation']),
 ('search_011_014.json',['"CNN-based in situ tool wear detection" doi','"Automatic tool wear detection" "Bergs" 2020','"Evaluation of Data Augmentation and Loss Functions" drilling doi','"tool wear" "vision transformer" Sun micro-milling']),
 ('search_015_018.json',['"tool wear" "YOLOv8" cutting wear detection paper doi','"Automatic tool wear detection" "Bergs" "2020"','"tool wear" "Swin" image classification','"tool wear" "DINO" "LLaVA" "Qwen-VL"']),
 ('search_019_022.json',['"Digital image processing with deep learning for automated cutting tool wear detection"','"Deep learning and rule-based image processing pipeline" tool wear','"A computer vision approach to analyze and classify tool wear level" milling','"10.1016/j.ress.2026.113287" "Available online"']),
 ('search_023_026.json',['"reamer" "wear monitoring" machine learning tool','"tap wear" "monitoring" machine learning','"radius end mill" "wear" "monitoring" AI','工具 摩耗 判定 リーマ タップ AI 論文']),
]
qnum=0
for raw,queries in query_batches:
    path=ROOT/'evidence/raw/image'/raw
    result=json.loads(path.read_text(encoding='utf-8'))
    returned=len(set(re.findall(r'(turn\w+)',str(result))))
    recorded=datetime.fromtimestamp(path.stat().st_mtime,timezone(timedelta(hours=9))).isoformat()
    for query in queries:
        qnum+=1
        searches.append({'search_id':f'QIM{qnum:03d}','executed_at':'2026-10-20 JST（個別分秒未記録）','query':query,'target':'Web検索（原資料優先）','returned_count':f'同時実行バッチ全体{returned}、クエリ別未提供','total_hits':'未提供','candidate_count':'候補台帳参照、クエリ別未集計','adopted_count':'未集計','excluded_count':'未集計','exclusion_reason':'除外台帳参照','raw_path':'evidence/raw/image/'+raw,'recorded_at':recorded+'（保存時刻）'})
followup=json.loads((ROOT/'evidence/raw/image/coverage_followup.json').read_text(encoding='utf-8'))
for i,query in enumerate(followup['queries']):
    searches.append({'search_id':f'QIMF{i+1:03d}','executed_at':followup['executed_at'],'query':query,'target':'Web追加カバレッジ検索','returned_count':'同時バッチ内、個別未提供','total_hits':'未提供','candidate_count':'国内4研究を追加精査へ','adopted_count':'候補台帳参照','excluded_count':'未集計','exclusion_reason':'リーマtorque予測を摩耗推定と誤認しない','raw_path':'evidence/raw/image/coverage_followup.json'})
followup2=json.loads((ROOT/'evidence/raw/image/coverage_followup_2.json').read_text(encoding='utf-8'))
for i,query in enumerate(followup2['queries']):
    searches.append({'search_id':f'QIMF2{i+1:03d}','executed_at':followup2['executed_at'],'query':query,'target':'Web追加カバレッジ検索','returned_count':'同時バッチ内、個別未提供','total_hits':'未提供','candidate_count':'ラジアス/複合加工2研究を追加精査へ','adopted_count':'候補台帳参照','excluded_count':'未集計','exclusion_reason':'原因説明の注目領域を因果推定実証としない','raw_path':'evidence/raw/image/coverage_followup_2.json'})

download=json.loads((ROOT/'evidence/raw/image/download_log.json').read_text(encoding='utf-8'))
for i,item in enumerate(download['results']):
    if 'api.crossref.org/works?' not in item['url']:continue
    response=json.loads((ROOT/'evidence/raw/image'/item['file']).read_text(encoding='utf-8'))
    searches.append({'search_id':f'QIMCR{i:03d}','executed_at':download['executed_at']+'（バッチ完了時刻UTC）','query':item['url'],'target':'Crossref title API rows=3','returned_count':len(response['message']['items']),'total_hits':response['message'].get('total-results','未提供'),'candidate_count':'完全一致候補のみ目視採用','adopted_count':'書誌照合用、候補台帳参照','excluded_count':'未集計','exclusion_reason':'別題/訂正/既収集資料は重複排除','raw_path':'evidence/raw/image/'+item['file']})

excluded=[dict(row) for b in bundles for row in b.get('excluded',[])]
for row in excluded:
    row['name']=row.get('name',row.get('title','未確認'))
    url=str(row.get('url','')).strip()
    if not url:continue
    key=url.rstrip('/').lower()
    if key in url_ids:
        row['source_id']=url_ids[key]
        continue
    sid=f'SCAND{len(sources)+1:03d}'
    sources.append({'source_id':sid,'title':row['name'],'publisher':'未確認（候補・除外資料）','year':'未確認','url':url,'type':'候補・除外資料','primary':'未確認（原資料候補）','accessed':'2026-10-20','verification':'候補所在/検索結果確認。本文確認は候補状態を参照','saved_path':'未保存（検索記録またはURL参照）','locator':'候補の採否理由をexcluded_candidates.csvに記載'})
    url_ids[key]=sid
    aliases[sid]=sid
    row['source_id']=sid
unverified=[dict(row) for b in bundles for row in b.get('unverified',[])]
allrows=products+papers+candidates
ids=[r.get('製品ID',r.get('論文ID')) for r in allrows]
sidset={s['source_id'] for s in sources}
cidset={c['claim_id'] for c in claims}
errors=[]
for values,kind in [(ids,'entity'),([s['source_id'] for s in sources],'source'),([c['claim_id'] for c in claims],'claim')]:
    errors.extend(f'duplicate {kind}: {k}' for k,v in Counter(values).items() if v>1)
for row in links:
    if row['source_id'] not in sidset:errors.append('missing source '+row['source_id'])
    if row['claim_id'] not in cidset:errors.append('missing claim '+row['claim_id'])
for row in claims:
    if row['entity_id'] not in ids:errors.append('missing entity '+row['entity_id'])
for row in allrows:
    for sid in split_ids(row['エビデンスID']):
        if sid not in sidset:errors.append('row source '+sid)
    for cid in split_ids(row['Claim ID']):
        if cid not in cidset:errors.append('row claim '+cid)
for source in sources:
    p=source['saved_path']
    if p and not any(x in p for x in ['未','http','Web tool']) and not (ROOT/p).exists():errors.append('missing saved path '+p)
dois=[p['DOI'].lower().replace('https://doi.org/','').strip() for p in papers if str(p['DOI']).startswith('10.')]
errors.extend('duplicate doi '+k for k,v in Counter(dois).items() if v>1)
if errors:
    (ROOT/'data/integrity_errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit('\n'.join(errors))

def counts(rows,key):return dict(Counter(str(r.get(key,'未確認')) for r in rows))
stats={'as_of':'2026-10-20','products':len(products),'papers':len(papers),'held_papers':len(candidates),'sources':len(sources),'claims':len(claims),'links':len(links),'search_log_rows':len(searches),'excluded_rows':len(excluded),'integrity_errors':0,'products_japan':sum(p['国・地域']=='日本' for p in products),'product_status':counts(products,'提供区分'),'confidence':counts(products,'技術情報の確度'),'paper_category':counts(papers,'主カテゴリ'),'paper_year':counts(papers,'発表年'),'paper_verification':counts(papers,'確認状況'),'paper_country':counts(papers,'国・地域'),'paper_fulltext':sum(str(p['確認状況']).startswith('全文') for p in papers),'product_country':counts(products,'国・地域'),'paper_process':counts(papers,'対象加工法')}
stats['commercial_candidate_name_records']=len(products)+len(bundles[0]['excluded'])+len(bundles[1]['excluded'])
stats['academic_candidate_records']=len(papers)+len(candidates)+sum(len(b.get('excluded',[])) for b in bundles[2:])-1 # R0027 is also explicitly retained in XS003
stats['paper_japan_included']=sum('日本' in p['国・地域'] for p in papers)
source_lookup={s['source_id']:s for s in sources}
stats['primary_products']=sum(any(str(source_lookup[s]['primary']).startswith('一次') for s in split_ids(p['エビデンスID'])) for p in products)
stats['primary_papers']=sum(any(str(source_lookup[s]['primary']).startswith('一次') and 'Crossref' not in source_lookup[s]['title'] for s in split_ids(p['エビデンスID'])) for p in papers)
merged={'products':products,'papers':papers,'candidates':candidates,'sources':sources,'claims':claims,'claim_evidence':links,'searches':searches,'excluded':excluded,'unverified':unverified,'stats':stats}
(ROOT/'data/integrated.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
for name,rows,columns in [('commercial_tool_benchmark',products,schema['products']),('academic_paper_benchmark',papers,schema['papers']),('academic_candidates',candidates,schema['papers'])]:save_csv('outputs/'+name+'.csv',rows,columns)
for name,key in [('sources','sources'),('claims','claims'),('claim_evidence','claim_evidence'),('search_log','searches'),('excluded_candidates','excluded'),('unverified_items','unverified')]:save_csv('evidence/'+name+'.csv',merged[key])
save_csv('evidence/source_aliases.csv',[{'original_source_id':k,'canonical_source_id':v} for k,v in aliases.items() if k!=v])
save_csv('SOURCES.csv',sources)
save_csv('SEARCH_LOG.csv',searches)
print(json.dumps(stats,ensure_ascii=False,indent=2))
