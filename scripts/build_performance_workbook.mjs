import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const d=JSON.parse(await fs.readFile(path.join(root,'data/performance_digest.json'),'utf8'));
const qa=path.join(root,'evidence/workbook_qa/performance');await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const cols=[['id','論文ID',12],['name','論文・モデル',34],['status','採否',12],['metric','代表値の指標・条件',32],['value','代表値',16],['unit','単位・表現',14],['result','実際の成績',65],['note','数値の読み方・注意',65],['split','分割・評価条件',65],['model_family','モデル系統',28],['input','入力区分',30],['labels','クラスラベル',65],['title','原題',65],['url','原資料URL',55],['locator','原資料内位置',45],['source_ids','Source ID',32],['claim_ids','Claim ID',50],['verification','確認状態',45]];
function col(i){return String.fromCharCode(65+i);}
for(const [index,scope] of ['工具摩耗','工業欠陥'].entries()){
 const rows=d.records.filter(r=>r.scope===scope),bottom=rows.length+4,sh=wb.worksheets.add(scope);
 sh.showGridLines=false;sh.tabColor=index===0?'#233E54':'#456B60';
 sh.getRange('A2').values=[[scope+'：種類分類の性能値']];sh.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#233E54'};
 sh.getRange('A3').values=[['2026-11-11。代表値は対応する条件の報告値。指標・データ・分割の異なる行を直接順位付けしない。']];
 sh.getRange('A3').format.font={name:'Arial',size:10,color:'#495663'};
 const area=sh.getRange(`A4:R${bottom}`);area.values=[cols.map(c=>c[1]),...rows.map(r=>cols.map(([key])=>key==='value'?(r[key]??r.unit):r[key]))];
 area.format.font={name:'Arial',size:10,color:'#172533'};area.format.wrapText=true;area.format.verticalAlignment='top';
 cols.forEach(([, ,width],i)=>{sh.getRange(`${col(i)}4:${col(i)}${bottom}`).format.columnWidth=width;});
 const t=sh.tables.add(`A4:R${bottom}`,true,`Performance${index+1}`);t.style='TableStyleMedium2';t.showFilterButton=true;
 const header=sh.getRange('A4:R4');header.format.fill='#233E54';header.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};header.format.horizontalAlignment='center';header.format.verticalAlignment='center';header.format.rowHeight=34;
 rows.forEach((r,i)=>{
  const row=i+5;
  if(r.value!==null)sh.getRange(`E${row}`).setNumberFormat(r.unit==='%超'?'0.00%"超"':r.unit==='%'?'0.00%':'0.000');
  sh.getRange(`E${row}`).format.horizontalAlignment='right';
  const lines=Math.max(...cols.map(([key,,width])=>String(r[key]??'未確認').split('\n').reduce((s,line)=>s+Math.max(1,Math.ceil([...line].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0)/(width-2))),0)));
  const height=Math.max(64,14*lines+10);if(height>409)throw new Error(`${r.id}: row too tall ${height}`);
  sh.getRange(`A${row}:R${row}`).format.rowHeight=height;
 });
 sh.getRange(`N5:N${bottom}`).format.font={name:'Arial',size:10,color:'#0563C1'};
 sh.freezePanes.freezeRows(4);sh.freezePanes.freezeColumns(2);
}
wb.recalculate();
const scan=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'formula error scan'});
await fs.writeFile(path.join(qa,'formula_errors.ndjson'),scan.ndjson);
for(const sh of wb.worksheets.items){
 const pic=await wb.render({sheetName:sh.name,range:'A1:H8',scale:1.4,format:'png'});await fs.writeFile(path.join(qa,sh.name+'.png'),new Uint8Array(await pic.arrayBuffer()));
 const count=d.records.filter(r=>r.scope===sh.name).length;
 const tail=await wb.render({sheetName:sh.name,range:`A${count+2}:H${count+4}`,scale:1.2,format:'png'});await fs.writeFile(path.join(qa,sh.name+'_追加行.png'),new Uint8Array(await tail.arrayBuffer()));
 const inspected=await wb.inspect({kind:'table',range:`${sh.name}!A4:H8`,include:'values,formulas',tableMaxRows:5,tableMaxCols:8,maxChars:3500});await fs.writeFile(path.join(root,'evidence/workbook_qa','performance_'+sh.name+'.inspect.ndjson'),inspected.ndjson);
}
const file='classification_performance_summary.xlsx';await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'outputs',file));
await fs.rename(path.join(root,'outputs',file+'.inspect.ndjson'),path.join(root,'evidence/workbook_qa',file+'.inspect.ndjson'));
console.log(JSON.stringify({sheets:wb.worksheets.items.map(s=>s.name),records:d.records.length,formulaScan:scan.ndjson}));
