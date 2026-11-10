"""Render the reviewed paper records and authored analysis into Japanese reports."""
import csv, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/industrial_integrated.json').read_text(encoding='utf-8'))
records={r['id']:r for r in d['records']}
main=[r for r in d['records'] if r['adoption_group']=='採用']
def ref(i):
 r=records[i]
 return f"[{i}: {r['title']}]({r['url']})"
def clean(v): return str(v).replace('|','／').replace('\n','<br>')
def table(headers, rows):
 return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(clean(v) for v in row)+' |' for row in rows)
def paper_table(prefix):
 return table(['ID・原著','年','主モデル','原語クラス／粒度','種類分類の指標・条件'],[[ref(r['id']),r['year'],r['primary_model'],r['labels'],r['performance']] for r in main if r['id'].startswith(prefix)])

coverage_groups=[
 ('モデル系統','視覚Transformer','IT001 IT002 IT003 IT004 IT005 IT006 IT007 IT008 IT009 IT010 IT011','該当事例あり'),
 ('モデル系統','VLM／VLM由来特徴','IV001 IV002 IV003 IV004 IV005 IV006 IV007','該当事例あり'),
 ('モデル系統','MLLM','IM001 IM002 IM003 IM004 IM005 IM006 IM007 IM008 IM009 IM010','該当事例あり'),
 ('モデル系統','純粋なテキストLLMのみ','','適合事例未発見・画像入力条件に注意'),
 ('対象','鋼材・金属表面','IT001 IT002 IT003 IV006','該当事例あり'),
 ('対象','半導体SEM','IT004 IV003 IM003','該当事例あり・IT004は匿名種類'),
 ('対象','ウェハビンマップ','IT005 IT006 IT007 IV007','該当事例あり・外観写真と別'),
 ('対象','PCB','IV004 IV005','該当事例あり・正解領域切出し'),
 ('対象','太陽電池EL','IT009 IT011','該当事例あり'),
 ('対象','繊維製品','IT008','該当事例あり・工場外撮影'),
 ('対象','竹製品','IT010','該当事例あり'),
 ('対象','金属積層造形','IM004','該当事例あり・小標本'),
 ('対象','複数製品・共通ベンチマーク','IV001 IV002 IM001 IM002 IM005 IM006 IM007 IM008 IM009 IM010','該当事例あり・同じデータへの集中'),
 ('入力','画像／画像化マップのみ・学習済み分類器','IT001 IT002 IT003 IT004 IT005 IT006 IT007 IT008 IT009 IT010 IT011 IV004','該当事例あり'),
 ('入力','画像＋ROI／少数サポート例','IV001 IV002 IV005','該当事例あり・クエリROI条件に差'),
 ('入力','画像＋候補文プロトタイプ','IV003 IV006 IV007','該当事例あり'),
 ('入力','画像＋質問／プロンプト（正常参照・RAG等を含む）','IM001 IM002 IM003 IM004 IM005 IM006 IM007 IM008 IM009 IM010','該当事例あり'),
 ('入力','画像＋同時取得の非画像物理センサ','','適合事例未発見・追加調査'),
 ('出力','欠陥種類VQA','IM001 IM003 IM005 IM006 IM007 IM008 IM009 IM010','該当事例あり'),
 ('出力','複合クラスまたは多ラベルを明示','IT005 IT006 IT009 IT010 IT011 IM004','該当事例あり'),
 ('出力','種類付き検出・分割','IV008 IR001 IR002','関連表に分離'),
 ('出力','匿名欠陥種類ID','IT004','種類分類は明示、意味名の対応は要追加調査'),
 ('学習','少数ショット・転移学習','IT004 IV001 IV002 IV003 IV004 IV005','該当事例あり'),
 ('学習','言語を使う厳密な未知欠陥ゼロショット','','比較条件の統一が不足・要追加調査'),
 ('地域','国内機関・日本語学会','','今回の系統的な所属国監査は未実施・要追加調査'),
]
coverage=[{'axis':a,'category':b,'paper_ids':ids,'count':len(ids.split()),'status':status} for a,b,ids,status in coverage_groups]
with (ROOT/'outputs/industrial_coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)

report=f'''# 工業・産業の欠陥種類分類：Transformer・VLM・MLLMベンチマーク

調査基準日：2026-11-11（日本時間）。公開資料の確認に基づく調査版。工具摩耗の既存成果物とは別の拡張調査である。

## 1. エグゼクティブサマリー

**欠陥の種類をカテゴリとして答える28本を主比較対象とした。** 視覚Transformer11本、VLM／VLM由来特徴7本、MLLM10本。関連5本・保留5本を別に収録し、Excelは計38行。主比較のうちIT004は欠陥種類を匿名IDで表すため、名称の共通語彙比較には使えない。その他にも原語ラベルの全量一覧が未抽出の部分集合があり、各行に明記した。

[Excel](../outputs/industrial_defect_classification_benchmark.xlsx)／[CSV](../outputs/industrial_defect_classification_benchmark.csv)／[系統集計](../outputs/industrial_model_family_summary.csv)／[品質監査](industrial_defect_classification_audit.md)／[代表論文の詳細](../details/industrial_defect_classification/README.md)。

画像から傷・穴・汚染・短絡等を分類する研究は複数産業で確認できた。一方、画像の正常／異常を判定するAUROC、位置検出のmAP、VQA全体の平均を、欠陥種類の分類精度と読み替えることはできない。CLIP採用も、推論時に自然言語を使うことを必ずしも意味しない。

## 2. 調査目的・方法・範囲

工業製品、材料、部品の画像に基づく種類分類を対象とした。単一ラベル、複数ラベル、複合クラスを含む。画像だけでなく、候補ラベル、質問、プロンプト、参照画像、文献情報を入力する方式を収録した。純粋なCNNだけの研究、程度のみの分類、二値検知のみ、センサ／ログのみは主比較から分けた。種類付きbbox検出・画素分割は関連表に置いた。

出版社、国際会議の公開原著、著者版、arXiv、公式コード／データ定義、原著の引用を横断し、51行の検索・直接確認ログを残した。1行が複数クエリのバッチを含み、51個の独立した検索語を意味しない。全データベースの系統的検索や引用の完全追跡は未達である。仕様は[採否基準](industrial_defect_classification_scope.md)、原資料は[出典台帳](../evidence/industrial_defect_classification/sources.csv)を参照。

## 3. モデルと入力の分類

{table(['主モデル系統','主比較','関連','保留'],[[x['model_family'],x['accepted_count'],x['related_count'],x['held_count']] for x in d['family_summary']])}

モデルの名称と入力のモダリティを別軸で管理した。画像に正常参照画像を追加すること、画像にテキストを付けること、画像と物理センサを融合することは異なる。今回採用した研究で、画像と同時取得の非画像物理センサを融合して種類を分類する適合例は確認できなかった。LPBFのRAG論文も、評価入力は可視画像と文献の画像・文章であり、赤外線等の同時計測融合を実証した結果ではない（IM004）。

```mermaid
flowchart LR
 A[工業対象の画像] --> B[ViT・Swin・DINO等の視覚特徴]
 B --> C[単一ラベル／複合クラス／多ラベル分類]
 A --> D[VLMの画像・文特徴または視覚塔]
 E[候補ラベル文／少数例] --> D
 D --> C
 A --> F[MLLM]
 G[質問・選択肢・正常参照・RAG] --> F
 F --> H[種類回答／種類選択VQA]
```

これは文献群を整理する独自概念図であり、個別モデルの構成図の転載ではない。すべての研究が図中の全入力を必要とするわけではない。

## 4. 視覚Transformerの研究

{paper_table('IT')}

ウェハビンマップは電気検査結果の空間パターンであり、表面の光学写真やSEM像とは区別する。布汚れ研究IT008も工業ライン上の実証ではなく、家庭環境で撮影した布のデータを含む。タイトルにCross-Datasetを含むIT003はデータセットごとの個別学習比較であり、その結果を未知データセットへ移す性能とは読めない。

## 5. VLM・対照学習型モデルの研究

{paper_table('IV')}

IV001・IV002はAlphaCLIP由来の特徴、IV004はCLIPの視覚塔を利用する。これらを「自然言語を理解して欠陥名を生成するモデル」と一括するのは不適切である。IV007は画像特徴とMiniLM由来の文章プロトタイプを整合させる方式で、CLIPチェックポイントの採用とは異なる。

SEM-CLIPでは視覚分類ヘッドだけのAccuracy83.6%に対し、テキスト類似度も使う方式は83.7%であった。この実験だけから言語モデル一般の優劣は言えないが、言語導入の寄与をアブレーションで確認する必要性を示す。{ref('IV003')}。

## 6. MLLM・LLMを含む研究

{paper_table('IM')}

MMAD系7本（IM001、IM005–IM010）は同じベンチマークへの集中を含み、独立した7種類の工場データ検証ではない。MMADの244欠陥カテゴリと、各設問の4択は異なる単位である。標準1-shotは正常参照画像1枚であり、各欠陥のラベル付き学習例1枚を与えるfew-shotと同義ではない。{ref('IM001')}。

純粋なテキストLLMだけで画像から欠陥種類を分類する主採用例は0本だった。画像を受け取るGPT-4o、Qwen-VL、Gemma等はこの調査ではMLLMに集計する。0本は文献の不存在を証明するものではない。

## 7. タスク・性能比較の読み方

| 評価単位 | 代表例 | 入力側の条件 | 比較時の注意 |
|---|---|---|---|
| 画像全体の閉集合分類 | IT001・IT002・IV006 | 画像、方式によって候補文 | クラス集合、製品、撮像条件、splitを揃える |
| 正解領域のパッチ／インスタンス分類 | IV001・IV004・IV005 | 正解マスク・bboxや切出し画像 | 欠陥発見・位置推定の難しさを含まない |
| 複合クラス分類 | IT005・IT011 | 一枚に複数欠陥が含まれる場合 | 複合を一クラスにする方式と多ラベルを分ける |
| 多ラベル分類 | IT009・IT010・IM004 | 画像、方式によってプロンプト／RAG | exact match、macro-F1、分類mAP、種類別有無のAccuracyは異なる |
| 欠陥種類VQA | IM001・IM003・IM005–IM010 | 質問、選択肢、場合によって正常参照 | 選択肢設計、質問数、学習・参照条件を確認 |
| 種類付きbbox／画素予測 | IR001・IR002・IV008 | 画像と候補文等 | 関連研究。検出mAPやIoUを画像分類Accuracyと並べない |

論文をまたぐ総合順位は作成していない。NEUの約99%とMMAD種類VQAの約66%は、異なる課題を測っている。比較の出発点はモデルの大きさではなく、出力単位と利用可能な入力・正解情報である。

## 8. 技術動向・年表

{table(['採用論文の年','本数'],sorted(Counter(str(r['year']) for r in main).items()))}

2022年のCNN–Transformer鋼板分類から、2024年のSEM向けCLIPやFabGPT、2025年の少数ショット適応・MMAD・RAG、2026年の細粒度VQA学習や多ラベル分類までを確認した。この収集分布は発表総数の年次統計ではない。2026年には査読前原稿も含み、媒体欄で区別する。IV003は会議2024年と著者版2025年、IV007はオンライン2025年末と巻号2026年を混同しない。視覚分類と対話型分類は併存しており、一方向の置換とは解釈しない。

## 9. 工場適用に向けたギャップ

固定カメラ・定義済みクラスの分類では、ViTやCNN–Transformerが比較しやすい。少数サンプルの新種対応にはDINO／CLIP由来特徴の適応を検討できるが、正解切出しやサポート例への依存を確認する必要がある。MLLMは質問・文献・参照画像を取り込める一方、選択式ベンチマーク成績と、工場で全候補から自律判断する成績の間に差がある。

IV005の「unseen」は比較用ResNetの学習に含まれない種類であり、提案法には各種類30枚の参照例が与えられる。厳密なゼロショットと解釈しない。DeepPCBを用いるIV004・IV005は実基板画像に人為的欠陥を加えたデータと正解領域切出しを使用し、自然発生欠陥の一貫した検出・分類実証とは条件が異なる。{ref('IV004')}、{ref('IV005')}。

## 10. 技術的な限界と評価上の注意

- IT004は同一ウェハがtrain/testをまたがない分割を明示する一方、種類名は匿名。データ階層の分離と語彙の公開度を別々に評価する。
- IT008の高いF1は拡張画像を含む10-fold条件。元画像単位の独立性は未確認。工場横断の汎化精度として扱わない。
- IT009は固定閾値0.5の結果を主記録とし、テスト側で閾値を最適化した高い値とは分けた。
- IT010、IT005、IM002では本文・抄録・表の数値や指標表記に不一致があり、該当表と条件を明記した。
- IM010は評価回答で構成・設定を選択しており、完全に未使用のテスト成績として扱えない。
- IM004は54画像の小標本で、種類ごとの有無を判定するAccuracyを平均する。負例の比率に影響されるため、単一ラベルの多クラスAccuracyとは異なる。

各根拠は該当論文行のlimitations・split・Claim IDと[監査報告](industrial_defect_classification_audit.md)に記録した。数値の転載は各論文の報告値であり、実験を再現したものではない。

## 11. 研究開発で比較すべきテーマ

以下は文献から導く調査者の提案であり、既に実証済みの効果ではない。

| テーマ | 比較する方式・参考 | 必要データ・検証 | 想定難易度／期待する効果 |
|---|---|---|---|
| 定義済み欠陥の安定分類 | CNN、ViT、DINO線形／適応、IV004 | 同一欠陥・同一splitでmacro-F1、少数クラスRecall、推論時間 | 中／方式の費用対効果を検証 |
| 新規種類への少数例対応 | IV001・IV002・IV003 | 1/5/10/30-shotを揃え、未知製品・ロットを分離 | 中〜高／再ラベル・再学習負担の削減 |
| 言語の寄与の定量化 | IV003・IV006・IV007 | 同じ視覚塔、画像のみ・クラス名・詳細文・誤った文の対照 | 中／言語追加が有効な条件を特定 |
| 複合欠陥と未学習組合せ | IT005・IT006・IT009・IT010 | 単独型を学習、未知組合せをtest。macro-F1とexact match | 高／複合クラスの爆発を抑える |
| 説明と種類判定の両立 | IM002・IM003・IM004 | 固定ラベル出力と根拠文を別採点、誤説明・棄却率を評価 | 高／作業者レビューの支援 |
| 欠陥検出から分類までの一貫評価 | IV004・IV005・IR001 | 正解ROIあり／なしを同一実欠陥で比較。検出失敗を最終成績へ反映 | 高／切出し依存を解消 |
| 工場変化への耐性と未知種の棄却 | IT004・IM009 | ロット・工場・撮像条件を分離し、未知種・汚れ・照明変化を追加 | 高／誤確信の抑制 |

## 12. 網羅性・制約

38本の詳細表に加え、除外・保留・関連・重複候補25行を管理した。後者には同一論文の異版や同定できない名称も含み、合計63本の実在する独立論文を確認したという意味ではない。76出典、221主張、230根拠対応を登録した。主採用28本は一次資料に対応するが、全体を完全精読した割合とは異なる。

鋼材、SEM、ウェハパターン、PCB、太陽電池、繊維、竹製品、積層造形をカバーする。日本語・国内機関の網羅検索、包装・食品・自動車部品など個別産業、画像＋物理センサの種類分類、独立工場評価は不足する。追加探索でも新しい候補が出ており、探索飽和は証明していない。詳細は[カバレッジCSV](../outputs/industrial_coverage.csv)と監査報告を参照。

## 13. 参考資料・再利用

上表の論文名から原資料へ移動できる。Excelの論文ID → Claim ID → Source ID → 表・節の位置を辿る。台帳は[claims](../evidence/industrial_defect_classification/claims.csv)、[claim_evidence](../evidence/industrial_defect_classification/claim_evidence.csv)、[sources](../evidence/industrial_defect_classification/sources.csv)、[search_log](../evidence/industrial_defect_classification/search_log.csv)、[exclusions](../evidence/industrial_defect_classification/exclusions.csv)、[unverified_items](../evidence/industrial_defect_classification/unverified_items.csv)。

第三者の原著PDF・HTML・図表はGitHubへ転載しない。図や実験例は原著のlocator欄を参照する。CSVはUTF-8 BOM付き、Excelはフィルタ・見出し固定・改行・クリック可能なURLを備える。再生成順は `build_industrial_review.py` → `write_industrial_reports.py` → `build_industrial_workbook.mjs` → `finalize_industrial_workbook.py`。
'''
(ROOT/'reports/industrial_defect_classification_benchmark.md').write_text(report,encoding='utf-8')

selected=['IT003','IT004','IT009','IT010','IV001','IV003','IV004','IV006','IM001','IM002','IM003','IM004']
detail_dir=ROOT/'details/industrial_defect_classification';detail_dir.mkdir(exist_ok=True)
for i in selected:
 r=records[i]
 fields=[('概要・対象','domain'),('対象製品','product'),('モデル系統','model_family'),('主要モデル・処理','primary_model'),('入力','input'),('プロンプト','prompt'),('出力タスク','task'),('原語クラス','labels'),('複合・多ラベル','mixed'),('データ','dataset'),('規模','data_size'),('学習・分割','split'),('学習方式','learning'),('性能','performance'),('比較モデル','baseline_models'),('未知条件への評価','generalization'),('制約','limitations'),('確認状態','verification'),('図・表・構成の参照','locator'),('Claim ID','claim_ids')]
 body=f"# {i}：{r['title']}\n\n{r['authors']}。{r['year']}、{r['venue']}。\n\n{ref(i)}／DOI：{r['doi']}\n\n"+table(['項目','内容'],[(label,r[key]) for label,key in fields])
 body+='\n\nSource ID：'+ '; '.join(r['source_ids'])+'。数値は原著の報告値。図版を転載せず上記位置へ参照する。\n'
 (detail_dir/(i+'.md')).write_text(body,encoding='utf-8')
(detail_dir/'README.md').write_text('# 代表論文の詳細シート\n\n主比較から12本を選択。モデル方式、入力、出力、条件、制約、出典を記録した。\n\n'+'\n'.join(f"- [{i}：{records[i]['title']}]({i}.md)" for i in selected)+'\n',encoding='utf-8')
print(json.dumps({'report':True,'details':len(selected),'coverage_rows':len(coverage)},ensure_ascii=False))
