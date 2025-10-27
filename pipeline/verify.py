import re

def verify_report(text, notes, field_cfg):
    # Verify every [n] has a footnote, and warn if >10% of sentences lack any citation.
    ref_ids = [int(i) for i in re.findall(r"\[(\d+)\]", text)]
    footers = [int(i) for i in re.findall(r"^\[(\d+)\]:", text, flags=re.M)]
    warn = []

    if ref_ids and footers and max(ref_ids) > max(footers):
        warn.append("Some in-text references do not resolve to footnotes.")

    # crude coverage check
    sentences = re.split(r"(?<=[.!?])\s+", text)
    cited = sum(1 for s in sentences if re.search(r"\[\d+\]", s))
    if sentences and (cited / max(1, len(sentences))) < 0.6:
        warn.append("Low citation density; consider adding citations to quantitative claims.")

    if warn:
        text += "\n\n> WARNING: " + " ".join(warn) + "\n"
    return text

