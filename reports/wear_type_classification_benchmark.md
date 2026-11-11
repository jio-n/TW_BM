# 工具画像からの摩耗・損傷種類分類ベンチマーク

調査基準日：2026-11-11。今回の対象は、工具の実写画像を入力し、摩耗・損傷の名前をカテゴリとして出力するタスクである。画像とセンサ等を統合する方法は別表にした。

## 1. 収集結果

主比較は**画像のみ11本、マルチモーダル1本**。さらに先行公開日の確認を要する1本を保留表に置いた。種類付き検出・領域分割と研削工具の境界事例の計5本は関連表として分けた。Round2で新規2本と既存保留1本を主比較に追加。[引用追跡と追加調査](round2_findings.md)／[探索監査](search_process_audit.md)。

既存59本から **R0102（提示されたWu2019）とR0106（Singh2026）**を再採用。Round2本文確認によりR0116は領域分割として主分類から除外、R0118はラベル未確定で保留。R0103/R0105/R0117は領域系の関連資料として記録した。旧保留R0027のYan論文もマルチモーダル候補として再調査した。

[専用Excel](../outputs/wear_type_classification_benchmark.xlsx)／[再利用用CSV](../outputs/wear_type_classification_benchmark.csv)／[既存59本の採否](../evidence/wear_type_classification/existing_papers_screening.csv)。原著者の性能値を条件間でランキングしない。

### 1.1 モデル系統による分類

CNN、ViT、VLM/MLLMはいずれも深層学習を使うため、「深層学習かvisionか」という二分ではなく、**主モデルの構造・最終判定方式**で分類した。入力が画像のみか画像＋センサかという軸とは独立している。比較用のベースラインだけにCNNを使用する論文は、CNN系の主提案として重複集計しない。

| 主モデル系統 | 画像のみ・採用 | マルチモーダル・採用 | 保留 | 関連の領域系 | 該当論文ID |
|---|---:|---:|---:|---:|---|
| CNN系 | 8 | 0 | 0 | 3 | FT001; FT003; FIA03; FIA04; FIA05; FIA06; FIA07; FIA08; FW2001; FW2002; FW2003 |
| CNN特徴＋従来ML系 | 1 | 1 | 0 | 0 | FIA02; MM001 |
| 視覚Transformer系 | 1 | 0 | 0 | 1 | FT002; FA001 |
| VLM／MLLM系 | 0 | 0 | 1 | 0 | MM002 |
| Attention検出器＋CNN系 | 0 | 0 | 0 | 1 | FIA09 |
| 非深層学習（画像処理・ルール） | 1 | 0 | 0 | 0 | FIA01 |

