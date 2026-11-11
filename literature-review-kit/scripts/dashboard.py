"""Render the review ledgers as an offline, read-only Japanese dashboard."""

from html import escape
import json


def render(config, data, status, actions, audit):
    """Return one self-contained HTML page, including request-file drafting."""
    outputs = {}
    for entry in data.get("evidence", []):
        if entry.get("field") in ("labels", "output") and entry.get("value"):
            outputs.setdefault(entry["paper_id"], []).append({key: entry.get(key, "") for key in ("evidence_id", "field", "value", "verification")})
    payload = json.dumps(
        {"config": config, "data": data, "status": status,
         "actions": actions, "audit": audit, "paper_outputs": outputs},
        ensure_ascii=False,
        allow_nan=False,
    )
    for char, replacement in (("&", "\\u0026"), ("<", "\\u003c"),
                              (">", "\\u003e"), ("\u2028", "\\u2028"),
                              ("\u2029", "\\u2029")):
        payload = payload.replace(char, replacement)
    return (HTML.replace("__PAGE_TITLE__", escape(str(config.get("title", "文献調査"))))
            .replace("__STYLES__", CSS)
            .replace("__SCRIPT__", SCRIPT)
            .replace("__PAYLOAD__", payload))


HTML = r'''<!doctype html>
<html lang="ja">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__PAGE_TITLE__ · 調査ダッシュボード</title><style>__STYLES__</style></head>
<body>
<header><div class="wrap"><p class="eyebrow">文献調査ダッシュボード</p>
<h1 id="title">__PAGE_TITLE__</h1><p id="topic"></p><p id="dates" class="meta"></p></div></header>
<nav aria-label="ページ内の移動"><div class="wrap">
<a href="#overview">現状</a><a href="#searches">検索集合</a><a href="#next">次の候補</a>
<a href="#hits">全検索ヒット</a><a href="#papers">論文の確認状態</a>
<a href="#tasks">利用者の指示</a><a href="#requests">指示を下書き</a><a href="#ledgers">補助台帳</a>
</div></nav>
<main class="wrap">
<section id="overview"><h2>現状と残作業</h2><div id="kpis" class="kpis"></div>
<div class="notice">保存、読了、抽出はそれぞれの記録です。保存済みPDFの件数と、本文を確認した件数は別々に表示します。</div>
<details class="scope"><summary>対象範囲・設定</summary><div id="scope"></div></details>
<div id="plan-checks"></div>
<div id="audit"></div><div id="limitations"></div></section>
<section id="searches"><h2>検索集合の取得・判定状況</h2>
<p class="help">検索条件・並び順・索引時点を共有する検索集合ごとの表示です。「残順位」は既知の検索集合内の未取得順位、「予定残」は設定した取得範囲までの残作業です。判定率は取得した重複除外後の論文に対する割合、有望率は判定済み上位結果の実測値です。総数が不明な集合の未発見論文数は推定しません。</p>
<div id="search-table"></div><details><summary>登録した検索式をすべて表示</summary><div id="query-table"></div></details></section>
<section id="next"><h2>次の候補</h2>
<p class="help">候補は調査を進める順番の目安です。スコアは確率、論文の品質、採用判定を表しません。引用数は出典と確認日を論文詳細に記録し、未取得の情報は未知のまま表示します。</p>
<div id="action-table"></div></section>
<section id="hits"><h2>検索ヒット全行</h2><p class="help">同じ論文が複数の検索に出た行も残します。検索結果の行数と、識別した論文数はそれぞれの集計です。</p><div id="hit-table"></div></section>
<section id="papers"><h2>論文ごとの確認状態</h2><p class="help">判定対象・クラス、採否・保存・読了・抽出・引用追跡を同じ行で確認できます。判定対象は抽出済みのlabels/outputの根拠から表示し、未抽出は未確認とします。詳細から書誌、判定理由、根拠、引用数の確認元を閲覧できます。</p><div id="paper-table"></div></section>
<section id="tasks"><h2>利用者の指示と作業状態</h2><div id="task-table"></div></section>
<section id="requests"><h2>追加指示を下書きする</h2>
<div class="notice">下書きは現在の台帳に未反映です。JSONを保存した後、CLIの <code>import-requests</code> で対象プロジェクトに読み込んでください。指示の登録後も、調査を実施し根拠を確認してから作業を完了にします。</div>
<form id="request-form" class="request-form">
<label>指示対象<select id="request-type"><option value="paper">論文</option><option value="query">検索式</option><option value="project">プロジェクト</option></select></label>
<label class="target-field">対象ID<input id="request-target" list="target-options" required placeholder="論文または検索式のID"><datalist id="target-options"></datalist></label>
<label>作業<select id="request-action"></select></label>
<label>優先度<select id="request-priority"><option value="1">1 · 最高</option><option value="2">2 · 高</option><option value="3" selected>3 · 通常</option><option value="4">4 · 低</option><option value="5">5 · 最低</option></select></label>
<label>量・範囲<input id="request-amount" placeholder="例 25、全文、次の1ページ"></label>
<label class="reason-field">理由・追加条件<textarea id="request-reason" rows="2" placeholder="確認したい項目や優先する理由"></textarea></label>
<div class="form-buttons"><button type="submit">下書きに追加</button><button id="download-requests" type="button" class="secondary" disabled>指示JSONを保存</button></div>
</form><p id="request-message" role="status" aria-live="polite"></p><div id="draft-table"></div>
</section>
<section id="ledgers"><h2>補助台帳</h2><p class="help">実行履歴、主張の根拠、引用確認、既知論文の回収試験を必要に応じて開けます。</p><div id="extra-ledgers"></div></section>
<noscript><p class="notice">一覧表示と指示の下書きにはJavaScriptを有効にしてください。このファイルはオフラインで動作します。</p></noscript>
</main><footer class="wrap">この画面は保存時点の台帳です。監査結果は記録の整合性に対する確認であり、全学術文献に対する網羅率ではありません。</footer>
<script id="review-data" type="application/json">__PAYLOAD__</script>
<script>__SCRIPT__</script></body></html>'''


