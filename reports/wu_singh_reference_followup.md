# Wu2019・Singh2026の参考文献から探す摩耗種類分類

調査期間：2026-11-11〜12（日本時間）。対象は**工具の実写画像から摩耗・損傷の種類名を出力するタスク**。複合摩耗を一つのクラスにする方式も含む。画像＋センサは別区分。摩耗量、寿命、程度のみ、使用可否のみ、信号を画像化しただけの入力は主比較に含めない。

## 結果

**Singh2026の直接参考文献から、起点のWu2019を除く3本が適合すると確認できた。** このうちHG-XAIとRealizingは既収録。残るデータセット論文は既存保留候補WR2C003（別名RWU155）であり、今回公開図を確認して種類ラベルを確定した。新たに初発見した適合論文としては数えない。

Wu2019の直接参考文献31件から、追加の適合原著は確認できなかった。ただし31件すべての被引用原著全文を読んだという意味ではない。題名・引用文脈で範囲外を選別し、近接する画像研究は原著抄録等で再確認した。

| 論文・引用位置 | 判定クラス（原語） | 入力／モデル系統 | 報告値と条件 | 今回の状態 |
|---|---|---|---|---|
| **Kumarほか：HG-XAI**（2025巻号、online 2024）／Singh [20] | Flank; Flank+BUE; Flank+Face; Chipping | 工具画像／EfficientNet-b0＋人の判断・XAI、CNN系 | Accuracy **93.08%**。人の介入を含む方式。評価件数・分割単位は未確認 | 既収録FW2001。原著抄録で確認。[原著](https://doi.org/10.1007/s10845-024-02476-2) |
| **Singhほか：Systematic approach for generating diversity-enhanced image dataset for vision-based on-machine tool wear monitoring systems**（2026）／Singh [21] | Flank; Flank+BUE; Flank+Face; Chipping | 機上顕微鏡の工具画像／EfficientNet-b0、CNN系 | Accuracy **84.16%**、MCC **0.772**。評価混同行列は120件。元のテスト画像40枚とは区別 | **旧保留WR2C003の適合確認**。抄録＋公開Figs.1,2,6,7。本文詳細未取得。[原著](https://doi.org/10.1007/s00170-026-17619-3) |
| **Kumarほか：Realizing on-machine tool wear monitoring through integration of vision-based system with CNC milling machine**（2025）／Singh [31] | Flank; Flank+BUE; Flank+Face; Chipping | 機上顕微鏡の工具画像／EfficientNet-b0、CNN系 | Accuracy **94.11%**。未見テスト画像。件数・工具単位分割は未確認 | 既収録FIA04。原著抄録・章抜粋で確認。[原著](https://doi.org/10.1016/j.jmsy.2024.12.004) |
| **Wuほか：Automatic Identification of Tool Wear Based on Convolutional Neural Network in Face Milling Process**（2019）／Singh [22] | Adhesive wear; Tool breakage; Rake face wear; Flank wear | 工具画像／ToolWearnet、CNN系 | 平均recognition precision（著者AP）**96.20%**。Accuracyと同一指標として比較しない | 既収録FT001・今回の起点自身。[原著](https://www.mdpi.com/1424-8220/19/18/3817) |

上の3本は同じ研究グループの系列。独立した3データセットで再現されたとは認定しない。実験画像の重複は未確認。複合状態は4クラスの択一分類であり、複数ラベルを同時出力するmulti-labelとは区別する。

日本語ではFlank＝逃げ面摩耗、BUE＝構成刃先、Chipping＝チッピング。**Faceという原語を、確認なしに独立した「クレーター摩耗」クラスへ置換しない。** 今回の直接引用で確認した分類は、逃げ面＋Faceなどの複合クラスである。異なる評価条件・人の介入・指標を持つため、表の数値をランキングしない。

## 保留を解消したデータセット論文の追加確認

対象はViT論文そのものではなく、その参考文献[21]にある**CNNの前報**。公開原著[Fig.2](https://link.springer.com/article/10.1007/s00170-026-17619-3/figures/2)で4種類名と元画像の分割を確認した。

| 判定クラス | 元train画像 | 元test画像 | Fig.7の評価件数 | Fig.7から計算したRecall |
|---|---:|---:|---:|---:|
| Flank | 74 | 15 | 45 | 44/45＝97.78% |
| Flank+BUE | 12 | 5 | 15 | **5/15＝33.33%** |
| Flank+Face | 54 | 15 | 45 | 37/45＝82.22% |
| Chipping | 20 | 5 | 15 | 15/15＝100% |
| 合計 | 160 | 40 | 120 | 対角和101/120＝84.1667% |

Recallは今回の調査で[原著Fig.7](https://link.springer.com/article/10.1007/s00170-026-17619-3/figures/7)から計算した値で、著者がこの形式で報告した数値ではない。元画像200枚をtrain/testに分け、学習は28,000枚へ拡張。抄録は残り20%の画像にも複合拡張を施して評価すると記すが、40枚を各々どの操作で何枚にしたかは未確認。120件を独立した120工具と解釈しない。

抄録の84.16%は原文のまま保持した。行列の101/120を通常の小数第2位に丸めると84.17%となるため、切捨てか別集計かは未確認。平均値だけを見るとBUE複合クラスの見逃しを過小評価する。工具・加工系列単位の分割、validation方法、工具仕様の本文確認は残る。根拠：SWSC004／CWSC031–CWSC035。

## 一段先の参考文献で確認した研究

直接引用とは別枠で、近接する2経路を追った。二段目の参考文献全件を探索したわけではない。

| 経路・論文 | 判定クラス | 入力・モデル | 性能／確認状態 |
|---|---|---|---|
| **Wu [11] → Ong2019 [19] → Sun・Yeh2018**：Using the Machine Vision Method to Develop an On-machine Insert Condition Monitoring System for Computer Numerical Control Turning Machine Tools | BUE、fracture、chipping、normal wear、over-wear。逃げ面摩耗を通常／過大へ細分 | 機上CCD画像／輪郭・ヒストグラム・閾値ルール。深層学習ではない | 種類判別に適合、既収録FIA01。20個の実験例。独立Accuracy/F1なし。[原著](https://doi.org/10.3390/ma11101977)、[OngのReferences 19](https://link.springer.com/article/10.1007/s00170-019-04020-6) |
| **Singh [20] → HG-XAI → Kumarほか2023**：Vision-Based Tool Wear Classification During End-Milling of Inconel 718 Using a Pre-Trained Convolutional Neural Network | **原語の出力クラス未確認**。背景にある摩耗現象を分類ラベルと見なさない | 工具画像。前回の機関抄録記録ではEfficientNet-b3 | 既知保留WR2C021を継続。ASME書誌・著者業績で実在確認、本文取得不可。性能未確定。[DOI](https://doi.org/10.1115/IMECE2023-113344)、[著者機関の業績](https://webpages.charlotte.edu/aagarw31/publications.html) |

## 似た題名でも対象に採用しなかったもの

| 引用位置・論文 | 実際の判定対象・クラス | 入力／モデル | 判定と根拠 |
|---|---|---|---|
| Wu [7] García-Ordás2018 | serviceable / disposable | 工具写真／局所テクスチャ＋SVM | 使用可否の二値。原著抄録で確認。[原著](https://doi.org/10.1016/j.ymssp.2018.04.035) |
| Wu [9] García-Ordás2017 | low/high、またはlow/medium/high | 工具写真／B-ORCHIZ＋SVM | 摩耗程度。原著抄録で確認。[原著](https://doi.org/10.1007/s00170-016-9541-0) |
| Wu [11] Ong2019 | 逃げ面摩耗の程度予測、種類クラスなし | 工具画像特徴＋切削条件／WNN | 入力を複合化しても、出力が量・程度のため対象外。[原著](https://doi.org/10.1007/s00170-019-04020-6) |
| Singh [17] Bergs2020 | ball end mill / end mill / corner-radius end mill / insert / drill。別工程は摩耗領域分割 | 工具写真／CNN＋U-Net | **95.6%は工具形状5種の分類精度**。摩耗種類精度ではない。本文Table3、§3.1、Table7確認。[公開原著](https://d-nb.info/1229969632/34) |
| Singh [18] García-Pérez2023 | acceptable（OK）/ non-acceptable（NOK） | 工具写真／CNN | 97.8%は二値判定。原著公開箇所で確認。[原著](https://doi.org/10.1016/j.jmsy.2023.03.005) |
| Singh [19] Scharf2023 | seedはOK/NOKと紹介。原著の全出力ラベルは未確認 | **工具画像＋電流＋振動**／U-Net＋Random Forest | 種類分類の採用は保留。融合の96%を摩耗種類精度に流用しない。[原著](https://doi.org/10.1016/j.jmapro.2023.07.028) |
| Singh [29] Sun2021 | seedはno-wear / initial / normal / severeと紹介。原著本文で未確認 | 工具写真／ViT | 程度分類の除外候補として保留。著者会議要約の92.5%を種類分類精度には採用しない。[IEEE](https://doi.org/10.1109/3M-NANO49087.2021.9599807) |

今回の適合直接引用3本はすべてCNN系。追加のViT／VLM／MLLMによる種類名分類は、この2つの起点の直接参考文献からは確認していない。これは分野全体に存在しないという結論ではない。

## 探索範囲・監査・残件

| 指標 | 結果 |
|---|---:|
| Wuの直接参考文献を一次選別 | 31/31位置 |
| Singhの直接参考文献を一次選別 | 36/36位置 |
| 直接引用の適合確認 | 4（うちWu自身1） |
| 直接引用の対象外 | 61（題名・引用文脈での一次選別を含む） |
| 直接引用の保留 | 2（Scharf2023、Sun2021） |
| 被引用原著の本文・抄録・公開図を確認した直接引用位置 | 12 |
| 上記以外の著者会議要約を確認 | 1（Sun2021） |
| 今回、旧保留から適合を確認 | 1（WR2C003） |
| 初めて発見した適合論文 | 0 |

全67位置の題名・引用文脈をチェックしたことと、67原著の全文精読は別である。全件の採否と確認深度は[references.csv](../evidence/wu_singh_references/references.csv)。レビュー論文の全参考文献、すべての二段目、前方引用、DBキーワード検索の再実行は今回の範囲に含めない。

優先残件はASME2023のクラス定義・成績、Scharf2023とSun2021の原著出力定義、データセット論文の評価条件、同一研究系列の画像重複。アクセス制約は書誌の不在や研究の不存在とは区別した。

Crossrefの引用メタデータにも差があった。Wu [9]の筆頭著者、Wu [11]の巻・頁、Wu [22]のpreprint/出版版DOI、Singh [18]のauthor欄を原著・出版社参考文献と区別して記録した。Singh本文による[18]のモデル紹介と原著公開箇所のspecialized Xceptionも、同一モデルだと断定しない。

## 再利用できる台帳

- [候補15件の確認結果](../evidence/wu_singh_references/candidate_checks.csv)：入力、判定クラス、モデル、成績、確認段階。
- [出典](../evidence/wu_singh_references/sources.csv)、[主張](../evidence/wu_singh_references/claims.csv)、[根拠対応](../evidence/wu_singh_references/claim_evidence.csv)、[引用経路](../evidence/wu_singh_references/citation_edges.csv)。
- [検索・閲覧履歴](../evidence/wu_singh_references/search_log.csv)、[取得試行](../evidence/wu_singh_references/retrieval_attempts.csv)、[監査結果](../evidence/wu_singh_references/audit.json)。
- [5境界候補の原著確認JSON](../data/wu_singh_reference_candidate_checks.json)：原図URL・行列・旧ID・未確認事項を保持。

この追加調査は別台帳として公開し、旧Excel・HTML・汎用キットの集計は今回再生成していない。旧WR2C003の保留理由「原語ラベル未確認」は本報告で更新された。完全本文取得済みへは変更していない。公開図・第三者PDF自体は再配布せず、URLと抽出事実を記録する。

再出力：`python scripts/build_wu_singh_reference_review.py`。元の参考文献書誌もJSONに保持しているため、原著のローカルキャッシュなしで台帳を再生成できる。スクリプトの成功は件数・ID参照の整合確認であり、文献分野全体の網羅保証ではない。
