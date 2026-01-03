from pathlib import Path
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
import json

VIDEO_DIR = Path("data/videos")
OUTPUT_DIR = Path("data/scenes")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def analyze_video(video_path: Path):
    video_manager = VideoManager([str(video_path)])
    scene_manager = SceneManager()

    scene_manager.add_detector(ContentDetector(threshold=20.0))

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    scene_list = scene_manager.get_scene_list()
    video_manager.release()

    scenes = []
    for idx, (start, end) in enumerate(scene_list):
        scenes.append({
            "scene_id": f"{video_path.stem}_{idx}",
            "video": video_path.name,
            "start": start.get_seconds(),
            "end": end.get_seconds(),
            "duration": end.get_seconds() - start.get_seconds()
        })

    return scenes


def run():
    all_scenes = []

    videos = sorted(VIDEO_DIR.glob("*.*"))
    if not videos:
        print("❌ No videos found in data/videos")
        return

    for video in videos:
        print(f"🎥 Analyzing scenes: {video.name}")
        scenes = analyze_video(video)
        print(f"   → Found {len(scenes)} scenes")
        all_scenes.extend(scenes)

    output_file = OUTPUT_DIR / "scenes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_scenes, f, indent=2)

    print(f"\n✅ Scene analysis done. Saved to {output_file}")


if __name__ == "__main__":
    run()