CSS = r'''
:root{color-scheme:light;--navy:#123047;--teal:#087f83;--ink:#1e3344;--muted:#586b78;--line:#d5e1e5;--pale:#eef5f6;--warn:#8b5b14}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:5rem}body{margin:0;background:#f7fafb;color:var(--ink);font:15px/1.65 system-ui,-apple-system,"Segoe UI","Yu Gothic",sans-serif}.wrap{width:min(1580px,94%);margin:auto}header{background:var(--navy);color:#fff;padding:2.2rem 0 1.6rem}.eyebrow{color:#a8dcda;font-size:.85rem;letter-spacing:.08em;margin:0}h1{font-size:clamp(1.5rem,3vw,2.4rem);line-height:1.4;margin:.35rem 0}.meta{font-size:.85rem;color:#c8dadd;margin-bottom:0}nav{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line)}nav .wrap{display:flex;gap:1.3rem;overflow:auto;padding:.8rem 0;white-space:nowrap}a{color:#086b79;text-underline-offset:.18em}nav a{text-decoration:none;font-weight:600;font-size:.9rem}section{padding:1.7rem 0;border-bottom:1px solid var(--line)}h2{font-size:1.3rem;color:var(--navy);margin:0 0 .8rem}h3{font-size:1.05rem}.help{color:var(--muted);max-width:110ch}.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.8rem;margin:1rem 0}.kpi{background:#fff;border:1px solid var(--line);border-top:3px solid var(--teal);border-radius:8px;padding:.85rem 1rem}.kpi strong{font-size:1.8rem;display:block;font-variant-numeric:tabular-nums;line-height:1.35}.kpi span{color:var(--muted);font-size:.85rem}.notice{border-left:4px solid var(--teal);background:#e7f2f2;padding:.8rem 1rem;margin:1rem 0}.alert{border-left-color:#b67d26;background:#fff3dc}.ok{color:#126d59}.muted{color:var(--muted)}.small{font-size:.82rem}.controls{display:flex;flex-wrap:wrap;align-items:flex-end;gap:.6rem;margin:1rem 0 .6rem}.controls label{min-width:160px}.controls .search-label{flex:1;max-width:480px}.result-count{margin-left:auto;font-size:.85rem;color:var(--muted);align-self:center}label{display:flex;flex-direction:column;gap:.25rem;font-size:.85rem;font-weight:600}input,select,textarea,button{font:inherit}input,select,textarea{width:100%;padding:.55rem .65rem;border:1px solid #abc0ca;border-radius:5px;background:#fff;color:var(--ink)}textarea{resize:vertical}button{cursor:pointer;border:1px solid var(--teal);background:var(--teal);color:#fff;border-radius:5px;padding:.5rem .8rem;font-weight:600}button.secondary{color:var(--teal);background:#fff}button:disabled{opacity:.5;cursor:default}button.tiny{padding:.25rem .5rem;white-space:nowrap;font-size:.8rem}a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #d39621;outline-offset:3px}.table-scroll{overflow:auto;border:1px solid var(--line);border-radius:7px;background:#fff;max-height:70vh}table{width:100%;border-collapse:collapse;font-size:.87rem;text-align:left}th{background:#e8f0f3;color:var(--navy);font-weight:700;position:sticky;top:0;z-index:1;border-bottom:2px solid #c3d5dd;padding:.65rem .7rem;white-space:nowrap}td{border-bottom:1px solid #e2eaed;padding:.65rem .7rem;vertical-align:top;min-width:85px;max-width:460px;overflow-wrap:anywhere;white-space:pre-wrap}tr:last-child td{border-bottom:0}tbody tr:hover{background:#f2f8f8}.cell-title{min-width:230px;max-width:430px}.cell-wide{min-width:220px;max-width:460px}.badge{display:inline-block;padding:.1rem .45rem;border-radius:4px;background:#edf1f4;font-size:.78rem;white-space:nowrap}.badge.good{background:#ddf2eb;color:#17634c}.badge.pending{background:#fff0d2;color:#805115}.badge.bad{background:#f8e6e5;color:#933f39}.empty{padding:1rem;color:var(--muted)}details{margin:.7rem 0}summary{cursor:pointer;font-weight:600;color:var(--navy);padding:.45rem 0}.paper-detail{min-width:230px}.paper-detail summary{font-size:.8rem;white-space:nowrap}.field-list{display:grid;grid-template-columns:minmax(100px,150px) minmax(230px,1fr);gap:.2rem .8rem;margin:.4rem 0;min-width:360px;white-space:normal}.field-list dt{font-weight:600;color:var(--muted)}.field-list dd{margin:0;overflow-wrap:anywhere;white-space:pre-wrap}.evidence-item{padding:.65rem 0;border-top:1px solid var(--line);white-space:normal}.request-form{display:grid;grid-template-columns:140px minmax(210px,2fr) minmax(180px,2fr) 130px minmax(150px,1fr);gap:.85rem;background:#fff;border:1px solid var(--line);padding:1rem;border-radius:7px}.reason-field{grid-column:1/-1}.form-buttons{grid-column:1/-1;display:flex;gap:.6rem;flex-wrap:wrap}#request-message{min-height:1.5em}code{font-size:.92em;background:#e4edef;border-radius:3px;padding:.1em .3em}footer{padding:1.7rem 0 2.5rem;color:var(--muted);font-size:.82rem}ul{padding-left:1.3rem}.scope{background:#fff;border:1px solid var(--line);padding:.5rem 1rem;border-radius:7px}
@media(max-width:1000px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.request-form{grid-template-columns:repeat(2,minmax(0,1fr))}.request-form .target-field{grid-column:auto}.table-scroll{max-height:65vh}}@media(max-width:560px){body{font-size:14px}.wrap{width:94%}header{padding:1.4rem 0}.kpi{padding:.7rem}.kpi strong{font-size:1.5rem}.request-form{grid-template-columns:1fr}.controls{display:block}.controls label{margin:.5rem 0}.result-count{display:block;margin:.3rem 0}.field-list{min-width:260px;grid-template-columns:90px 1fr}.table-scroll{max-height:60vh}}@media print{nav,.controls,.tiny,.request-form,#draft-table,#request-message{display:none}header{background:none;color:var(--ink);padding:0}.meta{color:var(--muted)}.wrap{width:100%}section{break-inside:auto}.kpis{grid-template-columns:repeat(4,1fr)}.table-scroll{max-height:none;overflow:visible}th{position:static}table{font-size:8pt}td{min-width:0!important}.notice{background:none}details:not([open]){display:none}a{color:inherit}footer{padding:1rem 0}}
'''


