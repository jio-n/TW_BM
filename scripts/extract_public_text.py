from pathlib import Path
from pypdf import PdfReader
from html.parser import HTMLParser
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'tr', 'section'):
            self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

folder = Path(__file__).resolve().parents[1] / 'evidence/raw/image'
for f in folder.glob('*.pdf'):
    reader = PdfReader(f)
    f.with_suffix('.txt').write_text('\n\n'.join(f'=== PDF p.{i+1} ===\n'+(page.extract_text() or '') for i, page in enumerate(reader.pages)), encoding='utf-8')
for f in folder.glob('*.html'):
    parser = Text()
    parser.feed(f.read_text(encoding='utf-8'))
    f.with_suffix('.txt').write_text(''.join(parser.parts), encoding='utf-8')
for f in sorted(folder.glob('crossref*.json')):
    m = json.loads(f.read_text(encoding='utf-8'))['message']
    print(json.dumps({'file':f.name,'title':m.get('title'),'authors':[' '.join([a.get('given',''),a.get('family','')]) for a in m.get('author',[])], 'published':m.get('published'),'online':m.get('published-online'),'print':m.get('published-print'),'DOI':m.get('DOI')},ensure_ascii=False))
