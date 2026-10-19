# 画像系の代表論文詳細

基準日2026-10-20。下表の数値は原論文の実験値であり、条件間ランキングを行わない。原著図版は転載しない。
## R0101 工具逃げ面画像処理による摩耗解析

2017 / Ovidiu Moldovan; Simona Dzitac; Ioan Moga; Tiberiu Vesselenyi; Ioan Dzitac

工具マガジンで取得する逃げ面画像を使い、従来画像処理で求めた特徴量とニューラルネットワーク、画像直接入力方式を比較する。少数画像でも判別できる可能性を示すが、同一工具の連続摩耗画像に基づく評価である。

| 項目 | 内容 |
|---|---|
| 対象工具 | エンドミル（HSS、φ14mm、2枚刃、形状区分未確認） |
| 加工・材料 | エンドミル加工 |
| 入力 | 逃げ面顕微鏡画像 |
| 出力 | 逃げ面摩耗の有無、正常/摩耗2分類 |
| モデル | Otsu、Sobel、Hough、形態処理＋ANN; 生画像ANN; 2隠れ層autoencoder |
| 構成 | 特徴EN/NSP＋1隠れ層ANNと画像直接入力ANNを比較 |
| 学習 | 教師あり分類、autoencoderによる特徴表現 |
| 規模 | 連続摩耗21画像 |
| 分割・未知条件 | 同一摩耗系列の21画像から学習/テストを選択（§4、Tables 1–3）。独立工具単位分割は未確認 |
| 指標 | 分類成功率、Training Success Rate（TSR） |
| 性能 | 著者はautoencoder分類100%成功を報告。21画像由来の小規模実験で独立工場性能ではない |
| 時間・設備 | 未確認 |
| 限界 | 1工具・1材料・21画像、手調整特徴と照明への依存。100%を汎用精度と解釈不可 |
| 確認状態 | 全文確認 |

