"""RAG pipeline for the music recommender using Claude."""
import csv
import os
from pathlib import Path
from typing import Optional

import anthropic


def get_anthropic_client() -> anthropic.Anthropic:
    """Create an Anthropic client using Claude Code's OAuth token when no API key is set."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic()

    # Claude Code exposes its OAuth token via a numbered file descriptor.
    # This allows subprocesses to call the Anthropic API without a separate key.
    token_fd_str = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR")
    if token_fd_str:
        raw = os.read(int(token_fd_str), 8192).decode().strip()
        return anthropic.Anthropic(auth_token=raw)

    raise RuntimeError(
        "No Anthropic authentication found. "
        "Set ANTHROPIC_API_KEY or run inside a Claude Code session."
    )


def load_songs_as_context(csv_path: str) -> str:
    """Format the songs CSV as a plain-text block for use as RAG context."""
    lines = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            lines.append(
                f"- {row['title']} by {row['artist']} | genre={row['genre']} | "
                f"mood={row['mood']} | energy={row['energy']} | "
                f"tempo={row['tempo_bpm']} BPM | valence={row['valence']} | "
                f"danceability={row['danceability']} | acousticness={row['acousticness']}"
            )
    return "\n".join(lines)


def query_rag(question: str, csv_path: Optional[str] = None) -> str:
    """Answer a natural-language question about the music catalog using Claude."""
    if csv_path is None:
        csv_path = str(Path(__file__).parent.parent / "data" / "songs.csv")

    context = load_songs_as_context(csv_path)
    client = get_anthropic_client()

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=(
            "You are a music recommender assistant. "
            "Use only the song catalog below to answer questions. "
            "Do not invent songs that are not listed.\n\n"
            f"Song catalog:\n{context}"
        ),
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text


if __name__ == "__main__":
    answer = query_rag("Which songs are best for studying or focusing?")
    print(answer)