SCRIPT = r'''
"use strict";
(() => {
  const payload = JSON.parse(document.getElementById("review-data").textContent);
  const config = payload.config || {}, data = payload.data || {};
  const status = payload.status || {}, audit = payload.audit || {};
  const rows = name => Array.isArray(data[name]) ? data[name] : [];
  const papers = rows("papers"), queries = rows("queries"), runs = rows("runs");
  const paperMap = new Map(papers.map(row => [row.paper_id, row]));
  const queryMap = new Map(queries.map(row => [row.query_id, row]));
  const runMap = new Map(runs.map(row => [row.run_id, row]));
  const drafts = [];
  const byId = id => document.getElementById(id);
  const text = value => value === null || value === undefined || value === "" ? "未記録" : String(value);
  const el = (tag, value, cls) => {
    const node = document.createElement(tag);
    if (value !== undefined) node.textContent = text(value);
    if (cls) node.className = cls;
    return node;
  };
  const number = value => value !== "" && value !== null && value !== undefined && Number.isFinite(Number(value)) ? Number(value) : null;
  const count = value => number(value) === null ? "不明" : number(value).toLocaleString("ja-JP");
  const pct = (numerator, denominator) => number(numerator) !== null && number(denominator) > 0 ? (100 * number(numerator) / number(denominator)).toFixed(1) + "%" : "未算出";
  const names = {
    unreviewed:"未判定", potential:"有望候補", include:"採用", exclude:"除外", hold:"保留",
    unknown:"不明", metadata:"書誌のみ", abstract:"抄録", online_fulltext:"オンライン全文", blocked:"阻害あり", not_found:"未発見",
    not_attempted:"未試行", saved:"保存済み", failed:"失敗", not_saved:"未保存",
    not_started:"未着手", partial_text:"本文一部", sections:"方法・結果等の該当節", full:"全文確認", partial:"一部完了", complete:"完了", not_applicable:"非該当",
    planned:"計画", active:"実施中", paused:"一時停止", closed:"終了", pending:"待機", in_progress:"実施中", done:"完了", cancelled:"取消",
    success:"成功", diagnostic:"診断", duplicate:"重複", checked:"確認済み", uncertain:"不確か", invalid:"無効",
    verified_identifier:"識別子照合済み", title_match_unverified:"題名一致・未照合", unresolved:"未同定",
    exact:"正確な総数", approximate:"概数", confirmed:"根拠確認済み", yes:"はい", no:"いいえ", predeclared:"事前登録", posthoc:"事後照合", draft:"未反映の下書き", paper:"論文", query:"検索式", project:"プロジェクト", backward:"参考文献", forward:"被引用文献"
  };
  const actionNames = {search_more:"検索を追加取得",screen:"採否を確認",obtain_fulltext:"全文を入手",read_fulltext:"本文を読む",extract:"情報を抽出",trace_backward:"参考文献を追跡",trace_forward:"被引用文献を追跡",verify_identity:"同一性を確認",reconsider:"判定を再検討",custom:"その他の指示"};
  const fieldNames = {paper_id:"論文ID",title:"題名",authors:"著者",year:"年",doi:"DOI",arxiv_id:"arXiv ID",url:"原資料URL",identity_status:"同一性の照合",domain:"対象領域",tags:"タグ",screening:"採否",screening_reason:"採否の理由",screening_evidence:"採否の根拠",access_status:"アクセス",download_status:"保存状態",local_path:"保存パス",reading_status:"確認深度",extraction_status:"抽出",backward_status:"後方引用",forward_status:"前方引用",relevance:"関連性",relevance_reason:"関連性の理由",citation_count:"被引用数",citation_source:"引用数の出典",citation_checked_at:"引用数確認日時",user_priority:"利用者優先度",notes:"注記",updated_at:"更新日時",research_question:"研究課題",method:"手法",results:"結果",evaluation_conditions:"評価条件",limitations:"限界"};
  const label = value => names[value] || text(value);
  Object.assign(fieldNames, {classification_output:"判定対象・クラス",labels:"判定クラス",output:"判定対象・出力"});
  const outputText = paperId => {
    const entries = (payload.paper_outputs || {})[paperId] || [];
    return entries.length ? entries.map(entry => text(entry.value) + "\n確認状態：" + label(entry.verification) + " ／ 根拠：" + text(entry.evidence_id)).join("\n\n") : "未確認（判定対象・クラスの根拠未抽出）";
  };
  const withOutputs = records => records.map(row => ({...row,classification_output:row.target_type === "paper" ? outputText(row.target_id) : "非該当（検索式・プロジェクトへの指示）"}));
  const badge = value => {
    const positive = ["include","saved","sections","full","complete","done","success","checked","confirmed","verified_identifier"];
    const negative = ["failed","invalid","blocked"];
    const cls = positive.includes(value) ? "good" : negative.includes(value) ? "bad" : "pending";
    return el("span", label(value), "badge " + cls);
  };
  const link = value => {
    const string = value === null || value === undefined ? "" : String(value);
    try {
      const url = new URL(string, location.href);
      if (!string || !["https:","http:","file:"].includes(url.protocol)) return el("span", value);
      const node = el("a", string); node.href = url.href; node.target = "_blank"; node.rel = "noopener noreferrer"; return node;
    } catch (_) { return el("span", value); }
  };
  function instructionButton(targetType, targetId, action) {
    const button = el("button", "指示", "tiny secondary"); button.type = "button";
    button.addEventListener("click", () => {
      byId("request-type").value = ["paper","query","project"].includes(targetType) ? targetType : "project";
      updateTargets(); byId("request-target").value = targetId || config.project_id || "";
      if (actionNames[action]) byId("request-action").value = action;
      byId("requests").scrollIntoView({behavior:"smooth"}); byId("request-reason").focus({preventScroll:true});
    }); return button;
  }
  function table(containerId, records, columns, filters) {
    const host = typeof containerId === "string" ? byId(containerId) : containerId;
    host.replaceChildren();
    const controls = el("div", undefined, "controls");
    const searchLabel = el("label", "検索", "search-label");
    const search = document.createElement("input"); search.type = "search"; search.placeholder = "ID・題名・注記など"; searchLabel.append(search);
    const filterLabel = el("label", "状態・区分"); const filter = document.createElement("select"); filter.append(new Option("すべて", ""));
    const choices = new Map();
    for (const row of records) for (const [key, title] of filters) {
      if (row[key] !== undefined && row[key] !== null && row[key] !== "") choices.set(key + "\u001f" + row[key], title + " · " + label(row[key]));
    }
    for (const [key, title] of [...choices.entries()].sort((a,b) => a[1].localeCompare(b[1],"ja"))) filter.append(new Option(title, key));
    filterLabel.append(filter); const tally = el("span", "", "result-count"); tally.setAttribute("aria-live", "polite");
    controls.append(searchLabel, filterLabel, tally); host.append(controls);
    const scroller = el("div", undefined, "table-scroll"); const grid = document.createElement("table");
    const thead = document.createElement("thead"), header = document.createElement("tr");
    columns.forEach(column => {const th = el("th", column.title); th.scope = "col"; header.append(th);}); thead.append(header);
    const tbody = document.createElement("tbody"); grid.append(thead, tbody); scroller.append(grid); host.append(scroller);
    const indexed = records.map(row => ({row, search:JSON.stringify(row).toLocaleLowerCase("ja")}));
    function draw() {
      const term = search.value.trim().toLocaleLowerCase("ja"), chosen = filter.value.split("\u001f");
      const selected = indexed.filter(item => (!term || item.search.includes(term)) && (!filter.value || String(item.row[chosen[0]]) === chosen[1]));
      const fragment = document.createDocumentFragment();
      for (const item of selected) {
        const tr = document.createElement("tr");
        for (const column of columns) {
          const td = el("td", undefined, column.cls); const value = column.cell ? column.cell(item.row) : item.row[column.key];
          td.append(value instanceof Node ? value : document.createTextNode(text(value))); tr.append(td);
        } fragment.append(tr);
      }
      if (!selected.length) {const tr = document.createElement("tr"), td = el("td", "該当する記録はありません。", "empty"); td.colSpan = columns.length; tr.append(td); fragment.append(tr);}
      tbody.replaceChildren(fragment); tally.textContent = selected.length.toLocaleString("ja-JP") + " / " + records.length.toLocaleString("ja-JP") + " 行";
    }
    search.addEventListener("input", draw); filter.addEventListener("change", draw); draw();
  }
  const col = (key, title, cell, cls) => ({key,title,cell,cls});
  const state = (key, title) => col(key,title,row => badge(row[key]));
  const outputColumn = col("classification_output", "判定対象・クラス", undefined, "cell-wide");
  function fieldList(record) {
    const list = el("dl", undefined, "field-list");
    for (const [key, value] of Object.entries(record)) {
      list.append(el("dt", fieldNames[key] || key)); const dd = document.createElement("dd");
      dd.append(key === "url" ? link(value) : document.createTextNode(text(value))); list.append(dd);
    } return list;
  }
  function paperDetails(row) {
    const node = el("details", undefined, "paper-detail"); node.append(el("summary", "書誌・根拠を開く")); node.append(fieldList(row));
    const evidence = rows("evidence").filter(entry => entry.paper_id === row.paper_id);
    node.append(el("h3", "抽出した根拠 " + evidence.length + "件"));
    evidence.forEach(entry => {const box = el("div",undefined,"evidence-item");box.append(fieldList(entry));node.append(box);}); return node;
  }
  byId("title").textContent = text(config.title);
  byId("topic").textContent = config.topic || "";
  byId("dates").textContent = "基準日 " + text(config.as_of) + " ／ 生成日時 " + text(status.generated_at) + " ／ プロジェクト " + text(config.project_id);
  const kpis = [["paper_total","識別した論文"],["screen_unreviewed","採否の未判定"],["download_saved","本文ファイル保存済み"],["read_sections_or_full","該当節・全文を確認"],["extraction_complete","抽出完了"],["user_pending","利用者指示の未完了"],["required_queries_unsearched","必須検索の未実行"]];
  for (const [key,title] of kpis) {const card = el("div",undefined,"kpi");card.append(el("strong", count((status.counts || {})[key])),el("span",title));byId("kpis").append(card);}
  byId("scope").append(fieldList({topic:config.topic || "",...(config.scope || {}),mode:config.mode || "",required_extraction_fields:(config.required_extraction_fields || []).join("、")}));
  const planChecks = Array.isArray(status.plan_checks) ? status.plan_checks : [];
  const planHost = byId("plan-checks");
  planHost.append(el("h3", "今回の計画内の到達判定"));
  if (planChecks.length) {
    const passedCount = planChecks.filter(check => check.passed === true).length;
    planHost.append(el("p", "計画条件 " + passedCount + " / " + planChecks.length + " 項目を達成。"));
    const checkTable = document.createElement("div");
    planHost.append(checkTable);
    const checkRows = planChecks.map(check => ({
      ...check,
      result:check.passed === true ? "達成" : check.passed === false ? "未達" : "未確認"
    }));
    table(checkTable, checkRows, [
      col("label", "計画条件", undefined, "cell-wide"),
      col("result", "到達判定", row => el("span", row.result, "badge " + (row.passed === true ? "good" : "pending"))),
      col("observed", "現在の実数", row => count(row.observed)),
      col("limit", "許容上限", row => count(row.limit)),
      col("unit", "単位", row => row.unit || "")
    ], [["result", "到達判定"]]);
  } else {
    planHost.append(el("p", "計画内の到達判定は未記録です。", "muted"));
  }
  planHost.append(el("p", "全項目の達成は、設定した計画範囲の到達を示します。未発見文献の総数や、全世界の文献に対する網羅性は確認していません。", "help"));
  const auditBlock = el("div",undefined,"notice" + (audit.errors && audit.errors.length ? " alert" : ""));
  auditBlock.append(el("strong", "記録の整合性監査 " + text(audit.status)));
  for (const [kind, list] of [["エラー",audit.errors],["注意",audit.warnings]]) if (Array.isArray(list) && list.length) {
    auditBlock.append(el("p",kind)); const ul = document.createElement("ul"); list.forEach(item => ul.append(el("li", typeof item === "string" ? item : JSON.stringify(item))));auditBlock.append(ul);
  } byId("audit").append(auditBlock);
  if (Array.isArray(status.limitations) && status.limitations.length) {
    byId("limitations").append(el("h3","未確認・調査範囲の制約"));const ul=document.createElement("ul");status.limitations.forEach(item=>ul.append(el("li",item)));byId("limitations").append(ul);
  }
  const searchSets = (status.search_sets || []).map(set => {
    if (number(set.unique_papers) !== null) return set;
    const matchingRuns = new Set(runs.filter(run => run.query_id === set.query_id && run.search_set_id === set.search_set_id).map(run => run.run_id));
    const ids = new Set(rows("hits").filter(hit => matchingRuns.has(hit.run_id) && hit.paper_id).map(hit => hit.paper_id));
    return {...set, unique_papers:matchingRuns.size ? ids.size : null};
  });
  table("search-table", searchSets, [
    col("query_id","検索式ID"),col("search_set_id","集合ID"),col("source","情報源"),col("query_text","検索式",undefined,"cell-wide"),
    col("total_hits","総ヒット数",row => number(row.total_hits) === null ? "不明" : count(row.total_hits) + "（" + label(row.total_kind) + "）"),
    col("retrieved_slots","実取得順位数",row=>count(row.retrieved_slots)),col("unique_papers","取得論文数（重複除外）",row=>count(row.unique_papers)),col("first_missing_rank","最初の未取得順位",row=>count(row.first_missing_rank)),
    col("remaining_slots","残順位数",row=>count(row.remaining_slots)),col("remaining_to_target","予定範囲までの残",row=>count(row.remaining_to_target)),
    col("decided","判定済み／取得論文（判定率）",row=>count(row.decided)+" / "+count(row.unique_papers)+"（"+pct(row.decided,row.unique_papers)+"）"),
    col("positive","有望な結果",row=>count(row.positive)),col("yield_pct","上位結果の有望率",row=>number(row.yield_pct)===null?"未算出":text(row.yield_pct)+"%"),
    col("prospect","見込み",row=>label(row.prospect)),col("notes","注記",undefined,"cell-wide"),col("","指示",row=>instructionButton("query",row.query_id,"search_more"))
  ],[["source","情報源"],["prospect","見込み"],["total_kind","総数の確度"]]);
  table("query-table", queries,[col("query_id","検索式ID"),col("source","情報源"),col("query_text","検索式",undefined,"cell-wide"),state("state","状態"),col("required","必須"),col("planned_limit","予定取得数"),col("sort_order","並び順"),col("coverage_cell","カバレッジ"),col("purpose","目的"),col("notes","注記"),col("","指示",row=>instructionButton("query",row.query_id,"search_more"))],[["state","状態"],["source","情報源"],["required","必須"]]);
  table("action-table",withOutputs(payload.actions || []),[
    col("action_id","候補ID"),col("action","作業",row=>actionNames[row.action]||text(row.action)),col("target_type","対象種別",row=>label(row.target_type)),col("target_id","対象ID"),col("target_title","対象の題名・検索式",row=>row.target_type==="paper"?(paperMap.get(row.target_id)||{}).title:row.target_type==="query"?(queryMap.get(row.target_id)||{}).query_text:config.title,"cell-title"),outputColumn,col("priority","優先度（1が最高）"),col("lane","選定枠"),
    col("score","スコア",row=>number(row.score)===null?"未知":Number(row.score).toFixed(3)),
    col("score_known_weight","既知情報の重み",row=>number(row.score_known_weight)===null?"未知":Number(row.score_known_weight).toFixed(3)),col("score_upper","スコア上限",row=>number(row.score_upper)===null?"未知":Number(row.score_upper).toFixed(3)),
    col("reason","理由",undefined,"cell-wide"),col("amount","量・範囲"),col("","指示",row=>instructionButton(row.target_type,row.target_id,row.action))
  ],[["action","作業"],["lane","選定枠"],["target_type","対象種別"]]);
  const hitRows = rows("hits").map(hit=>{const run=runMap.get(hit.run_id)||{},q=queryMap.get(run.query_id)||{},p=paperMap.get(hit.paper_id)||{};return {...hit,classification_output:outputText(hit.paper_id),query_id:run.query_id || "",search_set_id:run.search_set_id || "",source:q.source || "",run_status:run.status || "",screening:p.screening || "unreviewed",reading_status:p.reading_status || "not_started",extraction_status:p.extraction_status || "not_started"};});
  table("hit-table",hitRows,[col("hit_id","ヒットID"),col("query_id","検索式"),col("search_set_id","集合"),col("source","情報源"),col("run_id","取得実行"),col("rank","順位"),col("paper_id","論文ID"),col("title","検索時の題名",undefined,"cell-title"),outputColumn,state("screening","採否"),state("reading_status","読了"),col("url","出典",row=>link(row.url)),col("","指示",row=>instructionButton("paper",row.paper_id,"screen"))],[["screening","採否"],["reading_status","読了"],["run_status","実行状態"],["source","情報源"]]);
  table("paper-table",papers.map(row=>({...row,classification_output:outputText(row.paper_id)})),[col("paper_id","論文ID"),col("title","題名",undefined,"cell-title"),outputColumn,col("year","年"),state("screening","採否"),state("download_status","保存"),state("reading_status","読了"),state("extraction_status","抽出"),state("backward_status","後方引用"),state("forward_status","前方引用"),state("identity_status","同一性"),col("","詳細",paperDetails),col("","指示",row=>instructionButton("paper",row.paper_id,"read_fulltext"))],[["screening","採否"],["download_status","保存"],["reading_status","読了"],["extraction_status","抽出"],["backward_status","後方引用"],["forward_status","前方引用"],["identity_status","同一性"]]);
  table("task-table",withOutputs(rows("tasks")),[col("task_id","指示ID"),col("action","作業",row=>actionNames[row.action]||row.action),col("target_type","対象種別"),col("target_id","対象ID"),outputColumn,state("status","状態"),col("priority","優先度（1が最高）"),col("amount","量・範囲"),col("reason","理由",undefined,"cell-wide"),col("requested_by","依頼者"),col("created_at","登録日時"),col("completed_at","完了日時"),col("evidence_ref","完了根拠")],[["status","状態"],["action","作業"],["requested_by","依頼者"]]);
  const extraTables=[
    ["runs","検索実行履歴",[["status","状態"],["semantics","意味の確認"],["total_kind","総数の確度"]]],
    ["evidence","主張と出典",[["verification","確認深度"],["field","抽出項目"]]],
    ["citation_checks","引用確認",[["state","状態"],["direction","方向"],["total_kind","総数の確度"]]],
    ["known_items","既知論文の回収試験",[["test_type","試験区分"],["database_indexed","索引確認"]]]
  ];
  for(const[name,title,filters]of extraTables){const details=document.createElement("details");details.append(el("summary",title+"（"+rows(name).length+"行）"));const host=document.createElement("div");details.append(host);byId("extra-ledgers").append(details);const keys=[...new Set(rows(name).flatMap(Object.keys))];table(host,rows(name),keys.map(key=>col(key,fieldNames[key]||key,key==="url"||key==="evidence_url"?row=>link(row[key]):undefined)),filters);}
  for (const [value,title] of Object.entries(actionNames)) byId("request-action").append(new Option(title,value));
  byId("request-action").value="read_fulltext";
  function updateTargets(){
    const type=byId("request-type").value, options=byId("target-options");options.replaceChildren();
    const targets=type==="paper"?papers.map(p=>[p.paper_id,p.title]):type==="query"?queries.map(q=>[q.query_id,q.query_text]):[[config.project_id,config.title]];
    targets.forEach(([id,title])=>{if(id){const option=document.createElement("option");option.value=id;option.label=title||id;options.append(option);}});
    byId("request-target").value=type==="project"?config.project_id||"":"";
  }
  function drawDrafts(){
    table("draft-table",withOutputs(drafts.map(row=>({...row,status:"draft"}))),[col("request_id","下書きID"),col("target_type","対象種別"),col("target_id","対象ID"),outputColumn,col("action","作業",row=>actionNames[row.action]||row.action),col("priority","優先度（1が最高）"),col("amount","量・範囲"),col("reason","理由",undefined,"cell-wide"),state("status","状態"),col("","操作",row=>{const button=el("button","削除","tiny secondary");button.type="button";button.addEventListener("click",()=>{const index=drafts.findIndex(item=>item.request_id===row.request_id);if(index>=0)drafts.splice(index,1);drawDrafts();byId("request-message").textContent="下書きを削除しました。";});return button;})],[["status","状態"],["target_type","対象種別"],["action","作業"]]);
    byId("download-requests").disabled=drafts.length===0;
  }
  byId("request-type").addEventListener("change",updateTargets);
  byId("request-form").addEventListener("submit",event=>{
    event.preventDefault();const type=byId("request-type").value,id=byId("request-target").value.trim();
    const known=type==="paper"?paperMap.has(id):type==="query"?queryMap.has(id):id===config.project_id;
    if(!known){byId("request-message").textContent="この台帳に登録されている対象IDを選択してください。";return;}
    const unique=globalThis.crypto&&typeof globalThis.crypto.randomUUID==="function"?globalThis.crypto.randomUUID():Date.now().toString(36)+"-"+Math.random().toString(36).slice(2);
    drafts.push({request_id:"request-"+unique,action:byId("request-action").value,target_type:type,target_id:id,priority:Number(byId("request-priority").value),amount:byId("request-amount").value.trim(),reason:byId("request-reason").value.trim()});
    drawDrafts();byId("request-message").textContent="下書きに追加しました。台帳へ反映するにはJSON保存後に import-requests を実行してください。";
  });
  byId("download-requests").addEventListener("click",()=>{
    const blob=new Blob([JSON.stringify({requests:drafts},null,2)+"\n"],{type:"application/json;charset=utf-8"});const url=URL.createObjectURL(blob),anchor=document.createElement("a");
    anchor.href=url;anchor.download="review-requests-"+new Date().toISOString().replace(/[:.]/g,"-")+".json";document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    byId("request-message").textContent="保存したJSONを CLI import-requests で読み込んでください。下書きはまだ台帳に未反映です。";
  });
  updateTargets();drawDrafts();
})();
'''
