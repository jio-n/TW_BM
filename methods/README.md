# 再利用する文献探索・監査手順

このフォルダは特定のテーマに依存しない調査手順を扱う。工具摩耗・工業欠陥は適用例であり、目的は「何件見つけたか」だけでなく、未実施・未取得・未判定を後から点検できるようにすること。

独自検索基盤やWebアプリは作らず、既存の学術データベースと検索サービス、JSON/CSV台帳、軽量な整合性監査を組み合わせる。文献が存在しないことや絶対的な完全網羅を自動証明する仕組みではない。

- `literature_search_playbook.md`：探索設計から終了判断までの手順。
- `current_search_process.md`：今回まで実際に使った探索方法と不足。
- `audit_checklist.md`：後から確認する項目と、何を証拠とするか。
- `templates/`：次のテーマへコピーする台帳の列定義。

今回の実施記録は `evidence/round2/`、結果は `reports/round2_findings.md` と `reports/search_process_audit.md` に出力する。

次の調査では `templates/review_protocol_template.md` に対象と除外条件を記入し、`search_matrix.csv` で未探索の軸を管理する。各台帳を記録した後に監査する。既知論文回収試験は `known_item_recall.csv` に記録する。

今回の台帳・監査の再生成は以下の順。Python標準ライブラリで動き、ネットワークや認証は不要。

```text
python scripts/build_round2_ledger.py
python scripts/audit_literature_search.py
python scripts/audit_literature_search.py --self-test
python scripts/write_round2_reports.py
```

`data/round2_search_plan.json` が今回のseed計画。別テーマでは計画と入力束を変更してから使う。監査は記録構造の検証であり、自動文献選別器ではない。OpenAlexの列挙だけを再実行する場合は `scripts/fetch_openalex_citations.py --help` を参照する。通信が必要で、索引更新により同じ件数になるとは限らない。

比較表の再生成順は、`build_focused_review.py` と `build_industrial_review.py` → `write_industrial_reports.py` → `build_performance_digest.py` → 各 `build_*_workbook.mjs` → 各 `finalize_*_workbook.py`。Excel生成にはartifact-tool、読取検証にはopenpyxlを用いる。最後に上記の台帳・監査・Round2レポートを更新する。

## DB別キーワード検索

継続的な運用には [文献調査キット](../literature-review-kit/README.md) を追加した。上記の調査方法を、8表のCSV、更新履歴、設定可能な優先度、HTMLでの進捗確認・追加指示へ具体化している。新テーマはキットの `init` から開始し、この調査固有の語群・採否を引き継がない。

[DB検索プロトコル](database_search_protocol.md) と [今回の試行結果](../reports/database_keyword_search_pilot.md) を追加。`evidence/database_keyword_pilot/` に5サイトの検索・順位・候補・残件を保存した。再生成と監査は `python scripts/build_database_pilot.py --self-test`。このスクリプトは保存済みデータの整形であり、ネット検索の自動実行ではない。
