# 実工具画像と別モダリティによる摩耗種類分類

調査基準日 2026年11月11日。推論時に実工具の画像と別のデータを使い、定義済みの摩耗・損傷形態を出力する研究を対象にした。複合形態は含め、VBの数値・程度段階、正常／摩耗、残存寿命は集計から外した。

## 確認結果

| 研究 | 分類ラベル | 推論入力と分類器 | 評価条件と結果 |
|---|---|---|---|
| Ahangarほか（2026年10月3日公開、採用） | `0 (flank)`、`1 (needs inspection: adhesive/combined)`。凝着と複合は同じ群。 | 刃先RGB実写のResNet-18特徴と、加速度・マイク音響・三軸切削力・履歴の特徴を連結し、クラス重み付きXGBoostへ入力。 | MATWIの独立工具セット。学習1/5/7/8/10/12、検証6/13/15、テスト4/9/11/16。検証で選んだ閾値0.30で、テストROC-AUC 0.928、Recall 65.5%、Precision 96.2%、誤警報率1.1%。§5.2、§5.4 Algorithm 2、§6.9 Table 10。 [原論文](https://doi.org/10.3390/ai7100400) |
| Yanほか（2027年1月巻、先行公開日未確認） | `flank wear`、`adhesion`、`flank wear with adhesion`。 | Qwen3-VL-8B。実刃先画像、加速度・音響の時周波数表現、切削力由来の下位モデルの出力、工程文脈を統合して種類と診断レポートを生成。 | MATWIの独立工具セット。学習2/3/5/7/8/10/11、検証6/12、テスト4/9/13（247件）。Accuracy 93.12%、Macro-F1 77.09%。§3、§4.1–4.6 Tables 2–7。 [出版社プレビュー](https://www.sciencedirect.com/science/article/abs/pii/S0951832026010963) |

Ahangarほかの三分類ではAccuracy 70.5%でも、複合摩耗96件と凝着20件をすべて見逃した。その後の二群化は、凝着の関与を点検フラグとして使う設計であり、凝着と複合の識別精度は得られない。分類の閾値を0.50から0.30に下げるとテストRecallが18.1%から65.5%へ上がった。 [§6.9 Fig. 13、Table 10](https://www.mdpi.com/2673-2688/7/10/400)

Yanほかの同一論文内の画像単独ResNet18は、刃先帯画像でAccuracy 90.98%、Macro-F1 61.79%だった。提案モデルは構成と学習方式も異なるため、差分には融合以外の要因も含まれる。出版社プレビューで方法と結果を確認した。Crossrefは2027年1月巻号を示し、DOIレコードの作成・登録更新日と先行公開日を区別した。 [§4.3 Table 3、§4.4–4.6 Tables 4–7](https://www.sciencedirect.com/science/article/abs/pii/S0951832026010963) [Crossref登録情報](https://api.crossref.org/works/10.1016/j.ress.2026.113287)

両研究は同じMATWIの超硬フライス用インサートを対象とするが、工具分割と分類体系が異なる。MATWIは刃先実写と加速度・音響・三軸力を組み合わせ、逃げ面、凝着、両者の複合を記録している。今回の採用・保留例で、クレータ、すくい面、境界、チッピング、破損を個別に分類する同様の評価は確認できなかった。 [KU Leuvenのデータ仕様](https://iiw.kuleuven.be/onderzoek/eavise/MATWI/MATWI)

## 近接事例と判定根拠

| 誤収録しやすい事例 | 判定根拠 |
|---|---|
| Visual-Acoustic Cross-Attention、Tool-MMGPT | 実工具画像と信号を併用。出力は摩耗量の回帰。 [XAF-IG論文](https://doi.org/10.3390/machines14070826) [Tool-MMGPT論文](https://doi.org/10.1016/j.compind.2025.104302) |
| OmniFuser、Kouほか | 画像と信号を併用するが、分類の対象は程度段階または逃げ面摩耗量の区分。 [OmniFuser](https://arxiv.org/html/2511.01320v1) [Kouほか](https://doi.org/10.1007/s00170-021-08282-x) |
| Amarnathほか | 光学測定でクレータ・逃げ面・チッピング等を確認する。モデル推論には切削力と加速度の特徴を使用。 [Fig. 2、Table 1、入力データI–III](https://doi.org/10.3390/machines13020132) |
| 画像測定とセンサ判定を併設する研究 | 画像確認をセンサ警報の後に実施する例や、段付きドリルのU-Netと電流・振動の監視を併設する例を確認。公開節で両入力を使う形態分類は確認できなかった。 [Dual-method論文](https://www.sciencedirect.com/science/article/pii/S1526612525006991) [段付きドリル論文](https://doi.org/10.1016/j.jmapro.2023.07.028) |
| TEA-net、Verbekeほか | 複数種類のデータを扱うが、取得した抄録・公開箇所で元のモデルの形態出力クラスが未確認。Yanの再実装は独立研究の結果として集計しない。 [TEA-net](https://doi.org/10.1016/j.wear.2025.206484) [Verbekeほか](https://doi.org/10.1007/978-3-031-74640-6_39) |

採用1件、技術適合で書誌日付保留1件、除外13件、近接事例で保留2件。原文箇所、除外・保留理由、検索23バッチを[構造化台帳](../data/focused_multimodal.json)に記録した。