[原資料](https://www.mdpi.com/2073-8994/9/12/296)。参照：PDF pp.4–5, §§4–5, pp.15–17。根拠：SIM001; SIM001M。Claim：CIM001_01; CIM001_02; CIM001_03; CIM001_04; CIM001_05; CIM001_06; CIM001_07; CIM001_08; CIM001_09; CIM001_10; CIM001_11。

## R0102 面フライス加工のCNN工具摩耗自動識別

2019 / Xuefeng Wu; Yahui Liu; Xianliang Zhou; Aolei Mou

摩耗種類のCNN分類と、分類結果に応じた従来画像処理による摩耗幅計測を連結する。凝着物が外接矩形を過大化する問題に画像位置合わせを用い、種類分類と定量測定を別段階で評価している。種類分類と幅計測の指標を混同しない。

| 項目 | 内容 |
|---|---|
| 対象工具 | フェイスミルのインサート |
| 加工・材料 | フライス加工 |
| 入力 | 機上工具画像 |
| 出力 | 逃げ面/すくい面/凝着/欠損の4種類分類、VB測定 |
| モデル | ToolWearnet（CNN）＋ATWVD、watershed、Roberts、画像位置合わせ、最小外接矩形 |
| 構成 | 11畳み込み＋pooling＋FC4出力、224×224 RGB入力 |
| 学習 | CAE事前学習＋教師ありSGD微調整 |
| 規模 | 画像拡張5倍。具体枚数はTable5参照 |
| 分割・未知条件 | 70/15/15、条件別の完全寿命画像系列をテスト/検証に各12組 |
| 指標 | 平均認識precision（著者AP。検出mAPとは異なる）、VB MAPE |
| 性能 | 平均認識precision 96.20%; VB MAPE約5% |
| 時間・設備 | 未確認 |
| 限界 | 凝着物の除去と輪郭処理に依存。原文の層数表記に揺れがあるため構造はTable4準拠 |
| 確認状態 | 全文確認 |

[原資料](https://www.mdpi.com/1424-8220/19/18/3817)。参照：PDF pp.7–15, Table 4/5/7, §4。根拠：SIM002; SIM002M。Claim：CIM002_01; CIM002_02; CIM002_03; CIM002_04; CIM002_05; CIM002_06; CIM002_07; CIM002_08; CIM002_09; CIM002_10; CIM002_11; CIM002_12; CIM002_13。

## R0104 反射赤外画像と多視点CNNによるミリング工具摩耗推定

2023 / Woong-Ki Jang; Dong-Wook Kim; Young-Ho Seo; Byeong-Hee Kim

赤外ラインレーザと3カメラで反射光を取得し、複数露光を融合した画像から逃げ面摩耗幅を回帰する。偏光フィルタの有無を工具群ごとに比較し、同種工具の個体単位交差検証で光学設計の効果を示す。光学条件の寄与が大きい。

| 項目 | 内容 |
|---|---|
| 対象工具 | TH308インサートを用いるエンドミル |
| 加工・材料 | エンドミル加工 |
| 入力 | 3カメラ赤外反射画像、5露光HDR |
| 出力 | 平均逃げ面摩耗幅（µm） |
| モデル | Mertens露光融合＋multi-view CNN、VAEで前処理を比較 |
| 構成 | 3視点を3channel入力、4畳み込みブロック＋FC回帰 |
| 学習 | 摩耗実測値による教師あり回帰 |
| 規模 | 10工具、各4800データ |
| 分割・未知条件 | 5工具群ごとleave-one-tool-out、残り4工具データ20%を検証 |
| 指標 | 工具別MAE（µm） |
| 性能 | 無偏光平均31.10µm、偏光平均16.84µm（個別9.50–23.67µm） |
| 時間・設備 | 未確認 |
| 限界 | 専用IR光学と偏光、乾式条件。画像枚数は独立工具数と区別が必要 |
| 確認状態 | 全文確認 |

[原資料](https://www.mdpi.com/1424-8220/23/3/1208)。参照：PDF §§2–4, Fig.9–10, Table2。根拠：SIM004; SIM004M。Claim：CIM004_01; CIM004_02; CIM004_03; CIM004_04; CIM004_05; CIM004_06; CIM004_07; CIM004_08; CIM004_09; CIM004_10; CIM004_11; CIM004_12。

## R0105 回転工具の合成画像に対する改良YOLOv4欠陥検査

2023 / Bor-Haur Lin; Ju-Chin Chen; Jenn-Jier James Lien

工具を回転させた複数画像を接続し、細かな表面欠陥を改良YOLOv4で検出する。検出headを増やして小欠陥の取りこぼしを抑えるが、全工程時間は画像合成と撮像を含むため、検出単体時間と区別が必要である。

| 項目 | 内容 |
|---|---|
| 対象工具 | 回転切削工具（個別形状は未確認） |
| 加工・材料 | 未確認（工具表面検査） |
| 入力 | 回転画像をSIFT/RANSACで360度合成 |
| 出力 | 工具表面小欠陥の位置検出。VB回帰とは別機能 |
| モデル | SIFT、RANSAC、改良YOLOv4、ASPP、4検出head |
| 構成 | 高解像度特徴を追加した4head YOLOv4 |
| 学習 | 教師ありbbox検出 |
| 規模 | train10417/validation5924/inference4808 patches |
| 分割・未知条件 | patch単位train/validation/inference枚数を記載。元工具独立性は未確認 |
| 指標 | Recall、Precision、処理時間 |
| 性能 | Recall98.7%、Precision97.3%、合成画像1枚の検出7.6秒 |
| 時間・設備 | 検出7.6秒/合成画像、撮像から13–15秒 |
| 限界 | 高い検出率は摩耗幅精度ではない。原文Table1の分数/丸めとF1表記の整合は要確認 |
| 確認状態 | 全文確認 |

[原資料](https://www.mdpi.com/1424-8220/23/9/4476)。参照：PDF §5, Table1, pp.12–14。根拠：SIM005; SIM005M。Claim：CIM005_01; CIM005_02; CIM005_03; CIM005_04; CIM005_05; CIM005_06; CIM005_07; CIM005_08; CIM005_09; CIM005_10; CIM005_11; CIM005_12。

## R0106 Inconel718ミリングの画像ViT工具摩耗監視

2026 / Garvit Singh; Ankit Agarwal; Kaushal A. Desai; Laine Mears

実画像をパッチ列に変換するViT-Largeで、複合摩耗を含む4状態を分類する。元画像200枚と別照明80枚でEfficientNet-b0と比較し照明耐性を検証するが、工場横断・未知工具形状の評価ではない。

| 項目 | 内容 |
|---|---|
| 対象工具 | インデキサブル2枚刃エンドミル |
| 加工・材料 | エンドミル加工 |
| 入力 | 機上RGB顕微鏡画像 |
| 出力 | 逃げ面、逃げ面+正面、逃げ面+BUE、チッピング4分類 |
| モデル | ViT-Large、16×16patch、24encoder、16heads |
| 構成 | 224×224入力、196patch、hidden1024、分類token＋MLP |
| 学習 | 教師あり分類 |
| 規模 | 元200枚、train160→28000拡張、test40、別照明80 |
| 分割・未知条件 | 元200を160/40に分割後学習側を拡張。別照明は独立insert |
| 指標 | Accuracy、class precision/recall/F1 |
| 性能 | 通常40枚97.50%（39/40）、別照明80枚96.25%（77/80） |
| 時間・設備 | 学習ViT約150分/4epochs、同環境CNN約539分/20epochs。推論時間は未確認 |
| 限界 | 元画像数が少なく、BUE微小特徴で誤分類。冷却液・付着・カメラずれは今後の課題 |
| 確認状態 | 全文確認 |

[原資料](https://www.mdpi.com/2075-1702/14/6/589)。参照：PDF §§2–3, Tables1–4, pp.5–12。根拠：SIM006; SIM006M。Claim：CIM006_01; CIM006_02; CIM006_03; CIM006_04; CIM006_05; CIM006_06; CIM006_07; CIM006_08; CIM006_09; CIM006_10; CIM006_11; CIM006_12; CIM006_13; CIM006_14。

## R0109 LoRA-SAMと点プロンプトによる工具摩耗分割

2025 / Zongshuo Li; Ding Huo; Markus Meurer; Miguel Panesso; Welf-Guntram Drossel; Thomas Bergs

12種類の工具顕微鏡画像に対してSAMをLoRAまたはMoE-LoRAで適応し、点プロンプトの配置と数を比較する。3正点で改善が大きいが、論文のIoU名称と数式に不整合があり、標準IoUへの読み替えはできない。

| 項目 | 内容 |
|---|---|
| 対象工具 | エンドミル4種、旋削insert7種、ミリングinsert1種 |
| 加工・材料 | 旋削/エンドミル加工/フライス加工 |
| 入力 | RGB顕微鏡画像＋正負point prompts |
| 出力 | 逃げ面摩耗領域セグメンテーション |
| モデル | ViT-L SAM、LoRA rank4、MoE-LoRA 3expert |
| 構成 | SAM image encoderのQ,Vを低rank適応、prompt/mask decoderは原設定 |
| 学習 | 教師ありparameter-efficient fine-tuning、点promptあり |
| 規模 | 977画像、12tool types |
| 分割・未知条件 | 各tool type内で約80/20、wear分布を考慮。未知type holdoutではない |
| 指標 | 著者表記IoU（Eq3はDice型、指標定義要確認） |
| 性能 | Table2: C+M1+M2点でLoRA/MoE-LoRAとも著者表記IoU0.914。標準IoUとして横比較不可 |
| 時間・設備 | 未確認 |
| 限界 | 点promptの品質に依存。Eq3は2/交差//(/予測/+/GT/)。本文U-Net0.849とTable2 0.839の矛盾もある |
| 確認状態 | 全文確認（Web PDF抽出） |

[原資料](https://d-nb.info/1383631603/34)。参照：Procedia CIRP pp.707–710, Eq3, Table1–2。根拠：SIM009; SIM009M。Claim：CIM009_01; CIM009_02; CIM009_03; CIM009_04; CIM009_05; CIM009_06; CIM009_07; CIM009_08; CIM009_09; CIM009_10; CIM009_11; CIM009_12; CIM009_13。

## R0110 SAMと自動プロンプトによる切削工具摩耗分割

2024 / Zongshuo Li; Ding Huo; Markus Meurer; Thomas Bergs

U-Netの粗い摩耗領域から点プロンプトを自動生成し、固定SAMで領域を精密化する。6工具の混合画像を用い、学習量やプロンプト生成法を比較する。SAMは固定でも前段のU-Netには教師データが必要である。

| 項目 | 内容 |
|---|---|
| 対象工具 | 3エンドミル＋3insert |
| 加工・材料 | エンドミル加工/旋削等（tool別詳細未確認） |
| 入力 | RGB顕微鏡画像 |
| 出力 | 逃げ面摩耗領域分割 |
| モデル | U-Net→PoI(MS/CoGA/RCoGA)→ViT-L SAM |
| 構成 | U-Net粗maskから正負点とmask prompt、SAMを再学習せず後処理 |
| 学習 | U-Net教師あり、SAM重み固定 |
| 規模 | Table1 train912/test190=1102画像 |
| 分割・未知条件 | 各6工具dataset内80/20と記載、Table1実数は912/190 |
| 指標 | 著者表記IoU（Eq1はDice型、要確認） |
| 性能 | 全train100epochs条件の著者表記IoU約0.87。標準IoUとして横比較不可 |
| 時間・設備 | 未確認 |
| 限界 | U-Net学習と画素ラベルは必要。SAM単体では適切promptがなく精度低下。数式と指標名不整合 |
| 確認状態 | 全文確認 |

[原資料](https://arxiv.org/html/2407.01211v1)。参照：§§2–4, Tables1–3, Eq1, Fig12。根拠：SIM010。Claim：CIM010_01; CIM010_02; CIM010_03; CIM010_04; CIM010_05; CIM010_06; CIM010_07; CIM010_08; CIM010_09; CIM010_10; CIM010_11; CIM010_12; CIM010_13。

## R0114 歯切り工具の画像摩耗領域と摩耗幅の定量化

2025 / Melina Kamratowski; Christopher Janßen; Mareike Davidovic; Thomas Bergs

歯切り工具画像をU-NetとEfficientNetで分割し、後処理と画素校正でVBmaxなどを算出する。分割IoUと寸法誤差を別々に提示しており、顕微鏡画像の分割性能がそのまま摩耗幅の精度にならないことを確認できる。

| 項目 | 内容 |
|---|---|
| 対象工具 | 歯切りstick blade、hob/fly-cutter |
| 加工・材料 | その他（歯切り/ホブ/face hobbing） |
| 入力 | 顕微鏡摩耗画像 |
| 出力 | VBm、VBmax、VBarea |
| モデル | U-Net＋EfficientNet、二値化、k-means、凸包、dilation |
| 構成 | 領域分割→輪郭後処理→pixel校正→VB値 |
| 学習 | 教師あり分割 |
| 規模 | 独立定量比較:bevel126枚/hobbing101枚 |
| 分割・未知条件 | 未確認 |
| 指標 | validation IoU、手動VBmaxとの差（µm） |
| 性能 | validation IoU0.64、例示摩耗曲線の平均絶対差7.99µm/bevel、19.95µm/hobbing |
| 時間・設備 | CNN読込後約2秒/画像、i9-10900K、64GB RAM |
| 限界 | 欠損内部の未検出でVBmax過小。撮像位置決め/洗浄の工程時間は未解決 |
| 確認状態 | 全文確認 |

[原資料](https://link.springer.com/article/10.1007/s10010-025-00864-5)。参照：§§5–7, Figs5–9。根拠：SIM014; SIM014M。Claim：CIM014_01; CIM014_02; CIM014_03; CIM014_04; CIM014_05; CIM014_06; CIM014_07; CIM014_08; CIM014_09; CIM014_10; CIM014_11; CIM014_12; CIM014_13。

## R0115 異常検知と画像分類を併用したボールエンドミル摩耗状態判定システムの開発

2024 / Hiroyuki KODAMA; Soto KOGUE; Takahiro NISHI; Kazuhito OHASHI

ボールエンドミル外観をYOLOで切り出しPatchCoreで異常検知し、送り軸電流のリカレンス画像をEfficientNetで分類する。両判定を併用して寿命工具の見逃し低減を図る。TOOL COLLAGEは撮像装置として使用される。

| 項目 | 内容 |
|---|---|
| 対象工具 | φ8/φ10ボールエンドミル、2枚刃 |
| 加工・材料 | エンドミル加工 |
| 入力 | TOOL COLLAGE工具画像＋送り軸サーボ電流 |
| 出力 | 工具寿命OK/NG、4摩耗状態 |
| モデル | YOLO切出し、PatchCore、recurrence plot、EfficientNet |
| 構成 | 外観正常画像異常検知と電流画像分類の判定を併用 |
| 学習 | 外観は正常のみ、電流画像は教師あり分類 |
| 規模 | 未確認 |
| 分割・未知条件 | 未確認 |
| 指標 | AUC、正答率、真陰性率（論文のラベル定義） |
| 性能 | 外観AUC0.92（側面/45°）、併用で全体約90%と寿命工具真陰性率98% |
| 時間・設備 | 未確認 |
| 限界 | 工具単位ラベルを2枚の刃先画像に付与し片刃の誤ラベルが生じる。商用AI搭載の根拠にはしない |
| 確認状態 | 全文確認 |

[原資料](https://www.jstage.jst.go.jp/article/transjsme/advpub/0/advpub_24-00127/_pdf/-char/ja)。参照：PDF §§2–6, pp.5–14、結言。根拠：SIM015; SIM015M。Claim：CIM015_01; CIM015_02; CIM015_03; CIM015_04; CIM015_05; CIM015_06; CIM015_07; CIM015_08; CIM015_09; CIM015_10。

## R0117 ドリル摩耗分割のデータ拡張・損失関数評価

2024 / Elke Schlager; Andreas Windisch; Lukas Hanna; Thomas Klünsner; Elias Jan Hagendorfer; Tamara Feil

ドリルのインサート画像をタイル化し、U-Netの損失・拡張強度・タイル寸法・分類定義を比較する。元画像単位で先にテストを分離しており、画像窓の混入を避ける設計と、反射に対する誤検出分析が有用である。精度指標の定義も明記する。

| 項目 | 内容 |
|---|---|
| 対象工具 | Ceratizit MaxiDrill900交換insert XOMT060304SN |
| 加工・材料 | 穴あけ |
| 入力 | 光学顕微鏡画像約4700×1200pixel |
| 出力 | abrasive wear/transfer material領域（2/多クラス） |
| モデル | U-Net、batch normalization、CE/Focal CE/IoU loss、augmentation |
| 構成 | 未確認 |
| 学習 | 教師ありsemantic segmentation |
| 規模 | 24元画像、test4、train20をtile化 |
| 分割・未知条件 | 元画像4枚を先にholdout、20枚内cross-validation、最終train90%/earlystop10% |
| 指標 | IoU、Dice、TPR/TNR |
| 性能 | binary適度拡張IoU loss:512tile IoU0.886、256tile IoU0.904（Table4） |
| 時間・設備 | 未確認 |
| 限界 | 24元画像に依存、tile数は独立画像数でない。強反射・合成顕微鏡境界に偽陽性 |
| 確認状態 | 全文確認（著者公開版） |

[原資料](https://arxiv.org/html/2302.05262v2)。参照：§§2–4, Tables1–4。根拠：SIM017; SIM017M。Claim：CIM017_01; CIM017_02; CIM017_03; CIM017_04; CIM017_05; CIM017_06; CIM017_07; CIM017_08; CIM017_09; CIM017_10; CIM017_11。

## R0120 事前学習モデルによるゼロショット工具摩耗計測

2025 / Sakib Ul Islam; Hari krishna Kandasamy; Nelson Santos; Siyu Tu; Mohammed Tauhiduzzaman

工具固有の追加学習なしにSAMやHQ-SAMを使い、工具の位置と倍率を揃えて摩耗領域を測定する。乾式ミリングで共焦点計測と比較するが、ゼロショットは校正やプロンプト、画像整列が不要という意味ではない。

| 項目 | 内容 |
|---|---|
| 対象工具 | 2インサート式ミリング工具 |
| 加工・材料 | フライス加工（乾式） |
| 入力 | ノーズ/逃げ面画像、基準新品mask |
| 出力 | ノーズ摩耗面積/逃げ面VB |
| モデル | SAM、HQ-SAM、倍率校正・mask alignment・差分 |
| 構成 | 事前学習分割→位置合わせ→摩耗領域差分/幅計測 |
| 学習 | 工具専用再学習なし（prompt/後処理は必要） |
| 規模 | 未確認 |
| 分割・未知条件 | 未確認 |
| 指標 | 相対摩耗誤差、照明CV、処理時間 |
| 性能 | 漸進逃げ面摩耗相対誤差3.81%、照明変更CV約10%、0.572秒/画像 |
| 時間・設備 | 0.572秒/画像（計算機条件は未転記） |
| 限界 | 未査読、少数実験。SAMは凝着物で過分割しHQ-SAMで補う。専用校正・基準mask必要 |
| 確認状態 | 全文確認（プレプリント） |

[原資料](https://www.researchsquare.com/article/rs-6975138/v1)。参照：PDF §§2–4, pp.17–24。根拠：SIM020; SIM020M。Claim：CIM020_01; CIM020_02; CIM020_03; CIM020_04; CIM020_05; CIM020_06; CIM020_07; CIM020_08; CIM020_09; CIM020_10; CIM020_11; CIM020_12。

## R0122 画像接続・物体検出・分割の統合による工具摩耗領域検出

2021 / Wan-Ju Lin; Jian-Wen Chen; Jian-Ping Jhuang; Meng-Shiun Tsai; Che-Lun Hung; Kuan-Ming Li; Hong-Tsu Young

回転工具を展開した合成画像からYOLOv4で刃先を見つけ、U-Netなどで逃げ面摩耗領域を分割する。分割精度と速度を比較する研究であり、局所的な良好例ではなく平均IoUと全工程の時間を見て評価する必要がある。

| 項目 | 内容 |
|---|---|
| 対象工具 | ねじれエンドミル |
| 加工・材料 | エンドミル加工 |
| 入力 | 回転工具のpanorama画像 |
| 出力 | 逃げ面摩耗領域 |
| モデル | template matching/stitching→YOLOv4→U-Net |
| 構成 | 工具展開panoramaから刃先bboxを切出しpixel分割 |
| 学習 | 教師あり検出/分割 |
| 規模 | U-Net学習約200刃先画像、Table5 FPSは70frames |
| 分割・未知条件 | training約200画像。元工具単位の独立性未確認 |
| 指標 | IoU、Dice、FPS |
| 性能 | U-Net mean IoU0.47、Dice0.65、19FPS（Table5） |
| 時間・設備 | 分割19FPS、全工程の速度とは区別 |
| 限界 | 平均IoUは0.47。局所的な高Diceだけを引用しない。工具単位独立性は未確認 |
| 確認状態 | 全文確認 |

[原資料](https://pmc.ncbi.nlm.nih.gov/articles/PMC8497480/)。参照：Methods / Experiments / Tables4–5。根拠：SIM022; SIM022M。Claim：CIM022_01; CIM022_02; CIM022_03; CIM022_04; CIM022_05; CIM022_06; CIM022_07; CIM022_08; CIM022_09; CIM022_10; CIM022_11; CIM022_12。

## R0125 深層学習とルール処理を連結する工具摩耗検出・計測

2022 / Carsten Holst; Taha Berk Yavuz; Pranjul Gupta; Philipp Ganser; Thomas Bergs

機上顕微鏡の画像から工具の存在を判定し、U-Netで摩耗領域を分け、ルール処理でVBmaxなどを計算する。画像AIと計測幾何を組み合わせる構成で、分類・分割・寸法評価の指標がそれぞれ異なる点を明確にする必要がある。

| 項目 | 内容 |
|---|---|
| 対象工具 | ボールエンドミル |
| 加工・材料 | エンドミル加工 |
| 入力 | 機上デジタル顕微鏡画像 |
| 出力 | 工具存在検出、摩耗領域、VBmax/VBmean/面積 |
| モデル | CNN tool detection、adapted U-Net、rule-based metric measurement |
| 構成 | 工具有無分類→摩耗分割→刃先に沿う幾何寸法算出 |
| 学習 | 教師あり分類/分割＋ルール後処理 |
| 規模 | 未確認 |
| 分割・未知条件 | 未確認 |
| 指標 | 工具存在Accuracy、領域Dice、摩耗測定R² |
| 性能 | 工具存在Accuracy100%、摩耗Dice0.85、手動寸法とのR²0.99（別タスクの指標） |
| 時間・設備 | 学習NVIDIA QuadroP4000、機上edge computer/USB microscope |
| 限界 | 100%は工具存在検出、R²0.99は相関でありµmの絶対誤差や寿命精度ではない |
| 確認状態 | 全文確認（Web PDF抽出） |

[原資料](https://publications.rwth-aachen.de/record/846759/files/846759.pdf)。参照：IFAC pp.534–539, §3, Conclusion, Fig13。根拠：SIM025; SIM025M。Claim：CIM025_01; CIM025_02; CIM025_03; CIM025_04; CIM025_05; CIM025_06; CIM025_07; CIM025_08; CIM025_09; CIM025_10。

