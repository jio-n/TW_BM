# 学術データベースのキーワード検索を再利用する手順

版：2026-11-11。全体の採否・引用追跡・成績抽出は [文献探索手順](literature_search_playbook.md) を使い、この文書でデータベース別の検索と取得範囲を管理する。実施例は [検索試行報告](../reports/database_keyword_search_pilot.md)。

## 1. 検索開始前に固定すること

対象を「入力→出力」で定義する。本調査では工具実写→摩耗種類名、工具実写＋他センサ→摩耗種類名、工業画像＋任意のプロンプト→欠陥種類名。工具の摩耗量・段階・RUL、工業の正常／異常二値だけの判定、対象物カテゴリの識別は別タスクとする。検出・領域分割のmAP/IoUを画像単位の種類分類精度と混ぜない。信号のスペクトログラムは実写と分ける。

対象期間、基準日、言語、モデル系統、産業、境界領域（食品・インフラ等）、全文未取得時の扱いをprotocolに書く。食品などを追加するときは黙って採用範囲を変えず、境界候補のまま判断を記録する。

既知論文を検索前に固定する。広い検索の設計用seedと、検索式を調整しない検証用seedを分けると、既知題名に過適合した確認を避けられる。DBに収録されているかは個別題名検索で別途調べ、一般キーワードでの回収試験と混ぜない。

## 2. 検索語を複数の方向から組む

| 語群 | 工具摩耗の例 | 工業欠陥の例 |
|---|---|---|
| 対象 | tool wear、cutting insert、end mill、工具摩耗 | surface defect、wafer、SEM、PCB、steel、fabric、外観検査 |
| 入力 | image、vision、microscopy、thermography、画像 | image、vision、X-ray、infrared、prompt |
| 出力 | classification、identification、wear type、chipping、adhesive、flank | defect classification、defect type、multi-class、multi-label、scratch、crack |
| モデル | CNN、ResNet、ViT、VLM（指定しない式も残す） | transformer、Swin、CLIP、vision-language、MLLM、multimodal large language model |

最初から全語群をANDすると、抄録に分類という語がない研究を落とす。広い式、出力語を足す式、具体的ラベル語を足す式、モデル名を足す式を分ける。日本語・英語、年代、工具・産業を替えた追加検索を行う。単純な二つ程度の概念から始め、複雑な式へ拡張したときは返却題名が意図と合うか確認する。

今回実行した再現可能な例：

```text
Google Scholar: "tool wear" "chipping" classification image
IEEE Xplore:    "defect classification" "vision transformer"
J-STAGE text:   工具摩耗 画像
CiNii q:        defect classification transformer
arXiv:          all:"tool wear" AND all:classification
arXiv:          all:"defect classification" AND all:transformer
```

同じ文字列でも、全文検索と書誌検索では検索集合が違う。複雑な括弧・引用符・AND/ORを全DBへそのままコピーして、同じ意味で検索できたと扱わない。

## 3. DBごとの取得方法と記録

| DB | 基本経路 | 実装時に残す情報 | 今回確認した制限 |
|---|---|---|---|
| Google Scholar | サイト内検索、詳細検索、引用・異版表示 | 検索式、年、並び順、取得ページ、画面の概数、題名とリンク | 今回は先頭10件／式のみ。公式ヘルプは一検索の表示上限1,000件、bulk取得非提供と説明。概数を正確な母集団としない |
| IEEE Xplore | サイト内検索／利用権限がある公式API | 検索フィールド、期間、content type、並び順、順位、article number | 今回は画面の先頭25件。検索エラーを0件としない。検索できることと本文を閲覧できることは別 |
| J-STAGE | 記事WebAPI `service=3` | `text`/`article`/`abst`、発行年、`start`、`count`、XML総数、entry数 | 今回は全文`text`。半角スペースのAND、発行年指定。記事・要旨・解説を区別 |
| CiNii Research | 論文OpenSearch／検索画面 | `articles`、`q`、`from/until`、`sortorder`、`start/count`、総数とitems数 | 通常画面GETは空応答。公式仕様はappid必須と記載。今回無指定GETで成功したが、継続運用は仕様に従う |
| arXiv | 公式legacy API | `search_query`、`start`、`max_results`、sort、Atom総数とentry数、初出・改訂日 | 1接続・3秒以上の間隔。複合式の解釈に疑義が出た実行は診断として分離し単純式で再試験 |

