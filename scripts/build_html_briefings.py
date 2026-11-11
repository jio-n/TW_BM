"""Build three standalone Japanese HTML briefings from reviewed research records."""
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/html'
GH = 'https://github.com/jio-n/TW_BM/blob/main/'
CSS = (ROOT / 'scripts/html_briefing_style.css').read_text(encoding='utf-8')
JS = (ROOT / 'scripts/html_briefing_interactions.js').read_text(encoding='utf-8')
FILES = [('research_methodology.html', '01 調査方法'),
         ('tool_wear_classification.html', '02 工具摩耗'),
         ('industrial_defect_classification.html', '03 工業欠陥')]


def load(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))


def esc(value):
    if isinstance(value, list):
        value = '; '.join(map(str, value))
    return html.escape(str(value if value is not None else '未確認').replace('。。', '。'), quote=True)


def link(url, label):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


def ref(path, label):
    return link(GH + path, label)


def note(title, text, warning=False):
    return f'<aside class="note{" warning" if warning else ""}"><strong>{title}</strong><p>{text}</p></aside>'


def section(number, ident, title, body, intro=''):
    return f'<section class="section" id="{ident}"><div class="section-number">{number:02d} / {esc(ident)}</div><h2>{title}</h2>' + (f'<p class="section-intro">{intro}</p>' if intro else '') + body + '</section>'


def table(headers, rows, classname=''):
    return '<div class="table-wrap"><table class="' + classname + '"><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def stats(items):
    return '<div class="stats">' + ''.join(f'<div class="stat"><b>{esc(n)}</b><span>{esc(label)}</span><small>{esc(detail)}</small></div>' for n, label, detail in items) + '</div>'


def page(filename, number, title, subtitle, stat_items, navigation, body, accent='#147d77'):
    nav = ''.join(f'<a href="{f}"' + (' aria-current="page"' if f == filename else '') + f'>{label}</a>' for f, label in FILES)
    toc = ''.join(f'<a href="#{ident}">{i+1:02d}　{label}</a>' for i, (ident, label) in enumerate(navigation))
    text = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(subtitle)}"><title>{esc(title.replace("<br>", ""))} | TW Benchmark</title>
