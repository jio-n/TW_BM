"""Assemble the manually verified wear-type classification review and evidence CSVs."""
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; EV=ROOT/'evidence/wear_type_classification'; EV.mkdir(exist_ok=True)
def read(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf-8-sig'))
root=read('focused_root.json'); img=read('focused_image_additional.json')
multi=read('focused_multimodal.json')
def dumpcsv(path,rows,cols=None):
 if cols is None:cols=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def joined(v):return '; '.join(v) if isinstance(v,list) else (v or '未確認')
sources=list(img['sources'])+list(multi['sources'])
# Patent claims stay in the discovery bundle; the Yan ablation belongs to MM002.
# Its verified labels and baseline results are already covered by the multimodal claims.
image_claims=[c for c in img['claims'] if c['entity_id'] not in ['FIA10','FIA11']]
claims=image_claims+list(multi['claims'])
image_claim_ids={c['claim_id'] for c in image_claims}
links=[l for l in img['claim_evidence'] if l['claim_id'] in image_claim_ids]+[{k:c.get(k,'') for k in ['claim_id','source_id','locator','verification']} for c in multi['claims']]
records=root['records']+root['adjacent']
ja={'FIA01':'構成刃先／破断／チッピング／通常摩耗／過大摩耗（種類と程度の混合）','FIA02':'逃げ面摩耗の有無／チッピングの有無','FIA03':'構成刃先／変形／通常摩耗','FIA04':'逃げ面／逃げ面＋構成刃先／逃げ面＋Face／チッピング','FIA05':'クレータ摩耗／構成刃先／熱き裂／刃先チッピング／アブレシブ摩耗','FIA06':'構成刃先／チッピング','FIA07':'背景／逃げ面摩耗／チッピング／構成刃先','FIA08':'背景／逃げ面摩耗／チッピング／構成刃先','FIA09':'刃先摩耗／付着物／汚染'}
counts={'FIA01':5,'FIA02':2,'FIA03':3,'FIA04':4,'FIA05':5,'FIA06':2,'FIA07':4,'FIA08':4,'FIA09':3}
sizes={'FIA01':'評価20使用済インサート','FIA02':'648画像、2台、1種類インサート','FIA03':'296画像（207学習/89検証）','FIA04':'未確認','FIA05':'元150画像→拡張1,200、840/360分割','FIA06':'学習規模未確認。外部例各5枚','FIA07':'213画像、152/10/51','FIA08':'213画像。同系列FIA07参照','FIA09':'21工具・50スキャン・2,500画像'}
for r in img['records']:
 if r['id'] in ['FIA10','FIA11']:continue
 sid=r['source_ids'][0]; source=next(s for s in sources if s['source_id']==sid)
 rec={'id':r['id'],'existing_id':'追加','group':'画像のみ' if r['id']<='FIA06' else '種類付き領域分割・検出','status':'保留（書誌・完全本文）' if r['id']=='FIA06' else ('採用' if r['id']<='FIA05' else '関連（主比較外）'),'year':r['year'],'authors':joined(r['authors']),'title':r['title'],'doi':r['doi'],'url':source['url'],'input':r['input'],'tool':r['input'],'labels':joined(r['exact_labels']),'labels_ja':ja[r['id']],'classes':counts[r['id']],'task':r['category'],'mixed':('2つの独立二値出力。同時陽性可' if r['id']=='FIA02' else ('複合摩耗を単一クラス化' if r['id']=='FIA04' else '原語クラスを参照')),'model':r['model'],'data':sizes[r['id']],'split':r['split'],'performance':r['performance'],'metric':'成績欄に原指標を併記','limitation':r['limitations'],'locator':r['locators'],'verification':r['verification'],'source_id':joined(r['source_ids']),'dataset_family':('IN718／Kumar–Singh系列' if r['id']=='FIA04' else ('KIT213画像系列' if r['id'] in ['FIA07','FIA08'] else '本文参照'))}
 records.append(rec)
# Multimodal mapping is kept explicit after inspecting the team's schema.
for r in multi['records']:
 src=next(s for s in sources if s['source_id']==r['source_ids'][0])
 records.append({'id':r['id'],'existing_id':'R0027（旧保留）' if r['id']=='MM002' else '追加','group':'マルチモーダル','status':r['status'],'year':r['year'],'authors':joined(r['authors']),'title':r['title'],'doi':r['doi'],'url':src['url'],'tool':r['tool']+'／'+r['process'],'input':joined(r['modalities']),'labels':joined(r['exact_labels']),'labels_ja':'逃げ面／要確認（凝着または複合）' if r['id']=='MM001' else '逃げ面摩耗／凝着／逃げ面摩耗＋凝着','classes':len(r['exact_labels']),'task':r['output'],'mixed':'凝着と複合を一群に統合' if r['id']=='MM001' else '複合を独立した単一クラス化','model':r['model'],'data':r['dataset']+'。'+r['split'],'split':r['split'],'metric':'分類指標のみ、成績欄参照','performance':r['metrics'],'limitation':r['limitations'],'locator':src['locator'],'verification':src['verification'],'source_id':joined(r['source_ids']),'dataset_family':'MATWI','online_status':r['published']})
for r in root['records']+root['adjacent']:
 sources.append({'source_id':r['source_id'],'title':r['title'],'url':r['url'],'doi':r['doi'],'primary':True,'accessed':'2026-11-11','verification':r['verification'],'locator':r['locator'],'saved_path':r['saved_path']})
 for f in ['labels','input','model','data','split','performance','limitation']:
  cid=f"CF_{r['id']}_{f}"
  claims.append({'claim_id':cid,'entity_id':r['id'],'field':f,'claim':r[f],'status':r['verification']})
  links.append({'claim_id':cid,'source_id':r['source_id'],'locator':r['locator'],'quote':'','verification':r['verification']})
sources.append({'source_id':'SF005','title':root['exclusions'][0]['title'],'url':root['exclusions'][0]['url'],'doi':root['exclusions'][0]['doi'],'primary':True,'accessed':'2026-11-11','verification':'PDF §3.1確認','locator':root['exclusions'][0]['locator']})
existing=read('integrated.json'); screening=[]
for p in existing['papers']:
 pid=p['論文ID']; output=p['判定対象の摩耗種類・指標']
 if pid in ['R0102','R0106']:status='採用';reason='実際の種類名クラス分類。専用比較FT001/FT002'
 elif pid in ['R0116','R0118']:status='保留';reason='既存記録では具体的な種類ラベル・分類出力を確定できない'
 elif pid in ['R0103','R0105','R0117']:status='関連・主比較外';reason='画像の領域検出/種類付き分割。画像単位の種類分類と別タスク'
 elif pid.startswith('R00'):status='対象外';reason='既存記録の推論入力はセンサ等、または量・寿命・状態を対象。工具実写の種類分類ではない'
 elif pid in ['R0109','R0110','R0111','R0121','R0122','R0123','R0125']:status='対象外';reason='工具種類識別、摩耗領域分割、または摩耗量測定。摩耗名分類の実証未確認'
 else:status='対象外';reason='摩耗程度・正常異常・交換要否・量/寿命、または信号画像からの設備故障。種類名分類の要件外'
 screening.append({'既存論文ID':pid,'判定':status,'理由':reason,'論文名':p['論文タイトル（原題）'],'既存記録の出力':output,'入力':p['入力データ'],'DOI':p['DOI'],'URL':p['原文URL'],'確認範囲':'既存構造化記録に基づく再選別。FT001/2、R0115は本文も再確認'})
exclusions=root['exclusions']+img['exclusions']+multi['exclusions']
searches=img['search_log']+multi['search_log']
queries=[
 'tool wear classification flank adhesive images CNN','tool wear chipping Vision Transformer classification','tool wear type classification images',
 'tool wear classification crater image types','tool wear classification adhesive wear','A Qualitative Tool Condition Monitoring Framework classes',
 'tool wear wear type classification image SVM','工具 摩耗形態 分類 画像 AI','tool wear multi-label classification images',
 'tool wear SVM-WOA Type 1 Type 2','Qualitative Tool Condition 7298 wear categories',
 'High-accuracy tool wear monitoring for micro-milling method based on improved Pyramid Vision Transformer wear',
 'Development of ball end-mill wear condition wear classification four','site:mdpi.com/2504-4494/10/8/286 MaskLenNet mIoU Li','MaskLenNet 2026 authors','A Qualitative Tool Condition Monitoring Framework convolutional layers']
for i,q in enumerate(queries,1):searches.append({'search_id':f'QFR{i:03}','executed_at':'2026-11-11 JST（時分未記録）','target':'Web検索・出版社一次本文','queries':q,'returned_count':'個別未記録','total_hits':'未提供','raw_path':'evidence/raw/focused_root/（一部検索スナップショット保存）'})
source_ids={s['source_id'] for s in sources}; claim_ids={c['claim_id'] for c in claims}
assert len(source_ids)==len(sources),'duplicate source IDs'
assert len(claim_ids)==len(claims),'duplicate claim IDs'
assert all(l['source_id'] in source_ids and l['claim_id'] in claim_ids for l in links),'broken reference'
assert all(c['entity_id'] in {r['id'] for r in records}|{'MM-DATA'} for c in claims),'unknown entity'
assert len(screening)==59
result={'as_of':'2026-11-11','records':records,'sources':sources,'claims':claims,'claim_evidence':links,'search_log':searches,'screening':screening,'exclusions':exclusions}
(ROOT/'data/focused_integrated.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for key in ['sources','claims','claim_evidence','search_log','exclusions']:
 dumpcsv(EV/(key+'.csv'),result[key])
dumpcsv(EV/'existing_papers_screening.csv',screening)
dumpcsv(OUT/'wear_type_classification_benchmark.csv',records)
image_rows=[r for r in records if r['group']=='画像のみ' and '保留' not in r['status']]
multi_rows=[r for r in records if r['group']=='マルチモーダル' and '保留' not in r['status']]
held=[r for r in records if '保留' in r['status']]
adjacent=[r for r in records if '関連' in r['status']]
def mdtable(rows):
 lines=['| ID・論文 | 実際のクラスラベル | 手法・入力 | 種類分類の成績 | 確認・評価上の注意 |','|---|---|---|---|---|']
 for r in rows:
  vals=[f"**{r['id']}** [{r['authors'].split(';')[0]}ら ({r['year']})]({r['url']})",r['labels'],r['model'],r['performance'],r['verification']+'。'+r['limitation']]
  lines.append('| '+' | '.join(str(v).replace('|','／').replace('\n','<br>') for v in vals)+' |')
 return '\n'.join(lines)
report=f'''# 工具画像からの摩耗・損傷種類分類ベンチマーク

調査基準日：2026-11-11。今回の対象は、工具の実写画像を入力し、摩耗・損傷の名前をカテゴリとして出力するタスクである。画像とセンサ等を統合する方法は別表にした。

## 1. 収集結果

主比較は**画像のみ{len(image_rows)}本、マルチモーダル{len(multi_rows)}本**。さらに技術内容は適合するが書誌または先行公開日の確認を要する{len(held)}本を保留表に置いた。種類を付与する検出・領域分割{len(adjacent)}本は関連表であり、画像単位の分類性能と比較しない。

既存59本を再選別した結果、明確に再採用したのは **R0102（提示されたWu2019）とR0106（Singh2026）**。R0116/R0118はクラス定義未確定で保留、R0103/R0105/R0117は領域系の関連資料として記録した。旧保留R0027のYan論文は今回のマルチモーダル候補として再調査した。

[専用Excel](../outputs/wear_type_classification_benchmark.xlsx)／[再利用用CSV](../outputs/wear_type_classification_benchmark.csv)／[既存59本の採否](../evidence/wear_type_classification/existing_papers_screening.csv)。原著者の性能値を条件間でランキングしない。

## 2. 画像のみを入力する種類分類

{mdtable(image_rows)}

## 3. 工具画像を含むマルチモーダル

{mdtable(multi_rows)}

ここでのマルチモーダルは**推論時に工具実写を使う**ものを指す。センサ波形をスペクトログラムにしてCNN/ViTへ渡すだけの研究や、正解ラベル測定にだけ工具写真を使う研究は含めない。

MATWI系列は同じデータ出所でも採用tool setとクラス統合が違う。Ahangarの2群分類とYanの3種類分類は同じ課題・同じ評価集合として比較できない。ROC-AUC、Precision、Recall、Accuracy、Macro-F1も相互に置換しない。

## 4. 内容適合・書誌等の保留

{mdtable(held)}

保留理由：Yongの微細ドリル論文は著者公開原稿の表紙・方法・結果を確認したが、DOI/出版社記事ページと完全本文が未確認。Yanの巻号日とオンライン初出日は同一でないため、出典に示す公開日確認状況を参照する。主比較に確定採用したものと件数を分ける。

## 5. 複合摩耗と出力形式

| 方式 | 例 | 意味 |
|---|---|---|
| 単一ラベルの種類分類 | Wu2019の4クラス | 凝着＋破損が共存しても独立クラスなし。混合状態は誤分類要因 |
| 複合状態を1クラスにする | Kumar2025・Singh2026のFlank+BUE、Flank+Face | 4つから1つを選ぶ。任意の組合せを同時出力するmulti-labelとは異なる |
| 種類ごとの独立二値判定 | Walk2020のflank wearとchipping | 同じ工具で両方陽性になり得る。BUEは元データにあっても学習・評価対象外 |
| 種類を集合へまとめる | Ahangar2026のflank対adhesive/combined | 凝着単独と凝着＋逃げ面を区別できない。正常/異常だけの分類とも異なる |
| 領域ごとに種類を出す | MaskLenNet、U-Net、YOLO系 | 複数種類を位置付きで表現。別表の領域分類・分割性能で評価 |

ラベルは原語を保持した。**flank wearは逃げ面摩耗**。BUE（構成刃先）、adhesion/adhesive wear（凝着）、Face/rake face wear、crater wear、chipping、fracture/breakageを根拠なく同一ラベルに統合しない。摩耗位置、形態、機構、損傷状態が混在する分類体系もあるため、クラス数だけで難易度を比べない。

## 6. 種類付き領域検出・分割の関連研究

{mdtable(adjacent)}

MaskLenNetの96.52%は対応付け済みインスタンスの条件付きAccuracyで、画像全体の分類Accuracyや検出APではない。Walk2023/Treiss2021は同じ213画像系列・同じ基準成績を含み、独立なベンチマークとして加算しない。ホブ研究の分割F1も摩耗種類分類精度ではない。

## 7. 採用しなかった代表例

- [児玉ら2024](https://doi.org/10.1299/transjsme.24-00127)：画像＋電流の構成は近いが、新品・摩耗初期・摩耗終期・工具寿命の段階分類。今回の種類名分類から除外。
- [Visual–Acoustic Cross-Attention 2026](https://doi.org/10.3390/machines14070826)：画像＋音響でも摩耗幅・劣化段階が出力。今回の種類比較から除外。
- [Yang2025](https://doi.org/10.15282/ijame.22.4.2025.15.0992)：切削・擦過・疲労・凝着の名前付き4種類を報告するが工具実写を推論入力にしない。
- Wu2019の後段VB測定、Mamledesai2020の後段GO/NO-GO、Mamledesai2022の後段ファジィ制御は本比較の成績へ混ぜない。

## 8. 研究を読む際の優先点と未確認事項

提示例に最も近い比較の起点は **Wu2019 → Kumar2025/Singh2026 → Walk2020**。前者は4種類、中央は複合クラス、後者は種類別の独立出力という違いを確認できる。クレータ・熱き裂を含むLakshmaiya2025も対象に合うが、拡張後分割と報告値の集計を追加確認する必要がある。

画像枚数だけでなく、独立工具数、拡張前の分割、工具単位・機械単位の分離、少数クラスのRecall/Macro-F1を比較する。クラス別再現率のない高いAccuracyだけでは、凝着やチッピングを見逃さないか判断できない。ラベルのアノテータ数、一致度、混在時の優先規則は多くの論文で十分確認できていない。

本追加調査は既存59本の再選別と一次資料・引用探索による重点収集であり、種類分類研究の完全網羅や探索飽和を保証しない。リーマ・タップ・境界摩耗の画像種類分類、任意の複合状態を扱う大規模multi-label評価、外部工場に一般化する成績は引き続き不足している。

## 9. エビデンスと調査履歴

- [出典台帳](../evidence/wear_type_classification/sources.csv)：{len(sources)}件（補助書誌・除外資料を含む）。
- [主張台帳](../evidence/wear_type_classification/claims.csv)と[根拠対応](../evidence/wear_type_classification/claim_evidence.csv)：{len(claims)}主張。MM-DATAは共通データセットMATWIの根拠であり、追加の論文を意味しない。
- [検索履歴](../evidence/wear_type_classification/search_log.csv)：{len(searches)}行。バッチと個別クエリが混在する。検索エンジン総件数は未提供、一部時分・個別返却数は未記録。
- [除外・保留台帳](../evidence/wear_type_classification/exclusions.csv)、[追加調査仕様](wear_type_classification_scope.md)。

確認済みは書誌・入力・ラベル・当該論文の報告を意味し、実験再現済みという意味ではない。ローカル保存PDF/HTMLは再配布せず、外部からはURL/DOIを参照する。
'''
(ROOT/'reports/wear_type_classification_benchmark.md').write_text(report,encoding='utf-8')
print(json.dumps({'records':len(records),'sources':len(sources),'claims':len(claims),'screening':len(screening)},ensure_ascii=False))
