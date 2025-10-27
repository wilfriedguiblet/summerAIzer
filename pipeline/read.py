from typing import List, Dict

def _shorten(s, n=350):
    s = (s or "").strip().replace("\n"," ")
    return s if len(s) <= n else s[: n-3] + "..."

def _first_sentence(s: str) -> str:
    s = (s or "").strip()
    for sep in [". ", ".\n", "\n"]:
        if sep in s:
            return s.split(sep, 1)[0] + "."
    return s

def make_notes(papers: List[Dict], field_cfg) -> List[Dict]:
    notes = []
    for p in papers:
        abs_txt = p.get("abstract") or ""
        note = {
            "id": p.get("id"),
            "title": (p.get("title") or "").strip(),
            "venue": p.get("venue"),
            "url": p.get("url"),
            "doi": p.get("doi"),
            "year": int(str(p.get("published"))[:4]) if p.get("published") else None,
            "summary": _shorten(_first_sentence(abs_txt), 300) if abs_txt else "(no abstract available)",
            "details": _shorten(abs_txt, 700),
            "claims": [],
            "citations": [p.get("doi") or p.get("url") or ""],
            "is_novel": True
        }
        notes.append(note)
    return notes
