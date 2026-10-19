# 国内代表製品の詳細シート

調査基準日：2026-10-20。国内分担では19名称を候補として確認し、11製品・系列を比較表に採用した。AIツールソムリエは既存ツールソムリエを基にした研究実証機/機能名称として統合し、独立販売製品として件数を加算しない。MULTI INTELLIGENCEの系列も一行に統合した。販売終了製品は区別する。

## 1. P0001 TOOL COLLAGE — 画像取得とAI刃先検出

| 項目 | 確認内容 |
|---|---|
| 提供 | 単体購入可能。TOOL SOMMELIERの管理系と連携 |
| 対象・入出力 | エンドミル、ドリル、チップの刃先画像 → 欠け・摩耗の自動検出と目視確認用画像 |
| モデル | 販売版の具体名は未確認。共同特許の構成例とは分ける |
| 性能・制約 | 公式FAQはφ2mm以上、変位量依存とする。商用版の検出率、VB測定誤差、母数は未確認 |
| 実装 | 機外撮像。導入時の工具仕様・撮像条件・判定基準の確認が必要 |
| Claim | CJP001–CJP006 |

[公式製品・FAQ](https://mori-machinery.com/product/tool-sommelier)、[共同特許JP7548520B1](https://patents.google.com/patent/JP7548520B1/ja)。

共同特許の実施形態1、図5A–Dは上面・斜め・外周・すくい面の方向別モデルM1–M4を示す。EfficientDetは構成例として示され、YOLO/R-CNN/SSDおよびU-Net/FCN/SegNetは代替可能な方式として列挙される。図7は反転画像も使うTTAを示す。実施形態2、図9–10BにはTOOL COLLAGEの名称が現れる。しかし、現行販売版がこの実施例のモデルを採用したという仕様書は未取得であり、具体モデルの確度はBとする。原資料の図はリンク先を参照し、転載しない。

岡山大学[関連論文 DOI:10.1299/transjsme.24-00127](https://doi.org/10.1299/transjsme.24-00127)は同撮像装置を研究設備として使う。研究のYOLO切出し、PatchCore異常検知、EfficientNetによる電流画像分類を、撮像装置の販売版内蔵モデルと読み替えてはいけない。

## 2. P0002 TOOL SOMMELIER／AIツールソムリエ — 管理製品と研究機能の関係

| 項目 | 確認内容 |
|---|---|
| 役割 | 自動工具ストッカー、工具情報DB、状態画像を一元管理 |
| AI機能 | 現行メーカーサイトはユーザー毎の学習と欠け・摩耗自動検出を説明 |
| 関連事業 | 2020年8月–2023年2月の共同開発、モリ・岡山大学・両備システムズ |
| 実証値 | 欠陥検出の正答率85%以上、摩耗予測70%以上（2023年研究成果）。商用保証値ではない |
| 未確認 | 商用モデル名、寿命予測の現行搭載範囲、学習データと評価分割、独立AI版SKU |
| Claim | CJP007–CJP012 |

[2023年共同発表](https://www.okayama-u.ac.jp/up_load_files/press_r5/press20230602-1.pdf) pp.2–5は、既存製品を基にAI実証機を開発した経緯と役割分担を示す。欠陥画像処理は両備システムズ、分散学習は岡山大学高橋研究室、工具劣化・摩耗予測は児玉研究室が担当した。[Go-Tech紹介](https://www.chusho.meti.go.jp/sapoin/index.php/cooperation/project/detail/4825)は画像の深層学習、分散学習、電流特徴量を用いた勾配ブースティング＋時系列データマイニングを説明する。これは各研究要素の根拠であり、すべての手法が販売製品に同時搭載された根拠とはしない。

開始年には一次資料内の不整合がある。共同発表p.2は2018年より開発・販売、p.5は2019年から提供と記す。いずれかに断定せず比較表に両記した。2023年資料の将来売上目標は、売上実績や市場規模へ転用しない。

## 3. P0003 OSP-AI加工診断 — CNC内部信号を使う深層学習

| 項目 | 確認内容 |
|---|---|
| 対象 | ドリル加工。現行例にガンドリル |
| 入力 → 出力 | CNC制御情報 → 加工異常度・摩耗可視化・停止退避 |
| 確認済み技法 | NECのRAPID機械学習技術、Deep Learning（2018共同発表で採用明示） |
| 運用 | メーカーが複数加工条件のデータを事前学習した構成を説明 |
| 性能 | 寿命1.4倍になる場合があるとのメーカー効果例。判定Accuracyではない |
| 制約 | CNN/ResNet等の構造、VB量への換算、未知工具評価は未確認 |
| Claim | CJP013–CJP016 |

[オークマ現行製品説明](https://www.okuma.co.jp/smart-factory/osp-suite/osp-ai.php)、[2018年共同発表](https://jpn.nec.com/press/201810/20181029_03.html)「特長と実現技術」「注3」。数値制御と診断が連携し、異常の検出後に工具退避へ直結する点が機外画像方式との大きな実装差である。2018年の採用技術と現在版の内部実装が同一かは追加確認が必要。

## 4. P0004 NC MachiningAID — 特徴量選択と工具寿命学習

| 項目 | 確認内容 |
|---|---|
| 入力 | 三菱電機CNC各軸の加工特徴量、工具使用履歴 |
| 出力 | 工程ごとの劣化予測、交換時期通知。加工異常・作業ミスも別機能 |
| モデル | AI/機械学習、摩耗に対応する特徴量の自動選択。具体学習器未確認 |
| 対象例 | Co-Cr合金人工関節の旋盤加工による摩耗診断 |
| 実用制約 | 工具摩耗の注意・警告はサイクルを停止しない |
| 性能 | 共通ベンチマークのAccuracy、VB誤差は未確認 |
| Claim | CJP017–CJP019 |

[公式機能・事例](https://www.mitsubishielectric.com/fa/products/cnt/cnc/pmerit/iot/nc_machining_aid/)、[国内製品解説](https://www.mitsubishielectric.co.jp/fa/topics/2025/10_cnc/index.html)。磨耗幅を画像から直接測る装置ではなく、加工状態から劣化と交換を診断する。用途と出力単位をそろえず画像VB回帰論文と精度順位を付けることはできない。

先行するP0005 [iQ Monozukuri工作機械工具摩耗診断](https://dl.mitsubishielectric.co.jp/dl/fa/document/catalog/sol/iqmonozukuri/l16091/l16091b.pdf)は独立製品として比較する。公式比較カタログ[SJP012](https://www.mitsubishielectric.co.jp/dl/fa/document/catalog/competencies/l08163/l08163.pdf) p.63には重回帰分析・σ逸脱が示されるが、この手法を新製品NC MachiningAIDに自動継承して記載しない。

## 5. P0006 VIMOA AIモニタリングプラン — 2026年の外付け振動AI

| 項目 | 確認内容 |
|---|---|
| 提供開始 | 2026-05-26、買い切り販売・個別見積 |
| 入力 → 出力 | 3軸振動 → 正常パターンに対する摩耗進行スコア・閾値通知・履歴 |
| モデル | 正常時加工パターンを学習するAI。具体モデル名は未確認 |
| 構成 | 無線センサ＋AI搭載産業用PC、機械工程認識、表示端末 |
| 仕様 | 第2世代22.0kHz、IP67。これらは判定精度を意味しない |
| 制約 | 個別工具範囲、学習必要量、VBとの校正、誤報率を未確認 |
| Claim | CJP023–CJP025 |

[メーカー2026年発表](https://www.kyocera.co.jp/newsroom/news/2026/002998.html)、[現行仕様](https://toolsp.kyocera.com/vimoa/ja/ai/)。従来VIMOA全体のサービス開始年と、AIモニタリングプランの開始年を区別した。後付けや量産常時監視の実装面を比較し、モデルが未確認という理由だけで技術的劣位と判定しない。

## 6. P0011 Komtas — ドリル・リーマに対する特徴量と閾値

| 項目 | 確認内容 |
|---|---|
| 対象 | 技報の専用摩耗監視アプリは鉄/鋳物量産のドリル・リーマ工程 |
| 入力 → 出力 | NC/外部アナログ信号 → 加工区間の特徴量（摩耗度）・閾値発報 |
| 方式 | 平均/標準偏差、周波数処理、品質工学を踏襲した特徴量計算と閾値 |
| 速度 | 1msデータ収集。判定処理の遅延と区別 |
| 導入例 | リーマ工具使用回数を従来比最大76%延長した顧客例 |
| 制約 | 当時、タップ・フライス工程やアルミ合金への専用アプリ拡張は今後の課題 |
| Claim | CJP034–CJP037 |

[日本語メーカー技報](https://www.komatsu.jp/ja/-/media/home/aboutus/innovation/technology/techreport/2022/ja/175-j06.pdf?hash=4A2C23CB71E2F9C14CDCCBB36C6495FF&rev=1924577ebeb34e85ba4f844a864b4005)印刷pp.34–39、図10・14・17・18、[現行製品](https://www.komatsu.com/en-us/products/equipment/machine-tools/dx-solutions/komtas)。

2022年度Vol.68 No.175の[実発行日は2023-03-31](https://www.komatsu.jp/en/aboutus/innovation/technology/techreport)。原資料の年度と発売開始日を混同しない。最大76%は顧客の工具使用回数延長例であり、検出Accuracyや全顧客平均ではない。公式NTCページの「日本のみ」とKomatsu米国ページの「Japan & US」には地域記載差があり、現行販売条件の確認事項として残す。

## 補足：残る国内製品の位置付け

| 製品 | 比較上の注意 |
|---|---|
| P0007 MAZIN切削工具監視AI | モータ電流の独自特徴量から異常/摩耗値を推定。摩耗値の単位・VBとの関係とモデル名は未確認。[公式](https://lp.mazin.tech/cut-tool/cut-tool-02) |
| P0008 RICOH AP-10F/AP-SH05 | 正常振動学習とスコア監視の実在例。ただし2024-10-31販売終了。[公式注記](https://rpc.ricoh.com/products/vibration_monitoring/point) |
| P0009 MULTI INTELLIGENCE | 温度・振動の計測と摩耗判断支援。匿名顧客の温度基準交換例、FFT/RMS解析例を公開。AI構造は未確認。[製品](https://www.yama-kin.co.jp/lp/multi-intelligence/)・[b-series](https://yama-kin.co.jp/products/m-intel/b-series) |
| P0010 イージーツールモニタリング | 正常加工電流を基準とする二段階閾値。基準登録を機械学習と呼ばない。[公式](https://www.dmgmori.co.jp/products/machine/id%3D2693) |

本文は出典の要点を独自に整理した。元図は転載していない。数値の母集団・評価条件・提供時点が不明な箇所を、比較可能な統一精度へ換算していない。

