# 3つのHTML資料：作成と品質確認

作成日：2026-11-11。調査方法、工具摩耗種類分類、工業欠陥種類分類を独立した3ファイルへ整理した。新規の論文採用・性能値変更はない。

| 資料 | 保存先 | 収録内容 |
|---|---|---|
| 調査方法 | `outputs/html/research_methodology.html` | 検討経緯、初回・引用追跡・5DB検索、再利用手順、監査、残課題 |
| 工具摩耗 | `outputs/html/tool_wear_classification.html` | 18件＝採用12・保留1・関連5。数値あり17行 |
| 工業欠陥 | `outputs/html/industrial_defect_classification.html` | 49件＝採用38・保留5・関連6。数値あり44行 |

## 内容と構造の確認

最新のfocused/industrial統合JSONとperformance_digestから生成。ID・採否・原語ラベル・著者・性能文・確認状態を67件すべて元データと照合した。百分率の小数尺度と「%超」の限定、MCC/F1/Diceの尺度を保持。HTML IDの一意性、内部アンカー、同梱HTMLリンク、GitHub参照先のリポジトリ内実在、外部描画依存がないことを検査し、全3ファイルPASS・エラー0。JavaScriptのNode構文検査も通過した。

[機械検査の記録](../evidence/html_qa/validation.json)。リンク先論文の全件HTTP再取得は行っていないため、現在の外部サイトの到達性を保証する検査ではない。

本文の二重句点のみ表示時に整形し、元データは維持。FIA06採用への更新、MM002保留、研削工具を含む関連5件を反映。方法資料は最新DBパイロットを含む。工業の旧51検索ログを現時点の総数へ転記せず、古いHCG-MLLMAD候補保留は詳細49件に混入させていない。

## 表示検証の制約

一時HTTPサーバーからの表示を試みたが、IABからlocalhostへ接続できなかった。file URLでの直接表示はブラウザURLポリシーで拒否された。制限を迂回せず、一時サーバーを停止した。

デスクトップ・モバイル幅でのスクリーンショット、絞り込みのブラウザ実操作、印刷ページ割付は未検証。レスポンシブ・印刷CSSは実装済みだが、実機確認済みとは表記しない。構造検査PASSと表示検証の完了は別である。

## 利用・再生成

HTMLを保存してブラウザで開く。比較表は静的HTMLなのでJavaScriptなしでも全件を読める。絞り込みと印刷時の詳細展開にはJavaScriptを使用。原資料URLにはネット接続が必要。3ファイルを同じフォルダへ置くと相互ナビゲーションも利用できる。

```text
python scripts/build_html_briefings.py
python scripts/verify_html_briefings.py
node --check scripts/html_briefing_interactions.js
```

生成はPython標準ライブラリ、構造検査にはlxmlを利用。閲覧時に依存パッケージやHTTPサーバーは不要。
