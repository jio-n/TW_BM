# 学術DB内キーワード検索の実施状況と不足

基準日：2026-11-11。今回の問いは「論文サイト内のキーワード検索を実際に使っているか、その仕組みを再利用できるか」。既存の種類分類ベンチマークを保持し、5サイトの検索を試行して、検索範囲と未確認候補を記録した。

## これまでと今回の違い

これまではWeb横断のキーワード検索・ドメイン指定、出版社原著の確認、Crossref/OpenAlex等の書誌・引用追跡が中心だった。Google Scholar／IEEE／J-STAGE／CiNii／arXivを仕様に挙げていたが、各DBのサイト内検索・公式APIを同じ検索設計で実行し、集合とページを記録する運用は不足していた。[従来の実施記録](../methods/current_search_process.md)を遡って「実施済み」に書き換えない。

今回は一般キーワードから各DBを直接検索した。取得結果には新たな候補があり、以前の結果を「ほぼ網羅」と判断する根拠には不足があることを再確認した。

## 実際の取得範囲

| DB | 今回使った経路と式数 | 取得した範囲 | 残る不足 |
|---|---|---|---|
| Google Scholar | 公式検索画面・4式 | 各10件、延べ40順位枠。画面概数は25,000／4,530／2,590／634 | 先頭ページだけ、年フィルタ未指定、最初の2式は時分未記録 |
| IEEE Xplore | 公式検索画面・2式成功、初回エラー1回 | 工具30件中25件、工業ViT77件中25件 | それぞれ残5／52件。VLM系の独立式は未実施 |
| J-STAGE | 公式記事WebAPI・6式＋1追加ページ | 延べ66書誌。各式10件以内、工具和文は次10件も取得 | 多くの式で未取得ページあり。全文・抄録の選別は一部のみ |
| CiNii Research | 公式OpenSearch・6式＋1追加ページ | 延べ60書誌。工業ViTは51件中40件。接続確認の重複30枠は別記録 | 工業ViT残11件。通常画面GETの6式はHTTP 202空応答 |
| arXiv | 公式legacy API・18式／19取得 | 診断を含む延べ120枠、87候補を題名・抄録で確認。単純工具分類8件、工業ViT11件は当該式の全件取得 | 広い工業分類111件中11件、マルチモーダル54件中13件など上位のみ |

検索ログは48行。内訳は通常取得32、失敗7、重複接続確認2、構文診断7。順位台帳366行には重複接続確認30行と構文診断61行を含み、それらを除く取得枠は275。いずれも独立論文数・関連論文数・採用数ではない。重点候補台帳は189行（ブラウザ90、arXiv87、日本DB12）で確認深度が異なる。日本DBの残りの書誌も順位台帳に保持しているが全件詳細選別済みとはしない。

根拠：[実行ログ](../evidence/database_keyword_pilot/search_log.csv)、[取得順位](../evidence/database_keyword_pilot/result_occurrences.csv)、[候補と判断](../evidence/database_keyword_pilot/candidates.csv)、[網羅性の検索枠](../evidence/database_keyword_pilot/coverage_matrix.csv)。検索語の意味・検索対象フィールド・期間が違うため、DBの総ヒット数を足したり、総数の大小で優劣をつけたりしない。

## 今回見えた候補と検索上の学び

| 発見例 | 経路 | 今回の扱い |
|---|---|---|
| Wu 2019、Realizing on-machine tool wear monitoring | Scholarの一般語 | 既収録の主要工具論文を再発見 |
| Machine vision and convolutional neural networks for tool wear identification and classification | Scholar・chipping追加式 | 既存引用探索の保留候補。出力ラベルと成績の本文確認を優先 |
| TEA-net: A multimodal deep learning framework for tool wear classification in biomedical machining | Scholar・chipping追加式 | 工具実写の有無、摩耗種類か段階かを原著で確認する候補 |
| Weft-knitted fabric defect classification based on a Swin transformer deformable convolutional network | CiNii | 新規候補。書誌・抄録段階、クラス名・成績・分割が未確認 |
| QRコード・ケーブル・溶接・半導体SEMのTransformer分類 | Scholar／IEEE | 従来の分野偏りを補う候補。題名のみで種類分類と確定しない |
| ASEを用いる半導体VLM/LLM分類、半導体パッケージ3D X線ViT | arXiv | 新規有望候補2件。本文のラベル・評価条件を確認待ち |
| 食品（マグロ・青梅）・下水・コンクリート | Scholar／IEEE | 産業範囲の境界候補。採用範囲を黙って拡大しない |

候補の原資料：[Bandaらの章](https://doi.org/10.1007/978-981-33-4597-3_66)、[TEA-net出版社ページ](https://www.sciencedirect.com/science/article/pii/S0043164825007537)、[緯編地Swin研究](https://doi.org/10.1177/00405175221137010)、[ASE研究](https://arxiv.org/abs/2404.05183)、[3D X線ViT研究](https://arxiv.org/abs/2605.01742)。この表の新規候補について、全文検証済み・性能抽出済みとは主張しない。

arXivでは事前seed17件中10件を再発見したが、未回収seedがそもそもarXivに収録されているかの確認が完了していないため、10/17を検索再現率とは呼ばない。Scholar等の既収録一致は事後照合であり、独立した検証用seed試験ではない。

## 誤った完了判定を防ぐ処理

- IEEE初回に「No results」と取得エラーが同時に表示されたため、総数を不明と記録。同じ式を画面で再実行し30件を取得した。
- CiNiiの空応答6式は検索不能の記録。OpenSearchが明示した0件の2式と区別した。公式仕様のappid必須と今回の無指定GET成功も区別して記録した。
- arXivの複合式で意図しない物理・数学分野が大量に返ったため、先頭7式を診断扱いにし、単純式で再試験した。HTTP 200と結果件数だけで検索が正しいとは判定しない。
- DOI・題名・出版社IDによる既収録一致を記録したが、異版・同一研究系列の完全な統合とは扱わない。
- 自動監査は検索ID、取得順位数、失敗の0件化、診断式の昇格を検査しPASS。3種の意図的な誤りを検出するself-testも通過。本文内容や網羅性の保証とは分けた。

## 次に埋めるべき範囲

1. IEEEの残ページ、CiNiiの工業ViT残11件、arXivの広い工業分類など、取得途中の集合を候補選別まで完了する。
2. Scholar／IEEEの画像＋センサ専用検索とIEEEのVLM／MLLM検索、年代・工具・産業別の追加式を実行する。大きな集合は年・検索フィールドで分割し範囲を記録する。
3. 新規候補・既存保留の原著から実際のクラスラベルと成績を抽出する。TEA-net等は題名のclassificationだけで採用しない。
4. DBへの収録確認と一般語の既知論文回収試験を分け、未回収の原因を整理する。除外候補の独立再判定、新採用論文の前後引用も追う。

今回の範囲は検索経路の実証と台帳化まで。従来の工具18行・工業49行、採用計50本、精度一覧67行は変更していない。新規候補を採用論文として水増しせず、精度表更新は本文検証後に行う。再利用する具体手順は [DB検索プロトコル](../methods/database_search_protocol.md)。