根拠：[Scholar Help](https://scholar.google.com/intl/en/scholar/help.html)、[IEEE API検索パラメータ](https://developer.ieee.org/docs/read/Metadata_API_details)、[J-STAGE API仕様 pp.2–5](https://www.jstage.jst.go.jp/static/files/ja/manual_api.pdf)、[CiNii OpenSearch仕様](https://support.nii.ac.jp/ja/cir/r_opensearch)、[arXiv API仕様](https://info.arxiv.org/help/api/user-manual.html)。仕様確認日：2026-11-11。

APIは公式仕様に従う範囲を自動化し、Scholar等は画面検索と許容される書誌出力を使う。認証・検索制限を回避する仕組みは作らない。契約DBが利用できる場合はScopus/Web of Science/Engineering Village等も候補にできるが、今回これらの利用権や検索を確認したとは扱わない。

## 4. 後から追える記録の単位

`検索実行ID → 結果順位 → 候補ID → 採否 → 本文取得 → Claim/精度表`をつなぐ。

1. **search_log**：検索式、日時、フィールド、期間、経路、URL、総数、取得数、開始順位、ページ、成功／失敗／診断／重複再取得。
2. **result_occurrences**：同じ論文でも見つかった検索・順位ごとに一行。検索結果の実取得範囲を失わない。
3. **candidates**：DOI、arXiv ID、出版社ID、正規化題名で同一候補を照合。異版は人が確認して統合し、発見経路を保持する。
4. **coverage_matrix**：DB×対象×入力×モデルの検索済み・未実施、検索ID、残ページ、意味検証、本文確認を別欄にする。
5. **followup_queue**：未判定と本文未取得の候補。候補数を精度表の採用数に足さない。

今回の [実行ログ](../evidence/database_keyword_pilot/search_log.csv)、[順位台帳](../evidence/database_keyword_pilot/result_occurrences.csv)、[候補台帳](../evidence/database_keyword_pilot/candidates.csv)、[実施範囲](../evidence/database_keyword_pilot/coverage_matrix.csv) はその最小例。元束は `data/database_*_pilot.json`。原応答はローカルの `evidence/raw/` に保持し、GitHubには構造化書誌とURLを公開する。

## 5. 網羅性を点検する基準

| 判定 | 点検内容 | 今回の状態 |
|---|---|---|
| 検索漏れ | 予定したDB・言語・入力・モデル・年代のセルを実行したか | 一部未実施。5DBを試しただけで全セル完了ではない |
| 取得漏れ | 各式の末尾まで取得したか。上限超過なら年・分野で分割したか | 多くは上位ページのみ。未取得順位を残す |
| 意味の誤り | エラー／複合構文誤解を0件と扱っていないか | エラー7実行と診断7実行を区別 |
| 回収能力 | 既知の関連論文を一般語で回収できるか | arXivの事前seed確認と他DBの事後再発見を区別。全DBの独立テスト未達 |
| 選別漏れ | 取得書誌を全件選別したか。除外を独立に再確認したか | 日本DBは重点12候補のみ詳細判断。二重選別未実施 |
| 引用漏れ | seedの前方・後方引用をどこまで追ったか | Round2の32方向を別台帳で追跡。新候補の再帰追跡は未実施 |
| 終了判断 | 追加探索の新規適合数と未判定残数を示したか | 新候補が出ており、飽和は宣言しない |

既知論文回収率＝一般キーワードで回収した検証用seed／そのDBに収録を確認した検証用seed。この限定的な指標を「全世界の論文の再現率」と呼ばない。DB同士の重複率、新規候補率、本文取得率も併記するが、独立性を仮定した総論文数の推計は今回行わない。

終了条件は検索前に決める。例：必須セルを実行、取得範囲を決めて全件選別、重要保留に本文取得を試行、既知論文の未回収理由を説明、追加の語群・引用追跡で新規適合が減ったことを記録、重大な未解決を公開。連続して新規0件でも検索式が狭ければ不十分である。

## 6. 軽量な自動監査

```text
python scripts/build_database_pilot.py
python scripts/build_database_pilot.py --self-test
```

実行ログと順位件数、候補の検索ID、エラーの数値化、未検証構文の扱いを検査する。self-testは「失敗を0件に変更」「診断式を網羅性根拠に昇格」「存在しない検索ID」を故意に入れ、検出できることを確かめる。PASSは台帳構造の判定であり、検索終了・本文採否・転記精度・完全網羅の認定ではない。

次の調査では [検索枠テンプレート](templates/database_search_matrix.csv) と既存protocol・known-itemテンプレートをコピーする。検索・取得・採否・精度抽出を一度に自動確定せず、各段階の残件を維持する。
