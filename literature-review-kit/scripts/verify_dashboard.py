"""Check saved HTML data, structure, and JS syntax; does not claim browser QA."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile

from review import load, digest, TABLES


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.scripts=[];self.current=None;self.external=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a' and attrs.get('href','').startswith('#'):self.links.append(attrs['href'][1:])
        if tag=='script':
            self.current={'id':attrs.get('id'),'text':''};self.scripts.append(self.current)
            if 'src' in attrs:self.external.append(attrs['src'])
        if tag=='link' and attrs.get('rel')=='stylesheet':self.external.append(attrs.get('href'))
    def handle_endtag(self,tag):
        if tag=='script':self.current=None
    def handle_data(self,data):
        if self.current is not None:self.current['text']+=data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True);parser.add_argument('--node',default='node')
    args=parser.parse_args();project=args.project.resolve()
    cfg,data=load(project);html=(project/'outputs/dashboard.html').read_text(encoding='utf-8')
    page=Page();page.feed(html)
    assert len(page.ids)==len(set(page.ids)),'Duplicate HTML IDs'
    assert set(page.links)<=set(page.ids),'Unresolved page anchors'
    assert not page.external,'External assets prevent standalone use'
    payload=json.loads(next(s['text'] for s in page.scripts if s['id']=='review-data'))
    assert payload['config']==cfg and payload['data']==data,'Embedded data stale'
    assert payload['status']['data_hash']==digest(cfg,data),'Status stale'
    expected_outputs={}
    for entry in data['evidence']:
        if entry['field'] in ('labels','output') and entry['value']:
            expected_outputs.setdefault(entry['paper_id'],[]).append({k:entry[k] for k in ('evidence_id','field','value','verification')})
    assert payload['paper_outputs']==expected_outputs,'Classification targets differ from recorded evidence'
    assert len(payload['status']['plan_checks'])>=6,'Missing plan checks'
    scripts=[s['text'] for s in page.scripts if s['id']!='review-data']
    with tempfile.TemporaryDirectory(dir=project/'outputs') as folder:
        path=Path(folder)/'dashboard.js';path.write_text('\n'.join(scripts),encoding='utf-8')
        subprocess.run([args.node,'--check',str(path)],check=True,capture_output=True)
    result=dict(static_validation='PASS',rows={t:len(data[t]) for t in TABLES},html_bytes=len(html.encode()),javascript_syntax='PASS',embedded_data='exact match',papers_with_output_evidence=len(expected_outputs),browser_visual_and_interaction='not verified',evidence_note='Static checks validate records and syntax; they do not prove UI operation or literature coverage.')
    (project/'outputs/html_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
