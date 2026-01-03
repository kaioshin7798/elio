import json
from pathlib import Path
from pydub import AudioSegment
import random

SCENES_FILE = Path("data/scenes/scored_scenes.json")
MUSIC_FILE = Path("data/music/track.mp3")
OUTPUT_FILE = Path("data/timeline/timeline.json")

MODE = "random"  # or "linear"


def run():
    music = AudioSegment.from_file(MUSIC_FILE)
    music_duration = music.duration_seconds

    with open(SCENES_FILE, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    if MODE == "random":
        scenes = sorted(scenes, key=lambda s: s["final_score"], reverse=True)
    else:
        scenes = sorted(scenes, key=lambda s: (s["video"], s["start"]))

    timeline = []
    current_time = 0.0

    for scene in scenes:
        if current_time >= music_duration:
            break

        scene_duration = scene["duration"]
        remaining = music_duration - current_time

        used_duration = min(scene_duration, remaining)

        timeline.append({
            "scene_id": scene["scene_id"],
            "video": scene["video"],
            "start": scene["start"],
            "duration": round(used_duration, 2),
            "score": scene["final_score"]
        })

        current_time += used_duration

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "music": MUSIC_FILE.name,
            "music_duration": round(music_duration, 2),
            "mode": MODE,
            "timeline": timeline
        }, f, indent=2)

    print(f"✅ Timeline built → {OUTPUT_FILE}")
    print(f"🎵 Music duration: {music_duration:.2f}s")
    print(f"🎬 Timeline duration: {current_time:.2f}s")


if __name__ == "__main__":
    run()
