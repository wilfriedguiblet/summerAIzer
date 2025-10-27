import datetime, math
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from .llm import generate_markdown

def _ref_block(refs):
    lines = []
    for i, r in enumerate(refs, 1):
        lines.append(f"[{i}]: {r or ''}")
    return "\n".join(lines)

def _topic_clusters(notes: List[Dict], k_min=3, k_max=6):
    texts = [(n["title"] + " " + (n.get("details") or "")) for n in notes]
    if len(texts) < k_min:
        return {0: list(range(len(notes)))}

    vec = TfidfVectorizer(max_df=0.8, min_df=2, ngram_range=(1,2), stop_words="english")
    X = vec.fit_transform(texts)

    # heuristic k
    k = max(k_min, min(k_max, int(math.sqrt(len(texts)))))
    km = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = km.fit_predict(X)

    clusters = {}
    for idx, lab in enumerate(labels):
        clusters.setdefault(int(lab), []).append(idx)
    return clusters

def _map_refs(cluster_notes: List[Dict]) -> str:
    """
    Builds a bracketed reference mapping 'Paper Title [n]' deterministically by local order.
    """
    lines = []
    for i, n in enumerate(cluster_notes, 1):
        lines.append(f"- {n['title']} [{i}]")
    return "\n".join(lines)

def _llm_section(title: str, notes: List[Dict]) -> str:
    # Build a grounded prompt: the model may only use provided notes.
    refs = [n.get("doi") or n.get("url") for n in notes if (n.get("doi") or n.get("url"))]
    mapping = "\n".join([f"[{i+1}]: {r}" for i, r in enumerate(refs)])
    bullets = []
    for i,n in enumerate(notes,1):
        b = " • ".join(n.get("bullets") or [n.get("summary","")])
        bullets.append(f"({i}) {b}")

    system = (
        "You are a meticulous scientific writer. "
        "Write concise, factual paragraphs suitable for expert readers. "
        "You MUST only use facts from the provided NOTES. "
        "Every concrete claim should include a bracketed citation like [1] that maps to the footnotes block. "
        "Prefer specifics (methods, datasets, magnitudes) over adjectives. "
        "Flag uncertainty with '(speculative)'."
    )

    user = f"""Write a short section titled: {title}

NOTES:
- Field notes with local reference numbers:
{chr(10).join(bullets)}

FOOTNOTES (mapping):
{mapping}

Constraints:
- 120–180 words.
- Use bracketed citations [n] that map to the footnotes.
- No new information beyond NOTES.
"""

    body = generate_markdown(system, user)
    return body + "\n\n" + mapping + "\n"

def write_state(notes, field_cfg):
    today = datetime.date.today().strftime("%Y-%m")
    field = field_cfg["name"]

    # cluster topics
    clusters = _topic_clusters(notes)
    cluster_titles = [f"Topic {i+1}" for i in range(len(clusters))]

    # pick best 3–4 clusters by average year/recency
    cluster_items = []
    for ci, idxs in clusters.items():
        cnotes = [notes[i] for i in idxs]
        avg_year = sum([n.get("year") or 0 for n in cnotes]) / max(1, len(cnotes))
        cluster_items.append((ci, cnotes, avg_year))
    cluster_items.sort(key=lambda x: x[2], reverse=True)
    cluster_items = cluster_items[:4]

    sections = []
    for j, (ci, cnotes, _) in enumerate(cluster_items):
        title = cluster_titles[j] if j < len(cluster_titles) else f"Topic {j+1}"
        sections.append(_llm_section(title, cnotes[:6]))  # keep each section tight

    # top-level refs (union, deterministic order)
    refs = []
    for _, cnotes, _ in cluster_items:
        for n in cnotes:
            link = n.get("doi") or n.get("url")
            if link and link not in refs:
                refs.append(link)

    header = f"# {field} — A Short, Opinionated Overview (as of {today})\n\n"
    header += "> Auto-generated. Facts are grounded in the notes and footnotes; please verify critical numbers.\n\n"
    key_takeaways_prompt = _llm_section("Key Takeaways", notes[:10])

    body = header + key_takeaways_prompt + "\n".join(sections) + "\n## References\n" + _ref_block(refs[:80]) + "\n"
    return body

def write_monthly(notes, field_cfg):
    month = datetime.date.today().strftime("%Y-%m")
    field = field_cfg["name"]

    # choose top ~12 items by recency
    recent = sorted(notes, key=lambda n: n.get("year") or 0, reverse=True)[:12]
    refs = [n.get("doi") or n.get("url") for n in recent if (n.get("doi") or n.get("url"))]
    mapping = "\n".join([f"[{i+1}]: {r}" for i, r in enumerate(refs)])
    bullets = []
    for i, n in enumerate(recent, 1):
        bullets.append(f"- **{n['title']}** — {n.get('summary','')} [{i}]")

    system = (
        "You are a meticulous scientific writer. "
        "Write a 1-page monthly update for experts, grounded only in NOTES. "
        "Each concrete claim must carry a bracketed citation that maps to the footnotes."
    )
    user = f"""Write the Highlights and Signals sections.

NOTES:
{chr(10).join(bullets)}

FOOTNOTES:
{mapping}

Constraints:
- Highlights ≤ 10 bullets.
- Add a brief 'Signals to Watch' paragraph (repro issues, notable datasets/tools), citing if mentioned in NOTES.
- No claims beyond NOTES.
"""

    highlights = generate_markdown(system, user)

    body = f"# {field} — Monthly Update ({month})\n\n{highlights}\n\n## References\n{mapping}\n"
    return body

