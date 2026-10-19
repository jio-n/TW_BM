import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/academic_sensor.json').read_text(encoding='utf-8'))
papers={p['論文ID']:p for p in data['papers']}
selected=['R0007','R0001','R0013','R0014','R0016','R0017','R0019','R0021','R0029']
figures={'R0007':'抄録のみ。元資料の構成図は未確認。','R0001':'Fig.3: MFSAN全体、Fig.4:非定常encoder、Table A1:27転移task。','R0013':'Fig.2–5:構成、Table7:9工具比較、Fig.10:PHM2010。','R0014':'著者公開コード https://github.com/tvhahn/ml-tool-wear のnotebookに再現図。本文図番号は未確認。','R0016':'Fig.1:全体、Fig.3:GNN、Fig.4–5:未ラベル/有ラベル学習、Fig.13:PHM2010比較。','R0017':'出版社追加Table10:計算時間、Fig.13:機械ごとの特徴分布。プレプリントは同一研究の https://arxiv.org/abs/2412.19950 。','R0019':'先行公開抄録のみ。構成図・表番号は未確認。','R0021':'Fig.1–2:network/全体、Fig.10:PG-MGAF、Table6:モデル比較。','R0029':'Fig.5:torque、Fig.12:ラベル率と精度、Table9:拡張特徴、Eq3:指標定義。'}
text=['# センサ・時系列系の代表論文詳細','', '調査基準日：2026-10-20。著作権図版は転載せず、原資料の図表位置を参照する。原著の実験設定が異なる数値を順位付けしない。確認状態は各シートで区別する。','', '| ID | 系統 | 論文 | 確認状態 |','|---|---|---|---|']
for ident in selected:
 p=papers[ident];text.append(f"| {ident} | {p['主カテゴリ']} | [{p['論文タイトル（日本語訳）']}]({p['DOIリンク']}) | {p['確認状況（全文／抄録のみ等）']} |")
for ident in selected:
 p=papers[ident]
 text += ['',f"## {ident} — {p['論文タイトル（日本語訳）']}",'',f"{p['発表年']} / {p['著者']} / {p['掲載誌・国際会議']}",'',p['研究概要（100〜200字程度）'],'','| 項目 | 確認内容 |','|---|---|']
 for label,key in [('対象工具・加工','対象工具'),('加工法・被削材','対象加工法'),('入力','入力データ'),('出力','判定対象の摩耗種類・指標'),('モデル','具体的なモデル・手法'),('処理フロー','モデルアーキテクチャ'),('新規性','提案手法の技術的新規性'),('学習','学習方式'),('データ','データ規模'),('性能','判定精度・性能'),('評価条件','評価データの規模・クラス数'),('分割','学習・検証・テストの分割方法'),('未知条件','未知の工具・加工条件での評価有無'),('実装・速度','推論時間・計算環境'),('限界・監査上の留意点','技術的な限界'),('公開データ・コード','データ・コード公開有無')]:
  val=p[key]+(' / '+p['被削材'] if key=='対象加工法' else '')
  text.append(f'| {label} | {val} |')
 text+=['',f"原資料：[出版社・原文]({p['論文URL']}) / [DOI]({p['DOIリンク']})。位置：{p['参照ページ・表・図番号']}。",'',f"構成図・判定例への参照：{figures[ident]}",'',f"エビデンス：{p['エビデンスID']}。Claim ID：{p['Claim ID']}。確認状態：{p['確認状況（全文／抄録のみ等）']}。"]
(ROOT/'details').mkdir(exist_ok=True)
(ROOT/'details/papers_sensor.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
print('Wrote 9 representative sensor-paper sheets.')
