"""Output guardrails for the RAG pipeline."""

from typing import List, Dict


def validate(text: str, candidates: List[Dict]) -> str:
    """Validate a Claude response against the candidate song list.

    Checks (in order):
    - Non-empty response
    - Minimum length of 40 characters
    - All candidate scores are >= 0
    - At least one candidate song title is mentioned in the response

    Returns the original text if all checks pass, otherwise raises ValueError
    with a descriptive message.
    """
    if not text or not text.strip():
        raise ValueError("Guardrail failed: response is empty.")

    if len(text.strip()) < 40:
        raise ValueError(
            f"Guardrail failed: response too short "
            f"({len(text.strip())} chars, minimum 40)."
        )

    for song in candidates:
        score = song.get("score", 0)
        if score < 0:
            raise ValueError(
                f"Guardrail failed: negative score ({score}) for "
                f"'{song.get('title', 'unknown')}'."
            )

    titles = [song.get("title", "") for song in candidates if song.get("title")]
    if titles and not any(title.lower() in text.lower() for title in titles):
        raise ValueError(
            "Guardrail failed: response does not mention any recommended song title. "
            f"Expected at least one of: {titles}."
        )

    return text
