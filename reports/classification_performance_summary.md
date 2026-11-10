# 種類分類の性能値まとめと調査範囲の評価

基準日：2026-11-11。工具摩耗15本と工業欠陥38本、計53本の比較表掲載論文について、指標名だけでなく報告値とその読み方を抽出した。主比較は工具9本・工業28本の計37本。保留7本、関連9本を別区分で残す。元の広域工具研究59本のうち、量・寿命・程度だけを扱う対象外研究はこのまとめに戻していない。

[精度一覧Excel](../outputs/classification_performance_summary.xlsx)／[CSV](../outputs/classification_performance_summary.csv)。Excelは数値を読みやすい左側に配置し、原語クラス・評価分割・出典と根拠IDを右側に保持した。代表値は対応する指標・条件の値で、論文の最高値を一律に選んだものではない。表全体の平均やランキングは作成しない。

## 結果をどう読むか

工具摩耗では、通常テストの高い数字だけでなく、独立工具の結果と種類別の見逃しを見る必要がある。Wuの96.20%はクラス平均Precision（著者AP）であり、一律にAccuracyと呼ばない。SinghのViTは通常97.50%に対して独立インサート・別照明では96.25%だった。Ahangarの元3種類モデルはAccuracy70.5%でも凝着・複合を全件見逃し、2群に再定義したモデルはRecall65.5%、Precision96.2%を報告する。クラス集合としきい値が変わっている。

工業分野では、同じ「精度」でも問題設定による差が大きい。正解PCB領域を切り出したCLIP-VPTはAccuracy99.0%だが、工業画像の欠陥種類を四択で答えるMMADのGPT-4oは65.80%。これをモデル性能の直接順位にはできない。太陽電池の多ラベル課題では、ViT-S＋GDIのmacro-F1は0.5965、全ラベル一致は0.3883と、単一ラベル分類と異なる難しさが見える。各根拠は以下の該当行に付した原著リンクと既存Claim IDで確認できる。

Accuracy＝全体正答率、Precision＝陽性とした予測の的中率、Recall＝該当種類を拾う率。F1はPrecisionとRecallの調和平均で、macro-F1は種類別F1を平均する。MCC、ROC-AUC、Dice、分類mAP、検出mAPも定義が違う。0.99という共通の数字でも置換できない。本文が平均方式を明記していない場合は推測しない。

## 工具摩耗：全15本

