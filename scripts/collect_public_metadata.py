"""Download public DOI metadata and explicitly listed open-access documents only."""
import concurrent.futures
import json
import pathlib
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'evidence/raw/image'
RAW.mkdir(parents=True, exist_ok=True)
DOIS = [
    '10.3390/sym9120296', '10.3390/s19183817', '10.3390/ma14195690',
    '10.3390/s23031208', '10.3390/s23094476', '10.3390/machines14060589',
    '10.3390/f17070778', '10.3390/machines14070826',
    '10.1016/j.procir.2025.02.184', '10.1109/TIM.2025.3527601',
    '10.1016/j.jmsy.2023.03.005', '10.1016/j.ymssp.2017.11.022',
    '10.1007/s10010-025-00864-5', '10.1299/transjsme.24-00127',
    '10.1016/j.jmapro.2026.06.072', '10.1016/j.ress.2026.113287',
    '10.1007/s10845-023-02313-y', '10.1007/s11227-025-07650-8',
    '10.1038/s41598-025-26550-8', '10.21203/rs.3.rs-6975138/v1',
]
DOCUMENTS = {
    'sam2024.html': 'https://arxiv.org/html/2407.01211v1',
    'lora_sam2025.pdf': 'https://d-nb.info/1383631603/34',
    'drilling2023.html': 'https://arxiv.org/html/2302.05262v2',
    'stitched2021.html': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8497480/',
    'japan2024.pdf': 'https://www.jstage.jst.go.jp/article/transjsme/advpub/0/advpub_24-00127/_pdf/-char/ja',
    'sym2017.pdf': 'https://mdpi-res.com/d_attachment/symmetry/symmetry-09-00296/article_deploy/symmetry-09-00296.pdf',
    'cnn2019.pdf': 'https://mdpi-res.com/d_attachment/sensors/sensors-19-03817/article_deploy/sensors-19-03817.pdf',
    'endmill2021.pdf': 'https://mdpi-res.com/d_attachment/materials/materials-14-05690/article_deploy/materials-14-05690.pdf',
    'ir2023.pdf': 'https://mdpi-res.com/d_attachment/sensors/sensors-23-01208/article_deploy/sensors-23-01208.pdf',
    'yolo2023.pdf': 'https://mdpi-res.com/d_attachment/sensors/sensors-23-04476/article_deploy/sensors-23-04476.pdf',
    'vit2026.pdf': 'https://mdpi-res.com/d_attachment/machines/machines-14-00589/article_deploy/machines-14-00589.pdf',
    'eva2026.pdf': 'https://mdpi-res.com/d_attachment/forests/forests-17-00778/article_deploy/forests-17-00778.pdf',
    'fusion2026.pdf': 'https://mdpi-res.com/d_attachment/machines/machines-14-00826/article_deploy/machines-14-00826.pdf',
    'zero_sam2025.pdf': 'https://assets-eu.researchsquare.com/files/rs-6975138/v1_covered_bf043a86-e9a5-4b88-a88c-65bdd9801911.pdf',
    'gear2025.html': 'https://link.springer.com/article/10.1007/s10010-025-00864-5',
    'semisupervised2025.html': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12660822/',
}
TITLE_QUERIES = [
    'Digital image processing with deep learning for automated cutting tool wear detection',
    'Integrating object detection and image segmentation for detecting the tool wear area on stitched image',
    'The Automatic Tool Wear Monitoring System for Micro-Milling Application with Image-Based Wear Detection',
    'A computer vision approach to analyze and classify tool wear level in milling processes using shape descriptors and machine learning techniques',
]

def fetch(item):
    name, url = item
    path = RAW / name
    if path.exists():
        return {'file': name, 'url': url, 'status': 'already saved'}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'ToolWearBenchmark/1.0 (public academic research)'})
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read()
            path.write_bytes(body)
        return {'file': name, 'url': url, 'status': 'saved', 'bytes': len(body)}
    except Exception as exc:
        return {'file': name, 'url': url, 'status': str(exc)}

items = [(f'crossref_{i+1:02d}.json', 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')) for i, doi in enumerate(DOIS)]
items.extend(DOCUMENTS.items())
items.extend((f'crossref_title_{i+1:02d}.json', 'https://api.crossref.org/works?rows=3&query.title='+urllib.parse.quote(title)) for i,title in enumerate(TITLE_QUERIES))
results = []
for item in items:
    results.append(fetch(item))
    if results[-1]['status'] != 'already saved':
        time.sleep(0.5)
(RAW / 'download_log.json').write_text(json.dumps({'executed_at': datetime.now(timezone.utc).isoformat(), 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(results, ensure_ascii=False, indent=2))
