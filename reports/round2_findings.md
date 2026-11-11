# 引用追跡と保留論文再確認：Round2

調査基準日：2026-11-11。工具の実写から摩耗種類を出力する研究と、工業欠陥種類を出力するTransformer／VLM／MLLM研究を追跡した。摩耗量、寿命、摩耗程度、正常／異常だけの分類は主比較に含めない。

## 更新結果

新規詳細収録は14本。このうち工具2本・工業10本の計12本を主採用し、既存保留FIA06を採用へ更新した。研削フラップホイールと未知SEM欠陥のクラス発見は関連研究として別集計した。

| 範囲 | 詳細表総数 | 主採用 | 保留 | 関連 |
|---|---|---|---|---|
| 工具摩耗 | 18 | 12 | 1 | 5 |
| 工業欠陥 | 49 | 38 | 5 | 6 |

[精度一覧Excel](../outputs/classification_performance_summary.xlsx)／[CSV](../outputs/classification_performance_summary.csv)／[数値の読み方](classification_performance_summary.md)。67行のうち61行に数値の代表指標を格納し、6行は未報告・未抽出・未確認を区別して残した。代表値以外のF1や条件別の値も結果欄に記載した。関連タスクの数値は種類分類Accuracyへ換算していない。

## 新規に詳細収録した研究

