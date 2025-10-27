import re

def verify_report(text, notes, field_cfg):
    ref_ids = re.findall(r"\[(\d+)\]", text)
    if not ref_ids:
        return text
    footers = re.findall(r"^\[(\d+)\]:", text, flags=re.M)
    if not footers:
        text += "\n\n> WARNING: Some references in text do not resolve to footnotes.\n"
        return text
    max_ref = max(int(i) for i in ref_ids)
    max_footer = max(int(i) for i in footers)
    if max_ref > max_footer:
        text += "\n\n> WARNING: Some references in text do not resolve to footnotes.\n"
    return text
