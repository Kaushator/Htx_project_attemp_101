import argparse, os, datetime, json
from pathlib import Path

BASE = Path(__file__).resolve().parent
JOURNAL = BASE / "journal.md"
ROADMAP = BASE / "roadmap.md"
ENV_PATH = BASE / ".env"

def load_env():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def log_task(prompt, result):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"## {ts}\n- **Prompt:** {prompt}\n- **Result:** {result}\n\n"
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(entry)

def roadmap_update(task, status="in progress"):
    with open(ROADMAP, "a", encoding="utf-8") as f:
        f.write(f"- {task} → {status}\n")

def main():
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", help="Prompt to log")
    parser.add_argument("--result", default="", help="Result/outcome summary")
    parser.add_argument("--roadmap", help="Add/update roadmap item (text)")
    parser.add_argument("--status", default="in progress", help="Roadmap status")
    args = parser.parse_args()

    if args.log:
        log_task(args.log, args.result)
    if args.roadmap:
        roadmap_update(args.roadmap, args.status)

if __name__ == "__main__":
    main()