"""Export the manually screened Wu citation metadata; preserve unresolved candidates."""
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
raw = ROOT/'evidence/raw/round2_root/FT001'
rows = list(csv.DictReader((raw/'screening.csv').open(encoding='utf-8-sig')))
assert len(rows) == 191
prior=ROOT/'data/round2_root.json'
if prior.exists():
    previous=json.loads(prior.read_text(encoding='utf-8'))['candidates']
    assert [r['openalex_id'] for r in rows]==[r['openalex_id'] for r in previous], 'Citation order/set changed: manually rescreen before applying the recorded decisions'
# These index sets were assigned after reading the returned titles and available abstracts.
reasons = {}
def mark(indices, reason, decision='除外'):
    for i in indices: reasons[i] = (decision, reason)
mark([0,1,2,3,4,5,6,7,8,9,11,12,13,14,19,23,26,27,68,70,83,85,94,96,106,109,114,115,118,125,142,148,151,157,158,161,163,165,168,171,178], '題名・取得できた抄録で、工具摩耗種類分類とは異なる対象・目的。一般手法や工具自体の識別を含む')
mark([10,30,31,32,33,35,36,37,41,42,45,47,49,51,52,53,55,62,87,91,95,98,116,153,189], 'レビュー・背景資料。原著の種類分類実験としては採用しない', '関連（背景）')
mark([15,18,25,28,29,58,59,61,63,72,79,90,104,108,117,119,127,133,134,138,140,144,150,159,160,162,166,167,169,174,187,190], '題名・取得できた抄録ではセンサ信号、量・寿命予測等。工具実写を入力する種類分類を確認できない')
mark([16,17,20,21,22,24,39,43,44,46,60,65,67,69,71,73,75,76,80,81,97,102,103,105,107,113,120,121,122,124,132,136,152,155,170,172,175,180,185,188], '題名・取得できた抄録で摩耗量・程度・正常異常・寿命、または加工物画像が対象。摩耗種類分類の主比較外')
mark([34,56,78,93,99,100,112,128,135,143,146,177,181,186], '領域検出・分割・幾何測定の関連研究。画像単位の種類分類とは別タスク', '関連（領域・測定）')
mark([86,184], '未使用工具の製造時表面欠陥検査。切削中に生じた摩耗種類分類とは区別し、工業拡張でも本稿主モデルはCNN・画像処理のため主比較外', '関連（製造欠陥）')
mark([182,183], '研削・アブレシブ摩耗の境界領域。今回の切削工具の主比較へ自動拡張しない', '関連（境界）')
for i in [17,20,21,22,28,79,148,159]:
    reasons.pop(i, None)  # The title alone cannot establish the exact labels or inference input.
known = {50:'FIA04',66:'FT003',89:'MM-DATA',126:'FIA03',139:'FA001',156:'FT002'}
bundle = {'new_records':[], 'record_updates':[], 'sources':[], 'claims':[], 'claim_evidence':[], 'search_log':[], 'candidates':[], 'citation_edges':[], 'retrieval_attempts':[], 'seed_checks':[]}
for i,r in enumerate(rows):
    cid=f'RWU{i+1:03}'
    decision,reason=reasons.get(i,('保留','題名／取得できた抄録だけでは、原語ラベルと種類分類出力を確定できない。本文・著者版を要確認'))
    if i in known: decision,reason='既存収録','既存比較表またはデータセット台帳に収録。新規論文として二重計上しない'
    if i==1: reason+='。異分野Piezo論文はWu原文References #13にも実在。引用されていることは対象適合の証明ではない'
    if i==154: reason+='。同時調査WR2C003で出版社抄録を追加確認。採否は同候補の記録を参照'
    if i==190: reason+='。索引年2022とモデル名の整合にも疑義があり、書誌再確認が必要'
    bundle['candidates'].append({'candidate_id':cid,'title':r['title'],'doi':r['doi'],'url':r['landing_url'] or r['openalex_id'],'scope':'工具摩耗','discovered_by':'OpenAlex引用集合 FT001','seed_id':'FT001','decision':decision,'reason':reason,'record_id':known.get(i,''),'verification':'タイトル＋索引抄録の一次選別（抄録欠落時はタイトルのみ）。個別本文の確認完了を意味しない','openalex_id':r['openalex_id'],'publication_date':r['publication_date']})
    bundle['citation_edges'].append({'edge_id':f'ERWU{i+1:03}','seed_id':'FT001','candidate_id':cid,'direction':r['direction'],'relation_status':'索引で確認（原文未照合）' if i!=1 else '原文で確認','evidence_url':r['openalex_id'],'locator':'FT001 referenced_works / cites filter' if i!=1 else 'Wu2019 PDF p.16 References #13','notes':'類似候補ではなくOpenAlexの引用リンク。索引の同定・年・網羅性には誤差があり得る'})
retrieval=json.loads((raw/'retrieval_log.json').read_text(encoding='utf-8'))
bundle['retrieval_metadata']=retrieval
for j,q in enumerate(retrieval['requests']):
    bundle['search_log'].append({'search_id':f'QRRWU{j+1:03}','executed_at':q['at'],'query':q['url'],'provider':'OpenAlex REST API','target':'FT001 seed metadata' if j==0 else 'FT001 backward' if j==1 else 'FT001 forward','returned_count':1 if j==0 else q['returned'],'total_hits':'非該当（単一Work）' if j==0 else q['count'],'result_scope':'API全ページ取得。forwardはpublication_date<=2026-11-11','candidate_ids':'; '.join(c['candidate_id'] for c,e in zip(bundle['candidates'],bundle['citation_edges']) if (j==1 and e['direction']=='backward') or (j==2 and e['direction']=='forward')),'notes':'raw/round2_root/FT001。全取得は当該索引・条件内の意味。全世界の引用総数ではない'})
for direction in ['backward','forward']:
    count=sum(r['direction']==direction for r in rows)
    bundle['seed_checks'].append({'seed_id':'FT001','scope':'工具摩耗','direction':direction,'method':'OpenAlex REST、本文Referencesも照合（全件対照は未完了）','executed_at':retrieval['requests'][-1]['at'],'available_total':count,'screened_count':count,'scope_status':'索引集合全件取得・全件タイトル／利用可能抄録選別','candidate_ids':'; '.join(c['candidate_id'] for c,e in zip(bundle['candidates'],bundle['citation_edges']) if e['direction']==direction),'notes':'本文全件確認ではない。原文参考文献と索引リストの件数一致は対応の完全性を保証しない'})
bundle['notes']=['FT001の原文31参考文献とOpenAlex31件は件数一致だけで同一集合と断定しない。索引にはerratumが含まれ、原文Zhang2017項目との全件照合は未完了。','191件は引用メタデータの一次選別数。191件すべての本文を読んだという意味ではない。']
(ROOT/'data/round2_root.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidates':len(rows),'decisions':{x:sum(c['decision']==x for c in bundle['candidates']) for x in sorted({c['decision'] for c in bundle['candidates']})}},ensure_ascii=False))
