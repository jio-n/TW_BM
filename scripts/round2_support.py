"""Apply the reviewed second-round records without losing the original evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def append_round2(data, filenames, wear=False):
    for name in filenames:
        path=ROOT/'data'/name
        if not path.exists():
            continue
        extra=json.loads(path.read_text(encoding='utf-8-sig'))
        records={r['id']:r for r in data['records']}
        for update in extra['record_updates']:
            r=records[update['id']]
            r.update(update['fields'])
            key='source_id' if wear else 'source_ids'
            ids=r.get(key,[])
            if isinstance(ids,str): ids=[x.strip() for x in ids.split(';') if x.strip()]
            ids=list(dict.fromkeys(ids+update.get('source_ids',[])))
            r[key]='; '.join(ids) if wear else ids
            for claim in data['claims']:
                if claim['entity_id']==r['id'] and claim['field'] in update['fields']:
                    claim['revision_note']='Round2で当該項目を再確認。現在値は最新レコードと追加Claimを参照'
        data['records'].extend(extra['new_records'])
        for key in ['sources','claims','claim_evidence','search_log']:
            data[key].extend(extra.get(key,[]))
