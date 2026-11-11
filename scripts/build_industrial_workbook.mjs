import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const d=JSON.parse(await fs.readFile(path.join(root,'data/industrial_integrated.json'),'utf8'));
const qa=path.join(root,'evidence/workbook_qa/industrial');await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const columns=[['id','論文ID'],['year','年'],['model_family','モデル系統'],['primary_model','主モデル'],['labels','欠陥クラス（原語）'],['performance','種類分類の成績・条件'],['title','原題'],['authors','著者'],['venue','媒体'],['domain','産業分野'],['product','対象製品・材料'],['input_group','入力区分'],['input','推論時の入力'],['prompt','プロンプト・候補ラベル'],['task','出力タスク・単位'],['class_count','欠陥クラス数'],['mixed','複合・多ラベル'],['dataset','データセット'],['data_size','データ規模'],['split','分割・評価条件'],['learning','学習方式・shot条件'],['pretraining','事前学習'],['baseline_models','比較モデル'],['metrics','評価指標'],['class_results','クラス別結果'],['generalization','未知条件評価'],['limitations','制約・未確認'],['code_data','データ・コード'],['verification','確認状態'],['status','採否'],['doi','DOI'],['url','原資料URL'],['locator','該当箇所'],['source_ids','Source ID'],['claim_ids','Claim ID'],['family_group','集計用モデル系統']];
const val=v=>v==null?'未確認':Array.isArray(v)?v.join('; '):typeof v==='object'?JSON.stringify(v):v;
function col(n){let s='';for(n++;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function width(k){return ['id','year'].includes(k)?12:k.endsWith('_count')?16:['doi','source_id','source_ids','claim_ids'].includes(k)?34:['labels','performance','limitations','split','prompt'].includes(k)?66:52;}
let seq=0;
function table(name,rows,cols,note){
 const sh=wb.worksheets.add(name),last=col(cols.length-1),bottom=rows.length+4;
 sh.showGridLines=false;
 sh.getRange('A2').values=[[name+' — 工業欠陥種類分類']];sh.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#203B53'};
 sh.getRange('A3').values=[[note]];sh.getRange('A3').format.font={name:'Arial',size:10,color:'#495663'};
 const area=sh.getRange(`A4:${last}${bottom}`);area.values=[cols.map(c=>c[1]),...rows.map(r=>cols.map(([k])=>val(r[k])))];
 area.format.font={name:'Arial',size:10,color:'#172533'};area.format.wrapText=true;area.format.verticalAlignment='top';
 cols.forEach(([k],i)=>{sh.getRange(`${col(i)}4:${col(i)}${bottom}`).format.columnWidth=width(k);});
 const t=sh.tables.add(`A4:${last}${bottom}`,true,`IndustrialTable${++seq}`);t.style='TableStyleMedium2';t.showFilterButton=true;
 const h=sh.getRange(`A4:${last}4`);h.format.fill='#203B53';h.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};h.format.rowHeight=36;h.format.verticalAlignment='center';h.format.horizontalAlignment='center';
 rows.forEach((r,i)=>{const lines=Math.max(...cols.map(([k])=>String(val(r[k])).split('\n').reduce((sum,line)=>sum+Math.max(1,Math.ceil([...line].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0)/(width(k)-2))),0)));const height=Math.max(62,lines*14+10);if(height>409)throw new Error(`${name} row ${i+5} requires ${height} points; shorten/widen verified fields`);sh.getRange(`A${i+5}:${last}${i+5}`).format.rowHeight=height;});
 cols.forEach(([k],i)=>{if(k==='url'&&rows.length)sh.getRange(`${col(i)}5:${col(i)}${bottom}`).format.font={name:'Arial',size:10,color:'#0563C1'};});
 sh.freezePanes.freezeRows(4);sh.freezePanes.freezeColumns(2);
 return sh;
}
table('モデル系統',d.family_summary,[['model_family','モデル系統'],['accepted_count','主比較'],['related_count','関連'],['held_count','保留'],['paper_ids','論文ID']],'2026-11-11。欠陥の種類名を出す研究。二値の正常／異常や全VQA平均は種類分類の精度と区別。');
const main=d.records.filter(r=>r.adoption_group==='採用');
table('視覚Transformer',main.filter(r=>r.family_group==='視覚Transformer'),columns,'画像・ウェハマップ・EL等の入力種別と、閉集合／多ラベルの評価条件を確認。');
table('VLM・対照学習',main.filter(r=>r.family_group==='VLM／VLM由来特徴'),columns,'CLIP等。視覚塔のみを使う構成、推論時テキスト、学習時だけの言語利用を区別。');
table('MLLM・LLM',main.filter(r=>['MLLM','LLM（テキスト中心）'].includes(r.family_group)),columns,'画像分類と欠陥種類VQAを区別。全タスク平均や位置推定のスコアを混ぜない。');
table('関連・保留',d.records.filter(r=>r.adoption_group!=='採用'),columns,'種類付き検出・分割、本文・クラス・評価が未確認の候補。主比較数には含めない。');
table('除外候補',d.exclusions,[['id','候補ID'],['title','題名'],['status','判定'],['reason','採否理由'],['doi','DOI'],['url','原資料URL'],['source_ids','Source ID']],'二値検知・重症度・ドメイン外・未確認・同一論文の異版等の理由を保持。');
table('出典',d.sources,[['source_id','Source ID'],['title','資料名'],['url','原資料URL'],['doi','DOI'],['publisher','発行者・著者'],['year','年'],['verification','確認範囲'],['locator','該当箇所'],['accessed','取得日'],['saved_path','ローカル保存先']],'取得元資料は再配布せずURL/DOIを参照。一次本文・要旨・検索抜粋を区別。');
const claims=new Map(d.claims.map(c=>[c.claim_id,c]));
table('主張と根拠',d.claim_evidence.map(l=>({...claims.get(l.claim_id),...l})),[['entity_id','論文ID'],['claim_id','Claim ID'],['field','項目'],['claim','主張'],['source_id','Source ID'],['locator','原資料位置'],['verification','確認範囲']],'論文ID → Claim ID → Source ID → 原資料内位置。');
wb.recalculate();
const check=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'formula error scan'});
await fs.writeFile(path.join(qa,'formula_errors.ndjson'),check.ndjson);
for(const sh of wb.worksheets.items){
 const pic=await wb.render({sheetName:sh.name,range:sh.name==='モデル系統'?'A1:E8':'A1:F7',scale:1.2,format:'png'});await fs.writeFile(path.join(qa,sh.name+'.png'),new Uint8Array(await pic.arrayBuffer()));
 if(['視覚Transformer','MLLM・LLM'].includes(sh.name)){
  const count=main.filter(r=>r.family_group===(sh.name==='視覚Transformer'?'視覚Transformer':'MLLM')).length;
  const tail=await wb.render({sheetName:sh.name,range:`A${count+2}:F${count+4}`,scale:1.2,format:'png'});await fs.writeFile(path.join(qa,sh.name+'_追加行.png'),new Uint8Array(await tail.arrayBuffer()));
 }
}
const file='industrial_defect_classification_benchmark.xlsx';
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'outputs',file));
await fs.rename(path.join(root,'outputs',file+'.inspect.ndjson'),path.join(root,'evidence/workbook_qa',file+'.inspect.ndjson'));
console.log(JSON.stringify({sheets:wb.worksheets.items.map(s=>s.name),records:d.records.length,formulaScan:check.ndjson}));
