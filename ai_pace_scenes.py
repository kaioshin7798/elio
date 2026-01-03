import random

PACE_DURATION = {
    "fast":   (1.8, 2.5),   # ⬅️ tăng
    "medium": (2.8, 4.0),
    "slow":   (4.0, 6.0),
}


def decide_pace(scene):
    m = scene.get("motion_score", 0)
    if m > 80:
        return "fast"
    if m > 40:
        return "medium"
    return "slow"

def ai_pace_scenes(scenes):
    results = []

    # sort by motion ASC
    sorted_scenes = sorted(scenes, key=lambda s: s.get("motion_score", 0))

    slow_count = max(1, int(len(sorted_scenes) * 0.2))  # 20% slow
    slow_ids = {s["scene_id"] for s in sorted_scenes[:slow_count]}

    for s in scenes:
        if s["scene_id"] in slow_ids:
            pace = "slow"
        else:
            pace = decide_pace(s)

        dmin, dmax = PACE_DURATION[pace]
        suggested = min(
            random.uniform(dmin, dmax),
            s["duration"]
        )

        results.append({
            "scene_id": s["scene_id"],
            "pace": pace,
            "suggested_duration": round(suggested, 2),
            "cut": "crossfade" if pace == "slow" else "hard",
            "confidence": round(min(1.0, s.get("final_score", 50) / 100), 2),
        })

    return results

