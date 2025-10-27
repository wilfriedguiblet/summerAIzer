import requests, time
from urllib.parse import quote_plus

def _eupmc_search(boolean_queries, max_n=250):
    out = []
    for q in boolean_queries:
        cursor = "*"
        fetched = 0
        while fetched < max_n and cursor:
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={quote_plus(q)}&resultType=core&cursorMark={quote_plus(cursor)}&pageSize=100&format=json"
            r = requests.get(url, timeout=45)
            r.raise_for_status()
            js = r.json()
            hits = js.get("resultList",{}).get("result",[]) or []
            for it in hits:
                rec = {
                    "id": f"eupmc:{it.get('id') or it.get('pmid') or it.get('doi') or ''}",
                    "title": (it.get("title") or "").strip(),
                    "venue": it.get("journalTitle"),
                    "published": it.get("firstPublicationDate") or it.get("pubYear"),
                    "doi": it.get("doi"),
                    "url": (("https://doi.org/" + it["doi"]) if it.get("doi") else None),
                    "abstract": it.get("abstractText","") or "",
                    "source": "europe_pmc"
                }
                if rec["title"]:
                    out.append(rec)
                fetched += 1
                if fetched >= max_n:
                    break
            cursor = js.get("nextCursorMark") if js.get("hitCount",0) > fetched else None
            time.sleep(0.2)
    return out

def _crossref_search(boolean_queries, max_n=200):
    out = []
    for q in boolean_queries:
        url = f"https://api.crossref.org/works?query.bibliographic={quote_plus(q)}&rows={max_n}"
        r = requests.get(url, timeout=45)
        r.raise_for_status()
        items = r.json().get("message",{}).get("items",[])
        for it in items:
            rec = {
                "id": f"doi:{(it.get('DOI') or '').lower()}",
                "title": (it.get("title") or [''])[0],
                "venue": it.get("container-title", [None])[0],
                "published": (it.get("issued",{}).get("date-parts") or [[None]])[0][0],
                "doi": it.get("DOI"),
                "url": it.get("URL"),
                "abstract": (it.get("abstract") or "").replace("<jats:p>", "").replace("</jats:p>", ""),
                "source": "crossref"
            }
            if rec["title"]:
                out.append(rec)
        time.sleep(0.2)
    return out

def _dedupe(papers):
    seen = set(); out = []
    for p in papers:
        key = (p.get("doi") or p.get("title") or "").strip().lower()
        if key and key not in seen:
            seen.add(key); out.append(p)
    return out

def ingest_all(field_cfg):
    papers = []
    boolean = field_cfg.get("queries",{}).get("boolean",[]) or []
    if boolean:
        papers += _eupmc_search(boolean, max_n=250)
        papers += _crossref_search(boolean, max_n=200)
    return _dedupe(papers)
