import json
from pathlib import Path
import subprocess
import numpy as np

SCENES_FILE = Path("data/scenes/scenes.json")
VIDEO_DIR = Path("data/videos")
OUTPUT_FILE = Path("data/scenes/scored_scenes.json")


def motion_score(video_path, start, end):
    """
    Rough motion estimation using frame difference
    """
    cmd = [
        "ffmpeg",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(video_path),
        "-vf", "fps=5,scale=320:-1",
        "-f", "rawvideo",
        "-"
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw = process.stdout.read()
    process.wait()

    if not raw:
        return 0.0

    frame_size = 320 * int(320 * 9 / 16) * 3
    frames = np.frombuffer(raw, dtype=np.uint8)

    if len(frames) < frame_size * 2:
        return 0.0

    frames = frames[: len(frames) // frame_size * frame_size]
    frames = frames.reshape((-1, frame_size))

    diffs = np.abs(frames[1:] - frames[:-1])
    return float(np.mean(diffs))


def duration_score(duration):
    if duration < 1.0:
        return 0.1
    if duration > 8.0:
        return 0.4
    return 1.0


def run():
    with open(SCENES_FILE, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    scored = []

    for scene in scenes:
        video_path = VIDEO_DIR / scene["video"]
        print(f"🎬 Scoring {scene['scene_id']}")

        motion = motion_score(
            video_path,
            scene["start"],
            scene["end"]
        )

        score = (
            motion * 0.7 +
            duration_score(scene["duration"]) * 30
        )

        scene["motion_score"] = round(motion, 2)
        scene["final_score"] = round(score, 2)

        scored.append(scene)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2)

    print(f"\n✅ Scene scoring done → {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