| 論文・モデル | 採否 | 種類分類の報告値 | 条件・制約 |
|---|---|---|---|
| [FW2001：HG-XAI: human-guided tool wear identification approach through augmentation of explainable artificial intelligence with machine vision](https://link.springer.com/article/10.1007/s10845-024-02476-2) | 採用 | HG-XAIによる摩耗4種類のAccuracy 93.08%（出版社抄録）。 | 原著抄録の結果。人の介入条件、評価画像数、既存IN718研究との画像重複は未確認。 |
| [FW2002：Improving vision-based tool wear state identification under varying lighting conditions using human guided-explainable AI approach](https://www.sciencedirect.com/science/article/pii/S2213846325001154) | 採用 | L2評価のAccuracy 96%、MCC 0.96、F1-score 0.97。F1の平均化方式は抄録で未確認。 | 照明条件の移行と人の支援を含む。工具・現場を単位とした外部検証かは未確認。 |
| [FW2003：Wear Classification of Abrasive Flap Wheels using a Hierarchical Deep Learning Approach](https://arxiv.org/html/2603.12852) | 関連（主比較外） | 形状 Accuracy 95.4%・F1 0.954（Table 5）。裂け Accuracy 93.8%・F1 0.935（Table 8）。階層全体 Accuracy 87.5%（§5.4、独立9本）。 | 研削工具の変形・裂け分類を境界事例として収録。切削刃の摩耗分類への転用評価は未確認。 |
| [IVT2001：Pre-trained CNN-based TransUNet Model for Mixed-Type Defects in Wafer Maps](https://factory.skku.edu/factory/research.do?articleNo=160425&attachNo=128003&mode=download) | 採用 | 2種類混合の評価2,600マップでAccuracy 0.995、F1 0.995（Table 2／§4.3） | 重なった欠陥領域では個々の分離に失敗し得る。データ全体には3種類以上の混合例もあるが、代表分類値は2種類混合で評価。Fig. 8キャプションはEL+Lを重複記載するため、原語ラベルはTable 3を採用 |
| [IVT2002：Solar Photovoltaic System Fault Classification via Hierarchical Deep Learning with Imbalanced Multi-Class Thermal Dataset](https://www.mdpi.com/1996-1073/19/2/462) | 採用 | 8クラス階層のテストでSwin-T Accuracy 89.48%、macro F1 80.50%、weighted F1 89.43%。同一テストのViT-B/16 77.81%／60.56%、SlantNet 86.15%／73.03%（Accuracy／macro F1） | 正常多数で集計方法によりF1が変わる。Shadowing、Vegetation、Soilingはセル内部損傷以外の運用時外乱。赤外熱画像はEL画像の比較へ直接転用不可 |
| [IVT2003：FAX-Net: An Enhanced ConvNeXt Model with Symmetric Attention and Transformer-FPN for Steel Defect Classification](https://www.mdpi.com/2073-8994/17/8/1313) | 採用 | NEU-CLS 6分類 Accuracy 97.78%、クラス平均F1 97.51%（§4.3 Table 1, Fig. 5） | 単一データセット。Table 1とアブレーション表の一部クラス別precision/recallは丸めまたは記載差があるため、Table 1のF1を収録 |
| [IVL2001：Can Multimodal Large Language Models be Guided to Improve Industrial Anomaly Detection?](https://arxiv.org/html/2501.15795v1) | 採用 | Table 1のDefect Classification AccuracyはMVTec-AD 72.86%、VisA 62.35%。同じQwen2-VL 7Bのベースは68.46%、57.06%。 | MMAD全4データセットとは異なる部分集合。外部知識なしとの比較はTable 2・3の条件を参照。 |
| [IVL2002：Towards Explainable Industrial Anomaly Detection via Knowledge-Guided Latent Reasoning](https://arxiv.org/html/2602.09850v4) | 採用 | v4 Table 1の1-shot種類AccuracyはReason-IAD Qwen3-VL-8B 75.07%、同基盤62.33%。 | 表の種類列を採用。本文に記された総合平均と表の総合平均に差があるため総合平均を比較値に使わない。 |
| [IVL2003：AgentIAD: Agentic Industrial Anomaly Detection via Adaptive Memory Augmentation](https://arxiv.org/html/2512.13671v2) | 採用 | Table 1のDefect Classification AccuracyはAgentIAD 72.73%、Qwen2.5-VL-3B 41.07%、AnomalyR1 63.56%。 | MMAD内部学習を含むため、学習なしで全MMADを評価した結果とは条件が異なる。 |
| [IVL2004：Global Logic and Local Search: Dual-Stream Multimodal In-Context Learning for Verifiable Industrial Anomaly Detection](https://arxiv.org/html/2607.03817) | 採用 | Table 1のCls. Accuracy、Qwen3-VL-8B GLLS 1-shot MVTec 87.7%、VisA 83.5%。0-shot 81.9%、65.2%。同基盤74.2%、61.4%。 | 評価はMMAD-QA部分集合。1-shotと0-shotは正常参照に加えて局所化器も異なる。 |
| [IVL2005：ADOPD: Reference-Privileged On-Policy Distillation for MLLM-Based Industrial Anomaly Detection](https://arxiv.org/html/2608.09789v1) | 採用 | Table 1のzero-shot Defect Classification AccuracyはADOPD 57.03%、同基盤53.90%、同論文で再評価したReason-IAD 73.12%。77.31%は全タスク平均。 | 著者の全タスク平均の改善は種類分類での首位を意味しない。ゼロショットは正常参照0枚を指し、学習にはReal-IADデータを使用。 |
| [IVL2006：EMIT: Enhancing MLLMs for Industrial Anomaly Detection via Difficulty-Aware GRPO](https://arxiv.org/html/2507.21619v1) | 採用 | Table 1の1-shot Defect Classification Accuracy 80.85%。比較Qwen2.5-VL 7B 69.35%、GLM-4.1V-Thinking 9B 72.01%。 | MMAD由来正常例からの説明生成も用いる。完全なドメイン未接触学習ではない。 |
| [IVL2007：InspectorGPT: A Comparative Reasoning Enhanced VLM for Comprehensive Industrial Anomaly Detection](https://arxiv.org/html/2608.29783v1) | 採用 | Table 1のDefect Cls. Accuracy 75.32%。同基盤56.15%。全タスク平均82.38%。 | MMADの内部学習あり。実験表中に異なる学習設定の比較器も明記。 |
| [IVL2008：Open-world scanning electron microscope nano-defect category discovery via self-normal prototypes](https://link.springer.com/content/pdf/10.1007/s44443-026-00893-2.pdf) | 関連 | Table 2の種類分類F1（0–1尺度）はBEOL 0.7825、DEP 0.9695、DPR 0.9411。同順のNMI 0.7226／0.8517／0.9249、ARI 0.8046／0.9282／0.9682。 | 未知出力はクラスタIDで、評価時に正解クラスへ対応付ける。欠陥名をそのまま生成する方式とは出力が異なる。 |

数値は原著の報告であり実験を再現した値ではない。HG-XAIの2本は同じ研究系列で、既存IN718画像との独立性は未確認。新規論文2本を独立した工場実証2件とは数えない。

MLLMのMMAD系では全タスク平均とDefect Classification列を分けた。正常参照1枚の1-shot、MMAD内での学習、別データでの学習、未学習モデルを同じ条件として順位付けしない。SNAP-SEMはHungarian対応付け後のクラス発見を評価するため、既知の摩耗・欠陥名を直接選ぶ閉集合分類とは別に扱った。

## 保留の再確認

- **FIA06は採用へ変更**。[出版社記事](https://semarakilmu.my/index.php/sijaset/article/view/1136)で正式著者順と2026年6月9日の公開を確認した。号の名称はMarch 2026。DOIは記事に記載がなく、内部検証99.26%の主要な分割条件は未確認。出版社PDFの新規解析が完了したという意味ではなく、先に確認した著者版と正式書誌を結び付けた。
- **MM002は保留を維持**。3種類の分類内容と成績は確認しているが、2027年巻と先行公開日は別。基準日までの正確な初出日を確定できていない。
- **IT012–IT016の5本は保留を維持**。出版社、DOI、著者版、機関経路を再探索した。ViViTの4状態名やDeepSEM-NetのSSRN版等は補完したが、種類名・Transformer別の数値・分割などの確認が残る。
- **R0116は本文で領域分割と確認して除外**。種類名の分類精度としてmIoUを使用しない。R0118のGPVTは出力ラベルが未確認。
- HCG-MLLMADは種類分類の独立成績を確認できず除外候補台帳で記録。FabGPTの2026年誌版は既存IM003の関連書誌へ追加し、同一研究を新規論文として二重計上しなかった。

詳細は[取得試行76行](../evidence/round2/retrieval_attempts.csv)、[候補台帳](../evidence/round2/candidates.csv)、[レコード更新履歴](../evidence/round2/record_updates.csv)を参照。403、未発見、抄録のみ、部分本文を区別した。

## 追加探索で分かったこと

工具摩耗は「分類」というタイトルだけでは種類分類を見つけにくい。Wu2019の引用メタデータ191件を一次選別しても、程度分類・量予測・領域分割・一般画像認識の引用が多かった。参考文献に現れた異分野のPiezo論文はWu原文にも実在しており、引用関係だけでは対象適合性を保証しない。

工業欠陥では、画像分類、欠陥名VQA、未知クラス発見、種類付き領域検出が別の評価問題になる。複合クラスを許容しても、単一ラベルAccuracy、多ラベル完全一致、分類F1、検出mAP、領域IoUは区別する。高い数値の多くは特定のデータ・条件で得られ、独立工場への一般化を証明するものではない。

## 次に調べる優先順

1. 今回の新規12本を起点に第2周回を行い、引用先・引用元の未追跡部分を埋める。
2. Round2の保留候補をDOI・版で重複整理し、種類ラベルと性能表の本文を優先取得する。HG-XAI2本の完全本文と、同一画像系列の独立性を確認する。
3. 部分確認にとどまる工業側の前方引用を索引APIまたは学術DBで列挙し、取得ページを記録する。
4. IEEE、J-STAGE、CiNii等のDB内検索、国内機関、タップ・リーマ、複数工具を横断する種類分類、非画像センサ融合を補完する。
5. 検索式の既知論文回収試験と除外候補の独立再査読を行う。現在これらを実施済みとはしていない。

[探索の監査結果](search_process_audit.md)／[再利用できる探索手順](../methods/README.md)／[新規14本の詳細](../details/round2/README.md)。
