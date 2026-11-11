"""Export database keyword pilot records and audit provenance, not completeness."""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/database_keyword_pilot'


def read(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8-sig'))


def titlekey(title):
    return ''.join(c for c in title.casefold() if c.isalnum())


def identifiers(row):
    keys = {'title:' + titlekey(row.get('title', ''))}
    doi = str(row.get('doi') or '').lower().removeprefix('https://doi.org/').strip()
    if doi:
        keys.add('doi:' + doi)
    for field in ['url', 'source_url', 'version_url']:
        url = row.get(field) or ''
        if url:
            keys.add('url:' + url.rstrip('/').lower())
        arxiv = re.search(r'arxiv.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', url)
        ieee = re.search(r'ieeexplore.ieee.org/(?:abstract/)?document/(\d+)', url)
        if arxiv:
            keys.add('arxiv:' + arxiv[1])
        if ieee:
            keys.add('ieee:' + ieee[1])
    return keys - {'title:'}


def write_csv(name, rows):
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                          for k, v in row.items()} for row in rows)


def audit(searches, candidates, occurrences):
    errors = []
    search_ids = {s['search_id'] for s in searches}
    counts = Counter(r['search_id'] for r in occurrences)
    if len(search_ids) != len(searches):
        errors.append('duplicate search IDs')
    if len({c['candidate_id'] for c in candidates}) != len(candidates):
        errors.append('duplicate candidate IDs')
    for s in searches:
        sid = s['search_id']
        for field in ['query', 'executed_at', 'platform', 'url', 'result_scope']:
            if not s.get(field):
                errors.append(f'{sid}: missing {field}')
        n = s.get('returned_count')
        if s['execution_state'] == 'failed' and (n is not None or s.get('total_hits') is not None):
            errors.append(f'{sid}: failure encoded as numeric result')
        if n is not None and counts[sid] != n:
            errors.append(f'{sid}: returned {n}, recorded ranks {counts[sid]}')
        if s['execution_state'] == 'diagnostic' and s['coverage_eligible']:
            errors.append(f'{sid}: unvalidated query used as coverage evidence')
    for c in candidates:
        for sid in c['query_ids']:
            if sid not in search_ids:
                errors.append(f'{c["candidate_id"]}: unknown search {sid}')
        if not c.get('title') or not c.get('url') or not c.get('decision'):
            errors.append(f'{c["candidate_id"]}: missing screening provenance')
    for o in occurrences:
        if o['search_id'] not in search_ids:
            errors.append('orphan result occurrence')
    return errors


def main():
    bundles = [read('database_' + p + '_pilot.json') for p in ['root', 'japan', 'arxiv']]
    searches, candidates, occurrences, platforms = [], [], [], []
    existing = read('focused_integrated.json')['records'] + read('industrial_integrated.json')['records']
    for bundle in bundles:
        platforms.extend(bundle['platforms'])
        for s in bundle['searches']:
            s = dict(s)
            sid = s['search_id']
            diagnostic = sid in {f'ARXQ{i:02}' for i in range(1, 8)}
            duplicate = sid in {'DBCNI07', 'DBCNI08'}
            failed = s.get('returned_count') is None
            s['execution_state'] = 'failed' if failed else 'diagnostic' if diagnostic else 'duplicate_probe' if duplicate else 'retrieved'
            s['coverage_eligible'] = not (failed or diagnostic or duplicate)
            searches.append({k: v for k, v in s.items() if k != 'results'})
            for r in s.get('results', []):
                occurrences.append(dict(search_id=sid, rank=r['rank'], title=r['title'], url=r['url'], doi=r.get('doi', ''), candidate_id=''))
        for c in bundle['candidates']:
            c = dict(c)
            c['query_ids'] = c.get('query_ids', c.get('search_ids', [c.get('search_id')]))
            matches = [r['id'] for r in existing if identifiers(c) & identifiers(r)]
            c['matched_existing_ids'] = sorted(set(matches) | set(c.get('existing_record_ids', [])))
            c['identity_note'] = 'DOI・URL・正規化題名の一致候補。版と研究同一性は別途確認。'
            candidates.append(c)
            for r in c.get('retrieval_ranks', []):
                occurrences.append(dict(search_id=r['search_id'], rank=r['rank'], title=c['title'], url=c['url'], doi=c.get('doi', ''), candidate_id=c['candidate_id']))
    # Japanese focus candidates link back to the complete returned bibliographic slots.
    for o in occurrences:
        if not o['candidate_id']:
            found = [c['candidate_id'] for c in candidates if o['search_id'] in c['query_ids'] and identifiers(o) & identifiers(c)]
            o['candidate_id'] = ';'.join(found)
        o['screening_depth'] = '重点候補の判断あり' if o['candidate_id'] else '書誌取得のみ・詳細選別未完了'
    errors = audit(searches, candidates, occurrences)
    with (OUT / 'coverage_matrix.csv').open(encoding='utf-8-sig', newline='') as f:
        matrix = list(csv.DictReader(f))
    known_search_ids = {s['search_id'] for s in searches}
    for cell in matrix:
        for sid in filter(None, cell['executed_search_ids'].split(';')):
            if sid not in known_search_ids:
                errors.append(f'{cell["cell_id"]}: unexecuted search {sid}')
    required_platforms = {'Google Scholar', 'IEEE Xplore', 'J-STAGE', 'CiNii Research', 'arXiv'}
    if {c['platform'] for c in matrix} != required_platforms:
        errors.append('coverage matrix missing a required platform')
    if '--self-test' in sys.argv:
        bad = [dict(s) for s in searches]
        failed = next(s for s in bad if s['execution_state'] == 'failed')
        failed['returned_count'] = 0
        assert any('failure encoded' in e for e in audit(bad, candidates, occurrences))
        bad = [dict(s) for s in searches]
        next(s for s in bad if s['execution_state'] == 'diagnostic')['coverage_eligible'] = True
        assert any('unvalidated query' in e for e in audit(bad, candidates, occurrences))
        bad_candidates = [dict(c) for c in candidates]
        bad_candidates[0]['query_ids'] = ['NOT_EXECUTED']
        assert any('unknown search' in e for e in audit(searches, bad_candidates, occurrences))
        print('Self-test: rejected false zero, unvalidated coverage, and orphan candidate')
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in [('search_log', searches), ('candidates', candidates), ('result_occurrences', occurrences), ('platforms', platforms)]:
        write_csv(name, rows)
    write_csv('followup_queue', [c for c in candidates if not c['matched_existing_ids'] and '除外' not in c['decision']])
    report = dict(as_of='2026-11-11', status='PASS' if not errors else 'FAIL', errors=errors,
                  search_calls=len(searches), focused_candidate_rows=len(candidates), result_occurrences=len(occurrences),
                  execution_states=dict(Counter(s['execution_state'] for s in searches)),
                  coverage_cells=len(matrix),
                  unexecuted_cells=[c['cell_id'] for c in matrix if not c['executed_search_ids']],
                  unique_exact_title_keys=len({titlekey(c['title']) for c in candidates}),
                  limitations=['PASS is structural only; no estimate of global recall.',
                               'Candidate rows are mixed screening depth and not independent papers.',
                               'Date-only timestamps remain explicitly missing time-of-day.',
                               'No new candidate has been admitted to the performance benchmark.'])
    (OUT / 'audit_result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
