"""One-time, read-only migration of the legacy tool-wear review into this kit.

Run without arguments from any directory. Existing example output is never replaced.
The import does not search, download, claim full-paper reading, or complete extraction.
"""

import csv
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit, urlunsplit


KIT = Path(__file__).resolve().parents[1]
LEGACY = KIT.parent
DEST = KIT / "examples" / "tool-wear-review"
PILOT = LEGACY / "evidence" / "database_keyword_pilot"


def text(value):
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def load_csv(name):
    with (PILOT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_title(value):
    return re.sub(r"[^\w]", "", text(value).casefold())


def identifiers(row):
    """Use explicit identifiers and primary publisher URLs, never title as proof."""
    doi = text(row.get("doi")).lower()
    urls = [text(row.get(key)) for key in ("url", "source_url", "version_url")]
    if not doi.startswith("10."):
        doi = ""
    for url in urls:
        match = re.search(r"(?:doi\.org/|/article/)(10\.\d{4,9}/[^?#\s]+)", url, re.I)
        if match and not doi:
            doi = unquote(match.group(1)).lower().rstrip("/")
    arxiv = text(row.get("arxiv_id"))
    if arxiv:
        arxiv = re.sub(r"^(?:arxiv:|https?://arxiv\.org/(?:abs|pdf)/)", "", arxiv, flags=re.I)
    for url in urls + ([doi] if doi else []):
        match = re.search(r"(?:arxiv\.org/(?:abs|pdf)/|arxiv[.:/])((?:\d{4}\.\d{4,5}|[a-z-]+/\d{7})(?:v\d+)?)", url, re.I)
        if match:
            arxiv = match.group(1)
    arxiv = re.sub(r"(?:v\d+)?(?:\.pdf)?$", "", arxiv, flags=re.I)
    if arxiv and not re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-z-]+/\d{7})", arxiv, re.I):
        arxiv = ""
    keys = set()
    if doi:
        keys.add("doi:" + doi)
    if arxiv:
        keys.add("arxiv:" + arxiv.lower())
    publishers = ("mdpi.com", "sciencedirect.com", "springer.com", "springeropen.com",
                  "nature.com", "wiley.com", "tandfonline.com", "ieee.org", "jstage.jst.go.jp",
                  "openaccess.thecvf.com", "acm.org", "scientific.net", "frontiersin.org",
                  "iop.org", "sagepub.com", "hindawi.com", "degruyter.com", "aaai.org",
                  "openreview.net")
    for url in urls:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower().removeprefix("www.")
        if any(host == domain or host.endswith("." + domain) for domain in publishers):
            path = unquote(parts.path).rstrip("/")
            # Publisher /pdf and /abs are representations of the same article.
            path = re.sub(r"/(?:pdf|full|abstract)$", "", path)
            path = path.replace("/article/abs/pii/", "/article/pii/")
            keys.add("publisher:" + urlunsplit(("https", host, path, "", "")))
    return keys, doi, arxiv


def screen(status):
    status = text(status)
    if "除外" in status:
        return "exclude", "0"
    if status.startswith(("採用", "主採用")):
        return "include", "3"
    if "保留" in status or "期間外" in status:
        return "hold", ""
    if "関連" in status or "有望" in status:
        return "potential", "2"
    return "unreviewed", ""


def reading(verification):
    value = text(verification)
    if "抜粋" in value or "部分" in value:
        return "partial_text", "online_fulltext", "partial"
    if ("本文" in value or "全文" in value) and "未確認" not in value:
        return "sections", "online_fulltext", "confirmed"
    if "抄録" in value:
        return "abstract", "abstract", "abstract"
    if value:
        return "metadata", "metadata", "unknown"
    return "not_started", "unknown", "unknown"


def local_file(values):
    for value in values:
        value = text(value)
        if not value or value.startswith(("http", "未", "非")):
            continue
        path = Path(value)
        path = path if path.is_absolute() else LEGACY / path
        if path.is_file():
            return Path(os.path.relpath(path.resolve(), DEST)).as_posix()
    return ""


def integer(value):
    value = text(value).replace(",", "")
    return str(int(value)) if re.fullmatch(r"\d+", value) else ""


