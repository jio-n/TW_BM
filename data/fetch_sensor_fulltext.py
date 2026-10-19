import json,pathlib,urllib.request,concurrent.futures
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parents[1]
RAW=ROOT/'evidence/raw/sensor'
URLS={
'R0001':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11946328/',
'R0002':'https://www.mdpi.com/2075-4442/13/2/72',
'R0003':'https://www.mdpi.com/2073-8994/11/10/1233',
'R0004':'https://pmc.ncbi.nlm.nih.gov/articles/PMC9229539/',
'R0012':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11460470/',
'R0013':'https://pmc.ncbi.nlm.nih.gov/articles/PMC9418252/',
'R0016':'https://pmc.ncbi.nlm.nih.gov/articles/PMC12251633/',
'R0018':'https://www.mdpi.com/2075-1702/14/5/471',
'R0021':'https://pmc.ncbi.nlm.nih.gov/articles/PMC13211143/',
'R0022':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11820217/',
'R0023':'https://www.mdpi.com/1424-8220/24/13/4117',
'R0024':'https://pmc.ncbi.nlm.nih.gov/articles/PMC11054666/',
'R0028':'https://www.mdpi.com/1424-8220/21/9/3137'}
def fetch(item):
    k,u=item
    try:
        req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 ToolWearResearch/1.0'})
        with urllib.request.urlopen(req,timeout=45) as r: html=r.read().decode('utf-8')
        soup=BeautifulSoup(html,'html.parser')
        for tag in soup(['script','style','nav','header','footer']): tag.decompose()
        text=soup.get_text('\n',strip=True)
        if len(text)<1000 or 'Checking your browser - reCAPTCHA' in text[:200]:
            return {'id':k,'url':u,'error':'Article content was not returned; challenge page was not saved'}
        (RAW/(k+'_fulltext.txt')).write_text(text,encoding='utf-8')
        return {'id':k,'url':u,'characters':len(text),'start':text[:150]}
    except Exception as e: return {'id':k,'url':u,'error':str(e)}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p: res=list(p.map(fetch,URLS.items()))
    (RAW/'fulltext_fetch_status.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(res,ensure_ascii=True,indent=2))
