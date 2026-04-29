"""
Evaluation harness: runs the recommender on 3 predefined profiles and prints
a pass/fail summary with per-check confidence scores.

Usage:
    python tests/eval_harness.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

# ---------------------------------------------------------------------------
# Profiles and their pass/fail criteria
# Each profile is a dict with:
#   profile   – user prefs passed to recommend_songs
#   mode      – scoring mode
#   k         – number of results to request
#   checks    – list of (description, callable(results) -> bool)
# ---------------------------------------------------------------------------

PROFILES = [
    {
        "name": "High-Energy Pop (best-case)",
        "profile": {"genre": "pop", "mood": "happy", "energy": 0.8},
        "mode": "genre-first",
        "k": 3,
        "checks": [
            (
                "#1 result matches genre=pop",
                lambda r: r[0][0]["genre"] == "pop",
            ),
            (
                "#1 result matches mood=happy",
                lambda r: r[0][0]["mood"] == "happy",
            ),
            (
                "#1 score >= 5.0",
                lambda r: r[0][1] >= 5.0,
            ),
            (
                "All top-3 scores > 0",
                lambda r: all(score > 0 for _, score, _ in r),
            ),
        ],
    },
    {
        "name": "Genre Trap — metal + happy (adversarial)",
        "profile": {"genre": "metal", "mood": "happy", "energy": 0.5},
        "mode": "genre-first",
        "k": 3,
        "checks": [
            (
                "#1 result is the only metal song (Neon Rage)",
                lambda r: r[0][0]["title"] == "Neon Rage",
            ),
            (
                "#1 score < 4.0 (catalog gap — no full match possible)",
                lambda r: r[0][1] < 4.0,
            ),
            (
                "#1 mood does NOT match happy (exposes genre-loyalty trap)",
                lambda r: r[0][0]["mood"] != "happy",
            ),
            (
                "mood-first mode surfaces a different #1 than genre-first",
                lambda r: r[0][0]["genre"] != "metal",
            ),
        ],
        # The last check uses mood-first results; we run both modes below
        "_mood_first": True,
    },
    {
        "name": "Chill Lofi + Acoustic (best-case)",
        "profile": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.4,
            "likes_acoustic": True,
        },
        "mode": "genre-first",
        "k": 3,
        "checks": [
            (
                "#1 result matches genre=lofi",
                lambda r: r[0][0]["genre"] == "lofi",
            ),
            (
                "#1 result matches mood=chill",
                lambda r: r[0][0]["mood"] == "chill",
            ),
            (
                "#1 score >= 6.5 (genre + mood + energy + acoustic all fire)",
                lambda r: r[0][1] >= 6.5,
            ),
            (
                "Top-2 both have acousticness > 0.6",
                lambda r: all(
                    float(song.get("acousticness", 0)) > 0.6
                    for song, _, _ in r[:2]
                ),
            ),
        ],
    },
]


def confidence(passed: int, total: int) -> float:
    """Return a 0.0–1.0 confidence score as fraction of checks passed."""
    return passed / total if total else 0.0


def run_harness() -> None:
    songs = load_songs(DATA_PATH)

    total_checks = 0
    total_passed = 0

    print("=" * 60)
    print("  EVAL HARNESS — Music Recommender")
    print("=" * 60)

    for profile_def in PROFILES:
        name    = profile_def["name"]
        prefs   = profile_def["profile"]
        mode    = profile_def["mode"]
        k       = profile_def["k"]
        checks  = profile_def["checks"]

        # Primary results (genre-first or specified mode)
        results = recommend_songs(prefs, songs, k=k, mode=mode)

        # For the adversarial profile the last check needs mood-first results
        if profile_def.get("_mood_first"):
            mood_first_results = recommend_songs(prefs, songs, k=k, mode="mood-first")
            # Swap in mood-first results only for the last check
            check_inputs = [results] * (len(checks) - 1) + [mood_first_results]
        else:
            check_inputs = [results] * len(checks)

        passed = 0
        print(f"\nProfile: {name}")
        print(f"  mode={mode}  |  top-{k} results:")
        for song, score, _ in results:
            print(f"    {song['title']:<25} score={score:.2f}  genre={song['genre']}  mood={song['mood']}")

        print("  Checks:")
        for (desc, fn), data in zip(checks, check_inputs):
            try:
                ok = fn(data)
            except Exception as e:
                ok = False
                desc = f"{desc}  [ERROR: {e}]"
            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            print(f"    [{status}] {desc}")

        conf = confidence(passed, len(checks))
        total_checks += len(checks)
        total_passed += passed
        print(f"  Confidence: {conf:.0%}  ({passed}/{len(checks)} checks passed)")

    overall = confidence(total_passed, total_checks)
    print("\n" + "=" * 60)
    print(f"  OVERALL: {total_passed}/{total_checks} checks passed")
    print(f"  Overall confidence: {overall:.0%}")
    print("=" * 60)

    if total_passed < total_checks:
        sys.exit(1)


if __name__ == "__main__":
    run_harness()
