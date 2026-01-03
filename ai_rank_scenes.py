import json
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

MODEL = "gpt-4.1-mini"

PROMPT = """
You are a professional video editor AI.

Given a list of video scenes with metadata:
- scene_id
- duration (seconds)
- motion (0-1)
- brightness (0-1)
- faces (count)

Goal:
Rank scenes for a short cinematic montage.
Prefer scenes that are engaging, emotional, and visually clear.

Return JSON only, no markdown:
[
  {
    "scene_id": number,
    "ai_score": 0-100,
    "reason": "short explanation"
  }
]
"""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ai_rank_scenes(scenes):
    """
    scenes: list of dicts from score_scenes output
    returns: list of {scene_id, ai_score, reason}
    """

    payload = []
    for s in scenes:
        payload.append({
            "scene_id": s["scene_id"],
            "duration": round(s["end"] - s["start"], 2),
            "motion": s.get("motion", 0),
            "brightness": s.get("brightness", 0),
            "faces": s.get("faces", 0),
        })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print("[AI RANK] Failed, fallback to rule-based only:", e)
        return []
