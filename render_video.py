import json
import subprocess
import sys
from pathlib import Path

CROSSFADE_DURATION = 0.4

VIDEOS_DIR = Path("data/videos")
TIMELINE_FILE = Path("data/timeline/timeline.json")
MUSIC_DIR = Path("data/music")


def run(cmd):
    subprocess.run(cmd, check=True)


def render_scene(scene, out_path):
    src = VIDEOS_DIR / scene["video"]

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(scene["start"]),
        "-t", str(scene["duration"]),
        "-i", str(src),
        "-vf", "scale=1280:720",
        "-r", "30",
        "-an",
        str(out_path),
    ]
    run(cmd)


def concat(a, b, out):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(a),
        "-i", str(b),
        "-filter_complex",
        "[0:v][1:v]concat=n=2:v=1:a=0[v]",
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out),
    ]
    run(cmd)


def xfade(a, b, out, duration):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(a),
        "-i", str(b),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={duration}:offset=0[v]",
        "-map", "[v]",
        "-an",
        str(out),
    ]
    run(cmd)


def add_music(video, music, out):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video),
        "-i", str(music),
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(out),
    ]
    run(cmd)


def main(run_dir: Path):
    timeline = json.loads(TIMELINE_FILE.read_text())
    scenes = timeline["timeline"]

    tmp_dir = run_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    clips = []

    print("🎬 Rendering scenes...")
    for i, scene in enumerate(scenes):
        out = tmp_dir / f"{i:03d}.mp4"
        render_scene(scene, out)
        clips.append(out)

    print("✂️ Applying cuts...")
    current = clips[0]

    for i in range(1, len(clips)):
        next_clip = clips[i]
        cut = scenes[i].get("cut", "hard")

        out = tmp_dir / f"mix_{i:03d}.mp4"

        if cut == "crossfade":
            xfade(current, next_clip, out, CROSSFADE_DURATION)
        else:
            concat(current, next_clip, out)

        current = out

    video_no_music = run_dir / "video_no_music.mp4"
    current.rename(video_no_music)

    print("🎵 Adding music...")
    music_file = MUSIC_DIR / timeline["music"]
    final_video = run_dir / "final_video.mp4"

    add_music(video_no_music, music_file, final_video)

    print(f"✅ Final video → {final_video}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_video.py <run_dir>")
        sys.exit(1)

    main(Path(sys.argv[1]))
