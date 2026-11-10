import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const d=JSON.parse(await fs.readFile(path.join(root,'data/focused_integrated.json'),'utf8'));
const qa=path.join(root,'evidence/workbook_qa/focused');await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const columns=[['id','ID'],['year','発表年'],['labels','摩耗クラス（原語）'],['model','モデル・判定方式'],['performance','種類分類の成績'],['title','論文タイトル'],['tool','対象工具・加工'],['input','推論時の入力'],['labels_ja','クラスの日本語'],['classes','クラス数・出力数'],['task','出力単位・分類タスク'],['mixed','複合摩耗の扱い'],['data','データ規模'],['split','学習・検証・テスト分割'],['metric','評価指標'],['class_results','クラス別結果・比較'],['generalization','未知条件での評価'],['limitation','制約・未確認事項'],['verification','確認範囲'],['status','採否'],['authors','著者'],['dataset_family','データ系列'],['online_status','公開日・巻号'],['existing_id','既存論文ID'],['doi','DOI'],['url','原資料URL'],['locator','該当箇所'],['source_id','Source ID']];
columns.splice(2,0,['model_family','主モデル系統'],['primary_models','主モデル']);
columns.push(['model_pipeline','モデル構成・判定方式'],['baseline_families','比較モデルの系統'],['language_model','言語モデル'],['model_family_basis','系統分類の根拠Claim ID']);
function col(n){let s='';for(n++;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function val(v){return v==null?'未確認':typeof v==='object'?JSON.stringify(v):v;}
let seq=0;
function table(name,rows,cols,note){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;
 const last=col(cols.length-1),bottom=rows.length+4;
 sh.getRange('A2').values=[[name+' — 摩耗種類分類']];sh.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#203B53'};
 sh.getRange('A3').values=[[note]];sh.getRange('A3').format.font={name:'Arial',size:10,color:'#495663'};
 const area=sh.getRange(`A4:${last}${bottom}`);area.values=[cols.map(x=>x[1]),...rows.map(r=>cols.map(([k])=>val(r[k])))];
 area.format.font={name:'Arial',size:10,color:'#172533'};area.format.wrapText=true;area.format.verticalAlignment='top';
 cols.forEach(([k],i)=>{let width=k.endsWith('_count')?19:['id','year','classes'].includes(k)?13: ['doi','source_id'].includes(k)?32:54;sh.getRange(`${col(i)}4:${col(i)}${bottom}`).format.columnWidth=width;});
 const t=sh.tables.add(`A4:${last}${bottom}`,true,`FocusedTable${++seq}`);t.style='TableStyleMedium2';t.showFilterButton=true;
 const h=sh.getRange(`A4:${last}4`);h.format.fill='#203B53';h.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};h.format.rowHeight=34;h.format.verticalAlignment='center';h.format.horizontalAlignment='center';
 rows.forEach((r,i)=>{const lines=Math.max(...cols.map(([k])=>{const s=String(val(r[k]));return Math.ceil([...s].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0)/(['id','year','classes'].includes(k)?12:['doi','source_id'].includes(k)?30:51));}));sh.getRange(`A${i+5}:${last}${i+5}`).format.rowHeight=Math.max(54,lines*14+10);});
 // HYPERLINK calculation is not implemented by this runtime. Keep visible URLs;
 // finalize_focused_workbook.py adds native Excel hyperlinks after export.
 cols.forEach(([k],c)=>{if(k==='url')sh.getRange(`${col(c)}5:${col(c)}${bottom}`).format.font={name:'Arial',size:10,color:'#0563C1'};});
 sh.freezePanes.freezeRows(4);sh.freezePanes.freezeColumns(2);return sh;
}
table('モデル系統',d.model_family_summary,[['family','主モデル系統'],['image_count','画像のみ・採用'],['multimodal_count','画像＋信号・採用'],['held_count','保留'],['related_count','関連・領域系'],['paper_ids','該当論文ID'],['examples','モデル例'],['definition','分類定義']],'主提案の構造・最終判定方式で集計。入力のマルチモーダルとVLM/MLLMは別の軸。');
table('画像のみ',d.records.filter(r=>r.group==='画像のみ'&&!r.status.includes('保留')),columns,'2026-11-11確認。主モデル系統でフィルタ可。比較用ベースラインは別列。精度を順位付けしない。');
table('マルチモーダル',d.records.filter(r=>r.group==='マルチモーダル'&&!r.status.includes('保留')),columns,'推論時に工具実写画像を含む。量予測・寿命予測の成績は比較対象外。');
table('保留',d.records.filter(r=>r.status.includes('保留')),columns,'内容適合でも書誌・公開日などの確認が残る候補。確定採用数には含めない。');
table('領域分類の関連研究',d.records.filter(r=>r.status.includes('関連')),columns,'種類付き検出・分割。画像単位の分類Accuracyと直接比較しない。');
table('既存59本の再選別',d.screening,Object.keys(d.screening[0]).map(k=>[k,k]),'旧ベンチマークの記録を入出力要件で再選別。未確認ラベルは保留。');
table('出典',d.sources,[['source_id','Source ID'],['title','資料名'],['url','原資料URL'],['doi','DOI'],['primary','一次情報'],['verification','確認範囲'],['locator','該当箇所'],['accessed','取得日'],['saved_path','ローカル保存先']],'論文・メタデータ・除外候補を含む。保存パスは調査環境内の所在。');
const cMap=new Map(d.claims.map(c=>[c.claim_id,c]));
const ev=d.claim_evidence.map(l=>({...cMap.get(l.claim_id),...l}));
table('主張と根拠',ev,[['entity_id','論文ID'],['claim_id','Claim ID'],['field','項目'],['claim','主張'],['source_id','Source ID'],['locator','該当箇所'],['quote','短い根拠引用'],['verification','確認範囲']],'論文ID → Claim ID → Source ID。未確認内容を確定情報として補わない。');
wb.recalculate();
const check=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'focused workbook formula errors'});
await fs.writeFile(path.join(qa,'formula_errors.ndjson'),check.ndjson);
for(const sh of wb.worksheets.items){
 const pic=await wb.render({sheetName:sh.name,range:sh.name==='モデル系統'?'A1:F10':'A1:F7',scale:1.3,format:'png'});
 await fs.writeFile(path.join(qa,sh.name+'.png'),new Uint8Array(await pic.arrayBuffer()));
}
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(root,'outputs/wear_type_classification_benchmark.xlsx'));
await fs.rename(path.join(root,'outputs/wear_type_classification_benchmark.xlsx.inspect.ndjson'),path.join(root,'evidence/workbook_qa/wear_type_classification_benchmark.xlsx.inspect.ndjson'));
console.log(JSON.stringify({sheets:wb.worksheets.items.map(s=>s.name),records:d.records.length,formulaScan:check.ndjson}));
