import json
import subprocess
import sys
from run_manager import create_run, save_log

def run():
    run_id, run_dir = create_run()
    log_path = run_dir / "log.json"

    def update(step, data):
        log = json.loads(log_path.read_text())
        log["steps"][step] = data
        save_log(run_dir, log)

    try:
        print(f"🚀 Starting {run_id}")

        subprocess.run([sys.executable, "validate_inputs.py"], check=True)
        update("validate_inputs", {"status": "ok"})

        subprocess.run([sys.executable, "analyze_scenes.py"], check=True)
        update("analyze_scenes", {"status": "ok"})

        subprocess.run([sys.executable, "score_scenes.py"], check=True)
        update("score_scenes", {"status": "ok"})

        subprocess.run([sys.executable, "build_timeline.py"], check=True)
        update("timeline", {"status": "ok"})

        subprocess.run([sys.executable, "render_video.py", str(run_dir)], check=True)
        update("render", {"status": "ok", "output": "final_video.mp4"})

        log = json.loads(log_path.read_text())
        log["status"] = "success"
        save_log(run_dir, log)

        print("🎉 DONE")

    except Exception as e:
        log = json.loads(log_path.read_text())
        log["status"] = "failed"
        log["error"] = str(e)
        save_log(run_dir, log)
        raise

if __name__ == "__main__":
    run()