<style>{CSS}</style><style>:root{{--accent:{accent}}}</style></head><body>
<a class="skip" href="#main">本文へ移動</a>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="research_methodology.html">TW / RESEARCH BRIEFINGS</a><nav class="suite-nav" aria-label="3つの資料">{nav}</nav><button class="print-button">印刷 / PDF保存</button></div></header>
<div class="wrap"><header class="hero"><div class="eyebrow">RESEARCH BRIEFING {number} / 03</div><h1>{title}</h1><p class="lede">{subtitle}</p><div class="meta"><span class="pill">調査基準日 2026.11.11</span><span class="pill">エビデンスに基づく文献ベンチマーク</span><span class="pill">単体HTML・オフライン閲覧対応</span></div></header>
{stats(stat_items)}<div class="layout"><nav class="toc" aria-label="この資料の目次"><div class="toc-title">CONTENTS</div>{toc}</nav><main id="main">{body}</main></div>
<footer class="footer"><p>TOOL WEAR TECHNOLOGY BENCHMARK<br>資料 {number} / 03 · 2026-11-11版<br>本文・スタイル・操作を単一ファイルに収録。原資料のリンク先はオンライン接続が必要。</p><p>{ref('README.md','GitHub / TW_BM')}<br>数値は著者報告値。実験再現・完全網羅を保証するものではありません。</p></footer></div>
<script>{JS}</script></body></html>'''
    (OUT / filename).write_text(text, encoding='utf-8')


def methodology():
    nav = [('scope','何を調べるか'),('history','これまでの進め方'),('workflow','再利用する手順'),('databases','5サイトの検索実績'),('coverage','網羅性の点検'),('evidence','根拠と性能の管理'),('next','残課題と使い方')]
    body = section(1,'scope','「何の種類か」を出力する研究に絞る',
        '<div class="axis-box"><div><small>INPUT</small><b>画像、または画像を含む入力</b><div class="pill-group"><span>工具実写</span><span>工業画像</span><span>任意のセンサ・プロンプト</span></div></div><div class="arrow">→</div><div><small>OUTPUT</small><b>摩耗・欠陥のカテゴリー名</b><div class="pill-group"><span>逃げ面摩耗</span><span>チッピング</span><span>傷・亀裂</span><span>複合クラスも可</span></div></div></div>' +
        table(['判断軸','採用する課題','区別して管理する課題'],[
            ['出力','種類名の単一ラベル／複数ラベル分類、候補付き種類VQA','量・寿命・程度だけの予測、正常／異常だけの二値判定'],
            ['工具の入力','推論時に工具実写を使用。実写＋センサは別区分','信号のスペクトログラムだけ、正解測定時だけの工具写真'],
            ['工業のモデル','ViT等、VLM由来特徴、MLLMを主構成で分類','比較モデルだけに使う方式を主提案として重複計上しない'],
            ['関連研究','領域検出・分割、未知カテゴリー発見を別表へ','検出mAP・IoUを画像分類Accuracyに置き換えない']
        ]) + note('分類軸は独立している','CNNかViTかという構造、画像のみか画像＋センサかという入力、単一ラベルか複数ラベルかという出力は別の軸。ViTもVLMも深層学習であり、「深層学習対vision」という二分はしない。'))
    history = [
        ('広域調査 → 問いを絞る','商用製品と工具状態研究を広く集めた後、ユーザーの意図に合わせて「摩耗量・寿命」から「摩耗種類の分類」へ再選別。工業欠陥の視覚Transformer／VLM／MLLMへ対象を拡張した。'),
        ('初回重点調査 → 原著の成績を確認','Web横断の一般語・ドメイン指定検索から出版社、著者版、機関リポジトリへ進んだ。工具55行・工業51行の検索／直接確認ログ。各DBの独立した検索集合を全件取得する運用は不足していた。'),
        ('引用追跡 Round2 → 発見経路を台帳化','主要16本×前方・後方の32方向を確認。128実行ログ、279候補発見行、276引用・関連・異版行、76取得試行。16方向は申告した索引集合を全件一次選別、残16方向は部分確認。'),
        ('DB内検索の試行 → 未取得範囲を見える形に','Google Scholar／IEEEの公式画面とJ-STAGE／CiNii／arXivの公式APIを実行。検索・取得順位・候補・意味検証を分離した。48実行ログを残し、追加候補は本文確認待ちに置いた。')]
    body += section(2,'history','実際の調査を、時点ごとに区別する','<div class="timeline">'+''.join(f'<div class="timeline-item"><h3>{t}</h3><p>{v}</p></div>' for t,v in history)+'</div>'+note('仕様に書いたDB名を、検索実績と取り違えない','過去の未実施・未記録を後から「調査済み」へ変更していない。初回、引用追跡、DB検索試行は別の記録であり、ログ行数を足して独立論文数にはしない。')+'<p class="source-line">根拠：'+ref('methods/current_search_process.md','従来の方法')+ref('reports/search_process_audit.md','Round2監査')+'</p>')
    steps=[('問い・採否を固定','入力、出力、モデル、期間、境界事例を定義'),('語群と検索枠を設計','同義語・日本語／英語・広い式／狭い式'),('DBと引用を探索','検索フィールド・順位・前後引用を記録'),('重複と異版を照合','発見経路を保持しDOI・題名・著者を確認'),('題名・抄録で選別','種類／段階／量、実写の有無を切り分け'),('本文で成績を抽出','ラベル・指標・値・分割・図表位置を保存'),('未処理と根拠を監査','未実施・未取得・未判定・根拠抜けを点検'),('差分を公開し再探索','追加候補と不足セルを次の周回へ戻す')]
    body += section(3,'workflow','毎回使える、8段階の探索と確認','<div class="flow">'+''.join(f'<div class="step"><b>{t}</b><span>{v}</span></div>' for t,v in steps)+'</div>'+note('検索語は、全条件を最初から必須にしない','対象語＋課題語の広い式、具体的ラベルを足した式、モデル語を足した式を併用する。必要に応じて語群を一つ外し、用語が異なる研究を補う。複雑な式は単純式と返却題名で意味を確認する。')+'''<pre><code>工具 / 広く：       "tool wear" classification image
