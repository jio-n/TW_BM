# 文献調査キット

検索結果、まだ調べていない範囲、論文の採否、PDF取得・読了・抽出、優先度と指示をチャット外に保存する。JSON/CSVを更新し、単体HTMLで進み具合を確認できる。

調査の仕様は [DESIGN.md](DESIGN.md)、エージェントの作業手順は [SKILL.md](SKILL.md)、列と状態値は [schema.json](schema.json) を参照する。

まず [実データ入りのHTML](examples/tool-wear-review/outputs/dashboard.html) を保存してブラウザで開く。検索・論文の状態を絞り込み、各行の「指示」から追加調査のJSONを作れる。全体の検索設計は [分野共通の検索プロトコル](references/search_protocol.md)、検証範囲と移行上の制約は [QA.md](QA.md) を参照する。

このフォルダを次の作業場所へコピーして使える。`SKILL.md` は同梱した可搬用手順であり、利用環境のグローバルなスキル一覧への自動登録はしていない。AIにはこのファイルのパスを指定する。既存例は読取用に残し、新テーマは別の `--project` に初期化する。

## 新しいテーマで始める

Pythonを使い、この `literature-review-kit` ディレクトリで実行する。`--project` には調査ごとの専用ディレクトリを指定する。

```powershell
python scripts/review.py init --project reviews/polymer-degradation --title "高分子材料の劣化予測" --topic "劣化機構と予測手法の比較" --as-of 2026-11-11 --mode standard
```

生成された `project.json` に対象、入力・出力、期間、言語、採用・除外条件、抽出したい項目を記入する。例えば特定の劣化量を予測する研究に絞るか、劣化原因の分類も含むかを定める。既存プロジェクトの採否条件は、そのテーマに合わせて見直す。

`quick`、`standard`、`deep` は探索量の初期設定を選ぶ。標準は1式100件を取得目標、1回25本を選別、5本を読む設定である。目標量とバッチは後で変更できる。

```powershell
python scripts/review.py configure --project reviews/polymer-degradation --set limits.screen_batch=50 --reason "抄録による選別を先に進める"
```

## 検索を計画し、実行結果を取り込む

検索DBと検索語は調査の担当エージェントへ指定できる。

> 高分子材料の劣化予測を、J-STAGEとCrossrefで日本語・英語の両方から探して。入力が材料画像か計測信号かを記録し、まず各検索式の上位20件を取得して。

エージェントは公式API・DB画面等で検索を実行し、返った全結果をrun/hitsへ残す。CLIの `ingest` は、その結果をプロジェクトへ取り込む。キット単体で検索DBを巡回する動作は持たない。

取込用JSONは、表名をキー、行を配列とする。まず検索計画だけを取り込む例は次のとおり。

```json
{
  "queries": [
    {
      "query_id": "Q0001",
      "source": "J-STAGE",
      "query_text": "高分子 劣化 予測",
      "search_field": "全文",
      "filters": "発行年2015–2026",
      "sort_order": "関連度順",
      "purpose": "劣化予測手法の候補を収集する",
      "coverage_cell": "日本語・材料劣化予測",
      "required": "true",
      "planned_limit": 20,
      "priority": 2,
      "state": "planned"
    }
  ]
}
```

```powershell
python scripts/review.py ingest --project reviews/polymer-degradation --file query-plan.json
```

実検索の結果には `runs`、`hits`、同定した `papers` を追加する。検索日時・条件・並び順・ページ・総数の確度・実行URL・原応答へのパスを記録する。エラー時は総数を不明に保ち、DBが明示した0件と区別する。最初のページだけ取得した場合は、残る順位も表示される。

検索結果を取得できなかったrunでは、`total_hits`、`start_rank`、`returned_count` を `null` にする。次は形式確認用の合成例で、検索を実行した記録として流用しない。

```json
{
  "runs": [
    {
      "run_id": "R-synthetic-failure",
      "query_id": "Q0001",
      "search_set_id": "S-synthetic",
      "executed_at": "2026-11-11T00:00:00+09:00",
      "status": "failed",
      "semantics": "uncertain",
      "total_hits": null,
      "total_kind": "unknown",
      "start_rank": null,
      "requested_count": 20,
      "returned_count": null,
      "notes": "合成例。接続エラーにより検索結果を取得できなかった"
    }
  ]
}
```

同じ論文が別DBから見つかっても発見経路を残す。検索結果の延べ数と重複を除いた論文数は別に確認する。

## 論文を読み、確認できた範囲を記録する

以下の `P0001` は、検索結果を取り込んで登録した論文IDの例である。作業対象の実際のIDに置き換える。

```powershell
python scripts/review.py update --project reviews/polymer-degradation --table papers --id P0001 --set screening=potential --set screening_reason="対象の入力と予測量に合う。本文で評価条件を確認する" --reason "抄録を確認した"
```

PDFを保存したら保存状態とファイルパスを、読んだら読了状態を更新する。必要な結果・単位・条件・限界は `evidence` に取り込む。

```powershell
python scripts/review.py update --project reviews/polymer-degradation --table papers --id P0001 --set download_status=saved --set local_path=files/P0001.pdf --reason "公開著者版PDFを取得した"
python scripts/review.py update --project reviews/polymer-degradation --table papers --id P0001 --set reading_status=sections --set extraction_status=partial --reason "方法節と結果表を読んだ。外部検証と限界は未確認"
```

`saved` はファイルが保存された状態、`full` は全文を確認した状態である。オンラインで全文を読んだ場合も記録できる。抽出完了は、`project.json` に指定した項目と出典位置を確認してから付ける。

