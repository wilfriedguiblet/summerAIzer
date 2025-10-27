from sentence_transformers import SentenceTransformer, util
from datetime import datetime
import numpy as np

_model = None
def _model_load():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _venue_weight(venue, whitelist):
    if not venue:
        return 0.5
    v = venue.lower()
    for w in whitelist:
        if w.lower() in v:
            return 1.0
    return 0.6

def _recency_weight(published):
    try:
        y = int(str(published)[:4])
        delta = max(0, datetime.utcnow().year - y)
        return max(0.4, min(1.0, 1.0 - 0.1 * delta))
    except Exception:
        return 0.6

def curate(papers, field_cfg):
    include_terms = field_cfg.get("queries",{}).get("keywords",{}).get("include",[])
    model = _model_load()
    if include_terms:
        seed_vec = np.mean([model.encode(k, normalize_embeddings=True) for k in include_terms], axis=0)
    else:
        seed_vec = model.encode("G-quadruplex nucleic acids", normalize_embeddings=True)

    wl = field_cfg.get("venues",{}).get("whitelist",[])
    min_rank = field_cfg.get("thresholds",{}).get("min_rank_score", 0.35)

    def score(p):
        text = (p.get("abstract") or p.get("title") or "")[:4096]
        v = model.encode(text, normalize_embeddings=True)
        novelty = 1 - float(util.cos_sim(v, seed_vec))
        vw = _venue_weight(p.get("venue",""), wl)
        rw = _recency_weight(p.get("published"))
        return 0.55*novelty + 0.25*vw + 0.20*rw

    ranked = sorted(papers, key=score, reverse=True)
    out = []
    for p in ranked:
        s = float(score(p))
        if s >= min_rank:
            q = dict(p); q["rank_score"] = s
            out.append(q)
    return out