工具 / 種類を追加： "tool wear" "chipping" classification image
工業 / ViT：        "defect classification" "vision transformer"
工業 / VLM：        "defect classification" "vision-language"
国内：              工具摩耗 画像 ／ 外観検査 欠陥 分類 Transformer
arXiv API：         all:"tool wear" AND all:classification</code></pre>'''+ '<p class="source-line">これらは今回実行した式の例。各DBの構文・対象フィールドに合わせて変換する。'+ref('methods/database_search_protocol.md','詳細プロトコル')+'</p>')
    dbrows=[['Google Scholar','公式画面・4式','各上位10件、延べ40枠','総数は概数。2ページ目以降未取得。年フィルタ未指定。'],['IEEE Xplore','公式画面・2式成功','工具25/30件、工業ViT25/77件','残5／52件。初回エラーは0件として数えない。'],['J-STAGE','記事API・6式＋追加ページ','延べ66書誌','大半は上位10件。重点候補以外の詳細選別は未完了。'],['CiNii Research','OpenSearch・6式＋追加ページ','延べ60書誌、工業ViT40/51件','残11件。通常画面GETは6式とも空応答。'],['arXiv','公式API・18式／19取得','診断込み120枠、87候補を題名・抄録確認','工具分類8件、ViT分類11件は当該式全件。他は一部ページ。']]
    body += section(4,'databases','5つの論文サイトで、検索経路を実証する',table(['サイト','経路','取得範囲','限界'],dbrows,'wide')+note('48実行 ≠ 48件の論文','通常取得32、失敗7、重複接続確認2、構文診断7。順位台帳366行には重複・診断を含み、それらを除く取得枠は275。関連文献数でも独立論文数でもない。')+'<div class="grid2"><div class="card"><h3>成功応答でも、式の意味を確認</h3><p>arXivの複合式で別分野が多数返ったため、先頭7式を診断扱いにし、単純式で再試験した。HTTP 200だけで有効な検索と判断しない。</p></div><div class="card"><h3>サイトとAPIの違いを記録</h3><p>CiNiiは通常画面GETが空応答でもOpenSearchで取得できた。公式仕様のappid必須と、今回の無指定GET成功は区別して残した。</p></div></div>'+'<p class="source-line">根拠：'+ref('evidence/database_keyword_pilot/search_log.csv','48実行ログ')+ref('evidence/database_keyword_pilot/result_occurrences.csv','取得順位')+ref('reports/database_keyword_search_pilot.md','試行報告')+'</p>')
    coverage=list(csv.DictReader((ROOT/'evidence/database_keyword_pilot/coverage_matrix.csv').open(encoding='utf-8-sig')))
    rows=[]
    for db in ['Google Scholar','IEEE Xplore','J-STAGE','CiNii Research','arXiv']:
        cells=[c for c in coverage if c['platform']==db]
        rows.append([esc(db)]+[f'<span class="status {"hold" if not c["executed_search_ids"] else "accept"}">{"未実施" if not c["executed_search_ids"] else "試行済"}</span><div class="small">{esc(c["retrieval_range"])}</div>' for c in cells])
    body += section(5,'coverage','網羅性は、件数より「残る範囲」で判断する',table(['検索元','工具・実写','工具・実写＋センサ','工業・ViT','工業・VLM/MLLM'],rows,'wide')+note('20の検索枠のうち、専用式が未実施なのは3枠','試行済みの17枠も、全ページ取得・全文確認の完了を意味しない。新規候補が出ているため、探索飽和や完全網羅を宣言できない。',True)+table(['点検','今回確認できたこと','まだ必要なこと'],[
        ['既知論文の回収','arXivの事前seed17件中10件を再発見','未回収seedのDB収録確認。10/17を全論文の再現率としない'],
        ['取得・選別','順位と件数、候補IDを保持','未取得ページ、日本DBの未選別書誌、本文未取得を解消'],
        ['引用追跡','32方向の取得範囲を記録','部分確認16方向、新採用論文からの再帰追跡'],
        ['独立した見直し','担当分担で確認、構造チェックを実施','独立二重スクリーニング・除外候補の抽出再判定'],
        ['終了判断','新候補・保留・未実施を公開','検索枠を埋め、追加探索での新規適合数の推移を確認']
    ])+'<p class="source-line">'+ref('evidence/database_keyword_pilot/coverage_matrix.csv','20セルの実施範囲')+ref('methods/audit_checklist.md','監査チェックリスト')+'</p>')
    body += section(6,'evidence','主張から原資料へ戻れる形にする','<div class="axis-box"><div><small>TRACEABILITY</small><b>論文ID → Claim ID</b></div><div class="arrow">→</div><div><small>PRIMARY SOURCE</small><b>Source ID → 原著の表・図・節</b></div></div>'+table(['必ず対にする情報','理由'],[['指標名＋数値＋単位','Precision、Accuracy、MCC、F1、mAPを混ぜない'],['ラベル＋推論入力＋評価単位','画像全体、正解ROI、領域対応後、4択VQAを区別'],['データ規模＋分割＋未知条件','画像ランダム分割と工具・ロット単位の外部検証は別'],['確認状態＋本文位置＋原資料URL','本文、抄録、検索結果のみを区別。未確認を0や非公開にしない']])+note('自動監査のPASSは、網羅性の合格ではない','検索IDと順位件数、失敗の0件化、診断式の誤った昇格を機械検査する。意味理解、原文の値の正しさ、研究の網羅性は別途レビューが必要。故意の3種の誤りを検出するself-testも実施した。')+'<p class="source-line">'+ref('evidence/database_keyword_pilot/audit_result.json','監査結果')+ref('scripts/build_database_pilot.py','台帳・監査スクリプト')+'</p>')
    sources=[('https://scholar.google.com/intl/en/scholar/help.html','Google Scholar Help'),('https://developer.ieee.org/docs/read/Metadata_API_details','IEEE API仕様'),('https://www.jstage.jst.go.jp/static/files/ja/manual_api.pdf','J-STAGE WebAPI仕様'),('https://support.nii.ac.jp/ja/cir/r_opensearch','CiNii OpenSearch仕様'),('https://info.arxiv.org/help/api/user-manual.html','arXiv API仕様'),('https://www.prisma-statement.org/prisma-search','PRISMA-S'),('https://www.wohlin.eu/ease14.pdf','Wohlin：引用追跡の原著')]
    body += section(7,'next','次の調査へ、そのまま持ち出す','<div class="grid2"><div class="card"><h3>優先して埋める残件</h3><ol><li>IEEE・CiNii・arXiv等の残ページを取得・選別。</li><li>未実施3枠、工具・産業・年代別の追加語を検索。</li><li>新候補と保留の本文から種類ラベル・成績を抽出。</li><li>既知論文の収録確認、除外の独立再判定を実施。</li></ol></div><div class="card"><h3>新テーマでの利用手順</h3><ol><li>仕様テンプレートへ入力・出力・除外条件を書く。</li><li>検索行列と検証用seedを先に固定する。</li><li>検索、順位、候補、本文、根拠を記録する。</li><li>監査し、実施範囲と残件を添えて公開する。</li></ol></div></div><pre><code>python scripts/build_database_pilot.py --self-test\npython scripts/audit_literature_search.py --self-test</code></pre><p class="small">保存済み台帳の構造検査。上のコマンド自体がネット検索を自動実行するものではない。</p><p class="source-line">'+ref('methods/templates/review_protocol_template.md','調査仕様テンプレート')+ref('methods/templates/database_search_matrix.csv','検索枠テンプレート')+ref('methods/README.md','手順書一覧')+'</p><div class="panel"><h3>方法と仕様の参照資料</h3><p class="small">'+ ' ／ '.join(link(u,t) for u,t in sources)+'</p><p class="small">PRISMA-Sは検索の報告指針として参照。完全準拠・完全網羅を認定するものではない。公式仕様確認日：2026-11-11。</p></div>')
    page(FILES[0][0],'01','調べた範囲を、<br>後から確かめられる文献調査へ。','検討してきた調査設計、実際に使った検索経路、残る不足を一つの資料に。検索件数だけでなく、未実施・未取得・未判定を追跡できる仕組みを整理する。',[(5,'学術サイトを試行','公式画面または公式API'),(16,'引用追跡の主要seed','前方・後方の32方向'),(3,'専用検索が未実施の枠','DB×対象の20セル中'),(50,'種類分類の主採用論文','工具12本＋工業38本')],nav,body)


def category(record):
    status = record['status']
    return 'hold' if '保留' in status else 'related' if '関連' in status else 'accept'


def label(cat):
    return {'accept':'採用','hold':'保留','related':'関連'}[cat]


def badge(record):
    cat=category(record)
    return f'<span class="status {cat}">{label(cat)}</span>'


def score(perf):
    value=perf['value']
    if value is None:
        return '未確定'
    if perf['unit'].startswith('%'):
        return f'{value*100:.2f}{perf["unit"]}'
    return f'{value:g}'


def class_description(record):
    original=record.get('labels') or '未確認'
    japanese=record.get('labels_ja')
    content=f'<div class="class-labels">{esc(japanese or original)}</div>'
    if japanese and japanese!=original:
        content+=f'<div class="class-original">原語：{esc(original)}</div>'
    content+=f'<div class="output-task">出力形式：{esc(record.get("task") or "未確認")}</div>'
    if record.get('mixed') and record['mixed']!='未確認':
        content+=f'<div class="class-original">複合状態：{esc(record["mixed"])}</div>'
    return content


def cases(records, performance, ids):
    index={r['id']:r for r in records}
    cards=[]
    for ident in ids:
        r,p=index[ident],performance[ident]
        cards.append(f'<article class="card" data-case="{ident}"><div class="kicker">{esc(ident)} / {esc(r["year"])}</div><h3>{esc(p["name"])}</h3><div class="metric-name">{esc(p["metric"])}</div><div class="metric">{score(p)}</div><p>{esc(p["result"])}</p><div class="case-labels"><strong>判定クラス・出力</strong>{class_description(r)}</div><p class="case-note">{esc(p["note"])}</p><div class="card-links"><a href="#{ident}">条件・根拠を開く</a>{link(r["url"],"原資料")}</div></article>')
    return '<div class="grid2">'+''.join(cards)+'</div>'


def family_chart(records, industrial):
    counts=defaultdict(Counter)
    for r in records:
        counts[r['family_group'] if industrial else r['model_family']][category(r)]+=1
    max_count=max(sum(c.values()) for c in counts.values())
    rows=[]
    for family,c in counts.items():
        bars=''.join(f'<span class="{cat}" style="width:{100*c[cat]/max_count:.3f}%" title="{label(cat)} {c[cat]}本"></span>' for cat in ['accept','hold','related'])
        rows.append(f'<div class="bar-row"><span>{esc(family)}</span><div class="bar" role="img" aria-label="{esc(family)}：採用{c["accept"]}、保留{c["hold"]}、関連{c["related"]}">{bars}</div><strong>{sum(c.values())}</strong></div>')
    return '<div class="panel">'+''.join(rows)+'<div class="legend"><span><i class="accept"></i>採用</span><span><i class="hold"></i>保留</span><span><i class="related"></i>関連</span><span>棒は収録論文数。性能の順位ではありません。</span></div></div>'


def catalogue(data, performance, industrial):
    records=data['records']
    families=sorted({r['family_group'] if industrial else r['model_family'] for r in records})
    inputs=sorted({r.get('input_group',r.get('group')) for r in records})
    options=lambda values: '<option value="">すべて</option>'+''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in values)
    controls=f'''<noscript><p class="nojs">JavaScriptが無効のため絞り込みは使えません。一覧と各論文の詳細はそのまま閲覧できます。</p></noscript>
