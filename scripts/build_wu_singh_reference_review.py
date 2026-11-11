"""Export this bounded citation review; no network access or inference of labels."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/wu_singh_references'
OUT.mkdir(exist_ok=True)

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def write_csv(name, rows):
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in r.items()} for r in rows)

SEEDS = {
    'FT001': ('Wu2019', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6767294/'),
    'FT002': ('Singh2026ViT', 'https://www.mdpi.com/2075-1702/14/6/589'),
}
# Reasons reflect either seed citation context/title screening or a separate original check.
WU = {
1:'汎用のファジーニューラル学習法', 2:'TCMレビュー。個別の種類分類原著ではない',
3:'seed本文によればAE・電流の信号入力', 4:'AEによる信頼性予測',
5:'切削力・振動の信号解析', 6:'音響光学放射の監視。工具写真による種類分類の確認なし',
7:'使用可能／廃棄の二値分類（原著抄録確認）', 8:'工具寿命予測',
9:'low/high または low/medium/high の程度分類（原著抄録確認）',
10:'摩耗量・程度予測（seed引用文脈）', 11:'画像特徴と加工条件による逃げ面摩耗程度予測（原著抄録確認）',
12:'刃先摩耗の画像計測（seed引用文脈）', 13:'Piezoイオンチャネル。原文参考文献のまま保持',
14:'果実検出', 15:'トマト病害・害虫検出',16:'果実計数',17:'軸受故障',18:'回転機械故障',
19:'運動想起EEG',20:'皮膚電気活動からの感情認識',21:'歯車故障',22:'振動信号からの機械故障',
23:'歯車故障',24:'音響信号によるTCM（seed引用文脈）',
25:'振動信号をウェーブレットエネルギー画像へ変換。工具実写ではない（seed §1）',
26:'信号からの健康状態・摩耗推定（seed引用文脈）',27:'汎用Faster R-CNN',28:'音声認識',
29:'汎用視覚モデル',30:'軸受ローラ表面検査',31:'巻上げ機ロープ監視',
}
SINGH = {
1:'人工摩耗付与・加工実験',2:'Waspaloyの被削性・切削力・摩耗',3:'IN718高速旋削実験',
4:'加工時の摩耗評価',5:'切削刃・摩耗・切屑形成の関係',6:'表面健全性レビュー',
7:'TCMのAIレビュー',8:'物理/データ/ハイブリッド摩耗監視レビュー',9:'脆性材料の加工機構レビュー',
10:'画像による摩耗量計測',11:'微小工具の摩耗量・進展計測（原著プレビュー確認）',
12:'逃げ面摩耗面積・幅の計測（原著抄録確認）',13:'ステレオ視による摩耗評価・予測',
14:'TCMレビュー',15:'AI摩耗監視レビュー',16:'加工・工具監視の深層学習レビュー',
17:'5工具形状の分類＋摩耗領域分割。摩耗種類分類ではない（原著公開本文）',
18:'使用可否の二値分類（原著抄録）',19:'OK/NOK（seed紹介）。原著公開抄録は工具条件監視',
20:'4種類名分類。HG-XAI。既収録FW2001',21:'4種類名分類。公開Fig.2で旧保留WR2C003のラベルを確認',
22:'4種類名分類。Wu2019自身。既収録FT001',23:'音声MFCC画像・idle/fresh/moderate/worn',
24:'汎用転移学習レビュー',25:'汎用ViT原著',26:'切削力・振動・AEからの摩耗推定',
27:'信号からのCNN–Transformer摩耗推定',28:'ボールエンドミル摩耗量計測',
29:'no-wear/initial/normal/severe の程度分類（seed紹介）。原著本文未取得',
30:'力信号をMTF画像化。工具写真ではない',31:'4種類名分類。既収録FIA04',
32:'トロコイド加工の実験比較',33:'切削データ計算サービス',34:'工具寿命試験規格',
35:'汎用ViTの可視化',36:'汎用Grad-CAM',
}
PRIMARY = {
('FT001',7):('https://www.sciencedirect.com/science/article/pii/S088832701830236X','原著抄録・公開抜粋'),
('FT001',9):('https://link.springer.com/article/10.1007/s00170-016-9541-0','原著抄録'),
('FT001',11):('https://link.springer.com/article/10.1007/s00170-019-04020-6','原著抄録'),
('FT002',11):('https://www.sciencedirect.com/science/article/pii/S0141635917302817','原著抄録・公開抜粋'),
('FT002',12):('https://link.springer.com/article/10.1007/s00170-021-07522-4','原著抄録'),
('FT002',17):('https://doi.org/10.1016/j.promfg.2020.05.134','公開原著本文'),
('FT002',18):('https://doi.org/10.1016/j.jmsy.2023.03.005','原著抄録'),
('FT002',19):('https://doi.org/10.1016/j.jmapro.2023.07.028','原著抄録＋seed本文のラベル紹介'),
('FT002',20):('https://link.springer.com/article/10.1007/s10845-024-02476-2','原著抄録'),
('FT002',21):('https://link.springer.com/article/10.1007/s00170-026-17619-3','原著抄録＋公開Figs.2,6,7を目視確認'),
('FT002',22):('https://pmc.ncbi.nlm.nih.gov/articles/PMC6767294/','原著公開本文'),
('FT002',31):('https://www.sciencedirect.com/science/article/pii/S0278612524002978','原著抄録・公開抜粋'),
}
references=[]
for seed, (label, url) in SEEDS.items():
    refs=read('data/wu_singh_seed_references.json')[seed]['reference']
    reasons = WU if seed=='FT001' else SINGH
    assert len(refs)==len(reasons)
    for n, ref in enumerate(refs,1):
        primary, level=PRIMARY.get((seed,n),(url,'参考文献題名・seed本文の引用文脈。被引用原著は未確認'))
        row={'reference_id':f'{seed}-R{n:02}', 'seed_id':seed, 'seed':label, 'reference_number':n,
             'depth':1,'title_as_cited':ref.get('article-title',ref.get('unstructured','')),
             'author_as_cited':ref.get('author','参考文献文字列参照'),'year_as_cited':ref.get('year','参考文献文字列参照'),
             'doi_as_registered':ref.get('DOI','未登録'),'decision':'適合確認' if seed=='FT002' and n in (20,21,22,31) else '対象外（一次選別を含む）',
             'reason':reasons[n],'verification':level,'seed_url':url,'seed_locator':f'References [{n}] / Introduction',
             'evidence_url':primary,'existing_record_id':{20:'FW2001',21:'WR2C003 / RWU155',22:'FT001',31:'FIA04'}.get(n,'') if seed=='FT002' else '',
             'metadata_note':''}
        if seed=='FT001' and n==9:
            row['metadata_note']='原著筆頭はGarcía-Ordás。seed登録はAlegre。2016 online / 2017巻号。'
        if seed=='FT001' and n==11:
            row['metadata_note']='原著DOI 10.1007/s00170-019-04020-6、104:1369–1379。seedの巻29/p112と不一致。'
        if seed=='FT001' and n==22:
            row['metadata_note']='Crossref引用はpreprint DOI。PMC参考文献の出版版は10.3390/s17020425。'
        if seed=='FT002' and n==18:
            row['metadata_note']='Crossref引用登録のauthorはZiegenbein。seed本文の参考文献と原著筆頭はGarcía-Pérez。'
        if seed=='FT002' and n in (19,29):
            row['decision']='保留（対象外候補・原著ラベル未確認）'
        references.append(row)
write_csv('references.csv',references)

# Original-document checks and retrievals are retained separately in the candidate-check JSON.
root=read('data/wu_singh_reference_root.json')
checks=read('data/wu_singh_reference_candidate_checks.json')
for i, row in enumerate(root['candidates']):
    row['source_ids']=[root['sources'][i]['source_id']]
for row in checks['records']:
    root['citation_edges'].append({'edge_id':f"EWS_A{row['seed_reference']}",
        'entity_id':row['id'], 'route':f"FT002 [{row['seed_reference']}]", 'depth':1,
        'evidence_url':row['seed_url'],'status':'原著参考文献で確認'})
    root['candidates'].append({
        'id':row['id'], 'existing_ids':row.get('existing_ids',[]), 'depth':1,
        'route':f"FT002 [{row['seed_reference']}]", 'authors':row['authors'],
        'year':row['year'],'title':row['title'],'doi':row['doi'],
        'url':'https://doi.org/'+row['doi'],'decision':row['decision'],
        'input':row['input'],'classes':'; '.join(row['original_labels']) or '原著ラベル未確認',
        'model':row['model'],'performance_and_conditions':row['performance'],
        'verification':row['verification'],'locator':row['locator'],
        'source_ids':row['source_ids'],'secondary_label_evidence':row.get('secondary_label_evidence',{}),
    })
for key in ('sources','claims','claim_evidence'):
    root[key].extend(checks[key])
write_csv('candidate_checks.csv',root['candidates'])
write_csv('sources.csv',root['sources'])
write_csv('claims.csv',root['claims'])
write_csv('claim_evidence.csv',root['claim_evidence'])
write_csv('citation_edges.csv',root['citation_edges'])
write_csv('search_log.csv',read('data/wu_singh_search_log.json')+checks['search_log'])
write_csv('retrieval_attempts.csv',root['retrieval_attempts']+checks['retrieval_attempts'])
counts=Counter(r['decision'] for r in references)
audit={'as_of':'2026-11-12','seed_reference_positions':{'FT001':31,'FT002':36},
       'screened_reference_positions':len(references),'decisions':dict(counts),
       'direct_confirmed_including_seed':4,'direct_confirmed_excluding_Wu_seed':3,
       'previously_adopted_direct':3,'previously_held_now_scope_confirmed':1,
       'newly_discovered_confirmed_papers':0,
       'original_checked_reference_positions':len(PRIMARY),
       'author_conference_digest_additional_positions':1,
       'checks':'67 unique seed-reference IDs; root claims/sources/edges referential integrity',
       'limitations':['67原著の全文確認ではない。12引用位置は原著本文/抄録/図の確認を伴う。Sun2021は別に著者発表要約を確認。',
       '二段目はSun2018とASME2023を重点追跡しただけで、二段目全集合は未選別。',
       'Sun2021は原著本文未取得。除外ラベルはSingh2026による紹介。',
       '旧Excel/HTML/キットは今回の追加表へ未統合。今回の判定差分を別台帳で保持。']}
assert len(references)==67 and len({r['reference_id'] for r in references})==67
assert counts['適合確認']==4
source_ids={s['source_id'] for s in root['sources']}
claim_ids={c['claim_id'] for c in root['claims']}
assert len(source_ids)==len(root['sources']) and len(claim_ids)==len(root['claims'])
for link in root['claim_evidence']:
    assert link['source_id'] in source_ids and link['claim_id'] in claim_ids
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False,indent=2))
