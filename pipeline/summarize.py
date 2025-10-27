import datetime

def _ref_block(refs):
    lines = []
    for i, r in enumerate(refs, 1):
        r = r or ""
        lines.append(f"[{i}]: {r}")
    return "\n".join(lines)

def write_state(notes, field_cfg):
    today = datetime.date.today().strftime("%Y-%m")
    field = field_cfg["name"]
    refs = [n.get("doi") or n.get("url") for n in notes if (n.get("doi") or n.get("url"))]
    highlights = "\n".join([f"- {n['title']} [{i+1}]" for i,n in enumerate(notes[:8])])

    body = f"# {field} - A Short, Opinionated Overview (as of {today})\n\n"
    body += "> Auto-generated. Please verify citations and numbers before external sharing.\n\n"
    body += "## Key Takeaways\n"
    body += "- Placeholder bullets; will improve with LLM extraction.\n"
    body += "- Notable themes over the last year: TBD.\n\n"
    body += "## Landscape in Brief\n"
    body += "- Core subareas: detection, ligands, helicases, telomere maintenance, promoter regulation, RNA G4s.\n"
    body += "- Common assays: FRET-melting, CD spectra, BG4 immunoprecipitation, rG4-seq, polymerase stop.\n"
    body += "- Open debates: in vivo prevalence and stability; functional roles vs. epiphenomena.\n\n"
    body += "## Recent Momentum\n"
    body += highlights + "\n\n"
    body += "## Limitations and Pitfalls\n"
    body += "- Conditions (ions, crowding) change G4 stability; be careful when extrapolating in vitro to in vivo.\n\n"
    body += "## What Is Next (speculative)\n"
    body += "- Live-cell probes with better specificity; systematic functional screens for RNA G4s.\n\n"
    body += "## References\n"
    body += _ref_block(refs[:50]) + "\n"
    return body

def write_monthly(notes, field_cfg):
    month = datetime.date.today().strftime("%Y-%m")
    field = field_cfg["name"]
    refs = [n.get("doi") or n.get("url") for n in notes if (n.get("doi") or n.get("url"))]
    bullets = [f"- **{n['title']}** - {n.get('summary','')} [{i+1}]" for i,n in enumerate(notes[:20])]
    body = f"# {field} - Monthly Update ({month})\n\n"
    body += "## Highlights\n" + "\n".join(bullets) + "\n\n"
    body += f"## What Changed vs Last Month\n- New items: {len(notes)}\n\n"
    body += "## Signals to Watch\n- Retractions or expressions of concern will appear here.\n\n"
    body += "## References\n" + _ref_block(refs[:80]) + "\n"
    return body
