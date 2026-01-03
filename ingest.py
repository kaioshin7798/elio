# ingest.py
import os
import subprocess
import json
from pathlib import Path

VIDEO_DIR = Path("data/videos")

def get_video_metadata(video_path: Path):
    """
    Read basic metadata using ffprobe (part of ffmpeg)
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-of", "json",
        str(video_path)
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {video_path.name}")

    data = json.loads(result.stdout)
    stream = data["streams"][0]

    return {
        "file": video_path.name,
        "width": stream.get("width"),
        "height": stream.get("height"),
        "fps": stream.get("r_frame_rate"),
        "duration": float(stream.get("duration", 0))
    }


def ingest_videos():
    videos = sorted(VIDEO_DIR.glob("*.*"))

    if not videos:
        print("❌ No videos found in data/videos/")
        return

    print(f"🎬 Found {len(videos)} video(s):\n")

    for video in videos:
        try:
            meta = get_video_metadata(video)
            print(
                f"- {meta['file']} | "
                f"{meta['width']}x{meta['height']} | "
                f"fps: {meta['fps']} | "
                f"duration: {meta['duration']:.2f}s"
            )
        except Exception as e:
            print(f"⚠️ Failed to read {video.name}: {e}")


if __name__ == "__main__":
    ingest_videos()
