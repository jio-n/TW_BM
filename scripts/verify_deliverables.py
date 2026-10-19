"""Read-only structural checks of exported XLSX/CSV, records and document references."""
import csv
import json
import re
import zipfile
from pathlib import Path
import openpyxl
import sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/integrated.json').read_text(encoding='utf-8'))
schema=json.loads((ROOT/'data/schema.json').read_text(encoding='utf-8'))
errors=[]
result={}
for kind,filename,sheet in [('products','commercial_tool_benchmark.xlsx','製品比較'),('papers','academic_paper_benchmark.xlsx','論文比較')]:
    p=ROOT/'outputs'/filename
    with zipfile.ZipFile(p) as z:
        if z.testzip():errors.append('zip CRC error '+filename)
    wb=openpyxl.load_workbook(p,data_only=False,read_only=False)
    ws=wb[sheet]
    headers=[c.value for c in ws[1]]
    if headers!=schema[kind]:errors.append('headers '+filename)
    if ws.max_row!=len(d[kind])+1:errors.append('rows '+filename)
    if len(ws.tables)!=1:errors.append('main table '+filename)
    current_table=list(ws.tables.values())[0]
    if current_table.autoFilter is None:errors.append('filter '+filename)
    if ws.freeze_panes is None:errors.append('freeze '+filename)
    formulas=sum(c.data_type=='f' for sh in wb for row in sh for c in row)
    links=sum(c.data_type=='f' and str(c.value).startswith('=HYPERLINK(') for sh in wb for row in sh for c in row)
    xl_errors=[f'{sh.title}!{c.coordinate}:{c.value}' for sh in wb for row in sh for c in row if c.data_type=='e']
    errors.extend(xl_errors)
    result[filename]={'rows':ws.max_row-1,'columns':ws.max_column,'main_table_ref':current_table.ref,'filter_ref':current_table.autoFilter.ref,'freeze_panes':str(ws.freeze_panes),'sheets':[sh.title for sh in wb],'formulas':formulas,'hyperlinks':links,'zip_crc':'ok','formula_error_cells':xl_errors,'bytes':p.stat().st_size}
    with (p.with_suffix('.csv')).open(encoding='utf-8-sig',newline='') as f:
        csvrows=list(csv.reader(f))
    if len(csvrows)!=ws.max_row:errors.append('CSV/XLSX row mismatch '+filename)
    if csvrows[0]!=headers:errors.append('CSV/XLSX header mismatch '+filename)
    for i,row in enumerate(d[kind],2):
        if ws.cell(i,1).value!=row[schema[kind][0]]:errors.append('ID order '+filename)
    wb.close()

entity_ids={p.get('製品ID',p.get('論文ID')) for p in d['products']+d['papers']+d['candidates']}
for folder,pattern in [('reports','*.md'),('details','*.md')]:
    for p in (ROOT/folder).glob(pattern):
        body=p.read_text(encoding='utf-8')
        if re.search(r'@@[A-Z_]+@@',body):errors.append('unreplaced marker '+str(p))
        for ent in set(re.findall(r'\b[PR]\d{4}\b',body)):
            if ent not in entity_ids:errors.append(f'unknown entity {ent}: {p.name}')
        for target in re.findall(r'\]\(([^)]+)\)',body):
            if target.startswith(('https://','http://','#')):continue
            if not (p.parent/target.split('#')[0]).exists():errors.append(f'broken local link {target}: {p.name}')
for p in d['papers']:
    if not 100<=len(p['研究概要'])<=200:errors.append('summary length '+p['論文ID'])
for file in ['evidence/coverage_matrix.csv','reports/technology_comparison.csv','reports/research_opportunities.csv']:
    body=(ROOT/file).read_text(encoding='utf-8-sig')
    for ent in set(re.findall(r'\b[PR]\d{4}\b',body)):
        if ent not in entity_ids:errors.append('unknown table entity '+ent+': '+file)
for req in ['README.md','AGENTS.md','RESEARCH_SPEC.md','TASKS.md','PROGRESS.md','SEARCH_LOG.csv','SOURCES.csv','outputs/commercial_tool_benchmark.xlsx','outputs/academic_paper_benchmark.xlsx','reports/tool_wear_technology_benchmark.md','reports/coverage_and_quality_audit.md','evidence/sources.csv','evidence/claims.csv','evidence/claim_evidence.csv','evidence/search_log.csv','evidence/excluded_candidates.csv','evidence/unverified_items.csv']:
    if not (ROOT/req).is_file():errors.append('missing deliverable '+req)
result['errors']=errors
result['limitations']=['ネイティブExcelアプリの全セル操作検証は未実施','Webリンク全件の将来の可用性検証ではない','出典・書誌照合は技術的実験再現の代替ではない']
(ROOT/'evidence/workbook_qa/saved_workbook_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
