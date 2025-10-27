
import argparse, yaml, os, datetime

def main(field, mode):
    print(f"Generating {mode} report for {field}")
    path = f"reports/{field}/" + ("STATE_OF_FIELD.md" if mode=="init" else f"monthly_{datetime.date.today().strftime('%Y-%m')}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w") as f:
        f.write(f"# {field} report ({mode})\n\nGenerated on {datetime.date.today()}\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", required=True)
    ap.add_argument("--mode", choices=["init","monthly"], default="monthly")
    a=ap.parse_args()
    main(a.field, a.mode)
