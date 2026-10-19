import json, pathlib, urllib.request, concurrent.futures, re
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'evidence/raw/sensor'
RAW.mkdir(parents=True, exist_ok=True)
DOIS = '''10.3390/s25061742
10.3390/lubricants13020072
10.3390/sym11101233
10.3390/mi13060873
10.3390/machines11010094
10.3390/machines13020115
10.1115/1.4036350
10.1016/j.rcim.2016.12.009
10.1016/j.jmsy.2017.01.004
10.3390/s20174657
10.1016/j.aei.2025.103503
10.1016/j.mex.2024.102965
10.1038/s41598-022-18235-3
10.1504/IJHM.2021.114174
10.1016/j.rcim.2022.102368
10.3390/s25134068
10.1007/s10845-026-02939-8
10.3390/machines14050471
10.1038/s41598-026-72453-7
10.1016/j.jmapro.2026.01.047
10.3390/s26102937
10.3390/s25030662
10.3390/s24134117
10.3390/s24082652
10.1016/j.mfglet.2021.10.002
10.2991/isrme-15.2015.11
10.1016/j.measurement.2019.107461
10.3390/s21093137'''.splitlines()

def fetch(item):
    i, doi = item
    request = urllib.request.Request('https://api.crossref.org/works/' + doi, headers={'User-Agent': 'ToolWearResearch/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.load(response)
        (RAW / f'R{i:04d}_crossref.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        m = data['message']
        abstract = unescape(re.sub('<[^>]+>', ' ', m.get('abstract', '')))
        record = {'id':f'R{i:04d}','doi':doi,'title':m.get('title'),'authors':[a.get('given','')+' '+a.get('family','') for a in m.get('author',[])], 'affiliations':list(set(x.get('name','') for a in m.get('author',[]) for x in a.get('affiliation',[]))), 'year':m.get('published',{}).get('date-parts'), 'journal':m.get('container-title'),'abstract':abstract}
        return record
    except Exception as e:
        return {'id':f'R{i:04d}','doi':doi,'error':str(e)}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(fetch,enumerate(DOIS,1)))
    (RAW/'crossref_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
