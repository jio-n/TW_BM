"""Save public OA articles through NCBI's documented text-mining API."""
import pathlib,json,urllib.request,concurrent.futures
RAW=pathlib.Path(__file__).resolve().parents[1]/'evidence/raw/sensor'
IDS={'R0001':'PMC11946328','R0004':'PMC9229539','R0012':'PMC11460470','R0013':'PMC9418252','R0016':'PMC12251633','R0021':'PMC13211143'}
def save(item):
    paper,pmc=item
    u=f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmc}/unicode'
    try:
        with urllib.request.urlopen(u,timeout=45) as response: data=json.load(response)
        texts=[p.get('text','') for col in data for doc in col['documents'] for p in doc['passages']]
        text='\n'.join(texts)
        assert len(text)>1000
        (RAW/(paper+'_bioc.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        (RAW/(paper+'_fulltext.txt')).write_text(text,encoding='utf-8')
        return {'id':paper,'url':u,'characters':len(text),'status':'archived OA text via official BioC API'}
    except Exception as e: return {'id':paper,'url':u,'error':str(e)}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: out=list(pool.map(save,IDS.items()))
    (RAW/'bioc_archive_status.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=True))
