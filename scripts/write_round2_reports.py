"""Publish the reviewed round results and the limitations exposed by the search audit."""
import csv, json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
wear=read('focused_integrated.json');ind=read('industrial_integrated.json');d=read('round2_integrated.json')
audit=json.loads((ROOT/'evidence/round2/audit_result.json').read_text(encoding='utf-8'))
perf=read('performance_digest.json')
allrows={r['id']:r for b in [wear,ind] for r in b['records']}
new=[r for name in ['round2_wear.json','round2_vit.json','round2_vlm.json'] for r in read(name)['new_records']]
def clean(x):return str(x).replace('|','／').replace('\n','<br>')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(clean(x) for x in row)+' |' for row in rows)
def link(r):return f"[{r['id']}：{r['title']}]({r['url']})"
counts=[]
for name,b in [('工具摩耗',wear),('工業欠陥',ind)]:
    rs=b['records'];counts.append([name,len(rs),sum('採用' in r['status'] for r in rs),sum('保留' in r['status'] for r in rs),sum('関連' in r['status'] for r in rs)])
new_table=table(['論文・モデル','採否','種類分類の報告値','条件・制約'],[[link(r),r['status'],r['performance'],r.get('limitation',r.get('limitations',''))] for r in new])
report=f'''# 引用追跡と保留論文再確認：Round2

調査基準日：2026-11-11。工具の実写から摩耗種類を出力する研究と、工業欠陥種類を出力するTransformer／VLM／MLLM研究を追跡した。摩耗量、寿命、摩耗程度、正常／異常だけの分類は主比較に含めない。

## 更新結果

新規詳細収録は14本。このうち工具2本・工業10本の計12本を主採用し、既存保留FIA06を採用へ更新した。研削フラップホイールと未知SEM欠陥のクラス発見は関連研究として別集計した。

{table(['範囲','詳細表総数','主採用','保留','関連'],counts)}

[精度一覧Excel](../outputs/classification_performance_summary.xlsx)／[CSV](../outputs/classification_performance_summary.csv)／[数値の読み方](classification_performance_summary.md)。67行のうち61行に数値の代表指標を格納し、6行は未報告・未抽出・未確認を区別して残した。代表値以外のF1や条件別の値も結果欄に記載した。関連タスクの数値は種類分類Accuracyへ換算していない。

## 新規に詳細収録した研究

{new_table}

数値は原著の報告であり実験を再現した値ではない。HG-XAIの2本は同じ研究系列で、既存IN718画像との独立性は未確認。新規論文2本を独立した工場実証2件とは数えない。

MLLMのMMAD系では全タスク平均とDefect Classification列を分けた。正常参照1枚の1-shot、MMAD内での学習、別データでの学習、未学習モデルを同じ条件として順位付けしない。SNAP-SEMはHungarian対応付け後のクラス発見を評価するため、既知の摩耗・欠陥名を直接選ぶ閉集合分類とは別に扱った。

## 保留の再確認

- **FIA06は採用へ変更**。[出版社記事](https://semarakilmu.my/index.php/sijaset/article/view/1136)で正式著者順と2026年6月9日の公開を確認した。号の名称はMarch 2026。DOIは記事に記載がなく、内部検証99.26%の主要な分割条件は未確認。出版社PDFの新規解析が完了したという意味ではなく、先に確認した著者版と正式書誌を結び付けた。
- **MM002は保留を維持**。3種類の分類内容と成績は確認しているが、2027年巻と先行公開日は別。基準日までの正確な初出日を確定できていない。
- **IT012–IT016の5本は保留を維持**。出版社、DOI、著者版、機関経路を再探索した。ViViTの4状態名やDeepSEM-NetのSSRN版等は補完したが、種類名・Transformer別の数値・分割などの確認が残る。
- **R0116は本文で領域分割と確認して除外**。種類名の分類精度としてmIoUを使用しない。R0118のGPVTは出力ラベルが未確認。
- HCG-MLLMADは種類分類の独立成績を確認できず除外候補台帳で記録。FabGPTの2026年誌版は既存IM003の関連書誌へ追加し、同一研究を新規論文として二重計上しなかった。

詳細は[取得試行76行](../evidence/round2/retrieval_attempts.csv)、[候補台帳](../evidence/round2/candidates.csv)、[レコード更新履歴](../evidence/round2/record_updates.csv)を参照。403、未発見、抄録のみ、部分本文を区別した。

## 追加探索で分かったこと

工具摩耗は「分類」というタイトルだけでは種類分類を見つけにくい。Wu2019の引用メタデータ191件を一次選別しても、程度分類・量予測・領域分割・一般画像認識の引用が多かった。参考文献に現れた異分野のPiezo論文はWu原文にも実在しており、引用関係だけでは対象適合性を保証しない。

工業欠陥では、画像分類、欠陥名VQA、未知クラス発見、種類付き領域検出が別の評価問題になる。複合クラスを許容しても、単一ラベルAccuracy、多ラベル完全一致、分類F1、検出mAP、領域IoUは区別する。高い数値の多くは特定のデータ・条件で得られ、独立工場への一般化を証明するものではない。

## 次に調べる優先順

1. 今回の新規12本を起点に第2周回を行い、引用先・引用元の未追跡部分を埋める。
2. Round2の保留候補をDOI・版で重複整理し、種類ラベルと性能表の本文を優先取得する。HG-XAI2本の完全本文と、同一画像系列の独立性を確認する。
3. 部分確認にとどまる工業側の前方引用を索引APIまたは学術DBで列挙し、取得ページを記録する。
4. IEEE、J-STAGE、CiNii等のDB内検索、国内機関、タップ・リーマ、複数工具を横断する種類分類、非画像センサ融合を補完する。
5. 検索式の既知論文回収試験と除外候補の独立再査読を行う。現在これらを実施済みとはしていない。

[探索の監査結果](search_process_audit.md)／[再利用できる探索手順](../methods/README.md)／[新規14本の詳細](../details/round2/README.md)。
'''
(ROOT/'reports/round2_findings.md').write_text(report,encoding='utf-8')
seedtable=table(['範囲','seed','方向','確認状態','件数・記録範囲'],[[r['scope'],r['seed_id'],r['direction'],r['status'],r['details']] for r in audit['seed_checks']])
auditreport=f'''# 文献探索プロセス・網羅性監査：Round2

基準日：2026-11-11。**構造検査は{audit['structural_status']}だが、完全網羅・探索飽和は未確認。** 採用条件に合う新規12本が見つかっている。未確認候補や未探索経路を隠して終了条件を満たしたとは扱わない。

## 実際に行った探索

初回はWebの複数キーワード検索から出版社・著者版・機関リポジトリへ進む重点調査で、引用追跡は部分的だった。検索履歴は工具55行・工業51行で、APIの全件列挙や候補の発見関係が十分残っていなかった。詳細は[従来の方法の記録](../methods/current_search_process.md)を参照。

Round2は主要16本をseedに、原著References、Crossrefの登録書誌、OpenAlexの引用関係、タイトル／DOI／cited-by検索を組み合わせた。研究系列・異版・単なるテーマ類似を区別し、本文取得に失敗した経路も記録した。検索サービスで返却された上位件数を、データベース全件数とはしていない。

## 数量と単位

| 項目 | 実績 | 解釈 |
|---|---:|---|
| 検索・API・直接確認の実行記録 | {audit['search_rows']}行 | 1行にバッチやURL確認を含む。独立した128検索式ではない |
| 候補の発見記録 | {audit['candidate_discovery_rows']}行 | 同一候補の複数経路、未同定の名称、既存論文も含む |
| DOI・正規化題名でまとめた候補キー | {audit['candidate_keys']} | 実在する独立論文の確定数ではない。版や題名違いの手動確認が残る |
| 引用・関連・異版関係 | {audit['citation_edges']}行 | 原文確認、索引確認、類似検索、異版を識別。全件を確定引用と数えない |
| 本文・公開版の取得試行 | {audit['retrieval_attempts']}行 | 成功／失敗／本文未発見を含む |
| 計画したseed方向 | {audit['planned_seed_directions']} | 16論文×前方／後方 |
| 取得集合を全件一次選別できた方向 | {audit['seed_states'].get('申告した取得集合を全件一次選別',0)} | 当該索引・提供集合に限る。全世界の引用を保証しない |
| 部分確認または総数未確認の方向 | {audit['seed_states'].get('部分確認／総数未確認',0)} | 追加取得・選別が必要 |
| 保留等の候補記録 | {audit['unresolved_discovery_rows']}行／{audit['unresolved_candidate_keys']}キー | 詳細表の保留6本より広い、一次選別段階の候補を含む |

候補キー間でも同じ論文のDOIあり／なし、異版・改題が残り得る。台帳行数をPRISMAの独立論文数へ直接流用しない。今回は独立二重スクリーニングを実施していない。

## 主要seedの追跡範囲

{seedtable}

FT001のOpenAlex取得は後方31件、基準日フィルタ付き前方160件。合わせて191件のタイトル・利用できた抄録を一次選別した。191件すべての全文を読んだわけではない。原文の参考文献31件と索引31件の件数一致も同一集合の証明ではなく、erratum等の同定差の全件照合は未完了。

同じFT001でもwork表示161、基準日フィルタ160、Crossref被引用145という差があった。索引・条件・更新時点を記録し、一つの数字へ無根拠に統合しない。返却0件も「その研究に後続研究が存在しない」という証明にはしない。

## 自動監査と手作業の境界

`scripts/audit_literature_search.py` はID重複、検索の必須記録、候補リンク、Claim–Source対応、比較項目、計画seedの方向、保留の取得試行を検査する。異常を注入した自己検査で、存在しない候補ID・検索式欠落・seed追跡欠落を検出した。

このプログラムは原論文の意味を判定せず、分類ラベルや精度値が正しいことを自動保証しない。今回のPASSは記録構造の整合性であり、全件精読、研究再現、網羅率100%を意味しない。[監査JSON](../evidence/round2/audit_result.json)／[方向別CSV](../evidence/round2/seed_coverage.csv)／[未判定候補](../evidence/round2/unresolved_candidates.csv)。

## 残る不足と終了判断

- 新規適合論文が発見されたため、飽和は未確認。今回の追加論文からさらに引用を追う第2周回は未完了。
- 工業側の前方引用は検索上位・選択項目に依存。全件取得・全件一次選別済みと主張しない。
- 国内DB・日本語学会、産業別の網羅探索、独立した既知論文回収試験、除外候補の無作為再査読が未実施。
- 学習画像の重複、工具・ロット分離、匿名欠陥IDと名前の対応、クラス不均衡、人の介入条件は、収録後も未確認欄に残る。
- 採用数は50本だが、同じMMADやIN718系列を複数論文が使う。独立データセット・工場実証の数とは異なる。

今回の成果は「選定seedを一周調べ、範囲と残件を引き継げる状態にする」こと。全対象文献数の分母が確定していないため、「何割網羅したか」は算出しない。再利用手順は[playbook](../methods/literature_search_playbook.md)、確認項目は[チェックリスト](../methods/audit_checklist.md)にまとめた。
'''
(ROOT/'reports/search_process_audit.md').write_text(auditreport,encoding='utf-8')
audit_path=ROOT/'reports/industrial_defect_classification_audit.md'
old=audit_path.read_text(encoding='utf-8').split('<!-- INITIAL_AUDIT -->')[-1]
prefix=f'''# 工業欠陥種類分類：現在の監査結果

2026-11-11 Round2更新。現在は49本＝主比較38本（視覚Transformer14、VLM系7、MLLM17）、関連6本、保留5本。114出典、300主張、317根拠対応、129検索・直接確認ログを保持する。Round2の候補・引用・取得試行は[別台帳](../evidence/round2/)で管理する。

元の保留5本は再確認後も保留。10本を主採用、未知SEM欠陥のクラス発見1本を関連へ追加。同一FabGPT誌版は既存研究の書誌に結び付け、重複採用していない。IT005の誌版ではAccuracy 98.4%だが、旧版の指標不一致を過去に遡って消していない。

[現在の探索・網羅性監査](search_process_audit.md)と[追加調査結果](round2_findings.md)を参照。全49行の主要項目、根拠ID、Excel/CSV、表・フィルタ・固定ペインを検証した。[検証記録](../evidence/workbook_qa/industrial/validation.json)。

## 初回監査の記録（以下の件数は更新前）

以降は前回の状態・注意点を保存した履歴。現在の件数や探索完了率を表すものではない。

<!-- INITIAL_AUDIT -->'''
audit_path.write_text(prefix+old,encoding='utf-8')
details=ROOT/'details/round2';details.mkdir(exist_ok=True)
for r in new:
    s=allrows[r['id']];keys=['model_family','primary_model','primary_models','input','labels','task','data','data_size','dataset','split','performance','verification','limitation','limitations','locator','source_id','source_ids']
    body=f"# {link(s)}\n\n{s['authors']}。{s['year']}。DOI: {s['doi']}。採否: {s['status']}。\n\n"+table(['項目','確認内容'],[[k,s[k]] for k in keys if k in s])+'\n\n原著の図版は転載せず、上記の節・表へ参照する。\n'
    (details/(s['id']+'.md')).write_text(body,encoding='utf-8')
(details/'README.md').write_text('# Round2追加14本の詳細\n\n主採用12本、関連2本。\n\n'+'\n'.join(f"- [{r['id']}：{r['title']}]({r['id']}.md)" for r in new)+'\n',encoding='utf-8')
print(json.dumps({'reports':2,'details':len(new),'main':sum('採用' in r['status'] for r in new)},ensure_ascii=False))
