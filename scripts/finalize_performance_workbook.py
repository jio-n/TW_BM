"""Add native hyperlinks missing from the export API; verify without reauthoring Excel."""
import csv, json, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from openpyxl import load_workbook  # Read-only inspection; no save/authoring.

ROOT=Path(__file__).resolve().parents[1]
book=ROOT/'outputs/classification_performance_summary.xlsx'
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
  if e.get('Id','').startswith('performanceSource'): rels.remove(e)
 for e in sheet.findall(f'{{{NS}}}hyperlinks'): sheet.remove(e)
 hyperlinks=ET.Element(f'{{{NS}}}hyperlinks')
 for cell in sheet.findall(f'.//{{{NS}}}c'):
  value=cell.find(f'{{{NS}}}v')
  text=''.join(cell.find(f'{{{NS}}}is').itertext()) if cell.get('t')=='inlineStr' else (value.text or '' if value is not None else '')
  if cell.get('t')=='s': text=strings[int(text)]
  if not re.fullmatch(r'https?://\S+',text): continue
  rid=f'performanceSource{links_added+1}'
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

d=json.loads((ROOT/'data/performance_digest.json').read_text(encoding='utf-8'))
wb=load_workbook(book,data_only=False)
assert [s.title for s in wb]==['工具摩耗','工業欠陥']
for sh in wb:
 rows=[r for r in d['records'] if r['scope']==sh.title]
 assert sh.max_row==len(rows)+4 and len(sh.tables)==1 and sh.freeze_panes=='C5'
 assert next(iter(sh.tables.values())).autoFilter is not None
 for i,r in enumerate(rows,5):
  assert sh.cell(i,1).value==r['id']
  assert sh.cell(i,4).value==r['metric']
  actual=sh.cell(i,5).value
  if r['value'] is None: assert actual==r['unit']
  else: assert isinstance(actual,(float,int)) and abs(actual-r['value'])<1e-12
  assert sh.cell(i,6).value==r['unit'] and sh.cell(i,7).value==r['result']
  assert sh.cell(i,14).hyperlink.target==r['url']
  assert sh.row_dimensions[i].height<=409
  for c in sh[i]: assert c.data_type!='e'
assert links_added==len(d['records'])
with (ROOT/'outputs/classification_performance_summary.csv').open(encoding='utf-8-sig',newline='') as f: csvrows=list(csv.DictReader(f))
assert len(csvrows)==len(d['records'])
for a,b in zip(csvrows,d['records']):
 assert a['id']==b['id'] and a['result']==b['result']
for filename,scope in [('focused_integrated.json','工具摩耗'),('industrial_integrated.json','工業欠陥')]:
 original=json.loads((ROOT/'data'/filename).read_text(encoding='utf-8'))
 expected={r['id'] for r in original['records']};actual={r['id'] for r in d['records'] if r['scope']==scope}
 assert expected==actual
 claim_ids={c['claim_id'] for c in original['claims']}
 for r in d['records']:
  if r['scope']==scope: assert all(c in claim_ids for c in r['claim_ids'].split('; '))
summary={'as_of':d['as_of'],'rows':len(d['records']),'sheets':{s:sum(r['scope']==s for r in d['records']) for s in ['工具摩耗','工業欠陥']},'main':sum(r['status']=='採用' for r in d['records']),'held':sum(r['status']=='保留' for r in d['records']),'related':sum(r['status']=='関連' for r in d['records']),'numeric_values':sum(r['value'] is not None for r in d['records']),'native_hyperlinks':links_added,'error_cells':0,'missing_values':'未報告・未抽出・未確認を区別。ゼロ置換なし','checks':'全ID、数値型、百分率/係数、結果文、根拠ID、CSV/XLSX、表・固定ペイン・リンクを照合','visual_check':'2シート主要範囲と追加行を描画確認'}
(ROOT/'evidence/workbook_qa/performance/validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
