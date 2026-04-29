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

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

def main() -> None:
    songs = load_songs(_DATA_PATH)

    # Demo: same profile run through all three scoring modes
    demo_profile = {"genre": "metal", "mood": "happy", "energy": 0.5}

    for mode in ["genre-first", "mood-first", "energy-focus"]:
        print(f"\n{'='*50}")
        print(f"  Mode: {mode.upper()}  |  Profile: metal + happy + energy 0.5")
        print(f"{'='*50}")
        for song, score, explanation in recommend_songs(demo_profile, songs, k=3, mode=mode):
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"  Because: {explanation}")


if __name__ == "__main__":
    main()
