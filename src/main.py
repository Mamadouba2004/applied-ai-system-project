"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import os
from src.recommender import load_songs, recommend_songs
from src.rag import query_rag

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

def main() -> None:
    songs = load_songs(_DATA_PATH)

    # Demo: same profile run through all three scoring modes
    demo_profile = {"genre": "metal", "mood": "happy", "energy": 0.5}

    all_titles: list[str] = []
    for mode in ["genre-first", "mood-first", "energy-focus"]:
        print(f"\n{'='*50}")
        print(f"  Mode: {mode.upper()}  |  Profile: metal + happy + energy 0.5")
        print(f"{'='*50}")
        for song, score, explanation in recommend_songs(demo_profile, songs, k=3, mode=mode):
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"  Because: {explanation}")
            all_titles.append(song["title"])

    unique_titles = list(dict.fromkeys(all_titles))
    print(f"\n{'='*50}")
    print("  Claude AI Explanation")
    print(f"{'='*50}")
    question = (
        f"A user likes metal music, happy mood, and medium energy (0.5). "
        f"The scoring system recommended these songs across three modes: "
        f"{', '.join(unique_titles)}. "
        f"In 3-4 sentences, explain why these songs fit (or don't fit) this profile "
        f"and highlight any interesting patterns."
    )
    # Build a minimal candidates list for guardrail score validation
    all_results = []
    for mode in ["genre-first", "mood-first", "energy-focus"]:
        for song, score, _ in recommend_songs(demo_profile, songs, k=3, mode=mode):
            all_results.append({"title": song["title"], "score": score})
    print(query_rag(
        question,
        genre=demo_profile["genre"],
        mood=demo_profile["mood"],
        candidates=all_results,
    ))


if __name__ == "__main__":
    main()
