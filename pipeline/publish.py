import os, datetime

def save_report(text, field_cfg, mode):
    d = f"reports/{field_cfg['slug']}"
    os.makedirs(d, exist_ok=True)
    if mode == "init":
        fname = "STATE_OF_FIELD.md"
    else:
        fname = f"monthly_{datetime.date.today().strftime('%Y-%m')}.md"
    path = os.path.join(d, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def update_changelog(path, field_cfg, mode):
    clog = f"reports/{field_cfg['slug']}/CHANGELOG.md"
    os.makedirs(os.path.dirname(clog), exist_ok=True)
    line = f"- {datetime.date.today().isoformat()} - wrote `{os.path.basename(path)}` ({mode})\n"
    if os.path.exists(clog):
        with open(clog, "a", encoding="utf-8") as f:
            f.write(line)
    else:
        with open(clog, "w", encoding="utf-8") as f:
            f.write(f"# Changelog - {field_cfg['name']}\n\n{line}")
