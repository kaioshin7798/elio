# Elio 🎬

Elio is a personal AI-assisted video montage pipeline.

It ingests multiple videos, analyzes scenes, builds a timeline, and renders
a final video synced to music.  
Each run is versioned so results can be compared, regenerated, and later
mapped into a UI.

---

## 🚀 Features
- Multiple video ingestion
- Scene analysis & scoring
- Timeline generation (random / linear)
- FFmpeg-based rendering
- Versioned outputs (`run_XXX`)
- Structured JSON logging
- Input validation (fail fast)

---

## 🖥️ Requirements
- Windows
- Python **3.11+**
- FFmpeg (must be available in `PATH`)
- Virtual environment recommended

---

## 📦 Setup

```bash
python -m venv .venv
source .venv/Scripts/activate    # Git Bash
# or
.venv\Scripts\activate           # CMD / PowerShell

pip install -r requirements.txt

## Verify FFmpeg
ffmpeg -version
```

## Project structure
```bash
data/
 ├─ videos/          # input .mp4 videos
 ├─ music/           # background music (.mp3)
 ├─ scenes/          # scenes.json
 ├─ timeline/        # timeline.json
 └─ tmp/             # temporary files

output/
 ├─ run_001/
 │   ├─ final_video.mp4
 │   └─ log.json
 ├─ run_002/
 │   ├─ final_video.mp4
 │   └─ log.json
 ```

## Run pipeline
```bash
python run_all.py
```