def publication_year(value):
    match = re.fullmatch(r"(\d{4})(?:-\d{2}(?:-\d{2})?)?", text(value))
    return match.group(1) if match else ""


def main():
    if DEST.exists():
        raise SystemExit(f"Refusing to overwrite existing example: {DEST}")
    schema = json.loads((KIT / "schema.json").read_text(encoding="utf-8"))
    project = json.loads((KIT / "templates" / "project.json").read_text(encoding="utf-8"))
    tables = {name: [] for name in schema["tables"]}
    searches = load_csv("search_log.csv")
    candidates = load_csv("candidates.csv")
    followups = {row["candidate_id"]: row for row in load_csv("followup_queue.csv")}
    occurrences = load_csv("result_occurrences.csv")
    coverage = load_csv("coverage_matrix.csv")
    input_paths = [PILOT / name for name in ("search_log.csv", "candidates.csv", "result_occurrences.csv", "coverage_matrix.csv", "followup_queue.csv")]
    bundles = []
    for name in ("focused_integrated.json", "industrial_integrated.json"):
        path = LEGACY / "data" / name
        bundles.append((path, json.loads(path.read_text(encoding="utf-8"))))
        input_paths.append(path)

    papers, exact, titles = {}, {}, {}
    candidate_map = {}
    serial = 0

    def add_index(paper, keys):
        for key in keys:
            exact.setdefault(key, set()).add(paper["paper_id"])
        title = normalized_title(paper["title"])
        if title:
            titles.setdefault(title, set()).add(paper["paper_id"])

    def create(row, paper_id="", legacy_record=False, domain="", source_rows=()):
        nonlocal serial
        keys, doi, arxiv = identifiers(row)
        if not paper_id:
            serial += 1
            paper_id = f"W{serial:04d}"
            while paper_id in papers:
                serial += 1
                paper_id = f"W{serial:04d}"
        if paper_id in papers:
            raise ValueError(f"Duplicate legacy comparison ID: {paper_id}")
        status = row.get("status") if legacy_record else row.get("decision") or row.get("status")
        screening, relevance = screen(status)
        depth, access, verification = reading(row.get("verification"))
        same_title = sorted(titles.get(normalized_title(row.get("title")), set()))
        identity = "verified_identifier" if keys else "title_match_unverified" if same_title else "unresolved"
        path = local_file([row.get("saved_path")] + [source.get("saved_path") for source in source_rows])
        notes = {
            "legacy_id": row.get("id") or row.get("candidate_id", ""),
            "legacy_status": status, "legacy_verification": row.get("verification", ""),
            "identity_rule": "DOI/arXiv/primary-publisher URL exact; title alone is not verified",
            "possible_title_matches": same_title,
            "legacy_matched_ids_unverified": row.get("matched_existing_ids") or row.get("existing_record_ids", ""),
            "legacy_updated": row.get("updated", ""),
            "legacy_year_or_date": row.get("year", ""),
            "reading_caveat": "legacy本文・全文確認はsections以下として移行。全頁読了は未確認。",
        }
        reason = text(row.get("reason")) or (f"既存比較表の採否: {text(status)}" if legacy_record else "採否未確認")
        paper = dict(paper_id=paper_id, title=text(row.get("title")), authors=text(row.get("authors")),
                     year=publication_year(row.get("year")), doi=doi, arxiv_id=arxiv,
                     url=text(row.get("url") or row.get("source_url")), identity_status=identity,
                     domain=domain or text(row.get("scope")), tags=text(row.get("model_family") or row.get("primary_category")),
                     screening=screening, screening_reason=reason,
                     screening_evidence=text(row.get("locator") or row.get("verification")),
                     access_status=access, download_status="saved" if path else "not_attempted", local_path=path,
                     reading_status=depth, extraction_status="partial" if legacy_record else "not_started",
                     backward_status="not_started", forward_status="not_started", relevance=relevance,
                     relevance_reason=f"{screening}→{relevance}: {reason}" if relevance else "",
                     notes=json.dumps(notes, ensure_ascii=False), updated_at="")
        papers[paper_id] = paper
        add_index(paper, keys)
        return paper_id, verification

    def resolve(row):
        keys, _, _ = identifiers(row)
        matches = set().union(*(exact.get(key, set()) for key in keys)) if keys else set()
        if len(matches) == 1:
            paper_id = next(iter(matches))
            add_index(papers[paper_id], keys)
            return paper_id
        paper_id, _ = create(row)
        if len(matches) > 1:
            papers[paper_id]["identity_status"] = "unresolved"
            papers[paper_id]["notes"] += "\nConflicting exact identifier matches: " + ";".join(sorted(matches))
        return paper_id

    # Comparison IDs and their original detailed extraction remain authoritative.
    for path, bundle in bundles:
        source_index = {source["source_id"]: source for source in bundle.get("sources", [])}
        for row in bundle["records"]:
            ids = row.get("source_ids") or [row.get("source_id", "")]
            ids = ids if isinstance(ids, list) else [ids]
            sources = [source_index[key] for key in ids if key in source_index]
            paper_id, verification = create(row, row["id"], True,
                                            "工具摩耗・損傷種類" if "focused" in path.name else "工業欠陥種類", sources)
            values = {
                "input": row.get("input"),
                "labels": row.get("labels"),
                "model": row.get("model") or row.get("primary_model"),
                "results": row.get("performance"),
                "evaluation_conditions": " | ".join(text(row.get(key)) for key in ("data", "data_size", "dataset", "split", "generalization") if row.get(key)),
                "limitations": row.get("limitation") or row.get("limitations"),
            }
            for field, value in values.items():
                if not text(value):
                    continue
                tables["evidence"].append(dict(
                    evidence_id=f"E{len(tables['evidence']) + 1:05d}", paper_id=paper_id, field=field,
                    value=text(value), unit="", context=json.dumps({"legacy_file": path.relative_to(LEGACY).as_posix(),
                        "source_ids": ids, "legacy_verification": row.get("verification", ""),
                        "task": row.get("task", ""), "metric": row.get("metric") or row.get("metrics", ""),
                        "claim_ids": row.get("claim_ids", ""), "extraction_scope": "legacy field only; not complete"}, ensure_ascii=False),
                    url=text(row.get("url")), locator=text(row.get("locator")), verification=verification))

    # Candidate IDs are discovery aliases, not proof that title matches are identical.
    for row in candidates:
        paper_id = resolve(row)
        candidate_map[row["candidate_id"]] = paper_id
        paper = papers[paper_id]
        paper["notes"] += "\nLegacy candidate: " + json.dumps(row, ensure_ascii=False)
        if row["candidate_id"] in followups:
            paper["notes"] += "\nLegacy automatic follow-up (not a user task): " + json.dumps(followups[row["candidate_id"]], ensure_ascii=False)

    query_map, query_keys = {}, {}
    occurrence_counts = {}
    for hit in occurrences:
        occurrence_counts[hit["search_id"]] = occurrence_counts.get(hit["search_id"], 0) + 1
    cells_by_run = {}
    for cell in coverage:
        for run_id in cell["executed_search_ids"].split(";"):
            if run_id.strip():
                cells_by_run.setdefault(run_id.strip(), []).append(cell["cell_id"])

    for row in searches:
        run_id = row["search_id"]
        source = row.get("platform") or row.get("database") or row.get("provider", "")
        search_field = "field-qualified query" if source == "arXiv" else "legacy field unspecified"
        filters = " | ".join(row.get(key, "") for key in ("filters", "applied_cutoff", "cutoff_filter") if row.get(key))
        sort = " | ".join(row.get(key, "") for key in ("sort_by", "sort_order") if row.get(key))
        if not sort and "関連度" in filters:
            sort = "relevance (legacy stated)"
        key = (source, row["query"], search_field, filters, sort)
        if key not in query_keys:
            query_id = f"Q{len(tables['queries']) + 1:04d}"
            query_keys[key] = query_id
            tables["queries"].append(dict(query_id=query_id, source=source, query_text=row["query"],
                search_field=search_field, filters=filters, sort_order=sort, purpose=row.get("scope") or row.get("target", ""),
                coverage_cell=";".join(cells_by_run.get(run_id, [])), required="true", planned_limit=100,
                priority="", state="active", notes="Imported legacy query; unspecified search field/filter/sort was not reconstructed."))
        query_id = query_keys[key]
        query_map[run_id] = query_id
        state = row.get("execution_state", "")
        status = {"failed": "failed", "diagnostic": "diagnostic", "duplicate_probe": "duplicate"}.get(state, "success")
        semantics = "uncertain"
        if source == "arXiv" and status == "success" and "単純式" in row.get("quality", ""):
            semantics = "checked"
        kind = "approximate" if row.get("total_kind") == "概数" else "unknown"
        total = integer(row.get("total_hits")) if status != "failed" else ""
        if total and kind != "approximate" and (source in ("arXiv", "J-STAGE", "CiNii Research") or row.get("total_kind") == "画面表示値"):
            kind = "exact"
        # Preserve source timestamp, including explicit missing-time annotations.
        executed = row.get("executed_at", "")
        day_match = re.search(r"\d{4}-\d{2}-\d{2}", executed)
        day = day_match.group(0) if day_match else "unknown:" + run_id
        search_set = "SS" + hashlib.sha256(json.dumps([*key, day], ensure_ascii=False).encode()).hexdigest()[:14]
        start = integer(row.get("start") or row.get("start_index"))
        if start:
            start = str(int(start) + 1)
        elif row.get("requested_page") or row.get("page"):
            page = integer(row.get("requested_page") or row.get("page"))
            size = integer(row.get("requested_count") or row.get("max_results"))
            start = str((int(page) - 1) * int(size) + 1) if page and size else "1" if page == "1" else ""
        returned = integer(row.get("returned_count") or row.get("retrieved_count"))
        tables["runs"].append(dict(run_id=run_id, query_id=query_id, search_set_id=search_set,
            executed_at=executed, status=status, semantics=semantics, total_hits=total, total_kind=kind,
            start_rank=start, requested_count=integer(row.get("requested_count") or row.get("max_results")),
            returned_count=returned, next_cursor="", url=row.get("url", ""),
            raw_path=local_file([row.get("raw_path")]),
            notes=json.dumps({"legacy": row, "migrated_hit_rows": occurrence_counts.get(run_id, 0),
                "total_scope": "database-reported count, not independent papers or relevant papers",
                "timestamp_precision": "preserved as recorded; no invented time",
                "count_kind": "exact means displayed/API count, not independently validated index completeness"}, ensure_ascii=False)))

    for query in tables["queries"]:
        runs = [run for run in tables["runs"] if run["query_id"] == query["query_id"]]
        if runs and all(run["status"] == "diagnostic" for run in runs):
            query["required"] = "false"
            query["state"] = "paused"
            query["notes"] += " 診断式として保持。次の探索対象に自動昇格しない"

    for hit in occurrences:
        if hit["search_id"] not in query_map:
            raise ValueError(f"Hit references unknown run: {hit['search_id']}")
        keys, doi, _ = identifiers(hit)
        matches = set().union(*(exact.get(key, set()) for key in keys)) if keys else set()
        if len(matches) == 1:
            paper_id = next(iter(matches))
        else:
            aliases = [candidate_map[key.strip()] for key in hit.get("candidate_id", "").split(";") if key.strip() in candidate_map]
            # Reuse a candidate alias only when its title is exactly the same; it
            # remains unverified unless a separate identifier supports identity.
            aliases = {key for key in aliases if normalized_title(papers[key]["title"]) == normalized_title(hit["title"])}
            if len(aliases) == 1 and not keys:
                paper_id = next(iter(aliases))
            else:
                paper_id = resolve(hit)
        tables["hits"].append(dict(hit_id=f"H{len(tables['hits']) + 1:05d}", run_id=hit["search_id"],
            rank=hit["rank"], paper_id=paper_id, title=hit["title"], url=hit["url"], doi=doi))

    for cell in coverage:
        if cell["executed_search_ids"].strip():
            continue
        query = ('"tool wear" (image OR vision) (sensor OR multimodal OR fusion) (type OR classification)'
                 if cell["domain"] == "工具" else
                 '(industrial OR manufacturing) "defect classification" ("vision language" OR multimodal OR MLLM)')
        tables["queries"].append(dict(query_id=f"Q{len(tables['queries']) + 1:04d}", source=cell["platform"],
            query_text=query, search_field="platform default (proposed; not executed)", filters="", sort_order="",
            purpose=f"{cell['domain']} / {cell['input_scope']} / {cell['model_family']}", coverage_cell=cell["cell_id"],
            required="true", planned_limit=100, priority="", state="planned",
            notes="Proposed query for an unexecuted legacy coverage cell; not a historical search. " + json.dumps(cell, ensure_ascii=False)))

    tables["papers"] = list(papers.values())

    project.update(project_id="tool-wear-review", title="工具摩耗・工業欠陥の種類分類：既存調査の移行例",
        as_of="2026-11-11", topic="工具実写画像・マルチモーダルによる摩耗損傷種類分類と工業欠陥のViT/VLM分類",
        required_extraction_fields=["input", "labels", "model", "results", "evaluation_conditions", "limitations"],
        migration_scope=("既存比較67行とDBキーワードpilotの検索48行・出現366行・候補189行を移行対象とする。"
            "件数は入力snapshotの説明であり独立論文数ではない。DOI/arXiv/出版社URLの厳密一致で統合、題名のみは未検証。"
            "旧候補の生行をnotesに保存し保留・未選別を残す。全文確認はsections以下、抽出はpartialにとどめる。"
            "旧followup_queue99行は自動候補でありpapers.notesに保存。ユーザー明示指示ではないためtasksは空とし、残作業は各状態から提示する。"
            "rawは複製せず実在確認したファイルへ相対参照。引用数は未移行。過去の前後引用調査は別範囲のため移行せずnot_started。"
            "事後的known-item照合は独立回収試験でないためknown_itemsへ移行しない。citation_checks/known_itemsは空。"
            "検索の未知フィールド・未知時刻・未知requested_countは推定しない。未実施3セルの検索式は移行時の提案。"))
    project["scope"] = dict(input="工具の実写画像、画像＋センサ／工業製品の画像（prompt可）", output="名前付き欠陥・摩耗・損傷種類のカテゴリ分類",
        population="工具と工業製品。関連境界・保留も台帳に残す", include=["工具画像の種類分類", "工業欠陥のViT/VLM/MLLM種類分類"],
        exclude=["正常異常だけ", "摩耗段階・VB回帰・寿命だけ", "工具写真でない信号の画像化だけ"],
        period="原則2015年以降、基準日2026-11-11まで。旧比較表の留保を保持", languages=["en", "ja"])
    # Validate all relationships and enums before creating the destination.
    assert len(tables["hits"]) == len(occurrences)
    assert {row["paper_id"] for row in tables["hits"]} <= papers.keys()
    for table, rows in tables.items():
        for row in rows:
            if set(row) - set(schema["tables"][table]):
                raise ValueError(f"Unexpected {table} fields: {set(row) - set(schema['tables'][table])}")
            for field, value in row.items():
                allowed = schema["enums"].get(f"{table}.{field}")
                if allowed and text(value) and value not in allowed:
                    raise ValueError(f"Invalid enum {table}.{field}: {value}")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".tool-wear-import-", dir=DEST.parent))
    try:
        (staging / "tables").mkdir()
        (staging / "history").mkdir()
        (staging / "outputs").mkdir()
        (staging / "project.json").write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for table, columns in schema["tables"].items():
            with (staging / "tables" / f"{table}.csv").open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns)
                writer.writeheader()
                writer.writerows(tables[table])
        # Root engine records the initial checkpoint; avoid inventing its event schema.
        (staging / "history" / "events.jsonl").write_text("", encoding="utf-8")
        if DEST.exists():
            raise FileExistsError(f"Refusing to overwrite existing example: {DEST}")
        staging.rename(DEST)
    except Exception:
        # Keep failed staging output for inspection; never alter an existing example.
        print(f"Import incomplete; staging retained at {staging}")
        raise
    print(json.dumps({"destination": str(DEST), "rows": {key: len(value) for key, value in tables.items()},
        "source_sha256": {path.relative_to(LEGACY).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in input_paths}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
