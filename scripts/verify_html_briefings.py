"""Validate HTML records, metric scales, anchors, and standalone dependencies."""
import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlparse
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/html'
performance={r['id']:r for r in json.loads((ROOT/'data/performance_digest.json').read_text(encoding='utf-8'))['records']}
expected={'tool_wear_classification.html':'focused_integrated.json',
          'industrial_defect_classification.html':'industrial_integrated.json'}
results=[]
for path in sorted(OUT.glob('*.html')):
    errors=[]
    tree=html.fromstring(path.read_text(encoding='utf-8'))
    ids=tree.xpath('//@id')
    if len(ids)!=len(set(ids)):
        errors.append('duplicate HTML ID')
    if tree.get('lang')!='ja':
        errors.append('missing Japanese language attribute')
    if tree.xpath('//script[@src] | //link[@rel="stylesheet"] | //img[@src] | //iframe'):
        errors.append('external rendering dependency')
    for a in tree.xpath('//a[@href]'):
        url=a.get('href')
        if url.startswith('#') and url[1:] not in ids:
            errors.append('missing anchor: '+url)
        elif not urlparse(url).scheme and not url.startswith('#') and not (path.parent/url).exists():
            errors.append('missing companion file: '+url)
        elif url.startswith('https://github.com/jio-n/TW_BM/blob/main/'):
            relative=unquote(url.split('/blob/main/',1)[1].split('#')[0])
            if not (ROOT/relative).exists():
                errors.append('missing repository reference: '+relative)
    count=0
    if path.name in expected:
        records=json.loads((ROOT/'data'/expected[path.name]).read_text(encoding='utf-8'))['records']
        index={r['id']:r for r in records}
        rows=tree.xpath('//tr[@data-paper]')
        count=len(rows)
        if {r.get('data-paper') for r in rows}!=set(index) or len(rows)!=len(index):
            errors.append('catalogue ID mismatch')
        if len(tree.xpath('//details[@class="paper"]'))!=len(index):
            errors.append('details count mismatch')
        headers=tree.xpath('//table[@class="matrix"]/thead/tr/th/text()')
        if len(headers)!=5 or headers[2]!='判定クラス・出力':
            errors.append('classification target column missing')
        for row in rows:
            ident=row.get('data-paper'); r=index[ident]; p=performance[ident]
            cat='hold' if '保留' in r['status'] else 'related' if '関連' in r['status'] else 'accept'
            if row.get('data-status')!=cat:
                errors.append(ident+': status changed')
            cells=row.xpath('./td[@class="target-classes"]')
            if len(row.xpath('./td'))!=5 or len(cells)!=1:
                errors.append(ident+': classification target cell missing')
            else:
                target_text=cells[0].text_content()
                for field in ['labels','labels_ja','task','mixed']:
                    value=r.get(field)
                    if value and value!='未確認' and str(value).replace('。。','。') not in target_text:
                        errors.append(ident+': summary missing '+field)
                if r['labels']=='未確認' and '未確認' not in target_text:
                    errors.append(ident+': unverified labels not marked')
            detail=tree.get_element_by_id(ident).text_content()
            for field in ['title','authors','labels','performance','verification']:
                if str(r[field]).replace('。。','。') not in detail:
                    errors.append(ident+': missing '+field)
            value_text=row.xpath('.//b[@class="metric-value"]')[0].text_content()
            if p['value'] is None:
                if value_text!='未確定': errors.append(ident+': missing value fabricated')
            else:
                number=Decimal(re.search(r'[\d.]+',value_text)[0])
                expected_value=Decimal(str(p['value']))
                if p['unit'].startswith('%'):
                    expected_value*=100
                    if p['unit'] not in value_text:errors.append(ident+': percentage qualifier lost')
                if abs(number-expected_value)>Decimal('0.000001'):
                    errors.append(ident+': numeric scale changed')
            if p['metric'] not in row.text_content() or p['result'].replace('。。','。') not in row.text_content():
                errors.append(ident+': metric/result mismatch')
        for card in tree.xpath('//article[@data-case]'):
            record=index[card.get('data-case')]
            for field in ['labels','task']:
                if record[field].replace('。。','。') not in card.text_content():
                    errors.append(record['id']+': highlight missing '+field)
        category_counts=dict(Counter(r.get('data-status') for r in rows))
    else:
        category_counts={}
    results.append(dict(file=path.name,bytes=path.stat().st_size,records=count,status_counts=category_counts,
                        internal_ids=len(ids),links=len(tree.xpath('//a[@href]')),errors=errors))
result=dict(status='PASS' if all(not r['errors'] for r in results) else 'FAIL',files=results,
            visual_validation='未実施：IABのlocalhost接続タイムアウト。file URLはブラウザポリシーで拒否。',
            interaction_validation='静的検査とJavaScript構文確認。ブラウザでの実操作は未検証。')
qa=ROOT/'evidence/html_qa';qa.mkdir(exist_ok=True)
(qa/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if result['status']!='PASS':
    raise SystemExit(1)
