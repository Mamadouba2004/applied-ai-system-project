"""Retrieval layer: returns grounded context from a knowledge base."""

KNOWLEDGE_BASE = {
    "genres": {
        "pop":        "Polished, radio-friendly songs with strong hooks and broad appeal. Typically upbeat with high production.",
        "lofi":       "Low-fidelity beats with warm, lo-fi textures. Calm and studious atmosphere, often instrumental.",
        "rock":       "Guitar-driven energy with an emphasis on power and attitude. Ranges from anthemic to aggressive.",
        "metal":      "High-intensity, distortion-heavy genre built around aggression, speed, and dark themes.",
        "ambient":    "Atmospheric and texture-focused music designed for passive listening or background focus.",
        "jazz":       "Improvisational, harmonically rich genre with swing rhythms and expressive soloists.",
        "synthwave":  "Retro-futuristic electronic genre inspired by 1980s film scores and arcade soundtracks.",
        "indie pop":  "Independent pop with a DIY aesthetic — melodic but less polished than mainstream pop.",
        "country":    "Storytelling-driven genre rooted in rural American traditions, acoustic instruments, and themes of home.",
        "hip-hop":    "Rhythm-based genre built on beats, samples, and spoken or rapped vocal delivery.",
        "classical":  "Orchestral or chamber music tradition emphasising form, harmonic complexity, and dynamic range.",
        "rnb":        "Smooth, groove-oriented genre blending soul, funk, and pop with expressive vocals.",
        "electronic": "Synthesiser and sequencer-driven music covering a wide range of tempos and moods.",
        "funk":       "Groove-first genre rooted in syncopated bass lines, brass, and a strong danceable feel.",
    },
    "moods": {
        "happy":      "Uplifting, positive energy. Songs feel optimistic, bright, and good for celebration or motivation.",
        "chill":      "Relaxed and unhurried. Good for winding down, studying, or background listening.",
        "intense":    "High tension and drive. Songs feel urgent, powerful, or confrontational.",
        "relaxed":    "Calm and gentle. Lower energy than chill — meant for rest or quiet reflection.",
        "focused":    "Minimal distraction. Steady rhythm and neutral emotional tone to support concentration.",
        "moody":      "Atmospheric and introspective. Can feel melancholic, mysterious, or emotionally complex.",
        "nostalgic":  "Evokes memory and longing. Warm tonality and familiar sonic textures.",
        "melancholic":"Sad or bittersweet emotional tone. Often slower tempo and lower valence.",
        "romantic":   "Intimate and warm. Smooth textures and expressive vocals suggesting closeness.",
        "energetic":  "High drive and excitement. Built for movement, workouts, or peak-energy moments.",
    },
}


def retrieve_context(genre: str, mood: str) -> str:
    """Return genre and mood descriptions from the knowledge base.

    Falls back gracefully when genre or mood is not recognised.
    """
    genre_desc = KNOWLEDGE_BASE["genres"].get(
        genre.lower(),
        f"'{genre}' is not a recognised genre in the knowledge base.",
    )
    mood_desc = KNOWLEDGE_BASE["moods"].get(
        mood.lower(),
        f"'{mood}' is not a recognised mood in the knowledge base.",
    )
    return (
        f"Genre context — {genre}: {genre_desc}\n"
        f"Mood context — {mood}: {mood_desc}"
    )
