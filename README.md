# 工具摩耗判定技術ベンチマーク

最終更新: 2026-11-11（日本時間）。国内外の商用ソリューションと学術研究を根拠に追跡可能な形で比較する。広域調査の基準日は2026-10-20、種類分類の追加調査は2026-11-11。既存の研究開発コード・データは変更しない。

## 成果物と利用方法

### Wu・Singhの参考文献からの追加確認（2026-11-12）

[追補レポート](reports/wu_singh_reference_followup.md)／[直接参考文献67件の採否](evidence/wu_singh_references/references.csv)／[候補のクラス・成績](evidence/wu_singh_references/candidate_checks.csv)。Wu2019とSingh2026の直接引用を一次選別し、Wu自身を除く3本の適合を確認。旧保留WR2C003は出版社公開図で4種類名を確認した。旧Excel・HTML・キットへは未統合のため、この判定差分は追補を参照する。

### テーマを変えて使う文献調査キット

[現在の調査ダッシュボード](literature-review-kit/examples/tool-wear-review/outputs/dashboard.html) ／ [使い方](literature-review-kit/README.md) ／ [設計](literature-review-kit/DESIGN.md) ／ [AI用手順](literature-review-kit/SKILL.md)。検索式・全ヒット・採否・保存・読了・抽出・引用・追加指示をCSV/JSONへ保存し、単体HTMLで確認する。調査量・優先点・探索配分を変更できる。既存調査の移行例は48実行・366ヒット行・338論文台帳行であり、詳細比較済みの本数や世界全体の網羅率ではない。[検証結果と移行範囲](literature-review-kit/QA.md)を参照。

### 3つのHTML資料

各ファイルを保存し、ブラウザで開く。本文・CSS・操作用JavaScriptを内蔵した単体HTML。原資料リンクにはネット接続が必要。GitHubのファイル画面ではソースが表示されるため、Download raw fileで保存する。

1. [調査方法と網羅性を高める仕組み](outputs/html/research_methodology.html)：実際の探索、DB検索、引用追跡、根拠管理、監査、残課題。
2. [工具摩耗・損傷の種類分類](outputs/html/tool_wear_classification.html)：18件（採用12・保留1・関連5）。
3. [工業欠陥の種類分類](outputs/html/industrial_defect_classification.html)：49件（採用38・保留5・関連6）。

結果資料には絞り込み、論文詳細、原資料リンクを収録。性能一覧は判定クラス・出力形式を入力・報告値と同じ行で表示する。比較表の採否・値は維持。[HTML品質確認](reports/html_briefings_quality.md)に数値・構造の検査結果とブラウザ表示確認の制約を記録した。

**論文ごとの実際の精度を見る場合**は、工具摩耗18本・工業欠陥49本をまとめた [性能値のExcel](outputs/classification_performance_summary.xlsx) / [CSV](outputs/classification_performance_summary.csv) / [数値の読み方](reports/classification_performance_summary.md) を参照。計67本＝主採用50本、保留6本、関連11本。Accuracy、Precision、Recall、F1等の数値と評価条件を併記し、数値未確認は埋めていない。

引用追跡・保留再確認で主比較に新規12本を追加し、保留1本を採用へ移した。[追加調査結果](reports/round2_findings.md) / [探索の監査](reports/search_process_audit.md) / [再利用する探索手順・テンプレート・監査スクリプト](methods/README.md)。主要16本の両方向を追ったが、部分確認と未判定候補が残り、完全網羅・探索飽和は未確認。

**工業製品・材料の欠陥種類分類を行う視覚Transformer／VLM／MLLM論文**は主比較38本（視覚Transformer14、VLM系7、MLLM17）、関連6本、保留5本。入力画像、候補ラベル・プロンプト、参照画像を区別し、二値異常検出や種類付き領域検出との違いを記録している。主比較の1本は匿名の欠陥種類IDであり、名称との対応は未確認。

- [工業欠陥種類分類のExcel](outputs/industrial_defect_classification_benchmark.xlsx) / [CSV](outputs/industrial_defect_classification_benchmark.csv) / [モデル系統集計](outputs/industrial_model_family_summary.csv)
- [日本語レポート・13章](reports/industrial_defect_classification_benchmark.md) / [網羅性・品質監査](reports/industrial_defect_classification_audit.md) / [調査仕様](reports/industrial_defect_classification_scope.md)
- [代表12本の詳細](details/industrial_defect_classification/README.md) / [カバレッジ表](outputs/industrial_coverage.csv) / [出典・主張・検索・採否台帳](evidence/industrial_defect_classification/)

