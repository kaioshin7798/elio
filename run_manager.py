import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("output")

def get_next_run_id():
    OUTPUT_DIR.mkdir(exist_ok=True)
    runs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name.startswith("run_")]
    if not runs:
        return "run_001"

    last = max(int(d.name.split("_")[1]) for d in runs)
    return f"run_{last + 1:03d}"

def create_run():
    run_id = get_next_run_id()
    run_dir = OUTPUT_DIR / run_id
    run_dir.mkdir()

    log = {
        "run_id": run_id,
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "steps": {}
    }

    save_log(run_dir, log)
    return run_id, run_dir

def save_log(run_dir, log):
    with open(run_dir / "log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
