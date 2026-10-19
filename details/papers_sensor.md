# センサ・時系列系の代表論文詳細

調査基準日：2026-10-20。著作権図版は転載せず、原資料の図表位置を参照する。原著の実験設定が異なる数値を順位付けしない。確認状態は各シートで区別する。

| ID | 系統 | 論文 | 確認状態 |
|---|---|---|---|
| R0007 | 特徴量ML | [スマート製造向け機械学習アルゴリズムの比較：ランダムフォレストによる工具摩耗予測](https://doi.org/10.1115/1.4036350) | 抄録のみ確認（出版社登録Crossref＋Web補足） |
| R0001 | Domain Adaptation | [切削条件変動下における複数ソース教師なしドメイン適応による工具摩耗状態識別](https://doi.org/10.3390/s25061742) | 全文確認（Web本文） |
| R0013 | 時系列 | [局所特徴と大域依存を統合した深層学習による工具摩耗予測](https://doi.org/10.1038/s41598-022-18235-3) | 全文確認（Web本文） |
| R0014 | 自己教師 | [分離型変分オートエンコーダによる自己教師あり工具摩耗監視](https://doi.org/10.1504/ijhm.2021.114174) | 抄録・本文抜粋確認（出版社索引/公開抄録） |
| R0016 | 自己教師 | [未ラベルデータで強化したグラフニューラルネットワークによる工具残存寿命予測](https://doi.org/10.3390/s25134068) | 全文確認（Web本文） |
| R0017 | 転移 | [工程に組み込める単一センサによるデータ駆動型ミリング工具摩耗予測](https://doi.org/10.1007/s10845-026-02939-8) | 抄録・本文抜粋確認（出版社索引/公開抄録） |
| R0019 | 物理AI | [物理制約付きニューラルネットワークによる工具残存寿命予測](https://doi.org/10.1038/s41598-026-72453-7) | 抄録のみ確認（出版社登録Crossref＋Web補足） |
| R0021 | Transformer/ViT | [P25旋削における物理誘導型特徴融合と軽量CSAKansformerによる摩耗診断](https://doi.org/10.3390/s26102937) | 全文確認（Web本文） |
| R0029 | 特徴量ML | [実工場条件の球状黒鉛鋳鉄に対する半教師ありタップ摩耗検知](https://doi.org/10.1007/s00170-025-16491-x) | 全文確認（Web本文） |

## R0007 — スマート製造向け機械学習アルゴリズムの比較：ランダムフォレストによる工具摩耗予測

2017 / Dazhong Wu; Connor Jennings; Janis Terpenny; Robert X. Gao; Soundar Kumara / Journal of Manufacturing Science and Engineering

複雑な物理モデルの作成に依存しない工具摩耗予測法として、ランダムフォレスト回帰を検討する。315回のフライス加工実験から得たデータで、単一隠れ層の順伝播誤差逆伝播ニューラルネットワークおよびSVRと比較した。抄録はRFの優位性を報告するが、評価誤差の絶対値や条件間移植性は別途確認が必要である。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | フライス工具（形状未確認） |
| 加工法・被削材 | フライス加工 / 未確認 |
| 入力 | 加工実験データ、センサ詳細未確認 |
| 出力 | 摩耗量予測 |
| モデル | Random Forest regression |
| 処理フロー | Random Forest regression |
| 新規性 | 同一工具摩耗データでRF/FFBP ANN/SVRを比較 |
| 学習 | 教師あり回帰 |
| データ | 315フライス試験 |
| 性能 | 未確認（根拠付き数値を抽出できず） |
| 評価条件 | 未確認 |
| 分割 | 未確認 |
| 未知条件 | 未確認 |
| 実装・速度 | 未確認 |
| 限界・監査上の留意点 | 抄録のみ。未知工具・条件の分割方法、性能絶対値、センサ詳細は未確認。 |
| 公開データ・コード | 未確認 |

原資料：[出版社・原文](https://pure.psu.edu/en/publications/a-comparative-study-on-machine-learning-algorithms-for-smart-manu/) / [DOI](https://doi.org/10.1115/1.4036350)。位置：Abstract;Crossref metadata。

構成図・判定例への参照：抄録のみ。元資料の構成図は未確認。

エビデンス：SS007;SSM007。Claim ID：CS019;CS020。確認状態：抄録のみ確認（出版社登録Crossref＋Web補足）。

## R0001 — 切削条件変動下における複数ソース教師なしドメイン適応による工具摩耗状態識別

2025 / Zhigang Cai; Wangyang Li; Jianxin Song; Hongyu Jin; Hongya Fu / Sensors

切削条件が変化すると監視信号の分布も変わる問題に対し、複数の既知条件を独立したソースとして利用する。力・振動の統計特徴を非定常Transformerで抽出し、分布と分類器を整合する。未ラベルの対象条件を利用した27転移課題で検証し、境界付近とびびり混入が誤認要因となった。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | TiAlN被覆4枚刃超硬エンドミル（形状詳細未確認） |
| 加工法・被削材 | エンドミル加工 / 40Cr13鋼、290 HB |
| 入力 | 切削力・振動、10 kHz、各channel11統計特徴 |
| 出力 | 逃げ面摩耗VBmaxに基づく3状態 |
| モデル | MFSAN;非定常Transformer Encoder (NSTE);sliced Wasserstein distance |
| 処理フロー | 11種統計特徴→NSTE共通特徴→各source-target固有分布整合→分類器出力整合→3状態 |
| 新規性 | 非定常共通特徴とSWDによる複数source個別整合 |
| 学習 | 複数source教師あり＋target教師なし適応 |
| データ | 9工具・9条件、27転移課題 |
| 性能 | 27課題平均93.22%、範囲86.01–98.45% |
| 評価条件 | 3状態（VB≤85 μm、85<VB≤165 μm、VB>165 μm）、9条件の27課題 |
| 分割 | source有ラベル、targetから一部の未ラベルを適応に使用し残部で評価 |
| 未知条件 | あり：切削速度・径方向幅・軸方向深さの各未学習値へ適応。ただしtarget信号へアクセス |
| 実装・速度 | 未確認 |
| 限界・監査上の留意点 | びびり混入と大切込みで正常→重度誤分類。未見工場・材種・工具形状へ一般化は未検証。 |
| 公開データ・コード | 未確認 |

原資料：[出版社・原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC11946328/) / [DOI](https://doi.org/10.3390/s25061742)。位置：§2;§3.1–3.2;§4.1;Table A1。

構成図・判定例への参照：Fig.3: MFSAN全体、Fig.4:非定常encoder、Table A1:27転移task。

エビデンス：SS001;SSM001。Claim ID：CS001;CS002;CS003;CS004。確認状態：全文確認（Web本文）。

## R0013 — 局所特徴と大域依存を統合した深層学習による工具摩耗予測

2022 / Changsen Yang; Jingtao Zhou; Enming Li; Mingwei Wang; Ting Jin / Scientific Reports

手設計特徴と自動学習特徴を併用し、波形の局所的な周波数表現と長期依存から工具摩耗を回帰する。波レット画像を多尺度CNNで処理し、系列をLSTMへ入力する。9工具・9切削条件の工具単位交差検証とPHM2010で評価するが、PHM2010では既存モデルを必ずしも上回らず、複雑化による過学習を自ら指摘する。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | フライス工具Zhuzhou GM-4E-D10.0（形状未確認） |
| 加工法・被削材 | フライス加工 / 1045鋼 |
| 入力 | SPIKE曲げモーメント・トルク、2500 Hz |
| 出力 | 全刃の最大逃げ面摩耗 |
| モデル | LFGD-TWP;wavelet scalogram;enhanced CNN;multi-layer LSTM |
| 処理フロー | 曲げモーメント/トルク→wavelet scalogram→multi-scale CNN＋手動特徴→2層LSTM→摩耗回帰 |
| 新規性 | 多尺度自動特徴と手動特徴をLSTMへ統合 |
| 学習 | 教師あり回帰 |
| データ | 9工具・9条件、補足PHM2010 C1/C4/C6各315cut |
| 性能 | 9条件平均MAE=7.36、RMSE=9.65（摩耗尺度、表7単位未明示）。PHM2010平均MAE=6.65、RMSE=8.42 |
| 評価条件 | Table7は9工具leave-one-tool-out。PHM2010の別結果と混ぜない |
| 分割 | 9工具のうち8訓練/1テストを9回。PHM2010別途交差検証 |
| 未知条件 | あり：工具単位・9切削条件。ただしハイパラメータをtest MSEで選択した記述あり |
| 実装・速度 | 未確認 |
| 限界・監査上の留意点 | 本文にtest MSEで構造選択と記載、ネストした検証独立性に懸念。sampling変化とPHM2010過学習を著者が指摘。 |
| 公開データ・コード | 自収集データは要求時提供。PHM2010公開。コード未確認。 |

原資料：[出版社・原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9418252/) / [DOI](https://doi.org/10.1038/s41598-022-18235-3)。位置：Experimental setup/Table1;Results/Table7;Conclusions。

構成図・判定例への参照：Fig.2–5:構成、Table7:9工具比較、Fig.10:PHM2010。

エビデンス：SS013;SSM013。Claim ID：CS035;CS036;CS037;CS038。確認状態：全文確認（Web本文）。

## R0014 — 分離型変分オートエンコーダによる自己教師あり工具摩耗監視

2021 / Tim Von Hahn; Chris K. Mechefske / International Journal of Hydromechatronics

時系列畳み込みネットワークを用いた分離型変分オートエンコーダで、工具摩耗を自己教師ありに表現する。入力空間と潜在空間の異常検知をミリングと実工場CNCデータで評価した。切削条件全体と浅切込みでPR-AUCが大きく異なり、多様な製造部品への一般化の難しさを定量的に示す事例である。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | フライス工具、工業CNC工具（形状未確認） |
| 加工法・被削材 | フライス加工;工業CNCの加工詳細未確認 / 未確認 |
| 入力 | 工具状態監視時系列 |
| 出力 | 摩耗トレンド・異常検知 |
| モデル | disentangled β-VAE;Temporal CNN;入力/潜在空間異常検知 |
| 処理フロー | disentangled β-VAE;Temporal CNN;入力/潜在空間異常検知 |
| 新規性 | 分離型潜在表現と時間畳み込みによる摩耗トレンド |
| 学習 | 自己教師あり・異常検知 |
| データ | 未確認 |
| 性能 | ミリング全条件0.45、浅切込み最大0.80、実工場最大0.41 |
| 評価条件 | 全条件と部分集合、工場データで異なる条件。Accuracyとは別指標 |
| 分割 | 未確認 |
| 未知条件 | あり：工業CNCへの評価。ただし部品横断一般化が弱い |
| 実装・速度 | 未確認 |
| 限界・監査上の留意点 | 実工場の多様な部品へ一般化が低下。最大値を全体値としない。 |
| 公開データ・コード | 著者公開GitHub https://github.com/tvhahn/ml-tool-wear |

原資料：[出版社・原文](https://www.inderscience.com/info/inarticle.php?artid=114174) / [DOI](https://doi.org/10.1504/ijhm.2021.114174)。位置：Publisher Abstract;author GitHub README。

構成図・判定例への参照：著者公開コード https://github.com/tvhahn/ml-tool-wear のnotebookに再現図。本文図番号は未確認。

エビデンス：SS014;SSM014。Claim ID：CS039;CS040;CS041;CS042。確認状態：抄録・本文抜粋確認（出版社索引/公開抄録）。

## R0016 — 未ラベルデータで強化したグラフニューラルネットワークによる工具残存寿命予測

2025 / Dingli Guo; Honggen Zhou; Li Sun; Guochao Li / Sensors

未ラベル工具データを使い切るため、切削回数とともに摩耗が増す性質を事前学習の損失へ組み込む。7センサをグラフのノードとして融合し、未ラベルで学んだGNNを有ラベルRUL回帰へ転移する。PHM2010と独自データで検証するが、RULラベルは選んだ摩耗閾値に依存し、加工条件は同一である。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | PHM2010:3枚刃ボールエンドミル、JUST_T05:4枚刃フライス工具 |
| 加工法・被削材 | フライス加工;エンドミル加工 / 未確認 |
| 入力 | 3軸力・3軸振動・AE、センサ各30特徴 |
| 出力 | RUL（残りcut数、摩耗閾値0.16 mm） |
| モデル | GNN;ULDTM/LDTM;monotonicity loss |
| 処理フロー | 7センサ各30特徴→完全結合graph→未ラベル単調性事前学習→パラメータ転移→RUL回帰 |
| 新規性 | センサgraph融合と単調な潜在表現を利用する未ラベル活用 |
| 学習 | 未ラベル単調性事前学習＋教師あり転移 |
| データ | C1 306+C4 278を教師あり訓練、C6 238をvalidation、C2 289/C3 238/C5 238を事前学習 |
| 性能 | PHM2010で最大RMSE50.6%/MAE53.9%/MAPE23.66%低減、JUST_T05で37.3%/29.1%/1.82% |
| 評価条件 | C1+C4 train、C6 validation。最大改善率で絶対残寿命誤差とは別。RUL=閾値到達cut−現在cut |
| 分割 | 工具単位分割、未ラベルC2/C3/C5を別々に転移。validationの独立test化は未確認 |
| 未知条件 | 工具違いは評価、PHM/独自とも条件は固定、工場・条件外は未検証 |
| 実装・速度 | 未確認 |
| 限界・監査上の留意点 | 閾値0.16mmに依存し同一加工条件。図だけの絶対誤差は読み取り推定しない。 |
| 公開データ・コード | Data are contained within the article（原文）。PHM2010公開、独自生データURL未確認。 |

原資料：[出版社・原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12251633/) / [DOI](https://doi.org/10.3390/s25134068)。位置：§2;§3.1–3.2/Table3–4;§4;§5。

構成図・判定例への参照：Fig.1:全体、Fig.3:GNN、Fig.4–5:未ラベル/有ラベル学習、Fig.13:PHM2010比較。

エビデンス：SS016;SSM016。Claim ID：CS045;CS046;CS047;CS048。確認状態：全文確認（Web本文）。

## R0017 — 工程に組み込める単一センサによるデータ駆動型ミリング工具摩耗予測

2026 / Eric Hirsch; Christian Friedrich / Journal of Intelligent Manufacturing

工場への取り付けやすさを重視し、単一の加速度計と少数の工具寿命データから状態分類・逃げ面摩耗回帰を行う。手設計特徴とSTFTを複数モデルで比較し、2種類の機械間移植も評価する。4工具寿命で同一ドメインの精度は高い一方、別機械への移植で全モデルの性能が低下した点が実装上重要である。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | フライス工具（形状未確認） |
| 加工法・被削材 | フライス加工 / 未確認 |
| 入力 | 単一加速度、手設計特徴またはSTFT |
| 出力 | OK/Worn分類;逃げ面摩耗回帰 |
| モデル | Random Forest;SVM;Gradient Boosting;EfficientNetV2;LSTM;ConvNeXt |
| 処理フロー | Random Forest;SVM;Gradient Boosting;EfficientNetV2;LSTM;ConvNeXt |
| 新規性 | 単一センサ・低データ量・機械間移植を同時評価 |
| 学習 | 教師あり、機械間transfer評価 |
| データ | 最少4工具寿命、2工作機械 |
| 性能 | ConvNeXt 99.1%、R²0.95、RF分類99.3%（source domain） |
| 評価条件 | 4工具寿命訓練のsource評価。別機械転移では低下、絶対値未確認 |
| 分割 | 未確認 |
| 未知条件 | あり：2機械間移植。移植後数値は未確認 |
| 実装・速度 | 追加Table10:Ryzen7 5700X/64GB/RTX4090、時間数値未確認 |
| 限界・監査上の留意点 | sourceでの99%台を別機械での性能と混同しない。出版版本文は購読制限、プレプリント同一研究。 |
| 公開データ・コード | データは要求時提供、コードURL未確認 |

原資料：[出版社・原文](https://link.springer.com/article/10.1007/s10845-026-02939-8) / [DOI](https://doi.org/10.1007/s10845-026-02939-8)。位置：Publisher Abstract;Data Availability;Additional Table10。

構成図・判定例への参照：出版社追加Table10:計算時間、Fig.13:機械ごとの特徴分布。プレプリントは同一研究の https://arxiv.org/abs/2412.19950 。

エビデンス：SS017;SSM017。Claim ID：CS049;CS050;CS051;CS052。確認状態：抄録・本文抜粋確認（出版社索引/公開抄録）。

## R0019 — 物理制約付きニューラルネットワークによる工具残存寿命予測

2026 / Jinping Chen; Lijuan Shen; Zhisheng Ye; Jing Chen; Kun Luo; Weiwang Chen; Shuai Li; Rui He; Qing Han / Scientific Reports

Archard摩耗則から得る摩耗速度を損失関数に加え、LSTMで工具劣化と残存寿命を予測する。PHM2010の有ラベル群で比較し、未ラベル群でも一般化試験を記載する。抄録のμm単位誤差は摩耗量の誤差でありRUL時間誤差と区別する。摩耗係数はハンドブック値に固定され、適応同定は今後の課題である。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | PHM2010フライス工具（形状は当該抄録で未確認） |
| 加工法・被削材 | フライス加工 / 未確認 |
| 入力 | PHM2010監視信号 |
| 出力 | 逃げ面摩耗とRUL |
| モデル | PINN;Archard wear constraint;LSTM |
| 処理フロー | PINN;Archard wear constraint;LSTM |
| 新規性 | Archard速度制約とLSTMのhybrid損失 |
| 学習 | 教師あり＋物理損失 |
| データ | 未確認 |
| 性能 | MAE4.25 μm;RMSE4.83 μm;同一条件寿命末期偏差2.46% |
| 評価条件 | PHM2010 test、割当詳細未確認。未ラベル群の真値評価法は要確認 |
| 分割 | 未確認 |
| 未知条件 | 未ラベル群への一般化と記載、真の条件外は未確認 |
| 実装・速度 | 未確認 |
| 限界・監査上の留意点 | Archard係数k固定。未ラベル群の評価根拠と寿命末期偏差の定義を本文で要確認。2026-10-01先行公開。 |
| 公開データ・コード | 著者Zenodoソフト https://zenodo.org/records/22765591（コード内容未精査） |

原資料：[出版社・原文](https://www.nature.com/articles/s41598-026-72453-7) / [DOI](https://doi.org/10.1038/s41598-026-72453-7)。位置：Publisher Abstract;early-access notice。

構成図・判定例への参照：先行公開抄録のみ。構成図・表番号は未確認。

エビデンス：SS019;SSM019。Claim ID：CS056;CS057;CS058;CS059。確認状態：抄録のみ確認（出版社登録Crossref＋Web補足）。

## R0021 — P25旋削における物理誘導型特徴融合と軽量CSAKansformerによる摩耗診断

2026 / Shuqiang Wang; Tianyue Zhang; Ximin Liu; Wei Liu; Huanqi Zhang; Feng Chang / Sensors

旋削の多センサ特徴を物理的な順序で並べ、GASF・GADF・外積をRGBへ配置して14層のCSAKansformerで分類する。3工具のleave-one-tool-outで評価するが、クラスは各工具全寿命の15/70/15%区間から作る。全寿命の最大値を使う正規化も記載され、オンライン実装に対して未来情報への依存を監査する必要がある。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | P25無被覆超硬旋削インサート |
| 加工法・被削材 | 旋削 / 19NiMoCr6鋼 |
| 入力 | Vicomtech turning、力・振動・AE・電流電圧等の多センサ特徴 |
| 出力 | 寿命進行割合で定義した軽度/中度/重度3状態（VB閾値分類とは異なる） |
| モデル | PG-MGAF;SCConv;CSAM;KAN-Transformer;WGAN-Div |
| 処理フロー | 力・振動・AE等特徴→頑健処理→WGAN-Div→GASF/GADF/外積RGB→SCConv/CSAM/KAN→3状態 |
| 新規性 | 物理誘導GAF融合とKANを組み込む軽量14層ネット |
| 学習 | 教師あり分類、WGAN-Div少数クラス拡張 |
| データ | Tool11:146pass、Tool14:165pass、Tool15:214pass |
| 性能 | 3fold平均Accuracy93.6%、1step5.90 ms。Tool15 fold94.0%、重度Recall100%（160試料） |
| 評価条件 | LOTO3fold、3状態=工具寿命の最初15%/中70%/最後15%、Tool15 test470試料 |
| 分割 | 工具単位LOTO：他2工具訓練、残1工具test。生成はtrain少数class |
| 未知条件 | あり：同一材/同一条件の工具間。未知加工条件・工場は未検証 |
| 実装・速度 | 14層、1step5.90ms（ハードウェア条件未確認、end-to-end遅延ではない） |
| 限界・監査上の留意点 | PG-MGAFが工具全寿命最大値で正規化(§4.1.4)。将来情報を使わない再評価が必要。クラスはVB固定閾値でなく寿命割合。 |
| 公開データ・コード | 原データ名Vicomtech、コードURL未確認 |

原資料：[出版社・原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13211143/) / [DOI](https://doi.org/10.3390/s26102937)。位置：Abstract;§4.1.1/Table1–2;§4.1.4;§4.2.4/Table6。

構成図・判定例への参照：Fig.1–2:network/全体、Fig.10:PG-MGAF、Table6:モデル比較。

エビデンス：SS021;SSM021。Claim ID：CS062;CS063;CS064;CS065。確認状態：全文確認（Web本文）。

## R0029 — 実工場条件の球状黒鉛鋳鉄に対する半教師ありタップ摩耗検知

2025 / Jose Alberto Maestro-Prieto; Alain Gil-Del-Val; Andres Bustillo / The International Journal of Advanced Manufacturing Technology

実工場の36本のタップと7000超のねじ加工から、摩耗に伴うねじ品質を半教師ありで判定する。内部主軸トルクを領域積分し、トレンド平滑化と11点窓勾配を追加してCo-Forest等を比較する。少数ラベルの利用を検証するが、出力はゲージによる品質合否でありVB値ではない。未知工具への独立評価も未確認である。

| 項目 | 確認内容 |
|---|---|
| 対象工具・加工 | 3溝タップ、M10×1.5 mm、5種コーティング |
| 加工法・被削材 | ねじ切り / 球状黒鉛鋳鉄GGG50 |
| 入力 | CNC内部主軸モータtorqueのA1–A7面積、被覆ID、window11の7勾配 |
| 出力 | 摩耗に関連するねじGo/No-Go品質（摩耗量VBの直接測定ではない） |
| モデル | Co-Forest;co-training;tri-training;SMO/SVM;KEEL |
| 処理フロー | 内部torque→A1–A7領域特徴→回帰平滑化＋window11勾配→半教師分類→ねじGo/No-Go |
| 新規性 | 実工場ねじ品質で古典半教師学習＋物理的なtorque区間処理を検証 |
| 学習 | 半教師ありco-training、ラベル比1–90%比較 |
| データ | 36タップ、7000超threads |
| 性能 | §4.5/Table9:50%ラベル98.20%、90%ラベル98.88%。Co-ForestのRecallは30%ラベル94.38%、90%98.34% |
| 評価条件 | 2class Go/No-Go。回帰平滑化＋window11勾配の拡張dataset、5×2ランダム分割 |
| 分割 | 5×2-fold、instanceを概ね半分にランダム分割しcoating比保持。tap単位holdoutではない |
| 未知条件 | 同一加工条件。未知タップ・被削材・設備の独立評価は未確認 |
| 実装・速度 | 2×AMD EPYC7513、各32core、RAM2TB、GPUなし、Ubuntu22.04.1。Co-Forest test<1ms/foldとの本文記述 |
| 限界・監査上の留意点 | 出力はねじ合否という摩耗proxy。instance splitと平滑化により工具独立/未来情報の再監査が必要。Eq3のprecision=TN/(TN+FP)は通常positive precisionと異なる。 |
| 公開データ・コード | 補足資料にdatasetとtorque図。KEEL公開ソフト使用、全実験設定の再現確認未実施 |

原資料：[出版社・原文](https://link.springer.com/article/10.1007/s00170-025-16491-x) / [DOI](https://doi.org/10.1007/s00170-025-16491-x)。位置：§3.1–3.6;§4.4–4.5/Table9–13;Eq3;Supplementary information。

構成図・判定例への参照：Fig.5:torque、Fig.12:ラベル率と精度、Table9:拡張特徴、Eq3:指標定義。

エビデンス：SS029;SSM029。Claim ID：CS083;CS084;CS085;CS086。確認状態：全文確認（Web本文）。