**工具画像から摩耗・損傷の種類名を分類する論文**は画像のみ11本、画像を含むマルチモーダル1本、先行公開日の保留1本、関連5本を分けて収録した。関連は領域検出・分割4本と研削工具の境界1本。摩耗量・寿命予測、程度だけの段階分類は主比較から除外している。

- [種類分類に絞ったExcel](outputs/wear_type_classification_benchmark.xlsx) / [CSV](outputs/wear_type_classification_benchmark.csv)
- [モデル系統別の集計](outputs/wear_type_model_family_summary.csv)：CNN、CNN特徴＋従来ML、視覚Transformer、VLM／MLLM等を分類。Excelの「モデル系統」シートと個別論文のフィルタにも反映。
- [種類分類の調査レポート](reports/wear_type_classification_benchmark.md) / [調査仕様と採否基準](reports/wear_type_classification_scope.md)
- [既存59本の再選別](evidence/wear_type_classification/existing_papers_screening.csv) / [追加調査の根拠台帳](evidence/wear_type_classification/)

以下は2026-10-20の広域調査であり、今回の限定条件を満たす件数とは区別する。

| 成果物 | リンク |
|---|---|
| 商用製品ベンチマーク（33件） | [Excel](outputs/commercial_tool_benchmark.xlsx) / [CSV](outputs/commercial_tool_benchmark.csv) |
| 学術論文ベンチマーク（59本） | [Excel](outputs/academic_paper_benchmark.xlsx) / [CSV](outputs/academic_paper_benchmark.csv) |
| 総合技術レポート | [日本語・13章](reports/tool_wear_technology_benchmark.md) |
| 網羅性・品質監査 | [監査報告](reports/coverage_and_quality_audit.md) |
| 代表製品・論文の解説 | [詳細シート](details/) |
| エビデンス | [出典](evidence/sources.csv) / [主張](evidence/claims.csv) / [根拠対応](evidence/claim_evidence.csv) / [検索履歴](evidence/search_log.csv) |

商用51候補から33比較行（国内11・海外22）、学術72候補レコードから59本を採用。論文は本文の該当節確認25本、抄録・公開抜粋中心34本。件数達成は完全網羅を意味しない。

- `outputs/commercial_tool_benchmark.xlsx` / 同名CSV: 1製品1行。実装モデルと関連研究モデルを区別する。
- `outputs/academic_paper_benchmark.xlsx` / 同名CSV: 1論文1行。抄録確認と全文確認を区別する。
- `reports/tool_wear_technology_benchmark.md`: 日本語の技術分析。
- `reports/coverage_and_quality_audit.md`: 件数・分布・未充足領域。
- `details/`: 代表製品・論文の解説。
- `evidence/`: 出典・主張・対応関係・検索・除外・未確認台帳。
- `data/`: 統合前の調査データ。`scripts/`: 整形・Excel出力用の小規模スクリプト。

Excelでは対象工具、加工法、技術カテゴリ、確認状態でフィルタする。Claim IDから `evidence/claim_evidence.csv` を経由してSource IDと原資料内位置を確認する。未知情報を空欄やゼロで補完せず「未確認」とする。異なるデータセット・分割・指標の性能値を順位付けしない。

## 注意

GitHubには調査成果、構造化データ、出典URL、詳細解説、整形スクリプトと品質確認結果を収録する。取得元資料の再配布条件を一律に確認できていないため、ダウンロードした第三者のPDF・HTML・本文等（`evidence/raw/`）はローカルのみに保持し、アップロードしない。台帳の保存パスは調査実施環境での所在を示す。GitHubで原資料を確認する際はURL・DOIを利用する。実行環境の依存フォルダと大型の中間検査ダンプも収録しない。

候補20製品・詳細比較40論文は探索目標であり網羅性の証明ではない。メーカーの性能・効果はメーカー主張、論文性能は当該実験条件の結果として扱う。販売年・価格・市場規模が確認できない場合は推計しない。公開Web調査の限界と追加確認項目を監査に残す。

## 学術DB内のキーワード検索（2026-11-11追加）

[実施結果と不足](reports/database_keyword_search_pilot.md)／[再利用する検索手順](methods/database_search_protocol.md)／[DB別の実施範囲](evidence/database_keyword_pilot/coverage_matrix.csv)。Scholar・IEEEの画面とJ-STAGE・CiNii・arXivの公式APIを試行し、検索・取得順位・候補・残ページを記録した。新候補は本文検証前のため、精度表の採用本数へ追加していない。
