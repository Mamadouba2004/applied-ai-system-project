# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

```bash
# Run the recommender CLI
python -m src.main

# Run all tests
pytest tests/

# Run a single test
pytest tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score
```

## Architecture

This project has two parallel implementations of the same recommender logic:

**Functional API** (used by `src/main.py`):
- `load_songs(csv_path)` → `List[Dict]`
- `score_song(user_prefs: Dict, song: Dict)` → `(float, List[str])` — returns score + reasons
- `recommend_songs(user_prefs, songs, k=5)` → `List[Tuple[Dict, float, str]]` — returns (song, score, explanation) tuples

**OOP API** (tested by `tests/test_recommender.py`):
- `Song` dataclass: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- `UserProfile` dataclass: favorite_genre, favorite_mood, target_energy, likes_acoustic
- `Recommender(songs)` class with `.recommend(user, k)` and `.explain_recommendation(user, song)` methods

The functional API is entry-pointed from `src/main.py` (uses dict-based `user_prefs = {"genre": ..., "mood": ..., "energy": ...}`). The OOP API is what the tests validate. Both live in `src/recommender.py`.

## Data

`data/songs.csv` has 18 songs with these numeric features (all 0.0–1.0 except tempo_bpm): `energy`, `valence`, `danceability`, `acousticness`, and `tempo_bpm` (72–152 BPM). Categorical features: `genre` (pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, hip-hop, classical, rnb, metal, funk, electronic) and `mood` (happy, chill, intense, relaxed, focused, moody, nostalgic, energetic, melancholic, romantic).

## Scoring Design

The recommender uses **content-based filtering** — matching song attributes to a user taste profile. The intended scoring approach rewards proximity for numeric features (e.g., energy close to `target_energy` scores higher than just high/low energy) and exact-match bonuses for categorical features (genre, mood). Weights should reflect that genre/mood matches matter more than numeric feature differences.