- **CNN系**：ToolWearnet、VGG、EfficientNet、AlexNet、U-Net等。現在の件数は上表に示す。画像特徴だけをCNNから取り出す方式は次の区分へ分けた。
- **CNN特徴＋従来ML系**：Walk2020はVGG16＋Gradient Boosting、Ahangar2026はResNet18＋XGBoost。後者は画像＋センサでも言語モデルを含まないためMLLMではない。
- **視覚Transformer系**：Singh2026のViT-Large。関連表のMaskLenNetはSwin backbone。EfficientNet-B0はSingh論文の比較用CNNとして別列に残した。
- **VLM／MLLM系**：YanのQwen3-VL-8B。LLMを中核に持つ画像・言語モデルなのでMLLMとして整理する。VLMとMLLMを別論文として二重計上しない。先行公開日未確認の保留区分は維持する。
- **Attention検出器＋CNN系**：ホブ論文のYOLO12s＋Ghost Slim U-Net。[工具論文のモデル構成](https://link.springer.com/article/10.1007/s10845-026-02944-x)と[YOLOv12原著の抄録](https://arxiv.org/abs/2502.12524)に基づき併記した。単純なCNNまたはViTへ一律に割り当てない。
- **非深層学習**：Sun・Yeh2018の輪郭・ヒストグラム・閾値による画像処理。

Excelには「主モデル系統」「モデル構成・判定方式」「主モデル」「比較モデルの系統」「言語モデル」「系統分類の根拠Claim ID」を追加した。[分類定義と個別割当](../data/focused_model_families.json)と[系統別集計CSV](../outputs/wear_type_model_family_summary.csv)も参照できる。分類は調査者による整理であり、各論文の性能比較や優劣を示さない。

## 2. 画像のみを入力する種類分類

| ID・論文 | 実際のクラスラベル | 手法・入力 | 種類分類の成績 | 確認・評価上の注意 |
|---|---|---|---|---|
| **FT001** [Xuefeng Wuら (2019)](https://www.mdpi.com/1424-8220/19/18/3817) | Adhesive wear; Tool breakage; Rake face wear; Flank wear | **CNN系**<br>ToolWearnet CNN（CAE事前学習＋教師あり微調整）、VGGNet-16比較 | ToolWearnet平均96.20%。凝着97.27／破損96.35／すくい面95.78／逃げ面95.41% | 全文の方法・結果を再確認（ローカル公開PDF）。混合摩耗・微小凝着・付着切粉に弱い。認識時間11sは1画像当たりと確認できない。VB測定成績は本表に含めない |
| **FT002** [Garvit Singhら (2026)](https://www.mdpi.com/2075-1702/14/6/589) | Flank; Flank + BUE; Flank + Face; Chipping | **視覚Transformer系**<br>事前学習ViT-Large（16×16パッチ、24層、hidden1024、16heads）、EfficientNet-b0比較 | 通常test39/40=97.50%。独立インサート・別照明77/80=96.25% | 全文の方法・結果を再確認（ローカル公開PDF）。元200枚とBUE17枚の少数性。微小BUEが大きなFace特徴に隠れる。Kumar2025系とのデータ非独立性に注意 |
| **FT003** [Harshavardhan Mamledesaiら (2020)](https://www.mdpi.com/2076-3417/10/20/7298) | Damaged; Deformation; Abrasive | **CNN系**<br>独自CNN。畳み込み4層（32/32/64/64）、3×3kernel、max-pooling、FC、softmax | 著者記載83.75%（約200epochで安定） | 全文の方法・結果確認（出版社公開PDF）。本論文後段のGO/NO-GO転移は今回の対象外。83.75%は3種類base modelの検証値で独立test値ではない |
| **FIA01** [Wei-Heng Sunら (2018)](https://www.mdpi.com/1996-1944/11/10/1977/pdf?version=1539498597) | BUE; fracture; chipping; normal wear; over-wear | **非深層学習（画像処理・ルール）**<br>輪郭二値化と基準線から破断/BUEを判定し、逃げ面ROIのグレーヒストグラムからチッピングと摩耗を識別。逃げ面摩耗を normal wear と over-wear に分ける（0.3 mm、チッピング指標50%の閾値）。 | 20個の使用済インサートを例示評価。Table 1の出力集計はBUE 3、fracture 1、chipping 3、normal wear 6、over-wear 7。独立Accuracy/F1なし。2.75秒平均判定、約13秒全工程。 | 出版社PDF本文確認。論文の4形態（flank wear, chipping, fracture, BUE）とTable 1の5状態出力を区別。0.67%と0.62%は同一個体反復時のチッピング率・摩耗量の相対標準偏差で分類精度ではない。 |
| **FIA02** [Jannis Walkら (2020)](https://publikationen.bibliothek.kit.edu/1000099219/56353670) | flank wear: present/absent; chipping: present/absent | **CNN特徴＋従来ML系**<br>ImageNet事前学習VGG-16の畳み込み部で固定特徴を抽出、scikit-learn Gradient Boostingを種類ごとに学習。 | 3-fold CVのMatthews correlation coefficient：逃げ面摩耗0.878、チッピング0.644。 | KIT公開著者本文・会議抄録・DOI書誌確認。二つの出力は同時陽性可。元注釈にflank wear536、chipping359、no wear96、built-up edge90を含むが、BUEのモデル評価なし。 |
| **FIA03** [Harshavardhan Mamledesaiら (2022)](https://link.springer.com/article/10.1007/s42452-022-04987-0) | BUE; Deformation; Normal wear | **CNN系**<br>CNN（畳み込み、max-pooling、dense、3クラス出力）で画像から種類予測。摩耗量は別途手計測、切削速度とともに後段ファジィ制御へ入力。 | 検証89枚でaccuracy 86.52%、loss 0.3752（Table 4）。 | 出版社本文確認。Normal wearは無摩耗と同義ではない。クレータやチッピングは今後の課題。Mamledesai 2020と同研究系列、画像重複未確認。 |
| **FIA04** [Aitha Sudheer Kumarら (2025)](https://www.sciencedirect.com/science/article/pii/S0278612524002978) | Flank; Flank+BUE; Flank+Face; Chipping | **CNN系**<br>事前学習EfficientNet-B0（出版社表記 Efficient-Net-b0）を画像分類に転移学習。 | 未見テストデータに対する4種類分類accuracy 94.11%（出版社抄録）。 | 出版社抄録・章抜粋確認。複合ラベルは4つの択一クラスで、多ラベル出力と区別。後続ViT (R0106) と著者・工具/材・分類が重なる。データ同一性は未確認、独立再現と数えない。 |
| **FIA05** [Natrayan Lakshmaiyaら (2025)](https://www.sciencedirect.com/science/article/pii/S2590123025018134) | crater wear; built-up edge (BUE) formation; thermal cracking; edge chipping; abrasion | **CNN系**<br>VGG16とVGG19。150元画像を回転/反転/平行移動/輝度等で1200枚に拡張。 | 論文報告のテストaccuracy VGG16 98.86%、VGG19 92.3%。VGG16 F1 98.86%、VGG19 F1 92.30%（平均化定義未確認）。再現・独立評価は未確認。 | 出版社抄録・本文該当箇所の検索抜粋確認。360枚に対する単純な整数正解数比を小数第2位に丸めても98.86%にならない。集計方法・図の元データ未確認のため報告値と明示し、ランキング根拠にしない。 |
| **FIA06** [Aini Zuhra Abdul Kadirら (2026)](https://semarakilmu.my/index.php/sijaset/article/view/1136) | Built-up Edge (BUE); Chipping | **CNN系**<br>AlexNet派生CNN/Adam。Gray_Edge, Gray_MorphEdge, RGB_Enhanced, ContourOnlyの4前処理比較。 | ContourOnly内部validation accuracy 99.26%、recall BUE 0.99、Chipping 1.00（原稿Table 1）。別データ例ではRGB_EnhancedとContourOnlyがチッピング5枚中4枚を判定（著者抜粋）。 | 出版社記事と号目次で正式掲載・著者順を確認。記事公開日は2026-06-09、Vol. 9 No. 1の号名はMarch 2026。評価は著者原稿の抄録・方法/結果抜粋。。99.26%は内部validation。主学習/検証の工具単位分割は未確認。軽微チッピング少数。出版社の正式記事の著者順を採用。著者公開稿とは著者順差あり。記事ページにDOIの記載なし。 |
| **FW2001** [Aitha Sudheer Kumarら (2025)](https://link.springer.com/article/10.1007/s10845-024-02476-2) | Flank; Flank+BUE; Flank+Face; Chipping | **CNN系**<br>事前学習EfficientNet-b0と人の知見・説明可能AIを組み合わせたHG-XAI。単独モデルと比較。 | HG-XAIによる摩耗4種類のAccuracy 93.08%（出版社抄録）。 | 出版社・所属機関の原著抄録確認。2024-08-14 online、2025年巻。。原著抄録の結果。人の介入条件、評価画像数、既存IN718研究との画像重複は未確認。 |
| **FW2002** [Ankit Agarwalら (2025)](https://www.sciencedirect.com/science/article/pii/S2213846325001154) | Flank; Flank + BUE; Flank + Face; Chipping | **CNN系**<br>L1で事前学習EfficientNet-b0を微調整し、HG-XAIを組み合わせL2を判定。 | L2評価のAccuracy 96%、MCC 0.96、F1-score 0.97。F1の平均化方式は抄録で未確認。 | 出版社抄録および機関原著抄録の索引を確認。。照明条件の移行と人の支援を含む。工具・現場を単位とした外部検証かは未確認。 |

## 3. 工具画像を含むマルチモーダル

| ID・論文 | 実際のクラスラベル | 手法・入力 | 種類分類の成績 | 確認・評価上の注意 |
|---|---|---|---|---|
| **MM001** [M. Nadeem Ahangarら (2026)](https://www.mdpi.com/2673-2688/7/10/400) | 0 (flank); 1 (needs inspection: adhesive/combined) | **CNN特徴＋従来ML系**<br>ResNet-18の512次元画像特徴と84次元信号・履歴特徴を連結し、クラス重み付きXGBoostで判定。 | 2群 ROC-AUC 0.928。検証で選んだ閾値0.30でテストRecall 65.5%、誤警報率1.1%、Precision 96.2%。三分類Accuracy 70.5%、複合96件と凝着20件を全件見逃し。 | 全文確認。同一公開データセットの固定工具分割。二群のしきい値は運用条件に依存。単独の凝着・複合を判別するモデルとしては評価できない。 |

ここでのマルチモーダルは**推論時に工具実写を使う**ものを指す。センサ波形をスペクトログラムにしてCNN/ViTへ渡すだけの研究や、正解ラベル測定にだけ工具写真を使う研究は含めない。

MATWI系列は同じデータ出所でも採用tool setとクラス統合が違う。Ahangarの2群分類とYanの3種類分類は同じ課題・同じ評価集合として比較できない。ROC-AUC、Precision、Recall、Accuracy、Macro-F1も相互に置換しない。

## 4. 内容適合・書誌等の保留

| ID・論文 | 実際のクラスラベル | 手法・入力 | 種類分類の成績 | 確認・評価上の注意 |
|---|---|---|---|---|
| **MM002** [Liang Yanら (2027)](https://www.sciencedirect.com/science/article/abs/pii/S0951832026010963) | flank wear; adhesion; flank wear with adhesion | **VLM／MLLM系**<br>Qwen3-VL-8Bを段階学習し、工具実写・センサ由来表現・工程文脈・下位モデルの証拠を統合。Adhesion GateとWear Type Refinementを使い、摩耗種類を含む診断レポートを生成。 | Accuracy 93.12%、Macro-F1 77.09%。同論文の画像単独ResNet18エッジ帯はAccuracy 90.98%、Macro-F1 61.79%（Table 3）。 | 出版社プレビュー、DOI登録、著者所属機関の公開PDF経路を再照合。出版社の先行公開日は未確認。。単一データセット。画像単独との比較はモデル構成・学習も異なる。論文の巻号日と先行公開日を区別。 |

Yanの巻号日とオンライン初出日は同一ではなく、先行公開日は引き続き未確認。微細ドリルのFIA06は出版社記事で正式掲載と著者順・公開日を確認して主採用へ移した。DOIは出版社記事に記載がなく、内部検証99.26%の分割条件には未確認が残る。

## 5. 複合摩耗と出力形式

| 方式 | 例 | 意味 |
|---|---|---|
| 単一ラベルの種類分類 | Wu2019の4クラス | 凝着＋破損が共存しても独立クラスなし。混合状態は誤分類要因 |
| 複合状態を1クラスにする | Kumar2025・Singh2026のFlank+BUE、Flank+Face | 4つから1つを選ぶ。任意の組合せを同時出力するmulti-labelとは異なる |
| 種類ごとの独立二値判定 | Walk2020のflank wearとchipping | 同じ工具で両方陽性になり得る。BUEは元データにあっても学習・評価対象外 |
| 種類を集合へまとめる | Ahangar2026のflank対adhesive/combined | 凝着単独と凝着＋逃げ面を区別できない。正常/異常だけの分類とも異なる |
| 領域ごとに種類を出す | MaskLenNet、U-Net、YOLO系 | 複数種類を位置付きで表現。別表の領域分類・分割性能で評価 |

ラベルは原語を保持した。**flank wearは逃げ面摩耗**。BUE（構成刃先）、adhesion/adhesive wear（凝着）、Face/rake face wear、crater wear、chipping、fracture/breakageを根拠なく同一ラベルに統合しない。摩耗位置、形態、機構、損傷状態が混在する分類体系もあるため、クラス数だけで難易度を比べない。

## 6. 領域検出・分割と研削工具の関連研究

| ID・論文 | 実際のクラスラベル | 手法・入力 | 種類分類の成績 | 確認・評価上の注意 |
|---|---|---|---|---|
| **FA001** [Yi Panら (2026)](https://www.mdpi.com/2504-4494/10/8/286) | breakage; chipping; flank wear; cracking | **視覚Transformer系**<br>Swin backbone＋query-based class/mask出力（MaskLenNet） | 96.52%。未対応/重複予測をこのAccuracyの分母に含めない | 出版社本文該当節・大学書誌確認。種類分類は領域対応後の評価。量予測成績は対象外。データ/予測記録は企業制約で未公開 |
| **FIA07** [Jannis Walkら (2023)](https://arxiv.org/pdf/2303.13540) | Background; Flank wear; Chipping; Built-up edge | **CNN系**<br>U-Net、種類ごとのピクセル意味分割。 | 51テスト画像でDice：background 0.991 / flank 0.695 / chipping 0.244 / BUE 0.596、平均0.631、pixel accuracy 0.977。 | 著者本文・出版社版書誌確認。画像レベル分類でない。Treiss et al. の213枚/同Diceのベース結果と重複が強く示唆され、独立データ・別ベンチマーク性能と扱わない。 |
| **FIA08** [Alexander Treissら (2021)](https://publikationen.bibliothek.kit.edu/1000124315/89528219) | Background; Flank wear; Chipping; Built-up edge | **CNN系**<br>U-Netセマンティック分割、Monte Carlo dropout不確実性、低品質予測を人へ回すシミュレーション。 | Table 1のtool wear Dice平均0.631、チッピング0.244、pixel accuracy 0.977。予測品質と不確実性の回帰R² 0.718は種類分類の指標でない。 | KIT公開著者原稿・書誌確認。ピクセル出力。画像レベルの低信頼判定は品質推定であって摩耗種類分類でない。同じ213枚・同DiceのFIA07との独立性なしとして監査。 |
| **FIA09** [Kacper Marciniakら (2026)](https://link.springer.com/article/10.1007/s10845-026-02944-x) | edge wear; built-up; contamination | **Attention検出器＋CNN系**<br>YOLO12sが3種類の矩形を出力し、Ghost Slim U-Netがedge wear ROIを分割、ポリゴンから摩耗量を算出。 | 分割F1 0.886 ± 0.004、摩耗量MAE 4.05 ± 0.23 µm（要約の測定指標、画像分類精度ではない）。 | 出版社本文確認。導入のflank/notch/BUE/contamination一覧をそのまま学習ラベルとしない。edge wearは分割、built-up/contaminationは検出。 |
| **FW2003** [Falko Kählerら (2026)](https://arxiv.org/html/2603.12852) | rectangular; concave; convex; with tear; without tear | **CNN系**<br>形状はEfficientNetV2-S、裂けはEfficientNetV2-Lを転移学習。 | 形状 Accuracy 95.4%・F1 0.954（Table 5）。裂け Accuracy 93.8%・F1 0.935（Table 8）。階層全体 Accuracy 87.5%（§5.4、独立9本）。 | 著者プレプリント原文確認。研削工具の変形・裂け分類を境界事例として収録。切削刃の摩耗分類への転用評価は未確認。 |

MaskLenNetの96.52%は対応付け済みインスタンスの条件付きAccuracyで、画像全体の分類Accuracyや検出APではない。Walk2023/Treiss2021は同じ213画像系列・同じ基準成績を含み、独立なベンチマークとして加算しない。ホブ研究の分割F1も摩耗種類分類精度ではない。

## 7. 採用しなかった代表例

- [児玉ら2024](https://doi.org/10.1299/transjsme.24-00127)：画像＋電流の構成は近いが、新品・摩耗初期・摩耗終期・工具寿命の段階分類。今回の種類名分類から除外。
- [Visual–Acoustic Cross-Attention 2026](https://doi.org/10.3390/machines14070826)：画像＋音響でも摩耗幅・劣化段階が出力。今回の種類比較から除外。
- [Yang2025](https://doi.org/10.15282/ijame.22.4.2025.15.0992)：切削・擦過・疲労・凝着の名前付き4種類を報告するが工具実写を推論入力にしない。
- Wu2019の後段VB測定、Mamledesai2020の後段GO/NO-GO、Mamledesai2022の後段ファジィ制御は本比較の成績へ混ぜない。

## 8. 研究を読む際の優先点と未確認事項

提示例に最も近い比較の起点は **Wu2019 → Kumar2025/Singh2026 → Walk2020**。前者は4種類、中央は複合クラス、後者は種類別の独立出力という違いを確認できる。クレータ・熱き裂を含むLakshmaiya2025も対象に合うが、拡張後分割と報告値の集計を追加確認する必要がある。

画像枚数だけでなく、独立工具数、拡張前の分割、工具単位・機械単位の分離、少数クラスのRecall/Macro-F1を比較する。クラス別再現率のない高いAccuracyだけでは、凝着やチッピングを見逃さないか判断できない。ラベルのアノテータ数、一致度、混在時の優先規則は多くの論文で十分確認できていない。

本追加調査は既存59本の再選別と一次資料・引用探索による重点収集であり、種類分類研究の完全網羅や探索飽和を保証しない。リーマ・タップ・境界摩耗の画像種類分類、任意の複合状態を扱う大規模multi-label評価、外部工場に一般化する成績は引き続き不足している。

## 9. エビデンスと調査履歴

- [出典台帳](../evidence/wear_type_classification/sources.csv)：93件（補助書誌・除外資料を含む）。
- [主張台帳](../evidence/wear_type_classification/claims.csv)と[根拠対応](../evidence/wear_type_classification/claim_evidence.csv)：120主張。MM-DATAは共通データセットMATWIの根拠であり、追加の論文を意味しない。
- [検索履歴](../evidence/wear_type_classification/search_log.csv)：102行。バッチと個別クエリが混在する。検索エンジン総件数は未提供、一部時分・個別返却数は未記録。
- [除外・保留台帳](../evidence/wear_type_classification/exclusions.csv)、[追加調査仕様](wear_type_classification_scope.md)。

確認済みは書誌・入力・ラベル・当該論文の報告を意味し、実験再現済みという意味ではない。ローカル保存PDF/HTMLは再配布せず、外部からはURL/DOIを参照する。
