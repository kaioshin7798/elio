import json
import subprocess
from pathlib import Path
import sys

VIDEO_DIR = Path("data/videos")
MUSIC_DIR = Path("data/music")
TIMELINE_FILE = Path("data/timeline/timeline.json")


def get_video_info(path: Path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name",
        "-of", "json",
        str(path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return data["streams"][0]


def run():
    if not TIMELINE_FILE.exists():
        raise ValueError("timeline.json not found")

    data = json.loads(TIMELINE_FILE.read_text(encoding="utf-8"))

    # 1️⃣ Validate music
    music = MUSIC_DIR / data["music"]
    if music.suffix.lower() != ".mp3":
        raise ValueError("Music must be .mp3")
    if not music.exists():
        raise ValueError(f"Music file not found: {music}")

    # 2️⃣ Validate videos
    resolutions = set()

    for item in data["timeline"]:
        video = VIDEO_DIR / item["video"]

        if video.suffix.lower() != ".mp4":
            raise ValueError(f"Invalid video format: {video.name}")

        if not video.exists():
            raise ValueError(f"Video not found: {video}")

        if item["duration"] <= 0:
            raise ValueError("Clip duration must be > 0")

        info = get_video_info(video)
        resolutions.add((info["width"], info["height"]))

    # 3️⃣ Resolution consistency
    if len(resolutions) > 1:
        raise ValueError(f"Mixed resolutions detected: {resolutions}")

    print("✅ Input validation passed")


if __name__ == "__main__":
    run()