## 進捗を開く

```powershell
python scripts/review.py build --project reviews/polymer-degradation
python scripts/review.py next --project reviews/polymer-degradation
python scripts/review.py audit --project reviews/polymer-degradation
```

`reviews/polymer-degradation/outputs/dashboard.html` をブラウザーで開く。ローカルHTMLのため、ファイル更新後は再読み込みする。

| 見るもの | ファイル |
| --- | --- |
| 進捗と残範囲を画面で確認 | `outputs/dashboard.html` |
| 次の作業候補を表で確認 | `outputs/next_actions.csv` |
| 検索集合ごとの取得範囲を表で確認 | `outputs/search_coverage.csv` |
| 次のエージェントへ現在地を渡す | `outputs/status.json`、`outputs/next.json` |
| 台帳の整合性を確認 | `outputs/audit.json` |
| 検索結果と論文を直接確認 | `tables/` の8つのCSV |
| 更新理由・時点・差分を確認 | `history/events.jsonl`、`history/checkpoints/` |

表示される未取得順位・未選別・未読・抽出残件は、既に判明している作業量である。未検索の語やDBにある文献の総数は不明として扱う。候補率は判定済みのinclude/potential/excludeから計算し、保留と未判定は別に示す。母数10未満では見込み不明となる。

## 優先度や追加作業を指定する

次のようにチャットで指示できる。

> 本文が読めていないP0001を最優先で取得して。取得済みの候補5本は方法と評価条件を読んでから、引用追跡へ進んで。

> Q0001の21–40位を追加取得して。新しい論文だけに偏らないよう、関連度が高い基礎研究も残して。

> 評価分割が不明な論文は保留にして。精度値の高い順ではなく、同じ入力と予測対象の研究から比較して。

CLIからも作業を登録できる。優先度1が最高、5が最低である。

```powershell
python scripts/review.py request --project reviews/polymer-degradation --action obtain_fulltext --target-type paper --target-id P0001 --priority 1 --amount 1 --reason "比較の中心となる手法のため本文を先に確認する"
python scripts/review.py request --project reviews/polymer-degradation --action search_more --target-type query --target-id Q0001 --priority 2 --amount 20 --reason "現在の取得範囲の次の20件を確認する"
```

HTMLから指示を作る場合は、対象と作業を選び、指示JSONをダウンロードする。形式は次のとおり。

```json
{
  "requests": [
    {
      "action": "read_fulltext",
      "target_type": "paper",
      "target_id": "P0001",
      "priority": 1,
      "amount": 1,
      "reason": "予測対象とデータ分割を確認したい"
    }
  ]
}
```

```powershell
python scripts/review.py import-requests --project reviews/polymer-degradation --file review-requests.json
python scripts/review.py build --project reviews/polymer-degradation
```

取込後、新しい指示は `tasks.csv` の `pending` へ入る。同じJSONを再取込した場合は同じ指示として照合し、既存作業の状態を保持する。`request_id` を省略した場合は内容から安定IDを補う。同じ内容を改めて別作業として依頼する場合は、別の `request_id` を付けるか `request` コマンドを使う。

エージェントが内容を実行し、結果と完了根拠を記録する。HTMLでの指示作成後は、JSONの取込を確認する。

作業を完了にする際は、`tasks` の `status=done` と合わせて `completed_at` に実際の完了日時、`evidence_ref` に結果の根拠を設定する。読了作業であれば、対象論文の `reading_status` も実際に読んだ状態へ更新する。未読のまま読了作業を完了扱いにした場合は監査で検出される。

自動提案は関連度65%、新しさ25%、年当たり引用数10%の優先点と、優先点・新しい研究・探索の60/20/20配分を使う。未知の項目は未評価の重みとして表示する。点数は読む順番の材料として使用する。ユーザーの作業指示が先に扱われる。

論文の `user_priority` や検索式の `priority` を空欄にした場合は通常の3として扱う。関連度や引用数の空欄は未評価であり、優先度の既定値とは扱いが異なる。

## CSVを直接編集した場合

列名とIDを保って編集し、理由を付けて履歴を残す。

```powershell
python scripts/review.py checkpoint --project reviews/polymer-degradation --reason "対象材料のタグと採否理由をCSVで修正した"
python scripts/review.py build --project reviews/polymer-degradation
python scripts/review.py audit --project reviews/polymer-degradation
```

生成されたHTMLや状態JSONは再生成できる。CSV・設定と履歴を、調査プロジェクト一式として保存する。

## 次のAIへ渡す開始プロンプト

次の文のパスと今回の指示を変更して使う。

```text
literature-review-kit/SKILL.md と literature-review-kit/DESIGN.md を読んでください。
調査プロジェクトは literature-review-kit/reviews/polymer-degradation です。
project.json、outputs/status.json、tables/tasks.csv、outputs/next.json を読み、現在の採否基準と残作業を確認してください。
pending のユーザー指示を優先し、実施可能な作業から進めてください。
今回の指示は「P0001の本文を確認し、評価分割と限界を抽出する」です。
公式DBや公開原著で実行・確認した結果を台帳へ取り込み、取得・読了・抽出を実態に合わせて更新してください。
最後に build と audit を実行し、終わった範囲、残件、取得制約、次に進める作業を示してください。
```

監査で整合性が確認できても、未検索のDBや未取得順位があれば残る範囲として表示する。詳細な状態・比較条件・終了判断は [DESIGN.md](DESIGN.md) を参照する。
