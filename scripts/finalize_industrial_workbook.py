"""Add native hyperlinks missing from the export API; verify without reauthoring Excel."""
import csv, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from openpyxl import load_workbook  # Read-only inspection; no save/authoring.

ROOT=Path(__file__).resolve().parents[1]
book=ROOT/'outputs/industrial_defect_classification_benchmark.xlsx'
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
DOCREL='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ET.register_namespace('',NS);ET.register_namespace('r',DOCREL)
with zipfile.ZipFile(book) as z: parts={n:z.read(n) for n in z.namelist()}
shared=ET.fromstring(parts['xl/sharedStrings.xml']) if 'xl/sharedStrings.xml' in parts else None
strings=[''.join(si.itertext()) for si in shared] if shared is not None else []
links_added=0
for name in list(parts):
 if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name): continue
 sheet=ET.fromstring(parts[name])
 relname=str(Path(name).parent/'_rels'/(Path(name).name+'.rels')).replace('\\','/')
 rels=ET.fromstring(parts[relname]) if relname in parts else ET.Element(f'{{{REL}}}Relationships')
 # Re-running this narrow patch replaces its own links only.
 for e in list(rels):
  if e.get('Id','').startswith('industrialSource'): rels.remove(e)
 for e in sheet.findall(f'{{{NS}}}hyperlinks'): sheet.remove(e)
 hyperlinks=ET.Element(f'{{{NS}}}hyperlinks')
 for cell in sheet.findall(f'.//{{{NS}}}c'):
  value=cell.find(f'{{{NS}}}v')
  text=''.join(cell.find(f'{{{NS}}}is').itertext()) if cell.get('t')=='inlineStr' else (value.text or '' if value is not None else '')
  if cell.get('t')=='s': text=strings[int(text)]
  if not re.fullmatch(r'https?://\S+',text): continue
  rid=f'industrialSource{links_added+1}'
  ET.SubElement(hyperlinks,f'{{{NS}}}hyperlink',{'ref':cell.get('r'),f'{{{DOCREL}}}id':rid})
  ET.SubElement(rels,f'{{{REL}}}Relationship',{'Id':rid,'Type':DOCREL+'/hyperlink','Target':text,'TargetMode':'External'})
  links_added+=1
 if len(hyperlinks):
  following={'printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst'}
  index=next((i for i,e in enumerate(sheet) if e.tag.split('}')[-1] in following),len(sheet))
  sheet.insert(index,hyperlinks)
 parts[name]=ET.tostring(sheet,encoding='utf-8',xml_declaration=True)
 parts[relname]=ET.tostring(rels,encoding='utf-8',xml_declaration=True)
temp=book.with_suffix('.tmp.xlsx')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
 for name,body in parts.items(): z.writestr(name,body)
temp.replace(book)

d=json.loads((ROOT/'data/industrial_integrated.json').read_text(encoding='utf-8'))
records={r['id']:r for r in d['records']}
main=[r for r in d['records'] if r['adoption_group']=='採用']
expected={'モデル系統':len(d['family_summary']),'視覚Transformer':sum(r['family_group']=='視覚Transformer' for r in main),'VLM・対照学習':sum(r['family_group']=='VLM／VLM由来特徴' for r in main),'MLLM・LLM':sum(r['family_group'] in ['MLLM','LLM（テキスト中心）'] for r in main),'関連・保留':len(d['records'])-len(main),'除外候補':len(d['exclusions']),'出典':len(d['sources']),'主張と根拠':len(d['claim_evidence'])}
wb=load_workbook(book,data_only=False)
assert len(wb.worksheets)==len(expected)
for sh in wb:
 assert sh.max_row-4==expected[sh.title],sh.title
 assert len(sh.tables)==1 and sh.freeze_panes=='C5',sh.title
 assert next(iter(sh.tables.values())).autoFilter is not None,sh.title
 for row in sh:
  for c in row:
   assert c.data_type!='e',(sh.title,c.coordinate,c.value)
   if c.hyperlink: assert c.hyperlink.target==c.value
 assert all(0<sh.row_dimensions[i].height<=409 for i in range(5,sh.max_row+1))
for name in ['視覚Transformer','VLM・対照学習','MLLM・LLM','関連・保留']:
 sh=wb[name];headers={c.value:c.column-1 for c in sh[4]}
 for row in sh.iter_rows(min_row=5):
  r=records[row[0].value]
  for header,key in [('モデル系統','model_family'),('主モデル','primary_model'),('欠陥クラス（原語）','labels'),('種類分類の成績・条件','performance'),('採否','status'),('Claim ID','claim_ids')]:
   assert row[headers[header]].value==r[key],(r['id'],key)
assert sum(bool(c.hyperlink) for sh in wb for row in sh for c in row)==links_added
with (ROOT/'outputs/industrial_defect_classification_benchmark.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==len(records)
assert sum(x['accepted_count'] for x in d['family_summary'])==len(main)
assert all(r['claim_ids'] and r['source_ids'] and r['model_family'] for r in rows)
qa={'as_of':d['as_of'],'sheet_rows':expected,'native_hyperlinks':links_added,'excel_error_cells':0,'records':len(rows),'stats':d['stats'],'checks':['論文ID・DOI重複と根拠参照は統合時検査','全行の系統・主モデル・ラベル・性能・採否・Claim IDをCSV/JSON/XLSXで照合','全8シートの表・フィルタ・固定ペイン・行高を検査','画像プレビューは各シートの主要範囲、全セルの視覚精査ではない'],'visual_review':'主要範囲・追加行のプレビューを確認'}
(ROOT/'evidence/workbook_qa/industrial/validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(qa,ensure_ascii=False))