| 論文・モデル | 採否 | 指標と実際の成績 | 評価上の注意 |
|---|---|---|---|
| **FT001** [Wu 2019 / ToolWearnet](https://www.mdpi.com/1424-8220/19/18/3817) | 採用 | 平均96.20%。凝着97.27／破損96.35／すくい面95.78／逃げ面95.41%。 | Accuracyや検出mAPと同義にしない。混合摩耗で誤認識。 |
| **FT002** [Singh 2026 / ViT-Large](https://www.mdpi.com/2075-1702/14/6/589) | 採用 | 通常test97.50%（39/40）。独立インサート・別照明96.25%（77/80）。 | 独立試験の方を代表値に表示。80枚という小標本。 |
| **FT003** [Mamledesai 2020 / CNN](https://www.mdpi.com/2076-3417/10/20/7298) | 採用 | 3種類の検証Accuracy 83.75%。 | 独立テストではなくvalidation。後段のGO/NO-GO成績を除外。 |
| **FIA01** [Sun・Yeh 2018 / 画像処理](https://www.mdpi.com/1996-1944/11/10/1977/pdf?version=1539498597) | 採用 | 分類Accuracy・F1の報告なし。20インサートの出力例を評価。 | 出力件数や反復測定の再現性を正答率とみなさない。 |
| **FIA02** [Walk 2020 / VGG16＋GB](https://publikationen.bibliothek.kit.edu/1000099219/56353670) | 採用 | 3-fold CV：逃げ面MCC 0.878、チッピングMCC 0.644。 | MCCはAccuracyではない。チッピングの判別が相対的に弱い。 |
| **FIA03** [Mamledesai 2022 / CNN](https://link.springer.com/article/10.1007/s42452-022-04987-0) | 採用 | 3種類の検証Accuracy 86.52%（89枚）。 | 独立testと工具個体分割は未確認。 |
| **FIA04** [Kumar 2025 / EfficientNet-B0](https://www.sciencedirect.com/science/article/pii/S0278612524002978) | 採用 | 4種類の未見テストAccuracy 94.11%。 | 抄録確認。テスト枚数・工具分割未確認。Singhとデータ非独立の可能性。 |
| **FIA05** [Lakshmaiya 2025 / VGG16・19](https://www.sciencedirect.com/science/article/pii/S2590123025018134) | 採用 | VGG16 Accuracy/F1 98.86%。VGG19 Accuracy 92.3%、F1 92.30%。 | 拡張前の分割未確認。360枚の単純正解数比と98.86%が整合せず集計要確認。 |
| **MM001** [Ahangar 2026 / ResNet18＋XGBoost](https://www.mdpi.com/2673-2688/7/10/400) | 採用 | 2群：Recall65.5%、Precision96.2%、誤警報1.1%、AUC0.928。元3種類：Accuracy70.5%。 | 3種類では凝着20件・複合96件を全件見逃し。2群では両者を一群に統合。 |
| **FIA06** [Yong 2026 / AlexNet系](https://www.researchgate.net/publication/406927055_Tool_Wear_Classification_Based_on_Convolutional_Neural_Network_in_Micro_Drilling) | 保留 | 内部validation99.26%。BUE Recall0.99、Chipping1.00。別例のチッピング4/5。 | 保留：書誌・完全本文未確認。99.26%は外部試験の値ではない。 |
| **MM002** [Yan / Qwen3-VL-8B](https://www.sciencedirect.com/science/article/abs/pii/S0951832026010963) | 保留 | Accuracy93.12%、macro-F1 77.09%。画像単独ResNet18は90.98%／61.79%。 | 保留：2027年巻の先行公開日未確認。モデル構成も異なる比較。 |
| **FA001** [Pan 2026 / MaskLenNet](https://www.mdpi.com/2504-4494/10/8/286) | 関連 | 対応付け済み前景インスタンスのAccuracy96.52%。 | 関連：見逃し・未対応・重複予測を分母に含めない条件付き成績。 |
| **FIA07** [Walk 2023 / U-Net](https://arxiv.org/pdf/2303.13540) | 関連 | Dice平均0.631。逃げ面0.695、チッピング0.244、BUE0.596。pixel accuracy0.977。 | 関連：画素分割。背景の高成績がpixel accuracyに影響。FIA08と同系列。 |
| **FIA08** [Treiss 2021 / U-Net](https://publikationen.bibliothek.kit.edu/1000124315/89528219) | 関連 | Dice平均0.631、チッピング0.244。pixel accuracy0.977。 | 関連：画素分割。FIA07と同じ213画像系列・基準成績。独立実証でない。 |
| **FIA09** [Marciniak 2026 / YOLO12s＋U-Net](https://link.springer.com/article/10.1007/s10845-026-02944-x) | 関連 | 分割F1 0.886±0.004。画像単位の種類分類Accuracyは未確認。 | 関連：検出・分割の方式。摩耗量MAEは対象外として要約から除いた。 |

## 工業欠陥：主比較28本

| 論文・モデル | 採否 | 指標と実際の成績 | 評価上の注意 |
|---|---|---|---|
| **IT001** [CNN–Transformer / 鋼板6種類](https://www.mdpi.com/2079-9292/11/8/1200) | 採用 | Accuracy99.17%、Precision99.21%、Recall/F1 99.17%（10実験平均）。 | NEUの学習80%条件。未知工場の性能ではない。 |
| **IT002** [ViT / 熱延鋼6種類](https://d-nb.info/1370185472/34) | 採用 | Accuracy96.39%（347/360）。 | 最良設定の値。モデル選択と最終テストの独立性は未確認。 |
| **IT003** [Swin / 金属表面の比較](https://www.mdpi.com/2076-3417/16/6/3022) | 採用 | Swin Acc/F1：NEU100/100%、X-SDD94.9/94.0%、MTDD88.7/76.9%。 | データセットごとに個別学習。100%を未知データへの転移精度と解釈しない。 |
| **IT004** [DINOv2 / SEM匿名欠陥](https://arxiv.org/pdf/2506.03345) | 採用 | Layer1は5枚/種、Layer2は15枚/種の微調整で各90%超。 | 11種類だが名前は匿名。90.00%という点推定ではない。同一ウェハをtrain/test分離。 |
| **IT005** [ViT-Tiny / ウェハ38クラス](https://arxiv.org/pdf/2504.02494) | 採用 | 表のAccuracy98.4%。4複合グループ平均F1 0.9767。 | 抄録は98.4%をF1と表現し不一致。validationと明記。 |
| **IT006** [ViT-Lite＋Mixup / 複合ウェハ](https://globals.ieice.org/en_publications/elex/10.1587/elex.21.20240054/_f) | 採用 | 無mixup比：2複合+17.1、3複合は少なくとも+21.8、4複合+24.7（原著%表記）。 | 絶対精度を未抽出。相対%かポイント差か未確定のため変換しない。 |
| **IT007** [ViT / ウェハ8種類](https://www.nature.com/articles/s41598-026-52885-x_reference.pdf) | 採用 | Accuracy94.83%、macro-F1 92.44%、balanced accuracy92.18%（3,828例）。 | Grad-CAMのIoU0.129は別の位置評価。 |
| **IT008** [LeViT / 布の汚れ12種類](https://pmc.ncbi.nlm.nih.gov/articles/PMC12915276/) | 採用 | F1 99.95±0.40%（拡張データ10-fold）。 | Accuracyではない。元画像単位の独立性未確認、工場外撮影。 |
| **IT009** [ViT-S＋GDI / 太陽電池多ラベル](https://arxiv.org/html/2608.12725v1) | 採用 | 固定閾値0.5：macro-F1 0.5965±0.0119、全ラベル一致0.3883±0.0111。 | 学習20%、4 seed。テストで閾値調整した高い値は別条件。 |
| **IT010** [C-ViT＋HCL / 竹箸多ラベル](https://www.mdpi.com/1424-8220/26/3/812/pdf) | 採用 | 分類mAP94.3%、OF1 90.2%、CF1 88.5%。ViT-Smallは91.6/85.8/81.7%。 | 分類mAPは検出mAPと別。序論93.8%とTable2の94.3%に差。 |
| **IT011** [CNN–Transformer / PVセル8種類](https://www.mdpi.com/1424-8220/26/8/2450) | 採用 | Accuracy95.71%（95%CI95.26–96.16）。VGG19 94.69%、DarkNet53 94.65%。 | 7,508枚の未拡張test。訓練時のみ拡張。 |
| **IV001** [MVREC / AlphaCLIP](https://arxiv.org/html/2412.16897) | 採用 | 1/3/5-shot Accuracy73.7/86.1/89.4%。テキスト0-shot37.4%。 | 欠陥マスクとサポート例を利用。自動発見からの一貫評価ではない。 |
| **IV002** [HypDFS / AlphaCLIP](https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Hyperbolic_Defect_Feature_Synthesis_for_Few-Shot_Defect_Classification_CVPR_2026_paper.pdf) | 採用 | MVTec-FS 1/3/5-shot79.3/89.3/91.7%。MTD59.4/78.6/86.4%。 | 製品別の種類分類。クエリマスクの詳細は未確認。 |
| **IV003** [SEM-CLIP](https://arxiv.org/html/2502.14884) | 採用 | Accuracy83.7%、F1 84.4%。視覚ヘッドのみ83.6%／84.3%。 | この条件での言語追加の差はAccuracy0.1ポイント。平均化方式未確認。 |
| **IV004** [CLIP-VPT / PCB欠陥パッチ](https://www.mdpi.com/2313-433X/11/11/415) | 採用 | CLIP-VPT Acc0.990、macro-F1 0.991、AUPRC0.998。DINOv2-VPT Acc0.988。 | 正解bbox切出し、DeepPCBの人工的欠陥。99%はfew-shotの成績ではない。 |
| **IV005** [VLM-AOI / PCB 30-shot](https://etasr.com/index.php/ETASR/article/download/18859/6787/94416) | 採用 | unseen群Acc82.9%、F1 0.898。seen群Acc61.3%、F1 0.643。 | 提案法はunseen群にも30枚/種を使用。ゼロショットでなく正解ROI条件。 |
| **IV006** [SteelDefectX / LongCLIP](https://arxiv.org/html/2603.21824v2) | 採用 | 25種類：Acc94.45%、mAcc93.66%。T3→T1は93.12%／90.70%。 | 詳細文で学習しクラス名で評価する条件。条件を揃えて比較する。 |
| **IV007** [YOLO-LA / ウェハパターン](https://pmc.ncbi.nlm.nih.gov/articles/PMC12844300/) | 採用 | 言語整合85.75%、同視覚バックボーンのみ83.50%（+2.25ポイント）。 | 光学写真ではなくウェハマップ。None/Backgroundの寄与は不明瞭。 |
| **IM001** [MMAD / GPT-4o等](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d91ffbe9c126765755ff52d36b715683-Abstract-Conference.html) | 採用 | GPT-4o65.80%、Claude3.5-Sonnet60.14%、Gemini1.5-Pro60.12%。 | 4択、標準正常参照1枚。GPT-4o74.92%は7タスク平均で分類精度ではない。 |
| **IM002** [VELM / DDAD＋GPT-4o](https://openaccess.thecvf.com/content/CVPR2025W/VAND/papers/Mokhtar_Detect_Classify_Act_Categorizing_Industrial_Anomalies_with_Multi-Modal_Large_Language_CVPRW_2025_paper.pdf) | 採用 | MVTec-AC Acc84.0%、F1 80.3%。VisA-AC Acc69.6%。 | クラス統合・combined除去。GTマスクoracle87.8%／87.6%は別条件。 |
| **IM003** [FabGPT / SEM Category Q&A](https://doi.org/10.1145/3676536.3676750) | 採用 | FabGPT97.50%、Lisa92.50%、AnomalyGPT75.00%、GPT-4 37.50%。 | 質問数の分母未確認。全QA平均96.86%と区別。 |
| **IM004** [LPBF / GPT-4o-mini＋RAG](https://doi.org/10.1115/DETC2025-168615) | 採用 | 4機種・材条件の平均Acc62.0/62.1/52.1/73.8%。RAGなし61.0/47.1/40.1/52.3%。 | 54画像。種類別有無を平均する多ラベル評価。多クラス単一ラベル正答率と別。 |
| **IM005** [AnomalyR1 / Qwen2.5-VL](https://arxiv.org/html/2504.11914) | 採用 | 種類分類63.56%。base41.07%、SFT41.51%。 | 76.96%は全VQA平均。学習・評価画像IDの詳細は要確認。 |
| **IM006** [OmniAD / Qwen2.5-VL](https://arxiv.org/html/2505.22039) | 採用 | 7B78.80%、3B75.90%。 | 7Bの79.9%は全VQA平均。学習条件がMMAD未学習モデルと異なる。 |
| **IM007** [JUDO / Qwen2.5-VL](https://arxiv.org/html/2605.20284) | 採用 | 74.74%。同表base54.35%、AnomalyR1-7B64.81%。 | 81.20%は全VQA平均。学習データ分離の詳細は未確認。 |
| **IM008** [MAUGPT / Gemma3](https://ojs.aaai.org/index.php/AAAI/article/download/39889/43850) | 採用 | 39.31%。Gemma3-4B37.07%、GPT-4o65.80%。 | 61.41%は全VQA平均。専用モデルというだけで高精度とは限らない。 |
| **IM009** [AnomalyLR / Qwen2.5-VL](https://arxiv.org/html/2609.29457) | 採用 | 7B82.70%、3B82.49%。 | 87.12%／86.00%は全VQA平均。MMAD20/80学習・評価条件。 |
| **IM010** [SiGMA / MLLM組合せ](https://arxiv.org/html/2610.12310) | 採用 | 種類分類79.2%。 | 85.2%は全VQA平均。評価回答による構成選択を含み独立testとは扱えない。 |

## 工業欠陥：保留・関連10本

| 論文・モデル | 採否 | 指標と実際の成績 | 評価上の注意 |
|---|---|---|---|
| **IT012** [PCB / CNN・Transformer比較](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003352160) | 保留 | CNNのConvNeXt-Tiny macro-F1 0.99743。ViT/Swinの絶対値未確認。 | 保留：比較CNNの成績をViTの精度として記載しない。 |
| **IT013** [ViViT / LPBF熱動画](https://www.sciencedirect.com/science/article/pii/S1526612526003907) | 保留 | 種類分類の定量性能は未確認。 | 保留：keyholing等の4ラベルは確認、分割・成績の本文が必要。 |
| **IT014** [PVEL-ViT / 太陽電池](https://www.sciencedirect.com/science/article/abs/pii/S1568494626009427) | 保留 | Accuracy0.9584（95.84%）。 | 保留：種類ラベル・splitを照合できず、採用精度に混ぜない。 |
| **IT015** [DeepSEM-Net](https://www.sciencedirect.com/science/article/abs/pii/S0360835224004224) | 保留 | 5クラスAccuracy97.25%。分割IoU84.40%は別。 | 保留：欠陥クラス名未確認。 |
| **IT016** [低ランク適応 / LPBF](https://www.sciencedirect.com/science/article/abs/pii/S0143816624006614) | 保留 | 元課題93.28%、転移先SLS99.32%。 | 保留：多ラベルの全一致率。クラス名・詳細分割を未確認。 |
| **IT017** [PCBVisionNet / 主提案CNN](https://www.mdpi.com/2079-3197/14/8/168) | 関連 | 主CNNは本文98.27%、Fig.3では98.67%。Transformerの絶対値未取得。 | 関連：主提案はCNN。数値不一致を含みViT成績へ転記しない。 |
| **IV008** [MultiADS / 種類付き画素分割](https://arxiv.org/html/2504.06740) | 関連 | MVTec→VisA画素F1 22.3%、AP24.8%。→MPDD F1 42.8%、AP53.0%。 | 関連：画素の種類分割。画像レベルの分類正答率ではない。 |
| **IV009** [CLIP-MDC](https://link.springer.com/article/10.1007/s10845-025-02773-4) | 関連 | 種類分類の定量Accuracy/F1は未確認。種類名予測例のみ。 | 関連：二値検出AUROCや約6.6msという速度を分類精度の代用にしない。 |
| **IR001** [手袋 / Qwen2.5-VL](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0339867) | 関連 | 青手袋mAP0.63、混合製品0.61。YOLOの青手袋0.62。 | 関連：種類付きbbox検出。画像分類Accuracyは未確認。 |
| **IR002** [YOLO-World / few-shot検出](https://www.mdpi.com/1999-4893/19/4/259) | 関連 | Tile mAP@50 64.9%（学習9インスタンス）。 | 関連：種類付きbbox検出。画像分類Accuracyは未確認。 |

## 論文はだいたい調べられているか

**技術系統と代表事例を広く把握するための重点調査にはなっているが、「該当論文をほぼ網羅した」と言える段階ではない。** 全対象論文数という分母を確定できておらず、「80%・90%を収集済み」といった網羅率は算出できない。論文数の多さと探索の完了は別である。

| 確認軸 | 今回できていること | 残る不足 |
|---|---|---|
| 工具摩耗の対象選別 | 元の59本を種類分類の条件で再選別。画像のみ8・画像＋センサ1を主採用 | 母集団自体が完全ではない。タップ・リーマ・境界摩耗、工具横断の種類分類が不足 |
| 工業分野のモデル | ViT/DINO/Swin、CLIP系、MLLMの代表方式を確認 | 各系統内の全論文探索・全前方後方引用追跡は未完了 |
| 産業の広さ | 鋼材、SEM、ウェハマップ、PCB、太陽電池、繊維、竹製品、積層造形 | 国内機関・日本語学会、包装・食品・自動車等を産業別に網羅していない |
| データの多様性 | 複数データセットを記録し、画像・プロンプト・正解ROI等を区別 | MMAD系7本など同じデータに集中。論文数ほど独立工場実証は多くない |
| 一次資料 | 原著本文・著者版を優先し、資料内位置と数値を対応 | 有料本文、補足資料、元画像単位のsplit等に未確認が残る |
| 探索方法 | 工具フォーカス55行、工業51行の検索・確認ログを保持 | バッチ・直接取得が混在。一部の採否数や時刻が未記録。データベース別の完全な取得母集団なし |
| 探索終了の根拠 | 未発見・保留・対象外を台帳化 | 追加検索で新候補が出なくなる「探索飽和」は未確認 |

つまり、方式の比較と精読対象の選定には使えるが、新規性を主張する先行研究調査や「他に同種論文がない」という判断には追加調査が必要である。今回の性能要約作成では新たな網羅検索をしておらず、既存の採否件数は変更していない。

## 網羅性を高める次の作業

1. 出力を「種類分類」と定義した共通検索式を、Crossref/OpenAlex/IEEE/出版社/J-STAGE/CiNii等の経路別に実行し、取得集合・重複・採否を記録する。一般異常検知や劣化段階分類を混ぜない。
2. 工具の主9本、工業の主28本の前方・後方引用を系統的に追跡する。新規適合候補が出るかを周回ごとに記録する。
3. 保留論文を全文・補足・著者版で再確認し、クラスラベル、種類分類の数値、公開日を確定する。
4. 少数クラスRecall/macro-F1、独立工具・ロット・工場のsplit、同一データの再使用、正解ROIなしの性能を優先して補完する。

「すべての分類論文を調べた」という保証ではなく、この手順の実施と追加発見の推移を網羅性の根拠とする。

## 元資料・監査との対応

- 工具：[種類分類レポート](wear_type_classification_benchmark.md)、[出典・主張・根拠](../evidence/wear_type_classification/)、[元59本の選別](../evidence/wear_type_classification/existing_papers_screening.csv)
- 工業：[種類分類レポート](industrial_defect_classification_benchmark.md)、[監査](industrial_defect_classification_audit.md)、[出典・主張・根拠](../evidence/industrial_defect_classification/)、[カバレッジ](../outputs/industrial_coverage.csv)

今回の要約は既存の根拠付き報告値を再配置し、無次元小数と百分率の表示を明記したもの。原著の実験再現や全論文の再精読を行ったという意味ではない。数値未報告、未抽出、未確認、評価対象外を区別して保持した。
