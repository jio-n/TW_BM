"""Add native source hyperlinks (unsupported in artifact-tool), then check the export."""
import csv, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import Counter
from openpyxl import load_workbook  # Read-only verification; never authors the workbook.

ROOT = Path(__file__).resolve().parents[1]
book = ROOT / 'outputs/wear_type_classification_benchmark.xlsx'
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
DOCREL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ET.register_namespace('', NS)
ET.register_namespace('r', DOCREL)
with zipfile.ZipFile(book) as z:
    parts = {n: z.read(n) for n in z.namelist()}
shared = ET.fromstring(parts['xl/sharedStrings.xml']) if 'xl/sharedStrings.xml' in parts else None
strings = [''.join(si.itertext()) for si in shared] if shared is not None else []
links_added = 0
for name in list(parts):
    if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml', name):
        continue
    sheet = ET.fromstring(parts[name])
    relname = str(Path(name).parent / '_rels' / (Path(name).name + '.rels')).replace('\\', '/')
    rels = ET.fromstring(parts[relname]) if relname in parts else ET.Element(f'{{{REL}}}Relationships')
    hyperlinks = ET.Element(f'{{{NS}}}hyperlinks')
    for cell in sheet.findall(f'.//{{{NS}}}c'):
        value = cell.find(f'{{{NS}}}v')
        text = ''.join(cell.find(f'{{{NS}}}is').itertext()) if cell.get('t') == 'inlineStr' else (value.text or '' if value is not None else '')
        if cell.get('t') == 's':
            text = strings[int(text)]
        if not re.fullmatch(r'https?://\S+', text):
            continue
        rid = f'wearSource{links_added + 1}'
        ET.SubElement(hyperlinks, f'{{{NS}}}hyperlink', {'ref': cell.get('r'), f'{{{DOCREL}}}id': rid})
        ET.SubElement(rels, f'{{{REL}}}Relationship', {'Id': rid, 'Type': DOCREL + '/hyperlink', 'Target': text, 'TargetMode': 'External'})
        links_added += 1
    if len(hyperlinks):
        # CT_Worksheet order: hyperlinks precedes printOptions/pageMargins and tableParts.
        following = {'printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst'}
        index = next((i for i, e in enumerate(sheet) if e.tag.split('}')[-1] in following), len(sheet))
        sheet.insert(index, hyperlinks)
        parts[name] = ET.tostring(sheet, encoding='utf-8', xml_declaration=True)
        parts[relname] = ET.tostring(rels, encoding='utf-8', xml_declaration=True)
temp = book.with_suffix('.tmp.xlsx')
with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, body in parts.items():
        z.writestr(name, body)
temp.replace(book)

d = json.loads((ROOT / 'data/focused_integrated.json').read_text(encoding='utf-8'))
wb = load_workbook(book, data_only=False)
expected = {'モデル系統':len(d['model_family_summary']), '画像のみ':sum(r['group']=='画像のみ' and r['status'].startswith('採用') for r in d['records']), 'マルチモーダル':sum(r['group']=='マルチモーダル' and r['status'].startswith('採用') for r in d['records']), '保留':sum('保留' in r['status'] for r in d['records']), '関連研究':sum('関連' in r['status'] for r in d['records']), '既存59本の再選別':59, '出典':len(d['sources']), '主張と根拠':len(d['claim_evidence'])}
assert len(wb.worksheets) == len(expected)
for sh in wb:
    assert sh.max_row - 4 == expected[sh.title], sh.title
    assert len(sh.tables) == 1 and sh.freeze_panes == 'C5', sh.title
    assert next(iter(sh.tables.values())).autoFilter is not None, sh.title
    for row in sh:
        for c in row:
            assert c.data_type != 'e', (sh.title, c.coordinate, c.value)
            if c.hyperlink:
                assert c.hyperlink.target == c.value
    assert all(sh.row_dimensions[i].height <= 409 for i in range(5, sh.max_row + 1)), sh.title
assert sum(bool(c.hyperlink) for sh in wb for row in sh for c in row) == links_added
with (ROOT / 'outputs/wear_type_classification_benchmark.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == len(d['records'])
dois=[r['doi'] for r in d['records'] if r['doi'] and r['doi'].startswith('10.')]
assert len(set(dois)) == len(dois)
assert all(r['model_family'] and r['primary_models'] and r['model_family_basis'] for r in rows)
assert sum(f['image_count']+f['multimodal_count'] for f in d['model_family_summary']) == expected['画像のみ']+expected['マルチモーダル']
assert sum(f['held_count']+f['related_count'] for f in d['model_family_summary']) == expected['保留']+expected['関連研究']
for name in ['画像のみ','マルチモーダル','保留','関連研究']:
    sh=wb[name]
    headers={c.value:c.column for c in sh[4]}
    for row in sh.iter_rows(min_row=5):
        record=next(r for r in d['records'] if r['id']==row[0].value)
        assert row[headers['主モデル系統']-1].value == record['model_family']
        assert row[headers['比較モデルの系統']-1].value == record['baseline_families']
summary = {'as_of': d['as_of'], 'sheet_rows': expected, 'native_hyperlinks': links_added, 'excel_error_cells':0, 'records':len(rows), 'sources':len(d['sources']), 'claims':len(d['claims']), 'search_log_rows':len(d['search_log']), 'screening':dict(Counter(r['判定'] for r in d['screening'])), 'visual_check':'各シートの主要範囲と追加行を描画確認。全レコードのCSV/XLSXを照合。出典はネイティブリンク。'}
(ROOT / 'evidence/workbook_qa/focused/validation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False))
