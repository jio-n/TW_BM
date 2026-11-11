---
name: literature-review-kit
description: Plan and conduct reusable literature reviews with persistent search-result, paper, reading, evidence, and user-request ledgers. Use for multi-paper investigations where search coverage, remaining work, and adjustable depth must be visible outside the chat; not for a single-paper summary.
---

# 文献調査を、台帳を持つ継続作業として進める

ユーザーのテーマに合わせて採否・情報源・探索量を設定し、チャット外に現在の状態と次の作業を残す。手順・データ仕様は [DESIGN.md](DESIGN.md)、実行方法は [README.md](README.md)。検索DBや件数は固定的な必須リストにせず、テーマと利用可能な権限から選ぶ。

## 最初にすること

1. 既存プロジェクトがあれば `project.json` と `outputs/status.json`、未完了tasksを読む。新規なら `scripts/review.py init` で分離したプロジェクトを作る。
2. 入力・出力・対象・期間・採否基準、情報源、検索語群、予定取得範囲、確認用の既知論文を設定。引用数・新しさ・検索順位は読む順番の材料であり、採用基準や品質判定そのものにしない。
   検索式の作り方、DB選択、引用拡張と停止判断は [検索プロトコル](references/search_protocol.md) に従う。
3. `next` の候補とユーザーtasksから今回の小さな作業単位を決める。ユーザーの指定を優先し、未評価領域・低引用・新規研究の探索枠も残す。

## 調査中に残す情報

- 検索式と検索フィールド、並び順、日時、返却総数の確度、取得順位を実行ごとに記録。異なる索引時点・並び順を同一集合として混ぜない。エラーを0件としない。
- 取得した結果は未選別も含めhitsへ残し、論文のIDと発見経路を結ぶ。DOI・出版社ID・arXiv版を確認し、題名一致だけの同一性は未検証と表示する。
- screening、download、reading、extraction、前方／後方引用は別状態。保存済みPDFを精読済みにしない。本文未取得でも題名・抄録による判定はできるが確認深度を残す。
- 原資料の種類ラベル、値、単位、条件、限界をevidenceへ記録。`complete`にする前に指定された抽出項目と原資料内位置を確認する。
- 保留・除外は理由を付ける。情報不足を対象外と決めつけない。高引用や新しいという理由だけで採用しない。

## 更新と終了

`ingest`、`update`、`request`で台帳と履歴を更新し、各バッチの終わりに `build` する。CSVを直接編集した場合は理由付き `checkpoint` を使い、未追跡編集を隠さない。HTMLで作った指示JSONはtasksへの追加として読み込み、研究を実行・完了したことにはしない。

各報告は、対象範囲／検索済み集合／未取得順位／未選別／本文未取得／未精読／抽出未完了／引用未追跡／次の候補を示す。「あと何本」は既知の残作業と未知の未発見文献を区別する。上位順のヒット率を未取得全体へ外挿せず、根拠のない網羅率・予測残数を出さない。

取得上限を満たしただけで探索終了としない。監査PASSは台帳の整合であり、世界中の全文献を拾った証明ではない。予定範囲を完了したか、打ち切ったか、未判定が残るかを状態表示する。

このキットは各DBの検索・全文閲覧権限を提供しない。実際の検索と原著確認は利用できる公式API、コネクタ、ブラウザ等を用いる。ユーザーが依頼していない購入・照会メール・公開先変更を自動で行う権限は含まない。