<form class="filters" onsubmit="return false"><label class="search-label">キーワード<input type="search" aria-label="論文、ラベル、モデルを検索" placeholder="例：chipping、Swin、MMAD、著者名"></label><label>採否<select name="status"><option value="">すべて</option><option value="accept">採用</option><option value="hold">保留</option><option value="related">関連</option></select></label><label>モデル系統<select name="family">{options(families)}</select></label><label>入力<select name="input">{options(inputs)}</select></label><button type="button" id="reset-filters">条件をリセット</button></form><p class="result-count" id="result-count" aria-live="polite">全{len(records)}件</p>'''
    rows=[]
    details=[]
    sources={s['source_id']:s for s in data['sources']}
    claim_links=defaultdict(list)
    for ce in data['claim_evidence']:
        claim_links[ce['claim_id']].append(ce)
    for r in records:
        ident=r['id'];p=performance[ident];cat=category(r)
        family=r['family_group'] if industrial else r['model_family']
        inp=r.get('input_group',r.get('group'))
        search=' '.join(str(v) for v in r.values()).lower()
        rows.append(f'<tr data-paper="{ident}" data-status="{cat}" data-family="{esc(family)}" data-input="{esc(inp)}" data-search="{esc(search)}"><td><span class="paper-id">{ident} · {esc(r["year"])}</span><a class="paper-name" href="#{ident}">{esc(p["name"])}</a><div class="paper-meta">{badge(r)} {esc(r["status"] if r["status"] not in ["採用","主採用","関連","保留"] else "")}</div></td><td>{esc(family)}<div class="paper-meta">{esc(inp)}</div></td><td class="target-classes">{class_description(r)}</td><td><span class="metric-name">{esc(p["metric"])}</span><b class="metric-value">{score(p)}</b><div class="paper-meta">{esc(p["verification"])}</div></td><td><div class="result-text">{esc(p["result"])}</div><div class="condition">{esc(p["note"])}</div></td></tr>')
        field_pairs=[('採用区分',r['status']),('対象',r.get('tool',r.get('product'))),('原語クラス',r['labels']),('日本語ラベル',r.get('labels_ja')),('分類タスク',r['task']),('複合状態の扱い',r.get('mixed')),('推論時入力',r['input']),('プロンプト',r.get('prompt')),('主モデル',r.get('model',r.get('primary_model'))),('モデル系統',family),('最終判定構成',r.get('model_pipeline')),('比較モデル',r.get('baseline_models',r.get('baseline_families'))),('学習・事前学習',r.get('learning')),('事前学習',r.get('pretraining')),('データセット／系列',r.get('dataset',r.get('dataset_family'))),('データ規模',r.get('data',r.get('data_size'))),('分割・評価条件',p['split']),('代表指標の単位・尺度',p['unit']),('報告性能',r['performance']),('クラス別結果',r.get('class_results')),('一般化評価',r.get('generalization')),('技術上の限界',r.get('limitation',r.get('limitations'))),('公開データ・コード',r.get('code_data')),('確認状態',r['verification']),('原資料内の位置',p['locator']),('Source ID',p['source_ids']),('性能のClaim ID',p['claim_ids'])]
        facts='<dl class="fact-grid">'+''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k,v in field_pairs if v is not None)+'</dl>'
        evidence_rows=[]
        for claim in data['claims']:
            if claim.get('entity_id')!=ident:
                continue
            refs=[]
            for ce in claim_links[claim['claim_id']]:
                s=sources.get(ce['source_id'],{})
                source_link=link(s['url'],ce['source_id']) if s.get('url') else esc(ce['source_id'])
                refs.append(source_link+'<br>'+esc(ce.get('locator','未確認')))
            evidence_rows.append([esc(claim['claim_id']),esc(claim.get('field','')),esc(claim.get('claim','')), '<hr>'.join(refs) or '個別台帳を参照'])
        evidence='<details class="evidence"><summary>主張と原資料の対応を確認する（'+str(len(evidence_rows))+'件）</summary>'+table(['Claim ID','項目','記録した主張','原資料・位置'],evidence_rows)+'</details>'
        doi=link('https://doi.org/'+r['doi'],'DOI') if str(r.get('doi','')).startswith('10.') else 'DOI未確認'
        details.append(f'<details class="paper" id="{ident}"><summary><span class="paper-id">{ident} · {esc(r["year"])}</span><span class="summary-title">{esc(r["title"])}</span>{badge(r)}</summary><div class="paper-body"><p class="paper-head">{esc(r["authors"])}<br>{link(r["url"],"原論文／公開版を開く")}　{doi}</p>{facts}{evidence}</div></details>')
    summary=controls+'<div class="table-wrap"><table class="matrix"><thead><tr><th scope="col">論文・採否</th><th scope="col">モデル・入力</th><th scope="col">判定クラス・出力</th><th scope="col">代表指標と報告値</th><th scope="col">結果と解釈上の注意</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div><p class="empty" id="empty" hidden>該当する論文はありません。検索語や絞り込み条件を変更してください。</p>'
    detailed='<div class="details-toolbar"><button data-expand="true">表示中の詳細をすべて開く</button><button data-expand="false">詳細を閉じる</button></div>'+''.join(details)
    return summary,detailed


def research(industrial=False):
    name='industrial_integrated.json' if industrial else 'focused_integrated.json'
    data=load(name);records=data['records']
    perf={r['id']:r for r in load('performance_digest.json')['records']}
    assert all(r['id'] in perf for r in records)
    counts=Counter(category(r) for r in records)
    numeric=sum(perf[r['id']]['value'] is not None for r in records)
    scope='工業欠陥' if industrial else '工具摩耗'
    nav=[('overview','対象と主な結論'),('families','モデル系統の全体像'),('highlights','代表研究と性能'),('comparison','論文・精度一覧'),('details','論文別の詳細と根拠'),('limits','解釈・網羅性・次の課題')]
    if industrial:
        title='工業製品の欠陥を、<br>種類名で分類する。'
        subtitle='視覚Transformer、VLM、MLLMによる欠陥種類分類の研究を比較。鋼材・ウェハ・SEM・PCB・太陽電池などの画像分類と、画像＋言語による種類判定を、入力と評価条件を添えて整理する。'
        overview='<div class="axis-box"><div><small>INPUT</small><b>工業画像 ＋ 任意の参照・言語</b><div class="pill-group"><span>実写・SEM・X線・熱画像</span><span>ROI・参照画像</span><span>テキスト・候補ラベル</span></div></div><div class="arrow">→</div><div><small>OUTPUT</small><b>傷・亀裂・欠陥パターンの種類</b><div class="pill-group"><span>閉集合分類</span><span>multi-label</span><span>欠陥種類VQA</span></div></div></div>'
        overview+=note('主要な到達点','視覚Transformer14本、VLM／VLM由来特徴7本、MLLM17本を主採用。モデルの構造だけでなく、正解ROIの利用、正常参照の枚数、学習データ、出力形式によって課題の難しさが変わる。')
        overview+='<div class="grid2"><div class="card"><h3>画像分類とVQAは条件が違う</h3><p>固定クラスの画像分類、複数欠陥の同時予測、設問ごとに候補が変わる4択VQAを区別する。製品種類の識別や正常／異常だけの判定は主比較の対象外。</p></div><div class="card"><h3>高い総合点が、種類分類の高精度とは限らない</h3><p>MMAD系は複数タスクを持つ。総合平均ではなくDefect Classification列を抽出し、正常参照・学習条件と一緒に記録した。</p></div></div>'
        family_note='VLM由来のCLIP視覚塔だけを使う研究と、画像・言語を生成的に扱うMLLMを分離。CNN＋Transformerのハイブリッドは視覚Transformer群へ整理した。テキスト中心LLM単独の主採用は0本。主採用のうち1本は匿名の欠陥種類IDで、名称との対応が未確認。'
        selected=['IT001','IT009','IV001','IV004','IM001','IVL2005']
        limit_rows=[['指標の混同','Accuracy、macro/weighted F1、分類mAP、全ラベル一致、VQA正答率を区別する。'],['ROI・参照の差','正解bboxや欠陥マスクを使う分類と、自動検出から始める検査を同列にしない。'],['学習の有無','zero-shotが正常参照0枚を指す場合、学習データを使っていないことを意味しない。'],['データの独立性','同一基板・ウェハ・コイル・視点をまたがない分割かを確認する。MMAD内部学習にも注意。'],['関連研究の範囲','未知クラスタIDの発見、領域検出・分割は既知欠陥名の直接分類と別に扱う。'],['保留の範囲','詳細表の保留5本はIT012–IT016。検索候補台帳の全保留数とは異なる。']]
        next_text='未見工場・製品の検証、少数クラスと混合欠陥、正解ROIを使わない一貫評価、学習条件を揃えたVLM／MLLM比較が優先課題。検索で見つかったQRコード、ケーブル、溶接、半導体等の候補は本文確認待ち。'
        report='reports/industrial_defect_classification_benchmark.md';workbook='outputs/industrial_defect_classification_benchmark.xlsx'
    else:
        title='工具の摩耗・損傷を、<br>種類名で分類する。'
        subtitle='逃げ面摩耗、凝着、チッピング、クレータ摩耗などを画像から判定する研究にフォーカス。画像のみと画像＋センサを分け、CNN・視覚Transformer・VLM／MLLMの構成と報告性能を比較する。'
        overview='<div class="axis-box"><div><small>INPUT</small><b>工具の実写画像</b><div class="pill-group"><span>機上撮像</span><span>顕微鏡画像</span><span>別区分：画像＋センサ</span></div></div><div class="arrow">→</div><div><small>OUTPUT</small><b>摩耗・損傷のカテゴリー名</b><div class="pill-group"><span>flank wear</span><span>adhesive wear</span><span>chipping</span><span>複合クラス</span></div></div></div>'
        overview+=note('主比較は12本：画像のみ11本、画像を含む融合1本','CNN系8本、CNN特徴＋従来ML2本、視覚Transformer1本、画像処理・ルール1本。VLM／MLLMの直接候補1本は、基準日前の先行公開日を確定できず保留を維持している。')
        overview+=table(['出力の形','代表例','解釈'],[['4種類から1つ','Wu：凝着／破損／すくい面／逃げ面','共存摩耗を独立クラスにしていない'],['複合状態を1クラス','Singh：Flank+BUE、Flank+Face','任意の複数ラベルを同時に出す方式とは違う'],['種類ごとに独立判定','Walk：逃げ面とチッピングの有無','同じ画像で両方が陽性になり得る'],['種類を2群へ統合','Ahangar：flank 対 adhesive/combined','凝着単独と複合状態を区別する3分類ではない']])
        family_note='入力モダリティとモデル構造は別軸。画像＋センサを使うだけではMLLMにならない。関連5本には種類付き領域検出・分割に加え、研削工具の形態分類も含む。'
        selected=['FT001','FT002','FIA02','MM001','FIA06','FW2002']
        limit_rows=[['指標の違い','Wuの96.20%はクラス平均Precision。WalkのMCCをAccuracyに換算しない。'],['検証とテスト','FIA06の99.26%は内部validation。Sun・Yehの分類Accuracyは未報告。'],['少数クラスの見逃し','Ahangarの3分類Accuracy70.5%でも凝着20件・複合96件を全件見逃し。平均値だけでは判断できない。'],['研究系列の重複','IN718のCNN・ViT・HG-XAI研究は画像独立性が未確認。独立工場実証の件数として数えない。'],['保留の理由','Yan/MM002は内容・数値を確認しているが、2027年巻と基準日前公開日の確認を分けている。'],['ラベルの意味','flankは逃げ面。BUE、adhesion、rake face、crater、chipping、fractureを根拠なく同一視しない。']]
        next_text='複数工具・撮像条件をまたぐ種類分類、少数の凝着・チッピング、任意の複合摩耗、画像＋センサの公平比較を優先する。TEA-netやBandaらの候補は、画像入力と種類ラベル・成績の本文確認を待っている。'
        report='reports/wear_type_classification_benchmark.md';workbook='outputs/wear_type_classification_benchmark.xlsx'
    body=section(1,'overview','対象と、今回確認できたこと',overview+'<p class="source-line">根拠：'+ref(report,'分類ベンチマーク')+ref('reports/round2_findings.md','引用追跡による更新')+'</p>')
    body+=section(2,'families','主モデルの構成で分類する',family_chart(records,industrial)+f'<p class="source-line">{esc(family_note)}</p>')
    body+=section(3,'highlights','代表研究を、条件付きの数値で読む',cases(records,perf,selected),intro='方式と評価上の論点が異なる研究を選んだ。掲載順は性能順位ではなく、異なる指標を直接比較するものではない。')
    summary,details=catalogue(data,perf,industrial)
    body+=section(4,'comparison','全収録論文の性能一覧',note('数値を並べても、一律の精度ランキングにはしない','代表値には対応する指標を表示。判定クラス欄には原語・確認済みの日本語ラベルと出力形式を併記し、複合クラス、独立二値判定、質問ごとに選択肢が変わるVQAを区別する。ラベルの例示・一部確認・未確認という制約も保持した。結果欄には他の報告値、注意欄には条件差を残した。「未確定」は未報告・未抽出・未確認等を含むため、論文詳細で理由を確認する。')+summary,intro='採否・モデル系統・入力で絞り込み、判定クラスと性能を同じ行で確認できる。論文名から詳細を開ける。保留と関連の数値は主採用研究とは区別する。')
    body+=section(5,'details','ラベル、モデル、分割、根拠を確認する',details,intro='各論文を開くと、原語ラベル・実数性能・評価分割・制約・原資料へのリンクを確認できる。さらに主張とSource IDの対応を展開できる。')
    body+=section(6,'limits','比較の限界と、次の調査',table(['注意点','読み方'],limit_rows)+note('網羅探索は継続中','5つの論文サイトで検索を試行したが、20検索枠中3枠は専用式未実施で、多くの未取得ページ・未判定候補が残る。新候補は今回の詳細表へ未検証のまま追加していない。',True)+f'<div class="panel"><h3>次に確認すること</h3><p>{next_text}</p><p class="source-line"><a href="research_methodology.html">調査方法のHTMLへ</a>'+ref('reports/database_keyword_search_pilot.md','最新DB検索の実施範囲')+ref('evidence/database_keyword_pilot/followup_queue.csv','本文確認待ち候補')+'</p></div><p class="source-line">再利用用：'+ref(workbook,'専用Excel')+ref('outputs/classification_performance_summary.xlsx','指標・実数・条件の精度一覧')+ref('data/'+name,'構造化データ')+'</p>')
    page(FILES[2 if industrial else 1][0],'03' if industrial else '02',title,subtitle,[(len(records),'詳細収録',f'採用{counts["accept"]}・保留{counts["hold"]}・関連{counts["related"]}'),(counts['accept'],'主比較に採用','工具・工場の独立実証数ではない'),(counts['hold'],'詳細表の保留','検索候補台帳の保留数とは別'),(numeric,'数値を確認した収録行',f'{len(records)-numeric}行は未報告・未抽出・未確認等')],nav,body,'#326d96' if industrial else '#a1662d')


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    methodology()
    research()
    research(True)
    print(json.dumps({p.name:p.stat().st_size for p in OUT.glob('*.html')},ensure_ascii=False))
