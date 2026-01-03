import json
import subprocess
from pathlib import Path
import shutil
import sys
from pathlib import Path

TIMELINE_FILE = Path("data/timeline/timeline.json")
VIDEO_DIR = Path("data/videos")
MUSIC_DIR = Path("data/music")
TEMP_DIR = Path("data/tmp")

TEMP_DIR.mkdir(parents=True, exist_ok=True)

def run():
    run_dir = Path(sys.argv[1])
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    inputs = []
    filter_inputs = []

    for idx, item in enumerate(data["timeline"]):
        src = VIDEO_DIR / item["video"]
        inputs.extend([
            "-ss", str(item["start"]),
            "-t", str(item["duration"]),
            "-i", str(src)
        ])
        filter_inputs.append(f"[{idx}:v]")

    filter_complex = (
        "".join(filter_inputs)
        + f"concat=n={len(filter_inputs)}:v=1:a=0[outv]"
    )

    final_output = run_dir / "final_video.mp4"
    music = MUSIC_DIR / data["music"]

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", str(music),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", f"{len(filter_inputs)}:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.2",
        "-c:a", "aac",
        "-movflags", "+faststart",
        "-shortest",
        str(final_output)
    ]

    print("🎬 Rendering final video (CPU-safe mode)...")
    subprocess.run(cmd, check=True)

    print(f"\n🎉 FINAL VIDEO READY → {final_output}")


if __name__ == "__main__":
    run()
