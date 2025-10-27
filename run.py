import argparse, yaml, os
from pipeline.ingest import ingest_all
from pipeline.curate import curate
from pipeline.read import make_notes
from pipeline.summarize import write_state, write_monthly
from pipeline.verify import verify_report
from pipeline.publish import save_report, update_changelog

def main(field_slug: str, mode: str):
    fields = yaml.safe_load(open("config/fields.yaml"))["fields"]
    field_cfg = next(f for f in fields if f["slug"] == field_slug)

    papers = ingest_all(field_cfg)
    selected = curate(papers, field_cfg)
    notes = make_notes(selected, field_cfg)
    if mode == "init":
        report = write_state(notes, field_cfg)
    else:
        report = write_monthly(notes, field_cfg)
    checked = verify_report(report, notes, field_cfg)
    path = save_report(checked, field_cfg, mode)
    update_changelog(path, field_cfg, mode)
    print(f"Wrote {path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", required=True, help="field slug, e.g., g-quadruplexes")
    ap.add_argument("--mode", choices=["init","monthly"], default="monthly")
    args = ap.parse_args()
    os.makedirs("reports", exist_ok=True)
    main(args.field, args.mode)
