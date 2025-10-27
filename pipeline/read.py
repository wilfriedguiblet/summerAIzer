from typing import List, Dict, Tuple
import re, math
import nltk

# bootstrap punkt if not installed
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

def _short(s, n=350):
    s = (s or "").strip().replace("\n"," ")
    return s if len(s) <= n else s[: n-3] + "..."

def _sentences(s: str) -> List[str]:
    try:
        return nltk.sent_tokenize(s or "")
    except Exception:
        # naive fallback
        return [t.strip()+("." if not t.strip().endswith(".") else "") for t in (s or "").split(".") if t.strip()]

def _first(s: str) -> str:
    ss = _sentences(s)
    return ss[0] if ss else ""

def _bullets_from_abstract(abs_txt: str, k: int = 3) -> List[str]:
    # very light extractive bullets: first sentence + 2 informative ones
    sents = _sentences(abs_txt)
    if not sents:
        return []
    cand = sents[:8]  # avoid super long abstracts
    # rank by length (proxy for info density) minus penalty for numbers-only
    scored = sorted(
        [(i, len(re.findall(r"\w+", s)) - 0.4*len(re.findall(r"\d", s))) for i,s in enumerate(cand)],
        key=lambda x: x[1], reverse=True
    )
    picks = [cand[0]] + [cand[i] for i,_ in scored if i != 0][: (k-1)]
    return [b if b.endswith(".") else b+"." for b in picks]

def make_notes(papers: List[Dict], field_cfg) -> List[Dict]:
    notes = []
    for p in papers:
        abs_txt = p.get("abstract") or ""
        bullets = _bullets_from_abstract(abs_txt, k=3)
        note = {
            "id": p.get("id"),
            "title": (p.get("title") or "").strip(),
            "venue": p.get("venue"),
            "url": p.get("url"),
            "doi": p.get("doi"),
            "year": int(str(p.get("published"))[:4]) if p.get("published") else None,
            "summary": _short(_first(abs_txt) or abs_txt, 300) if abs_txt else "(no abstract available)",
            "details": _short(abs_txt, 900),
            "bullets": bullets,
            "claims": [],  # you can fill with numeric findings later
            "citations": [p.get("doi") or p.get("url") or ""],
            "is_novel": True
        }
        notes.append(note)
    return notes

