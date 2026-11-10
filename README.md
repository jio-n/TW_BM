# 工具摩耗判定技術ベンチマーク

基準日: 2026-10-20（日本時間）。国内外の商用ソリューションと原則2015年以降の学術研究を、根拠に追跡可能な形で比較する。既存リポジトリのコード・データは変更しない。

## 成果物と利用方法

2026-11-11の拡張調査として、**工業製品・材料の欠陥種類分類を行う視覚Transformer／VLM／MLLM論文**を追加した。主比較28本（視覚Transformer11、VLM系7、MLLM10）、関連5本、保留5本。入力画像、候補ラベル・プロンプト、参照画像を区別し、二値異常検出や種類付き領域検出との違いを記録している。主比較の1本は匿名の欠陥種類IDであり、名称との対応は未確認。

- [工業欠陥種類分類のExcel](outputs/industrial_defect_classification_benchmark.xlsx) / [CSV](outputs/industrial_defect_classification_benchmark.csv) / [モデル系統集計](outputs/industrial_model_family_summary.csv)
- [日本語レポート・13章](reports/industrial_defect_classification_benchmark.md) / [網羅性・品質監査](reports/industrial_defect_classification_audit.md) / [調査仕様](reports/industrial_defect_classification_scope.md)
- [代表12本の詳細](details/industrial_defect_classification/README.md) / [カバレッジ表](outputs/industrial_coverage.csv) / [出典・主張・検索・採否台帳](evidence/industrial_defect_classification/)

2026-11-11の追加調査は、**工具画像から摩耗・損傷の種類名を分類する論文**に対象を絞った。画像のみ8本、画像を含むマルチモーダル1本、書誌等の保留2本、領域検出・分割の関連4本を分けて収録した。摩耗量・寿命予測、程度だけの段階分類は主比較から除外している。

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
