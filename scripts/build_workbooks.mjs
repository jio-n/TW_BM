import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:\/)/,'$1')),'..');
const data=JSON.parse(await fs.readFile(path.join(root,'data/integrated.json'),'utf8'));
const schema=JSON.parse(await fs.readFile(path.join(root,'data/schema.json'),'utf8'));
const out=path.join(root,'outputs');
const qa=path.join(root,'evidence/workbook_qa');
await fs.mkdir(qa,{recursive:true});

function col(n){let s='';for(n++;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function ids(value){return String(value).split(/[;,；]/).map(x=>x.trim()).filter(Boolean);}
function width(key){
 if(/^(製品ID|論文ID|claim_id|source_id|entity_id)$/.test(key))return 15;
 if(/^(発表年|開発開始年|販売開始年|year)$/.test(key))return 22;
 if(/URL|url|リンク/.test(key))return 52;
 if(/Claim ID|エビデンスID/.test(key))return 55;
 if(/概要|独自性|新規性|限界|制約|未確認|claim|quote|title|原題|locator|publisher|学習|条件|方式|モデル|フロー|状態/.test(key))return 55;
 if(/著者|所属機関/.test(key))return 75;
 return 33;
}
function makeTable(wb,name,rows,columns,tableName,rowHeight=150){
 const sh=wb.worksheets.add(name);
 sh.showGridLines=false;
 const matrix=[columns,...rows.map(r=>columns.map(k=>r[k]??'未確認'))];
 const last=col(columns.length-1);
 const range=sh.getRange(`A1:${last}${matrix.length}`);
 range.values=matrix;
 range.format.font={name:'Arial',size:10,color:'#172533'};
 range.format.wrapText=true;
 range.format.verticalAlignment='top';
 range.format.rowHeight=rowHeight;
 columns.forEach((key,i)=>{sh.getRange(`${col(i)}1:${col(i)}${matrix.length}`).format.columnWidth=width(key);});
 const t=sh.tables.add(`A1:${last}${matrix.length}`,true,tableName);
 t.style='TableStyleMedium2';
 t.showFilterButton=true;
 const h=sh.getRange(`A1:${last}1`);
 h.format.fill='#203B53';
 h.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};
 h.format.horizontalAlignment='center';
 h.format.verticalAlignment='center';
 h.format.rowHeight=60;
 rows.forEach((r,i)=>{
   const lines=Math.max(...columns.map(k=>{
     const text=String(r[k]??'');
     const units=[...text].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0);
     return Math.ceil(units/Math.max(10,width(k)-3))+text.split('\n').length-1;
   }));
   sh.getRange(`A${i+2}:${last}${i+2}`).format.rowHeight=Math.max(44,lines*15+12);
 });
 sh.freezePanes.freezeRows(1);
 sh.freezePanes.freezeColumns(name==='製品比較'?3:2);
 columns.forEach((key,c)=>{
   if(!/URL|url|リンク/.test(key))return;
   rows.forEach((r,i)=>{
     const v=String(r[key]??'');
     if(/^https?:\/\/[^\s;]+$/.test(v)){
       const q=v.replace(/"/g,'""');
       sh.getRange(`${col(c)}${i+2}`).formulas=[[`=HYPERLINK("${q}","${q}")`]];
       sh.getRange(`${col(c)}${i+2}`).format.font.color='#145EA8';
     }
   });
 });
 return sh;
}

for(const kind of ['products','papers']){
 const wb=Workbook.create();
 const academic=kind==='papers';
 const rows=data[kind];
 const entityIds=new Set([...rows,...(academic?data.candidates:[])].map(r=>r[academic?'論文ID':'製品ID']));
 const claims=data.claims.filter(c=>entityIds.has(c.entity_id));
 const claimIds=new Set(claims.map(c=>c.claim_id));
 const links=data.claim_evidence.filter(c=>claimIds.has(c.claim_id));
 const sourceIds=new Set(links.map(c=>c.source_id));
 for(const row of rows)for(const id of ids(row['エビデンスID']))sourceIds.add(id);
 const sources=data.sources.filter(s=>sourceIds.has(s.source_id));
 const main=makeTable(wb,academic?'論文比較':'製品比較',rows,schema[kind],academic?'PapersTable':'ProductsTable',180);
 main.tabColor='#203B53';
 if(academic&&data.candidates.length)makeTable(wb,'候補保留',data.candidates,schema.papers,'HeldPapersTable',180);
 makeTable(wb,'出典',sources,['source_id','title','publisher','year','url','type','primary','accessed','verification','saved_path','locator'],'SourcesTable',125);
 makeTable(wb,'主張',claims,['claim_id','entity_id','field','claim','status'],'ClaimsTable',125);
 makeTable(wb,'根拠対応',links,['claim_id','source_id','locator','quote','verification'],'EvidenceLinksTable',125);
 const guide=wb.worksheets.add('利用ガイド');
 guide.showGridLines=false;
 const guideRows=[
  ['工具摩耗技術ベンチマーク','2026-10-20 公開資料版'],
  ['比較対象数',rows.length],
  ['提供状態/確認深度',academic?`本文該当節確認${data.stats.paper_fulltext}、抄録/抜粋${data.stats.papers-data.stats.paper_fulltext}、候補保留${data.stats.held_papers}（採用数外）`:'商用28、関連計測/欠損3、販売終了/現状未確認2'],
  ['調査目標と限界','候補件数の目標は達成。探索飽和と全カテゴリの網羅性は未達。追加調査領域は監査報告へ。'],
  ['基本操作','比較表は1製品/1論文1行。列フィルタと並べ替えで工具、加工法、入力、モデル、確認状態を選ぶ。製品は先頭3列、論文は2列と見出しを固定。'],
  ['根拠の追跡','比較表のClaim ID→主張→根拠対応→出典URL・資料内位置。CSVのエビデンス台帳が再利用用の正本。'],
  ['欠測の扱い','未確認=未取得/根拠不足。非公開=明示的非開示。非該当=機能に適用しない。未知を0と置かない。'],
  ['技術確度','A:対象製品に技法明示、B:関連研究/特許のみ、C:AI/MLのみ、D:手法未確認。AはAI使用や固有モデル公開を意味しない。'],
  ['モデルと研究','確認済み実装モデルと関連研究モデルを別列化。特許の選択肢、論文での撮像装置利用を販売版内蔵モデルと解釈しない。'],
  ['性能の読み方','Accuracy、IoU/Dice、µm誤差、R²、寿命延長、繰返し性は異なる指標。条件の違う数値を直接ランキングしない。'],
  ['論文の確認状態','全文確認は本文の対象・方法・評価該当節を確認した意味。抄録/抜粋行の未取得実験条件は未確認のまま。全採用論文の全文精読ではない。'],
  ['重点監査','SAM系のIoU名称/式不整合、全寿命正規化、テストによる構造選択、ねじ品質proxy、工具数の不整合を注記。'],
  ['時点・市場情報','現行Web案内は購入契約や販売地域を保証しない。発売日、価格、製品別市場規模は多くが未確認。'],
  ['出典ファイル','Webツール抽出記録、Crossrefメタデータ、著者公開版、OA原PDFを区別。保存できない資料はURLを参照。'],
 ];
 guide.getRange(`A1:B${guideRows.length}`).values=guideRows;
 guide.getRange(`A1:B${guideRows.length}`).format.font={name:'Arial',size:11,color:'#172533'};
 guide.getRange(`A1:B${guideRows.length}`).format.wrapText=true;
 guide.getRange(`A1:B${guideRows.length}`).format.verticalAlignment='center';
 guide.getRange(`A1:A${guideRows.length}`).format.columnWidth=29;
 guide.getRange(`B1:B${guideRows.length}`).format.columnWidth=110;
 guide.getRange(`A1:B${guideRows.length}`).format.rowHeight=54;
 guide.getRange('A1:B1').format.font={name:'Arial',size:14,bold:true,color:'#203B53'};
 guide.tabColor='#8998A5';
 wb.recalculate();
 const prefix=academic?'academic':'commercial';
 const summary=await wb.inspect({kind:'table',range:`${main.name}!A1:F3`,include:'values,formulas',tableMaxRows:3,tableMaxCols:6,maxChars:2500});
 await fs.writeFile(path.join(qa,`${prefix}_inspection.ndjson`),summary.ndjson);
 const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'formula error scan',maxChars:3000});
 await fs.writeFile(path.join(qa,`${prefix}_formula_errors.ndjson`),errors.ndjson);
 for(let i=0;i<wb.worksheets.items.length;i++){
   const sh=wb.worksheets.getItemAt(i);
   const range=sh.name==='利用ガイド'?'A1:B6':sh.name.includes('比較')||sh.name==='候補保留'?'A1:D3':'A1:D3';
   const preview=await wb.render({sheetName:sh.name,range,scale:1,format:'png'});
   await fs.writeFile(path.join(qa,`${prefix}_${i+1}.png`),new Uint8Array(await preview.arrayBuffer()));
 }
 const filename=academic?'academic_paper_benchmark.xlsx':'commercial_tool_benchmark.xlsx';
 await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,filename));
 try{await fs.rename(path.join(out,filename+'.inspect.ndjson'),path.join(qa,filename+'.inspect.ndjson'));}catch(e){if(e.code!=='ENOENT')throw e;}
 console.log(JSON.stringify({filename,rows:rows.length,sources:sources.length,claims:claims.length,sheets:wb.worksheets.items.map(s=>s.name)}));
}
