import json
from pathlib import Path
from pydub import AudioSegment
from ai_rank_scenes import ai_rank_scenes
from ai_pace_scenes import ai_pace_scenes

SCENES_FILE = Path("data/scenes/scored_scenes.json")
MUSIC_FILE = Path("data/music/track.mp3")
OUTPUT_FILE = Path("data/timeline/timeline.json")

MODE = "random"  # or "linear"
USE_AI = True

MAX_SCENE_DURATION = 4.0  # 🔥 quan trọng: montage feel

def get_rule_score(scene):
    # fallback priority
    return (
        scene.get("score")
        or scene.get("motion_score")
        or scene.get("final_score")
        or 0
    )

def split_long_scene(scene):
    """
    Split a long scene into smaller chunks
    """
    chunks = []
    t = scene["start"]

    while t < scene["end"]:
        end = min(t + MAX_SCENE_DURATION, scene["end"])

        chunk = scene.copy()
        chunk["start"] = round(t, 2)
        chunk["end"] = round(end, 2)
        chunk["duration"] = round(end - t, 2)

        chunks.append(chunk)
        t = end

    return chunks


def run():
    music = AudioSegment.from_file(MUSIC_FILE)
    music_duration = music.duration_seconds

    with open(SCENES_FILE, "r", encoding="utf-8") as f:
        scenes = json.load(f)

    # 🔹 Split long scenes first
    processed_scenes = []
    for s in scenes:
        if s["duration"] > MAX_SCENE_DURATION:
            processed_scenes.extend(split_long_scene(s))
        else:
            processed_scenes.append(s)

    scenes = processed_scenes

    # 🔹 AI ranking (random mode only)
    if MODE == "random":
        if USE_AI:
            ai_scores = ai_rank_scenes(scenes)
            ai_map = {s["scene_id"]: s for s in ai_scores}

            for s in scenes:
                ai = ai_map.get(s["scene_id"])
                if ai:
                    rule_score = get_rule_score(s)

                    s["final_score"] = (
                        rule_score * 0.6 +
                        (ai["ai_score"] / 100) * 0.4
                    )
                else:
                    s["final_score"] = rule_score

        scenes.sort(
            key=lambda x: x.get("final_score", get_rule_score(x)),
            reverse=True
        )
    else:
        scenes = sorted(scenes, key=lambda s: (s["video"], s["start"]))

    pace_map = {}

    if MODE == "random":
        pace_results = ai_pace_scenes(scenes)
        pace_map = {p["scene_id"]: p for p in pace_results}

    # 🔹 Build timeline
    timeline = []
    current_time = 0.0

    for scene in scenes:
        if current_time >= music_duration:
            break

        pace = pace_map.get(scene["scene_id"])
        target_duration = scene["duration"]

        if pace:
            target_duration = pace["suggested_duration"]

        remaining = music_duration - current_time
        used_duration = min(target_duration, remaining)

        timeline.append({
            "scene_id": scene["scene_id"],
            "video": scene["video"],
            "start": scene["start"],
            "duration": round(used_duration, 2),
            "score": round(scene.get("final_score", scene.get("score", 50)), 2),
            "cut": pace["cut"] if pace else "hard",
            "pace": pace["pace"] if pace else "medium",
        })

        current_time += used_duration


    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "music": MUSIC_FILE.name,
                "music_duration": round(music_duration, 2),
                "mode": MODE,
                "timeline": timeline,
            },
            f,
            indent=2,
        )

    print(f"✅ Timeline built → {OUTPUT_FILE}")
    print(f"🎵 Music duration: {music_duration:.2f}s")
    print(f"🎬 Timeline duration: {current_time:.2f}s")
    print(f"🎞️ Scenes used: {len(timeline)}")


if __name__ == "__main__":
    run()
